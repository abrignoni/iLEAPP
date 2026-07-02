__artifacts_v2__ = {
    "protonMail": {
        "name": "Proton Mail - Decrypted Emails",
        "description": "Decrypted Proton Mail emails and attachments (requires the device keychain "
                       "in scripts/keychain/)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "pgpy, pycryptodome, ccl_bplist; a keychain plist placed in scripts/keychain/",
        "category": "Proton Mail",
        "notes": "Decryption requires the device keychain plist in scripts/keychain/. Email bodies and "
                 "attachments are decrypted with the account's PGP key. Message timestamps are Cocoa "
                 "(Mac absolute) time, stored as UTC.",
        "paths": ('*/group.ch.protonmail.protonmail.plist', '*/ProtonMail.sqlite*',
                  '*/Containers/Data/Application/*/tmp/*'),
        "output_types": "standard",
        "artifact_icon": "mail"
    }
}

import html
import json
import os
import plistlib
from base64 import b64decode
from io import BytesIO
from pathlib import Path

import ccl_bplist
import pgpy
from Crypto.Cipher import AES

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               check_in_embedded_media, convert_cocoa_core_data_ts_to_utc, logfunc)

_DECODE_ERRORS = (KeyError, ValueError, TypeError, IndexError, plistlib.InvalidFileException)
_IV_SIZE = 16

_QUERY = '''SELECT
    ZMESSAGE.ZTIME, ZMESSAGE.ZBODY, ZMESSAGE.ZMIMETYPE, ZMESSAGE.ZTOLIST, ZMESSAGE.ZREPLYTOS,
    ZMESSAGE.ZSENDER, ZMESSAGE.ZTITLE, ZMESSAGE.ZISENCRYPTED, ZMESSAGE.ZNUMATTACHMENTS,
    ZATTACHMENT.ZFILESIZE, ZATTACHMENT.ZFILENAME, ZATTACHMENT.ZMIMETYPE, ZATTACHMENT.ZHEADERINFO,
    ZATTACHMENT.ZLOCALURL, ZATTACHMENT.ZKEYPACKET
    FROM ZMESSAGE
    LEFT JOIN ZATTACHMENT ON ZMESSAGE.Z_PK = ZATTACHMENT.ZMESSAGE'''


def _build_keychain_values(plist):
    """Collect the protonmail keychain account -> v_Data entries from the keychain plist."""
    values = {}
    rows = plist if isinstance(plist, list) else [dd for d in plist for dd in plist[d]]
    for dd in rows:
        if isinstance(dd, dict) and 'svce' in dd and 'protonmail' in str(dd['svce']):
            values[dd['acct']] = dd['v_Data']
    return values


