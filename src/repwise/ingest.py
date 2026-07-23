import sqlite3

import pandas as pd
from pyprojroot import here

from .gcloud import get_dataframe

REQUIRED_COLUMNS = ["date", "exercise", "record"]
RECORD_PATTERN = r"(\d+)x(\d+)@(\d+(?:\.\d+)?)"

ARTIFACTS = {}
DB_PATH = here("db/repwise.db")


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalise a workout DataFrame.

    Ensures required columns are present, explodes the `record` column into
    separate rows, extracts `sets`, `reps`, and `weight`, and returns a
    cleaned DataFrame ready for database insertion.
    """
    global ARTIFACTS

    df = df.copy()

    # pre-process
    df.columns = df.columns.str.lower().str.strip()

    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Data must contain column {col!r}"

    if "notes" in df.columns:
        notes = df.copy()
        ARTIFACTS["notes"] = notes
        df = df.drop(columns=["notes"])

    # Format datetime
    df["date"] = pd.to_datetime(
        df["date"].replace("", pd.NA), errors="coerce", dayfirst=True
    )
    df["date"] = df["date"].ffill()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Explode the record columns
    df["record"] = df["record"].str.strip(" ,").str.split(",")
    df = df.explode(column="record", ignore_index=True)
    df["record"] = df["record"].str.strip()

    # Extract the NaN records
    missed = df[df["record"].isna()].copy()
    ARTIFACTS["missed"] = missed

    df = df.dropna()

    assert not df.isna().sum().sum(), "Data still contains NaN values"

    # Extract the records that do not match the pattern
    invalid = df.loc[~df["record"].str.fullmatch(RECORD_PATTERN, na=False)]
    ARTIFACTS["invalid"] = invalid

    # Assert that all records now match the pattern
    df = df.loc[df["record"].str.fullmatch(RECORD_PATTERN, na=False)]
    assert df.loc[~df["record"].str.fullmatch(RECORD_PATTERN, na=False)].empty, (
        f"Found {len(invalid)} invalid Record values:\n{invalid}"
    )

    # Extract sets, reps, weight
    df[["sets", "reps", "weight"]] = df["record"].str.extract(RECORD_PATTERN)

    # Explicitly convert
    df["sets"] = df["sets"].astype(int)
    df["reps"] = df["reps"].astype(int)
    df["weight"] = df["weight"].astype(float)

    df = df.drop(columns=["record"], errors="ignore")

    # Add order
    df["order"] = df.groupby(["date", "exercise"]).cumcount() + 1

    return df


def create_db(db_path=DB_PATH):
    """Create the SQLite database schema if missing.

    Creates `staging`, `exercises`, `sessions`, and `entries` tables at
    the given `db_path`. Foreign keys are enabled for `entries`.
    """
    # Staging
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS staging")
        cur.execute(
            """
            CREATE TABLE staging (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL NOT NULL,
                "order" INTEGER NOT NULL
            );
            """
        )

    # Exercises
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY NOT NULL,
                name TEXT UNIQUE NOT NULL
            )
            """
        )

    # Sessions
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY NOT NULL,
                date TEXT UNIQUE NOT NULL
            )
            """
        )

    # Entries
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Enable Foreign Key support in SQLite (disabled by default)
        cur.execute("PRAGMA foreign_keys = ON;")

        cur.execute(
            """
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


def populate_db(df: pd.DataFrame, db_path=DB_PATH):
    """Populate the database from a processed DataFrame.

    Inserts processed rows into `staging`, upserts distinct exercises and
    session dates, then inserts resolved rows into the `entries` table.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Insert using explicit column names, passing only required DataFrame columns
        cols = ["date", "exercise", "sets", "reps", "weight", "order"]
        cur.executemany(
            "INSERT INTO staging ('date', 'exercise', 'sets', 'reps', 'weight', 'order') VALUES (?, ?, ?, ?, ?, ?)",
            df[cols].to_numpy(),
        )

        exercises = cur.execute(
            "SELECT DISTINCT exercise FROM staging ORDER BY exercise"
        ).fetchall()
        cur.executemany(
            "INSERT OR IGNORE INTO exercises (name) VALUES(?)",
            [e for e in exercises],
        )

        dates = cur.execute(
            "SELECT DISTINCT date FROM staging ORDER BY date"
        ).fetchall()
        cur.executemany(
            "INSERT OR IGNORE INTO sessions (date) VALUES(?)",
            [d for d in dates],
        )

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


def ingest_pipeline():
    """Run the full ingestion pipeline.

    Fetches a DataFrame via `get_dataframe()`, processes the data,
    creates the database schema, and populates the database.
    """
    df = get_dataframe()
    df = process_data(df)

    create_db()
    populate_db(df)


if __name__ == "__main__":
    ingest_pipeline()
