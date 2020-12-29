import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_addressBook(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    ABPerson.ROWID,
    VALUE,
    FIRST,
    MIDDLE,
    LAST,
    DATETIME(CREATIONDATE+978307200,'UNIXEPOCH'),
    DATETIME(MODIFICATIONDATE+978307200,'UNIXEPOCH'),
    NAME
    FROM ABPerson
    LEFT OUTER JOIN ABMultiValue ON ABPerson.ROWID = ABMultiValue.RECORD_ID
    LEFT OUTER JOIN ABStore ON ABPerson.STOREID = ABStore.ROWID
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            an = str(row[0])
            an = an.replace("b'", "")
            an = an.replace("'", "")
            data_list.append((an, row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report = ArtifactHtmlReport('Address Book Contacts')
        report.start_artifact_report(report_folder, 'Address Book Contacts')
        report.add_script()
        data_headers = ('Contact ID', 'Contact Number', 'First Name', 'Middle Name', 'Last Name', 'Creation Date', 'Modification Date', 'Storage Place')
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
