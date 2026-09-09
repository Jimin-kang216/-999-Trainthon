"""Step 1: index the Maxar Open Data STAC catalog, pair pre/post tiles, download.

Usage:
    python -m src.ingest index            # build data/index.csv
    python -m src.ingest pairs            # build data/pairs.csv
    python -m src.ingest download --n 3   # download top-N pairs to data/tiles/
    python -m src.ingest all --n 3
"""

from __future__ import annotations

import argparse
import json
import math
import os
import posixpath
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from .config import (
    EVENT_DATE,
    EVENT_URL,
    FIRE_CENTROIDS,
    INDEX_CSV,
    PAIRS_CSV,
    TILE_DIR,
    TILE_SIZE,
)

# GDAL settings that make remote COG reads fast (no directory listing, only .tif).
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("GDAL_HTTP_MULTIRANGE", "YES")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")

_session = requests.Session()


def _get_json(url: str) -> dict:
    r = _session.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def _resolve(base_url: str, href: str) -> str:
    """Resolve a relative STAC href against the URL of the document it came from."""
    if href.startswith("http"):
        return href
    base_dir = base_url.rsplit("/", 1)[0]
    joined = posixpath.normpath(posixpath.join(base_dir, href))
    # normpath collapses the double slash after the scheme; restore it.
    return joined.replace("https:/", "https://", 1).replace("http:/", "http://", 1)


# --------------------------------------------------------------------------- #
# 1. Index
# --------------------------------------------------------------------------- #
def _item_record(item_url: str) -> dict | None:
    try:
        it = _get_json(item_url)
    except Exception as e:  # noqa: BLE001
        print(f"  ! failed {item_url}: {e}", file=sys.stderr)
        return None
    p = it.get("properties", {})
    assets = it.get("assets", {})
    bbox = it.get("bbox", [None] * 4)
    return {
        "item_url": item_url,
        "acquisition": p.get("catalog_id") or item_url.rsplit("/", 1)[-1].replace(".json", ""),
        "datetime": p.get("datetime"),
        "quadkey": p.get("quadkey"),
        "gsd": p.get("gsd"),
        "off_nadir": p.get("view:off_nadir"),
        "sun_elevation": p.get("view:sun_elevation"),
        "clouds_pct": p.get("tile:clouds_percent"),
        "epsg": p.get("proj:epsg"),
        "platform": p.get("platform"),
        "bbox_w": bbox[0],
        "bbox_s": bbox[1],
        "bbox_e": bbox[2],
        "bbox_n": bbox[3],
        "visual_href": _resolve(item_url, assets["visual"]["href"]) if "visual" in assets else None,
        "ms_href": _resolve(item_url, assets["ms_analytic"]["href"]) if "ms_analytic" in assets else None,
        "pan_href": _resolve(item_url, assets["pan_analytic"]["href"]) if "pan_analytic" in assets else None,
    }


def build_index(workers: int = 16) -> pd.DataFrame:
    col_url = f"{EVENT_URL}/collection.json"
    col = _get_json(col_url)
    acq_urls = [_resolve(col_url, l["href"]) for l in col["links"] if l["rel"] == "child"]
    print(f"{len(acq_urls)} acquisitions in {col.get('title')}")

    item_urls: list[str] = []
    for a in tqdm(acq_urls, desc="acquisitions"):
        d = _get_json(a)
        item_urls += [_resolve(a, l["href"]) for l in d["links"] if l["rel"] == "item"]
    print(f"{len(item_urls)} tiles (STAC items)")

    rows = []
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(_item_record, u) for u in item_urls]
        for f in tqdm(as_completed(futs), total=len(futs), desc="items"):
            rec = f.result()
            if rec:
                rows.append(rec)

    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
    df["phase"] = np.where(df["date"] < EVENT_DATE, "pre", "post")
    df = df.sort_values(["quadkey", "datetime"]).reset_index(drop=True)
    df.to_csv(INDEX_CSV, index=False)
    print(f"wrote {INDEX_CSV} ({len(df)} rows; pre={int((df.phase=='pre').sum())}, post={int((df.phase=='post').sum())})")
    return df


