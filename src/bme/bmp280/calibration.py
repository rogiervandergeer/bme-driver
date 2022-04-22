from struct import unpack
from typing import Optional

from bme.exceptions import MissingTemperatureReading


class BMP280Calibration:
    def __init__(
        self,
        t1: int,
        t2: int,
        t3: int,
        p1: int,
        p2: int,
        p3: int,
        p4: int,
        p5: int,
        p6: int,
        p7: int,
        p8: int,
        p9: int,
    ):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5
        self.p6 = p6
        self.p7 = p7
        self.p8 = p8
        self.p9 = p9
        self.temperature = None

    @classmethod
    def from_bytes(cls, data: bytes) -> "BMP280Calibration":
        return BMP280Calibration(*unpack("<HhhHhhhhhhhh", data))

    def compensate_pressure(self, raw: int) -> Optional[float]:
        """Perform pressure compensation

        Accepts the raw sensor value and returns hPa.
        As the pressure compensation depends on the temperature,
        a temperature compensation must be performed before"""
        if self.temperature is None:
            raise MissingTemperatureReading(
                f"A temperature reading is required to compensate pressure data."
            )
        if raw == 0x80000:
            return None
        var1 = self.temperature / 2.0 - 64000.0
        var2 = var1 * var1 * self.p6 / 32768.0
        var2 = var2 + var1 * self.p5 * 2
        var2 = var2 / 4.0 + self.p4 * 65536.0
        var1 = (self.p3 * var1 * var1 / 524288.0 + self.p2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.p1
        pressure = 1048576.0 - raw
        pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
        var1 = self.p9 * pressure * pressure / 2147483648.0
        var2 = pressure * self.p8 / 32768.0
        return pressure + (var1 + var2 + self.p7) / 16.0

    def compensate_temperature(self, raw: int) -> Optional[float]:
        """Perform temperature compensation

        Accepts the raw sensor value and returns °C."""
        if raw == 0x80000:
            return None
        var1 = (raw / 16384.0 - self.t1 / 1024.0) * self.t2
        var2 = raw / 131072.0 - self.t1 / 8192.0
        var2 = var2 * var2 * self.t3
        self.temperature = var1 + var2
        return self.temperature / 5120.0
