from __future__ import annotations

import os
import pandas as pd
from typing import Tuple


def load_unclaimed_dataset(tsv_path: str) -> pd.DataFrame:
    # Resolve common Windows path issues (spaces, quoting)
    candidate_paths = []
    if tsv_path:
        candidate_paths.append(tsv_path)
        # If path contains backslashes, also try forward-slash version
        candidate_paths.append(tsv_path.replace("\\", "/"))

    # Fallback defaults commonly used in this project
    candidate_paths.extend([
        "C:/spotify api/unclaimedmusicalworkrightshares.tsv",
        "C:/data/unclaimedmusicalworkrightshares.tsv",
    ])

    resolved_path = None
    for p in candidate_paths:
        if os.path.isfile(p):
            resolved_path = p
            break

    if resolved_path is None:
        raise FileNotFoundError(
            f"Dataset file not found. Tried: {candidate_paths}"
        )

    df = pd.read_csv(resolved_path, sep="\t", dtype=str, keep_default_na=False)
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
