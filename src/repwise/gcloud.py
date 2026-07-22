"""
Helpers for reading Google Sheets data into pandas DataFrames.
"""

from pathlib import Path

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pyprojroot import here

from .config import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_dataframe(
    spreadsheet_id: str | None = None,
    range_name: str | None = None,
) -> pd.DataFrame:
    """Return a Google Sheet as a pandas DataFrame."""
    sheet_id = spreadsheet_id or config.spreadsheet_id
    selected_range = range_name or config.range

    credential_path = Path(here("credentials/credentials.json"))
    if not credential_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credential_path}")

    credentials = Credentials.from_service_account_file(
        str(credential_path),
        scopes=SCOPES,
    )

    service = build("sheets", "v4", credentials=credentials)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=selected_range)
        .execute()
    )

    values = result.get("values", [])
    if not values:
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]
    return pd.DataFrame(rows, columns=header)
