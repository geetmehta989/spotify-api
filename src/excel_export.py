from __future__ import annotations

import pandas as pd


def export_to_excel(
    artist_catalog_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    notes: str,
    output_path: str,
) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        artist_catalog_df.to_excel(writer, index=False, sheet_name="Artist Catalog")
        matches_df.to_excel(writer, index=False, sheet_name="Matches")
        pd.DataFrame({"Notes": [notes]}).to_excel(writer, index=False, sheet_name="Notes")
