#include "contiki.h"
#include "net/linkaddr.h"
#include <stdio.h>

PROCESS(pqc_leaf_process, "PQC Leaf Node");
AUTOSTART_PROCESSES(&pqc_leaf_process);

PROCESS_THREAD(pqc_leaf_process, ev, data)
{
  PROCESS_BEGIN();
  printf("PQC_LOG: leaf node %d started\n", linkaddr_node_addr.u8[7]);
  PROCESS_END();
}
