"""Traditional almanac: lunar phase (Astral), moon sign (Skyfield), GDD phenology."""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, cast

from astral.moon import phase as astral_phase_day
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

from app.logic import traditional_rules as tr

logger = logging.getLogger(__name__)

_ts = load.timescale()
_eph: Any | None = None
_eph_load_failed = False


def _ephemeris() -> Any | None:
    """Load JPL ephemeris once; return None if download/load fails (offline, sandbox, etc.)."""
    global _eph, _eph_load_failed
    if _eph_load_failed:
        return None
    if _eph is None:
        try:
            _eph = load("de421.bsp")
        except Exception:
            logger.warning(
                "Skyfield de421.bsp unavailable; using Astral-only moon (phase + rough sign).",
                exc_info=True,
            )
            _eph_load_failed = True
            return None
    return _eph


SIGNS: list[str] = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _utc_now(utc_now: datetime | None) -> datetime:
    if utc_now is None:
        return datetime.now(timezone.utc)
    if utc_now.tzinfo is None:
        return utc_now.replace(tzinfo=timezone.utc)
    return utc_now.astimezone(timezone.utc)


def _astral_phase_bucket(p: float) -> tr.PhaseBucket:
    """Map Astral phase (0–28 lunar day) to four buckets."""
    if p < 7.0:
        return "new"
    if p < 14.0:
        return "waxing"
    if p < 21.0:
        return "full"
    return "waning"


def _phase_display_name(bucket: tr.PhaseBucket) -> str:
    return {
        "new": "New Moon",
        "waxing": "Waxing Moon",
        "full": "Full Moon",
        "waning": "Waning Moon",
    }[bucket]


