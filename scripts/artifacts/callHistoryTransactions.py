__artifacts_v2__ = {
    "callHistoryTransactions": {
        "name": "Call History Transactions",
        "description": "Parses the records of the transactions.log file in the CallHistoryTransactions folder. Only the first remote participant handle of each record is shown.",
        "author": "@JohnHyla",
        "creation_date": "2024-12-11",
        "last_update_date": "2026-11-03",
        "requirements": "none",
        "category": "Call History",
        "notes": "The pattern without var/ finds the file where the extraction holds the Data "
                 "volume under a folder of its own: abe_ios16, felix23_ios16 and hickman_ios15 "
                 "store it as filesystem2/mobile/, and the var/ pattern matched nothing there. It "
                 "is also the shape of a raw image of the Data volume alone, which was checked on "
                 "extractions' path listings with private/var removed, not on a raw image. A field "
                 "a record does not hold is left blank: neither record on hickman_ios15 held "
                 "disconnectedCause.",
        "paths": ('*/var/mobile/Library/CallHistoryTransactions/transactions.log*',
                  '*/mobile/Library/CallHistoryTransactions/transactions.log*'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows, transactions.log was empty",
            "felix23_ios16": "iOS 16.5 | 0 rows, transactions.log was empty",
            "hickman_ios15": "iOS 15 | 2 rows",
        }
    }
}

import struct
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, \
    convert_plist_date_to_utc

from datetime import datetime as _dt

def _safe_plist_date(value):
    """Convert plist <date> objects to UTC; pass strings/None through unchanged."""
    return convert_plist_date_to_utc(value) if isinstance(value, _dt) else value



@artifact_processor
def callHistoryTransactions(context):
    data_list = []
    source_files = set()

    for file_found in context.get_files_found():
        file_found = str(file_found)
        source_files.add(file_found)
        with open(file_found, 'rb') as file:
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

            while file.tell() < file_size:
                length = struct.unpack('<I', file.read(4))[0]
                plist_data = file.read(length)
                ds_plist = nd.deserialize_plist_from_string(plist_data)
                inner_record = nd.deserialize_plist_from_string(ds_plist['record'])
                date = _safe_plist_date(inner_record.get('date', ''))
                handles = inner_record.get('remoteParticipantHandles') or [{}]
                data_list.append((date, inner_record.get('handleType', ''), inner_record.get('callStatus', ''),
                                  inner_record.get('duration', ''), handles[0].get('value', ''),
                                  inner_record.get('callerId', ''), inner_record.get('timeToEstablish', ''),
                                  inner_record.get('disconnectedCause', ''), inner_record.get('uniqueId', ''),
                                  context.get_relative_path(file_found)))

    data_headers = (('Date', 'datetime'), 'handleType', 'callStatus', 'duration', 'remoteParticipantHandle', 'callerId',
                    'timeToEstablish', 'disconnectedCause', 'uniqueId', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_files))


