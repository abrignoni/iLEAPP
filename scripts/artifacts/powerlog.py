__artifacts_v2__ = {
    "powerlogApplicationRuntime": {
        "name": "PowerLog - Application Runtime",
        "description": "Application foreground and background runtime recorded by PowerLog",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "PowerLog",
        "notes": (
            "Parses PLAppTimeService_Aggregate_AppRunTime. PowerLog contains many additional "
            "version-specific tables that require separate validation. "
            "Reference: Sarah Edwards, APOLLO powerlog_app_usage_by_hour module, "
            "https://github.com/mac4n6/APOLLO/blob/master/modules/powerlog_app_usage_by_hour.txt "
            "(SCREENONTIME/BACKGROUNDTIME in seconds)."
        ),
        "paths": (
            "*/BatteryLife/*.PLSQL*",
            "*/BatteryLife/Archives/*.PLSQL*",
            "*/Powerlog/*.PLSQL*",
            "*/PowerLog/*.PLSQL*",
            "*/powerlog/*.PLSQL*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1256 rows",
            "hickman_ios15": "iOS 15 | 3322 rows",
            "jess_ios15": "iOS 15.0.2 | 723 rows",
            "magnet_ios16": "iOS 16.1.1 | 933 rows",
            "felix_ios17": "iOS 17.6.1 | 5662 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4127 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4244 rows",
        },
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    does_table_exist_in_db,
    get_sqlite_db_records,
)


@artifact_processor
def powerlogApplicationRuntime(context):
    data_headers = (
        ("Timestamp", "datetime"), "Bundle ID", "Background Time (seconds)",
        "Screen-on Time (seconds)", "Source File",
    )
    data_list = []
    source_paths = [
        str(path) for path in context.get_files_found()
        if str(path).endswith(".PLSQL")
    ]
    for source_path in source_paths:
        if not does_table_exist_in_db(source_path, "PLAppTimeService_Aggregate_AppRunTime"):
            continue
        query = """
            SELECT datetime(timestamp, 'unixepoch'), BundleID, BackgroundTime, ScreenOnTime
            FROM PLAppTimeService_Aggregate_AppRunTime
            ORDER BY timestamp
        """
        relative_path = context.get_relative_path(source_path)
        data_list.extend(tuple(row) + (relative_path,)
                         for row in get_sqlite_db_records(source_path, query))

    source = "See source paths in data" if source_paths else ""
    return data_headers, data_list, source
