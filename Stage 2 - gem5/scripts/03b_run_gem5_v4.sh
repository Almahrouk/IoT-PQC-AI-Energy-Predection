#!/bin/bash
# 03b_run_gem5_v4.sh — sequential, one job at a time
echo "=== Running PQC bench under gem5 ARM ==="
mkdir -p /home/user/gem5_results
LOG=/home/user/gem5_results/pqc_raw_v4.log
> $LOG   # clear log

KEMS="Kyber512 Kyber768 Kyber1024 ML-KEM-512 ML-KEM-768 ML-KEM-1024"
SIGS="ML-DSA-44 ML-DSA-65 ML-DSA-87 Falcon-512 Falcon-1024"
KEM_OPS="KEYGEN ENCAP DECAP"
SIG_OPS="KEYGEN SIGN VERIFY"

run_one() {
    local algo=$1
    local op=$2
    local outdir=/home/user/gem5_results/${algo}_${op}
    local tmplog=${outdir}/stdout.txt
    mkdir -p $outdir

    echo "--- Running $algo $op ---"
    /home/user/gem5/build/ARM/gem5.opt \
        --outdir=$outdir \
        /home/user/gem5/configs/deprecated/example/se.py \
        --cmd=/home/user/pqc_bench_arm_v4 \
        --options="$algo $op" \
        --cpu-type=AtomicSimpleCPU \
        --mem-size=512MB \
        --output=$tmplog \
        2>/dev/null

    if [ -f "$tmplog" ]; then
        cat $tmplog >> $LOG
        grep "GEM5_RESULT" $tmplog || echo "  WARNING: no result for $algo $op"
    else
        echo "  WARNING: no output file for $algo $op"
    fi
}

for algo in $KEMS; do
    for op in $KEM_OPS; do
        run_one $algo $op
    done
done

for algo in $SIGS; do
    for op in $SIG_OPS; do
        run_one $algo $op
    done
done

echo ""
echo "=== Results ==="
grep "GEM5_RESULT" $LOG

echo ""
echo "=== Count ==="
grep -c "GEM5_RESULT" $LOG || echo "0"

# Can Ignored and go directly to 06_run_gem5_all_ops.sh
# Before: run 02b
# Next: run scripts\04b_parse_gem5_results.py

# root@debian:/home/user/scripts# ./03b_run_gem5_v4.sh
# === Running PQC bench under gem5 ARM ===
# --- Running Kyber512 KEYGEN ---
# gem5 Simulator System.  https://www.gem5.org
# gem5 is copyrighted software; use the --copyright option for details.

# gem5 version 25.1.0.1
# gem5 compiled May 19 2026 16:16:10
# gem5 started May 29 2026 07:00:03
# gem5 executing on debian, pid 39951
# command line: /home/user/gem5/build/ARM/gem5.opt --outdir=/home/user/gem5_results/Kyber512_KEYGEN /home/user/gem5/configs/deprecated/example/se.py --cmd=/home/user/pqc_bench_arm_v4 '--options=Kyber512 KEYGEN' --cpu-type=AtomicSimpleCPU --mem-size=512MB --output=/home/user/gem5_results/Kyber512_KEYGEN/stdout.txt

# Global frequency set at 1000000000000 ticks per second
# **** REAL SIMULATION ****
# Exiting @ tick 526243500 because exiting with last active thread context
# GEM5_RESULT algo=Kyber512 op=KEYGEN ns=50692
# --- Running Kyber512 ENCAP ---
# gem5 Simulator System.  https://www.gem5.org
# gem5 is copyrighted software; use the --copyright option for details.

# gem5 version 25.1.0.1
# gem5 compiled May 19 2026 16:16:10
# gem5 started May 29 2026 07:00:05
# gem5 executing on debian, pid 39959
# command line: /home/user/gem5/build/ARM/gem5.opt --outdir=/home/user/gem5_results/Kyber512_ENCAP /home/user/gem5/configs/deprecated/example/se.py --cmd=/home/user/pqc_bench_arm_v4 '--options=Kyber512 ENCAP' --cpu-type=AtomicSimpleCPU --mem-size=512MB --output=/home/user/gem5_results/Kyber512_ENCAP/stdout.txt

