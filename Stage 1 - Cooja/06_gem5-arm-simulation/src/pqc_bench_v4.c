#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <oqs/oqs.h>

static char _buf[512];
static void emit(const char *msg) { write(1, msg, strlen(msg)); }
static void emit_result(const char *alg, const char *op, const char *status) {
    int len = snprintf(_buf, sizeof(_buf),
                       "GEM5_RESULT algo=%s op=%s status=%s\n", alg, op, status);
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
    if (!k) { emit_result(name, op, "SKIP"); return; }
    uint8_t *pk = malloc(k->length_public_key);
    uint8_t *sk = malloc(k->length_secret_key);
    uint8_t *ct = malloc(k->length_ciphertext);
    uint8_t *s1 = malloc(k->length_shared_secret);
    uint8_t *s2 = malloc(k->length_shared_secret);

    if (strcmp(op, "KEYGEN") == 0) {
        OQS_KEM_keypair(k, pk, sk);
    } else if (strcmp(op, "ENCAP") == 0) {
        OQS_KEM_keypair(k, pk, sk);
        OQS_KEM_encaps(k, ct, s1, pk);
    } else if (strcmp(op, "DECAP") == 0) {
        OQS_KEM_keypair(k, pk, sk);
        OQS_KEM_encaps(k, ct, s1, pk);
        OQS_KEM_decaps(k, s2, ct, sk);
    }
    emit_result(name, op, "OK");
    free(pk); free(sk); free(ct); free(s1); free(s2);
    OQS_KEM_free(k);
}

void run_sig(const char *name, const char *op) {
    OQS_SIG *s = OQS_SIG_new(name);
    if (!s) { emit_result(name, op, "SKIP"); return; }
    uint8_t *pk  = malloc(s->length_public_key);
    uint8_t *sk  = malloc(s->length_secret_key);
    uint8_t *sig = malloc(s->length_signature);
    size_t   slen = 0;
    uint8_t  msg[32];
    fixed_rand(msg, sizeof(msg));

    if (strcmp(op, "KEYGEN") == 0) {
        OQS_SIG_keypair(s, pk, sk);
    } else if (strcmp(op, "SIGN") == 0) {
        OQS_SIG_keypair(s, pk, sk);
        OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk);
    } else if (strcmp(op, "VERIFY") == 0) {
        OQS_SIG_keypair(s, pk, sk);
        OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk);
        OQS_SIG_verify(s, msg, sizeof(msg), sig, slen, pk);
    }
    emit_result(name, op, "OK");
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

    /* KEM algorithms */
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
