from fastapi import APIRouter

from app.schemas.analyze import AnalyzeResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str | bool]:
    """Lightweight probe. If the JSON only has status=ok, traffic is not reaching this build (wrong port/process)."""
    return {
        "status": "ok",
        "opendss": "field-api",
        "health_schema": "almanac-v1",
        "analyze_includes_almanac": "almanac" in AnalyzeResponse.model_fields,
    }
