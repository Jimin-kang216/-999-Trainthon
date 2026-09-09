"""Step 3b: validate the unsupervised damage score against CAL FIRE DINS inspections.

CAL FIRE publishes structure-level Damage Inspection (DINS) points for the Eaton and
Palisades fires. Each inspected structure is assigned the score of the grid cell it
falls in; "Destroyed (>50%)" vs "No Damage" gives a binary benchmark.

Usage:
    python -m src.validate                # download DINS (cached) + evaluate all tiles
    python -m src.validate --qk 031311103033
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score

from .config import DATA_DIR, RESULTS_DIR, TILE_DIR
from .damage import MODERATE_T, SEVERE_T

DINS_SERVICES = {
    "Eaton": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/DINS_2025_Eaton_Public_View/FeatureServer/0",
    "Palisades": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/DINS_2025_Palisades_Public_View/FeatureServer/0",
}
DESTROYED = "Destroyed (>50%)"
NO_DAMAGE = "No Damage"


def fetch_dins(fire: str) -> gpd.GeoDataFrame:
    out = DATA_DIR / f"dins_{fire.lower()}.geojson"
    if out.exists():
        return gpd.read_file(out)
    url = DINS_SERVICES[fire] + "/query"
    feats, offset = [], 0
    while True:
        r = requests.get(
            url,
            params={"where": "1=1", "outFields": "DAMAGE,STRUCTURETYPE", "outSR": 4326, "f": "geojson",
                    "resultOffset": offset, "resultRecordCount": 8000},
            timeout=120,
        ).json()
        batch = r.get("features", [])
        feats += batch
        if len(batch) < 8000:
            break
        offset += len(batch)
    gdf = gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326")
    gdf.to_file(out, driver="GeoJSON")
    print(f"DINS {fire}: {len(gdf)} structures -> {out}")
    return gdf


def evaluate_tile(qk: str, dins: dict[str, gpd.GeoDataFrame]) -> dict | None:
    grid = gpd.read_file(RESULTS_DIR / f"{qk}_damage_grid.geojson")
    fire = json.loads((TILE_DIR / qk / "pair.json").read_text()).get("fire")
    pts = dins[fire]
    pts = pts[pts.within(grid.union_all().envelope)]
    if pts.empty:
        print(f"[{qk}] no DINS points inside tile")
        return None

    joined = gpd.sjoin(pts, grid[["score", "d_ndvi", "ssim", "damage_class", "geometry"]], how="inner", predicate="within")
    joined.to_file(RESULTS_DIR / f"{qk}_dins_joined.geojson", driver="GeoJSON")

    counts = joined.DAMAGE.value_counts().to_dict()
    binary = joined[joined.DAMAGE.isin([DESTROYED, NO_DAMAGE])]
    y = (binary.DAMAGE == DESTROYED).astype(int).values
    s = binary.score.values
    res = {"quadkey": qk, "fire": fire, "n_structures_in_tile": int(len(joined)), "dins_counts": counts}
    if y.sum() == 0 or y.sum() == len(y):
        print(f"[{qk}] DINS has only one class here ({counts}); skipping AUC")
        return res

    res["roc_auc"] = round(float(roc_auc_score(y, s)), 3)
    res["average_precision"] = round(float(average_precision_score(y, s)), 3)
    for name, t in (("severe", SEVERE_T), ("moderate", MODERATE_T)):
        pred = s >= t
        tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum()); fn = int((~pred & (y == 1)).sum())
        res[f"{name}_threshold"] = t
        res[f"{name}_precision"] = round(tp / max(tp + fp, 1), 3)
        res[f"{name}_recall"] = round(tp / max(tp + fn, 1), 3)
    # Mean score per DINS class: shows the score is monotone in inspected damage.
    res["mean_score_by_class"] = {k: round(float(v), 3) for k, v in joined.groupby("DAMAGE").score.mean().items()}

    # PR curve figure
    p, r, _ = precision_recall_curve(y, s)
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.plot(r, p, lw=2)
    ax.set_xlabel("recall (destroyed structures)"); ax.set_ylabel("precision")
    ax.set_title(f"{fire} fire, tile {qk}\nAUC={res['roc_auc']}  AP={res['average_precision']}  n={len(y)}")
    ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"{qk}_dins_pr_curve.png", dpi=150); plt.close(fig)

    # Score distribution per class
    fig, ax = plt.subplots(figsize=(6, 3.5))
    order = [NO_DAMAGE, "Affected (1-9%)", "Minor (10-25%)", "Major (26-50%)", DESTROYED]
    data = [joined[joined.DAMAGE == c].score.values for c in order if (joined.DAMAGE == c).any()]
    labels = [f"{c}\n(n={int((joined.DAMAGE == c).sum())})" for c in order if (joined.DAMAGE == c).any()]
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.axhline(SEVERE_T, color="r", ls="--", lw=1, label=f"severe ≥ {SEVERE_T}")
    ax.set_ylabel("cell damage score"); ax.tick_params(axis="x", labelsize=7); ax.legend(fontsize=8)
    ax.set_title(f"AfterMap score vs CAL FIRE DINS inspection — {fire}, {qk}", fontsize=9)
    fig.tight_layout(); fig.savefig(RESULTS_DIR / f"{qk}_dins_boxplot.png", dpi=150); plt.close(fig)

    (RESULTS_DIR / f"{qk}_validation.json").write_text(json.dumps(res, indent=2))
    print(f"[{qk}] {fire}: n={len(joined)} destroyed={int(y.sum())} AUC={res['roc_auc']} AP={res['average_precision']} "
          f"severe P/R={res['severe_precision']}/{res['severe_recall']} moderate P/R={res['moderate_precision']}/{res['moderate_recall']}")
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qk", nargs="*")
    a = ap.parse_args()
    dins = {f: fetch_dins(f) for f in DINS_SERVICES}
    qks = a.qk or sorted(p.name.split("_")[0] for p in RESULTS_DIR.glob("*_damage_grid.geojson"))
    rows = [r for q in qks if (r := evaluate_tile(q, dins))]
    pd.DataFrame(rows).drop(columns=["dins_counts", "mean_score_by_class"], errors="ignore").to_csv(RESULTS_DIR / "validation_summary.csv", index=False)


if __name__ == "__main__":
    main()
