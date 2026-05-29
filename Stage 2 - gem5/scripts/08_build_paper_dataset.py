#!/usr/bin/env python3
# 08_build_paper_dataset.py
# Reads gem5_pqc_energy.csv and builds paper_dataset.csv with full metadata

import csv

GEM5_CSV = '/home/user/gem5_results/gem5_pqc_energy.csv'
OUT      = '/home/user/gem5_results/paper_dataset.csv'

META = {
    'Kyber512':    {'family': 'Kyber',   'type': 'KEM', 'sec': 1, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 800,  'sk': 1632, 'ct': 768},
    'Kyber768':    {'family': 'Kyber',   'type': 'KEM', 'sec': 3, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1184, 'sk': 2400, 'ct': 1088},
    'Kyber1024':   {'family': 'Kyber',   'type': 'KEM', 'sec': 5, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1568, 'sk': 3168, 'ct': 1568},
    'ML-KEM-512':  {'family': 'ML-KEM',  'type': 'KEM', 'sec': 1, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 800,  'sk': 1632, 'ct': 768},
    'ML-KEM-768':  {'family': 'ML-KEM',  'type': 'KEM', 'sec': 3, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1184, 'sk': 2400, 'ct': 1088},
    'ML-KEM-1024': {'family': 'ML-KEM',  'type': 'KEM', 'sec': 5, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1568, 'sk': 3168, 'ct': 1568},
    'ML-DSA-44':   {'family': 'ML-DSA',  'type': 'SIG', 'sec': 2, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1312, 'sk': 2528, 'ct': 2420},
    'ML-DSA-65':   {'family': 'ML-DSA',  'type': 'SIG', 'sec': 3, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 1952, 'sk': 4000, 'ct': 3309},
    'ML-DSA-87':   {'family': 'ML-DSA',  'type': 'SIG', 'sec': 5, 'lattice_dim': 256,  'uses_fpu': 0, 'pk': 2592, 'sk': 4864, 'ct': 4595},
    'Falcon-512':  {'family': 'Falcon',  'type': 'SIG', 'sec': 1, 'lattice_dim': 512,  'uses_fpu': 1, 'pk': 897,  'sk': 1281, 'ct': 666},
    'Falcon-1024': {'family': 'Falcon',  'type': 'SIG', 'sec': 5, 'lattice_dim': 1024, 'uses_fpu': 1, 'pk': 1793, 'sk': 2305, 'ct': 1280},
}

fields = ['algorithm','operation','family','type','security_level',
          'lattice_dim','uses_fpu','pk_bytes','sk_bytes','ct_or_sig_bytes',
          'instructions','time_us','energy_mj','iot_feasible']

rows = []

with open(GEM5_CSV, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        alg  = row['algorithm']
        op   = row['operation']
        m    = META.get(alg)
        if not m:
            print(f"  WARNING: no metadata for {alg}, skipping")
            continue

        time_us   = float(row['time_us'])
        energy_mj = float(row['energy_mj'])
        insts     = int(row['instructions'])
        iot       = 1 if time_us < 500_000 else 0   # under 500ms = feasible

        rows.append({
            'algorithm':       alg,
            'operation':       op,
            'family':          m['family'],
            'type':            m['type'],
            'security_level':  m['sec'],
            'lattice_dim':     m['lattice_dim'],
            'uses_fpu':        m['uses_fpu'],
            'pk_bytes':        m['pk'],
            'sk_bytes':        m['sk'],
            'ct_or_sig_bytes': m['ct'],
            'instructions':    insts,
            'time_us':         time_us,
            'energy_mj':       energy_mj,
            'iot_feasible':    iot,
        })

with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"Saved {len(rows)} rows to {OUT}")
print()
print(f"{'Algorithm':<14} {'Op':<8} {'Time(us)':>12} {'Energy(mJ)':>12} {'IoT':>5}")
print("-" * 55)
for r in rows:
    iot = "YES" if r['iot_feasible'] else "NO"
    print(f"{r['algorithm']:<14} {r['operation']:<8} "
          f"{r['time_us']:>12.2f} {r['energy_mj']:>12.6f} {iot:>5}")
    
"""
root@debian:/home/user/scripts# python3 08_build_paper_dataset.py 
Saved 33 rows to /home/user/gem5_results/paper_dataset.csv

Algorithm      Op           Time(us)   Energy(mJ)   IoT
-------------------------------------------------------
Kyber512       KEYGEN         526.24     0.034732   YES
Kyber512       ENCAP          596.19     0.039348   YES
Kyber512       DECAP          657.85     0.043418   YES
Kyber768       KEYGEN         557.90     0.036821   YES
Kyber768       ENCAP          669.31     0.044174   YES
Kyber768       DECAP          768.86     0.050745   YES
Kyber1024      KEYGEN         601.44     0.039695   YES
Kyber1024      ENCAP          764.36     0.050448   YES
Kyber1024      DECAP          914.08     0.060329   YES
ML-KEM-512     KEYGEN         546.80     0.036089   YES
ML-KEM-512     ENCAP          624.90     0.041243   YES
ML-KEM-512     DECAP          719.67     0.047498   YES
ML-KEM-768     KEYGEN         582.20     0.038425   YES
ML-KEM-768     ENCAP          694.52     0.045838   YES
ML-KEM-768     DECAP          830.75     0.054830   YES
ML-KEM-1024    KEYGEN         637.61     0.042082   YES
ML-KEM-1024    ENCAP          809.40     0.053420   YES
ML-KEM-1024    DECAP         1014.68     0.066969   YES
ML-DSA-44      KEYGEN         734.61     0.048484   YES
ML-DSA-44      SIGN          1234.30     0.081464   YES
ML-DSA-44      VERIFY        1479.00     0.097614   YES
ML-DSA-65      KEYGEN         926.52     0.061150   YES
ML-DSA-65      SIGN          1429.62     0.094355   YES
ML-DSA-65      VERIFY        1846.12     0.121844   YES
ML-DSA-87      KEYGEN        1249.52     0.082468   YES
ML-DSA-87      SIGN          2257.70     0.149008   YES
ML-DSA-87      VERIFY        2984.36     0.196968   YES
Falcon-512     KEYGEN       20017.38     1.321147   YES
Falcon-512     SIGN         20895.38     1.379095   YES
Falcon-512     VERIFY       21083.73     1.391526   YES
Falcon-1024    KEYGEN       63625.08     4.199255   YES
Falcon-1024    SIGN         65404.33     4.316686   YES
Falcon-1024    VERIFY       65770.15     4.340830   YES

"""