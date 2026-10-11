import pandas as pd
import pvlib
import pytest

from pvyield.config import SystemConfig
from pvyield.geometry import clearsky_poa, solar_position


def test_equator_equinox_noon_sun_nearly_overhead():
    times = pd.DatetimeIndex(["2020-03-20 12:00"], tz="UTC")
    assert solar_position(0.0, 0.0, times)["elevation"].iloc[0] > 85


def test_oldenburg_summer_solstice_max_elevation():
    times = pd.date_range("2020-06-21", periods=24 * 60, freq="min", tz="UTC")
    elev = solar_position(53.14, 8.21, times)["elevation"].max()
    assert 59.5 < elev < 61.0


def test_sun_below_horizon_at_midnight_in_winter():
    times = pd.DatetimeIndex(["2020-12-21 00:00"], tz="UTC")
    assert solar_position(53.14, 8.21, times)["elevation"].iloc[0] < 0


def test_clearsky_poa_is_zero_at_night(cfg):
    times = pd.DatetimeIndex(["2020-12-21 00:00"], tz="UTC")
    assert clearsky_poa(cfg, times).iloc[0] == pytest.approx(0.0, abs=1e-6)


def test_horizontal_plane_poa_matches_ghi():
    flat = SystemConfig(latitude=53.14, longitude=8.21, tilt=0)
    times = pd.DatetimeIndex(["2020-06-21 11:00"], tz="UTC")
    ghi = pvlib.location.Location(53.14, 8.21, tz="UTC").get_clearsky(times)["ghi"]
    assert clearsky_poa(flat, times).iloc[0] == pytest.approx(ghi.iloc[0], rel=0.02)


def test_clearsky_poa_within_physical_bounds(cfg):
    times = pd.date_range("2020-06-21", periods=24, freq="h", tz="UTC")
    poa = clearsky_poa(cfg, times)
    assert (poa >= 0).all() and (poa <= 1400).all()