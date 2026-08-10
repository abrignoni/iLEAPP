__artifacts_v2__ = {
    "personalizationPortraitLocations": {
        "name": "Personalization Portrait - Locations",
        "description": "Locations aggregated for Apple's personalization features",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-28",
        "requirements": "none",
        "category": "Locations",
        "notes": (
            "Aggregated locations are not proof that the device visited a place; the source "
            "bundle and group provide essential attribution context. Based on research by "
            "Sarah Edwards: https://www.mac4n6.com/blog/2020/6/2/guest-post-by-bizzybarney-"
            "a-peek-inside-the-ppsqldatabasedb-personalization-portrait-database"
        ),
        "paths": (
            "*/mobile/Library/PersonalizationPortrait/PPSQLDatabase.db*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "map",
        "sample_data": {
            "hickman_ios15": "iOS 15 | 169 rows",
            "jess_ios15": "iOS 15.0.2 | 16 rows",
            "magnet_ios16": "iOS 16.1.1 | 20 rows",
            "felix_ios17": "iOS 17.6.1 | 76 rows",
            "iphone14plus_ios18": "iOS 18.0 | 664 rows",
            "hc_ios18_7": "iOS 18.7.8 | 726 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def personalizationPortraitLocations(context):
    data_headers = (
        ("Source Time", "datetime"), "Location ID", "Bundle ID", "Group ID",
        ("Latitude", "latitude"), ("Longitude", "longitude"), "Name", "Road", "Street Number",
        "City", "Sub-locality", "Administrative Area", "Sub-administrative Area", "Postal Code",
        "Country Code", "Country", "iOS Build", "Category", "Algorithm", "Initial Score",
        "Sync Eligible",
    )
    data_list = []
    source_path = next(
        (str(path) for path in context.get_files_found()
         if str(path).endswith("PPSQLDatabase.db")),
        "",
    )
    if not source_path:
        return data_headers, data_list, ""

    query = """
        SELECT datetime(sources.seconds_from_1970, 'unixepoch'),
               loc_records.id, sources.bundle_id, sources.group_id,
               loc_records.cll_latitude_degrees, loc_records.cll_longitude_degrees,
               loc_records.clp_name, loc_records.clp_thoroughfare,
               loc_records.clp_subThoroughfare, loc_records.clp_locality,
               loc_records.clp_subLocality, loc_records.clp_administrativeArea,
               loc_records.clp_subAdministrativeArea, loc_records.clp_postalCode,
               loc_records.clp_ISOcountryCode, loc_records.clp_country,
               loc_records.extraction_os_build, loc_records.category, loc_records.algorithm,
               loc_records.initial_score,
               CASE loc_records.is_sync_eligible WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' END
        FROM loc_records
        LEFT JOIN sources ON loc_records.source_id = sources.id
        ORDER BY sources.seconds_from_1970
    """
    data_list.extend(tuple(row) for row in get_sqlite_db_records(source_path, query))
    return data_headers, data_list, context.get_relative_path(source_path)
