#!/bin/bash
# =====================================================
# EXP03 Star Topology 8 Nodes
# =====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SIM_PATH="$(dirname "$(dirname "$SCRIPT_DIR")")"

CNG_PATH="/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/contiki-ng"

CSC="$SCRIPT_DIR/exp03.csc"

RESULTS="$SCRIPT_DIR/results"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

LOG="$RESULTS/run_${TIMESTAMP}.log"

RAW="$RESULTS/pqc_raw.log"

CSV="$RESULTS/pqc_energy_exp03_star_topology_${TIMESTAMP}.csv"


echo "=============================="
echo " EXP03 Star Topology 8 Nodes"
echo " Log: $LOG"
echo " CSV: $CSV"
echo "=============================="


mkdir -p "$RESULTS"
chmod 777 "$RESULTS"


docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \
  --mount type=bind,source="$SIM_PATH",destination=/home/user/simulation \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/simulation/experiments/exp03_star_topology/exp03.csc\""\
  2>&1 | tee "$LOG"


if grep -q "TEST OK" "$LOG"; then

    echo ""
    echo "✅ EXP03 Star Topology 8 Nodes PASSED — $(date)"

    python3 "$SIM_PATH/ml/parse_logs.py" \
        --log "$RAW" \
        --csv "$CSV" \
        --topology star \
        --hop 1 \
        --payload 100

    echo "Dataset: $CSV"
    wc -l "$CSV"

    echo "Preview:"
    head -4 "$CSV"

else

    echo "❌ FAILED — check $LOG"
    exit 1

fi
