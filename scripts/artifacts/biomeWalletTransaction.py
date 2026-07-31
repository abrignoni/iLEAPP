__artifacts_v2__ = {
    "get_biomeWalletTransaction": {
        "name": "Biome - Wallet Transactions",
        "description": "Parses Wallet transaction events from the Wallet.Transaction biome "
                       "stream: record time, the card used (name as shown in Wallet), the "
                       "pass identifier and a per-transaction UUID.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field mapped from a private sample of this stream; the stream is absent from "
                 "the iOS 17 and iOS 18 test images. The stream folder name on disk is "
                 "singular: Wallet.Transaction.",
        "paths": ('*/streams/*/Wallet.Transaction/local/*',),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
        },
    }
}


import os
import struct
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Pin flat fields so card/pass strings are never eagerly decoded as nested protobuf.
TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '5': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


@artifact_processor
def get_biomeWalletTransaction(context):

    data_list = []
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Wallet Transactions: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                card_name = _to_str(protostuff.get('2', b''))
                pass_id = _to_str(protostuff.get('1', b''))
                transaction_uuid = _to_str(protostuff.get('4', b''))
                field3 = protostuff.get('3', '')
                field5 = protostuff.get('5', '')

                data_list.append((ts, record.state.name, card_name, pass_id, transaction_uuid,
                                  field3, field5, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Card Name', 'Pass ID',
                    'Transaction UUID', 'Field 3 (raw)', 'Field 5 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
