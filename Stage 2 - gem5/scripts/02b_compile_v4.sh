#!/bin/bash
set -e
echo "=== Compiling pqc_bench_v4 for AArch64 ==="
aarch64-linux-gnu-gcc \
  -static -O2 \
  /home/user/pqc_bench_v4.c \
  -I/home/user/liboqs/build-aarch64/install/include \
  /home/user/liboqs/build-aarch64/install/lib/liboqs.a \
  -lm -lpthread \
  -o /home/user/pqc_bench_arm_v4
echo "=== Done ==="
file /home/user/pqc_bench_arm_v4

# Brfore: run scripts\01_rebuild_liboqs_arm.sh Nessusary 
# Brfore (Optinal): run scripts\02_compile_pqc_bench.sh
# Next: 
# Next (to get Results): ...

# Old Code:
# arm-linux-gnueabihf-gcc \

# Run results:
# root@debian:/home/user/scripts# ./02_compile_pqc_bench.sh 
# === Compiling pqc_bench_v3 for ARM ===
# === Done ===
# /home/user/pqc_bench_arm_v3: ELF 32-bit LSB executable, ARM, EABI5 version 1 (GNU/Linux), statically linked, BuildID[sha1]=6f449b638ad5a9bf7287972578a4398452c9bfb4, for GNU/Linux 3.2.0, not stripped
# -rwxrwxr-x 1 root root 8.3M May 29 05:42 /home/user/pqc_bench_arm_v3
