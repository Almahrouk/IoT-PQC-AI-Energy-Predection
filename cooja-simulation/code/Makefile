CONTIKI_PROJECT = pqc-root-node pqc-stub-node pqc-leaf-node
all: $(CONTIKI_PROJECT)
CONTIKI = /home/user/contiki-ng

# Forward experiment parameters as compiler defines
ifdef PQC_PAYLOAD
  CFLAGS += -DPQC_PAYLOAD=$(PQC_PAYLOAD)
endif
ifdef PQC_HOP_COUNT
  CFLAGS += -DPQC_HOP_COUNT=$(PQC_HOP_COUNT)
endif
ifdef PQC_TOPO
  CFLAGS += -DPQC_TOPO=\"$(PQC_TOPO)\"
endif

include $(CONTIKI)/Makefile.include
