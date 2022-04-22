from struct import unpack, pack

from bme.exceptions import MissingTemperatureReading
from bme.bmp280 import BMP280Calibration


class BME280Calibration(BMP280Calibration):
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
        h1: int,
        h2: int,
        h3: int,
        h4: int,
        h5: int,
        h6: int,
    ):
        super().__init__(t1, t2, t3, p1, p2, p3, p4, p5, p6, p7, p8, p9)
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.h4 = h4
        self.h5 = h5
        self.h6 = h6

    @classmethod
    def from_bytes(cls, data: bytes) -> "BME280Calibration":
        x, y, z = unpack("<BBB", data[28:31])
        # Use bitshift trick to interpret 12-bit signed integers.
        h4 = unpack("<h", pack("<H", (x << 4) + (y & 0x0F) << 4))[0] >> 4
        h5 = unpack("<h", pack("<H", (y >> 4) + (z << 4) << 4))[0] >> 4
        h6 = unpack("<b", data[31:32])[0]
        return BME280Calibration(
            *unpack("<HhhHhhhhhhhhBhB", data[:28]), h4=h4, h5=h5, h6=h6
        )

    def compensate_humidity(self, raw: int) -> float:
        if self.temperature is None:
            raise MissingTemperatureReading(
                f"A temperature reading is required to compensate humidity data."
            )
        var1 = self.temperature - 76800.0
        var2 = self.h4 * 64.0 + (self.h5 / 16384.0) * var1
        var3 = raw - var2
        var4 = self.h2 / 65536.0
        var5 = 1.0 + (self.h3 / 67108864.0) * var1
        var6 = 1.0 + (self.h6 / 67108864.0) * var1 * var5
        var6 = var3 * var4 * (var5 * var6)

        humidity = var6 * (1.0 - self.h1 * var6 / 524288.0)
        return max(0.0, min(100.0, humidity))
