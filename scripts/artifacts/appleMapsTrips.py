__artifacts_v2__ = {
    "appleMapsTrips": {
        "name": "Apple Maps Trips",
        "description": "Examines the ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO and ZRTLEARNEDLOCATIONOFINTERESTVISITMO tables. The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence. For details: https://doubleblak.com/blogPost.php?k=Locations",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin"
    },
    "appleMapsSignificantLocations": {
        "name": "Apple Maps Significant Locations",
        "description": "The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin"
    },
    "appleMapsSignificantLocationsVisits": {
        "name": "Apple Maps Significant Locations Visits",
        "description": "The Google Maps Link are constructed from the coordinates. They DO NOT exist in the evidence.",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/Library/Caches/com.apple.routined/Local.sqlite*',
                  '*/Library/Caches/com.apple.routined/Cloud-V2.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "html_columns": ["Google Maps Link"],
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

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
        
        LocalDB = str(file_found)
        LocalDB_found.append(LocalDB)
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        db = open_sqlite_db_readonly(LocalDB)
        cursor = db.cursor()
        cursor.execute('''
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

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6], get_google_dir_link(row[2], row[3], row[4], row[5], row[6]), LocalDB))

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
        
        LocalDB = str(file_found)
        LocalDB_found.append(LocalDB)
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        db = open_sqlite_db_readonly(LocalDB)
        cursor = db.cursor()
        cursor.execute('''
        SELECT m.ZNAME, m.ZCATEGORY, a.ZSUBTHOROUGHFARE || ' ' || a.ZTHOROUGHFARE as Address, a.ZLOCALITY, a.ZADMINISTRATIVEAREA, a.ZADMINISTRATIVEAREACODE, 
            a.ZCOUNTRY, a.ZPOSTALCODE, a.ZSUBLOCALITY, a.ZAREASOFINTEREST, m.ZLATITUDE, m.ZLONGITUDE, 
            datetime(p.ZCREATIONDATE + 978307200, 'unixepoch') as CreationDateTime
        FROM ZRTLEARNEDPLACEMO as p INNER JOIN
        ZRTADDRESSMO as a on p.ZMAPITEM = a.ZMAPITEM AND p.ZDEVICE = a.ZDEVICE INNER JOIN 
        ZRTMAPITEMMO as m on p.ZDEVICE = m.ZDEVICE AND p.ZMAPITEM = m.ZPLACE
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], get_google_map_link(row[10], row[11]),row[12],LocalDB))

        cursor.execute('''
        SELECT NULL,NULL,NULL,NULL, NULL, NULL, NULL, NULL, NULL, NULL, p.ZLOCATIONLATITUDE, p.ZLOCATIONLONGITUDE, 
            datetime(p.ZPLACECREATIONDATE + 978307200, 'unixepoch') as CreationDateTime
        FROM ZRTLEARNEDLOCATIONOFINTERESTMO as p
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], get_google_map_link(row[10], row[11]),row[12],LocalDB))

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
        
        LocalDB = str(file_found)
        LocalDB_found.append(LocalDB)
        
    for i in range(len(LocalDB_found)):
        LocalDB = LocalDB_found[i]
        
        db = open_sqlite_db_readonly(LocalDB)
        cursor = db.cursor()
        cursor.execute('''
        SELECT  datetime(ZENTRYDATE + 978307200, 'unixepoch') as VicinityEntryDate,  
                datetime(ZEXITDATE + 978307200, 'unixepoch') as VicinityExitDate, 
                datetime(ZCREATIONDATE + 978307200, 'unixepoch') as CreatedDateTime, 
                ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE, ZLOCATIONHORIZONTALUNCERTAINTY  
        FROM ZRTLEARNEDLOCATIONOFINTERESTVISITMO
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)

            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5], get_google_map_link(row[3], row[4]), LocalDB))

    data_headers = (('Vicinity Entry Datetime','datetime'), ('Vicinity Exit Datetime','datetime'), ('Created Datetime','datetime'), 'Latitude', 'Longitude', 'Uncertainty', 'Google Maps Link', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'