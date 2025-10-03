from __future__ import annotations

import os
import glob
import tempfile
import re
from urllib.parse import urlparse

try:
    import gdown  # type: ignore
except Exception:
    gdown = None
import pandas as pd
from typing import Tuple


def _maybe_download_from_url(source: str) -> str | None:
    """If source looks like a URL, attempt to download and return local path."""
    if not source:
        return None
    parsed = urlparse(source)
    if not parsed.scheme or parsed.scheme.lower() not in {"http", "https"}:
        return None

    # Handle Google Drive URL id formats
    drive_id = None
    m = re.search(r"/d/([^/]+)/view", source)
    if m:
        drive_id = m.group(1)
    elif "id=" in source:
        drive_id = re.search(r"id=([A-Za-z0-9_-]+)", source).group(1) if re.search(r"id=([A-Za-z0-9_-]+)", source) else None

    tmpdir = tempfile.mkdtemp(prefix="tritone_dl_")
    out_path = os.path.join(tmpdir, "unclaimedmusicalworkrightshares.tsv")

    if drive_id and gdown:
        gdown.download(id=drive_id, output=out_path, quiet=True)
        return out_path if os.path.isfile(out_path) else None

    # Fallback: plain HTTP download via requests
    try:
        import requests
        with requests.get(source, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return out_path if os.path.isfile(out_path) else None
    except Exception:
        return None


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

    # If tsv_path is a URL, try downloading
    if resolved_path is None:
        dl = _maybe_download_from_url(tsv_path)
        if dl and os.path.isfile(dl):
            resolved_path = dl
    for p in candidate_paths:
        if os.path.isfile(p):
            resolved_path = p
            break

    if resolved_path is None:
        # Try to discover a likely TSV in common locations
        search_roots = [
            os.getcwd(),
            os.path.join(os.getcwd(), "data"),
        ]
        candidates_glob = [
            "*unclaimed*musical*work*right*shares*.tsv",
            "*unclaimed*work*shares*.tsv",
            "*.tsv",
        ]
        discovered = []
        for root in search_roots:
            for pat in candidates_glob:
                discovered.extend(glob.glob(os.path.join(root, pat)))

        if len(discovered) == 1 and os.path.isfile(discovered[0]):
            resolved_path = discovered[0]
        else:
            raise FileNotFoundError(
                "Dataset file not found. Tried: "
                + str(candidate_paths)
                + "; also searched: "
                + ", ".join(search_roots)
                + "; found: "
                + str(discovered[:10])
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
