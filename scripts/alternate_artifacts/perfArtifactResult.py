"""Synthetic artifacts for comparing legacy list output with ArtifactResult."""

from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc


PERF_DB_NAME = "leapp_perf_artifact_result.sqlite"
PERF_DB_PATH = f"*/{PERF_DB_NAME}"


def _source_path(context):
    return get_file_path(context.get_files_found(), PERF_DB_PATH)


def _row_count(source_path, table_name):
    records = get_sqlite_db_records(source_path, f"SELECT COUNT(*) FROM {table_name}")
    for record in records:
        return record[0]
    return None


def _datetime_from_unix(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def _narrow_rows(source_path):
    query = "SELECT id, event_ts, item_key, item_value FROM perf_narrow ORDER BY id"
    for record in get_sqlite_db_records(source_path, query):
        yield (
            record["id"],
            _datetime_from_unix(record["event_ts"]),
            record["item_key"],
            record["item_value"],
        )


def _medium_rows(source_path):
    query = """
    SELECT id, event_ts, bundle_id, item_path, event_type, flag, score, note, source_file
    FROM perf_medium
    ORDER BY id
    """
    for record in get_sqlite_db_records(source_path, query):
        yield (
            record["id"],
            _datetime_from_unix(record["event_ts"]),
            record["bundle_id"],
            record["item_path"],
            record["event_type"].upper(),
            record["flag"],
            record["score"],
            record["note"],
            record["source_file"],
            "Enabled" if record["flag"] else "Disabled",
        )


NARROW_HEADERS = (
    "ID",
    ("Event Time", "datetime"),
    "Item Key",
    "Item Value",
)

MEDIUM_HEADERS = (
    "ID",
    ("Event Time", "datetime"),
    "Bundle ID",
    "Item Path",
    "Event Type",
    "Flag",
    "Score",
    "Note",
    "Source File",
    "Readable Flag",
)


def _wide_headers():
    return ("ID",) + tuple(f"Column {number:03d}" for number in range(1, 81))


__artifacts_v2__ = {
    "perf_narrow_legacy_list": {
        "name": "Performance - Narrow Legacy List",
        "description": "Synthetic narrow rows returned as a normal in-memory list",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for ArtifactResult benchmark baselines.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_narrow_artifact_result": {
        "name": "Performance - Narrow ArtifactResult",
        "description": "Synthetic narrow rows returned through ArtifactResult",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for ArtifactResult benchmark comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_narrow_artifact_result_sync": {
        "name": "Performance - Narrow ArtifactResult Sync",
        "description": "Synthetic narrow rows streamed through ArtifactResult without async LAVA writes",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for synchronous ArtifactResult benchmark comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_medium_legacy_transform": {
        "name": "Performance - Medium Legacy Transform",
        "description": "Synthetic transformed rows returned as a normal in-memory list",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for transformed-row benchmark baselines.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_medium_artifact_result_transform": {
        "name": "Performance - Medium ArtifactResult Transform",
        "description": "Synthetic transformed rows returned through ArtifactResult",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for transformed-row ArtifactResult comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_medium_artifact_result_transform_sync": {
        "name": "Performance - Medium ArtifactResult Transform Sync",
        "description": "Synthetic transformed rows streamed through ArtifactResult without async LAVA writes",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for synchronous transformed-row ArtifactResult comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_wide_legacy_list": {
        "name": "Performance - Wide Legacy List",
        "description": "Synthetic wide rows returned as a normal in-memory list",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for wide-row benchmark baselines.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_wide_artifact_result_cursor": {
        "name": "Performance - Wide ArtifactResult Cursor",
        "description": "Synthetic wide rows returned through ArtifactResult from a SQLite cursor",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for direct cursor ArtifactResult comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
    "perf_wide_artifact_result_cursor_sync": {
        "name": "Performance - Wide ArtifactResult Cursor Sync",
        "description": "Synthetic wide rows streamed through ArtifactResult from a SQLite cursor without async LAVA writes",
        "author": "LEAPP",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-07-24",
        "requirements": "none",
        "category": "Performance Testing",
        "notes": "Developer-only alternate artifact for synchronous direct cursor ArtifactResult comparisons.",
        "paths": (PERF_DB_PATH,),
        "output_types": "lava_only",
        "artifact_icon": "activity",
        "sample_data": {"synthetic": "configurable row count"},
    },
}


@artifact_processor
def perf_narrow_legacy_list(context):
    source_path = _source_path(context)
    data_list = []
    if not source_path:
        logfunc(f"{PERF_DB_NAME} not found")
        return NARROW_HEADERS, data_list, source_path

    query = "SELECT id, event_ts, item_key, item_value FROM perf_narrow ORDER BY id"
    for record in get_sqlite_db_records(source_path, query):
        data_list.append(
            (
                record["id"],
                _datetime_from_unix(record["event_ts"]),
                record["item_key"],
                record["item_value"],
            )
        )
    return NARROW_HEADERS, data_list, source_path


@artifact_processor
def perf_narrow_artifact_result(context):
    return _perf_narrow_artifact_result(context, async_write=True, label="perf_narrow_artifact_result")


@artifact_processor
def perf_narrow_artifact_result_sync(context):
    return _perf_narrow_artifact_result(context, async_write=False, label="perf_narrow_artifact_result_sync")


def _perf_narrow_artifact_result(context, async_write, label):
    source_path = _source_path(context)
    result = context.create_artifact_result(
        headers=NARROW_HEADERS,
        source_path=source_path,
        estimated_row_count=_row_count(source_path, "perf_narrow") if source_path else None,
        rows=_narrow_rows(source_path) if source_path else None,
        async_write=async_write,
        label=label,
    )
    if not source_path:
        logfunc(f"{PERF_DB_NAME} not found")
    return result


@artifact_processor
def perf_medium_legacy_transform(context):
    source_path = _source_path(context)
    data_list = []
    if not source_path:
        logfunc(f"{PERF_DB_NAME} not found")
        return MEDIUM_HEADERS, data_list, source_path

    query = """
    SELECT id, event_ts, bundle_id, item_path, event_type, flag, score, note, source_file
    FROM perf_medium
    ORDER BY id
    """
    for record in get_sqlite_db_records(source_path, query):
        data_list.append(
            (
                record["id"],
                _datetime_from_unix(record["event_ts"]),
                record["bundle_id"],
                record["item_path"],
                record["event_type"].upper(),
                record["flag"],
                record["score"],
                record["note"],
                record["source_file"],
                "Enabled" if record["flag"] else "Disabled",
            )
        )
    return MEDIUM_HEADERS, data_list, source_path


@artifact_processor
def perf_medium_artifact_result_transform(context):
    return _perf_medium_artifact_result_transform(
        context,
        async_write=True,
        label="perf_medium_artifact_result_transform",
    )


@artifact_processor
def perf_medium_artifact_result_transform_sync(context):
    return _perf_medium_artifact_result_transform(
        context,
        async_write=False,
        label="perf_medium_artifact_result_transform_sync",
    )


def _perf_medium_artifact_result_transform(context, async_write, label):
    source_path = _source_path(context)
    result = context.create_artifact_result(
        headers=MEDIUM_HEADERS,
        source_path=source_path,
        estimated_row_count=_row_count(source_path, "perf_medium") if source_path else None,
        rows=_medium_rows(source_path) if source_path else None,
        async_write=async_write,
        label=label,
    )
    if not source_path:
        logfunc(f"{PERF_DB_NAME} not found")
    return result


@artifact_processor
def perf_wide_legacy_list(context):
    source_path = _source_path(context)
    data_list = []
    if not source_path:
        logfunc(f"{PERF_DB_NAME} not found")
        return _wide_headers(), data_list, source_path

    columns = ", ".join(f"c{number:03d}" for number in range(1, 81))
    query = f"SELECT id, {columns} FROM perf_wide ORDER BY id"
    for record in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(record))
    return _wide_headers(), data_list, source_path


@artifact_processor
def perf_wide_artifact_result_cursor(context):
    return _perf_wide_artifact_result_cursor(
        context,
        async_write=True,
        label="perf_wide_artifact_result_cursor",
    )


@artifact_processor
def perf_wide_artifact_result_cursor_sync(context):
    return _perf_wide_artifact_result_cursor(
        context,
        async_write=False,
        label="perf_wide_artifact_result_cursor_sync",
    )


def _perf_wide_artifact_result_cursor(context, async_write, label):
    source_path = _source_path(context)
    if not source_path:
        result = context.create_artifact_result(
            headers=_wide_headers(),
            source_path=source_path,
            label=label,
        )
        logfunc(f"{PERF_DB_NAME} not found")
        return result

    columns = ", ".join(f"c{number:03d}" for number in range(1, 81))
    query = f"SELECT id, {columns} FROM perf_wide ORDER BY id"
    cursor = get_sqlite_db_records(source_path, query)
    return context.create_artifact_result(
        headers=_wide_headers(),
        source_path=source_path,
        estimated_row_count=_row_count(source_path, "perf_wide"),
        rows=cursor,
        async_write=async_write,
        label=label,
    )
