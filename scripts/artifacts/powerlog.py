__artifacts_v2__ = {
    "powerlogApplicationRuntime": {
        "name": "PowerLog - Application Runtime",
        "description": "Application foreground and background runtime recorded by PowerLog "
                       "(PLAppTimeService_Aggregate_AppRunTime table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Raw PowerLog 'timestamp' values run on the log's internal clock, which can "
            "diverge from wall-clock time. The PLStorageOperator_EventForward_TimeOffset "
            "table records the correction in effect across the span of the log ('system' "
            "column, in seconds). Each row here is adjusted by the offset entry at or "
            "before its raw timestamp (rows older than the oldest retained entry use that "
            "oldest entry) and the applied offset is reported in its own column. Checked "
            "against test images: raw values lagged an iOS 18.7 acquisition date by ~32 "
            "days and led an iOS 12.4 acquisition by 69 seconds; corrected values align "
            "with the acquisition dates. ScreenOnTime/BackgroundTime read as seconds are "
            "consistent with the sampling-window durations in test data. PowerLog holds "
            "many additional version-specific tables that require separate validation; "
            "gzipped archive logs (*.PLSQL.gz) are not parsed."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4317 rows",
            "hickman_ios13": "iOS 13.3.1 | 2723 rows",
            "hickman_ios14": "iOS 14.3 | 4040 rows",
            "jess_ios15": "iOS 15.0.2 | 723 rows",
            "hickman_ios15": "iOS 15 | 3322 rows",
            "magnet_ios16": "iOS 16.1.1 | 933 rows",
            "abe_ios16": "iOS 16.5 | 7211 rows",
            "felix23_ios16": "iOS 16.5 | 2170 rows",
            "fsfull002_ios17": "iOS 17.1 | 1717 rows",
            "iphone11_ios17": "iOS 17.3 | 6235 rows",
            "otto_ios17": "iOS 17.5.1 | 2364 rows",
            "felix_ios17": "iOS 17.6.1 | 5662 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4127 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2425 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4244 rows",
            "hc_ios26": "iOS 26 | 3550 rows",
        },
    },
    "powerlogBatteryLevel": {
        "name": "PowerLog - Battery Level",
        "description": "Battery level and charging state samples recorded by PowerLog "
                       "(PLBatteryAgent_EventBackward_BatteryUI table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Level values ranged 1-100 across test images (iOS 12.4-26), consistent "
            "with a percentage. IsCharging holds 0/1, reported as No/Yes with other "
            "values passed through as stored. Timestamps are adjusted using PowerLog's "
            "time-offset table and the applied offset is reported per row; see the "
            "PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 3994 rows",
            "hickman_ios13": "iOS 13.3.1 | 1743 rows",
            "hickman_ios14": "iOS 14.3 | 1470 rows",
            "jess_ios15": "iOS 15.0.2 | 507 rows",
            "hickman_ios15": "iOS 15 | 1584 rows",
            "magnet_ios16": "iOS 16.1.1 | 210 rows",
            "abe_ios16": "iOS 16.5 | 1652 rows",
            "felix23_ios16": "iOS 16.5 | 530 rows",
            "fsfull002_ios17": "iOS 17.1 | 671 rows",
            "iphone11_ios17": "iOS 17.3 | 1585 rows",
            "otto_ios17": "iOS 17.5.1 | 5229 rows",
            "felix_ios17": "iOS 17.6.1 | 7115 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3165 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2117 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1527 rows",
            "hc_ios26": "iOS 26 | 810 rows",
        },
    },
    "powerlogDevicePowerState": {
        "name": "PowerLog - Device Power State",
        "description": "Device sleep and wake power state events recorded by PowerLog "
                       "(PLSleepWakeAgent_EventForward_PowerState table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Event, State, and Reason are integer codes reported as stored; their "
            "meanings are not decoded here. Observed in test images (iOS 12.4-26): "
            "State 0-2, Event 0-5, Reason 1 or null. Timestamps are adjusted using "
            "PowerLog's time-offset table and the applied offset is reported per row; "
            "see the PowerLog - Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "power",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 14721 rows",
            "hickman_ios13": "iOS 13.3.1 | 5893 rows",
            "hickman_ios14": "iOS 14.3 | 2762 rows",
            "jess_ios15": "iOS 15.0.2 | 75 rows",
            "hickman_ios15": "iOS 15 | 6242 rows",
            "magnet_ios16": "iOS 16.1.1 | 1472 rows",
            "abe_ios16": "iOS 16.5 | 2686 rows",
            "felix23_ios16": "iOS 16.5 | 1124 rows",
            "fsfull002_ios17": "iOS 17.1 | 664 rows",
            "iphone11_ios17": "iOS 17.3 | 2670 rows",
            "otto_ios17": "iOS 17.5.1 | 5809 rows",
            "felix_ios17": "iOS 17.6.1 | 509 rows",
            "iphone14plus_ios18": "iOS 18.0 | 832 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 1048 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1334 rows",
            "hc_ios26": "iOS 26 | 406 rows",
        },
    },
    "powerlogAppState": {
        "name": "PowerLog - Application State",
        "description": "Application state transition events recorded by PowerLog "
                       "(PLApplicationAgent_EventForward_Application table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "State and Reason are integer codes reported as stored; their meanings are "
            "not decoded here. Observed in test images (iOS 12.4-26): State 0, 1, 2, 4, "
            "8, 32; Reason 0 or 1. Timestamps are adjusted using PowerLog's time-offset "
            "table and the applied offset is reported per row; see the PowerLog - "
            "Application Runtime notes for the mechanism."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/[Pp]ower[Ll]og/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4292 rows",
            "hickman_ios13": "iOS 13.3.1 | 4743 rows",
            "hickman_ios14": "iOS 14.3 | 4590 rows",
            "jess_ios15": "iOS 15.0.2 | 324 rows",
            "hickman_ios15": "iOS 15 | 2916 rows",
            "magnet_ios16": "iOS 16.1.1 | 360 rows",
            "abe_ios16": "iOS 16.5 | 1775 rows",
            "felix23_ios16": "iOS 16.5 | 901 rows",
            "fsfull002_ios17": "iOS 17.1 | 550 rows",
            "iphone11_ios17": "iOS 17.3 | 5189 rows",
            "otto_ios17": "iOS 17.5.1 | 5404 rows",
            "felix_ios17": "iOS 17.6.1 | 2577 rows",
            "iphone14plus_ios18": "iOS 18.0 | 799 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 9604 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2023 rows",
            "hc_ios26": "iOS 26 | 1307 rows",
        },
    },
}

