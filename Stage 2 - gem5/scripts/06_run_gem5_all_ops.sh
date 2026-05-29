#!/bin/bash
# 06_run_gem5_all_ops.sh
# Runs gem5 once per algo/op — each run gives isolated simInsts count
# simTicks from gem5 stats -> more accurate than clock_gettime
# Run it instead of 03b_run_gem5_v4.sh

OUTBASE=/home/user/gem5_results/per_op
RESULTS=/home/user/gem5_results/raw_insts.txt
mkdir -p $OUTBASE
> $RESULTS

KEMS="Kyber512 Kyber768 Kyber1024 ML-KEM-512 ML-KEM-768 ML-KEM-1024"
KEM_OPS="KEYGEN ENCAP DECAP"
SIGS="ML-DSA-44 ML-DSA-65 ML-DSA-87 Falcon-512 Falcon-1024"
SIG_OPS="KEYGEN SIGN VERIFY"

run_one() {
    local algo=$1
    local op=$2
    local tag="${algo}_${op}"
    local outdir=$OUTBASE/$tag
    mkdir -p $outdir

    echo -n "Running $tag ... "

    /home/user/gem5/build/ARM/gem5.opt \
      --outdir=$outdir \
      /home/user/gem5/configs/deprecated/example/se.py \
      --cmd=/home/user/pqc_bench_arm_v4 \
      --options="$algo $op" \
      --cpu-type=AtomicSimpleCPU \
      --mem-size=512MB \
      --output=$outdir/output.log \
      2>$outdir/gem5.log

    INSTS=$(grep "^simInsts" $outdir/stats.txt 2>/dev/null | awk '{print $2}')
    TICKS=$(grep "^simTicks" $outdir/stats.txt 2>/dev/null | awk '{print $2}')
    echo "insts=$INSTS ticks=$TICKS"
    echo "$algo $op $INSTS $TICKS" >> $RESULTS
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
echo "=== All done. Results in $RESULTS ==="
cat $RESULTS

# Before: run 02b
# Next: run scripts\04b_parse_gem5_results.py