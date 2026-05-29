#!/bin/bash
# 03_run_gem5.sh — AtomicSimpleCPU, no cycle counter needed
echo "=== Running PQC bench under gem5 ARM ==="
mkdir -p /home/user/gem5_results

/home/user/gem5/build/ARM/gem5.opt \
  --outdir=/home/user/gem5_results \
  /home/user/gem5/configs/deprecated/example/se.py \
  --cmd=/home/user/pqc_bench_arm_v3 \
  --cpu-type=AtomicSimpleCPU \
  --mem-size=512MB \
  --output=/home/user/gem5_results/pqc_raw.log

echo ""
echo "=== Raw output ==="
cat /home/user/gem5_results/pqc_raw.log
echo ""
echo "=== Total instructions from stats ==="
grep "simInsts\|sim_insts\|committedInsts" /home/user/gem5_results/stats.txt | head -5



"""
root@debian:/home/user/scripts# aarch64-linux-gnu-gcc -O2 -static     -I/home/user/liboqs/build-aarch64/install/include     /home/user/pqc_bench_v3.c     -o /home/user/pqc_bench_arm_v3     -L/home/user/liboqs/build-aarch64/install/lib -loqs -lm
root@debian:/home/user/scripts# ./03_run_gem5.sh 
=== Running PQC bench under gem5 ARM ===
gem5 Simulator System.  https://www.gem5.org
gem5 is copyrighted software; use the --copyright option for details.

gem5 version 25.1.0.1
gem5 compiled May 19 2026 16:16:10
gem5 started May 29 2026 05:09:10
gem5 executing on debian, pid 25851
command line: /home/user/gem5/build/ARM/gem5.opt --outdir=/home/user/gem5_results /home/user/gem5/configs/deprecated/example/se.py --cmd=/home/user/pqc_bench_arm_v3 --cpu-type=AtomicSimpleCPU --mem-size=512MB --output=/home/user/gem5_results/pqc_raw.log

warn: The se.py script is deprecated. It will be removed in future releases of  gem5.
warn: Base 10 memory/cache size 512MB will be cast to base 2 size 512MiB.
Global frequency set at 1000000000000 ticks per second
src/mem/dram_interface.cc:690: warn: DRAM device capacity (8192 Mbytes) does not match the address range assigned (512 Mbytes)
src/base/statistics.hh:279: warn: One of the stats is a legacy stat. Legacy stat is a stat that does not belong to any statistics::Group. Legacy stat is deprecated.
system.remote_gdb: Listening for connections on port 7000
**** REAL SIMULATION ****
src/arch/arm/insts/pseudo.cc:174: warn: 	instruction 'bti' unimplemented
src/sim/syscall_emul.cc:86: warn: ignoring syscall set_robust_list(...)
src/sim/syscall_emul.cc:97: warn: ignoring syscall rseq(...)
      (further warnings will be suppressed)
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/syscall_emul.cc:86: warn: ignoring syscall mprotect(...)
src/arch/arm/insts/pseudo.cc:174: warn: 	instruction 'unallocated_hint' unimplemented
src/arch/arm/insts/pseudo.cc:174: warn: 	instruction 'bti' unimplemented
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
src/sim/mem_state.cc:443: info: Increasing stack size by one page.
Exiting @ tick 129164456000 because exiting with last active thread context

=== Raw output ===
GEM5_BENCH_START
GEM5_RESULT algo=Kyber512 op=KEYGEN ns=50692
GEM5_RESULT algo=Kyber512 op=ENCAP ns=69951
GEM5_RESULT algo=Kyber512 op=DECAP ns=61658
GEM5_RESULT algo=Kyber768 op=KEYGEN ns=81343
GEM5_RESULT algo=Kyber768 op=ENCAP ns=110934
GEM5_RESULT algo=Kyber768 op=DECAP ns=99074
GEM5_RESULT algo=Kyber1024 op=KEYGEN ns=128103
GEM5_RESULT algo=Kyber1024 op=ENCAP ns=165802
GEM5_RESULT algo=Kyber1024 op=DECAP ns=152574
GEM5_RESULT algo=ML-KEM-512 op=KEYGEN ns=63036
GEM5_RESULT algo=ML-KEM-512 op=ENCAP ns=70281
GEM5_RESULT algo=ML-KEM-512 op=DECAP ns=86964
GEM5_RESULT algo=ML-KEM-768 op=KEYGEN ns=105645
GEM5_RESULT algo=ML-KEM-768 op=ENCAP ns=112262
GEM5_RESULT algo=ML-KEM-768 op=DECAP ns=136180
GEM5_RESULT algo=ML-KEM-1024 op=KEYGEN ns=160995
GEM5_RESULT algo=ML-KEM-1024 op=ENCAP ns=171811
GEM5_RESULT algo=ML-KEM-1024 op=DECAP ns=205263
GEM5_RESULT algo=ML-DSA-44 op=KEYGEN ns=258497
GEM5_RESULT algo=ML-DSA-44 op=SIGN ns=499528
GEM5_RESULT algo=ML-DSA-44 op=VERIFY ns=244710
GEM5_RESULT algo=ML-DSA-65 op=KEYGEN ns=450357
GEM5_RESULT algo=ML-DSA-65 op=SIGN ns=1507805
GEM5_RESULT algo=ML-DSA-65 op=VERIFY ns=416552
GEM5_RESULT algo=ML-DSA-87 op=KEYGEN ns=773404
GEM5_RESULT algo=ML-DSA-87 op=SIGN ns=1018171
GEM5_RESULT algo=ML-DSA-87 op=VERIFY ns=726403
GEM5_RESULT algo=Falcon-512 op=KEYGEN ns=49015156
GEM5_RESULT algo=Falcon-512 op=SIGN ns=883977
GEM5_RESULT algo=Falcon-512 op=VERIFY ns=188357
GEM5_RESULT algo=Falcon-1024 op=KEYGEN ns=68491737
GEM5_RESULT algo=Falcon-1024 op=SIGN ns=1782742
GEM5_RESULT algo=Falcon-1024 op=VERIFY ns=366007
GEM5_BENCH_END

=== Total instructions from stats ===
simInsts                                    246728086                       # Number of instructions simulated (Count)
root@debian:/home/user/scripts# 
"""
