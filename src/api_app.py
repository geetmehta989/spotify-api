from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import load_settings
from src.dataset_loader import load_unclaimed_dataset
from src.spotify_client import create_spotify_client, fetch_full_catalog
from src.cross_reference import catalog_to_dataframe, compute_matches
from src.excel_export import export_to_excel

app = FastAPI(title="Tritone Excel Generator")


class GenerateRequest(BaseModel):
    artist: str | None = None
    dataset_path: str | None = None
    output_excel: str | None = None


@app.post("/generate")
def generate(req: GenerateRequest):
    settings = load_settings()
    if req.artist:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=req.artist,
            dataset_path=settings.dataset_path,
            output_excel=settings.output_excel,
        )
    if req.dataset_path:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=settings.artist_name,
            dataset_path=req.dataset_path,
            output_excel=settings.output_excel,
        )
    if req.output_excel:
        settings = settings.__class__(
            spotify_client_id=settings.spotify_client_id,
            spotify_client_secret=settings.spotify_client_secret,
            spotify_redirect_uri=settings.spotify_redirect_uri,
            artist_name=settings.artist_name,
            dataset_path=settings.dataset_path,
            output_excel=req.output_excel,
        )

    try:
        unclaimed_df = load_unclaimed_dataset(settings.dataset_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dataset error: {e}")

    sp = create_spotify_client(settings.spotify_client_id, settings.spotify_client_secret)
    catalog = fetch_full_catalog(sp, settings.artist_name)
    catalog_df = catalog_to_dataframe(catalog)

    full_catalog_df, matches_df = compute_matches(catalog_df, unclaimed_df)

    notes = (
        f"Artist: {settings.artist_name}. Total tracks: {len(full_catalog_df)}. "
        f"Tracks missing ISRC: {int((full_catalog_df['__ISRC_UPPER_STRIPPED'] == '').sum())}."
    )

    output_path = settings.output_excel
    try:
        export_to_excel(full_catalog_df, matches_df, notes, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel error: {e}")

    return {"status": "ok", "output_excel": output_path}
