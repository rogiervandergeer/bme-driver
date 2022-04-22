from enum import Enum
from time import sleep
from typing import Union

from smbus2 import SMBus

from bme.common import FilterCoefficient, Mode, Oversampling, Status
from bme.exceptions import IncorrectBMEDevice
from bme.measurement import BMEMeasurement
from .calibration import BMP280Calibration


class BMP280MeasurementInterval(Enum):
    interval_0_5 = 0b000
    interval_62_5 = 0b001
    interval_125 = 0b010
    interval_250 = 0b011
    interval_500 = 0b100
    interval_1000 = 0b101
    interval_2000 = 0b110
    interval_4000 = 0b111


class BMP280:
    chip_id: int = 0x58

    def __init__(self, bus: SMBus, address: int = 0x76):
        self.address = address
        self.bus = bus
        if self.id != self.chip_id:
            raise IncorrectBMEDevice(f"Device is not a {self.__class__.__name__}.")
        self._calibration = None

    @property
    def calibration(self) -> "BMP280Calibration":
        """Get the sensor calibration.

        The calibration is user to convert the raw measurement
        values into user-readable values."""
        if self._calibration is None:
            self._read_calibration()
        return self._calibration

    @property
    def id(self) -> int:
        """Read the Chip ID."""
        return self._read(0xD0)[0]

    @property
    def unique_id(self) -> int:
        """Unique sensor id

        As documented here:
        https://community.bosch-sensortec.com/t5/MEMS-sensors-forum/Unique-IDs-in-Bosch-Sensors/td-p/6012"""
        data = self._read(0x83, 4)
        return data[0] + (data[1] << 8) + (((data[3] + (data[2] << 8)) & 0x7FFFF) << 16)

    # ========= #
    # Operation #
    # ========= #

    @property
    def mode(self) -> Mode:
        """Get or set the sensor mode.

        The device has three modes:
        - sleep, in which no measurements are done
        - normal, in which the sensor cycles through standby and measurement periodically
        - forced, in which the sensor takes a single measurement and then returns to sleep mode

        Getting the mode always returns a Mode enum object. When setting the mode the
        strings "sleep", "normal" and "forced" may be used interchangeably with Mode.sleep,
        Mode.normal and Mode.forced."""
        return Mode(self._read_bits(0xF4, mask=0b11))

    @mode.setter
    def mode(self, value: Union[Mode, str]) -> None:
        if not isinstance(value, Mode):
            value = Mode[value]
        self._write_bits(0xF4, value=value.value, mask=0b11)

    def update(self) -> None:
        """Force a single update.

        After the update, the device will return to sleep."""
        self.mode = Mode.forced
        while self.status == Status.measuring:
            sleep(0.0001)

    def enable(self) -> None:
        """Set the mode to normal."""
        self.mode = Mode.normal

    def sleep(self) -> None:
        """Set the mode to sleep."""
        self.mode = Mode.sleep

    def reset(self) -> None:
        """Perform a reset."""
        self._write(0xE0, b"\xB6")

    @property
    def status(self) -> Status:
        """Look up the status of the device."""
        raw = self._read_bits(0xF3, mask=0b00001001)
        return Status.measuring if raw == 0b00001001 else Status(raw)

    # ============= #
    # Configuration #
    # ============= #

    @property
    def measurement_interval(self) -> BMP280MeasurementInterval:
        return BMP280MeasurementInterval(self._read_bits(0xF5, mask=0b11100000) >> 5)

    @measurement_interval.setter
    def measurement_interval(self, value: BMP280MeasurementInterval) -> None:
        self._write_bits(0xF5, mask=0b11100000, value=value.value << 5)

    @property
    def filter_coefficient(self) -> FilterCoefficient:
        return FilterCoefficient(self._read_bits(0xF5, mask=0b00011100) >> 2)

    @filter_coefficient.setter
    def filter_coefficient(self, value: FilterCoefficient) -> None:
        mode = self.mode
        self.sleep()
        self._write_bits(0xF5, mask=0b00011100, value=value.value << 2)
        self.mode = mode

    # ============ #
    # Measurements #
    # ============ #

    @property
    def measurement(self) -> BMEMeasurement:
        data = self._read(0xF7, length=6)
        raw_temperature = int.from_bytes(data[3:6], byteorder="big") >> 4
        raw_pressure = int.from_bytes(data[0:3], byteorder="big") >> 4
        return BMEMeasurement(
            temperature=self.calibration.compensate_temperature(raw_temperature),
            pressure=self.calibration.compensate_pressure(raw_pressure),
        )

    @property
    def pressure(self) -> float:
        """Returns the pressure in hPa."""
        return self.measurement.pressure

    @property
    def temperature(self) -> float:
        """Returns the temperature in °C."""
        return self.measurement.temperature

    # ===================== #
    # Oversampling controls #
    # ===================== #

    @property
    def pressure_oversampling(self) -> Oversampling:
        return Oversampling(self._read_bits(0xF4, mask=0b00011100) >> 2)

    @pressure_oversampling.setter
    def pressure_oversampling(self, value: Oversampling) -> None:
        self._write_bits(0xF4, value=value.value << 2, mask=0b00011100)

    @property
    def temperature_oversampling(self) -> Oversampling:
        return Oversampling(self._read_bits(0xF4, mask=0b11100000) >> 5)

    @temperature_oversampling.setter
    def temperature_oversampling(self, value: Oversampling) -> None:
        self._write_bits(0xF4, value=value.value << 5, mask=0b11100000)

    # ======= #
    # Private #
    # ======= #

    def _read(self, register: int, length: int = 1) -> bytes:
        return bytes(
            self.bus.read_i2c_block_data(self.address, register=register, length=length)
        )

    def _write(self, register: int, value: bytes) -> None:
        self.bus.write_i2c_block_data(self.address, register=register, data=list(value))

    def _read_bits(self, register: int, mask: int) -> int:
        return self._read(register=register)[0] & mask

    def _write_bits(self, register: int, value: int, mask: int) -> None:
        old_bits = self._read_bits(register=register, mask=self._invert_mask(mask))
        new_bits = old_bits | (value & mask)
        self._write(register=register, value=bytes([new_bits]))

    def _read_calibration(self) -> None:
        """Read the sensor calibration from NVM."""
        data = self._read(0x88, length=24)
        self._calibration = BMP280Calibration.from_bytes(data)

    @staticmethod
    def _invert_mask(mask: int) -> int:
        return 0xFF - mask


__all__ = [
    BMP280,
    BMP280MeasurementInterval,
]
