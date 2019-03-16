# Plugin to control Proscenic Vacuum
#
# Author: trandbert37
#
"""
<plugin key="ProscenicVaccum" name="Proscenic Vacuum" author="trandbert37" version="1.0.0" externallink="https://github.com/trandbert37/DomoticzProscenicVacuum">
    <description>
        <h2>Proscenic vacuum</h2><br/>
        Python plugin to control your Proscenic Vacuum
    </description>
</plugin>
"""
import Domoticz

import xml.etree.cElementTree as ET
from base64 import b64encode
from socket import *

class BasePlugin:
    enabled = True

    controlUnit = 1
    modeUnit = 2
    voiceUnit = 3

    iconName = 'proscenic-790t-vacuum-icon'

    controlOptions = {
        "LevelActions": "||",
        "LevelNames": "Off|Run|Dock",
        "LevelOffHidden": "false",
        "SelectorStyle": "0"
    }

    modeOptions = {
        "LevelActions": "|||",
        "LevelNames": "Off|Auto|Area|Edge|Zigzag",
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

    voiceStatus = {
        0: "AA55A55A0BFDE20906000100040000000001", #Off
        1: "AA55A55A0AFDE20906000100040000000002", #On
    }

    def __init__(self):
        self.port = 10684
        return

    def onStart(self):
        if self.iconName not in Images: Domoticz.Image('icons.zip').Create()
        iconID = Images[self.iconName].ID

        if self.controlUnit not in Devices:
            Domoticz.Device(Name='Control', Unit=self.controlUnit, TypeName='Selector Switch', Image=iconID, Options=self.controlOptions).Create()

        if self.modeUnit not in Devices:
            Domoticz.Device(Name='Mode', Unit=self.modeUnit, TypeName='Selector Switch', Image=iconID, Options=self.modeOptions).Create()

        if self.voiceUnit no in Devices:
            Domoticz.Device(Name='Voice', Unit=self.voiceUnit, TypeName='Switch', Image=Images['Speaker'].ID).Create()

    def onStop(self):
        pass

    def onConnect(self, Connection, Status, Description):
        pass

    def onMessage(self, Connection, Data):
        pass

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if self.controlUnit == Unit:
            if self.apiRequest(Level, self.control):
                UpdateDevice(self.controlUnit, Level)
                if Level != 10:
                    UpdateDevice(self.modeUnit, 0)
        elif self.modeUnit == Unit:
            if self.apiRequest(Level, self.mode):
                UpdateDevice(self.modeUnit, Level)
                UpdateDevice(self.controlUnit, 10)
        elif self.voiceUnit == Unit:
            if self.apiRequest(Level, self.voiceStatus):
                UpdateDevice(self.voiceUnit, Level)

    def generateMessageBody(self, command, action):
        transitInfo = ET.Element('TRANSIT_INFO')
        ET.SubElement(transitInfo, 'COMMAND').text = 'ROBOT_CMD'
        ET.SubElement(transitInfo, 'RTU').text = action[command]
        return ET.tostring(transitInfo)

    def apiRequest(self, command, action):
        try:
            cs = socket(AF_INET, SOCK_DGRAM)
            cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            message = ET.Element("MESSAGE", Version="1.0")
            ET.SubElement(message, "HEADER", MsgType="MSG_TRANSIT_SHAS_REQ", MsgSeq="1", From="020000000000000000", To="01801930aea421f164", Keep="0")
            ET.SubElement(message, "BODY").text = b64encode(self.generateMessageBody(command, action)).decode('ascii')

            cs.sendto(ET.tostring(message, encoding='utf8', method='xml'), ('255.255.255.255', self.port))

            return True

        except Exception as e:
            Domoticz.Error('Send exception [%s]' % str(e))

            return False

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        pass

    def onDisconnect(self, Connection):
        pass

    def onHeartbeat(self):
        pass

def UpdateDevice(Unit, sValue, BatteryLevel=255, AlwaysUpdate=False):
    if Unit not in Devices: return
    nValue = (0 if sValue == 0 else 1)
    if Devices[Unit].nValue != nValue\
        or Devices[Unit].sValue != sValue\
        or Devices[Unit].BatteryLevel != BatteryLevel\
        or AlwaysUpdate == True:

        Devices[Unit].Update(nValue, str(sValue), BatteryLevel=BatteryLevel)

        Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
            Devices[Unit].Name,
            nValue,
            sValue,
            BatteryLevel
        ))

def UpdateIcon(Unit, iconID):
    if Unit not in Devices: return
    d = Devices[Unit]
    if d.Image != iconID: d.Update(d.nValue, d.sValue, Image=iconID)

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
