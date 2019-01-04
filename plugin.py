# Plugin to control Proscenic Vacuum
#
# Author: trandbert37
#
"""
<plugin key="ProscenicVaccum" name="Proscenic Vacuum" author="trandbert37" version="1.0.0" externallink="https://github.com/trandbert37/DomoticzProscenicVacuum">
    <description>
        <h2>Proscenic vacuum</h2><br/>
        Overview...
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
    <param field="Address" label="IP Address" width="200px" required="true"/>
    </params>
</plugin>
"""
import Domoticz
from base64 import b64encode

class BasePlugin:
    enabled = True

    controlUnit = 1
    modeUnit = 2

    controlOptions = {
        "LevelActions": "||",
        "LevelNames": "Off|Run|Dock",
        "LevelOffHidden": "false",
        "SelectorStyle": "0"
    }

    modeOptions = {
        "LevelActions": "|||",
        "LevelNames": "Auto|Area|Edge|Zigzag",
        "LevelOffHidden": "true",
        "SelectorStyle": "0"
    }

    control = {
        0: "AA55A55A0DFDE20906000100030000000000", #Off
        10: "AA55A55A0DFDE20906000100020000000100", #RUN
        20: "AA55A55A0FFDE20906000100010000000000" #DOCK
    }

    mode = {
        10: "AA55A55A09FDE20906000100020500000000", #AUTO
        20: "AA55A55A0AFDE20906000100020400000000", #AREA
        30: "AA55A55A0BFDE20906000100020300000000", #EDGE
        40: "AA55A55A0CFDE20906000100020200000000" #ZIGZAG
    }

    def __init__(self):
        self.host = None
        self.port = "10684"
        self.udpConn = None
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        self.host=Parameters['Address']
        self.udpConn = Domoticz.Connection(Name='ProscenicServer', Transport='UDP/IP', Protocol='None', Address=self.host, Port=self.port)

        if self.controlUnit not in Devices:
            Domoticz.Device(Name='Control', Unit=self.controlUnit, TypeName='Selector Switch', Options=self.controlOptions).Create()

        if self.modeUnit not in Devices:
            Domoticz.Device(Name='Mode', Unit=self.modeUnit, TypeName='Selector Switch', Options=self.modeOptions).Create()
    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called " + str(Description))

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if self.controlUnit == Unit:
            self.apiRequest(Level, self.control)
        elif self.modeUnit == Unit:
            self.apiRequest(Level, self.mode)


    def apiRequest(self, cmd_number, action):
        try:
            encodedBody = b64encode(b'<TRANSIT_INFO><COMMAND>ROBOT_CMD</COMMAND><RTU>' + action[cmd_number].encode() + b'</RTU></TRANSIT_INFO>')
            self.udpConn.Send('<HEADER MsgType="MSG_TRANSIT_SHAS_REQ" MsgSeq="1" From="02000000000000000" To="01801930aea421f164" Keep="1"/><BODY>' + encodedBody.decode() + '</BODY></MESSAGE>\r\n\r\n')
            return True
        except Exception as e:
            Domoticz.Error('Send exception [%s]' % str(e))
            return False

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
