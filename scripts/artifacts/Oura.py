__artifacts_v2__ = {
    "oura_account_identity_profile": {
        "name": "Oura - Account, Identity & Profile",
        "description": "Account identity, paired-ring hardware, demographics, health "
                       "profile, cross-service identifiers and support tokens, grouped "
                       "by category.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-01",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Merges the account/device, user-profile and identifier data into one view.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 15 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 11 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 1 row",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 12 rows",
        },
    },
    "oura_find_my_ring_location": {
        "name": "Oura - Find My Ring Last Known Location",
        "description": "Last known GPS fix from Find My Ring: lat/long, altitude, speed "
                       "and accuracy. Exportable to KML.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-06-02",
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
        },
    },
    "oura_ring_status": {
        "name": "Oura - Ring Status & Battery",
        "description": "Ring hardware events: battery records, low-battery notifications, "
                       "firmware date, last-seen date and ring/UTC time mapping.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-07-01",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Battery/notification timestamps are Apple Cocoa/NSDate values.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "oura_app_activity": {
        "name": "Oura - App Activity Timeline",
        "description": "Every timestamp-bearing field in the suite plist: launches, "
                       "syncs, token refresh, uploads, PPG/stress sensing, and more.",
        "author": "@slay3r00",
        "creation_date": "2026-06-02",
        "last_update_date": "2026-06-02",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "Mixed ISO/Unix/Cocoa timestamps are normalised to UTC.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "activity",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "oura_daytime_heart_rate": {
        "name": "Oura - Daytime Heart Rate",
        "description": "Cached widget heart-rate summary: min/max/most-recent bpm over a "
                       "window, with window and most-recent timestamps.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-06-04",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "From 'widgetInfo.daytimeHeartRate'; a cached summary, not the full series.",
        "paths": (
            '*/Containers/Data/Application/*/Library/Preferences/com.ouraring.oura.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.segment.storage.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.zendesk.*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/????????-????-????-????-????????????.plist',
        ),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "heart",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | Life360: Stay Connected & Safe 25.37.0, ChatGPT 1.2025.261 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360: Find Family & Friends 24.34.0, ChatGPT 1.2024.233 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360: Find Friends & Family 23.15.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Claude by Anthropic 1.260604.0, Life360: Family Safety & GPS 26.22.0, Citizen: Safety & Live Video 0.1296.0 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | BeReal. Your friends for real. 2.24.0, Life360: Find Friends & Family 24.28.0 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | Booksy for Customers 25.11.2500 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "oura_analytics_integrations": {
        "name": "Oura - Analytics Integrations",
        "description": "Segment analytics destinations (Amplitude, Braze, Segment.io, "
                       "AWS S3) with API key, type, SDK version and consent category.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-06-04",
        "requirements": "none",
        "category": "Oura Ring",
        "notes": "From the 'integrations' block of 'segment.settings'.",
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
        },
    },
    "oura_analytics_event_plan": {
        "name": "Oura - Analytics Event Plan",
        "description": "Segment tracking plan: every analytics event name the app records "
                       "(track/identify/group), showing collected telemetry.",
        "author": "@slay3r00",
        "creation_date": "2026-06-04",
        "last_update_date": "2026-06-04",
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
        },
    },
}

import os
import re
import json
import base64
import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_file_path, logfunc

# Cocoa/NSDate epoch (2001-01-01 UTC) as Unix seconds.
COCOA_EPOCH = 978307200

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_DATEISH_KEY_RE = re.compile(
    r"(date|time|timestamp|_at$|/.*at$|seen|performed|displayed|launch|refresh)",
    re.IGNORECASE,
)


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
    if isinstance(value, str) and _ISO_DATE_RE.match(value):
        return ts_iso(value)
    if isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        v = float(value)
        if 5e8 < v < 1e9:
            return ts_cocoa(v)
        if 1e9 <= v < 1e13:
            return ts_unix(v)
    return ""


def _load_oura_plists(files_found):
    """Load every plist in the Oura Preferences dir, keyed by filename.

    The bulk lives in a plist named after the account UID (so it varies per
    device); we find the dir off the fixed com.ouraring.oura.plist. If that one
    isn't in the extraction, fall back to whichever plist has a deviceUid.
    """
    bundle_path = get_file_path(files_found, "com.ouraring.oura.plist")
    pref_dir = os.path.dirname(str(bundle_path)) if bundle_path else None
    candidates = [str(fp) for fp in files_found if str(fp).endswith(".plist")]

    if pref_dir is None:
        for fp in candidates:
            try:
                with open(fp, "rb") as fh:
                    data = plistlib.load(fh)
            except Exception:  # pylint: disable=broad-exception-caught
                continue
            if isinstance(data, dict) and "deviceUid" in data:
                pref_dir = os.path.dirname(fp)
                break

    data_by_name, path_by_name = {}, {}
    for fp in candidates:
        if pref_dir and os.path.dirname(fp) != pref_dir:
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
    return data_by_name, path_by_name, bundle_path


