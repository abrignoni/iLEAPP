#'*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist' unused
__artifacts_v2__ = {
    "get_waze_account": {
        "name": "Waze - Account",
        "description": "Get Waze account information.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user',),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_waze_session": {
        "name": "Waze - Session",
        "description": "Get Waze session information.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/session',),
        "output_types": "standard",
        "artifact_icon": "globe"
    },
    "get_waze_tts": {
        "name": "Waze - TTS Navigation",
        "description": "Get Waze text-to-speech navigation entries.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/tts/tts.db*',),
        "output_types": "standard",
        "artifact_icon": "volume-2"
    },
    "get_waze_gps_quality": {
        "name": "Waze - GPS Quality",
        "description": "Get Waze GPS quality track logs.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Documents/spdlog*.logdata',
            '**/Documents/spdlog*.logdata',
        ),
        "output_types": "standard",
        "artifact_icon": "map"
    },
    "get_waze_searched_locations": {
        "name": "Waze - Searched Locations",
        "description": "Get Waze searched locations from user.db.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.db*',),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "get_waze_recent_locations": {
        "name": "Waze - Recent Locations",
        "description": "Get Waze recent locations from user.db.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.db*',),
        "output_types": "standard",
        "artifact_icon": "clock"
    },
    "get_waze_favorite_locations": {
        "name": "Waze - Favorite Locations",
        "description": "Get Waze favorite locations from user.db.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.db*',),
        "output_types": "standard",
        "artifact_icon": "star"
    },
    "get_waze_shared_locations": {
        "name": "Waze - Shared Locations",
        "description": "Get Waze shared locations from user.db.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-11-20",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.db*',),
        "output_types": "standard",
        "artifact_icon": "search-2"
    }
}

import os
import re
import pathlib
import sqlite3


from scripts.ilapfuncs import (
    logfunc,
    open_sqlite_db_readonly,
    convert_unix_ts_to_utc,
    artifact_processor,
    get_file_path,
    get_sqlite_db_records
    )


# format location
def FormatLocation(location, value, tableName, key):
    newLocation = ''
    if value:
        s = value.split(chr(29))
        for elem in range(0, len(s)):
            if bool(s[elem]) and (s[elem].lower() != 'none'):
                if newLocation:
                    newLocation = newLocation + ', '
                newLocation = newLocation + '(' + key + ': ' + s[elem] + ')'
        if newLocation:
            newLocation = tableName + ' ' + newLocation
            if location:
                newLocation = ', ' + newLocation
    return location + newLocation


