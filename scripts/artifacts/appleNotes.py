# Body decoding logic adapted from mac_apt Notes plugin by Yogesh Khatri
# (https://github.com/ydkhatri/mac_apt), used under the MIT License.
#
# NOTE: A legacy v1 plugin (notes.py) also parses this artifact.
# This is a modernised v2 rewrite using artifact_processor and get_sqlite_db_records.

__artifacts_v2__ = {
    "appleNotes": {
        "name": "Apple Notes",
        "description": "Extracts note metadata and plain-text body from the Notes app NoteStore database",
        "author": "@example_author",
        "creation_date": "2026-02-18",
        "last_update_date": "2026-02-18",
        "requirements": "none",
        "category": "Notes",
        "notes": "Body text is decoded from ZICNOTEDATA.ZDATA (gzip-compressed protobuf). "
                 "Locked (password-protected) notes return an empty body.",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "file-text"
    }
}

import zlib

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    does_column_exist_in_db,
    logfunc,
    convert_utc_human_to_timezone,
)


# ---------------------------------------------------------------------------
# Body decoding helpers
# ---------------------------------------------------------------------------

def _read_length_field(blob):
    """
    Read a protobuf varint from the start of blob.
    Returns (value, bytes_consumed).
    """
    value = 0
    skip = 0
    try:
        b = blob[0]
        value = b & 0x7F
        while b > 0x7F:
            skip += 1
            b = blob[skip]
            value |= (b & 0x7F) << (skip * 7)
    except (IndexError, ValueError):
        logfunc('appleNotes: error reading protobuf length field')
    return value, skip + 1


def _decode_note_body(zdata):
    """
    Decompress and parse the protobuf blob stored in ZICNOTEDATA.ZDATA.
    Returns the plain-text note body, or '' on any failure.

    On-disk layout (after gzip decompression):
      \x08\x00\x12  <varint: outer-field-2 length>
        \x08\x00\x10  <varint: skip>
        \x1A  <varint: field-3 length>
          \x12  <varint: text length>
            <UTF-8 text>
    """
    if not zdata:
        return ''
    try:
        data = zlib.decompress(bytes(zdata), 15 + 32)   # 15+32 = auto-detect gzip
    except zlib.error:
        return ''

    try:
        pos = 0
        if data[pos:pos + 3] != b'\x08\x00\x12':
            return ''
        pos += 3
        _, skip = _read_length_field(data[pos:])
        pos += skip                                      # now at start of outer-field-2 content

        if data[pos:pos + 3] != b'\x08\x00\x10':
            return ''
        pos += 3
        _, skip = _read_length_field(data[pos:])
        pos += skip                                      # skip the varint value

        if data[pos] != 0x1A:                            # field 3, wire-type 2
            return ''
        pos += 1
        _, skip = _read_length_field(data[pos:])
        pos += skip

        if data[pos] != 0x12:                            # field 2 inside field 3, wire-type 2
            return ''
        pos += 1
        length, skip = _read_length_field(data[pos:])
        pos += skip

        return data[pos:pos + length].decode('utf-8', 'backslashreplace')
    except (IndexError, ValueError):
        return ''


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------

@artifact_processor
def appleNotes(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, 'NoteStore.sqlite')
    data_list = []

    if not source_path:
        return (), data_list, source_path

    # Apple Notes uses a single polymorphic Core Data table (ZICCLOUDSYNCINGOBJECT)
    # for notes, folders, and accounts.  Column names shifted across iOS versions:
    #
    #   iOS 13+  — ZCREATIONDATE3, ZACCOUNT4
    #   iOS 12   — ZCREATIONDATE1, ZACCOUNT4
    #   older    — ZCREATIONDATE1, ZACCOUNT3 or ZACCOUNT2
    has_account4    = does_column_exist_in_db(source_path, 'ZICCLOUDSYNCINGOBJECT', 'ZACCOUNT4')
    has_createdate3 = does_column_exist_in_db(source_path, 'ZICCLOUDSYNCINGOBJECT', 'ZCREATIONDATE3')
    has_account3    = does_column_exist_in_db(source_path, 'ZICCLOUDSYNCINGOBJECT', 'ZACCOUNT3')

    if has_account4 and has_createdate3:
        creation_col = 'TabA.ZCREATIONDATE3'
        account_col  = 'TabA.ZACCOUNT4'
    elif has_account4:
        creation_col = 'TabA.ZCREATIONDATE1'
        account_col  = 'TabA.ZACCOUNT4'
    elif has_account3:
        creation_col = 'TabA.ZCREATIONDATE1'
        account_col  = 'TabA.ZACCOUNT3'
    else:
        creation_col = 'TabA.ZCREATIONDATE1'
        account_col  = 'TabA.ZACCOUNT2'

    # Build query with the correct column references for this iOS version.
    # Column names come from code logic (not user input), so the f-string is safe.
    query = f'''
        SELECT
            DATETIME({creation_col}            + 978307200, 'UNIXEPOCH') AS created,
            DATETIME(TabA.ZMODIFICATIONDATE1   + 978307200, 'UNIXEPOCH') AS modified,
            TabA.ZTITLE1        AS title,
            TabB.ZTITLE2        AS folder,
            TabC.ZNAME          AS account,
            CASE TabA.ZISPINNED
                WHEN 1 THEN 'Yes' ELSE 'No'
            END                 AS pinned,
            CASE TabA.ZISPASSWORDPROTECTED
                WHEN 1 THEN 'Yes' ELSE 'No'
            END                 AS locked,
            TabF.ZDATA
        FROM  ZICCLOUDSYNCINGOBJECT TabA
        INNER JOIN ZICCLOUDSYNCINGOBJECT TabB ON TabA.ZFOLDER  = TabB.Z_PK
        INNER JOIN ZICCLOUDSYNCINGOBJECT TabC ON {account_col} = TabC.Z_PK
        LEFT  JOIN ZICNOTEDATA           TabF ON TabF.ZNOTE    = TabA.Z_PK
        WHERE TabA.ZTITLE1 IS NOT NULL
        ORDER BY TabA.ZMODIFICATIONDATE1 DESC
    '''

    for record in get_sqlite_db_records(source_path, query):
        created  = convert_utc_human_to_timezone(record[0], timezone_offset)
        modified = convert_utc_human_to_timezone(record[1], timezone_offset)
        is_locked = record[6]
        body = '' if is_locked == 'Yes' else _decode_note_body(record[7])

        data_list.append((
            created,
            modified,
            record[2],   # title
            record[3],   # folder
            record[4],   # account
            record[5],   # pinned
            is_locked,
            body,
        ))

    data_headers = (
        ('Date Created',  'datetime'),
        ('Date Modified', 'datetime'),
        'Title',
        'Folder',
        'Account',
        'Pinned',
        'Locked',
        'Body',
    )

    return data_headers, data_list, source_path
