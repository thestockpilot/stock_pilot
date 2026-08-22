"""
Model quality & robustness validation (TC-ML-01..05) with real PASS/FAIL logic.
Run:  cd backend && uv run python ../AI_Test_Plan/validate_model.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import numpy as np
import logging
logging.disable(logging.CRITICAL)

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss
from app.services.recommendation.engine import StockPredictor

# ==============  CONFIGURABLE THRESHOLDS  ==============
TH_ACC_BASELINE = 0.50          # must beat random guess
TH_LOG_LOSS_BASELINE = 0.693    # -ln(0.5), baseline for balanced binary
TH_STD_MAX = 0.15               # max allowed std dev across folds
TH_REPRO_TOL = 1e-6             # tolerance for reproducibility

# ==============  RUN TESTS  ==============
p = StockPredictor()
X, y = p.prepare_data("AAPL", "5y")

def walk_forward(X, yv):
    accuracies = []
    loglosses = []
    tscv = TimeSeriesSplit(5)
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = yv.iloc[train_idx], yv.iloc[test_idx]

        model = p._make_model(scale_pos_weight=p._class_ratio(y_train))
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        accuracies.append(accuracy_score(y_test, preds))
        loglosses.append(log_loss(y_test, probs, labels=[0, 1]))

    return np.array(accuracies), np.mean(loglosses)

print("Running 5-fold walk-forward validation (twice for reproducibility)...")
acc1, ll1 = walk_forward(X, y)
acc2, _  = walk_forward(X, y)

# Train on full data to check early stopping
p.train("AAPL", period="5y", save=False)
try:
    trees_used = p.model.get_booster().best_iteration
except Exception:
    trees_used = p.model.n_estimators

max_trees = p.config.max_estimators

# ==============  EVALUATE EACH TEST  ==============
results = {
    "tc1": acc1.mean() > TH_ACC_BASELINE,
    "tc2": ll1 < TH_LOG_LOSS_BASELINE,
    "tc3": acc1.std() < TH_STD_MAX,
    "tc4": trees_used < max_trees,
    "tc5": abs(acc1.mean() - acc2.mean()) < TH_REPRO_TOL,
}
all_pass = all(results.values())

# ==============  PRINT REPORT  ==============
print("=" * 58)
print("  MODEL QUALITY & ROBUSTNESS  (AAPL, 5y, 5-fold walk-forward)")
print("=" * 58)

print(f"  TC-ML-01  Beats random baseline    "
      f"accuracy {acc1.mean():.4f} > {TH_ACC_BASELINE}      "
      f"{'PASS' if results['tc1'] else 'FAIL'}")

print(f"  TC-ML-02  Probability calibration   "
      f"log loss {ll1:.4f} < {TH_LOG_LOSS_BASELINE}     "
      f"{'PASS' if results['tc2'] else 'FAIL'}")

print(f"  TC-ML-03  Cross-validation stable   "
      f"std {acc1.std():.4f} < {TH_STD_MAX}      "
      f"{'PASS' if results['tc3'] else 'FAIL'}")

print(f"  TC-ML-04  No overfitting            "
      f"{trees_used} of {max_trees} trees (early stop)  "
      f"{'PASS' if results['tc4'] else 'FAIL'}")

print(f"  TC-ML-05  Reproducible              "
      f"run1 {acc1.mean():.4f} = run2 {acc2.mean():.4f}   "
      f"{'PASS' if results['tc5'] else 'FAIL'}")

print("=" * 58)

if all_pass:
    print("  ✅ All model-quality checks PASSED.")
    sys.exit(0)
else:
    print("  ❌ Some model-quality checks FAILED. Review metrics above.")
    sys.exit(1)