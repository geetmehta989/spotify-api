## Tritone Task: Spotify ISRC Cross-Reference

This project loads a TSV dataset of unclaimed musical work right shares, fetches a Spotify artist's full catalog (albums, singles, EPs, compilations, appearances), cross-references by ISRC, and exports a 3-sheet Excel workbook.

### What it does
- Loads `unclaimedmusicalworkrightshares.tsv` from a local path
- Fetches the artist catalog via Spotify Web API using Spotipy
- Extracts Track Name, Album, Release Date, and ISRC per track
- Cross-references ISRCs against the dataset
- Exports `final_results.xlsx` with 3 sheets: Artist Catalog, Matches, Notes

### Requirements
- Python 3.10+
- Spotify API credentials
- Local TSV dataset path (defaults to `C:/data/unclaimedmusicalworkrightshares.tsv` per assignment)

### Setup
1. Clone the repository and cd into it.
2. Create and activate a virtual environment and install deps:
```bash
./scripts/setup.sh
```
3. Copy `.env.example` to `.env` and fill in values:
```bash
cp .env.example .env
# edit .env with your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
```

### Configuration
- Configure via environment variables or `.env` file:
  - `SPOTIFY_CLIENT_ID`: your client ID
  - `SPOTIFY_CLIENT_SECRET`: your client secret
  - `SPOTIFY_REDIRECT_URI`: not used for client credentials, kept for completeness
  - `ARTIST_NAME`: artist to fetch (default: Ed Sheeran)
  - `DATASET_PATH`: path to TSV file (default: `C:/data/unclaimedmusicalworkrightshares.tsv`)
  - `OUTPUT_EXCEL`: output filename (default: `final_results.xlsx`)

### Run
```bash
./scripts/run.sh
```
The script will:
On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH=(Get-Location)
python -m src.main --artist "Ed Sheeran" --dataset "C:/data/unclaimedmusicalworkrightshares.tsv" --output "final_results.xlsx"
```
- Load the TSV dataset
- Fetch the artist catalog
- Cross-reference ISRCs
- Write `final_results.xlsx`

### Notes on Dataset
- Large datasets are not checked into git. Place your TSV at the path you set in `.env`.
- The loader attempts to detect the ISRC column; it expects a column named like `ISRC`.

### GitHub Publishing
- Ensure you have `gh` CLI installed and authenticated:
```bash
gh auth login
```
- Publish to GitHub as a new repo named `tritone-task`:
```bash
./scripts/github_publish.sh
```

### Error Handling
- Missing dataset or ISRC column: clear error message and non-zero exit.
- Spotify auth issues: clear error message.
- API retries: Spotipy client configured with retries and timeout.

### Deployment on Another Machine
- Install Python 3.10+
- Run `scripts/setup.sh`
- Create `.env` with credentials and dataset path
- Run `scripts/run.sh`

### Project Structure
```
src/
  config.py
  dataset_loader.py
  spotify_client.py
  cross_reference.py
  excel_export.py
  main.py
scripts/
  setup.sh
  run.sh
  github_publish.sh
requirements.txt
.env.example
```

### License
MIT
