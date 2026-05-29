/**
 * pqc-stub-node.c  (v2 — includes topology metadata in PQC_LOG)
 * Each node emits topology info + PQC energy for all 11 algorithms.
 *
 * PQC_LOG format:
 *   PQC_LOG node=<id> hop=<hop> topo=<topo> payload=<bytes>
 *            algo=<name> type=<KEM|SIG> op=<name>
 *            cycles=<n> time_us=<n> energy_uj=<n>
 */

#include "contiki.h"
#include "net/linkaddr.h"
#include "sys/node-id.h"
#include "pqc-timing-stubs.h"
#include <stdio.h>

/* Set per-experiment via compiler flags:
   -DPQC_HOP_COUNT=1 -DPQC_TOPO=\"star\" -DPQC_PAYLOAD=100  */
#ifndef PQC_HOP_COUNT
#define PQC_HOP_COUNT 1
#endif
#ifndef PQC_TOPO
#define PQC_TOPO "star"
#endif
#ifndef PQC_PAYLOAD
#define PQC_PAYLOAD 100
#endif

#define PQC_NUM_ALGORITHMS  11
#define PQC_NUM_OPS          3

PROCESS(pqc_stub_process, "PQC Stub Node v2");
AUTOSTART_PROCESSES(&pqc_stub_process);

PROCESS_THREAD(pqc_stub_process, ev, data)
{
    static struct etimer et;
    static uint8_t alg = 0;
    static uint8_t op  = 0;
    PROCESS_BEGIN();
    /* node_id comes from node-id.h, set by Cooja mote ID */
    printf("PQC_LOG node=%u STATUS=START topo=%s hop=%d\n",
           node_id, PQC_TOPO, PQC_HOP_COUNT);

    etimer_set(&et, CLOCK_SECOND / 10);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    for(alg = 0; alg < PQC_NUM_ALGORITHMS; alg++) {
        for(op = 0; op < PQC_NUM_OPS; op++) {
            uint32_t cycles   = PQC_CYCLES[alg][op];
            uint32_t time_us  = (uint32_t)((uint64_t)cycles * 1000000UL
                                           / PQC_CLOCK_HZ);
            uint32_t energy_uj = (uint32_t)((uint64_t)time_us
                                             * PQC_ACTIVE_UW / 1000000UL);
            printf("PQC_LOG node=%u hop=%d topo=%s payload=%d"
                   " algo=%s type=%s op=%s"
                   " cycles=%lu time_us=%lu energy_uj=%lu\n",
                   node_id, PQC_HOP_COUNT, PQC_TOPO, PQC_PAYLOAD,
                   PQC_ALG_NAMES[alg], PQC_TYPE_NAMES[alg],
                   PQC_OP_NAMES[op],
                   (unsigned long)cycles,
                   (unsigned long)time_us,
                   (unsigned long)energy_uj);

            etimer_set(&et, CLOCK_SECOND / 10);
            PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
        }
    }

    printf("PQC_LOG node=%u STATUS=DONE topo=%s hop=%d\n",
           node_id, PQC_TOPO, PQC_HOP_COUNT);

    PROCESS_END();
}
