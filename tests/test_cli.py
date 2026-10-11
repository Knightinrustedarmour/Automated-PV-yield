import json
from pathlib import Path

from pvyield.cli import main


def test_cli_end_to_end(tmp_path):
    csv = Path(__file__).parent / "data" / "weather_oldenburg_2020.csv"
    code = main(["--lat", "53.14", "--lon", "8.21",
                 "--weather-csv", str(csv), "--out", str(tmp_path)])
    assert code == 0
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["energy_kwh"] > 0
    assert (tmp_path / "monthly_energy.png").exists()
    assert (tmp_path / "hourly_results.csv").exists()