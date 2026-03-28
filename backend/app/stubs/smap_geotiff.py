"""
Boilerplate for reading GeoTIFF rasters (optional dependency: rasterio).

Install: pip install rasterio

Not used by the API runtime; intended for LANCE GeoTIFF ingestion pipelines.
"""

from __future__ import annotations

from pathlib import Path


def read_geotiff_value_at_lonlat(geotiff_path: Path, lon: float, lat: float) -> float | None:
    """Sample a raster cell covering (lon, lat) using rasterio."""
    try:
        import rasterio  # type: ignore[import-not-found]
        from rasterio.transform import rowcol
    except ImportError:
        return None

    with rasterio.open(geotiff_path) as ds:
        rows, cols = rowcol(ds.transform, lon, lat)
        if rows < 0 or cols < 0 or rows >= ds.height or cols >= ds.width:
            return None
        window = rasterio.windows.Window(cols, rows, 1, 1)
        arr = ds.read(1, window=window)
        val = float(arr[0, 0])
        if val == ds.nodata:
            return None
        return val
