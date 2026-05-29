#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <oqs/oqs.h>

static char _buf[512];

static void emit(const char *msg) { write(1, msg, strlen(msg)); }

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

void run_kem(const char *name, const char *op) {
    OQS_KEM *k = OQS_KEM_new(name);
    if (!k) {
        int len = snprintf(_buf, sizeof(_buf), "GEM5_SKIP algo=%s op=%s\n", name, op);
        write(1, _buf, len);
        return;
    }
    uint8_t *pk = malloc(k->length_public_key);
    uint8_t *sk = malloc(k->length_secret_key);
    uint8_t *ct = malloc(k->length_ciphertext);
    uint8_t *s1 = malloc(k->length_shared_secret);
    uint8_t *s2 = malloc(k->length_shared_secret);

    struct timespec t0, t1;

    if (strcmp(op, "KEYGEN") == 0) {
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_KEM_keypair(k, pk, sk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));

    } else if (strcmp(op, "ENCAP") == 0) {
        OQS_KEM_keypair(k, pk, sk);          // setup only, not timed
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_KEM_encaps(k, ct, s1, pk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));

    } else if (strcmp(op, "DECAP") == 0) {
        OQS_KEM_keypair(k, pk, sk);          // setup only, not timed
        OQS_KEM_encaps(k, ct, s1, pk);       // setup only, not timed
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_KEM_decaps(k, s2, ct, sk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));
    }

    free(pk); free(sk); free(ct); free(s1); free(s2);
    OQS_KEM_free(k);
}

void run_sig(const char *name, const char *op) {
    OQS_SIG *s = OQS_SIG_new(name);
    if (!s) {
        int len = snprintf(_buf, sizeof(_buf), "GEM5_SKIP algo=%s op=%s\n", name, op);
        write(1, _buf, len);
        return;
    }
    uint8_t *pk  = malloc(s->length_public_key);
    uint8_t *sk  = malloc(s->length_secret_key);
    uint8_t *sig = malloc(s->length_signature);
    size_t   slen = 0;
    uint8_t  msg[32];
    fixed_rand(msg, sizeof(msg));

    struct timespec t0, t1;

    if (strcmp(op, "KEYGEN") == 0) {
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_SIG_keypair(s, pk, sk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));

    } else if (strcmp(op, "SIGN") == 0) {
        OQS_SIG_keypair(s, pk, sk);          // setup only, not timed
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));

    } else if (strcmp(op, "VERIFY") == 0) {
        OQS_SIG_keypair(s, pk, sk);          // setup only, not timed
        OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk); // setup only, not timed
        clock_gettime(CLOCK_MONOTONIC, &t0);
        OQS_SIG_verify(s, msg, sizeof(msg), sig, slen, pk);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        emit_result(name, op, ns_diff(&t0, &t1));
    }

    free(pk); free(sk); free(sig);
    OQS_SIG_free(s);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        emit("Usage: pqc_bench_v4 <algo> <op>\n");
        return 1;
    }
    const char *algo = argv[1];
    const char *op   = argv[2];
    emit("GEM5_BENCH_START\n");

    if (strcmp(algo, "Kyber512")    == 0 ||
        strcmp(algo, "Kyber768")    == 0 ||
        strcmp(algo, "Kyber1024")   == 0 ||
        strcmp(algo, "ML-KEM-512")  == 0 ||
        strcmp(algo, "ML-KEM-768")  == 0 ||
        strcmp(algo, "ML-KEM-1024") == 0) {
        run_kem(algo, op);
    } else {
        run_sig(algo, op);
    }

    emit("GEM5_BENCH_END\n");
    return 0;
}

/*
aarch64-linux-gnu-gcc -O2 -static \
    -I/home/user/liboqs/build-aarch64/install/include \
    /home/user/pqc_bench_v4.c \
    -o /home/user/pqc_bench_arm_v4 \
    -L/home/user/liboqs/build-aarch64/install/lib -loqs -lm

file /home/user/pqc_bench_arm_v4
*/