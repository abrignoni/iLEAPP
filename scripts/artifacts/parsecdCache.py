""" parsecdCache """
__artifacts_v2__ = {
    "parse_cd_cache": {
        "name": "ParseCD Cache",
        "description": (
            "Parses Spotlight search completion from ParseCD Cache "
            "database. If completion is a bundle ID it's likely that "
            "application opened as a result of completing the search"
        ),
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Spotlight Searches",
        "notes": "",
        "paths": ("**/EngagedCompletions/Cache.db*"),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 19 rows",
            "dexter_ios18": "iOS 18.3.2 | group.com.apple.PegasusConfiguration | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | group.com.apple.PegasusConfiguration | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | group.com.apple.PegasusConfiguration | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | group.com.apple.PegasusConfiguration | 1 row",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 7 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    }
}


from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    does_column_exist_in_db,
    get_sqlite_db_records,
)


@artifact_processor
def parse_cd_cache(context):
    """ see artifact description """
    data_list = []
    report_file = "Unknown"

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(".db"):
            continue  # Skip all other files
        report_file = context.get_relative_path(file_found)
        score_column = "score"
        if not does_column_exist_in_db(file_found, "completion_cache_engagement", "score"):
            score_column = "NULL AS score"

        qry = f"""
            select
                engagement_date,
                input,
                completion,
                transformed,
                {score_column}
            from completion_cache_engagement
        """

        all_rows = get_sqlite_db_records(file_found, qry)

        for row in all_rows:
            timestamp = convert_cocoa_core_data_ts_to_utc(row[0])

            data_list.append((timestamp, row[1], row[2], row[3], row[4]))

    data_headers = (
        ("Engagement Date", "datetime"),
        "Input",
        "Completion",
        "Transformed",
        "Score",
    )

    return data_headers, data_list, report_file
