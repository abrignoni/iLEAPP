__artifacts_v2__ = {
    "callHistoryTransactions": {
        "name": "Call History Transactions",
        "description": "Parses transaction.log file in Call History Transactions",
        "author": "@JohnHyla",
        "version": "0.0.1",
        "date": "2024-12-11",
        "requirements": "none",
        "category": "Call History",
        "notes": "",
        "paths": ('*/var/mobile/Library/CallHistoryTransactions/transactions.log*'),
        "output_types": "standard"
    }
}

import os
import blackboxprotobuf
from datetime import *
import struct
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_ts_human_to_timezone_offset, \
    convert_plist_date_to_timezone_offset


@artifact_processor
def callHistoryTransactions(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
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
                date = convert_plist_date_to_timezone_offset(inner_record.get('date', ''), timezone_offset)
                data_list.append([date, inner_record['handleType'], inner_record['callStatus'],
                                  inner_record['duration'], inner_record['remoteParticipantHandles'][0]['value'],
                                  inner_record['callerId'], inner_record['timeToEstablish'],
                                  inner_record['disconnectedCause'], inner_record['uniqueId']])

    data_headers = [('Date', 'datetime'), 'handleType', 'callStatus', 'duration', 'remoteParticipantHandle', 'callerId',
                    'timeToEstablish', 'disconnectedCause', 'uniqueId']

    return data_headers, data_list, file_found


