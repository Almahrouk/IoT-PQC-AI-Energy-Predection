#!/bin/bash
# =====================================================
# EXP02 — PQC Timing Stubs
# 3 stub nodes × 11 algorithms × 3 operations
# Emits PQC_LOG lines → parsed to CSV dataset
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/contiki-ng"
CSC="$SCRIPT_DIR/exp02.csc"
RESULTS="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$RESULTS/run_${TIMESTAMP}.log"
RAW="$RESULTS/pqc_raw.log"
CSV="$RESULTS/pqc_energy_${TIMESTAMP}.csv"
SIM_PATH="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=============================="
echo " EXP02: PQC Timing Stubs"
echo " Nodes: 3 stub + 1 root"
echo " Algorithms: 11 × 3 operations"
echo " Log: $LOG"
echo " CSV: $CSV"
echo "=============================="

mkdir -p "$RESULTS"

docker run --rm --privileged \
  -u $(id -u):$(id -g) \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \
  --mount type=bind,source="$SIM_PATH",destination=/home/user/simulation \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/simulation/experiments/exp02_pqc_stubs/exp02.csc\"" \
  2>&1 | tee "$LOG"

if grep -q "TEST OK" "$LOG"; then
    echo ""
    echo "✅ EXP02 PASSED — $(date)"
    echo "   Log: $LOG"
    echo ""
    echo "Parsing PQC_LOG lines to CSV..."
    PARSER="$(dirname "$(dirname "$SCRIPT_DIR")")/ml/parse_logs.py"
    python3 "$PARSER" \
    	--log "$RAW" --csv "$CSV"
    echo "   CSV: $CSV"
    echo ""
    echo "Preview (first 5 rows):"
    head -6 "$CSV"
else
    echo "❌ EXP02 FAILED — check $LOG"
    exit 1
fi
