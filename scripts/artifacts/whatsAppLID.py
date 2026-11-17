__artifacts_v2__ = {
    "whatsapp_lid_phone_numbers": {
        "name": "WhatsApp - LID Phone Numbers",
        "description": "WhatsApp LID identifiers from LID.sqlite with the phone number stored beside them, the display "
                       "name stored for the LID, and the matching ContactsV2 address book name.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Reads LID.sqlite in WhatsApp's shared app group container (group.net.whatsapp.WhatsApp.shared on "
                 "all 11 images with LID.sqlite, read from each container's metadata plist), read-only, together "
                 "with the ContactsV2.sqlite in the same folder. One row per ZWAPHONENUMBERLIDPAIR row and per "
                 "ZWAZACCOUNT row; Table names which. No LID was on more than one row on the tested images. On the "
                 "tested images ZWAPHONENUMBERLIDPAIR stored the LID as bare digits and ZWAZACCOUNT as digits@lid, "
                 "and LID shows the digits. Pair Timestamp is ZWAPHONENUMBERLIDPAIR.ZTIMESTAMP and ZWAZACCOUNT "
                 "Created At is ZWAZACCOUNT.ZCREATEDAT, both Core Data timestamps shown in UTC; what moment either "
                 "marks is not established. Of the 11 images with LID.sqlite, 8 (WhatsApp 23.8.78 to 24.17.78) held "
                 "rows only in ZWAPHONENUMBERLIDPAIR and 3 (25.26.72 to 26.28.75) only in ZWAZACCOUNT, so Table held "
                 "one value on all rows of each image, Pair Timestamp has no value on any row of the 3 and "
                 "ZWAZACCOUNT Created At has no value on any row of the 8. On fsfull002_ios17 Pair Timestamp held "
                 "one value on all 4 rows. Every LID held one phone number on the tested images, and a phone number "
                 "was stored under two LIDs on abe_ios16 (2 numbers), dexter_ios18 (1), iphone11_ios17 (2) and "
                 "otto_ios17 (4). As a second record, where a ContactsV2 address book contact stores the same LID in "
                 "ZLID, its ZWHATSAPPID held the same phone number on all 40 such contacts (otto_ios17 20, "
                 "felix_ios17 5, iphone11_ios17 3, dexter_ios18 8, hc_ios18_7 2, hc_ios26 2). Address Book Name is "
                 "that contact's ZFULLNAME. ContactsV2 had no ZLID column on abe_ios16, felix23_ios16, "
                 "fsfull002_ios17, hc_ios17_2 and hickman_ios15, so Address Book Name has no value on any row there, "
                 "and elsewhere Address Book Name has no value where no contact stores the LID or the contact has no "
                 "ZFULLNAME (1 contact each on otto_ios17, hc_ios18_7 and hc_ios26). LID Display Name is the "
                 "ZDISPLAYNAME stored for the LID in ZWALIDPROPERTIES. That table held rows only on otto_ios17, "
                 "where 653 of 794 rows have one, so LID Display Name has no value on any row of the other images. "
                 "Whose name it is is not established. The 1,423 LIDs on otto_ios17 that have a display name but no "
                 "stored phone number are not rows here; all are group member LIDs and their names are in WhatsApp - "
                 "Group Members. On otto_ios17, 3 of the 4 JIDs ending in @lid in WhatsApp - Message Reactions match "
                 "a LID here. ZWALIDTHREADPROPERTIES and ZWASINTEROPINTEGRATORPROPERTIES were empty or absent on all "
                 "11 images and are not read, nor are the other ZWAZACCOUNT columns or ZWALIDPROPERTIES.ZUSERNAME. "
                 "hc_ios18_7 and hc_ios26 held the same 3 ZWAZACCOUNT rows.",
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/LID.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
        ),
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 51 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 10 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | WhatsApp Messenger 23.25.85 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | WhatsApp Messenger 26.28.75 | 3 rows",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | WhatsApp Messenger 23.8.78 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 925 rows",
            "magnet_ios16": "iOS 16.1.1 | WhatsApp Messenger 22.23.77 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 794 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
    },
    "whatsapp_group_members": {
        "name": "WhatsApp - Group Members",
        "description": "Rows of ZWAGROUPMEMBER in WhatsApp's ChatStorage.sqlite with the chat each belongs to, the "
                       "stored member JID and, for a LID member, the phone number and display name stored for that "
                       "LID in LID.sqlite.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per ZWAGROUPMEMBER row in ChatStorage.sqlite, read-only, with LID.sqlite and "
                 "ContactsV2.sqlite from the same folder. Chat Name and Chat JID are the member's chat ZPARTNERNAME "
                 "and ZCONTACTJID, and Member JID is ZMEMBERJID as stored. For a member JID ending in "
                 "@s.whatsapp.net, Phone Number is its digits and Phone Number From reads Member JID. For a member "
                 "JID ending in @lid, Phone Number is the one phone number stored for that LID in "
                 "ZWAPHONENUMBERLIDPAIR or ZWAZACCOUNT (see WhatsApp - LID Phone Numbers) and Phone Number From "
                 "names the table; both have no value when none is stored, or when more than one number is stored "
                 "for the LID (not seen on the tested images). On otto_ios17 2,080 of 2,918 rows have a LID member "
                 "JID, 657 of which resolve through ZWAPHONENUMBERLIDPAIR; on hickman_ios15 4 of 8 rows have a LID "
                 "member JID and none resolves. On abe_ios16, dexter_ios18, felix23_ios16, felix_ios17, "
                 "fsfull002_ios17 and iphone11_ios17 every member JID ends in @s.whatsapp.net, so Phone Number From "
                 "held one value on all rows. One phone number can appear on two rows of a chat: on otto_ios17 68 "
                 "chat and phone number pairs appear on 2 rows each, once as a phone member JID and once as a LID "
                 "that resolves to the same number. The row count is not a count of members. LID Display Name is the "
                 "ZDISPLAYNAME stored for a LID member in ZWALIDPROPERTIES. LID Display Name had a value on all "
                 "2,080 LID rows of otto_ios17 and no value on any row of the other images, whose ZWALIDPROPERTIES "
                 "was empty. Whose name it is is not established. Address Book Name is the ContactsV2 ZFULLNAME "
                 "whose ZWHATSAPPID matches Phone Number; when two contacts store the same ZWHATSAPPID, one of their "
                 "names is shown. Address Book Name has no value on any row of hickman_ios15. Some rows belong to "
                 "the chat whose JID is status@broadcast (ZSESSIONTYPE 2), which has no ZPARTNERNAME: 54 on "
                 "abe_ios16, 9 on dexter_ios18, 6 on felix23_ios16, 5 on felix_ios17, 2 on fsfull002_ios17, 3 on "
                 "iphone11_ios17 and 35 on otto_ios17. On dexter_ios18, felix_ios17, felix23_ios16 and "
                 "fsfull002_ios17 every row is from that chat, so Chat Name has no value on any row and Chat JID "
                 "held one value on all rows. On otto_ios17 a further 11 rows belong to @g.us chats with "
                 "ZSESSIONTYPE 4, not interpreted. What that chat's member list records is not established. Admin "
                 "and Active are ZISADMIN and ZISACTIVE as stored and not interpreted; Admin held one value on all "
                 "rows of dexter_ios18, felix_ios17, felix23_ios16 and fsfull002_ios17, Active held one value on all "
                 "rows of felix_ios17 and fsfull002_ios17, and on hickman_ios15 Admin and Active were identical on "
                 "all 8 rows. ZCONTACTNAME held no value on any of the 3,012 rows of the 8 images with rows and is "
                 "not shown; the other ZWAGROUPMEMBER columns and ZWAGROUPINFO are not read. Message senders in "
                 "group chats are not linked to these rows.",
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/LID.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
        ),
        "sample_data": {
            "abe_ios16": "iOS 16.5 | WhatsApp Messenger 23.11.80 | 57 rows",
            "ctf2020_ios12": "iOS 12.4 | net.whatsapp.WhatsApp | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | WhatsApp Messenger 25.26.72 | 9 rows",
            "felix23_ios16": "iOS 16.5 | WhatsApp Messenger 23.12.76 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | WhatsApp Messenger 24.17.78 | 5 rows",
            "fsfull002_ios17": "iOS 17.1 | WhatsApp Messenger 23.8.78 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | WhatsApp Messenger 23.25.85 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | WhatsApp Messenger 26.14.76 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | WhatsApp Messenger 26.28.75 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | WhatsApp Messenger 2.20.31 | 0 rows",
            "hickman_ios14": "iOS 14.3 | WhatsApp Messenger 2.21.20 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | WhatsApp Messenger 23.8.78 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | WhatsApp Messenger 24.15.1 | 7 rows",
            "magnet_ios16": "iOS 16.1.1 | WhatsApp Messenger 22.23.77 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | WhatsApp Messenger 24.13.79 | 2918 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
    },
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               does_column_exist_in_db, logfunc)

