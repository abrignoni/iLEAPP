__artifacts_v2__ = {
    "allTrailsTrailDetails": {
        "name": "AllTrails - Trail Details",
        "description": "Extract trail details from AllTrails App",
        "author": "@stark4n6",
        "creation_date": "2022-04-28",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "",
        "paths": ('*/Documents/AllTrails.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map"
    },
    "allTrailsUserInfo": {
        "name": "AllTrails - User Info",
        "description": "Extract user info from AllTrails App",
        "author": "@stark4n6",
        "creation_date": "2022-04-28",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "",
        "paths": ('*/Documents/AllTrails.sqlite*'),
        "output_types": "all",
        "artifact_icon": "user"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def allTrailsTrailDetails(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "AllTrails.sqlite")
    data_list = []

    query = '''
    SELECT 
        ZTRAIL.ZNAME,
        ZTRAIL.ZROUTETYPENAME,
        CASE ZACTIVITYSTATS.ZDIFFICULTY
            WHEN 1 THEN 'Easy'
            WHEN 3 THEN 'Moderate'
            WHEN 5 THEN 'Hard'
        END,
        ZTRAIL.ZRATING,
        ZTRAIL.ZREVIEWCOUNT,
        ZTRAIL.ZLENGTH AS "Length (Meters)",
        ZTRAIL.ZELEVATIONGAIN AS "Elevation Gain (Meters)",
        ZLOCATION.ZLATITUDE,
        ZLOCATION.ZLONGITUDE,
        ZLOCATION.ZCITY,
        ZLOCATION.ZREGION,
        ZLOCATION.ZREGIONNAME,
        ZLOCATION.ZPOSTALCODE,
        ZLOCATION.ZCOUNTRY,
        ZLOCATION.ZCOUNTRYNAME,
        ZPARKAREA.ZNAME AS "Park Area Name"
    FROM ZLOCATION
    JOIN ZTRAIL ON ZLOCATION.Z_PK = ZTRAIL.ZLOCATION
    JOIN ZPARKAREA ON ZTRAIL.Z_PK = ZPARKAREA.ZTRAIL
    JOIN ZACTIVITYSTATS ON ZTRAIL.Z_PK = ZACTIVITYSTATS.ZTRAIL
    '''

    data_headers = (
        'Trail Name', 
        'Route Type', 
        'Trail Difficulty', 
        'Rating',
        'Review Count',
        'Length (Meters)', 
        'Elevation Gain (Meters)', 
        'Latitude', 
        'Longitude', 
        'City', 
        'State/Region', 
        'State/Region Name', 
        'Zip Code', 
        'Country', 
        'Country Name', 
        'Parking Area Name'
        )
    
    data_list = get_sqlite_db_records(source_path, query)

    return data_headers, data_list, source_path


@artifact_processor
def allTrailsUserInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "AllTrails.sqlite")
    data_list = []

    query = '''
    SELECT 
        ZUSER.ZCREATIONTIME,
        ZUSER.ZFIRSTNAME,
        ZUSER.ZLASTNAME,
        ZUSER.ZUSERNAME,
        ZPROFILE.ZEMAIL,
        ZUSER.ZREFERRALLINK,
        ZLOCATION.ZLATITUDE,
        ZLOCATION.ZLONGITUDE,
        ZLOCATION.ZCITY,
        ZLOCATION.ZREGION,
        ZLOCATION.ZREGIONNAME,
        ZLOCATION.ZCOUNTRY,
        ZLOCATION.ZCOUNTRYNAME,
        ZLOCATION.ZPOSTALCODE
    FROM ZUSER
    INNER JOIN ZPROFILE ON ZUSER.Z_PK = ZPROFILE.ZUSER
    INNER JOIN ZLOCATION ON ZUSER.ZLOCATION = ZLOCATION.Z_PK
    '''

    data_headers = (
        ('Creation Timestamp', 'datetime'), 
        'First Name', 
        'Last Name', 
        'User Name', 
        'Email', 
        'Referral Link', 
        'Latitude', 
        'Longitude', 
        'City', 
        'Region', 
        'Region Name', 
        'Country', 
        'Country Name', 
        'Zip Code'
        )

    db_records = get_sqlite_db_records(source_path, query)    

    for record in db_records:
        creation_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append(
            (creation_timestamp, record[1], record[2], record[3], record[4], record[5], record[6], 
             record[7], record[8], record[9], record[10], record[11], record[12], record[13]))

    return data_headers, data_list, source_path
