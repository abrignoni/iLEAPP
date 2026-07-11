__artifacts_v2__ = {
    "keychain_wifi": {
        "name": "Keychain Wifi Credentials",
        "description": "Parses keychain to extract stored Wi-Fi credentials",
        "author": "@kobo220",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Keychain",
        "notes": "",
        "paths": (
            '*/keychain-backup.plist',
            '*/extra/KeychainDump/backup_keychain_v2.plist',
            '*/Keychains/keychain-2.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 10 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 11 rows",
        },
        "function": "keychain_wifi"
    },
    "keychain_web_passwords": {
        "name": "Keychain Web Passwords",
        "description": "Parses keychain to extract stored web passwords",
        "author": "@kobo220",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Keychain",
        "notes": "",
        "paths": (
            '*/keychain-backup.plist',
            '*/extra/KeychainDump/backup_keychain_v2.plist',
            '*/Keychains/keychain-2.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 15 rows",
            "felix_ios17": "iOS 17.6.1 | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
        },
        "function": "keychain_web_passwords"
    },
    "keychain_bluetooth_info": {
        "name": "Bluetooth Information",
        "description": "Parses keychain to extract the device's Bluetooth information",
        "author": "@kobo220",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Keychain",
        "notes": "",
        "paths": (
            '*/keychain-backup.plist',
            '*/extra/KeychainDump/backup_keychain_v2.plist',
            '*/Keychains/keychain-2.db*',
        ),
        "output_types": "none",
        "function": "keychain_bluetooth_info",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | files found",
            "dexter_ios18": "iOS 18.3.2 | files found",
            "felix_ios17": "iOS 17.6.1 | files found",
            "fsfull002_ios17": "iOS 17.1 | files found",
            "hc_ios18_7": "iOS 18.7.8 | files found",
            "iphone11_ios17": "iOS 17.3 | files found",
            "iphone12_ios18": "iOS 18.7 | files found",
            "iphone14plus_ios18": "iOS 18.0 | files found",
            "otto_ios17": "iOS 17.5.1 | files found",
        }
    },
    "keychain_bluetooth_paired": {
        "name": "Paired Bluetooth Devices",
        "description": "Parses keychain to extract the device's paired Bluetooth devices",
        "author": "@kobo220",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Keychain",
        "notes": "",
        "paths": (
            '*/keychain-backup.plist',
            '*/extra/KeychainDump/backup_keychain_v2.plist',
            '*/Keychains/keychain-2.db*',
            '*/com.apple.MobileBluetooth.ledevices.paired.db*',
            '*/com.apple.MobileBluetooth.devices.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 5 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
        },
        "function": "keychain_bluetooth_paired"
    },
    "keychain_mail_accounts": {
        "name": "Mail Accounts",
        "description": "Parses keychain to extract stored mail/calDAV/cardDAV account credentials",
        "author": "@kobo220",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-06-18",
        "requirements": "none",
        "category": "Keychain",
        "notes": "",
        "paths": (
            '*/keychain-backup.plist',
            '*/extra/KeychainDump/backup_keychain_v2.plist',
            '*/Keychains/keychain-2.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "at",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
        "function": "keychain_mail_accounts"
    },
}

from scripts.ilapfuncs import (
    device_info,
    artifact_processor,
    get_file_path,
    get_plist_file_content,
    get_plist_content,
    logfunc,
    open_sqlite_db_readonly,
    get_sqlite_db_records
)
from scripts.search_files import FileSeekerZip

import base64
import re
import struct
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

from Crypto.Cipher import AES

UDID_RE = re.compile(r"([0-9A-Fa-f]{40}|[0-9A-Fa-f]{8}-[0-9A-Fa-f]{16})")
_keychain_cache: dict[str, tuple] = {}

