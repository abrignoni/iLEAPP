__artifacts_v2__ = {
    "notesPasswordProtected": {
        "name": "Notes - Password Protected",
        "description": "Locked Apple Notes: the password hint and the wrapped-key length that "
                       "classifies the encryption scheme of each note, as stored.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Notes",
        "notes": "The main Notes artifact reports that a note is locked but not how it is locked. "
                 "This surfaces ZPASSWORDHINT and labels each row from the stored length of "
                 "ZCRYPTOWRAPPEDKEY alone; the iteration count is reported and not used. A 24-byte "
                 "wrapped key matches the scheme described in the cited "
                 "research (PBKDF2-SHA256 -> AES Key Wrap -> AES-GCM), which the research reports "
                 "as recoverable with the note password; hashcat lists mode 16200 as 'Apple Secure "
                 "Notes' (https://hashcat.net/wiki/doku.php?id=example_hashes). A 16-byte wrapped "
                 "key is a layout the cited research does not cover, so its row reads 'Not covered "
                 "by the cited research'; that is a statement about the research, not that the "
                 "note cannot be recovered. In tested samples 24 byte keys were found on iOS "
                 "13.3.1, 15 and 17.5.1 and 16 byte keys on iOS 16.5, 17.3, 18.3.2, 18.7 and "
                 "18.7.8, so the key length does not follow the iOS version alone; what decides it "
                 "is not established here. A row with a hint and no wrapped key is labelled "
                 "'Hint stored, no wrapped key'; what such a row is in the Notes data model is "
                 "not established here. The note body stays encrypted and this artifact does "
                 "not attempt to decrypt it. Note Title is the title column as stored (ZTITLE1, "
                 "ZTITLE2 or ZTITLE, the first one the database has); the cited research found "
                 "ZTITLE1 left unencrypted on a locked note. A non-empty Note Title was reported "
                 "on 6 of the 18 rows that carry a wrapped key on iphone12_ios18 and on 1 of 8 on "
                 "hc_ios18_7. Why the title is empty on the other rows was not established. "
                 "Reference: Ciofeca Forensics, 'Apple Notes Revisited: Encrypted Notes', "
                 "https://www.ciofecaforensics.com/2020/07/31/apple-notes-revisited-encrypted-notes/",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows (24-byte keys)",
            "hickman_ios14": "iOS 14.3 | 4 rows (no crypto columns)",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15 | 5 rows (24-byte keys)",
            "abe_ios16": "iOS 16.5 | 2 rows (16-byte keys)",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows (16-byte keys)",
            "otto_ios17": "iOS 17.5.1 | 5 rows (24-byte keys)",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows (16-byte keys)",
            "iphone12_ios18": "iOS 18.7 | 19 rows (16-byte keys)",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows (16-byte keys)",
        }
    },
    "notesEncryptionKeys": {
        "name": "Notes - Encryption Keys (John the Ripper)",
        "description": "The PBKDF2 salt, iteration count and wrapped key held against each locked "
                       "Apple Notes record, assembled into the hash string that hashcat (-m 16200, "
                       "Apple Secure Notes) consumes.",
        "author": "@Rugikex",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Notes",
        "notes": "Each ZICCLOUDSYNCINGOBJECT row that carries Notes key material becomes one "
                 "hashcat/John hash string, reproducing the field order of John the Ripper's "
                 "run/applenotes2john.py: $ASN$*<Z_PK>*<ZCRYPTOITERATIONCOUNT>*<ZCRYPTOSALT hex>*"
                 "<ZCRYPTOWRAPPEDKEY hex>, falling back to ZCRYPTOVERIFIER when ZCRYPTOWRAPPEDKEY "
                 "is NULL. A row is skipped when the iteration count is zero or missing, or when "
                 "neither a wrapped key nor a verifier is stored. "
                 "Unlike the Notes - Password Protected artifact this does NOT filter on "
                 "ZISPASSWORDPROTECTED: an account-wide ('universal') Notes password is stored on "
                 "the account record (entity ICAccount), and applenotes2john.py's own comment "
                 "records that ZISPASSWORDPROTECTED can be 0 there while the iteration count is "
                 "non-zero, so filtering on that flag drops the account hash. The Entity column is "
                 "resolved from each row's Z_ENT through the Core Data Z_PRIMARYKEY table "
                 "(Z_ENT and Z_NAME); an ICAccount hash recovers one password that unlocks every "
                 "note secured with it, an ICNote hash recovers a single note's password. "
                 "To crack, save a hash string to a file and run "
                 "'hashcat -m 16200 -a 0 <file> <wordlist>' "
                 "Reference: John The Ripper's repository, "
                 "https://github.com/openwall/john/blob/bleeding-jumbo/run/applenotes2john.py",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "key",
    }
}

