#!/usr/bin/env python3
"""
=====================================================================
EXP03 + EXP04 Setup — Topology Variation Experiments
=====================================================================
EXP03: Star topology  — 1 root + 8 stub nodes (1-hop, direct)
EXP04: Chain topology — 1 root + 4 relay + 4 stub nodes (2-3 hops)

New features added to dataset:
  - topology    (star / chain)
  - hop_count   (1 / 2 / 3)
  - node_count  (8 / 9)
  - tx_range_m  (50 / 30)  radio range

After EXP03+04 the dataset grows from 99 → ~594 rows total.

Usage:
    python3 setup_exp03_exp04_topology.py
=====================================================================
"""

import os, stat

BASE = os.path.expanduser("~/contiki-ng/examples/pqc-iot-sim")
CODE = f"{BASE}/code"
SCRIPTS = f"{BASE}/scripts"

# ─────────────────────────────────────────────────────────────────
# SHARED: updated pqc-stub-node.c that also logs topology features
# ─────────────────────────────────────────────────────────────────
stub_c = r"""/**
 * pqc-stub-node.c  (v2 — includes topology metadata in PQC_LOG)
 * Each node emits topology info + PQC energy for all 11 algorithms.
 *
 * PQC_LOG format:
 *   PQC_LOG node=<id> hop=<hop> topo=<topo> payload=<bytes>
 *            algo=<name> type=<KEM|SIG> op=<name>
 *            cycles=<n> time_us=<n> energy_uj=<n>
 */

#include "contiki.h"
#include "net/linkaddr.h"
#include "pqc-timing-stubs.h"
#include <stdio.h>

/* Set per-experiment via compiler flags:
   -DPQC_HOP_COUNT=1 -DPQC_TOPO=\"star\" -DPQC_PAYLOAD=100  */
#ifndef PQC_HOP_COUNT
#define PQC_HOP_COUNT 1
#endif
#ifndef PQC_TOPO
#define PQC_TOPO "star"
#endif
#ifndef PQC_PAYLOAD
#define PQC_PAYLOAD 100
#endif

#define PQC_NUM_ALGORITHMS  11
#define PQC_NUM_OPS          3

PROCESS(pqc_stub_process, "PQC Stub Node v2");
AUTOSTART_PROCESSES(&pqc_stub_process);

PROCESS_THREAD(pqc_stub_process, ev, data)
{
    static struct etimer et;
    static uint8_t alg = 0;
    static uint8_t op  = 0;
    uint8_t node_id;

    PROCESS_BEGIN();

    node_id = linkaddr_node_addr.u8[7];
    printf("PQC_LOG node=%u STATUS=START topo=%s hop=%d\n",
           node_id, PQC_TOPO, PQC_HOP_COUNT);

    etimer_set(&et, CLOCK_SECOND / 10);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    for(alg = 0; alg < PQC_NUM_ALGORITHMS; alg++) {
        for(op = 0; op < PQC_NUM_OPS; op++) {
            uint32_t cycles   = PQC_CYCLES[alg][op];
            uint32_t time_us  = (uint32_t)((uint64_t)cycles * 1000000UL
                                           / PQC_CLOCK_HZ);
            uint32_t energy_uj = (uint32_t)((uint64_t)time_us
                                             * PQC_ACTIVE_UW / 1000000UL);
            printf("PQC_LOG node=%u hop=%d topo=%s payload=%d"
                   " algo=%s type=%s op=%s"
                   " cycles=%lu time_us=%lu energy_uj=%lu\n",
                   node_id, PQC_HOP_COUNT, PQC_TOPO, PQC_PAYLOAD,
                   PQC_ALG_NAMES[alg], PQC_TYPE_NAMES[alg],
                   PQC_OP_NAMES[op],
                   (unsigned long)cycles,
                   (unsigned long)time_us,
                   (unsigned long)energy_uj);

            etimer_set(&et, CLOCK_SECOND / 10);
            PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
        }
    }

    printf("PQC_LOG node=%u STATUS=DONE topo=%s hop=%d\n",
           node_id, PQC_TOPO, PQC_HOP_COUNT);

    PROCESS_END();
}
"""

with open(f"{CODE}/pqc-stub-node.c", "w") as f:
    f.write(stub_c)
print("✅ code/pqc-stub-node.c  (v2 — topology-aware)")


