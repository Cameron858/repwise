import logging
import sqlite3

import pandas as pd
from pyprojroot import here

from .gcloud import get_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ingest")

REQUIRED_COLUMNS = ["date", "exercise", "record"]
RECORD_PATTERN = r"(\d+)x(\d+)@(\d+(?:\.\d+)?)"
DB_PATH = here("db/repwise.db")


def process_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Validate and normalise a workout DataFrame."""
    logger.info(f"Processing {len(df)} rows of workout data")
    artifacts = {}
    df = df.copy()

    df.columns = df.columns.str.lower().str.strip()

    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Data must contain column {col!r}"
    logger.debug(f"All required columns present: {REQUIRED_COLUMNS}")

    if "notes" in df.columns:
        artifacts["notes"] = df[df["notes"].notna()].copy()
        logger.info(f"Extracted {len(artifacts['notes'])} rows with notes")
        df = df.drop(columns=["notes"])

    df["date"] = (
        pd.to_datetime(df["date"].replace("", pd.NA), errors="coerce", dayfirst=True)
        .ffill()
        .dt.strftime("%Y-%m-%d")
    )

    df["record"] = df["record"].str.strip(" ,").str.split(",")
    df = df.explode(column="record", ignore_index=True)
    df["record"] = df["record"].str.strip()

    artifacts["missed"] = df[df["record"].isna()].copy()
    logger.info(f"Found {len(artifacts['missed'])} missed records")
    df = df.dropna(subset=["record"])

    is_valid = df["record"].str.fullmatch(RECORD_PATTERN, na=False)
    artifacts["invalid"] = df[~is_valid].copy()
    logger.info(f"Found {len(artifacts['invalid'])} invalid records")
    df = df[is_valid].copy()

    df[["sets", "reps", "weight"]] = df["record"].str.extract(RECORD_PATTERN)
    df["sets"] = df["sets"].astype(int)
    df["reps"] = df["reps"].astype(int)
    df["weight"] = df["weight"].astype(float)
    df = df.drop(columns=["record"])

    df["order"] = df.groupby(["date", "exercise"]).cumcount() + 1
    logger.info(f"Successfully processed {len(df)} valid records")

    return df, artifacts


def create_db(db_path=DB_PATH):
    """Create the SQLite database schema if missing."""
    logger.info(f"Creating database schema at {db_path}")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.executescript(
            """
            DROP TABLE IF EXISTS staging;

            CREATE TABLE staging (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                "order" INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                "order" INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
            );
            """
        )
        logger.debug("Database schema created successfully")

    conn.close()


def populate_db(df: pd.DataFrame, db_path=DB_PATH):
    """Populate the database from a processed DataFrame."""
    logger.info(f"Populating database with {len(df)} entries")
    cols = ["date", "exercise", "sets", "reps", "weight", "order"]

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        cur.executescript("DELETE FROM staging;")
        logger.debug("Cleared staging table")

        cur.executemany(
            """
            INSERT INTO staging (date, exercise, sets, reps, weight, "order")
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            df[cols].to_records(index=False).tolist(),
        )
        logger.debug(f"Inserted {len(df)} records into staging table")

        cur.execute(
            """
            INSERT OR IGNORE INTO exercises (name)
            SELECT DISTINCT exercise FROM staging ORDER BY exercise
            """
        )
        logger.debug("Inserted exercises")

        cur.execute(
            """
            INSERT OR IGNORE INTO sessions (date)
            SELECT DISTINCT date FROM staging ORDER BY date
            """
        )
        logger.debug("Inserted sessions")

        cur.execute(
            """
            INSERT INTO entries (session_id, exercise_id, sets, reps, weight, "order")
            SELECT 
                s.id AS session_id,
                e.id AS exercise_id,
                st.sets,
                st.reps,
                st.weight,
                st."order"
            FROM staging st
            JOIN sessions s ON st.date = s.date
            JOIN exercises e ON st.exercise = e.name;
            """
        )
        logger.info(f"Successfully populated {cur.rowcount} entries into database")

    conn.close()


def ingest_pipeline():
    """Run the full ingestion pipeline."""

    logger.info("Starting ingest pipeline")

    try:
        logger.info("Fetching raw data from Google Sheets")
        raw_df = get_dataframe()
        logger.info(f"Retrieved {len(raw_df)} rows of raw data")

        processed_df, artifacts = process_data(raw_df)

        create_db()
        populate_db(processed_df)

        logger.info("Ingest pipeline completed successfully")
    except Exception as e:
        logger.error(f"Ingest pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    ingest_pipeline()
