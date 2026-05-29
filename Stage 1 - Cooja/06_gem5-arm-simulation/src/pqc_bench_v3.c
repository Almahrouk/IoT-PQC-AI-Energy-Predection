#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <oqs/oqs.h>

static char _buf[512];

static void emit(const char *msg) {
    write(1, msg, strlen(msg));
}

static void emit_start(const char *alg, const char *op) {
    int len = snprintf(_buf, sizeof(_buf),
                       "GEM5_START algo=%s op=%s\n", alg, op);
    write(1, _buf, len);
}

static void emit_end(const char *alg, const char *op) {
    int len = snprintf(_buf, sizeof(_buf),
                       "GEM5_END algo=%s op=%s\n", alg, op);
    write(1, _buf, len);
}

static void emit_skip(const char *alg) {
    int len = snprintf(_buf, sizeof(_buf), "GEM5_SKIP algo=%s\n", alg);
    write(1, _buf, len);
}

static void fixed_rand(uint8_t *buf, size_t len) {
    static unsigned int s = 0xDEADBEEF;
    for (size_t i = 0; i < len; i++) {
        s ^= s << 13;
        s ^= s >> 17;
        s ^= s << 5;
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

    emit_start(name, "KEYGEN");
    OQS_KEM_keypair(k, pk, sk);
    emit_end(name, "KEYGEN");

    emit_start(name, "ENCAP");
    OQS_KEM_encaps(k, ct, s1, pk);
    emit_end(name, "ENCAP");

    emit_start(name, "DECAP");
    OQS_KEM_decaps(k, s2, ct, sk);
    emit_end(name, "DECAP");

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

    emit_start(name, "KEYGEN");
    OQS_SIG_keypair(s, pk, sk);
    emit_end(name, "KEYGEN");

    emit_start(name, "SIGN");
    OQS_SIG_sign(s, sig, &slen, msg, sizeof(msg), sk);
    emit_end(name, "SIGN");

    emit_start(name, "VERIFY");
    OQS_SIG_verify(s, msg, sizeof(msg), sig, slen, pk);
    emit_end(name, "VERIFY");

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
