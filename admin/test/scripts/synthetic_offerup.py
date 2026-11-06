#!/usr/bin/env python3
"""Build a SYNTHETIC OfferUp (com.offerup.iphone.consumer) data container: invented values, no data from any device.

The layout mirrors what the offerup artifacts read in an iOS full file system extraction:

    .com.apple.mobile_container_manager.metadata.plist      names the bundle id
    Documents/mmkv/redux (+ .crc)                           redux-persist stores in an MMKV file
    Documents/mmkv/statsig (+ .crc)                         Statsig SDK sessions and stable id
    Library/Preferences/com.offerup.iphone.consumer.plist   SDK install and launch values
    Library/Application Support/com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/manifest.json
                                                            (+ an overflow file named by MD5(key))
    Library/Caches/com.offerup.iphone.consumer/Cache.db     NSURLCache

Two variants:
    current   an OfferUp 2026.9.0-shaped container with every store
    earlier   a 2026.3.0-shaped container with no feedAffinity store, no chat draft, no Cache.db, and a
              recent-searches value kept in the React Native overflow file

A decoy container of another app (a different bundle id) carries the same Documents/mmkv names; it must
produce no rows.

    python synthetic_offerup.py current out.tar.gz
    python synthetic_offerup.py earlier out.tar.gz

All names, places, identifiers and text are invented. ``build_files(variant)`` returns
{path below the extraction root: bytes}.
"""

import datetime
import hashlib
import io
import json
import plistlib
import sqlite3
import struct
import sys
import tarfile
import tempfile
import uuid
import os

BUNDLE_ID = "com.offerup.iphone.consumer"
_NS = uuid.UUID("11111111-2222-3333-4444-555555555555")
APPS = "private/var/mobile/Containers/Data/Application"
ACCOUNT_ID = "900000001"
PUSH_SUFFIX = "0123456789ABCDEF" * 4          # invented hex
ADVERTISING_ID = "00000000-0000-4000-8000-000000000001"
DEVICE_ID = "00000000-0000-4000-8000-000000000002"
STABLE_ID = "synthetic-stable-id-0001"
# Unix milliseconds used for every invented time (2026-09-21 and a little later)
T0 = 1790000000000


def container_uuid(label):
    return str(uuid.uuid5(_NS, label)).upper()


def _varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _entry(key, text):
    key_bytes = key.encode("utf-8")
    text_bytes = text.encode("utf-8")
    container = _varint(len(text_bytes)) + text_bytes
    return _varint(len(key_bytes)) + key_bytes + _varint(len(container)) + container


def mmkv_store(entries):
    """An MMKV file: [u32 size][items-size varint][entries][zero padding] from [(key, text)]."""
    data = b"".join(_entry(key, text) for key, text in entries)
    region = _varint(len(data)) + data
    return struct.pack("<I", len(region)) + region + b"\x00" * 64


def mmkv_meta(actual_size):
    """A .crc sibling: meta version 3 with the recorded size and no vector."""
    out = bytearray(32)
    struct.pack_into("<I", out, 4, 3)
    struct.pack_into("<I", out, 28, actual_size)
    return bytes(out)


def _with_meta(entries):
    payload = mmkv_store(entries)
    size = struct.unpack_from("<I", payload, 0)[0]
    return payload, mmkv_meta(size)


def _j(value):
    return json.dumps(value, separators=(",", ":"))


def _persist(fields):
    """redux-persist value: an object whose fields are JSON strings, plus the _persist marker."""
    body = {name: _j(value) for name, value in fields.items()}
    body["_persist"] = _j({"version": -1, "rehydrated": True})
    return _j(body)


