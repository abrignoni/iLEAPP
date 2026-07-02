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
