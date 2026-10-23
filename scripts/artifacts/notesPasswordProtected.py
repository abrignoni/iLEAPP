__artifacts_v2__ = {
    "notesPasswordProtected": {
        "name": "Notes - Password Protected",
        "description": "Password-protected Apple Notes records (notes, their attachments and media, "
                       "and the account record): the Core Data entity name, the password hint as stored, "
                       "and the length of the wrapped key, which labels the encryption scheme of each.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "Notes",
        "notes": "The main Notes artifact reports that a note is locked and its password hint, but not "
                 "how it is locked. "
                 "This surfaces ZPASSWORDHINT and labels each row from the stored length of "
                 "ZCRYPTOWRAPPEDKEY alone; the iteration count is reported and not used. A 24-byte "
                 "wrapped key matches the scheme described in the cited "
                 "research (PBKDF2-SHA256 -> AES Key Wrap -> AES-GCM), which the research reports "
                 "as recoverable with the note password; hashcat lists mode 16200 as 'Apple Secure "
                 "Notes' (https://hashcat.net/wiki/doku.php?id=example_hashes). A 16-byte wrapped "
                 "key is a layout the cited research does not cover, so its row reads 'Not covered "
                 "by the cited research'; that is a statement about the research, not that the "
                 "note cannot be recovered. In tested samples 24 byte keys were found on iOS "
                 "13.3.1, 14.3, 15.3.1 and 17.5.1 and 16 byte keys on iOS 16.5, 17.3, 18.3.2, 18.7 and "
                 "18.7.8, so the key length does not follow the iOS version alone; what decides it "
                 "is not established here. "
                 "A row is any ZICCLOUDSYNCINGOBJECT record with ZISPASSWORDPROTECTED 1 that holds a "
                 "wrapped key or a password hint; flagged records with neither are not reported (14 "
                 "of 33 on iphone12_ios18 and 3 of 5 on abe_ios16, all attachment or preview-image "
                 "records). An account record whose ZISPASSWORDPROTECTED is 0 is not reported either "
                 "(hickman_ios13, otto_ios17); the Notes - Encryption Key Hashes artifact reports it. "
                 "That table holds several Core Data entities; Entity is the entity name resolved from "
                 "the row's Z_ENT through Z_PRIMARYKEY, or the raw Z_ENT number when Z_PRIMARYKEY has "
                 "no entry for it. In tested samples the rows were ICNote, "
                 "ICAttachment, ICAttachmentPreviewImage, ICMedia and ICAccount records (on "
                 "iphone12_ios18, 6 ICNote, 7 ICAttachment, 5 ICMedia and 1 ICAccount). A row with "
                 "a hint and no wrapped key is labelled 'Hint stored, no wrapped key'; in tested "
                 "samples every such row was the ICAccount record. "
                 "The table carries numbered variants of some property columns (ZTITLE, ZTITLE1 and "
                 "so on), and no row in the tested stores filled more than one variant of ZTITLE, "
                 "ZCREATIONDATE or ZMODIFICATIONDATE, so Title, Creation Date and Last Modified are "
                 "each taken from whichever variant the row fills. In tested samples Title and both dates were filled on every ICNote "
                 "row, both dates but not Title on every ICAttachment row, and none of the three "
                 "on ICMedia, ICAttachmentPreviewImage and ICAccount rows. The cited research found "
                 "ZTITLE1 left unencrypted on a locked note. Record ID is the row's Z_PK. The note "
                 "body stays encrypted and this artifact does not attempt to decrypt it. "
                 "Reference: Ciofeca Forensics, 'Apple Notes Revisited: Encrypted Notes', "
                 "https://www.ciofecaforensics.com/2020/07/31/apple-notes-revisited-encrypted-notes/",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows (24-byte keys)",
            "hickman_ios14": "iOS 14.3 | 4 rows (3 with 24-byte keys, 1 account row with hint only)",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 5 rows (4 with 24-byte keys, 1 account row with hint only)",
            "abe_ios16": "iOS 16.5 | 2 rows (16-byte keys)",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows (6 with 16-byte keys, 1 account row with hint only)",
            "otto_ios17": "iOS 17.5.1 | 5 rows (24-byte keys)",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows (16-byte keys)",
            "iphone12_ios18": "iOS 18.7 | 19 rows (18 with 16-byte keys, 1 account row with hint only)",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows (8 with 16-byte keys, 1 account row with hint only)",
        }
    },
    "notesEncryptionKeys": {
        "name": "Notes - Encryption Key Hashes",
        "description": "Apple Notes records that carry a PBKDF2 salt, a non-zero iteration count "
                       "and a 24-byte wrapped key or verifier, each assembled into the $ASN$ hash "
                       "string that hashcat mode 16200 (Apple Secure Notes) and John the Ripper "
                       "take as input.",
        "author": "@Rugikex, @AlexisBrignoni, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "Notes",
        "notes": "Each ZICCLOUDSYNCINGOBJECT row whose key material passes the checks below "
                 "becomes one hash string in the field order John the Ripper's "
                 "run/applenotes2john.py writes: "
                 "$ASN$*<Z_PK>*<ZCRYPTOITERATIONCOUNT>*<ZCRYPTOSALT hex>*<key hex>, where the key "
                 "is ZCRYPTOWRAPPEDKEY, or ZCRYPTOVERIFIER when ZCRYPTOWRAPPEDKEY is NULL, as "
                 "applenotes2john.py does. Hash Source Column names which one was used. "
                 "A row is emitted only when its salt is 16 bytes, its key 24 bytes and its "
                 "iteration count at least 1, the three field checks in hashcat's "
                 "module_16200.c. hashcat also caps Z_PK at 10 digits and the iteration count "
                 "at 6; this artifact does not check those. The strings were checked against "
                 "that field layout, not run through hashcat or John. "
                 "Rows with an iteration count of 0 are not read. In tested samples every "
                 "0-iteration row that held a wrapped key held a 16-byte one, the layout the "
                 "Notes - Password Protected artifact labels as not covered by its cited "
                 "research, and one 0-iteration ICAccount row (iphone12_ios18) held a salt and "
                 "no key. A row read but refused for its salt or key length is counted in the "
                 "log; no tested sample had one. "
                 "This artifact does not filter on ZISPASSWORDPROTECTED, which Password "
                 "Protected Flag reports as stored. applenotes2john.py notes that the flag can "
                 "be 0 while the iteration count is non-zero, and in tested samples the "
                 "ICAccount row carried a 24-byte ZCRYPTOVERIFIER with ZISPASSWORDPROTECTED 0 "
                 "on hickman_ios13 and otto_ios17, so that row is missing from the Notes - "
                 "Password Protected artifact on those images. Password Hint is ZPASSWORDHINT "
                 "as stored. "
                 "Entity is the Core Data entity name, resolved from each row's Z_ENT through "
                 "Z_PRIMARYKEY. Entities seen in tested samples: ICAccount, ICNote, "
                 "ICAttachment, ICAttachmentPreviewImage and ICMedia. In tested samples every "
                 "emitted row of an image, the ICAccount row included, held the same salt "
                 "value, and on otto_ios17 the note, attachment, preview and media rows held "
                 "the same wrapped key. Whether they share one password was not tested. "
                 "On iphone11_ios17 and hc_ios18_7 the ICAccount row was the only one emitted, "
                 "while their notes, attachments and media held 16-byte keys with 0 iterations; "
                 "whether the account password opens those records was not tested. In tested "
                 "samples KDF Iterations held 20000 on every emitted row, and Password Hint "
                 "held one value across all rows of an image, or was empty on all of them "
                 "(hc_ios18_7). This artifact does not crack or decrypt anything. To try a "
                 "password list, save the hash string to a file and run "
                 "'hashcat -m 16200 -a 0 <file> <wordlist>'. "
                 "References: John the Ripper, https://github.com/openwall/john/blob/"
                 "edf64e8690b7770ff18a193cecc52b1ff21f6a33/run/applenotes2john.py; hashcat, "
                 "https://github.com/hashcat/hashcat/blob/"
                 "19c84e076fa6627a60fa32e7e352b96e45422d3a/src/modules/module_16200.c",
        "paths": ('*/NoteStore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | 3 rows (1 ICAccount, 2 ICNote)",
            "hickman_ios14": "iOS 14.3 | 4 rows (1 ICAccount, 3 ICNote)",
            "hickman_ios15": "iOS 15 | 5 rows (1 ICAccount, 4 ICNote)",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row (ICAccount)",
            "otto_ios17": "iOS 17.5.1 | 6 rows (1 ICAccount, 1 ICNote, 4 attachment and media)",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row (ICAccount)",
        }
    }
}