def redux_entries(variant):
    root = {
        "adsDevSettings": {"showFloatingGoogleButton": False, "adEvents": []},
        "coupons": {},
        "deals": {"dealsAlertsEnabled": False},
        "devSettings": {"showDeveloperSettings": False},
        "exposureTracking": {"exposures": {
            "POST_DETAIL_FTUE_KEY": {"exposureCount": 2, "lastSuccessfulExposureTimestamp": T0 + 5000,
                                     "attemptedExposureCount": 3, "lastAttemptedExposureTimestamp": T0 + 6000}}},
        "instrumentation": {
            "attributes": {"deviceId": DEVICE_ID, "deviceUserAgent": "OfferUp/0.0 (SyntheticPhone; iOS 0.0)",
                           "locale": "en", "screenName": "Home"},
            "tags": {"isFirstOpenAfterInstall": False, "isPremiumUser": False, "previousVersion": "2026.3.0",
                     "isDeepLink": False, "isFirstOpenAfterUpdate": True, "isHeadless": False}},
        "pushNotificationPermissions": {"numberOfTimesShown": 1, "smallCooldown": 1, "bigCooldown": 2,
                                        "seenLimit": 3, "lastShown": T0 + 1000},
        "rentals": {"rentalsSearchLocation": {"latitude": "11.1111", "longitude": "-22.2222",
                                              "locationName": "Rentville, EX"}},
        "servicePosting": {"hasDraftStarted": False},
        "theme": {"isSystemPreference": True},
        "notifications": {"ablyState": {"lastHeartbeatTime": T0 + 7000, "useLocalHeartbeat": True,
                                        "statsigHeartbeatInterval": 30}},
    }
    older_root = dict(root)
    older_root["notifications"] = {"ablyState": {"lastHeartbeatTime": T0 + 100, "useLocalHeartbeat": True,
                                                 "statsigHeartbeatInterval": 30}}
    entries = [
        ("hasMigratedFromAsyncStorage", _j(["persist:root"])),
        ("persist:root", _persist(older_root)),
        ("persist:core", _persist({"currentVersion": "2026.9.0" if variant == "current" else "2026.3.0",
                                   "previousVersion": "2026.3.0" if variant == "current" else "2025.51.0"})),
        ("persist:onboarding", _persist({
            "userHasLoggedInAtLeastOnce": True,
            "steps": {"searchLocation": {"completed": True}, "notificationPermissions": {"completed": True},
                      "buyerInterests": {"completed": False}, "tappedOnSaveItem": {"completed": True}}})),
        ("persist:ads", _persist({"doNotSellMyData": False, "doNotUsePPID": False,
                                  "advertisingInfo": {"isLimitAdTrackingEnabled": False,
                                                      "advertisingId": ADVERTISING_ID}})),
        ("persist:search", _persist({"location": {"city": "Exampleton", "locationName": "Exampleton, EX",
                                                  "adminArea": "Example County", "lon": -65.4321,
                                                  "zipcode": "00000", "lat": 12.3456, "state": "EX"}})),
        ("persist:navigation", _persist({"verticalsEnabled": {"aaaa": {"services": True}}})),
        ("persist:root", _persist(root)),
    ]
    if variant == "current":
        entries.insert(3, ("persist:feedAffinity", _persist({
            "listingAffinities": [{"listingId": "1000000001", "categoryId": "1.1"},
                                  {"listingId": "1000000002", "categoryId": "2.3"},
                                  {"listingId": "1000000003", "categoryId": "1.1"}],
            "formattedAffinities": {"LAST_VIEWED_CATEGORIES": "1.1,2.3,9.9"}})))
        entries.insert(4, ("persist:itemPosting", _persist({"drafts": {}})))
    return entries


def statsig_entries():
    def session(session_id, start, update):
        return _j({"sessionID": session_id, "startTime": T0 + start, "lastUpdate": T0 + update})
    return [
        ("hasMigratedFromAsyncStorage", "true"),
        ("statsig.stable_id.1111111111", _j(STABLE_ID)),
        ("statsig.session_id.1111111111", session("00000000-0000-4000-8000-0000000000a1", 0, 60000)),
        ("statsig.session_id.1111111111", session("00000000-0000-4000-8000-0000000000a1", 0, 300000)),
        ("statsig.session_id.1111111111", session("00000000-0000-4000-8000-0000000000a2", 900000, 960000)),
        ("statsig.cached.evaluations.2222222222", _j({"source": "Network", "data": "{}", "receivedAt": T0,
                                                      "stableID": STABLE_ID, "fullUserHash": "0"})),
    ]


