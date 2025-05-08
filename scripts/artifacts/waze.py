__artifacts_v2__ = {
    "waze_account": {
        "name": "Account",
        "description": "Parses and extract Waze Account",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "lava", "html", "tsv" ],
        "artifact_icon": "user"
    },
    "waze_session_info": {
        "name": "Session Info",
        "description": "Parses and extract Waze Session Info",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "artifact_icon": "navigation-2"
    },
    "waze_track_gps_quality": {
        "name": "Track GPS Quality",
        "description": "Parses and extract Waze Track GPS Quality",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "all" ],
        "artifact_icon": "navigation-2"
    },
    "waze_searched_locations": {
        "name": "Searched Locations",
        "description": "Parses and extract Waze Searched Locations",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "all" ],
        "artifact_icon": "search"
    },
    "waze_recent_locations": {
        "name": "Recent Locations",
        "description": "Parses and extract Waze Recent Locations",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "all" ],
        "artifact_icon": "map-pin"
    },
    "waze_favorite_locations": {
        "name": "Favorite Locations",
        "description": "Parses and extract Waze Favorite Locations",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "all" ],
        "artifact_icon": "star"
    },
    "waze_share_locations": {
        "name": "Share Locations",
        "description": "Parses and extract Waze Share Locations",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "all" ],
        "artifact_icon": "map-pin"
    },
    "waze_tts": {
        "name": "Text-To-Speech navigation",
        "description": "Parses and extract Waze Text-To-Speech navigation",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-05-04",
        "requirements": "none",
        "category": "Waze",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Preferences/com.waze.iphone.plist'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "artifact_icon": "volume-2"
    }
}

import re
from pathlib import Path
from scripts.ilapfuncs import get_file_path, get_sqlite_db_records, get_txt_file_content, convert_unix_ts_to_utc, artifact_processor, logfunc


# constants
LINE_BREAK = '\n'
COMMA_SEP = ', '
HTML_LINE_BREAK = '<br>'


# device path/local path
def get_device_file_path(file_path, seeker):
    device_path = file_path

    if bool(file_path):
        file_info = seeker.file_infos.get(file_path) if file_path else None
        # data folder: /path/to/report/data
        if file_info:
            source_path = file_info.source_path
        # extraction folder: /path/to/directory
        else:
            source_path = file_path
        if source_path.startswith('\\\\?\\'): source_path = source_path[4:]
        source_path = Path(source_path).as_posix()

        index_private = source_path.find('/private/')
        if index_private > 0:
            device_path = source_path[index_private:]
        else:
            device_path = source_path

    return device_path


# unordered list
def unordered_list(values, html_format=False):
    if not bool(values):
        return None

    return HTML_LINE_BREAK.join(values) if html_format else LINE_BREAK.join(values)


# get application id
def get_application_id(files_found):
    file_found = get_file_path(files_found, "com.waze.iphone.plist")
    return Path(file_found).parents[2].name if bool(file_found) else None


# account
@artifact_processor
def waze_account(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'First name',
        'Last name',
        'User name',
        'Nickname',
        ('First launched', 'datetime')
    )
    data_list = []
    SEP = ': '
    first_name = None
    last_name = None
    user_name = None
    nickname = None
    first_launched = None

    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/user", return_on_first_hit=True)
    lines = get_txt_file_content(file_found)
    for line in lines:
        root = line.split('.', 1)[0]
        if not root in ( 'Realtime', 'General' ):
            continue

        # first name
        if line.startswith('Realtime.FirstName:'):
            first_name = line.split(SEP, 1)[1]
        # last name
        elif line.startswith('Realtime.LastName:'):
            last_name = line.split(SEP, 1)[1]
        # user name
        elif line.startswith('Realtime.Name:'):
            user_name = line.split(SEP, 1)[1]
        # nickname
        elif line.startswith('Realtime.Nickname:'):
            nickname = line.split(SEP, 1)[1]
        # first launched
        elif line.startswith('General.First use:'):
            timestamp = float(line.split(SEP, 1)[1])
            first_launched = convert_unix_ts_to_utc(timestamp)

    # lava row
    data_list.append((first_name, last_name, user_name, nickname, first_launched))

    return data_headers, data_list, file_found


