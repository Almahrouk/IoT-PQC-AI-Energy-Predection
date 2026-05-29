#!/usr/bin/env python3
"""
=======================================================================
PQC x86 Real-Measurement Analysis
Files:  pqc_energy_data.csv   — 100-run averaged benchmark (10 algs)
        final_dataset.csv     — 20 individual runs × 10 algs
        full_dataset.csv      — identical to final_dataset (no header)
        pqc_energy_measure.c  — the C program that produced the data
=======================================================================
Run:  python3 pqc_x86_analysis.py
=======================================================================
"""
import pandas as pd, numpy as np
from hashlib import md5

# ── Load ─────────────────────────────────────────────────────────────
pqc   = pd.read_csv("pqc_energy_data.csv")
final = pd.read_csv("final_dataset.csv")
full  = pd.read_csv("full_dataset.csv", header=None,
                    names=['run','algorithm','type','op1_ms','op2_ms',
                           'op3_ms','pk_bytes','sk_bytes','ct_or_sig_bytes'])

# ═══════════════════════════════════════════════════════════════════
# SECTION 1  — File relationship
# ═══════════════════════════════════════════════════════════════════
print("=" * 65)
print("  SECTION 1 — File Relationship")
print("=" * 65)
hf = md5(final.to_csv(index=False).encode()).hexdigest()[:8]
hx = md5(full.to_csv(index=False).encode()).hexdigest()[:8]
print(f"\n  pqc_energy_data.csv : {len(pqc):4d} rows — 100-run AVERAGED result per alg")
print(f"  final_dataset.csv   : {len(final):4d} rows — 20 individual timed runs")
print(f"  full_dataset.csv    : {len(full):4d} rows — same as final (no CSV header)")
print(f"\n  final == full  →  {hf == hx}  (content hash match: {hf})")
print(f"\n  Source program: pqc_energy_measure.c")
print(f"    Benchmarks 100 runs internally, saves the MEAN to pqc_energy_data.csv")
print(f"    final_dataset records 20 separate executions of that program")

# ═══════════════════════════════════════════════════════════════════
# SECTION 2  — SPHINCS+ gap
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 2 — Missing Algorithms (SPHINCS+)")
print("=" * 65)
c_targets = ['Kyber512','Kyber768','Kyber1024','ML-KEM-512','ML-KEM-768',
             'ML-KEM-1024','Falcon-512','Falcon-1024','ML-DSA-44','ML-DSA-65',
             'SPHINCS+-SHA2-128f','SPHINCS+-SHA2-256f']
present = list(pqc.algorithm)
missing = [a for a in c_targets if a not in present]
print(f"\n  Algorithms targeted in .c : {len(c_targets)}")
print(f"  Algorithms in CSV output  : {len(present)}")
print(f"  Missing                   : {missing}")
print(f"  Reason: liboqs build did not expose SPHINCS+ headers — skipped at runtime")

# ═══════════════════════════════════════════════════════════════════
# SECTION 3  — 100-run mean benchmark (pqc_energy_data)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 3 — 100-Run Mean Benchmark (pqc_energy_data.csv)")
print("=" * 65)
pqc['total_ms'] = pqc.op1_ms + pqc.op2_ms + pqc.op3_ms
pqc['total_bytes'] = pqc.pk_bytes + pqc.sk_bytes + pqc.ct_or_sig_bytes

print(f"\n  {'Algorithm':15s}  {'Type':4}  "
      f"{'Keygen(ms)':>11}  {'Op2(ms)':>9}  {'Op3(ms)':>9}  "
      f"{'Total(ms)':>10}  {'TotalKB':>8}")
print("  " + "-"*75)
for _, r in pqc.sort_values('total_ms').iterrows():
    print(f"  {r.algorithm:15s}  {r.type:4}  "
          f"{r.op1_ms:11.4f}  {r.op2_ms:9.4f}  {r.op3_ms:9.4f}  "
          f"{r.total_ms:10.4f}  {r.total_bytes/1024:8.2f}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 4  — Run variance (final_dataset, 20 runs)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 4 — Keygen Variance Across 20 Runs (final_dataset.csv)")
print("=" * 65)
cv_tbl = final.groupby('algorithm')['op1_ms'].agg(['mean','std','min','max'])
cv_tbl['cv_pct'] = (cv_tbl['std'] / cv_tbl['mean'] * 100).round(1)
cv_tbl = cv_tbl.sort_values('mean')
print(f"\n  {'Algorithm':15s}  {'Mean(ms)':>9}  {'Std':>8}  "
      f"{'Min':>8}  {'Max':>8}  {'CV%':>6}  {'Stability':>10}")
print("  " + "-"*72)
for alg, row in cv_tbl.iterrows():
    stab = "stable" if row.cv_pct < 20 else ("variable" if row.cv_pct < 40 else "HIGH VAR")
    print(f"  {alg:15s}  {row['mean']:9.4f}  {row['std']:8.4f}  "
          f"{row['min']:8.4f}  {row['max']:8.4f}  {row.cv_pct:6.1f}%  {stab:>10}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 5  — Kyber vs ML-KEM (same algorithm, different naming)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 5 — Kyber vs ML-KEM Comparison")
