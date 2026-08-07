__artifacts_v2__ = {
    "appleMapsTrips": {
        "name": "Apple Maps Trips (routined)",
        "description": "Examines the ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO and ZRTLEARNEDLOCATIONOFINTERESTVISITMO tables from the routined (Significant Locations) cache, not the Apple Maps app. The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence. For details: https://doubleblak.com/blogPost.php?k=Locations",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Locations",
        "notes": "Motion-activity value mapping observed in testing; raw column preserved.",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 206 rows",
            "felix_ios17": "iOS 17.6.1 | 45 rows",
            "fsfull002_ios17": "iOS 17.1 | 50 rows",
            "hc_ios18_7": "iOS 18.7.8 | 22 rows",
            "iphone11_ios17": "iOS 17.3 | 155 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 242 rows",
            "abe_ios16": "iOS 16.5 | 370 rows",
            "felix23_ios16": "iOS 16.5 | 28 rows",
            "hickman_ios13": "iOS 13.3.1 | 13 rows",
            "hickman_ios14": "iOS 14.3 | 81 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 23 rows",
        }
    },
    "appleMapsSignificantLocations": {
        "name": "Apple Maps Significant Locations (routined)",
        "description": "Location data comes from the routined (Significant Locations) cache, not the Apple Maps app. The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 206 rows",
            "felix_ios17": "iOS 17.6.1 | 45 rows",
            "fsfull002_ios17": "iOS 17.1 | 50 rows",
            "hc_ios18_7": "iOS 18.7.8 | 22 rows",
            "iphone11_ios17": "iOS 17.3 | 155 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 242 rows",
            "abe_ios16": "iOS 16.5 | 370 rows",
            "felix23_ios16": "iOS 16.5 | 28 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 81 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 23 rows",
        }
    },
    "appleMapsSignificantLocationsVisits": {
        "name": "Apple Maps Significant Locations Visits (routined)",
        "description": "Location data comes from the routined (Significant Locations) cache, not the Apple Maps app. The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 136 rows",
            "felix_ios17": "iOS 17.6.1 | 38 rows",
            "fsfull002_ios17": "iOS 17.1 | 9 rows",
            "hc_ios18_7": "iOS 18.7.8 | 13 rows",
            "iphone11_ios17": "iOS 17.3 | 103 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 241 rows",
            "abe_ios16": "iOS 16.5 | 191 rows",
            "felix23_ios16": "iOS 16.5 | 11 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 11 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 13 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.html_safe import esc

def get_google_map_link(latitude_value, longitude_value):
    """Return the coordinates as escaped text.

    This was a live google.com/maps anchor. A report links to nothing outside its own
    folder, so the coordinates are reported as the data they are; an examiner who
    wants a map pastes them into one deliberately.
    """
    if latitude_value is None or longitude_value is None:
        return ""

    return f"{esc(latitude_value)}, {esc(longitude_value)}"

def get_google_dir_link(o_latitude_value, o_longitude_value, d_latitude_value, d_longitude_value, mode):
    """Return the origin, destination and travel mode as escaped text.

    Formerly a google.com/maps directions anchor; see get_google_map_link().
    """
    if o_latitude_value is None or o_longitude_value is None or d_latitude_value is None or d_longitude_value is None:
        return ""

    origin = f"{esc(o_latitude_value)}, {esc(o_longitude_value)}"
    destination = f"{esc(d_latitude_value)}, {esc(d_longitude_value)}"

    # Travel mode
    if mode == 1:
        travel_mode = " (walking)"
    elif mode == 4:
        travel_mode = " (driving)"
    else:
        travel_mode = ""

    return f"From {origin} to {destination}{travel_mode}"

@artifact_processor
def appleMapsTrips(context):
    files_found = context.get_files_found()

    LocalDB = '' 
    LocalDB_found = []

    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):   # skip -wal/-shm/-journal sidecar files
            LocalDB_found.append(str(file_found))
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        all_rows = get_sqlite_db_records(LocalDB, '''
        SELECT 
        CASE 
            WHEN trip.ZSTARTDATE < 0 THEN NULL 
            ELSE datetime(trip.ZSTARTDATE + 978307200, 'unixepoch') END as StartDateTime, 
        CASE 
            WHEN trip.ZSTOPDATE < 0 THEN NULL 
            ELSE  datetime(trip.ZSTOPDATE + 978307200, 'unixepoch') END as EndDateTime, 
        orig.ZLOCATIONLATITUDE as OriginLatitude, orig.ZLOCATIONLONGITUDE as OriginLongitude, dest.ZLOCATIONLATITUDE as DestinationLatitude, dest.ZLOCATIONLONGITUDE as DestinationLongitude,
        trip.ZPREDOMINANTMOTIONACTIVITYTYPE
        FROM ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO as trip LEFT OUTER JOIN
        ZRTLEARNEDLOCATIONOFINTERESTVISITMO as orig
        on trip.ZVISITIDENTIFIERORIGIN = orig.ZIDENTIFIER LEFT OUTER JOIN
        ZRTLEARNEDLOCATIONOFINTERESTVISITMO as dest
        on trip.ZVISITIDENTIFIERDESTINATION = dest.ZIDENTIFIER
        ''')
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6], get_google_dir_link(row[2], row[3], row[4], row[5], row[6]), context.get_relative_path(LocalDB)))

    data_headers = (('Start DateTime', 'datetime'), ('End DateTime', 'datetime'), 'Origin Latitude','Origin Longitude', 'Destination Latitude', 'Destination Longitude','ZZPREDOMINANTMOTIONACTIVITYTYPE', 'Google Maps Link','Source File')
    return data_headers, data_list, 'See source file(s) below:'

