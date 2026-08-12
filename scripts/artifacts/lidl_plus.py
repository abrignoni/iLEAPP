"""
Parses Apple iOS Lidl Plus application artifacts.
"""
# pylint: disable=too-many-lines

import os
import json
from json import JSONDecodeError
import re
import sqlite3
import base64
from hashlib import sha256, md5
from urllib.parse import urlparse, unquote_plus
from datetime import timezone, datetime
from scripts.artifacts.keychain import parse_keychain
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.html_safe import esc, safe_join
from scripts.ilapfuncs import (
    open_sqlite_db_readonly, does_column_exist_in_db, convert_unix_ts_to_utc,
    convert_cocoa_core_data_ts_to_utc, get_plist_file_content, get_plist_content,
    check_in_media, artifact_processor, logfunc
)

SOURCE_FILE_NAME = 'Source File Name'

__artifacts_v2__ = {
    "lidl_shopping_list": {
        "name": "Lidl Plus - Shopping List",
        "description": "Extracts shopping lists and item details.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Application Support/databases/ShoppingListDatabase.db*",
                  "*/Library/Caches/com.onevcat.Kingfisher.ImageCache.default/*",),
        "output_types": [ "standard" ],
        "artifact_icon": "clipboard"
    },
    "lidl_tickets": {
        "name": "Lidl Plus - Ticket List",
        "description": "Extracts cached ticket and transaction metadata.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "standard" ],
        "artifact_icon": "file-text"
    },
    "lidl_receipt_items": {
        "name": "Lidl Plus - Receipt Items",
        "description": "Extracts purchased items from cached receipt details.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "standard" ],
        "html_columns": [ "Line Item" ],
        "artifact_icon": "list"
    },
    "lidl_payment_methods": {
        "name": "Lidl Plus - Payment Methods",
        "description": "Extracts cached payment methods and Lidl Pay profile status.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "standard" ],
        "artifact_icon": "credit-card"
    },
    "lidl_loyalty_card": {
        "name": "Lidl Plus - Loyalty Card",
        "description": "Extracts cached payment QR data and the derived loyalty card number.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "standard" ],
        "artifact_icon": "credit-card"
    },
    "lidl_promotion_details": {
        "name": "Lidl Plus - Promotion Details",
        "description": "Extracts cached coupon and promotion details.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",
                  "*/Library/Caches/com.onevcat.Kingfisher.ImageCache.default/*",),
        "output_types": [ "standard" ],
        "artifact_icon": "tag"
    },
    "lidl_product_details": {
        "name": "Lidl Plus - Product Details",
        "description": "Extracts cached product details.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",
                  "*/Library/Caches/com.onevcat.Kingfisher.ImageCache.default/*",),
        "output_types": [ "standard" ],
        "artifact_icon": "package"
    },
    "lidl_searched_terms": {
        "name": "Lidl Plus - Searched Terms",
        "description": "Extracts cached product-search requests and sequence metadata.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "standard" ],
        "html_columns": [ "Returned Products" ],        
        "artifact_icon": "search"
    },
    "lidl_store_searches": {
        "name": "Lidl Plus - Store Searches",
        "description": "Extracts cached store-search requests, request coordinates, and returned stores.",  # pylint: disable=line-too-long
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",),
        "output_types": [ "all" ],
        "artifact_icon": "search"
    },
    "lidl_offers": {
        "name": "Lidl Plus - Offers",
        "description": "Extracts cached promotional offer data.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",
                  "*/Library/Caches/com.onevcat.Kingfisher.ImageCache.default/*",),
        "output_types": [ "standard" ],
        "artifact_icon": "tag"
    },
    "lidl_mypoints": {
        "name": "Lidl Plus - Loyalty Points Marketplace",
        "description": "Extracts cached loyalty-points marketplace rewards and account points metadata.",   # pylint: disable=line-too-long
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Caches/com.lidl.eci.lidl.plus/Cache.db*",
                  "*/Library/Caches/com.onevcat.Kingfisher.ImageCache.default/*",),
        "output_types": [ "standard" ],
        "artifact_icon": "gift"
    },
    "lidl_last_known_location": {
        "name": "Lidl Plus - Last Known Location",
        "description": "Extracts the last known location stored by the application.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/"
                  "Preferences/com.lidl.eci.lidl.plus.plist",),
        "output_types": [ "all" ],
        "artifact_icon": "map-pin"
    },
    "lidl_selfscan_basket": {
        "name": "Lidl Plus - Self Scanning Basket",
        "description": "Extracts self-scanning basket items.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/"
            "Application Support/SelfScanning/selfScanning.sqlite*",
        ),
        "output_types": ["standard"],
        "artifact_icon": "shopping-cart"
    },
    "lidl_selfscan_journey": {
        "name": "Lidl Plus - Self Scanning Journey",
        "description": "Extracts self-scanning barcode events.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/"
            "Application Support/SelfScanning/selfScanning.sqlite*",
        ),
        "output_types": ["standard"],
        "artifact_icon": "align-justify"
    },
    "lidl_selfscan_removed": {
        "name": "Lidl Plus - Removed Self Scanning Items",
        "description": "Extracts removed self-scanning basket items.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/"
            "Application Support/SelfScanning/selfScanning.sqlite*",
        ),
        "output_types": ["standard"],
        "artifact_icon": "trash-2"
    },
    "lidl_grocery_pickup_cart": {
        "name": "Lidl Plus - Grocery Pickup Cart",
        "description": "Extracts Click&Collect grocery pickup cart contents.",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/"
            "Application Support/GroceryPickup/groceryPickup.sqlite*",
            "*/keychain-backup.plist",
            "*/extra/KeychainDump/backup_keychain_v2.plist",
            "*/Keychains/keychain-2.db*"
        ),
        "output_types": [ "standard" ],
        "html_columns": [ "Validations" ],
        "artifact_icon": "shopping-bag"
    },
    "lidl_account": {
        "name": "Lidl Plus - Account",
        "description": "Extracts user account information stored in the iOS Keychain",
        "author": "@djangofaiola",
        "creation_date": "2026-07-03",
        "last_update_date": "2026-08-12",
        "requirements": "none",
        "category": "Lidl Plus",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": (
            "*/keychain-backup.plist",
            "*/extra/KeychainDump/backup_keychain_v2.plist",
            "*/Keychains/keychain-2.db*"
        ),
        "output_types": [ "html", "tsv", "lava" ],
        "artifact_icon": "user"
    },
}

# Constants
COMMA_SEP = ', '
LIST_SEP = '|'
SOURCE_PATH_NOTE = f"Refer to the '{SOURCE_FILE_NAME}' column to identify the exact " \
                   "device location of the origin file."

# Lidl Bundle ID
LIDL_BUNDLE_ID = 'com.lidl.eci.lidl.plus'

# Team ID
LIDL_TEAM_ID = 'P593BEJ5Y8'

# Observed keys in the Lidl Plus storedUser Keychain payload
LIDL_KNOWN_STORED_USER_KEYS = {
    'sub',
    'name',
    'middle_name',
    'email',
    'phone_number',
    'phone_prefix_number',
    'birthdate',
    'amr',
}

# Default decryption parameters for SQLCipher
DEFAULT_CIPHER_PARAMS = {
    'kdf_iterations': 256000,
    'hmac_algorithm': 'sha512',
    'kdf_algorithm': 'sha512'
}

# Database encryption configurations
DB_CONFIGS = {
    'selfScanning.sqlite': {
        'static_keys': [ '20Lidl26' ],
        'keychain': None,
        'cipher_version': 'SQLCipher4',
        'cipher_params': {
            'kdf_iterations': 256000,
            'hmac_algorithm': 'sha512',
            'kdf_algorithm': 'sha512'
        }
    },

    'groceryPickup.sqlite': {
        'static_keys': None,
        'keychain': {
            'access_group': f"{LIDL_TEAM_ID}.{LIDL_BUNDLE_ID}",
            'account': 'database_key',
            'service': LIDL_BUNDLE_ID,
            'expected_length': None
        },
        'cipher_version': 'GRDB',
        'cipher_params': {
            'kdf_iterations': 256000,
            'hmac_algorithm': 'sha512',
            'kdf_algorithm': 'sha512'
        }
    }
}

# Cache.db query
LIDL_CACHE_DB_QUERY = """
    SELECT
        cr.entry_ID,
        CAST(strftime("%s", cr.time_stamp) AS INTEGER) AS cache_time,
        cr.request_key,
        crd.isDataOnFS,
        crd.receiver_data
    FROM cfurl_cache_response AS cr
    LEFT JOIN cfurl_cache_receiver_data AS crd ON (cr.entry_ID = crd.entry_ID)
    WHERE cr.request_key REGEXP "{regex_pattern}"
    ORDER BY cache_time DESC
    """
# Ticket List
RE_CACHE_DB_TICKET_LIST = (
    r"^https:\/\/tickets\.lidlplus\.com\/api\/(v\d+)\/[A-Z]{2}\/tickets\?"
)
# Ticket Detail
RE_CACHE_DB_TICKET_DETAIL = (
    r"^https:\/\/tickets\.lidlplus\.com\/api\/(v\d+)\/[A-Z]{2}\/tickets\/"
)
RE_RECEIPT_SPAN_PATTERN = re.compile(
    r'<span\b(?P<attrs>[^>]*)>(?P<content>.*?)</span>',
    re.I | re.S
)
RE_RECEIPT_ATTR_PATTERN = re.compile(
    r'([^\s=]+)\s*=\s*"([^"]*)"',
    re.S
)
RE_RECEIPT_DISCOUNT_CONTENT_PATTERN = re.compile(
    r'(?P<description>.*?)'
    r'(?P<tax>\d+%)\s+'
    r'(?P<discount>-\d+,\d+)\s*$',
    re.S
)
# Payment Methods
RE_CACHE_DB_PAYMENT_METHODS = (
    r"^https?://payments\.lidlplus\.com/"
    r"(?:payment-methods/v\d+/lidl/[A-Z]{2}/wallet/all"
    r"|user-profiles/v\d+/lidl/[A-Z]{2}/(?:store|wallet))"
    r"(?:\?.*)?$"
)
# Payment QR
RE_CACHE_DB_PAYMENT_QR = (
    r"^https?:\/\/payments\.lidlplus\.com\/payment-methods\/v\d+\/lidl\/[A-Z]{2}\/store\/qr$"
)
# Coupon Promotion Details
RE_CACHE_DB_PROMOTION_DETAILS = (
    r"^https?:\/\/coupons\.lidlplus\.com\/app\/api\/v\d+\/(?:[A-Z]{2}\/)?promotionsdetails\/"
)
# Product Showcase Details
RE_CACHE_DB_PRODUCT_SHOWCASE = (
    r"^https?:\/\/productshowcase\.lidlplus\.com\/products\/v\d+\/"
)

# Product Search Terms Endpoint
RE_CACHE_DB_SEARCHED_TERMS = (
    r"^https?:\/\/shopping-list\.lidlplus\.com\/api\/v\d+\/[A-Z]{2}\/store\/([A-Z0-9]+)"
    r"\/search\?q=(.*)$"
)

# Store Search / Autocomplete
RE_CACHE_DB_STORE_SEARCHES = (
    r"^https?://stores\.lidlplus\.com/api/v\d+/autocomplete/[A-Z]{2}\?(?:[^#]*)$"
)

# Offers Details
RE_CACHE_DB_OFFERS = (
    r"^https?:\/\/offers\.lidlplus\.com\/app\/api\/v\d+\/"
)

# Loyalty Points Marketplace
RE_CACHE_DB_MYPOINTS = (
    r"^https?:\/\/mypoints\.lidl\.com\/mobile-bff\/api\/v\d+\/(?:[A-Z]{2}\/)?marketplace\/"
)

# Pattern to normalize timezone offsets from +HHMM -> +HH:MM
ISO_OFFSET_FIX = re.compile(r'([+-]\d{2})(\d{2})$')

