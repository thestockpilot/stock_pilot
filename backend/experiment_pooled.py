"""Experiment: does training one model on several tickers (pooled) beat a
single-ticker model?

For each ticker we build the stationary-feature dataset, split it chronologically
80:20 (no look-ahead), then compare:
  (A) single-ticker  - train on that ticker's 80%, test on its 20%
  (B) pooled         - train on ALL tickers' 80% combined, test on each 20%
"""
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, log_loss
from app.services.recommendation.engine import StockPredictor

logging.getLogger().setLevel(logging.WARNING)  # quiet the per-fetch logs

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
PERIOD = "5y"
TEST = 0.2

pred = StockPredictor()
data = {}
for t in TICKERS:
    X, y = pred.prepare_data(t, PERIOD)
    cut = int(len(X) * (1 - TEST))
    data[t] = {
        "Xtr": X.iloc[:cut], "ytr": y.iloc[:cut],
        "Xte": X.iloc[cut:], "yte": y.iloc[cut:],
    }
    print(f"{t}: {len(X)} rows  (train {cut}, test {len(X)-cut})")

# ---- (A) single-ticker baselines ----
print("\n== (A) single-ticker models ==")
single_acc = {}
for t in TICKERS:
    d = data[t]
    m = pred._make_model(scale_pos_weight=pred._class_ratio(d["ytr"]))
    m.fit(d["Xtr"], d["ytr"], eval_set=[(d["Xte"], d["yte"])], verbose=False)
    acc = accuracy_score(d["yte"], m.predict(d["Xte"]))
    single_acc[t] = acc
    print(f"  {t}: test accuracy = {acc:.4f}")
print(f"  MEAN single-ticker accuracy = {np.mean(list(single_acc.values())):.4f}")

# ---- (B) pooled model ----
print("\n== (B) pooled model (trained on all 5 tickers) ==")
Xtr_all = pd.concat([data[t]["Xtr"] for t in TICKERS])
ytr_all = pd.concat([data[t]["ytr"] for t in TICKERS])
Xte_all = pd.concat([data[t]["Xte"] for t in TICKERS])
yte_all = pd.concat([data[t]["yte"] for t in TICKERS])
print(f"  pooled train rows = {len(Xtr_all)}, pooled test rows = {len(Xte_all)}")

pm = pred._make_model(scale_pos_weight=pred._class_ratio(ytr_all))
pm.fit(Xtr_all, ytr_all, eval_set=[(Xte_all, yte_all)], verbose=False)

pooled_overall = accuracy_score(yte_all, pm.predict(Xte_all))
pooled_ll = log_loss(yte_all, pm.predict_proba(Xte_all)[:, 1], labels=[0, 1])
print(f"  pooled OVERALL test accuracy = {pooled_overall:.4f}  (logloss {pooled_ll:.4f})")

print("  pooled model tested on each ticker (vs its own single model):")
for t in TICKERS:
    d = data[t]
    acc = accuracy_score(d["yte"], pm.predict(d["Xte"]))
    delta = acc - single_acc[t]
    flag = "better" if delta > 0 else "worse "
    print(f"    {t}: pooled {acc:.4f}  vs single {single_acc[t]:.4f}  ({flag} {delta:+.4f})")
