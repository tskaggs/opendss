from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.limiter import limiter
from app.schemas.analyze import (
    AgronomyData,
    AnalyzeRequest,
    AnalyzeResponse,
    Location,
    SoilMoistureData,
    SoilMoistureSeriesPoint,
    SoilProperties,
    SoilTemperatureData,
    SoilTempSeriesPoint,
    SprayInfo,
    TraditionalAlmanac,
    WeatherData,
    WeatherSeriesPoint,
)
from app.services.almanac import build_traditional_almanac_payload_safe
from app.services.fallback_weather import synthetic_gdd_ytd, synthetic_power_bundle
from app.services.nasa_power import PowerBundle, fetch_power_bundle, fetch_ytd_gdd_base10
from app.services.plant_readiness import assess_ready_to_plant
from app.services.smap import mock_smap
from app.services.soilgrids import fetch_soil_properties
from app.services.spray_window import classify_spray

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analyze"])

_rate_limit = get_settings().rate_limit_analyze
_EMPTY_SOIL = {
    "clay_percent": None,
    "sand_percent": None,
    "silt_percent": None,
    "bulk_density_kg_m3": None,
    "organic_carbon_g_kg": None,
}


def _http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise RuntimeError("HTTP client not initialized; app lifespan must run before requests")
    return client


async def _fetch_power_bundle_safe(
    client: httpx.AsyncClient, lat: float, lng: float
) -> PowerBundle:
    try:
        return await fetch_power_bundle(lat, lng, client)
    except httpx.HTTPStatusError as e:
        logger.warning(
            "NASA POWER HTTP %s; using synthetic weather",
            e.response.status_code,
        )
        return synthetic_power_bundle(lat, lng)
    except Exception:
        logger.warning("NASA POWER fetch failed; using synthetic weather", exc_info=True)
        return synthetic_power_bundle(lat, lng)


async def _fetch_gdd_ytd_safe(
    client: httpx.AsyncClient, lat: float, lng: float
) -> float | None:
    try:
        return await fetch_ytd_gdd_base10(lat, lng, client)
    except Exception:
        logger.warning("NASA POWER YTD GDD fetch failed; using synthetic GDD estimate", exc_info=True)
        return None


async def _fetch_soil_safe(client: httpx.AsyncClient, lat: float, lng: float) -> dict:
    try:
        return await fetch_soil_properties(lat, lng, client)
    except httpx.HTTPStatusError as e:
        logger.warning(
            "SoilGrids HTTP %s; soil properties will be null",
            e.response.status_code,
        )
        return dict(_EMPTY_SOIL)
    except Exception:
        logger.warning("SoilGrids fetch failed; soil properties will be null", exc_info=True)
        return dict(_EMPTY_SOIL)


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit(_rate_limit)
async def analyze(request: Request, body: AnalyzeRequest) -> AnalyzeResponse:
    lat, lng = body.lat, body.lng
    client = _http_client(request)

    power = await _fetch_power_bundle_safe(client, lat, lng)
    gdd_ytd = await _fetch_gdd_ytd_safe(client, lat, lng)
    soil_raw = await _fetch_soil_safe(client, lat, lng)

    gdd_for_almanac = gdd_ytd if gdd_ytd is not None else synthetic_gdd_ytd(lat, lng)

    smap = mock_smap(lat, lng)
    spray_status, spray_reasons = classify_spray(
        power.wind_speed_kmh,
        power.next_6h_precip_mm,
        power.relative_humidity_percent,
    )
    ready, reason = assess_ready_to_plant(power.soil_temp_c, smap.value_percent)

    weather = WeatherData(
        wind_speed_kmh=power.wind_speed_kmh,
        relative_humidity_percent=power.relative_humidity_percent,
        next_6h_precip_mm=power.next_6h_precip_mm,
        precip_risk=power.precip_risk,
        series_7d=[WeatherSeriesPoint.model_validate(p) for p in power.weather_series_7d],
    )

    soil_moisture = SoilMoistureData(
        value_percent=smap.value_percent,
        source="mock",
        series_7d=[SoilMoistureSeriesPoint.model_validate(p) for p in smap.series_7d],
    )

    soil_temperature = SoilTemperatureData(
        value_c=power.soil_temp_c,
        series_7d=[SoilTempSeriesPoint.model_validate(p) for p in power.soil_temp_series_7d],
    )

    soil_properties = SoilProperties(
        sand_percent=soil_raw.get("sand_percent"),
        silt_percent=soil_raw.get("silt_percent"),
        clay_percent=soil_raw.get("clay_percent"),
        bulk_density_kg_m3=soil_raw.get("bulk_density_kg_m3"),
        organic_carbon_g_kg=soil_raw.get("organic_carbon_g_kg"),
    )

    agronomy = AgronomyData(
        ready_to_plant=ready,
        ready_to_plant_reason=reason,
        spray=SprayInfo(status=spray_status, reasons=spray_reasons),
    )

    almanac = TraditionalAlmanac.model_validate(
        build_traditional_almanac_payload_safe(
            lat=lat,
            lng=lng,
            utc_now=None,
            gdd_base10_ytd=gdd_for_almanac,
            soil_moisture_pct=smap.value_percent,
            precip_risk=weather.precip_risk,
            relative_humidity_percent=weather.relative_humidity_percent,
        )
    )

    return AnalyzeResponse(
        location=Location(lat=lat, lng=lng),
        weather=weather,
        soil_moisture=soil_moisture,
        soil_temperature=soil_temperature,
        soil_properties=soil_properties,
        agronomy=agronomy,
        almanac=almanac,
    )
