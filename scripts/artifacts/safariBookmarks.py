from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_safariBookmarks(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        title,
        url,
        hidden
    FROM
    bookmarks
            """)

    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2]))

    db.close()

    data_headers = ('Title', 'URL', 'Hidden')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_safariBookmarks": {
        "name": "Safari Bookmarks",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('**/Safari/Bookmarks.db*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