import re

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc)

TABLE = 'ZICCLOUDSYNCINGOBJECT'

# The documented scheme wraps a 16-byte note key with AES Key Wrap, which is 24 bytes
# on disk, and derives the wrapping key with PBKDF2. Some stores instead hold a 16-byte
# wrapped key with the iteration count zeroed; which one a store uses does not follow
# the iOS version alone (17.3 held 16-byte keys, 17.5.1 held 24-byte keys).
CLASSIC_WRAPPED_LEN = 24
REVISED_WRAPPED_LEN = 16


def _existing_columns(file_found):
    """Return the set of ZICCLOUDSYNCINGOBJECT column names present in this db."""
    return {row[0] for row in get_sqlite_db_records(
        file_found, f"SELECT name FROM pragma_table_info('{TABLE}')")}


def _variants(columns, name):
    """COALESCE over every numbered column Core Data made for one property name.

    A property that several entities in the table define gets ZNAME, ZNAME1, ...;
    a row fills only the variant of its own entity, so the first non-null one
    is that row's value. 'NULL' when the table has none of them.
    """
    found = sorted((c for c in columns if re.fullmatch(f'Z{name}\\d*', c)),
                   key=lambda c: (len(c), c))
    if not found:
        return 'NULL'
    return found[0] if len(found) == 1 else f"COALESCE({', '.join(found)})"


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
    # A hint with no wrapped key; in tested samples always the ICAccount record,
    # which the Entity column shows. Named by what is stored.
    return ('Hint stored, no wrapped key', 'n/a')


