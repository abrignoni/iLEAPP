""" home_depot """
__artifacts_v2__ = {
    "home_depot_account": {
        "name": "Home Depot - Account & Store",
        "description": "Home Depot account profile and preferred local store details",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "nska_deserialize",
        "category": "Home Depot",
        "notes": (
            "Account data is parsed from three sources when present: USER_INFO_KEY in "
            "com.thehomedepot.homedepot.plist, SharedUserInfoKey in group.com.thehomedepot.homedepot.plist, "
            "and userInfo.txt in the App Group container. Contains PII."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',
            '*/Shared/AppGroup/*/userInfo.txt',
            '*/Shared/AppGroup/*/Library/Preferences/group.com.thehomedepot.homedepot.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "home_depot_saved_searches": {
        "name": "Home Depot - Saved Searches",
        "description": "Saved search terms and last-used timestamps",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "none",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "home_depot_search_history": {
        "name": "Home Depot - Search History",
        "description": "Search history from THDConsumer Core Data store",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "nska_deserialize",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Documents/THDConsumer.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "home_depot_products_viewed": {
        "name": "Home Depot - Products Viewed",
        "description": "Cached product details from THDConsumer Core Data store",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "nska_deserialize",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Documents/THDConsumer.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "shopping-bag",
    },
    "home_depot_shopping_lists": {
        "name": "Home Depot - Shopping Lists",
        "description": "Local shopping list items from THDConsumer Core Data store",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "nska_deserialize",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Documents/THDConsumer.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "list",
    },
    "home_depot_last_location": {
        "name": "Home Depot - Last Known Location",
        "description": "Last known GPS location from Home Depot app preferences",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "nska_deserialize",
        "category": "Home Depot",
        "notes": "Parsed from currentLocationKey CLLocation blob.",
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "home_depot_product_image_cache": {
        "name": "Home Depot - Product Image Cache",
        "description": "Cached product image URLs and HTTP Last-Modified timestamps",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "none",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "home_depot_search_url_cache": {
        "name": "Home Depot - Search URL Cache",
        "description": "Cached thdws.com search API URLs (deduplicated keystroke chains)",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "none",
        "category": "Home Depot",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',),
        "output_types": "standard",
        "artifact_icon": "link",
    },
    "home_depot_preferences": {
        "name": "Home Depot - Other Preferences",
        "description": "Remaining Home Depot preference keys not parsed by other artifacts",
        "author": "@jameshabben",
        "creation_date": "2026-06-26",
        "last_update_date": "2026-06-26",
        "requirements": "none",
        "category": "Home Depot",
        "notes": "Excludes product image cache, search URL cache, and SDK analytics keys.",
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.thehomedepot.homedepot.plist',),
        "output_types": "standard",
        "artifact_icon": "sliders",
    },
}

import datetime
import json
import re
import sqlite3
import urllib.parse
from email.utils import parsedate_to_datetime

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    convert_plist_date_to_utc,
    get_plist_content,
    get_plist_file_content,
    get_sqlite_db_path,
    logfunc,
)

_PREFERENCES_NAME = 'com.thehomedepot.homedepot.plist'
_GROUP_PREFERENCES_NAME = 'group.com.thehomedepot.homedepot.plist'
_USER_INFO_TXT = 'userInfo.txt'
_SQLITE_NAME = 'THDConsumer.sqlite'

_SOURCE_USER_INFO_KEY = 'USER_INFO_KEY (com.thehomedepot.homedepot.plist)'
_SOURCE_SHARED_USER_INFO = 'SharedUserInfoKey (group.com.thehomedepot.homedepot.plist)'
_SOURCE_USER_INFO_TXT = 'userInfo.txt (App Group)'

_PARSED_PLIST_KEYS = frozenset({
    'USER_INFO_KEY',
    'currentLocationKey',
    'savedSearches',
    'savedSearchesdates',
    'savedStorePreference',
    'lastUpdatedLocalList',
})

_EXCLUDED_PREFIXES = (
    'https://',
    'Adobe.',
    'AppsFlyer',
    'clearingCoTheVeryFirstTime',
    'hasAlreadyRegisteredForRemoteNotifications',
    'com.akamai.',
)

_PRODUCT_IMAGE_RE = re.compile(
    r'/productImages/[a-f0-9-]+/svn/(.+)-64_400\.jpg(?:-LastModified|-Etag)?$',
    re.IGNORECASE,
)


def _find_file_by_name(context, filename):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(filename):
            return file_found
    return ''


def _find_preferences(context):
    return _find_file_by_name(context, _PREFERENCES_NAME)


def _find_sqlite(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(_SQLITE_NAME):
            return file_found
    return ''


def _load_preferences(context):
    source_path = _find_preferences(context)
    if not source_path:
        return '', {}
    plist = get_plist_file_content(source_path)
    if not isinstance(plist, dict):
        return source_path, {}
    return source_path, plist


def _query_sqlite(path, query):
    db_path = get_sqlite_db_path(path)
    for uri_suffix in ('?mode=ro', '?mode=ro&immutable=1'):
        try:
            conn = sqlite3.connect(f'file:{db_path}{uri_suffix}', uri=True)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
            conn.close()
            return rows
        except sqlite3.OperationalError:
            continue
    logfunc(f'Home Depot: unable to open SQLite database at {path}')
    return []


def _load_blob(blob):
    if blob is None:
        return None
    if isinstance(blob, dict):
        return blob
    if not isinstance(blob, (bytes, bytearray)):
        return blob
    return get_plist_content(bytes(blob))


def _extract_user_info(blob):
    if blob is None:
        return None
    obj = _load_blob(blob)
    if isinstance(obj, dict) and 'accountIdentity' in obj:
        return obj

    if not isinstance(blob, (bytes, bytearray)):
        return None

    text = blob.decode('utf-8', errors='replace')
    start = text.find('{"accountIdentity"')
    if start < 0:
        return None
    depth = 0
    for idx in range(start, len(text)):
        if text[idx] == '{':
            depth += 1
        elif text[idx] == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:idx + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _load_user_info_txt(path):
    try:
        with open(path, encoding='utf-8') as handle:
            user_info = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(user_info, dict) and 'accountIdentity' in user_info:
        return user_info
    return None


def _dig(mapping, *keys, default=''):
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _format_store_ids(store_pref):
    if not isinstance(store_pref, dict):
        return ''
    ids = []
    for store_id, values in store_pref.items():
        if isinstance(values, list):
            ids.extend(str(v) for v in values)
        else:
            ids.append(str(store_id))
    seen = set()
    ordered = []
    for store_id in ids:
        if store_id not in seen:
            seen.add(store_id)
            ordered.append(store_id)
    return ', '.join(ordered)


def _to_utc(value):
    if value is None or value == '':
        return ''
    if isinstance(value, datetime.datetime):
        return convert_plist_date_to_utc(value)
    if isinstance(value, (int, float)):
        return convert_cocoa_core_data_ts_to_utc(value)
    return value


def _parse_http_date(value):
    if not value:
        return ''
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value


def _stringify(value):
    if isinstance(value, datetime.datetime):
        return convert_plist_date_to_utc(value).isoformat()
    if isinstance(value, bytes):
        return f'<binary {len(value)} bytes>'
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return str(value)


def _is_product_cache_key(key):
    return bool(key.startswith('https://') and 'productImages' in key and key.endswith('-LastModified'))


def _is_search_url_key(key):
    base = re.sub(r'-(LastModified|Etag)$', '', key)
    return 'thdws.com' in base and '/search?' in base


def _parse_product_image_key(key, value):
    base_url = key[:-len('-LastModified')] if key.endswith('-LastModified') else key
    match = _PRODUCT_IMAGE_RE.search(base_url)
    slug = match.group(1).replace('-', ' ') if match else base_url
    return slug, base_url, value


def _parse_search_term_from_key(key):
    base = re.sub(r'-(LastModified|Etag)$', '', key)
    match = re.search(r'[?&]term=([^&]+)', base)
    if not match:
        return None, base
    term = urllib.parse.unquote(match.group(1).replace('+', ' '))
    return term, base


def _collapse_search_terms(terms):
    unique_terms = sorted(set(terms), key=lambda item: (-len(item), item.lower()))
    kept = []
    for term in unique_terms:
        if any(term != other and other.startswith(term) for other in unique_terms if len(other) > len(term)):
            continue
        kept.append(term)
    return sorted(kept, key=str.lower)


def _should_exclude_preference_key(key):
    if key in _PARSED_PLIST_KEYS:
        return True
    if any(key.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
        return True
    if _is_product_cache_key(key) or _is_search_url_key(key):
        return True
    return False


def _product_field(product, field_name):
    value = product.get(field_name, '')
    if isinstance(value, dict) and 'NS.string' in value:
        return value['NS.string']
    return value


def _build_account_row(user_info, preferred_store_ids, source):
    account = user_info.get('accountInfo', {}).get('accountInfoB2C', {}).get('account', {})
    phone_list = account.get('profilePhones', {}).get('phone', [])
    phone = phone_list[0].get('number', '') if phone_list else ''
    store = user_info.get('localStore', {})
    address = store.get('address', {})
    coords = store.get('coordinates', {})

    return (
        source,
        _dig(user_info, 'accountIdentity', 'userId'),
        _dig(user_info, 'accountIdentity', 'logonId'),
        _dig(user_info, 'accountInfo', 'accountInfoB2C', 'account', 'profile', 'name', 'firstName'),
        _dig(user_info, 'accountInfo', 'accountInfoB2C', 'account', 'profile', 'name', 'lastName'),
        phone,
        _dig(user_info, 'accountIdentity', 'customerType'),
        _dig(user_info, 'accountInfo', 'accountInfoB2C', 'account', 'profile', 'zipCode'),
        _dig(user_info, 'accountInfo', 'accountInfoB2C', 'account', 'customerAccountId'),
        _dig(user_info, 'accountInfo', 'accountInfoB2C', 'account', 'profile', 'localStoreId'),
        preferred_store_ids,
        store.get('name', ''),
        address.get('street', ''),
        address.get('city', ''),
        address.get('state', ''),
        address.get('postalCode', ''),
        coords.get('lat', ''),
        coords.get('lng', ''),
        store.get('phone', ''),
    )


@artifact_processor
def home_depot_account(context):
    """ see artifact description """
    data_headers = (
        'Source', 'User ID', 'Email', 'First Name', 'Last Name', ('Phone', 'phonenumber'), 'Customer Type',
        'Zip Code', 'Customer Account ID', 'Local Store ID', 'Preferred Store IDs', 'Store Name', 'Store Street',
        'Store City', 'Store State', 'Store Postal Code', 'Store Latitude', 'Store Longitude',
        ('Store Phone', 'phonenumber'),
    )
    # TODO: wire in location data for KML output
    data_list = []
    source_paths = []

    source_path, plist = _load_preferences(context)
    if plist:
        user_info = _extract_user_info(plist.get('USER_INFO_KEY'))
        if user_info:
            preferred_store_ids = _format_store_ids(plist.get('savedStorePreference'))
            data_list.append(_build_account_row(user_info, preferred_store_ids, _SOURCE_USER_INFO_KEY))
            source_paths.append(context.get_relative_path(source_path))

    group_path = _find_file_by_name(context, _GROUP_PREFERENCES_NAME)
    if group_path:
        group_plist = get_plist_file_content(group_path)
        if isinstance(group_plist, dict):
            user_info = _extract_user_info(group_plist.get('SharedUserInfoKey'))
            if user_info:
                data_list.append(_build_account_row(user_info, '', _SOURCE_SHARED_USER_INFO))
                source_paths.append(context.get_relative_path(group_path))

    txt_path = _find_file_by_name(context, _USER_INFO_TXT)
    if txt_path:
        user_info = _load_user_info_txt(txt_path)
        if user_info:
            data_list.append(_build_account_row(user_info, '', _SOURCE_USER_INFO_TXT))
            source_paths.append(context.get_relative_path(txt_path))

    return data_headers, data_list, '; '.join(source_paths)


@artifact_processor
def home_depot_saved_searches(context):
    """ see artifact description """
    data_headers = (('Date Saved', 'datetime'), 'Search Term', 'In Saved List')
    data_list = []
    source_path, plist = _load_preferences(context)
    if not plist:
        return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''

    saved = set(plist.get('savedSearches', []) or [])
    dates = plist.get('savedSearchesdates', {}) or {}
    for term, saved_date in dates.items():
        data_list.append((
            _to_utc(saved_date),
            term,
            'Yes' if term in saved else 'No',
        ))

    for term in sorted(saved):
        if term not in dates:
            data_list.append(('', term, 'Yes'))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_search_history(context):
    """ see artifact description """
    data_headers = (('Date Accessed', 'datetime'), 'Search Term', 'History Type')
    data_list = []
    source_path = _find_sqlite(context)
    if not source_path:
        return data_headers, data_list, ''

    query = 'SELECT ZHISTORYID, ZHISTORY FROM ZHISTORYENTITY'
    for row in _query_sqlite(source_path, query):
        _history_id, blob = row[0], row[1]
        history = _load_blob(blob)
        if not isinstance(history, dict):
            continue
        data_list.append((
            _to_utc(history.get('dateAccessedKey')),
            history.get('strIdKey', ''),
            history.get('historyTypeKey', ''),
        ))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_products_viewed(context):
    """ see artifact description """
    data_headers = (
        'Item ID', 'Product Label', 'Brand', 'Model Number', 'Store SKU', 'Price', 'Product URL', 'Image URL',
    )
    data_list = []
    source_path = _find_sqlite(context)
    if not source_path:
        return data_headers, data_list, ''

    query = 'SELECT ZPRODUCTID, ZPRODUCTSEARCHSKU FROM ZPRODUCTENTITY'
    for row in _query_sqlite(source_path, query):
        product_id, blob = row[0], row[1]
        product = _load_blob(blob)
        if not isinstance(product, dict):
            continue
        data_list.append((
            product_id or _product_field(product, 'itemIdKey'),
            _product_field(product, 'productLabelKey'),
            _product_field(product, 'brandNameKey'),
            _product_field(product, 'modelNumberKey'),
            _product_field(product, 'storeSkuNumberKey'),
            _product_field(product, 'specialPriceKey'),
            _product_field(product, 'serviceUrlKey'),
            _product_field(product, 'imageKey'),
        ))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_shopping_lists(context):
    """ see artifact description """
    data_headers = ('List Item ID', 'Details')
    data_list = []
    source_path = _find_sqlite(context)
    if not source_path:
        return data_headers, data_list, ''

    query = 'SELECT ZLOCALLISTITEMID, ZLOCALLISTITEM FROM ZLOCALLISTITEMENTITY'
    for row in _query_sqlite(source_path, query):
        item_id, blob = row[0], row[1]
        item = _load_blob(blob)
        if isinstance(item, dict):
            details = json.dumps(item, default=str)
        elif item is None:
            details = ''
        else:
            details = str(item)
        data_list.append((item_id, details))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_last_location(context):
    """ see artifact description """
    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy', 'Altitude',
    )
    # TODO: wire in location data for KML output
    data_list = []
    source_path, plist = _load_preferences(context)
    if not plist:
        return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''

    location = _load_blob(plist.get('currentLocationKey'))
    if not isinstance(location, dict):
        return data_headers, data_list, context.get_relative_path(source_path)

    latitude = location.get('kCLLocationCodingKeyCoordinateLatitude')
    if latitude in (None, ''):
        latitude = location.get('kCLLocationCodingKeyRawCoordinateLatitude', '')

    longitude = location.get('kCLLocationCodingKeyCoordinateLongitude')
    if longitude in (None, ''):
        longitude = location.get('kCLLocationCodingKeyRawCoordinateLongitude', '')

    data_list.append((
        _to_utc(location.get('kCLLocationCodingKeyTimestamp')),
        latitude,
        longitude,
        location.get('kCLLocationCodingKeyHorizontalAccuracy', ''),
        location.get('kCLLocationCodingKeyAltitude', ''),
    ))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_product_image_cache(context):
    """ see artifact description """
    data_headers = (('Cache Date', 'datetime'), 'Product Slug', 'Image URL')
    data_list = []
    source_path, plist = _load_preferences(context)
    if not plist:
        return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''

    for key, value in plist.items():
        if not _is_product_cache_key(key):
            continue
        slug, image_url, cache_date = _parse_product_image_key(key, value)
        data_list.append((_parse_http_date(cache_date), slug, image_url))

    data_list.sort(key=lambda row: (row[0] or '', row[1].lower()))
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_search_url_cache(context):
    """ see artifact description """
    data_headers = ('Search Term', 'Search URL')
    data_list = []
    source_path, plist = _load_preferences(context)
    if not plist:
        return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''

    term_urls = {}
    for key in plist:
        if not _is_search_url_key(key):
            continue
        term, url = _parse_search_term_from_key(key)
        if not term:
            continue
        term_urls.setdefault(term, url)

    for term in _collapse_search_terms(term_urls):
        data_list.append((term, term_urls[term]))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def home_depot_preferences(context):
    """ see artifact description """
    data_headers = ('Key Name', 'Value Data')
    data_list = []
    source_path, plist = _load_preferences(context)
    if not plist:
        return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''

    for key in sorted(plist):
        if _should_exclude_preference_key(key):
            continue
        data_list.append((key, _stringify(plist[key])))

    return data_headers, data_list, context.get_relative_path(source_path)
