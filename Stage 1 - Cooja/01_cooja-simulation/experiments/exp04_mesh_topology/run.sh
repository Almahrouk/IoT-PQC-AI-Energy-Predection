#!/bin/bash
# =====================================================
# EXP04 Chain Topology Multi-Hop
# =====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 01_cooja-simulation directory
SIM_PATH="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Contiki-NG path
CNG_PATH="/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/contiki-ng"

CSC="$SCRIPT_DIR/exp04.csc"

RESULTS="$SCRIPT_DIR/results"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

LOG="$RESULTS/run_${TIMESTAMP}.log"

# Cooja writes this file
RAW="$RESULTS/pqc_raw.log"

CSV="$RESULTS/pqc_energy_exp04_chain_topology_${TIMESTAMP}.csv"

PARSER="/home/user/New IOT/IoT-PQC-AI-Energy-Predection/Stage 1 - Cooja/01_cooja-simulation/ml/parse_logs.py"


echo "=============================="
echo " EXP04 Chain Topology Multi-Hop"
echo " Script: $SCRIPT_DIR"
echo " Log: $LOG"
echo " CSV: $CSV"
echo "=============================="


mkdir -p "$RESULTS"

# Fix docker writing permission problem
chmod 777 "$RESULTS"


docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \
  --mount type=bind,source="$SIM_PATH",destination=/home/user/simulation \
  contiker/contiki-ng \
  bash -c "
    cd /home/user/contiki-ng/tools/cooja &&
    ./gradlew run \
    --args=\"--no-gui --autostart /home/user/simulation/experiments/exp04_mesh_topology/exp04.csc\"
  " \
  2>&1 | tee "$LOG"



if grep -q "TEST OK" "$LOG"; then

    echo ""
    echo "✅ EXP04 PASSED — $(date)"

    echo ""
    echo "Parsing PQC logs..."

    python3 "$PARSER" \
        --log "$RAW" \
        --csv "$CSV" \
        --topology chain \
        --hop 2 \
        --payload 100


    echo ""
    echo "Dataset created:"
    echo "$CSV"

    wc -l "$CSV"

    echo ""
    echo "Preview:"
    head -5 "$CSV"

else

    echo ""
    echo "❌ EXP04 FAILED"
    echo "Check:"
    echo "$LOG"

    exit 1

fi