# Global frequency set at 1000000000000 ticks per second
# ######################################################################################
# **** REAL SIMULATION ****
# Exiting @ tick 65404333500 because exiting with last active thread context
# GEM5_RESULT algo=Falcon-1024 op=SIGN ns=1779266
# --- Running Falcon-1024 VERIFY ---
# gem5 Simulator System.  https://www.gem5.org
# gem5 is copyrighted software; use the --copyright option for details.

# gem5 version 25.1.0.1
# gem5 compiled May 19 2026 16:16:10
# gem5 started May 29 2026 07:04:06
# gem5 executing on debian, pid 40221
# command line: /home/user/gem5/build/ARM/gem5.opt --outdir=/home/user/gem5_results/Falcon-1024_VERIFY /home/user/gem5/configs/deprecated/example/se.py --cmd=/home/user/pqc_bench_arm_v4 '--options=Falcon-1024 VERIFY' --cpu-type=AtomicSimpleCPU --mem-size=512MB --output=/home/user/gem5_results/Falcon-1024_VERIFY/stdout.txt

# Global frequency set at 1000000000000 ticks per second
# **** REAL SIMULATION ****
# Exiting @ tick 65770152500 because exiting with last active thread context
# GEM5_RESULT algo=Falcon-1024 op=VERIFY ns=365812

# === Results ===
# GEM5_RESULT algo=Kyber512 op=KEYGEN ns=50692
# GEM5_RESULT algo=Kyber512 op=ENCAP ns=69952
# GEM5_RESULT algo=Kyber512 op=DECAP ns=61658
# GEM5_RESULT algo=Kyber768 op=KEYGEN ns=82102
# GEM5_RESULT algo=Kyber768 op=ENCAP ns=111415
# GEM5_RESULT algo=Kyber768 op=DECAP ns=99555
# GEM5_RESULT algo=Kyber1024 op=KEYGEN ns=125543
# GEM5_RESULT algo=Kyber1024 op=ENCAP ns=162944
# GEM5_RESULT algo=Kyber1024 op=DECAP ns=149714
# GEM5_RESULT algo=ML-KEM-512 op=KEYGEN ns=71152
# GEM5_RESULT algo=ML-KEM-512 op=ENCAP ns=78109
# GEM5_RESULT algo=ML-KEM-512 op=DECAP ns=94769
# GEM5_RESULT algo=ML-KEM-768 op=KEYGEN ns=106290
# GEM5_RESULT algo=ML-KEM-768 op=ENCAP ns=112327
# GEM5_RESULT algo=ML-KEM-768 op=DECAP ns=136230
# GEM5_RESULT algo=ML-KEM-1024 op=KEYGEN ns=161585
# GEM5_RESULT algo=ML-KEM-1024 op=ENCAP ns=171806
# GEM5_RESULT algo=ML-KEM-1024 op=DECAP ns=205277
# GEM5_RESULT algo=ML-DSA-44 op=KEYGEN ns=259235
# GEM5_RESULT algo=ML-DSA-44 op=SIGN ns=499660
# GEM5_RESULT algo=ML-DSA-44 op=VERIFY ns=244727
# GEM5_RESULT algo=ML-DSA-65 op=KEYGEN ns=451099
# GEM5_RESULT algo=ML-DSA-65 op=SIGN ns=503079
# GEM5_RESULT algo=ML-DSA-65 op=VERIFY ns=416519
# GEM5_RESULT algo=ML-DSA-87 op=KEYGEN ns=774061
# GEM5_RESULT algo=ML-DSA-87 op=SIGN ns=1008146
# GEM5_RESULT algo=ML-DSA-87 op=VERIFY ns=726681
# GEM5_RESULT algo=Falcon-512 op=KEYGEN ns=19542171
# GEM5_RESULT algo=Falcon-512 op=SIGN ns=878024
# GEM5_RESULT algo=Falcon-512 op=VERIFY ns=188329
# GEM5_RESULT algo=Falcon-1024 op=KEYGEN ns=63149643
# GEM5_RESULT algo=Falcon-1024 op=SIGN ns=1779266
# GEM5_RESULT algo=Falcon-1024 op=VERIFY ns=365812

# === Count ===
# 33
