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
