#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <oqs/oqs.h>

typedef unsigned long long u64;

static u64 get_cycles() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (u64)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

void bench_kem(const char *name) {
    OQS_KEM *kem = OQS_KEM_new(name);
    if (!kem) { printf("SKIP %s (not available)\n", name); return; }

    uint8_t *pk = malloc(kem->length_public_key);
    uint8_t *sk = malloc(kem->length_secret_key);
    uint8_t *ct = malloc(kem->length_ciphertext);
    uint8_t *ss1 = malloc(kem->length_shared_secret);
    uint8_t *ss2 = malloc(kem->length_shared_secret);

    u64 t0, t1;

    // KEYGEN
    t0 = get_cycles();
    OQS_KEM_keypair(kem, pk, sk);
    t1 = get_cycles();
    printf("RESULT %s KEYGEN cycles=%llu\n", name, t1 - t0);

    // ENCAP
    t0 = get_cycles();
    OQS_KEM_encaps(kem, ct, ss1, pk);
    t1 = get_cycles();
    printf("RESULT %s ENCAP_SIGN cycles=%llu\n", name, t1 - t0);

    // DECAP
    t0 = get_cycles();
    OQS_KEM_decaps(kem, ss2, ct, sk);
    t1 = get_cycles();
    printf("RESULT %s DECAP_VERIFY cycles=%llu\n", name, t1 - t0);

    free(pk); free(sk); free(ct); free(ss1); free(ss2);
    OQS_KEM_free(kem);
}

void bench_sig(const char *name) {
    OQS_SIG *sig = OQS_SIG_new(name);
    if (!sig) { printf("SKIP %s (not available)\n", name); return; }

    uint8_t *pk = malloc(sig->length_public_key);
    uint8_t *sk = malloc(sig->length_secret_key);
    uint8_t *sm = malloc(sig->length_signature);
    size_t smlen;
    uint8_t msg[100];
    memset(msg, 0xAB, sizeof(msg));

    u64 t0, t1;

    // KEYGEN
    t0 = get_cycles();
    OQS_SIG_keypair(sig, pk, sk);
    t1 = get_cycles();
    printf("RESULT %s KEYGEN cycles=%llu\n", name, t1 - t0);

    // SIGN
    t0 = get_cycles();
    OQS_SIG_sign(sig, sm, &smlen, msg, sizeof(msg), sk);
    t1 = get_cycles();
    printf("RESULT %s ENCAP_SIGN cycles=%llu\n", name, t1 - t0);

    // VERIFY
    t0 = get_cycles();
    OQS_SIG_verify(sig, msg, sizeof(msg), sm, smlen, pk);
    t1 = get_cycles();
    printf("RESULT %s DECAP_VERIFY cycles=%llu\n", name, t1 - t0);

    free(pk); free(sk); free(sm);
    OQS_SIG_free(sig);
}

int main() {
    printf("=== PQC Benchmark ===\n");

    // KEMs
    bench_kem(OQS_KEM_alg_kyber_512);
    bench_kem(OQS_KEM_alg_kyber_768);
    bench_kem(OQS_KEM_alg_kyber_1024);

    // Signatures
    bench_sig(OQS_SIG_alg_dilithium_2);
    bench_sig(OQS_SIG_alg_dilithium_3);
    bench_sig(OQS_SIG_alg_dilithium_5);
    bench_sig(OQS_SIG_alg_falcon_512);
    bench_sig(OQS_SIG_alg_falcon_1024);
    bench_sig(OQS_SIG_alg_sphincs_sha2_128f_simple);
    bench_sig(OQS_SIG_alg_sphincs_sha2_192f_simple);
    bench_sig(OQS_SIG_alg_sphincs_sha2_256f_simple);

    printf("=== Done ===\n");
    return 0;
}
