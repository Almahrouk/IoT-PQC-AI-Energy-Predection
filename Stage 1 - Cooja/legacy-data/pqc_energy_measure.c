#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <oqs/oqs.h>

double cpu_ms() { return (double)clock() / CLOCKS_PER_SEC * 1000.0; }

void test_kem(const char *name, FILE *csv) {
    OQS_KEM *kem = OQS_KEM_new(name);
    if (!kem) { fprintf(stderr, "Skipping %s\n", name); return; }
    uint8_t *pk = malloc(kem->length_public_key);
    uint8_t *sk = malloc(kem->length_secret_key);
    uint8_t *ct = malloc(kem->length_ciphertext);
    uint8_t *ss1 = malloc(kem->length_shared_secret);
    uint8_t *ss2 = malloc(kem->length_shared_secret);
    double t1, t2, tkg=0, tenc=0, tdec=0;
    int runs = 100;
    for (int i = 0; i < runs; i++) {
        t1=cpu_ms(); OQS_KEM_keypair(kem,pk,sk);      t2=cpu_ms(); tkg  += t2-t1;
        t1=cpu_ms(); OQS_KEM_encaps(kem,ct,ss1,pk);   t2=cpu_ms(); tenc += t2-t1;
        t1=cpu_ms(); OQS_KEM_decaps(kem,ss2,ct,sk);   t2=cpu_ms(); tdec += t2-t1;
    }
    fprintf(csv,"%s,KEM,%.4f,%.4f,%.4f,%zu,%zu,%zu\n",
        name, tkg/runs, tenc/runs, tdec/runs,
        kem->length_public_key, kem->length_secret_key, kem->length_ciphertext);
    printf("✅ %-40s keygen=%.3fms encap=%.3fms decap=%.3fms\n", name, tkg/runs, tenc/runs, tdec/runs);
    free(pk); free(sk); free(ct); free(ss1); free(ss2);
    OQS_KEM_free(kem);
}

void test_sig(const char *name, FILE *csv) {
    OQS_SIG *sig = OQS_SIG_new(name);
    if (!sig) { fprintf(stderr, "Skipping %s\n", name); return; }
    uint8_t *pk = malloc(sig->length_public_key);
    uint8_t *sk = malloc(sig->length_secret_key);
    uint8_t *sm = malloc(sig->length_signature);
    uint8_t msg[64]; memset(msg, 0xAB, 64);
    size_t smlen;
    double t1, t2, tkg=0, tsgn=0, tvfy=0;
    int runs = 100;
    for (int i = 0; i < runs; i++) {
        t1=cpu_ms(); OQS_SIG_keypair(sig,pk,sk);                    t2=cpu_ms(); tkg  += t2-t1;
        t1=cpu_ms(); OQS_SIG_sign(sig,sm,&smlen,msg,64,sk);         t2=cpu_ms(); tsgn += t2-t1;
        t1=cpu_ms(); OQS_SIG_verify(sig,msg,64,sm,smlen,pk);        t2=cpu_ms(); tvfy += t2-t1;
    }
    fprintf(csv,"%s,SIG,%.4f,%.4f,%.4f,%zu,%zu,%zu\n",
        name, tkg/runs, tsgn/runs, tvfy/runs,
        sig->length_public_key, sig->length_secret_key, sig->length_signature);
    printf("✅ %-40s keygen=%.3fms sign=%.3fms verify=%.3fms\n", name, tkg/runs, tsgn/runs, tvfy/runs);
    free(pk); free(sk); free(sm);
    OQS_SIG_free(sig);
}

int main() {
    FILE *csv = fopen("pqc_energy_data.csv","w");
    fprintf(csv,"algorithm,type,op1_ms,op2_ms,op3_ms,pk_bytes,sk_bytes,ct_or_sig_bytes\n");
    printf("\n=== KEM Algorithms ===\n");
    test_kem(OQS_KEM_alg_kyber_512, csv);
    test_kem(OQS_KEM_alg_kyber_768, csv);
    test_kem(OQS_KEM_alg_kyber_1024, csv);
    test_kem(OQS_KEM_alg_ml_kem_512, csv);
    test_kem(OQS_KEM_alg_ml_kem_768, csv);
    test_kem(OQS_KEM_alg_ml_kem_1024, csv);
    printf("\n=== Signature Algorithms ===\n");
    test_sig(OQS_SIG_alg_falcon_512, csv);
    test_sig(OQS_SIG_alg_falcon_1024, csv);
    test_sig(OQS_SIG_alg_ml_dsa_44, csv);
    test_sig(OQS_SIG_alg_ml_dsa_65, csv);
    test_sig("SPHINCS+-SHA2-128f-simple", csv);
    test_sig("SPHINCS+-SHA2-256f-simple", csv);
    fclose(csv);
    printf("\n📁 Saved to pqc_energy_data.csv\n");
    return 0;
}