def _decode_der(data: bytes) -> dict:
    """
    Simple DER parser.
    This avoids adding another dependency. If things get more complicated may need full ASN1 DER library.
    Returns a dictionary of decoded key-value pairs.
    """
    result = {}
    pos = 0

    class DerParseError(ValueError):
        pass

    def read_length(data, pos):
        """Read DER length field"""
        if pos >= len(data):
            raise DerParseError("unexpected end of data while reading length")
        first = data[pos]
        pos += 1
        if first & 0x80 == 0:
            return first, pos
        num_bytes = first & 0x7f
        if num_bytes == 0 or num_bytes > len(data) - pos:
            raise DerParseError("invalid DER length")
        length = int.from_bytes(data[pos:pos+num_bytes], 'big')
        return length, pos + num_bytes

    def read_value(data, pos):
        """Read a single DER value"""
        if pos >= len(data):
            raise DerParseError("unexpected end of data while reading value")
        tag = data[pos]
        pos += 1
        length, pos = read_length(data, pos)
        end = pos + length
        if end > len(data):
            raise DerParseError("truncated DER value")
        value = data[pos:pos+length]
        return tag, value, pos + length

    def parse_string(data):
        """Decode UTF8 string or return base64 for binary data"""
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return base64.b64encode(data).decode('utf-8')

    # Skip outer container (SET or SEQUENCE), and bound iteration to its declared content
    end_pos = len(data)
    if data[pos] in (0x30, 0x31):  # SEQUENCE or SET
        pos += 1
        outer_length, pos = read_length(data, pos)
        end_pos = min(pos + outer_length, len(data))

    # Parse all items in the container
    while pos < end_pos:
        if end_pos - pos < 2:  # Not enough data for another item
            break
        try:
            # Expect SEQUENCE for each key-value pair
            tag, seq_data, pos = read_value(data, pos)

            if tag not in (0x30, 0x31):  # Not a SEQUENCE/SET
                continue

            # Parse the sequence contents
            seq_pos = 0
            key = None
            value = None

            while seq_pos < len(seq_data):
                item_tag, item_value, seq_pos = read_value(seq_data, seq_pos)

                if item_tag == 0x0c:  # UTF8String
                    decoded = parse_string(item_value)
                    if key is None:
                        key = decoded
                    else:
                        value = decoded
                elif item_tag == 0x02:  # INTEGER
                    value = int.from_bytes(item_value, 'big')
                elif item_tag == 0x04:  # OCTET STRING
                    value = item_value
                elif item_tag == 0x18:  # GeneralizedTime
                    value = parse_string(item_value)
                elif item_tag in (0x30, 0x31):  # Nested SEQUENCE/SET
                    value = item_value  # Keep as raw bytes for now

            if key is not None:
                result[key] = value
        except DerParseError as e:
            logfunc(f"Error parsing DER at position {pos}: {e}")
            break

    return result