_COCOA = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_NAMES = ('LID.sqlite', 'ChatStorage.sqlite', 'ContactsV2.sqlite')


def _cocoa(value):
    if value in (None, ''):
        return ''
    try:
        return _COCOA + datetime.timedelta(seconds=float(value))
    except (ValueError, OverflowError, TypeError):
        return ''


def _text(value):
    return '' if value is None else str(value)


def _containers(context):
    """{folder: {database name: path}}: the three databases are paired by the folder that holds them."""
    found = {}
    for path in context.get_files_found():
        path = str(path)
        name = os.path.basename(path)
        if name in _NAMES:
            found.setdefault(os.path.dirname(path), {})[name] = path
    return found


def _rows(path, sql):
    if not path:
        return []
    db = open_sqlite_db_readonly(path)
    if db is None:
        return []
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error as error:
        logfunc(f'WhatsApp LID: could not read {path}: {error}')
        return []
    finally:
        db.close()


def _bare(jid):
    """The user part of a JID: '123@lid' and '123' both give '123'."""
    return _text(jid).split('@', 1)[0]


class _Lid:
    """What LID.sqlite and ContactsV2.sqlite in one folder store about each LID, keyed by its bare digits."""

    def __init__(self, files):
        self.pairs = {}      # bare LID -> list of (phone, ZTIMESTAMP)
        self.accounts = {}   # bare LID -> list of (phone, ZCREATEDAT)
        self.names = {}      # bare LID -> ZDISPLAYNAME
        self.book_by_lid = {}
        self.book_by_phone = {}
        lid = files.get('LID.sqlite')
        if lid and does_table_exist_in_db(lid, 'ZWAPHONENUMBERLIDPAIR'):
            for key, phone, stamp in _rows(lid, 'SELECT ZLID, ZPHONENUMBER, ZTIMESTAMP FROM ZWAPHONENUMBERLIDPAIR'):
                self.pairs.setdefault(_bare(key), []).append((_text(phone), stamp))
        if lid and does_table_exist_in_db(lid, 'ZWAZACCOUNT'):
            for key, phone, stamp in _rows(lid, 'SELECT ZIDENTIFIER, ZPHONENUMBER, ZCREATEDAT FROM ZWAZACCOUNT'):
                self.accounts.setdefault(_bare(key), []).append((_text(phone), stamp))
        if lid and does_table_exist_in_db(lid, 'ZWALIDPROPERTIES'):
            for key, name in _rows(lid, 'SELECT ZLID, ZDISPLAYNAME FROM ZWALIDPROPERTIES'):
                self.names[_bare(key)] = _text(name)
        book = files.get('ContactsV2.sqlite')
        if book and does_table_exist_in_db(book, 'ZWAADDRESSBOOKCONTACT'):
            lid_column = 'ZLID' if does_column_exist_in_db(book, 'ZWAADDRESSBOOKCONTACT', 'ZLID') else 'NULL'
            for key, jid, name in _rows(book, f'SELECT {lid_column}, ZWHATSAPPID, ZFULLNAME '
                                              'FROM ZWAADDRESSBOOKCONTACT'):
                if key:
                    self.book_by_lid[_bare(key)] = _text(name)
                if jid:
                    self.book_by_phone[_bare(jid)] = _text(name)

    def phone(self, bare):
        """(phone, table) when exactly one phone number is stored for the LID across both tables."""
        found = {(p, 'ZWAPHONENUMBERLIDPAIR') for p, _ in self.pairs.get(bare, ())}
        found |= {(p, 'ZWAZACCOUNT') for p, _ in self.accounts.get(bare, ())}
        phones = {p for p, _ in found}
        if len(phones) != 1:
            return '', ''
        return phones.pop(), ', '.join(sorted(t for _, t in found))


