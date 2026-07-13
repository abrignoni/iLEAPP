# Parts of this script have been modified from code
# found in Yogesh Khatri's mac_apt project Notes plugin (https://github.com/ydkhatri/mac_apt)
# and used under terms of the MIT License.
__artifacts_v2__ = {
    "notes": {
        "name": "Notes",
        "description": "Apple Notes including decoded note body text and embedded attachments",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Notes",
        "notes": "Note body text is decompressed and parsed from the protobuf blob. "
                 "Password-protected note contents are not decoded.",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | group.com.apple.notes | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | group.com.apple.notes | 0 rows",
            "felix_ios17": "iOS 17.6.1 | group.com.apple.notes | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | group.com.apple.notes | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | group.com.apple.notes | 0 rows",
            "iphone11_ios17": "iOS 17.3 | group.com.apple.notes | 0 rows",
            "iphone12_ios18": "iOS 18.7 | group.com.apple.notes | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | group.com.apple.notes | 0 rows",
            "otto_ios17": "iOS 17.5.1 | group.com.apple.notes | 0 rows",
            "abe_ios16": "iOS 16.5 | group.com.apple.notes | 0 rows",
            "felix23_ios16": "iOS 16.5 | group.com.apple.notes | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | group.com.apple.notes | 3 rows",
            "hickman_ios14": "iOS 14.3 | group.com.apple.notes | 7 rows",
            "jess_ios15": "iOS 15.0.2 | group.com.apple.notes | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | group.com.apple.notes | 0 rows",
        }
    }
}

import binascii
import os
import zlib
from os.path import dirname, join

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media,
                               does_column_exist_in_db, get_sqlite_db_records, logfunc)


def _build_query(creation_col, account_col):
    """Notes schema varies by iOS version; only the creation-date and account columns differ."""
    return f'''
    SELECT
        DATETIME(TabA.{creation_col}+978307200,'UNIXEPOCH'),
        TabA.ZTITLE1,
        TabA.ZSNIPPET,
        TabB.ZTITLE2,
        TabC.ZNAME,
        DATETIME(TabA.ZMODIFICATIONDATE1+978307200,'UNIXEPOCH'),
        CASE TabA.ZISPASSWORDPROTECTED WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        TabA.ZPASSWORDHINT,
        CASE TabA.ZMARKEDFORDELETION WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        CASE TabA.ZISPINNED WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        TabE.ZFILENAME,
        TabE.ZIDENTIFIER,
        TabD.ZFILESIZE,
        TabD.ZTYPEUTI,
        DATETIME(TabD.ZCREATIONDATE+978307200,'UNIXEPOCH'),
        DATETIME(TabD.ZMODIFICATIONDATE+978307200,'UNIXEPOCH'),
        TabF.ZDATA
    FROM ZICCLOUDSYNCINGOBJECT TabA
    INNER JOIN ZICCLOUDSYNCINGOBJECT TabB on TabA.ZFOLDER = TabB.Z_PK
    INNER JOIN ZICCLOUDSYNCINGOBJECT TabC on TabA.{account_col} = TabC.Z_PK
    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabD on TabA.Z_PK = TabD.ZNOTE
    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabE on TabD.Z_PK = TabE.ZATTACHMENT1
    LEFT JOIN ZICNOTEDATA TabF on TabF.ZNOTE = TabA.Z_PK
    '''


def _query_for_db(file_found):
    if does_column_exist_in_db(file_found, 'ZICCLOUDSYNCINGOBJECT', 'ZACCOUNT4'):
        if does_column_exist_in_db(file_found, 'ZICCLOUDSYNCINGOBJECT', 'ZCREATIONDATE3'):
            return _build_query('ZCREATIONDATE3', 'ZACCOUNT4')
        return _build_query('ZCREATIONDATE1', 'ZACCOUNT3')
    return _build_query('ZCREATIONDATE1', 'ZACCOUNT2')


