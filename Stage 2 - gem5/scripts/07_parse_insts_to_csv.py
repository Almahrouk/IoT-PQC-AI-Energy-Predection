#!/usr/bin/env python3
# 07_parse_insts_to_csv.py
# Converts raw_insts.txt to energy CSV using ARM Cortex-M4 power model
#
# Energy model:
#   cycles    = ticks / (1000000000000 / CLOCK_HZ)
#             = ticks * CLOCK_HZ / 1e12
#   time_us   = cycles / CLOCK_HZ * 1e6
#   energy_uj = time_us * ACTIVE_UW / 1e6
#   energy_mj = energy_uj / 1000

import csv
import os

RAW    = '/home/user/gem5_results/raw_insts.txt'
OUT    = '/home/user/gem5_results/gem5_pqc_energy.csv'

# ARM Cortex-M4 model
CLOCK_HZ   = 64_000_000      # 64 MHz
GEM5_FREQ  = 1_000_000_000_000  # gem5 ticks per second (1 THz)
ACTIVE_UW  = 66_000           # 66 mW active power (20mA x 3.3V)

SECURITY = {
    'Kyber512':    1, 'Kyber768':    3, 'Kyber1024':   5,
    'ML-KEM-512':  1, 'ML-KEM-768':  3, 'ML-KEM-1024': 5,
    'ML-DSA-44':   2, 'ML-DSA-65':   3, 'ML-DSA-87':   5,
    'Falcon-512':  1, 'Falcon-1024': 5,
}

ALGO_TYPE = {
    'Kyber512':   'KEM', 'Kyber768':   'KEM', 'Kyber1024':  'KEM',
    'ML-KEM-512': 'KEM', 'ML-KEM-768': 'KEM', 'ML-KEM-1024':'KEM',
    'ML-DSA-44':  'SIG', 'ML-DSA-65':  'SIG', 'ML-DSA-87':  'SIG',
    'Falcon-512': 'SIG', 'Falcon-1024':'SIG',
}

# For cumulative ops (each run includes previous ops), compute delta
# raw_insts.txt format: algo op insts ticks
# The v4 binary runs ONE op per invocation, so values are already isolated
# EXCEPT: ENCAP includes KEYGEN, DECAP includes KEYGEN+ENCAP
# We need to subtract to get isolated op costs

# Load all raw rows
raw = {}
with open(RAW) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 4:
            continue
        algo, op, insts, ticks = parts[0], parts[1], int(parts[2]), int(parts[3])
        raw[(algo, op)] = (insts, ticks)

def get_isolated(algo, op, is_kem):
    insts, ticks = raw[(algo, op)]
    # if is_kem:
    #     if op == 'KEYGEN':
    #         return insts, ticks
    #     elif op == 'ENCAP':
    #         ki, kt = raw[(algo, 'KEYGEN')]
    #         return insts - ki, ticks - kt
    #     elif op == 'DECAP':
    #         ei, et = raw[(algo, 'ENCAP')]
    #         return insts - ei, ticks - et
    # else:  # SIG
    #     if op == 'KEYGEN':
    #         return insts, ticks
    #     elif op == 'SIGN':
    #         ki, kt = raw[(algo, 'KEYGEN')]
    #         return insts - ki, ticks - kt
    #     elif op == 'VERIFY':
    #         ei, et = raw[(algo, 'SIGN')]
    #         return insts - ei, ticks - et
    return insts, ticks

