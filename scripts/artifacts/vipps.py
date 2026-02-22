import io
import nska_deserialize as nd
import plistlib
import json
from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db


@artifact_processor
def get_vipps(files_found, report_folder, seeker, wrap_text, time_offset):
    file_found = str(files_found[0])
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

    for row in all_rows:
        plist_file_object = io.BytesIO(row[4])
        if row[4].find(b'NSKeyedArchiver') == -1:
            plist = plistlib.load(plist_file_object)
        else:
            try:
                plist = nd.deserialize_plist(plist_file_object)
            except (nd.DeserializeError, nd.biplist.NotBinaryPlistException, nd.biplist.InvalidPlistException,
                    nd.plistlib.InvalidFileException, nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
                logfunc(f'Failed to read plist for {row[0]}, error was:' + str(ex))

        for _, y in plist.items():
            jsonitems = json.loads(y)
            telephone = row[0].split('-')[1]

            cursor1 = db.cursor()
            cursor1.execute('''
            SELECT
            ZNAME,
            ZRAWPHONENUMBERS,
            ZPROFILEIMAGEDATA,
            ZCONTACTSTOREIDENTIFIER
            FROM ZCONTACTMODEL
            WHERE ZRAWPHONENUMBERS LIKE ?
            ''', ('%' + telephone + '%',))
            all_rows1 = cursor1.fetchall()

            name = ''
            if len(all_rows1) > 0:
                for row1 in all_rows1:
                    name = row1[0]
            else:
                # Check if ZPHONENUMBERS exists, if so, use it instead
                if does_column_exist_in_db(file_found, 'ZCONTACTMODEL', 'ZPHONENUMBERS'):
                    cursor1.execute('''
                    SELECT
                    ZNAME,
                    ZPHONENUMBERS,
                    ZPROFILEIMAGEDATA,
                    ZCONTACTSTOREIDENTIFIER
                    FROM ZCONTACTMODEL
                    WHERE ZPHONENUMBERS LIKE ?
                    ''', ('%' + telephone + '%',))
                    all_rows1 = cursor1.fetchall()

                    if len(all_rows1) > 0:
                        for row1 in all_rows1:
                            name = row1[0]
                            break

            data = (telephone, name)
            if jsonitems['model'] == "CHAT":
                for key in jsonitems['data'].keys():
                    data += (jsonitems['data'][key],)
            data_list.append(data)

    db.close()

    data_headers = ('Telephone', 'Name', 'Message', 'Amount', 'Status Text',
                    'Status Category', 'Direction', 'Transaction ID', 'Type')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_vipps": {
        "name": "Vipps Transactions",
        "description": "Vipps mobile payment transactions.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Vipps",
        "notes": "",
        "paths": ('*/Vipps.sqlite*',),
        "output_types": "all",
        "artifact_icon": "credit-card"
    }
}