def manifest_and_overflow(variant):
    """AsyncStorage manifest.json and the overflow files React Native names by MD5(key)."""
    recent = [{"__typename": "Suggestion", "type": "keyword", "label": "synthetic bike",
               "actionPath": "/search/?q=synthetic+bike", "subLabel": None, "preposition": None},
              {"__typename": "Suggestion", "type": "keyword", "label": "synthetic couch",
               "actionPath": "/search/?q=synthetic+couch&delivery_param=p", "subLabel": "in Exampleton",
               "preposition": "in"}]
    manifest = {
        "push_permission_status": _j({"settings": {"alert": True, "sound": True, "badge": True,
                                                   "providesAppSettings": False}, "status": "granted"}),
        "ANALYTICS_INFO_KEY": _j({"shouldLogSampledEvent": False}),
        "PUSH_NOTIFICATION_PERMISSIONS_RUNNER_KEY": _j({"runCount": 1, "lastSuccessfulRunDate": T0 + 1000,
                                                        "attemptedRunCount": 1,
                                                        "lastAttemptedRunDate": T0 + 1000}),
        "BUSINESS_TOOLS": _j({"runCount": 4, "lastSuccessfulRunDate": T0 + 2000, "attemptedRunCount": 6,
                              "lastAttemptedRunDate": T0 + 2500}),
        f"{ACCOUNT_ID}:LAST_REGISTERED_AT:{PUSH_SUFFIX}": str(T0 + 3000),
        "LAST_ACCOUNT_PAGE_REFRESH": str(T0 + 4000),
        "profile_location_after_filter": str(T0 + 4500),
        "ou_post_flow_preferences": _j({"location": {"locationName": "Posttown, EX", "lat": 33.3333,
                                                     "lon": -44.4444, "didUseGPS": True}, "condition": "new"}),
        "recent_searches_rentals": _j([{"label": "synthetic flat", "subLabel": "Rentville, EX",
                                        "actionPath": "/rentals/search?q=synthetic+flat", "type": "keyword"}]),
    }
    overflow = {}
    if variant == "current":
        manifest["ou-recent-searches"] = _j(recent)
        manifest["chat_draft_message"] = _j({"7000000000000000001": "Synthetic draft text, not sent",
                                             "7000000000000000002": "ok"})
    else:
        manifest["ou-recent-searches"] = None
        overflow[hashlib.md5(b"ou-recent-searches").hexdigest()] = _j(recent).encode("utf-8")
    return json.dumps(manifest).encode("utf-8"), overflow


def prefs_plist():
    return plistlib.dumps({
        "VersionOfLastRun": "2026.9.0",
        "AppsFlyerUserId": "synthetic-appsflyer-id-0001",
        "AppsFlyerRealLaunchCounter": 42,
        "AppsFlyerReInstallCounter": 0,
        "AppsFlyerInstallTimestamp": str((T0 - 86400000) / 1000),
        "AppsFlyerInstallDate": "2026-09-20_000000-0000",
        "com.facebook.sdk:FBSDKSettingsInstallTimestamp": datetime.datetime(2026, 9, 20, 0, 0, 5),
    }, fmt=plistlib.PlistFormat.FMT_BINARY)


