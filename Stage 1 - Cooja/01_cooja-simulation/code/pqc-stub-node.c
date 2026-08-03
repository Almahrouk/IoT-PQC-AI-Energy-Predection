/**
 * pqc-stub-node.c
 *
 * PQC timing stub node using pqm4 benchmark cycle counts.
 *
 * PQC_LOG format:
 *   PQC_LOG node=<id> hop=<hop> topo=<topo> payload=<bytes>
 *            algo=<name> type=<KEM|SIG> op=<name>
 *            cycles=<n> time_us=<n> energy_uj=<n>
 */

#include "contiki.h"
#include "net/linkaddr.h"
#include "sys/node-id.h"

#include "pqc-stub.h"

#include <stdio.h>


/* Experiment metadata */
#ifndef PQC_HOP_COUNT
#define PQC_HOP_COUNT 1
#endif

#ifndef PQC_TOPO
#define PQC_TOPO "star"
#endif

#ifndef PQC_PAYLOAD
#define PQC_PAYLOAD 100
#endif


PROCESS(pqc_stub_process, "PQC Stub Node");
AUTOSTART_PROCESSES(&pqc_stub_process);


PROCESS_THREAD(pqc_stub_process, ev, data)
{
    static struct etimer et;

    static uint8_t alg;
    static uint8_t op;

    PROCESS_BEGIN();


    printf("PQC_LOG node=%u STATUS=START topo=%s hop=%d\n",
           node_id,
           PQC_TOPO,
           PQC_HOP_COUNT);



    etimer_set(&et, CLOCK_SECOND / 10);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));


    /*
     * Run all PQC algorithms and valid operations
     */
    for(alg = 0; alg < PQC_ALGO_COUNT; alg++) {

        for(op = 0; op < PQC_OP_COUNT; op++) {


            /*
             * Skip unsupported operations
             */
            if(pqc_cycles_per_op[alg][op] == 0) {
                continue;
            }


            uint32_t cycles =
                pqc_cycles_per_op[alg][op];


            uint32_t time_us =
                pqc_us_per_op(
                    (pqc_algo_t)alg,
                    (pqc_op_t)op
                );


            /*
             * Energy model:
             * 66 mW active power
             */
            uint32_t energy_uj =
                (uint32_t)((uint64_t)time_us * 66 / 1000);



            const char *type;

            if(alg <= PQC_KYBER_1024) {
                type = "KEM";
            }
            else {
                type = "SIG";
            }



            printf(
                "PQC_LOG node=%u hop=%d topo=%s payload=%d "
                "algo=%s type=%s op=%s "
                "cycles=%lu time_us=%lu energy_uj=%lu\n",

                node_id,

                PQC_HOP_COUNT,

                PQC_TOPO,

                PQC_PAYLOAD,

                pqc_algo_name[alg],

                type,

                pqc_op_name[op],

                (unsigned long)cycles,

                (unsigned long)time_us,

                (unsigned long)energy_uj
            );



            etimer_set(&et, CLOCK_SECOND / 10);
            PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

        }
    }



    printf(
        "PQC_LOG node=%u STATUS=DONE topo=%s hop=%d\n",
        node_id,
        PQC_TOPO,
        PQC_HOP_COUNT
    );


    PROCESS_END();
}
