#!/usr/bin/env python3
"""
parse_logs.py  (v2)
Parses Cooja pqc_raw.log → structured CSV for ML training.

Handles both EXP02 format (no topology) and EXP03/04 format
(with hop, topo, payload fields).

Usage:
    python3 parse_logs.py --log pqc_raw.log --csv dataset.csv
                          [--topology star] [--hop 1] [--payload 100]
"""

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
