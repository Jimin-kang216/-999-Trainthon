"""AfterMap demo: pre/post satellite co-registration -> damage grid -> map.

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.config import RESULTS_DIR, TILE_DIR

st.set_page_config(page_title="AfterMap", layout="wide")


@st.cache_data
def load_pairs() -> list[dict]:
    out = []
    for d in sorted(TILE_DIR.iterdir()):
        if (d / "pair.json").exists() and (RESULTS_DIR / f"{d.name}_damage_summary.json").exists():
            rec = json.loads((d / "pair.json").read_text())
            rec["_has_dins"] = (RESULTS_DIR / f"{d.name}_validation.json").exists()
            out.append(rec)
    out.sort(key=lambda p: (not p["_has_dins"], p.get("dist_to_fire_km", 99)))
    return out


@st.cache_data
def load_metrics() -> pd.DataFrame:
    p = RESULTS_DIR / "registration_metrics.csv"
    return pd.read_csv(p, dtype={"quadkey": str}) if p.exists() else pd.DataFrame()


def read_json(p: Path) -> dict | None:
    return json.loads(p.read_text()) if p.exists() else None


pairs = load_pairs()
if not pairs:
    st.error("No processed tiles. Run: python -m src.ingest all --n 4 && python -m src.register && python -m src.damage")
    st.stop()

st.title("AfterMap — 재난 전·후 위성영상 자동 정합 및 피해 지도")
st.caption("Maxar Open Data (LA wildfires, Jan 2025) · DISK+LightGlue co-registration · ΔNDVI + SSIM change score · validated against CAL FIRE DINS")

labels = {p["quadkey"]: f"{p['quadkey']} — {p['fire']} fire ({p['dist_to_fire_km']} km) · pre {p['pre_date']} / post {p['post_date']}" for p in pairs}
qk = st.sidebar.selectbox("Tile", list(labels), format_func=labels.get)
pair = next(p for p in pairs if p["quadkey"] == qk)
summary = read_json(RESULTS_DIR / f"{qk}_damage_summary.json")
validation = read_json(RESULTS_DIR / f"{qk}_validation.json")
metrics = load_metrics()

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline**")
st.sidebar.markdown("1. STAC index → quadkey pairing\n2. Learned matching → MAGSAC homography\n3. ΔNDVI + SSIM → 50 m grid\n4. GeoJSON / web map")
show_heat = st.sidebar.checkbox("Damage heatmap", True)
show_grid = st.sidebar.checkbox("Grid cells (severe/moderate only — can be slow)", False)
show_dins = st.sidebar.checkbox("CAL FIRE DINS inspections (sampled)", False)

# ------------------------------------------------------------------ summary cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Severe cells", f"{summary['n_severe']:,}", f"{summary['severe_area_ha']:,} ha")
c2.metric("Moderate cells", f"{summary['n_moderate']:,}", f"{summary['moderate_area_ha']:,} ha")
c3.metric("Mean ΔNDVI", f"{summary['mean_d_ndvi']:+.3f}")
removed = 1 - summary["mean_change_registered"] / summary["mean_change_raw"]
c4.metric("False change removed by registration", f"{removed:.0%}", f"{summary['mean_change_raw']:.3f} → {summary['mean_change_registered']:.3f}")

tab_map, tab_reg, tab_val = st.tabs(["Damage map", "Registration (AI vs classical)", "Validation vs DINS"])

# ------------------------------------------------------------------ map
with tab_map:
    w, s, e, n = summary["bounds_wgs84"]
    m = folium.Map(location=[(s + n) / 2, (w + e) / 2], zoom_start=13, tiles="OpenStreetMap")
    folium.TileLayer("Esri.WorldImagery", name="Esri imagery (basemap)").add_to(m)
    if show_heat:
        folium.raster_layers.ImageOverlay(
            image=str(RESULTS_DIR / f"{qk}_damage_heat.png"), bounds=[[s, w], [n, e]], opacity=0.85, name="Damage score"
        ).add_to(m)
    if show_grid:
        grid_path = RESULTS_DIR / f"{qk}_damage_grid.geojson"
        gj = json.loads(grid_path.read_text())
        gj["features"] = [f for f in gj["features"] if f["properties"]["damage_class"] != "none"]
        colors = {"severe": "#d7191c", "moderate": "#fdae61"}
        folium.GeoJson(
            gj,
            name="Damage grid",
            style_function=lambda f: {"color": colors[f["properties"]["damage_class"]], "weight": 0.5, "fillOpacity": 0.25},
            tooltip=folium.GeoJsonTooltip(fields=["damage_class", "score", "d_ndvi", "ssim"], aliases=["class", "score", "ΔNDVI", "SSIM"]),
        ).add_to(m)
    if show_dins and (RESULTS_DIR / f"{qk}_dins_joined.geojson").exists():
        dj = json.loads((RESULTS_DIR / f"{qk}_dins_joined.geojson").read_text())
        feats = dj["features"]
        if len(feats) > 2500:
            rng = np.random.default_rng(0)
            feats = list(rng.choice(feats, 2500, replace=False))
        dcol = {"Destroyed (>50%)": "#000000", "Major (26-50%)": "#7b3294", "Minor (10-25%)": "#c2a5cf", "Affected (1-9%)": "#a6dba0", "No Damage": "#008837"}
        fg = folium.FeatureGroup(name="DINS inspections")
        for f in feats:
            lon, lat = f["geometry"]["coordinates"]
            dmg = f["properties"]["DAMAGE"]
            folium.CircleMarker([lat, lon], radius=2, color=dcol.get(dmg, "#888"), fill=True, fill_opacity=0.9, weight=0,
                                tooltip=f"{dmg} · score {f['properties']['score']}").add_to(fg)
        fg.add_to(m)
    folium.LayerControl().add_to(m)
    st_folium(m, height=650, width="stretch")

    dl1, dl2 = st.columns(2)
    dl1.download_button("Download damage grid (GeoJSON)", (RESULTS_DIR / f"{qk}_damage_grid.geojson").read_bytes(),
                        file_name=f"{qk}_damage_grid.geojson", mime="application/geo+json")
    score_tif = TILE_DIR / qk / "damage_score.tif"
    if score_tif.exists():
        dl2.download_button("Download score raster (GeoTIFF)", score_tif.read_bytes(), file_name=f"{qk}_damage_score.tif", mime="image/tiff")

# ------------------------------------------------------------------ registration
with tab_reg:
    st.markdown(
        f"Pre/post off-nadir difference for this tile: **{pair.get('off_nadir_diff')}°**. "
        "Both matchers feed the same MAGSAC++ homography; only the correspondences differ."
    )
    mt = metrics[metrics.quadkey == qk] if not metrics.empty else pd.DataFrame()
    if not mt.empty:
        cols = ["pre_source", "match_size", "method", "n_matches", "n_inliers", "inlier_ratio", "rmse_px", "raw_offset_median_m", "empty_cells_8x8", "time_s"]
        st.dataframe(mt[[c for c in cols if c in mt.columns]].sort_values(["pre_source", "match_size", "method"]), hide_index=True, use_container_width=True)
        naip = mt[(mt.pre_source == "naip") & (mt.match_size == mt.match_size.min())]
        if len(naip) == 2:
            a = naip.set_index("method").n_inliers
            st.info(f"Cross-source test (2022 NAIP aerial → 2025 Maxar satellite): SIFT {a['sift']} inliers vs LightGlue {a['lightglue']} inliers "
                    f"(**{a['lightglue'] / max(a['sift'], 1):.0f}×**). Same-sensor Maxar pairs are already well aligned; the learned matcher matters when the 'before' image is an old aerial basemap.")

    src_choice = st.radio("Pre-event source", ["maxar", "naip"], horizontal=True)
    i1, i2 = st.columns(2)
    for col, method in ((i1, "sift"), (i2, "lightglue")):
        p = RESULTS_DIR / f"{qk}_{src_choice}_{method}_matches.jpg"
        if p.exists():
            col.image(str(p), caption=f"{method.upper()} inlier matches — pre ({src_choice}) | post", width="stretch")
        grid_p = RESULTS_DIR / f"{qk}_{src_choice}_{method}_inlier_grid.npy"
        if grid_p.exists():
            g = np.load(grid_p)
            col.caption(f"inliers per 8×8 cell — empty cells: {(g == 0).sum()}/64, min: {g.min()}, max: {g.max()}")

    st.markdown("**Checkerboard: pre | post** (left: raw overlay, right: after registration)")
    k1, k2 = st.columns(2)
    for col, name in ((k1, "checker_raw"), (k2, "checker_registered")):
        p = RESULTS_DIR / f"{qk}_{name}.jpg"
        if p.exists():
            col.image(str(p), width="stretch")

# ------------------------------------------------------------------ validation
with tab_val:
    if validation and "roc_auc" in validation:
        v1, v2, v3 = st.columns(3)
        v1.metric("Inspected structures in tile", f"{validation['n_structures_in_tile']:,}")
        v2.metric("ROC-AUC (destroyed vs no damage)", validation["roc_auc"])
        v3.metric("Average precision", validation["average_precision"])
        st.markdown(
            f"At the *severe* threshold ({validation['severe_threshold']}): precision **{validation['severe_precision']}**, recall **{validation['severe_recall']}**. "
            f"At *moderate* ({validation['moderate_threshold']}): precision {validation['moderate_precision']}, recall {validation['moderate_recall']}."
        )
        b1, b2 = st.columns(2)
        b1.image(str(RESULTS_DIR / f"{qk}_dins_boxplot.png"), width="stretch")
        b2.image(str(RESULTS_DIR / f"{qk}_dins_pr_curve.png"), width="stretch")
        st.caption("Ground truth: CAL FIRE Damage Inspection (DINS) public feature service, structure-level field inspections.")
    else:
        st.warning("No DINS inspections fall inside this tile, so no ground-truth comparison is available.")
