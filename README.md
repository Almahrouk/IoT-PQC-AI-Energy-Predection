# IoT PQC AI Energy Prediction Framework

An energy evaluation framework for Post-Quantum Cryptographic (PQC) algorithms
deployed in IoT networks, combining simulation and machine learning.

## Total Energy Model

    Total Energy = Computation Energy (gem5) + Communication Energy (Cooja)

## Target Algorithms

Kyber-512/768/1024 · Dilithium-2/3/5 · FALCON-512/1024 · SPHINCS+-128/192/256

## Repository Structure

| Folder | Contents |
|--------|----------|
| cooja-simulation/ | Contiki-NG/Cooja firmware, .csc configs, experiment scripts |
| dataset/          | All experiment CSVs and master_dataset.csv (1,947 rows) |
| ml/               | ML pipeline scripts and baseline results |
| gem5-benchmarking/| gem5 ARM Cortex-M4 configs and benchmark setup |
| scripts/          | Experiment setup and reproduction scripts |
| legacy-data/      | Earlier PQC energy measurements |

## Reproducibility

    # Replicate all Cooja experiments
    bash cooja-simulation/scripts/run_all.sh

    # Run ML baseline
    python3 ml/train_baseline.py

## Status (May 2026)

- Complete: Cooja simulation pipeline (EXP01-EXP05)
- Complete: Dataset: 1,947 rows, 11 algorithms, 2 topologies, 3 payload sizes
- Complete: ML baseline: Random Forest, XGBoost, Gradient Boosting
- Upcoming: gem5 ARM Cortex-M4 benchmarking
- Upcoming: Radio energy integration (Cooja PowerTracker)
- Upcoming: Combined energy model + ML retrain

## Platform

AlmaLinux 10.1 · Contiki-NG + Cooja (Docker) · Python 3.12 · scikit-learn · XGBoost
