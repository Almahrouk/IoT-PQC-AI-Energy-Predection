#!/usr/bin/env python3
"""
=======================================================================
PQC Energy Analysis — All Uploaded Experiment Files
=======================================================================
Files analysed:
  pqc_energy_exp02.csv                  — baseline star, payload=100
  pqc_energy_exp03_star_topology...csv  — expanded star, payload=100
  pqc_energy_exp04_mesh_topology...csv  — chain topology, payload=100
  pqc_energy_exp05_chain_p50/100/200    — payload variation (chain)
  pqc_energy_exp05_star_p50/100/200     — payload variation (star)
  master_dataset.csv                    — combined master

Run:
    python3 pqc_analysis.py
=======================================================================
"""

import pandas as pd
import numpy as np
from hashlib import md5

# ── File registry ────────────────────────────────────────────────────
FILES = {
    "exp02":            "pqc_energy_exp02.csv",
    "exp03_star":       "pqc_energy_exp03_star_topology_20260515_100643.csv",
    "exp04_chain":      "pqc_energy_exp04_mesh_topology_20260515_101010.csv",
    "exp05_chain_p50":  "pqc_energy_exp05_chain_p50.csv",
    "exp05_chain_p100": "pqc_energy_exp05_chain_p100.csv",
    "exp05_chain_p200": "pqc_energy_exp05_chain_p200.csv",
    "exp05_star_p50":   "pqc_energy_exp05_star_p50.csv",
    "exp05_star_p100":  "pqc_energy_exp05_star_p100.csv",
    "exp05_star_p200":  "pqc_energy_exp05_star_p200.csv",
    "master":           "master_dataset.csv",
}

# ── Load ─────────────────────────────────────────────────────────────
dfs = {}
for tag, fname in FILES.items():
    dfs[tag] = pd.read_csv(fname)

master = dfs["master"]

# =======================================================================
# SECTION 1 — Dataset inventory
# =======================================================================
print("=" * 70)
print("  SECTION 1 — Dataset Inventory")
print("=" * 70)
for tag, df in dfs.items():
    h = md5(df[["algorithm","operation","energy_mj","cycles"]]
            .to_csv(index=False).encode()).hexdigest()[:8]
    print(f"  {tag:25s}  rows={len(df):4d}  "
          f"topo={df.topology.unique().tolist()}  "
          f"payloads={sorted(df.payload_bytes.unique())}  "
          f"hash={h}")

# =======================================================================
# SECTION 2 — Data quality / duplication flags
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 2 — Data Quality Checks")
print("=" * 70)

# (a) Duplicate detection among exp05 variants
hashes = {}
for tag in ["exp05_chain_p50","exp05_chain_p100","exp05_chain_p200",
            "exp05_star_p50","exp05_star_p100","exp05_star_p200"]:
    h = md5(dfs[tag][["algorithm","operation","energy_mj","cycles"]]
            .to_csv(index=False).encode()).hexdigest()[:8]
    hashes[tag] = h

chain_hashes = set(v for k, v in hashes.items() if "chain" in k)
star_hashes  = set(v for k, v in hashes.items() if "star"  in k)
print(f"  exp05 chain variants (p50/p100/p200) — unique content hashes: "
      f"{len(chain_hashes)} — {'⚠ IDENTICAL FILES' if len(chain_hashes)==1 else 'distinct'}")
print(f"  exp05 star  variants (p50/p100/p200) — unique content hashes: "
      f"{len(star_hashes)}  — {'⚠ IDENTICAL FILES' if len(star_hashes)==1 else 'distinct'}")

# (b) Payload_bytes vs energy — does payload actually change energy?
print("\n  Payload bytes vs mean energy (master):")
pay_tbl = master.groupby("payload_bytes")["energy_mj"].mean()
for p, v in pay_tbl.items():
    print(f"    payload={p:>3d}  mean_energy={v:.4f} mJ")
all_same = pay_tbl.std() < 0.001
print(f"  → Payload has {'NO' if all_same else 'A'} effect on energy "
      f"({'payload column not yet wired into simulation' if all_same else 'real effect detected'})")

# (c) Topology vs energy
print("\n  Topology vs mean energy (master):")
topo_tbl = master.groupby("topology")["energy_mj"].mean()
for t, v in topo_tbl.items():
    print(f"    topology={t:8s}  mean_energy={v:.4f} mJ")
topo_same = topo_tbl.std() < 0.001
print(f"  → Topology has {'NO' if topo_same else 'A'} effect on energy "
      f"({'topology column not yet wired in' if topo_same else 'real effect detected'})")

# (d) Missing values
nulls = master.isnull().sum().sum()
print(f"\n  Missing values in master: {nulls} — {'clean' if nulls==0 else 'NEEDS CLEANING'}")

# =======================================================================
# SECTION 3 — Algorithm energy breakdown
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 3 — Algorithm Energy Breakdown (master)")
print("=" * 70)

