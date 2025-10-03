import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str
    artist_name: str
    dataset_path: str
    output_excel: str = "final_results.xlsx"


def load_settings() -> Settings:
    # Allow .env but do not require it
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

    client_id = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

    artist_name = os.getenv("ARTIST_NAME", "Ed Sheeran")

    # Windows path in requirement (user provided). Allow override via DATASET_PATH.
    dataset_path = os.getenv(
        "DATASET_PATH", os.path.expanduser("C:/data/unclaimedmusicalworkrightshares.tsv")
    )

    output_excel = os.getenv("OUTPUT_EXCEL", "final_results.xlsx")

    return Settings(
        spotify_client_id=client_id,
        spotify_client_secret=client_secret,
        spotify_redirect_uri=redirect_uri,
        artist_name=artist_name,
        dataset_path=dataset_path,
        output_excel=output_excel,
    )
