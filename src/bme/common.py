from enum import Enum


class Status(Enum):
    idle = 0x00
    copying = 0b0001
    measuring = 0b1000


class FilterCoefficient(Enum):
    off = 0b000
    f2 = 0b001
    f4 = 0b010
    f8 = 0b011
    f16 = 0b100


class Mode(Enum):
    """Sensor mode"""

    sleep = 0x00
    forced = 0x01
    normal = 0x03


class Oversampling(Enum):
    skipped = 0x00
    oversample_1 = 0x01
    oversample_2 = 0x02
    oversample_4 = 0x03
    oversample_8 = 0x04
    oversample_16 = 0x05