@artifact_processor
def whatsapp_lid_phone_numbers(context):
    data_list = []
    sources = []
    for files in _containers(context).values():
        if 'LID.sqlite' not in files:
            continue
        sources.append(files['LID.sqlite'])
        lid = _Lid(files)
        for bare in sorted(set(lid.pairs) | set(lid.accounts)):
            book = lid.book_by_lid.get(bare, '')
            entries = [('ZWAPHONENUMBERLIDPAIR', phone, stamp, '') for phone, stamp in lid.pairs.get(bare, ())]
            entries += [('ZWAZACCOUNT', phone, '', stamp) for phone, stamp in lid.accounts.get(bare, ())]
            for table, phone, pair_stamp, created in entries:
                data_list.append((_cocoa(pair_stamp), _cocoa(created), bare, phone, lid.names.get(bare, ''), book,
                                  table))
    data_headers = (
        ('Pair Timestamp', 'datetime'), ('ZWAZACCOUNT Created At', 'datetime'), 'LID', 'Phone Number',
        'LID Display Name', 'Address Book Name', 'Table',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_group_members(context):
    data_list = []
    sources = []
    for files in _containers(context).values():
        chat = files.get('ChatStorage.sqlite')
        if not chat or not does_table_exist_in_db(chat, 'ZWAGROUPMEMBER'):
            continue
        sources.append(chat)
        lid = _Lid(files)
        optional = {name: f'm.{name}' if does_column_exist_in_db(chat, 'ZWAGROUPMEMBER', name) else 'NULL'
                    for name in ('ZISADMIN', 'ZISACTIVE')}
        sql = f'''
            SELECT s.ZPARTNERNAME, s.ZCONTACTJID, m.ZMEMBERJID, {optional['ZISADMIN']}, {optional['ZISACTIVE']}
            FROM ZWAGROUPMEMBER m LEFT JOIN ZWACHATSESSION s ON s.Z_PK = m.ZCHATSESSION
            ORDER BY s.Z_PK, m.Z_PK'''
        for group, group_jid, member, admin, active in _rows(chat, sql):
            member = _text(member)
            bare, _, domain = member.partition('@')
            phone, phone_from, display = '', '', ''
            if domain == 's.whatsapp.net':
                phone, phone_from = bare, 'Member JID'
            elif domain == 'lid':
                phone, phone_from = lid.phone(bare)
                display = lid.names.get(bare, '')
            book = lid.book_by_phone.get(phone, '') if phone else ''
            data_list.append((_text(group), _text(group_jid), member, phone, phone_from, display, book, admin,
                              active))
    data_headers = (
        'Chat Name', 'Chat JID', 'Member JID', 'Phone Number', 'Phone Number From', 'LID Display Name',
        'Address Book Name', ('Admin (as stored)', 'number'),
        ('Active (as stored)', 'number'),
    )
    return data_headers, data_list, '\n'.join(sources)
