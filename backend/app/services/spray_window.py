"""Spray window rules (wind + precip + humidity).

Priority: danger > caution > safe.
"""

from __future__ import annotations

from typing import Literal

HIGH_RH_THRESHOLD = 80.0  # percent; tunable


def classify_spray(
    wind_kmh: float,
    next_6h_precip_mm: float,
    relative_humidity_percent: float,
) -> tuple[Literal["safe", "caution", "danger"], list[str]]:
    reasons: list[str] = []

    if wind_kmh > 20:
        reasons.append(f"Wind {wind_kmh:.1f} km/h exceeds 20 km/h")
    if next_6h_precip_mm > 1:
        reasons.append(f"Next 6h precipitation {next_6h_precip_mm:.2f} mm exceeds 1 mm")

    if wind_kmh > 20 or next_6h_precip_mm > 1:
        return "danger", reasons

    caution_reasons: list[str] = []
    if 15 <= wind_kmh <= 20:
        caution_reasons.append(f"Wind {wind_kmh:.1f} km/h in caution band (15–20 km/h)")
    if relative_humidity_percent >= HIGH_RH_THRESHOLD:
        caution_reasons.append(
            f"High humidity {relative_humidity_percent:.0f}% (≥ {HIGH_RH_THRESHOLD:.0f}%)"
        )

    if caution_reasons:
        return "caution", caution_reasons

    if wind_kmh < 15 and next_6h_precip_mm < 1:
        return "safe", ["Wind under 15 km/h and next 6h precipitation under 1 mm"]

    return "safe", ["Conditions acceptable for spray per configured rules"]
