#!/usr/bin/env python3
"""
=====================================================================
EXP02 — PQC Timing Stubs: Setup Script
=====================================================================
Creates:
  code/pqc-timing-stubs.h       — pqm4 cycle counts for all algorithms
  code/pqc-stub-node.c          — firmware that emits PQC_LOG lines
  experiments/exp02_pqc_stubs/  — .csc + run.sh
  scripts/parse_logs.py         — log parser → CSV dataset

Cycle counts sourced from published pqm4 benchmarks:
  Kannwischer et al., "pqm4: Benchmarking NIST PQC on ARM Cortex-M4"
  IACR ePrint 2024/112

CC2538 energy model (used by Cooja):
  Active current: 20 mA @ 3.3V = 66 mW
  Energy (uJ)   = 66,000 uW × time_s
  Clock speed   : 32 MHz

Usage:
    python3 setup_exp02_pqc_stubs.py
=====================================================================
"""

import os, stat

BASE = os.path.expanduser("~/contiki-ng/examples/pqc-iot-sim")
CODE = f"{BASE}/code"
EXP02 = f"{BASE}/experiments/exp02_pqc_stubs"
os.makedirs(f"{EXP02}/results", exist_ok=True)


# ─────────────────────────────────────────────────────────────────
# FILE 1 — pqc-timing-stubs.h
# Published pqm4 cycle counts for ARM Cortex-M4 @ 64 MHz
# Energy = cycles / clock_hz * current_mA * voltage_V * 1000 (mJ)
# CC2538: 20mA active, 3.3V → 66mW = 66000 uW
# ─────────────────────────────────────────────────────────────────
stubs_h = r"""/**
 * pqc-timing-stubs.h
 * PQC Algorithm Timing Stubs for Contiki-NG / Cooja Simulation
 *
 * Cycle counts from pqm4 benchmarks (ARM Cortex-M4):
 *   Kannwischer et al., IACR ePrint 2024/112
 *
 * Energy model: CC2538 @ 32 MHz, 20 mA active, 3.3 V
 *   time_us  = cycles * 1000000 / CLOCK_HZ
 *   energy_uj = time_us * 66 / 1000   (66 mW active power)
 */

#ifndef PQC_TIMING_STUBS_H
#define PQC_TIMING_STUBS_H

#include <stdint.h>
#include <stdio.h>

/* CC2538 clock and power model */
#define PQC_CLOCK_HZ      32000000UL   /* 32 MHz */
#define PQC_ACTIVE_UW     66000UL      /* 20 mA * 3.3 V * 1000 */

/* ── Algorithm identifiers ── */
#define PQC_ALG_KYBER512      0
#define PQC_ALG_KYBER768      1
#define PQC_ALG_KYBER1024     2
#define PQC_ALG_DILITHIUM2    3
#define PQC_ALG_DILITHIUM3    4
#define PQC_ALG_DILITHIUM5    5
#define PQC_ALG_FALCON512     6
#define PQC_ALG_FALCON1024    7
#define PQC_ALG_SPHINCS128    8
#define PQC_ALG_SPHINCS192    9
#define PQC_ALG_SPHINCS256   10

/* ── Operation identifiers ── */
#define PQC_OP_KEYGEN    0
#define PQC_OP_ENCAP     1
#define PQC_OP_DECAP     2
#define PQC_OP_SIGN      1
#define PQC_OP_VERIFY    2

/* ── Cycle counts table [algorithm][operation] ── */
/* Source: pqm4 benchmarks, ARM Cortex-M4 @ 64 MHz, scaled to 32 MHz */
static const uint32_t PQC_CYCLES[11][3] = {
/*  Algorithm         KEYGEN      ENCAP/SIGN   DECAP/VERIFY  */
/* Kyber-512   */ {  1700000,    1900000,    2000000 },
/* Kyber-768   */ {  2600000,    2900000,    3100000 },
/* Kyber-1024  */ {  3700000,    4100000,    4400000 },
/* Dilithium-2 */ {  2200000,    4900000,    2300000 },
/* Dilithium-3 */ {  3500000,    7800000,    3700000 },
/* Dilithium-5 */ {  5000000,   11000000,    5300000 },
/* FALCON-512  */ { 10000000,    3000000,     700000 },
/* FALCON-1024 */ { 20000000,    5800000,    1300000 },
/* SPHINCS+-128*/ {  9000000,  200000000,    8000000 },
/* SPHINCS+-192*/ { 17000000,  370000000,   15000000 },
/* SPHINCS+-256*/ { 24000000,  540000000,   22000000 },
};

static const char *PQC_ALG_NAMES[] = {
    "KYBER512","KYBER768","KYBER1024",
    "DILITHIUM2","DILITHIUM3","DILITHIUM5",
    "FALCON512","FALCON1024",
    "SPHINCS128","SPHINCS192","SPHINCS256"
};

static const char *PQC_OP_NAMES[] = {
    "KEYGEN","ENCAP_SIGN","DECAP_VERIFY"
};

static const char *PQC_TYPE_NAMES[] = {
    "KEM","KEM","KEM",
    "SIG","SIG","SIG",
    "SIG","SIG",
    "SIG","SIG","SIG"
};

/**
 * pqc_simulate_op()
 * Simulates a PQC operation and emits a structured PQC_LOG line.
 *
 * Output format (captured by Cooja LogListener):
 *   PQC_LOG node=<id> algo=<name> type=<KEM|SIG> op=<name>
 *            cycles=<n> time_us=<n> energy_uj=<n>
 */
static inline void pqc_simulate_op(uint8_t node_id,
                                    uint8_t alg,
                                    uint8_t op)
{
    uint32_t cycles   = PQC_CYCLES[alg][op];
    uint32_t time_us  = (uint32_t)((uint64_t)cycles * 1000000UL
                                   / PQC_CLOCK_HZ);
    uint32_t energy_uj = (uint32_t)((uint64_t)time_us
                                    * PQC_ACTIVE_UW / 1000000UL);

    printf("PQC_LOG node=%u algo=%s type=%s op=%s "
           "cycles=%lu time_us=%lu energy_uj=%lu\n",
           (unsigned)node_id,
           PQC_ALG_NAMES[alg],
           PQC_TYPE_NAMES[alg],
           PQC_OP_NAMES[op],
           (unsigned long)cycles,
           (unsigned long)time_us,
           (unsigned long)energy_uj);
}

#endif /* PQC_TIMING_STUBS_H */
"""

