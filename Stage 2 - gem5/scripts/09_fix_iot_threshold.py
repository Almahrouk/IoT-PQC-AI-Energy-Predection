import csv

# IoT feasibility rules:
# KEYGEN: must complete in < 10ms (10000 us) for rekeying
# ENCAP/DECAP/SIGN/VERIFY: must complete in < 100ms (100000 us) for handshake

THRESHOLDS = {
    'KEYGEN': 10000,
    'ENCAP':  100000,
    'DECAP':  100000,
    'SIGN':   100000,
    'VERIFY': 100000,
}

inp = '/home/user/gem5_results/paper_dataset.csv'
out = '/home/user/gem5_results/paper_dataset_fixed.csv'

rows = []
with open(inp) as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    for r in reader:
        op = r['operation']
        threshold = THRESHOLDS.get(op, 10000)
        r['iot_feasible'] = 1 if float(r['time_us']) < threshold else 0
        rows.append(r)

with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"{'Algorithm':<14} {'Op':<8} {'Time(us)':>12} {'Energy(mJ)':>12} {'IoT':>5}")
print("-" * 55)
for r in rows:
    iot = "YES" if int(r['iot_feasible']) else "NO "
    print(f"{r['algorithm']:<14} {r['operation']:<8} {float(r['time_us']):>12.2f} {float(r['energy_mj']):>12.6f} {iot:>5}")

print(f"\nSaved to {out}")

"""
root@debian:/home/user/scripts# python3 09_fix_iot_threshold.py 
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
Falcon-512     KEYGEN       20017.38     1.321147   NO 
Falcon-512     SIGN         20895.38     1.379095   YES
Falcon-512     VERIFY       21083.73     1.391526   YES
Falcon-1024    KEYGEN       63625.08     4.199255   NO 
Falcon-1024    SIGN         65404.33     4.316686   YES
Falcon-1024    VERIFY       65770.15     4.340830   YES

Saved to /home/user/gem5_results/paper_dataset_fixed.csv

"""