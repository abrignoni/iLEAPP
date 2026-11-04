__artifacts_v2__ = {
    "textReplacements": {
        "name": "Keyboard Text Replacements",
        "description": "Text replacement shortcuts and the phrases they expand to, from "
        "KeyboardServices/TextReplacements.db, with the CloudKit record times and the "
        "ModifiedByDevice value from each entry's CloudKit record.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Keyboard",
        "notes": "Reads ZTEXTREPLACEMENTENTRY in mobile/Library/KeyboardServices/TextReplacements.db and "
        "its -wal. Timestamp is ZTIMESTAMP, which the store's own Core Data model (Z_MODELCACHE) "
        "declares as a date attribute (attribute type 900), read as seconds since 2001-01-01 "
        "UTC. What it marks is not established: it travels with the entry, so the same Unique "
        "Name and Timestamp appear on hc_ios18_7 and hc_ios26, whose extraction folders carry "
        "different device identifiers, and on ctf2020_ios12 one entry's Timestamp falls in 1989 "
        "while its CloudKit times fall in March 2020. CloudKit Record Created, CloudKit Record "
        "Modified and Modified By Device are the RecordCtime, RecordMtime and ModifiedByDevice "
        "entries of ZREMOTERECORDINFO, an NSKeyedArchiver archive of the entry's CloudKit record "
        "whose RecordType was TextReplacementEntry and whose zone was TextReplacements on every "
        "tested row; they are named from the archive's own keys, and no Apple documentation of "
        "those keys was found. Unique Name is ZUNIQUENAME, which equalled the CloudKit record "
        "name (RecordID) on every tested row. Modified By Device is reported as stored and is "
        "not a stable record of which device last changed the entry: on hickman_ios15 and "
        "iphone11_ios17 the entry had the same Unique Name, Timestamp and CloudKit times as on "
        "hickman_ios13 and hickman_ios14 and a different Modified By Device value, and the same "
        "held for one entry on felix23_ios16 and felix_ios17. Was Deleted (as stored) is "
        "ZWASDELETED and held 0 on every tested row; ZNEEDSSAVETOCLOUD held 0 on every tested "
        "row and is not reported. On the tested images: 27 rows on 24 images. CloudKit Record "
        "Created was later than Timestamp on 26 rows, by 1 second to 26 days on 25 of them, and "
        "about 3 years earlier on fsfull002_ios17; CloudKit Record Modified was never earlier "
        "than CloudKit Record Created. One shortcut and phrase pair was on all 24 images; the "
        "sync plist named below carries keys named KSSampleShortcutWasImported_CK and "
        "kDidInsertSampleShortcutForPeer, and whether this pair is a system-inserted sample is "
        "not established; felix23_ios16 and felix_ios17 held one more pair, and ctf2020_ios12 "
        "held one more whose phrase is an email address. Not read: the ZTRCLOUDKITSYNCSTATE "
        "table (a pull flag and a change token) and "
        "Library/Preferences/com.apple.textInput.keyboardServices.textReplacement.plist, which "
        "holds CloudKit sync state, and Library/Keyboard/textReplacements.cache, which was "
        "present on ctf2020_ios12 and in both backups below and was not examined. The decrypted "
        "iTunes backups hickman_ios13_itunes_backup_decrypted and "
        "hickman_ios14_itunes_backup_decrypted hold no TextReplacements.db; their Manifest.db "
        "lists that plist and that cache, neither read.",
        "paths": ('*/mobile/Library/KeyboardServices/TextReplacements.db*',),
        "output_types": "standard",
        "artifact_icon": "keyboard",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
            "belkactf6_tar": "iOS 16.3 | 1 row",
            "cookbook_ios1751": "iOS 17.5.1 | 1 row",
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "falken_ios26": "iOS 26.2.1 | 1 row",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios17_2": "iOS 17.2.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
        },
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, \
    does_table_exist_in_db, get_file_path, get_sqlite_db_records

_QUERY = '''
SELECT ZTIMESTAMP, ZSHORTCUT, ZPHRASE, ZWASDELETED, ZUNIQUENAME, ZREMOTERECORDINFO
FROM ZTEXTREPLACEMENTENTRY
ORDER BY ZTIMESTAMP, Z_PK
'''


def _cocoa(value):
    """Seconds since 2001-01-01 UTC as a UTC datetime; '' when absent.

    convert_cocoa_core_data_ts_to_utc passes 0 through unchanged, so the offset is added here."""
    if value is None or value == '':
        return ''
    return convert_unix_ts_to_utc(value + 978307200)


def _record_fields(blob):
    """RecordCtime, RecordMtime and ModifiedByDevice from the CloudKit record's system fields.

    The fields are keyed archive entries at the archive's $top level, not under a root
    object. Returns ('', '', '') when the blob is absent or is not a keyed archive."""
    if not blob:
        return '', '', ''
    try:
        archive = plistlib.loads(bytes(blob))
    except (plistlib.InvalidFileException, ValueError, TypeError, OverflowError):
        return '', '', ''
    if not isinstance(archive, dict) or '$objects' not in archive:
        return '', '', ''
    objects, top = archive['$objects'], archive.get('$top', {})

    def value(key):
        uid = top.get(key)
        if not isinstance(uid, plistlib.UID) or uid.data >= len(objects):
            return None
        obj = objects[uid.data]
        return None if obj == '$null' else obj

    def date(key):
        obj = value(key)
        return _cocoa(obj['NS.time']) if isinstance(obj, dict) and 'NS.time' in obj else ''

    device = value('ModifiedByDevice')
    if isinstance(device, dict):
        device = device.get('NS.string')
    return date('RecordCtime'), date('RecordMtime'), device if isinstance(device, str) else ''


@artifact_processor
def textReplacements(context):
    data_headers = (
        ('Timestamp', 'datetime'), ('CloudKit Record Created', 'datetime'),
        ('CloudKit Record Modified', 'datetime'), 'Shortcut', 'Phrase',
        'Was Deleted (as stored)', 'Modified By Device (as stored)', 'Unique Name')
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'TextReplacements.db')
    if not db_file or not does_table_exist_in_db(db_file, 'ZTEXTREPLACEMENTENTRY'):
        return data_headers, data_list, ''

    for row in get_sqlite_db_records(db_file, _QUERY):
        created, modified, device = _record_fields(row['ZREMOTERECORDINFO'])
        data_list.append((
            _cocoa(row['ZTIMESTAMP']), created, modified, row['ZSHORTCUT'] or '',
            row['ZPHRASE'] or '', '' if row['ZWASDELETED'] is None else str(row['ZWASDELETED']),
            device, row['ZUNIQUENAME'] or ''))
    return data_headers, data_list, db_file
