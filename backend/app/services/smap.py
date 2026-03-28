"""SMAP soil moisture — mocked until NASA Earthdata + LANCE pipeline is wired."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class MockSmapResult:
    value_percent: float
    series_7d: list[dict]


def _seed(lat: float, lng: float) -> float:
    h = hashlib.sha256(f"{lat:.5f},{lng:.5f}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 2**32


def mock_smap(lat: float, lng: float) -> MockSmapResult:
    """Deterministic mock moisture % and 7-day series from coordinates."""
    seed = _seed(lat, lng)
    base = 35.0 + 40.0 * seed
    today = date.today()
    series: list[dict] = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        wobble = 4.0 * math.sin(seed * 10.0 + i)
        series.append(
            {
                "date": d.isoformat(),
                "value_percent": max(5.0, min(95.0, base + wobble)),
            }
        )
    current = round(series[-1]["value_percent"], 2)
    for p in series:
        p["value_percent"] = round(p["value_percent"], 2)
    return MockSmapResult(value_percent=current, series_7d=series)
