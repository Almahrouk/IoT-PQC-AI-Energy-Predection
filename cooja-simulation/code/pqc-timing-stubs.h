/**
 * pqc-timing-stubs.h
 * PQC Algorithm Timing Stubs for Contiki-NG / Cooja Simulation
 *
 * Cycle counts from pqm4 benchmarks (ARM Cortex-M4):
 *   Kannwischer et al., IACR ePrint 2024/112
 *
 * Energy model: CC2538 @ 32 MHz, 20 mA active, 3.3 V
 *   time_us  = cycles * 1000000 / CLOCK_HZ
 *   energy_uj = time_us * 66 / 1000   (66 mW active power)
 */

#ifndef PQC_TIMING_STUBS_H
#define PQC_TIMING_STUBS_H

#include <stdint.h>
#include <stdio.h>

/* CC2538 clock and power model */
#define PQC_CLOCK_HZ      32000000UL   /* 32 MHz */
#define PQC_ACTIVE_UW     66000UL      /* 20 mA * 3.3 V * 1000 */

/* ── Algorithm identifiers ── */
#define PQC_ALG_KYBER512      0
#define PQC_ALG_KYBER768      1
#define PQC_ALG_KYBER1024     2
#define PQC_ALG_DILITHIUM2    3
#define PQC_ALG_DILITHIUM3    4
#define PQC_ALG_DILITHIUM5    5
#define PQC_ALG_FALCON512     6
#define PQC_ALG_FALCON1024    7
#define PQC_ALG_SPHINCS128    8
#define PQC_ALG_SPHINCS192    9
#define PQC_ALG_SPHINCS256   10

/* ── Operation identifiers ── */
#define PQC_OP_KEYGEN    0
#define PQC_OP_ENCAP     1
#define PQC_OP_DECAP     2
#define PQC_OP_SIGN      1
#define PQC_OP_VERIFY    2

/* ── Cycle counts table [algorithm][operation] ── */
/* Source: pqm4 benchmarks, ARM Cortex-M4 @ 64 MHz, scaled to 32 MHz */
static const uint32_t PQC_CYCLES[11][3] = {
/*  Algorithm         KEYGEN      ENCAP/SIGN   DECAP/VERIFY  */
/* Kyber-512   */ {  1700000,    1900000,    2000000 },
/* Kyber-768   */ {  2600000,    2900000,    3100000 },
/* Kyber-1024  */ {  3700000,    4100000,    4400000 },
/* Dilithium-2 */ {  2200000,    4900000,    2300000 },
/* Dilithium-3 */ {  3500000,    7800000,    3700000 },
/* Dilithium-5 */ {  5000000,   11000000,    5300000 },
/* FALCON-512  */ { 10000000,    3000000,     700000 },
/* FALCON-1024 */ { 20000000,    5800000,    1300000 },
/* SPHINCS+-128*/ {  9000000,  200000000,    8000000 },
/* SPHINCS+-192*/ { 17000000,  370000000,   15000000 },
/* SPHINCS+-256*/ { 24000000,  540000000,   22000000 },
};

static const char *PQC_ALG_NAMES[] = {
    "KYBER512","KYBER768","KYBER1024",
    "DILITHIUM2","DILITHIUM3","DILITHIUM5",
    "FALCON512","FALCON1024",
    "SPHINCS128","SPHINCS192","SPHINCS256"
};

static const char *PQC_OP_NAMES[] = {
    "KEYGEN","ENCAP_SIGN","DECAP_VERIFY"
};

static const char *PQC_TYPE_NAMES[] = {
    "KEM","KEM","KEM",
    "SIG","SIG","SIG",
    "SIG","SIG",
    "SIG","SIG","SIG"
};

/**
 * pqc_simulate_op()
 * Simulates a PQC operation and emits a structured PQC_LOG line.
 *
 * Output format (captured by Cooja LogListener):
 *   PQC_LOG node=<id> algo=<name> type=<KEM|SIG> op=<name>
 *            cycles=<n> time_us=<n> energy_uj=<n>
 */
static inline void pqc_simulate_op(uint8_t node_id,
                                    uint8_t alg,
                                    uint8_t op)
{
    uint32_t cycles   = PQC_CYCLES[alg][op];
    uint32_t time_us  = (uint32_t)((uint64_t)cycles * 1000000UL
                                   / PQC_CLOCK_HZ);
    uint32_t energy_uj = (uint32_t)((uint64_t)time_us
                                    * PQC_ACTIVE_UW / 1000000UL);

    printf("PQC_LOG node=%u algo=%s type=%s op=%s "
           "cycles=%lu time_us=%lu energy_uj=%lu\n",
           (unsigned)node_id,
           PQC_ALG_NAMES[alg],
           PQC_TYPE_NAMES[alg],
           PQC_OP_NAMES[op],
           (unsigned long)cycles,
           (unsigned long)time_us,
           (unsigned long)energy_uj);
}

#endif /* PQC_TIMING_STUBS_H */
