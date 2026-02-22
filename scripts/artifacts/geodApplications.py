from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db


@artifact_processor
def get_geodApplications(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for ff in files_found:
        ff = str(ff)
        if ff.endswith('.db'):
            file_found = ff
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    if does_table_exist_in_db(file_found, 'mkcount'):
        query = "SELECT count_type, app_id, createtime FROM mkcount"
    elif does_table_exist_in_db(file_found, 'dailycounts'):
        query = "SELECT count_type, app_id, createtime FROM dailycounts"
    else:
        db.close()
        return (), [], ''

    cursor.execute(query)

    all_rows = cursor.fetchall()

    data_list = []
    if len(all_rows) > 0:
        for row in all_rows:
            data_list.append((row[2], row[0], row[1]))

    db.close()
    data_headers = ('Creation Time', 'Count ID', 'Application')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_geodApplications": {
        "name": "Geolocation Applications",
        "description": "Application geolocation access counts.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('**/AP.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}