import binascii

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
        return ('24-byte wrapped key (PBKDF2-SHA256 + AES Key Wrap per the cited research)',
                'Recoverable with the note password per the cited research')
    if wrapped_len == REVISED_WRAPPED_LEN:
        return ('16-byte wrapped key (layout not covered by the cited research)',
                'Not covered by the cited research')
    if wrapped_len:
        return (f'Unrecognized ({wrapped_len}-byte wrapped key)', 'Unknown')
    # A hint with no wrapped key. What that row is has not been sourced, so it
    # is named by what is stored.
    return ('Hint stored, no wrapped key', 'n/a')


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
            ORDER BY {creation}, Z_PK
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


def _entity_names(file_found):
    """Map Core Data Z_ENT integers to entity names via Z_PRIMARYKEY.

    ZICCLOUDSYNCINGOBJECT holds several entities in one table (Core Data
    single-table inheritance); Z_ENT says which one a row is. Z_PRIMARYKEY names
    them, which is how an account record (ICAccount, the account-wide password)
    is told apart from a note record (ICNote, a single note's password). An
    empty mapping when the table is absent leaves rows labelled by raw Z_ENT.
    """
    return {row[0]: row[1] for row in get_sqlite_db_records(
        file_found, 'SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY')}


def _asn_hash(z_pk, iterations, salt_blob, key_blob):
    """Assemble the hashcat/John ``$ASN$`` string body for one record.

    Reproduces the field order of John the Ripper's applenotes2john.py:
    ``$ASN$*<Z_PK>*<iterations>*<salt hex>*<key hex>``. Returns '' when the salt
    or key bytes are missing, since the hash cannot be built without them.
    """
    if not iterations or salt_blob is None or key_blob is None:
        return ''
    salt_hex = binascii.hexlify(salt_blob).decode('ascii')
    key_hex = binascii.hexlify(key_blob).decode('ascii')
    return f'$ASN$*{z_pk}*{iterations}*{salt_hex}*{key_hex}'


@artifact_processor
def notesEncryptionKeys(context):
    data_headers = (
        'Entity', 'Record ID', 'Password Protected Flag', 'Password Hint',
        'KDF Iterations', 'Wrapped Key Bytes', 'Salt (hex)',
        'Wrapped Key / Verifier (hex)', 'Hash Source Column',
        'hashcat/John Hash String ($ASN$, -m 16200)')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        if not does_table_exist_in_db(file_found, TABLE):
            continue

        columns = _existing_columns(file_found)
        wrapped = _first_present(columns, 'ZCRYPTOWRAPPEDKEY')
        verifier = _first_present(columns, 'ZCRYPTOVERIFIER')
        salt = _first_present(columns, 'ZCRYPTOSALT')
        iterations = _first_present(columns, 'ZCRYPTOITERATIONCOUNT')
        if wrapped == 'NULL' and verifier == 'NULL':
            continue  # schema predates encrypted notes; no key material to export
        if salt == 'NULL' or iterations == 'NULL':
            continue  # a hash needs both the salt and the iteration count

        hint = _first_present(columns, 'ZPASSWORDHINT')
        protected = _first_present(columns, 'ZISPASSWORDPROTECTED')
        entity_names = _entity_names(file_found)

        # No ZISPASSWORDPROTECTED filter: the account-wide key lives on the
        # ICAccount row, which can carry a non-zero iteration count while its
        # ZISPASSWORDPROTECTED flag is 0 (see applenotes2john.py).
        query = f'''
            SELECT Z_PK, Z_ENT, {protected}, {hint}, {iterations},
                   {salt}, {wrapped}, {verifier}
            FROM {TABLE}
            WHERE {iterations} > 0
              AND ({wrapped} IS NOT NULL OR {verifier} IS NOT NULL)
            ORDER BY Z_ENT, Z_PK
        '''
        rows = list(get_sqlite_db_records(file_found, query))
        if not rows:
            continue

        for (z_pk, z_ent, is_protected, note_hint, iters,
             salt_blob, wrapped_blob, verifier_blob) in rows:
            key_blob = wrapped_blob if wrapped_blob is not None else verifier_blob
            source_col = ('ZCRYPTOWRAPPEDKEY' if wrapped_blob is not None
                          else 'ZCRYPTOVERIFIER')
            data_list.append((
                entity_names.get(z_ent, f'Z_ENT {z_ent}'),
                z_pk,
                is_protected if is_protected is not None else '',
                note_hint or '',
                iters,
                len(key_blob) if key_blob is not None else '',
                binascii.hexlify(salt_blob).decode('ascii') if salt_blob is not None else '',
                binascii.hexlify(key_blob).decode('ascii') if key_blob is not None else '',
                source_col,
                _asn_hash(z_pk, iters, salt_blob, key_blob)))

        sources.append(context.get_relative_path(file_found))

    if data_list:
        accounts = sum(1 for row in data_list if row[0] == 'ICAccount')
        logfunc(f'Notes: {len(data_list)} encryption-key hash(es) built, '
                f'{accounts} on account records')

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
