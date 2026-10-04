__artifacts_v2__ = {
    "plz_interaction": {
        "name": "Swissmeteo - Interaction with places",
        "description": "Rows of the plz_interaction table of favorites_prediction_db.sqlite, with the place name looked up in localdata.sqlite",
        "author": "jonah.osterwalder@vd.ch",
        "creation_date": "2026-03-11",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Meteo",
        "notes": "What the app records as an interaction is not established. Interaction "
                 "Timestamp is the timestamp column read as Unix milliseconds. Postal Code (plz) "
                 "is the row's plz value as stored. Coordinates (lat/lon) holds the row's own lat "
                 "and lon, and is blank when either is empty or 0. When the row's postal code has "
                 "a row in the plz table of localdata.sqlite, Meteo of the city holds that row's "
                 "primary_name and Meteo of the city (lat/lon) holds coordinates this module "
                 "converts from the Swiss LV03 grid values in localdata.sqlite. When it has none, "
                 "or localdata.sqlite is absent, those two columns are blank. None of the 22 "
                 "registered iOS zip extractions listed on 2026-10-04 held this app's databases, "
                 "so the artifact was exercised on a constructed database only.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/databases/favorites_prediction_db.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/localdata.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "flag"
    },
    "swissmeteo_plz": {
        "name": "Swissmeteo - App opening with geolocation",
        "description": "Rows of the app_open table of favorites_prediction_db.sqlite, with the time and coordinates each row stores",
        "author": 'jonah.osterwalder@vd.ch, @AlexisBrignoni, Codex',
        "creation_date": "2026-03-11",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Meteo",
        "notes": "What the app records in this table, and what position the coordinates describe, "
                 "is not established. app_open.timestamp is the timestamp column read as Unix "
                 "milliseconds. No run against a registered image is recorded for this artifact.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/databases/favorites_prediction_db.sqlite*', '*/mobile/Containers/Data/Application/*/Documents/localdata.sqlite*'),
        "output_types": "all",
        "artifact_icon": "flag"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, open_sqlite_db_readonly

@artifact_processor
def plz_interaction(context):
    source_path = get_file_path(context.get_files_found(), "favorites_prediction_db.sqlite")
    data_headers = (('Interaction Timestamp','datetime'), "Postal Code (plz)", "Meteo of the city", "Meteo of the city (lat/lon)", "Coordinates (lat/lon)")
    data_list = []
    cursor = None
    prediction_db = ""
    localdata_db = ""

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith("favorites_prediction_db.sqlite"):
            prediction_db = file_found
        if file_found.endswith("localdata.sqlite"):
            localdata_db = file_found


    if prediction_db != "":
        query = '''
        SELECT
            datetime(timestamp/1000, 'unixepoch') AS created_date,
            plz,
            lat,
            lon
        FROM plz_interaction
        '''

        db_records = get_sqlite_db_records(prediction_db, query)

        local_data = []
        if localdata_db != "":
            db = open_sqlite_db_readonly(localdata_db)
            cursor = db.cursor()

        for record in db_records:
            local_data = get_location_infos(cursor, record[1]) if cursor else []
            if not (record[2] and record[3]):
                cons_link = ''
            else:
                cons_link = coordinate_to_text(record[2], record[3])
            # test for 1111 postal code case
            if len(local_data) > 0:
                meteo_link = lv03_to_text(local_data[0][1], local_data[0][2])
                data_list.append((record[0], record[1], local_data[0][4], meteo_link, cons_link))
            else:
                # no plz row to resolve the postal code: the two looked-up columns stay blank
                data_list.append((record[0], record[1], '', '', cons_link))
    else:
        logfunc('No Swissmeteo')

    return data_headers, data_list, source_path

@artifact_processor
def swissmeteo_plz(context):
    source_path = get_file_path(context.get_files_found(), "favorites_prediction_db.sqlite")
    data_headers = (('app_open.timestamp','datetime'), 'Latitude', 'Longitude', "Coordinates (lat/lon)")
    data_list = []
    prediction_db = ""

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('favorites_prediction_db.sqlite'):
            prediction_db = file_found

    if prediction_db != "":
        query = '''
        SELECT
            datetime(timestamp/1000, 'unixepoch') AS created_date,
            lat,
            lon
        FROM app_open
        '''

        db_records = get_sqlite_db_records(prediction_db, query)
        for record in db_records:
            data_list.append((record[0], record[1], record[2], coordinate_to_text(record[1], record[2])))
    else:
        logfunc('Swissmeteo favorites_prediction_db.sqlite not found')

    return data_headers, data_list, source_path

def coordinate_to_text(lat, lon):
    """Return the coordinates as text.

    This built an openstreetmap.org URL. A report links to nothing outside its own
    folder, so the coordinates are reported as the data they are.
    """
    return f"{lat}, {lon}"

def lv03_to_text(E, N): 
    # based on https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/f1a7e0129d93647c1c11e151b95a208a53e57ce6/scripts/py/wgs84_ch1903.py
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
    return f"{lat}, {lon}"

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
