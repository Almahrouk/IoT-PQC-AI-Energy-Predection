#include "contiki.h"
#include "net/routing/routing.h"
#include "net/netstack.h"
#include "sys/energest.h"
#include "sys/log.h"
#include "pqc-stub.h"
#include <stdio.h>

#define LOG_MODULE "PQC-Client"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Simulation parameters — modify per batch run */
#define PQC_ALGO   PQC_KYBER_512
#define PQC_OP     PQC_OP_KEYGEN
#define NUM_OPS    5

PROCESS(pqc_client_process, "PQC client");
AUTOSTART_PROCESSES(&pqc_client_process);

static void log_energy(const char *phase)
{
  energest_flush();
  unsigned long cpu  = energest_type_time(ENERGEST_TYPE_CPU);
  unsigned long lpm  = energest_type_time(ENERGEST_TYPE_LPM);
  unsigned long tx   = energest_type_time(ENERGEST_TYPE_TRANSMIT);
  unsigned long rx   = energest_type_time(ENERGEST_TYPE_LISTEN);
  LOG_INFO("ENERGY phase=%s cpu=%lu lpm=%lu tx=%lu rx=%lu\n",
           phase, cpu, lpm, tx, rx);
}

PROCESS_THREAD(pqc_client_process, ev, data)
{
  static struct etimer timer;
  static int op_count = 0;
  static clock_time_t t_start, t_end;

  PROCESS_BEGIN();

  /* Wait for RPL to converge */
  etimer_set(&timer, CLOCK_SECOND * 30);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  LOG_INFO("PQC_SIM_START algo=%s op=%s node=%d\n",
           pqc_algo_name[PQC_ALGO], pqc_op_name[PQC_OP], node_id);

  energest_init();

  while(op_count < NUM_OPS) {
    log_energy("pre-op");
    t_start = clock_time();

    clock_time_t ticks;
    PQC_SIMULATE_OP(PQC_ALGO, PQC_OP, ticks);

    t_end = clock_time();
    log_energy("post-op");

    unsigned long elapsed_ms = (1000UL * (t_end - t_start)) / CLOCK_SECOND;

    /* Machine-parseable log line for Python dataset builder */
    printf("PQC_LOG algo=%s op=%s sec_level=%d op_num=%d elapsed_ms=%lu node=%d\n",
           pqc_algo_name[PQC_ALGO], pqc_op_name[PQC_OP],
           PQC_ALGO, op_count, elapsed_ms, node_id);

    op_count++;
    etimer_set(&timer, CLOCK_SECOND * 2);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
  }

  LOG_INFO("PQC_SIM_DONE node=%d ops=%d\n", node_id, op_count);
  PROCESS_END();
}
