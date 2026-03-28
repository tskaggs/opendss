"""NASA POWER Data Services (async httpx)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

import httpx

POWER_DAILY = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_HOURLY = "https://power.larc.nasa.gov/api/temporal/hourly/point"

PARAMS_DAILY = "T2M,PRECTOTCORR,WS10M,RH2M,TSOIL1"


@dataclass
class PowerBundle:
    wind_speed_kmh: float
    relative_humidity_percent: float
    next_6h_precip_mm: float
    precip_risk: Literal["low", "medium", "high"]
    weather_series_7d: list[dict]
    soil_temp_series_7d: list[dict]
    soil_temp_c: float


async def fetch_power_bundle(lat: float, lng: float, client: httpx.AsyncClient) -> PowerBundle:
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)
    start_s = start.strftime("%Y%m%d")
    end_s = today.strftime("%Y%m%d")

    r = await client.get(
        POWER_DAILY,
        params={
            "parameters": PARAMS_DAILY,
            "community": "AG",
            "longitude": lng,
            "latitude": lat,
            "start": start_s,
            "end": end_s,
            "format": "JSON",
        },
        timeout=60.0,
    )
    r.raise_for_status()
    payload = r.json()
    param_block = payload.get("properties", {}).get("parameter", {})

    def series_for(key: str) -> dict[str, float]:
        block = param_block.get(key, {})
        out: dict[str, float] = {}
        for k, v in block.items():
            if _is_number(v):
                kk = k.split("T", 1)[0] if "T" in k else k
                out[kk] = float(v)
        return out

    t2m = series_for("T2M")
    prec = series_for("PRECTOTCORR")
    ws = series_for("WS10M")
    rh = series_for("RH2M")
    tsoil = series_for("TSOIL1")

    dates_sorted: list[str] = []
    d = start
    while d <= today:
        dates_sorted.append(d.strftime("%Y%m%d"))
        d += timedelta(days=1)
    weather_series_7d: list[dict] = []
    soil_temp_series_7d: list[dict] = []
    max_precip_7d = 0.0

    for d in dates_sorted:
        p = prec.get(d)
        if p is not None:
            max_precip_7d = max(max_precip_7d, p)
        air_c = t2m.get(d)
        soil_raw = tsoil.get(d) if tsoil else None
        soil_c = _to_celsius(soil_raw) if soil_raw is not None else _to_celsius(air_c)
        weather_series_7d.append(
            {
                "date": _fmt_date(d),
                "temp_c": _to_celsius(air_c),
                "precip_mm": p,
                "wind_kmh": ws.get(d),
                "rh_percent": rh.get(d),
            }
        )
        soil_temp_series_7d.append(
            {
                "date": _fmt_date(d),
                "value_c": float(soil_c) if soil_c is not None else float(_to_celsius(air_c) or 0.0),
            }
        )

    last = dates_sorted[-1] if dates_sorted else None

    def last_valid(series: dict[str, float], default: float) -> float:
        for d in reversed(dates_sorted):
            v = series.get(d)
            if v is not None and _is_number(v):
                return float(v)
        return default

    wind_now = last_valid(ws, 5.0)
    rh_now = last_valid(rh, 60.0)
    soil_now = soil_temp_series_7d[-1]["value_c"] if soil_temp_series_7d else 12.0

    next_6h = await _sum_next_6h_precip_mm(lat, lng, client)

    if next_6h > 5 or max_precip_7d > 15:
        precip_risk = "high"
    elif next_6h > 1 or max_precip_7d > 5:
        precip_risk = "medium"
    else:
        precip_risk = "low"

    return PowerBundle(
        wind_speed_kmh=wind_now,
        relative_humidity_percent=rh_now,
        next_6h_precip_mm=next_6h,
        precip_risk=precip_risk,
        weather_series_7d=weather_series_7d,
        soil_temp_series_7d=soil_temp_series_7d,
        soil_temp_c=float(soil_now),
    )


async def _sum_next_6h_precip_mm(lat: float, lng: float, client: httpx.AsyncClient) -> float:
    now = datetime.now(timezone.utc)
    start_d = now.date()
    end_d = start_d + timedelta(days=1)
    r = await client.get(
        POWER_HOURLY,
        params={
            "parameters": "PRECTOTCORR",
            "community": "AG",
            "longitude": lng,
            "latitude": lat,
            "start": start_d.strftime("%Y%m%d"),
            "end": end_d.strftime("%Y%m%d"),
            "format": "JSON",
        },
        timeout=60.0,
    )
    r.raise_for_status()
    block = r.json().get("properties", {}).get("parameter", {}).get("PRECTOTCORR", {})

    total = 0.0
    for i in range(6):
        dt = now + timedelta(hours=i)
        keys = (
            dt.strftime("%Y%m%d%H"),
            f"{dt.strftime('%Y%m%d')}T{dt.hour:02d}",
        )
        val = None
        for k in keys:
            if k in block and _is_number(block[k]):
                val = float(block[k])
                break
        if val is None:
            for bk, bv in block.items():
                if len(bk) >= 10 and bk.startswith(dt.strftime("%Y%m%d")) and _is_number(bv):
                    try:
                        suf = bk.replace(dt.strftime("%Y%m%d"), "").lstrip("T")
                        h = int(suf[:2]) if suf else -1
                        if h == dt.hour:
                            val = float(bv)
                            break
                    except ValueError:
                        continue
        if val is not None:
            total += val
    return max(0.0, total)


POWER_MISSING = -999.0


def _is_number(v: object) -> bool:
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return False
        if x <= POWER_MISSING + 1:  # NASA POWER fill for missing
            return False
        return True
    except (TypeError, ValueError):
        return False


def _fmt_date(power_key: str) -> str:
    k = power_key.split("T", 1)[0]
    if len(k) == 8 and k.isdigit():
        return f"{k[0:4]}-{k[4:6]}-{k[6:8]}"
    return power_key


def _to_celsius(v: float | None) -> float | None:
    if v is None:
        return None
    # POWER often returns K for temperature; if value looks like Kelvin, convert.
    if v > 100:
        return round(v - 273.15, 2)
    return round(v, 2)
