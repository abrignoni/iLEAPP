import io
import nska_deserialize as nd
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_vipps(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    
    data_list = []
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT 
    ZFEEDMODELKEY, 
    ZMODELTYPE, 
    ZSTATUS, 
    ZVIPPSTRANSACTIONID, 
    ZBLOB 
    FROM ZFEEDDETAILMODEL
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:
            plist_file_object = io.BytesIO(row[4])
            if row[4].find(b'NSKeyedArchiver') == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)
                except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                        nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                    logfunc(f'Failed to read plist for {row[0]}, error was:' + str(ex))
                
            for i, y in plist.items():
                jsonitems = json.loads(y)
                telephone = row[0].split('-')[1]

                cursor1 = db.cursor()
                cursor1.execute(f'''
                SELECT 
                ZNAME,
                ZPHONENUMBERS,
                ZPROFILEIMAGEDATA,
                ZCONTACTSTOREIDENTIFIER
                FROM ZCONTACTMODEL
                WHERE ZPHONENUMBERS LIKE "%{telephone}%"
                ''')
                all_rows1 = cursor1.fetchall()
                usageentries1 = len(all_rows1)
                
                if usageentries1 > 0:
                    for row1 in all_rows1:
                        name = row1[0]
                
                timestamp = (jsonitems['data']['messageTimeStamp'].replace('T', ' '). replace('Z', '').strip())
                message = (jsonitems['data']['message'])
                amount = (jsonitems['data'].get('amount', ''))
                statustext = (jsonitems['data'].get('statusText', ''))
                statuscat = (jsonitems['data'].get('statusCategory', ''))
                direction = (jsonitems['data']['direction'])
                transcaid = (jsonitems['data'].get('transactionId', ''))
                dtype = (jsonitems['data']['type'])
            
            data_list.append((timestamp, telephone, name, message, amount, statustext, statuscat, direction, transcaid, dtype))

        report = ArtifactHtmlReport('Vipps - Transactions')
        report.start_artifact_report(report_folder, 'Vipps - Transactions')
        report.add_script()
        data_headers = ('Timestamp', 'Telephone', 'Name', 'Message','Amount','Status Text','Status Category','Direction','Transaction ID','Type')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Vipps'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Vipps'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        db.close()
    else:
        logfunc('No data available for Vipps')
    
__artifacts__ = {
    "vipps": (
        "Vipps",
        ('*/Vipps.sqlite*'),
        get_vipps)
}