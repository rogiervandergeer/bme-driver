from pytest import approx, fixture

from bme.bme280.calibration import BME280Calibration


@fixture()
def calibration() -> BME280Calibration:
    return BME280Calibration(
        t1=28009,
        t2=25654,
        t3=50,
        p1=39145,
        p2=-10750,
        p3=3024,
        p4=5667,
        p5=-120,
        p6=7,
        p7=15500,
        p8=-14600,
        p9=6000,
        h1=75,
        h2=376,
        h3=0,
        h4=286,
        h5=50,
        h6=30,
    )


class TestCalibration:
    def test_from_bytes(self):
        data = [
            237,
            109,
            234,
            101,
            50,
            0,
            46,
            144,
            5,
            214,
            208,
            11,
            61,
            30,
            206,
            255,
            249,
            255,
            12,
            48,
            32,
            209,
            136,
            19,
            0,
            69,
            1,
            0,
            26,
            39,
            3,
            30,
            180,
        ]
        calibration = BME280Calibration.from_bytes(bytes(data))
        assert calibration.__dict__ == {
            "t1": 28141,
            "t2": 26090,
            "t3": 50,
            "p1": 36910,
            "p2": -10747,
            "p3": 3024,
            "p4": 7741,
            "p5": -50,
            "p6": -7,
            "p7": 12300,
            "p8": -12000,
            "p9": 5000,
            "h1": 0,
            "h2": 325,
            "h3": 0,
            "h4": 423,
            "h5": 50,
            "h6": 30,
            "temperature": None,
        }

    def test_compensate_temperature(self, calibration: BME280Calibration):
        assert calibration.compensate_temperature(529191) == approx(24.78948)

    def test_compensate_humidity(self, calibration: BME280Calibration):
        calibration.compensate_temperature(529191)
        assert calibration.compensate_humidity(30281) == approx(68.66996)

    def test_compensate_pressure(self, calibration: BME280Calibration):
        calibration.compensate_temperature(529191)
        assert calibration.compensate_pressure(326816) == approx(100661.51635)
