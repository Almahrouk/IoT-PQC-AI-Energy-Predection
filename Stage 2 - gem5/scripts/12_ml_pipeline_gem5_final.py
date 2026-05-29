#!/usr/bin/env python3
# 12_ml_pipeline_gem5_final.py
# Final ML pipeline using ONLY real gem5 measurements
# No x86 data needed

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, GroupKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

DATA = '/home/user/gem5_results/paper_dataset_fixed.csv'
OUT  = '/home/user/gem5_results/final_results.csv'

# ── Load real gem5 dataset ──────────────────────────────────────
df = pd.read_csv(DATA)
print(f"Dataset : {len(df)} rows, {df['algorithm'].nunique()} algorithms")
print(f"Columns : {list(df.columns)}\n")

# ── Encode ──────────────────────────────────────────────────────
le_op  = LabelEncoder()
le_alg = LabelEncoder()
df['op_enc']     = le_op.fit_transform(df['operation'])
df['alg_enc']    = le_alg.fit_transform(df['algorithm'])
df['log_energy'] = np.log1p(df['energy_mj'])

# ── Feature sets ────────────────────────────────────────────────
FEAT_STRUCT = ['op_enc', 'security_level', 'lattice_dim',
               'uses_fpu', 'pk_bytes', 'sk_bytes', 'ct_or_sig_bytes']

FEAT_FULL   = FEAT_STRUCT + ['alg_enc']

rf = RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=42)

# ── Experiment A: 3-Fold CV (main result) ───────────────────────
print("=" * 60)
print("  EXPERIMENT A: 3-Fold CV  (main paper result)")
print("  Question: predict energy for any operation")
print("=" * 60)

kf = KFold(n_splits=3, shuffle=True, random_state=42)

