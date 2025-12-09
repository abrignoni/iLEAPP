__artifacts_v2__ = {
    "get_mailprotect": {
        "function": "get_mailprotect",
        "name": "Apple Email",
        "description": "Apple Email.",
        "author": "@abrignoni - @stark4n6",
        "version": "0.3",
        "creation_date": "2020-05-07",
        "last_update_date": "2025-02-05",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": "",
        "paths": ('*/mobile/Library/Mail/* Index*'),
        "output_types": "none",
        "artifact_icon": "mail"
    }
}

import glob
import os
import pathlib
import plistlib
import sqlite3
import json
import textwrap
 
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, attach_sqlite_db_readonly, is_platform_windows, open_sqlite_db_readonly, iOS
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.parse3 import ParseProto

def get_mailprotect(files_found, report_folder, seeker, wrap_text, timezone_offset):
    iOSversion = iOS.get_version()
    
    envelope_db = ''
    protected_db = ''
    
    for file_found in files_found:
        if file_found.endswith('Envelope Index'):
            envelope_db = file_found
        if file_found.endswith('Protected Index'):
            protected_db = file_found
        else:
            continue

    if version.parse(iOSversion) <= version.parse("11"):
        logfunc("Unsupported version for iOS emails in iOS " + iOSversion)
        return ()

    if version.parse(iOSversion) < version.parse("13"):
        head, end = os.path.split(envelope_db)
        db = sqlite3.connect(os.path.join(report_folder, "emails.db"))
        cursor = db.cursor()
        cursor.execute(
            """
        create table email1(rowid int, ds text, dr text, size int, sender text, messid int, subject text, receipt text, cc text, bcc text)
        """
        )
        db.commit()

        cursor.execute(
            """
        create table email2(rowid int, data text)
        """
        )
        db.commit()
        db.close()

        with open_sqlite_db_readonly(os.path.join(head, "Envelope Index")) as db:
            # [PENTING] Inisialisasi cursor baru dari koneksi DB yang baru dibuka
            cursor = db.cursor() 

            # Baru kemudian lakukan ATTACH
            attach_query = attach_sqlite_db_readonly(f"{head}/Protected Index", 'PI')
            cursor.execute(attach_query)
            
            attach_query = attach_sqlite_db_readonly(f"{report_folder}/emails.db", 'emails')
            cursor.execute(attach_query)
            
            # Baris di bawah ini (baris 73 lama) bisa dihapus atau dibiarkan 
            # (tapi redundant karena sudah didefinisikan di atas)
            # cursor = db.cursor()
            cursor.execute(
                """
            select  
            main.messages.ROWID,
            main.messages.date_sent,
            main.messages.date_received,
            main.messages.size,
            PI.messages.sender,
            PI.messages.message_id,
            PI.messages.subject,
            PI.messages._to,
            PI.messages.cc,
            PI.messages.bcc
            from main.messages, PI.messages
            where main.messages.ROWID =  PI.messages.message_id 
            """
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                print(f"Total emails {usageentries}")
                for row in all_rows:
                    # print(row)
                    datainsert = (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                    )
                    cursor.execute(
                        "INSERT INTO emails.email1 (rowid, ds, dr, size, sender, messid, subject, receipt, cc, bcc) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        datainsert,
                    )
                    db.commit()
            else:
                print("Zero rows")

            cursor = db.cursor()
            cursor.execute(
                """
            select  
            main.messages.ROWID,
            PI.message_data.data
            from main.message_data, main.messages, PI.messages, PI.message_data
            where main.messages.ROWID = main.message_data.message_id and PI.messages.message_id = main.message_data.message_id 
            and PI.message_data.message_data_id = main.message_data.ROWID
            """
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                print(f"Total emails with message data {usageentries}")
                for row in all_rows:
                    datainsert = (
                        row[0],
                        row[1],
                    )
                    cursor.execute(
                        "INSERT INTO emails.email2 (rowid, data)  VALUES(?,?)",
                        datainsert,
                    )
                    db.commit()
            else:
                print("Zero rows")

            cursor.execute(
                """
            select 
            email1.rowid,
            datetime(email1.ds, 'unixepoch') as ds,
            datetime(email1.dr, 'unixepoch') as dr,
            email1.sender, 
            email1.messid, 
            email1.subject, 
            email1.receipt, 
            email1.cc,
            email1.bcc,
            email2.data 
            from email1
            left outer join email2
            on email2.rowid = email1.rowid
            """
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = [] 
                for row in all_rows:
                    timestampds = convert_ts_human_to_utc(row[1])
                    timestampds = convert_utc_human_to_timezone(timestampds,timezone_offset)
                    
                    timestampdr = convert_ts_human_to_utc(row[2])
                    timestampdr = convert_utc_human_to_timezone(timestampdr,timezone_offset)
                    
                    data_list.append((timestampds,timestampdr,row[3],row[4],row[5],row[6],row[9],row[7],row[8],row[0]))
                
                file_found = head
                description = ''
                report = ArtifactHtmlReport('Apple Email')
                report.start_artifact_report(report_folder, 'Emails', description)
                report.add_script()
                data_headers = ('Date Sent','Date Received','Sender','Message ID', 'Subject', 'Recipient', 'Message', 'CC', 'BCC','Row ID')     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'iOS Mail'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'iOS Mail'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                #LAVA Section
                data_headers = ['Date Sent','Date Received','Sender','Message ID', 'Subject', 'Recipient', 'Message', 'CC', 'BCC','Row ID']
                
                data_headers[0] = (data_headers[0], 'datetime')
                data_headers[1] = (data_headers[1], 'datetime')
                
                category = "Apple Email"
                module_name = "get_mailprotect"
                
                table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Apple Email', data_headers, len(data_list))
                
                lava_insert_sqlite_data(table_name1, data_list, object_columns1, data_headers, column_map1)
                   
            else:
                logfunc("No iOS emails available")
        db.close()

    if version.parse(iOSversion) >= version.parse("13"):
        head, end = os.path.split(envelope_db)
        with open_sqlite_db_readonly(os.path.join(head, "Envelope Index")) as db:
            attach_query = attach_sqlite_db_readonly(f"{head}/Protected Index", 'PI')

            cursor = db.cursor()
            cursor.execute(attach_query)
            
            cursor.execute(
                """
            SELECT
            datetime(main.messages.date_sent, 'UNIXEPOCH') as datesent,
            datetime(main.messages.date_received, 'UNIXEPOCH') as datereceived,
            PI.addresses.address,
            PI.addresses.comment,
            PI.subjects.subject,
            PI.summaries.summary,
            main.messages.read,
            main.messages.flagged,
            main.messages.deleted,
            main.mailboxes.url
            from main.mailboxes, main.messages, PI.subjects, PI.addresses, PI.summaries
            where main.messages.subject = PI.subjects.ROWID 
            and main.messages.sender = PI.addresses.ROWID 
            and main.messages.summary = PI.summaries.ROWID
            and main.mailboxes.ROWID = main.messages.mailbox
            """
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = [] 
                for row in all_rows:
                    timestampds = convert_ts_human_to_utc(row[0])
                    timestampds = convert_utc_human_to_timezone(timestampds,timezone_offset)
                    
                    timestampdr = convert_ts_human_to_utc(row[1])
                    timestampdr = convert_utc_human_to_timezone(timestampdr,timezone_offset)
                    
                    data_list.append((timestampds,timestampdr,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
                
                file_found = head
                description = ''
                report = ArtifactHtmlReport('Apple Email')
                report.start_artifact_report(report_folder, 'Emails', description)
                report.add_script()
                data_headers = ('Date Sent','Date Received','Address','Comment','Subject', 'Summary', 'Read?', 'Flagged?', 'Deleted', 'Mailbox')     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Apple Mail'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Apple Mail'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                #LAVA Section
                data_headers = ['Date Sent','Date Received','Address','Comment','Subject', 'Summary', 'Read?', 'Flagged?', 'Deleted', 'Mailbox']
                
                data_headers[0] = (data_headers[0], 'datetime')
                data_headers[1] = (data_headers[1], 'datetime')
                
                category = "Apple Email"
                module_name = "get_mailprotect"
                
                table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Apple Email', data_headers, len(data_list))
                
                lava_insert_sqlite_data(table_name1, data_list, object_columns1, data_headers, column_map1)
                    
            else:
                logfunc("No Apple Mail emails available")