from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class Location(BaseModel):
    lat: float
    lng: float


class WeatherSeriesPoint(BaseModel):
    date: str
    temp_c: float | None = None
    precip_mm: float | None = None
    wind_kmh: float | None = None
    rh_percent: float | None = None


class WeatherData(BaseModel):
    wind_speed_kmh: float
    relative_humidity_percent: float
    next_6h_precip_mm: float
    precip_risk: Literal["low", "medium", "high"]
    series_7d: list[WeatherSeriesPoint]


class SoilMoistureSeriesPoint(BaseModel):
    date: str
    value_percent: float


class SoilMoistureData(BaseModel):
    value_percent: float
    source: Literal["mock"]
    series_7d: list[SoilMoistureSeriesPoint]


class SoilTempSeriesPoint(BaseModel):
    date: str
    value_c: float


class SoilTemperatureData(BaseModel):
    value_c: float
    series_7d: list[SoilTempSeriesPoint]


class SoilProperties(BaseModel):
    sand_percent: float | None = None
    silt_percent: float | None = None
    clay_percent: float | None = None
    bulk_density_kg_m3: float | None = None
    organic_carbon_g_kg: float | None = None


class SprayInfo(BaseModel):
    status: Literal["safe", "caution", "danger"]
    reasons: list[str]


class AgronomyData(BaseModel):
    ready_to_plant: bool
    ready_to_plant_reason: str
    spray: SprayInfo


class AnalyzeResponse(BaseModel):
    location: Location
    weather: WeatherData
    soil_moisture: SoilMoistureData
    soil_temperature: SoilTemperatureData
    soil_properties: SoilProperties
    agronomy: AgronomyData
