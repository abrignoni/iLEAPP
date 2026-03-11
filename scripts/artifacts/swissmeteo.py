__artifacts_v2__ = {
    "plz_interaction": {
        "name": "Swissmeteo - Interaction with places",
        "description": "Parse the interaction with meteo prevision of particular places",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-11",
        "last_update_date": "2026-03-11",
        "requirements": "none",
        "category": "Meteo",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/databases/favorites_prediction_db.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/localdata.sqlite*'),
        "output_types": "standard",
        "html_columns": ['Meteo of the city (link)', 'Consultation Location'],
        "artifact_icon": "flag"
    },
    "swissmeteo_plz": {
        "name": "Swissmeteo - App opening with geolocation",
        "description": "Parse the app opening time and location",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-11",
        "last_update_date": "2026-03-11",
        "requirements": "none",
        "category": "Meteo",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/databases/favorites_prediction_db.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/localdata.sqlite*'),
        "output_types": "standard",
        "html_columns": ['Map link'],
        "artifact_icon": "flag"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, open_sqlite_db_readonly

@artifact_processor
def plz_interaction(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "favorites_prediction_db.sqlite")
    data_list = []
    cursor = None
    prediction_db = ""
    localdata_db = ""

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith("favorites_prediction_db.sqlite"):
            prediction_db = file_found
        if file_found.endswith("localdata.sqlite"):
            localdata_db = file_found


    if prediction_db != "":
        query = '''
        SELECT 
            datetime(timestamp/1000, 'unixepoch', 'localtime') AS created_date,
            plz,
            lat,
            lon
        FROM plz_interaction
        '''

        data_headers = ('Consulted timestamp', "Meteo of the city", "Meteo of the city (link)", "Consultation Location")
        db_records = get_sqlite_db_records(prediction_db, query)

        local_data = []
        if localdata_db != "":
            db = open_sqlite_db_readonly(localdata_db)
            cursor = db.cursor()

        for record in db_records:
            local_data = get_location_infos(cursor, record[1])
            # test for 1111 postal code case
            if len(local_data) > 0:
                meteo_link = lv03_to_osm(local_data[0][1], local_data[0][2])
                if not (record[2] and record[3]):
                    cons_link = ''
                else:
                    cons_link = coordinate_to_osm(record[2], record[3])
                data_list.append((record[0], local_data[0][4], meteo_link, cons_link))
            else:
                data_list.append(record)

        return data_headers, data_list, source_path
    else:
        logfunc('No Swissmeteo')

@artifact_processor
def swissmeteo_plz(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "favorites_prediction_db.sqlite")
    data_list = []
    prediction_db = ""

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('favorites_prediction_db.sqlite'):
            prediction_db = file_found

    if prediction_db != "":
        query = '''
        SELECT 
            datetime(timestamp/1000, 'unixepoch', 'localtime') AS created_date,
            lat,
            lon
        FROM app_open
        '''

        data_headers = ('Opened timestamp', 'Latitude', 'Longitude', "Map link")
        db_records = get_sqlite_db_records(prediction_db, query)
        for record in db_records:
            data_list.append((record[0], record[1], record[2], coordinate_to_osm(record[1], record[2])))

        return data_headers, data_list, source_path
    else:
        logfunc('No app_open')

def coordinate_to_osm(lat, lon): 
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"

def lv03_to_osm(E, N): 
    # based on https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py
    y, x = (E-600000)/1e6, (N-200000)/1e6
    lat = (16.9023892 + (3.238272 * x)) + \
            - (0.270978 * pow(y, 2)) + \
            - (0.002528 * pow(x, 2)) + \
            - (0.0447 * pow(y, 2) * x) + \
            - (0.0140 * pow(x, 3))
    lon = (2.6779094 + (4.728982 * y) + \
                + (0.791484 * y * x) + \
                + (0.1306 * y * pow(x, 2))) + \
                - (0.0436 * pow(y, 3))
    lat, lon = lat*100/36, lon*100/36
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"

def get_location_infos(cursor, NPA):
    query = '''
    SELECT 
        plz_pk,
        x,
        y,
        altitude,
        primary_name
    FROM plz
    WHERE plz_pk = ?
    '''

    cursor.execute(query, (NPA,))
    local_data = cursor.fetchall()
    return local_data