@artifact_processor
def protonMail(context):
    data_headers = (('Timestamp', 'datetime'), 'Sender', 'To Recipients', 'Reply To', 'Title',
                    'Body', 'Mime', 'Is encrypted?', 'File Size', ('Attachment', 'media'),
                    'Decrypted Attachment Filename', 'Type')
    data_list = []

    keychain_dir = Path(__file__).parents[1].joinpath('keychain')
    if not keychain_dir.exists() or len(os.listdir(keychain_dir)) <= 1:
        logfunc("No keychain provided")
        return data_headers, data_list, ''
    keychain_plist_path = ''
    for name in os.listdir(keychain_dir):
        if name.endswith('plist'):
            keychain_plist_path = keychain_dir.joinpath(name)
    if not keychain_plist_path:
        logfunc("No keychain plist found in scripts/keychain/")
        return data_headers, data_list, ''

    plist_name = db_name = ''
    files = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        files.append(file_found)
        if 'group.ch.protonmail.protonmail.plist' in file_found:
            plist_name = file_found
        elif file_found.endswith('ProtonMail.sqlite'):
            db_name = file_found
    if not (plist_name and db_name):
        logfunc("Proton Mail plist or database not found")
        return data_headers, data_list, ''

    with open(keychain_plist_path, 'rb') as f:
        keychain_values = _build_keychain_values(plistlib.load(f))
    try:
        main_key = keychain_values[b'NoneProtection']
    except KeyError:
        logfunc("No Protonmail data in the key chain")
        return data_headers, data_list, ''

    def decrypt_with_main_key(encrypted):
        iv = encrypted[:_IV_SIZE]
        cipher = AES.new(main_key, AES.MODE_CTR, initial_value=iv, nonce=b'')
        return cipher.decrypt(encrypted[_IV_SIZE:])

    with open(plist_name, 'rb') as p:
        prefplist = plistlib.load(p)
    enc_val = prefplist.get('authKeychainStoreKeyProtectedWithMainKey', 'empty')
    if enc_val == 'empty':
        enc_val = keychain_values.get(b'authKeychainStoreKeyProtectedWithMainKey')
    if not enc_val or enc_val == 'empty':
        logfunc('Decryption key not found in the keychain or the application plist.')
        return data_headers, data_list, ''

    keychain_store_plist1 = ccl_bplist.load(BytesIO(decrypt_with_main_key(enc_val)))
    keychain_store_plist = ccl_bplist.load(BytesIO(keychain_store_plist1[0]))
    keychain_store = ccl_bplist.deserialise_NsKeyedArchiver(keychain_store_plist,
                                                            parse_whole_structure=True)
    private_key = keychain_store['root']['NS.objects'][0]['privateKeyCoderKey']
    key, _ = pgpy.PGPKey.from_blob(private_key)
    pwd_key = keychain_store['root']['NS.objects'][0]['AuthCredential.Password']

    def decrypt_message(encm):
        if '-----BEGIN PGP MESSAGE-----' in encm:
            with key.unlock(pwd_key):
                assert key.is_unlocked
                decm = key.decrypt(pgpy.PGPMessage.from_blob(encm)).message
                return html.unescape(decm.encode('cp1252', errors='ignore').decode('utf8', errors='ignore'))
        return encm

    def decrypt_attachment_bytes(proton_path, key_packet, encfilename):
        att = None
        for root_dir, _, names in os.walk(proton_path):
            for fname in names:
                if encfilename in fname:
                    att = os.path.join(root_dir, fname)
                    break
            if att:
                break
        if not att:
            return None
        with key.unlock(pwd_key):
            assert key.is_unlocked
            with open(att, 'rb') as attfh:
                buf = b64decode(key_packet) + attfh.read()
                return key.decrypt(pgpy.PGPMessage.from_blob(buf)).message

    for row in get_sqlite_db_records(db_name, _QUERY):
        aggregatorto = aggregatorfor = ''
        decryptedtime = convert_cocoa_core_data_ts_to_utc(row[0])
        decryptedbody = decrypt_message(row[1])
        mime = row[2]

        to = json.loads(plistlib.loads(decrypt_with_main_key(row[3]))[0])
        aggregatorto = '; '.join(f"{r['Address']} {r['Name']}" for r in to)
        try:
            replyto = json.loads(plistlib.loads(decrypt_with_main_key(row[4]))[0])
            aggregatorfor = '; '.join(f"{r['Address']} {r['Name']}" for r in replyto)
        except _DECODE_ERRORS:
            aggregatorfor = ''
        try:
            sender = json.loads(plistlib.loads(decrypt_with_main_key(row[5]))[0])
            sender_info = f"{sender['Address']} {sender['Name']}"
        except _DECODE_ERRORS:
            sender_info = '<Not Decoded>'
        try:
            title = plistlib.loads(decrypt_with_main_key(row[6]))[0]
        except _DECODE_ERRORS:
            title = '<Not Decoded>'

        isencrypted = row[7]
        file_size = row[9]
        try:
            decfilename = plistlib.loads(decrypt_with_main_key(row[10]))[0]
        except _DECODE_ERRORS:
            decfilename = ''
        try:
            att_mimetype = plistlib.loads(decrypt_with_main_key(row[11]))[0]
        except _DECODE_ERRORS:
            att_mimetype = ''

        attachment_ref = ''
        if row[13]:
            try:
                objects = plistlib.loads(row[13])['$objects']
                encfilename = objects[2].split('/')[-1]
                guidi = objects[2].split('/')[-4]
            except _DECODE_ERRORS:
                encfilename = guidi = ''
            proton_path = ''
            if guidi:
                for match in files:
                    if f'/Data/Application/{guidi}/tmp/attachments' in match:
                        proton_path = match.split('/attachments')[0]
                        break
                    if f'\\Data\\Application\\{guidi}\\tmp\\attachments' in match:
                        proton_path = match.split('\\attachments')[0]
                        break
            if proton_path and encfilename:
                decbytes = decrypt_attachment_bytes(proton_path, row[14], encfilename)
                if decbytes:
                    attachment_ref = check_in_embedded_media(db_name, bytes(decbytes),
                                                             decfilename or encfilename)

        data_list.append((decryptedtime, sender_info, aggregatorto, aggregatorfor, title,
                          decryptedbody, mime, isencrypted, file_size, attachment_ref, decfilename,
                          att_mimetype))

    return data_headers, data_list, context.get_relative_path(db_name)
