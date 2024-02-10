__artifacts_v2__ = {
    "waze": {
        "name": "Waze",
        "description": "Get account, session, searched locations, recent locations, favorite locations, "
					   "share locations, text-to-speech navigation and track GPS quality.",
        "author": "Django Faiola (djangofaiola.blogspot.com @DjangoFaiola)",
        "version": "0.1.2",
        "date": "2024-02-02",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/user.db*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "function": "get_waze"
    }
}

import os
import re
import plistlib
import pathlib
import shutil
import sqlite3
import textwrap
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, open_sqlite_db_readonly, convert_ts_int_to_utc, convert_utc_human_to_timezone

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


def FormatTimestamp(utc, timezone_offset):
    if not bool(utc) or (utc == None):
        return ''
    else:
        timestamp = convert_ts_int_to_utc(int(float(utc)))
        return convert_utc_human_to_timezone(timestamp, timezone_offset)


# account
def get_account(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "r", encoding="utf-8")
    try:
        row = [ None ] * 5
        patternFirstName = 'Realtime.FirstName:'
        patternLastName = 'Realtime.LastName:'
        patternUserName = 'Realtime.Name:'
        patternNickname = 'Realtime.Nickname:'
        patternFirstLaunched = 'General.Last upgrade time:'
        sep = ': '

        data = f.readlines()
        for line in data:
            root = line.split('.', 1)[0]
            if not root in ( 'Realtime', 'General' ):
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
                row[4] = FormatTimestamp(timestamp, timezone_offset)

        # row
        if row.count(None) != len(row):
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

    finally:
        f.close()

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Waze Account')
        report.start_artifact_report(report_folder, 'Waze Account')
        report.add_script()
        data_headers = ('First name', 'Last name', 'User name', 'Nickname', 'First launched')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Account'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Account'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Account data available')


# session
def get_session(file_found, report_folder, timezone_offset):
    data_list = []

    f = open(file_found, "r", encoding="utf-8")
    try:
        row = [ None ] * 8
        patternLastSynced = 'Config.Last synced:'
        patternGPSPosition = 'GPS.Position:'
        patternLastPosition = 'Navigation.Last position:'
        patternLastDestName = 'Navigation.Last dest name:'
        patternLastDestState = 'Navigation.Last dest state:'
        patternLastDestCity = 'Navigation.Last dest city:'
        patternLastDestStreet = 'Navigation.Last dest street:'
        patternLastDestHouse = 'Navigation.Last dest number:'
        sep = ': '

        data = f.readlines()
        for line in data:
            root = line.split('.', 1)[0]
            if not root in ( 'Config', 'GPS', 'Navigation' ):
                continue
            
            # Last synced (ms)
            if line.startswith(patternLastSynced):
                timestamp = int(float(line.split(sep, 1)[1]) / 1000)
                row[0] = FormatTimestamp(timestamp, timezone_offset)
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

    finally:
        f.close()

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Waze Session info')
        report.start_artifact_report(report_folder, 'Waze Session info')
        report.add_script()
        data_headers = ('Last synced', 'Last position', 'Last navigation coordinates', 'Last navigation destination', 'State', 'City', 'Street', 'House')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Session info'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Session info'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Session info data available')


# recent locations
def get_recent_locations(file_found, report_folder, database, timezone_offset):
    cursor = database.cursor()
    cursor.execute('''
    SELECT 
        R.id,
        P.id,
        R.access_time,
        R.name AS "name",
        CAST((CAST(P.latitude AS REAL) / 1000000) AS TEXT) || "," || CAST((CAST(P.longitude AS REAL) / 1000000) AS TEXT) AS "coordinates",
	    R.created_time
    FROM RECENTS AS "R"
    LEFT JOIN PLACES AS "P" ON (R.place_id = P.id)
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Waze Recent locations')
        report.start_artifact_report(report_folder, 'Waze Recent locations')
        report.add_script()
        data_headers = ('Last access', 'Name', 'Coordinates', 'Created', 'Location') 
        data_list = []
        for row in all_rows:
            # R.id
            location = FormatLocation('', str(row[0]), 'RECENTS', 'id')

            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')

            # last access
            lastAccess = FormatTimestamp(row[2], timezone_offset)

            # created
            created = FormatTimestamp(row[5], timezone_offset)

            # row
            data_list.append((lastAccess, row[3], row[4], created, location))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Recent locations'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Recent locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Recent locations data available')


# favorite locations
def get_favorite_locations(file_found, report_folder, database, timezone_offset):
    cursor = database.cursor()
    cursor.execute('''
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
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Waze Favorite locations')
        report.start_artifact_report(report_folder, 'Waze Favorite locations')
        report.add_script()
        data_headers = ('Last access', 'Name', 'Coordinates', 'Created', 'Modified', 'Location') 
        data_list = []
        for row in all_rows:
            # F.id
            location = FormatLocation('', str(row[0]), 'FAVORITES', 'id')

            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')

            # last access
            lastAccess = FormatTimestamp(row[2], timezone_offset)

            # created
            created = FormatTimestamp(row[5], timezone_offset)

            # modified
            modified = FormatTimestamp(row[6], timezone_offset)

            # row
            data_list.append((lastAccess, row[3], row[4], created, modified, location))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Favorite locations'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Favorite locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Favorite locations data available')


