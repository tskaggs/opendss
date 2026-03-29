"""Traditional lunar planting heuristics and phenology flags (illustrative, not agronomic advice)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# --- Phenology (GDD base 10 °C, year-to-date cumulative daily mean T2M) ---
# Tunable illustrative bands; real phenology varies by species and region.
MOUSE_EAR_OAK_GDD10_MIN = 280.0
MOUSE_EAR_OAK_GDD10_MAX = 750.0
DANDELION_SPRING_GDD10_MIN = 40.0
DANDELION_SPRING_GDD10_MAX = 260.0

PhaseBucket = Literal["new", "waxing", "full", "waning"]
ZodiacElement = Literal["Fire", "Earth", "Air", "Water"]
CropCategory = Literal["Root", "Leaf", "Fruit", "Flower"]

SIGN_ELEMENTS: dict[str, ZodiacElement] = {
    "Aries": "Fire",
    "Taurus": "Earth",
    "Gemini": "Air",
    "Cancer": "Water",
    "Leo": "Fire",
    "Virgo": "Earth",
    "Libra": "Air",
    "Scorpio": "Water",
    "Sagittarius": "Fire",
    "Capricorn": "Earth",
    "Aquarius": "Air",
    "Pisces": "Water",
}


def zodiac_element(sign: str) -> ZodiacElement:
    return SIGN_ELEMENTS.get(sign, "Earth")


def recommended_crop_category(phase_bucket: PhaseBucket, element: ZodiacElement) -> CropCategory:
    """Map moon phase bucket + zodiac element to a folk crop-type hint."""
    if phase_bucket == "new":
        if element in ("Earth", "Water"):
            return "Root"
        if element == "Fire":
            return "Fruit"
        return "Flower"
    if phase_bucket == "waxing":
        if element in ("Earth", "Water"):
            return "Leaf"
        if element == "Fire":
            return "Fruit"
        return "Flower"
    if phase_bucket == "full":
        if element in ("Fire", "Air"):
            return "Fruit"
        if element == "Water":
            return "Leaf"
        return "Flower"
    # waning
    if element in ("Earth", "Water"):
        return "Root"
    if element == "Fire":
        return "Fruit"
    return "Flower"


def recommendation_badge_label(category: CropCategory) -> str:
    labels = {
        "Root": "Prime for root crops",
        "Leaf": "Prime for leafy greens",
        "Fruit": "Prime for fruiting crops",
        "Flower": "Prime for flowers & seed",
    }
    return labels[category]


def phenology_flags(gdd_base10_ytd: float | None) -> tuple[bool, bool]:
    """Oak 'mouse ear' and spring dandelion bloom windows from cumulative GDD₁₀."""
    if gdd_base10_ytd is None:
        return False, False
    mouse = MOUSE_EAR_OAK_GDD10_MIN <= gdd_base10_ytd <= MOUSE_EAR_OAK_GDD10_MAX
    dandy = DANDELION_SPRING_GDD10_MIN <= gdd_base10_ytd <= DANDELION_SPRING_GDD10_MAX
    return mouse, dandy


def traditional_favors_planting(phase_bucket: PhaseBucket, category: CropCategory) -> bool:
    """Heuristic: waxing/full moons favor sowing/transplant in folk practice."""
    if phase_bucket not in ("waxing", "full"):
        return False
    return category in ("Leaf", "Flower", "Fruit")


def modern_dry_signal(
    soil_moisture_pct: float,
    precip_risk: Literal["low", "medium", "high"],
    relative_humidity_percent: float,
) -> bool:
    """Satellite-era 'dry / risky to plant without water' composite."""
    if soil_moisture_pct < 32.0:
        return True
    if precip_risk == "low" and relative_humidity_percent < 42.0:
        return True
    return False


@dataclass(frozen=True)
class WiseCouncilResult:
    modern_traditional_alignment: Literal["aligned", "caution"]
    wise_council_tip: str | None


def wise_council(
    traditional_favors: bool,
    modern_dry: bool,
) -> WiseCouncilResult:
    if traditional_favors and modern_dry:
        return WiseCouncilResult(
            modern_traditional_alignment="caution",
            wise_council_tip=(
                "The Moon favors planting, but soil moisture looks low for your field—"
                "irrigate or wait for rain if you plant today."
            ),
        )
    return WiseCouncilResult(modern_traditional_alignment="aligned", wise_council_tip=None)
