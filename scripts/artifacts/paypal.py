"""PayPal (com.yourcompany.PPClient): the small set of stores that exist on the device.

In the five full file system installs examined (app versions 8.98 to 8.107), no readable local store
held a transaction history, contact list, balance or session token. What was readable is
account-identity preferences, dated preference keys, a security SDK log, a network cache of
telemetry requests, a queue of unsent analytics events and, in one install, an analytics SDK
session table. Absence from these installs is not shown to hold for every app version.
The Notes of each artifact say which store it reads and what it does not cover.
"""

__artifacts_v2__ = {
    "paypalRememberedAccount": {
        "name": "PayPal - Remembered Account",
        "description": "The account the app remembers for sign-in, from the shared app-group preferences.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from the RememberedUserV1 key of group.com.yourcompany.PPClient.plist, a keyed "
                 "archive. Each field is shown as stored; Account Type is the stored integer and its "
                 "meaning is not established. Fields absent from an archive are blank: in the tested "
                 "samples the photo URL and the phone-password flag were each present in only some of "
                 "them. Phone-Password Login Flag is blank when the archive has no phonePasswordLoginAccount "
                 "entry: it was present in 1 of the 4 archives found, so the column is empty on most "
                 "rows. The presence of the key does not show that anyone signed in, or when. No "
                 "transaction, balance or contact record was found in this file or in any other "
                 "readable store of the five installs examined. "
                 "Account Info (Documents/com.paypal.ios.AccountInfo) is a high-entropy blob (7.88 to "
                 "7.94 bits per byte) in the 4 tested installs that had it and is not decoded.",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.yourcompany.PPClient.plist",),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 1 row",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 1 row",
            "lab_ffs_ios26_2": "iOS 26.2 | 1 row",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 1 row",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 0 rows, no RememberedUserV1 key (the group preferences hold a logout key)",
        },
    },
    "paypalAccountKeys": {
        "name": "PayPal - Per-Account Preference Keys",
        "description": "Preference keys that carry an account identifier or e-mail address in their name.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from com.yourcompany.PPClient.plist. The key suffix (or prefix, for the e-mail form) "
                 "is shown as Account Key. Values are as stored. A key naming an account shows that the "
                 "app wrote a setting for that account key on this install; it does not show that the "
                 "account was signed in. Absence of these keys is not evidence that only one account was "
                 "used. The push notification key stores one value per notification channel, "
                 "shown as one row each. Account Key and Value held one value on every row of the install "
                 "that had a single account key (every stored channel value was true); that is the data, "
                 "not a derivation that did not run.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Preferences/com.yourcompany.PPClient.plist",),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 2 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 8 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 1 row",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 0 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 9 rows",
        },
    },
    "paypalDatedKeys": {
        "name": "PayPal - Dated Preference Keys",
        "description": "Date-typed keys of the app and app-group preferences, and the Kronos clock reference.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "One row per key whose stored type is a date, from com.yourcompany.PPClient.plist and "
                 "group.com.yourcompany.PPClient.plist, shown as stored (a plist date is UTC). The key "
                 "name is shown unchanged; the event each date records is not established by this "
                 "artifact. A preference key holds one value, so each date is the latest write to that "
                 "key, not a history. KronosStableTime.Timestamp is read as Unix seconds: in two tested "
                 "samples it fell within minutes of the last entry of the Thales SDK log of the same "
                 "container, which is an observation, not a documented meaning.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Preferences/com.yourcompany.PPClient.plist",
                  "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.yourcompany.PPClient.plist"),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 9 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 13 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 6 rows",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 7 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 8 rows",
        },
    },
    "paypalAppSettings": {
        "name": "PayPal - App Settings and Version Markers",
        "description": "Consent, push opt-in, locale and per-version first-launch markers from the app preferences.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "A curated set of keys from com.yourcompany.PPClient.plist and "
                 "group.com.yourcompany.PPClient.plist, shown by key name with the stored value. "
                 "appLaunchedFirstTime:<version> keys name the app versions that have started on this "
                 "install; the key carries no time, so the list is not an upgrade timeline, and a "
                 "version missing from it is not shown never to have run. Direct-deposit keys are "
                 "reported only as present, with whether the stored text is empty; they were empty in "
                 "the one tested install that had them. The many remote-configuration and feature-flag keys "
                 "(RCSDefault-*, kElmoSavedCacheKey, isPasskey* and similar) are server supplied and "
                 "are not reported. OptInData values pn_sync_time and pn_prev_sync_at are text with no "
                 "time zone.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Preferences/com.yourcompany.PPClient.plist",
                  "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.yourcompany.PPClient.plist"),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 46 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 62 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 26 rows",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 26 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 28 rows",
        },
    },
    "paypalSecuritySdkStarts": {
        "name": "PayPal - Security SDK Start Records",
        "description": "Start records of the Thales security SDK log kept in the app container.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from Library/Application Support/Thales-v2/slog-TSH-*.log, accepted only in a "
                 "container whose .com.apple.mobile_container_manager.metadata.plist names "
                 "com.yourcompany.PPClient. One row per line tagged SDKV, which carries the SDK build; "
                 "the time is the UTC stamp at the start of the line. SDK Build, OS Version (log header) and Device Model (log header) held one value on every row of "
                 "most tested logs; OS Version and Device Model come from the first line of the log and "
                 "repeat down its rows, and they are kept because that line is the only place the log "
                 "records them. The first line also holds the app name and a number whose meaning is not "
                 "established; neither is shown. This artifact does not claim that each row is an app launch. The log is a rolling file: its first entry is not the install date and a "
                 "quiet period is not shown to have had no use. Other record tags in the file "
                 "(LPIS, LPIE, LPIC, storage) are internal SDK traces and are not reported.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Application Support/Thales-v2/slog-TSH-*",
                  "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist"),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 5 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 89 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 8 rows",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 4 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 10 rows",
        },
    },
    "paypalCachedRequests": {
        "name": "PayPal - Cached Network Requests",
        "description": "Host and path of requests in the app's URL cache, with the fields of its statistics beacons.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from Library/Caches/com.yourcompany.PPClient/Cache.db (table "
                 "cfurl_cache_response). Cached Time is when the response was cached. Only the host and "
                 "path are shown, never the query or any body. For the *.stats.paypal.com/counter*.cgi "
                 "requests the query fields p, i, t and a are shown as stored: t read as Unix seconds "
                 "matched the cache time to within 2 seconds on every beacon of the tested samples, "
                 "and i held a private (RFC 1918) IPv4 address on every beacon; what p and a mean is "
                 "not established. In the tested samples the cache held telemetry, advertising "
                 "attribution and static-resource requests; none held a transaction, contact or "
                 "balance response. The cache is size-limited and rewritten by the system, so absence "
                 "of a request is not evidence the app did not send it. A second cache "
                 "(Library/Caches/CustomCache/Cache.db) held only two address-reference-data requests "
                 "and is not reported.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/com.yourcompany.PPClient/Cache.db*",),
        "output_types": "standard",
        "artifact_icon": "world",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 192 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 388 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 0 rows, no Cache.db in the container",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 54 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 101 rows",
        },
    },
    "paypalAnalyticsEvents": {
        "name": "PayPal - Queued Analytics Events",
        "description": "Events in the app's analytics queue database, with page, flow, network and sign-in fields.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from Library/Caches/com.paypal.lighthouseanalytics/lighthouseanalytics.db, table "
                 "events. Event Time is event_ts read as Unix seconds. Fields come from the JSON in "
                 "event_payload, falling back to original_event; a field absent from both is blank. "
                 "Dispatch Status and Dispatch Tries are as stored (every row of the tested samples "
                 "held -1 and 0) and their meaning is not established. The queue is a cache: events "
                 "appear to be removed once sent, so the rows are those still queued, not all activity. "
                 "Customer ID, Visitor ID and Session ID are identifiers as stored. Sign-in fields "
                 "(login method, auth state) are as the app recorded them for the event. The "
                 "tested samples held 0 rows on 2 of 4 databases. In the two databases with rows every event fell "
                 "within the same second, so Event Time is constant at whole-second resolution (the stored "
                 "value keeps the fraction and the rows are ordered by it); Channel, Network Type, Wi-Fi, "
                 "UI Mode and Orientation also held one value on every row of one database, which is the "
                 "data and not a derivation that did not run.",
        "paths": ("*/mobile/Containers/Data/Application/*/Library/Caches/com.paypal.lighthouseanalytics/"
                  "lighthouseanalytics.db*",),
        "output_types": "standard",
        "artifact_icon": "chart-line",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 0 rows",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 0 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 0 rows, no database in the container",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 25 rows",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 5 rows",
        },
    },
    "paypalMparticleSessions": {
        "name": "PayPal - Analytics SDK Sessions (mParticle)",
        "description": "Session rows of the legacy mParticle analytics database in the app's Documents folder.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from Documents/mParticle28.db (table sessions), accepted only in a container whose "
                 ".com.apple.mobile_container_manager.metadata.plist names com.yourcompany.PPClient. "
                 "Start, End and Length are the stored Unix seconds. Session Number was 0 on every row and is not shown. This database was present in 1 of 5 "
                 "tested installs and its newest session was years older than the install's other "
                 "files, so it is a leftover of an older app version, not current use. Other tables "
                 "(messages, consumer_info, cookies) are not reported.",
        "paths": ("*/mobile/Containers/Data/Application/*/Documents/mParticle*.db*",
                  "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist"),
        "output_types": "standard",
        "artifact_icon": "device-analytics",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 0 rows, no mParticle database",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 5 rows",
            "lab_ffs_ios26_2": "iOS 26.2 | 0 rows, no mParticle database",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 0 rows, no mParticle database",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 0 rows, no mParticle database",
        },
    },
    "paypalDebitTransactions": {
        "name": "PayPal - Wallet Transaction Store",
        "description": "Rows of the TransactionEntry table of the app-group default.store.",
        "author": "@danjethh",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "PayPal",
        "notes": "Read from Library/Application Support/default.store in the app-group container "
                 "(table ZTRANSACTIONENTRY), accepted only in a container whose "
                 ".com.apple.mobile_container_manager.metadata.plist names group.com.yourcompany.PPClient. "
                 "Validation boundary: the table was empty in all 5 tested installs, so this reader "
                 "was built from the schema and exercised only on synthetic rows. The date column is "
                 "typed TIMESTAMP and is read as Core Data seconds since 2001-01-01 UTC; that is the "
                 "usual convention and is not confirmed for this table, so the stored value is shown "
                 "beside it. Amount is shown as stored, with the stored display text; its scale "
                 "is not established. The status columns (approved, cleared, declined, refunded, "
                 "cashback, purchase, refund, unknown, withdrawal) are text columns shown as stored "
                 "with no interpretation. An empty table is not shown to mean that no card was used. "
                 "Sibling stores card_data.store, sync_queue.store and QRCodeOfflineCoreDataModel.sqlite "
                 "held 0 rows of card, sync or QR data in all tested installs and are not reported.",
        "paths": ("*/mobile/Containers/Shared/AppGroup/*/Library/Application Support/default.store*",
                  "*/mobile/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist"),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "lab_ffs_ios18_5": "iOS 18.5 | 0 rows, table present",
            "lab_ffs_ios18_6_2_a": "iOS 18.6.2 | 0 rows, table present",
            "lab_ffs_ios26_2": "iOS 26.2 | 0 rows, table present",
            "lab_ffs_ios18_6_2_b": "iOS 18.6.2 | 0 rows, table present",
            "lab_ffs_ios26_2_1": "iOS 26.2.1 | 0 rows, table present",
        },
    },
}