# shared locations
def get_shared_locations(file_found, report_folder, database, timezone_offset):
    cursor = database.cursor()
    cursor.execute('''
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
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Waze Shared locations')
        report.start_artifact_report(report_folder, 'Waze Shared locations')
        report.add_script()
        data_headers = ('Shared', 'Name', 'Coordinates', 'Created', 'Modified', 'Last access', 'Location') 
        data_list = []
        for row in all_rows:
            # SP.id
            location = FormatLocation('', str(row[0]), 'SHARED_PLACES', 'id')

            # P.id
            location = FormatLocation(location, str(row[1]), 'PLACES', 'id')

            # shared
            shared = FormatTimestamp(row[2], timezone_offset)

            # created
            created = FormatTimestamp(row[5], timezone_offset)

            # modified
            modified = FormatTimestamp(row[6], timezone_offset)

            # last access
            lastAccess = FormatTimestamp(row[7], timezone_offset)

            # row
            data_list.append((shared, row[3], row[4], created, modified, lastAccess, location))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Shared locations'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Shared locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Shared locations data available')


# searched locations
def get_searched_locations(file_found, report_folder, database, timezone_offset):
    cursor = database.cursor()
    cursor.execute('''
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
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Waze Searched locations')
        report.start_artifact_report(report_folder, 'Waze Searched locations')
        report.add_script()
        data_headers = ('Created', 'Name', 'Street', 'House', 'State', 'City', 'Country', 'Coordinates', 'Location') 
        data_list = []
        for row in all_rows:
            # P.id
            location = FormatLocation('', str(row[0]), 'PLACES', 'id')

            # created
            created = FormatTimestamp(row[1], timezone_offset)

            # row
            data_list.append((created, row[2], row[3], row[4], row[5], row[6], row[7], row[8], location))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Waze Searched locations'
        tsv(report_folder, data_headers, data_list, tsvname)
            
        tlactivity = f'Waze Searched locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Searched locations data available')


