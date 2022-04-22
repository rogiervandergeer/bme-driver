from bme.bme280 import BME280
from pytest import fixture, mark


@fixture()
@mark.parametrize(
    "mask, inverted",
    [
        (0b1111_0000, 0b0000_1111),
        (0b1111_1111, 0b0000_0000),
        (0b1010_1010, 0b0101_0101),
    ],
)
def test_invert_mask(mask, inverted):
    assert BME280._invert_mask(mask) == inverted
    assert BME280._invert_mask(inverted) == mask
