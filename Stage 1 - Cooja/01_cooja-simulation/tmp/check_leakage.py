import pandas as pd
import numpy as np

# Check the main dataset
df = pd.read_csv('/home/user/Desktop/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/01_cooja-simulation/results/master_dataset.csv')

print("=== COLUMNS ===")
print(df.columns.tolist())
print()

print("=== SHAPE ===")
print(df.shape)
print()

print("=== FIRST 3 ROWS ===")
print(df.head(3).to_string())
print()

print("=== DATA TYPES ===")
print(df.dtypes)
print()

# Find target column
target_candidates = [c for c in df.columns if 'energy' in c.lower()]
print(f"=== TARGET CANDIDATES: {target_candidates} ===")
print()

if target_candidates:
    target = target_candidates[0]
    numeric = df.select_dtypes(include=[np.number])
    if target in numeric.columns:
        corr = numeric.corrwith(numeric[target]).abs().sort_values(ascending=False)
        print(f"=== CORRELATION WITH {target} ===")
        print(corr)
