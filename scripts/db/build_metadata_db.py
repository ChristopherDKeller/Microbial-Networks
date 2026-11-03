
from pathlib import Path

import duckdb

# Paths
TSV_PATH = Path(
    "data/raw/AGP-sample-information/10317_20261015-100021.txt"
)
DB_PATH = Path("data/AGP-metadata.duckdb")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

if not TSV_PATH.exists():
    raise FileNotFoundError(f"Metadata file not found: {TSV_PATH}")

# Persistent database: existing database is reused.
con = duckdb.connect(str(DB_PATH))

try:
    # Import all columns as text to preserve metadata values.
    # A unique sentinel prevents ordinary empty strings from being
    # interpreted as SQL NULL during import.
    con.execute(
        """
        CREATE OR REPLACE TABLE agp_metadata AS
        SELECT *
        FROM read_csv(
            ?,
            delim = '\\t',
            header = true,
            all_varchar = true,
            nullstr = '__DUCKDB_NULL_SENTINEL_92817__'
        )
        """,
        [str(TSV_PATH.resolve())],
    )

    print("Database created:", DB_PATH.resolve())
    print("Rows:", con.execute(
        "SELECT COUNT(*) FROM agp_metadata"
    ).fetchone()[0])

    print("Columns:")
    print(con.execute("DESCRIBE agp_metadata").df())

finally:
    con.close()