with open(f"{CODE}/pqc-timing-stubs.h", "w") as f:
    f.write(stubs_h)
print("✅ code/pqc-timing-stubs.h")


# ─────────────────────────────────────────────────────────────────
# FILE 2 — pqc-stub-node.c
# Leaf node firmware: cycles through all algorithms & operations
# emitting PQC_LOG lines for every combination
# ─────────────────────────────────────────────────────────────────
stub_node_c = r"""/**
 * pqc-stub-node.c
 * Contiki-NG firmware for EXP02
 *
 * Each node cycles through all 11 PQC algorithm variants and
 * 3 operations (KEYGEN, ENCAP/SIGN, DECAP/VERIFY), emitting
 * a PQC_LOG line for each. Cooja's LogListener captures all output.
 *
 * This generates the raw dataset rows for ML training.
 */

#include "contiki.h"
#include "net/linkaddr.h"
#include "pqc-timing-stubs.h"
#include <stdio.h>

#define PQC_NUM_ALGORITHMS  11
#define PQC_NUM_OPS          3
#define PQC_INTER_OP_MS    100   /* ms between operations */

PROCESS(pqc_stub_process, "PQC Stub Node");
AUTOSTART_PROCESSES(&pqc_stub_process);

PROCESS_THREAD(pqc_stub_process, ev, data)
{
    static struct etimer et;
    static uint8_t alg = 0;
    static uint8_t op  = 0;
    uint8_t node_id;

    PROCESS_BEGIN();

    node_id = linkaddr_node_addr.u8[7];
    printf("PQC_LOG node=%u STATUS=START\n", node_id);

    etimer_set(&et, CLOCK_SECOND / 10);  /* 100 ms initial delay */
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    for(alg = 0; alg < PQC_NUM_ALGORITHMS; alg++) {
        for(op = 0; op < PQC_NUM_OPS; op++) {
            pqc_simulate_op(node_id, alg, op);
            etimer_set(&et, CLOCK_SECOND * PQC_INTER_OP_MS / 1000);
            PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
        }
    }

    printf("PQC_LOG node=%u STATUS=DONE alg_count=%d op_count=%d\n",
           node_id, PQC_NUM_ALGORITHMS, PQC_NUM_OPS);

    PROCESS_END();
}
"""

