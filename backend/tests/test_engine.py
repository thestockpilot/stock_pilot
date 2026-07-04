"""
Unit tests for the indicator pipeline and critical correctness properties.

Run with:
    uv run pytest tests/ -v

Your layout:
    app/services/indicators/featureEngine.py  -> class FeatureEngine
    app/services/market_data/fetcher.py       -> class DataFetcher
    app/services/recommendation/engine.py    -> class StockPredictor
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.services.indicators.featureEngine import FeatureEngine


# ------------------------------------------------------------------
# shared fake OHLCV data
# ------------------------------------------------------------------

def _fake_ohlcv(n: int = 120, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic OHLCV DataFrame with a geometric random walk.
    Uses only numpy so it works without a network connection.
    """
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.001, 0.018, size=n)
    close = 100.0 * np.cumprod(1.0 + returns)
    high   = close * (1.0 + np.abs(rng.normal(0, 0.004, n)))
    low    = close * (1.0 - np.abs(rng.normal(0, 0.004, n)))
    open_  = close * (1.0 + rng.normal(0, 0.002, n))
    volume = rng.integers(1_000_000, 8_000_000, size=n).astype(float)
    idx    = pd.date_range("2022-01-03", periods=n, freq="B")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low,
         "Close": close, "Volume": volume},
        index=idx,
    )


# ==================================================================
# 1. validate_data must not mutate the caller's DataFrame
# ==================================================================

class TestValidateData:

    def test_does_not_mutate_input(self):
        """
        validate_data used to call rename(..., inplace=True) on the argument.
        That silently changed the caller's object. Now it must work on a copy.
        """
        df = _fake_ohlcv(50)
        # Rename one column to force the renaming code path
        df = df.rename(columns={"Close": "Close_AAPL"})
        original_columns = list(df.columns)

        engine = FeatureEngine()
        engine.validate_data(df)

        # Caller's DataFrame is unchanged
        assert list(df.columns) == original_columns, (
            "validate_data mutated the caller's DataFrame"
        )
        # Engine's internal copy has the canonical column name
        assert "Close" in engine.data.columns

    def test_raises_on_empty_dataframe(self):
        engine = FeatureEngine()
        with pytest.raises(ValueError, match="empty"):
            engine.validate_data(pd.DataFrame())

    def test_raises_on_insufficient_rows(self):
        """Need at least ~35 rows to warm up all indicators (MACD uses 26+9)."""
        df = _fake_ohlcv(10)
        engine = FeatureEngine()
        with pytest.raises(ValueError):
            engine.validate_data(df)

    def test_accepts_case_insensitive_columns(self):
        """Columns named 'close', 'OPEN', etc. should be accepted."""
        df = _fake_ohlcv(50)
        df.columns = [c.lower() for c in df.columns]
        engine = FeatureEngine()
        engine.validate_data(df)          # must not raise
        assert "Close" in engine.data.columns


# ==================================================================
# 2. NaN handling must NOT back-fill (that would be look-ahead bias)
# ==================================================================

class TestHandleNaN:

    def test_warmup_rows_are_dropped_not_filled(self):
        """
        The original implementation used bfill() which fills an early NaN with
        a later value — i.e. from the future. That is look-ahead bias.
        The fix drops the warmup window instead.
        """
        engine = FeatureEngine()
        df = pd.DataFrame(
            {
                "Open":   [100, 101, 102, 103, 104],
                "High":   [101, 102, 103, 104, 105],
                "Low":    [ 99, 100, 101, 102, 103],
                "Close":  [100, 101, 102, 103, 104],
                "Volume": [1000, 1100, 1200, 1300, 1400],
                # Indicator is NaN for the first two rows (warmup period)
                "RSI_14": [np.nan, np.nan, 48.0, 52.0, 55.0],
            },
            index=pd.date_range("2024-01-01", periods=5, freq="B"),
        )

        cleaned = engine.handle_nan_values(df)

        # Two NaN rows must be gone
        assert len(cleaned) == 3, (
            f"Expected 3 rows after trimming warmup, got {len(cleaned)}"
        )
        # The remaining RSI values must be the original ones, not back-filled
        assert cleaned["RSI_14"].tolist() == [48.0, 52.0, 55.0], (
            "NaN rows appear to have been back-filled (look-ahead bias)"
        )

    def test_no_nans_in_result(self):
        df = _fake_ohlcv(120)
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        indicator_cols = engine.feature_columns
        nan_counts = result[indicator_cols].isna().sum()
        bad = nan_counts[nan_counts > 0]
        assert bad.empty, f"NaN values remain in indicator columns:\n{bad}"


