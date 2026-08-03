#ifndef PQC_STUB_H
#define PQC_STUB_H

/*
 * PQC timing stubs, derived from real pqm4 published benchmark cycle
 * counts — NOT hand-estimated placeholders.
 *
 * SOURCE: Kannwischer, Rijneveld, Schwabe, Stoffelen, "pqm4: Testing and
 * Benchmarking NIST PQC on ARM Cortex-M4", Cryptology ePrint 2019/844.
 * https://eprint.iacr.org/2019/844
 *
*/

#ifndef PQC_BENCH_FREQ_MHZ
#define PQC_BENCH_FREQ_MHZ 24u
#endif

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
  PQC_ALGO_COUNT
} pqc_algo_t;

typedef enum {
  PQC_OP_KEYGEN = 0,
  PQC_OP_ENCAP,   /* KEMs only; 0 for signature schemes */
  PQC_OP_DECAP,   /* KEMs only; 0 for signature schemes */
  PQC_OP_SIGN,    /* signature schemes only; 0 for KEMs */
  PQC_OP_VERIFY,
  PQC_OP_COUNT
} pqc_op_t;


static const uint32_t pqc_cycles_per_op[PQC_ALGO_COUNT][PQC_OP_COUNT] = {
  /*                  KEYGEN       ENCAP      DECAP        SIGN       VERIFY */
  /* Kyber-512   */ {   649678,     884848,    985258,          0,         0 }, /* kyber512 clean */
  /* Kyber-768   */ {  1196692,    1489909,   1613744,          0,         0 }, /* kyber768 clean */
  /* Kyber-1024  */ {  1891737,    2254703,   2407858,          0,         0 }, /* kyber1024 clean */
  /* Dilithium-2 */ {  1752194,          0,         0,    9342087,   2035881 }, /* dilithium2 clean */
  /* Dilithium-3 */ {  2733423,          0,         0,   14885750,   2946998 }, /* dilithium3 clean */
  /* Dilithium-5 */ {  3647486,          0,         0,   13615651,   4035259 }, /* (*) dilithium4 clean */
  /* Falcon-512  */ { 229088624,         0,         0,   62225400,    473964 }, /* falcon512 opt-ct */
  /* Falcon-1024 */ { 690147063,         0,         0,  136596407,    978558 }, /* falcon1024 opt-ct */
  /* SPHINCS-128 */ {  16552135,         0,         0,  521963206,  20850719 }, /* (*) sphincs-sha256-128f-simple */
  /* SPHINCS-192 */ {  24355501,         0,         0,  687693467,  35097457 }, /* (*) sphincs-sha256-192f-simple */
  /* SPHINCS-256 */ {  64184968,         0,         0, 1554168401,  36182488 }, /* (*) sphincs-sha256-256f-simple */
};

static const char *pqc_algo_name[PQC_ALGO_COUNT] = {
  "KYBER512","KYBER768","KYBER1024",
  "DILITH2","DILITH3","DILITH5",
  "FALCON512","FALCON1024",
  "SPHINCS128","SPHINCS192","SPHINCS256"
};

static const char *pqc_op_name[PQC_OP_COUNT] = {
  "KEYGEN","ENCAP","DECAP","SIGN","VERIFY"
};

static inline uint32_t pqc_us_per_op(pqc_algo_t algo, pqc_op_t op) {
  uint32_t cycles = pqc_cycles_per_op[algo][op];
  return cycles / PQC_BENCH_FREQ_MHZ;
}

#define PQC_SIMULATE_OP(algo, op, clock_ticks_out) \
  do { \
    uint32_t _us = pqc_us_per_op((algo), (op)); \
    (clock_ticks_out) = (_us * CLOCK_SECOND) / 1000000UL; \
    clock_delay_usec(_us); \
  } while(0)

#endif
