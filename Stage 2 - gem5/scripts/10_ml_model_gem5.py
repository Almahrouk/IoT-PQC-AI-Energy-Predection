import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

df = pd.read_csv('/home/user/gem5_results/paper_dataset_fixed.csv')
print(f"Dataset: {len(df)} rows, {df['algorithm'].nunique()} algorithms")
print(f"Columns: {list(df.columns)}\n")

# Encode
le_op  = LabelEncoder()
le_alg = LabelEncoder()
df['op_enc']  = le_op.fit_transform(df['operation'])
df['alg_enc'] = le_alg.fit_transform(df['algorithm'])
df['log_energy'] = np.log1p(df['energy_mj'])

FEATURES = ['alg_enc', 'op_enc', 'security_level', 'lattice_dim',
            'uses_fpu', 'pk_bytes', 'sk_bytes', 'ct_or_sig_bytes']

X = df[FEATURES]
y = df['log_energy']

rf = RandomForestRegressor(n_estimators=300, random_state=42)

# 3-fold CV (appropriate for 33 rows)
print("=" * 50)
print("  3-Fold CV (main result)")
print("=" * 50)
kf = KFold(n_splits=3, shuffle=True, random_state=42)
cv_r2  = cross_val_score(rf, X, y, cv=kf, scoring='r2')
cv_mae = cross_val_score(rf, X, y, cv=kf, scoring='neg_mean_absolute_error')
print(f"  R2  = {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
print(f"  MAE = {-cv_mae.mean():.4f} log-mJ units")
print(f"  Folds: {[round(x,3) for x in cv_r2]}")

# LeaveOneOut CV (most honest for small datasets)
print("\n" + "=" * 50)
print("  LeaveOneOut CV (honest small-dataset estimate)")
print("=" * 50)
loo = LeaveOneOut()
loo_r2 = cross_val_score(rf, X, y, cv=loo, scoring='r2')
print(f"  LOO R2 = {loo_r2.mean():.4f} +/- {loo_r2.std():.4f}")

# Final model
print("\n" + "=" * 50)
print("  Final Model (in-sample)")
print("=" * 50)
rf.fit(X, y)
pred = np.expm1(rf.predict(X))
true = df['energy_mj'].values
r2   = r2_score(true, pred)
mae  = mean_absolute_error(true, pred)
rmse = np.sqrt(mean_squared_error(true, pred))
print(f"  R2={r2:.4f}  MAE={mae:.6f}mJ  RMSE={rmse:.6f}mJ")

# Feature importance
print("\n" + "=" * 50)
print("  Feature Importance")
print("=" * 50)
imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, val in imp.items():
    bar = 'X' * int(val * 40)
    print(f"  {feat:<20} {val:.4f} ({val*100:.1f}%)  {bar}")

# IoT feasibility summary
print("\n" + "=" * 50)
print("  IoT Feasibility Summary")
print("=" * 50)
print(f"  {'Algorithm':<14} {'Op':<8} {'Time(us)':>12} {'Energy(mJ)':>12} {'IoT':>5}")
print("  " + "-" * 55)
for _, r in df.iterrows():
    iot = "YES" if r['iot_feasible'] else "NO"
    print(f"  {r['algorithm']:<14} {r['operation']:<8} "
          f"{r['time_us']:>12.2f} {r['energy_mj']:>12.6f} {iot:>5}")

# Save
imp.to_csv('/home/user/gem5_results/feature_importance_gem5.csv')
print(f"\nSaved feature_importance_gem5.csv")
print("DONE")

"""
root@debian:/home/user/scripts# python3 10_ml_model_gem5.py 
Dataset: 33 rows, 11 algorithms
Columns: ['algorithm', 'operation', 'family', 'type', 'security_level', 'lattice_dim', 'uses_fpu', 'pk_bytes', 'sk_bytes', 'ct_or_sig_bytes', 'instructions', 'time_us', 'energy_mj', 'iot_feasible']

==================================================
  3-Fold CV (main result)
==================================================
  R2  = 0.9580 +/- 0.0355
  MAE = 0.0531 log-mJ units
  Folds: [np.float64(0.984), np.float64(0.982), np.float64(0.908)]

==================================================
  Final Model (in-sample)
==================================================
  R2=0.9954  MAE=0.030113mJ  RMSE=0.083909mJ

==================================================
  Feature Importance
==================================================
  lattice_dim          0.3744 (37.4%)  XXXXXXXXXXXXXX
  uses_fpu             0.3261 (32.6%)  XXXXXXXXXXXXX
  alg_enc              0.2096 (21.0%)  XXXXXXXX
  ct_or_sig_bytes      0.0306 (3.1%)  X
  sk_bytes             0.0237 (2.4%)  
  security_level       0.0171 (1.7%)  
  pk_bytes             0.0138 (1.4%)  
  op_enc               0.0047 (0.5%)  

==================================================
  IoT Feasibility Summary
==================================================
  Algorithm      Op           Time(us)   Energy(mJ)   IoT
  -------------------------------------------------------
  Kyber512       KEYGEN         526.24     0.034732   YES
  Kyber512       ENCAP          596.19     0.039348   YES
  Kyber512       DECAP          657.85     0.043418   YES
  Kyber768       KEYGEN         557.90     0.036821   YES
  Kyber768       ENCAP          669.31     0.044174   YES
  Kyber768       DECAP          768.86     0.050745   YES
  Kyber1024      KEYGEN         601.44     0.039695   YES
  Kyber1024      ENCAP          764.36     0.050448   YES
  Kyber1024      DECAP          914.08     0.060329   YES
  ML-KEM-512     KEYGEN         546.80     0.036089   YES
  ML-KEM-512     ENCAP          624.90     0.041243   YES
  ML-KEM-512     DECAP          719.67     0.047498   YES
  ML-KEM-768     KEYGEN         582.20     0.038425   YES
  ML-KEM-768     ENCAP          694.52     0.045838   YES
  ML-KEM-768     DECAP          830.75     0.054830   YES
  ML-KEM-1024    KEYGEN         637.61     0.042082   YES
  ML-KEM-1024    ENCAP          809.40     0.053420   YES
  ML-KEM-1024    DECAP         1014.68     0.066969   YES
  ML-DSA-44      KEYGEN         734.61     0.048484   YES
  ML-DSA-44      SIGN          1234.30     0.081464   YES
  ML-DSA-44      VERIFY        1479.00     0.097614   YES
  ML-DSA-65      KEYGEN         926.52     0.061150   YES
  ML-DSA-65      SIGN          1429.62     0.094355   YES
  ML-DSA-65      VERIFY        1846.12     0.121844   YES
  ML-DSA-87      KEYGEN        1249.52     0.082468   YES
  ML-DSA-87      SIGN          2257.70     0.149008   YES
  ML-DSA-87      VERIFY        2984.36     0.196968   YES
  Falcon-512     KEYGEN       20017.38     1.321147    NO
  Falcon-512     SIGN         20895.38     1.379095   YES
  Falcon-512     VERIFY       21083.73     1.391526   YES
  Falcon-1024    KEYGEN       63625.08     4.199255    NO
  Falcon-1024    SIGN         65404.33     4.316686   YES
  Falcon-1024    VERIFY       65770.15     4.340830   YES

Saved feature_importance_gem5.csv
DONE
root@debian:/home/user/scripts# 
"""