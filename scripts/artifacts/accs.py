__artifacts_v2__ = {
    "accs": {
        "name": "Account Data",
        "description": "Extract information about configured user accounts",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-11-21",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/mobile/Library/Accounts/Accounts3.sqlite*'),
        "function": "get_accs"
    }
}


#from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone 

@artifact_processor(__artifacts_v2__["accs"])
def get_accs(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('Accounts3.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute('''
    select
        datetime(zdate+978307200,'unixepoch'),
        zaccounttypedescription,
        zusername,
        zaccountdescription,
        zaccount.zidentifier,
        zaccount.zowningbundleid
    from zaccount, zaccounttype 
    where zaccounttype.z_pk=zaccount.zaccounttype
    ''')

    all_rows = cursor.fetchall()

    data_list = []
    if len(all_rows) > 0:
        for row in all_rows:
            timestamp = row[0]
            if timestamp:
                timestamp = convert_ts_human_to_utc(timestamp)
                timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)
            
            data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5]))                
    else:
        logfunc("No Account Data available")

    db.close()

    data_headers = (('Timestamp', 'datetime'),'Account Desc.','Username','Description','Identifier','Bundle ID' )
    return data_headers, data_list, file_found
