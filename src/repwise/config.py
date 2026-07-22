"""
Application configuration loaded from environment variables.
"""

import os


class Config:
    """Load required runtime settings from the environment."""

    def __init__(self) -> None:
        self._load_environment()

        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise RuntimeError("SPREADSHEET_ID environment variable is required")

        sheet_range = os.getenv("RANGE")
        if not sheet_range:
            raise RuntimeError("RANGE environment variable is required")

        self.spreadsheet_id = spreadsheet_id
        self.range = sheet_range

    def _load_environment(self) -> None:
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise RuntimeError(
                "python-dotenv is required to load environment variables from .env"
            ) from exc

        load_dotenv()


config = Config()

__all__ = ["config"]
