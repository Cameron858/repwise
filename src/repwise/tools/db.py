import json
import sqlite3

from pyprojroot import here

DB_PATH = here("db/repwise.db")
ALLOWED_TABLES = {"staging", "exercises", "sessions", "entries"}


def get_schema() -> str:
    """Returns the schema mapping each table to its list of PRAGMA table_info dicts as JSON.

    Args:
        db_path: Path to the SQLite database file. Defaults to db/repwise.db.

    Returns:
        A JSON string where keys are table names and values are lists of column info
        dictionaries, each containing column metadata (name, type, notnull, dflt_value, pk).
    """

    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

        schema = {
            row["name"]: [
                dict(col)
                for col in cur.execute(f"PRAGMA table_info('{row['name']}')").fetchall()
            ]
            for row in tables
        }

    conn.close()

    return json.dumps(schema)


def sample_table_data(table_name: str, limit: int = 5, offset: int = 0) -> dict:
    """Retrieve sample rows from a specific database table for inspection.

    Args:
        table_name: The target table name (e.g. 'exercises', 'sessions',
          'entries').
        limit: Max number of rows to return (default: 5, max: 20).
        offset: Number of rows to skip for pagination (default: 0).

    Returns:
        dict: Status containing table records or error message.
    """
    clean_table = table_name.lower().strip()
    if clean_table not in ALLOWED_TABLES:
        return {
            "status": "error",
            "message": f"Invalid table '{table_name}'. Allowed tables: {sorted(list(ALLOWED_TABLES))}",
        }

    safe_limit = max(1, min(limit, 20))
    safe_offset = max(0, offset)

    try:
        # Open in read-only mode using a URI connection string
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT * FROM {clean_table} LIMIT ? OFFSET ?"  # noqa: S608
            cursor.execute(query, (safe_limit, safe_offset))

        conn.close()

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
