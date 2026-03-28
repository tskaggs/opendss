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
    WeatherData,
    WeatherSeriesPoint,
)
from app.services.fallback_weather import synthetic_power_bundle
from app.services.nasa_power import fetch_power_bundle
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


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit(_rate_limit)
async def analyze(request: Request, body: AnalyzeRequest) -> AnalyzeResponse:
    lat, lng = body.lat, body.lng

    async with httpx.AsyncClient() as client:
        try:
            power = await fetch_power_bundle(lat, lng, client)
        except httpx.HTTPStatusError as e:
            logger.warning(
                "NASA POWER HTTP %s; using synthetic weather",
                e.response.status_code,
            )
            power = synthetic_power_bundle(lat, lng)
        except Exception:
            logger.warning("NASA POWER fetch failed; using synthetic weather", exc_info=True)
            power = synthetic_power_bundle(lat, lng)

        try:
            soil_raw = await fetch_soil_properties(lat, lng, client)
        except httpx.HTTPStatusError as e:
            logger.warning(
                "SoilGrids HTTP %s; soil properties will be null",
                e.response.status_code,
            )
            soil_raw = dict(_EMPTY_SOIL)
        except Exception:
            logger.warning("SoilGrids fetch failed; soil properties will be null", exc_info=True)
            soil_raw = dict(_EMPTY_SOIL)

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

    return AnalyzeResponse(
        location=Location(lat=lat, lng=lng),
        weather=weather,
        soil_moisture=soil_moisture,
        soil_temperature=soil_temperature,
        soil_properties=soil_properties,
        agronomy=agronomy,
    )
