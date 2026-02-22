from scripts.ilapfuncs import artifact_processor, logfunc, strings, open_sqlite_db_readonly, does_table_exist_in_db


@artifact_processor
def get_geodPDPlaceCache(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for ff in files_found:
        ff = str(ff)
        if ff.endswith('.db'):
            file_found = ff
            break

    db = open_sqlite_db_readonly(file_found)
    if not does_table_exist_in_db(file_found, 'pdplacelookup'):
        logfunc('pdplacelookup table not found')
        db.close()
        return (), [], ''

    cursor = db.cursor()
    cursor.execute("""
    SELECT requestkey, pdplacelookup.pdplacehash, datetime('2001-01-01', "lastaccesstime" || ' seconds') as lastaccesstime, datetime('2001-01-01', "expiretime" || ' seconds') as expiretime, pdplace
    FROM pdplacelookup
    INNER JOIN pdplaces on pdplacelookup.pdplacehash = pdplaces.pdplacehash
    """)

    all_rows = cursor.fetchall()
    data_list = []
    if len(all_rows) > 0:
        for row in all_rows:
            pd_place = ''.join(f'{row}<br>' for row in set(strings(row[4])))
            data_list.append((row[2], row[0], row[1], row[3], pd_place))

    db.close()
    data_headers = ('Last Access Time', 'Request Key', 'PD Place Hash', 'Expire Time', 'PD Place')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_geodPDPlaceCache": {
        "name": "Geolocation PD Place Cache",
        "description": "Cached place data from geolocation services.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('**/PDPlaceCache.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "html_columns": ["PD Place"]
    }
}