# ==================================================================
# 3. Full pipeline sanity checks
# ==================================================================

class TestPipeline:

    def test_produces_expected_number_of_features(self):
        df = _fake_ohlcv(120)
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        # We computed at least 20 distinct indicators
        assert len(engine.feature_columns) >= 20, (
            f"Only {len(engine.feature_columns)} features produced"
        )

    def test_output_has_rows(self):
        df = _fake_ohlcv(120)
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        assert len(result) > 0

    def test_feature_columns_do_not_include_ohlcv(self):
        """OHLCV columns are raw data, not indicators — they should not leak."""
        df = _fake_ohlcv(120)
        engine = FeatureEngine()
        engine.calculate_all_features(df)
        raw_cols = {"Open", "High", "Low", "Volume", "Ticker"}
        overlap = raw_cols & set(engine.feature_columns)
        assert not overlap, (
            f"Raw OHLCV columns found in feature_columns: {overlap}"
        )

    def test_known_indicators_present(self):
        """Spot-check that key indicator groups were all computed."""
        df = _fake_ohlcv(120)
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        expected = ["RSI_14", "MACD", "MACD_Signal", "BB_High", "BB_Low",
                    "ATR_14", "OBV", "Volume_Ratio", "ROC_10"]
        missing = [c for c in expected if c not in result.columns]
        assert not missing, f"Expected indicators not found: {missing}"

    def test_sma_values_are_correct(self):
        """Manual sanity check: SMA_5 on a constant series should equal the constant."""
        n = 60
        df = pd.DataFrame(
            {"Open": [10.0] * n, "High": [11.0] * n, "Low": [9.0] * n,
             "Close": [10.0] * n, "Volume": [1_000_000.0] * n},
            index=pd.date_range("2023-01-01", periods=n, freq="B"),
        )
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        sma5 = result["SMA_5"].dropna()
        assert np.allclose(sma5, 10.0), (
            f"SMA_5 on a flat series should be 10.0, got {sma5.values}"
        )


# ==================================================================
# 4. Causality — indicators may not peek at the future
# ==================================================================

class TestCausality:

    def test_indicators_are_causal(self):
        """
        An indicator at time t must depend only on rows up to and including t.

        Method: compute features on the full series and on a truncated version.
        The values at the last shared date must be identical to floating-point
        precision. Any difference means a future row leaked into an earlier one.
        """
        df = _fake_ohlcv(150, seed=7)

        engine_full = FeatureEngine()
        features_full = engine_full.calculate_all_features(df)

        engine_trunc = FeatureEngine()
        features_trunc = engine_trunc.calculate_all_features(df.iloc[:100])

        common_idx = features_full.index.intersection(features_trunc.index)
        assert len(common_idx) > 0, "no rows in common between full and truncated series"

        check_at = common_idx[-1]

        violations = []
        for col in engine_full.feature_columns:
            if col not in features_trunc.columns:
                continue
            v_full  = features_full.loc[check_at, col]
            v_trunc = features_trunc.loc[check_at, col]
            if not np.isclose(v_full, v_trunc, rtol=1e-7, atol=1e-7):
                violations.append(
                    f"  {col}: full={v_full:.6f}  truncated={v_trunc:.6f}"
                )

        assert not violations, (
            "The following indicators differ between the full and truncated "
            "series — this indicates look-ahead bias:\n" + "\n".join(violations)
        )


# ==================================================================
# 5. Edge cases
# ==================================================================

class TestEdgeCases:

    def test_ticker_column_is_handled(self):
        """A Ticker column attached by yfinance/DataFetcher must not crash the engine."""
        df = _fake_ohlcv(120)
        df["Ticker"] = "AAPL"
        engine = FeatureEngine()
        result = engine.calculate_all_features(df)
        assert len(result) > 0

    def test_multiindex_columns_are_flattened(self):
        """yfinance sometimes returns MultiIndex columns. validate_data must handle them."""
        df = _fake_ohlcv(50)
        df.columns = pd.MultiIndex.from_tuples(
            [(c, "AAPL") for c in df.columns]
        )
        engine = FeatureEngine()
        engine.validate_data(df)          # must not raise
        assert "Close" in engine.data.columns

    def test_idempotent(self):
        """Running the pipeline twice on the same data returns the same result."""
        df = _fake_ohlcv(120)

        engine_a = FeatureEngine()
        result_a = engine_a.calculate_all_features(df)

        engine_b = FeatureEngine()
        result_b = engine_b.calculate_all_features(df)

        pd.testing.assert_frame_equal(
            result_a[engine_a.feature_columns],
            result_b[engine_b.feature_columns],
            check_exact=False,
            rtol=1e-10,
        )