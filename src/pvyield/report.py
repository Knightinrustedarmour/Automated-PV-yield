import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")   # no display needed, required in CI and Docker
import matplotlib.pyplot as plt


def write_report(result, summary: dict, outdir) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    result.to_csv(out / "hourly_results.csv")

    monthly = result["p_ac_w"].resample("MS").sum() / 1000.0   # kWh for hourly data
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(monthly.index.strftime("%b"), monthly.values, color="#888822")
    ax.set_ylabel("AC energy (kWh)")
    ax.set_title(f"Monthly yield, total {summary['energy_kwh']:.0f} kWh")
    fig.tight_layout()
    fig.savefig(out / "monthly_energy.png", dpi=150)
    plt.close(fig)

    july = result.loc[result.index.month == 7].groupby(result.loc[result.index.month == 7].index.hour)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(july["p_ac_w"].mean().index, july["p_ac_w"].mean().values / 1000.0)
    ax.set_xlabel("Hour (UTC)")
    ax.set_ylabel("Mean AC power (kW)")
    ax.set_title("Average July day")
    fig.tight_layout()
    fig.savefig(out / "july_day.png", dpi=150)
    plt.close(fig)