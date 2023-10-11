import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime
import blackboxprotobuf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_kikGroupadmins(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        Z_9ADMINSINVERSE.Z_9ADMINSINVERSE, /*Group ID of group where user is an administrator. */
        ZKIKUSEREXTRA.ZENTITYUSERDATA, /*BLOB from ZKIKUSEREXTRA that contains additional user information. */
        ZKIKUSEREXTRA.ZROSTERENTRYDATA /*Field from ZKIKUSEREXTRA that contains additional user information*/
    From ZKIKUSER
    Inner Join Z_9ADMINSINVERSE On ZKIKUSER.Z_PK = Z_9ADMINSINVERSE.Z_9ADMINS /*(matched Z_PK from ZKIKUSER table with Z_9ADMINS from Z_9ADMINSINVERSE table)*/
    LEFT JOIN ZKIKUSEREXTRA On ZKIKUSER.Z_PK = ZKIKUSEREXTRA.ZUSER /*(matched Z_PK from ZKIKUSER with ZUSER from ZKIKUSEREXTRA)*/
order by Z_9ADMINSINVERSE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    finalintlist = ''
    blobuser = ''
    blobdesc = ''
    addinfousera = ''
    addinfouserb = ''
    addinfodisp = ''
    addinfdesc = ''
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
            
            if row[6] is None:
                pass
            else:
                addinfousera = ''
                addinfouserb = ''
                addinfodisp = ''
                addinfdesc = ''
                
                data, typess = blackboxprotobuf.decode_message(row[6])
                addinfousera = data['1']['1']
                if type(addinfousera) is dict:
                    addinfousera = ''
                else:
                    addinfousera = data['1']['1'].decode('utf-8')
                
                if data.get('2') is not None:
                    addinfdesc = data.get('2')['1']['1']
                    if type(addinfdesc) is dict:
                        addinfdesc = ''
                    else:
                        addinfdesc = data.get('2')['1']['1'].decode('utf-8')

                addinfouserb = data['3']['1'].decode('utf-8')
                
                addinfodisp = data['4']['1']
                if type(addinfodisp) is dict:
                    addinfodisp = ''
                else:
                    addinfodisp = data['4']['1'].decode('utf-8')
            
            if row[5] is not None:

                finalintlist = ''
                blobuser = ''
                blobdesc = ''
                
                data, typess = blackboxprotobuf.decode_message(row[5])
                
                if (data['1'].get('5')) is not None:
                    listofinterests = (data['1']['5']['1'])
                    for x in listofinterests:
                        finalintlist = (x['2'].decode('utf-8')) + ', ' + finalintlist #interests
                    finalintlist = finalintlist[:-2]
                    
                if type(data['1'].get('1')) is bytes:
                    blobuser = (data['1'].get('1').decode('utf-8')) #Username?
                if type(data['1'].get('1')) is dict:
                    if (data['1']['1'].get('1')) is not None:
                        blobdesc = (data['1']['1'].get('1').decode('utf-8')) #Description
                        
                if (data['1'].get('7')) is not None:
                    if type(data['1']['7'].get('1')) is dict:
                        pass #has a dictionary with values i dont care about
                    else:
                        blobname = ((data['1']['7'].get('1').decode('utf-8'))) #some name?
                if (data.get('102')) is not None:
                    blobpicfull = (data['102']['1']['2']['1'].decode('utf-8')) #profilepic full
                    blobpicthu = (data['102']['1']['2']['2'].decode('utf-8')) #profile pic thumb
                if (data.get('104')) is not None:
                    listofinterests = data['104']['1']
                    for x in listofinterests:
                        finalintlist = (x['2'].decode('utf-8')) + ', ' + finalintlist #interests
                    finalintlist = finalintlist[:-2]
            
            data_list.append((row[0],row[1],row[2],row[3],row[4],grouptag,groupdname,zjid, zpurl, blobuser, blobdesc, finalintlist,addinfousera, addinfouserb, addinfodisp, addinfdesc))
            
            
        description = 'Kik users that are Administrators of a group.'
        report = ArtifactHtmlReport('Kik Group Administrators')
        report.start_artifact_report(report_folder, 'Kik Group Administrators', description)
        report.add_script()
        data_headers = ('User ID','Display Name','Username','Profile Pic URL','Member Group ID','Group Tag','Group Name','Group ID','Group Pic URL','Blob User','Blob Description','Blob Interests','Additional Info User','Additional Info User','Additional Info Display', 'Additional Info Value' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Kik Group Administrators'
        tsv(report_folder, data_headers, data_list, tsvname)
    
    else:
        logfunc('No Kik Group Administrators data available')
    
    
__artifacts__ = {
    "kikGroupadmins": (
        "Kik",
        ('*/kik.sqlite*'),
        get_kikGroupadmins)
}
        