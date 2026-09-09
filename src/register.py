"""Step 2: co-register post-event tiles onto pre-event tiles.

Two matchers are run on every pair so that the learned matcher (DISK + LightGlue)
can be compared against the classical baseline (SIFT + ratio test) under the same
robust estimator (MAGSAC++ homography).

Usage:
    python -m src.register                 # all downloaded pairs
    python -m src.register --qk 031311103033
    python -m src.register --match-size 1024 --warp-with lightglue
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import rasterio
import torch

from .config import RESULTS_DIR, TILE_DIR

torch.set_grad_enabled(False)
torch.set_num_threads(max(1, torch.get_num_threads()))

RANSAC_THRESH_PX = 2.5
MIN_INLIERS = 15


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #
def read_rgb(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as src:
        arr = src.read()
        prof = src.profile.copy()
    return np.ascontiguousarray(arr.transpose(1, 2, 0)), prof


def to_gray(rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


def _resize_for_matching(img: np.ndarray, size: int) -> tuple[np.ndarray, float]:
    h, w = img.shape[:2]
    if max(h, w) == size:
        return img, 1.0
    scale = size / max(h, w)
    out = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return out, scale


# --------------------------------------------------------------------------- #
# Matchers: each returns (pts_pre[N,2], pts_post[N,2]) in full-res pixel coords
# --------------------------------------------------------------------------- #
def match_sift(pre: np.ndarray, post: np.ndarray, match_size: int, nfeatures: int = 8000, ratio: float = 0.8):
    g1, s1 = _resize_for_matching(to_gray(pre), match_size)
    g2, s2 = _resize_for_matching(to_gray(post), match_size)
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    k1, d1 = sift.detectAndCompute(g1, None)
    k2, d2 = sift.detectAndCompute(g2, None)
    if d1 is None or d2 is None or len(k1) < 2 or len(k2) < 2:
        return np.zeros((0, 2)), np.zeros((0, 2)), {"kpts_pre": len(k1 or []), "kpts_post": len(k2 or [])}
    flann = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 5}, {"checks": 64})
    knn = flann.knnMatch(d1, d2, k=2)
    good = [m for m, n in (p for p in knn if len(p) == 2) if m.distance < ratio * n.distance]
    p1 = np.float32([k1[m.queryIdx].pt for m in good]) / s1
    p2 = np.float32([k2[m.trainIdx].pt for m in good]) / s2
    return p1, p2, {"kpts_pre": len(k1), "kpts_post": len(k2)}


_lg_cache: dict = {}


def _lightglue_models():
    if not _lg_cache:
        import kornia.feature as KF

        _lg_cache["disk"] = KF.DISK.from_pretrained("depth").eval()
        _lg_cache["lg"] = KF.LightGlueMatcher("disk").eval()
    return _lg_cache["disk"], _lg_cache["lg"]


def match_lightglue(pre: np.ndarray, post: np.ndarray, match_size: int, n_kpts: int = 4096):
    import kornia.feature as KF

    disk, lg = _lightglue_models()
    r1, s1 = _resize_for_matching(pre, match_size)
    r2, s2 = _resize_for_matching(post, match_size)

    def _tensor(x: np.ndarray) -> torch.Tensor:
        return torch.from_numpy(x).permute(2, 0, 1).float()[None] / 255.0

    t1, t2 = _tensor(r1), _tensor(r2)
    f1 = disk(t1, n=n_kpts, window_size=5, score_threshold=0.0, pad_if_not_divisible=True)[0]
    f2 = disk(t2, n=n_kpts, window_size=5, score_threshold=0.0, pad_if_not_divisible=True)[0]
    if len(f1.keypoints) < 2 or len(f2.keypoints) < 2:
        return np.zeros((0, 2)), np.zeros((0, 2)), {"kpts_pre": len(f1.keypoints), "kpts_post": len(f2.keypoints)}

    lafs1 = KF.laf_from_center_scale_ori(f1.keypoints[None])
    lafs2 = KF.laf_from_center_scale_ori(f2.keypoints[None])
    _, idxs = lg(f1.descriptors, f2.descriptors, lafs1, lafs2, hw1=t1.shape[-2:], hw2=t2.shape[-2:])
    idxs = idxs.cpu().numpy()
    p1 = f1.keypoints.cpu().numpy()[idxs[:, 0]] / s1
    p2 = f2.keypoints.cpu().numpy()[idxs[:, 1]] / s2
    return p1, p2, {"kpts_pre": len(f1.keypoints), "kpts_post": len(f2.keypoints)}


MATCHERS = {"sift": match_sift, "lightglue": match_lightglue}


# --------------------------------------------------------------------------- #
# Robust homography + metrics
# --------------------------------------------------------------------------- #
def estimate_homography(p_pre: np.ndarray, p_post: np.ndarray, thresh: float = RANSAC_THRESH_PX):
    """H maps post-event pixel coords -> pre-event pixel coords."""
    if len(p_pre) < 4:
        return None, np.zeros(len(p_pre), bool)
    H, mask = cv2.findHomography(p_post, p_pre, cv2.USAC_MAGSAC, thresh, maxIters=10000, confidence=0.9999)
    if H is None:
        return None, np.zeros(len(p_pre), bool)
    return H, mask.ravel().astype(bool)


def registration_metrics(p_pre, p_post, H, inl, gsd_m: float) -> dict:
    n_inl = int(inl.sum())
    out = {
        "n_matches": int(len(p_pre)),
        "n_inliers": n_inl,
        "inlier_ratio": round(n_inl / len(p_pre), 3) if len(p_pre) else 0.0,
        "success": bool(H is not None and n_inl >= MIN_INLIERS),
    }
    if not out["success"]:
        return out
    src = p_post[inl].astype(np.float64)
    dst = p_pre[inl].astype(np.float64)
    proj = cv2.perspectiveTransform(src[None], H)[0]
    resid = np.linalg.norm(proj - dst, axis=1)
    raw_offset = dst - src  # misalignment before registration, on trusted matches
    out.update(
        {
            "rmse_px": round(float(np.sqrt((resid**2).mean())), 3),
            "rmse_m": round(float(np.sqrt((resid**2).mean()) * gsd_m), 2),
            "raw_offset_median_px": round(float(np.median(np.linalg.norm(raw_offset, axis=1))), 2),
            "raw_offset_median_m": round(float(np.median(np.linalg.norm(raw_offset, axis=1)) * gsd_m), 2),
            "raw_offset_p90_px": round(float(np.percentile(np.linalg.norm(raw_offset, axis=1), 90)), 2),
            "raw_dx_px": round(float(np.median(raw_offset[:, 0])), 2),
            "raw_dy_px": round(float(np.median(raw_offset[:, 1])), 2),
        }
    )
    return out


def inlier_grid(p_pre_inl: np.ndarray, shape: tuple[int, int], n: int = 8) -> np.ndarray:
    """Count inliers per n x n cell, to show where a matcher stops working."""
    h, w = shape
    grid = np.zeros((n, n), int)
    if len(p_pre_inl) == 0:
        return grid
    ix = np.clip((p_pre_inl[:, 0] / w * n).astype(int), 0, n - 1)
    iy = np.clip((p_pre_inl[:, 1] / h * n).astype(int), 0, n - 1)
    np.add.at(grid, (iy, ix), 1)
    return grid


# --------------------------------------------------------------------------- #
# Visualisation
# --------------------------------------------------------------------------- #
def draw_matches(pre, post, p_pre, p_post, inl, out_path: Path, max_lines: int = 300, thumb: int = 1024):
    s = thumb / pre.shape[0]
    a = cv2.resize(pre, (thumb, thumb))
    b = cv2.resize(post, (thumb, thumb))
    canvas = np.concatenate([a, b], axis=1)
    idx = np.where(inl)[0]
    if len(idx) > max_lines:
        idx = np.random.default_rng(0).choice(idx, max_lines, replace=False)
    for i in idx:
        x1, y1 = (p_pre[i] * s).astype(int)
        x2, y2 = (p_post[i] * s).astype(int)
        cv2.line(canvas, (x1, y1), (x2 + thumb, y2), (0, 255, 0), 1, cv2.LINE_AA)
    cv2.imwrite(str(out_path), cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))


def draw_checkerboard(pre, post_reg, out_path: Path, cells: int = 8, thumb: int = 1024):
    a = cv2.resize(pre, (thumb, thumb))
    b = cv2.resize(post_reg, (thumb, thumb))
    cell = thumb // cells
    yy, xx = np.mgrid[0:thumb, 0:thumb]
    mask = ((yy // cell + xx // cell) % 2).astype(bool)
    out = np.where(mask[..., None], a, b)
    cv2.imwrite(str(out_path), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))


# --------------------------------------------------------------------------- #
# Warp
# --------------------------------------------------------------------------- #
def warp_to_pre(tile_dir: Path, H: np.ndarray, method: str) -> None:
    """Warp post_visual/post_ms into the pre-event pixel grid and save *_reg.tif."""
    with rasterio.open(tile_dir / "pre_visual.tif") as ref:
        ref_profile = ref.profile.copy()
        h, w = ref.height, ref.width
    for name in ("post_visual", "post_ms"):
        src_path = tile_dir / f"{name}.tif"
        if not src_path.exists():
            continue
        with rasterio.open(src_path) as src:
            arr = src.read()
            prof = src.profile.copy()
        interp = cv2.INTER_LINEAR
        warped = np.stack(
            [cv2.warpPerspective(b, H, (w, h), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0) for b in arr]
        )
        prof.update(transform=ref_profile["transform"], crs=ref_profile["crs"], height=h, width=w)
        with rasterio.open(tile_dir / f"{name}_reg.tif", "w", **prof) as dst:
            dst.write(warped.astype(arr.dtype))
    with open(tile_dir / "homography.json", "w") as f:
        json.dump({"method": method, "H_post_to_pre": H.tolist()}, f, indent=2)


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def register_pair(
    tile_dir: Path,
    match_size: int = 1024,
    warp_with: str = "lightglue",
    methods=("sift", "lightglue"),
    pre_source: str = "maxar",
) -> list[dict]:
    """pre_source='maxar' uses pre_visual.tif; 'naip' uses the 2022 aerial mosaic (cross-source test)."""
    qk = tile_dir.name
    if pre_source == "naip":
        with rasterio.open(tile_dir / "pre_naip.tif") as src:
            pre = np.ascontiguousarray(src.read([1, 2, 3]).transpose(1, 2, 0))
            prof = src.profile.copy()
    else:
        pre, prof = read_rgb(tile_dir / "pre_visual.tif")
    post, _ = read_rgb(tile_dir / "post_visual.tif")
    tag = f"{qk}_{pre_source}"
    gsd_m = abs(prof["transform"].a)
    meta = json.loads((tile_dir / "pair.json").read_text())

    rows, best = [], {}
    for m in methods:
        t0 = time.perf_counter()
        p_pre, p_post, info = MATCHERS[m](pre, post, match_size)
        t_match = time.perf_counter() - t0
        H, inl = estimate_homography(p_pre, p_post)
        met = registration_metrics(p_pre, p_post, H, inl, gsd_m)
        grid = inlier_grid(p_pre[inl], pre.shape[:2])
        row = {
            "quadkey": qk,
            "fire": meta.get("fire"),
            "pre_source": pre_source,
            "method": m,
            "match_size": match_size,
            "gsd_m": round(gsd_m, 3),
            "off_nadir_diff": meta.get("off_nadir_diff"),
            "pre_date": meta.get("pre_date"),
            "post_date": meta.get("post_date"),
            "time_s": round(t_match, 2),
            **info,
            **met,
            "empty_cells_8x8": int((grid == 0).sum()),
            "min_cell_inliers": int(grid.min()),
        }
        rows.append(row)
        np.save(RESULTS_DIR / f"{tag}_{m}_inlier_grid.npy", grid)
        draw_matches(pre, post, p_pre, p_post, inl, RESULTS_DIR / f"{tag}_{m}_matches.jpg")
        print(f"[{tag}] {m:9s} matches={row['n_matches']:5d} inliers={row['n_inliers']:5d} "
              f"rmse={row.get('rmse_px', float('nan')):.2f}px raw_offset={row.get('raw_offset_median_px', float('nan'))}px "
              f"empty_cells={row['empty_cells_8x8']}/64 t={t_match:.1f}s")
        if met["success"]:
            best[m] = H

    chosen = warp_with if warp_with in best else (max(best, key=lambda k: [r for r in rows if r["method"] == k][0]["n_inliers"]) if best else None)
    if pre_source != "maxar":
        pass  # cross-source runs are diagnostic only; the Maxar pre tile stays the reference grid
    elif chosen:
        warp_to_pre(tile_dir, best[chosen], chosen)
        post_reg, _ = read_rgb(tile_dir / "post_visual_reg.tif")
        draw_checkerboard(pre, post_reg, RESULTS_DIR / f"{qk}_checker_registered.jpg")
        draw_checkerboard(pre, post, RESULTS_DIR / f"{qk}_checker_raw.jpg")
        print(f"[{qk}] warped post -> pre with {chosen}")
    else:
        print(f"[{qk}] registration FAILED for all methods")
    for r in rows:
        r["warped_with"] = chosen
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qk", nargs="*", help="quadkeys to process (default: all in data/tiles)")
    ap.add_argument("--match-size", type=int, default=1024)
    ap.add_argument("--warp-with", default="lightglue", choices=["lightglue", "sift"])
    ap.add_argument("--pre-source", default="maxar", choices=["maxar", "naip"])
    a = ap.parse_args()

    dirs = [TILE_DIR / q for q in a.qk] if a.qk else sorted(d for d in TILE_DIR.iterdir() if (d / "pair.json").exists())
    all_rows = []
    for d in dirs:
        if a.pre_source == "naip" and not (d / "pre_naip.tif").exists():
            print(f"[{d.name}] no pre_naip.tif, skipping (run python -m src.naip --qk {d.name})")
            continue
        all_rows += register_pair(d, match_size=a.match_size, warp_with=a.warp_with, pre_source=a.pre_source)
    df = pd.DataFrame(all_rows)
    out = RESULTS_DIR / "registration_metrics.csv"
    if out.exists():
        old = pd.read_csv(out, dtype={"quadkey": str})
        key = ["quadkey", "pre_source", "method", "match_size"]
        merged = old.merge(df[key].drop_duplicates(), on=key, how="left", indicator=True)
        old = old[merged["_merge"].values == "left_only"]
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(out, index=False)
    cols = ["quadkey", "pre_source", "match_size", "method", "n_matches", "n_inliers", "inlier_ratio", "rmse_px", "raw_offset_median_px", "raw_offset_median_m", "empty_cells_8x8", "time_s"]
    print("\n" + df[[c for c in cols if c in df.columns]].to_string(index=False))


if __name__ == "__main__":
    main()