import datetime
import json
import os
import re
from urllib.parse import urlsplit, parse_qsl

from scripts.ilapfuncs import (
    artifact_processor, convert_cocoa_core_data_ts_to_utc, convert_plist_date_to_utc,
    convert_unix_ts_to_utc, does_table_exist_in_db, get_plist_content, get_plist_file_content,
    get_sqlite_db_records, logfunc,
)

BUNDLE_ID = 'com.yourcompany.PPClient'
GROUP_ID = 'group.com.yourcompany.PPClient'
MARKER = '.com.apple.mobile_container_manager.metadata.plist'
CONTAINER_RE = re.compile(r'^(.*/Containers/(?:Data/Application|Shared/AppGroup)/[0-9A-Fa-f-]{36})/', re.I)


def _norm(path):
    return str(path).replace('\\', '/')


def _find(files, name):
    """Paths in files whose base name is name (case-insensitive), in the order found."""
    return [f for f in files if os.path.basename(_norm(f)).lower() == name.lower()]


def _owned_roots(files, identifier):
    """Container folders whose metadata plist names the identifier; the check that a third-party
    file name (Thales-v2, mParticle, default.store) belongs to PayPal and not to another app."""
    roots = set()
    for found in _find(files, MARKER):
        meta = get_plist_file_content(found)
        if isinstance(meta, dict) and meta.get('MCMMetadataIdentifier') == identifier:
            roots.add(_norm(os.path.dirname(found)))
    return roots