# session info
@artifact_processor
def waze_session_info(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last synced', 'datetime'),
        'Last position latitude',
        'Last position longitude',
        'Last navigation latitude',
        'Last navigation longitude',
        'Last navigation destination',
        'State',
        'City',
        'Street',
        'House'
    )
    data_list = []
    SEP = ': '
    last_synced = None
    latitude = None
    longitude = None
    last_latitude = None
    last_longitude = None
    last_dest_name = None
    state = None
    city = None
    street = None
    house = None

    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/session", return_on_first_hit=True)
    lines = get_txt_file_content(file_found)
    for line in lines:
        root = line.split('.', 1)[0]
        if not root in ( 'Config', 'GPS', 'Navigation' ):
            continue

        # Last synced (ms)
        if line.startswith('Config.Last synced:'):
            timestamp = float(line.split(SEP, 1)[1])
            last_synced = convert_unix_ts_to_utc(timestamp)
        # last position
        elif line.startswith('GPS.Position:'):
            coordinates = line.split(SEP, 1)[1].split(',')      # lon,lat
            latitude = f"{float(coordinates[1]) / 1000000}"
            longitude = f"{float(coordinates[0]) / 1000000}"
        # last navigation coordinates
        elif line.startswith('Navigation.Last position:'):
            coordinates = line.split(SEP, 1)[1].split(',')      # lon,lat
            last_latitude = f"{float(coordinates[1]) / 1000000}"
            last_longitude = f"{float(coordinates[0]) / 1000000}"
        # last navigation destination
        elif line.startswith('Navigation.Last dest name:'):
            last_dest_name = line.split(SEP, 1)[1]
        # state
        elif line.startswith('Navigation.Last dest state:'):
            state = line.split(SEP, 1)[1]
        # city
        elif line.startswith('Navigation.Last dest city:'):
            city = line.split(SEP, 1)[1]
        # street
        elif line.startswith('Navigation.Last dest street:'):
            street = line.split(SEP, 1)[1]
        # house
        elif line.startswith('Navigation.Last dest number:'):
            house = line.split(SEP, 1)[1]

    # lava row
    data_list.append((last_synced, latitude, longitude, last_latitude, last_longitude, last_dest_name, state, city, street, house))

    return data_headers, data_list, file_found


