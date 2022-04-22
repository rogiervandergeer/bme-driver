class NoDeviceFound(ValueError):
    pass


class IncorrectBMEDevice(ValueError):
    pass


class MissingTemperatureReading(ValueError):
    pass


class UnsupportedDevice(NotImplementedError):
    pass
