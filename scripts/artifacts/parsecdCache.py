__artifacts_v2__ = {
    "get_parseCDCache": {
        "name": "ParseCD Cache",
        "description": "Parses Spotlight search completion from ParseCD Cache database. If completion is a bundle ID it's likely that application opened as a result of completing the search",
        "author": "@JohnHyla",
        "version": "0.0.1",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Spotlight Searches",
        "notes": "",
        "paths": ("**/EngagedCompletions/Cache.db*"),
        "output_types": "standard",
    }
}


from scripts.ilapfuncs import open_sqlite_db_readonly, convert_ts_human_to_utc
from scripts.ilapfuncs import artifact_processor, convert_utc_human_to_timezone


@artifact_processor
def get_parseCDCache(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    report_file = "Unknown"
    has_score = False
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(".db"):
            continue  # Skip all other files
        report_file = file_found
        db = open_sqlite_db_readonly(file_found)

        cursor = db.cursor()

        cursor.execute("pragma table_info(completion_cache_engagement)")
        cols = [row[1] for row in cursor.fetchall()]
        has_score = "score" in cols

        select_cols = [
            "datetime(engagement_date + 978307200,'unixepoch') as engagement_date",
            "input",
            "completion",
            "transformed",
        ]
        if has_score:
            select_cols.append("score")

        qry = f"""
            select {", ".join(select_cols)}
            from completion_cache_engagement
        """

        cursor.execute(qry)
        all_rows = cursor.fetchall()

        for row in all_rows:
            timestamp = convert_ts_human_to_utc(row[0])
            timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)

            # Save data to temp variable to check whether has "score" column or no
            temp = [timestamp, row[1], row[2], row[3]]
            if has_score:
                temp.append(row[4])

            data_list.append(tuple(temp))

        db.close()

    data_headers = [
        ("Engagement Date", "datetime"),
        "Input",
        "Completion",
        "Transformed",
    ]
    if has_score:
        data_headers.append("Score")

    return tuple(data_headers), data_list, report_file
