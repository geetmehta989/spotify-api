from __future__ import annotations

import time
from typing import Dict, Iterable, List, Sequence

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def create_spotify_client(client_id: str, client_secret: str) -> spotipy.Spotify:
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )
    return spotipy.Spotify(auth_manager=auth_manager, requests_timeout=20, retries=10)


def get_artist_id(sp: spotipy.Spotify, artist_name: str) -> str:
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    items = results.get("artists", {}).get("items", [])
    if not items:
        raise ValueError(f"Artist not found: {artist_name}")
    return items[0]["id"]


def paginate(sp_method, *args, limit: int = 50, sleep: float = 0.0, **kwargs) -> Iterable[Dict]:
    offset = 0
    while True:
        page = sp_method(*args, limit=limit, offset=offset, **kwargs)
        items = page.get("items", [])
        for item in items:
            yield item
        offset += len(items)
        if len(items) < limit:
            break
        if sleep:
            time.sleep(sleep)


def fetch_artist_albums(sp: spotipy.Spotify, artist_id: str) -> List[Dict]:
    album_types = ["album", "single", "compilation", "appears_on"]
    seen_albums = {}
    for album_type in album_types:
        for album in paginate(sp.artist_albums, artist_id, album_type=album_type, country="US"):
            album_id = album.get("id")
            if album_id and album_id not in seen_albums:
                seen_albums[album_id] = album
    return list(seen_albums.values())


def _chunks(items: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def fetch_album_tracks_with_isrc(sp: spotipy.Spotify, album_id: str) -> List[Dict]:
    tracks_meta: List[Dict] = list(paginate(sp.album_tracks, album_id, market="US"))
    track_ids: List[str] = [t["id"] for t in tracks_meta if t.get("id")]

    tracks: List[Dict] = []
    # Batch fetch up to 50 tracks at once
    for batch in _chunks(track_ids, 50):
        fulls = sp.tracks(batch).get("tracks", [])
        for track_full in fulls:
            isrc = (track_full.get("external_ids", {}) or {}).get("isrc")
            track_entry = {
                "track_name": track_full.get("name"),
                "track_id": track_full.get("id"),
                "album_id": album_id,
                "album_name": track_full.get("album", {}).get("name"),
                "album_release_date": track_full.get("album", {}).get("release_date"),
                "isrc": isrc,
            }
            tracks.append(track_entry)
    return tracks


def fetch_full_catalog(sp: spotipy.Spotify, artist_name: str) -> List[Dict]:
    artist_id = get_artist_id(sp, artist_name)
    albums = fetch_artist_albums(sp, artist_id)

    all_tracks: List[Dict] = []
    seen_track_ids = set()

    for album in albums:
        album_id = album.get("id")
        if not album_id:
            continue
        album_tracks = fetch_album_tracks_with_isrc(sp, album_id)
        for t in album_tracks:
            tid = t.get("track_id")
            if tid and tid not in seen_track_ids:
                seen_track_ids.add(tid)
                all_tracks.append(t)

    return all_tracks
