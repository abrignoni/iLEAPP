__artifacts_v2__ = {
    "notesPasswordProtected": {
        "name": "Notes - Password Protected",
        "description": "Locked Apple Notes: the password hint and the encryption scheme guarding "
                       "each note, so an examiner can tell at a glance which locked notes are "
                       "recoverable and which are not.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Notes",
        "notes": "The main Notes artifact reports that a note is locked but not how it is locked. "
                 "This surfaces ZPASSWORDHINT and classifies the per-note crypto: a 24-byte "
                 "wrapped key with a PBKDF2 iteration count is the documented scheme "
                 "(PBKDF2-SHA256 -> AES Key Wrap -> AES-GCM) and is recoverable with the note "
                 "password; a 16-byte wrapped key is the revised scheme seen from iOS 16 onward "
                 "and is not recoverable with that method. The scheme tracks how the note was "
                 "locked, not the iOS version, so both appear across the same releases. Note body "
                 "and title stay encrypted; this artifact does not attempt to decrypt them.",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows (classic)",
            "hickman_ios14": "iOS 14.3 | 0 rows (no crypto columns)",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 5 rows (classic)",
            "abe_ios16": "iOS 16.5 | 2 rows (revised)",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows (revised)",
            "otto_ios17": "iOS 17.5.1 | 5 rows (classic)",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows (revised)",
            "iphone12_ios18": "iOS 18.7 | 19 rows (revised)",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows (revised)",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc)

TABLE = 'ZICCLOUDSYNCINGOBJECT'

# The documented scheme wraps a 16-byte note key with AES Key Wrap, which is 24 bytes
# on disk, and derives the wrapping key with PBKDF2. The revised scheme, seen from
# iOS 16 onward, stores a 16-byte wrapped key with the iteration count zeroed.
CLASSIC_WRAPPED_LEN = 24
REVISED_WRAPPED_LEN = 16


def _existing_columns(file_found):
    """Return the set of ZICCLOUDSYNCINGOBJECT column names present in this db."""
    return {row[0] for row in get_sqlite_db_records(
        file_found, f"SELECT name FROM pragma_table_info('{TABLE}')")}


def _first_present(columns, *candidates):
    """First candidate column that exists, or 'NULL' so the SELECT still binds."""
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return 'NULL'


def _classify(wrapped_len):
    """Name the encryption scheme and say whether the note is recoverable.

    The wrapped-key length is the reliable discriminator: AES Key Wrap of a
    16-byte note key is 24 bytes, while the revised scheme stores 16. The
    iteration count moves with it (20000 vs 0) but is reported as data rather
    than used to classify, since only the length is load-bearing.
    """
    if wrapped_len == CLASSIC_WRAPPED_LEN:
        return ('Classic (PBKDF2-SHA256 + AES Key Wrap)',
                'Recoverable with the note password')
    if wrapped_len == REVISED_WRAPPED_LEN:
        return ('Revised (iOS 16+), 16-byte wrapped key',
                'Not recoverable with the published method')
    if wrapped_len:
        return (f'Unrecognized ({wrapped_len}-byte wrapped key)', 'Unknown')
    # A locked note always carries a wrapped key; a hint with no key is the
    # password-group definition row rather than an encrypted note.
    return ('Password group definition (no per-note key)', 'n/a')


@artifact_processor
def notesPasswordProtected(context):
    data_headers = (
        ('Creation Date', 'datetime'), ('Last Modified', 'datetime'), 'Note Title',
        'Password Hint', 'Encryption Scheme', 'KDF Iterations', 'Wrapped Key Bytes',
        'Recoverability', 'Note Row ID')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        if not does_table_exist_in_db(file_found, TABLE):
            continue

        columns = _existing_columns(file_found)
        if 'ZISPASSWORDPROTECTED' not in columns:
            continue  # schema predates locked notes; nothing to report

        creation = _first_present(columns, 'ZCREATIONDATE3', 'ZCREATIONDATE2',
                                  'ZCREATIONDATE1', 'ZCREATIONDATE')
        modified = _first_present(columns, 'ZMODIFICATIONDATE3', 'ZMODIFICATIONDATE2',
                                  'ZMODIFICATIONDATE1', 'ZMODIFICATIONDATE')
        title = _first_present(columns, 'ZTITLE1', 'ZTITLE2', 'ZTITLE')
        hint = _first_present(columns, 'ZPASSWORDHINT')
        wrapped = _first_present(columns, 'ZCRYPTOWRAPPEDKEY')
        iterations = _first_present(columns, 'ZCRYPTOITERATIONCOUNT')

        query = f'''
            SELECT {creation}, {modified}, {title}, {hint},
                   LENGTH({wrapped}), {iterations}, Z_PK
            FROM {TABLE}
            WHERE ZISPASSWORDPROTECTED = 1
              AND ({wrapped} IS NOT NULL OR {hint} IS NOT NULL)
            ORDER BY {creation}
        '''
        rows = list(get_sqlite_db_records(file_found, query))
        if not rows:
            continue

        for created, changed, note_title, note_hint, wrapped_len, iters, row_id in rows:
            scheme, recoverability = _classify(wrapped_len or 0)
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(created) if created else '',
                convert_cocoa_core_data_ts_to_utc(changed) if changed else '',
                note_title or '',            # title is itself encrypted, so usually blank
                note_hint or '',
                scheme,
                iters if iters is not None else '',
                wrapped_len if wrapped_len else '',
                recoverability,
                row_id))

        sources.append(context.get_relative_path(file_found))

    if data_list:
        recoverable = sum(1 for row in data_list if row[7].startswith('Recoverable'))
        logfunc(f'Notes: {len(data_list)} password-protected note(s), '
                f'{recoverable} in the recoverable scheme')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