def _in_roots(path, roots):
    match = CONTAINER_RE.match(_norm(path))
    return bool(match) and match.group(1) in roots


def _plist(path):
    content = get_plist_file_content(path)
    return content if isinstance(content, dict) else {}


def _clean(value):
    """Text for a report cell: None stays blank, bytes become a length note, the rest is str."""
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return f'({len(value)} bytes)'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return value if isinstance(value, (int, float)) else str(value)


def _rel(context, path):
    """The extraction-relative path with forward slashes, so a row reads the same on every platform."""
    return str(context.get_relative_path(path)).replace('\\', '/')


@artifact_processor
def paypalRememberedAccount(context):
    headers = ('Display Name', 'Username', 'Primary E-mail', 'Primary Phone', 'Account Profile ID',
               'Account Type (as stored)', 'Country Code', 'Photo URL', 'Phone-Password Login Flag',
               'Source File')
    rows = []
    source = []
    for found in context.get_files_found():
        raw = _plist(found).get('com.paypalRememberedUserV1')
        if not isinstance(raw, (bytes, bytearray)):
            continue
        user = get_plist_content(bytes(raw))
        if not isinstance(user, dict):
            logfunc('PayPal: RememberedUserV1 could not be read as a keyed archive')
            continue
        source.append(found)
        flag = user.get('phonePasswordLoginAccount')
        rows.append((user.get('RememberedUserDisplayName', ''), user.get('RememberedUsername', ''),
                     user.get('RememberedUserPrimaryEmail', ''), user.get('RememberedUserPrimaryPhone', ''),
                     user.get('RememberedAccountProfileId', ''), user.get('RememberedAccountType', ''),
                     user.get('RememberedUserCountryCode', ''), user.get('RememberedUserPhotoURL', ''),
                     '' if flag is None else _clean(flag), _rel(context, found)))
    return headers, rows, '\n'.join(source)


