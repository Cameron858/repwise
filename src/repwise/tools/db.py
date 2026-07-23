import sqlite3
from contextlib import closing

from pyprojroot import here

DB_PATH = here("db/repwise.db")
ALLOWED_TABLES = {"staging", "exercises", "sessions", "entries"}


def get_schema() -> dict:
    """Returns the schema mapping each table to its list of PRAGMA table_info dicts as JSON.

    Args:
        db_path: Path to the SQLite database file. Defaults to db/repwise.db.

    Returns:
        A dict where keys are table names and values are lists of column info
        dictionaries, each containing column metadata (name, type, notnull, dflt_value, pk).
    """
    try:
        with closing(sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            tables = cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()

            schema = {
                row["name"]: [
                    dict(col)
                    for col in cur.execute(
                        f"PRAGMA table_info('{row['name']}')"
                    ).fetchall()
                ]
                for row in tables
            }

        return {"status": "success", **schema}
    except Exception as e:
        return {"status": "error", "message": f"Database query failed: {e!s}"}


def sample_table_data(
    table_name: str,
    limit: int = 5,
    offset: int = 0,
    order_by: str | None = None,
    desc: bool = True,
) -> dict:
    """Retrieve sample rows from a specific database table for inspection.

    Args:
        table_name: Target table ('exercises', 'sessions', 'entries', etc.).
        limit: Max number of rows to return (default: 5, max: 20).
        offset: Number of rows to skip for pagination (default: 0).
        order_by: Optional column name to sort by (e.g., 'date', 'id').
        desc: Sort in descending order if True (default: True).
    """
    clean_table = table_name.lower().strip()
    if clean_table not in ALLOWED_TABLES:
        return {
            "status": "error",
            "message": f"Invalid table '{table_name}'. Allowed tables: {sorted(list(ALLOWED_TABLES))}",
        }

    safe_limit = max(1, min(limit, 20))
    safe_offset = max(0, offset)

    # Default to date DESC for sessions if no order column is explicitly provided
    if clean_table == "sessions" and order_by is None:
        order_by = "date"

    order_clause = ""
    if order_by:
        clean_order = "".join(c for c in order_by if c.isalnum() or c == "_")
        direction = "DESC" if desc else "ASC"
        order_clause = f" ORDER BY {clean_order} {direction}, id DESC"

    try:
        with closing(sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT * FROM {clean_table}{order_clause} LIMIT ? OFFSET ?"  # noqa: S608
            cursor.execute(query, (safe_limit, safe_offset))

            data = [dict(row) for row in cursor.fetchall()]
            return {
                "status": "success",
                "table": clean_table,
                "count": len(data),
                "offset": safe_offset,
                "data": data,
            }
    except Exception as e:
        return {"status": "error", "message": f"Database query failed: {e!s}"}


def get_exercise_history(exercise_name: str, limit: int = 20) -> dict:
    """Returns chronological history of a specific exercise.

    Args:
        exercise_name: The name of the exercise to retrieve history for.
        limit: Maximum number of historical records to return (default: 20).

    Returns:
        A dict containing exercise history with dates, weights, reps, and sets,
        ordered chronologically from oldest to newest.
    """
    raise NotImplementedError


def get_session_details(date: str) -> dict:
    """Returns all exercises performed on a specific date.

    Args:
        date: The session date in YYYY-MM-DD format.

    Returns:
        A dict containing all exercises from that session with their stats
        (sets, reps, weight, order).
    """
    raise NotImplementedError


def get_personal_records() -> dict:
    """Returns the maximum weight achieved for each exercise.

    Returns:
        A dict mapping exercise names to their personal record (max weight)
        and the date it was achieved.
    """
    raise NotImplementedError


def get_recent_workouts(days: int = 30) -> dict:
    """Returns unique session dates and exercise count in the last N days.

    Args:
        days: Number of past days to analyse (default: 30).

    Returns:
        A dict containing recent workout sessions with counts and frequency metrics.
    """
    raise NotImplementedError


def get_exercise_stats(exercise_name: str) -> dict:
    """Aggregates statistics for a specific exercise.

    Args:
        exercise_name: The name of the exercise to analyse.

    Returns:
        A dict containing: average weight, max reps, total volume,
        session count, and date range.
    """
    raise NotImplementedError


def get_progress_metrics(exercise_name: str, start_date: str, end_date: str) -> dict:
    """Calculates progress for an exercise between two dates.

    Args:
        exercise_name: The name of the exercise to track.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A dict containing weight increase, rep increase, volume change,
        and percentage improvements.
    """
    raise NotImplementedError


def list_all_exercises() -> dict:
    """Returns a normalised list of all exercises in the database.

    Returns:
        A dict containing all unique exercise names from the exercises table.
    """
    raise NotImplementedError


def get_workout_frequency(start_date: str, end_date: str) -> dict:
    """Analyses workout frequency between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A dict containing days trained, rest days, average gap between sessions,
        and workout frequency metrics.
    """
    raise NotImplementedError
