#!/usr/bin/env python3
"""
=====================================================================
PQC-IoT Energy Research — Reproducible Experiment Framework Setup
=====================================================================
Run this ONCE on your machine to create the full directory structure
and all experiment files.

Usage:
    python3 setup_experiment_framework.py

Author: Generated for PQC-IoT Energy Research Project
Date:   May 2026
=====================================================================
"""

import os
import stat

BASE = os.path.expanduser("~/contiki-ng/examples/pqc-iot-sim")

# ─────────────────────────────────────────────
# 1. CREATE DIRECTORY STRUCTURE
# ─────────────────────────────────────────────
dirs = [
    "experiments/exp01_baseline/results",
    "experiments/exp02_pqc_stubs/results",
    "experiments/exp03_star_topology/results",
    "experiments/exp04_mesh_topology/results",
    "experiments/exp05_multi_algorithm/results",
    "code",
    "scripts",
    "results/dataset",
    "results/plots",
    "results/ml_models",
]
for d in dirs:
    os.makedirs(f"{BASE}/{d}", exist_ok=True)
print("✅ Directories created")


# ─────────────────────────────────────────────
# 2. EXP01 — BASELINE (root + leaf, no PQC yet)
# ─────────────────────────────────────────────
exp01_csc = '''<?xml version="1.0" encoding="UTF-8"?>
<simconf version="2022112801">
  <simulation>
    <title>EXP01 - Baseline RPL Network</title>
    <randomseed>42</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range>
      <interference_range>50.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events><logoutput>100000</logoutput></events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>pqcroot1</identifier>
      <description>PQC Root Node</description>
      <source>[CONFIG_DIR]/../../code/pqc-root-node.c</source>
      <commands>$(MAKE) -j$(CPUS) pqc-root-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>pqcleaf1</identifier>
      <description>PQC Leaf Node</description>
      <source>[CONFIG_DIR]/../../code/pqc-leaf-node.c</source>
      <commands>$(MAKE) -j$(CPUS) pqc-leaf-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
    </motetype>
    <mote>
      <motetype_identifier>pqcroot1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>60.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>1</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcleaf1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>90.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>2</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcleaf1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>30.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>3</id>
      </interface_config>
    </mote>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
TIMEOUT(120000);
log.testOK();
      </script>
      <active>true</active>
    </plugin_config>
    <width>600</width><height>300</height>
    <location_x>0</location_x><location_y>460</location_y>
  </plugin>
</simconf>'''

with open(f"{BASE}/experiments/exp01_baseline/exp01.csc", "w") as f:
    f.write(exp01_csc)


# ─────────────────────────────────────────────
# 3. EXP01 RUN SCRIPT
# ─────────────────────────────────────────────
exp01_run = '''#!/bin/bash
# =====================================================
# EXP01 — Baseline RPL Network (Root + 2 Leaf Nodes)
# No PQC yet — validates network formation
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="$HOME/contiki-ng"
CSC="$SCRIPT_DIR/exp01.csc"
RESULTS="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$RESULTS/run_${TIMESTAMP}.log"

echo "=============================="
echo " EXP01: Baseline RPL Network"
echo " CSC:     $CSC"
echo " Log:     $LOG"
echo "=============================="

mkdir -p "$RESULTS"

docker run --rm --privileged \\
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \\
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \\
  contiker/contiki-ng \\
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \\
    --args=\\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp01_baseline/exp01.csc\\"" \\
  2>&1 | tee "$LOG"

if grep -q "TEST OK" "$LOG"; then
    echo ""
    echo "✅ EXP01 PASSED — $(date)"
    echo "   Log saved: $LOG"
else
    echo ""
    echo "❌ EXP01 FAILED — check $LOG"
    exit 1
fi
'''

run_path = f"{BASE}/experiments/exp01_baseline/run.sh"
with open(run_path, "w") as f:
    f.write(exp01_run)
os.chmod(run_path, os.stat(run_path).st_mode | stat.S_IEXEC | stat.S_IXGRP)


# ─────────────────────────────────────────────
# 4. MASTER RUN-ALL SCRIPT
# ─────────────────────────────────────────────
run_all = '''#!/bin/bash
# =====================================================
# PQC-IoT Research — Run All Experiments in Sequence
# =====================================================
set -e
BASE="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

run_exp() {
    local name=$1
    local script=$2
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Running: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if bash "$script"; then
        echo "  ✅ $name: PASSED"
        ((PASS++))
    else
        echo "  ❌ $name: FAILED"
        ((FAIL++))
    fi
}

run_exp "EXP01 Baseline"        "$BASE/experiments/exp01_baseline/run.sh"
# Uncomment as you add experiments:
# run_exp "EXP02 PQC Stubs"     "$BASE/experiments/exp02_pqc_stubs/run.sh"
# run_exp "EXP03 Star Topology" "$BASE/experiments/exp03_star_topology/run.sh"
# run_exp "EXP04 Mesh Topology" "$BASE/experiments/exp04_mesh_topology/run.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SUMMARY: $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
[ $FAIL -eq 0 ] && exit 0 || exit 1
'''

run_all_path = f"{BASE}/scripts/run_all.sh"
with open(run_all_path, "w") as f:
    f.write(run_all)
os.chmod(run_all_path, os.stat(run_all_path).st_mode | stat.S_IEXEC | stat.S_IXGRP)


# ─────────────────────────────────────────────
# 5. README
# ─────────────────────────────────────────────
readme = '''# PQC-IoT Energy Research — Experiment Framework

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
'''

with open(f"{BASE}/README.md", "w") as f:
    f.write(readme)

print("✅ EXP01 simulation file created")
print("✅ EXP01 run.sh created")
print("✅ scripts/run_all.sh created")
print("✅ README.md created")
print("")
print("=" * 50)
print("  DONE — Framework ready!")
print("=" * 50)
print("")
print("Next command to run EXP01:")
print(f"  bash {BASE}/experiments/exp01_baseline/run.sh")