def get_uncompressed_data(compressed):
    if compressed is None:
        return None
    try:
        return zlib.decompress(compressed, 15 + 32)
    except zlib.error:
        logfunc('Notes: zlib decompression failed')
        return None


def read_length_field(blob):
    '''Return a tuple (length, skip) where skip is the number of bytes read.'''
    length = 0
    skip = 0
    try:
        data_length = int(blob[0])
        length = data_length & 0x7F
        while data_length > 0x7F:
            skip += 1
            data_length = int(blob[skip])
            length = ((data_length & 0x7F) << (skip * 7)) + length
    except (IndexError, ValueError):
        logfunc('Error trying to read length field in note data blob')
    skip += 1
    return length, skip


def process_note_body_blob(blob):
    if blob is None:
        return ''
    try:
        pos = 0
        if blob[0:3] != b'\x08\x00\x12':  # header
            logfunc(f'Unexpected bytes in note header: {binascii.hexlify(blob[0:3])}')
            return ''
        pos += 3
        _, skip = read_length_field(blob[pos:])
        pos += skip
        if blob[pos:pos + 3] != b'\x08\x00\x10':  # header 2
            logfunc(f'Unexpected bytes in note header 2 at pos {pos}')
            return ''
        pos += 3
        _, skip = read_length_field(blob[pos:])
        pos += skip
        if blob[pos] != 0x1A:  # text header
            logfunc(f'Unexpected byte in note text header at pos {pos}')
            return ''
        pos += 1
        _, skip = read_length_field(blob[pos:])
        pos += skip
        if blob[pos] != 0x12:  # text tag
            logfunc(f'Unexpected byte at pos {pos}')
            return ''
        pos += 1
        length, skip = read_length_field(blob[pos:])
        pos += skip
        return blob[pos:pos + length].decode('utf-8', 'backslashreplace')
    except (IndexError, ValueError):
        logfunc('Error processing note data blob')
        return ''


@artifact_processor
def notes(context):
    data_headers = (
        ('Creation Date', 'datetime'), 'Note Title', 'Snippet', 'Note Contents', 'Folder',
        'Storage Place', ('Last Modified', 'datetime'), 'Password Protected', 'Password Hint',
        'Marked for Deletion', 'Pinned', ('Attachment', 'media'), 'Attachment Original Filename',
        'Attachment Storage Folder', 'Attachment Size in KB', 'Attachment Type',
        ('Attachment Creation Date', 'datetime'), ('Attachment Last Modified', 'datetime'))
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue

        rows = get_sqlite_db_records(file_found, _query_for_db(file_found))
        # if not rows:
        #     continue
        # NOTE: if the generator is empty, it won't loop, so we don't have to
        #   skip it here

        for row in rows:
            if row[6] == 'No' and row[16] is not None:
                text_content = process_note_body_blob(get_uncompressed_data(row[16]))
            else:
                text_content = ''

            media_ref = None
            attachment_storage = ''
            filename, identifier = row[10], row[11]
            if filename and identifier:
                attachment_file = join(dirname(file_found), 'Accounts/LocalAccount/Media',
                                       identifier, filename)
                attachment_storage = context.get_relative_path(dirname(attachment_file))
                if os.path.exists(attachment_file):
                    try:
                        with open(attachment_file, 'rb') as af:
                            media_ref = check_in_embedded_media(file_found, af.read(), filename)
                    except OSError as ex:
                        logfunc(f'Failed to read Notes attachment {attachment_file}: {ex}')

            if row[12] is not None:
                filesize = '.'.join(str(row[12])[i:i + 3] for i in range(0, len(str(row[12])), 3))
            else:
                filesize = ''

            data_list.append((row[0], row[1], row[2], text_content, row[3], row[4], row[5],
                              row[6], row[7], row[8], row[9], media_ref, row[10],
                              attachment_storage, filesize, row[13], row[14], row[15]))

        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