# ─────────────────────────────────────────────────────────────────
# SHARED: updated parse_logs.py — handles new topology fields
# ─────────────────────────────────────────────────────────────────
parse_py = r"""#!/usr/bin/env python3
"""
parse_py += '"""'
parse_py += r"""
parse_logs.py  (v2)
Parses Cooja pqc_raw.log → structured CSV for ML training.

Handles both EXP02 format (no topology) and EXP03/04 format
(with hop, topo, payload fields).

Usage:
    python3 parse_logs.py --log pqc_raw.log --csv dataset.csv
                          [--topology star] [--hop 1] [--payload 100]
"""
parse_py += '"""'
parse_py += r"""

import re, csv, argparse, os

SECURITY_LEVEL = {
    "KYBER512":1,"KYBER768":3,"KYBER1024":5,
    "DILITHIUM2":2,"DILITHIUM3":3,"DILITHIUM5":5,
    "FALCON512":1,"FALCON1024":5,
    "SPHINCS128":1,"SPHINCS192":3,"SPHINCS256":5,
}

# Full format: node hop topo payload algo type op cycles time_us energy_uj
FULL_RE = re.compile(
    r"PQC_LOG\s+node=(\d+)\s+hop=(\d+)\s+topo=(\w+)\s+payload=(\d+)\s+"
    r"algo=(\w+)\s+type=(\w+)\s+op=(\w+)\s+"
    r"cycles=(\d+)\s+time_us=(\d+)\s+energy_uj=(\d+)"
)

# Minimal format (EXP02): node algo type op cycles time_us energy_uj
MIN_RE = re.compile(
    r"PQC_LOG\s+node=(\d+)\s+"
    r"algo=(\w+)\s+type=(\w+)\s+op=(\w+)\s+"
    r"cycles=(\d+)\s+time_us=(\d+)\s+energy_uj=(\d+)"
)

FIELDS = ["node_id","topology","hop_count","payload_bytes",
          "algorithm","algo_type","operation","security_level",
          "cycles","time_us","energy_uj","energy_mj"]

def parse(log_path, csv_path, default_topo="star",
          default_hop=1, default_payload=100):
    rows = []
    with open(log_path) as f:
        for line in f:
            m = FULL_RE.search(line)
            if m:
                nid,hop,topo,pay,algo,atype,op,cyc,tus,euj = m.groups()
                rows.append({
                    "node_id":       int(nid),
                    "topology":      topo,
                    "hop_count":     int(hop),
                    "payload_bytes": int(pay),
                    "algorithm":     algo,
                    "algo_type":     atype,
                    "operation":     op,
                    "security_level": SECURITY_LEVEL.get(algo,-1),
                    "cycles":        int(cyc),
                    "time_us":       int(tus),
                    "energy_uj":     int(euj),
                    "energy_mj":     round(int(euj)/1000.0,6),
                })
                continue
            m = MIN_RE.search(line)
            if m:
                nid,algo,atype,op,cyc,tus,euj = m.groups()
                rows.append({
                    "node_id":       int(nid),
                    "topology":      default_topo,
                    "hop_count":     default_hop,
                    "payload_bytes": default_payload,
                    "algorithm":     algo,
                    "algo_type":     atype,
                    "operation":     op,
                    "security_level": SECURITY_LEVEL.get(algo,-1),
                    "cycles":        int(cyc),
                    "time_us":       int(tus),
                    "energy_uj":     int(euj),
                    "energy_mj":     round(int(euj)/1000.0,6),
                })

    if not rows:
        print("Warning: No PQC_LOG lines found.")
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"Parsed {len(rows)} rows to {csv_path}")
    return len(rows)

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log",      required=True)
    ap.add_argument("--csv",      required=True)
    ap.add_argument("--topology", default="star")
    ap.add_argument("--hop",      type=int, default=1)
    ap.add_argument("--payload",  type=int, default=100)
    a = ap.parse_args()
    parse(a.log, a.csv, a.topology, a.hop, a.payload)
"""

with open(f"{SCRIPTS}/parse_logs.py", "w") as f:
    f.write(parse_py)
print("✅ scripts/parse_logs.py  (v2 — topology-aware)")


