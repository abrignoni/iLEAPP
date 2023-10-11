# Secret Calculator Photo Album (xyz.hypertornado.calculator)
# Author:  John Hyla
# Version: 1.0.0
#
#   Description:
#   Obtains photos/videos stored in the Secret Calculator Photo Album and their corresponding album
#


import biplist
import plistlib
import pathlib
import sys


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, sanitize_file_name, media_to_html


def get_secretCalculator(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:

        with open(file_found, "rb") as fp:
            if sys.version_info >= (3, 9):
                plist = plistlib.load(fp)
            else:
                plist = biplist.readPlist(fp)
            bundleid = plist['MCMMetadataIdentifier']
            if bundleid == 'xyz.hypertornado.calculator':
                if is_platform_windows():
                    split_on = '\\private\\'
                else:
                    split_on = '/private/'
                p = str(pathlib.Path(file_found).parent).split(split_on, 1)
                file = f'**{p[1]}/Library/data.sqlite'
                if is_platform_windows():
                    file.replace('/', '\\')
                db_file = seeker.search(file, return_on_first_hit=True)
                if not db_file:
                    logfunc(' [!] Unable to extract db file: "{}"'.format(db_file))
                    return

                db = open_sqlite_db_readonly(db_file[0])

                cursor = db.cursor()
                cursor.execute('''
                    SELECT
                    datetime(Photos.date,'UNIXEPOCH') AS photoDate,
                    datetime(Albums.date,'UNIXEPOCH') AS albumDate,
                    Photos.path,
                    Photos.video,
                    Albums.name
                    from Photos
                    left join Albums on Photos.id = Albums.id
                    ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                data_list = []

                if usageentries > 0:
                    for row in all_rows:

                        fileNameToSearch = f'/private/{p[1]}/Library/Data/{row[2]}.mov'
                        if is_platform_windows():
                            fileNameToSearch.replace('/', '\\')
                        seekerResults = seeker.search(f'**{fileNameToSearch}', return_on_first_hit=True)
                        thumb = None
                        attachmentFile = None
                        if seekerResults:
                            attachmentFile = seekerResults[0]
                            thumb = media_to_html(attachmentFile, (attachmentFile,), report_folder)
                        data_list.append((row[0], thumb, row[4], row[1], fileNameToSearch.replace('\\', '/'), row[3]))

                description = 'Secret Calculator'
                report = ArtifactHtmlReport('Secret Calculator')
                report.start_artifact_report(report_folder, 'Secret Calculator', description)
                report.add_script()
                data_headers = ('Date', 'File', 'Album', 'Album Date', 'Filename', 'Is Video')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['File'])
                report.end_artifact_report()

                tsvname = 'Secret Calculator'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Secret Calculator'
                timeline(report_folder, tlactivity, data_list, data_headers)

    db.close()
    return
    
__artifacts__ = {
    "secretCalculatorPhotoAlbum": (
        "Secret Calculator Photo Album",
        ('**mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        get_secretCalculator)
}
