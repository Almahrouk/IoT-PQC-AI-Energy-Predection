<?xml version="1.0" encoding="UTF-8"?>
<simconf version="2022112801">
  <simulation>
    <title>EXP05 chain payload=200</title>
    <randomseed>42</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>35.0</transmitting_range>
      <interference_range>35.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events><logoutput>1000000</logoutput></events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>pqcroot1</identifier>
      <description>PQC Root Node</description>
      <source>[CONFIG_DIR]/../../code/pqc-root-node.c</source>
      <commands>$(MAKE) -j$(CPUS) pqc-root-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>pqcstub1</identifier>
      <description>PQC Stub Node payload=200</description>
      <source>[CONFIG_DIR]/../../code/pqc-stub-node.c</source>
      <commands>$(MAKE) -j$(CPUS) PQC_PAYLOAD=200 PQC_HOP_COUNT=2 PQC_TOPO=chain pqc-stub-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
    </motetype>
    <mote>
      <motetype_identifier>pqcroot1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>60.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>1</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>90.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>2</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>120.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>3</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>150.0</x><y>45.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>4</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>150.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>5</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>150.0</x><y>75.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>6</id>
      </interface_config>
    </mote>
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>150.0</x><y>90.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>7</id>
      </interface_config>
    </mote>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
TIMEOUT(300000, log.testFailed("Timed out"));
var fw = new java.io.FileWriter(
  "/home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp05_payload_sweep/results/pqc_raw_chain_p200.log",
  false);
var bw = new java.io.BufferedWriter(fw);
var done = 0;
while (done &lt; 6) {
  YIELD();
  if (msg.contains("PQC_LOG") || msg.contains("STATUS")) {
    bw.write(msg + "\n");
    bw.flush();
  }
  if (msg.contains("STATUS=DONE")) {
    done++;
  }
}
bw.close();
log.testOK();
      </script>
      <active>true</active>
    </plugin_config>
    <width>600</width><height>300</height>
    <location_x>0</location_x><location_y>460</location_y>
  </plugin>
</simconf>