code = r"""
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <oqs/oqs.h>

static char _buf[256];
static void emit_result(const char *alg, const char *op, unsigned long long ns) {
    int len = snprintf(_buf, sizeof(_buf), "RESULT %s %s cycles=%llu\n", alg, op, ns);
    write(1, _buf, len);
}
static void emit_skip(const char *alg) {
    int len = snprintf(_buf, sizeof(_buf), "SKIP %s\n", alg);
    write(1, _buf, len);
}

typedef unsigned long long u64;
static u64 get_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (u64)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
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
    u64 t0, t1;
    t0=get_ns(); OQS_KEM_keypair(k,pk,sk);   t1=get_ns(); emit_result(name,"KEYGEN",t1-t0);
    t0=get_ns(); OQS_KEM_encaps(k,ct,s1,pk); t1=get_ns(); emit_result(name,"ENCAP_SIGN",t1-t0);
    t0=get_ns(); OQS_KEM_decaps(k,s2,ct,sk); t1=get_ns(); emit_result(name,"DECAP_VERIFY",t1-t0);
    free(pk); free(sk); free(ct); free(s1); free(s2);
    OQS_KEM_free(k);
}

void bench_sig(const char *name) {
    OQS_SIG *s = OQS_SIG_new(name);
    if (!s) { emit_skip(name); return; }
    uint8_t *pk = malloc(s->length_public_key);
    uint8_t *sk = malloc(s->length_secret_key);
    uint8_t *sm = malloc(s->length_signature);
    uint8_t msg[32]; memset(msg, 0xAB, 32);
    size_t smlen; u64 t0, t1;
    t0=get_ns(); OQS_SIG_keypair(s,pk,sk);             t1=get_ns(); emit_result(name,"KEYGEN",t1-t0);
    t0=get_ns(); OQS_SIG_sign(s,sm,&smlen,msg,32,sk);  t1=get_ns(); emit_result(name,"ENCAP_SIGN",t1-t0);
    t0=get_ns(); OQS_SIG_verify(s,msg,32,sm,smlen,pk); t1=get_ns(); emit_result(name,"DECAP_VERIFY",t1-t0);
    free(pk); free(sk); free(sm);
    OQS_SIG_free(s);
}

int main(void) {
    OQS_randombytes_custom_algorithm(fixed_rand);
    bench_kem("ML-KEM-512");
    bench_kem("ML-KEM-768");
    bench_kem("ML-KEM-1024");
    bench_kem("Kyber512");
    bench_kem("Kyber768");
    bench_kem("Kyber1024");
    bench_sig("ML-DSA-44");
    bench_sig("ML-DSA-65");
    bench_sig("Falcon-512");
    bench_sig("Falcon-1024");
    return 0;
}
"""
with open('/home/user/pqc_bench_v2.c', 'w') as f:
    f.write(code.strip())
print("OK: /home/user/pqc_bench_v2.c")
