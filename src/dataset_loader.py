from __future__ import annotations

import pandas as pd
from typing import Tuple


def load_unclaimed_dataset(tsv_path: str) -> pd.DataFrame:
    df = pd.read_csv(tsv_path, sep="\t", dtype=str, keep_default_na=False)
    # Normalize ISRC column names, keep all original columns
    candidate_cols = [
        "ISRC", "isrc", "Isrc", "ISRC_code", "isrc_code", "ISRC Code",
    ]
    isrc_col = None
    for col in df.columns:
        if col.strip() in candidate_cols:
            isrc_col = col
            break
    if isrc_col is None:
        # Try fuzzy match by lowercase and removing spaces
        normalized = {c: c.lower().replace(" ", "") for c in df.columns}
        inv = {v: k for k, v in normalized.items()}
        if "isrc" in inv:
            isrc_col = inv["isrc"]
    if isrc_col is None:
        raise ValueError(
            "Could not locate ISRC column in dataset. Expected a column named like 'ISRC'."
        )

    # Create normalized columns for fast lookup
    df["__ISRC_UPPER_STRIPPED"] = df[isrc_col].astype(str).str.upper().str.strip()

    # Deduplicate on normalized ISRC to reduce noise
    df = df.drop_duplicates(subset=["__ISRC_UPPER_STRIPPED"])  # keep first occurrence

    return df


def build_isrc_index(df: pd.DataFrame) -> Tuple[pd.DataFrame, set[str]]:
    isrc_set = set(df["__ISRC_UPPER_STRIPPED"].dropna().tolist())
    return df, isrc_set
