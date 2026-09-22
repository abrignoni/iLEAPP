__artifacts_v2__ = {
    "personalizationPortraitLocations": {
        "name": "Personalization Portrait - Locations",
        "description": (
            "Location records from PPSQLDatabase.db, with the bundle ID and, where recorded, the "
            "group ID of the source each record references"
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Locations",
        "notes": (
            "A location record is not proof that the device was at that place. The cited "
            "research describes this database as aggregating data from many sources and says "
            "attribution must be done carefully. Bundle ID, Group ID and Source Time are read "
            "from the sources row that each record's source_id references; Source Time is that "
            "row's seconds_from_1970 value, read as Unix epoch seconds, and what it marks is not "
            "established here. Latitude and Longitude can be blank, and a record missing either "
            "is left out of the KML output. Reference: @bizzybarney, 'A Peek Inside the "
            "PPSQLDatabase.db Personalization Portrait Database', guest post on mac4n6.com, "
            "https://www.mac4n6.com/blog/2020/6/2/guest-post-by-bizzybarney-"
            "a-peek-inside-the-ppsqldatabasedb-personalization-portrait-database"
        ),
        "paths": (
            "*/mobile/Library/PersonalizationPortrait/PPSQLDatabase.db*",
        ),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "map",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 169 rows",
            "jess_ios15": "iOS 15.0.2 | 16 rows",
            "magnet_ios16": "iOS 16.1.1 | 20 rows",
            "felix_ios17": "iOS 17.6.1 | 76 rows",
            "iphone14plus_ios18": "iOS 18.0 | 664 rows",
            "hc_ios18_7": "iOS 18.7.8 | 726 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records


@artifact_processor
def personalizationPortraitLocations(context):
    data_headers = (
        ("Source Time", "datetime"), "Location ID", "Bundle ID", "Group ID",
        "Latitude", "Longitude", "Name", "Road", "Street Number",
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
        SELECT sources.seconds_from_1970,
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
    for row in get_sqlite_db_records(source_path, query):
        values = tuple(row)
        data_list.append((convert_unix_ts_to_utc(values[0]),) + values[1:])
    return data_headers, data_list, context.get_relative_path(source_path)
