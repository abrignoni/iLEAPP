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
        "paths": ('**/EngagedCompletions/Cache.db*'),
        "output_types": "standard"
    }
}


from scripts.ilapfuncs import open_sqlite_db_readonly, convert_ts_human_to_utc
from scripts.ilapfuncs import artifact_processor, convert_utc_human_to_timezone

@artifact_processor
def get_parseCDCache(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue # Skip all other files
        report_file = file_found
        db = open_sqlite_db_readonly(file_found)

        cursor = db.cursor()
        cursor.execute('''
        select 
            datetime(engagement_date + 978307200,'unixepoch') as engagement_date, 
            input, 
            completion, 
            transformed, 
            score
        FROM completion_cache_engagement
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            timestamp = row[0]
            timestamp = convert_ts_human_to_utc(timestamp)
            timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)

            data_list.append((timestamp, row[1], row[2], row[3], row[4]))

        db.close()

    data_headers = (('Engagement Date', 'datetime'), 'Input', 'Completion', 'Transformed', 'Score')

    return data_headers, data_list, report_file
