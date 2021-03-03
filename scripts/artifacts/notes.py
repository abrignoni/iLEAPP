from os.path import dirname, join
from PIL import Image
import imghdr

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_notes(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT 
                DATETIME(TabA.ZCREATIONDATE1+978307200,'UNIXEPOCH'), 
                TabA.ZTITLE1,
                TabA.ZSNIPPET,
                TabB.ZTITLE2,
                TabC.ZNAME,
                DATETIME(TabA.ZMODIFICATIONDATE1+978307200,'UNIXEPOCH'),
                case TabA.ZISPASSWORDPROTECTED
                when 0 then "No"
                when 1 then "Yes"
                end,
                TabA.ZPASSWORDHINT,
                case TabA.ZMARKEDFORDELETION
                when 0 then "No"
                when 1 then "Yes"
                end,
                case TabA.ZISPINNED
                when 0 then "No"
                when 1 then "Yes"
                end,
                TabE.ZFILENAME,
                TabE.ZIDENTIFIER,
                TabD.ZFILESIZE,
                TabD.ZTYPEUTI,
                DATETIME(TabD.ZCREATIONDATE+978307200,'UNIXEPOCH'),
                DATETIME(TabD.ZMODIFICATIONDATE+978307200,'UNIXEPOCH')
                FROM ZICCLOUDSYNCINGOBJECT TabA
                INNER JOIN ZICCLOUDSYNCINGOBJECT TabB on TabA.ZFOLDER = TabB.Z_PK
                INNER JOIN ZICCLOUDSYNCINGOBJECT TabC on TabA.ZACCOUNT3 = TabC.Z_PK
                LEFT JOIN ZICCLOUDSYNCINGOBJECT TabD on TabA.Z_PK = TabD.ZNOTE
                LEFT JOIN ZICCLOUDSYNCINGOBJECT TabE on TabD.Z_PK = TabE.ZATTACHMENT1
                WHERE TabA.ZTITLE1 <> ''
                ''')

            all_rows = cursor.fetchall()
            analyzed_file = file_found

    if len(all_rows) > 0:
        for row in all_rows:

            if row[10] is not None and row[11] is not None:
                attachment_file = join(dirname(analyzed_file), 'Accounts/LocalAccount/Media', row[11], row[10])
                attachment_storage_path = dirname(attachment_file)
                if imghdr.what(attachment_file) == 'jpeg' or imghdr.what(attachment_file) == 'jpg' or imghdr.what(attachment_file) == 'png':
                    thumbnail_path = join(report_folder, 'thumbnail_'+row[10])
                    save_original_attachment_as_thumbnail(attachment_file, thumbnail_path)
                    thumbnail = '<img src="{}">'.format(thumbnail_path)
                else:
                    thumbnail = 'File is not an image or the filetype is not supported yet.'
            else:
                thumbnail = ''
                attachment_storage_path = ''

            if row[12] is not None:
                filesize = '.'.join(str(row[12])[i:i+3] for i in range(0, len(str(row[12])), 3))
            else:
                filesize = ''

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], thumbnail, row[10], attachment_storage_path, filesize, row[13], row[14], row[15]))

        report = ArtifactHtmlReport('Notes')
        report.start_artifact_report(report_folder, 'Notes')
        report.add_script()
        data_headers = ('Creation Date', 'Note', 'Snippet', 'Folder', 'Storage Place', 'Last Modified',
                        'Password Protected', 'Password Hint', 'Marked for Deletion', 'Pinned', 'Attachment Thumbnail',
                        'Attachment Original Filename', 'Attachment Storage Folder', 'Attachment Size in KB',
                        'Attachment Type', 'Attachment Creation Date', 'Attachment Last Modified')
        report.write_artifact_data_table(data_headers, data_list, analyzed_file, html_no_escape=['Attachment Thumbnail'])
        report.end_artifact_report()

        tsvname = 'Notes'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Notes'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Notes available')

    db.close()
    return


def save_original_attachment_as_thumbnail(file, store_path):
    image = Image.open(file)
    thumbnail_max_size = (350, 350)
    image.thumbnail(thumbnail_max_size)
    image.save(store_path)
