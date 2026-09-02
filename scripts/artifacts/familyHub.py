__artifacts_v2__ = {
    "familyHubAccount": {
        "name": "Samsung Family Hub - Account",
        "description": "The Samsung account signed in to the Family Hub refrigerator app, with "
                       "the app's setup and last authorization times, the device identity it "
                       "registered, and which app features were switched on.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "Samsung Family Hub",
        "notes": "Read from Library/Preferences/com.samsung.familyhub.plist, including the "
                 "NSKeyedArchiver dictionary under its SessionData key, with Device ID and Last "
                 "Token Authorization joined from the authorizeToken response held in "
                 "Library/Caches/com.samsung.familyhub/Cache.db where that cache is present; on "
                 "the tested extraction every row of that cache lived in its write-ahead log, so "
                 "the -wal sidecar is part of the path pattern. The account's access and refresh "
                 "tokens, the app secret and the push tokens are in the same stores and are not "
                 "reported. Terms Agreed At is the agreeTime of the terms-and-conditions "
                 "agreement dictionary, localised with the IANA zone the same dictionary records "
                 "under timeZoneName and rendered in UTC; that zone is reported beside it as "
                 "stored, and the privacy-policy agreement carried the same time and zone on the "
                 "tested extraction. Country is the countryCode of that dictionary. First Launch "
                 "is reported as stored because it carries no zone; it agreed to the second with "
                 "the UTC time stamps of the first cache entries on the tested extraction, and no "
                 "zone is asserted for it. App Device ID is the deviceId the session dictionary "
                 "holds, which matched the deviceId in both agreement dictionaries; Samsung Auth "
                 "Device ID is the authenticateDeviceID in the authorizeToken response and is a "
                 "different, UUID-shaped identifier, so the two are reported separately. The "
                 "authenticateUserID in that response matched Account ID, and the userId in both "
                 "agreement dictionaries matched Account Email. The plist's last-cloud-sync value "
                 "predates the first launch by several years on the tested extraction and reads "
                 "as a default rather than an event, so it is not reported. Phone is the msisdn "
                 "the session dictionary holds, as stored, and was empty on the tested "
                 "extraction. Family Status and Food Recognition Supported are reported as "
                 "stored. The app's Realm store (Documents/default.realm, file format 9) was read "
                 "and is deliberately not reported: its 1,851 rows of class_FHFoodItemModel are "
                 "the food catalogue the app downloads from the Whisk service, which the cache "
                 "shows arriving in 38 paginated responses holding exactly 1,851 products, and "
                 "every user-data class in that store held no rows on the tested extraction, "
                 "namely class_FHFoodListModel (fridge inventory), class_FHShoppingListModel, "
                 "class_FHToDoListModel, class_FHToDoItemModel, class_FHMemoListModel, "
                 "class_FHWhiteBoardListModel, class_FHCalendarModel, class_FHCalendarEventModel, "
                 "class_FHDeals, class_FHGlazeCameraInfoModel (refrigerator camera images) and "
                 "class_FHInsideFridgeScannedItemModel. Documents/FamilyBoard/offlineDB held no "
                 "rows either. So a row here means the account was linked and the app set up, and "
                 "on the tested extraction none of the refrigerator features had been used. The "
                 "SafariViewService web cache beside the app holds the Samsung account sign-in "
                 "page and its static assets and is not reported. The app's data container was "
                 "present on 1 of the 24 registered iOS corpora swept for it, and no Android "
                 "corpus of 28 holds the app.",
        "paths": ('*/Library/Preferences/com.samsung.familyhub.plist',
                  '*/Library/Caches/com.samsung.familyhub/Cache.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | com.samsung.familyhub 5.0.6 | 1 row",
        },
    },
}

import os
import plistlib
import re
from datetime import datetime, timezone

import pytz

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, open_sqlite_db_readonly

_PLIST_NAME = 'com.samsung.familyhub.plist'
_CACHE_NAME = 'Cache.db'