@artifact_processor
def notesPasswordProtected(context):
    data_headers = (
        ('Creation Date', 'datetime'), ('Last Modified', 'datetime'), 'Entity', 'Title',
        'Password Hint', 'Encryption Scheme', 'KDF Iterations', 'Wrapped Key Bytes',
        'Recoverability', 'Record ID')
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

        creation = _variants(columns, 'CREATIONDATE')
        modified = _variants(columns, 'MODIFICATIONDATE')
        title = _variants(columns, 'TITLE')
        hint = _first_present(columns, 'ZPASSWORDHINT')
        wrapped = _first_present(columns, 'ZCRYPTOWRAPPEDKEY')
        iterations = _first_present(columns, 'ZCRYPTOITERATIONCOUNT')

        query = f'''
            SELECT {creation}, {modified}, {title}, {hint},
                   LENGTH({wrapped}), {iterations}, Z_PK, Z_ENT
            FROM {TABLE}
            WHERE ZISPASSWORDPROTECTED = 1
              AND ({wrapped} IS NOT NULL OR {hint} IS NOT NULL)
            ORDER BY {creation}, Z_PK
        '''
        rows = list(get_sqlite_db_records(file_found, query))
        if not rows:
            continue
        entity_names = _entity_names(file_found)

        for created, changed, row_title, note_hint, wrapped_len, iters, row_id, z_ent in rows:
            scheme, recoverability = _classify(wrapped_len or 0)
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(created) if created else '',
                convert_cocoa_core_data_ts_to_utc(changed) if changed else '',
                entity_names.get(z_ent, f'Z_ENT {z_ent}'),
                row_title or '',
                note_hint or '',
                scheme,
                iters if iters is not None else '',
                wrapped_len if wrapped_len else '',
                recoverability,
                row_id))

        sources.append(context.get_relative_path(file_found))

    if data_list:
        recoverable = sum(1 for row in data_list if row[8].startswith('Recoverable'))
        logfunc(f'Notes: {len(data_list)} password-protected record(s), '
                f'{recoverable} in the recoverable scheme')

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _entity_names(file_found):
    """Map Core Data Z_ENT integers to entity names via Z_PRIMARYKEY.

    ZICCLOUDSYNCINGOBJECT holds several entities in one table (Core Data
    single-table inheritance); Z_ENT says which one a row is and Z_PRIMARYKEY
    names it, so an account record (ICAccount) is told apart from a note
    (ICNote) or an attachment. An empty mapping when the table is absent leaves
    rows labelled by raw Z_ENT.
    """
    return {row[0]: row[1] for row in get_sqlite_db_records(
        file_found, 'SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY')}


# hashcat's mode 16200 parser (src/modules/module_16200.c) takes the salt as exactly
# 32 hex characters, the key as exactly 48, and refuses an iteration count below 1.
HASH_SALT_LEN = 16
HASH_KEY_LEN = 24


def _asn_hash(z_pk, iterations, salt_blob, key_blob):
    """Assemble the ``$ASN$`` string for one record, or '' when hashcat would refuse it.

    Field order follows John the Ripper's applenotes2john.py:
    ``$ASN$*<Z_PK>*<iterations>*<salt hex>*<key hex>``.
    """
    if (not iterations or iterations < 1 or salt_blob is None or key_blob is None
            or len(salt_blob) != HASH_SALT_LEN or len(key_blob) != HASH_KEY_LEN):
        return ''
    return f'$ASN$*{z_pk}*{iterations}*{bytes(salt_blob).hex()}*{bytes(key_blob).hex()}'


@artifact_processor
def notesEncryptionKeys(context):
    data_headers = (
        'Entity', 'Record ID', 'Password Protected Flag', 'Password Hint',
        'KDF Iterations', 'Hash Source Column', 'Hash String ($ASN$, hashcat -m 16200)')
    data_list = []
    sources = []
    skipped = 0

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

        emitted = 0
        for (z_pk, z_ent, is_protected, note_hint, iters,
             salt_blob, wrapped_blob, verifier_blob) in rows:
            key_blob = wrapped_blob if wrapped_blob is not None else verifier_blob
            hash_string = _asn_hash(z_pk, iters, salt_blob, key_blob)
            if not hash_string:
                skipped += 1
                continue
            data_list.append((
                entity_names.get(z_ent, f'Z_ENT {z_ent}'),
                z_pk,
                is_protected if is_protected is not None else '',
                note_hint or '',
                iters,
                'ZCRYPTOWRAPPEDKEY' if wrapped_blob is not None else 'ZCRYPTOVERIFIER',
                hash_string))
            emitted += 1

        if emitted:
            sources.append(context.get_relative_path(file_found))

    if skipped:
        logfunc(f'Notes: {skipped} record(s) with key material skipped: salt, key length '
                'or iteration count outside what hashcat mode 16200 accepts')
    if data_list:
        accounts = sum(1 for row in data_list if row[0] == 'ICAccount')
        logfunc(f'Notes: {len(data_list)} encryption-key hash(es) built, '
                f'{accounts} on account records')

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
