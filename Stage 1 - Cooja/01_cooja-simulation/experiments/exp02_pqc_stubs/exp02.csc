<?xml version="1.0" encoding="UTF-8"?>
<simconf version="2022112801">
  <simulation>
    <title>EXP02 - PQC Timing Stubs, Star Topology</title>
    <randomseed>42</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <!-- ================= RADIO / NETWORK MODEL ================= -->
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range> <!-- Communication distance -->
      <interference_range>50.0</interference_range> <!-- Interference distance -->
      <success_ratio_tx>1.0</success_ratio_tx> <!-- No packet loss (TX) -->
      <success_ratio_rx>1.0</success_ratio_rx> <!-- No packet loss (RX) -->
    </radiomedium>
    <events><logoutput>500000</logoutput></events>

    <!-- ================= ROOT NODE (central collector) ================= -->
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

    <!-- ================= STUB NODE TYPE (sensors / clients) ================= -->
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>pqcstub1</identifier>
      <description>PQC Stub Node</description>
      <source>[CONFIG_DIR]/../../code/pqc-stub-node.c</source>
      <commands>$(MAKE) -j$(CPUS) pqc-stub-node.cooja TARGET=cooja</commands>
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

     <!-- ================= NODE INSTANCES ================= -->

    <!-- ROOT NODE (center of star topology) -->
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

    <!-- STUB NODE 1 -->
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

    <!-- STUB NODE 2 -->
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>30.0</x><y>60.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>3</id>
      </interface_config>
    </mote>

    <!-- STUB NODE 3 -->
    <mote>
      <motetype_identifier>pqcstub1</motetype_identifier>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>60.0</x><y>90.0</y><z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>4</id>
      </interface_config>
    </mote>
  </simulation>



  <!-- ================= AUTOMATION SCRIPT ================= -->
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
TIMEOUT(180000, log.testFailed("Timed out"));
var outFile = new java.io.FileWriter(
  "/home/user/contiki-ng/examples/pqc-iot-sim/experiments/exp02_pqc_stubs/results/pqc_raw.log",
  true);
var bw = new java.io.BufferedWriter(outFile);
var done = 0;   <!-- Counts how many nodes finished -->
while (done &lt; 3) {
  YIELD();    <!-- Wait for next simulation event -->

  // Save only important logs
  if (msg.contains("PQC_LOG") || msg.contains("STATUS")) {
    bw.write(msg + "\n");
    bw.flush();
  }
  // Count completed nodes
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
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter></filter>
      <formatted_time/>
      <coloring/>
    </plugin_config>
    <width>1200</width>
    <height>240</height>
    <location_x>0</location_x>
    <location_y>0</location_y>
  </plugin>
</simconf>