def convert_iso8601_to_utc(str_date: str | bytes | None) -> str | None:
    """
    Convert an ISO 8601 formatted date string to a canonical UTC string
    consistent with convert_unix_ts_to_utc.
    - Input is expected to be a string or bytes.
    - Decodes byte input strictly as UTF-8.
    - Invalid UTF-8 byte input is logged and returns None.
    - Normalizes trailing 'Z' and compact offsets (+HHMM -> +HH:MM).
    - Returns the canonical UTC string on success.
    - On failure, returns the trimmed original string and logs the parse failure.
    Version 1.1

    Args:
        str_date: ISO 8601 formatted string or bytes, or None.

    Returns:
        str | None: Canonical UTC string, trimmed original string if parsing fails,
                    or None if input is None or cannot be decoded.
    """

    # Explicitly preserve None input
    if str_date is None:
        return None

    # Decode byte input strictly so encoding damage is never silent
    if isinstance(str_date, bytes):
        try:
            str_date = str_date.decode('utf-8')
        except UnicodeDecodeError as ex:
            logfunc(
                "Warning - convert_iso8601_to_utc: invalid UTF-8 input; "
                f"timestamp cannot be decoded losslessly: {ex}"
            )
            return None

    # Ensure the input is a string
    if not isinstance(str_date, str):
        str_date = str(str_date)

    # Trim leading/trailing whitespace
    s = str_date.strip()

    # Return early for empty or "null"-like values
    if not s or s.lower() == 'null':
        return s

    # Replace comma with dot in fractional seconds
    s = s.replace(",", ".")

    # Normalize trailing 'Z' (UTC designator) to explicit offset
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'

    # Normalize compact timezone offsets (+HHMM -> +HH:MM)
    s = ISO_OFFSET_FIX.sub(r"\1:\2", s)

    try:
        # Parse ISO 8601 string
        dt = datetime.fromisoformat(s)

        if dt.tzinfo is None:
            # Treat naive datetimes as UTC
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert aware datetimes to UTC
            dt = dt.astimezone(timezone.utc)

        # Convert to canonical UTC string using helper
        return convert_unix_ts_to_utc(dt.timestamp())

    except (ValueError, TypeError) as e:
        # Log parsing failure and return original trimmed string
        logfunc(f"Error - convert_iso8601_to_utc: parse failed for {s!r}: {e}")
        return s


def get_device_file_path(file_path: str, context) -> str:
    """
    Converts a local report file path back to the original iOS device path.
    """

    if not file_path:
        return ''

    seeker = context.get_seeker()
    base_folder = getattr(seeker, 'data_folder', '')

    norm_file_path = str(file_path).replace('\\', '/')
    norm_base_folder = str(base_folder).replace('\\', '/').rstrip('/')

    base_prefix = norm_base_folder + '/' if norm_base_folder else ''

    if norm_base_folder and (
        norm_file_path == norm_base_folder
        or norm_file_path.startswith(base_prefix)
    ):
        relative_path = norm_file_path[len(norm_base_folder):].lstrip('/')

        # Canonical iOS physical path
        if relative_path.startswith('var/'):
            return '/private/' + relative_path

        # Known iOS filesystem roots
        ios_system_roots = (
            'private/', 'Library/', 'System/',
            'Developer/', 'usr/'
        )

        if relative_path.startswith(ios_system_roots):
            return '/' + relative_path

        # Backup-domain or extraction-relative path
        return relative_path

    # Preserve unresolved external paths as observed
    return norm_file_path


def convert_bool_to_str(value, true_value='Yes', false_value='No', none_value='N/A'):
    """
    Converts a boolean value into a human-readable string.
    """

    if value is True:
        return true_value
    if value is False:
        return false_value
    return none_value


def convert_sqlite_bool_to_str(value, true_value='Yes', false_value='No', none_value='N/A'):
    """
    Converts SQLite 0/1 boolean values into report strings.
    """

    if value is None:
        return none_value
    if value is True or value == 1:
        return true_value
    if value is False or value == 0:
        return false_value
    return f"Unknown ({value})"


_decrypted_cache = {}
_decryption_metadata = {}

def _find_keychain_exact_matches(records, account=None, service=None, access_group=None):
    """
    Returns all Keychain records matching the supplied exact selectors.
    """

    matches = []

    for item in records:
        if not isinstance(item, dict):
            continue

        values = {}
        decode_failed = False

        for field in ('acct', 'svce', 'agrp'):
            value = item.get(field, '')
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    decode_failed = True
                    break
            values[field] = value

        if decode_failed:
            continue

        if account is not None and values['acct'] != account:
            continue
        if service is not None and values['svce'] != service:
            continue
        if access_group is not None and values['agrp'] != access_group:
            continue

        matches.append(item)

    return matches


def _query_keychain_item(context, access_group=None, account=None, service=None,
        expected_length=None, return_raw=False):
    """
    Uses parse_keychain(context) for native Keychain parsing and applies
    exact selector matching.

    When return_raw=True, preserves the original Keychain payload bytes.
    """

    try:
        inet_records, genp_records, keys_records, source_path = parse_keychain(context)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Error invoking parse_keychain: {ex}"
        )
        return None, None

    all_records = genp_records + inet_records + keys_records

    matches = _find_keychain_exact_matches(
        records=all_records,
        account=account,
        service=service,
        access_group=access_group
    )

    if not matches:
        return None, source_path

    if len(matches) > 1:
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Ambiguous Keychain match: {len(matches)} records matched "
            f"Account={account!r}, Service={service!r}, "
            f"AccessGroup={access_group!r}."
        )
        return None, source_path

    matched_item = matches[0]

    raw_secret = (
        matched_item.get('v_Data')
        or matched_item.get('secret')
        or matched_item.get('secretData')
    )

    if raw_secret is None:
        return None, source_path

    # Preserve serialized Keychain payload exactly as extracted.
    if return_raw:
        return raw_secret, source_path

    # Convert scalar secrets into strings for passphrase use.
    if isinstance(raw_secret, bytes):
        try:
            raw_secret = raw_secret.decode('utf-8')
        except UnicodeDecodeError:
            raw_secret = base64.b64encode(raw_secret).decode('utf-8')

    secret_str = str(raw_secret).rstrip('\x00').strip()

    if expected_length and len(secret_str) != expected_length:
        return None, source_path

    return secret_str, source_path


