"""Step 3: per-pixel change score -> 50 m grid -> GeoJSON.

Unsupervised burn/damage scoring on the co-registered pair:
  * dNDVI  (post - pre) from the multispectral tiles: vegetation loss / char
  * 1-SSIM on grayscale visual tiles: structural change (destroyed roofs, debris)
Both terms are scaled to [0, 1] and averaged; cells are classified by fixed thresholds.

Usage:
    python -m src.damage                  # all registered pairs
    python -m src.damage --qk 031311103033 --cell-m 50
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import xy
from shapely.geometry import box
from skimage.metrics import structural_similarity

from .config import RESULTS_DIR, TILE_DIR

# Band positions (0-based) of red / NIR for the Maxar sensors in this event.
BANDS = {8: {"red": 4, "nir": 6}, 4: {"red": 2, "nir": 3}}

W_NDVI, W_SSIM = 0.5, 0.5
NDVI_DROP_SAT = 0.5           # a dNDVI of -0.5 saturates the vegetation term
SSIM_SPAN = 0.6               # (1-SSIM) this far above the tile floor saturates the structure term
SEVERE_T, MODERATE_T = 0.30, 0.15
MIN_VALID_FRAC = 0.8


def ndvi(ms: np.ndarray) -> np.ndarray:
    b = BANDS[ms.shape[0]]
    red = ms[b["red"]].astype(np.float32)
    nir = ms[b["nir"]].astype(np.float32)
    out = (nir - red) / np.maximum(nir + red, 1.0)
    out[(nir + red) == 0] = np.nan
    return out


def gray(rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.ascontiguousarray(rgb.transpose(1, 2, 0)), cv2.COLOR_RGB2GRAY)


def _read(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as src:
        return src.read(), src.profile.copy()


def pixel_scores(tile_dir: Path, ssim_win: int = 11) -> dict:
    pre_vis, prof = _read(tile_dir / "pre_visual.tif")
    post_vis, _ = _read(tile_dir / "post_visual_reg.tif")
    post_raw, _ = _read(tile_dir / "post_visual.tif")
    pre_ms, _ = _read(tile_dir / "pre_ms.tif")
    post_ms, _ = _read(tile_dir / "post_ms_reg.tif")

    valid = (pre_vis.max(axis=0) > 0) & (post_vis.max(axis=0) > 0) & (pre_ms.max(axis=0) > 0) & (post_ms.max(axis=0) > 0)

    d_ndvi = ndvi(post_ms) - ndvi(pre_ms)
    veg_term = np.clip(-d_ndvi / NDVI_DROP_SAT, 0, 1)

    g_pre, g_post, g_raw = gray(pre_vis), gray(post_vis), gray(post_raw)
    _, ssim_map = structural_similarity(g_pre, g_post, win_size=ssim_win, full=True, data_range=255)
    _, ssim_raw = structural_similarity(g_pre, g_raw, win_size=ssim_win, full=True, data_range=255)
    # Sun angle, shadows and seasonal colour shifts give every pixel some SSIM loss.
    # Treat the 20th percentile of (1-SSIM) over the tile as the "no change" floor.
    change = 1 - ssim_map
    floor = float(min(np.percentile(change[valid], 20), 0.3)) if valid.any() else 0.0
    struct_term = np.clip((change - floor) / SSIM_SPAN, 0, 1)

    score = W_NDVI * veg_term + W_SSIM * struct_term
    score = cv2.GaussianBlur(score.astype(np.float32), (0, 0), 1.5)
    score[~valid] = np.nan
    d_ndvi[~valid] = np.nan

    return {
        "score": score.astype(np.float32),
        "d_ndvi": d_ndvi.astype(np.float32),
        "ssim": ssim_map.astype(np.float32),
        "valid": valid,
        "profile": prof,
        # How much apparent "change" registration removed (mean 1-SSIM, raw vs registered).
        "mean_change_raw": float(np.nanmean(1 - ssim_raw[valid])),
        "mean_change_registered": float(np.nanmean(1 - ssim_map[valid])),
    }


def grid_aggregate(px: dict, cell_m: float = 50.0) -> gpd.GeoDataFrame:
    prof = px["profile"]
    tr = prof["transform"]
    gsd = abs(tr.a)
    cell_px = max(4, int(round(cell_m / gsd)))
    h, w = px["score"].shape
    ny, nx = h // cell_px, w // cell_px

    def _block(a: np.ndarray, fn):
        a = a[: ny * cell_px, : nx * cell_px].reshape(ny, cell_px, nx, cell_px).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
        return fn(a, axis=2)

    valid_frac = _block(px["valid"].astype(np.float32), np.mean)
    score = _block(px["score"], np.nanmean)
    d_ndvi = _block(px["d_ndvi"], np.nanmean)
    ssim = _block(px["ssim"], np.nanmean)
    frac_severe_px = _block((np.nan_to_num(px["score"], nan=0) >= SEVERE_T).astype(np.float32), np.mean)

    rows = []
    for iy in range(ny):
        for ix in range(nx):
            if valid_frac[iy, ix] < MIN_VALID_FRAC:
                continue
            x0, y0 = xy(tr, iy * cell_px, ix * cell_px, offset="ul")
            x1, y1 = xy(tr, (iy + 1) * cell_px, (ix + 1) * cell_px, offset="ul")
            s = float(score[iy, ix])
            cls = "severe" if s >= SEVERE_T else "moderate" if s >= MODERATE_T else "none"
            rows.append(
                {
                    "row": iy, "col": ix,
                    "score": round(s, 3),
                    "d_ndvi": round(float(d_ndvi[iy, ix]), 3),
                    "ssim": round(float(ssim[iy, ix]), 3),
                    "frac_severe_px": round(float(frac_severe_px[iy, ix]), 3),
                    "damage_class": cls,
                    "geometry": box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)),
                }
            )
    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs=prof["crs"])
    gdf.attrs["cell_px"] = cell_px
    gdf.attrs["cell_m"] = cell_px * gsd
    return gdf


def save_outputs(tile_dir: Path, px: dict, gdf: gpd.GeoDataFrame) -> dict:
    qk = tile_dir.name
    prof = px["profile"]
    meta = json.loads((tile_dir / "pair.json").read_text())

    # Score raster (GeoTIFF, float32) for GIS users.
    p = {**prof, "count": 1, "dtype": "float32", "nodata": -9999.0, "compress": "deflate"}
    for k in ("blockxsize", "blockysize", "tiled"):
        p.pop(k, None)
    with rasterio.open(tile_dir / "damage_score.tif", "w", **p) as dst:
        dst.write(np.nan_to_num(px["score"], nan=-9999.0)[None])

    # PNG heatmap (RGBA) for the web map overlay.
    s = np.nan_to_num(px["score"], nan=0.0)
    s8 = (np.clip(s / 0.5, 0, 1) * 255).astype(np.uint8)
    heat = cv2.applyColorMap(s8, cv2.COLORMAP_INFERNO)[..., ::-1]
    alpha = (np.clip((s - 0.08) / 0.4, 0, 1) * 230).astype(np.uint8)
    alpha[~px["valid"]] = 0
    rgba = np.dstack([heat, alpha])
    cv2.imwrite(str(RESULTS_DIR / f"{qk}_damage_heat.png"), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))

    # Grid GeoJSON in WGS84.
    gdf_wgs = gdf.to_crs("EPSG:4326")
    gdf_wgs.to_file(RESULTS_DIR / f"{qk}_damage_grid.geojson", driver="GeoJSON")

    with rasterio.open(tile_dir / "pre_visual.tif") as src:
        from rasterio.warp import transform_bounds

        bounds_wgs = transform_bounds(src.crs, "EPSG:4326", *src.bounds)

    cell_area_ha = (gdf.attrs["cell_m"] ** 2) / 1e4
    summary = {
        "quadkey": qk,
        "fire": meta.get("fire"),
        "pre_date": meta.get("pre_date"),
        "post_date": meta.get("post_date"),
        "cell_m": round(gdf.attrs["cell_m"], 1),
        "n_cells": int(len(gdf)),
        "n_severe": int((gdf.damage_class == "severe").sum()),
        "n_moderate": int((gdf.damage_class == "moderate").sum()),
        "severe_area_ha": round(float((gdf.damage_class == "severe").sum() * cell_area_ha), 1),
        "moderate_area_ha": round(float((gdf.damage_class == "moderate").sum() * cell_area_ha), 1),
        "mean_d_ndvi": round(float(np.nanmean(px["d_ndvi"])), 3),
        "mean_change_raw": round(px["mean_change_raw"], 4),
        "mean_change_registered": round(px["mean_change_registered"], 4),
        "bounds_wgs84": [round(b, 6) for b in bounds_wgs],
    }
    (RESULTS_DIR / f"{qk}_damage_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def run(tile_dir: Path, cell_m: float) -> dict:
    px = pixel_scores(tile_dir)
    gdf = grid_aggregate(px, cell_m)
    summ = save_outputs(tile_dir, px, gdf)
    print(f"[{tile_dir.name}] cells={summ['n_cells']} severe={summ['n_severe']} ({summ['severe_area_ha']} ha) "
          f"moderate={summ['n_moderate']} mean_dNDVI={summ['mean_d_ndvi']} "
          f"change raw->reg: {summ['mean_change_raw']:.3f}->{summ['mean_change_registered']:.3f}")
    return summ


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qk", nargs="*")
    ap.add_argument("--cell-m", type=float, default=50.0)
    a = ap.parse_args()
    dirs = [TILE_DIR / q for q in a.qk] if a.qk else sorted(d for d in TILE_DIR.iterdir() if (d / "post_visual_reg.tif").exists())
    rows = [run(d, a.cell_m) for d in dirs]
    df = pd.DataFrame(rows)
    out = RESULTS_DIR / "damage_summary.csv"
    if out.exists() and a.qk:
        old = pd.read_csv(out, dtype={"quadkey": str})
        df = pd.concat([old[~old.quadkey.isin(df.quadkey)], df], ignore_index=True)
    df.to_csv(out, index=False)


if __name__ == "__main__":
    main()
