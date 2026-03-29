from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


PhaseBucket = Literal["new", "waxing", "full", "waning"]
ZodiacElement = Literal["Fire", "Earth", "Air", "Water"]
CropCategory = Literal["Root", "Leaf", "Fruit", "Flower"]


class MoonAlmanac(BaseModel):
    phase_name: str
    phase_bucket: PhaseBucket
    zodiac_sign: str
    zodiac_element: ZodiacElement
    lunar_cycle_progress: float = Field(..., ge=0.0, le=1.0)
    illumination: float = Field(..., ge=0.0, le=1.0)


class PhenologyAlmanac(BaseModel):
    mouse_ear_oak_likely: bool
    dandelion_spring_likely: bool
    gdd_base10_cumulative_ytd: float | None = None


class TraditionalAlmanac(BaseModel):
    moon: MoonAlmanac
    recommended_crop_category: CropCategory
    recommendation_badge_label: str
    phenology: PhenologyAlmanac
    modern_traditional_alignment: Literal["aligned", "caution"]
    wise_council_tip: str | None = None


class AnalyzeResponse(BaseModel):
    location: Location
    weather: WeatherData
    soil_moisture: SoilMoistureData
    soil_temperature: SoilTemperatureData
    soil_properties: SoilProperties
    agronomy: AgronomyData
    almanac: TraditionalAlmanac
