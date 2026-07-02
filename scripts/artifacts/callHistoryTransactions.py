__artifacts_v2__ = {
    "callHistoryTransactions": {
        "name": "Call History Transactions",
        "description": "Parses transaction.log file in Call History Transactions",
        "author": "@JohnHyla",
        "creation_date": "2024-12-11",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/var/mobile/Library/CallHistoryTransactions/transactions.log*'),
        "output_types": "standard",
        "artifact_icon": "phone-call"
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

    for file_found in context.get_files_found():
        file_found = str(file_found)
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
                data_list.append((date, inner_record['handleType'], inner_record['callStatus'],
                                  inner_record['duration'], inner_record['remoteParticipantHandles'][0]['value'],
                                  inner_record['callerId'], inner_record['timeToEstablish'],
                                  inner_record['disconnectedCause'], inner_record['uniqueId'], context.get_relative_path(file_found)))

    data_headers = (('Date', 'datetime'), 'handleType', 'callStatus', 'duration', 'remoteParticipantHandle', 'callerId',
                    'timeToEstablish', 'disconnectedCause', 'uniqueId', 'Source File')

    return data_headers, data_list, 'see Source File for more info'


