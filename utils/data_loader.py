"""Load and cache Oracle's Elixir LOL esports match data"""

from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

DATA_DIR = Path("data")
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "all_seasons.parquet"

YEAR_RANGE = range(2014, 2026)


def _csv_path(year: int) -> Path:
    return DATA_DIR / f"{year}_LoL_esports_match_data_from_OraclesElixir.csv"


def _cache_is_stale() -> bool:
    if not CACHE_FILE.exists():
        return True
    cache_mtime = CACHE_FILE.stat().st_mtime
    return any(_csv_path(y).stat().st_mtime > cache_mtime for y in YEAR_RANGE)


def load_all_seasons(use_cache: bool = True) -> pd.DataFrame:
    """Load all season CSVs into one DataFrame, with parquet caching"""
    if use_cache and not _cache_is_stale():
        return pd.read_parquet(CACHE_FILE)

    frames = []
    for year in tqdm(YEAR_RANGE, desc="Loading seasons"):
        df = pd.read_csv(_csv_path(year=year), low_memory=False, parse_dates=["date"])
        df["year"] = year
        frames.append(df)

    full: pd.DataFrame = pd.concat(frames, ignore_index=True)

    CACHE_DIR.mkdir(exist_ok=True)
    full.to_parquet(CACHE_FILE, index=False)
    return full
