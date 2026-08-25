"""
Parses Apple iOS Amazon Shopping application artifacts.

Every path and field in this module was derived from two private iOS Data containers
whose .com.apple.mobile_container_manager.metadata.plist records
MCMMetadataIdentifier = com.amazon.AmazonUK. Other Amazon storefront builds are not
covered by that observation.
"""
# pylint: disable=too-many-lines

import os
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (
    open_sqlite_db_readonly, get_plist_file_content, check_in_media,
    artifact_processor, logfunc
)

SOURCE_FILE = 'Source File'
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
COCOA_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

__artifacts_v2__ = {
    "amazon_account": {
        "name": "Amazon - Account and App State",
        "description": (
            "Reports selected account, marketplace, device and app-state values from the "
            "Amazon Shopping preferences store."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Values are read from Library/Preferences/com.amazon.AmazonUK.plist. Only keys "
            "on an explicit list are reported; the store holds several hundred further keys, "
            "most of them A/B test treatment codes. Timestamp units were established per key "
            "by decoding the stored value against each candidate epoch and keeping the only "
            "reading that falls inside the app's observed lifetime; the app binary is not "
            "present in a Data container, so no producing call site could be read. Keys "
            "carrying a converted value also report the stored value in Raw Value. "
            "AmazonAd: timestamps decode as Cocoa/Mac absolute seconds, DCMArcusLastSyncedTimeKey "
            "and MinervaArcusLastSyncedTimeKey as Unix milliseconds, and "
            "LocalSamplingKeyLastUpdatedTime as Unix seconds, so unit is a property of the key "
            "and not of the store. Pam* values are ISO 8601 strings carrying no UTC offset and "
            "are reported as stored. LastRefreshTime is a small number of seconds that does not "
            "decode to a plausible date under any epoch tried, so it is reported as stored "
            "without interpretation."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/com.amazon.AmazonUK.plist',),
        "output_types": ["standard"],
        "artifact_icon": "shopping-cart"
    },
    "amazon_profiles": {
        "name": "Amazon - Profiles",
        "description": (
            "Reports Amazon account profiles held in the app's React Native storage, and the "
            "account identifiers used to name per-account preference files."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Profile rows come from the pandaStore sub-store of persist:root in "
            "Documents/RCTAsyncLocalStorage_V1/manifest.json, which records accountId, fullName, "
            "primaryAccountClaim and primaryAccountClaimType per account. lastActive and "
            "lastUpdated decode as Unix milliseconds. That manifest path is the standard React "
            "Native AsyncStorage location and is not unique to this app, so rows are emitted only "
            "when the file carries an Amazon account identifier. Account rows without a profile "
            "come from the names of Library/Preferences/amzn1.account.*.plist files; the identifier "
            "is the file name, and the file contents are Alexa wakeword settings. Presence of an "
            "account identifier records that the account was known to the app on this device; it "
            "does not establish that the account was signed in at acquisition."),
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/manifest.json',
                  '*/mobile/Containers/Data/Application/*/Library/Preferences/amzn1.account.*.plist',),
        "output_types": ["standard"],
        "artifact_icon": "users"
    },
    "amazon_orders": {
        "name": "Amazon - Orders",
        "description": (
            "Reports orders and order line items from the app's cached orders API response."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Rows are parsed from the JSON body cached in the app's NSURLCache for requests to "
            "appx.transient.amazon.*/api/orders/v1. This is the order list the app last fetched "
            "for the tab that displays it, not a complete order history; the request URL caps the "
            "response with maxOrders and asinsPerOrder parameters, and the cached copy is replaced "
            "on the next fetch. orderDate decodes as Unix seconds. Cached is the NSURLCache entry "
            "time_stamp, stored by SQLite as UTC text. Line item images are linked by taking the "
            "image identifier from the line item imageUrl, matching it against the url column of "
            "the SSNAP image cache registry, and resolving that row's recorded filePath by file "
            "name inside Library/Caches/ssnap_image_cache; the recorded path carries the container "
            "UUID of the acquiring device, so only the file name is used. A line item whose image "
            "is not in that cache is reported with an empty media cell rather than dropped."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.amazon.AmazonUK/Cache.db*',
                  '*/mobile/Containers/Data/Application/*/Library/LocalDatabase/ssnapImageCacheRegistry.db*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/ssnap_image_cache/*',),
        "output_types": ["standard"],
        "artifact_icon": "package"
    },
    "amazon_products": {
        "name": "Amazon - Product Lookups",
        "description": (
            "Reports product detail responses held in the app's network cache, with the ASIN and "
            "the product title where the response carried one."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Rows come from NSURLCache entries for data.amazon.*/api/marketplaces/*/products/*. "
            "The ASIN and marketplace identifier are taken from the request URL. Response bodies "
            "are Snappy framed streams containing a multipart document; the module decodes them "
            "with a Snappy reader implemented in this file, then reads the part whose Type header "
            "ends in title/v1 for displayString. In the tested samples 7 of 22 responses contained "
            "only the product/v2 part and carried no title part at all, all with HTTP status 200, "
            "so those rows are reported with an empty title rather than skipped. Image Count is "
            "the number of physicalId values in the product-images part. A cached product response "
            "records that the app requested detail for that ASIN, which is not the same as the "
            "user opening the product page. Documents/asins/*.plist in the same container holds "
            "tens of thousands of ASINs and is a deep-link lookup table fetched from the server; "
            "it is not parsed here and must not be read as products the user viewed."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.amazon.AmazonUK/Cache.db*',),
        "output_types": ["standard"],
        "artifact_icon": "tag"
    },
    "amazon_delivery_location": {
        "name": "Amazon - Delivery Location",
        "description": (
            "Reports the delivery address label the app cached from the storefront location "
            "service."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Rows are parsed from JSON bodies cached in the app's NSURLCache for requests to "
            "*/portal-migration/hz/glow/get-location-label. The customerIntent object carries "
            "city, zipCode, state, countryCode and an addressSource value that is reported as "
            "stored. The values describe the delivery destination the storefront had selected for "
            "the session that made the request. They are not a device position fix and carry no "
            "coordinates. Page Type is the pageType parameter of the request URL, which records "
            "the app screen that triggered the lookup."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.amazon.AmazonUK/Cache.db*',),
        "output_types": ["standard"],
        "artifact_icon": "map-pin"
    },
    "amazon_network_cache": {
        "name": "Amazon - Network Cache",
        "description": "Reports the request URLs and entry times held in the app's network cache.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Reads the standard NSURLCache tables in "
            "Library/Caches/com.amazon.AmazonUK/Cache.db. time_stamp is stored by SQLite as UTC "
            "text. Response Size is the byte length of the stored body, which is not always the "
            "resource: image entries in the tested samples frequently hold a 36 byte token rather "
            "than image bytes, so a small size on an image URL means the bytes are not in this "
            "cache. The WAL sidecar is load bearing here, carrying entries absent from the "
            "committed file in both tested samples, so the path pattern picks up the sidecars."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/com.amazon.AmazonUK/Cache.db*',),
        "output_types": ["standard"],
        "artifact_icon": "globe"
    },
    "amazon_image_cache": {
        "name": "Amazon - Image Cache",
        "description": (
            "Reports the SSNAP image cache registry and the cached image files it points at, "
            "including cached files the registry does not reference."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Library/LocalDatabase/ssnapImageCacheRegistry.db records url, featureName, size, "
            "filePath, lastAccessed, expiryDate, lastModified and numHits per cached image. "
            "filePath is an absolute path carrying the container UUID of the acquiring device, so "
            "the file is resolved by file name inside Library/Caches/ssnap_image_cache. In the "
            "tested samples every registry row resolved to a file whose size matched the recorded "
            "size. lastAccessed and expiryDate decode as Unix milliseconds; lastModified is the "
            "HTTP Last-Modified header as stored. The cache directory also holds files the "
            "registry does not reference, which are reported with an empty URL so they are not "
            "lost. The directory also carries zero length files; those rows report the size and "
            "carry no media, since there are no bytes to render. numHits is the counter as "
            "stored and its increment rule is not documented."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/LocalDatabase/ssnapImageCacheRegistry.db*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/ssnap_image_cache/*',),
        "output_types": ["standard"],
        "artifact_icon": "image"
    },
    "amazon_metric_events": {
        "name": "Amazon - Metric Events",
        "description": (
            "Reports timestamped client metric events from the app's queued DCM batches."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "Batches under Library/METRICS_CRITICAL, METRICS_HIGH and METRICS_NORMAL are protocol "
            "buffers with no shipped descriptor, so the module walks the wire format directly. "
            "Field numbers are used positionally and no field is given a name the data does not "
            "supply: the reported attribute names are the key strings stored inside each event. "
            "The event timestamp is field 1 of each event, read as Unix milliseconds; that unit is "
            "corroborated by the batch file name, which is itself a Unix millisecond value. Across "
            "the 65 batches in the tested samples the file name was never earlier than the newest "
            "event it contains, and was within ten seconds of it on 45 of them; the rest were "
            "queued for longer before being written, the widest gap being about fifteen hours. "
            "Page Type, Sub Page Type, Ref Marker, Customer ID and Session ID are "
            "lifted from the event's own key strings where present and left empty otherwise. "
            "Remaining keys are joined into Attributes as stored. These batches are queued for "
            "upload, so their presence records what the client recorded, not what the server "
            "received. Other Amazon applications use the same metric format, so confirm the "
            "container the Source File belongs to before attributing a row to this app."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/METRICS_CRITICAL/*',
                  '*/mobile/Containers/Data/Application/*/Library/METRICS_HIGH/*',
                  '*/mobile/Containers/Data/Application/*/Library/METRICS_NORMAL/*',),
        "output_types": ["standard"],
        "artifact_icon": "activity"
    },
    "amazon_metric_batches": {
        "name": "Amazon - Metric Batch Context",
        "description": (
            "Reports the per-batch device, account and session context recorded in the app's "
            "queued DCM batches."),
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": (
            "One row per metric batch file. The context values are the key/value pairs the batch "
            "carries in field 4, reported under their own key names. Batch Time is taken from the "
            "batch file name, which is a Unix millisecond value. The user agent string carries an "
            "Amazon device serial and the app and OS versions in the form the client sent them. "
            "Event Count is the number of events the batch holds. See the Metric Events artifact "
            "for the format notes; the same caution applies that other Amazon applications write "
            "this format."),
        "paths": ('*/mobile/Containers/Data/Application/*/Library/METRICS_CRITICAL/*',
                  '*/mobile/Containers/Data/Application/*/Library/METRICS_HIGH/*',
                  '*/mobile/Containers/Data/Application/*/Library/METRICS_NORMAL/*',),
        "output_types": ["standard"],
        "artifact_icon": "smartphone"
    },
}


# ---------------------------------------------------------------------------
# Timestamp helpers.
#
# Unit is a property of the individual key or column, established by decoding the
# stored values against each candidate epoch and keeping the only reading that lands
# inside the app's observed lifetime. The app binary is not carried in a Data
# container, so no producing call site was available to read.
# ---------------------------------------------------------------------------

def _utc(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def _unix_seconds(value):
    """Unix epoch seconds to a UTC string, or '' when the value is not usable."""
    try:
        return _utc(UNIX_EPOCH + timedelta(seconds=float(value)))
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _unix_millis(value):
    """Unix epoch milliseconds to a UTC string, or '' when the value is not usable."""
    try:
        return _utc(UNIX_EPOCH + timedelta(milliseconds=float(value)))
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _cocoa_seconds(value):
    """Cocoa/Mac absolute seconds to a UTC string, or '' when the value is not usable."""
    try:
        return _utc(COCOA_EPOCH + timedelta(seconds=float(value)))
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


# ---------------------------------------------------------------------------
# Snappy reader.
#
# The product detail responses are served with Content-Encoding: snappy and stored in
# the cache still encoded. Format per Google's Snappy format description
# (framing format and compressed block format); implemented here so the module adds
# no dependency.
# ---------------------------------------------------------------------------

def _snappy_block(data):
    """Decompress one raw Snappy block."""
    out = bytearray()
    pos = 0
    expected = 0
    shift = 0
    while True:
        if pos >= len(data):
            raise ValueError('truncated Snappy length preamble')
        byte = data[pos]
        pos += 1
        expected |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            break
    while pos < len(data):
        tag = data[pos]
        kind = tag & 0x03
        if kind == 0:                                   # literal
            length = tag >> 2
            if length < 60:
                pos += 1
            else:
                width = length - 59
                pos += 1
                length = int.from_bytes(data[pos:pos + width], 'little')
                pos += width
            length += 1
            out += data[pos:pos + length]
            pos += length
            continue
        if kind == 1:                                   # 1 byte offset copy
            length = 4 + ((tag >> 2) & 0x07)
            offset = ((tag >> 5) << 8) | data[pos + 1]
            pos += 2
        elif kind == 2:                                 # 2 byte offset copy
            length = (tag >> 2) + 1
            offset = int.from_bytes(data[pos + 1:pos + 3], 'little')
            pos += 3
        else:                                           # 4 byte offset copy
            length = (tag >> 2) + 1
            offset = int.from_bytes(data[pos + 1:pos + 5], 'little')
            pos += 5
        if offset <= 0 or offset > len(out):
            raise ValueError('Snappy copy offset outside output')
        start = len(out) - offset
        for step in range(length):                      # may overlap, so copy byte wise
            out.append(out[start + step])
    if len(out) != expected:
        raise ValueError(f'Snappy length mismatch: {len(out)} decoded, {expected} declared')
    return bytes(out)


def _snappy_stream(data):
    """Decompress a Snappy framing-format stream."""
    out = bytearray()
    pos = 0
    while pos + 4 <= len(data):
        chunk_type = data[pos]
        chunk_len = int.from_bytes(data[pos + 1:pos + 4], 'little')
        pos += 4
        chunk = data[pos:pos + chunk_len]
        pos += chunk_len
        if chunk_type == 0x00:                          # compressed, 4 byte CRC first
            out += _snappy_block(chunk[4:])
        elif chunk_type == 0x01:                        # uncompressed, 4 byte CRC first
            out += chunk[4:]
        # 0xFF stream identifier and 0x80-0xFE skippable chunks carry no payload
    return bytes(out)


def _maybe_snappy(data):
    """Return the body decoded if it is a Snappy stream, otherwise unchanged."""
    if data[:4] == b'\xff\x06\x00\x00':
        try:
            return _snappy_stream(data)
        except (ValueError, IndexError) as err:
            logfunc(f'Amazon: could not decode a Snappy response body: {err}')
            return data
    return data


def _multipart_parts(body):
    """Yield (type, body) for each part of an Amazon multipart API response."""
    for chunk in re.split(rb'--[0-9a-fA-F-]{36}', body):
        head, _, part = chunk.partition(b'\r\n\r\n')
        if not part:
            head, _, part = chunk.partition(b'\n\n')
        if not part:
            continue
        match = re.search(rb'Type:\s*([\w.\-/]+)', head)
        yield (match.group(1).decode('utf-8', 'replace') if match else ''), part.strip()


# ---------------------------------------------------------------------------
# Protocol buffer reader for the DCM metric batches.
#
# No descriptor is shipped with the app, so the wire format is walked directly and
# field numbers are used positionally. Nothing here assigns a name to a field: the
# reported names are the key strings the batch itself stores.
# ---------------------------------------------------------------------------

def _read_varint(data, pos):
    value = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7
        if shift > 63:
            break
    raise ValueError('truncated varint')


def _read_fields(data):
    """Yield (field_number, wire_type, value) across one protobuf message."""
    pos = 0
    while pos < len(data):
        key, pos = _read_varint(data, pos)
        field, wire = key >> 3, key & 0x07
        if wire == 0:
            value, pos = _read_varint(data, pos)
        elif wire == 1:
            value, pos = data[pos:pos + 8], pos + 8
        elif wire == 2:
            length, pos = _read_varint(data, pos)
            value, pos = data[pos:pos + length], pos + length
        elif wire == 5:
            value, pos = data[pos:pos + 4], pos + 4
        else:
            raise ValueError(f'unsupported wire type {wire}')
        yield field, wire, value


def _kv_pairs(blob):
    """Read a repeated {1: key, 2: value} sub-message into a list of pairs."""
    key = value = ''
    for field, wire, raw in _read_fields(blob):
        if wire != 2:
            continue
        text = raw.decode('utf-8', 'replace')
        if field == 1:
            key = text
        elif field == 2:
            value = text
    return key, value


def _parse_metric_batch(data):
    """Return (batch_id, context pairs, events) for one DCM batch file."""
    batch_id = ''
    context = []
    events = []
    for field, wire, raw in _read_fields(data):
        if field == 1 and wire == 2:
            batch_id = raw.decode('utf-8', 'replace')
        elif field == 4 and wire == 2:
            key, value = _kv_pairs(raw)
            if key:
                context.append((key, value))
        elif field == 5 and wire == 2:
            timestamp = None
            program = event_name = ''
            attributes = []
            for sub, sub_wire, sub_raw in _read_fields(raw):
                if sub == 1 and sub_wire == 0:
                    timestamp = sub_raw
                elif sub == 2 and sub_wire == 2:
                    program = sub_raw.decode('utf-8', 'replace')
                elif sub == 3 and sub_wire == 2:
                    event_name = sub_raw.decode('utf-8', 'replace')
                elif sub == 4 and sub_wire == 2:
                    key, value = _kv_pairs(sub_raw)
                    if key:
                        attributes.append((key, value))
            events.append((timestamp, program, event_name, attributes))
    return batch_id, context, events


# ---------------------------------------------------------------------------
# Shared lookups
# ---------------------------------------------------------------------------

def _cache_databases(files_found):
    """Main Cache.db paths, with the WAL and shm sidecars filtered out."""
    return [f for f in files_found
            if os.path.basename(f) == 'Cache.db' and 'com.amazon.AmazonUK' in f]


def _registry_databases(files_found):
    return [f for f in files_found if os.path.basename(f) == 'ssnapImageCacheRegistry.db']


def _image_cache_files(files_found):
    """File name to found path for the on-disk SSNAP image cache."""
    found = {}
    for file_found in files_found:
        if f'ssnap_image_cache{os.sep}' in file_found or '/ssnap_image_cache/' in file_found:
            if os.path.isfile(file_found):
                found[os.path.basename(file_found)] = file_found
    return found


def _check_in_image(file_path, name):
    """Check in a cached image, skipping files that hold no bytes.

    The cache directory carries zero length files. Checking one in produces an empty
    media entry that renders as a broken image, so the row reports the size instead.
    """
    try:
        if os.path.getsize(file_path) == 0:
            return ''
    except OSError:
        return ''
    return check_in_media(file_path, name=name) or ''


def _image_url_index(files_found):
    """Map an Amazon image identifier to the SSNAP cache file name recorded for it.

    The registry's filePath column is an absolute path built on the acquiring device
    and carries that device's container UUID, so only its file name is usable here.
    """
    index = {}
    for db_path in _registry_databases(files_found):
        try:
            db = open_sqlite_db_readonly(db_path)
            rows = db.execute('SELECT url, filePath FROM FileCacheRegistry').fetchall()
            db.close()
        except sqlite3.Error as err:
            logfunc(f'Amazon: could not read the image cache registry {db_path}: {err}')
            continue
        for url, file_path in rows:
            if not url or not file_path:
                continue
            match = re.search(r'/images/[A-Za-z0-9]+/([^./]+)', url)
            if match:
                index.setdefault(match.group(1), os.path.basename(file_path))
    return index


def _cached_entries(db_path, url_like):
    """Rows of (request_key, time_stamp, body) for cache entries matching a pattern."""
    try:
        db = open_sqlite_db_readonly(db_path)
        db.text_factory = bytes
        rows = db.execute(
            'SELECT r.request_key, r.time_stamp, d.receiver_data '
            'FROM cfurl_cache_response r '
            'JOIN cfurl_cache_receiver_data d ON d.entry_ID = r.entry_ID '
            'WHERE r.request_key LIKE ? ORDER BY r.time_stamp DESC', (url_like,)).fetchall()
        db.close()
    except sqlite3.Error as err:
        logfunc(f'Amazon: could not read the network cache {db_path}: {err}')
        return []
    decoded = []
    for request_key, time_stamp, body in rows:
        decoded.append((
            request_key.decode('utf-8', 'replace') if isinstance(request_key, bytes) else request_key,
            time_stamp.decode('utf-8', 'replace') if isinstance(time_stamp, bytes) else str(time_stamp),
            body or b''))
    return decoded


# ---------------------------------------------------------------------------
# Account and app state
# ---------------------------------------------------------------------------

# Key, reported label, conversion. None means the stored value is reported unchanged.
_ACCOUNT_KEYS = (
    ('CMICustomerID', 'Customer ID', None),
    ('CMISessionID', 'Session ID', None),
    ('AnonymousCustomerId', 'Anonymous Customer ID', None),
    ('IsTeenAccount', 'Teen Account', None),
    ('AmazonMarketplace', 'Marketplace', None),
    ('kAMILocalizationSystemConfigDefaultKeyCountry', 'Localization Country', None),
    ('kAMILocalizationSystemConfigDefaultKeyLanguage', 'Localization Language', None),
    ('kAppleStorefrontCountryCode', 'Apple Storefront Country', None),
    ('AMIApplicationInformationImpl.LastRunAppVersion', 'Last Run App Version', None),
    ('kCurrentAppVersionKey', 'Current App Version', None),
    ('AMIUserDefaultsAppVersionKey', 'User Defaults App Version', None),
    ('SMASH_STORED_APP_VERSION_KEY', 'Stored App Version', None),
    ('SMASH_STORED_SYSTEM_VERSION_KEY', 'Stored System Version', None),
    ('SMASH_STORED_USER_AGENT_STRING_KEY', 'Stored User Agent', None),
    ('AmazonAd:userAgent', 'Advertising User Agent', None),
    ('AWPushNotificationsDeviceTokenKey', 'Push Notification Device Token', None),
    ('AWPushNotificationsAiIdKey', 'Push Notification AI ID', None),
    ('AWPushNotificationsAppIdKey', 'Push Notification App ID', None),
    ('kAWPushNotificationsEnabledOnDeviceStateKey', 'Push Notification Device State', None),
    ('AWPushNotificationsSequenceKey', 'Push Notification Sequence', None),
    ('SKADSPT_MSHOP_IDENTIFIER_FOR_VENDOR', 'Identifier For Vendor', None),
    ('CDVUUID', 'CDV UUID', None),
    ('BugsnagUserUserId', 'Bugsnag User ID', None),
    ('SyncPushStateBPTInstallUUID', 'Install UUID', None),
    ('AWApplicationDelegate.AppStartCount', 'App Start Count', None),
    ('AWApplicationDelegate.AppForegroundCount', 'App Foreground Count', None),
    ('AWApplicationDelegate.AppDeepLinkCount', 'App Deep Link Count', None),
    ('PamAppStartCounter', 'Pam App Start Counter', None),
    ('PamAppInstallDate', 'Pam App Install Date (as stored)', None),
    ('PamFirstAppStartDate', 'Pam First App Start Date (as stored)', None),
    ('PamAppCloseTimestamp', 'Pam App Close Timestamp (as stored)', None),
    ('SKADSPT_FIRST_UPDATE_TIMESTAMP', 'SKAdNetwork First Update (as stored)', None),
    ('SKADSPT_LAST_UPDATE_TIMESTAMP', 'SKAdNetwork Last Update (as stored)', None),
    ('kAMICartServiceCurrentCartCountCacheKey', 'Cached Cart Item Count', None),
    ('Preferences/TouchID/enabled', 'Biometric Unlock Enabled', None),
    ('TouchID/hasSucceeded', 'Biometric Unlock Has Succeeded', None),
    ('TouchID/mostRecentAttemptSucceeded', 'Biometric Most Recent Attempt Succeeded', None),
    ('CameraPermissionsDenied', 'Camera Permissions Denied', None),
    ('APSPermissionKey_permission_stylesnap_camera_permission', 'StyleSnap Camera Permission', None),
    ('APSPermissionKey_permission_credit_card_scan_camera_permission',
     'Credit Card Scan Camera Permission', None),
    ('AmazonPayEnabled', 'Amazon Pay Enabled', None),
    ('isInternationalShoppingMode', 'International Shopping Mode', None),
    ('a9vs_lens_last_used_mode_id', 'Camera Search Last Used Mode', None),
    ('AttestationState', 'Attestation State (as stored)', None),
    ('AWSignInInterstitialLastShownDate', 'Sign In Interstitial Last Shown', None),
    ('YOTooltipCacheShownLast', 'Your Orders Tooltip Last Shown', None),
    ('cxiRevertThresholdTimestampKey', 'CXI Revert Threshold', None),
    ('creation-date', 'Preferences Creation Date', None),
    ('expiration-date', 'Preferences Expiration Date', None),
    ('DCMArcusLastSyncedTimeKey', 'DCM Config Last Synced', _unix_millis),
    ('MinervaArcusLastSyncedTimeKey', 'Minerva Config Last Synced', _unix_millis),
    ('LocalSamplingKeyLastUpdatedTime', 'Local Sampling Key Last Updated', _unix_seconds),
    ('AmazonAd:DeviceInfoUpdateTimestampKey', 'Advertising Device Info Updated', _cocoa_seconds),
    ('AmazonAd:FetchConfigurationTimestampKey', 'Advertising Configuration Fetched', _cocoa_seconds),
    ('AmazonAd:IdentifyUserTimestampKey', 'Advertising Identify User', _cocoa_seconds),
    ('AmazonAd:LoginStatusChangeTimestampKey', 'Advertising Login Status Change', _cocoa_seconds),
    ('AmazonAd:SessionIdRegistrationTimestampKey', 'Advertising Session Registration', _cocoa_seconds),
    ('AmazonAd:UserSpecifiedMarketplaceKey', 'Advertising Marketplace', None),
    ('AmazonAd:SISDomainKey', 'Advertising SIS Domain', None),
    ('LastRefreshTime', 'Last Refresh Time (as stored)', None),
)

# Marketplace-scoped keys are stored as "<MARKETPLACE>/<key>".
_ACCOUNT_SCOPED_KEYS = (
    ('AWUser.MostRecentAuthenticatedAccountInMarketplace', 'Most Recent Authenticated Account'),
    ('AWUserKeyIsPrime', 'Prime'),
    ('AWUserKeyIsBusiness', 'Business Account'),
    ('AWUserKeyIsBusinessPrimeShipping', 'Business Prime Shipping'),
    ('AWUserKeyIsComplimentaryBusinessShipping', 'Complimentary Business Shipping'),
    ('AWUserStateStatus', 'User State Status (as stored)'),
)


def _render(value):
    if isinstance(value, datetime):
        return _utc(value if value.tzinfo else value.replace(tzinfo=timezone.utc))
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, bytes):
        return f'<{len(value)} bytes>'
    return str(value)


@artifact_processor
def amazon_account(context):
    """Reports selected account, marketplace, device and app-state preference values."""
    data_headers = ('Property', 'Value', 'Raw Value', SOURCE_FILE)
    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        if os.path.basename(file_found) != 'com.amazon.AmazonUK.plist':
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)

        for key, label, convert in _ACCOUNT_KEYS:
            if key not in plist:
                continue
            stored = plist[key]
            if convert:
                converted = convert(stored)
                data_list.append((label, converted or _render(stored),
                                  _render(stored) if converted else '', relative))
            else:
                data_list.append((label, _render(stored), '', relative))

        for key, label in _ACCOUNT_SCOPED_KEYS:
            for stored_key, stored in plist.items():
                if isinstance(stored_key, str) and stored_key.endswith('/' + key):
                    marketplace = stored_key.split('/', 1)[0]
                    data_list.append((f'{marketplace} - {label}', _render(stored), '', relative))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_profiles(context):
    """Reports Amazon account profiles and the account identifiers naming preference files."""
    data_headers = (
        ('Last Active', 'datetime'),
        ('Last Updated', 'datetime'),
        'Account ID',
        'Full Name',
        'Primary Account Claim',
        'Claim Type',
        'Marketplace',
        'Record Type',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''
    seen_accounts = set()

    for file_found in context.get_files_found():
        if os.path.basename(file_found) != 'manifest.json':
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as handle:
                manifest = json.load(handle)
        except (OSError, ValueError) as err:
            logfunc(f'Amazon: could not read the React Native storage manifest: {err}')
            continue
        if not isinstance(manifest, dict):
            continue
        # This manifest path is generic React Native storage, so only accept a file that
        # actually carries an Amazon account identifier.
        if 'amzn1.account.' not in json.dumps(manifest):
            continue
        source_path = source_path or file_found
        relative = context.get_relative_path(file_found)

        marketplace = ''
        profiles = {}
        try:
            root = json.loads(manifest.get('persist:root', '{}'))
            profiles = json.loads(root.get('pandaStore', '{}'))
            marketplace = json.loads(root.get('marketplaceStore', '{}')).get('marketplace', '')
        except (ValueError, AttributeError) as err:
            logfunc(f'Amazon: could not read the profile store: {err}')

        for account_id, record in (profiles.items() if isinstance(profiles, dict) else []):
            if not isinstance(record, dict):
                continue
            seen_accounts.add(account_id)
            data_list.append((
                _unix_millis(record.get('lastActive')),
                _unix_millis(record.get('lastUpdated')),
                record.get('accountId', account_id),
                record.get('fullName', ''),
                record.get('primaryAccountClaim', ''),
                record.get('primaryAccountClaimType', ''),
                marketplace,
                'Profile record',
                relative))

        # Accounts named only by a hamburger-menu key still evidence the account.
        for key in manifest:
            for match in re.finditer(r'(amzn1\.account\.[A-Z0-9]+)', str(key)):
                if match.group(1) not in seen_accounts:
                    seen_accounts.add(match.group(1))
                    data_list.append(('', '', match.group(1), '', '', '', '',
                                      'Referenced in app storage key', relative))

    for file_found in context.get_files_found():
        name = os.path.basename(file_found)
        if not (name.startswith('amzn1.account.') and name.endswith('.plist')):
            continue
        account_id = name[:-len('.plist')]
        if account_id in seen_accounts:
            continue
        seen_accounts.add(account_id)
        source_path = source_path or file_found
        data_list.append(('', '', account_id, '', '', '', '',
                          'Per-account preference file',
                          context.get_relative_path(file_found)))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_orders(context):
    """Reports orders and line items from the app's cached orders API response."""
    data_headers = (
        ('Order Date', 'datetime'),
        ('Cached', 'datetime'),
        'Order ID',
        'ASIN',
        'Quantity',
        ('Product Image', 'media'),
        'Adult Item',
        'Product Page URL',
        'Order Details URL',
        'Line Items In Order',
        'Request URL',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    files_found = context.get_files_found()
    image_index = _image_url_index(files_found)
    cache_files = _image_cache_files(files_found)

    for db_path in _cache_databases(files_found):
        for request_key, time_stamp, body in _cached_entries(db_path, '%/api/orders/v1%'):
            try:
                payload = json.loads(_maybe_snappy(body))
            except ValueError:
                logfunc(f'Amazon: an orders cache entry did not hold JSON: {request_key[:80]}')
                continue
            orders = payload.get('orderInfoList', {}).get('orderInfos', [])
            if not orders:
                continue
            source_path = source_path or db_path
            relative = context.get_relative_path(db_path)
            for order in orders:
                line_items = order.get('lineItemGroup', {}).get('lineItems', [])
                order_date = _unix_seconds(order.get('orderDate'))
                for item in line_items or [{}]:
                    media_ref = ''
                    image_url = item.get('imageUrl', '')
                    match = re.search(r'/images/[A-Za-z0-9]+/([^./]+)', image_url)
                    if match:
                        cache_name = image_index.get(match.group(1))
                        if cache_name and cache_name in cache_files:
                            media_ref = _check_in_image(
                                cache_files[cache_name],
                                f"{order.get('orderId', '')} {item.get('asin', '')}")
                    data_list.append((
                        order_date,
                        time_stamp,
                        order.get('orderId', ''),
                        item.get('asin', ''),
                        item.get('quantity', ''),
                        media_ref or '',
                        'Yes' if item.get('adult') else 'No',
                        item.get('detailsPageUrl', ''),
                        order.get('landingPageUrl', ''),
                        order.get('asinCounts', ''),
                        request_key,
                        relative))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Product lookups
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_products(context):
    """Reports cached product detail responses, with the ASIN and title where present."""
    data_headers = (
        ('Cached', 'datetime'),
        'ASIN',
        'Product Title',
        'Marketplace ID',
        'Image Count',
        'Response Parts',
        'Request URL',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    for db_path in _cache_databases(context.get_files_found()):
        entries = _cached_entries(db_path, '%/api/marketplaces/%/products/%')
        if not entries:
            continue
        source_path = source_path or db_path
        relative = context.get_relative_path(db_path)
        for request_key, time_stamp, body in entries:
            url_match = re.search(r'/marketplaces/([^/]+)/products/([A-Za-z0-9]+)', request_key)
            if not url_match:
                continue
            marketplace, asin = url_match.group(1), url_match.group(2)
            title = ''
            images = 0
            parts = []
            for part_type, part_body in _multipart_parts(_maybe_snappy(body)):
                if part_type:
                    parts.append(part_type)
                if part_type.endswith('title/v1'):
                    try:
                        title = json.loads(part_body).get('displayString', '')
                    except ValueError:
                        title = ''
                elif 'product-images' in part_type:
                    images = len(re.findall(rb'"physicalId"\s*:\s*"', part_body))
            # A response carrying no title part is still evidence the ASIN was requested.
            data_list.append((
                time_stamp, asin, title, marketplace,
                images or '', ', '.join(parts), request_key, relative))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Delivery location
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_delivery_location(context):
    """Reports the delivery address label cached from the storefront location service."""
    data_headers = (
        ('Cached', 'datetime'),
        'City',
        'Postal Code',
        'State',
        'Country',
        'Location Type (as stored)',
        'Address Source (as stored)',
        'Delivery Line 1',
        'Delivery Line 2',
        'Default Shipping Address',
        'Account Address',
        'Address ID',
        'Legacy Address ID',
        'Obfuscated ID',
        'Page Type',
        'Request URL',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    for db_path in _cache_databases(context.get_files_found()):
        entries = _cached_entries(db_path, '%get-location-label%')
        if not entries:
            continue
        source_path = source_path or db_path
        relative = context.get_relative_path(db_path)
        for request_key, time_stamp, body in entries:
            try:
                payload = json.loads(_maybe_snappy(body))
            except ValueError:
                continue
            if not isinstance(payload, dict):
                continue
            intent = payload.get('customerIntent') or {}
            page_type = ''
            page_match = re.search(r'[?&]pageType=([^&]+)', request_key)
            if page_match:
                page_type = page_match.group(1)
            data_list.append((
                time_stamp,
                intent.get('city') or '',
                intent.get('zipCode') or '',
                intent.get('state') or '',
                intent.get('countryCode') or '',
                intent.get('locationType') or '',
                intent.get('addressSource') or '',
                payload.get('deliveryLine1') or '',
                payload.get('deliveryLine2') or '',
                'Yes' if intent.get('isDefaultShippingAddress') else 'No',
                'Yes' if intent.get('isAccountAddress') else 'No',
                intent.get('addressId') or '',
                intent.get('legacyAddressId') or '',
                intent.get('obfuscatedId') or '',
                page_type,
                request_key,
                relative))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Network cache
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_network_cache(context):
    """Reports request URLs and entry times from the app's network cache."""
    data_headers = (
        ('Cached', 'datetime'),
        'Request URL',
        'Response Size',
        'Partition',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    for db_path in _cache_databases(context.get_files_found()):
        try:
            db = open_sqlite_db_readonly(db_path)
            db.text_factory = bytes
            rows = db.execute(
                'SELECT r.time_stamp, r.request_key, LENGTH(d.receiver_data), r.partition '
                'FROM cfurl_cache_response r '
                'LEFT JOIN cfurl_cache_receiver_data d ON d.entry_ID = r.entry_ID '
                'ORDER BY r.time_stamp DESC').fetchall()
            db.close()
        except sqlite3.Error as err:
            logfunc(f'Amazon: could not read the network cache {db_path}: {err}')
            continue
        if not rows:
            continue
        source_path = source_path or db_path
        relative = context.get_relative_path(db_path)
        for time_stamp, request_key, size, partition in rows:
            decode = lambda v: v.decode('utf-8', 'replace') if isinstance(v, bytes) else (
                '' if v is None else str(v))
            data_list.append((decode(time_stamp), decode(request_key),
                              '' if size is None else size, decode(partition), relative))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Image cache
# ---------------------------------------------------------------------------

@artifact_processor
def amazon_image_cache(context):
    """Reports the SSNAP image cache registry and the cached image files on disk."""
    data_headers = (
        ('Last Accessed', 'datetime'),
        ('Expiry', 'datetime'),
        'Last Modified (as stored)',
        ('Image', 'media'),
        'Image URL',
        'Feature Name',
        'Recorded Size',
        'Hits (as stored)',
        'Cache File Name',
        'Recorded File Path',
        'Registry Entry',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    files_found = context.get_files_found()
    cache_files = _image_cache_files(files_found)
    linked = set()

    for db_path in _registry_databases(files_found):
        try:
            db = open_sqlite_db_readonly(db_path)
            rows = db.execute(
                'SELECT lastAccessed, expiryDate, lastModified, url, featureName, size, '
                'numHits, filePath FROM FileCacheRegistry ORDER BY lastAccessed DESC').fetchall()
            db.close()
        except sqlite3.Error as err:
            logfunc(f'Amazon: could not read the image cache registry {db_path}: {err}')
            continue
        if not rows:
            continue
        source_path = source_path or db_path
        relative = context.get_relative_path(db_path)
        for last_accessed, expiry, modified, url, feature, size, hits, file_path in rows:
            cache_name = os.path.basename(file_path or '')
            linked.add(cache_name)
            media_ref = ''
            if cache_name in cache_files:
                media_ref = _check_in_image(cache_files[cache_name], cache_name)
            data_list.append((
                _unix_millis(last_accessed), _unix_millis(expiry), modified or '',
                media_ref, url or '', feature or '', size if size is not None else '',
                hits if hits is not None else '', cache_name, file_path or '',
                'Yes', relative))

    # Cached files the registry does not reference are reported rather than dropped.
    for cache_name, file_found in sorted(cache_files.items()):
        if cache_name in linked:
            continue
        source_path = source_path or file_found
        media_ref = _check_in_image(file_found, cache_name)
        data_list.append(('', '', '', media_ref, '', '', os.path.getsize(file_found), '',
                          cache_name, '', 'No', context.get_relative_path(file_found)))

    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Metric events and batches
# ---------------------------------------------------------------------------

_METRIC_DIRS = ('METRICS_CRITICAL', 'METRICS_HIGH', 'METRICS_NORMAL')

# Event attribute keys promoted to their own column. The names are the key strings the
# batch itself stores; nothing here renames or reinterprets them.
_PROMOTED = ('page-type', 'sub-page-type', 'ref-override', 'hitType', 'LineOfBusiness',
             'nonAnonymousCustomerId', 'nonAnonymousSessionId')


def _metric_files(files_found):
    found = []
    for file_found in files_found:
        parent = os.path.basename(os.path.dirname(file_found))
        if parent in _METRIC_DIRS and os.path.isfile(file_found):
            found.append(file_found)
    return sorted(found)


@artifact_processor
def amazon_metric_events(context):
    """Reports timestamped client metric events from the app's queued DCM batches."""
    data_headers = (
        ('Timestamp', 'datetime'),
        'Program',
        'Event',
        'Page Type',
        'Sub Page Type',
        'Ref Marker',
        'Hit Type',
        'Line Of Business',
        'Customer ID',
        'Session ID',
        'Attributes',
        'Batch File Name',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    for file_found in _metric_files(context.get_files_found()):
        try:
            with open(file_found, 'rb') as handle:
                _, _, events = _parse_metric_batch(handle.read())
        except (OSError, ValueError, IndexError) as err:
            logfunc(f'Amazon: could not read the metric batch '
                    f'{context.get_relative_path(file_found)}: {err}')
            continue
        if not events:
            continue
        source_path = source_path or file_found
        relative = context.get_relative_path(file_found)
        batch_name = os.path.basename(file_found)
        for timestamp, program, event_name, attributes in events:
            promoted = {key: value for key, value in attributes if key in _PROMOTED}
            remainder = '; '.join(f'{key}={value}' for key, value in attributes
                                  if key not in _PROMOTED)
            data_list.append((
                _unix_millis(timestamp) if timestamp is not None else '',
                program, event_name,
                promoted.get('page-type', ''),
                promoted.get('sub-page-type', ''),
                promoted.get('ref-override', ''),
                promoted.get('hitType', ''),
                promoted.get('LineOfBusiness', ''),
                promoted.get('nonAnonymousCustomerId', ''),
                promoted.get('nonAnonymousSessionId', ''),
                remainder, batch_name, relative))

    return data_headers, data_list, source_path


@artifact_processor
def amazon_metric_batches(context):
    """Reports per-batch device, account and session context from the DCM batches."""
    data_headers = (
        ('Batch Time', 'datetime'),
        'Batch ID',
        'Customer ID',
        'Session ID',
        'Marketplace ID',
        'Country Of Residence',
        'Device Language',
        'Device Model',
        'OS Version',
        'User Agent',
        'Event Count',
        'Batch File Name',
        SOURCE_FILE,
    )
    data_list = []
    source_path = ''

    for file_found in _metric_files(context.get_files_found()):
        try:
            with open(file_found, 'rb') as handle:
                batch_id, pairs, events = _parse_metric_batch(handle.read())
        except (OSError, ValueError, IndexError) as err:
            logfunc(f'Amazon: could not read the metric batch '
                    f'{context.get_relative_path(file_found)}: {err}')
            continue
        if not batch_id and not pairs:
            continue
        source_path = source_path or file_found
        context_values = dict(pairs)
        batch_name = os.path.basename(file_found)
        # The batch file name is itself a Unix millisecond value.
        batch_time = _unix_millis(batch_name) if batch_name.isdigit() else ''
        data_list.append((
            batch_time, batch_id,
            context_values.get('CustomerId', ''),
            context_values.get('Session', ''),
            context_values.get('MarketplaceID', ''),
            context_values.get('countryOfResidence', ''),
            context_values.get('deviceLanguage', ''),
            context_values.get('model', ''),
            context_values.get('softwareVersion', ''),
            context_values.get('HTTP_USER_AGENT', ''),
            len(events), batch_name, context.get_relative_path(file_found)))

    return data_headers, data_list, source_path
