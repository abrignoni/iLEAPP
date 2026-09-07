__artifacts_v2__ = {
    "mmkv_carved_records": {
        "name": "MMKV - Recovered Records",
        "description": "Records recovered from the device's MMKV stores, carved from the space past the recorded data region or read from a store whose recorded size is zero. Carved rows are inferences and some are wrong.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "MMKV",
        "notes": "Most of the rows here are carved, which is inference rather than parsing, and some of those rows are wrong. The Corroboration column separates them from the one case below that is not inferred. MMKV compacts a store by moving the surviving entries to the front of its data region with a memmove and lowering the recorded size (Tencent's MMKV_IO.cpp, memmoveDictionary and doFullWriteBack), and nothing zeroes what the move leaves behind. Space added to the file is zero filled straight after the ftruncate that adds it (MemoryFile.cpp), so what sits past the recorded size is content this store wrote earlier and not unrelated data left behind in the filesystem. This artifact reads records out of that space. There is no marker to synchronise on, so every byte offset is tested on its own and anything record-shaped is accepted: a key of 5 to 64 bytes that decodes as UTF-8 and is made only of letters, digits, underscore, hyphen, dollar, dot, slash and colon, followed by a value container that accounts for its own length, is a bare varint, or is the 4 or 8 bytes a float and a double are written as. A row is reported only where something corroborates it, and the Corroboration column says which: the key is also in that store's live region, or the same key was recovered more than once from that store. Uncorroborated single hits are not reported. Measured against data holding no MMKV structure at all, the same test returned nothing on zero-filled, natural-language and JSON input, between none and three records per mebibyte of random bytes, about 1.3 records per KiB on base64 text and about 35 per KiB on hexadecimal text, so a store whose values are encoded blobs would otherwise fill this table with records corresponding to nothing. Hexadecimal is the worst case because a decimal digit is itself a byte in the range a key length may take and the digits that follow it satisfy the character set. The space is deliberately absent from that character set: a space is byte 32, which is itself a valid key length, so allowing it makes running text read as records. A store whose recorded size is zero is a different case and is not carved. Clearing a store, and failing its CRC on load, both write a zero size into the meta file and leave the records in place, so that region is read by an ordinary walk of the layout and is reported only when the walk consumes whole entries and then meets nothing but the file's zero padding. Those rows say so in the Corroboration column and carry no offset, because nothing about them was inferred. A recovered record is not a deleted value. It is a write that was superseded or removed at some point before the store was last compacted, and nothing in the file establishes which of the two, or when. Offset gives the record's position in the source file so it can be located there. Values are reported as text exactly as stored: MMKV records a value's type in the calling code rather than in the file, so nothing here types them. A record whose header the compaction wrote over cannot be recovered at all: its key and lengths are gone and only a fragment of its value remains, with nothing to attribute it to. Those are not reported, so this table is not a complete account of what the space holds. Encrypted stores are skipped, because the space past their recorded region is ciphertext written under an earlier vector. Across the 1,840 MMKV stores in 78 tested extractions, counting a store as a file with a .crc sibling, 290 of the 1,710 that are not encrypted carried something other than zeros past the recorded size.",
        "paths": ('*/mmkv/*', '*/MMappedKV/*', '*/PIAMMKV/*'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 2,545 rows",
            "dexter_ios18": "iOS 18.3.2 | 7,480 rows",
            "hc_ios18_7": "iOS 18.7.8 | 371 rows",
            "hickman_ios14": "iOS 14.3 | 386 rows",
            "iphone12_ios18": "iOS 18.7 | 1,974 rows",
            "otto_ios17": "iOS 17.5.1 | 12,637 rows",
        },
    },
}

import os
from collections import Counter

from scripts.ilapfuncs import artifact_processor
from scripts.mmkv_parser import MMKVError, carve_slack, decode_value, read_entries

RESET = 'the store\'s recorded size is zero and the region walked cleanly to its padding'


def _render(container):
    """The value as text for the report; a removal marker says so.

    Everything is rendered as text. MMKV records a value's type in the calling code
    rather than in the file, so a carved container carries no type to honour, and a
    varint here can hold a number wider than a database integer column takes.
    """
    value = decode_value(container)
    if value is None:
        return '<removed>'
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def _store_rows(file_found, relative_path):
    """Rows for one store, or an empty list when there is nothing to report."""
    if os.path.isdir(file_found) or file_found.endswith('.crc'):
        return []
    try:
        live_entries = read_entries(file_found)
    except (MMKVError, OSError):
        # not an MMKV store, encrypted, or unreadable; reported by its absence
        return []

    if not live_entries:
        # A cleared store, or one whose CRC failed, keeps its records and reports a
        # size of zero. Reading those is a walk of the ordinary layout rather than a
        # carve, so they are reported whole and are not put through the tests below.
        try:
            recovered = read_entries(file_found, recover=True)
        except (MMKVError, OSError):
            recovered = []
        return [(key, _render(container), RESET, '', relative_path)
                for key, container in recovered]

    try:
        carved = carve_slack(file_found)
    except (MMKVError, OSError):
        return []
    counts = Counter(record.key for record in carved)
    rows = []
    for record in carved:
        if record.live_key:
            why = 'the key is also in the live region'
        elif counts[record.key] > 1:
            why = f'the key was recovered {counts[record.key]} times from this store'
        else:
            continue
        rows.append((record.key, _render(record.container), why,
                     record.offset, relative_path))
    return rows


@artifact_processor
def mmkv_carved_records(context):
    data_headers = (
        'Key',
        'Value',
        'Corroboration',
        'Offset',
        'Source File',
    )
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        rows = _store_rows(file_found, context.get_relative_path(file_found))
        if rows:
            data_list.extend(rows)
            sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)