# track gps tracker
@artifact_processor
def waze_track_gps_quality(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Sample count (bad)',
        'Average accuracy (min-max)',
        'Provider',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['waze_track_gps_quality']['name']

    waze_app_identifier = get_application_id(files_found)
    spdlog = seeker.search(f"*/{waze_app_identifier}/Documents/spdlog.*logdata")

    # all files
    for file_found in spdlog:
        file_name = Path(file_found).name
        device_file_path = get_device_file_path(file_found, seeker)
 
        # spdlog.*logdata
        if not (file_name.startswith('spdlog') and file_name.endswith('.logdata')):
            continue

        try:
            device_file_paths = [ device_file_path ]

            # regexpr pattern
            line_pattern = re.compile(r'STAT\(buffer#[\d]{1,2}\)\sGPS_QUALITY\s')
            values_pattern = re.compile(r'(?<=\{)(.*?)(?=\})')

            # text file
            lines = get_txt_file_content(file_found)

            line_count = 0
            for line in lines:
                line_count += 1

                device_file_paths = [ device_file_path ]

                # gps quality
                if not re.search(line_pattern, line):
                    continue

                timestamp = None
                latitude = None
                longitude = None
                sample_count = None
                average_accuracy = None
                provider = None

                values_iter = re.finditer(values_pattern, line)
                for kv in values_iter:
                    kv_split = kv.group().split('=', 1)
                
                    # timestamp
                    if kv_split[0] == 'TIMESTAMP':
                        timestamp = convert_unix_ts_to_utc(float(kv_split[1]))

                    # latitude
                    elif kv_split[0] == 'LAT':
                        latitude = float(kv_split[1]) / 1000000

                    # longitude
                    elif kv_split[0] == 'LON':
                        longitude = float(kv_split[1]) / 1000000

                    # sample count
                    elif kv_split[0] == 'SAMPLE_COUNT':
                        sample_count = kv_split[1]
                        
                    # bad sample count
                    elif kv_split[0] == 'BAD_SAMPLE_COUNT':
                        sample_count += f" ({kv_split[1]})"

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_AVG':
                        average_accuracy = kv_split[1]

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_MIN':
                        average_accuracy += f" ({kv_split[1]}-"

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_MAX':
                        average_accuracy += f"{kv_split[1]})"

                    # provider
                    elif kv_split[0] == 'PROVIDER':
                        provider = kv_split[1]

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f"{Path(file_found).name} (row: {line_count})"

                # html row
                data_list_html.append((timestamp, latitude, longitude, sample_count, average_accuracy, provider, source_file_name_html, location))
                # lava row
                data_list.append((timestamp, latitude, longitude, sample_count, average_accuracy, provider, source_file_name, location))
        except Exception as ex:
            logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
            pass

    return data_headers, (data_list, data_list_html), ' '


# searched locations
@artifact_processor
def waze_searched_locations(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Name',
        'Street',
        'House',
        'State',
        'City',
        'Country',
        'Latitude',
        'Longitude',
        'Location'
    )
    data_list = []
    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/user.db", return_on_first_hit=True)

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
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude"
    FROM PLACES AS "P"
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        # created
        created = convert_unix_ts_to_utc(record[1])
        # name
        name = record[2]
        # street
        street = record[3]
        # house
        house = record[4]
        # state
        state = record[5]
        # city
        city = record[6]
        # country
        country = record[7]
        # latitude
        latitude = record[8]
        # longitude
        longitude = record[9]

        # location
        location = f"PLACES (id: {record[0]})"

        # lava row
        data_list.append((created, name, street, house, state, city, country, latitude, longitude, location))

    return data_headers, data_list, file_found


# recent locations
@artifact_processor
def waze_recent_locations(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last access', 'datetime'),
        'Name',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        'Location'
    )
    data_list = []
    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/user.db", return_on_first_hit=True)

    query = '''
    SELECT 
        R.id,
        P.id,
        R.access_time,
        R.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    R.created_time
    FROM RECENTS AS "R"
    LEFT JOIN PLACES AS "P" ON (R.place_id = P.id)
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        # last access
        last_access = convert_unix_ts_to_utc(record[2])
        # name
        name = record[3]
        # latitude
        latitude = record[4]
        # longitude
        longitude = record[5]
        # created
        created = convert_unix_ts_to_utc(record[6])

        # location
        location = [ f"RECENTS (id: {record[0]})" ]
        if record[1] is not None: location.append(f"PLACES (id: {record[1]})")
        location = COMMA_SEP.join(location)

        # lava row
        data_list.append((last_access, name, latitude, longitude, created, location))

    return data_headers, data_list, file_found


# favorite locations
@artifact_processor
def waze_favorite_locations(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Last access', 'datetime'),
        'Name',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        'Location'
    )
    data_list = []
    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/user.db", return_on_first_hit=True)

    query = '''
    SELECT 
	    F.id,
	    P.id,
        F.access_time,
	    F.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    F.created_time,
	    F.modified_time
    FROM FAVORITES AS "F"
    LEFT JOIN PLACES AS "P" ON (F.place_id = P.id)
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        # last access
        last_access = convert_unix_ts_to_utc(record[2])
        # name
        name = record[3]
        # latitude
        latitude = record[4]
        # longitude
        longitude = record[5]
        # created
        created = convert_unix_ts_to_utc(record[6])
        # modified
        modified = convert_unix_ts_to_utc(record[7])

        # location
        location = [ f"FAVORITES (id: {record[0]})" ]
        if record[1] is not None: location.append(f"PLACES (id: {record[1]})")
        location = COMMA_SEP.join(location)

        # lava row
        data_list.append((last_access, name, latitude, longitude, created, modified, location))

    return data_headers, data_list, file_found


# share locations
@artifact_processor
def waze_share_locations(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Shared', 'datetime'),
        'Name',
        'Latitude',
        'Longitude',
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Last access', 'datetime'),
        'Location'
    )
    data_list = []
    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Documents/user.db", return_on_first_hit=True)

    query = '''
    SELECT 
	    SP.id,
	    P.id,
        SP.share_time,
	    SP.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) AS "latitude",
        CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "longitude",
	    SP.created_time,
	    SP.modified_time,
        SP.access_time
    FROM SHARED_PLACES AS "SP"
    LEFT JOIN PLACES AS "P" ON (SP.place_id = P.id)                   
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        # share time
        shared = convert_unix_ts_to_utc(record[2])
        # name
        name = record[3]
        # latitude
        latitude = record[4]
        # longitude
        longitude = record[5]
        # created
        created = convert_unix_ts_to_utc(record[6])
        # modified
        modified = convert_unix_ts_to_utc(record[7])
        # last access
        last_access = convert_unix_ts_to_utc(record[8])

        # location
        location = [ f"SHARED_PLACES (id: {record[0]})" ]
        if record[1] is not None: location.append(f"PLACES (id: {record[1]})")
        location = COMMA_SEP.join(location)

        # lava row
        data_list.append((shared, name, latitude, longitude, created, modified, last_access, location))

    return data_headers, data_list, file_found


# Text-To-Speech navigation
@artifact_processor
def waze_tts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Timestamp', 'datetime'),
        'Text',
        'Location'
    )
    data_list = []
    waze_app_identifier = get_application_id(files_found)
    file_found = seeker.search(f"*/{waze_app_identifier}/Library/Caches/tts/tts.db", return_on_first_hit=True)

    # list tables
    query = f"SELECT name FROM sqlite_master WHERE type='table'"

    all_tables = get_sqlite_db_records(file_found, query)
    for table in all_tables:
        # table name
        table_name = table[0]

        query = '''
        SELECT 
            rowid,
            update_time,
            text
        FROM {0}
        '''.format(table_name)

        db_records = get_sqlite_db_records(file_found, query)
        for record in db_records:
            # share timestamp
            timestamp = convert_unix_ts_to_utc(record[1])
            # text
            text = record[2]

            # location
            location = f"{table_name} (rowid: {record[0]})"

            # lava row
            data_list.append((timestamp, text, location))

    return data_headers, data_list, file_found
