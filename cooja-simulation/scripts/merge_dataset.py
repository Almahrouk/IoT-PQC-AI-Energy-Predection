#!/usr/bin/env python3
"""
merge_dataset.py
Combines all pqc_energy_*.csv files into one master dataset.

Usage:
    python3 merge_dataset.py
"""
import os, glob, csv

BASE    = os.path.expanduser("~/contiki-ng/examples/pqc-iot-sim")
DS_DIR  = f"{BASE}/results/dataset"
OUT     = f"{DS_DIR}/master_dataset.csv"

files = sorted(glob.glob(f"{DS_DIR}/pqc_energy_*.csv"))
if not files:
    print("No dataset files found in", DS_DIR)
    exit(1)

all_rows = []
header   = None
for fp in files:
    with open(fp) as f:
        reader = csv.DictReader(f)
        if header is None:
            header = reader.fieldnames
        for row in reader:
            all_rows.append(row)
    print(f"  Loaded {fp}  ({len(all_rows)} total so far)")

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_rows)

print(f"\nMaster dataset: {len(all_rows)} rows → {OUT}")
