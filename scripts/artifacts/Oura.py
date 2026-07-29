__artifacts_v2__ = {
    # The segment/zendesk/account-UID patterns below also match same-named SDK
    # plists inside other apps' containers (Life360, etc.). Parsing is anchored
    # to the directory that holds com.ouraring.oura.plist (_load_oura_plists),
    # so those foreign matches are never read.
    #
    # Coverage architecture: every key of every Oura plist is either claimed by
    # one of the topical artifacts below or reported raw by
    # oura_preferences_residue - nothing is silently dropped.
    "oura_account_identifiers": {
        "name": "Oura - Account & Identifiers",
        "description": "Account e-mail and UIDs plus every cross-service identifier "
                       "and token: Segment user/anonymous IDs, Zendesk user id, UUID "
                       "and auth tokens, Apple App-Attest UUID.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Identifiers allow correlation with Segment/Amplitude/Braze/Zendesk "
                 "server-side records. Each row cites the plist it came from.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
    },
    "oura_ring_hardware": {
        "name": "Oura - Ring Hardware & Status",
        "description": "Paired ring hardware: BLE MAC, model, color, size, firmware, "
                       "PPG LED parameters, battery records, low-battery notifications "
                       "and every ring/UTC time mapping variant.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "The Ring ID is the ring's Bluetooth MAC address - correlate with "
                 "device Bluetooth pairing records. ringTime values are raw ring "
                 "tick counters kept alongside their UTC anchor.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "circle",
    },
    "oura_find_my_ring_location": {
        "name": "Oura - Find My Ring Last Known Location",
        "description": "Last known GPS fix from Find My Ring: lat/long, altitude, "
                       "speed, course and all accuracy values. Exportable to KML.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "From 'findMyRingLastKnownLocation'; timestamp is Apple Cocoa/NSDate.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "kml", "lava", "timeline"],
        "html_columns": ["Map"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Grindr - Gay Dating & Chat 9.11.1, Life360: Find Friends & Family 23.19.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 0 rows",
        },
    },
    "oura_health_profile": {
        "name": "Oura - Health Profile & Disclosures",
        "description": "Demographics, body metrics, sleep/stress disclosures, "
                       "cycle & pregnancy settings, glucose settings, activity "
                       "habits and goals, consents, and remaining profile traits.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Values the user disclosed to the app (sleep problems, shift work, "
                 "GLP-1 use, cycle tracking...) plus profile traits Segment/Braze "
                 "cached. Each row cites its source plist.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "heart",
    },
    "oura_health_snapshot": {
        "name": "Oura - Health Data Snapshot (Widget Cache)",
        "description": "Cached health measurements from the widget blob: daytime "
                       "heart-rate clusters, steps and calories, 30-minute movement "
                       "intensity, stress, temperature trend and past-day scores.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Snapshot of 'widgetInfo' cached for the last day the widget "
                 "refreshed - not a full history. Series without their own "
                 "timestamps are reported in stored order.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
    },
    "oura_connected_services": {
        "name": "Oura - Connected Services & Permissions",
        "description": "Third-party and system integrations: Strava/Dexcom-style app "
                       "connections, HealthKit read/write authorizations and import "
                       "anchors, CarPlay head units, home-screen widgets, permissions.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "appConnections names the external accounts linked to Oura. "
                 "CarCapabilities entries are CarPlay head-unit identifiers - "
                 "evidence the device was used in specific vehicles.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "link",
    },
    "oura_app_activity": {
        "name": "Oura - App Activity Timeline",
        "description": "Every timestamp-bearing Oura key across the app's plists: "
                       "launches, syncs, token refresh, uploads, PPG/stress sensing, "
                       "onboarding milestones and more.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Mixed ISO/Unix/Cocoa timestamps normalised to UTC; day-only values "
                 "(YYYY-MM-DD) are reported as-is. Both the suite and the standard "
                 "defaults plist are scanned - older copies of the same key can "
                 "legitimately appear twice with different sources.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "clock",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Grindr - Gay Dating & Chat 9.11.1, Life360: Find Friends & Family 23.19.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 0 rows",
        },
    },
    "oura_app_environment": {
        "name": "Oura - App Environment & Versions",
        "description": "App versions across both preference files (they diverge), "
                       "build and migration numbers, locale, keyboards, unit system, "
                       "free disk space, network and permission state.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "The suite and com.ouraring.oura.plist copies of version keys are "
                 "written at different times - both are reported so the divergence "
                 "is visible instead of silently resolved.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone",
    },
    "oura_content_campaigns": {
        "name": "Oura - Content Caches & Campaigns",
        "description": "Cached health-topic articles (heart, glucose, reproductive "
                       "health, pregnancy...), marketing campaign engagement and "
                       "explore/meditation session traces.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Article caches show which health modules the app served to this "
                 "account. Cache presence alone is not proof the user read the "
                 "content; engagement keys (dismissed/played/interacted) are.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book-open",
    },
    "oura_analytics_integrations": {
        "name": "Oura - Analytics Integrations",
        "description": "Segment analytics destinations (Amplitude, Braze, Segment.io, "
                       "AWS S3) with API key, type, SDK version, consent categories, "
                       "plus queued event count and telemetry sample rate.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "From the 'integrations' block of 'segment.settings'. API keys can "
                 "support lawful-process requests to the analytics vendors.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "share-2",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 1 row",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | Grindr - Gay Dating & Chat 9.11.1, Life360: Find Friends & Family 23.19.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 0 rows",
        },
    },
    "oura_analytics_event_plan": {
        "name": "Oura - Analytics Event Plan",
        "description": "Segment tracking plan: every analytics event name the app "
                       "records (track/identify/group), showing collected telemetry.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "From the 'plan' block of 'segment.settings'; bulk, so TSV + LAVA only.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["lava", "tsv"],
        "artifact_icon": "list",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 18 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | Grindr - Gay Dating & Chat 9.11.1, Life360: Find Friends & Family 23.19.0 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Venmo 8.14.1 | 0 rows",
        },
    },
    "oura_feature_flags": {
        "name": "Oura - Feature Flags & Labs",
        "description": "Server-enabled feature flags, flag parameters, Oura Labs "
                       "enrollments and blackout-mode features cached in the "
                       "Segment traits.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Flags reveal which features/studies were active for this account "
                 "(e.g. blood-pressure study, AI coach). Bulk, so TSV + LAVA only.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["lava", "tsv"],
        "artifact_icon": "flag",
    },
    "oura_preferences_residue": {
        "name": "Oura - Preferences Residue (Unmapped Keys)",
        "description": "Every remaining key from the Oura preference plists that no "
                       "topical Oura artifact claims: UI state, migration flags, "
                       "OS/SDK housekeeping and any keys new app versions add.",
        "author": "@slay3r00",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Completeness guarantee: keys land here instead of being silently "
                 "dropped, so new-version keys surface for triage. Values are "
                 "decoded (nested bplist/JSON) and reported raw.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "archive",
    },
}

import base64
import json
import os
import plistlib
import re
from datetime import datetime, timezone

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, get_file_path, logfunc

# Cocoa/NSDate epoch (2001-01-01 UTC) as Unix seconds.
COCOA_EPOCH = 978307200

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_DAY_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATEISH_KEY_RE = re.compile(
    r"(date|time|timestamp|_at$|/.*at$|seen|performed|displayed|launch|refresh)",
    re.IGNORECASE,
)
_MAC_RE = re.compile(r"^[0-9A-Fa-f]{12}$")

# the OS and bundled SDKs (SiriKit, Wallet...) also stash keys in these
# defaults; they are reported in the residue artifact, not the Oura ones.
_OS_PREFIXES = ("com.apple.", "IN", "PK", "AK", "NS", "Web", "TTSN", "CarCapabilities")


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


def ts_cocoa(value):
    """Cocoa/NSDate seconds -> UTC string."""
    try:
        return _fmt(datetime.fromtimestamp(float(value) + COCOA_EPOCH, tz=timezone.utc))
    except (TypeError, ValueError, OSError, OverflowError):
        return ""


def ts_unix(value):
    """Unix seconds (milliseconds if > 1e12) -> UTC string."""
    try:
        v = float(value)
        if v > 1e12:
            v /= 1000.0
        return _fmt(datetime.fromtimestamp(v, tz=timezone.utc))
    except (TypeError, ValueError, OSError, OverflowError):
        return ""


