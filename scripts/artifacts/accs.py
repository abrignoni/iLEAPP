import os
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly 


def get_accs(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute("""
    select
    datetime(zdate+978307200,'unixepoch','utc' ),
    zaccounttypedescription,
    zusername,
    zaccountdescription,
    zaccount.zidentifier,
    zaccount.zowningbundleid
    from zaccount, zaccounttype 
    where zaccounttype.z_pk=zaccount.zaccounttype
    """
    )

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))                
        report = ArtifactHtmlReport('Account Data')
        report.start_artifact_report(report_folder, 'Account Data')
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

        