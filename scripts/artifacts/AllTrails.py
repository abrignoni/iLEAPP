import sqlite3
import textwrap
from datetime import datetime, timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_AllTrails(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('AllTrails.sqlite'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        Select 
        ZTRAIL.ZNAME,
        ZTRAIL.ZROUTETYPENAME,
        CASE ZACTIVITYSTATS.ZDIFFICULTY
            WHEN 1 THEN 'Easy'
            WHEN 3 THEN 'Moderate'
            WHEN 5 THEN 'Hard'
        END,
        ZTRAIL.ZRATING,
        ZTRAIL.ZREVIEWCOUNT,
        ZTRAIL.ZLENGTH as "Length (Meters)",
        ZTRAIL.ZELEVATIONGAIN as "Elevation Gain (Meters)",
        ZLOCATION.ZLATITUDE,
        ZLOCATION.ZLONGITUDE,
        ZLOCATION.ZCITY,
        ZLOCATION.ZREGION,
        ZLOCATION.ZREGIONNAME,
        ZLOCATION.ZPOSTALCODE,
        ZLOCATION.ZCOUNTRY,
        ZLOCATION.ZCOUNTRYNAME,
        ZPARKAREA.ZNAME as "Park Area Name"
        From ZLOCATION
        Join ZTRAIL On ZLOCATION.Z_PK = ZTRAIL.ZLOCATION
        Join ZPARKAREA On ZTRAIL.Z_PK = ZPARKAREA.ZTRAIL
        Join ZACTIVITYSTATS On ZTRAIL.Z_PK = ZACTIVITYSTATS.ZTRAIL
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('AllTrails - Trail Details')
            report.start_artifact_report(report_folder, 'AllTrails - Trail Details')
            report.add_script()
            data_headers = ('Trail Name','Route Type','Trail Difficulty','Rating','Review Count','Length (Meters)','Elevation Gain (Meters)','Latitude','Longitude','City','State/Region','State/Region Name','Zip Code','Country','Country Name','Parking Area Name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'AllTrails - Trail Details'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No AllTrails - Trail Details data available')
        
        cursor.execute('''
        Select 
        datetime(ZUSER.ZCREATIONTIME + 978307200,'unixepoch') as "Creation Timestamp",
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
        From ZUSER
        Inner Join ZPROFILE On ZUSER.Z_PK = ZPROFILE.ZUSER
        Inner Join ZLOCATION On ZUSER.ZLOCATION = ZLOCATION.Z_PK
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('AllTrails - User Info')
            report.start_artifact_report(report_folder, 'AllTrails - User Info')
            report.add_script()
            data_headers = ('Creation Timestamp','First Name','Last Name','User Name','Email','Referral Link','Latitude','Longitude','City','Region','Region Name','Country','Country Name','Zip Code') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                timestamp = convert_ts_human_to_utc(row[0])
                timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)
                data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'AllTrails - User Info'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'AllTrails - User Info'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No AllTrails - User Info data available')

        db.close()
        return

__artifacts__ = {
    "alltrails": (
        "AllTrails",
        ('**/Documents/AllTrails.sqlite*'),
        get_AllTrails)
}
