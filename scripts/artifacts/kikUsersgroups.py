import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_kikUsersgroups(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('kik.sqlite'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select ZKIKUSER.Z_PK, /*User ID*/
        ZKIKUSER.ZDISPLAYNAME, /*Display Name*/
        ZKIKUSER.ZUSERNAME, /*Username, if available*/
        ZKIKUSER.ZPPURL, /*Profile Picture URL*/
        Z_9MEMBERS.Z_9MEMBERSINVERSE, /*Group ID of group where user is a member. */
        ZKIKUSEREXTRA.ZENTITYUSERDATA, /*BLOB from ZKIKUSEREXTRA that contains additional user information. */
        ZKIKUSEREXTRA.ZROSTERENTRYDATA /*Field from ZKIKUSEREXTRA that contains additional user information*/
    From ZKIKUSER
        INNER Join Z_9MEMBERS On ZKIKUSER.Z_PK = Z_9MEMBERS.Z_9MEMBERS /*(joined Z_PK from ZKIKUSER table with Z_9MEMBERS in Z_9MEMBERS table)*/
        LEFT JOIN ZKIKUSEREXTRA On ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER /*(matched Z_PK from ZKIKUSER with ZUSER from ZKIKUSEREXTRA)*/
    order by Z_9MEMBERSINVERSE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:

        for row in all_rows:
        
            cursor2 = db.cursor()
            cursor2.execute(f'''
            SELECT ZGROUPTAG,
                ZDISPLAYNAME,
                ZJID,
                ZPPURL
            FROM ZKIKUSER 
            WHERE Z_PK = {row[4]}
            ''')
            
            all_rows2 = cursor2.fetchall()
            for rows2 in all_rows2:
                grouptag = rows2[0]
                groupdname = rows2[1]
                zjid = rows2[2]
                zpurl = rows2[3]
            
            data_list.append((row[0],row[1],row[2],row[3],row[4],grouptag,groupdname,zjid, zpurl,row[5],row[6]))
            
            
        description = 'Kik users that are members of a group.'
        report = ArtifactHtmlReport('Kik Users in Groups')
        report.start_artifact_report(report_folder, 'Kik Users in Groups', description)
        report.add_script()
        data_headers = ('User ID','Display Name','Username','Profile Pic URL','Member Group ID','Group Tag','Group Name','Group ID','Group Pic URL','Blob','Additional Information')     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Kik Users in Groups'
        tsv(report_folder, data_headers, data_list, tsvname)
    
    else:
        logfunc('No Kik Users in Groups data available')
    
__artifacts__ = {
    "kikUsersgroups": (
        "Kik",
        ('*/kik.sqlite*'),
        get_kikUsersgroups)
}
   
    
        