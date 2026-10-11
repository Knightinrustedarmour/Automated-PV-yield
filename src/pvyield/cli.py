import argparse

from .config import SystemConfig
from .model import annual_summary, simulate
from .report import write_report
from .weather import fetch_pvgis, load_csv, validate_weather


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="PV yield assessment")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--tilt", type=float, default=30.0)
    p.add_argument("--azimuth", type=float, default=180.0)
    p.add_argument("--kwp", type=float, default=10.0)
    p.add_argument("--year", type=int, default=2020)
    p.add_argument("--weather-csv", help="use a local weather file instead of PVGIS")
    p.add_argument("--out", default="outputs")
    a = p.parse_args(argv)

    cfg = SystemConfig(
        latitude=a.lat, longitude=a.lon, tilt=a.tilt, azimuth=a.azimuth,
        capacity_kwp=a.kwp, year=a.year,
    )
    weather = load_csv(a.weather_csv) if a.weather_csv else fetch_pvgis(cfg)
    validate_weather(weather)
    result = simulate(weather, cfg)
    summary = annual_summary(result, cfg)
    write_report(result, summary, a.out)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())