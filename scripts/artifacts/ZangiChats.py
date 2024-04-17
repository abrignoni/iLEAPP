#Update line 3-13
__artifacts_v2__ = {
    "Zangi_Chats": {
        "name": "Zangi Chats",
        "description": "Parses Zangi Chat database",
        "author": "Matt Beers",
        "version": "0.0.1",
        "date": "2024-04-16",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Shared/AppGroup/*/zangidb.sqlite*'),
        "function": "get_zangichats"#update line 22 to match this
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_zangichats(files_found, report_folder, seeker, wrap_text, time_offset):#your def variable should match what you have after function on line 13.
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('zangidb.sqlite'):#put the database name here
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            #SQL QUERY TIME! START YOUR QUERY AT THE SELECT STATEMENT. ITS A REQUIREMENT TO HAVE YOUR TIMESTAMPE FIRST FOR LEAPP ARTIFACTS
            cursor.execute('''
            select
	    datetime(ZZANGIMESSAGE.ZMESSAGETIME+978307200, 'unixepoch') AS 'MESSAGE DATE/TIME',
	    ZCONTACT.ZFIRSTNAME,
	    ZCONTACT.ZLASTNAME,
	    ZZANGIMESSAGE.ZMESSAGE,
	    CASE ZZANGIMESSAGE.ZISRECEIVED
	    WHEN '0' THEN 'SENT'
	    WHEN '1' THEN 'RECEIVED'
	    ELSE 'unknown'
	    END AS DIRECTION,
	    ZZNUMBER.ZNUMBER
	    FROM ZZANGIMESSAGE
	    JOIN ZZNUMBER ON ZZANGIMESSAGE.ZFROM = ZZNUMBER.ZCONTACTNUMBEROBJECT
	    left JOIN ZCONTACT ON ZZNUMBER.ZIDENTIFIRE = ZCONTACT.ZIDENTIFIRE
	    order by ZZANGIMESSAGE.ZMESSAGETIME DESC;--
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                #    last_mod_date = row[0]
                #   if last_mod_date is None:
                #       pass
                #   else:
                #       last_mod_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_mod_date),time_offset)
                
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))#**IMPORTANT THIS IS FOR HOW MANY TABLES ARE LISTED IN YOUR QUERY. IS MORE THAN 7 ADD MORE ROW, IF LESS REMOVE ROW. ROW MUST START AT ROW 0
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Zangi Chats' #THIS SHOWS UP ON THE REPORT SIDE
        report = ArtifactHtmlReport('Zangi Chats')#THIS IS WHAT SHOWS UP ON THE RIGHT SIDE OF THE HTML REPORT
        report.start_artifact_report(report_folder, 'Zangi Chats', description)
        report.add_script()
        data_headers = ('Timestamp','First Name','Last Name','Message Text','Direction','Number')#THIS IS WHERE YOU DEFINE THE COLUMN NAMES THAT SHOW UP IN THE REPORT AND SHOULD FOLLOW THE ORDER OF YOUR QUERY. 
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Zangi Chats'#UPDATE THIS TO MATCH YOUR ARTIFACT
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Zangi Chats'#UPDATE THIS TO MATCH YOUR ARTIFACT
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Zangi data available')#if not found in extractions, this is where it logs it wasn't found. update the name.
