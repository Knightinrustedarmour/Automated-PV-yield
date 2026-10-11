import pandas as pd
import pvlib

from .config import SystemConfig


def cell_temperature(poa, temp_air, wind_speed):
    return pvlib.temperature.faiman(poa, temp_air, wind_speed)


def dc_power(poa, temp_cell, cfg: SystemConfig):
    """DC power in W after temperature effect and lumped system losses."""
    p = pvlib.pvsystem.pvwatts_dc(
        poa,
        temp_cell,
        cfg.capacity_kwp * 1000.0,
        cfg.gamma_pdc,
    )
    return p * (1.0 - cfg.system_losses)


def ac_power(p_dc, cfg: SystemConfig):
    """AC power in W. Inverter nameplate = DC capacity / DC-AC ratio."""
    pdc0_inv = cfg.capacity_kwp * 1000.0 / cfg.dc_ac_ratio
    return pvlib.inverter.pvwatts(p_dc, pdc0_inv, eta_inv_nom=cfg.inverter_efficiency)


def simulate(weather: pd.DataFrame, cfg: SystemConfig) -> pd.DataFrame:
    out = pd.DataFrame(index=weather.index)
    out["poa_global"] = weather["poa_global"]
    out["temp_cell"] = cell_temperature(
        weather["poa_global"], weather["temp_air"], weather["wind_speed"]
    )
    out["p_dc_w"] = dc_power(out["poa_global"], out["temp_cell"], cfg)
    out["p_ac_w"] = ac_power(out["p_dc_w"], cfg).clip(lower=0.0)
    return out


def annual_summary(result: pd.DataFrame, cfg: SystemConfig) -> dict:
    step_h = (result.index[1] - result.index[0]).total_seconds() / 3600.0
    energy_kwh = float(result["p_ac_w"].sum() * step_h / 1000.0)
    poa_kwh_m2 = float(result["poa_global"].sum() * step_h / 1000.0)
    return {
        "energy_kwh": round(energy_kwh, 1),
        "specific_yield_kwh_per_kwp": round(energy_kwh / cfg.capacity_kwp, 1),
        "poa_irradiation_kwh_m2": round(poa_kwh_m2, 1),
        "performance_ratio": round(energy_kwh / (poa_kwh_m2 * cfg.capacity_kwp), 4),
        "capacity_factor": round(
            energy_kwh / (cfg.capacity_kwp * len(result) * step_h), 4
        ),
        "peak_ac_kw": round(float(result["p_ac_w"].max()) / 1000.0, 2),
    }