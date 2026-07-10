__artifacts_v2__ = {
    "appleMapsTrips": {
        "name": "Apple Maps Trips",
        "description": "Examines the ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO and ZRTLEARNEDLOCATIONOFINTERESTVISITMO tables. The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence. For details: https://doubleblak.com/blogPost.php?k=Locations",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
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
        }
    },
    "appleMapsSignificantLocations": {
        "name": "Apple Maps Significant Locations",
        "description": "The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
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
        }
    },
    "appleMapsSignificantLocationsVisits": {
        "name": "Apple Maps Significant Locations Visits",
        "description": "The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
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
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

def get_google_map_link(latitude_value, longitude_value):
    if latitude_value is None or longitude_value is None:
        return ""
    
    return f"<a href='https://www.google.com/maps?q={latitude_value},{longitude_value}' target='_blank'>https://www.google.com/maps?q={latitude_value},{longitude_value}</a>"

def get_google_dir_link(o_latitude_value, o_longitude_value, d_latitude_value, d_longitude_value, mode):
    if o_latitude_value is None or o_longitude_value is None or d_latitude_value is None or d_longitude_value is None:
        return ""
    
    base_url = "https://www.google.com/maps/dir/?api=1"
    origin = f"&origin={o_latitude_value},{o_longitude_value}"
    destination = f"&destination={d_latitude_value},{d_longitude_value}"

    # Travel mode
    if mode == 1:
        travel_mode = "&travelmode=walking"
    elif mode == 4:
        travel_mode = "&travelmode=driving"
    else:
        travel_mode = ""

    url = base_url + origin + destination + travel_mode

    return f"<a href='{url}' target='_blank'>{url}</a>"

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