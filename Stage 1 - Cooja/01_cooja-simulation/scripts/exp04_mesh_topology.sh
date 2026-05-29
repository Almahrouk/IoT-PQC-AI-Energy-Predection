#!/bin/bash
# =====================================================
# EXP04 Chain Topology Multi-Hop
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="$HOME/liboqs/build/contiki-ng"
CSC="$SCRIPT_DIR/exp04.csc"
RESULTS="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$RESULTS/run_${TIMESTAMP}.log"
RAW="$RESULTS/pqc_raw.log"
CSV="$HOME/contiki-ng/examples/pqc-iot-sim/results/dataset/pqc_energy_exp04_mesh_topology_${TIMESTAMP}.csv"

echo "=============================="
echo " EXP04 Chain Topology Multi-Hop"
echo " Log: $LOG"
echo "=============================="
mkdir -p "$RESULTS"
mkdir -p "$HOME/contiki-ng/examples/pqc-iot-sim/results/dataset"

docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp04_mesh_topology/exp04.csc\"" \
  2>&1 | tee "$LOG"

if grep -q "TEST OK" "$LOG"; then
    echo ""
    echo "✅ EXP04 Chain Topology Multi-Hop PASSED — $(date)"
    python3 "$HOME/contiki-ng/examples/pqc-iot-sim/scripts/parse_logs.py" \
        --log "$RAW" --csv "$CSV" \
        --topology chain --hop 2 --payload 100
    echo "   Dataset: $CSV"
    wc -l "$CSV"
    echo "   Preview:"
    head -4 "$CSV"
else
    echo "❌ FAILED — check $LOG"
    exit 1
fi