def _moon_tropical_sign(longitude_deg: float) -> str:
    idx = int(longitude_deg % 360.0 // 30.0) % 12
    return SIGNS[idx]


def build_moon_state(utc_now: datetime | None = None) -> dict[str, Any]:
    """Astral lunar day + Skyfield illumination, cycle progress, tropical sign."""
    now = _utc_now(utc_now)
    t = _ts.from_datetime(now)
    ap = float(astral_phase_day(now.date()))
    phase_bucket = _astral_phase_bucket(ap)

    eph = _ephemeris()
    if eph is None:
        # No ephemeris: phase-based approximation for illumination, cycle bar, and rough sign.
        phase_deg = (ap / 28.0) * 360.0
        illumination = (1.0 - math.cos(math.radians(phase_deg))) / 2.0
        lunar_cycle_progress = (ap % 28.0) / 28.0
        lon_deg = phase_deg
        sign = _moon_tropical_sign(lon_deg)
    else:
        earth = eph["earth"]
        moon = eph["moon"]

        try:
            from skyfield import almanac

            phase_angle = almanac.moon_phase(eph, t)
            phase_deg = float(phase_angle.degrees)
            illumination = (1.0 - math.cos(math.radians(phase_deg))) / 2.0
            lunar_cycle_progress = (phase_deg % 360.0) / 360.0
        except Exception:
            phase_deg = (ap / 28.0) * 360.0
            illumination = (1.0 - math.cos(math.radians(phase_deg))) / 2.0
            lunar_cycle_progress = (ap % 28.0) / 28.0

        try:
            ast = earth.at(t).observe(moon).apparent()
            _, moon_lon, _ = ast.frame_latlon(ecliptic_frame)
            lon_deg = moon_lon.degrees % 360.0
            sign = _moon_tropical_sign(lon_deg)
        except Exception:
            sign = _moon_tropical_sign(phase_deg)
            lon_deg = phase_deg

    element = tr.zodiac_element(sign)

    return {
        "phase_name": _phase_display_name(phase_bucket),
        "phase_bucket": phase_bucket,
        "zodiac_sign": sign,
        "zodiac_element": element,
        "lunar_cycle_progress": round(min(1.0, max(0.0, lunar_cycle_progress)), 4),
        "illumination": round(min(1.0, max(0.0, illumination)), 4),
        "astral_lunar_day": round(ap, 2),
    }


def build_traditional_almanac_payload(
    *,
    lat: float,
    lng: float,
    utc_now: datetime | None,
    gdd_base10_ytd: float | None,
    soil_moisture_pct: float,
    precip_risk: str,
    relative_humidity_percent: float,
) -> dict[str, Any]:
    """Assemble almanac + wise council for JSON response."""
    _ = lat, lng  # reserved for future locale-specific rules
    moon = build_moon_state(utc_now)
    element = cast(tr.ZodiacElement, moon["zodiac_element"])
    phase_bucket = cast(tr.PhaseBucket, moon["phase_bucket"])

    category = tr.recommended_crop_category(phase_bucket, element)
    badge = tr.recommendation_badge_label(category)
    mouse, dandy = tr.phenology_flags(gdd_base10_ytd)
    favors = tr.traditional_favors_planting(phase_bucket, category)
    dry = tr.modern_dry_signal(
        soil_moisture_pct,
        precip_risk,  # type: ignore[arg-type]
        relative_humidity_percent,
    )
    council = tr.wise_council(favors, dry)

    return {
        "moon": {
            "phase_name": moon["phase_name"],
            "phase_bucket": phase_bucket,
            "zodiac_sign": moon["zodiac_sign"],
            "zodiac_element": element,
            "lunar_cycle_progress": moon["lunar_cycle_progress"],
            "illumination": moon["illumination"],
        },
        "recommended_crop_category": category,
        "recommendation_badge_label": badge,
        "phenology": {
            "mouse_ear_oak_likely": mouse,
            "dandelion_spring_likely": dandy,
            "gdd_base10_cumulative_ytd": gdd_base10_ytd,
        },
        "modern_traditional_alignment": council.modern_traditional_alignment,
        "wise_council_tip": council.wise_council_tip,
    }


def build_traditional_almanac_payload_safe(
    *,
    lat: float,
    lng: float,
    utc_now: datetime | None,
    gdd_base10_ytd: float | None,
    soil_moisture_pct: float,
    precip_risk: str,
    relative_humidity_percent: float,
) -> dict[str, Any]:
    """Build almanac; never raises — uses minimal Astral-only data if the full path fails."""
    try:
        return build_traditional_almanac_payload(
            lat=lat,
            lng=lng,
            utc_now=utc_now,
            gdd_base10_ytd=gdd_base10_ytd,
            soil_moisture_pct=soil_moisture_pct,
            precip_risk=precip_risk,
            relative_humidity_percent=relative_humidity_percent,
        )
    except Exception:
        logger.exception("Almanac build failed; using minimal fallback")
        now = _utc_now(utc_now)
        try:
            ap = float(astral_phase_day(now.date()))
        except Exception:
            ap = 14.0
        phase_bucket = _astral_phase_bucket(ap)
        phase_deg = (ap / 28.0) * 360.0
        illum = (1.0 - math.cos(math.radians(phase_deg))) / 2.0
        prog = (ap % 28.0) / 28.0
        sign = _moon_tropical_sign(phase_deg)
        element = cast(tr.ZodiacElement, tr.zodiac_element(sign))
        category = tr.recommended_crop_category(phase_bucket, element)
        badge = tr.recommendation_badge_label(category)
        mouse, dandy = tr.phenology_flags(gdd_base10_ytd)
        favors = tr.traditional_favors_planting(phase_bucket, category)
        dry = tr.modern_dry_signal(
            soil_moisture_pct,
            precip_risk,  # type: ignore[arg-type]
            relative_humidity_percent,
        )
        council = tr.wise_council(favors, dry)
        return {
            "moon": {
                "phase_name": _phase_display_name(phase_bucket),
                "phase_bucket": phase_bucket,
                "zodiac_sign": sign,
                "zodiac_element": element,
                "lunar_cycle_progress": round(min(1.0, max(0.0, prog)), 4),
                "illumination": round(min(1.0, max(0.0, illum)), 4),
            },
            "recommended_crop_category": category,
            "recommendation_badge_label": badge,
            "phenology": {
                "mouse_ear_oak_likely": mouse,
                "dandelion_spring_likely": dandy,
                "gdd_base10_cumulative_ytd": gdd_base10_ytd,
            },
            "modern_traditional_alignment": council.modern_traditional_alignment,
            "wise_council_tip": council.wise_council_tip,
        }
