from __future__ import annotations

from typing import List, Tuple

import pandas as pd


def catalog_to_dataframe(catalog: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(catalog)
    if df.empty:
        return pd.DataFrame(
            columns=["track_name", "album_name", "album_release_date", "isrc", "track_id", "album_id"]
        )
    # Normalize ISRC for matching
    df["__ISRC_UPPER_STRIPPED"] = df["isrc"].fillna("").astype(str).str.upper().str.strip()
    return df


def compute_matches(catalog_df: pd.DataFrame, unclaimed_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Inner join on normalized ISRC helper column
    merged = catalog_df.merge(
        unclaimed_df,
        how="inner",
        on="__ISRC_UPPER_STRIPPED",
        suffixes=("_catalog", "_unclaimed"),
    )
    return catalog_df, merged
