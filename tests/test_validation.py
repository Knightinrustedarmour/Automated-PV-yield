import pandas as pd
import pytest

from pvyield.config import SystemConfig
from pvyield.weather import validate_weather


def good_df(n=24 * 30):
    idx = pd.date_range("2020-06-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {"poa_global": 100.0, "temp_air": 15.0, "wind_speed": 3.0}, index=idx
    )


def test_good_weather_passes():
    assert len(validate_weather(good_df())) == 720


def test_missing_column_rejected():
    with pytest.raises(ValueError, match="missing columns"):
        validate_weather(good_df().drop(columns=["wind_speed"]))


def test_nan_rejected():
    df = good_df()
    df.iloc[5, 0] = float("nan")
    with pytest.raises(ValueError, match="NaN"):
        validate_weather(df)


def test_negative_irradiance_rejected():
    df = good_df()
    df.iloc[5, 0] = -10.0
    with pytest.raises(ValueError, match="poa_global"):
        validate_weather(df)


def test_too_short_series_rejected():
    with pytest.raises(ValueError, match="28 days"):
        validate_weather(good_df(n=48))


def test_duplicate_timestamps_rejected():
    df = good_df()
    with pytest.raises(ValueError, match="unique"):
        validate_weather(pd.concat([df, df.iloc[:1]]).sort_index())


@pytest.mark.parametrize(
    "kwargs",
    [
        {"latitude": 95, "longitude": 0},
        {"latitude": 0, "longitude": 200},
        {"latitude": 0, "longitude": 0, "tilt": 120},
        {"latitude": 0, "longitude": 0, "capacity_kwp": -1},
        {"latitude": 0, "longitude": 0, "system_losses": 1.2},
    ],
)
def test_invalid_system_config_rejected(kwargs):
    with pytest.raises(ValueError):
        SystemConfig(**kwargs)