print("=" * 65)
pairs = [('Kyber512','ML-KEM-512'),('Kyber768','ML-KEM-768'),('Kyber1024','ML-KEM-1024')]
print(f"\n  {'Pair':>22s}  {'Kyber kg(ms)':>13}  {'ML-KEM kg(ms)':>14}  {'Faster':>10}")
print("  " + "-"*68)
for k, m in pairs:
    kg_k = pqc[pqc.algorithm==k]['op1_ms'].values[0]
    kg_m = pqc[pqc.algorithm==m]['op1_ms'].values[0]
    faster = f"ML-KEM {kg_k/kg_m:.1f}x" if kg_m < kg_k else f"Kyber {kg_m/kg_k:.1f}x"
    print(f"  {k:>10s} vs {m:10s}  {kg_k:13.4f}  {kg_m:14.4f}  {faster:>10}")
print("\n  Note: ML-KEM is the NIST-standardised rename of Kyber.")
print("  Performance differences reflect different run conditions, not algorithm changes.")

# ═══════════════════════════════════════════════════════════════════
# SECTION 6  — Sign/Verify asymmetry
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 6 — Sign vs Verify Ratio (SIG algorithms)")
print("=" * 65)
sigs = final[final.type=='SIG'].groupby('algorithm')[['op2_ms','op3_ms']].mean()
sigs['ratio'] = (sigs.op2_ms / sigs.op3_ms).round(1)
print(f"\n  {'Algorithm':15s}  {'Sign(ms)':>9}  {'Verify(ms)':>11}  {'Sign/Verify':>12}")
print("  " + "-"*52)
for alg, row in sigs.sort_values('ratio', ascending=False).iterrows():
    print(f"  {alg:15s}  {row.op2_ms:9.4f}  {row.op3_ms:11.4f}  {row.ratio:12.1f}x")
print("\n  Falcon sign is ~5x slower than verify — unusual for SIGs.")
print("  ML-DSA sign is ~3x slower than verify — more typical.")

# ═══════════════════════════════════════════════════════════════════
# SECTION 7  — ARM Cortex-M4 energy estimate
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 7 — ARM Cortex-M4 Estimated Energy (×55 scale, 80mW)")
print("=" * 65)
ARM_SCALE = 55.0
ARM_POWER_MW = 80.0
print(f"\n  Assumptions: ARM/x86 speed ratio = {ARM_SCALE}×, "
      f"active power = {ARM_POWER_MW} mW (64MHz, 1.25mW/MHz)")
print(f"\n  {'Algorithm':15s}  {'x86 total(ms)':>14}  "
      f"{'ARM est(ms)':>12}  {'ARM energy(mJ)':>15}  {'IoT <50mJ':>9}")
print("  " + "-"*72)
for _, r in pqc.sort_values('total_ms').iterrows():
    arm_ms = r.total_ms * ARM_SCALE
    arm_mj = arm_ms * ARM_POWER_MW / 1000
    iot    = "✅" if arm_mj < 50 else "❌"
    print(f"  {r.algorithm:15s}  {r.total_ms:14.4f}  "
          f"{arm_ms:12.2f}  {arm_mj:15.3f}  {iot:>9}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 8  — Key size analysis
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 8 — Key & Signature Sizes")
print("=" * 65)
pqc2 = pqc.sort_values('total_bytes').copy()
print(f"\n  {'Algorithm':15s}  {'Type':4}  "
      f"{'pk(B)':>7}  {'sk(B)':>7}  {'ct/sig(B)':>10}  {'total(B)':>9}")
print("  " + "-"*60)
for _, r in pqc2.iterrows():
    print(f"  {r.algorithm:15s}  {r.type:4}  "
          f"{r.pk_bytes:7}  {r.sk_bytes:7}  {r.ct_or_sig_bytes:10}  {r.total_bytes:9}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 9  — C code audit highlights
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  SECTION 9 — C Source Code Audit (pqc_energy_measure.c)")
print("=" * 65)
print("""
  ✅ Correct: uses clock() for timing, loops 100 iterations per algorithm
  ✅ Correct: averages timing across runs before saving to CSV
  ✅ Correct: frees all malloc'd buffers and OQS objects
  ✅ Correct: tests KEM and SIG operations separately

  ⚠ clock() measures CPU time, not wall time — fine for benchmarking
    but will differ from cycle-counter approaches
  ⚠ SPHINCS+ test_sig("SPHINCS+-SHA2-128f-simple") will silently skip
    via the if(!sig) check — no CSV row is written, no error to user
  ⚠ msg[64] is fixed zeros (0xAB) for all signature tests — not
    representative of real varied messages, but fine for timing
  ⚠ No warm-up run before timing — first iteration may include cache
    cold-start overhead (most visible in Kyber512 CV=48%)
""")

print("  DONE ✅")
