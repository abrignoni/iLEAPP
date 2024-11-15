__artifacts_v2__ = {
    "allTrailsTrailDetails": {
        "name": "AllTrails - Trail Details",
        "description": "Extract trail details from AllTrails App",
        "author": "@stark4n6",
        "version": "0.2",
        "date": "2022-04-28",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "",
        "paths": ('*/Documents/AllTrails.sqlite*'),
        "output_types": ["html", "tsv", "lava"]
    },
    "allTrailsUserInfo": {
        "name": "AllTrails - User Info",
        "description": "Extract user info from AllTrails App",
        "author": "@stark4n6",
        "version": "0.2",
        "date": "2022-04-28",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": "",
        "paths": ('*/Documents/AllTrails.sqlite*'),
        "output_types": "all"
    }
}


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset

@artifact_processor
def allTrailsTrailDetails(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('AllTrails.sqlite'):
            db_file = file_found
            break
    
    with open_sqlite_db_readonly(file_found) as db:
        cursor = db.cursor()
        cursor.execute('''
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
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], 
                    row[9], row[10], row[11], row[12], row[13], row[14], row[15],)
                )

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
    return data_headers, data_list, db_file


@artifact_processor
def allTrailsUserInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = None

    for file_found in files_found:
        if file_found.endswith('AllTrails.sqlite'):
            db_file = file_found
            break
    
    with open_sqlite_db_readonly(file_found) as db:
        cursor = db.cursor()
        
        cursor.execute('''
        SELECT 
            datetime(ZUSER.ZCREATIONTIME + 978307200,'unixepoch') AS "Creation Timestamp",
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
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            data_list.append(
                (timestamp, row[1], row[2], row[3], row[4], row[5], row[6], 
                    row[7], row[8], row[9], row[10], row[11], row[12], row[13])
                )

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
    return data_headers, data_list, db_file