# --------------------------------------------------------------------------- #
# 2. Pairs
# --------------------------------------------------------------------------- #
def _dist_km(lon1, lat1, lon2, lat2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


_mask_cache: dict[str, np.ndarray] = {}


def probe_valid_mask(href: str, size: int = 128) -> np.ndarray:
    """Cheap low-resolution read of a remote COG to get its valid-data footprint.

    ARD tiles at the edge of an image strip are only partially filled, so the
    STAC metadata alone is not enough to choose a usable pre/post pair.
    """
    if href in _mask_cache:
        return _mask_cache[href]
    import rasterio
    from rasterio.enums import Resampling

    with rasterio.open(f"/vsicurl/{href}") as src:
        arr = src.read(out_shape=(src.count, size, size), resampling=Resampling.nearest)
    mask = arr.max(axis=0) > 0
    _mask_cache[href] = mask
    return mask


def make_pairs(
    df: pd.DataFrame | None = None,
    max_clouds: float = 5.0,
    probe_within_km: float = 10.0,
    min_overlap: float = 0.80,
) -> pd.DataFrame:
    if df is None:
        df = pd.read_csv(INDEX_CSV, dtype={"quadkey": str})
    df = df[df["visual_href"].notna()].copy()
    df["clouds_pct"] = df["clouds_pct"].fillna(0)
    df = df[df["clouds_pct"] <= max_clouds]

    pairs = []
    for qk, g in tqdm(list(df.groupby("quadkey")), desc="pairing"):
        pre = g[g.phase == "pre"]
        post = g[g.phase == "post"]
        if pre.empty or post.empty:
            continue

        cx = (pre.iloc[0].bbox_w + pre.iloc[0].bbox_e) / 2
        cy = (pre.iloc[0].bbox_s + pre.iloc[0].bbox_n) / 2
        dists = {name: _dist_km(cx, cy, *c) for name, c in FIRE_CENTROIDS.items()}
        fire = min(dists, key=dists.get)

        overlap = None
        if dists[fire] <= probe_within_km:
            # Probe every candidate's footprint and pick the pair with the most
            # shared valid pixels; tie-break on earliest post-event date.
            best = None
            for _, pr in pre.iterrows():
                m_pre = probe_valid_mask(pr.visual_href)
                if m_pre.mean() < 0.5:
                    continue
                for _, po in post.iterrows():
                    m_post = probe_valid_mask(po.visual_href)
                    ov = float((m_pre & m_post).mean())
                    key = (round(ov, 2), -pd.Timestamp(po.datetime).value)
                    if best is None or key > best[0]:
                        best = (key, pr, po, ov)
            if best is None or best[3] < min_overlap:
                continue
            _, pre_row, post_row, overlap = best
        else:
            pre_row = pre.sort_values(["clouds_pct", "datetime"], ascending=[True, False]).iloc[0]
            post_row = post.sort_values(["clouds_pct", "datetime"], ascending=[True, True]).iloc[0]

        pairs.append(
            {
                "quadkey": qk,
                "fire": fire,
                "dist_to_fire_km": round(dists[fire], 2),
                "valid_overlap": None if overlap is None else round(overlap, 3),
                "center_lon": round(cx, 5),
                "center_lat": round(cy, 5),
                "pre_date": pre_row.date,
                "post_date": post_row.date,
                "pre_acq": pre_row.acquisition,
                "post_acq": post_row.acquisition,
                "pre_off_nadir": pre_row.off_nadir,
                "post_off_nadir": post_row.off_nadir,
                "off_nadir_diff": abs((pre_row.off_nadir or 0) - (post_row.off_nadir or 0)),
                "pre_gsd": pre_row.gsd,
                "post_gsd": post_row.gsd,
                "epsg": pre_row.epsg,
                "pre_visual": pre_row.visual_href,
                "post_visual": post_row.visual_href,
                "pre_ms": pre_row.ms_href,
                "post_ms": post_row.ms_href,
                "n_pre_candidates": len(pre),
                "n_post_candidates": len(post),
            }
        )

    out = pd.DataFrame(pairs).sort_values("dist_to_fire_km").reset_index(drop=True)
    out.to_csv(PAIRS_CSV, index=False)
    print(f"wrote {PAIRS_CSV} ({len(out)} pre/post pairs)")
    cols = ["quadkey", "fire", "dist_to_fire_km", "valid_overlap", "pre_date", "post_date", "off_nadir_diff"]
    print(out[cols].head(12).to_string())
    return out


# --------------------------------------------------------------------------- #
# 3. Download (downsampled reads straight from the remote COG)
# --------------------------------------------------------------------------- #
def _read_downsampled(href: str, size: int):
    """Read a whole COG resampled to size x size; returns (array[bands,h,w], profile)."""
    import rasterio
    from rasterio.enums import Resampling

    with rasterio.open(f"/vsicurl/{href}") as src:
        arr = src.read(out_shape=(src.count, size, size), resampling=Resampling.average)
        transform = src.transform * src.transform.scale(src.width / size, src.height / size)
        profile = {
            "driver": "GTiff",
            "dtype": src.dtypes[0],
            "count": src.count,
            "crs": src.crs,
            "nodata": src.nodata,
            "height": size,
            "width": size,
            "transform": transform,
            "compress": "deflate",
            "tiled": True,
            "blockxsize": 512,
            "blockysize": 512,
        }
        meta = {
            "src_width": src.width,
            "src_height": src.height,
            "src_res": src.res,
            "count": src.count,
            "dtype": str(src.dtypes[0]),
            "nodata": src.nodata,
        }
    return arr, profile, meta


def _valid_fraction(arr: np.ndarray) -> float:
    return float((arr.max(axis=0) > 0).mean())


def download_pair(row: pd.Series, size: int = TILE_SIZE, min_valid: float = 0.85) -> dict | None:
    import rasterio

    out_dir = TILE_DIR / str(row.quadkey)
    out_dir.mkdir(parents=True, exist_ok=True)
    info = {"quadkey": row.quadkey}
    for phase in ("pre", "post"):
        for asset in ("visual", "ms"):
            href = row[f"{phase}_{asset}"]
            if not isinstance(href, str):
                continue
            dst = out_dir / f"{phase}_{asset}.tif"
            if dst.exists():
                with rasterio.open(dst) as d:
                    info[f"{phase}_{asset}_valid"] = _valid_fraction(d.read())
                continue
            arr, profile, meta = _read_downsampled(href, size)
            vf = _valid_fraction(arr)
            info[f"{phase}_{asset}_valid"] = vf
            info[f"{phase}_{asset}_bands"] = meta["count"]
            info[f"{phase}_{asset}_src_px"] = meta["src_width"]
            if asset == "visual" and vf < min_valid:
                print(f"  skip {row.quadkey} {phase}: only {vf:.0%} valid pixels")
                return None
            with rasterio.open(dst, "w", **profile) as d:
                d.write(arr)
    with open(out_dir / "pair.json", "w") as f:
        json.dump({**row.to_dict(), **info}, f, indent=2, default=str)
    return info


def download_pairs(n: int = 3, size: int = TILE_SIZE, pairs: pd.DataFrame | None = None) -> list[dict]:
    if pairs is None:
        pairs = pd.read_csv(PAIRS_CSV, dtype={"quadkey": str})
    done = []
    for _, row in pairs.iterrows():
        if len(done) >= n:
            break
        print(f"downloading {row.quadkey} ({row.fire}, {row.dist_to_fire_km} km) pre={row.pre_date} post={row.post_date}")
        info = download_pair(row, size=size)
        if info:
            done.append(info)
            print(f"  ok: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})}")
    print(f"{len(done)} pairs ready in {TILE_DIR}")
    return done


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["index", "pairs", "download", "all"])
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--size", type=int, default=TILE_SIZE)
    a = ap.parse_args()
    if a.cmd in ("index", "all"):
        build_index()
    if a.cmd in ("pairs", "all"):
        make_pairs()
    if a.cmd in ("download", "all"):
        download_pairs(n=a.n, size=a.size)


if __name__ == "__main__":
    main()
