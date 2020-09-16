import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_interactionCcontacts(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("10"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(ZINTERACTIONS.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(ZINTERACTIONS.ZENDDATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            ZINTERACTIONS.ZBUNDLEID AS "BUNDLE ID",
            ZCONTACTS.ZDISPLAYNAME AS "DISPLAY NAME",
            ZCONTACTS.ZIDENTIFIER AS "IDENTIFIER",
            ZCONTACTS.ZPERSONID AS "PERSONID",
            ZINTERACTIONS.ZDIRECTION AS "DIRECTION",
            ZINTERACTIONS.ZISRESPONSE AS "IS RESPONSE",
            ZINTERACTIONS.ZMECHANISM AS "MECHANISM",
            ZINTERACTIONS.ZRECIPIENTCOUNT AS "RECIPIENT COUNT",
            DATETIME(ZINTERACTIONS.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ZINTERACTIONS CREATION DATE",
            DATETIME(ZCONTACTS.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ZCONTACTS CREATION DATE",
            DATETIME(ZCONTACTS.ZFIRSTINCOMINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "FIRST INCOMING RECIPIENT DATE",
            DATETIME(ZCONTACTS.ZFIRSTINCOMINGSENDERDATE + 978307200, 'UNIXEPOCH') AS "FIRST INCOMING SENDER DATE",
            DATETIME(ZCONTACTS.ZFIRSTOUTGOINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "FIRST OUTGOING RECIPIENT DATE",
            DATETIME(ZCONTACTS.ZLASTINCOMINGSENDERDATE + 978307200, 'UNIXEPOCH') AS "LAST INCOMING SENDER DATE",
            CASE
                ZLASTINCOMINGRECIPIENTDATE 
                WHEN
                    "0" 
                THEN
                    "0" 
                ELSE
                    DATETIME(ZCONTACTS.ZLASTINCOMINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') 
            END AS "LAST INCOMING RECIPIENT DATE", 
            DATETIME(ZCONTACTS.ZLASTOUTGOINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "LAST OUTGOING RECIPIENT DATE", 
            ZINTERACTIONS.ZACCOUNT AS "ACCOUNT", 
            ZINTERACTIONS.ZDOMAINIDENTIFIER AS "DOMAIN IDENTIFIER", 
            ZCONTACTS.ZINCOMINGRECIPIENTCOUNT AS "INCOMING RECIPIENT COUNT", 
            ZCONTACTS.ZINCOMINGSENDERCOUNT AS "INCOMING SENDER COUNT", 
            ZCONTACTS.ZOUTGOINGRECIPIENTCOUNT AS "OUTGOING RECIPIENT COUNT", 
            ZCONTACTS.ZCUSTOMIDENTIFIER AS "CUSTOM IDENTIFIER", 
            ZINTERACTIONS.ZCONTENTURL AS "CONTENT URL", 
            ZINTERACTIONS.ZLOCATIONUUID AS "LOCATION UUID", 
            ZINTERACTIONS.Z_PK AS "ZINTERACTIONS TABLE ID" 
        FROM
            ZINTERACTIONS 
            LEFT JOIN
                ZCONTACTS 
                ON ZINTERACTIONS.ZSENDER = ZCONTACTS.Z_PK
        ''')
    else:
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(ZINTERACTIONS.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(ZINTERACTIONS.ZENDDATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            DATETIME(ZINTERACTIONS.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ZINTERACTIONS CREATION DATE",
            ZINTERACTIONS.ZBUNDLEID AS "BUNDLE ID",
            ZCONTACTS.ZDISPLAYNAME AS "DISPLAY NAME",
            ZCONTACTS.ZIDENTIFIER AS "IDENTIFIER",
            ZCONTACTS.ZPERSONID AS "PERSONID",
            ZINTERACTIONS.ZDIRECTION AS "DIRECTION",
            ZINTERACTIONS.ZISRESPONSE AS "IS RESPONSE",
            ZINTERACTIONS.ZMECHANISM AS "MECHANISM",
            DATETIME(ZCONTACTS.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "ZCONTACTS CREATION DATE",
            DATETIME(ZCONTACTS.ZFIRSTINCOMINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "FIRST INCOMING RECIPIENT DATE",
            DATETIME(ZCONTACTS.ZFIRSTINCOMINGSENDERDATE + 978307200, 'UNIXEPOCH') AS "FIRST INCOMING SENDER DATE",
            DATETIME(ZCONTACTS.ZFIRSTOUTGOINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "FIRST OUTGOING RECIPIENT DATE",
            DATETIME(ZCONTACTS.ZLASTINCOMINGSENDERDATE + 978307200, 'UNIXEPOCH') AS "LAST INCOMING SENDER DATE",
            CASE
                ZLASTINCOMINGRECIPIENTDATE 
                WHEN
                    "0" 
                THEN
                    "0" 
                ELSE
                    DATETIME(ZCONTACTS.ZLASTINCOMINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') 
            END AS "LAST INCOMING RECIPIENT DATE", 
            DATETIME(ZCONTACTS.ZLASTOUTGOINGRECIPIENTDATE + 978307200, 'UNIXEPOCH') AS "LAST OUTGOING RECIPIENT DATE", 
            ZINTERACTIONS.ZACCOUNT AS "ACCOUNT", 
            ZINTERACTIONS.ZDOMAINIDENTIFIER AS "DOMAIN IDENTIFIER", 
            ZCONTACTS.ZINCOMINGRECIPIENTCOUNT AS "INCOMING RECIPIENT COUNT", 
            ZCONTACTS.ZINCOMINGSENDERCOUNT AS "INCOMING SENDER COUNT", 
            ZCONTACTS.ZOUTGOINGRECIPIENTCOUNT AS "OUTGOING RECIPIENT COUNT", 
            ZINTERACTIONS.ZCONTENTURL AS "CONTENT URL", 
            ZINTERACTIONS.ZLOCATIONUUID AS "LOCATION UUID", 
            ZINTERACTIONS.Z_PK AS "ZINTERACTIONS TABLE ID" 
        FROM
            ZINTERACTIONS 
            LEFT JOIN
                ZCONTACTS 
                ON ZINTERACTIONS.ZSENDER = ZCONTACTS.Z_PK
        ''')
        
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        if version.parse(iOSversion) >= version.parse("10"):
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26]))

            report = ArtifactHtmlReport('InteractionC')
            report.start_artifact_report(report_folder, 'Contacts')
            report.add_script()
            data_headers = ('Start Date','End Date','Bundle ID','Display Name','Identifier','Person ID','Direction','Is Response','Mechanism','Recipient Count','Zinteractions Creation Date','Zcontacs Creation Date','First Incoming Recipient Date', 'First Incoming Sender Date','First Outgoing Recipient Date','Last Incoming Sender Date','Last Incoming Recipient Date','Last Outgoing Recipient Date','Account','Domain Identifier','Incoming Recipient Count','Incoming Sender Count','Outgoing Recepient Count','Custom Identifier','Content URL','Location UUID','Zinteractions Table ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'InteractionC Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractonC Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            for row in all_rows:    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24]))
            
            report = ArtifactHtmlReport('InteractionC')
            report.start_artifact_report(report_folder, 'Contacts')
            report.add_script()
            data_headers = ('Start Date','End Date','Zinteractions Creation Date','Bundle ID','Display Name','Identifier','Person ID','Direction','Is Response','Mechanism','Zcontacs Creation Date','First Incoming Recipient Date', 'First Incoming Sender Date','First Outgoing Recipient Date','Last Incoming Sender Date','Last Incoming Recipient Date','Last Outgoing Recipient Date','Account','Domain Identifier','Incoming Recipient Count','Incoming Sender Count','Outgoing Recipient Count','Content URL','Location UUID','Zinteractions Table ID' )  
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'InteractionC Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractionC Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return      
    
    
