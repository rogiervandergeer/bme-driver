from enum import Enum
from time import sleep
from typing import Union

from smbus2 import SMBus

from bme.bmp280 import BMP280
from bme.common import Mode, Oversampling, Status
from bme.measurement import BMEMeasurement
from .calibration import BME280Calibration


class BME280MeasurementInterval(Enum):
    interval_0_5 = 0b000
    interval_10 = 0b110
    interval_20 = 0b111
    interval_62_5 = 0b001
    interval_125 = 0b010
    interval_250 = 0b011
    interval_500 = 0b100
    interval_1000 = 0b101


class BME280(BMP280):
    chip_id: int = 0x60

    @property
    def calibration(self) -> "BME280Calibration":
        """Get the sensor calibration.

        The calibration is user to convert the raw measurement
        values into user-readable values."""
        if self._calibration is None:
            self._read_calibration()
        return self._calibration

    # ============= #
    # Configuration #
    # ============= #

    @property
    def measurement_interval(self) -> BME280MeasurementInterval:
        return BME280MeasurementInterval(self._read_bits(0xF5, mask=0b11100000) >> 5)

    @measurement_interval.setter
    def measurement_interval(self, value: BME280MeasurementInterval) -> None:
        self._write_bits(0xF5, mask=0b11100000, value=value.value << 5)

    # ============ #
    # Measurements #
    # ============ #

    @property
    def measurement(self) -> BMEMeasurement:
        data = self._read(0xF7, length=8)
        raw_temperature = int.from_bytes(data[3:6], byteorder="big") >> 4
        raw_pressure = int.from_bytes(data[0:3], byteorder="big") >> 4
        raw_humidity = int.from_bytes(data[6:], byteorder="big")
        return BMEMeasurement(
            temperature=self.calibration.compensate_temperature(raw_temperature),
            pressure=self.calibration.compensate_pressure(raw_pressure),
            humidity=self.calibration.compensate_humidity(raw_humidity),
        )

    @property
    def humidity(self) -> float:
        """Returns the relative humidity in %H."""
        return self.measurement.humidity

    @property
    def absolute_humidity(self) -> float:
        """Returns the absolute humidity in g/m3."""
        return self.measurement.absolute_humidity

    # ===================== #
    # Oversampling controls #
    # ===================== #

    @property
    def humidity_oversampling(self) -> Oversampling:
        return Oversampling(self._read_bits(0xF2, mask=0b00000111))

    @humidity_oversampling.setter
    def humidity_oversampling(self, value: Oversampling) -> None:
        self._write_bits(0xF2, value.value, mask=0b00000111)
        self.mode = self.mode  # Update only takes effect after writing the mode.

    # ======= #
    # Private #
    # ======= #

    def _read_calibration(self) -> None:
        """Read the sensor calibration from NVM."""
        data = self._read(0x88, length=25) + self._read(0xE1, length=7)
        self._calibration = BME280Calibration.from_bytes(data)


__all__ = [BME280, BME280MeasurementInterval]