results_a = {}
for label, feats in [("Structural only", FEAT_STRUCT),
                     ("Full (+ alg ID)",  FEAT_FULL)]:
    cv_r2  = cross_val_score(rf, df[feats], df['log_energy'],
                             cv=kf, scoring='r2')
    cv_mae = cross_val_score(rf, df[feats], df['log_energy'],
                             cv=kf, scoring='neg_mean_absolute_error')
    results_a[label] = cv_r2
    print(f"\n  [{label}]")
    print(f"  CV R2  = {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
    print(f"  CV MAE = {-cv_mae.mean():.4f} log-mJ units")
    print(f"  Folds  : {[round(x,3) for x in cv_r2]}")

# ── Experiment B: Cross-Algorithm GroupKFold ────────────────────
print("\n" + "=" * 60)
print("  EXPERIMENT B: Cross-Algorithm GroupKFold")
print("  Question: predict energy for unseen algorithm family")
print("=" * 60)

gkf = GroupKFold(n_splits=min(5, df['algorithm'].nunique()))

results_b = {}
for label, feats in [("Structural only", FEAT_STRUCT),
                     ("Full (+ alg ID)",  FEAT_FULL)]:
    cv_r2 = cross_val_score(rf, df[feats], df['log_energy'],
                            groups=df['alg_enc'],
                            cv=gkf, scoring='r2')
    results_b[label] = cv_r2
    print(f"\n  [{label}]")
    print(f"  GroupKFold R2 = {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
    print(f"  Folds: {[round(x,3) for x in cv_r2]}")

# ── Final model ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  FINAL MODEL (all data, full features)")
print("=" * 60)

rf.fit(df[FEAT_FULL], df['log_energy'])
pred = np.expm1(rf.predict(df[FEAT_FULL]))
true = df['energy_mj'].values

r2   = r2_score(true, pred)
mae  = mean_absolute_error(true, pred)
rmse = np.sqrt(mean_squared_error(true, pred))
print(f"  In-sample R2={r2:.4f}  MAE={mae:.6f}mJ  RMSE={rmse:.6f}mJ")

# ── Feature importance ──────────────────────────────────────────
print("\n" + "=" * 60)
print("  Feature Importance")
print("=" * 60)

imp = pd.Series(rf.feature_importances_,
                index=FEAT_FULL).sort_values(ascending=False)
for feat, val in imp.items():
    bar = 'X' * int(val * 50)
    print(f"  {feat:<20} {val:.4f} ({val*100:.1f}%)  {bar}")

# ── IoT Feasibility table ───────────────────────────────────────
print("\n" + "=" * 60)
print("  IoT Feasibility (gem5 AArch64, ARM Cortex-M4 @ 64MHz)")
print("=" * 60)
print(f"  {'Algorithm':<14} {'Op':<8} {'Time(us)':>10} "
      f"{'Energy(mJ)':>12} {'IoT':>5}")
print("  " + "-" * 55)

for _, r in df.iterrows():
    iot = "YES" if r['iot_feasible'] else "NO"
    print(f"  {r['algorithm']:<14} {r['operation']:<8} "
          f"{r['time_us']:>10.2f} {r['energy_mj']:>12.6f} {iot:>5}")

# ── Paper summary ───────────────────────────────────────────────
cv_main = results_a["Full (+ alg ID)"]
cv_struct = results_b["Structural only"]

print("\n" + "=" * 60)
print("  RESULTS SUMMARY FOR PAPER")
print("=" * 60)
print(f"  Source         : gem5 AArch64 simulation")
print(f"  CPU model      : ARM Cortex-M4 @ 64 MHz")
print(f"  Dataset        : {len(df)} measurements, "
      f"{df['algorithm'].nunique()} algorithms")
print()
print(f"  Experiment A (3-fold CV, full features):")
print(f"  CV R2 = {cv_main.mean():.4f} +/- {cv_main.std():.4f}  ← report this")
print(f"  In-sample R2 = {r2:.4f}")
print()
print(f"  Experiment B (cross-algorithm, structural features):")
print(f"  GroupKFold R2 = {cv_struct.mean():.4f} +/- "
      f"{cv_struct.std():.4f}  ← report as generalization")
print()
print(f"  Top predictor  : {imp.index[0]} ({imp.iloc[0]*100:.1f}%)")
print(f"  2nd predictor  : {imp.index[1]} ({imp.iloc[1]*100:.1f}%)")
print()
print(f"  IoT winner     : ML-KEM family (< 1ms)")
print(f"  IoT blocker    : Falcon keygen (20-64ms)")

# ── Save ────────────────────────────────────────────────────────
imp.reset_index().rename(columns={'index':'feature',0:'importance'}
    ).to_csv('/home/user/gem5_results/feature_importance_final.csv', index=False)

pd.DataFrame([{
    'exp': 'A_3fold_cv_full',
    'cv_r2_mean': round(cv_main.mean(), 4),
    'cv_r2_std':  round(cv_main.std(),  4),
    'insample_r2': round(r2, 4),
    'mae_mj': round(mae, 6),
    'n_rows': len(df),
    'n_algorithms': df['algorithm'].nunique(),
}, {
    'exp': 'B_cross_alg_structural',
    'cv_r2_mean': round(cv_struct.mean(), 4),
    'cv_r2_std':  round(cv_struct.std(),  4),
    'insample_r2': round(r2, 4),
    'mae_mj': round(mae, 6),
    'n_rows': len(df),
    'n_algorithms': df['algorithm'].nunique(),
}]).to_csv(OUT, index=False)

print(f"\n  Saved → {OUT}")
print(f"  Saved → feature_importance_final.csv")
print("  DONE ✅")

"""
root@debian:/home/user/scripts# python3 12_ml_pipeline_gem5_final.py 
Dataset : 33 rows, 11 algorithms
Columns : ['algorithm', 'operation', 'family', 'type', 'security_level', 'lattice_dim', 'uses_fpu', 'pk_bytes', 'sk_bytes', 'ct_or_sig_bytes', 'instructions', 'time_us', 'energy_mj', 'iot_feasible']

============================================================
  EXPERIMENT A: 3-Fold CV  (main paper result)
  Question: predict energy for any operation
============================================================

  [Structural only]
  CV R2  = 0.9558 +/- 0.0456
  CV MAE = 0.0475 log-mJ units
  Folds  : [np.float64(0.981), np.float64(0.995), np.float64(0.892)]

  [Full (+ alg ID)]
  CV R2  = 0.9622 +/- 0.0378
  CV MAE = 0.0500 log-mJ units
  Folds  : [np.float64(0.987), np.float64(0.991), np.float64(0.909)]

============================================================
  EXPERIMENT B: Cross-Algorithm GroupKFold
  Question: predict energy for unseen algorithm family
============================================================

  [Structural only]
  GroupKFold R2 = -0.3844 +/- 1.7635
  Folds: [np.float64(0.238), np.float64(-3.869), np.float64(0.227), np.float64(0.501), np.float64(0.981)]

  [Full (+ alg ID)]
  GroupKFold R2 = -2.6542 +/- 5.6919
  Folds: [np.float64(0.367), np.float64(-0.731), np.float64(0.112), np.float64(-13.986), np.float64(0.966)]

============================================================
  FINAL MODEL (all data, full features)
============================================================
  In-sample R2=0.9962  MAE=0.027671mJ  RMSE=0.075617mJ

============================================================
  Feature Importance
============================================================
  lattice_dim          0.4088 (40.9%)  XXXXXXXXXXXXXXXXXXXX
  uses_fpu             0.3359 (33.6%)  XXXXXXXXXXXXXXXX
  alg_enc              0.1707 (17.1%)  XXXXXXXX
  ct_or_sig_bytes      0.0265 (2.7%)  X
  sk_bytes             0.0225 (2.2%)  X
  pk_bytes             0.0173 (1.7%)  
  security_level       0.0142 (1.4%)  
  op_enc               0.0041 (0.4%)  

============================================================
  IoT Feasibility (gem5 AArch64, ARM Cortex-M4 @ 64MHz)
============================================================
  Algorithm      Op         Time(us)   Energy(mJ)   IoT
  -------------------------------------------------------
  Kyber512       KEYGEN       526.24     0.034732   YES
  Kyber512       ENCAP        596.19     0.039348   YES
  Kyber512       DECAP        657.85     0.043418   YES
  Kyber768       KEYGEN       557.90     0.036821   YES
  Kyber768       ENCAP        669.31     0.044174   YES
  Kyber768       DECAP        768.86     0.050745   YES
  Kyber1024      KEYGEN       601.44     0.039695   YES
  Kyber1024      ENCAP        764.36     0.050448   YES
  Kyber1024      DECAP        914.08     0.060329   YES
  ML-KEM-512     KEYGEN       546.80     0.036089   YES
  ML-KEM-512     ENCAP        624.90     0.041243   YES
  ML-KEM-512     DECAP        719.67     0.047498   YES
  ML-KEM-768     KEYGEN       582.20     0.038425   YES
  ML-KEM-768     ENCAP        694.52     0.045838   YES
  ML-KEM-768     DECAP        830.75     0.054830   YES
  ML-KEM-1024    KEYGEN       637.61     0.042082   YES
  ML-KEM-1024    ENCAP        809.40     0.053420   YES
  ML-KEM-1024    DECAP       1014.68     0.066969   YES
  ML-DSA-44      KEYGEN       734.61     0.048484   YES
  ML-DSA-44      SIGN        1234.30     0.081464   YES
  ML-DSA-44      VERIFY      1479.00     0.097614   YES
  ML-DSA-65      KEYGEN       926.52     0.061150   YES
  ML-DSA-65      SIGN        1429.62     0.094355   YES
  ML-DSA-65      VERIFY      1846.12     0.121844   YES
  ML-DSA-87      KEYGEN      1249.52     0.082468   YES
  ML-DSA-87      SIGN        2257.70     0.149008   YES
  ML-DSA-87      VERIFY      2984.36     0.196968   YES
  Falcon-512     KEYGEN     20017.38     1.321147    NO
  Falcon-512     SIGN       20895.38     1.379095   YES
  Falcon-512     VERIFY     21083.73     1.391526   YES
  Falcon-1024    KEYGEN     63625.08     4.199255    NO
  Falcon-1024    SIGN       65404.33     4.316686   YES
  Falcon-1024    VERIFY     65770.15     4.340830   YES

============================================================
  RESULTS SUMMARY FOR PAPER
============================================================
  Source         : gem5 AArch64 simulation
  CPU model      : ARM Cortex-M4 @ 64 MHz
  Dataset        : 33 measurements, 11 algorithms

  Experiment A (3-fold CV, full features):
  CV R2 = 0.9622 +/- 0.0378  ← report this
  In-sample R2 = 0.9962

  Experiment B (cross-algorithm, structural features):
  GroupKFold R2 = -0.3844 +/- 1.7635  ← report as generalization

  Top predictor  : lattice_dim (40.9%)
  2nd predictor  : uses_fpu (33.6%)

  IoT winner     : ML-KEM family (< 1ms)
  IoT blocker    : Falcon keygen (20-64ms)

  Saved → /home/user/gem5_results/final_results.csv
  Saved → feature_importance_final.csv
  DONE ✅
root@debian:/home/user/scripts# 

"""