# ─────────────────────────────────────────────────────────────────
# SHARED: merge_dataset.py — combines all experiment CSVs
# ─────────────────────────────────────────────────────────────────
merge_py = '''#!/usr/bin/env python3
"""
merge_dataset.py
Combines all pqc_energy_*.csv files into one master dataset.

Usage:
    python3 merge_dataset.py
"""
import os, glob, csv

BASE    = os.path.expanduser("~/contiki-ng/examples/pqc-iot-sim")
DS_DIR  = f"{BASE}/results/dataset"
OUT     = f"{DS_DIR}/master_dataset.csv"

files = sorted(glob.glob(f"{DS_DIR}/pqc_energy_*.csv"))
if not files:
    print("No dataset files found in", DS_DIR)
    exit(1)

all_rows = []
header   = None
for fp in files:
    with open(fp) as f:
        reader = csv.DictReader(f)
        if header is None:
            header = reader.fieldnames
        for row in reader:
            all_rows.append(row)
    print(f"  Loaded {fp}  ({len(all_rows)} total so far)")

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_rows)

print(f"\\nMaster dataset: {len(all_rows)} rows → {OUT}")
'''

with open(f"{SCRIPTS}/merge_dataset.py", "w") as f:
    f.write(merge_py)
print("✅ scripts/merge_dataset.py")


# ─────────────────────────────────────────────────────────────────
# EXP03 — Star topology, 8 stub nodes, all at 1 hop from root
# Nodes placed in a ring at range 40m from root
# ─────────────────────────────────────────────────────────────────
import math

def make_csc(exp_id, title, nodes, tx_range, timeout_ms, out_path, num_done):
    """Generate a .csc file for a given node layout."""

    mote_blocks = ""
    # Root node always first
    mote_blocks += """    <mote>
      <motetype_identifier>pqcroot1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>60.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>1</id>
      </interface_config>
    </mote>\n"""

    for i, (x, y, mtype, mote_id) in enumerate(nodes):
        mote_blocks += f"""    <mote>
      <motetype_identifier>{mtype}</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>{x:.1f}</x><y>{y:.1f}</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>{mote_id}</id>
      </interface_config>
    </mote>\n"""

    csc = f"""<?xml version="1.0" encoding="UTF-8"?>
<simconf version="2022112801">
  <simulation>
    <title>{title}</title>
    <randomseed>42</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>{tx_range}.0</transmitting_range>
      <interference_range>{tx_range}.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events><logoutput>1000000</logoutput></events>
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
      <identifier>pqcstub1</identifier>
      <description>PQC Stub Node</description>
      <source>[CONFIG_DIR]/../../code/pqc-stub-node.c</source>
      <commands>$(MAKE) -j$(CPUS) pqc-stub-node.cooja TARGET=cooja</commands>
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
{mote_blocks}  </simulation>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
TIMEOUT({timeout_ms}, log.testFailed("Timed out"));
var fw = new java.io.FileWriter(
  "/home/user/contiki-ng/examples/pqc-iot-sim/experiments/{exp_id}/results/pqc_raw.log",
  false);
var bw = new java.io.BufferedWriter(fw);
var done = 0;
while (done &lt; {num_done}) {{
  YIELD();
  if (msg.contains("PQC_LOG") || msg.contains("STATUS")) {{
    bw.write(msg + "\\n");
    bw.flush();
  }}
  if (msg.contains("STATUS=DONE")) {{
    done++;
  }}
}}
bw.close();
log.testOK();
      </script>
      <active>true</active>
    </plugin_config>
    <width>600</width><height>300</height>
    <location_x>0</location_x><location_y>460</location_y>
  </plugin>
</simconf>"""
    with open(out_path, "w") as f:
        f.write(csc)


# EXP03: 8 stub nodes in a ring at radius 35m from root (all 1-hop)
exp03_dir = f"{BASE}/experiments/exp03_star_topology"
os.makedirs(f"{exp03_dir}/results", exist_ok=True)

star_nodes = []
for i in range(8):
    angle = 2 * math.pi * i / 8
    x = 60 + 35 * math.cos(angle)
    y = 60 + 35 * math.sin(angle)
    star_nodes.append((x, y, "pqcstub1", i + 2))

make_csc(
    exp_id="exp03_star_topology",
    title="EXP03 - Star Topology 8 Nodes 1-Hop",
    nodes=star_nodes,
    tx_range=50,
    timeout_ms=300000,
    out_path=f"{exp03_dir}/exp03.csc",
    num_done=8,
)
print("✅ experiments/exp03_star_topology/exp03.csc")


