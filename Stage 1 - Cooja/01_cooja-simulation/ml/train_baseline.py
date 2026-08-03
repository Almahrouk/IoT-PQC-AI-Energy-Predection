#!/usr/bin/env python3
"""
train_baseline.py
=================
Baseline ML pipeline for PQC energy prediction.

Input:  master_dataset.csv
Output: ml/results/baseline_results.txt
        ml/results/feature_importance.csv
        ml/results/predictions.csv

Models: Random Forest, XGBoost, Gradient Boosting
Target: energy_mj (total cryptographic computation energy)
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────
BASE = "/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/01_cooja-simulation"
DATA = f"{BASE}/results/master_dataset.csv"
OUT_DIR = f"{BASE}/ml/results"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv(DATA)
print(f"  {len(df)} rows, {df.shape[1]} columns")

# ── Features & target ─────────────────────────────────────────────
CATEGORICAL = [
    'algorithm',
    'algo_type',
    'operation',
    'topology'
]
NUMERICAL = [
    'security_level',
    'hop_count',
    'payload_bytes'
]
TARGET      = 'energy_mj'

# Encode categoricals
le = {}
df_enc = df.copy()
for col in CATEGORICAL:
    le[col] = LabelEncoder()
    df_enc[col] = le[col].fit_transform(df[col])

FEATURES = CATEGORICAL + NUMERICAL
X = df_enc[FEATURES]
y = df_enc[TARGET]

print(f"  Features: {FEATURES}")
print(f"  Target range: {y.min():.3f} mJ → {y.max():.1f} mJ")

# ── Train/test split ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTrain: {len(X_train)} rows | Test: {len(X_test)} rows")

# ── Model definitions ─────────────────────────────────────────────
models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    ),
    "XGBoost": xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0
    ),
}

# ── Train and evaluate ────────────────────────────────────────────
results = {}
all_lines = []

header = f"\n{'='*60}\n  PQC Energy Prediction — Baseline Results\n{'='*60}"
print(header)
all_lines.append(header)

best_model_name = None
best_r2 = -999

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    # 5-fold cross-validation on full dataset
    cv_r2 = cross_val_score(model, X, y, cv=5, scoring='r2', n_jobs=-1)

    results[name] = {
        'model': model,
        'y_pred': y_pred,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'cv_r2_mean': cv_r2.mean(),
        'cv_r2_std': cv_r2.std(),
    }

    if r2 > best_r2:
        best_r2 = r2
        best_model_name = name

    lines = [
        f"\n── {name} ──────────────────────────────",
        f"  RMSE:          {rmse:>10.4f} mJ",
        f"  MAE:           {mae:>10.4f} mJ",
        f"  R²:            {r2:>10.4f}",
        f"  CV R² (5-fold): {cv_r2.mean():.4f} ± {cv_r2.std():.4f}",
    ]
    for l in lines:
        print(l)
        all_lines.append(l)

# ── Best model summary ────────────────────────────────────────────
summary = [
    f"\n{'='*60}",
    f"  Best model: {best_model_name}  (R² = {best_r2:.4f})",
    f"{'='*60}",
]
for l in summary:
    print(l)
    all_lines.append(l)

# ── Feature importance (best model) ──────────────────────────────
best = results[best_model_name]['model']
if hasattr(best, 'feature_importances_'):
    fi = pd.DataFrame({
        'feature': FEATURES,
        'importance': best.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nFeature importances ({best_model_name}):")
    print(fi.to_string(index=False))
    all_lines.append(f"\nFeature importances ({best_model_name}):\n{fi.to_string(index=False)}")

    fi.to_csv(f"{OUT_DIR}/feature_importance.csv", index=False)

# ── Save predictions ──────────────────────────────────────────────
pred_df = X_test.copy()
pred_df['actual_mj'] = y_test.values
for name in models:
    pred_df[f'pred_{name.replace(" ","_")}_mj'] = results[name]['y_pred']
pred_df.to_csv(f"{OUT_DIR}/predictions.csv", index=False)

# ── Save results text ─────────────────────────────────────────────
with open(f"{OUT_DIR}/baseline_results.txt", "w") as f:
    f.write("\n".join(all_lines))

print(f"\nResults saved to {OUT_DIR}/")
print(f"  baseline_results.txt")
print(f"  feature_importance.csv")
print(f"  predictions.csv")