@artifact_processor
def get_waze_account(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'user')
    if not source_path:
        logfunc('No waze "user" file found')
        return (), [], ''
    data_headers = (
        'First name',
        'Last name',
        'User name',
        'Nickname',
        ('First launched', 'datetime')
    )
    row = [None] * 5
    patternFirstName = 'Realtime.FirstName:'
    patternLastName = 'Realtime.LastName:'
    patternUserName = 'Realtime.Name:'
    patternNickname = 'Realtime.Nickname:'
    patternFirstLaunched = 'General.Last upgrade time:'
    sep = ': '
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                root = line.split('.', 1)[0]
                if not root in ('Realtime', 'General'):
                    continue
                # first name
                if line.startswith(patternFirstName):
                    row[0] = line.split(sep, 1)[1]
                # last name
                elif line.startswith(patternLastName):
                    row[1] = line.split(sep, 1)[1]
                # user name
                elif line.startswith(patternUserName):
                    row[2] = line.split(sep, 1)[1]
                # nickname
                elif line.startswith(patternNickname):
                    row[3] = line.split(sep, 1)[1]
                # first launched
                elif line.startswith(patternFirstLaunched):
                    timestamp = line.split(sep, 1)[1]
                    row[4] = convert_unix_ts_to_utc(int(float(timestamp)))
        # row
        if row.count(None) != len(row):
            data_list.append((row[0], row[1], row[2], row[3], row[4]))
    except Exception as e:
        logfunc(f'Error reading Waze "user" file: {e}')
    if not data_list:
        logfunc('No Waze Account data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_session(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'session')
    if not source_path:
        logfunc('No Waze "session" file found.')
        return (), [], ''
    data_headers = (
        ('Last synced', 'datetime'),
        'Last position',
        'Last navigation coordinates',
        'Last navigation destination',
        'State',
        'City',
        'Street',
        'House'
        )
    row = [None] * 8
    patternLastSynced = 'Config.Last synced:'
    patternGPSPosition = 'GPS.Position:'
    patternLastPosition = 'Navigation.Last position:'
    patternLastDestName = 'Navigation.Last dest name:'
    patternLastDestState = 'Navigation.Last dest state:'
    patternLastDestCity = 'Navigation.Last dest city:'
    patternLastDestStreet = 'Navigation.Last dest street:'
    patternLastDestHouse = 'Navigation.Last dest number:'
    sep = ': '
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                root = line.split('.', 1)[0]
                if not root in ('Config', 'GPS', 'Navigation'):
                    continue
                # Last synced (ms)
                if line.startswith(patternLastSynced):
                    timestamp = int(float(line.split(sep, 1)[1]) / 1000)
                    row[0] = convert_unix_ts_to_utc(timestamp / 1000)
                # last position
                elif line.startswith(patternGPSPosition):
                    coordinates = line.split(sep, 1)[1].split(',')      # lon,lat
                    row[1] = f'{float(coordinates[1]) / 1000000},{float(coordinates[0]) / 1000000}'
                # last navigation coordinates
                elif line.startswith(patternLastPosition):
                    coordinates = line.split(sep, 1)[1].split(',')      # lon,lat
                    row[2] = f'{float(coordinates[1]) / 1000000},{float(coordinates[0]) / 1000000}'
                # last navigation destination
                elif line.startswith(patternLastDestName):
                    row[3] = line.split(sep, 1)[1]
                # state
                elif line.startswith(patternLastDestState):
                    row[4] = line.split(sep, 1)[1]
                # city
                elif line.startswith(patternLastDestCity):
                    row[5] = line.split(sep, 1)[1]
                # street
                elif line.startswith(patternLastDestStreet):
                    row[6] = line.split(sep, 1)[1]
                # house
                elif line.startswith(patternLastDestHouse):
                    row[7] = line.split(sep, 1)[1]
            # row
            if row.count(None) != len(row):
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                row = [None] * 8
    except Exception as e:
        logfunc(f'Error reading Waze "session" file: {e}')
    if not data_list:
        logfunc('No Wazew Session info data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_tts(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'tts.db')
    if not source_path:
        logfunc('Waze tts.db not found')
        return (), [], ''
    data_headers = (
        ('Timestamp', 'datetime'),
        'Text',
        'Location'
    )
    try:
        db = open_sqlite_db_readonly(source_path)
        # list tables
        cursor = db.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = cursor.fetchall()
        if len(all_tables) == 0:
            logfunc('No Waze Text-To-Speech navigation data available')
            return data_headers, [], source_path
        for table in all_tables:
            table_name = table[0]
            cursor = db.cursor()
            query = f'''
            SELECT
                rowid,
                update_time,
                text
            FROM "{table_name}"
            '''
            cursor.execute(query)
            all_rows = cursor.fetchall()
            for row in all_rows:
                location = FormatLocation('', str(row[0]), table_name, 'rowid')
                timestamp = convert_unix_ts_to_utc(int(float(row[1])))
                data_list.append((timestamp, row[2], location))
        db.close()
    except sqlite3.Error as e:
        logfunc(f"Error in Waze TTS database: {e}")
    if not data_list:
        logfunc('No Waze text-to-speech navigation data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_gps_quality(context):
    files_found = context.get_files_found()
    data_list = []
    source_files = []

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Sample count (bad)',
        'Average accuracy (min-max)',
        'Provider',
        'Location'
    )

    if not files_found:
        logfunc('No Waze GPS logs found with the provided paths.')
        return (), [], ''

    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)

        if not (file_name.startswith('spdlog') and file_name.endswith('.logdata')):
            continue

        try:
            with open(file_found, "r", encoding="utf-8", errors="ignore") as f:
                row = [None] * 6
                hit_count = 0
                line_count = 0

                line_filter = re.compile(r'STAT\(buffer#[\d]{1,2}\)\sGPS_QUALITY\s')
                values_filter = re.compile(r'(?<=\{)(.*?)(?=\})')

                for line in f:
                    line_count += 1

                    if not line_filter.search(line):
                        continue

                    hit_count += 1
                    location = FormatLocation('', str(line_count), file_name, 'row')
                    values_iter = values_filter.finditer(line)

                    row = [None] * 6

                    for kv in values_iter:
                        kv_split = kv.group().split('=', 1)
                        if len(kv_split) < 2: continue

                        key = kv_split[0]
                        val = kv_split[1]

                        if key == 'TIMESTAMP':
                            try:
                                row[0] = convert_unix_ts_to_utc(int(float(val)))
                            except ValueError:
                                row[0] = val
                        elif key == 'LAT':
                            try: row[1] = float(val) / 1000000
                            except: row[1] = val
                        elif key == 'LON':
                            try: row[2] = float(val) / 1000000
                            except: row[2] = val
                        elif key == 'SAMPLE_COUNT':
                            row[3] = val
                        elif key == 'BAD_SAMPLE_COUNT':
                            if row[3]: row[3] += f' ({val})'
                            else: row[3] = f'({val})'
                        elif key == 'ACC_AVG':
                            row[4] = val
                        elif key == 'ACC_MIN':
                            if row[4]: row[4] += f' ({val}-'
                            else: row[4] = f'({val}-'
                        elif key == 'ACC_MAX':
                            if row[4]: row[4] += f'{val})'
                            else: row[4] = f'(??-{val})'
                        elif key == 'PROVIDER':
                            row[5] = val

                    if row[0] is not None:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], location))

                if hit_count > 0:
                    source_files.append(file_found)

        except Exception as e:
            logfunc(f'Error reading Waze GPS log {file_name}: {e}')

    if not data_list:
        logfunc('No Waze Track GPS quality data available in the processed files.')
        return data_headers, [], ''

    return data_headers, data_list, ', '