def _decrypt_database(encrypted_path, context, db_config=None):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Decrypts a SQLCipher/GRDB database once per (case, database) pair.

    Uses static passphrases or an exact Keychain lookup and records
    decryption integrity metadata for verified, partial, and failed cases.
    """

    output_params = context.get_output_params()
    output_root = output_params.output_folder_base
    cache_key = (output_root, encrypted_path)

    # Return cached result, including cached failures.
    if cache_key in _decrypted_cache:
        return _decrypted_cache[cache_key]

    _decrypted_cache[cache_key] = None

    if db_config is None:
        db_config = {}

    label = db_config.get('cipher_version', 'SQLCipher4') or 'SQLCipher4'
    static_keys = db_config.get('static_keys')
    keychain_info = db_config.get('keychain')
    cipher_params = db_config.get('cipher_params', DEFAULT_CIPHER_PARAMS)

    keys_to_try = []

    # Prefer configured static keys.
    if static_keys:
        keys_to_try = [key for key in static_keys if key]

    # Fall back to exact Keychain lookup.
    if not keys_to_try:
        if keychain_info and keychain_info.get('account'):
            try:
                candidate_key, resolved_keychain = _query_keychain_item(
                    context=context,
                    account=keychain_info.get('account'),
                    service=keychain_info.get('service'),
                    access_group=keychain_info.get('access_group'),
                    expected_length=keychain_info.get('expected_length')
                )

            except Exception as ex:  # pylint: disable=broad-exception-caught
                _decryption_metadata[cache_key] = {
                    'integrity': 'failed',
                    'reason': 'keychain_lookup_error',
                    'pages': 0,
                    'verified': 0,
                    'failed': 0
                }

                logfunc(
                    f"[{context.get_artifact_name()}] {label}: "
                    f"Error during key search for {encrypted_path}: {ex}"
                )
                return None

            if not candidate_key:
                _decryption_metadata[cache_key] = {
                    'integrity': 'failed',
                    'reason': 'keychain_item_not_found',
                    'pages': 0,
                    'verified': 0,
                    'failed': 0
                }

                if resolved_keychain:
                    logfunc(
                        f"[{context.get_artifact_name()}] {label}: "
                        f"Keychain item not found "
                        f"(Account={keychain_info.get('account')!r}, "
                        f"Service={keychain_info.get('service')!r}, "
                        f"AccessGroup={keychain_info.get('access_group')!r}); "
                        "database remains encrypted."
                    )
                else:
                    logfunc(
                        f"[{context.get_artifact_name()}] {label}: "
                        f"Encrypted DB found at {encrypted_path}, "
                        "but no Keychain source was resolved by context."
                    )

                return None

            keys_to_try = [candidate_key]

        else:
            _decryption_metadata[cache_key] = {
                'integrity': 'failed',
                'reason': 'missing_key_configuration',
                'pages': 0,
                'verified': 0,
                'failed': 0
            }

            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error: No key or Keychain configuration provided "
                f"for {label} DB {encrypted_path}."
            )
            return None

    # Build decrypted output path.
    relative_path = context.get_relative_path(encrypted_path)

    if not relative_path or relative_path == encrypted_path:
        relative_path = os.path.basename(encrypted_path)

    rel_dir = os.path.dirname(relative_path)
    base_name, ext = os.path.splitext(os.path.basename(relative_path))

    output_path = os.path.join(
        output_root,
        'Decrypted Databases',
        rel_dir,
        f"{base_name}_decrypted{ext}"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    decrypted_successfully = False
    last_pages = 0
    last_verified = 0
    last_candidate = None

    # Try every configured key candidate.
    for idx, key_candidate in enumerate(keys_to_try, start=1):
        last_candidate = idx

        try:
            pages, verified = decrypt_sqlcipher_db(
                encrypted_path,
                key_candidate,
                output_path,
                **cipher_params
            )

        except (OSError, ValueError) as ex:
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error during decryption attempt for {encrypted_path} "
                f"(Candidate #{idx}): {ex}"
            )
            continue

        pages = pages or 0
        verified = verified or 0

        last_pages = pages
        last_verified = verified

        # No usable verified pages.
        if not pages or not verified:
            continue

        integrity = 'verified' if verified == pages else 'partial'
        failed_pages = max(pages - verified, 0)

        _decryption_metadata[cache_key] = {
            'integrity': integrity,
            'reason': (
                'hmac_verification_complete'
                if integrity == 'verified'
                else 'hmac_verification_partial'
            ),
            'pages': pages,
            'verified': verified,
            'failed': failed_pages,
            'candidate': idx
        }

        if integrity == 'partial':
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"{label} {encrypted_path}: "
                f"{failed_pages} out of {pages} pages failed "
                f"HMAC verification with key #{idx}. "
                "Data may be incomplete."
            )
        else:
            logfunc(
                f"[{context.get_artifact_name()}] {label}: "
                f"{os.path.basename(encrypted_path)} decrypted successfully "
                f"(Key #{idx})."
            )

        decrypted_successfully = True
        break

    if not decrypted_successfully:
        failed_pages = max(last_pages - last_verified, 0)

        _decryption_metadata[cache_key] = {
            'integrity': 'failed',
            'reason': 'decryption_failed',
            'pages': last_pages,
            'verified': last_verified,
            'failed': failed_pages,
            'candidate': last_candidate
        }

        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Failed to decrypt {label} {encrypted_path}: "
            f"none of the {len(keys_to_try)} candidate keys produced "
            "a usable verified database."
        )

        return None

    _decrypted_cache[cache_key] = output_path
    return output_path


def get_sqlite_db_records_regexpr(file_path, query, attach_query=None, regexpr=None):
    """
    Opens an SQLite database, optionally registers a REGEXP function,
    executes the query, and returns all result rows.
    """

    file_path = str(file_path)
    db = open_sqlite_db_readonly(file_path)
    if not bool(db):
        return None

    try:
        # SQLite REGEXP callback.
        if regexpr:
            def sqlite_regexp(pattern, value):
                if pattern is None or value is None:
                    return 0

                try:
                    return 1 if re.search(str(pattern), str(value)) else 0

                except (re.error, TypeError, ValueError):
                    return 0

            db.create_function('regexp', 2, sqlite_regexp)

        cursor = db.cursor()
        if bool(attach_query):
            cursor.execute(attach_query)
        cursor.execute(query)
        records = cursor.fetchall()
        return records

    except sqlite3.Error as ex:
        logfunc(
            f"Error - get_sqlite_db_records_regexpr: "
            f"SQLite query failed for {file_path}: {ex}"
        )
        return None

    finally:
        # Ensure the database connection is always closed to prevent resource leaks
        db.close()


def get_cache_db_records(context, regex_pattern):
    """
    Returns Cache.db records matching the supplied URL regex.
    """

    source_path = context.get_source_file_path('Cache.db')
    if not source_path:
        return None, None

    query = LIDL_CACHE_DB_QUERY.format(regex_pattern=regex_pattern)
    records = get_sqlite_db_records_regexpr(source_path, query, regexpr=True)

    return source_path, records


def get_cache_db_fs_path(data, cache_id, context):
    """
    Resolves the physical path of a cached filesystem object.
    Returns the file path if found, otherwise None.
    """

    if data is None:
        return None

    if isinstance(data, bytes):
        try:
            clean_data = data.decode('utf-8')
        except UnicodeDecodeError as ex:
            logfunc(
                "Warning - get_cache_db_fs_path: "
                f"invalid UTF-8 filesystem reference: {ex}"
            )
            return None

    elif isinstance(data, str):
        clean_data = data

    else:
        logfunc(
            "Warning - get_cache_db_fs_path: unsupported filesystem "
            f"reference type: {type(data).__name__}"
        )
        return None

    clean_data = clean_data.strip()

    if not clean_data:
        return None

    search_result = context.get_seeker().search(
        f"*/Library/Caches/{cache_id}/fsCachedData/{clean_data}",
        return_on_first_hit=True
    )

    return search_result


def get_json_file_content(file_path):
    """
    Read and parse JSON content from a file.

    Returns the decoded JSON value on success, including empty containers,
    or None if the file cannot be read or parsed.
    """

    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()

    except FileNotFoundError:
        logfunc(
            f"Error - get_json_file_content: file not found: {file_path}"
        )
        return None

    except PermissionError:
        logfunc(
            f"Error - get_json_file_content: permission denied: {file_path}"
        )
        return None

    except OSError as ex:
        logfunc(
            f"Error - get_json_file_content: failed reading "
            f"{file_path}: {ex}"
        )
        return None

    try:
        data = raw_data.decode('utf-8')
    except UnicodeDecodeError:
        data = raw_data.decode('utf-8', errors='replace')

    try:
        return json.loads(data)

    except JSONDecodeError as ex:
        logfunc(
            f"Error - get_json_file_content: invalid JSON in "
            f"{file_path}: {ex}"
        )
        return None


def get_json_content(data):
    """
    Parse JSON content from a string or bytes.

    Returns the decoded JSON value on success, including empty containers,
    or None if the input cannot be parsed.
    """

    if data is None:
        return None

    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            data = data.decode('utf-8', errors='replace')

    if not isinstance(data, str):
        logfunc(
            "Error - get_json_content: unsupported input type "
            f"{type(data).__name__}"
        )
        return None

    if not data.strip():
        return None

    try:
        return json.loads(data)

    except JSONDecodeError as ex:
        logfunc(
            f"Error - get_json_content: invalid JSON data: {ex}"
        )
        return None


def _build_kingfisher_photo_map(context):
    """
    Builds and incrementally updates an index of cached image files
    found in the Kingfisher cache directory based on MD5 or SHA-256 filenames.
    Safe to call multiple times: new entries are merged into the existing cache.

    Index structure:
      { "hash_string" : "/full/path/to/file" }

    Also tracks, once per session, whether any 32-char (MD5) and/or
    64-char (SHA-256) keys are present, so that _check_kingfisher_cache()
    can skip computing an algorithm that could never match anything in
    the current map (both formats can coexist on a real device after an
    app/library update, until the old orphaned cache files are purged).
    """

    seeker = context.get_seeker()
    session_key = getattr(seeker, 'data_folder', None) or id(seeker)

    # Reset the cache when the case changes, so photo paths from a previous
    # analysis run do not contaminate the current one.
    if (not hasattr(_build_kingfisher_photo_map, 'session_key')
            or _build_kingfisher_photo_map.session_key != session_key):
        _build_kingfisher_photo_map.data = {}
        _build_kingfisher_photo_map.has_md5 = False
        _build_kingfisher_photo_map.has_sha256 = False
        _build_kingfisher_photo_map.session_key = session_key

    cache = _build_kingfisher_photo_map.data

    # Match exactly 32 (MD5) or exactly 64 (SHA-256) hexadecimal characters
    hash_pattern = re.compile(r'^(?:[a-f0-9]{32}|[a-f0-9]{64})$', re.IGNORECASE)

    # Kingfisher cache filenames may be MD5 or SHA-256 URL hashes
    lookup_map = context.get_filename_lookup_map()

    for filename, paths in lookup_map.items():
        if not isinstance(filename, str):
            continue

        filename = filename.strip().lower()

        # Filter out unrelated configuration files or iOS system clutter
        if not hash_pattern.match(filename):
            continue

        if not paths:
            continue

        full_path = paths[0]

        # Directly map the hash string to its physical location on disk
        cache[filename] = full_path

        if len(filename) == 32:
            _build_kingfisher_photo_map.has_md5 = True
        else:
            _build_kingfisher_photo_map.has_sha256 = True

    return cache


def _format_kingfisher_match_type(match_type):
    """
    Returns a human-readable Kingfisher correlation type.
    """

    return {
        'direct': 'Direct',
        'fallback_list': 'Fallback List',
        'fallback_clean': 'Fallback Clean'
    }.get(match_type, 'N/A')


def _check_kingfisher_cache(images, image_map):
    # pylint: disable=too-many-branches
    """
    Parses the images array, sorts candidates by resolution, and checks the Kingfisher cache.
    If the highest resolution misses, it sequentially checks lower resolutions found in the list,
    and finally falls back to a clean URL string.

    Real devices can contain a mix of MD5 (32-char) and SHA-256 (64-char) cache
    filenames at the same time (e.g. right after an app/library update, before
    the old orphaned files are purged). For each candidate URL, every hash
    algorithm actually observed while building image_map is tried in turn -
    never a single algorithm guessed from one arbitrary sampled key.

    Returns:
        dict or None: Dict containing metadata if matched, otherwise None.
    """

    # Guard clause: combine early checks to save return statements and branches
    if not image_map or not isinstance(images, list):
        return None

    # Only try the algorithms whose output length has actually been observed
    # in image_map for this session (set once in _build_kingfisher_photo_map).
    hash_factories = []
    if getattr(_build_kingfisher_photo_map, 'has_md5', False):
        hash_factories.append(md5)
    if getattr(_build_kingfisher_photo_map, 'has_sha256', False):
        hash_factories.append(sha256)
    if not hash_factories:
        # Fallback for safety, should not normally happen if image_map is non-empty
        hash_factories = [sha256, md5]

    # Extract valid candidates flattening nested conditions to reduce complexity
    candidates = []
    for img in images:
        if not isinstance(img, dict):
            continue

        url = img.get('url')
        if not isinstance(url, str) or not url:
            continue

        res_match = re.search(r'Resize=\(?(\d+)\)?', url, re.IGNORECASE)
        resolution = int(res_match.group(1)) if res_match else 0

        candidates.append({'url': url, 'res': resolution})

    if not candidates:
        return None

    # Sort candidates in descending order (highest resolution first)
    candidates.sort(key=lambda x: x['res'], reverse=True)

    # Combined loop: Handles both 'direct' (index 0) and 'fallback_list' (subsequent indexes)
    for idx, candidate in enumerate(candidates):
        for hash_factory in hash_factories:
            url_hash = hash_factory(candidate['url'].encode('utf-8')).hexdigest()
            if url_hash in image_map:
                return {
                    'path': image_map[url_hash],
                    'source_url': candidate['url'],
                    'matched_url': candidate['url'],
                    'match_type': 'direct' if idx == 0 else 'fallback_list',
                    'resolution': candidate['res']
                }

    # Hard Fallback - Inlined best_url reference to minimize local variable footprint
    clean_url = candidates[0]['url'].split('?')[0]
    if clean_url != candidates[0]['url']:
        for hash_factory in hash_factories:
            clean_hash = hash_factory(clean_url.encode('utf-8')).hexdigest()
            if clean_hash in image_map:
                return {
                    'path': image_map[clean_hash],
                    'source_url': candidates[0]['url'],
                    'matched_url': clean_url,
                    'match_type': 'fallback_clean',
                    'resolution': 0
                }

    return None


def _build_cache_location_parts(entry_id, *extra_locations):
    """
    Builds the individual forensic provenance components for a Cache.db record.

    Args:
        entry_id (int):
            Cache.db entry identifier.

        *extra_locations (str):
            Optional additional evidence locations within the cached payload.

    Returns:
        list[str]:
            Ordered provenance components for the Cache.db record.
    """

    locations = [
        f'cfurl_cache_response (entry_ID: {entry_id})',
        f'cfurl_cache_receiver_data (entry_ID: {entry_id})'
    ]

    locations.extend(
        location for location in extra_locations if location
    )

    return locations


def _parse_html_attributes(attr_text):
    """
    Parses HTML tag attributes without depending on their order.
    """

    if not attr_text:
        return {}

    return {
        key: value
        for key, value in RE_RECEIPT_ATTR_PATTERN.findall(attr_text)
    }


@artifact_processor
def lidl_shopping_list(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts shopping lists and item details from the Lidl Plus shopping-list database.
    """

    data_headers = (
        ('Item Last Updated', 'datetime'),
        'Item Type',
        'Product ID',
        'Product Name',
        'Brand',
        'Packaging',
        'Quantity',
        'Price',
        'Discount Message',
        'Currency',
        'Is Purchased',
        ('Product Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Image URL',
        'Image Cache Match',
        'Product Source',
        'Item Position',
        'Offer ID',
        'Coupon ID',
        'Pending Action',
        'Item UUID',
        'List Type',
        'List Name',
        ('List Last Updated', 'datetime'),
        'List UUID',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Search for the ShoppingList database
    source_path = context.get_source_file_path('ShoppingListDatabase.db')
    if not source_path:
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(source_path)
    if not db:
        return data_headers, data_list, source_path

    # Build the Kingfisher photo map to resolve local cached images
    image_map = _build_kingfisher_photo_map(context)

    try:
        cursor = db.cursor()

        # priceDiscount
        if does_column_exist_in_db(source_path, 'ListItemEntity', 'priceDiscount'):
            has_price_discount = "I.priceDiscount"
        else:
            has_price_discount = "NULL"

        # offerId
        if does_column_exist_in_db(source_path, 'ListItemEntity', 'offerId'):
            has_offer_id = "I.offerId"
        else:
            has_offer_id = "NULL"

        # list type
        if does_column_exist_in_db(source_path, 'ListEntity', 'type'):
            has_list_type = "L.type"
        else:
            has_list_type = "NULL"

        query = f'''
        SELECT
            L.ROWID AS "L_id",
            I.ROWID AS "I_id",
            unixepoch(I.lastUpdate, 'subsec') AS "item_last_update",
            I.type AS "item_type",
            I.title AS "product_name",
            coalesce(I.imageOriginal, I.imageBig, I.imageMedium, I.imageThumbnail) AS "image_url",
            I.brand,
            I.quantity,
            CASE
                WHEN I.isChecked IS NULL THEN 'N/A'
                WHEN CAST(I.isChecked AS TEXT) = '' THEN 'N/D'
                WHEN I.isChecked = 1 THEN 'Yes'
                WHEN I.isChecked = 0 THEN 'No'
                ELSE 'Unknown (' || CAST(I.isChecked AS TEXT) || ')'
            END AS "purchased",
            I.price,
            {has_price_discount},
            I.currency,
            I.packaging,
            I.productId,
            I.productSource,
            I.position,
            {has_offer_id},
            I.couponId,
            I.pendingAction,
            I.id AS "item_uuid",
            {has_list_type} AS "list_type",
            L.name,
            unixepoch(L.lastUpdate, 'subsec') AS "list_last_update",
            L.id AS "list_uuid",
            (
                SELECT json_group_array(json_object('url', url))
                FROM (
                    SELECT I.imageOriginal AS url
                    UNION ALL SELECT I.imageBig
                    UNION ALL SELECT I.imageMedium
                    UNION ALL SELECT I.imageThumbnail
                )
                WHERE url IS NOT NULL
            ) AS "image_url_json"
        FROM ListEntity AS "L"
        LEFT JOIN ListItemEntity AS "I" ON (L.id = I.listId)
        ORDER BY item_last_update DESC
        '''

        cursor.execute(query)
        for record in cursor:
            device_file_paths = [ get_device_file_path(source_path, context) ]

            try:
                # Unpack record for clarity
                (l_rowid, i_rowid, raw_i_updated, i_type, prod_name, img_url,
                 brand, quantity, purchased, price, price_discount, currency,
                 packing, prod_id, prod_source, sort_pos, offer_id, coupon_id,
                 pend_action, i_uuid, l_type, l_name, raw_l_updated,
                 l_uuid, json_images_str) = record

                # Convert timestamps to UTC
                i_updated = convert_unix_ts_to_utc(raw_i_updated)
                l_updated = convert_unix_ts_to_utc(raw_l_updated)

                # Check the Kingfisher cache directory using the optimized helper
                # Parse the native JSON array string generated by the SQLite query
                wrapped_image_list = []
                physical_path = None
                image_cache_match = 'N/A'
                if json_images_str:
                    try:
                        wrapped_image_list = json.loads(json_images_str)
                    except json.JSONDecodeError:
                        wrapped_image_list = []

                    cache_hit = _check_kingfisher_cache(wrapped_image_list, image_map)
                    if cache_hit:
                        img_url = cache_hit.get('source_url')
                        physical_path = cache_hit.get('path')
                        image_cache_match = _format_kingfisher_match_type(
                            cache_hit.get('match_type')
                        )

                        if physical_path:
                            device_file_paths.append(
                                get_device_file_path(physical_path, context)
                            )

                media_ref_id = (
                    check_in_media(physical_path)
                    if physical_path
                    else None
                )

                # Standardize and join all collected device evidence file paths
                device_path = COMMA_SEP.join(device_file_paths)

                # Precise location within the source database table for validation
                location_parts = [ f"ListEntity (ROWID: {l_rowid})" ]
                if i_rowid is not None:
                    location_parts.append(f"ListItemEntity (ROWID: {i_rowid})")
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    i_updated, i_type, prod_id, prod_name, brand,
                    packing, quantity, price, price_discount,
                    currency, purchased, media_ref_id,
                    img_url,                                            # 12 Image URL
                    image_cache_match,
                    prod_source, sort_pos, offer_id, coupon_id,
                    pend_action, i_uuid, l_type, l_name, l_updated,
                    l_uuid,
                    device_path,                                        # 24 SOURCE_FILE_NAME
                    location                                            # 25 Location
                )

                data_list.append(base_data)

            except (AttributeError, ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record ListEntity {_id} in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, data_list, SOURCE_PATH_NOTE


def _get_cache_record(record, context, cache_id):
    """
    Retrieves and parses the JSON payload associated with a Cache.db record.

    Args:
        record (tuple):
            Record returned by LIDL_CACHE_DB_QUERY:
                (
                    entry_ID,
                    cache_time,
                    request_key,
                    isDataOnFS,
                    receiver_data
                )

        context:
            iLEAPP artifact context.

        cache_id (str):
            Application cache identifier (e.g. LIDL_BUNDLE_ID).

    Returns:
        tuple:
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            )

            entry_id          Cache.db entry identifier.
            cache_time        UTC datetime object.
            request_url       Original request URL.
            json_data         Parsed JSON value or None.
            device_file_paths List of evidence file paths.
    """

    # Cache.db is always the primary evidence source.
    source_path = context.get_source_file_path('Cache.db')

    device_file_paths = [
        get_device_file_path(source_path, context)
    ]

    try:
        # Extract Cache.db record fields.
        entry_id = record[0]
        cache_time = convert_unix_ts_to_utc(record[1])
        request_url = record[2]
        is_data_on_fs = bool(record[3])
        receiver_data = record[4]

        # Cached response stored as a separate filesystem object.
        if is_data_on_fs:

            fs_cached_data_path = get_cache_db_fs_path(receiver_data, cache_id, context)

            if not fs_cached_data_path:
                logfunc(
                    f"[{context.get_artifact_name()}] "
                    f"Cache.db entry {entry_id} references filesystem data "
                    f"but the cached object could not be resolved: "
                    f"{receiver_data!r}"
                )
                return (entry_id, cache_time, request_url, None, device_file_paths)

            json_data = get_json_file_content(fs_cached_data_path)

            # Track the filesystem evidence path.
            device_file_paths.append(
                get_device_file_path(fs_cached_data_path, context)
            )

        # Cached response stored directly inside Cache.db.
        else:
            json_data = get_json_content(receiver_data)

        if json_data is None:
            return (entry_id, cache_time, request_url, None, device_file_paths)

        return (entry_id, cache_time, request_url, json_data, device_file_paths)

    except (AttributeError, IndexError, TypeError, ValueError) as ex:
        _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Error - parsing Cache.db record {_id}: "
            f"{type(ex).__name__}: {ex}"
        )
        return (None, None, None, None, device_file_paths)


@artifact_processor
def lidl_tickets(context):
    # pylint: disable=too-many-branches, too-many-locals
    """
    Extracts cached Lidl Plus ticket and transaction metadata.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Cache Time', 'datetime'),
        'Store Code',
        'Total Amount',
        'Currency',
        'Articles Count',
        'Coupons Used',
        'Returns Count',
        'Is Favorite',
        'Has Invoice',
        'Has HTML',
        'Ticket ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Search for the Cache database
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_TICKET_LIST)
    if not records:
        return data_headers, data_list, source_path

    for record in records:
        try:
            # Retrieve JSON content
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data:
                continue

            # Device Path
            device_path = COMMA_SEP.join(device_file_paths)

            # Process tickets list if present
            if isinstance(json_data, dict):
                tickets = json_data.get('tickets', [])
                tickets_location = 'receiver_data.tickets'
            elif isinstance(json_data, list):
                tickets = json_data
                tickets_location = 'receiver_data'
            else:
                continue

            if not isinstance(tickets, list) or not tickets:
                continue

            for t, ticket in enumerate(tickets):
                if not isinstance(ticket, dict):
                    continue

                # Convert ticket timestamp to UTC
                current_date = convert_iso8601_to_utc(ticket.get('date'))
                ticket_id = ticket.get('id')

                # Safely preserve only dictionary-shaped nested objects.
                badges = ticket.get('badges')
                if not isinstance(badges, dict):
                    badges = {}

                currency = ticket.get('currency')
                if not isinstance(currency, dict):
                    currency = {}

                has_html = (
                    ticket.get('hasHtmlDocument')
                    if 'hasHtmlDocument' in ticket
                    else ticket.get('isHtml')
                )

                # Precise location within the source database table for validation
                location_parts = _build_cache_location_parts(
                    entry_id,
                    f"{tickets_location}[{t}]"
                )
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    current_date,
                    cache_time,
                    ticket.get('storeCode'),
                    ticket.get('totalAmount'),
                    currency.get('symbol'),
                    ticket.get('articlesCount'),
                    ticket.get('couponsUsedCount'),
                    badges.get('returns'),
                    convert_bool_to_str(ticket.get('isFavorite')),
                    convert_bool_to_str(badges.get('invoice')),
                    convert_bool_to_str(has_html),
                    ticket_id,
                    request_url,
                    device_path,                                        # 13 SOURCE_FILE_NAME
                    location                                            # 14 Location
                )

                data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
            logfunc(f"[{context.get_artifact_name()}] "
                    f"Error - Failed parsing record {_id} in {source_path}: {ex}")
            continue


    # Sort by Timestamp (index 0) in descending order (newest first)
    # We check if index 0 is valid (not None) to prevent errors
    data_list.sort(key=lambda x: x[0] if x[0] else '', reverse=True)
    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_receipt_items(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts purchased items from cached Lidl Plus receipt details.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Cache Time', 'datetime'),
        'Product Name',
        'Quantity',
        'Price',
        'Tax Type',
        'Promotion Description',
        'Promotion Discount',
        'Line Item',
        'Store Code',
        'Store Name',
        'Store Address',
        'Store Postal Code',
        'Store City',
        'Total Amount',
        'Coupons Count',
        'Is Favorite',
        'Has Invoice',
        'Barcode',
        'Is Deleted',
        'Ticket ID',
        'Product ID',
        'Promotion ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []
    data_list_html = []

    # Search for the Cache database.
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_TICKET_DETAIL)

    if not records:
        return data_headers, (data_list, data_list_html), source_path

    for record in records:
        try:
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data or not isinstance(json_data, dict):
                continue

            device_path = COMMA_SEP.join(device_file_paths)

            ticket_id = json_data.get('id')
            ticket_date = convert_iso8601_to_utc(json_data.get('date'))

            store_info = json_data.get('store')
            if not isinstance(store_info, dict):
                store_info = {}

            # Safely parse the coupons-used collection
            coupons_used = json_data.get('couponsUsed')
            if not isinstance(coupons_used, list):
                coupons_used = []
            coupons_count = len(coupons_used)

            # Only parse string-shaped HTML receipt content
            html_receipt = json_data.get('htmlPrintedReceipt')
            if not isinstance(html_receipt, str) or not html_receipt:
                continue

            # Parse article and discount spans without depending
            # on the original HTML attribute order.
            article_matches = []
            discounts = []

            for span_match in RE_RECEIPT_SPAN_PATTERN.finditer(html_receipt):
                attrs = _parse_html_attributes(span_match.group('attrs'))
                classes = str(attrs.get('class', '')).split()

                span_data = {
                    'start': span_match.start(),
                    'end': span_match.end(),
                    'attrs': attrs,
                    'content': span_match.group('content')
                }

                if 'article' in classes:
                    article_matches.append(span_data)

                elif 'discount' in classes:
                    discounts.append(span_data)


            # Precise location within the cached receipt
            location_parts = _build_cache_location_parts(
                entry_id,
                'receiver_data.htmlPrintedReceipt'
            )
            location = COMMA_SEP.join(location_parts)

            discount_index = 0

            for index, article in enumerate(article_matches):
                attrs = article['attrs']

                promotion_id = None
                promotion_description = None
                promotion_discount = None

                if discount_index < len(discounts):
                    discount = discounts[discount_index]

                    next_article_pos = (
                        article_matches[index + 1]['start']
                        if index + 1 < len(article_matches)
                        else len(html_receipt)
                    )

                    # Associate only discounts physically located
                    # after this article and before the next one.
                    if article['end'] < discount['start'] < next_article_pos:
                        discount_attrs = discount['attrs']
                        promotion_id = discount_attrs.get('data-promotion-id')
                        discount_content = discount['content'].strip()
                        discount_match = (
                            RE_RECEIPT_DISCOUNT_CONTENT_PATTERN.search(discount_content)
                        )

                        if discount_match:
                            promotion_description = discount_match.group('description').strip()
                            promotion_discount = discount_match.group('discount')

                        else:
                            # Preserve the raw discount content
                            # if its internal layout is unknown.
                            promotion_description = discount_content

                        discount_index += 1

                # Base row
                base_data = (
                    ticket_date,
                    cache_time,
                    attrs.get('data-art-description'),
                    attrs.get('data-art-quantity'),
                    attrs.get('data-unit-price'),
                    attrs.get('data-tax-type'),
                    promotion_description,
                    promotion_discount,
                    article['content'],                                 # 8 Line Item
                    store_info.get('id'),
                    store_info.get('name'),
                    store_info.get('address'),
                    store_info.get('postalCode'),
                    store_info.get('locality'),
                    json_data.get('totalAmount'),
                    coupons_count,
                    convert_bool_to_str(json_data.get('isFavorite')),
                    convert_bool_to_str(json_data.get('hasInvoice')),
                    json_data.get('barCode'),
                    convert_bool_to_str(json_data.get('isDeleted')),
                    ticket_id,
                    attrs.get('data-art-id'),
                    promotion_id,
                    request_url,
                    device_path,                                        # 24 SOURCE_FILE_NAME
                    location                                            # 25 Location
                )

                # LAVA row
                data_list.append(base_data)

                # HTML row
                html_data = list(base_data)
                html_data[8] = esc(article['content'])
                data_list_html.append(tuple(html_data))

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error parsing record: {ex}"
            )
            continue

    data_list.sort(
        key=lambda row: row[0] if row[0] else '',
        reverse=True
    )
    data_list_html.sort(
        key=lambda row: row[0] if row[0] else '',
        reverse=True
    )

    return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE


def _extract_last4(number_field):
    """
    Return the last four digits from a card number string or None.
    """

    if not number_field:
        return None
    s = str(number_field)
    digits = "".join(ch for ch in s if ch.isdigit())

    return digits[-4:] if len(digits) >= 4 else None


def _normalize_status(payment):
    """
    Return a normalized status string from a payment object or None.
    """

    status = payment.get("status")

    if status:
        return status

    if payment.get("isExpired"):
        return "Expired"

    if payment.get("isAboutToExpire"):
        return "AboutToExpire"

    return None


# Payment Containers
PAYMENT_CONTAINERS = (
    ('paymentMethods', None),
    ('cards', 'Card'),
    ('wallets', None),
    ('ibans', 'IBAN'),
    ('tokens', 'Token'),
)


def _build_payment_row(payment, source_key, default_type, cache_time,
                       lidl_pay_active, profile_status, request_url,
                       device_path, location):
    # pylint: disable=too-many-branches, too-many-positional-arguments, too-many-locals, too-many-arguments
    """
    Builds a single output row for one payment-container item.

    Defensive by design: the exact item shape of 'wallets', 'ibans' and
    'tokens' has not been confirmed on real populated data (only empty
    arrays have been observed so far). If an item turns out to be a plain
    string rather than an object (e.g. a bare IBAN string), it is still
    represented as a row - using the string itself as the identifier -
    instead of raising, which would otherwise abort every other container
    in the same cache record via the caller's broad except clause.

    Returns None if the item has no usable identifier.
    """

    if isinstance(payment, dict):
        payment_id = payment.get('id')
        payment_type = payment.get('type', default_type)
        alias = payment.get('alias')
        account_holder = payment.get('accountHolder')
        brand = payment.get('brand')
        last4 = _extract_last4(payment.get('number'))
        bank_name = payment.get('bankName')
        balance = payment.get('balance')
        currency = payment.get('currency')
        status = _normalize_status(payment)
        is_default = convert_bool_to_str(payment.get('isDefault'))

    elif isinstance(payment, str) and payment.strip():
        # Preserve unverified scalar container values without interpreting them.
        payment_id = payment.strip()
        payment_type = default_type
        alias = account_holder = brand = None
        last4 = None
        bank_name = currency = status = None
        balance = None
        is_default = convert_bool_to_str(None)

    else:
        logfunc(f"Warning - lidl_payment_methods: unrecognized '{source_key}' "
                f"item type: {type(payment).__name__}")
        return None

    if not payment_id:
        return None

    return (
        cache_time,
        payment_type,
        alias,
        account_holder,
        brand,
        last4,
        bank_name,
        balance,
        currency,
        status,
        is_default,
        convert_bool_to_str(lidl_pay_active),
        profile_status,
        source_key,
        payment_id,
        request_url,
        device_path,
        location
    )


@artifact_processor
def lidl_payment_methods(context):
    # pylint: disable=too-many-branches, too-many-locals
    """
    Extracts cached payment methods and Lidl Pay profile status.
    """

    data_headers = (
        ('Cache Time', 'datetime'),
        'Type',
        'Alias',
        'Account Holder',
        'Brand',
        'Last 4 Digits',
        'Bank Name',
        'Balance',
        'Currency',
        'Validation Status',
        'Is Default',
        'Lidl Pay Active',
        'Profile Status',
        'Source Container',
        'Payment ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Search for the Cache database
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_PAYMENT_METHODS)
    if not records:
        return data_headers, data_list, source_path

    for record in records:
        try:
            # Retrieve JSON content
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data or not isinstance(json_data, dict):
                continue

            # Device Path
            device_path = COMMA_SEP.join(device_file_paths)

            lidl_pay_active = json_data.get('hasLidlPayActive')
            profile_status = json_data.get('status')

            for source_key, default_type in PAYMENT_CONTAINERS:
                items = json_data.get(source_key)
                if not isinstance(items, list):
                    continue

                for index, payment in enumerate(items):
                    # Precise location of this item within the cached payload.
                    location_parts = _build_cache_location_parts(
                        entry_id,
                        f"receiver_data.{source_key}[{index}]"
                    )
                    location = COMMA_SEP.join(location_parts)

                    # Base row
                    base_data = _build_payment_row(
                        payment,
                        source_key,
                        default_type,
                        cache_time,
                        lidl_pay_active,
                        profile_status,
                        request_url,                                    # 15 Request URL
                        device_path,                                    # 16 SOURCE_FILE_NAME
                        location                                        # 17 Location
                    )
                    if base_data is None:
                        continue

                    data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error parsing record: {ex}")
            continue

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_loyalty_card(context):
    # pylint: disable=too-many-branches, too-many-locals
    """
    Extracts cached payment QR data and the derived Lidl Plus loyalty card number.
    """

    data_headers = (
        ('Cache Time', 'datetime'),
        'Payment QR',
        'Card Number (Derived)',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    source_path, records = get_cache_db_records(context, RE_CACHE_DB_PAYMENT_QR)
    if not records:
        return data_headers, data_list, source_path

    for record in records:
        try:
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data or not isinstance(json_data, dict):
                continue

            device_path = COMMA_SEP.join(device_file_paths)

            payment_qr = json_data.get('paymentQR')

            # Confirmed by observed on-device UI behavior:
            # the displayed loyalty-card number corresponds to the
            # first 17 characters of the paymentQR value.
            card_number = None

            if isinstance(payment_qr, str) and len(payment_qr) >= 17:
                card_number = payment_qr[:17]

            location_parts = _build_cache_location_parts(entry_id)
            location = COMMA_SEP.join(location_parts)

            # Base row
            base_data = (
                cache_time,
                payment_qr,
                card_number,
                request_url,                                    # 3 Request URL
                device_path,                                    # 4 SOURCE_FILE_NAME
                location                                        # 5 Location
            )

            data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error parsing record: {ex}"
            )
            continue

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_promotion_details(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts cached Lidl Plus coupon and promotion details.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Cache Time', 'datetime'),
        'Promotion Type',
        'Product Name',
        'Discount',
        'Brand',
        'Product',
        ('Product Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Image URL',
        'Image Cache Match',
        'Channel',
        ('Valid From', 'datetime'),
        ('Valid To', 'datetime'),
        'Activated',
        'Redeemed',
        'Processing',
        'Special',
        'Segmented',
        'Tag',
        'Promotion ID',
        'Coupon ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Search for the Cache database
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_PROMOTION_DETAILS)
    if not records:
        return data_headers, data_list, source_path

    # Build the Kingfisher image cache map
    image_map = _build_kingfisher_photo_map(context)

    for record in records:
        try:
            # Retrieve JSON content
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            # Only dictionary-shaped payloads are supported here
            if not json_data or not isinstance(json_data, dict):
                continue

            promotion_id = json_data.get('promotionId')
            if not promotion_id:
                continue

            # Promotion type
            prom_type = json_data.get('type')

            # Redemption channel
            channel = json_data.get('channel')

            # Safely parse validity information
            validity = json_data.get('validity')
            if not isinstance(validity, dict):
                validity = {}
            start_date = convert_iso8601_to_utc(validity.get('start'))
            end_date = convert_iso8601_to_utc(validity.get('end'))

            # Safely parse article descriptions
            articles = json_data.get('articles')
            if not isinstance(articles, list):
                articles = []

            art_descriptions = []
            for article in articles:
                if not isinstance(article, dict):
                    continue

                description = article.get('description')
                if description:
                    art_descriptions.append(str(description))

            articles_str = COMMA_SEP.join(art_descriptions) if art_descriptions else ''

            # Preserve the root description and enrich it only with
            # descriptions explicitly present in the articles array
            root_desc = json_data.get('description', '')

            if root_desc and articles_str:
                product_info = f"{root_desc} ({articles_str})"
            elif root_desc:
                product_info = root_desc
            else:
                product_info = articles_str

            # Resolve the image against the Kingfisher cache
            images = json_data.get('images', [])

            image_url = None
            physical_path = None
            image_cache_match = 'N/A'

            cache_hit = _check_kingfisher_cache(images, image_map)
            if cache_hit:
                # Preserve the URL observed in the source JSON
                image_url = cache_hit.get('source_url')
                physical_path = cache_hit.get('path')
                image_cache_match = _format_kingfisher_match_type(cache_hit.get('match_type'))
                if physical_path:
                    device_file_paths.append(get_device_file_path(physical_path, context))

            elif isinstance(images, list) and images:
                first_img = images[0]

                if isinstance(first_img, dict):
                    image_url = first_img.get('url')

            media_ref_id = check_in_media(physical_path) if physical_path else None

            # Device Path
            device_path = COMMA_SEP.join(device_file_paths)

            # Safely parse special-promotion metadata
            special_promo = json_data.get('specialPromotion')

            tag = special_promo.get('tag', '') if isinstance(special_promo, dict) else ''

            # Safely parse discount metadata
            discount_info = json_data.get('discount')
            discount = discount_info.get('title') if isinstance(discount_info, dict) else None

            # Preserve explicit boolean values.
            # Status is used only as a positive fallback when the
            # corresponding boolean field is absent from the payload.
            status = str(json_data.get('status') or '').upper()

            if 'isActivated' in json_data:
                activated = json_data.get('isActivated')
            else:
                activated = True if status == 'ACTIVATED' else None

            if 'isRedeemed' in json_data:
                redeemed = json_data.get('isRedeemed')
            else:
                redeemed = True if status == 'REDEEMED' else None

            is_activated = convert_bool_to_str(activated)
            is_redeemed = convert_bool_to_str(redeemed)

            # Precise location within the source cache record
            location_parts = _build_cache_location_parts(entry_id)
            location = COMMA_SEP.join(location_parts)

            # Base row
            base_data = (
                start_date,
                cache_time,
                prom_type,
                json_data.get('title'),
                discount,
                json_data.get('brand'),
                product_info,
                media_ref_id,
                image_url,                                              # 8 Image URL
                image_cache_match,
                channel,
                start_date,
                end_date,
                is_activated,
                is_redeemed,
                convert_bool_to_str(json_data.get('isProcessing')),
                convert_bool_to_str(json_data.get('isSpecial')),
                convert_bool_to_str(json_data.get('isSegmented')),
                tag,
                promotion_id,
                json_data.get('id'),
                request_url,                                            # 21 Request URL
                device_path,                                            # 22 SOURCE_FILE_NAME
                location                                                # 23 Location
            )

            data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error parsing record: {ex}"
            )
            continue

    # Sort the forensic timeline by Cache Time descending
    data_list.sort(key=lambda row: row[1] if row[1] else '', reverse=True)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_product_details(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts cached Lidl Plus product details.
    """

    data_headers = (
        ('Cache Time', 'datetime'),
        'Product Name',
        'Brand',
        'Characteristics',
        'Packaging',
        'Price',
        'Currency',
        'Price Per Unit',
        ('Product Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Image URL',
        'Image Cache Match',
        'Product ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Search for the Cache database
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_PRODUCT_SHOWCASE)
    if not records:
        return data_headers, data_list, source_path

    # Build the Kingfisher image cache map
    image_map = _build_kingfisher_photo_map(context)

    for record in records:
        try:
            # Retrieve JSON content
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            # Only dictionary-shaped payloads are supported here.
            if not json_data or not isinstance(json_data, dict):
                continue

            # Safely parse the result object.
            result = json_data.get('result')
            if not isinstance(result, dict) or not result:
                continue

            product_id = result.get('id')
            if not product_id:
                continue

            # Safely parse pricing information.
            price_info = result.get('price')
            if not isinstance(price_info, dict):
                price_info = {}

            amount_info = price_info.get('amount')
            if not isinstance(amount_info, dict):
                amount_info = {}

            price_val = amount_info.get('value')
            currency = price_info.get('type')
            price_per_unit = price_info.get('pricePerUnit')

            # Check the Kingfisher cache directory for local forensic file matching
            images = result.get('images', [])
            image_url = None
            physical_path = None
            image_cache_match = 'N/A'

            cache_hit = _check_kingfisher_cache(images, image_map)

            if cache_hit:
                image_url = cache_hit.get('source_url')
                physical_path = cache_hit.get('path')
                image_cache_match = _format_kingfisher_match_type(
                    cache_hit.get('match_type')
                )

                if physical_path:
                    device_file_paths.append(
                        get_device_file_path(physical_path, context)
                    )

            elif isinstance(images, list) and images:
                first_img = images[0]

                if isinstance(first_img, dict):
                    image_url = first_img.get('url')

            media_ref_id = (
                check_in_media(physical_path)
                if physical_path
                else None
            )

            # Device Path
            device_path = COMMA_SEP.join(device_file_paths)

            # Precise location within the source database table for validation
            location_parts = _build_cache_location_parts(
                entry_id,
                'receiver_data.result'
            )
            location = COMMA_SEP.join(location_parts)

            # Base row
            base_data = (
                cache_time,
                result.get('title'),
                result.get('brand'),
                result.get('characteristics'),
                result.get('packaging'),
                price_val,
                currency,
                price_per_unit,
                media_ref_id,
                image_url,                                      # 9 Image URL
                image_cache_match,
                product_id,
                request_url,                                    # 12 Request URL
                device_path,                                    # 13 SOURCE_FILE_NAME
                location                                        # 14 Location
            )

            data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error parsing record: {ex}")
            continue

    # Sort by Cache Time descending
    data_list.sort(key=lambda x: x[0] if x[0] else '', reverse=True)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_searched_terms(context):
    # pylint: disable=too-many-branches, too-many-locals
    """
    Extracts cached Lidl Plus product-search requests and returned results.

    Forensic notes:
    - Preserves every observed Cache.db request.
    - Keeps raw and decoded search terms separate.
    - Sequence metadata is derived from request timing and term progression.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Search Term (Raw)',
        'Search Term (Decoded)',
        'Store ID',
        'Returned Results Count',
        'Returned Products',
        'Sequence ID',
        'Sequence Position',
        'Sequence Final',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []
    data_list_html = []

    source_path, records = get_cache_db_records(
        context,
        RE_CACHE_DB_SEARCHED_TERMS
    )
    if not records:
        return data_headers, (data_list, data_list_html), source_path

    pattern = re.compile(RE_CACHE_DB_SEARCHED_TERMS)
    max_gap_seconds = 6.0
    search_records = []

    # Extract every matching cached request.
    for record in records:
        try:
            raw_timestamp = record[1]
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not request_url:
                continue

            match = pattern.match(request_url)
            if not match:
                continue

            store_id, raw_term = match.groups()
            try:
                decoded_term = unquote_plus(raw_term)
            except (TypeError, ValueError):
                decoded_term = raw_term

            # Preserve the distinction between no results and unavailable response data
            results = None

            if isinstance(json_data, dict):
                raw_results = json_data.get('results')
                if isinstance(raw_results, list):
                    results = raw_results

            products = []
            if results is not None:
                for item in results:
                    if not isinstance(item, dict):
                        continue

                    brand = str(item.get('brand') or '').strip()
                    title = str(item.get('title') or '').strip()
                    product_id = str(item.get('id') or '').strip()

                    name = f"{brand} - {title}" if brand and title else title or brand

                    if product_id:
                        name = f"{name} ({product_id})" if name else f"({product_id})"

                    if name:
                        products.append(name)

            # Device Path
            device_path = COMMA_SEP.join(device_file_paths)

            # Precise location within the source cache record
            location_parts = _build_cache_location_parts(entry_id)
            location = COMMA_SEP.join(location_parts)

            search_records.append({
                'raw_ts': raw_timestamp,
                'timestamp': cache_time,
                'raw_term': raw_term,
                'decoded_term': decoded_term,
                'store_id': store_id,
                'results_count': len(results) if results is not None else None,
                'products': LIST_SEP.join(products),
                'product_parts': products,
                'url': request_url,
                'source': device_path,
                'location': location,
                'sequence_id': None,
                'sequence_position': None,
                'sequence_final': False
            })

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            record_id = record[0] if record else 'UNKNOWN'
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error - Failed parsing search Cache.db record "
                f"{record_id} in {source_path}: {ex}"
            )

    if not search_records:
        return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE

    # Chronological order for derived sequence grouping.
    search_records.sort(
        key=lambda item: (
            item['raw_ts'] is None,
            item['raw_ts'] or 0
        )
    )

    def commit_sequence(items, sequence_number):
        """Assign derived sequence metadata."""

        label = f"SEQ-{sequence_number:04d}"
        last_position = len(items)

        for position, item in enumerate(items, start=1):
            item['sequence_id'] = label
            item['sequence_position'] = position
            item['sequence_final'] = position == last_position

    sequence_number = 0
    current_sequence = []

    for current in search_records:
        if not current_sequence:
            sequence_number += 1
            current_sequence = [current]
            continue

        previous = current_sequence[-1]

        previous_ts = previous['raw_ts']
        current_ts = current['raw_ts']

        same_sequence = False

        if previous_ts is not None and current_ts is not None:
            previous_query = previous['decoded_term'].lower()
            current_query = current['decoded_term'].lower()

            time_delta = current_ts - previous_ts

            is_extension = (
                previous_query
                and current_query.startswith(previous_query)
            )

            is_backspace = (
                current_query
                and previous_query.startswith(current_query)
                and len(previous_query) - len(current_query) <= 2
            )

            same_sequence = (
                0 <= time_delta <= max_gap_seconds
                and previous['store_id'] == current['store_id']
                and (is_extension or is_backspace)
            )

        if same_sequence:
            current_sequence.append(current)
            continue

        commit_sequence(current_sequence, sequence_number)

        sequence_number += 1
        current_sequence = [current]

    commit_sequence(current_sequence, sequence_number)

    # One cached request remains one report row.
    for item in search_records:
        base_data = (
            item['timestamp'],
            item['raw_term'],
            item['decoded_term'],
            item['store_id'],
            item['results_count'],
            item['products'],                                   # 5 Products
            item['sequence_id'],
            item['sequence_position'],
            convert_bool_to_str(item['sequence_final']),
            item['url'],                                        # 9 Request URL
            item['source'],                                     # 10 SOURCE_FILE_NAME
            item['location']                                    # 11 Location
        )

        # LAVA row
        data_list.append(base_data)

        # HTML row
        html_data = list(base_data)
        html_data[5] = safe_join(item['product_parts'])
        data_list_html.append(tuple(html_data))

    data_list.sort(key=lambda row: row[0] or '', reverse=True)
    data_list_html.sort(key=lambda row: row[0] or '', reverse=True)

    return data_headers, (data_list, data_list_html), SOURCE_PATH_NOTE


@artifact_processor
def lidl_store_searches(context):
    # pylint: disable=too-many-branches, too-many-locals
    """
    Extracts cached Lidl Plus store-search requests, request coordinates,
    and returned store details.

    Forensic notes:
    - Preserves every observed matching Cache.db request.
    - Keeps raw and decoded search terms separate.
    - Request coordinates are reported as transmitted and are not interpreted
      as the user's physical location.
    - A missing response body is distinct from an available empty response.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Search Term (Raw)',
        'Search Term (Decoded)',
        'Language',
        'Latitude',
        'Longitude',
        'Returned Store Count',
        'Result Position',
        'Store ID',
        'Store Name',
        'Store Address',
        'Store Postal Code',
        'Store Locality',
        'Store Latitude',
        'Store Longitude',
        'Distance (m)',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    source_path, records = get_cache_db_records(context, RE_CACHE_DB_STORE_SEARCHES)
    if not records:
        return data_headers, data_list, source_path

    def get_raw_query_value(query_string, parameter):
        """Return the raw query-string value without URL decoding."""

        match = re.search(
            rf'(?:^|&){re.escape(parameter)}=([^&]*)',
            query_string
        )
        return match.group(1) if match else None

    def decode_query_value(value):
        """Decode one query-string value while preserving missing values."""

        if value is None:
            return None

        try:
            return unquote_plus(value)
        except (TypeError, ValueError):
            return value

    for record in records:
        try:
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not request_url:
                continue

            parsed_url = urlparse(request_url)
            query_string = parsed_url.query

            raw_term = get_raw_query_value(query_string, 'input')
            decoded_term = decode_query_value(raw_term)
            language = decode_query_value(get_raw_query_value(query_string, 'language'))
            request_lat = decode_query_value(get_raw_query_value(query_string, 'latitude'))
            request_lon = decode_query_value(get_raw_query_value(query_string, 'longitude'))

            device_path = COMMA_SEP.join(device_file_paths)

            # Root payload is an observed JSON list of returned stores.
            # None means the response body was unavailable or not list-shaped.
            stores = json_data if isinstance(json_data, list) else None
            returned_count = len(stores) if stores is not None else None

            emitted_store = False

            if stores:
                for position, store in enumerate(stores, start=1):
                    if not isinstance(store, dict):
                        continue

                    store_location = store.get('location')
                    if not isinstance(store_location, dict):
                        store_location = {}

                    location_parts = _build_cache_location_parts(
                        entry_id,
                        f'receiver_data[{position - 1}]'
                    )
                    location = COMMA_SEP.join(location_parts)

                    # Base row
                    base_data = (
                        cache_time,
                        raw_term,
                        decoded_term,
                        language,
                        request_lat,
                        request_lon,
                        returned_count,
                        position,
                        store.get('storeKey'),
                        store.get('name'),
                        store.get('address'),
                        store.get('postalCode'),
                        store.get('locality'),
                        store_location.get('latitude'),
                        store_location.get('longitude'),
                        store.get('distance'),
                        request_url,                                    # 16 Request URL
                        device_path,                                    # 17 SOURCE_FILE_NAME
                        location                                        # 18 Location
                    )

                    data_list.append(base_data)

                    emitted_store = True

            # Preserve the request even when the response body is unavailable,
            # empty, or contains no dictionary-shaped store records.
            if not emitted_store:
                location_parts = _build_cache_location_parts(entry_id)
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    cache_time,
                    raw_term,
                    decoded_term,
                    language,
                    request_lat,
                    request_lon,
                    returned_count,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    request_url,                                    # 16 Request URL
                    device_path,                                    # 17 SOURCE_FILE_NAME
                    location                                        # 18 Location
                )

                data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            record_id = record[0] if record else 'UNKNOWN'
            logfunc(
                f"[{context.get_artifact_name()}] "
                f"Error - Failed parsing store-search Cache.db record "
                f"{record_id} in {source_path}: {ex}"
            )

    data_list.sort(key=lambda row: (row[0] or '', -(row[7] or 0)), reverse=True)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_offers(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts cached Lidl Plus promotional offer data.
    """

    data_headers = (
        ('Cache Time', 'datetime'),
        'Offer Type',
        'Product Name',
        'Brand',
        'Packaging',
        'Original Price',
        'Discounted Price',
        'Discount Message',
        'Currency',
        'Price Per Unit',
        'Channel',
        ('Product Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Image URL',
        'Image Cache Match',
        ('Valid From', 'datetime'),
        ('Valid To', 'datetime'),
        'Offer ID',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Query the Cache.db database for matching URL endpoints
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_OFFERS)
    if not records:
        return data_headers, data_list, source_path

    # Map all image assets available in the Kingfisher image cache directory
    image_map = _build_kingfisher_photo_map(context)

    for record in records:
        try:
            # Retrieve JSON payload content from the database row or local filesystem cache
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data or not isinstance(json_data, dict):
                continue

            # Offers list response
            offers_list = json_data.get('offers')

            if isinstance(offers_list, list) and offers_list:
                offers_source = offers_list
                offers_location = 'receiver_data.offers'
            # Offer detail response
            elif json_data.get('id'):
                offers_source = [json_data]
                offers_location = 'receiver_data'
            else:
                continue

            for o, offer in enumerate(offers_source):
                if not isinstance(offer, dict):
                    continue

                offer_id = offer.get('id')
                if not offer_id:
                    continue

                # Safely parse the nested price-box object.
                price_box = offer.get('priceBox')
                if not isinstance(price_box, dict):
                    price_box = {}

                # Standardize validity timestamps into regular UTC format
                start_date = convert_iso8601_to_utc(offer.get('startValidityDate'))
                end_date = convert_iso8601_to_utc(offer.get('endValidityDate'))

                # Resolve image tracking using Kingfisher cache mapping logic
                images = offer.get('images')
                if isinstance(images, list) and images:
                    image_candidates = images
                else:
                    legacy_image_url = offer.get('imageUrl')
                    image_candidates = [{'url': legacy_image_url}] if legacy_image_url else []

                image_url = None
                physical_path = None
                image_cache_match = 'N/A'

                local_device_paths = list(device_file_paths)

                cache_hit = _check_kingfisher_cache(image_candidates, image_map)
                if cache_hit:
                    image_url = cache_hit.get('source_url')
                    physical_path = cache_hit.get('path')
                    image_cache_match = _format_kingfisher_match_type(
                        cache_hit.get('match_type')
                    )
                    if physical_path:
                        local_device_paths.append(
                            get_device_file_path(physical_path, context)
                        )
                elif image_candidates:
                    first_img = image_candidates[0]
                    if isinstance(first_img, dict):
                        image_url = first_img.get('url')

                media_ref_id = (
                    check_in_media(physical_path)
                    if physical_path
                    else None
                )

                # Standardize and merge all collected device file system references
                device_path = COMMA_SEP.join(local_device_paths)

                # Reconstruct precise location indexing within the original cached array
                if offers_location == 'receiver_data':
                    location_parts = _build_cache_location_parts(
                        entry_id,
                        'receiver_data'
                    )
                else:
                    location_parts = _build_cache_location_parts(
                        entry_id,
                        f"{offers_location}[{o}]"
                    )
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    cache_time,
                    offer.get('offerType'),
                    offer.get('title'),
                    offer.get('brand'),
                    offer.get('packaging'),
                    price_box.get('smallPartNumeric'),
                    price_box.get('largePartNumeric'),
                    price_box.get('discountMessage'),
                    price_box.get('priceSymbol'),
                    offer.get('pricePerUnit'),
                    offer.get('redemptionChannel'),
                    media_ref_id,
                    image_url,                                      # 12 Image URL
                    image_cache_match,
                    start_date,
                    end_date,
                    offer_id,
                    request_url,                                    # 17 Request URL
                    device_path,                                    # 18 SOURCE_FILE_NAME
                    location                                        # 19 Location
                )

                data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error parsing record: {ex}")
            continue

    # Sort final timeline by Cache Time descending (newest updates first)
    data_list.sort(key=lambda x: x[0] if x[0] else '', reverse=True)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_mypoints(context):
    # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    """
    Extracts cached Lidl Plus loyalty-points marketplace rewards and account points metadata.
    """

    data_headers = (
        ('Cache Time', 'datetime'),
        'Type',
        'Sub Type',
        'Reward Name',
        'Points Cost',
        'Price',
        'Discount Value',
        'Discount Title',
        'State',
        'Is Disabled',
        'Is Blocked',
        'Is Favorite',
        'Already Exchanged',
        'Exchange Button Enabled',
        'Days Until Expiration',
        'Available Promotions',
        'Related Online Article Number',
        ('Reward Image', 'media', 'height: 48px; border-radius: 5%;'),
        'Image URL',
        'Image Cache Match',
        ('Available On', 'datetime'),
        'Reward ID',
        'Account Available Points',
        'Points To Expire',
        ('Next Expiration Date', 'datetime'),
        'Total Rewards In Catalog',
        'Request URL',
        SOURCE_FILE_NAME,
        'Location'
    )

    data_list = []

    # Query the Cache.db database for matching URL endpoints
    source_path, records = get_cache_db_records(context, RE_CACHE_DB_MYPOINTS)
    if not records:
        return data_headers, data_list, source_path

    # Map all image assets available in the Kingfisher image cache directory
    image_map = _build_kingfisher_photo_map(context)

    for record in records:
        try:
            # Retrieve JSON payload content from the database row or local filesystem cache
            (
                entry_id,
                cache_time,
                request_url,
                json_data,
                device_file_paths
            ) = _get_cache_record(record, context, LIDL_BUNDLE_ID)

            if not json_data or not isinstance(json_data, dict):
                continue

            # Account-level points snapshot, shared across every reward row
            # extracted from this same cache entry
            account_points = json_data.get('availablePoints')
            points_to_expire = json_data.get('pointsToExpire')
            next_expiration = convert_iso8601_to_utc(json_data.get('nextExpirationDate'))
            catalog_total = json_data.get('total')

            # Marketplace list response
            rewards_list = json_data.get('items')

            if isinstance(rewards_list, list) and rewards_list:
                rewards_source = rewards_list
                rewards_location = 'receiver_data.items'
            # Marketplace detail response
            elif json_data.get('id'):
                rewards_source = [json_data]
                rewards_location = 'receiver_data'
            else:
                continue

            for r, reward in enumerate(rewards_source):
                if not isinstance(reward, dict):
                    continue

                reward_id = reward.get('id')
                if not reward_id:
                    continue

                # Standardize the reward's redemption-window timestamp, if present
                available_on = convert_iso8601_to_utc(reward.get('availableOn'))

                # Resolve image tracking using Kingfisher cache mapping logic
                image_url = reward.get('imageUrl')
                images = [{'url': image_url}] if image_url else []

                physical_path = None
                image_cache_match = 'N/A'

                local_device_paths = list(device_file_paths)

                cache_hit = _check_kingfisher_cache(images, image_map)

                if cache_hit:
                    physical_path = cache_hit.get('path')
                    image_cache_match = _format_kingfisher_match_type(
                        cache_hit.get('match_type')
                    )

                    if physical_path:
                        local_device_paths.append(
                            get_device_file_path(physical_path, context)
                        )

                media_ref_id = (
                    check_in_media(physical_path)
                    if physical_path
                    else None
                )

                # Standardize and merge all collected device file system references
                device_path = COMMA_SEP.join(local_device_paths)

                # Reconstruct precise location indexing within the original cached array
                if rewards_location == 'receiver_data':
                    location_parts = _build_cache_location_parts(
                        entry_id,
                        'receiver_data'
                    )
                else:
                    location_parts = _build_cache_location_parts(
                        entry_id,
                        f"{rewards_location}[{r}]"
                    )
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    cache_time,
                    reward.get('type'),
                    reward.get('subType'),
                    reward.get('summary'),
                    reward.get('points'),
                    reward.get('price'),
                    reward.get('discountValue'),
                    reward.get('discountTitle'),
                    reward.get('state'),
                    convert_bool_to_str(reward.get('isDisabled')),
                    convert_bool_to_str(reward.get('isBlocked')),
                    convert_bool_to_str(reward.get('isFavorite')),
                    convert_bool_to_str(reward.get('isExchangedPreviously')),
                    convert_bool_to_str(reward.get('exchangeButtonIsEnabled')),
                    reward.get('daysUntilExpiration'),
                    reward.get('availablePromotions'),
                    reward.get('relatedOnlineArticleNumber'),
                    media_ref_id,
                    image_url,                                      # 18 Image URL
                    image_cache_match,
                    available_on,
                    reward_id,
                    account_points,
                    points_to_expire,
                    next_expiration,
                    catalog_total,
                    request_url,                                    # 26 Request URL
                    device_path,                                    # 27 SOURCE_FILE_NAME
                    location                                        # 28 Location
                )

                data_list.append(base_data)

        except (AttributeError, ValueError, IndexError, TypeError) as ex:
            logfunc(f"[{context.get_artifact_name()}] Error parsing record: {ex}")
            continue

    # Sort final timeline by Cache Time descending (newest updates first)
    data_list.sort(key=lambda x: x[0] if x[0] else '', reverse=True)

    return data_headers, data_list, SOURCE_PATH_NOTE


@artifact_processor
def lidl_last_known_location(context):
    # pylint: disable=too-many-locals
    """
    Extracts the last known location stored by the Lidl Plus application.
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Horizontal Accuracy (m)',
        'Altitude (m)',
        'Ellipsoidal Altitude (m)',
        'Vertical Accuracy (m)',
        'Speed (m/s)',
        'Speed Accuracy (m/s)',
        'Course (°)',
        'Course Accuracy (°)',
        'Floor Level',
        'Location',
    )

    data_list = []

    # Search for the plist preferences file
    source_path = context.get_source_file_path('com.lidl.eci.lidl.plus.plist')
    if not source_path:
        return data_headers, data_list, source_path

    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict) or not plist:
        return data_headers, data_list, source_path

    try:
        # Extract the serialized CLLocation dictionary
        ns_cll = plist.get('com.swiftlocation.last-gps-location')
        if not ns_cll:
            return data_headers, data_list, source_path

        cllocation = get_plist_content(ns_cll)
        if not isinstance(cllocation, dict) or not cllocation:
            return data_headers, data_list, source_path

        # Convert Cocoa Epoch timestamp to UTC
        creation_time = convert_cocoa_core_data_ts_to_utc(
            cllocation.get('kCLLocationCodingKeyTimestamp')
        )

        # Geographic coordinates and horizontal accuracy
        lat = cllocation.get('kCLLocationCodingKeyCoordinateLatitude')
        lon = cllocation.get('kCLLocationCodingKeyCoordinateLongitude')
        horiz_acc = cllocation.get('kCLLocationCodingKeyHorizontalAccuracy')

        # Altitude metrics and vertical accuracy
        alt = cllocation.get('kCLLocationCodingKeyAltitude')
        alt_ell = cllocation.get('kCLLocationCodingKeyEllipsoidalAltitude')
        alt_acc = cllocation.get('kCLLocationCodingKeyVerticalAccuracy')

        # Speed and speed-related accuracy metrics
        speed = cllocation.get('kCLLocationCodingKeySpeed')
        speed_acc = cllocation.get('kCLLocationCodingKeySpeedAccuracy')

        # Direction of travel (course) and course accuracy
        course = cllocation.get('kCLLocationCodingKeyCourse')
        course_acc = cllocation.get('kCLLocationCodingKeyCourseAccuracy')

        # Indoor floor level
        floor_lvl = cllocation.get('kCLLocationCodingKeyFloor')
        if isinstance(floor_lvl, dict):
            floor_lvl = floor_lvl.get('level')

        # Source key path inside the plist file for validation tracking
        location = "[com.swiftlocation.last-gps-location]"

        # Base row
        base_data = (
            creation_time,
            lat,
            lon,
            horiz_acc,
            alt,
            alt_ell,
            alt_acc,
            speed,
            speed_acc,
            course,
            course_acc,
            floor_lvl,
            location
        )

        # Lava row
        data_list.append(base_data)

    except (AttributeError, KeyError, ValueError, IndexError, TypeError) as ex:
        logfunc(f"[{context.get_artifact_name()}] Error parsing plist: {ex}")

    return data_headers, data_list, source_path