from bisect import bisect_right

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
)

TIME_OFFSET_TABLE = "PLStorageOperator_EventForward_TimeOffset"


def _powerlog_sources(context):
    """Plain .PLSQL files among the found paths, deduplicated.

    The path globs also surface -wal/-shm sidecars and gzipped archives; the
    sidecars ride along for SQLite to read, the .gz archives are not parsed.
    A file matched by more than one glob is returned once.
    """
    return list(dict.fromkeys(
        str(path) for path in context.get_files_found()
        if str(path).endswith(".PLSQL")
    ))


def _load_time_offsets(source_path):
    """Read the log's clock corrections as parallel timestamp-sorted lists.

    Returns ([raw timestamp], [offset seconds]); empty lists when the table
    is missing or holds no usable rows.
    """
    if not does_table_exist_in_db(source_path, TIME_OFFSET_TABLE):
        return [], []
    stamps = []
    offsets = []
    for row in get_sqlite_db_records(source_path, f'''
            SELECT timestamp, system
            FROM "{TIME_OFFSET_TABLE}"
            WHERE timestamp IS NOT NULL AND system IS NOT NULL
            ORDER BY timestamp
        '''):
        stamps.append(row[0])
        offsets.append(row[1])
    return stamps, offsets


def _corrected_utc(raw_ts, stamps, offsets):
    """Apply the clock correction in effect at raw_ts.

    Returns (aware datetime, applied offset in whole seconds). Rows older
    than the oldest retained offset entry use that oldest entry; a log with
    no offset entries gets the raw value back and no offset reported.
    """
    if raw_ts is None:
        return None, None
    if not stamps:
        return convert_unix_ts_to_utc(raw_ts), None
    idx = bisect_right(stamps, raw_ts) - 1
    if idx < 0:
        idx = 0
    offset = offsets[idx]
    return convert_unix_ts_to_utc(raw_ts + offset), int(round(offset))


def _parse_powerlog_table(context, table, columns, row_builder):
    """Run one query shape over every PowerLog db found.

    row_builder(corrected_ts, offset, row, relative_path) -> output tuple.
    """
    data_list = []
    source_paths = _powerlog_sources(context)
    for source_path in source_paths:
        if not does_table_exist_in_db(source_path, table):
            continue
        stamps, offsets = _load_time_offsets(source_path)
        relative_path = context.get_relative_path(source_path)
        for row in get_sqlite_db_records(source_path, f'''
                SELECT {", ".join(columns)}
                FROM "{table}"
                ORDER BY timestamp
            '''):
            ts, offset = _corrected_utc(row[0], stamps, offsets)
            data_list.append(row_builder(ts, offset, row, relative_path))
    source = "See source paths in data" if source_paths else ""
    return data_list, source


@artifact_processor
def powerlogApplicationRuntime(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Background Time (seconds)",
        "Screen-on Time (seconds)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLAppTimeService_Aggregate_AppRunTime",
        ("timestamp", "BundleID", "BackgroundTime", "ScreenOnTime"),
        lambda ts, offset, row, rel: (ts, row[1], row[2], row[3], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogBatteryLevel(context):
    data_headers = (
        ("Timestamp", "datetime"), "Battery Level (%)", "Is Charging",
        "Time Offset (seconds)", "Source File",
    )

    def build(ts, offset, row, rel):
        charging = {0: "No", 1: "Yes"}.get(row[2], row[2])
        return (ts, row[1], charging, offset, rel)

    data_list, source = _parse_powerlog_table(
        context, "PLBatteryAgent_EventBackward_BatteryUI",
        ("timestamp", "Level", "IsCharging"), build,
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogDevicePowerState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Event (as stored)", "State (as stored)",
        "Reason (as stored)", "UUID", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLSleepWakeAgent_EventForward_PowerState",
        ("timestamp", "Event", "State", "Reason", "UUID"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, data_list, source


@artifact_processor
def powerlogAppState(context):
    data_headers = (
        ("Timestamp", "datetime"), "Identifier", "PID", "State (as stored)",
        "Reason (as stored)", "Time Offset (seconds)", "Source File",
    )
    data_list, source = _parse_powerlog_table(
        context, "PLApplicationAgent_EventForward_Application",
        ("timestamp", "Identifier", "pid", "State", "Reason"),
        lambda ts, offset, row, rel: (
            ts, row[1], row[2], row[3], row[4], offset, rel),
    )
    return data_headers, data_list, source