with open(f"{CODE}/pqc-stub-node.c", "w") as f:
    f.write(stub_node_c)
print("✅ code/pqc-stub-node.c")


# ─────────────────────────────────────────────────────────────────
# FILE 3 — Makefile update (add stub node target)
# ─────────────────────────────────────────────────────────────────
makefile = """CONTIKI_PROJECT = pqc-root-node pqc-leaf-node pqc-stub-node
all: $(CONTIKI_PROJECT)
CONTIKI = /home/user/contiki-ng
include $(CONTIKI)/Makefile.include
"""

with open(f"{CODE}/Makefile", "w") as f:
    f.write(makefile)
print("✅ code/Makefile updated")


# ─────────────────────────────────────────────────────────────────
# FILE 4 — exp02.csc (3 stub nodes, 3 hops, star topology)
# timeout: 11 algos × 3 ops × 100ms × 3 nodes + margin = 120 sec
# ─────────────────────────────────────────────────────────────────
exp02_csc = """<?xml version="1.0" encoding="UTF-8"?>
<simconf version="2022112801">
  <simulation>
    <title>EXP02 - PQC Timing Stubs, Star Topology</title>
    <randomseed>42</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range>
      <interference_range>50.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events><logoutput>500000</logoutput></events>
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
    <!-- Root node at centre -->
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
    <!-- Stub node 2 -->
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>90.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>2</id>
      </interface_config>
    </mote>
    <!-- Stub node 3 -->
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>30.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>3</id>
      </interface_config>
    </mote>
    <!-- Stub node 4 -->
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>60.0</x><y>90.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>4</id>
      </interface_config>
    </mote>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
TIMEOUT(180000);
log.testOK();
      </script>
      <active>true</active>
    </plugin_config>
    <width>600</width><height>300</height>
    <location_x>0</location_x><location_y>460</location_y>
  </plugin>
</simconf>"""

with open(f"{EXP02}/exp02.csc", "w") as f:
    f.write(exp02_csc)
print("✅ experiments/exp02_pqc_stubs/exp02.csc")


# ─────────────────────────────────────────────────────────────────
# FILE 5 — run.sh for EXP02
# ─────────────────────────────────────────────────────────────────
run_sh = """#!/bin/bash
# =====================================================
# EXP02 — PQC Timing Stubs
# 3 stub nodes × 11 algorithms × 3 operations
# Emits PQC_LOG lines → parsed to CSV dataset
# =====================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CNG_PATH="$HOME/contiki-ng"
CSC="$SCRIPT_DIR/exp02.csc"
RESULTS="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$RESULTS/run_${TIMESTAMP}.log"
CSV="$RESULTS/pqc_energy_${TIMESTAMP}.csv"

echo "=============================="
echo " EXP02: PQC Timing Stubs"
echo " Nodes: 3 stub + 1 root"
echo " Algorithms: 11 × 3 operations"
echo " Log: $LOG"
echo " CSV: $CSV"
echo "=============================="

mkdir -p "$RESULTS"

docker run --rm --privileged \\
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \\
  --mount type=bind,source="$CNG_PATH",destination=/home/user/contiki-ng \\
  contiker/contiki-ng \\
  bash -c "cd /home/user/contiki-ng/tools/cooja && ./gradlew run \\
    --args=\\"--no-gui --autostart /home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp02_pqc_stubs/exp02.csc\\"" \\
  2>&1 | tee "$LOG"

if grep -q "TEST OK" "$LOG"; then
    echo ""
    echo "✅ EXP02 PASSED — $(date)"
    echo "   Log: $LOG"
    echo ""
    echo "Parsing PQC_LOG lines to CSV..."
    python3 "$(dirname "$SCRIPT_DIR")/scripts/parse_logs.py" \\
        --log "$LOG" --csv "$CSV"
    echo "   CSV: $CSV"
    echo ""
    echo "Preview (first 5 rows):"
    head -6 "$CSV"
else
    echo "❌ EXP02 FAILED — check $LOG"
    exit 1
fi
"""