rows = []
order = [
    ('Kyber512',    'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('Kyber768',    'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('Kyber1024',   'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('ML-KEM-512',  'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('ML-KEM-768',  'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('ML-KEM-1024', 'KEM',  ['KEYGEN','ENCAP','DECAP']),
    ('ML-DSA-44',   'SIG',  ['KEYGEN','SIGN','VERIFY']),
    ('ML-DSA-65',   'SIG',  ['KEYGEN','SIGN','VERIFY']),
    ('ML-DSA-87',   'SIG',  ['KEYGEN','SIGN','VERIFY']),
    ('Falcon-512',  'SIG',  ['KEYGEN','SIGN','VERIFY']),
    ('Falcon-1024', 'SIG',  ['KEYGEN','SIGN','VERIFY']),
]

for algo, atype, ops in order:
    is_kem = (atype == 'KEM')
    for op in ops:
        if (algo, op) not in raw:
            continue
        insts, ticks = get_isolated(algo, op, is_kem)
        cycles   = ticks * CLOCK_HZ / GEM5_FREQ
        time_us  = cycles / CLOCK_HZ * 1e6
        energy_uj = time_us * ACTIVE_UW / 1e6
        energy_mj = energy_uj / 1000

        rows.append({
            'source':         'gem5',
            'algorithm':      algo,
            'algo_type':      atype,
            'operation':      op,
            'security_level': SECURITY.get(algo, -1),
            'instructions':   insts,
            'ticks':          ticks,
            'cycles':         round(cycles, 2),
            'time_us':        round(time_us, 4),
            'energy_uj':      round(energy_uj, 4),
            'energy_mj':      round(energy_mj, 6),
        })

fields = ['source','algorithm','algo_type','operation','security_level',
          'instructions','ticks','cycles','time_us','energy_uj','energy_mj']

with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"Parsed {len(rows)} rows -> {OUT}")
print()
print(f"{'Algorithm':<16} {'Op':<8} {'Instructions':>14} {'Time (us)':>12} {'Energy (mJ)':>12}")
print("-" * 66)
for r in rows:
    print(f"{r['algorithm']:<16} {r['operation']:<8} "
          f"{r['instructions']:>14,} {r['time_us']:>12.2f} {r['energy_mj']:>12.6f}")

# Before: run 06_run_gem5_all_ops.sh
# Next: 

"""
root@debian:/home/user/scripts# python3 07_parse_insts_to_csv.py 
Parsed 33 rows -> /home/user/gem5_results/gem5_pqc_energy.csv

Algorithm        Op         Instructions    Time (us)  Energy (mJ)
------------------------------------------------------------------
Kyber512         KEYGEN        1,004,680       526.24     0.034732
Kyber512         ENCAP         1,125,732       596.19     0.039348
Kyber512         DECAP         1,230,556       657.85     0.043418
Kyber768         KEYGEN        1,058,582       557.90     0.036821
Kyber768         ENCAP         1,251,368       669.31     0.044174
Kyber768         DECAP         1,420,996       768.86     0.050745
Kyber1024        KEYGEN        1,131,129       601.44     0.039695
Kyber1024        ENCAP         1,411,418       764.36     0.050448
Kyber1024        DECAP         1,666,035       914.08     0.060329
ML-KEM-512       KEYGEN        1,046,730       546.80     0.036089
ML-KEM-512       ENCAP         1,187,481       624.90     0.041243
ML-KEM-512       DECAP         1,358,552       719.67     0.047498
ML-KEM-768       KEYGEN        1,109,614       582.20     0.038425
ML-KEM-768       ENCAP         1,311,387       694.52     0.045838
ML-KEM-768       DECAP         1,556,727       830.75     0.054830
ML-KEM-1024      KEYGEN        1,209,103       637.61     0.042082
ML-KEM-1024      ENCAP         1,517,961       809.40     0.053420
ML-KEM-1024      DECAP         1,888,189      1014.68     0.066969
ML-DSA-44        KEYGEN        1,383,960       734.61     0.048484
ML-DSA-44        SIGN          2,276,270      1234.30     0.081464
ML-DSA-44        VERIFY        2,717,016      1479.00     0.097614
ML-DSA-65        KEYGEN        1,729,955       926.52     0.061150
ML-DSA-65        SIGN          2,633,678      1429.62     0.094355
ML-DSA-65        VERIFY        3,385,397      1846.12     0.121844
ML-DSA-87        KEYGEN        2,311,900      1249.52     0.082468
ML-DSA-87        SIGN          4,125,784      2257.70     0.149008
ML-DSA-87        VERIFY        5,437,585      2984.36     0.196968
Falcon-512       KEYGEN       39,296,848     20017.38     1.321147
Falcon-512       SIGN         40,755,364     20895.38     1.379095
Falcon-512       VERIFY       41,104,846     21083.73     1.391526
Falcon-1024      KEYGEN      124,847,496     63625.08     4.199255
Falcon-1024      SIGN        127,775,399     65404.33     4.316686
Falcon-1024      VERIFY      128,457,057     65770.15     4.340830
"""