@artifact_processor
def get_waze_searched_locations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'user.db')
    if not source_path:
        logfunc('Waze user.db not found')
        return (), [], ''
    query = '''
    SELECT
        P.id,
        P.created_time,
        P.name,
        P.street,
        P.house,
        P.state,
        P.city,
        P.country,
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) || "," || CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "coordinates"
    FROM PLACES AS "P"
    '''

    all_rows = get_sqlite_db_records(source_path, query)
    data_list = []
    data_headers = (
        ('Created', 'datetime'),
        'Name',
        'Street',
        'House',
        'State',
        'City',
        'Country',
        'Coordinates',
        'Location'
        )
    if all_rows:
        for row in all_rows:
            # P.id
            location = FormatLocation('', str(row[0]), 'PLACES', 'id')
            # created
            created = convert_unix_ts_to_utc(int(float(row[0])))
            # row
            data_list.append((
                created,
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                location
                ))
    else:
        logfunc('No Waze Searched locations data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_recent_locations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'user.db')
    if not source_path:
        logfunc('Waze user.db not found')
        return (), [], ''
    query = '''
    SELECT
        R.id,
        P.id,
        R.access_time,
        R.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) || "," || CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "coordinates",
        R.created_time
    FROM RECENTS AS "R"
    LEFT JOIN PLACES AS "P" ON (R.place_id = P.id)
    '''
    all_rows = get_sqlite_db_records(source_path, query)
    data_headers = (
        ('Last access', 'datetime'),
        'Name',
        'Coordinates',
        ('Created', 'datetime'),
        'Location'
        )
    if all_rows:
        for row in all_rows:
            # R.id
            location = FormatLocation('', str(row[0]), 'RECENTS', 'id')
            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')
            # last access
            lastAccess = convert_unix_ts_to_utc(row[2])
            # created
            created = convert_unix_ts_to_utc(row[5])
            # row
            data_list.append((lastAccess, row[3], row[4], created, location))
    else:
        logfunc('No Waze Recent locations data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_favorite_locations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'user.db')
    if not source_path:
        logfunc('Waze user.db not found')
        return (), [], ''
    query = '''
    SELECT
        F.id,
        P.id,
        F.access_time,
         F.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) || "," || CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "coordinates",
        F.created_time,
        F.modified_time
    FROM FAVORITES AS "F"
    LEFT JOIN PLACES AS "P" ON (F.place_id = P.id)
    '''
    all_rows = get_sqlite_db_records(source_path, query)
    data_headers = (
        ('Last access', 'datetime'),
        'Name',
        'Coordinates',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        'Location'
        )
    if all_rows:
        for row in all_rows:
            # F.id
            location = FormatLocation('', str(row[0]), 'FAVORITES', 'id')
            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')
            # last access
            lastAccess = convert_unix_ts_to_utc(row[2])
            created = convert_unix_ts_to_utc(row[5])
            # modified
            modified = convert_unix_ts_to_utc(row[6])
            # row
            data_list.append((lastAccess, row[3], row[4], created, modified, location))
    else:
        logfunc('No Waze Favorite locations data available')
    return data_headers, data_list, source_path


@artifact_processor
def get_waze_shared_locations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'user.db')
    if not source_path:
        logfunc('Waze user.db not found')
        return (), [], ''
    query = '''
    SELECT
        SP.id,
        P.id,
        SP.share_time,
        SP.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) || "," || CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "coordinates",
        SP.created_time,
        SP.modified_time,
        SP.access_time
    FROM SHARED_PLACES AS "SP"
    LEFT JOIN PLACES AS "P" ON (SP.place_id = P.id)
    '''
    all_rows = get_sqlite_db_records(source_path, query)
    data_headers = (
        ('Shared', 'datetime'),
        'Name',
        'Coordinates',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Last access', 'datetime'),
        'Location'
        )
    if all_rows:
        for row in all_rows:
            # SP.id
            location = FormatLocation('', str(row[0]), 'SHARED_PLACES', 'id')
            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')
            # shared
            shared = convert_unix_ts_to_utc(row[2])
            created = convert_unix_ts_to_utc(row[5])
            # modified
            modified = convert_unix_ts_to_utc(row[6])
            # last access
            lastAccess = convert_unix_ts_to_utc(row[7])
            # row
            data_list.append((
                shared,
                row[3],
                row[4],
                created,
                modified,
                lastAccess,
                location
                ))
    else:
        logfunc('No Waze Shared locations data available')
    return data_headers, data_list, source_path