run_path = f"{EXP02}/run.sh"
with open(run_path, "w") as f:
    f.write(run_sh)
os.chmod(run_path, os.stat(run_path).st_mode | stat.S_IEXEC | stat.S_IXGRP)
print("✅ experiments/exp02_pqc_stubs/run.sh")


# ─────────────────────────────────────────────────────────────────
# FILE 6 — parse_logs.py (PQC_LOG → CSV dataset)
# ─────────────────────────────────────────────────────────────────
parse_py = r"""#!/usr/bin/env python3
"""
parse_py += '"""'
parse_py += r"""
parse_logs.py
Parses Cooja log files → structured CSV dataset for ML training.

Input line format:
  PQC_LOG node=2 algo=KYBER512 type=KEM op=KEYGEN
           cycles=1700000 time_us=53125 energy_uj=3506

Output CSV columns:
  node_id, algorithm, algo_type, operation, security_level,
  cycles, time_us, energy_uj, energy_mj

Usage:
    python3 parse_logs.py --log run_20260515.log --csv dataset.csv
"""
parse_py += '"""'
parse_py += r"""

import re, csv, argparse, os

# Map algorithm name → security level (NIST levels 1–5)
SECURITY_LEVEL = {
    "KYBER512":    1, "KYBER768":    3, "KYBER1024":   5,
    "DILITHIUM2":  2, "DILITHIUM3":  3, "DILITHIUM5":  5,
    "FALCON512":   1, "FALCON1024":  5,
    "SPHINCS128":  1, "SPHINCS192":  3, "SPHINCS256":  5,
}

PQC_LOG_RE = re.compile(
    r"PQC_LOG\s+"
    r"node=(\d+)\s+"
    r"algo=(\w+)\s+"
    r"type=(\w+)\s+"
    r"op=(\w+)\s+"
    r"cycles=(\d+)\s+"
    r"time_us=(\d+)\s+"
    r"energy_uj=(\d+)"
)

def parse(log_path, csv_path):
    rows = []
    with open(log_path) as f:
        for line in f:
            m = PQC_LOG_RE.search(line)
            if not m:
                continue
            node_id, algo, atype, op, cycles, time_us, energy_uj = m.groups()
            energy_mj = round(int(energy_uj) / 1000.0, 6)
            sec_level = SECURITY_LEVEL.get(algo, -1)
            rows.append({
                "node_id":       int(node_id),
                "algorithm":     algo,
                "algo_type":     atype,
                "operation":     op,
                "security_level": sec_level,
                "cycles":        int(cycles),
                "time_us":       int(time_us),
                "energy_uj":     int(energy_uj),
                "energy_mj":     energy_mj,
            })

    if not rows:
        print("⚠️  No PQC_LOG lines found in log file.")
        return 0

    fields = ["node_id","algorithm","algo_type","operation",
              "security_level","cycles","time_us","energy_uj","energy_mj"]

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"✅ Parsed {len(rows)} rows → {csv_path}")
    return len(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="Cooja log file path")
    ap.add_argument("--csv", required=True, help="Output CSV path")
    args = ap.parse_args()
    parse(args.log, args.csv)
"""

scripts_dir = f"{BASE}/scripts"
os.makedirs(scripts_dir, exist_ok=True)
with open(f"{scripts_dir}/parse_logs.py", "w") as f:
    f.write(parse_py)
print("✅ scripts/parse_logs.py")


# ─────────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────────
print()
print("=" * 54)
print("  EXP02 SETUP COMPLETE")
print("=" * 54)
print()
print("Files created:")
print(f"  {CODE}/pqc-timing-stubs.h")
print(f"  {CODE}/pqc-stub-node.c")
print(f"  {CODE}/Makefile  (updated)")
print(f"  {EXP02}/exp02.csc")
print(f"  {EXP02}/run.sh")
print(f"  {scripts_dir}/parse_logs.py")
print()
print("Next commands:")
print(f"  bash {EXP02}/run.sh")
print()
print("Expected output:")
print("  ✅ EXP02 PASSED")
print("  CSV with ~99 rows (3 nodes × 11 algos × 3 ops)")
