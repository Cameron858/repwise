import json
import sqlite3

from pyprojroot import here


def get_schema(db_path=None) -> str:
    """Returns the schema mapping each table to its list of PRAGMA table_info dicts as JSON.

    Args:
        db_path: Path to the SQLite database file. Defaults to db/repwise.db.

    Returns:
        A JSON string where keys are table names and values are lists of column info
        dictionaries, each containing column metadata (name, type, notnull, dflt_value, pk).
    """
    if db_path is None:
        db_path = here("db/repwise.db")

    with sqlite3.connect(db_path) as conn:
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

        return json.dumps(schema)
