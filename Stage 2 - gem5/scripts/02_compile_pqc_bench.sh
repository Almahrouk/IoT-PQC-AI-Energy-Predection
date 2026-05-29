#!/bin/bash
# 02_compile_pqc_bench.sh
set -e
echo "=== Compiling pqc_bench_v3 for AArch64 ==="
aarch64-linux-gnu-gcc -O2 -static \
    -I/home/user/liboqs/build-aarch64/install/include \
    /home/user/pqc_bench_v3.c \
    -o /home/user/pqc_bench_arm_v3 \
    -L/home/user/liboqs/build-aarch64/install/lib -loqs -lm
echo "=== Done ==="
file /home/user/pqc_bench_arm_v3
ls -lh /home/user/pqc_bench_arm_v3

# Brfore: run scripts\01_rebuild_liboqs_arm.sh
# Next (Optinal): run scripts\02b_compile_v4.sh
# Next (to get Results): ...

# + Source File
# /home/user/pqc_bench_v3.c \ 
# benchmark C program, measures:
# 1. key generation
# 2. encapsulation
# 3. decapsulation
# 4. signing
# 5. verification
# 6. timing
# 7. energy estimates
# for PQC algorithms.
# ==========================
# + Link the ARM liboqs Library
# /home/user/liboqs/build-arm/install/lib/liboqs.a \
# Links ARM-compiled static library.
# This contains PQC implementations like:
# 1. ML-KEM (Kyber)
# 2. ML-DSA (Dilithium)
# 3. Falcon
# 4. SPHINCS+