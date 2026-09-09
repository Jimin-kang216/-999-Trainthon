"""Project-wide constants for the AfterMap pipeline."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TILE_DIR = DATA_DIR / "tiles"
RESULTS_DIR = ROOT / "results"

for _d in (DATA_DIR, TILE_DIR, RESULTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Maxar Open Data Program (STAC, public S3 bucket)
MAXAR_BASE = "https://maxar-opendata.s3.amazonaws.com/events"
EVENT_ID = "WildFires-LosAngeles-Jan-2025"
EVENT_URL = f"{MAXAR_BASE}/{EVENT_ID}"

# Fires ignited 2025-01-07; anything acquired before this is "pre-event".
EVENT_DATE = "2025-01-07"

# Approximate fire centroids (lon, lat) used to rank tile pairs by relevance.
FIRE_CENTROIDS = {
    "Palisades": (-118.545, 34.070),
    "Eaton": (-118.130, 34.190),
}

INDEX_CSV = DATA_DIR / "index.csv"
PAIRS_CSV = DATA_DIR / "pairs.csv"

# Edge length (px) of the downsampled tile used for matching and analysis.
TILE_SIZE = 2048
