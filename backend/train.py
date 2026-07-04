# train.py
"""
Run this script to train the XGBoost model and evaluate it.
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.recommendation.engine import StockPredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    print("\n" + "=" * 60)
    print("🚀 STOCKPILOT - XGBOOST MODEL TRAINING")
    print("=" * 60 + "\n")

    predictor = StockPredictor()
    predictor.train(ticker="AAPL", period="5y", test_size=0.2)

    print("\n" + "=" * 60)
    print("📊 WALK-FORWARD VALIDATION")
    print("=" * 60)

    report = predictor.walk_forward_evaluate("AAPL", n_splits=5, period="5y")
    print(f"\nWalk-forward results across {report.n_splits} folds:")
    for i, (acc, ll) in enumerate(zip(report.accuracies, report.loglosses), 1):
        print(f"  Fold {i}: accuracy={acc:.4f}  logloss={ll:.4f}")
    print(f"\nMean accuracy : {report.mean_accuracy:.4f} ± {report.std_accuracy:.4f}")
    print(f"Mean logloss  : {report.mean_logloss:.4f}")

    print("\n" + "=" * 60)
    print("📊 LIVE PREDICTION (TODAY)")
    print("=" * 60)

    result = predictor.predict("AAPL")
    print(f"Ticker    : {result['ticker']}")
    print(f"Signal    : {result['signal']} (Confidence: {result['confidence']}%)")
    print(f"Prob UP   : {result['probability_up']}%")
    print(f"Prob DOWN : {result['probability_down']}%")
    print(f"As of     : {result['as_of']}")

    print("\n✅ Done. Model is ready for the API.")


if __name__ == "__main__":
    main()