@artifact_processor
def lidl_selfscan_basket(context):
    # pylint: disable=too-many-locals
    """
    Extracts self-scanning basket items from the encrypted Lidl Plus self-scanning database.
    """

    data_headers = (
        ('Scanned At', 'datetime'),
        ('Created', 'datetime'),
        ('Last Updated', 'datetime'),
        'Status',
        'Scan ID',
        'Product ID',
        'Barcode',
        'Product Name',
        'Quantity',
        'Unit Price',
        'Subtotal',
        'Discount',
        'Currency',
        'Deposit (MasterData)',
        'Restrictions (MasterData)',
        'Location'
    )

    data_list = []

    # Search for the encrypted self-scanning database
    source_path = context.get_source_file_path('selfScanning.sqlite')
    if not source_path:
        return data_headers, data_list, source_path

    plain_path = _decrypt_database(
        source_path, context, db_config=DB_CONFIGS['selfScanning.sqlite']
    )
    if not plain_path:
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(plain_path)
    if not db:
        return data_headers, data_list, source_path

    try:
        cursor = db.cursor()

        query = """
        SELECT
            B.rowid,
            M.rowId,
            unixepoch(B.scannedAt, 'auto', 'subsec') AS "scanned_at",
            unixepoch(B.createdAt, 'auto', 'subsec') AS "created_at",
            unixepoch(B.updatedAt, 'auto', 'subsec') AS "updated_at",
            B.status,
            B.scanId,
            B.productId,
            coalesce(B.barcode, M.barcode) AS "barcode",
            coalesce(B.name, M.name) AS "product_name",
            B.quantity,
            coalesce(B.unitPrice, M.unitPrice) AS "unit_price",
            B.subtotal,
            B.totalDiscount,
            B.currency,
            M.deposit,
            M.restrictions
        FROM BasketItemRows AS "B"
        LEFT JOIN MasterDataItemRows AS "M" ON (B.productId = M.id)
        ORDER BY B.scannedAt DESC
        """

        cursor.execute(query)
        for record in cursor:
            try:
                (b_row_id, m_row_id, raw_scanned_at, raw_created,
                 raw_updated, status, scan_id, product_id, barcode,
                 product_name, quantity, unit_price, subtotal, tot_discount,
                 currency, deposit, restrictions) = record

                # Convert timestamps to UTC
                scanned_at = convert_unix_ts_to_utc(raw_scanned_at)
                created = convert_unix_ts_to_utc(raw_created)
                updated = convert_unix_ts_to_utc(raw_updated)

                # Precise location within the source database table for validation
                location_parts = [ f"BasketItemRows (rowId: {b_row_id})" ]
                if m_row_id is not None:
                    location_parts.append(f"MasterDataItemRows (rowId: {m_row_id})")
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    scanned_at,
                    created,
                    updated,
                    status,
                    scan_id,
                    product_id,
                    barcode,
                    product_name,
                    quantity,
                    unit_price,
                    subtotal,
                    tot_discount,
                    currency,
                    deposit,
                    restrictions,
                    location                                        # 15 Location
                )

                data_list.append(base_data)

            except (AttributeError, ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record BasketItemRows {_id} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, data_list, source_path


@artifact_processor
def lidl_selfscan_journey(context):
    # pylint: disable=too-many-locals
    """
    Extracts self-scanning barcode events from the encrypted Lidl Plus self-scanning database.
    """

    data_headers = (
        ('Scanned At', 'datetime'),
        'Product ID (MasterData)',
        'Barcode',
        'Product Name (MasterData)',
        'Quantity',
        'Unit Price (MasterData)',
        'Deposit (MasterData)',
        'Location'
    )

    data_list = []

    # Search for the encrypted self-scanning database
    source_path = context.get_source_file_path('selfScanning.sqlite')
    if not source_path:
        return data_headers, data_list, source_path

    plain_path = _decrypt_database(
        source_path, context, db_config=DB_CONFIGS['selfScanning.sqlite']
    )
    if not plain_path:
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(plain_path)
    if not db:
        return data_headers, data_list, source_path

    try:
        cursor = db.cursor()

        query = """
        SELECT
            S.rowId,
            M.rowId,
            unixepoch(S.scannedAt, 'auto', 'subsec') AS "scanned_at",
            M.id,
            coalesce(S.barcode, M.barcode) AS "barcode",
            M.name,
            S.quantity,
            M.unitPrice,
            M.deposit
        FROM ScanningJourneyRows AS "S"
        LEFT JOIN MasterDataItemRows AS "M" ON (S.barcode = M.barcode)
        ORDER BY S.scannedAt DESC
        """

        cursor.execute(query)
        for record in cursor:
            try:
                (s_row_id, m_row_id, raw_scanned_at, product_id, barcode,
                 product_name, quantity, unit_price, deposit) = record

                # Convert timestamps to UTC
                scanned_at = convert_unix_ts_to_utc(raw_scanned_at)

                # Precise location within the source database table for validation
                location_parts = [ f"ScanningJourneyRows (rowId: {s_row_id})" ]
                if m_row_id is not None:
                    location_parts.append(f"MasterDataItemRows (rowId: {m_row_id})")
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    scanned_at,
                    product_id,
                    barcode,
                    product_name,
                    quantity,
                    unit_price,
                    deposit,
                    location                                        # 7 Location
                )

                data_list.append(base_data)

            except (AttributeError, ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record ScanningJourneyRows {_id} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, data_list, source_path


@artifact_processor
def lidl_selfscan_removed(context):
    # pylint: disable=too-many-locals
    """
    Extracts removed self-scanning basket items from the encrypted Lidl Plus self-scanning database.
    """

    data_headers = (
        ('Removed', 'datetime'),
        'Product ID (MasterData)',
        'Barcode',
        'Product Name (MasterData)',
        'Quantity',
        'Unit Price',
        'Total Price',
        'Savings',
        'VAT',
        'Weight',
        'Item Number',
        'Location'
    )

    data_list = []

    # Search for the encrypted self-scanning database
    source_path = context.get_source_file_path('selfScanning.sqlite')
    if not source_path:
        return data_headers, data_list, source_path

    plain_path = _decrypt_database(
        source_path, context, db_config=DB_CONFIGS['selfScanning.sqlite']
    )
    if not plain_path:
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(plain_path)
    if not db:
        return data_headers, data_list, source_path

    try:
        cursor = db.cursor()

        query = """
        SELECT
            R.rowId,
            M.rowId,
            unixepoch(R.removedAt, 'auto', 'subsec') AS "removed_at",
            M.id,
            coalesce(R.barcode, M.barcode) AS "barcode",
            M.name,
            R.quantity,
            coalesce(R.unitPrice, M.unitPrice) AS "unit_price",
            R.totalPrice,
            R.savings,
            R.vatAmount,
            R.weight,
            R.itemNr
        FROM RemovedItemRows AS "R"
        LEFT JOIN MasterDataItemRows AS "M" ON (R.barcode = M.barcode)
        ORDER BY R.removedAt DESC
        """

        cursor.execute(query)
        for record in cursor:
            try:
                (r_row_id, m_row_id, raw_removed_at, product_id, barcode,
                 product_name, quantity, unit_price, total_price, saving,
                 vat, weight, item_nr) = record

                # Convert timestamps to UTC
                removed_at = convert_unix_ts_to_utc(raw_removed_at)

                # Precise location within the source database table for validation
                location_parts = [ f"RemovedItemRows (rowId: {r_row_id})" ]
                if m_row_id is not None:
                    location_parts.append(f"MasterDataItemRows (rowId: {m_row_id})")
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    removed_at,
                    product_id,
                    barcode,
                    product_name,
                    quantity,
                    unit_price,
                    total_price,
                    saving,
                    vat,
                    weight,
                    item_nr,
                    location                                        # 11 Location
                )

                data_list.append(base_data)

            except (AttributeError, ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record RemovedItemRows {_id} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        # Log fatal database errors (e.g., malformed DB or missing tables)
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        # Ensure the database connection is closed safely
        db.close()

    return data_headers, data_list, source_path


@artifact_processor
def lidl_grocery_pickup_cart(context):
    # pylint: disable=too-many-locals
    """
    Extracts Click&Collect grocery pickup cart contents from the encrypted Lidl Plus database.
    """

    data_headers = (
        ('Last Updated', 'datetime'),
        ('Created', 'datetime'),
        'Product ID',
        'Product Name',
        'Subtitle',
        'Image URL',
        'Quantity',
        'Max Quantity (Cart)',
        'Unit Price',
        'Deposit Amount',
        'Deposit Name',
        'Discount Amount',
        'Original Amount',
        'Total Amount',
        'Currency',
        'Weight Unit',
        'Weight Value',
        'Weight Unit Price',
        'Allows Substitutions',
        'Available (Cart)',
        'Available (Server Restriction)',
        'Max Quantity (Server Restriction)',
        ('Restriction Last Updated', 'datetime'),
        'Validations',
        'Location'
    )

    data_list = []
    data_list_html = []

    # Search for the encrypted grocery pickup database
    source_path = context.get_source_file_path('groceryPickup.sqlite')
    if not source_path:
        return data_headers, (data_list, data_list_html), source_path

    plain_path = _decrypt_database(
        source_path, context, db_config=DB_CONFIGS['groceryPickup.sqlite']
    )
    if not plain_path:
        return data_headers, (data_list, data_list_html), source_path

    db = open_sqlite_db_readonly(plain_path)
    if not db:
        return data_headers, (data_list, data_list_html), source_path

    try:
        cursor = db.cursor()

        query = """
        SELECT
            C.rowId,
            R.rowid,
            C.productId,
            C.name,
            C.subtitle,
            C.imageUrl,
            C.quantity,
            C.maxQuantity,
            C.hasSubstitutions,
            C.isAvailable,
            C.validations,
            C.unitaryAmount,
            C.depositAmount,
            C.depositName,
            C.discountAmount,
            C.originalAmount,
            C.totalAmount,
            C.currency,
            C.weightUnit,
            C.weightUnitaryValue,
            C.weightUnitaryPrice,
            unixepoch(C.createdAt, 'auto', 'subsec') AS "created_at",
            unixepoch(C.updatedAt, 'auto', 'subsec') AS "updated_at",
            R.isAvailable AS "restr_is_available",
            R.maxQuantity AS "restr_max_quantity",
            unixepoch(R.updatedAt, 'auto', 'subsec') AS "restr_updated_at"
        FROM cart AS "C"
        LEFT JOIN productRestrictions AS "R" ON (C.productId = R.productId)
        ORDER BY C.updatedAt DESC
        """

        cursor.execute(query)
        for record in cursor:
            try:
                (c_row_id, r_row_id, product_id, name, subtitle, image_url,
                 quantity, max_qty_cart, has_subs, is_avail_cart, validations_raw,
                 unit_price, deposit_amt, deposit_name, discount_amt,
                 original_amt, total_amt, currency, weight_unit,
                 weight_value, weight_unit_price, raw_created, raw_updated,
                 restr_is_avail, restr_max_qty,
                 raw_restr_updated) = record

                # Convert GRDB timestamps to UTC
                created = convert_unix_ts_to_utc(raw_created)
                updated = convert_unix_ts_to_utc(raw_updated)
                restr_updated = (
                    convert_unix_ts_to_utc(raw_restr_updated)
                    if raw_restr_updated is not None else None
                )

                # Preserve the observed validation values.
                # If the TEXT column contains a JSON array, flatten its values for reporting.
                validation_values = validations_raw
                validation_parts = None

                if validations_raw:
                    try:
                        parsed = json.loads(validations_raw)
                        if isinstance(parsed, list):
                            validation_parts = [ str(value) for value in parsed ]
                            validation_values = LIST_SEP.join(validation_parts)

                    except (JSONDecodeError, TypeError):
                        pass

                # Precise location within the source database for validation
                location_parts = [ f"cart (rowId: {c_row_id})" ]
                if r_row_id is not None:
                    location_parts.append(f"productRestrictions (rowId: {r_row_id})")
                location = COMMA_SEP.join(location_parts)

                # Base row
                base_data = (
                    updated,
                    created,
                    product_id,
                    name,
                    subtitle,
                    image_url,                                      # 5 Image URL
                    quantity,
                    max_qty_cart,
                    unit_price,
                    deposit_amt,
                    deposit_name,
                    discount_amt,
                    original_amt,
                    total_amt,
                    currency,
                    weight_unit,
                    weight_value,
                    weight_unit_price,
                    convert_sqlite_bool_to_str(has_subs),
                    convert_sqlite_bool_to_str(is_avail_cart),
                    convert_sqlite_bool_to_str(restr_is_avail),
                    restr_max_qty,
                    restr_updated,
                    validation_values,                              # 23 Validation
                    location                                        # 24 Location
                )

                # LAVA row
                data_list.append(base_data)

                # HTML row
                html_data = list(base_data)

                if validation_parts is not None:
                    html_data[23] = safe_join(validation_parts)
                else:
                    html_data[23] = esc(validation_values)

                data_list_html.append(tuple(html_data))

            except (AttributeError, ValueError, IndexError, TypeError) as ex:
                _id = record[0] if record and len(record) > 0 else 'UNKNOWN'
                logfunc(f"[{context.get_artifact_name()}] "
                        f"Error - Failed parsing record cart {_id} "
                        f"in {source_path}: {ex}")
                continue

    except sqlite3.Error as db_ex:
        logfunc(f"[{context.get_artifact_name()}] "
                f"Error - executing query on {source_path}: {db_ex}")
    finally:
        db.close()

    return data_headers, (data_list, data_list_html), source_path


@artifact_processor
def lidl_account(context):
    # pylint: disable=too-many-locals
    """
    Extracts Lidl Plus user-account information stored in the iOS Keychain.
    """

    data_headers = (
        'Subject ID (User ID)',
        'Name',
        'Middle Name',
        'Email',
        ('Phone Number', 'phonenumber'),
        'Phone Prefix Number',
        ('Birthdate', 'date'),
        'Authentication (AMR)',
        'Location'
    )

    data_list = []
    source_path = ''

    # Retrieve the raw serialized account object from the active Keychain.
    try:
        account_blob, resolved_keychain = _query_keychain_item(
            context=context,
            account='storedUser',
            service='LidlPlus',
            access_group=f"{LIDL_TEAM_ID}.{LIDL_BUNDLE_ID}",
            return_raw=True
        )
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(
            f"[{context.get_artifact_name()}] Error retrieving the "
            f"'storedUser' Keychain item: {ex}"
        )
        return data_headers, data_list, source_path

    if resolved_keychain:
        source_path = resolved_keychain

    if not account_blob:
        if resolved_keychain:
            logfunc(
                f"[{context.get_artifact_name()}] No Keychain item matched "
                f"Account='storedUser', Service='LidlPlus', "
                f"AccessGroup='{LIDL_TEAM_ID}.{LIDL_BUNDLE_ID}'."
            )
        else:
            logfunc(
                f"[{context.get_artifact_name()}] No Keychain source was "
                "resolved for account extraction."
            )
        return data_headers, data_list, source_path

    # Decode the serialized plist / NSKeyedArchiver account payload
    account_info = get_plist_content(account_blob)
    if not isinstance(account_info, dict) or not account_info:
        return data_headers, data_list, source_path

    # Report additional storedUser keys without interpreting their semantics
    additional_keys = {
        key: type(value).__name__
        for key, value in account_info.items()
        if key not in LIDL_KNOWN_STORED_USER_KEYS
    }

    if additional_keys:
        additional_desc = ', '.join(
            f"{key} ({value_type})"
            for key, value_type in sorted(additional_keys.items())
        )

        logfunc(
            f"[{context.get_artifact_name()}] "
            f"Additional storedUser key(s) observed: {additional_desc}"
        )

    try:
        subject_id = account_info.get('sub')
        name = account_info.get('name')
        middle_name = account_info.get('middle_name')
        email = account_info.get('email')
        phone_number = account_info.get('phone_number')
        phone_prefix = account_info.get('phone_prefix_number')
        birthdate = account_info.get('birthdate')
        # Flatten Authentication Method Reference arrays for report output.
        amr = account_info.get('amr')
        if isinstance(amr, (list, tuple, set)):
            amr = COMMA_SEP.join(
                str(value)
                for value in amr
                if value is not None and str(value)
            )

        # Record the exact logical Keychain selector used for this evidence.
        location = (
            "Keychain: "
            "Account=storedUser; "
            "Service=LidlPlus; "
            f"AccessGroup={LIDL_TEAM_ID}.{LIDL_BUNDLE_ID}"
        )

        # Base row
        base_data = (
            subject_id,
            name,
            middle_name,
            email,
            phone_number,
            phone_prefix,
            birthdate,
            amr,
            location
        )

        # LAVA row
        data_list.append(base_data)

    except (AttributeError, ValueError, IndexError, TypeError) as ex:
        logfunc(
            f"[{context.get_artifact_name()}] Error parsing the decoded "
            f"'storedUser' Keychain account object from {source_path}: {ex}"
        )

    return data_headers, data_list, source_path
