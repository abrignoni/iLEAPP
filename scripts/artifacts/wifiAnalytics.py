__artifacts_v2__ = {
    "wifiAnalyticsGeotags": {
        "name": "Wi-Fi Analytics - Geotags",
        "description": "Geotagged Wi-Fi networks recorded by wifianalyticsd",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-28",
        "requirements": "none",
        "category": "Wi-Fi",
        "notes": "Dates use the Apple Cocoa epoch. Locations should be corroborated.",
        "paths": (
            "*/root/Library/Application Support/com.apple.wifianalyticsd/"
            "DeviceAnalyticsModel.sqlite*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hickman_ios15": "iOS 15 | 9 rows",
            "jess_ios15": "iOS 15.0.2 | 17 rows",
            "magnet_ios16": "iOS 16.1.1 | 14 rows",
            "felix_ios17": "iOS 17.6.1 | 15 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def wifiAnalyticsGeotags(context):
    data_headers = (
        ("Date", "datetime"), ("Last Seen", "datetime"), "Geotag ID", "Entity ID",
        ("Latitude", "latitude"), ("Longitude", "longitude"), "BSSID", "SSID",
    )
    data_list = []
    source_path = next(
        (str(path) for path in context.get_files_found()
         if str(path).endswith("DeviceAnalyticsModel.sqlite")),
        "",
    )
    if not source_path:
        return data_headers, data_list, ""

    query = """
        SELECT datetime(ZGEOTAG.ZDATE + 978307200, 'unixepoch'),
               datetime(ZBSS.ZLASTSEEN + 978307200, 'unixepoch'),
               ZGEOTAG.Z_PK, ZGEOTAG.Z_ENT,
               ZGEOTAG.ZLATITUDE, ZGEOTAG.ZLONGITUDE, ZBSS.ZBSSID, ZNETWORK.ZSSID
        FROM ZGEOTAG
        LEFT JOIN ZBSS ON ZBSS.Z_PK = ZGEOTAG.ZBSS
        LEFT JOIN ZNETWORK ON ZNETWORK.Z_PK = ZBSS.ZNETWORK
        ORDER BY ZGEOTAG.ZDATE
    """
    data_list.extend(tuple(row) for row in get_sqlite_db_records(source_path, query))
    return data_headers, data_list, context.get_relative_path(source_path)
