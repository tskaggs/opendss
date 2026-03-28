"""SoilGrids v2.0 REST (ISRIC) — point queries."""

from __future__ import annotations

import httpx

SOILGRIDS_QUERY = "https://rest.isric.org/soilgrids/v2.0/properties/query"


async def fetch_soil_properties(
    lat: float, lng: float, client: httpx.AsyncClient
) -> dict[str, float | None]:
    """Return texture, bulk density (bdod), and organic carbon (soc) means at 0–5 cm."""
    params: list[tuple[str, str | float]] = [
        ("lon", lng),
        ("lat", lat),
        ("depth", "0-5cm"),
        ("value", "mean"),
    ]
    for prop in ("clay", "sand", "silt", "bdod", "soc"):
        params.append(("property", prop))

    r = await client.get(SOILGRIDS_QUERY, params=params, timeout=60.0)
    r.raise_for_status()
    data = r.json()

    out: dict[str, float | None] = {
        "clay_percent": None,
        "sand_percent": None,
        "silt_percent": None,
        "bulk_density_kg_m3": None,
        "organic_carbon_g_kg": None,
    }

    for layer in data.get("properties", {}).get("layers", []):
        name = layer.get("name", "")
        depths = layer.get("depths", [])
        if not depths:
            continue
        mean = depths[0].get("values", {}).get("mean")
        if mean is None:
            continue
        try:
            v = float(mean)
        except (TypeError, ValueError):
            continue
        if name == "clay":
            out["clay_percent"] = v
        elif name == "sand":
            out["sand_percent"] = v
        elif name == "silt":
            out["silt_percent"] = v
        elif name == "bdod":
            # ISRIC bdod: cg/cm³ → kg/m³ (×10)
            out["bulk_density_kg_m3"] = v * 10.0
        elif name == "soc":
            # SOC mean is typically reported in g/kg scale for topsoil
            out["organic_carbon_g_kg"] = v

    return out
