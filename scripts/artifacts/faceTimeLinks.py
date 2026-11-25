__artifacts_v2__ = {
    "faceTimeLinks": {
        "name": "FaceTime - Links",
        "description": "FaceTime links recorded in FaceTime.sqlite3: the creation, expiration and "
                       "deletion dates, a link URL built from the stored pseudonym and public key, "
                       "the originator handle and the invited handles.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Calls & Contacts",
        "notes": "One row per row of ZCONVERSATIONLINK in FaceTime.sqlite3, the Core Data store "
                 "under Library/FaceTime. The column names are the only labels used here. Values "
                 "other than the dates, Link URL and Invited Handles are reported as stored, with "
                 "NULL shown as empty; Invited Handles joins the stored values with a comma. "
                 "Creation Date, Expiration Date and Deletion Date are ZCREATIONDATE, "
                 "ZEXPIRATIONDATE and ZDELETIONDATE read as Core Data seconds since 2001, "
                 "truncated to whole seconds and shown in UTC; a missing or non-positive value "
                 "shows as blank. For a link with no name, Link URL is built the way the "
                 "TUConversationLink class of Apple's TelephonyUtilities framework builds its URL: "
                 "https://facetime.apple.com/join#v=1&p= then ZPSEUDONYM without its prefix before "
                 "the colon, then &k= and ZPUBLICKEY as unpadded base64url. The framework also "
                 "appends &l= and the link name when a link has one; this artifact does not, so "
                 "the Link URL of a named link is shorter than the one the framework gives. A "
                 "pseudonym without exactly one colon gives no Link URL. That construction was "
                 "read from the framework on macOS 27.2.1, and on all 5 rows of the tested images, "
                 "none of which has a link name, the framework, given the stored pseudonym and "
                 "public key, gave the same URL. Originator Handle is ZVALUE of the ZHANDLE row "
                 "that ZORIGINATORHANDLE names; Invited Handles lists ZVALUE of the ZHANDLE rows "
                 "whose ZINVITEDCONVERSATIONLINK names the link, and was empty on every row of the "
                 "tested images. Activated, Lifetime Type and Delete Reason are integers with no "
                 "names given here. The framework's description of a link prints linkLifetimeScope "
                 "and deleteReason as numbers and prints no activated value. ZPRIVATEKEY and "
                 "ZGROUPUUID are not read. On the tested images every link has a Deletion Date and "
                 "is still in the table, so a row with a Deletion Date can remain in the table; "
                 "what sets that date is not established here. The Expiration Date fell within 8 "
                 "seconds of 30 days after the Creation Date on all 5 rows. "
                 "wilkerson_iphone16_ios26 holds 3 links, with the same Originator Handle value on "
                 "every row, Activated 0 and Lifetime Type 0 on every row and Link Name empty, and "
                 "the database file without its write-ahead log holds none of them. iphone11_ios17 "
                 "(iOS 17.3) holds 2; its store has no ZDELETEREASON column, so Delete Reason is "
                 "empty there, and the database file without its write-ahead log holds 1. "
                 "hill_iphone15pro_ios26 has the store with no link.",
        "paths": ('*/mobile/Library/FaceTime/FaceTime.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, store with no link",
        },
    }
}


import base64
import os

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, is_sqlite_sidecar,
                               null_absent_columns)


def _utc(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _url(pseudonym, public_key):
    '''The link URL as TelephonyUtilities' TUConversationLink builds it, or '' when a part is
    missing: the pseudonym without its prefix and the public key as unpadded base64url.'''
    if not isinstance(pseudonym, str) or pseudonym.count(':') != 1:
        return ''
    if not isinstance(public_key, bytes) or not public_key:
        return ''
    key = base64.urlsafe_b64encode(public_key).decode('ascii').rstrip('=')
    return f'https://facetime.apple.com/join#v=1&p={pseudonym.split(":", 1)[1]}&k={key}'


def _text(value):
    return '' if value is None else value


@artifact_processor
def faceTimeLinks(context):
    data_list, sources = [], []
    for found in sorted(str(path) for path in context.get_files_found()):
        if os.path.basename(found) != 'FaceTime.sqlite3' or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'ZCONVERSATIONLINK'):
            continue
        sources.append(found)
        invited = {}
        has_handles = does_table_exist_in_db(found, 'ZHANDLE')
        if has_handles:
            for row in get_sqlite_db_records(
                    found, 'SELECT ZINVITEDCONVERSATIONLINK, ZVALUE FROM ZHANDLE '
                           'WHERE ZINVITEDCONVERSATIONLINK IS NOT NULL ORDER BY Z_PK'):
                invited.setdefault(row[0], []).append(_text(row[1]))
        handle = 'H.ZVALUE' if has_handles else 'NULL'
        join = 'LEFT JOIN ZHANDLE H ON H.Z_PK = L.ZORIGINATORHANDLE' if has_handles else ''
        query = null_absent_columns(found, f'''
            SELECT L.ZCREATIONDATE, L.ZEXPIRATIONDATE, L.ZDELETIONDATE, L.ZNAME, L.ZPSEUDONYM,
                   L.ZPUBLICKEY, {handle}, L.ZACTIVATED, L.ZLIFETIMETYPE, L.ZDELETEREASON,
                   L.ZORIGINATORREVISION, L.Z_PK
            FROM ZCONVERSATIONLINK L
            {join}
            ORDER BY L.ZCREATIONDATE, L.Z_PK
        ''')
        for row in get_sqlite_db_records(found, query):
            data_list.append((
                _utc(row[0]), _utc(row[1]), _utc(row[2]), _text(row[3]), _url(row[4], row[5]),
                _text(row[6]), ', '.join(invited.get(row[11], [])), _text(row[7]),
                _text(row[8]), _text(row[9]), _text(row[10])))
    data_headers = (
        ('Creation Date', 'datetime'), ('Expiration Date', 'datetime'),
        ('Deletion Date', 'datetime'), 'Link Name', 'Link URL', 'Originator Handle',
        'Invited Handles', 'Activated (as stored)', 'Lifetime Type (as stored)',
        'Delete Reason (as stored)', 'Originator Revision')
    return data_headers, data_list, '\n'.join(sources)
