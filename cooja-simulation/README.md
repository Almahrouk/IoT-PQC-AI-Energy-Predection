# PQC-IoT Energy Research — Experiment Framework

## Structure
```
pqc-iot-sim/
├── code/                         # Shared firmware (C files)
│   ├── pqc-root-node.c
│   ├── pqc-leaf-node.c
│   └── pqc-timing-stubs.h        # (added in EXP02)
├── experiments/
│   ├── exp01_baseline/           # ✅ Done — basic RPL network
│   ├── exp02_pqc_stubs/          # Next — PQC timing injection
│   ├── exp03_star_topology/      # Star layout, 5-10 nodes
│   ├── exp04_mesh_topology/      # Mesh layout
│   └── exp05_multi_algorithm/    # All 4 PQC algorithms
├── scripts/
│   └── run_all.sh                # Run everything at once
└── results/
    ├── dataset/                  # Raw CSV outputs
    ├── plots/                    # Figures for paper
    └── ml_models/                # Saved ML models

## How to Replicate

### Run one experiment:
    bash experiments/exp01_baseline/run.sh

### Run all experiments:
    bash scripts/run_all.sh

### Requirements:
- Docker running: sudo systemctl start docker
- CNG_PATH set:  export CNG_PATH=$HOME/contiki-ng

## Experiment Status
| ID    | Name               | Status  |
|-------|--------------------|---------|
| EXP01 | Baseline RPL       | ✅ Done |
| EXP02 | PQC Timing Stubs   | ⏳ Next |
| EXP03 | Star Topology      | ⏳ Pending |
| EXP04 | Mesh Topology      | ⏳ Pending |
| EXP05 | Multi-Algorithm    | ⏳ Pending |
