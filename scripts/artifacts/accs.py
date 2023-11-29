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


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone 


def get_accs(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('/Accounts3.sqlite'):
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
    '''
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    if usageentries > 0:
        data_list = []
        for row in all_rows:
            timestamp = row[0]
            if timestamp:
                timestamp = convert_ts_human_to_utc(timestamp)
                timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)
            
            data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5]))                

        description = "Configured user accounts"
        report = ArtifactHtmlReport('Account Data')
        report.start_artifact_report(report_folder, 'Account Data', description)
        report.add_script()
        data_headers = ('Timestamp','Account Desc.','Username','Description','Identifier','Bundle ID' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Account Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Account Data'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc("No Account Data available")

    db.close()
