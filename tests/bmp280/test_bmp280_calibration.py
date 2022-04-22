from pytest import approx, fixture

from bme.bmp280.calibration import BMP280Calibration


@fixture()
def bmp280_calibration() -> BMP280Calibration:
    return BMP280Calibration(
        t1=27504,
        t2=26435,
        t3=-1000,
        p1=36477,
        p2=-10685,
        p3=3024,
        p4=2855,
        p5=140,
        p6=-7,
        p7=15500,
        p8=-14600,
        p9=6000,
    )


class TestCalibration:
    def test_compensate_temperature(self, bmp280_calibration: BMP280Calibration):
        assert bmp280_calibration.compensate_temperature(519888) == approx(
            25.08, abs=0.005
        )

    def test_compensate_pressure(self, bmp280_calibration: BMP280Calibration):
        bmp280_calibration.compensate_temperature(
            519888
        )  # We need to initialize with temperature
        assert bmp280_calibration.compensate_pressure(415148) == approx(100653, abs=0.5)
