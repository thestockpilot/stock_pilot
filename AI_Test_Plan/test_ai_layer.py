"""AI-layer test cases for StockPilot.

Executable pytest cases that verify the AI pipeline end to end:
DataFetcher -> FeatureEngine -> StockPredictor (prepare/predict/walk-forward/backtest).

Assertions check structural CONTRACTS and valid RANGES (not exact accuracy, which
is data-dependent), so the suite is deterministic pass/fail.

Run:  cd backend && uv run python -m pytest ../AI_Test_Plan/test_ai_layer.py -v
"""
import sys
from pathlib import Path

# make the backend package importable regardless of where pytest is invoked
BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

import pytest
from app.services.market_data.fetcher import DataFetcher
from app.services.indicators.featureEngine import FeatureEngine
from app.services.recommendation.engine import StockPredictor, PredictorConfig

TICKER = "AAPL"
PERIOD = "2y"


@pytest.fixture(scope="module")
def predictor():
    return StockPredictor()


@pytest.fixture(scope="module")
def ohlcv():
    return DataFetcher().fetch_historical(TICKER, period=PERIOD)


# TC-AI-01 -----------------------------------------------------------------
def test_datafetcher_returns_valid_ohlcv(ohlcv):
    """DataFetcher returns non-empty OHLCV with the required columns."""
    assert not ohlcv.empty
    for col in ("Open", "High", "Low", "Close", "Volume"):
        assert col in ohlcv.columns
    assert len(ohlcv) > 100


# TC-AI-02 -----------------------------------------------------------------
def test_featureengine_produces_indicators(ohlcv):
    """FeatureEngine adds technical indicators without dropping all rows."""
    feats = FeatureEngine().calculate_all_features(ohlcv)
    assert len(feats) > 0
    assert feats.shape[1] > ohlcv.shape[1]          # new indicator columns added
    assert not feats.isna().all(axis=0).any()       # no fully-empty column


# TC-AI-03 -----------------------------------------------------------------
def test_prepare_data_labels_are_binary(predictor):
    """Labels are strictly binary UP/DOWN after the +/-1% dead-band filter."""
    X, y = predictor.prepare_data(TICKER, PERIOD)
    assert set(y.unique()).issubset({0, 1})
    assert len(X) == len(y) and len(X) > 0
    assert X.shape[1] > 0                            # feature columns present


# TC-AI-04 -----------------------------------------------------------------
def test_predict_output_contract(predictor):
    """predict() returns a valid signal, confidence and normalised probabilities."""
    result = predictor.predict(TICKER)
    assert result["signal"] in {"BUY", "HOLD", "SELL"}
    assert 0.0 <= result["confidence"] <= 100.0
    total = result["probability_up"] + result["probability_down"]
    assert abs(total - 100.0) < 0.5                 # probabilities sum to ~100%


# TC-AI-05 -----------------------------------------------------------------
def test_walk_forward_metrics_valid(predictor):
    """Walk-forward evaluation returns 5 folds with in-range accuracy and log loss."""
    report = predictor.walk_forward_evaluate(TICKER, n_splits=5, period="5y")
    assert report.n_splits == 5
    assert len(report.accuracies) == 5
    assert all(0.0 <= a <= 1.0 for a in report.accuracies)
    assert report.mean_logloss > 0.0                # a real probabilistic loss


# TC-AI-06 -----------------------------------------------------------------
def test_backtest_report_contract(predictor):
    """Backtest returns all required metrics plus an equity curve and a benchmark."""
    bt = predictor.backtest(TICKER, period="5y").as_dict()
    for key in ("trades", "win_rate", "total_return_pct",
                "buy_hold_return_pct", "sharpe", "profit_factor", "equity_curve"):
        assert key in bt
    assert len(bt["equity_curve"]) > 0
    assert 0.0 <= bt["win_rate"] <= 1.0


# TC-AI-07 -----------------------------------------------------------------
def test_hold_band_configuration():
    """The live HOLD band is a valid sub-interval of [0, 1] around 0.5."""
    cfg = PredictorConfig()
    assert 0.0 < cfg.hold_lower < 0.5 < cfg.hold_upper < 1.0
