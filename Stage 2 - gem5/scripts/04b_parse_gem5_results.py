#!/usr/bin/env python3
# 04_parse_gem5_results.py
import re, csv, os

LOG  = '/home/user/gem5_results/pqc_raw_v4.log'
OUT  = '/home/user/gem5_results/gem5_pqc_results_v4.csv'

CLOCK_HZ  = 64_000_000
ACTIVE_UW = 66_000

SECURITY = {
    'Kyber512':1,    'Kyber768':3,    'Kyber1024':5,
    'ML-KEM-512':1,  'ML-KEM-768':3,  'ML-KEM-1024':5,
    'ML-DSA-44':2,   'ML-DSA-65':3,   'ML-DSA-87':5,
    'Falcon-512':1,  'Falcon-1024':5,
}
ALGO_TYPE = {
    'Kyber512':'KEM',   'Kyber768':'KEM',   'Kyber1024':'KEM',
    'ML-KEM-512':'KEM', 'ML-KEM-768':'KEM', 'ML-KEM-1024':'KEM',
    'ML-DSA-44':'SIG',  'ML-DSA-65':'SIG',  'ML-DSA-87':'SIG',
    'Falcon-512':'SIG', 'Falcon-1024':'SIG',
}

pattern = re.compile(r'GEM5_RESULT algo=(.+?) op=(.+?) ns=(\d+)')
rows = []
with open(LOG) as f:
    for line in f:
        m = pattern.search(line)
        if m:
            algo, op, ns = m.group(1), m.group(2), int(m.group(3))
            cycles    = int(ns * CLOCK_HZ / 1e9)
            time_us   = ns / 1000
            energy_uj = time_us * ACTIVE_UW / 1e6
            energy_mj = energy_uj / 1000
            rows.append({
                'source':'gem5', 'algorithm':algo,
                'algo_type':ALGO_TYPE.get(algo,'UNK'),
                'operation':op,
                'security_level':SECURITY.get(algo,-1),
                'ns':ns, 'cycles':cycles,
                'time_us':round(time_us,2),
                'energy_uj':round(energy_uj,4),
                'energy_mj':round(energy_mj,6),
            })

if not rows:
    print("ERROR: No GEM5_RESULT lines found in", LOG)
    exit(1)

fields = ['source','algorithm','algo_type','operation','security_level',
          'ns','cycles','time_us','energy_uj','energy_mj']
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"Parsed {len(rows)} results -> {OUT}")
for r in rows:
    print(f"  {r['algorithm']:35s} {r['operation']:8s} {r['energy_mj']:10.4f} mJ  ({r['cycles']:,} cycles)")

"""
Before: make sure to run pqc_bench_v3.c first 
Now: python3 04_parse_gem5_results.py
Next: run scripts\03b_run_gem5.sh
"""

"""
Results:
root@debian:/home/user/scripts# python3 ./04_parse_gem5_results_v4.py
Parsed 33 results -> /home/user/gem5_results/gem5_pqc_results_v4.csv
  Kyber512                            KEYGEN       0.0033 mJ  (3,244 cycles)
  Kyber512                            ENCAP        0.0046 mJ  (4,476 cycles)
  Kyber512                            DECAP        0.0041 mJ  (3,946 cycles)
  Kyber768                            KEYGEN       0.0054 mJ  (5,254 cycles)
  Kyber768                            ENCAP        0.0074 mJ  (7,130 cycles)
  Kyber768                            DECAP        0.0066 mJ  (6,371 cycles)
  Kyber1024                           KEYGEN       0.0083 mJ  (8,034 cycles)
  Kyber1024                           ENCAP        0.0108 mJ  (10,428 cycles)
  Kyber1024                           DECAP        0.0099 mJ  (9,581 cycles)
  ML-KEM-512                          KEYGEN       0.0047 mJ  (4,553 cycles)
  ML-KEM-512                          ENCAP        0.0052 mJ  (4,998 cycles)
  ML-KEM-512                          DECAP        0.0063 mJ  (6,065 cycles)
  ML-KEM-768                          KEYGEN       0.0070 mJ  (6,802 cycles)
  ML-KEM-768                          ENCAP        0.0074 mJ  (7,188 cycles)
  ML-KEM-768                          DECAP        0.0090 mJ  (8,718 cycles)
  ML-KEM-1024                         KEYGEN       0.0107 mJ  (10,341 cycles)
  ML-KEM-1024                         ENCAP        0.0113 mJ  (10,995 cycles)
  ML-KEM-1024                         DECAP        0.0135 mJ  (13,137 cycles)
  ML-DSA-44                           KEYGEN       0.0171 mJ  (16,591 cycles)
  ML-DSA-44                           SIGN         0.0330 mJ  (31,978 cycles)
  ML-DSA-44                           VERIFY       0.0162 mJ  (15,662 cycles)
  ML-DSA-65                           KEYGEN       0.0298 mJ  (28,870 cycles)
  ML-DSA-65                           SIGN         0.0332 mJ  (32,197 cycles)
  ML-DSA-65                           VERIFY       0.0275 mJ  (26,657 cycles)
  ML-DSA-87                           KEYGEN       0.0511 mJ  (49,539 cycles)
  ML-DSA-87                           SIGN         0.0665 mJ  (64,521 cycles)
  ML-DSA-87                           VERIFY       0.0480 mJ  (46,507 cycles)
  Falcon-512                          KEYGEN       1.2898 mJ  (1,250,698 cycles)
  Falcon-512                          SIGN         0.0580 mJ  (56,193 cycles)
  Falcon-512                          VERIFY       0.0124 mJ  (12,053 cycles)
  Falcon-1024                         KEYGEN       4.1679 mJ  (4,041,577 cycles)
  Falcon-1024                         SIGN         0.1174 mJ  (113,873 cycles)
  Falcon-1024                         VERIFY       0.0241 mJ  (23,411 cycles)
"""