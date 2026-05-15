#ifndef PQC_STUB_H
#define PQC_STUB_H

/* PQC timing stubs (microseconds) derived from gem5 ARM Cortex-M4 benchmarks.
   Replace these values with your actual gem5 measurements once validated. */

typedef enum {
  PQC_KYBER_512 = 0,
  PQC_KYBER_768,
  PQC_KYBER_1024,
  PQC_DILITHIUM_2,
  PQC_DILITHIUM_3,
  PQC_DILITHIUM_5,
  PQC_FALCON_512,
  PQC_FALCON_1024,
  PQC_SPHINCS_128,
  PQC_SPHINCS_192,
  PQC_SPHINCS_256,
} pqc_algo_t;

typedef enum {
  PQC_OP_KEYGEN = 0,
  PQC_OP_ENCAP,
  PQC_OP_DECAP,
  PQC_OP_SIGN,
  PQC_OP_VERIFY,
} pqc_op_t;

/* us_per_op[algo][op] — placeholder values from pqm4 published benchmarks */
static const uint32_t pqc_us_per_op[11][5] = {
  /* KEYGEN   ENCAP    DECAP    SIGN     VERIFY */
  {  50200,   62100,   71300,       0,       0 }, /* Kyber-512   */
  {  82400,  101200,  114700,       0,       0 }, /* Kyber-768   */
  { 121600,  146900,  164200,       0,       0 }, /* Kyber-1024  */
  {  87300,       0,       0,  306500,   89200 }, /* Dilithium-2 */
  { 128400,       0,       0,  476100,  130600 }, /* Dilithium-3 */
  { 196200,       0,       0,  691300,  194700 }, /* Dilithium-5 */
  { 212400,       0,       0,  482100,  146300 }, /* FALCON-512  */
  { 418700,       0,       0,  942600,  286500 }, /* FALCON-1024 */
  {1120000,       0,       0, 8340000,  846000 }, /* SPHINCS-128 */
  {1680000,       0,       0,13200000, 1240000 }, /* SPHINCS-192 */
  {2340000,       0,       0,22100000, 1760000 }, /* SPHINCS-256 */
};

static const char *pqc_algo_name[] = {
  "KYBER512","KYBER768","KYBER1024",
  "DILITH2","DILITH3","DILITH5",
  "FALCON512","FALCON1024",
  "SPHINCS128","SPHINCS192","SPHINCS256"
};

static const char *pqc_op_name[] = {
  "KEYGEN","ENCAP","DECAP","SIGN","VERIFY"
};

#define PQC_SIMULATE_OP(algo, op, clock_ticks_out) \
  do { \
    uint32_t _us = pqc_us_per_op[(algo)][(op)]; \
    (clock_ticks_out) = (_us * CLOCK_SECOND) / 1000000UL; \
    clock_delay_usec(_us); \
  } while(0)

#endif /* PQC_STUB_H */
