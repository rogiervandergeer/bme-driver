from dataclasses import dataclass
from math import exp
from typing import Optional


@dataclass()
class BMEMeasurement:
    temperature: Optional[float]
    pressure: Optional[float]
    humidity: Optional[float] = None

    def __repr__(self) -> str:
        values = []
        if self.temperature:
            values.append(f"{self.temperature:1.2f}°C")
        if self.pressure:
            values.append(f"{self.pressure:1.2f}hPa")
        if self.humidity:
            values.append(f"{self.humidity:1.2f}%H")
            if self.temperature:
                values.append(f"{self.absolute_humidity:1.2f} g/m3")
        return f"BMEMeasurement({', '.join(values)})"

    @property
    def absolute_humidity(self) -> Optional[float]:
        if self.humidity is None or self.temperature is None:
            return None
        return (
            13.2471
            * self.humidity
            * exp((17.67 * self.temperature) / (243.5 + self.temperature))
            / (273.15 + self.temperature)
        )
