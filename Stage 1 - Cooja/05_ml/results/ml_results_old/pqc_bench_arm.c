#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <oqs/oqs.h>

typedef struct { const char *name; const char *type; } AlgoInfo;

AlgoInfo ALGOS[] = {
    {"KYBER512",   "KEM"}, {"KYBER768",   "KEM"}, {"KYBER1024",  "KEM"},
    {"DILITHIUM2", "SIG"}, {"DILITHIUM3", "SIG"}, {"DILITHIUM5", "SIG"},
    {"FALCON512",  "SIG"}, {"FALCON1024", "SIG"},
    {"SPHINCS128", "SIG"}, {"SPHINCS192", "SIG"}, {"SPHINCS256", "SIG"},
};

const char* to_oqs_kem(const char *name) {
    if (!strcmp(name,"KYBER512"))  return OQS_KEM_alg_kyber_512;
    if (!strcmp(name,"KYBER768"))  return OQS_KEM_alg_kyber_768;
    if (!strcmp(name,"KYBER1024")) return OQS_KEM_alg_kyber_1024;
    return NULL;
}

const char* to_oqs_sig(const char *name) {
    if (!strcmp(name,"DILITHIUM2")) return OQS_SIG_alg_ml_dsa_44;
    if (!strcmp(name,"DILITHIUM3")) return OQS_SIG_alg_ml_dsa_65;
    if (!strcmp(name,"DILITHIUM5")) return OQS_SIG_alg_ml_dsa_87;
    if (!strcmp(name,"FALCON512"))  return OQS_SIG_alg_falcon_512;
    if (!strcmp(name,"FALCON1024")) return OQS_SIG_alg_falcon_1024;
    if (!strcmp(name,"SPHINCS128")) return OQS_SIG_alg_slh_dsa_pure_shake_128f;
    if (!strcmp(name,"SPHINCS192")) return OQS_SIG_alg_slh_dsa_pure_shake_192f;
    if (!strcmp(name,"SPHINCS256")) return OQS_SIG_alg_slh_dsa_pure_shake_256f;
    return NULL;
}

#define BENCH(label, code) do { \
    clock_t _t0 = clock(); \
    code; \
    clock_t _t1 = clock(); \
    uint64_t _cycles = (uint64_t)(_t1 - _t0); \
    printf("%s,%s\n", label, #code); \
    _cycles = _cycles; \
} while(0)

int main() {
    printf("algo,type,operation,ticks\n");

    for (int i = 0; i < 11; i++) {
        const char *name = ALGOS[i].name;
        const char *type = ALGOS[i].type;
        clock_t t0, t1;

        if (!strcmp(type, "KEM")) {
            OQS_KEM *kem = OQS_KEM_new(to_oqs_kem(name));
            if (!kem) { fprintf(stderr, "KEM not available: %s\n", name); continue; }

            uint8_t *pk  = malloc(kem->length_public_key);
            uint8_t *sk  = malloc(kem->length_secret_key);
            uint8_t *ct  = malloc(kem->length_ciphertext);
            uint8_t *ss1 = malloc(kem->length_shared_secret);
            uint8_t *ss2 = malloc(kem->length_shared_secret);

            t0 = clock(); OQS_KEM_keypair(kem, pk, sk);      t1 = clock();
            printf("%s,%s,KEYGEN,%lu\n",      name, type, (unsigned long)(t1-t0));
            t0 = clock(); OQS_KEM_encaps(kem, ct, ss1, pk);  t1 = clock();
            printf("%s,%s,ENCAP_SIGN,%lu\n",  name, type, (unsigned long)(t1-t0));
            t0 = clock(); OQS_KEM_decaps(kem, ss2, ct, sk);  t1 = clock();
            printf("%s,%s,DECAP_VERIFY,%lu\n",name, type, (unsigned long)(t1-t0));

            free(pk); free(sk); free(ct); free(ss1); free(ss2);
            OQS_KEM_free(kem);

        } else {
            OQS_SIG *sig = OQS_SIG_new(to_oqs_sig(name));
            if (!sig) { fprintf(stderr, "SIG not available: %s\n", name); continue; }

            uint8_t *pk = malloc(sig->length_public_key);
            uint8_t *sk = malloc(sig->length_secret_key);
            uint8_t *sm = malloc(sig->length_signature);
            uint8_t msg[100] = {0};
            size_t smlen;

            t0 = clock(); OQS_SIG_keypair(sig, pk, sk);               t1 = clock();
            printf("%s,%s,KEYGEN,%lu\n",      name, type, (unsigned long)(t1-t0));
            t0 = clock(); OQS_SIG_sign(sig, sm, &smlen, msg, 100, sk); t1 = clock();
            printf("%s,%s,ENCAP_SIGN,%lu\n",  name, type, (unsigned long)(t1-t0));
            t0 = clock(); OQS_SIG_verify(sig, msg, 100, sm, smlen, pk);t1 = clock();
            printf("%s,%s,DECAP_VERIFY,%lu\n",name, type, (unsigned long)(t1-t0));

            free(pk); free(sk); free(sm);
            OQS_SIG_free(sig);
        }
    }
    return 0;
}
