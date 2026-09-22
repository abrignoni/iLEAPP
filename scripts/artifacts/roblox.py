__artifacts_v2__ = {
    "robloxAccount": {
        "name": "Roblox - Account",
        "description": "Account identity and login state recorded by the Roblox iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the client's LocalStorage key value store, appStorage.json, paired with "
                 "com.roblox.robloxmobile.plist from the same app container. Both stores carry the "
                 "signed in account, so each is reported and a disagreement between them stays "
                 "visible: appStorage.json holds User ID and Display Name, and the preferences plist "
                 "holds Last User ID Logged In and Last User Logged In. On the one device tested the "
                 "two agreed on the user id, and the display name in appStorage.json equalled the "
                 "user name in the plist. First Launch and Install Date come from the AppsFlyer SDK "
                 "keys in the preferences plist and are written as a local time with an explicit UTC "
                 "offset, which is converted here; they record when the SDK first ran, which is not "
                 "necessarily when the account was created. Login Expiry is stored as an eight byte "
                 "little endian double of Unix seconds and is a future expiry rather than a login "
                 "event. Contact Import Sync is stored as the user id, a colon, and Unix "
                 "milliseconds; that the part before the colon is the user id was measured on the one "
                 "device tested and is not established for other devices, so the timestamp is read "
                 "from the part after the colon only. Membership is reported as stored: no mapping "
                 "for the integer was recoverable, because the client is closed source and the tested "
                 "extraction carries no documentation of it. Client Version is the version the "
                 "preferences plist records as installed; on the device tested it equalled the "
                 "CFBundleShortVersionString of the Roblox application bundle on the same image. "
                 "PreviousAccountsList was present and "
                 "empty on the device tested, so no previous account rows exist here and no artifact "
                 "reports them. Field mapping was done against a single private sample; no sample "
                 "data is recorded for it. An extraction can hold more than one Roblox container, so "
                 "every container is reported rather than the first one found, and each key value "
                 "store is paired with the preferences plist from its own container. A store that "
                 "carries none of the client's own marker keys is skipped and logged, so another "
                 "app's file of the same name cannot be reported as Roblox. That skip was exercised "
                 "against a constructed store of the same name holding none of those keys, which "
                 "produced no row; no tested extraction carries such a file.",
        "paths": ('*/Library/Application Support/LocalStorage/appStorage.json',
                  '*/Library/Preferences/com.roblox.robloxmobile.plist'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "robloxAppLaunches": {
        "name": "Roblox - App Launches",
        "description": "Per launch client log files written by the Roblox iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Roblox",
        "notes": "One row per client log file in Library/Logs/Roblox. The client names each file with "
                 "the client version, a UTC timestamp, the log type and a short identifier, and Log "
                 "Start is read from that name. The first timestamped line inside the file carries "
                 "its own time and is reported beside it so the two can be compared. A log file "
                 "records that the client started, not that a person opened it. The client keeps only "
                 "the most recent files, each named with a _last suffix, so the rows here are a "
                 "window rather than a full launch history: the device tested held two Player log "
                 "files, both written on one day. Log Type is reported as stored so a client "
                 "that wrote another kind of log would show it. Field mapping was done against a "
                 "single private sample; no sample data is recorded for it. Files whose name does not "
                 "match the client's naming pattern are still reported, with the name derived fields "
                 "left blank, rather than being dropped, which was exercised against a constructed "
                 "log rather than against the device tested, where both files matched the pattern.",
        "paths": ('*/Library/Logs/Roblox/*.log',),
        "output_types": "standard",
        "artifact_icon": "clock"
    },
    "robloxGameActivity": {
        "name": "Roblox - Game Activity",
        "description": "Experience joins and game server connections from the Roblox iOS client logs",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the client logs in Library/Logs/Roblox. A join is assembled from two "
                 "lines the client writes together: the join line, which carries the game job id, the "
                 "place id and the server address, and the game_join_loadtime report line, which "
                 "carries the play session id, the user id, the universe id, the place id, the "
                 "referral page and a client time. The analytics session id line earlier in the same "
                 "log supplies Session ID. Roblox's own vocabulary is kept: a place id identifies a "
                 "place, a universe id identifies the experience that contains it, and a game job id "
                 "identifies the running server instance. Join Time is the ISO 8601 UTC stamp the "
                 "client writes on the line; Client Time is the clienttime value on the report line, "
                 "which is Unix seconds. The two are reported separately because they do not always "
                 "agree: on the five joins of the device tested they matched within a second on "
                 "three, and clienttime ran 420 seconds ahead of the line stamp on the other two, "
                 "which were the second and third joins of one session. Neither is a substitute for "
                 "the other and the line stamp is the one the client wrote when it logged the join. "
                 "Referral Page is reported as stored and was empty on every row of the device "
                 "tested. User ID and Client Version each held one value on every row of that device, "
                 "because it carried one signed in account and one installed client; both are kept "
                 "because an extraction holding a second account or a client update would differ. "
                 "Client Version here comes from the log file name, which writes the version in a "
                 "four part form, where the installed bundle and the preferences plist write three. "
                 "Server Address is the address the client connected to, not the device's own "
                 "address, and on the device tested every one was a private range address, which is "
                 "the Roblox server's internal address as the client logged it. A report line with no "
                 "join line, and a join line with no report line, are each reported with the missing "
                 "side blank rather than dropped, so a partial record stays visible. Every join on the "
                 "device tested carried both lines, so each unpaired case was exercised against a "
                 "constructed log instead. Field mapping "
                 "was done against a single private sample; no sample data is recorded for it. The "
                 "client retains only its most recent logs, so an absent join is not evidence that no "
                 "join happened.",
        "paths": ('*/Library/Logs/Roblox/*.log',),
        "output_types": "standard",
        "artifact_icon": "player-play"
    },
    "robloxCachedAssets": {
        "name": "Roblox - Cached Assets",
        "description": "Content cache index the Roblox iOS client keeps in rbx-storage.db",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "Roblox",
        "notes": "One row per entry in the files table of rbx-storage.db, the client's content cache "
                 "index. Last Access is the atime column, which is Unix milliseconds. Expires is the "
                 "ttl column, Unix seconds, and is left blank where it is zero. Asset URL is read "
                 "from the cached entry itself: an entry begins with the ASCII magic RBXH, a four "
                 "byte little endian version, and a four byte little endian length, followed by that "
                 "many bytes of URL. That layout is derived from the data rather than from any "
                 "published specification, because the client is closed source, and it was validated "
                 "on the device tested by requiring the length field to stay inside the entry and the "
                 "bytes it covers to be printable and to begin with http: of 8,191 rows, 1,977 held "
                 "no inline content, 3,836 yielded a URL this way, 2,267 carried the magic with a "
                 "zero length field, and 111 did not carry the magic. Rows with no URL are reported "
                 "with the column blank rather than dropped, because the access time and hit count "
                 "are still evidence. The URLs are signed content delivery URLs and carry the "
                 "client's own expiry and signature parameters, reported as stored. A cached entry "
                 "records that the client fetched the content, not that a person saw it. The score "
                 "column is not reported: on the device tested it tracked the access time to within "
                 "milliseconds on every row, so it would be a second copy of a column already shown. "
                 "Field mapping was done against a single private sample; no sample data is recorded "
                 "for it.",
        "paths": ('*/Library/Application Support/rbx-storage.db*',),
        "output_types": "standard",
        "artifact_icon": "package"
    },
}

import datetime
import json
import os
import re
import struct

from scripts.ilapfuncs import (artifact_processor, get_plist_file_content,
                               get_sqlite_db_records, convert_unix_ts_to_utc, logfunc)

# Keys the Roblox client writes into its own appStorage.json. A file of that name in a
# container holding none of these is not this client's, and is skipped rather than reported.
MARKER_KEYS = ('RobloxLocaleId', 'BrowserTrackerId', 'AppInstallationId',
               'PlayerHydrationSignature', 'PreviousAccountsList')

# 2.738.0.1390_20260912T081159Z_Player_43885_last.log
LOG_NAME = re.compile(r'^(?P<version>[\d.]+)_(?P<stamp>\d{8}T\d{6}Z)_'
                      r'(?P<logtype>[A-Za-z]+)_(?P<ident>[^_]+)_last\.log$')
LINE_TIME = re.compile(r'^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)')
JOIN_LINE = re.compile(r"! Joining game '(?P<jobid>[0-9a-fA-F-]{36})' "
                       r"place (?P<placeid>\d+) at (?P<server>[0-9a-fA-F.:]+)")
LOADTIME_LINE = re.compile(r'Report game_join_loadtime:\s*(?P<body>.+)$')
SESSION_LINE = re.compile(r'AnalyticsSessionId is (?P<sid>[0-9a-fA-F-]{36})')

RBXH_MAGIC = b'RBXH'


def _container_of(path):
    """The app data container a staged file sits in, or its parent directory."""
    found = re.match(r'(?P<root>.*/Data/Application/[^/]+)/', path.replace('\\', '/'))
    if found:
        return found.group('root')
    return os.path.dirname(path.replace('\\', '/'))


def _iso_to_utc(stamp):
    """ISO 8601 UTC as the client writes it, to an aware datetime."""
    try:
        return datetime.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _name_stamp_to_utc(stamp):
    """The 20260912T081159Z form used in log file names."""
    try:
        return datetime.datetime.strptime(stamp, '%Y%m%dT%H%M%SZ').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _appsflyer_to_utc(value):
    """2026-09-12_100634+0200, a local time carrying its own offset."""
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d_%H%M%S%z').astimezone(
            datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _double_to_utc(value):
    """Eight bytes of little endian double holding Unix seconds."""
    if not isinstance(value, (bytes, bytearray)) or len(value) != 8:
        return ''
    try:
        return convert_unix_ts_to_utc(struct.unpack('<d', bytes(value))[0])
    except (struct.error, ValueError, OverflowError, OSError):
        return ''


def _ms_to_utc(value):
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (ValueError, TypeError, OverflowError, OSError):
        return ''


def _roblox_stores(context):
    """Group the client's own key value stores and preference plists by container."""
    stores = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        if name not in ('appStorage.json', 'com.roblox.robloxmobile.plist'):
            continue
        entry = stores.setdefault(_container_of(file_found), {})
        if name == 'appStorage.json':
            entry['storage_path'] = file_found
        else:
            entry['prefs_path'] = file_found
    return stores


def _read_storage(path):
    """appStorage.json, confirmed to be this client's by its own marker keys."""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            loaded = json.load(handle)
    except (OSError, ValueError) as error:
        logfunc(f'Roblox: could not read {os.path.basename(path)}: {error}')
        return None
    if not isinstance(loaded, dict):
        logfunc(f'Roblox: {os.path.basename(path)} is not a key value store, skipped')
        return None
    if not any(key in loaded for key in MARKER_KEYS):
        logfunc(f'Roblox: {os.path.basename(path)} carries none of the client\'s keys, skipped')
        return None
    return loaded


@artifact_processor
def robloxAccount(context):
    data_headers = (
        ('First Launch', 'datetime'),
        ('Install Date', 'datetime'),
        ('Login Expiry', 'datetime'),
        ('Contact Import Sync', 'datetime'),
        'User ID',
        'Display Name',
        'Last User ID Logged In',
        'Last User Logged In',
        'Under 13',
        'Membership (as stored)',
        'Has Subscription',
        'Country Code',
        'Locale',
        'Client Version',
        'App Installation ID',
        'Browser Tracker ID',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_roblox_stores(context).items()):
        storage_path = entry.get('storage_path')
        prefs_path = entry.get('prefs_path')
        storage = _read_storage(storage_path) if storage_path else None
        prefs = get_plist_file_content(prefs_path) if prefs_path else {}
        if not isinstance(prefs, dict):
            prefs = {}
        if storage is None and not prefs:
            continue
        if storage is None:
            # A preferences plist named for this client, with no key value store beside it.
            storage = {}
            if 'LastUserIDLoggedIn' not in prefs:
                continue

        sync_value = str(storage.get('ContactImporterSyncTimestamp') or '')
        sync_time = _ms_to_utc(sync_value.rpartition(':')[2]) if ':' in sync_value else ''

        data_list.append((
            _appsflyer_to_utc(prefs.get('AppsFlyerFirstLaunchDate')),
            _appsflyer_to_utc(prefs.get('AppsFlyerInstallDate')),
            _double_to_utc(prefs.get('LastSuccessfulLoginExpectedExpiration')),
            sync_time,
            storage.get('UserId', ''),
            storage.get('DisplayName', ''),
            prefs.get('LastUserIDLoggedIn', ''),
            prefs.get('LastUserLoggedIn', ''),
            storage.get('IsUnder13', ''),
            storage.get('Membership', ''),
            storage.get('HasRobloxSubscription', ''),
            storage.get('CountryCode', ''),
            storage.get('RobloxLocaleId', ''),
            prefs.get('RBLatestVersionInstalled', ''),
            storage.get('AppInstallationId', ''),
            storage.get('BrowserTrackerId', ''),
            context.get_relative_path(storage_path or prefs_path),
        ))
        for path in (storage_path, prefs_path):
            if path:
                source_paths.append(path)

    return data_headers, data_list, '\n'.join(source_paths)


def _client_logs(context):
    for file_found in sorted(str(path) for path in context.get_files_found()):
        if file_found.replace('\\', '/').endswith('.log') and '/Logs/Roblox/' in \
                file_found.replace('\\', '/'):
            yield file_found


def _read_log(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            return handle.read().splitlines()
    except OSError as error:
        logfunc(f'Roblox: could not read {os.path.basename(path)}: {error}')
        return None


@artifact_processor
def robloxAppLaunches(context):
    data_headers = (
        ('Log Start', 'datetime'),
        ('First Line Time', 'datetime'),
        'Client Version',
        'Log Type',
        'Log Identifier',
        'Lines',
        'Source File',
    )
    data_list = []
    source_paths = []

    for file_found in _client_logs(context):
        lines = _read_log(file_found)
        if lines is None:
            continue
        name = os.path.basename(file_found.replace('\\', '/'))
        found = LOG_NAME.match(name)

        first_line_time = ''
        for line in lines:
            found_time = LINE_TIME.match(line)
            if found_time:
                first_line_time = _iso_to_utc(found_time.group('stamp'))
                break

        data_list.append((
            _name_stamp_to_utc(found.group('stamp')) if found else '',
            first_line_time,
            found.group('version') if found else '',
            found.group('logtype') if found else '',
            found.group('ident') if found else '',
            len(lines),
            context.get_relative_path(file_found),
        ))
        source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)


def _report_fields(body):
    fields = {}
    for part in body.split(','):
        key, sep, value = part.partition(':')
        if sep:
            fields[key.strip()] = value.strip()
    return fields


@artifact_processor
def robloxGameActivity(context):
    data_headers = (
        ('Join Time', 'datetime'),
        ('Client Time', 'datetime'),
        'Place ID',
        'Universe ID',
        'User ID',
        'Game Job ID',
        'Server Address',
        'Session ID',
        'Referral Page',
        'Join Load Time (s)',
        'Client Version',
        'Source File',
    )
    data_list = []
    source_paths = []

    for file_found in _client_logs(context):
        lines = _read_log(file_found)
        if lines is None:
            continue
        name = os.path.basename(file_found.replace('\\', '/'))
        found_name = LOG_NAME.match(name)
        version = found_name.group('version') if found_name else ''
        relative = context.get_relative_path(file_found)

        session_id = ''
        pending = []      # joins seen with no report line yet
        rows = 0

        for line in lines:
            stamp = ''
            found_time = LINE_TIME.match(line)
            if found_time:
                stamp = _iso_to_utc(found_time.group('stamp'))

            found = SESSION_LINE.search(line)
            if found:
                session_id = found.group('sid')

            found = JOIN_LINE.search(line)
            if found:
                pending.append({'stamp': stamp, 'jobid': found.group('jobid'),
                                'placeid': found.group('placeid'),
                                'server': found.group('server')})
                continue

            found = LOADTIME_LINE.search(line)
            if not found:
                continue
            fields = _report_fields(found.group('body'))
            placeid = fields.get('placeid', '')

            # Pair with the most recent unmatched join for the same place. The client
            # writes the two lines together, but a report can arrive with no join line.
            join = {}
            for index in range(len(pending) - 1, -1, -1):
                if pending[index]['placeid'] == placeid or not placeid:
                    join = pending.pop(index)
                    break

            data_list.append((
                join.get('stamp', ''),
                convert_unix_ts_to_utc(fields['clienttime']) if fields.get('clienttime') else '',
                placeid or join.get('placeid', ''),
                fields.get('universeid', ''),
                fields.get('userid', ''),
                join.get('jobid', ''),
                join.get('server', ''),
                fields.get('sid', '') or session_id,
                fields.get('referral_page', ''),
                fields.get('join_time', ''),
                version,
                relative,
            ))
            rows += 1

        # A join the client never reported on is still a join.
        for join in pending:
            data_list.append((join['stamp'], '', join['placeid'], '', '', join['jobid'],
                              join['server'], session_id, '', '', version, relative))
            rows += 1

        if rows:
            source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)


def _rbxh_url(content):
    """The source URL an RBXH cache entry carries, or '' when it holds none.

    Layout derived from the cached entries themselves: the ASCII magic, a four byte
    little endian version, a four byte little endian URL length, then the URL.
    """
    if not content or len(content) < 12 or not bytes(content[:4]) == RBXH_MAGIC:
        return ''
    try:
        length = struct.unpack_from('<I', content, 8)[0]
    except struct.error:
        return ''
    if length == 0 or 12 + length > len(content):
        return ''
    url = bytes(content[12:12 + length])
    if not url.startswith(b'http') or not all(32 <= byte < 127 for byte in url):
        return ''
    return url.decode('ascii')


@artifact_processor
def robloxCachedAssets(context):
    data_headers = (
        ('Last Access', 'datetime'),
        ('Expires', 'datetime'),
        'Asset URL',
        'Size (bytes)',
        'Hits',
        'Category',
        'Asset ID',
        'Source File',
    )
    data_list = []
    source_paths = []

    for file_found in sorted(str(path) for path in context.get_files_found()):
        if not file_found.replace('\\', '/').endswith('rbx-storage.db'):
            continue
        query = 'SELECT id, content, size, hits, atime, category, ttl FROM files'
        rows = 0
        for row in get_sqlite_db_records(file_found, query):
            asset_id = row[0]
            if isinstance(asset_id, (bytes, bytearray)):
                asset_id = bytes(asset_id).hex()
            data_list.append((
                _ms_to_utc(row[4]),
                convert_unix_ts_to_utc(row[6]) if row[6] else '',
                _rbxh_url(row[1]),
                row[2],
                row[3],
                row[5],
                asset_id,
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)