def _text(value):
    """A displayable scalar. A list is rendered as its members, not its length."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple)):
        return ', '.join(str(item) for item in value)
    return value


def _session(blob):
    """The NSKeyedArchiver NSMutableDictionary under SessionData, as a plain dict."""
    if not isinstance(blob, (bytes, bytearray)):
        return {}
    try:
        archive = plistlib.loads(blob)
        objects = archive['$objects']
        root = objects[archive['$top']['root'].data]
        out = {}
        for key_uid, value_uid in zip(root['NS.keys'], root['NS.objects']):
            key = objects[key_uid.data]
            value = objects[value_uid.data]
            if isinstance(key, str) and isinstance(value, (str, int, float, bool)):
                out[key] = value
        return out
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Family Hub: SessionData did not decode: {error}')
        return {}


def _agreement(value):
    """(aware UTC datetime or '', zone name as stored, country as stored) from a
    terms-agreement dictionary. agreeTime is 'YYYY.MM.DD HH:MM:SS' in the zone the
    same dictionary records under timeZoneName, so it is localised with that zone
    rather than assumed; a value that cannot be placed is returned as stored."""
    if not isinstance(value, dict):
        return '', '', ''
    stamp = str(value.get('agreeTime') or '')
    zone = str(value.get('timeZoneName') or '')
    country = _text(value.get('countryCode'))
    if not stamp:
        return '', zone, country
    try:
        naive = datetime.strptime(stamp, '%Y.%m.%d %H:%M:%S')
        when = pytz.timezone(zone).localize(naive).astimezone(timezone.utc) if zone else stamp
    except (ValueError, pytz.UnknownTimeZoneError):
        when = stamp
    return when, zone, country


def _cache_authorization(files_found):
    """(device id, UTC time) of the newest authorizeToken response in the URL cache."""
    best = (None, '', '')
    for file_found in files_found:
        file_found = str(file_found)
        # The pattern also returns the -wal and -shm sidecars; only the database is opened.
        if os.path.isdir(file_found) or not file_found.endswith(_CACHE_NAME):
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        try:
            rows = db.execute(
                "SELECT e.time_stamp, d.receiver_data "
                "FROM cfurl_cache_response e "
                "JOIN cfurl_cache_receiver_data d ON d.entry_ID = e.entry_ID "
                "WHERE e.request_key LIKE '%/authorizeToken%' "
                "ORDER BY e.time_stamp DESC").fetchall()
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'Family Hub: {os.path.basename(file_found)}: {error}')
            continue
        finally:
            db.close()
        for stamp, body in rows:
            text = body.decode('utf-8', 'replace') if isinstance(body, (bytes, bytearray)) else str(body or '')
            match = re.search(r'<authenticateDeviceID>([^<]+)</authenticateDeviceID>', text)
            device = match.group(1) if match else ''
            if stamp and (best[1] == '' or str(stamp) > str(best[1])):
                best = (file_found, str(stamp), device)
    when = ''
    if best[1]:
        try:
            when = datetime.strptime(best[1][:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        except ValueError:
            when = best[1]
    return best[0], best[2], when


@artifact_processor
def familyHubAccount(context):
    data_headers = (
        ('Terms Agreed At', 'datetime'),
        ('Last Token Authorization', 'datetime'),
        'First Launch (as stored)',
        'Terms Time Zone (as stored)',
        'Account Email',
        'Account ID',
        'Logged In',
        'App Device ID',
        'Samsung Auth Device ID',
        'Phone (as stored)',
        'Country',
        'Language',
        'Region',
        'App Version',
        'App Build',
        'Family Status (as stored)',
        'Food Recognition Supported',
        'Home Screen Order',
        'Source File',
    )
    data_list = []
    sources = []
    files_found = [str(f) for f in context.get_files_found()]
    cache_file, cache_device, last_auth = _cache_authorization(files_found)

    for file_found in files_found:
        if os.path.isdir(file_found) or not file_found.endswith(_PLIST_NAME):
            continue
        try:
            plist = get_plist_file_content(file_found) or {}
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'Family Hub: {os.path.basename(file_found)} did not parse: {error}')
            continue
        session = _session(plist.get('SessionData'))
        agreed_at, agreed_zone, country = _agreement(plist.get('FH_TERMS_AGREEMENT_INFO_TNC'))
        order = list(plist.get('CurrentSequenceOfItems0') or []) + \
            list(plist.get('CurrentSequenceOfItems1') or [])
        data_list.append((
            agreed_at,
            last_auth,
            _text(plist.get('GAIFirstInitTimeStamp')),
            agreed_zone,
            _text(plist.get('SAMSUNG_ACCOUNT_USER_NAME')),
            _text(plist.get('FH_SAMSUNG_ACCOUNT_GUID')),
            _text(plist.get('FH_IS_USER_LOGGED_IN')),
            _text(session.get('deviceId')),
            cache_device,
            _text(session.get('msisdn') or session.get('phone')),
            country,
            _text(plist.get('FH_IPHONE_LANGUAGE')),
            _text(plist.get('FH_IPHONE_REGION')),
            _text(plist.get('FH_CURRENT_APP_VERSION')),
            _text(plist.get('FH_CURRENT_APP_BUILD')),
            _text(plist.get('FH_CURRENT_FAMILY_STATUS')),
            _text(plist.get('IS_FOOD_RECOGNITION_SUPPORTED')),
            _text(order),
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)
    if data_list and cache_file:
        sources.append(cache_file)
    return data_headers, data_list, '\n'.join(sources)
