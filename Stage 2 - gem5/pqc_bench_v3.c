#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <oqs/oqs.h>

static char _buf[512];

static void emit(const char *msg) {
    write(1, msg, strlen(msg));
}

static void emit_skip(const char *alg) {
    int len = snprintf(_buf, sizeof(_buf), "GEM5_SKIP algo=%s\n", alg);
    write(1, _buf, len);
}

/* THIS MUST BE BEFORE bench_kem and bench_sig */
static long long ns_diff(struct timespec *t0, struct timespec *t1) {
    return (long long)(t1->tv_sec - t0->tv_sec) * 1000000000LL
           + (t1->tv_nsec - t0->tv_nsec);
}

static void emit_result(const char *alg, const char *op, long long ns) {
    int len = snprintf(_buf, sizeof(_buf),
                       "GEM5_RESULT algo=%s op=%s ns=%lld\n", alg, op, ns);
    write(1, _buf, len);
}

static void fixed_rand(uint8_t *buf, size_t len) {
    static unsigned int s = 0xDEADBEEF;
    for (size_t i = 0; i < len; i++) {
        s ^= s << 13; s ^= s >> 17; s ^= s << 5;
        buf[i] = (uint8_t)(s & 0xFF);
    }
}

void bench_kem(const char *name) {
    OQS_KEM *k = OQS_KEM_new(name);
    if (!k) { emit_skip(name); return; }

    uint8_t *pk = malloc(k->length_public_key);
    uint8_t *sk = malloc(k->length_secret_key);
    uint8_t *ct = malloc(k->length_ciphertext);
    uint8_t *s1 = malloc(k->length_shared_secret);
    uint8_t *s2 = malloc(k->length_shared_secret);

    struct timespec t0, t1;

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_KEM_keypair(k, pk, sk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "KEYGEN", ns_diff(&t0, &t1));

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_KEM_encaps(k, ct, s1, pk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "ENCAP", ns_diff(&t0, &t1));

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_KEM_decaps(k, s2, ct, sk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "DECAP", ns_diff(&t0, &t1));

    free(pk); free(sk); free(ct); free(s1); free(s2);
    OQS_KEM_free(k);
}

void bench_sig(const char *name) {
    OQS_SIG *s = OQS_SIG_new(name);
    if (!s) { emit_skip(name); return; }

    uint8_t *pk  = malloc(s->length_public_key);
    uint8_t *sk  = malloc(s->length_secret_key);
    uint8_t *sig = malloc(s->length_signature);
    size_t   slen = 0;
    uint8_t  msg[32];
    fixed_rand(msg, sizeof(msg));

    struct timespec t0, t1;

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_SIG_keypair(s, pk, sk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "KEYGEN", ns_diff(&t0, &t1));

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "SIGN", ns_diff(&t0, &t1));

    clock_gettime(CLOCK_MONOTONIC, &t0);
    OQS_SIG_verify(s, msg, sizeof(msg), sig, slen, pk);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    emit_result(name, "VERIFY", ns_diff(&t0, &t1));

    free(pk); free(sk); free(sig);
    OQS_SIG_free(s);
}

int main(void) {
    emit("GEM5_BENCH_START\n");

    bench_kem(OQS_KEM_alg_kyber_512);
    bench_kem(OQS_KEM_alg_kyber_768);
    bench_kem(OQS_KEM_alg_kyber_1024);
    bench_kem(OQS_KEM_alg_ml_kem_512);
    bench_kem(OQS_KEM_alg_ml_kem_768);
    bench_kem(OQS_KEM_alg_ml_kem_1024);

    bench_sig(OQS_SIG_alg_ml_dsa_44);
    bench_sig(OQS_SIG_alg_ml_dsa_65);
    bench_sig(OQS_SIG_alg_ml_dsa_87);
    bench_sig(OQS_SIG_alg_falcon_512);
    bench_sig(OQS_SIG_alg_falcon_1024);

    emit("GEM5_BENCH_END\n");
    return 0;
}

/*
Before:
make sure to run scripts\01_rebuild_liboqs_arm.sh first 

Old: "Not support time"
arm-linux-gnueabihf-gcc -O2 -static \
    -I/home/user/liboqs/build-arm/install/include \
    /home/user/pqc_bench_v3.c \
    -o /home/user/pqc_bench_arm_v3 \
    -L/home/user/liboqs/build-arm/install/lib -loqs -lm

Now: or run 02_compile_pqc_bench.sh
aarch64-linux-gnu-gcc -O2 -static \
    -I/home/user/liboqs/build-aarch64/install/include \
    /home/user/pqc_bench_v3.c \
    -o /home/user/pqc_bench_arm_v3 \
    -L/home/user/liboqs/build-aarch64/install/lib -loqs -lm

Next:
run scripts\03_run_gem5.sh
*/