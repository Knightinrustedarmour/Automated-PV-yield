import pandas as pd
import pvlib

from .config import SystemConfig


def solar_position(lat: float, lon: float, times: pd.DatetimeIndex) -> pd.DataFrame:
    return pvlib.solarposition.get_solarposition(times, lat, lon)


def clearsky_poa(cfg: SystemConfig, times: pd.DatetimeIndex) -> pd.Series:
    """Clear-sky plane-of-array irradiance (W/m2) for the configured tilt/azimuth."""
    loc = pvlib.location.Location(cfg.latitude, cfg.longitude, tz=str(times.tz))
    cs = loc.get_clearsky(times, model="ineichen")
    sp = loc.get_solarposition(times)
    poa = pvlib.irradiance.get_total_irradiance(
        cfg.tilt, cfg.azimuth,
        sp["apparent_zenith"], sp["azimuth"],
        cs["dni"], cs["ghi"], cs["dhi"],
        albedo=0.2,
    )
    return poa["poa_global"].fillna(0.0)