ACCOUNT_KEY_PATTERNS = (
    (re.compile(r'^com\.paypal\.pushNotification\.preference\.(?P<k>.+)$'), 'Push notification preference'),
    (re.compile(r'^socialTooltipViewedFirstTimeShown\.(?P<k>.+)$'), 'Social tooltip flag (socialTooltipViewedFirstTimeShown)'),
    (re.compile(r'^(?P<k>.+)\.hasUserSeenFXPopup$'), 'FX popup flag (hasUserSeenFXPopup)'),
)


@artifact_processor
def paypalAccountKeys(context):
    headers = ('Account Key', 'Setting', 'Value', 'Source File')
    rows = []
    source = []
    for found in context.get_files_found():
        prefs = _plist(found)
        used = False
        for key, value in prefs.items():
            if not isinstance(key, str):
                continue
            for pattern, label in ACCOUNT_KEY_PATTERNS:
                match = pattern.match(key)
                if not match:
                    continue
                used = True
                account = match.group('k')
                if isinstance(value, dict):
                    for name, item in sorted(value.items()):
                        rows.append((account, f'{label}: {name}', _clean(item), _rel(context, found)))
                else:
                    rows.append((account, label, _clean(value), _rel(context, found)))
                break
        if used:
            source.append(found)
    return headers, rows, '\n'.join(source)


