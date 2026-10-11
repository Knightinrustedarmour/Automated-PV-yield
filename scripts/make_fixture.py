"""Download weather once and store fixture + golden result for the tests.

Usage:  python scripts/make_fixture.py            # download weather and golden
        python scripts/make_fixture.py --golden-only   # recompute golden only
"""
import json
import sys
from pathlib import Path

from pvyield.config import SystemConfig
from pvyield.model import annual_summary, simulate
from pvyield.weather import fetch_pvgis, load_csv, save_csv, validate_weather

DATA = Path(__file__).resolve().parents[1] / "tests" / "data"
CFG = SystemConfig(latitude=53.14, longitude=8.21, tilt=30, azimuth=180, capacity_kwp=10, year=2020)

DATA.mkdir(parents=True, exist_ok=True)
weather_path = DATA / "weather_oldenburg_2020.csv"

if "--golden-only" not in sys.argv:
    save_csv(fetch_pvgis(CFG), weather_path)

weather = validate_weather(load_csv(weather_path))
summary = annual_summary(simulate(weather, CFG), CFG)
(DATA / "golden_oldenburg_2020.json").write_text(json.dumps(summary, indent=2))
print(summary)