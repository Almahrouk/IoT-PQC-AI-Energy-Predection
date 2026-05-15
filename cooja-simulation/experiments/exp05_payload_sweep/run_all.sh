#!/bin/bash
set -e
BASE="$HOME/contiki-ng/examples/pqc-iot-sim"
DS="$BASE/results/dataset"
SCRIPTS="$BASE/scripts"
mkdir -p "$DS"


echo "=== star_p50 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/star_p50.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_star_p50.log" \
       --csv "$DS/pqc_energy_exp05_star_p50.csv" \
       --topology star --hop 1 --payload 50 \
  && echo "✅ star_p50 done" \
  || { echo "❌ star_p50 FAILED"; exit 1; }

echo "=== chain_p50 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/chain_p50.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_chain_p50.log" \
       --csv "$DS/pqc_energy_exp05_chain_p50.csv" \
       --topology chain --hop 2 --payload 50 \
  && echo "✅ chain_p50 done" \
  || { echo "❌ chain_p50 FAILED"; exit 1; }

echo "=== star_p100 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/star_p100.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_star_p100.log" \
       --csv "$DS/pqc_energy_exp05_star_p100.csv" \
       --topology star --hop 1 --payload 100 \
  && echo "✅ star_p100 done" \
  || { echo "❌ star_p100 FAILED"; exit 1; }

echo "=== chain_p100 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/chain_p100.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_chain_p100.log" \
       --csv "$DS/pqc_energy_exp05_chain_p100.csv" \
       --topology chain --hop 2 --payload 100 \
  && echo "✅ chain_p100 done" \
  || { echo "❌ chain_p100 FAILED"; exit 1; }

echo "=== star_p200 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/star_p200.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_star_p200.log" \
       --csv "$DS/pqc_energy_exp05_star_p200.csv" \
       --topology star --hop 1 --payload 200 \
  && echo "✅ star_p200 done" \
  || { echo "❌ star_p200 FAILED"; exit 1; }

echo "=== chain_p200 ==="
docker run --rm --privileged \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  --mount type=bind,source="$HOME/contiki-ng",destination=/home/user/contiki-ng \
  contiker/contiki-ng \
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \
    --args=\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/chain_p200.csc\"" \
  && python3 "$SCRIPTS/parse_logs.py" \
       --log "$BASE/experiments/exp05_payload_sweep/results/pqc_raw_chain_p200.log" \
       --csv "$DS/pqc_energy_exp05_chain_p200.csv" \
       --topology chain --hop 2 --payload 200 \
  && echo "✅ chain_p200 done" \
  || { echo "❌ chain_p200 FAILED"; exit 1; }

echo ""
echo "All EXP05 sub-experiments complete. Merging..."
python3 "$SCRIPTS/merge_dataset.py"