@artifact_processor
def paypalDatedKeys(context):
    headers = (('Stored Date', 'datetime'), 'Key', 'Source File')
    rows = []
    source = []
    for found in context.get_files_found():
        prefs = _plist(found)
        before = len(rows)
        for key, value in prefs.items():
            if isinstance(value, datetime.datetime):
                rows.append((convert_plist_date_to_utc(value), key, _rel(context, found)))
        kronos = prefs.get('KronosStableTime')
        if isinstance(kronos, dict) and isinstance(kronos.get('Timestamp'), (int, float)):
            rows.append((convert_unix_ts_to_utc(kronos['Timestamp']),
                         'KronosStableTime.Timestamp (read as Unix seconds)', _rel(context, found)))
        if len(rows) > before:
            source.append(found)
    rows.sort(key=lambda r: (str(r[0]), r[1]))
    return headers, rows, '\n'.join(source)


SETTING_KEYS = (
    'OptInStatus', 'gdprConsented', 'home.appLocale', 'hub.appLocale', 'is_app_reinstalled',
    'isNativePasskeyEnrolled', 'isNotificationSubscriptionEnabled', 'com.paypal.notificationCenterBadgeCount',
    'com.paypal.DidRequestedNotificationPermissionKey', 'hasUserAcceptedPrivacyStatementPopup',
    'iRateUseCount', 'iRateEventCount', 'iRateLastVersionUsed', 'kCurrentNativeAuthType',
    'com.paypalAppleLocale', 'com.paypalAppleLanguages', 'com.paypalpinLoginApplicable',
    'com.paypalloginSkipCount', 'com.paypalUserClickedLogout', 'com.paypaltouchID.promptCount', 'com.paypalenablePinConsentDisplayCount',
)
DIRECT_DEPOSIT_KEYS = ('com.directdeposit.accountnumber', 'com.directdeposit.accounttype',
                       'com.directdeposit.routingnumber')
VERSION_RE = re.compile(r'^appLaunchedFirstTime:(?P<v>.+)$')


def _version_key(text):
    return tuple(int(part) if part.isdigit() else 0 for part in re.split(r'[.\-]', text))


@artifact_processor
def paypalAppSettings(context):
    headers = ('Group', 'Key (as stored)', 'Value', 'Source File')
    rows = []
    source = []
    for found in context.get_files_found():
        prefs = _plist(found)
        rel = _rel(context, found)
        before = len(rows)
        versions = []
        for key, value in prefs.items():
            if not isinstance(key, str):
                continue
            match = VERSION_RE.match(key)
            if match:
                versions.append((match.group('v'), value))
            elif key in SETTING_KEYS:
                rows.append(('Setting', key, _clean(value if not isinstance(value, list) else ', '.join(map(str, value))), rel))
            elif key in DIRECT_DEPOSIT_KEYS:
                rows.append(('Direct-deposit key', key, 'present, empty' if value in ('', None) else 'present, not empty', rel))
        for version, value in sorted(versions, key=lambda item: _version_key(item[0])):
            rows.append(('First-launch marker', f'appLaunchedFirstTime:{version}', _clean(value), rel))
        opt = prefs.get('OptInData')
        if isinstance(opt, dict):
            for key, value in sorted(opt.items()):
                rows.append(('OptInData', key, _clean(value), rel))
        if len(rows) > before:
            source.append(found)
    return headers, rows, '\n'.join(source)


LOG_LINE_RE = re.compile(r'^(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d:\d{3})Z (?P<tag>\w+) (?P<n>\d+) (?P<rest>.*)$')
LOG_HEADER_RE = re.compile(r'^TSH-\S+ (?P<app>.+?) (?P<num>\d+)\s+(?P<os>iOS \S+) (?P<model>\S+)\s*$')


def _log_time(stamp):
    """2025-06-17T20:51:00:871 (colon before the milliseconds) as UTC."""
    try:
        base = datetime.datetime.strptime(stamp[:19], '%Y-%m-%dT%H:%M:%S')
        return (base + datetime.timedelta(milliseconds=int(stamp[20:23]))).replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return stamp


