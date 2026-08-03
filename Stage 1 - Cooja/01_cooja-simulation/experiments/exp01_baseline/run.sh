#!/bin/bash
# =====================================================
# EXP01 — Baseline RPL Network (Root + 2 Leaf Nodes)
# No PQC yet — validates network formation
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/contiki-ng"
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

docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \
  --mount type=bind,source="$(dirname "$(dirname "$SCRIPT_DIR")")",destination=/home/user/simulation \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/simulation/experiments/exp01_baseline/exp01.csc\"" \
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
