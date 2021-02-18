import shutil
import json
from os import listdir
from re import search, DOTALL
from os.path import isfile, join, basename, dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_appleWalletPasses(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('json'):
            unique_id = search(r'(?<=ards/)(.*?)(?=.pkpass)', dirname(file_found), flags=DOTALL).group(0)
            filename = '{}_{}'.format(unique_id, basename(file_found))
            shutil.copyfile(file_found, join(report_folder, filename))

        json_files = [join(report_folder, file) for file in listdir(report_folder) if isfile(join(report_folder, file))]

        if file_found.endswith('.sqlite3'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''SELECT UNIQUE_ID, ORGANIZATION_NAME, TYPE_ID, LOCALIZED_DESCRIPTION, 
                            DATETIME(INGESTED_DATE + 978307200,'UNIXEPOCH'), DELETE_PENDING, ENCODED_PASS, 
                            FRONT_FIELD_BUCKETS, BACK_FIELD_BUCKETS
                            FROM PASS
                            ''')

            all_rows = cursor.fetchall()
            db_file = file_found

    if len(all_rows) > 0:
        for row in all_rows:
            for json_file in json_files:
                if row[0] in basename(json_file):

                    # noinspection PyBroadException
                    try:
                        with open(json_file) as json_content:
                            json_data = json.load(json_content)
                    except Exception:
                        json_data = 'Malformed data'

                    encoded_pass = str(row[6], 'utf-8', 'ignore')
                    front_field = str(row[7], 'utf-8', 'ignore')
                    back_field = str(row[8], 'utf-8', 'ignore')
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], json_data, front_field, back_field, encoded_pass))

        report = ArtifactHtmlReport('Passes')
        report.start_artifact_report(report_folder, 'Passes')
        report.add_script()
        data_headers = ('Unique ID', 'Organization Name', 'Type', 'Localized Description', 'Pass Added',
                        'Pending Delete', 'Pass Details', 'Front Fields Content', 'Back Fields Content', 'Encoded Pass')
        report.write_artifact_data_table(data_headers, data_list, db_file)
        report.end_artifact_report()

        tsvname = 'Apple Wallet Passes'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Apple Wallet Passes'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Apple Wallet Passes available')

    db.close()
    return