@artifact_processor
def paypalSecuritySdkStarts(context):
    headers = (('SDK Record Time', 'datetime'), 'SDK Build', 'OS Version (log header)',
               'Device Model (log header)', 'Source File')
    files = context.get_files_found()
    roots = _owned_roots(files, BUNDLE_ID)
    rows = []
    source = []
    for found in files:
        if not os.path.basename(_norm(found)).startswith('slog-TSH-') or not _in_roots(found, roots):
            continue
        try:
            with open(found, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.read().splitlines()
        except OSError as error:
            logfunc(f'PayPal: Thales log could not be read: {error}')
            continue
        header = LOG_HEADER_RE.match(lines[0]) if lines else None
        os_version, model = header.group('os', 'model') if header else ('', '')
        found_rows = 0
        for line in lines:
            match = LOG_LINE_RE.match(line)
            if match and match.group('tag') == 'SDKV':
                rows.append((_log_time(match.group('ts')), match.group('rest'), os_version, model,
                             _rel(context, found)))
                found_rows += 1
        if found_rows:
            source.append(found)
    return headers, rows, '\n'.join(source)


STATS_RE = re.compile(r'(^|\.)stats\.paypal\.com$', re.I)


def _beacon_fields(host, query):
    if not STATS_RE.search(host):
        return ('', '', '', '')
    fields = dict(parse_qsl(query, keep_blank_values=True))
    stamp = fields.get('t', '')
    try:
        stamp = convert_unix_ts_to_utc(float(stamp)) if stamp else ''
    except ValueError:
        pass
    return (stamp, fields.get('i', ''), fields.get('p', ''), fields.get('a', ''))


@artifact_processor
def paypalCachedRequests(context):
    headers = (('Cached Time', 'datetime'), 'Host', 'Path', ('Beacon t (Unix seconds)', 'datetime'),
               'Beacon i (as stored)', 'Beacon p (as stored)', 'Beacon a (as stored)', 'Source File')
    rows = []
    source = []
    for found in _find(context.get_files_found(), 'Cache.db'):
        if not does_table_exist_in_db(found, 'cfurl_cache_response'):
            logfunc('PayPal: Cache.db has no cfurl_cache_response table')
            continue
        query = 'SELECT time_stamp, request_key FROM cfurl_cache_response ORDER BY time_stamp'
        found_rows = 0
        for stamp, key in get_sqlite_db_records(found, query):
            parts = urlsplit(key or '')
            cached = ''
            if stamp:
                try:
                    cached = datetime.datetime.strptime(str(stamp)[:19], '%Y-%m-%d %H:%M:%S').replace(
                        tzinfo=datetime.timezone.utc)
                except ValueError:
                    cached = stamp
            rows.append((cached, parts.hostname or '', parts.path, *_beacon_fields(parts.hostname or '', parts.query),
                         _rel(context, found)))
            found_rows += 1
        if found_rows:
            source.append(found)
    return headers, rows, '\n'.join(source)


def _field_reader(data):
    """A function returning the first non-empty value of data under the given names, as a report cell."""
    def field(*names):
        for name in names:
            if data.get(name) not in (None, ''):
                return _clean(data[name])
        return ''
    return field


def _json_object(text):
    try:
        value = json.loads(text) if text else {}
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


@artifact_processor
def paypalAnalyticsEvents(context):
    headers = (('Event Time', 'datetime'), 'Event Name', 'Page', 'Page Group', 'Event Type', 'Flow', 'Channel',
               'Network Type', 'Wi-Fi', 'UI Mode', 'Orientation', 'Device Locked', 'Login Method',
               'Auth State', 'API Response', 'Session ID', 'Customer ID', 'Visitor ID',
               'Dispatch Status (as stored)', 'Dispatch Tries (as stored)', 'Source File')
    rows = []
    source = []
    for found in _find(context.get_files_found(), 'lighthouseanalytics.db'):
        if not does_table_exist_in_db(found, 'events'):
            logfunc('PayPal: lighthouseanalytics.db has no events table')
            continue
        query = ('SELECT event_ts, event_payload, original_event, dispatch_status, network_dispatch_try_count '
                 'FROM events ORDER BY event_ts')
        found_rows = 0
        for stamp, payload, original, status, tries in get_sqlite_db_records(found, query):
            data = {**_json_object(original), **_json_object(payload)}
            field = _field_reader(data)

            rows.append((convert_unix_ts_to_utc(stamp), field('event_name', 'eventName'), field('page'),
                         field('pgrp'), field('evnt_type'), field('flow'), field('channel'),
                         field('network_type'), field('wifi'), field('ui_mode'), field('device_orientation'),
                         field('is_device_locked'), field('login_method'), field('auth_state'),
                         field('api_response'), field('sessn_id'), field('cust_id'), field('visitor_id'),
                         '' if status is None else status, '' if tries is None else tries,
                         _rel(context, found)))
            found_rows += 1
        if found_rows:
            source.append(found)
    return headers, rows, '\n'.join(source)


@artifact_processor
def paypalMparticleSessions(context):
    headers = (('Session Start', 'datetime'), ('Session End', 'datetime'), 'Length (seconds)',
               'Interruptions', 'Event Count', 'Source File')
    files = context.get_files_found()
    roots = _owned_roots(files, BUNDLE_ID)
    rows = []
    source = []
    for found in files:
        name = os.path.basename(_norm(found)).lower()
        if not (name.startswith('mparticle') and name.endswith('.db')) or not _in_roots(found, roots):
            continue
        if not does_table_exist_in_db(found, 'sessions'):
            logfunc('PayPal: mParticle database has no sessions table')
            continue
        query = ('SELECT start_time, end_time, length, number_interruptions, event_count '
                 'FROM sessions ORDER BY start_time')
        found_rows = 0
        for start, end, length, interruptions, count in get_sqlite_db_records(found, query):
            rows.append((convert_unix_ts_to_utc(start), convert_unix_ts_to_utc(end),
                         '' if length is None else round(length, 1), _clean(interruptions),
                         _clean(count), _rel(context, found)))
            found_rows += 1
        if found_rows:
            source.append(found)
    return headers, rows, '\n'.join(source)


@artifact_processor
def paypalDebitTransactions(context):
    headers = (('Transaction Date (read as Core Data seconds)', 'datetime'), 'Transaction Date (as stored)',
               'Amount (as stored)', 'Display Amount', 'Currency', 'Merchant Name', 'Merchant Category Code',
               'Merchant Postal Code', 'Card ID', 'Transaction ID', 'Approved', 'Cleared', 'Declined',
               'Refunded', 'Cashback', 'Purchase', 'Refund', 'Unknown', 'Withdrawal', 'Source File')
    files = context.get_files_found()
    roots = _owned_roots(files, GROUP_ID)
    rows = []
    source = []
    for found in files:
        if os.path.basename(_norm(found)).lower() != 'default.store' or not _in_roots(found, roots):
            continue
        if not does_table_exist_in_db(found, 'ZTRANSACTIONENTRY'):
            logfunc('PayPal: default.store has no ZTRANSACTIONENTRY table')
            continue
        query = ('SELECT ZTRANSACTIONDATE, ZAMOUNT, ZDISPLAYAMOUNT, ZCURRENCYCODE, ZMERCHANTNAME, '
                 'ZMERCHANTCATEGORYCODE, ZMERCHANTPOSTALCODE, ZCARDID, ZID, ZAPPROVED, ZCLEARED, ZDECLINED, '
                 'ZREFUNDED, ZCASHBACK, ZPURCHASE, ZREFUND, ZUNKNOWN, ZWITHDRAWAL '
                 'FROM ZTRANSACTIONENTRY ORDER BY ZTRANSACTIONDATE')
        found_rows = 0
        for record in get_sqlite_db_records(found, query):
            values = [_clean(item) for item in record]
            stamp = record[0]
            when = convert_cocoa_core_data_ts_to_utc(stamp) if isinstance(stamp, (int, float)) else ''
            rows.append((when, values[0], *values[1:], _rel(context, found)))
            found_rows += 1
        if found_rows:
            source.append(found)
    return headers, rows, '\n'.join(source)