def ts_iso(value):
    """ISO-8601 string, or a plist datetime, -> UTC string."""
    if not value:
        return ""
    if isinstance(value, datetime):
        return _fmt(value)
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            return ""
    s = str(value)
    try:
        return _fmt(datetime.fromisoformat(s.replace("Z", "+00:00")))
    except ValueError:
        try:
            return _fmt(datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
        except ValueError:
            return s


def ts_auto(value):
    """Timestamp of unknown encoding. Numbers 5e8-1e9 read as Cocoa, >=1e9 as Unix."""
    if isinstance(value, datetime):
        return _fmt(value)
    if isinstance(value, str):
        if _ISO_DATE_RE.match(value):
            return ts_iso(value)
        if _DAY_DATE_RE.match(value):
            return value
    if isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        v = float(value)
        if 5e8 < v < 1e9:
            return ts_cocoa(v)
        if 1e9 <= v < 1e13:
            return ts_unix(v)
    return ""


def _fmt_mac(value):
    """'A038F8C6B6AB' -> 'A0:38:F8:C6:B6:AB' (ring IDs are BLE MAC addresses)."""
    s = str(value)
    if _MAC_RE.match(s):
        return ":".join(s[i:i + 2] for i in range(0, 12, 2)).upper()
    return s


def _load_oura_plists(files_found):
    """Load the plists in the Oura app's own Preferences dir, keyed by filename.

    The companion search patterns (com.segment.storage.*, com.zendesk.*, the
    account-UID plist) also match same-named SDK plists inside other apps'
    containers, so only files sitting next to the Oura-specific
    com.ouraring.oura.plist are parsed. Without that anchor the Oura app is
    not in the extraction and nothing is returned.
    """
    bundle_path = get_file_path(files_found, "com.ouraring.oura.plist")
    if not bundle_path:
        return {}, {}
    pref_dir = os.path.dirname(str(bundle_path))

    data_by_name, path_by_name = {}, {}
    for file_found in files_found:
        fp = str(file_found)
        if not fp.endswith(".plist") or os.path.dirname(fp) != pref_dir:
            continue
        try:
            with open(fp, "rb") as fh:
                data = plistlib.load(fh)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logfunc(f"Oura: failed to parse {fp}: {exc}")
            continue
        name = os.path.basename(fp)
        data_by_name[name] = data
        path_by_name[name] = fp
    return data_by_name, path_by_name


def _suite_plist(data_by_name, path_by_name):
    """The account 'suite' plist: the big one, found by its deviceUid key."""
    for name, data in data_by_name.items():
        if isinstance(data, dict) and "deviceUid" in data:
            return data, path_by_name.get(name, name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    return bundle, path_by_name.get("com.ouraring.oura.plist", "")


def _segment_plist(data_by_name, path_by_name):
    """Oura's Segment SDK storage plist -> (data, full path)."""
    for name, data in data_by_name.items():
        if name.startswith("com.segment.storage.") and isinstance(data, dict):
            return data, path_by_name.get(name, "")
    return {}, ""


def _decode_nsdecimal(value):
    """NSDecimalNumber struct -> number. mantissa is little-endian 16-bit words,
    value = mantissa * 10**exponent, negated when isNegative."""
    try:
        mantissa = 0
        for i, word in enumerate(value.get("mantissa") or []):
            mantissa += int(word) << (16 * i)
        number = mantissa * (10 ** int(value.get("exponent", 0)))
        if value.get("isNegative"):
            number = -number
        if isinstance(number, float) and number.is_integer():
            number = int(number)
        return number
    except (TypeError, ValueError):
        return value


def _decode(value, depth=0):
    """Any plist value -> plain JSON-safe Python.

    Unwraps nested bplists and JSON hiding in bytes/str, NSDecimalNumber, NSDate
    and UID. Real binary that's none of those becomes base64.
    """
    if depth > 15:
        return value

    if isinstance(value, bytes):
        if value[:8] == b"bplist00":
            try:
                return _decode(plistlib.loads(value), depth + 1)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(value).decode("ascii")
        if text.lstrip()[:1] in "{[":
            try:
                return _decode(json.loads(text), depth + 1)
            except (ValueError, TypeError):
                pass
        return text

    if isinstance(value, str):
        if value.lstrip()[:1] in "{[":
            try:
                return _decode(json.loads(value), depth + 1)
            except (ValueError, TypeError):
                pass
        return value

    if isinstance(value, dict):
        if "mantissa" in value and "exponent" in value:
            return _decode_nsdecimal(value)
        return {k: _decode(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [_decode(v, depth + 1) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, plistlib.UID):
        return value.data
    return value


def _jload(value):
    """_decode, but keep the result only if it's a dict or list."""
    decoded = _decode(value)
    return decoded if isinstance(decoded, (dict, list)) else None


def _cell(value):
    """Value -> report cell text. Lists comma-joined, dicts compact JSON,
    control characters flattened so TSV/HTML stay one-row-per-record."""
    if isinstance(value, list):
        text = ", ".join(str(x) for x in value)
    elif isinstance(value, dict):
        text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    else:
        text = str(value)
    return text.replace("\r", " ").replace("\n", " ").replace("\t", " ")


def _dig(obj, path):
    """Follow a dotted path down nested dicts. None if it dead-ends."""
    for part in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def _is_empty(value):
    return value is None or value == "" or value == [] or value == {}


def _braze(suite):
    return _jload(suite.get("brazeUserAttributesV2")) or {}


def _traits(segment):
    return _jload(segment.get("segment.traits")) or {}


def _ring_ids(suite):
    """Ring BLE MACs: the dict keys inside the per-ring status blobs."""
    ids = []
    for key in ("batteryLevelRecords", "ringLowBatteryNotifications",
                "latestRingTimeMappingsRingEventParser",
                "latestRingTimeMappingsRingEventParserV2",
                "ringParametersDict"):
        obj = _jload(suite.get(key))
        if isinstance(obj, dict):
            inner = obj.get("records") or obj.get("notifications") or obj
            if isinstance(inner, dict):
                for ring in inner.keys():
                    if _MAC_RE.match(str(ring)) and ring not in ids:
                        ids.append(ring)
    return ids


# ---------------------------------------------------------------------------
# Claimed-key registry. A suite/bundle key must appear here (or produce an App
# Activity Timeline row) to stay out of the residue artifact; braze/traits
# sub-keys claimed by topical artifacts are listed so the leftovers can be
# reported as 'Other' profile rows. Update these when adding extractions.
# ---------------------------------------------------------------------------
_CLAIMED_SUITE = frozenset((
    # identity
    "accountEmail", "accountUid", "deviceUid", "com.apple.DC.AppAttestAppUUID",
    "brazeUserAttributesV2",
    # ring hardware
    "batteryLevelRecords", "ringLowBatteryNotifications",
    "latestRingTimeMapping", "latestRingTimeMappingRingEventParser",
    "latestRingTimeMappingRingTimeResolverV2",
    "latestRingTimeMappingsRingEventParser",
    "latestRingTimeMappingsRingEventParserV2",
    "ringParameters", "ringParametersDict",
    "findMyRingLastKnownRingState", "findMyRingLastKnownRingSeenDate",
    "lastUpdatedFirmwareDate", "shouldInvalidateTimeOnNextRingStart",
    "isForcedUserInfoInRing", "hasSeenFirmwareUpdateInfoCount",
    # location
    "findMyRingLastKnownLocation", "lastLocationTimestamp",
    # health profile
    "pendingUserSettingsUpdates", "defaultActivityDurations",
    "defaultActivityIntensities", "recentActivities",
    "previousActivityGoalProgress", "sleepChart/hrPercentileRange",
    "sleepChart/hrvPercentileRange", "heartHealth/algorithmUpdateDates",
    "heartHealth/algorithmUpdateVersions", "metabolic/hasGlp1Tag",
    "biomarkers/appointmentsPendingResults", "hasAnsweredMindfulnessPrompt",
    "shareReportPrivacyConsentGranted",
    # widget snapshot
    "widgetInfo",
    # connected services
    "healthKit/listOfTypesReadAuthorizationHasBeenPrompted",
    "healthKit/listOfTypesWriteAuthorizationHasBeenPrompted",
    "healthKitImportedSampleAnchorsByType", "healthKitExportedSleepDay",
    "healthKitAccessAsked", "healhtKitRespiratoryAccessAsked",
    "installedWidgets", "isNotificationsPermissionAsked", "CarCapabilities",
    # app environment
    "AppleLocale", "AppleLanguages", "AppleKeyboards", "ApplePasscodeKeyboards",
    "AppleLanguagesDidMigrate", "AppleLanguagesSchemaVersion",
    "SEGVersionKey", "SEGBuildKeyV2", "latestAppDetails", "latestAppUpdate",
    "lastDatabaseMigrationBuildNumber", "assaCurrentMigrationVersion",
    "remainingFreeDiskSpaceInBytes", "lastNetworkStatusIsSatisfied",
    "blePrivacyActivationSuccessful", "wasDismissedBlePrivacyActivationInfo",
    "userInformationAsked",
    "hasMigratedFromStandardToSuitNameUserDefaults",
    "hasMigratedPregnancyEnrollmentEndTimezone",
    "hasResetChargerSyncSettingsMigration",
    "hasRunCorruptChargerDebugInfoRecordsRemovalMigration",
    "hasRunCorruptImportedHeartRateRemovalMigration", "hasFixedImportedStepCount",
    # content & campaigns
    "blogPosts", "babyCenterArticles", "bloodPressureInPregnancyBlogPosts",
    "bloodPressureProfileBlogPosts", "glucoseGraphBlogPosts",
    "heartHealthBlogPosts", "metabolicHealthBlogPosts", "perimenopauseBlogPosts",
    "reproductiveHealthBlogPosts", "stressManagementBlogPosts",
    "blogPostsUpdatedAt", "lastDismissedBlogPostSlug",
    "currentCampaignIdentifier", "currentCampaignArrivalDate",
    "didUserInteractWithCampaign", "identifierOfLastDismissedCampaign",
    "stress/exploreLatestPlayedStory", "stress/latestExploreSessionChangeDay",
    "stress/latestExploreSessionReason", "discovery_hub/new_discoveries_ids",
    "introducedCategories", "introducedContributors", "onboardedCategories",
    "ctp/lastRequestedDay",
))

_CLAIMED_BUNDLE = frozenset((
    "accountEmail", "accountUid", "SEGVersionKey", "SEGBuildKeyV2",
    "lastBackgroundDate", "lastTokenRefreshTime",
))

_CLAIMED_BRAZE = frozenset((
    "userEmail", "age", "gender", "chosenCountryOfResidence", "currentRing",
    "ringColor", "ringDesign", "ringModel", "currentSleep",
    "cycleInsightsEnabled", "cycleInsightsHormones", "cyclePhasesEnabled",
    "glucoseSensorActive", "hideCalories", "isHipaa",
    "isMenopauseImpactScaleOn", "language", "circleMember",
    "firstActivitySummaryDate",
))

_CLAIMED_TRAITS = frozenset((
    # identity
    "email",
    # ring hardware
    "currentRing", "ringColor", "ringDesign", "ringModel", "ringSize",
    "ringFirmwareVersion", "automaticFwUpdateEnabled",
    "chargerFirmwareVersions", "chargingCaseModel",
    # health profile
    "age", "gender", "height", "weight", "chosenCountryOfResidence",
    "membershipStatus", "currentSleep", "sleepDetractors",
    "cycleInsightsEnabled", "cycleInsightsHormones", "cyclePhasesEnabled",
    "fertileWindowShown", "gestationalAgeDays", "misEnabled",
    "periodLoggingReminderDays", "periodPredictionOptIn",
    "selectedGlucoseTargetRange", "glucoseSensorActive", "spo2enabled",
    "hideCalories", "movementGoalOption", "movementGoalPercentage",
    "commonActivities", "newSleepStagingEnabled", "circleMember",
    "circleSizes", "numberOfCircles", "firstActivitySummaryDate",
    "isHipaa",
    # connected services
    "appConnections", "ehrConnected", "enterpriseOrganizationIDs",
    "enterpriseProducts", "enabledNotificationsApp", "availableLocalLLMs",
    "locationEnabled", "stepMotionUploadsEnabled", "pdfImported",
    # app environment
    "appFlavor", "language", "biometricLockStatus",
    # feature flags
    "enabledFeatureFlagsApp", "enabledFeatureFlagsAppParameters",
    "ouraLabsFeaturesAvailable", "ouraLabsFeaturesInTesting",
    "blackoutModeFeatures",
))

# nicer names for the timestamp keys we know about; anything else falls through
# under its raw key.
_ACTIVITY_LABELS = {
    "lastAppLaunchDate": "Last app launch",
    "lastBackgroundDate": "Last background",
    "firstForegroundSyncDateForToday": "First foreground sync (today)",
    "latestTimeseriesCleanupTime": "Time-series cleanup",
    "exploreTabLastVisitedAt": "Explore tab last visited",
    "appUx/welcomeMessageFirstSeen": "Welcome message first seen",
    "currentCampaignArrivalDate": "Campaign arrival",
    "lastOuraAnniversaryGenerationTimestamp": "Anniversary generated",
    "uploader.last_upload_timestamp.debuglog": "Last debug-log upload",
    "blogPostsUpdatedAt": "Blog posts updated",
    "lastLocationTimestamp": "Last location recorded",
    "circles/lastLoadedAt": "Circles last loaded",
    "lastSyncDate": "Last sync",
    "lastForegroundSyncDate": "Last foreground sync",
    "lastTokenRefreshTime": "Auth token refreshed",
    "heartHealth/lastPPGFeatureSessionEndTimestamp": "PPG (heart) feature session ended",
    "heartHealth/lastProcessedPPGSampleTimestamp": "Last PPG (heart) sample processed",
    "heartHealth/lastProcessedPPGFoundationTimestamp": "Last PPG foundation model run",
    "heartHealth/lastProcessedBloodPressureAlgorithmTimestamp":
        "Blood-pressure algorithm run",
    "heartHealth/heartCheckinTipFirstDisplayedAtDate": "Heart check-in tip first shown",
    "healthRadar/promoFirstDisplayedDate": "Health Radar promo first shown",
    "healthRecords/labsIntroFirstDisplayedDate": "Labs intro first shown",
    "stress/stressSensingCalculationsLastPerformed": "Stress-sensing calculation",
    "stress/stressSensingCalculationsLastPerformedTriggeringDailyStressUpdate":
        "Stress-sensing daily update",
    "stress/stressLastSealedClusterEnd": "Stress cluster sealed",
    "stress/latestExploreSessionChangeDay": "Explore stress session day",
    "timelineSessionIndexUpdatedAt": "Timeline session updated",
    "updateProfileReminderCardDisplayedDate": "Profile-update reminder shown",
    "lastUpdatedFirmwareDate": "Firmware updated",
    "findMyRingLastKnownRingSeenDate": "Ring last seen",
    "healthKitExportedSleepDay": "Last sleep day exported to HealthKit",
    "resilience/mostRecentResilienceAlgorithmRunDay": "Resilience algorithm run day",
    "ctp/lastRequestedDay": "Content last requested day",
}

# cocoa timestamps hiding inside the JSON blobs: (container, dotted path, label)
_NESTED_ACTIVITY = (
    ("latestAppUpdate", "updatedAt", "App updated"),
    ("latestAppDetails", "currentVersionReleaseDate", "App version released"),
    ("widgetInfo", "metadata.updatedAt", "Widget refreshed"),
    ("brazeUserAttributesV2", "firstActivitySummaryDate", "First activity summary"),
)


def _timeline_when(key, value):
    """Timestamp string if this key/value belongs on the activity timeline."""
    if key.startswith(_OS_PREFIXES) or key in ("SEGVersionKey", "SEGBuildKeyV2"):
        return ""
    dateish = (isinstance(value, datetime)
               or (isinstance(value, str)
                   and (_ISO_DATE_RE.match(value) or _DAY_DATE_RE.match(value)))
               or (isinstance(value, (int, float)) and not isinstance(value, bool)
                   and _DATEISH_KEY_RE.search(key)))
    return ts_auto(value) if dateish else ""


def _zendesk_account(data_by_name):
    """Decode com.zendesk.core.account.plist -> (help center URL, app id)."""
    z_account = data_by_name.get("com.zendesk.core.account.plist", {})
    raw = z_account.get("account-id") if isinstance(z_account, dict) else None
    if not raw:
        return "", ""
    try:
        decoded = base64.b64decode(raw).decode("utf-8", "replace")
    except Exception:  # pylint: disable=broad-exception-caught
        return _cell(raw), ""
    match = re.match(r"^(.*?)([0-9a-f]{40,64})$", decoded)
    if match:
        return match.group(1), match.group(2)
    return decoded, ""


# ---------------------------------------------------------------------------
# artifact 1: account & identifiers
# ---------------------------------------------------------------------------
@artifact_processor
def oura_account_identifiers(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    bundle_path = path_by_name.get("com.ouraring.oura.plist", "")
    braze = _braze(suite)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)

    rows, sources = [], []

    def add(category, attribute, value, src):
        if _is_empty(value):
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((category, attribute, _cell(value), context.get_relative_path(src)))

    def pick(*candidates):
        for obj, key, path in candidates:
            value = obj.get(key)
            if not _is_empty(value):
                return value, path
        return None, ""

    add("Account", "Email",
        *pick((suite, "accountEmail", suite_path),
              (bundle, "accountEmail", bundle_path),
              (braze, "userEmail", suite_path)))
    add("Account", "Account UID",
        *pick((suite, "accountUid", suite_path), (bundle, "accountUid", bundle_path)))
    add("Account", "Device UID", suite.get("deviceUid"), suite_path)

    add("Apple", "App-Attest UUID", suite.get("com.apple.DC.AppAttestAppUUID"),
        suite_path)

    add("Segment", "User ID", segment.get("segment.userId"), segment_path)
    add("Segment", "Anonymous ID", segment.get("segment.anonymousId"), segment_path)

    url, app_id = _zendesk_account(data_by_name)
    z_account_path = path_by_name.get("com.zendesk.core.account.plist", "")
    add("Zendesk", "Help Center URL", url, z_account_path)
    add("Zendesk", "Application ID", app_id, z_account_path)

    z_identity = data_by_name.get("com.zendesk.core.identity.plist", {})
    z_identity_path = path_by_name.get("com.zendesk.core.identity.plist", "")
    if isinstance(z_identity, dict):
        for ident_val in z_identity.values():
            if not isinstance(ident_val, dict):
                continue
            add("Zendesk", "User ID", ident_val.get("user_id"), z_identity_path)
            add("Zendesk", "Device UUID", ident_val.get("uuid"), z_identity_path)
            add("Zendesk", "Auth Token", ident_val.get("auth_token"), z_identity_path)
            add("Zendesk", "Identity JWT", _dig(ident_val, "identity.jwt.token"),
                z_identity_path)

    z_settings = _jload(data_by_name.get("com.zendesk.core.settings.plist")) or {}
    z_settings_path = path_by_name.get("com.zendesk.core.settings.plist", "")
    if isinstance(z_settings, dict):
        for settings_val in z_settings.values():
            settings_val = _jload(settings_val) if not isinstance(settings_val, dict) \
                else settings_val
            if not isinstance(settings_val, dict):
                continue
            add("Zendesk", "Brand ID", _dig(settings_val, "core.brand_id"),
                z_settings_path)
            add("Zendesk", "Config Updated", ts_iso(_dig(settings_val, "core.updated_at")),
                z_settings_path)
            add("Zendesk", "SDK-Counted App Visits", _dig(settings_val, "rma.visits"),
                z_settings_path)

    z_session = data_by_name.get("com.zendesk.core.session.plist", {})
    z_session_path = path_by_name.get("com.zendesk.core.session.plist", "")
    if isinstance(z_session, dict):
        for sess_val in z_session.values():
            if isinstance(sess_val, dict):
                add("Zendesk", "Push Token", sess_val.get("pushToken"), z_session_path)

    data_headers = ("Category", "Attribute", "Value", "Source File")
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 2: ring hardware & status
# ---------------------------------------------------------------------------
@artifact_processor
def oura_ring_hardware(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    braze = _braze(suite)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    traits = _traits(segment)
    rings = _ring_ids(suite)
    default_ring = _fmt_mac(rings[0]) if rings else ""

    rows, sources = [], []

    def add(when, ring, item, value, details, src):
        if _is_empty(value) and _is_empty(details) and not when:
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((when, ring, item, _cell(value), _cell(details) if details else "",
                     context.get_relative_path(src)))

    def pick(*candidates):
        for obj, key, path in candidates:
            value = obj.get(key)
            if not _is_empty(value):
                return value, path
        return None, ""

    model = braze.get("ringModel")
    if isinstance(model, list):
        add("", default_ring, "Model", ", ".join(str(m) for m in model), "", suite_path)
    else:
        value, src = pick((braze, "currentRing", suite_path),
                          (traits, "currentRing", segment_path))
        add("", default_ring, "Model", value, "", src)
    for label, key in (("Color", "ringColor"), ("Design", "ringDesign")):
        value, src = pick((braze, key, suite_path), (traits, key, segment_path))
        add("", default_ring, label, value, "", src)
    add("", default_ring, "Size", traits.get("ringSize"), "", segment_path)
    add("", default_ring, "Firmware Version", traits.get("ringFirmwareVersion"), "",
        segment_path)
    add("", default_ring, "Automatic Firmware Update",
        traits.get("automaticFwUpdateEnabled"), "", segment_path)
    add("", default_ring, "Charger Firmware Versions",
        traits.get("chargerFirmwareVersions"), "", segment_path)
    add("", default_ring, "Charging Case Model", traits.get("chargingCaseModel"), "",
        segment_path)

    battery = _jload(suite.get("batteryLevelRecords")) or {}
    for ring, rec in (battery.get("records") or {}).items():
        if isinstance(rec, dict):
            add(ts_cocoa(rec.get("lastUpdated")), _fmt_mac(ring),
                "Battery level recorded", rec.get("batteryLevel"), "percent",
                suite_path)

    low = _jload(suite.get("ringLowBatteryNotifications")) or {}
    for ring, note in (low.get("notifications") or {}).items():
        if isinstance(note, dict):
            add(ts_cocoa(note.get("ringNotificationDate")), _fmt_mac(ring),
                "Low-battery notification", note.get("batteryLevel"),
                f"hoursToEmpty={note.get('hoursToEmpty', '')} type={note.get('type', '')}",
                suite_path)

    # every ring/UTC time mapping variant the app keeps
    mapping = _jload(suite.get("latestRingTimeMapping"))
    if isinstance(mapping, dict):
        add(ts_unix(mapping.get("utcTime")), default_ring, "Ring/UTC time mapping",
            f"ringTime={mapping.get('ringTime', '')}", "latestRingTimeMapping",
            suite_path)
    mapping = _jload(suite.get("latestRingTimeMappingRingEventParser"))
    if isinstance(mapping, dict):
        add(ts_unix(mapping.get("utcTime")), default_ring, "Ring/UTC time mapping",
            f"ringTime={mapping.get('ringTime', '')}",
            "latestRingTimeMappingRingEventParser", suite_path)
    mapping = _jload(suite.get("latestRingTimeMappingRingTimeResolverV2"))
    if isinstance(mapping, dict):
        add(ts_unix(mapping.get("utcTime")), default_ring, "Ring/UTC time mapping",
            f"ringTime={mapping.get('ringTime', '')}",
            "latestRingTimeMappingRingTimeResolverV2 "
            f"lowBatteryReboot={mapping.get('lowBatteryReboot', '')}", suite_path)
    for blob_key in ("latestRingTimeMappingsRingEventParser",
                     "latestRingTimeMappingsRingEventParserV2"):
        per_ring = _jload(suite.get(blob_key))
        if isinstance(per_ring, dict):
            for ring, mapping in per_ring.items():
                if isinstance(mapping, dict):
                    extra = "" if "lowBatteryReboot" not in mapping else \
                        f" lowBatteryReboot={mapping.get('lowBatteryReboot')}"
                    add(ts_unix(mapping.get("utcTime")), _fmt_mac(ring),
                        "Ring/UTC time mapping",
                        f"ringTime={mapping.get('ringTime', '')}",
                        blob_key + extra, suite_path)

    params = _jload(suite.get("ringParameters"))
    if isinstance(params, dict):
        add("", default_ring, "PPG sensor parameters", params, "ringParameters",
            suite_path)
    params_by_ring = _jload(suite.get("ringParametersDict"))
    if isinstance(params_by_ring, dict):
        for ring, params in params_by_ring.items():
            add("", _fmt_mac(ring), "PPG sensor parameters", params,
                "ringParametersDict", suite_path)

    if suite.get("lastUpdatedFirmwareDate"):
        add(ts_iso(suite.get("lastUpdatedFirmwareDate")), default_ring,
            "Firmware updated", "", "", suite_path)
    if suite.get("findMyRingLastKnownRingSeenDate"):
        add(ts_iso(suite.get("findMyRingLastKnownRingSeenDate")), default_ring,
            "Ring last seen", "", "", suite_path)
    if not _is_empty(suite.get("findMyRingLastKnownRingState")):
        add("", default_ring, "Find My Ring last known state (raw)",
            suite.get("findMyRingLastKnownRingState"), "", suite_path)
    add("", default_ring, "Invalidate time on next ring start",
        _decode(suite.get("shouldInvalidateTimeOnNextRingStart")), "", suite_path)
    add("", default_ring, "User info written to ring",
        suite.get("isForcedUserInfoInRing"), "", suite_path)
    add("", default_ring, "Firmware-update info shown (count)",
        suite.get("hasSeenFirmwareUpdateInfoCount"), "", suite_path)

    rows.sort(key=lambda r: r[0], reverse=True)
    data_headers = (
        ("Timestamp", "datetime"),
        "Ring (BLE MAC)",
        "Item",
        "Value",
        "Details",
        "Source File",
    )
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 3: find my ring location
# ---------------------------------------------------------------------------
@artifact_processor
def oura_find_my_ring_location(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)

    data_list = []
    loc = _jload(suite.get("findMyRingLastKnownLocation"))
    if isinstance(loc, dict) and "latitude" in loc and "longitude" in loc:
        lat = loc.get("latitude", "")
        lon = loc.get("longitude", "")
        map_link = (f'<a href="https://www.google.com/maps?q={esc(lat)},{esc(lon)}" '
                    f'target="_blank">View on map</a>') if lat != "" and lon != "" else ""
        data_list.append((
            ts_cocoa(loc.get("timestamp")),
            lat,
            lon,
            loc.get("altitude", ""),
            loc.get("horizontalAccuracy", ""),
            loc.get("verticalAccuracy", ""),
            loc.get("speed", ""),
            loc.get("speedAccuracy", ""),
            loc.get("course", ""),
            loc.get("courseAccuracy", ""),
            map_link,
            "findMyRingLastKnownLocation",
        ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Latitude",
        "Longitude",
        "Altitude (m)",
        "Horizontal Accuracy (m)",
        "Vertical Accuracy (m)",
        "Speed (m/s)",
        "Speed Accuracy (m/s)",
        "Course",
        "Course Accuracy",
        "Map",
        "Source Key",
    )
    return data_headers, data_list, source if data_list else ""


# ---------------------------------------------------------------------------
# artifact 4: health profile & disclosures
# ---------------------------------------------------------------------------
@artifact_processor
def oura_health_profile(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    braze = _braze(suite)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    traits = _traits(segment)
    widget = _jload(suite.get("widgetInfo")) or {}

    rows, sources = [], []

    def add(category, attribute, value, src, details=""):
        if _is_empty(value):
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((category, attribute, _cell(value),
                     _cell(details) if details else "",
                     context.get_relative_path(src)))

    def pick(*candidates):
        for obj, key, path in candidates:
            value = obj.get(key)
            if not _is_empty(value):
                return value, path
        return None, ""

    value, src = pick((traits, "age", segment_path), (braze, "age", suite_path))
    add("Demographics", "Age", value, src)
    value, src = pick((traits, "gender", segment_path), (braze, "gender", suite_path))
    add("Demographics", "Gender", value, src)
    value, src = pick((traits, "chosenCountryOfResidence", segment_path),
                      (braze, "chosenCountryOfResidence", suite_path))
    add("Demographics", "Country of Residence", value, src)
    add("Demographics", "Membership Status", traits.get("membershipStatus"),
        segment_path)
    value, src = pick((traits, "isHipaa", segment_path), (braze, "isHipaa", suite_path))
    add("Demographics", "HIPAA Account", value, src)

    height = traits.get("height")
    if not _is_empty(height):
        try:
            detail = f"~{float(height) * 3.28084:.1f} ft"
        except (TypeError, ValueError):
            detail = ""
        add("Body", "Height (m)", height, segment_path, detail)
    weight = traits.get("weight")
    if not _is_empty(weight):
        try:
            detail = f"~{float(weight) * 2.20462:.1f} lb"
        except (TypeError, ValueError):
            detail = ""
        add("Body", "Weight (kg)", weight, segment_path, detail)

    value, src = pick((traits, "currentSleep", segment_path),
                      (braze, "currentSleep", suite_path))
    add("Sleep", "Self-Reported Sleep Status", value, src)
    add("Sleep", "Self-Reported Sleep Detractors", traits.get("sleepDetractors"),
        segment_path)
    add("Sleep", "New Sleep Staging Enabled", traits.get("newSleepStagingEnabled"),
        segment_path)
    add("Sleep", "Nightly HR Percentile Range",
        _jload(suite.get("sleepChart/hrPercentileRange")), suite_path)
    add("Sleep", "Nightly HRV Percentile Range",
        _jload(suite.get("sleepChart/hrvPercentileRange")), suite_path)

    for label, key in (("Cycle Insights Enabled", "cycleInsightsEnabled"),
                       ("Cycle Insights Hormones", "cycleInsightsHormones"),
                       ("Cycle Phases Enabled", "cyclePhasesEnabled"),
                       ("Fertile Window Shown", "fertileWindowShown"),
                       ("Period Prediction Opt-In", "periodPredictionOptIn"),
                       ("Period Logging Reminder (days)", "periodLoggingReminderDays"),
                       ("Menopause Impact Scale Enabled", "misEnabled")):
        value, src = pick((traits, key, segment_path), (braze, key, suite_path))
        add("Cycle & Reproductive", label, value, src)
    gest = traits.get("gestationalAgeDays")
    if not _is_empty(gest) and gest != -1:
        add("Cycle & Reproductive", "Gestational Age (days)", gest, segment_path)

    value, src = pick((traits, "glucoseSensorActive", segment_path),
                      (braze, "glucoseSensorActive", suite_path))
    add("Glucose & Metabolic", "Glucose Sensor Active", value, src)
    add("Glucose & Metabolic", "Selected Glucose Target Range",
        traits.get("selectedGlucoseTargetRange"), segment_path)
    add("Glucose & Metabolic", "GLP-1 Medication Tag",
        suite.get("metabolic/hasGlp1Tag"), suite_path)

    add("Heart Health", "SpO2 Enabled", traits.get("spo2enabled"), segment_path)
    add("Heart Health", "Algorithm Versions",
        _jload(suite.get("heartHealth/algorithmUpdateVersions")), suite_path)
    add("Heart Health", "Algorithm Update Dates",
        suite.get("heartHealth/algorithmUpdateDates"), suite_path)
    add("Heart Health", "Biomarker Appointments Pending Results",
        suite.get("biomarkers/appointmentsPendingResults"), suite_path)

    add("Activity", "Movement Goal", traits.get("movementGoalOption"), segment_path)
    add("Activity", "Movement Goal (%)", traits.get("movementGoalPercentage"),
        segment_path)
    add("Activity", "Common Activities", traits.get("commonActivities"), segment_path)
    add("Activity", "Recently Logged Activities", suite.get("recentActivities"),
        suite_path)
    add("Activity", "Default Activity Durations (min)",
        _jload(suite.get("defaultActivityDurations")), suite_path)
    add("Activity", "Default Activity Intensities",
        _jload(suite.get("defaultActivityIntensities")), suite_path)
    add("Activity", "Previous Goal Progress",
        suite.get("previousActivityGoalProgress"), suite_path)
    value, src = pick((traits, "hideCalories", segment_path),
                      (braze, "hideCalories", suite_path))
    add("Activity", "Hide Calories", value, src)

    value, src = pick((traits, "circleMember", segment_path),
                      (braze, "circleMember", suite_path))
    add("Circles (Social)", "Circle Member", value, src)
    add("Circles (Social)", "Number of Circles", traits.get("numberOfCircles"),
        segment_path)
    add("Circles (Social)", "Circle Sizes", traits.get("circleSizes"), segment_path)

    add("Consents", "Share-Report Privacy Consent",
        suite.get("shareReportPrivacyConsentGranted"), suite_path)
    add("Consents", "Mindfulness Prompt Answered",
        _decode(suite.get("hasAnsweredMindfulnessPrompt")), suite_path)
    add("Consents", "Pending Profile Sync Flags",
        _jload(suite.get("pendingUserSettingsUpdates")), suite_path)

    add("Milestones", "First Activity Summary",
        ts_auto(traits.get("firstActivitySummaryDate")
                or braze.get("firstActivitySummaryDate")), segment_path)

    user = widget.get("user") if isinstance(widget, dict) else None
    if isinstance(user, dict):
        add("Account State", "Churned Member", user.get("isChurned"), suite_path)
        add("Account State", "HIPAA Mode Enabled (widget)",
            user.get("isHipaaEnabled"), suite_path)

    # every braze/traits key not claimed by a topical artifact still gets a row
    for profile_dict, profile_path, claimed in (
            (braze, suite_path, _CLAIMED_BRAZE),
            (traits, segment_path, _CLAIMED_TRAITS)):
        for key in sorted(profile_dict.keys()):
            if key in claimed:
                continue
            add("Other Profile Trait", key, _cell(profile_dict[key]), profile_path)

    data_headers = ("Category", "Attribute", "Value", "Details", "Source File")
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 5: health data snapshot (widgetInfo)
# ---------------------------------------------------------------------------
@artifact_processor
def oura_health_snapshot(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)
    widget = _jload(suite.get("widgetInfo")) or {}
    if not isinstance(widget, dict) or not widget:
        return (("Timestamp", "datetime"), "Category", "Metric", "Value",
                "Details"), [], ""

    rows = []
    day = widget.get("dayString", "")

    def add(when, category, metric, value, details=""):
        if _is_empty(value) and _is_empty(details):
            return
        rows.append((when, category, metric, _cell(value),
                     _cell(details) if details else ""))

    add("", "Snapshot", "Cached Day", day)
    meta = widget.get("metadata") or {}
    if meta.get("updatedAt"):
        add(ts_cocoa(meta.get("updatedAt")), "Snapshot", "Widget Refreshed",
            f"update #{meta.get('updateCountToday', '?')} that day")

    battery = widget.get("battery") or {}
    add(ts_cocoa(battery.get("updatedAt")), "Ring Battery", "Level (%)",
        battery.get("level"),
        f"charging={battery.get('isCharging')} needsCharging={battery.get('needsCharging')}")

    activity = widget.get("activity") or {}
    goal = activity.get("goalProgress") or {}
    add("", "Activity", "Steps", goal.get("steps"), f"day {day}")
    add("", "Activity", "Active Calories", goal.get("activeCalories"),
        f"target {goal.get('targetCalories', '')} kcal, goal type "
        f"{goal.get('selectedGoal', '')}, target steps {goal.get('targetSteps', '')}")
    add("", "Activity", "Activity Score", activity.get("score"), f"day {day}")
    add("", "Activity", "Rest Mode Active", activity.get("isRestModeActive"))
    intensity = activity.get("intensityChartInfo") or {}
    intervals = intensity.get("intervals") or []
    start = intensity.get("intervalsStart")
    length_min = intensity.get("intervalLengthInMinutes") or 30
    if start and intervals:
        add("", "Movement Intensity", "Active Minutes",
            intensity.get("activeMinutes"), f"day {day}")
        for i, val in enumerate(intervals):
            if val is None:
                continue
            try:
                when = ts_cocoa(float(start) + i * length_min * 60)
                add(when, "Movement Intensity", f"{length_min}-min interval",
                    round(float(val), 3))
            except (TypeError, ValueError):
                continue

    hr = widget.get("daytimeHeartRate") or {}
    if isinstance(hr, dict) and hr:
        add(ts_cocoa(hr.get("mostRecentEntryDate")), "Daytime Heart Rate",
            "Most Recent HR (bpm)", hr.get("mostRecentHeartRate"),
            f"window {ts_cocoa(hr.get('startDate'))} - {ts_cocoa(hr.get('endDate'))}")
        add("", "Daytime Heart Rate", "Window Min HR (bpm)", hr.get("minHeartRate"))
        add("", "Daytime Heart Rate", "Window Max HR (bpm)", hr.get("maxHeartRate"))
        for group in hr.get("timeseriesGroups") or []:
            if not isinstance(group, dict):
                continue
            clusters = [c for c in (group.get("clusters") or [])
                        if isinstance(c, dict)]
            if group.get("average") is None and not clusters:
                continue
            detail = "; ".join(
                f"{c.get('type', '')} {c.get('min', '')}-{c.get('max', '')} bpm"
                for c in clusters)
            avg = group.get("average")
            add(ts_cocoa(group.get("startDate")), "Daytime Heart Rate",
                "Window Average (bpm)",
                round(avg, 1) if isinstance(avg, (int, float)) else avg, detail)

    stress = widget.get("dailyStress") or {}
    if isinstance(stress, dict) and stress:
        add("", "Stress", "Enabled", stress.get("isEnabled"),
            f"calibrated={stress.get('isCalibrationPeriodOver')}")
        add("", "Stress", "Stressed Duration (s)", stress.get("stressedDuration"),
            f"day {day}")
        add("", "Stress", "Restored Duration (s)", stress.get("restoredDuration"),
            f"day {day}")
        intensity_scaled = stress.get("currentIntensityScaled")
        add("", "Stress", "Current Intensity (0-1)",
            round(intensity_scaled, 4)
            if isinstance(intensity_scaled, (int, float)) else intensity_scaled,
            f"latest sample (device-local time) "
            f"{stress.get('latestStressSampleTimestampStringForToday', '')}")

    temp = widget.get("temperature") or {}
    if isinstance(temp, dict) and temp:
        add("", "Temperature Deviation", "Range",
            f"{temp.get('minValueString', '')} to {temp.get('maxValueString', '')}",
            f"unit={temp.get('unit', '')} last night={temp.get('lastNightValueString', '')}")
        values = temp.get("values") or []
        if any(v is not None for v in values):
            add("", "Temperature Deviation", "Series (stored order)",
                ", ".join("-" if v is None else str(round(v, 2)) for v in values),
                f"{len(values)} entries ending {day}")

    scores = widget.get("pastDayScores") or {}
    for metric in sorted(scores.keys() if isinstance(scores, dict) else []):
        series = scores[metric]
        if isinstance(series, list) and any(v is not None for v in series):
            add("", "Past Day Scores", metric.capitalize(),
                ", ".join("-" if v is None else str(v) for v in series),
                "stored order, most recent day first")

    blackout = widget.get("blackout") or {}
    if isinstance(blackout, dict) and blackout.get("enabled"):
        add("", "Snapshot", "Blackout Mode", blackout.get("enabled"),
            _cell(blackout.get("features")))

    tz = _dig(widget, "timeZone.identifier")
    add("", "Snapshot", "Device Time Zone", tz)

    data_headers = (
        ("Timestamp", "datetime"),
        "Category",
        "Metric",
        "Value",
        "Details",
    )
    return data_headers, rows, source


# ---------------------------------------------------------------------------
# artifact 6: connected services & permissions
# ---------------------------------------------------------------------------
@artifact_processor
def oura_connected_services(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    traits = _traits(segment)

    rows, sources = [], []

    def add(category, item, value, src, details=""):
        if _is_empty(value):
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((category, item, _cell(value), _cell(details) if details else "",
                     context.get_relative_path(src)))

    for conn in traits.get("appConnections") or []:
        add("App Connection", conn, "connected", segment_path)
    add("App Connection", "EHR (health records)", traits.get("ehrConnected"),
        segment_path)
    add("App Connection", "PDF Imported", traits.get("pdfImported"), segment_path)
    add("Enterprise", "Organization IDs", traits.get("enterpriseOrganizationIDs"),
        segment_path)
    add("Enterprise", "Products", traits.get("enterpriseProducts"), segment_path)

    for hk_key, label in (
            ("healthKit/listOfTypesReadAuthorizationHasBeenPrompted",
             "HealthKit Read Prompted"),
            ("healthKit/listOfTypesWriteAuthorizationHasBeenPrompted",
             "HealthKit Write Prompted")):
        for hk_type in suite.get(hk_key) or []:
            add(label, hk_type, "prompted", suite_path)
    anchors = _jload(suite.get("healthKitImportedSampleAnchorsByType"))
    if isinstance(anchors, dict):
        for hk_type, anchor in anchors.items():
            rowid = ""
            if isinstance(anchor, dict):
                for obj in anchor.get("$objects", []):
                    if isinstance(obj, dict) and "rowid" in obj:
                        rowid = obj["rowid"]
                        break
            add("HealthKit Import Anchor", hk_type, f"rowid={rowid}" if rowid else
                "present", suite_path, "proof samples were imported from HealthKit")
    add("HealthKit", "Access Asked", suite.get("healthKitAccessAsked"), suite_path)
    add("HealthKit", "Respiratory Access Asked",
        suite.get("healhtKitRespiratoryAccessAsked"), suite_path,
        "key name typo is the app's own")
    add("HealthKit", "Last Sleep Day Exported",
        suite.get("healthKitExportedSleepDay"), suite_path)

    car = suite.get("CarCapabilities")
    if isinstance(car, dict):
        for unit_id, caps in car.items():
            if isinstance(caps, dict):
                add("CarPlay Head Unit", unit_id,
                    f"UI version {caps.get('CRCapabilitiesVersionKey', '?')}",
                    suite_path, "evidence of use in this vehicle head unit")
        add("CarPlay", "Capabilities Content Version",
            car.get("CarCapabilitiesContentVersion"), suite_path)

    for widget_entry in _jload(suite.get("installedWidgets")) or []:
        if isinstance(widget_entry, dict):
            add("Home-Screen Widget", widget_entry.get("kind", ""),
                widget_entry.get("size", ""), suite_path)

    add("Permissions", "Notifications Permission Asked",
        suite.get("isNotificationsPermissionAsked"), suite_path)
    add("Permissions", "Location Enabled", traits.get("locationEnabled"),
        segment_path)
    add("Permissions", "Step/Motion Uploads Enabled",
        traits.get("stepMotionUploadsEnabled"), segment_path)
    add("Notifications", "Enabled App Notifications",
        traits.get("enabledNotificationsApp"), segment_path)
    add("On-Device AI", "Available Local LLMs", traits.get("availableLocalLLMs"),
        segment_path)

    data_headers = ("Category", "Item", "Value", "Details", "Source File")
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 7: app activity timeline
# ---------------------------------------------------------------------------
@artifact_processor
def oura_app_activity(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    bundle_path = path_by_name.get("com.ouraring.oura.plist", "")

    rows, sources = [], []

    def add(when, label, key, src):
        if not when:
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((when, label, key, context.get_relative_path(src)))

    scanned = [(suite, suite_path)]
    if bundle_path and bundle_path != suite_path:
        scanned.append((bundle, bundle_path))
    for plist_data, plist_path in scanned:
        if not isinstance(plist_data, dict):
            continue
        for key, value in plist_data.items():
            add(_timeline_when(key, value), _ACTIVITY_LABELS.get(key, key), key,
                plist_path)

    # then the ones tucked inside the JSON blobs
    for container, path, label in _NESTED_ACTIVITY:
        when = ts_auto(_dig(_jload(suite.get(container)), path))
        add(when, label, f"{container}.{path}", suite_path)

    z_settings = _jload(data_by_name.get("com.zendesk.core.settings.plist")) or {}
    z_settings_path = path_by_name.get("com.zendesk.core.settings.plist", "")
    if isinstance(z_settings, dict):
        for settings_val in z_settings.values():
            if isinstance(settings_val, dict):
                add(ts_iso(_dig(settings_val, "core.updated_at")),
                    "Zendesk config updated", "core.updated_at", z_settings_path)
        add(ts_iso(z_settings.get("updated_at")), "Zendesk settings written",
            "updated_at", z_settings_path)

    rows.sort(key=lambda r: r[0], reverse=True)
    data_headers = (("Timestamp", "datetime"), "Event", "Source Key", "Source File")
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 8: app environment & versions
# ---------------------------------------------------------------------------
@artifact_processor
def oura_app_environment(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    bundle_path = path_by_name.get("com.ouraring.oura.plist", "")
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    traits = _traits(segment)
    widget = _jload(suite.get("widgetInfo")) or {}

    rows, sources = [], []

    def add(category, attribute, value, src, details=""):
        if _is_empty(value):
            return
        if src and src not in sources:
            sources.append(src)
        rows.append((category, attribute, _cell(value), _cell(details) if details
                     else "", context.get_relative_path(src)))

    app_details = _jload(suite.get("latestAppDetails")) or {}
    add("App Version", "App Store Version Cache", app_details.get("version"),
        suite_path,
        f"released {ts_cocoa(app_details.get('currentVersionReleaseDate'))}, "
        f"min iOS {app_details.get('minimumOsVersion', '')}, notes: "
        f"{app_details.get('releaseNotes', '')}")
    app_update = _jload(suite.get("latestAppUpdate")) or {}
    add("App Version", "Last In-App Update", app_update.get("version"), suite_path,
        f"updated {ts_cocoa(app_update.get('updatedAt'))}")
    # SEGVersionKey is the app version Segment records to spot updates (alongside
    # SEGBuildKeyV2), not the Segment SDK version. The suite and bundle copies
    # are written at different times - both are reported deliberately.
    version_sources = [(suite, suite_path)]
    if isinstance(bundle, dict) and bundle_path and bundle_path != suite_path:
        version_sources.append((bundle, bundle_path))
    for plist_data, plist_path in version_sources:
        add("App Version", "Segment-Tracked Version",
            plist_data.get("SEGVersionKey"), plist_path)
        add("App Version", "Segment-Tracked Build",
            plist_data.get("SEGBuildKeyV2"), plist_path)
    add("App Version", "Last DB Migration Build",
        suite.get("lastDatabaseMigrationBuildNumber"), suite_path)
    add("App Version", "ASSA Migration Version",
        suite.get("assaCurrentMigrationVersion"), suite_path)
    add("App Version", "App Flavor", traits.get("appFlavor"), segment_path)

    add("Locale", "Locale", suite.get("AppleLocale"), suite_path)
    add("Locale", "Languages", suite.get("AppleLanguages"), suite_path)
    add("Locale", "Keyboards", suite.get("AppleKeyboards"), suite_path)
    add("Locale", "Passcode Keyboards", suite.get("ApplePasscodeKeyboards"),
        suite_path)
    add("Locale", "Language (analytics)", traits.get("language"), segment_path)
    add("Locale", "iOS Build at Language Migration",
        suite.get("AppleLanguagesDidMigrate"), suite_path)
    add("Locale", "Languages Schema Version",
        suite.get("AppleLanguagesSchemaVersion"), suite_path)
    add("Locale", "Device Time Zone", _dig(widget, "timeZone.identifier"), suite_path)
    add("Locale", "Unit System", _dig(widget, "user.unitSystem"), suite_path)

    disk = suite.get("remainingFreeDiskSpaceInBytes")
    if not _is_empty(disk):
        try:
            detail = f"{float(disk) / 1e9:.1f} GB free"
        except (TypeError, ValueError):
            detail = ""
        add("Device State", "Remaining Free Disk Space (bytes)", disk, suite_path,
            detail)
    add("Device State", "Last Network Status Satisfied",
        suite.get("lastNetworkStatusIsSatisfied"), suite_path)
    add("Device State", "Biometric App Lock", traits.get("biometricLockStatus"),
        segment_path)

    add("Bluetooth Privacy", "BLE Privacy Activation Successful",
        suite.get("blePrivacyActivationSuccessful"), suite_path)
    add("Bluetooth Privacy", "BLE Privacy Info Dismissed",
        suite.get("wasDismissedBlePrivacyActivationInfo"), suite_path)

    add("Onboarding", "User Information Asked", suite.get("userInformationAsked"),
        suite_path)

    for flag in ("hasMigratedFromStandardToSuitNameUserDefaults",
                 "hasMigratedPregnancyEnrollmentEndTimezone",
                 "hasResetChargerSyncSettingsMigration",
                 "hasRunCorruptChargerDebugInfoRecordsRemovalMigration",
                 "hasRunCorruptImportedHeartRateRemovalMigration",
                 "hasFixedImportedStepCount"):
        add("Migration Flag", flag, suite.get(flag), suite_path)

    data_headers = ("Category", "Attribute", "Value", "Details", "Source File")
    return data_headers, rows, "\n".join(sources)


# ---------------------------------------------------------------------------
# artifact 9: content caches & campaigns
# ---------------------------------------------------------------------------
_CONTENT_CACHES = (
    ("blogPosts", "General"),
    ("babyCenterArticles", "Pregnancy (BabyCenter)"),
    ("bloodPressureInPregnancyBlogPosts", "Blood Pressure in Pregnancy"),
    ("bloodPressureProfileBlogPosts", "Blood Pressure"),
    ("glucoseGraphBlogPosts", "Glucose"),
    ("heartHealthBlogPosts", "Heart Health"),
    ("metabolicHealthBlogPosts", "Metabolic Health"),
    ("perimenopauseBlogPosts", "Perimenopause"),
    ("reproductiveHealthBlogPosts", "Reproductive Health"),
    ("stressManagementBlogPosts", "Stress Management"),
)


@artifact_processor
def oura_content_campaigns(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)

    rows = []

    def add(topic, item, value, details=""):
        if _is_empty(value):
            return
        rows.append((topic, item, _cell(value), _cell(details) if details else ""))

    for key, topic in _CONTENT_CACHES:
        for post in _jload(suite.get(key)) or []:
            if not isinstance(post, dict):
                continue
            title = post.get("title")
            if isinstance(title, dict):
                title = title.get("rendered", "")
            add(f"Cached Articles: {topic}", title or post.get("slug", ""),
                post.get("url") or post.get("slug", ""),
                f"id={post.get('id', '')} "
                f"created={ts_iso(post.get('createDate')) if post.get('createDate') else ''}")

    add("Campaigns", "Current Campaign", suite.get("currentCampaignIdentifier"),
        f"arrived {ts_iso(suite.get('currentCampaignArrivalDate'))}")
    add("Campaigns", "User Interacted With Campaign",
        suite.get("didUserInteractWithCampaign"))
    add("Campaigns", "Last Dismissed Campaign",
        suite.get("identifierOfLastDismissedCampaign"))
    add("Engagement", "Last Dismissed Blog Post",
        suite.get("lastDismissedBlogPostSlug"))
    add("Engagement", "Blog Posts Updated",
        ts_iso(suite.get("blogPostsUpdatedAt")))
    add("Engagement", "Content Last Requested Day", suite.get("ctp/lastRequestedDay"))
    add("Explore", "Latest Played Story", suite.get("stress/exploreLatestPlayedStory"))
    add("Explore", "Latest Session Reason",
        suite.get("stress/latestExploreSessionReason"),
        f"day {suite.get('stress/latestExploreSessionChangeDay', '')}")
    add("Explore", "New Discovery IDs",
        suite.get("discovery_hub/new_discoveries_ids"))
    add("Onboarding", "Introduced Categories",
        _decode(suite.get("introducedCategories")))
    add("Onboarding", "Onboarded Categories",
        _decode(suite.get("onboardedCategories")))
    add("Onboarding", "Introduced Contributors",
        _decode(suite.get("introducedContributors")))

    data_headers = ("Topic", "Item", "Value", "Details")
    return data_headers, rows, source if rows else ""


# ---------------------------------------------------------------------------
# artifact 10: analytics integrations
# ---------------------------------------------------------------------------
def _segment_settings(data_by_name, path_by_name):
    """Decode the segment.settings bplist -> (settings dict, plist path)."""
    segment, path = _segment_plist(data_by_name, path_by_name)
    return _jload(segment.get("segment.settings")) or {}, path


@artifact_processor
def oura_analytics_integrations(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    settings, source = _segment_settings(data_by_name, path_by_name)
    integrations = settings.get("integrations", {}) if isinstance(settings, dict) else {}

    data_list = []
    for name in sorted(integrations.keys()):
        cfg = integrations[name] if isinstance(integrations[name], dict) else {}
        version = (cfg.get("versionSettings") or {}).get("version", "")
        consent = (cfg.get("consentSettings") or {}).get("categories", "")
        if isinstance(consent, list):
            consent = ", ".join(consent)
        data_list.append((
            name,
            cfg.get("type", ""),
            cfg.get("apiKey", ""),
            version,
            consent,
        ))
    if isinstance(settings, dict) and settings:
        consent_all = _dig(settings, "consentSettings.allCategories")
        if consent_all:
            data_list.append(("(consent categories granted)", "", "", "",
                              _cell(consent_all)))
        sample_rate = _dig(settings, "metrics.sampleRate")
        if sample_rate is not None:
            data_list.append(("(telemetry sample rate)", "", "", "",
                              str(sample_rate)))
    events = segment.get("segment.events")
    if not _is_empty(events):
        data_list.append(("(queued/recorded event count)", "", "", "", str(events)))

    data_headers = ("Integration", "Type", "API Key", "Version",
                    "Consent / Details")
    return data_headers, data_list, source or segment_path


# ---------------------------------------------------------------------------
# artifact 11: analytics event plan
# ---------------------------------------------------------------------------
@artifact_processor
def oura_analytics_event_plan(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    settings, source = _segment_settings(data_by_name, path_by_name)
    plan = settings.get("plan", {}) if isinstance(settings, dict) else {}

    data_list = []
    for section in sorted(plan.keys()):
        events = plan[section] if isinstance(plan[section], dict) else {}
        for event_name in sorted(events.keys(), key=str):
            entry = events[event_name] if isinstance(events[event_name], dict) else {}
            enabled = entry.get("enabled", "")
            suppressed = ", ".join(
                dest for dest, on in (entry.get("integrations") or {}).items()
                if on is False)
            data_list.append((section, event_name, str(enabled), suppressed))

    data_headers = ("Section", "Event Name", "Enabled", "Suppressed Destinations")
    return data_headers, data_list, source


# ---------------------------------------------------------------------------
# artifact 12: feature flags & labs
# ---------------------------------------------------------------------------
@artifact_processor
def oura_feature_flags(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    segment, segment_path = _segment_plist(data_by_name, path_by_name)
    traits = _traits(segment)

    data_list = []
    for flag in traits.get("enabledFeatureFlagsApp") or []:
        data_list.append(("Feature Flag (enabled)", str(flag), ""))
    for entry in traits.get("enabledFeatureFlagsAppParameters") or []:
        name, _, value = str(entry).partition("=")
        data_list.append(("Flag Parameter", name.strip(), value.strip()))
    for lab in traits.get("ouraLabsFeaturesAvailable") or []:
        data_list.append(("Oura Labs (available)", str(lab), ""))
    for lab in traits.get("ouraLabsFeaturesInTesting") or []:
        data_list.append(("Oura Labs (in testing)", str(lab), ""))
    for feature in traits.get("blackoutModeFeatures") or []:
        data_list.append(("Blackout-Mode Feature", str(feature), ""))

    data_headers = ("Type", "Name", "Value")
    return data_headers, data_list, segment_path if data_list else ""


# ---------------------------------------------------------------------------
# artifact 13: preferences residue (completeness guarantee)
# ---------------------------------------------------------------------------
def _residue_category(key):
    if key.startswith(_OS_PREFIXES) or key in ("SEGVersionKey", "SEGBuildKeyV2"):
        return "OS/SDK housekeeping"
    lowered = key.lower()
    if "migration" in lowered or "migrated" in lowered:
        return "Migration flag"
    if key.startswith(("appUx/", "awhr/", "sharing", "is", "was", "should", "has",
                       "did", "timelineSession", "badgeNumber", "womensHealth")):
        return "UI / app state"
    return "Unmapped (triage: consider a topical artifact)"


@artifact_processor
def oura_preferences_residue(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name = _load_oura_plists(files_found)
    suite, suite_path = _suite_plist(data_by_name, path_by_name)
    bundle_path = path_by_name.get("com.ouraring.oura.plist", "")
    suite_name = os.path.basename(str(suite_path)) if suite_path else ""

    rows, sources = [], []

    def add(src, key, value):
        decoded = _decode(value)
        if _is_empty(decoded):
            decoded = "(empty)"
        if src and src not in sources:
            sources.append(src)
        rows.append((_residue_category(key), key, _cell(decoded),
                     context.get_relative_path(src)))

    if isinstance(suite, dict):
        for key in sorted(suite.keys(), key=str.lower):
            if key in _CLAIMED_SUITE or _timeline_when(key, suite.get(key)):
                continue
            add(suite_path, key, suite.get(key))

    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    if isinstance(bundle, dict) and bundle_path != suite_path:
        for key in sorted(bundle.keys(), key=str.lower):
            if key in _CLAIMED_BUNDLE or _timeline_when(key, bundle.get(key)):
                continue
            add(bundle_path, key, bundle.get(key))

    # any extra files in the Oura Preferences dir that no artifact reads
    handled = {suite_name, "com.ouraring.oura.plist", "com.zendesk.core.account.plist",
               "com.zendesk.core.identity.plist", "com.zendesk.core.session.plist",
               "com.zendesk.core.settings.plist"}
    for name, data in sorted(data_by_name.items()):
        if name in handled or name.startswith("com.segment.storage."):
            continue
        if isinstance(data, dict):
            if not data:
                add(path_by_name.get(name, name), "(file)", "(empty plist)")
            for key in sorted(data.keys(), key=str.lower):
                add(path_by_name.get(name, name), key, data.get(key))
        else:
            add(path_by_name.get(name, name), "(root)", data)

    data_headers = ("Category", "Key", "Decoded Value", "Source File")
    return data_headers, rows, "\n".join(sources)