def _suite_plist(data_by_name, path_by_name):
    """The account 'suite' plist: the big one, found by its deviceUid key."""
    for name, data in data_by_name.items():
        if isinstance(data, dict) and "deviceUid" in data:
            return data, path_by_name.get(name, name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    return bundle, path_by_name.get("com.ouraring.oura.plist", "")


def _find_by_prefix(data_by_name, prefix):
    for name, data in data_by_name.items():
        if name.startswith(prefix):
            return data
    return {}


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


def _flatten(value):
    """Value -> cell text. Lists get comma-joined, dicts dumped as compact JSON."""
    if isinstance(value, list):
        return ", ".join(str(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def _dig(obj, path):
    """Follow a dotted path down nested dicts. None if it dead-ends."""
    for part in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def _ring_id(suite):
    """The ring's BLE id. It shows up as the dict key inside the status blobs."""
    for key in ("batteryLevelRecords", "ringLowBatteryNotifications",
                "latestRingTimeMappingsRingEventParser"):
        obj = _jload(suite.get(key))
        if isinstance(obj, dict):
            inner = obj.get("records") or obj.get("notifications") or obj
            if isinstance(inner, dict) and inner:
                return next(iter(inner.keys()))
    return ""


@artifact_processor
def oura_account_identity_profile(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)
    bundle = data_by_name.get("com.ouraring.oura.plist", {})
    braze = _jload(suite.get("brazeUserAttributesV2")) or {}
    widget = _jload(suite.get("widgetInfo")) or {}
    app_details = _jload(suite.get("latestAppDetails")) or {}
    segment = _find_by_prefix(data_by_name, "com.segment.storage.")
    traits = (_jload(segment.get("segment.traits")) if isinstance(segment, dict) else None) or {}

    ring_models = braze.get("ringModel")
    ring_model = ", ".join(ring_models) if isinstance(ring_models, list) else \
        (braze.get("currentRing") or traits.get("currentRing"))

    rows = []
    consumed = set()  # braze/traits keys already covered by a row above

    def add(category, attribute, value, *profile_keys):
        consumed.update(profile_keys)
        if value not in (None, "", [], {}):
            rows.append((category, attribute, _flatten(value)))

    add("Account", "Email",
        suite.get("accountEmail") or bundle.get("accountEmail") or braze.get("userEmail"),
        "userEmail", "email")
    add("Account", "Account UID", suite.get("accountUid") or bundle.get("accountUid"))
    add("Account", "Device UID", suite.get("deviceUid"))

    add("Ring", "BLE Identifier", _ring_id(suite))
    add("Ring", "Model", ring_model, "ringModel", "currentRing")
    add("Ring", "Color", braze.get("ringColor") or traits.get("ringColor"), "ringColor")
    add("Ring", "Design", braze.get("ringDesign") or traits.get("ringDesign"), "ringDesign")
    add("Ring", "Size", traits.get("ringSize"), "ringSize")
    add("Ring", "Firmware Version", traits.get("ringFirmwareVersion"), "ringFirmwareVersion")

    add("Demographics", "Age", braze.get("age") or traits.get("age"), "age")
    add("Demographics", "Gender", braze.get("gender") or traits.get("gender"), "gender")
    add("Demographics", "Country of Residence",
        braze.get("chosenCountryOfResidence") or traits.get("chosenCountryOfResidence"),
        "chosenCountryOfResidence")
    add("Demographics", "Membership Status", traits.get("membershipStatus"), "membershipStatus")
    add("Body", "Height (m)", traits.get("height"), "height")
    add("Body", "Weight (kg)", traits.get("weight"), "weight")

    add("App", "App Version", app_details.get("version"))
    # SEGVersionKey is the app version Segment records to spot updates (alongside
    # SEGBuildKeyV2), not the Segment SDK version.
    add("App", "App Version (Segment-tracked)", suite.get("SEGVersionKey"))
    add("App", "Locale", suite.get("AppleLocale"))
    langs = suite.get("AppleLanguages")
    add("App", "Languages", ", ".join(langs) if isinstance(langs, list) else langs)
    add("App", "Time Zone", (widget.get("timeZone") or {}).get("identifier"))
    add("App", "Last Firmware Update", ts_iso(suite.get("lastUpdatedFirmwareDate")))

    add("Identifiers", "Apple App-Attest UUID", suite.get("com.apple.DC.AppAttestAppUUID"))
    if isinstance(segment, dict):
        add("Identifiers", "Segment User ID", segment.get("segment.userId"))
        add("Identifiers", "Segment Anonymous ID", segment.get("segment.anonymousId"))
        add("Identifiers", "Segment Event Count", segment.get("segment.events"))

    z_account = data_by_name.get("com.zendesk.core.account.plist", {})
    if isinstance(z_account, dict) and z_account.get("account-id"):
        try:
            decoded = base64.b64decode(z_account["account-id"]).decode("utf-8", "replace")
        except Exception:  # pylint: disable=broad-exception-caught
            decoded = z_account["account-id"]
        add("Support", "Zendesk Help Center URL", decoded)
    z_identity = data_by_name.get("com.zendesk.core.identity.plist", {})
    if isinstance(z_identity, dict):
        for ident_val in z_identity.values():
            if isinstance(ident_val, dict):
                add("Tokens", "Zendesk Auth Token", ident_val.get("auth_token"))
    z_session = data_by_name.get("com.zendesk.core.session.plist", {})
    if isinstance(z_session, dict):
        for sess_val in z_session.values():
            if isinstance(sess_val, dict):
                add("Tokens", "Zendesk Push Token", sess_val.get("pushToken"))

    # whatever else braze/segment know about the user: health status, feature
    # flags, HealthKit links, and so on.
    for src in (braze, traits):
        for key in sorted(src.keys()):
            if key in consumed:
                continue
            consumed.add(key)
            value = _flatten(src[key])
            if value not in ("", "[]", "{}"):
                rows.append(("Profile", key, value))

    data_headers = ("Category", "Attribute", "Value")
    return data_headers, rows, source


@artifact_processor
def oura_find_my_ring_location(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)

    data_list = []
    loc = _jload(suite.get("findMyRingLastKnownLocation"))
    if isinstance(loc, dict) and "latitude" in loc and "longitude" in loc:
        lat = loc.get("latitude", "")
        lon = loc.get("longitude", "")
        map_link = (f'<a href="https://www.google.com/maps?q={lat},{lon}" '
                    f'target="_blank">View on map</a>') if lat != "" and lon != "" else ""
        data_list.append((
            ts_cocoa(loc.get("timestamp")),
            lat,
            lon,
            loc.get("altitude", ""),
            loc.get("horizontalAccuracy", ""),
            loc.get("verticalAccuracy", ""),
            loc.get("speed", ""),
            loc.get("course", ""),
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
        "Course",
        "Map",
        "Source Field",
    )
    return data_headers, data_list, source


@artifact_processor
def oura_ring_status(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)
    ring = _ring_id(suite)

    data_list = []

    battery = _jload(suite.get("batteryLevelRecords")) or {}
    rec = (battery.get("records") or {}).get(ring, {}) if isinstance(battery, dict) else {}
    if rec:
        data_list.append((ts_cocoa(rec.get("lastUpdated")), ring, "Battery level recorded",
                          rec.get("batteryLevel", ""), "", ""))

    low = _jload(suite.get("ringLowBatteryNotifications")) or {}
    note = (low.get("notifications") or {}).get(ring, {}) if isinstance(low, dict) else {}
    if note:
        data_list.append((ts_cocoa(note.get("ringNotificationDate")), ring,
                          "Low-battery notification", note.get("batteryLevel", ""),
                          note.get("hoursToEmpty", ""), f"type={note.get('type', '')}"))

    mapping = _jload(suite.get("latestRingTimeMapping"))
    if isinstance(mapping, dict):
        data_list.append((ts_unix(mapping.get("utcTime")), ring, "Ring/UTC time mapping",
                          "", "", f"ringTime={mapping.get('ringTime', '')}"))

    if suite.get("lastUpdatedFirmwareDate"):
        data_list.append((ts_iso(suite.get("lastUpdatedFirmwareDate")), ring,
                          "Firmware updated", "", "", ""))
    if suite.get("findMyRingLastKnownRingSeenDate"):
        data_list.append((ts_iso(suite.get("findMyRingLastKnownRingSeenDate")), ring,
                          "Ring last seen", "", "", ""))

    data_list.sort(key=lambda r: r[0], reverse=True)
    data_headers = (
        ("Timestamp", "datetime"),
        "Ring BLE Identifier",
        "Event",
        "Battery Level (%)",
        "Hours To Empty",
        "Details",
    )
    return data_headers, data_list, source


# the OS and bundled SDKs (SiriKit, Wallet...) also stash dated keys in these
# defaults; skip them so the timeline is just Oura.
_NON_OURA_PREFIXES = ("com.apple.", "IN", "PK", "AK", "NS", "SEG", "Web")

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
    "heartHealth/heartCheckinTipFirstDisplayedAtDate": "Heart check-in tip first shown",
    "stress/stressSensingCalculationsLastPerformed": "Stress-sensing calculation",
    "stress/stressSensingCalculationsLastPerformedTriggeringDailyStressUpdate":
        "Stress-sensing daily update",
    "timelineSessionIndexUpdatedAt": "Timeline session updated",
    "updateProfileReminderCardDisplayedDate": "Profile-update reminder shown",
    "lastUpdatedFirmwareDate": "Firmware updated",
    "findMyRingLastKnownRingSeenDate": "Ring last seen",
}

# cocoa timestamps hiding inside the JSON blobs: (container, dotted path, label)
_NESTED_ACTIVITY = (
    ("latestAppUpdate", "updatedAt", "App updated"),
    ("latestAppDetails", "currentVersionReleaseDate", "App version released"),
    ("widgetInfo", "metadata.updatedAt", "Widget refreshed"),
    ("brazeUserAttributesV2", "firstActivitySummaryDate", "First activity summary"),
)


@artifact_processor
def oura_app_activity(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)

    data_list = []
    # datetimes and ISO strings are always timestamps; a bare number only counts
    # when the key name looks date-ish, else we'd pick up counts and IDs too.
    for key, value in suite.items():
        if key.startswith(_NON_OURA_PREFIXES):
            continue
        dateish = (isinstance(value, datetime)
                   or (isinstance(value, str) and _ISO_DATE_RE.match(value))
                   or (isinstance(value, (int, float)) and not isinstance(value, bool)
                       and _DATEISH_KEY_RE.search(key)))
        when = ts_auto(value) if dateish else ""
        if when:
            data_list.append((when, _ACTIVITY_LABELS.get(key, key), key))

    # then the ones tucked inside the JSON blobs
    for container, path, label in _NESTED_ACTIVITY:
        when = ts_cocoa(_dig(_jload(suite.get(container)), path))
        if when:
            data_list.append((when, label, f"{container}.{path}"))

    data_list.sort(key=lambda r: r[0], reverse=True)
    data_headers = (("Timestamp", "datetime"), "Event", "Source Key")
    return data_headers, data_list, source


@artifact_processor
def oura_daytime_heart_rate(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    suite, source = _suite_plist(data_by_name, path_by_name)
    widget = _jload(suite.get("widgetInfo")) or {}
    hr = widget.get("daytimeHeartRate") if isinstance(widget, dict) else None

    data_list = []
    if isinstance(hr, dict):
        # cocoa timestamps here (~7.8e8), not unix
        data_list.append((
            ts_cocoa(hr.get("mostRecentEntryDate")),
            ts_cocoa(hr.get("startDate")),
            ts_cocoa(hr.get("endDate")),
            hr.get("minHeartRate", ""),
            hr.get("maxHeartRate", ""),
            hr.get("mostRecentHeartRate", ""),
        ))

    data_headers = (
        ("Most Recent Reading", "datetime"),
        ("Window Start", "datetime"),
        ("Window End", "datetime"),
        "Min HR (bpm)",
        "Max HR (bpm)",
        "Most Recent HR (bpm)",
    )
    return data_headers, data_list, source


def _segment_settings(data_by_name):
    """Decode the segment.settings bplist to a dict."""
    segment = _find_by_prefix(data_by_name, "com.segment.storage.")
    if not isinstance(segment, dict):
        return {}
    return _jload(segment.get("segment.settings")) or {}


@artifact_processor
def oura_analytics_integrations(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    _, source = _suite_plist(data_by_name, path_by_name)
    settings = _segment_settings(data_by_name)
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

    data_headers = ("Integration", "Type", "API Key", "Version", "Consent Categories")
    return data_headers, data_list, source


@artifact_processor
def oura_analytics_event_plan(context):
    files_found = context.get_files_found()
    data_by_name, path_by_name, _ = _load_oura_plists(files_found)
    _, source = _suite_plist(data_by_name, path_by_name)
    settings = _segment_settings(data_by_name)
    plan = settings.get("plan", {}) if isinstance(settings, dict) else {}

    data_list = []
    for section in sorted(plan.keys()):
        events = plan[section] if isinstance(plan[section], dict) else {}
        for event_name in sorted(events.keys(), key=str):
            entry = events[event_name] if isinstance(events[event_name], dict) else {}
            enabled = entry.get("enabled", "")
            data_list.append((section, event_name, str(enabled)))

    data_headers = ("Section", "Event Name", "Enabled")
    return data_headers, data_list, source
