"""
Create a synthetic SQLite fixture for ArtifactResult performance testing.

The generated database intentionally includes narrow, medium, and wide tables
so benchmark runs can separate high-row-count behavior from wide-row behavior.
The data is deterministic and contains Unicode text to exercise serialization
without depending on real device extractions.
"""

import argparse
import sqlite3
from pathlib import Path


DEFAULT_OUTPUT = (
    Path("admin")
    / "test"
    / "perf_data"
    / "artifact_result_fixture"
)


def batched_rows(row_count, batch_size, row_factory):
    """Yield lists of generated rows for efficient SQLite inserts."""
    batch = []
    for index in range(row_count):
        batch.append(row_factory(index))
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def create_narrow_table(db, row_count, batch_size):
    db.execute(
        """
        CREATE TABLE perf_narrow (
            id INTEGER PRIMARY KEY,
            event_ts INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            item_value TEXT NOT NULL
        )
        """
    )

    def row_factory(index):
        return (
            index,
            1700000000 + index,
            f"key-{index % 1000:04d}",
            f"value-{index:08d}",
        )

    for batch in batched_rows(row_count, batch_size, row_factory):
        db.executemany("INSERT INTO perf_narrow VALUES (?, ?, ?, ?)", batch)


def create_medium_table(db, row_count, batch_size):
    db.execute(
        """
        CREATE TABLE perf_medium (
            id INTEGER PRIMARY KEY,
            event_ts INTEGER NOT NULL,
            bundle_id TEXT NOT NULL,
            item_path TEXT NOT NULL,
            event_type TEXT NOT NULL,
            flag INTEGER NOT NULL,
            score REAL NOT NULL,
            note TEXT NOT NULL,
            source_file TEXT NOT NULL
        )
        """
    )

    def row_factory(index):
        return (
            index,
            1700000000 + (index * 3),
            f"com.example.app{index % 250:03d}",
            f"/private/var/mobile/Containers/Data/Application/{index % 500:04d}/file-{index}.dat",
            ("create", "update", "delete", "visit")[index % 4],
            index % 2,
            round((index % 10000) / 17.0, 4),
            f"medium row {index} unicode snowman \u2603",
            "leapp_perf_artifact_result.sqlite",
        )

    for batch in batched_rows(row_count, batch_size, row_factory):
        db.executemany(
            "INSERT INTO perf_medium VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            batch,
        )


def create_wide_table(db, row_count, batch_size, wide_columns):
    column_defs = ",\n            ".join(
        f"c{number:03d} TEXT NOT NULL" for number in range(1, wide_columns + 1)
    )
    db.execute(
        f"""
        CREATE TABLE perf_wide (
            id INTEGER PRIMARY KEY,
            {column_defs}
        )
        """
    )

    placeholders = ", ".join("?" for _ in range(wide_columns + 1))

    def row_factory(index):
        values = [index]
        for number in range(1, wide_columns + 1):
            values.append(
                f"row={index:08d};column={number:03d};payload=abcdefghijklmnopqrstuvwxyz0123456789"
            )
        return tuple(values)

    for batch in batched_rows(row_count, batch_size, row_factory):
        db.executemany(f"INSERT INTO perf_wide VALUES ({placeholders})", batch)


def write_metadata(db, narrow_rows, medium_rows, wide_rows, wide_columns):
    db.execute(
        """
        CREATE TABLE perf_metadata (
            name TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    db.executemany(
        "INSERT INTO perf_metadata VALUES (?, ?)",
        (
            ("narrow_rows", str(narrow_rows)),
            ("medium_rows", str(medium_rows)),
            ("wide_rows", str(wide_rows)),
            ("wide_columns", str(wide_columns)),
        ),
    )


def create_database(output_path, narrow_rows, medium_rows, wide_rows, wide_columns, batch_size):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with sqlite3.connect(output_path) as db:
        db.execute("PRAGMA journal_mode = OFF")
        db.execute("PRAGMA synchronous = OFF")
        db.execute("PRAGMA temp_store = MEMORY")
        create_narrow_table(db, narrow_rows, batch_size)
        create_medium_table(db, medium_rows, batch_size)
        create_wide_table(db, wide_rows, batch_size, wide_columns)
        write_metadata(db, narrow_rows, medium_rows, wide_rows, wide_columns)
        db.commit()
        db.execute("VACUUM")


def main():
    parser = argparse.ArgumentParser(
        description="Create a synthetic SQLite fixture for iLEAPP performance testing."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--narrow-rows", type=int, default=50000)
    parser.add_argument("--medium-rows", type=int, default=20000)
    parser.add_argument("--wide-rows", type=int, default=5000)
    parser.add_argument("--wide-columns", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    create_database(
        args.output,
        args.narrow_rows,
        args.medium_rows,
        args.wide_rows,
        args.wide_columns,
        args.batch_size,
    )
    print(f"Created {args.output}")
    print(
        "Rows: "
        f"narrow={args.narrow_rows}, "
        f"medium={args.medium_rows}, "
        f"wide={args.wide_rows}, "
        f"wide_columns={args.wide_columns}"
    )


if __name__ == "__main__":
    main()
