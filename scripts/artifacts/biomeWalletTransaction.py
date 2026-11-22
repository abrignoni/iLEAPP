__artifacts_v2__ = {
    "get_biomeWalletTransaction": {
        "name": "Biome - Wallet Transactions",
        "description": "Parses Wallet transaction events from the Wallet.Transaction biome "
                       "stream: record time, a card name, a pass identifier and a UUID, as "
                       "labelled from a private sample.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field mapped from a private sample of this stream. On the tested images the "
                 "stream held 8 rows, 1 written, on dexter_ios18 and wilkerson_iphone16_ios26; "
                 "the written record had Transaction Type 1 (Payment) and Merchant Type 0 "
                 "(Unknown). The stream folder name on disk is "
                 "singular: Wallet.Transaction. The Transaction Type and Merchant Type field "
                 "names and their value names are those of the BMWalletTransaction class, read "
                 "from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class "
                 "was read. The class reads only data version 0 (the unnamed integer the SEGB reader "
                 "returns with each entry); a record of another version, or a value outside the class's "
                 "lists, keeps its integer in the (raw) column with the name blank. Transaction "
                 "Type was reported before as Field 3 (raw) and Merchant Type as Field 5 (raw). "
                 "The class names the fields shown here as Card Name, Pass ID and Transaction UUID "
                 "passLocalizedDescription, passUniqueID and transactionID.",
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

# transactionType and merchantType names, read from BiomeLibrary.framework
# BMWalletTransaction on macOS 27.2.1 (26B131). The class reads only data version 0 (the
# unnamed int the SEGB reader returns per entry); other versions get no name, and so do values the
# class renders only as its fallback.
TRANSACTION_TYPE_BY_VERSION = {
    0: dict(enumerate(('Unknown', 'Payment', 'VAS', 'Transit', 'Access', 'EMoney',
                       'Identity'))),
}
MERCHANT_TYPE_BY_VERSION = {
    0: dict(enumerate(('Unknown', 'FoodAndDrinks', 'Shopping', 'Travel', 'Services', 'Fun',
                       'Health', 'Transport'))),
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
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
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
                transaction_type = protostuff.get('3', '')
                merchant_type = protostuff.get('5', '')
                version = getattr(record, '_unknown_value', None)

                data_list.append((ts, record.state.name, card_name, pass_id, transaction_uuid,
                                  TRANSACTION_TYPE_BY_VERSION.get(version, {}).get(
                                      transaction_type, ''),
                                  transaction_type,
                                  MERCHANT_TYPE_BY_VERSION.get(version, {}).get(
                                      merchant_type, ''),
                                  merchant_type, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Card Name', 'Pass ID',
                    'Transaction UUID', 'Transaction Type', 'Transaction Type (raw)',
                    'Merchant Type', 'Merchant Type (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
