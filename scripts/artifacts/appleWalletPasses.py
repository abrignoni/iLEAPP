import json
import nska_deserialize as nd
from os import listdir
from re import search, DOTALL
from os.path import isfile, join, basename, dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_appleWalletPasses(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_list_json = []
    all_rowsc = 0
    counter = 0
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('pass.json'):
            with open(file_found, 'r') as f:
                data = json.load(f)
                desc = ''
                for x, y in data.items():
                    data_list_json.append((x,y))
                    if x == 'description':
                        desc = y
            
            
            if len(data_list_json) > 0:
                
                if desc == '':
                    counter = counter + 1
                    desc = counter
                
                report = ArtifactHtmlReport('PK Passes')
                report.start_artifact_report(report_folder, f'PK Pass - {desc}')
                report.add_script()
                data_headers = ('Key','Value')
                report.write_artifact_data_table(data_headers, data_list_json, file_found)
                report.end_artifact_report()
                
                tsvname = 'PK Passes'
                tsv(report_folder, data_headers, data_list_json, tsvname)
                

            else:
                logfunc('No PK passes available')
            
        
        if file_found.endswith('.sqlite3'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''SELECT UNIQUE_ID, ORGANIZATION_NAME, TYPE_ID, LOCALIZED_DESCRIPTION, 
                            DATETIME(INGESTED_DATE + 978307200,'UNIXEPOCH'), DELETE_PENDING, ENCODED_PASS, 
                            FRONT_FIELD_BUCKETS, BACK_FIELD_BUCKETS
                            FROM PASS
                            ''')

            all_rows = cursor.fetchall()
            all_rowsc = len(all_rows)
    

            if all_rowsc > 0:
                for row in all_rows:
                    typeID = row[2]
                    
                    agg = ''
                    encoded_pass = nd.deserialize_plist_from_string(row[6])
                    for x in encoded_pass:
                        if isinstance(x, list):
                            for a in x:
                                agg = agg + f'{a}<br><br>'
                        elif isinstance(x, dict):
                            for y,z in x.items():
                                agg = agg + f'{y}: {z}<br><br>'
                        else:
                            agg = agg + f'{x}<br>'
                    encoded_pass = agg + f'<br>'
                    
                    agg = ''
                    front_field = nd.deserialize_plist_from_string(row[7])
                    for x in front_field:
                        if isinstance(x, list):
                            for a in x:
                                agg = agg + f'{a}<br><br>'
                        elif isinstance(x, dict):
                            for y,z in x.items():
                                agg = agg + f'{y}: {z}<br><br>'
                        else:
                            agg = agg + f'{x}<br>'
                    front_field = agg + f'<br>'
                    
                    agg = ''
                    back_field = nd.deserialize_plist_from_string(row[8])
                    for x in back_field:
                        if isinstance(x, list):
                            for a in x:
                                agg = agg + f'{a}<br><br>'
                        elif isinstance(x, dict):
                            for y,z in x.items():
                                agg = agg + f'{y}: {z}<br>'
                        else:
                            agg = agg + f'{x}<br>'
                            
                    back_field = agg
                    
                    timestamp = convert_ts_human_to_utc(row[4])
                    timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)
                    
                    data_list.append((timestamp, row[0], row[1], row[2], row[3], row[5], front_field, back_field, encoded_pass))
        
                report = ArtifactHtmlReport('Nano Passes')
                report.start_artifact_report(report_folder, f'Nano Pass - {typeID}')
                report.add_script()
                data_headers = ('Pass Added','Unique ID', 'Organization Name', 'Type', 'Localized Description',
                                'Pending Delete', 'Front Fields Content', 'Back Fields Content', 'Encoded Pass')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Front Fields Content', 'Back Fields Content', 'Encoded Pass'])
                report.end_artifact_report()
        
                tsvname = 'Nano Passes'
                tsv(report_folder, data_headers, data_list, tsvname)
        
                tlactivity = 'Nano Passes'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Nano Passes available')

__artifacts__ = {
    "applewalletpasses": (
        "Apple Wallet",
        ('**/nanopasses.sqlite3*', '**/Cards/*.pkpass/pass.json'),
        get_appleWalletPasses)
}