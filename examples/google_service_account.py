"""
Read a Google Sheets worksheet into a pandas DataFrame.
Mainly followed from `https://developers.google.com/workspace/sheets/api/quickstart/python`
"""

from pathlib import Path

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pyprojroot import here

SPREADSHEET_ID = "1umi2ExhzsNmPXrEmWHLIhFz9U7w_cjAQco6pcPIR4zY"
RANGE = "records!A:D"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def load_sheet_data(spreadsheet_id: str, range_name: str = RANGE) -> pd.DataFrame:
    """Load worksheet values from Google Sheets into a DataFrame."""
    credential_path = Path(here("credentials/credentials.json"))
    if not credential_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credential_path}")

    creds = Credentials.from_service_account_file(
        str(credential_path),
        scopes=SCOPES,
    )

    service = build("sheets", "v4", credentials=creds)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )

    values = result.get("values", [])
    if not values:
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]
    return pd.DataFrame(rows, columns=header)


def main() -> None:
    df = load_sheet_data(SPREADSHEET_ID)
    print(df.head())


if __name__ == "__main__":
    main()