agg = (master.groupby(["algorithm","algo_type"])["energy_mj"]
       .agg(["mean","std","min","max"])
       .sort_values("mean"))
print(f"\n  {'Algorithm':12s}  {'Type':4s}  {'Mean(mJ)':>9}  "
      f"{'Std':>8}  {'Min':>8}  {'Max':>9}")
print("  " + "-"*60)
for (alg, typ), row in agg.iterrows():
    print(f"  {alg:12s}  {typ:4s}  {row['mean']:9.3f}  "
          f"{row['std']:8.3f}  {row['min']:8.3f}  {row['max']:9.3f}")

# =======================================================================
# SECTION 4 — Operation breakdown
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 4 — Energy by Operation (mean mJ)")
print("=" * 70)

ops_tbl = (master.groupby(["algorithm","operation"])["energy_mj"]
           .mean().unstack("operation"))
print(f"\n  {'Algorithm':12s}  {'KEYGEN':>10}  {'ENCAP_SIGN':>11}  {'DECAP_VERIFY':>12}")
print("  " + "-"*50)
for alg, row in ops_tbl.sort_values("KEYGEN").iterrows():
    print(f"  {alg:12s}  {row.get('KEYGEN',float('nan')):10.3f}  "
          f"{row.get('ENCAP_SIGN',float('nan')):11.3f}  "
          f"{row.get('DECAP_VERIFY',float('nan')):12.3f}")

# Notable outliers
print("\n  Key outliers:")
print(f"    SPHINCS256 ENCAP_SIGN = "
      f"{ops_tbl.loc['SPHINCS256','ENCAP_SIGN']:.1f} mJ "
      f"({ops_tbl.loc['SPHINCS256','ENCAP_SIGN'] / ops_tbl.loc['KYBER512','ENCAP_SIGN']:.0f}× KYBER512)")
print(f"    FALCON1024 KEYGEN    = "
      f"{ops_tbl.loc['FALCON1024','KEYGEN']:.1f} mJ "
      f"({ops_tbl.loc['FALCON1024','KEYGEN'] / ops_tbl.loc['KYBER512','KEYGEN']:.0f}× KYBER512)")

# =======================================================================
# SECTION 5 — Experiment progression (what each exp added)
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 5 — Experiment Progression")
print("=" * 70)

descriptions = {
    "exp02":            "Baseline — 11 algs × 3 ops × 3 nodes, star, p=100",
    "exp03_star":       "Expanded star — more nodes (2→8), star, p=100",
    "exp04_chain":      "Chain topology added — 2-hop, p=100",
    "exp05_chain_p50":  "Payload 50 trial (chain) — ⚠ same as p100 in content",
    "exp05_chain_p100": "Payload 100 trial (chain) — ⚠ same as p50 in content",
    "exp05_chain_p200": "Payload 200 trial (chain) — ⚠ same as p50 in content",
    "exp05_star_p50":   "Payload 50 trial (star)  — ⚠ same as p100 in content",
    "exp05_star_p100":  "Payload 100 trial (star)  — ⚠ same as p50 in content",
    "exp05_star_p200":  "Payload 200 trial (star)  — ⚠ same as p50 in content",
    "master":           "Combined master — star+chain, p=50/100/200, 11 algs",
}
for tag, desc in descriptions.items():
    df = dfs[tag]
    print(f"  {tag:25s}  {len(df):4d} rows  {desc}")

# =======================================================================
# SECTION 6 — Node / topology structure
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 6 — Network Structure in Master")
print("=" * 70)

print(f"\n  Topology distribution: {master.topology.value_counts().to_dict()}")
print(f"  Hop counts: {dict(master.groupby('topology')['hop_count'].first())}")
print(f"  Node count: {master.node_id.nunique()} unique nodes")
print(f"  Node IDs: {sorted(master.node_id.unique())}")
node_topo = master.groupby(["topology","node_id"]).size().unstack(fill_value=0)
print(f"\n  Nodes per topology:\n{node_topo.to_string()}")

# =======================================================================
# SECTION 7 — IoT feasibility verdict
# =======================================================================
print("\n" + "=" * 70)
print("  SECTION 7 — IoT Feasibility (Cooja simulation data)")
print("=" * 70)

THRESHOLD_MJ = 50.0
print(f"\n  Threshold: {THRESHOLD_MJ} mJ total (all 3 ops combined)")
totals = master.groupby("algorithm")["energy_mj"].sum() / master.groupby("algorithm").size() * 3
# more correct: mean per op × 3
mean3 = master.groupby(["algorithm","operation"])["energy_mj"].mean().groupby("algorithm").sum()
print(f"\n  {'Algorithm':12s}  {'Total3Op(mJ)':>13}  {'IoT?':>8}")
print("  " + "-"*38)
for alg, val in mean3.sort_values().items():
    verdict = "✅ feasible" if val < THRESHOLD_MJ else "❌ too costly"
    print(f"  {alg:12s}  {val:13.3f}  {verdict}")

print("\n  DONE ✅")
