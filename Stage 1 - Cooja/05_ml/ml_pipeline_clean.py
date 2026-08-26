import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv('/home/user/Desktop/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/01_cooja-simulation/results/master_dataset.csv')
print(f"Dataset: {len(df)} rows, {df['algorithm'].nunique()} algorithms")

# DROP leaked columns - these directly calculate the target
LEAK_COLS = ['cycles', 'time_us', 'energy_mj', 'node_id']
df = df.drop(columns=[c for c in LEAK_COLS if c in df.columns])
print(f"Dropped leaked columns: {LEAK_COLS}")
print(f"Remaining columns: {list(df.columns)}")

# Target
TARGET = 'energy_uj'
df['log_energy'] = np.log1p(df[TARGET])

# Encode categorical features
le_algo = LabelEncoder()
le_op   = LabelEncoder()
le_topo = LabelEncoder()
le_type = LabelEncoder()

df['algo_enc'] = le_algo.fit_transform(df['algorithm'])
df['op_enc']   = le_op.fit_transform(df['operation'])
df['topo_enc'] = le_topo.fit_transform(df['topology'])
df['type_enc'] = le_type.fit_transform(df['algo_type'])

# Features - NO leaked columns
FEATURES = ['algo_enc', 'op_enc', 'topo_enc', 'type_enc',
            'security_level', 'hop_count', 'payload_bytes']

X = df[FEATURES]
y = df['log_energy']

print(f"\nFeatures used: {FEATURES}")
print(f"Target: {TARGET} (log-transformed)")

# 5-Fold CV
kf = KFold(n_splits=5, shuffle=True, random_state=42)

print("\n" + "="*55)
print("  RANDOM FOREST — Clean (no leakage)")
print("="*55)
rf = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
cv_r2  = cross_val_score(rf, X, y, cv=kf, scoring='r2')
cv_mae = cross_val_score(rf, X, y, cv=kf, scoring='neg_mean_absolute_error')
print(f"  CV R2  = {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
print(f"  CV MAE = {-cv_mae.mean():.4f} log-uj units")
print(f"  Folds : {[round(x,3) for x in cv_r2]}")

rf.fit(X, y)
pred = np.expm1(rf.predict(X))
true = df[TARGET].values
r2   = r2_score(true, pred)
mae  = mean_absolute_error(true, pred)
rmse = np.sqrt(mean_squared_error(true, pred))
print(f"  In-sample R2={r2:.4f}  MAE={mae:.2f}uj  RMSE={rmse:.2f}uj")

print("\n" + "="*55)
print("  FEATURE IMPORTANCE")
print("="*55)
imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, val in imp.items():
    bar = 'X' * int(val * 50)
    print(f"  {feat:<20} {val:.4f} ({val*100:.1f}%)  {bar}")

print("\n" + "="*55)
print("  GRADIENT BOOSTING — Clean")
print("="*55)
gb = GradientBoostingRegressor(n_estimators=300, random_state=42)
cv_r2_gb = cross_val_score(gb, X, y, cv=kf, scoring='r2')
print(f"  CV R2  = {cv_r2_gb.mean():.4f} +/- {cv_r2_gb.std():.4f}")
print(f"  Folds : {[round(x,3) for x in cv_r2_gb]}")

print("\n" + "="*55)
print("  RESULTS SUMMARY")
print("="*55)
print(f"  Dataset rows     : {len(df)}")
print(f"  Algorithms       : {df['algorithm'].nunique()}")
print(f"  Features used    : {len(FEATURES)} (no leakage)")
print(f"  RF CV R2         : {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
print(f"  GB CV R2         : {cv_r2_gb.mean():.4f} +/- {cv_r2_gb.std():.4f}")
print(f"  Top predictor    : {imp.index[0]} ({imp.iloc[0]*100:.1f}%)")
print(f"  2nd predictor    : {imp.index[1]} ({imp.iloc[1]*100:.1f}%)")
print()
print("  NOTE: R2 < 1.0 is EXPECTED and CORRECT.")
print("  The model predicts from structure, not from formulas.")

imp.reset_index().rename(columns={'index':'feature', 0:'importance'}).to_csv(
    '/home/user/Desktop/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/05_ml/results/feature_importance_clean.csv',
    index=False)
print("\n  Saved feature_importance_clean.csv")
print("  DONE")
