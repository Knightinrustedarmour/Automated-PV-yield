import json
from pathlib import Path

import pytest

from pvyield.model import annual_summary, simulate

GOLDEN = json.loads(
    (Path(__file__).parent / "data" / "golden_oldenburg_2020.json").read_text()
)


@pytest.mark.parametrize("key", list(GOLDEN))
def test_summary_matches_golden(cfg, weather, key):
    summary = annual_summary(simulate(weather, cfg), cfg)
    assert summary[key] == pytest.approx(GOLDEN[key], rel=0.005), (
        f"{key} changed from {GOLDEN[key]} to {summary[key]}. "
        "If intentional, run: python scripts/make_fixture.py --golden-only"
    )