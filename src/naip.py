"""Optional cross-source pre-event imagery: USDA NAIP aerial photos (via Planetary Computer).

Real agencies often have only an older aerial basemap as the "before" image.
Matching a 2022 leaf-on aerial photo to a 2025 winter satellite image (different
sensor, sun angle, season, off-nadir) is the hard case for feature matching.

Usage:
    python -m src.naip --qk 031311103033 [--year 2022]
Writes data/tiles/<qk>/pre_naip.tif on the same grid as pre_visual.tif.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds

from .config import TILE_DIR

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")

PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PC_SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/naip"


def fetch_naip_for_tile(qk: str, year: int = 2022) -> str:
    tile_dir = TILE_DIR / qk
    ref_path = tile_dir / "pre_visual.tif"
    with rasterio.open(ref_path) as ref:
        crs, transform, h, w = ref.crs, ref.transform, ref.height, ref.width
        bbox = transform_bounds(crs, "EPSG:4326", *ref.bounds)

    items = requests.post(
        PC_STAC,
        json={"collections": ["naip"], "bbox": list(bbox), "datetime": f"{year}-01-01/{year}-12-31", "limit": 50},
        timeout=60,
    ).json()["features"]
    if not items:
        raise SystemExit(f"no NAIP {year} scenes over {qk}")
    token = requests.get(PC_SAS, timeout=60).json()["token"]
    print(f"{len(items)} NAIP {year} scenes over {qk}")

    mosaic = np.zeros((4, h, w), np.uint8)
    for it in items:
        href = it["assets"]["image"]["href"] + "?" + token
        with rasterio.open(f"/vsicurl/{href}") as src:
            with WarpedVRT(src, crs=crs, transform=transform, height=h, width=w, resampling=Resampling.average) as vrt:
                arr = vrt.read()
        arr = arr[:4] if arr.shape[0] >= 4 else np.concatenate([arr, np.zeros((4 - arr.shape[0], h, w), arr.dtype)])
        fill = (mosaic.max(axis=0) == 0) & (arr.max(axis=0) > 0)
        mosaic[:, fill] = arr[:, fill]
        print(f"  {it['id']} -> coverage {(mosaic.max(axis=0) > 0).mean():.0%}")

    out = tile_dir / "pre_naip.tif"
    with rasterio.open(
        out, "w", driver="GTiff", dtype="uint8", count=4, crs=crs, transform=transform, height=h, width=w,
        compress="deflate", tiled=True, blockxsize=512, blockysize=512,
    ) as dst:
        dst.write(mosaic)
        dst.set_band_description(1, "red"); dst.set_band_description(2, "green")
        dst.set_band_description(3, "blue"); dst.set_band_description(4, "nir")
    print(f"wrote {out}")
    return str(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--qk", required=True)
    ap.add_argument("--year", type=int, default=2022)
    a = ap.parse_args()
    fetch_naip_for_tile(a.qk, a.year)
