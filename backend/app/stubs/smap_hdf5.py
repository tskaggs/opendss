"""
Boilerplate for reading NASA SMAP LANCE HDF5 products (optional dependency: h5py).

Install: pip install h5py

This module is not imported by the running API; copy patterns into a LANCE
download worker when Earthdata credentials are available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_smap_hdf5_scalar_example(hdf5_path: Path, lat: float, lng: float) -> float | None:
    """Example: open HDF5 and read a soil moisture value at a lon/lat (conceptual).

    Real SMAP files expose swath grids; you would:
    - open the file with h5py
    - navigate to the soil moisture dataset
    - find nearest row/col or reproject to the grid
    """
    try:
        import h5py  # type: ignore[import-not-found]
    except ImportError:
        return None

    with h5py.File(hdf5_path, "r") as f:  # noqa: SIM117
        _ = f.visititems(lambda name, obj: None)  # explore structure
    del lat, lng
    return None


def list_top_level_datasets(hdf5_path: Path) -> list[str]:
    try:
        import h5py  # type: ignore[import-not-found]
    except ImportError:
        return []

    out: list[str] = []
    with h5py.File(hdf5_path, "r") as f:

        def visitor(name: str, obj: Any) -> None:
            if isinstance(obj, h5py.Dataset):
                out.append(name)

        f.visititems(visitor)
    return out
