from __future__ import annotations

import sys
import traceback
from typing import List
import argparse

import pandas as pd

from src.config import load_settings
from src.dataset_loader import load_unclaimed_dataset, build_isrc_index
from src.spotify_client import create_spotify_client, fetch_full_catalog
from src.cross_reference import catalog_to_dataframe, compute_matches
from src.excel_export import export_to_excel


def run() -> int:
    settings = load_settings()

    # CLI overrides for ad-hoc runs
    parser = argparse.ArgumentParser(description="Tritone task runner")
    parser.add_argument("--artist", dest="artist_name", help="Artist name override")
    parser.add_argument("--dataset", dest="dataset_path", help="Path to TSV dataset override")
    parser.add_argument("--output", dest="output_excel", help="Output Excel path override")
    args, _ = parser.parse_known_args()

    if args.artist_name:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=args.artist_name,
            dataset_path=settings.dataset_path,
            output_excel=settings.output_excel,
        )
    if args.dataset_path:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=settings.artist_name,
            dataset_path=args.dataset_path,
            output_excel=settings.output_excel,
        )
    if args.output_excel:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=settings.artist_name,
            dataset_path=settings.dataset_path,
            output_excel=args.output_excel,
        )

    # Load dataset
    try:
        unclaimed_df = load_unclaimed_dataset(settings.dataset_path)
        _, isrc_index = build_isrc_index(unclaimed_df)
    except Exception as exc:
        print(f"ERROR: Failed to load dataset at {settings.dataset_path}: {exc}")
        return 2

    # Spotify
    try:
        sp = create_spotify_client(settings.spotify_client_id, settings.spotify_client_secret)
    except Exception as exc:
        print("ERROR: Failed to create Spotify client. Check credentials.")
        print(str(exc))
        return 3

    # Fetch catalog
    try:
        catalog: List[dict] = fetch_full_catalog(sp, settings.artist_name)
    except Exception as exc:
        print(f"ERROR: Failed to fetch catalog for artist '{settings.artist_name}': {exc}")
        return 4

    catalog_df = catalog_to_dataframe(catalog)

    # Notes gathering
    missing_isrc_count = int((catalog_df["__ISRC_UPPER_STRIPPED"] == "").sum()) if not catalog_df.empty else 0
    total_tracks = int(len(catalog_df))

    # Cross-reference
    try:
        full_catalog_df, matches_df = compute_matches(catalog_df, unclaimed_df)
    except Exception as exc:
        print(f"ERROR: Failed during cross-reference: {exc}")
        return 5

    notes = (
        f"Artist: {settings.artist_name}. Total tracks: {total_tracks}. "
        f"Tracks missing ISRC: {missing_isrc_count}. "
        f"Dataset path: {settings.dataset_path}. "
        f"Matched rows: {len(matches_df)}."
    )

    # Export
    try:
        export_to_excel(full_catalog_df, matches_df, notes, settings.output_excel)
    except Exception as exc:
        print(f"ERROR: Failed to write Excel '{settings.output_excel}': {exc}")
        return 6

    print(f"Wrote results to {settings.output_excel}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
