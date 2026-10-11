from dataclasses import dataclass


@dataclass(frozen=True)
class SystemConfig:
    latitude: float
    longitude: float
    tilt: float = 30.0            # degrees from horizontal
    azimuth: float = 180.0        # pvlib convention: 180 = south
    capacity_kwp: float = 10.0    # DC nameplate
    gamma_pdc: float = -0.004     # power temperature coefficient, 1/degC
    system_losses: float = 0.14   # soiling, wiring, mismatch, availability (fraction)
    inverter_efficiency: float = 0.96
    dc_ac_ratio: float = 1.2
    year: int = 2020

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"latitude out of range: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"longitude out of range: {self.longitude}")
        if not 0 <= self.tilt <= 90:
            raise ValueError(f"tilt must be 0-90 degrees: {self.tilt}")
        if not 0 <= self.azimuth <= 360:
            raise ValueError(f"azimuth must be 0-360 degrees: {self.azimuth}")
        if self.capacity_kwp <= 0:
            raise ValueError("capacity_kwp must be positive")
        if not 0 <= self.system_losses < 1:
            raise ValueError("system_losses must be in [0, 1)")
        if not 0 < self.inverter_efficiency <= 1:
            raise ValueError("inverter_efficiency must be in (0, 1]")
        if self.dc_ac_ratio <= 0:
            raise ValueError("dc_ac_ratio must be positive")