# EXP04: Chain topology — root → 2 relays → 4 stub nodes (2-3 hops)
# Root at (60,60), relay1 at (90,60), relay2 at (120,60)
# Stubs behind relay2 at (150,45), (150,60), (150,75), (150,90)
exp04_dir = f"{BASE}/experiments/exp04_mesh_topology"
os.makedirs(f"{exp04_dir}/results", exist_ok=True)

chain_nodes = [
    # relays at hop-1 and hop-2 (still stub nodes, just placed in chain)
    (90.0,  60.0, "pqcstub1", 2),
    (120.0, 60.0, "pqcstub1", 3),
    # leaves at hop-3
    (150.0, 45.0, "pqcstub1", 4),
    (150.0, 60.0, "pqcstub1", 5),
    (150.0, 75.0, "pqcstub1", 6),
    (150.0, 90.0, "pqcstub1", 7),
]

make_csc(
    exp_id="exp04_mesh_topology",
    title="EXP04 - Chain Topology Multi-Hop",
    nodes=chain_nodes,
    tx_range=35,
    timeout_ms=300000,
    out_path=f"{exp04_dir}/exp04.csc",
    num_done=6,
)
print("✅ experiments/exp04_mesh_topology/exp04.csc")


# ─────────────────────────────────────────────────────────────────
# run.sh generator (shared template for EXP03 and EXP04)
# ─────────────────────────────────────────────────────────────────
def make_run_sh(exp_id, exp_name, csc_name, topo, hop, payload, path):
    sh = f"""#!/bin/bash
# =====================================================
# {exp_name}
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="$HOME/contiki-ng"
CSC="$SCRIPT_DIR/{csc_name}"
RESULTS="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$RESULTS/run_${{TIMESTAMP}}.log"
RAW="$RESULTS/pqc_raw.log"
CSV="$HOME/contiki-ng/examples/pqc-iot-sim/results/dataset/pqc_energy_{exp_id}_${{TIMESTAMP}}.csv"

echo "=============================="
echo " {exp_name}"
echo " Log: $LOG"
echo "=============================="
mkdir -p "$RESULTS"
mkdir -p "$HOME/contiki-ng/examples/pqc-iot-sim/results/dataset"

docker run --rm --privileged \\
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \\
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \\
  contiker/contiki-ng \\
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \\
    --args=\\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/{exp_id}/{csc_name}\\"" \\
  2>&1 | tee "$LOG"

if grep -q "TEST OK" "$LOG"; then
    echo ""
    echo "✅ {exp_name} PASSED — $(date)"
    python3 "$HOME/contiki-ng/examples/pqc-iot-sim/scripts/parse_logs.py" \\
        --log "$RAW" --csv "$CSV" \\
        --topology {topo} --hop {hop} --payload {payload}
    echo "   Dataset: $CSV"
    wc -l "$CSV"
    echo "   Preview:"
    head -4 "$CSV"
else
    echo "❌ FAILED — check $LOG"
    exit 1
fi
"""
    with open(path, "w") as f:
        f.write(sh)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP)


import stat
make_run_sh("exp03_star_topology", "EXP03 Star Topology 8 Nodes",
            "exp03.csc", "star", 1, 100,
            f"{exp03_dir}/run.sh")
print("✅ experiments/exp03_star_topology/run.sh")

make_run_sh("exp04_mesh_topology", "EXP04 Chain Topology Multi-Hop",
            "exp04.csc", "chain", 2, 100,
            f"{exp04_dir}/run.sh")
print("✅ experiments/exp04_mesh_topology/run.sh")


# ─────────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────────
print()
print("=" * 54)
print("  EXP03 + EXP04 SETUP COMPLETE")
print("=" * 54)
print()
print("Run order:")
print(f"  bash {exp03_dir}/run.sh")
print(f"  bash {exp04_dir}/run.sh")
print()
print("Then merge all CSVs:")
print(f"  python3 {SCRIPTS}/merge_dataset.py")
print()
print("Expected total rows after EXP03+04:")
print("  EXP02:  99 rows (3 nodes, stub)")
print("  EXP03: 264 rows (8 nodes, star, 1-hop)")
print("  EXP04: 198 rows (6 nodes, chain, 2-3 hop)")
print("  TOTAL: 561 rows")