def cache_db():
    """A synthetic NSURLCache Cache.db with OfferUp, Ably and advertising entries."""
    def response(url, status=200, content_type="application/json"):
        array = [{"_CFURLStringType": 15, "_CFURLString": url}, 794000000.5, 0, status,
                 {"Content-Type": content_type, "Content-Length": "10"},
                 "__CFURLResponseNullTokenString__", "__CFURLResponseNullTokenString__"]
        return plistlib.dumps({"Version": 0, "Array": array}, fmt=plistlib.PlistFormat.FMT_BINARY)

    rows = [
        ("https://offerup-rest.ably.io:443/comet/connect", "2026-09-21 10:00:01", 0,
         b'[{"action":4,"connectionId":"synthetic","connectionDetails":{"clientId":"synthetic"}}]'),
        ("https://offerup-realtime.ably.io:443/channels/notification%3Asynthetic/messages",
         "2026-09-21 10:00:09", 0, b'{"statusCode":200,"response":[]}'),
        ("https://images.offerup.com/synthetic/100x100/smart", "2026-09-21 10:00:20", 0, b"\x89PNG\r\n"),
        ("https://static.offerup.com/high_intent/variants/pill", "2026-09-21 10:00:30", 1, b"fsCachedData-name"),
        ("https://googleads.g.doubleclick.net/pagead/interaction/?ai=synthetic", "2026-09-21 10:01:00", 0,
         b"ad"),
    ]
    path = tempfile.mktemp(suffix=".db")
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE cfurl_cache_response (entry_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            version INTEGER, hash_value INTEGER, storage_policy INTEGER, request_key TEXT UNIQUE,
            time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP, partition TEXT);
        CREATE TABLE cfurl_cache_blob_data (entry_ID INTEGER PRIMARY KEY, response_object BLOB,
            request_object BLOB, proto_props BLOB, user_info BLOB);
        CREATE TABLE cfurl_cache_receiver_data (entry_ID INTEGER PRIMARY KEY, isDataOnFS INTEGER,
            receiver_data BLOB);""")
    for index, (url, stamp, on_disk, body) in enumerate(rows, start=1):
        con.execute("INSERT INTO cfurl_cache_response VALUES (?,?,?,?,?,?,?)", (index, 0, index, 0, url, stamp, None))
        mime = "image/png" if "images." in url else "application/json"
        con.execute("INSERT INTO cfurl_cache_blob_data VALUES (?,?,?,?,?)",
                    (index, response(url, content_type=mime), None, None, None))
        con.execute("INSERT INTO cfurl_cache_receiver_data VALUES (?,?,?)", (index, on_disk, body))
    con.commit()
    con.close()
    with open(path, "rb") as handle:
        data = handle.read()
    os.remove(path)
    return data


def _metadata(bundle_id):
    return plistlib.dumps({"MCMMetadataIdentifier": bundle_id, "MCMMetadataContentClass": 2,
                           "MCMMetadataVersion": 15}, fmt=plistlib.PlistFormat.FMT_BINARY)


def build_files(variant="current"):
    """{path below the extraction root: bytes} for the OfferUp container and a decoy container."""
    base = f"{APPS}/{container_uuid('offerup-' + variant)}"
    files = {f"{base}/.com.apple.mobile_container_manager.metadata.plist": _metadata(BUNDLE_ID)}
    payload, meta = _with_meta(redux_entries(variant))
    files[f"{base}/Documents/mmkv/redux"] = payload
    files[f"{base}/Documents/mmkv/redux.crc"] = meta
    payload, meta = _with_meta(statsig_entries())
    files[f"{base}/Documents/mmkv/statsig"] = payload
    files[f"{base}/Documents/mmkv/statsig.crc"] = meta
    files[f"{base}/Library/Preferences/{BUNDLE_ID}.plist"] = prefs_plist()
    storage = f"{base}/Library/Application Support/{BUNDLE_ID}/RCTAsyncLocalStorage_V1"
    manifest, overflow = manifest_and_overflow(variant)
    files[f"{storage}/manifest.json"] = manifest
    for name, data in overflow.items():
        files[f"{storage}/{name}"] = data
    if variant == "current":
        files[f"{base}/Library/Caches/{BUNDLE_ID}/Cache.db"] = cache_db()

    decoy = f"{APPS}/{container_uuid('decoy-' + variant)}"
    files[f"{decoy}/.com.apple.mobile_container_manager.metadata.plist"] = _metadata("com.example.otherapp")
    payload, meta = _with_meta([("persist:core", _persist({"currentVersion": "9.9.9"})),
                                ("persist:search", _persist({"location": {"locationName": "Decoyville",
                                                                           "lat": 1.0, "lon": 2.0}}))])
    files[f"{decoy}/Documents/mmkv/redux"] = payload
    files[f"{decoy}/Documents/mmkv/redux.crc"] = meta
    payload, meta = _with_meta(statsig_entries())
    files[f"{decoy}/Documents/mmkv/statsig"] = payload
    files[f"{decoy}/Documents/mmkv/statsig.crc"] = meta
    return files


def write_archive(path, variant="current"):
    files = build_files(variant)
    with tarfile.open(path, "w:gz") as tar:
        for name in sorted(files):
            info = tarfile.TarInfo(name)
            info.size = len(files[name])
            info.mtime = 1799970000
            tar.addfile(info, io.BytesIO(files[name]))
    return path


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("current", "earlier"):
        sys.exit("usage: synthetic_offerup.py current|earlier output.tar.gz")
    write_archive(sys.argv[2], sys.argv[1])
