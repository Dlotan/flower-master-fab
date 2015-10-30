import struct

from third_party.bluepy.bluepy.btle import *

def to_flower_uuid(hex_value):
    return UUID("%08X-84a8-11e2-afba-0002a5d5c51b" % (0x39e10000 + hex_value))


class FlowerService(object):
    def __init__(self):
        self.service = None

    def enable(self, periph):
        self.service = periph.getServiceByUUID(self.uuid)
        for characteristic in self.characteristics:
            characteristic.enable(self.service)

    def __getitem__(self, item):
        for characteristic in self.characteristics:
            if characteristic.name == item:
                return characteristic


class FlowerCharacteristic(object):
    def __init__(self):
        self.characteristic = None

    def enable(self, service):
        self.characteristic = service.getCharacteristics(self.uuid)[0]


class TimeDateCharacteristic(FlowerCharacteristic):
    name = "Date"
    uuid = to_flower_uuid(0xfd01)

    def __init__(self):
        super(TimeDateCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("<i", self.characteristic.read())[0]


class TimeService(FlowerService):
    name = "Time"
    uuid = to_flower_uuid(0xfd00)

    def __init__(self):
        super(TimeService, self).__init__()
        self.characteristics = [TimeDateCharacteristic()]


class LEDCharacteristic(FlowerCharacteristic):
    name = "LED"
    uuid = to_flower_uuid(0xfa07)

    def __init__(self):
        super(LEDCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("?", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("?", value))


class LightCharacteristic(FlowerCharacteristic):
    name = "Light"
    uuid = to_flower_uuid(0xfa01)

    def __init__(self):
        super(LightCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("<h", self.characteristic.read())[0]


class TemperatureCharacteristic(FlowerCharacteristic):
    name = "Temperature"
    uuid = to_flower_uuid(0xfa0a)

    def __init__(self):
        super(TemperatureCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class WaterCharacteristic(FlowerCharacteristic):
    name = "Water"
    uuid = to_flower_uuid(0xfa09)

    def __init__(self):
        super(WaterCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class DLICharacteristic(FlowerCharacteristic):
    name = "DLI"
    uuid = to_flower_uuid(0xfa0b)

    def __init__(self):
        super(DLICharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class EaCharacteristic(FlowerCharacteristic):
    name = "Ea"
    uuid = to_flower_uuid(0xfa0c)

    def __init__(self):
        super(EaCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class EcbCharacteristic(FlowerCharacteristic):
    name = "Ecb"
    uuid = to_flower_uuid(0xfa0d)

    def __init__(self):
        super(EcbCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class EcPorusCharacteristic(FlowerCharacteristic):
    name = "EcPorus"
    uuid = to_flower_uuid(0xfa0e)

    def __init__(self):
        super(EcPorusCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("f", self.characteristic.read())[0]


class PeriodCharacteristic(FlowerCharacteristic):
    name = "Period"
    uuid = to_flower_uuid(0xfa06)

    def __init__(self):
        super(PeriodCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("B", self.characteristic.read())[0]

    def write(self, value):
        if self.characteristic:
            self.characteristic.write(struct.pack("B", value))


class LiveService(FlowerService):
    name = "Live"
    uuid = to_flower_uuid(0xfa00)

    def __init__(self):
        super(LiveService, self).__init__()
        self.characteristics = [
            LEDCharacteristic(),
            LightCharacteristic(),
            TemperatureCharacteristic(),
            WaterCharacteristic(),
            PeriodCharacteristic(),
            DLICharacteristic(),
            EaCharacteristic(),
            EcbCharacteristic(),
            EcPorusCharacteristic()
        ]


class BatteryCharacteristic(FlowerCharacteristic):
    name = "Battery"
    uuid = UUID("00002a19-0000-1000-8000-00805f9b34fb")

    def __init__(self):
        super(BatteryCharacteristic, self).__init__()

    def read(self):
        if self.characteristic:
            return struct.unpack("b", self.characteristic.read())[0]


class BatteryService(FlowerService):
    name = "Battery"
    uuid = UUID("0000180f-0000-1000-8000-00805f9b34fb")

    def __init__(self):
        super(BatteryService, self).__init__()
        self.characteristics = [
            BatteryCharacteristic(),
        ]


class FlowerDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, handle, data):
        print("Notification")


class FlowerPeripheral(Peripheral):
    addr_type = ADDR_TYPE_PUBLIC

    def __init__(self, dev_addr):
        if not os.path.isfile(helperExe):
            raise ImportError("Cannot find required executable '%s'" % helperExe)

        Peripheral.__init__(self, dev_addr, self.addr_type)
        self.flower_services = {
            TimeService.name: TimeService(),
            LiveService.name: LiveService(),
            BatteryService.name: BatteryService()
        }
        self.dev_addr = dev_addr
        self.setDelegate(FlowerDelegate())

    def print_all_connections(self):
        for service in self.getServices():
            print("-------")
            print(str(service.uuid) + " " + str(service))
            for characteristic in service.getCharacteristics():
                print("    " + str(characteristic.uuid) + " " + str(characteristic)
                      + " Handle " + str(characteristic.getHandle()))

    def _make_all_connections(self):
        for service in self.getServices():
            for _ in service.getCharacteristics():
                pass

    def enable(self):
        self._make_all_connections() # Have to make all connections at start otherwise the Battery can't connect
        for service in self.flower_services:
            self.flower_services[service].enable(self)

    def flower_connect(self):
        Peripheral.connect(self, self.dev_addr, self.addr_type)

    def get_data(self):
        attributes = {
            "Light": [],
            "Temperature": [],
            "Water": [],
            "DLI": [],
            "Ea": [],
            "Ecb": [],
            "EcPorus": []
        }
        self.flower_services["Live"]["Period"].write(1)
        for i in range(3):
            for attribute in attributes:
                attributes[attribute].append(abs(self.flower_services["Live"][attribute].read()))
            time.sleep(1)
        self.flower_services["Live"]["Period"].write(0)
        # Get Median
        for attribute in attributes:
            attributes[attribute] = attributes[attribute][len(attributes[attribute]) / 2] 
        attributes["Battery"] = self.flower_services["Battery"]["Battery"].read()
        return attributes


mac_to_connection = {}


def get_flower_data(flower_mac_address):
    # Caching by MacAddress to reduce connection time.
    if flower_mac_address in mac_to_connection:
        conn = mac_to_connection[flower_mac_address]
    else:
        conn = FlowerPeripheral(flower_mac_address)
        mac_to_connection[flower_mac_address] = conn
        try:
            conn.enable()
        finally:
            conn.disconnect()
    try:
        conn.flower_connect()
        data = conn.get_data()
    finally:
        conn.disconnect()
    return data

if __name__ == '__main__':
    print("test")
    print get_flower_data("A0:14:3D:08:B4:90")