def _normalize_date(date_str: str | datetime) -> datetime | None:
    """Normalize date string or datetime object to UTC datetime."""
    if date_str is None or date_str == "":
        return None
    if isinstance(date_str, datetime):
        if date_str.tzinfo is None:
            return date_str.replace(tzinfo=timezone.utc)
        return date_str
    if isinstance(date_str, bytes):
        date_str = date_str.decode('utf-8')
    # Truncate fractional seconds to 6 digits (Python's %f max) since ASN1 GeneralizedTime can have more
    if '.' in date_str:
        base, frac = date_str.split('.', 1)
        frac = frac.rstrip('Z')[:6]
        date_str = f"{base}.{frac}Z"
    # ASN1 GeneralizedTime with and without fractional seconds, plus ISO 8601
    for date_format in ("%Y%m%d%H%M%S.%fZ", "%Y%m%d%H%M%SZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    logfunc(f"Unrecognized keychain date format: {date_str}")
    return None

def _extract_udid(text: str) -> str | None:
    """Extract UDID from text, supporting both 40-char hex and 8-16 format. Returns UDID in uppercase."""
    match = UDID_RE.search(text)
    return match.group(1).upper() if match else None

def _find_keychain_for_zip(zip_path: Path) -> Path | None:
    """Check for external keychain plist (teamblue style) based on the zip file name or directory structure."""

    # Check if keychain plist exists in the same directory as the zip file
    # UDID should be in the zip file name (ie: UDID_files_full.zip)
    udid = _extract_udid(zip_path.name)
    if udid:
        keychain_path = zip_path.parent / f"{udid}_keychain.plist"
        return keychain_path if keychain_path.exists() else None

    # Check for UDID in parent-parent directory name
    # Check the zip's parent and parent-parent directories for keychain plists matching the UDID
    # (ie: UDID/fs/fs-partial-afu.zip)
    udid_dir = zip_path.parent.parent
    udid = _extract_udid(udid_dir.name)

    if not udid:
        # Not a teamblue style directory structure, give up on finding a keychain plist
        return None

    for keychain_path in (
        udid_dir / f"{udid}_keychain.plist",
        udid_dir.parent / f"{udid}_keychain.plist",
    ):
        if keychain_path.is_file():
            return keychain_path

    return None

def _decrypt_itb_key(data, decryption_keys) -> bytes | None:
    """Decrypt a key from the iTunes backup using the provided decryption keys and custom gcm."""

    _, key_class, key_klen = struct.unpack("<III", data[:12])
    key_dkey = decryption_keys[0].get(key_class)
    key_wkey = data[12:12+key_klen]
    key_data = data[12+key_klen:]

    if key_dkey is None:
        logfunc(f"No decryption key found for class {key_class}")
        return None

    if int.from_bytes(key_dkey['WRAP']) != 2:
        # Values x00 00 00 01 & 0x00 00 00 03 need device key, WPKY value for these is wrong, so we can't decrypt these items.
        return None

    try:
        key_uwkey = AES.new(key_dkey['Unwrapped'], AES.MODE_KW).unseal(key_wkey)  # type: ignore[attr-defined]  # pylint: disable=no-member
        decrypted_data = gcm_decrypt(key_uwkey, b"", key_data, b"")
        return decrypted_data
    except ValueError as e:
        logfunc(f"Error unsealing key: {e}")
        return None

def _decrypt_data(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes | None:
    """Decrypt data using AES-GCM. Returns decrypted data or None if decryption fails."""

    try:
        gcm = AES.new(key, AES.MODE_GCM, nonce=iv)
        decrypted = gcm.decrypt_and_verify(ciphertext, tag)
        return decrypted
    except ValueError:
        return None

def _is_clean_text(text: str) -> bool:
    """Check if text contains only clean Unicode characters (no control characters)."""

    for char in text:
        category = unicodedata.category(char)

        if category in ('Cc', 'Cf', 'Co', 'Cs', 'Cn'):
            return False
    return True

def _decode_value(value):
    """
        Decode a value from the teamblue keychain plist, which may be a UTF-8 string or binary data.
        Returns a string if it's clean UTF-8, otherwise returns bytes.
    """
    if not isinstance(value, bytes):
        return value

    if b"\x00" in value:
        return value

    try:
        text = value.decode('utf-8')
        if _is_clean_text(text):
            return text
    except UnicodeDecodeError:
        pass

    return value

def _decode_values(plist):
    """
        Recursively decode values in the teamblue keychain plist.
        Old format had all values as bytes.
    """

    if isinstance(plist, dict):
        return {
            k: _decode_values(v)
            for k, v in plist.items()
        }

    if isinstance(plist, list):
        return [_decode_values(v) for v in plist]

    if isinstance(plist, tuple):
        return tuple(_decode_values(v) for v in plist)

    if isinstance(plist, bytes):
        return _decode_value(plist)

    return plist

def _get_type_map(keychain_db_path) -> dict:
    """Get a mapping of UUID to key type (inet, genp, keys) from the keychain database."""

    uuid_to_type = {}

    queries = {
        "inet": "SELECT uuid FROM inet WHERE uuid IS NOT NULL",
        "genp": "SELECT uuid FROM genp WHERE uuid IS NOT NULL",
        "keys": "SELECT uuid FROM keys WHERE uuid IS NOT NULL",
    }

    for key_type, query in queries.items():
        for record in get_sqlite_db_records(keychain_db_path, query):
            uuid_to_type[record['uuid']] = key_type

    return uuid_to_type

def parse_keychain(context) -> tuple[list[dict], list[dict], list[dict], str]:
    """
        Process found files for keychain data. Determines keychain source type and hands off to the appropriate parser.
        Caches results to avoid duplicate parsing across artifacts.
        Returns tuple of (inet_records, genp_records, keys_records, source_path).
    """

    seeker = context.get_seeker()

    itunes_keychain = context.get_source_file_path("keychain-backup.plist")
    teamred_keychain = context.get_source_file_path("backup_keychain_v2.plist")
    teamblue_keychain = _find_keychain_for_zip(Path(seeker.zip_file.filename)) if isinstance(seeker, FileSeekerZip) and seeker.zip_file.filename else None
    keychain_db_path = context.get_source_file_path("keychain-2.db")

    # Check for teamred first, old versions of teamred might also have a keychain-backup.plist which results in false iTunes detection
    if teamred_keychain:
        source_path = teamred_keychain
    elif itunes_keychain:
        source_path = itunes_keychain
    elif teamblue_keychain:
        source_path = teamblue_keychain
    else:
        return [], [], [], ""

    cache_key = str(source_path)
    if cache_key in _keychain_cache:
        # logfunc(f"Using cached keychain data for {source_path}")
        return _keychain_cache[cache_key]

    inet_records, genp_records, keys_records = [], [], []

    # Same ordering as above.
    if teamred_keychain:
        source_path = teamred_keychain
        inet_records, genp_records, keys_records = _parse_teamred_keychain(source_path, keychain_db_path)

    elif itunes_keychain:
        decryption_keys = getattr(seeker, 'decryption_keys', None)
        if decryption_keys is not None:
            inet_records, genp_records, keys_records = _parse_itunes_keychain(source_path, decryption_keys)
        else:
            logfunc("No decryption keys found in iTunes seeker, cannot parse encrypted keychain.")

    elif teamblue_keychain:
        if teamblue_keychain.is_file():
            dst_dir = Path(context.get_data_folder())
            file_name = teamblue_keychain.name
            source_path = dst_dir / file_name
            copy2(teamblue_keychain, dst_dir / file_name)

        inet_records, genp_records, keys_records = _parse_teamblue_keychain(source_path)

    result = (inet_records, genp_records, keys_records, str(source_path))
    _keychain_cache[cache_key] = result

    return result

def _parse_itunes_keychain(source_path, decryption_keys) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse an iTunes backup keychain, uses the decrypted keys from Context's seeker."""

    keychain_plist = get_plist_file_content(source_path)

    if not isinstance(keychain_plist, dict):
        logfunc(f"Unexpected keychain plist format in {source_path}, expected a dictionary at the top level.")
        return [], [], []

    inet_records = []
    genp_records = []
    keys_records = []

    for blob_key, record_list in (("inet", inet_records), ("genp", genp_records), ("keys", keys_records)):
        for item in keychain_plist.get(blob_key, []):
            if not isinstance(item, dict):
                continue
            item_data = item.get("v_Data")
            item_persistref = item.get('v_PersistentRef')
            if not isinstance(item_data, bytes):
                continue
            decrypted_data = _decrypt_itb_key(item_data, decryption_keys)
            if decrypted_data is not None:
                decoded_der = _decode_der(decrypted_data)
                record_list.append(decoded_der | {"v_PersistentRef": item_persistref})

    return inet_records, genp_records, keys_records

def _parse_teamred_keychain(source_path, keychain_db_path=None) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse a TeamRed keychain."""

    keychain_plist = get_plist_file_content(source_path)

    if not isinstance(keychain_plist, dict):
        logfunc(f"Unexpected keychain plist format in {source_path}, expected a dictionary at the top level.")
        return [], [], []

    inet_records = []
    genp_records = []
    keys_records = []

    class_keys = keychain_plist["classKeyIdxToUnwrappedMetadataClassKey"]

    if not isinstance(class_keys, dict):
        logfunc(f"Unexpected class key format in {source_path}, expected a dictionary for classKeyIdxToUnwrappedMetadataClassKey.")
        return [], [], []

    keychain_entries = keychain_plist["keychainEntries"]

    # Define this here, but it will be lazy loaded only if needed
    uuid_type_map = None

    for entry in keychain_entries:
        if not isinstance(entry, dict):
            continue

        class_key_idx = entry.get("classKeyIdx")
        if class_key_idx is None:
            logfunc(f"Class key index not found in entry {entry.get('rowID')}, skipping entry")
            continue
        class_key = class_keys.get(str(class_key_idx))

        if class_key is None:
            logfunc(f"Class key for index {class_key_idx} not found, unable to decrypt metadata")
            continue

        metadata_wrapped_key_raw = entry["metadata"]["wrappedKey"]
        metadata_wrapped_key_plist = get_plist_content(metadata_wrapped_key_raw)

        if not isinstance(metadata_wrapped_key_plist, dict):
            continue

        key_iv = metadata_wrapped_key_plist.get("SFInitializationVector")
        key_ct = metadata_wrapped_key_plist.get("SFCiphertext")
        key_tag = metadata_wrapped_key_plist.get("SFAuthenticationCode")

        if not isinstance(key_iv, bytes) or not isinstance(key_ct, bytes) or not isinstance(key_tag, bytes):
            continue

        metadata_key = _decrypt_data(key_ct, class_key, key_iv, key_tag)

        if metadata_key is None:
            logfunc(f"Failed to decrypt metadata key for entry {entry['rowID']}, skipping entry")
            continue

        metadata_ciphertext_raw = entry["metadata"]["ciphertext"]
        metadata_ciphertext_plist = get_plist_content(metadata_ciphertext_raw)

        if not isinstance(metadata_ciphertext_plist, dict):
            continue

        meta_iv = metadata_ciphertext_plist.get("SFInitializationVector")
        meta_ct = metadata_ciphertext_plist.get("SFCiphertext")
        meta_tag = metadata_ciphertext_plist.get("SFAuthenticationCode")

        if not isinstance(meta_iv, bytes) or not isinstance(meta_ct, bytes) or not isinstance(meta_tag, bytes):
            continue

        decrypted_metadata = _decrypt_data(meta_ct, metadata_key, meta_iv, meta_tag)
        if decrypted_metadata is None:
            logfunc(f"Failed to decrypt metadata for entry {entry['rowID']}, skipping entry")
            continue
        metadata = _decode_der(decrypted_metadata)

        data_key = entry["data"]["unwrappedKey"]
        data_ciphertext = entry["data"]["ciphertext"]
        data_ciphertext_plist = get_plist_content(data_ciphertext)

        if not isinstance(data_ciphertext_plist, dict):
            continue

        data_iv = data_ciphertext_plist.get("SFInitializationVector")
        data_ct = data_ciphertext_plist.get("SFCiphertext")
        data_tag = data_ciphertext_plist.get("SFAuthenticationCode")

        if not isinstance(data_iv, bytes) or not isinstance(data_ct, bytes) or not isinstance(data_tag, bytes):
            continue

        decrypted_data = _decrypt_data(data_ct, data_key, data_iv, data_tag)
        if decrypted_data is None:
            logfunc(f"Failed to decrypt data for entry {entry['rowID']}, skipping entry")
            continue
        data_obj = _decode_der(decrypted_data)

        table = entry.get("table")

        # Older versions of the plist did not include the table name, so we need to use the keychain db to cross-reference UUIDs.
        if table is None and keychain_db_path is not None:
            if uuid_type_map is None:
                uuid_type_map = _get_type_map(keychain_db_path)
            table = uuid_type_map.get(metadata.get("UUID"))

        if table == "inet":
            inet_records.append(
                metadata | data_obj
            )
        elif table == "genp":
            genp_records.append(
                metadata | data_obj
            )
        elif table == "keys":
            keys_records.append(
                metadata | data_obj
            )

    return inet_records, genp_records, keys_records

def _parse_teamblue_keychain(source_path) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse a TeamBlue keychain. Expects external plist to exist next to the zip file, or up to two directories up, with the UDID in the file name."""

    keychain_plist = get_plist_file_content(source_path)
    keychain_plist = _decode_values(keychain_plist)

    if not isinstance(keychain_plist, dict):
        logfunc(f"Unexpected keychain plist format in {source_path}, expected a dictionary at the top level.")
        return [], [], []

    inet_raw = keychain_plist.get("inet", [])
    genp_raw = keychain_plist.get("genp", [])
    keys_raw = keychain_plist.get("keys", [])

    inet_records = [r for r in inet_raw if isinstance(r, dict)] if isinstance(inet_raw, list) else []
    genp_records = [r for r in genp_raw if isinstance(r, dict)] if isinstance(genp_raw, list) else []
    keys_records = [r for r in keys_raw if isinstance(r, dict)] if isinstance(keys_raw, list) else []

    return inet_records, genp_records, keys_records

@artifact_processor
def keychain_web_passwords(context):
    data_headers = ('Server', 'Account', 'Password', 'Label', 'Desc', ('Created', 'datetime'), ('Modified', 'datetime'), 'Tombstoned')
    data_list = []

    inet_records, _, _, source_path = parse_keychain(context)

    for inet in inet_records:
        if inet.get("agrp") == "com.apple.cfnetwork" and inet.get("atyp") == "form":
            srvr = inet.get("srvr", "")
            acct = inet.get("acct", "")
            labl = inet.get("labl", "")
            desc = inet.get("desc", "")
            password = inet.get("v_Data", b"")

            if isinstance(password, bytes):
                password = password.decode("utf-8", errors="backslashreplace")

            cdat = _normalize_date(inet.get("cdat", ""))
            mdat = _normalize_date(inet.get("mdat", ""))
            deleted = inet.get("tomb", 0) in ("1", b"1", 1, True)

            data_list.append((
                srvr,
                acct,
                password,
                labl,
                desc,
                cdat,
                mdat,
                deleted,
            ))

    return data_headers, data_list, source_path

@artifact_processor
def keychain_wifi(context):
    data_headers = ('SSID', 'Password', ('Created', 'datetime'), ('Modified', 'datetime'), 'Tombstoned')
    data_list = []

    _, genp_records, _, source_path = parse_keychain(context)
    for genp in genp_records:
        if genp.get("agrp") == "apple" and genp.get("svce") == "AirPort":
            ssid = genp.get("acct", "")
            password = genp.get("v_Data", b"")

            if isinstance(password, bytes):
                password = password.decode("utf-8", errors="backslashreplace")

            cdat = _normalize_date(genp.get("cdat", ""))
            mdat = _normalize_date(genp.get("mdat", ""))
            deleted = genp.get("tomb", 0) in ("1", b"1", 1, True)

            data_list.append((
                ssid,
                password,
                cdat,
                mdat,
                deleted,
            ))

    return data_headers, data_list, source_path

@artifact_processor
def keychain_bluetooth_info(context):
    _, genp_records, _, source_path = parse_keychain(context)
    mac_ids = set()
    for genp in genp_records:
        if genp.get("agrp") == "com.apple.bluetooth" and genp.get("acct") == "Identity Root Key":
            v_data = genp.get("v_Data", b"")
            if isinstance(v_data, str):
                v_data = v_data.encode()
            irk_plist = get_plist_content(v_data)

            if not isinstance(irk_plist, dict):
                logfunc(f"Unexpected IRK data format for UUID: {genp.get('UUID', 'unknown')} in {source_path}. Expected a plist dictionary.")
                continue

            irk = irk_plist.get("KEY", b"")
            if irk and isinstance(irk, bytes):
                device_info("Network", "Bluetooth IRK", base64.b64encode(irk).decode(), source_path)

        elif genp.get("agrp") == "com.apple.bluetooth" and genp.get("svce") == "MobileBluetooth":
            v_data = genp.get("v_Data", b"")
            if isinstance(v_data, str):
                v_data = v_data.encode()
            plist = get_plist_content(v_data)
            if not isinstance(plist, dict):
                logfunc(f"Unexpected MobileBluetooth data format for UUID: {genp.get('UUID', 'unknown')} in {source_path}. Expected a plist dictionary.")
                continue
            mac = plist.get("LocalAddress")
            if mac and mac not in mac_ids:
                mac_ids.add(mac)
                device_info("Network", "Bluetooth Address", mac, source_path)

    return (), [], source_path

@artifact_processor
def keychain_bluetooth_paired(context):
    data_headers = ('Name', 'MAC', 'IRK', 'UUID', ('Created', 'datetime'), ('Modified', 'datetime'), 'Tombstoned')
    data_list = []

    _, genp_records, _, source_path = parse_keychain(context)

    files_found = context.get_files_found()

    paired_db_path = get_file_path(files_found, "com.apple.MobileBluetooth.ledevices.paired.db")
    paired_plist_path = get_file_path(files_found, "com.apple.MobileBluetooth.devices.plist")

    db = open_sqlite_db_readonly(paired_db_path)
    cursor = db.cursor() if db else None

    paired_plist = get_plist_file_content(paired_plist_path) if paired_plist_path else None

    for genp in genp_records:
        mac = genp.get("acct", "")
        uuid = genp.get("labl", "")
        cdat = _normalize_date(genp.get("cdat", ""))
        mdat = _normalize_date(genp.get("mdat", ""))
        deleted = genp.get("tomb", 0) in ("1", b"1", 1, True)

        if genp.get("agrp") == "com.apple.bluetooth" and genp.get("svce") == "BluetoothLE":
            mac = mac.split(" ")[1] if " " in mac else mac

            raw_data = genp.get("v_Data", b"")
            if isinstance(raw_data, str):
                raw_data = raw_data.encode()
            irk_plist = get_plist_content(raw_data)
            if not isinstance(irk_plist, dict):
                irk = ""

            else:
                irk = irk_plist.get("Remote IRK", b"")

            if cursor:
                cursor.execute("SELECT Name FROM PairedDevices WHERE ResolvedAddress LIKE ?", (f"%{mac}",))
                row = cursor.fetchone()
                name = row[0] if row else ""
            else:
                name = ""

            data_list.append((
                name,
                mac,
                base64.b64encode(irk).decode() if irk and isinstance(irk, bytes) else "",
                uuid,
                cdat,
                mdat,
                deleted,
            ))

        elif genp.get("agrp") == "com.apple.bluetooth" and genp.get("svce") == "MobileBluetooth" and isinstance(paired_plist, dict):

            raw_data = genp.get("v_Data", b"")
            if isinstance(raw_data, str):
                raw_data = raw_data.encode()
            irk_plist = get_plist_content(raw_data)
            if not isinstance(irk_plist, dict):
                name = ""
                irk = ""

            else:
                irk = irk_plist.get("MagicAccIRK", "")
                if isinstance(irk, str):
                    irk = bytes.fromhex(irk.replace("-", ""))

                device = paired_plist.get(mac)
                if not isinstance(device, dict):
                    name = ""
                else:
                    name = device.get("UserNameKey")
                    if name is None:
                        name = device.get("Name", "")

            data_list.append((
                name,
                mac,
                base64.b64encode(irk).decode() if irk and isinstance(irk, bytes) else "",
                uuid,
                cdat,
                mdat,
                deleted,
            ))

    if db:
        db.close()

    return data_headers, data_list, source_path

@artifact_processor
def keychain_mail_accounts(context):
    data_headers = ('Server', 'Account', 'Password', 'Type', ('Created', 'datetime'), ('Modified', 'datetime'), 'Tombstoned')
    data_list = []

    _, genp_records, _, source_path = parse_keychain(context)

    svce_match = re.compile(r"com\.apple\.account\.(SMTP|IMAP|CardDAV|CalDAV)\.password")

    for genp in genp_records:
        svce = genp.get("svce", "")

        if isinstance(svce, bytes):
            svce = svce.decode('utf-8', errors='ignore')
        elif not isinstance(svce, str):
            continue

        match = svce_match.fullmatch(svce)

        if genp.get("agrp") != "apple" or not match:
            continue

        svce_type = match.group(1)

        acct = genp.get("acct", "")
        if isinstance(acct, bytes):
            acct = acct.decode('utf-8', errors='ignore')
        elif not isinstance(acct, str):
            continue
        if "@" not in acct:
            continue
        account, server = acct.rsplit("@", 1)

        cdat = _normalize_date(genp.get("cdat", ""))
        mdat = _normalize_date(genp.get("mdat", ""))
        deleted = genp.get("tomb", 0) in ("1", b"1", 1, True)

        password = genp.get("v_Data", b"")
        if isinstance(password, bytes):
            try:
                password = password.decode("utf-8")
            except UnicodeDecodeError:
                password = base64.b64encode(password).decode("utf-8")

        data_list.append((
            server,
            account,
            password,
            svce_type,
            cdat,
            mdat,
            deleted,
        ))

    return data_headers, data_list, source_path



# ============================================================
# Apple AES-GCM helpers (null-IV support for iOS keychain)
# Implemented from NIST SP 800-38D, using an LLM
# Move to a shared module if reuse is needed elsewhere.
# ============================================================
# import struct
# from Crypto.Cipher import AES

_GCM_R = 0xE1000000000000000000000000000000

def _gf128_mul(X, Y):
    Z, V = 0, X
    for _ in range(128):
        if Y & (1 << 127):
            Z ^= V
        Y = (Y << 1) & ((1 << 128) - 1)
        V = (V >> 1) ^ _GCM_R if V & 1 else V >> 1
    return Z

def _ghash(H, data):
    Y = 0
    for i in range(0, len(data), 16):
        Y = _gf128_mul(Y ^ int.from_bytes(data[i:i+16], "big"), H)
    return Y

def _inc32(block):
    arr = bytearray(block)
    for i in range(15, 11, -1):
        arr[i] = (arr[i] + 1) & 0xFF
        if arr[i] != 0:
            break
    return bytes(arr)

def _pad16(data):
    r = len(data) % 16
    return data + b"\x00" * (16 - r if r else 0)

def gcm_decrypt(key, nonce, ciphertext, aad=b""):
    if len(ciphertext) < 16:
        raise ValueError("ciphertext too short to contain a GCM tag")
    tag, ciphertext = ciphertext[-16:], ciphertext[:-16]
    ecb = AES.new(key, AES.MODE_ECB)
    H   = int.from_bytes(ecb.encrypt(b"\x00" * 16), "big")
    J0  = (nonce + b"\x00\x00\x00\x01") if len(nonce) == 12 else b"\x00" * 16
    tag_mask = ecb.encrypt(J0)
    counter, plaintext = _inc32(J0), bytearray()
    for i in range(0, len(ciphertext), 16):
        ks      = ecb.encrypt(counter)
        counter = _inc32(counter)
        plaintext.extend(a ^ b for a, b in zip(ks, ciphertext[i:i+16]))
    S = _ghash(H, _pad16(aad) + _pad16(ciphertext) + struct.pack(">QQ", len(aad)*8, len(ciphertext)*8))
    if bytes(a ^ b for a, b in zip(S.to_bytes(16, "big"), tag_mask)) != tag:
        raise ValueError("GCM tag mismatch — wrong key, nonce, or corrupted data")
    return bytes(plaintext)

# ============================================================
# End Apple AES-GCM helpers
# ============================================================
