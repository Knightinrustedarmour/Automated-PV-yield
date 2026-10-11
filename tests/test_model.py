from dataclasses import replace

import pandas as pd
import pytest

from pvyield.model import ac_power, annual_summary, dc_power, simulate


def test_dc_power_at_stc_equals_nameplate(cfg):
    no_loss = replace(cfg, system_losses=0.0)
    p = dc_power(pd.Series([1000.0]), pd.Series([25.0]), no_loss)
    assert p.iloc[0] == pytest.approx(10000.0)


def test_system_losses_reduce_dc_power(cfg):
    p = dc_power(pd.Series([1000.0]), pd.Series([25.0]), cfg)   # 14 % losses
    assert p.iloc[0] == pytest.approx(8600.0)


def test_zero_irradiance_gives_zero_power(cfg):
    p_dc = dc_power(pd.Series([0.0]), pd.Series([10.0]), cfg)
    assert p_dc.iloc[0] == 0.0
    assert ac_power(p_dc, cfg).iloc[0] == 0.0


def test_hotter_cell_produces_less(cfg):
    cool = dc_power(pd.Series([800.0]), pd.Series([25.0]), cfg).iloc[0]
    hot = dc_power(pd.Series([800.0]), pd.Series([60.0]), cfg).iloc[0]
    assert hot < cool


def test_inverter_clips_at_nameplate(cfg):
    limit = cfg.capacity_kwp * 1000 / cfg.dc_ac_ratio * cfg.inverter_efficiency
    p_ac = ac_power(pd.Series([50000.0]), cfg)
    assert p_ac.max() <= limit + 1e-6


def test_simulate_output_shape(cfg, weather):
    out = simulate(weather, cfg)
    assert len(out) == len(weather)
    assert {"poa_global", "temp_cell", "p_dc_w", "p_ac_w"} <= set(out.columns)
    assert (out["p_ac_w"] >= 0).all()


def test_annual_summary_is_physically_plausible(cfg, weather):
    s = annual_summary(simulate(weather, cfg), cfg)
    assert 600 < s["specific_yield_kwh_per_kwp"] < 1300
    assert 0.6 < s["performance_ratio"] < 0.95
    assert 0.0 < s["capacity_factor"] < 0.25


def test_energy_scales_linearly_with_capacity(cfg, weather):
    e1 = annual_summary(simulate(weather, cfg), cfg)["energy_kwh"]
    big = replace(cfg, capacity_kwp=20.0)
    e2 = annual_summary(simulate(weather, big), big)["energy_kwh"]
    assert e2 == pytest.approx(2 * e1, rel=1e-3)