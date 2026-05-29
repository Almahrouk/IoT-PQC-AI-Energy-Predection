#include "contiki.h"
#include "net/routing/routing.h"
#include <stdio.h>

PROCESS(pqc_root_process, "PQC Root Node");
AUTOSTART_PROCESSES(&pqc_root_process);

PROCESS_THREAD(pqc_root_process, ev, data)
{
  PROCESS_BEGIN();
  NETSTACK_ROUTING.root_start();
  printf("PQC_LOG root started\n");
  while(1) {
    PROCESS_YIELD();
  }
  PROCESS_END();
}
