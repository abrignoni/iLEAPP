from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_safariFavicons(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('Favicons.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select
    datetime('2001-01-01', "timestamp" || ' seconds') as icon_timestamp,
    page_url.url,
    icon_info.url,
    icon_info.width,
    icon_info.height,
    icon_info.has_generated_representations
    FROM icon_info
    LEFT JOIN page_url
    on icon_info.uuid = page_url.uuid
    ''')

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

    db.close()

    data_headers = ('Timestamp', 'Page URL', 'Icon URL', 'Width', 'Height', 'Generated Representations?')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_safariFavicons": {
        "name": "Safari Favicons",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Safari Browser",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Image Cache/Favicons/Favicons.db*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
