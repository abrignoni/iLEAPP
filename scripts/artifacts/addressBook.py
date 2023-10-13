__artifacts_v2__ = {
    "addressbook": {
        "name": "Address Book Contacts",
        "description": "Extract information from the native contacts application",
        "author": "@AlexisBrignoni",
        "version": "0.3",
        "date": "2022-10-25",
        "requirements": "none",
        "category": "Address Book",
        "notes": "",
        "paths": ('**/AddressBook.sqlitedb*',),
        "function": "get_addressBook"
    }
}


import sqlite3
from datetime import datetime, timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_addressBook(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('.sqlitedb'):
            break
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    ABPerson.ROWID,
    c16Phone,
    FIRST,
    MIDDLE,
    LAST,
    c17Email,
    DATETIME(CREATIONDATE+978307200,'UNIXEPOCH'),
    DATETIME(MODIFICATIONDATE+978307200,'UNIXEPOCH'),
    NAME
    FROM ABPerson
    LEFT OUTER JOIN ABStore ON ABPerson.STOREID = ABStore.ROWID
    LEFT OUTER JOIN ABPersonFullTextSearch_content on ABPerson.ROWID = ABPersonFullTextSearch_content.ROWID
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            if row[1] is not None:
                try:
                    numbers = row[1].split(" +")
                    number = numbers[1].split(" ")
                    phone_number = "+{}".format(number[0])
                except:
                    phone_number = row[1]
            else:
                phone_number = ''
            
            creationdate = row[6]
            if creationdate is None:
                pass
            else:
                creationdate = convert_ts_human_to_utc(creationdate)
                creationdate = convert_utc_human_to_timezone(creationdate,timezone_offset)
            
            modifieddate = row[7]
            if modifieddate is None:
                pass
            else:
                modifieddate = convert_ts_human_to_utc(modifieddate)
                modifieddate = convert_utc_human_to_timezone(modifieddate,timezone_offset)
            
            data_list.append((creationdate,row[0], phone_number, row[2], row[3], row[4], row[5], modifieddate, row[8]))

        report = ArtifactHtmlReport('Address Book Contacts')
        report.start_artifact_report(report_folder, 'Address Book Contacts')
        report.add_script()
        data_headers = ('Creation Date','Contact ID', 'Contact Number', 'First Name', 'Middle Name', 'Last Name', 'Email Address', 'Modification Date', 'Storage Place')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Address Book'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Address Book'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Address Book data available')

    db.close()
    return

# __artifacts__ = {
#     "addressbook": (
#         "Address Book",
#         ('**/AddressBook.sqlitedb*'),
#         get_addressBook)
# }