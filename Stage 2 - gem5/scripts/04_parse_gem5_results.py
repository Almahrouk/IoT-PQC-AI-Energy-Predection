#!/usr/bin/env python3
# 04_parse_gem5_results.py
import re, csv, os

LOG  = '/home/user/gem5_results/pqc_raw.log'
OUT  = '/home/user/gem5_results/gem5_pqc_results.csv'

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
Next: run scripts\03_run_gem5.sh
"""

"""
Results:
root@debian:/home/user/scripts# python3 04_parse_gem5_results.py 
Parsed 33 results -> /home/user/gem5_results/gem5_pqc_results.csv
  Kyber512                            KEYGEN       0.0033 mJ  (3,244 cycles)
  Kyber512                            ENCAP        0.0046 mJ  (4,476 cycles)
  Kyber512                            DECAP        0.0041 mJ  (3,946 cycles)
  Kyber768                            KEYGEN       0.0054 mJ  (5,205 cycles)
  Kyber768                            ENCAP        0.0073 mJ  (7,099 cycles)
  Kyber768                            DECAP        0.0065 mJ  (6,340 cycles)
  Kyber1024                           KEYGEN       0.0085 mJ  (8,198 cycles)
  Kyber1024                           ENCAP        0.0109 mJ  (10,611 cycles)
  Kyber1024                           DECAP        0.0101 mJ  (9,764 cycles)
  ML-KEM-512                          KEYGEN       0.0042 mJ  (4,034 cycles)
  ML-KEM-512                          ENCAP        0.0046 mJ  (4,497 cycles)
  ML-KEM-512                          DECAP        0.0057 mJ  (5,565 cycles)
  ML-KEM-768                          KEYGEN       0.0070 mJ  (6,761 cycles)
  ML-KEM-768                          ENCAP        0.0074 mJ  (7,184 cycles)
  ML-KEM-768                          DECAP        0.0090 mJ  (8,715 cycles)
  ML-KEM-1024                         KEYGEN       0.0106 mJ  (10,303 cycles)
  ML-KEM-1024                         ENCAP        0.0113 mJ  (10,995 cycles)
  ML-KEM-1024                         DECAP        0.0135 mJ  (13,136 cycles)
  ML-DSA-44                           KEYGEN       0.0171 mJ  (16,543 cycles)
  ML-DSA-44                           SIGN         0.0330 mJ  (31,969 cycles)
  ML-DSA-44                           VERIFY       0.0162 mJ  (15,661 cycles)
  ML-DSA-65                           KEYGEN       0.0297 mJ  (28,822 cycles)
  ML-DSA-65                           SIGN         0.0995 mJ  (96,499 cycles)
  ML-DSA-65                           VERIFY       0.0275 mJ  (26,659 cycles)
  ML-DSA-87                           KEYGEN       0.0510 mJ  (49,497 cycles)
  ML-DSA-87                           SIGN         0.0672 mJ  (65,162 cycles)
  ML-DSA-87                           VERIFY       0.0479 mJ  (46,489 cycles)
  Falcon-512                          KEYGEN       3.2350 mJ  (3,136,969 cycles)
  Falcon-512                          SIGN         0.0583 mJ  (56,574 cycles)
  Falcon-512                          VERIFY       0.0124 mJ  (12,054 cycles)
  Falcon-1024                         KEYGEN       4.5205 mJ  (4,383,471 cycles)
  Falcon-1024                         SIGN         0.1177 mJ  (114,095 cycles)
  Falcon-1024                         VERIFY       0.0242 mJ  (23,424 cycles)
"""