from typing import Optional

from smbus2 import SMBus


from bme import BMP280, BME280
from bme.exceptions import IncorrectBMEDevice, NoDeviceFound, UnsupportedDevice


def autodetect(bus: SMBus, address: Optional[int] = None):
    if address is None:
        for address in (0x76, 0x77):
            try:
                result = autodetect(bus=bus, address=address)
            except NoDeviceFound:
                continue
            return result
        raise NoDeviceFound("No device was found on either address.")
    response = False
    for sensor in (BMP280, BME280):
        try:
            device = sensor(bus=bus, address=address)
        except OSError:
            continue
        except IncorrectBMEDevice:
            response = True
            continue
        return device
    if response:
        raise UnsupportedDevice(f"The device on address {hex(address)} is unsupported.")
    raise NoDeviceFound(f"No device was found on address {hex(address)}")
