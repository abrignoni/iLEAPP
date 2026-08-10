__artifacts_v2__ = {
    "appleRecents": {
        "name": "Apple Recents",
        "description": "Recent interactions with Apple apps, contacts and addresses",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-28",
        "requirements": "none",
        "category": "User Activity",
        "notes": (
            "The Dates field may contain multiple comma-separated Unix timestamps in "
            "milliseconds. Parsed Dates preserves all valid values. Query adapted from "
            "https://github.com/kacos2000/Queries/blob/master/recents.sql"
        ),
        "paths": ("*/mobile/Library/Recents/Recents*",),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "history",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 19 rows",
            "hickman_ios15": "iOS 15 | 39 rows",
            "jess_ios15": "iOS 15.0.2 | 17 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 56 rows",
            "iphone14plus_ios18": "iOS 18.0 | 14 rows",
            "hc_ios18_7": "iOS 18.7.8 | 53 rows",
        },
    }
}

from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _parse_dates(value):
    parsed = []
    for item in str(value or "").split(","):
        try:
            parsed.append(datetime.fromtimestamp(float(item.strip()) / 1000, timezone.utc))
        except (ValueError, TypeError, OverflowError, OSError):
            continue
    return ", ".join(value.isoformat() for value in parsed)


@artifact_processor
def appleRecents(context):
    data_headers = (
        ("Last Date", "datetime"), "Parsed Dates (UTC)", "Dates (Raw)", "Recent ID",
        "Contact Kind", "Sending Address", "Contact Address", "Display Name",
        "Metadata Key", "Metadata Value", "Original Source", "Weight", "Record Hash",
        "Count", "Group Kind",
    )
    data_list = []
    source_path = next(
        (str(path) for path in context.get_files_found()
         if str(path).replace("\\", "/").endswith("/Recents/Recents")),
        "",
    )
    if not source_path:
        return data_headers, data_list, ""

    query = """
        SELECT datetime(recents.last_date / 1000, 'unixepoch'),
               recents.ROWID, contacts.kind, recents.sending_address, contacts.address,
               contacts.display_name, metadata.key, metadata.value, recents.original_source,
               recents.dates, recents.weight, recents.record_hash, recents.count,
               recents.group_kind
        FROM recents
        LEFT JOIN contacts ON recents.ROWID = contacts.recent_id
        LEFT JOIN metadata ON metadata.recent_id = recents.ROWID
        ORDER BY recents.last_date DESC
    """
    for row in get_sqlite_db_records(source_path, query):
        metadata_value = row[7]
        if isinstance(metadata_value, bytes):
            metadata_value = metadata_value.hex()
        data_list.append(
            (row[0], _parse_dates(row[9]), row[9]) + tuple(row[1:7])
            + (metadata_value, row[8]) + tuple(row[10:])
        )

    return data_headers, data_list, context.get_relative_path(source_path)
