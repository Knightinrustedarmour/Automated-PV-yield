import pytest

from pvyield.weather import fetch_pvgis, validate_weather


@pytest.mark.integration
def test_pvgis_returns_a_valid_year(cfg):
    df = fetch_pvgis(cfg)
    validate_weather(df)
    assert len(df) in (8760, 8784)
    assert df.index.tz is not None
    annual_poa = df["poa_global"].sum() / 1000.0   # kWh/m2, hourly data
    assert 900 < annual_poa < 1500


@pytest.mark.integration
def test_pvgis_still_matches_stored_fixture(cfg, weather):
    """Detects upstream data changes: live download vs the committed file."""
    live = fetch_pvgis(cfg)["poa_global"].sum()
    stored = weather["poa_global"].sum()
    assert live == pytest.approx(stored, rel=0.01)