# text-to-speech navigation
def get_tts(file_found, report_folder, timezone_offset):
    db = open_sqlite_db_readonly(file_found)
    try:
        # list tables
        cursor = db.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = cursor.fetchall()
        if len(all_tables) == 0:
            logfunc('No Waze Text-To-Speech navigation data available')
            return
        
        for table in all_tables:
            table_name = table[0]
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
                rowid,
                update_time,
                text
            FROM {0}
            '''.format(table_name))

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Waze Text-To-Speech navigation')
                report.start_artifact_report(report_folder, 'Waze Text-To-Speech navigation')
                report.add_script()
                data_headers = ('Timestamp', 'Text', 'Location') 
                data_list = []
                for row in all_rows:
                    # rowid
                    location = FormatLocation('', str(row[0]), table_name, 'rowid')

                    # timestamp
                    timestamp = FormatTimestamp(row[1], timezone_offset)

                    # row
                    data_list.append((timestamp, row[2], location))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Waze Text-To-Speech navigation'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Waze Text-To-Speech navigation'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Waze Text-To-Speech navigation data available')
    finally:
        db.close()
        

# track gps quality
def get_gps_quality(files_found, report_folder, timezone_offset):
    data_list = []
    source_files = []

    for file_found in files_found:
        file_found = str(file_found)
        file_name = pathlib.Path(file_found).name

        if not (file_name.startswith('spdlog') and file_name.endswith('.logdata')):
            continue

        f = open(file_found, "r", encoding="utf-8")
        try:
            row = [ None ] * 6
            hit_count = 0
            line_count = 0
            line_filter = re.compile(r'STAT\(buffer#[\d]{1,2}\)\sGPS_QUALITY\s')
            values_filter = re.compile(r'(?<=\{)(.*?)(?=\})')

            data = f.readlines()
            for line in data:
                line_count += 1
                
                # gps quality
                if not re.search(line_filter, line):
                    continue

                hit_count += 1
                location = FormatLocation('', str(line_count), file_name, 'row')
                    
                values_iter = re.finditer(values_filter, line)
                for kv in values_iter:
                    kv_split = kv.group().split('=', 1)
                    
                    # timestamp
                    if kv_split[0] == 'TIMESTAMP':
                        row[0] = FormatTimestamp(kv_split[1], timezone_offset)

                    # latitude
                    elif kv_split[0] == 'LAT':
                        row[1] = float(kv_split[1]) / 1000000

                    # longitude
                    elif kv_split[0] == 'LON':
                        row[2] = float(kv_split[1]) / 1000000

                    # sample count
                    elif kv_split[0] == 'SAMPLE_COUNT':
                        row[3] = kv_split[1]
                        
                    # bad sample count
                    elif kv_split[0] == 'BAD_SAMPLE_COUNT':
                        row[3] += ' (' + kv_split[1] + ')'

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_AVG':
                        row[4] = kv_split[1]

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_MIN':
                        row[4] += ' (' + kv_split[1] + '-'

                    # accuracy "avg (min-max)"
                    elif kv_split[0] == 'ACC_MAX':
                        row[4] += kv_split[1] + ')'

                    # provider
                    elif kv_split[0] == 'PROVIDER':
                        row[5] = kv_split[1]

                # row
                if row.count(None) != len(row):
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], location))

            if hit_count > 0:
                if file_found.startswith('\\\\?\\'):
                    source_files.append(file_found[4:])
                else:
                    source_files.append(file_found)
        finally:
            f.close()

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Waze Track GPS quality')
        report.start_artifact_report(report_folder, 'Waze Track GPS quality')
        report.add_script()
        data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Sample count (bad)', 'Average accuracy (min-max)', 'Provider', 'Location')

        report.write_artifact_data_table(data_headers, data_list, ', '.join(source_files))
        report.end_artifact_report()
                
        tsvname = f'Waze Track GPS quality'
        tsv(report_folder, data_headers, data_list, tsvname)
                
        tlactivity = f'Waze Track GPS quality'
        timeline(report_folder, tlactivity, data_list, data_headers) 

        kmlactivity = 'Waze Track GPS quality'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
    else:
        logfunc('No Waze Track GPS quality data available')


# waze
def get_waze(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #datos =  seeker.search('**/*com.apple.mobile_container_manager.metadata.plist')
    for file_foundm in files_found:
        if file_foundm.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            with open(file_foundm, 'rb') as f:
                pl = plistlib.load(f)
                if pl['MCMMetadataIdentifier'] == 'com.waze.iphone':
                    fulldir = (os.path.dirname(file_foundm))
                    identifier = (os.path.basename(fulldir))
                    
                    # user
                    path_list = seeker.search(f'*/{identifier}/Documents/user', True)
                    if len(path_list) > 0:
                        get_account(path_list[0], report_folder, timezone_offset)

                    # session
                    path_list = seeker.search(f'*/{identifier}/Documents/session', True)
                    if len(path_list) > 0:
                        get_session(path_list[0], report_folder, timezone_offset)

                    # tts.db
                    path_list = seeker.search(f'*/{identifier}/Library/Caches/tts/tts.db', True)
                    if len(path_list) > 0:
                        get_tts(path_list[0], report_folder, timezone_offset)

                    # spdlog.*logdata
                    path_list = seeker.search(f'*/{identifier}/Documents/spdlog.*logdata')
                    if len(path_list) > 0:
                        get_gps_quality(path_list, report_folder, timezone_offset)

                    break

    for file_found in files_found:
        # user.db
        if file_found.endswith('user.db'):
            db = open_sqlite_db_readonly(file_found)
            try:
                # searched locations
                get_searched_locations(file_found, report_folder, db, timezone_offset)

                # recent locations
                get_recent_locations(file_found, report_folder, db, timezone_offset)

                # favorite locations
                get_favorite_locations(file_found, report_folder, db, timezone_offset)

                # shared locations
                get_shared_locations(file_found, report_folder, db, timezone_offset)
            finally:
                db.close()
