import pandas as pd
from pvlib.iotools import get_pvgis_hourly

from .config import SystemConfig

REQUIRED_COLUMNS = ["poa_global", "temp_air", "wind_speed"]


def fetch_pvgis(cfg: SystemConfig) -> pd.DataFrame:
    """Download hourly POA irradiance and weather for one year from PVGIS."""
    result = get_pvgis_hourly(
        latitude=cfg.latitude,
        longitude=cfg.longitude,
        start=cfg.year,
        end=cfg.year,
        surface_tilt=cfg.tilt,
        surface_azimuth=cfg.azimuth,   # pvlib converts to PVGIS convention
        components=True,
        pvcalculation=False,
    )
    data = result[0]                   # first element is always the DataFrame
    data["poa_global"] = (
        data["poa_direct"] + data["poa_sky_diffuse"] + data["poa_ground_diffuse"]
    )
    return data[REQUIRED_COLUMNS].copy()


def load_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def save_csv(df: pd.DataFrame, path) -> None:
    df.to_csv(path)


def validate_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Raise ValueError if the weather data is not usable. Returns df if fine."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("index must be a DatetimeIndex")
    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("weather data contains NaN values")
    if not df.index.is_monotonic_increasing or df.index.has_duplicates:
        raise ValueError("timestamps must be sorted and unique")
    if not df["poa_global"].between(0, 1500).all():
        raise ValueError("poa_global outside 0-1500 W/m2")
    if not df["temp_air"].between(-60, 60).all():
        raise ValueError("temp_air outside -60 to 60 degC")
    if not df["wind_speed"].between(0, 60).all():
        raise ValueError("wind_speed outside 0-60 m/s")
    if len(df) < 24 * 28:
        raise ValueError("fewer than 28 days of data")
    return df