#!/usr/bin/env python3
"""
merge_dataset.py
Combines all pqc_energy_*.csv files into one master dataset.
"""

import os
import glob
import csv

BASE = "/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/01_cooja-simulation"

OUT = f"{BASE}/results/master_dataset.csv"

files = sorted(glob.glob(
    f"{BASE}/experiments/**/pqc_energy_*.csv",
    recursive=True
))

if not files:
    print("No dataset files found")
    exit(1)

all_rows = []
header = None

for fp in files:
    with open(fp) as f:
        reader = csv.DictReader(f)

        if header is None:
            header = reader.fieldnames

        count = 0
        for row in reader:
            all_rows.append(row)
            count += 1

    print(f"  Loaded {fp} ({len(all_rows)} total so far)")


# Create output directory
os.makedirs(os.path.dirname(OUT), exist_ok=True)


with open(OUT, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=header,
        extrasaction="ignore"
    )

    writer.writeheader()
    writer.writerows(all_rows)


print("")
print(f"Master dataset: {len(all_rows)} rows → {OUT}")
