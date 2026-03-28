"""Heuristic "ready to plant" from soil temperature and moisture."""

from __future__ import annotations

MIN_SOIL_TEMP_C = 10.0
MIN_MOISTURE_PCT = 25.0
MAX_MOISTURE_PCT = 85.0


def assess_ready_to_plant(soil_temp_c: float, soil_moisture_pct: float) -> tuple[bool, str]:
    if soil_temp_c < MIN_SOIL_TEMP_C:
        return (
            False,
            f"Soil temperature {soil_temp_c:.1f}°C is below planting minimum ({MIN_SOIL_TEMP_C:.0f}°C).",
        )
    if soil_moisture_pct < MIN_MOISTURE_PCT:
        return (
            False,
            f"Soil moisture {soil_moisture_pct:.0f}% is too dry for safe germination (below {MIN_MOISTURE_PCT:.0f}%).",
        )
    if soil_moisture_pct > MAX_MOISTURE_PCT:
        return (
            False,
            f"Soil moisture {soil_moisture_pct:.0f}% is too high; delay planting to avoid compaction (above {MAX_MOISTURE_PCT:.0f}%).",
        )
    return (
        True,
        f"Soil temp {soil_temp_c:.1f}°C and moisture {soil_moisture_pct:.0f}% are within typical planting bands.",
    )