@artifact_processor
def appleMapsSignificantLocationsVisits(context):
    files_found = context.get_files_found()

    LocalDB = '' 
    LocalDB_found = []

    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):   # skip -wal/-shm/-journal sidecar files
            LocalDB_found.append(str(file_found))
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        all_rows = get_sqlite_db_records(LocalDB, '''
        SELECT m.ZNAME, m.ZCATEGORY, a.ZSUBTHOROUGHFARE || ' ' || a.ZTHOROUGHFARE as Address, a.ZLOCALITY, a.ZADMINISTRATIVEAREA, a.ZADMINISTRATIVEAREACODE, 
            a.ZCOUNTRY, a.ZPOSTALCODE, a.ZSUBLOCALITY, a.ZAREASOFINTEREST, m.ZLATITUDE, m.ZLONGITUDE, 
            datetime(p.ZCREATIONDATE + 978307200, 'unixepoch') as CreationDateTime
        FROM ZRTLEARNEDPLACEMO as p INNER JOIN
        ZRTADDRESSMO as a on p.ZMAPITEM = a.ZMAPITEM AND p.ZDEVICE = a.ZDEVICE INNER JOIN 
        ZRTMAPITEMMO as m on p.ZDEVICE = m.ZDEVICE AND p.ZMAPITEM = m.ZPLACE
        ''')
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], get_google_map_link(row[10], row[11]),row[12],context.get_relative_path(LocalDB)))

        all_rows = get_sqlite_db_records(LocalDB, '''
        SELECT NULL,NULL,NULL,NULL, NULL, NULL, NULL, NULL, NULL, NULL, p.ZLOCATIONLATITUDE, p.ZLOCATIONLONGITUDE, 
            datetime(p.ZPLACECREATIONDATE + 978307200, 'unixepoch') as CreationDateTime
        FROM ZRTLEARNEDLOCATIONOFINTERESTMO as p
        ''')
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], get_google_map_link(row[10], row[11]),row[12],context.get_relative_path(LocalDB)))

    data_headers = ('Significant Location Name', 'Category', 'Address','City', 'State', 'State-Abbrev',  'Country', 'Zip Code', 'ZSUBLOCALITY', 'ZAREASOFINTEREST', 'Latitude', 'Longitude', 'Google Maps Link', ('Created DateTime','datetime'), 'Source File')
    return data_headers, data_list, 'See source file(s) below:'

@artifact_processor
def appleMapsSignificantLocations(context):
    files_found = context.get_files_found()

    LocalDB = '' 
    LocalDB_found = []

    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):   # skip -wal/-shm/-journal sidecar files
            LocalDB_found.append(str(file_found))
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        all_rows = get_sqlite_db_records(LocalDB, '''
        SELECT  datetime(ZENTRYDATE + 978307200, 'unixepoch') as VicinityEntryDate,  
                datetime(ZEXITDATE + 978307200, 'unixepoch') as VicinityExitDate, 
                datetime(ZCREATIONDATE + 978307200, 'unixepoch') as CreatedDateTime, 
                ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE, ZLOCATIONHORIZONTALUNCERTAINTY  
        FROM ZRTLEARNEDLOCATIONOFINTERESTVISITMO
        ''')
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5], get_google_map_link(row[3], row[4]), context.get_relative_path(LocalDB)))

    data_headers = (('Vicinity Entry Datetime','datetime'), ('Vicinity Exit Datetime','datetime'), ('Created Datetime','datetime'), 'Latitude', 'Longitude', 'Uncertainty', 'Google Maps Link', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'