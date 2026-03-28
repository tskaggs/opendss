"""Deterministic fallback when NASA POWER is unreachable."""

from __future__ import annotations

import hashlib
import math
from datetime import date, timedelta

from app.services.nasa_power import PowerBundle


def synthetic_power_bundle(lat: float, lng: float) -> PowerBundle:
    h = hashlib.sha256(f"{lat:.4f},{lng:.4f}".encode()).digest()
    seed = int.from_bytes(h[:4], "big") / 2**32
    today = date.today()
    weather_series = []
    soil_series = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        ds = d.isoformat()
        temp = 12.0 + 8.0 * math.sin(seed * 5 + i)
        weather_series.append(
            {
                "date": ds,
                "temp_c": round(temp, 1),
                "precip_mm": max(0.0, 2.0 * math.cos(seed + i)),
                "wind_kmh": round(8.0 + 6.0 * seed, 1),
                "rh_percent": round(55.0 + 20.0 * seed, 0),
            }
        )
        soil_series.append({"date": ds, "value_c": round(temp - 1.0, 1)})
    return PowerBundle(
        wind_speed_kmh=10.0 + 5.0 * seed,
        relative_humidity_percent=60.0,
        next_6h_precip_mm=0.2,
        precip_risk="low",
        weather_series_7d=weather_series,
        soil_temp_series_7d=soil_series,
        soil_temp_c=soil_series[-1]["value_c"],
    )
