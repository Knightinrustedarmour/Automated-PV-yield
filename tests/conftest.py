from pathlib import Path

import pytest

from pvyield.config import SystemConfig
from pvyield.weather import load_csv

DATA = Path(__file__).parent / "data"


@pytest.fixture
def cfg():
    return SystemConfig(latitude=53.14, longitude=8.21, tilt=30, azimuth=180,
                        capacity_kwp=10, year=2020)


@pytest.fixture
def weather():
    return load_csv(DATA / "weather_oldenburg_2020.csv")