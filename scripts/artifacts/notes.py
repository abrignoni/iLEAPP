from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_notes(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
            DATETIME(TabA.ZCREATIONDATE1+978307200,'UNIXEPOCH'), 
            TabA.ZTITLE1, 
            TabB.ZTITLE2, 
            TabC.ZNAME, 
            DATETIME(TabA.ZMODIFICATIONDATE1+978307200,'UNIXEPOCH'),
            case TabA.ZISPASSWORDPROTECTED 
            when 0 then "No"
            when 1 then "Yes"
            end,
            case TabA.ZMARKEDFORDELETION
            when 0 then "No"
            when 1 then "Yes"
            end, 
            case TabA.ZISPINNED
            when 0 then "No"
            when 1 then "Yes"
            end,
            TabD.ZFILESIZE,
            TabD.ZTYPEUTI,
            DATETIME(TabD.ZCREATIONDATE+978307200,'UNIXEPOCH'), 
            DATETIME(TabD.ZMODIFICATIONDATE+978307200,'UNIXEPOCH')
            FROM ZICCLOUDSYNCINGOBJECT TabA
            INNER JOIN ZICCLOUDSYNCINGOBJECT TabB on TabA.ZFOLDER = TabB.Z_PK
            INNER JOIN ZICCLOUDSYNCINGOBJECT TabC on TabA.ZACCOUNT3 = TabC.Z_PK
            LEFT JOIN ZICCLOUDSYNCINGOBJECT TabD on TabA.Z_PK = TabD.ZNOTE
            WHERE TabA.ZTITLE1 <> ''
            ''')

        all_rows = cursor.fetchall()
    if len(all_rows) > 0:
        for row in all_rows:
            if row[8] is not None:
                filesize = '.'.join(str(row[8])[i:i+3] for i in range(0, len(str(row[8])), 3))
            else:
                filesize = ''
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], filesize, row[9], row[10], row[11]))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Notes')
        report.start_artifact_report(report_folder, 'Notes')
        report.add_script()
        data_headers = ('Creation Date', 'Note', 'Folder', 'Storage Place', 'Last Modified', 'Password Protected',
                        'Marked for Deletion', 'Pinned', 'Attachment Size in KB', 'Attachment Type',
                        'Attachment Creation Date', 'Attachment Last Modified')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Notes'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Notes'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Notes available')

    db.close()
    return
