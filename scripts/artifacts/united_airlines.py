"""
United Airlines (com.united.UnitedCustomerFacingIPhone) artifact module.

Parses MileagePlus account data, saved travelers, wallet trips/passengers,
PNR documents, booking and flight-status searches, boarding status logs,
inflight entertainment watch history, Watch complications trip summaries,
and United iMessage extension recipient cache.
"""

__artifacts_v2__ = {
    "united_account": {
        "name": "United - Account",
        "description": "MileagePlus account profile from United Core Data.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": "Core Data table: ZUACDUSER.",
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "united_saved_travelers": {
        "name": "United - Saved Travelers",
        "description": "Saved travelers / companions from the United profile.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data: ZUACDUSER.ZSAVEDTRAVELERSJSON (simplifiedTravelers). "
            "Per-traveler MileagePlus/KTN are usually on trip passengers, not this list. "
            "Column may be absent on older app versions."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "united_trips": {
        "name": "United - Trips",
        "description": "Active and past United wallet reservations and flight segments.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data tables: ZUACDWALLETRESERVATION, ZUACDWALLETRESERVATIONSEGMENT, "
            "ZUACDWALLETPASTRESERVATION, ZUACDWALLETPASTRESERVATIONSEGMENT."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "navigation",
    },
    "united_trip_passengers": {
        "name": "United - Trip Passengers",
        "description": "Passengers on United trips, including MileagePlus IDs and KTNs when present.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data: ZUACDWALLETRESERVATION.ZJSON / ZUACDWALLETPASTRESERVATION.ZJSON "
            "(pnr.passengers); falls back to ZUACDWALLETMBP when reservation JSON is empty."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "united_boarding_passes": {
        "name": "United - Boarding Passes",
        "description": "Mobile boarding passes (MBP) from United wallet Core Data.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data table: ZUACDWALLETMBP. "
            "Often present on older app versions when wallet reservation JSON is empty."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "credit-card",
    },
    "united_pnr_documents": {
        "name": "United - PNR Documents",
        "description": "Cached PNR documents and reservation response summaries from the United app.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data tables: ZUACDPNRDOCUMENT (ZJSONRESPONSE) and "
            "ZUACDRESERVATIONRESPONSEJSON (ZRESPONSEJSON)."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "united_booking_searches": {
        "name": "United - Booking Searches",
        "description": "Recent United flight booking searches.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": "Core Data table: ZUACDBOOKINGRECENTSEARCH.",
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "united_flight_status_searches": {
        "name": "United - Flight Status Searches",
        "description": "Recent United flight status (FLIFO) lookups.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": "Core Data table: ZUACDFLIFORECENTSEARCH.",
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "united_boarding_status_log": {
        "name": "United - Boarding Status Log",
        "description": "Boarding / travel-day status snapshots from Documents/logFile.txt.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Source: Documents/logFile.txt (concatenated JSON travel-mode status history). "
            "Not present on all app versions."
        ),
        "paths": (
            "*/com.united.UnitedCustomerFacingIPhone*/Documents/logFile.txt",
            "*/AppDomain-com.united.UnitedCustomerFacingIPhone/Documents/logFile.txt",
        ),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "united_ife_watch_history": {
        "name": "United - IFE Watch History",
        "description": "Inflight entertainment watch / resume history from prefs and Core Data.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Core Data table: ZUACDINFLIGHTMEDIA; also app prefs "
            "com.united.UnitedCustomerFacingIPhone.plist (.mpd / MOV_* resume keys)."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone*/UnitediPhoneCoreData.sqlite*",
            "*/com.united.UnitedCustomerFacingIPhone/Library/Preferences/"
            "com.united.UnitedCustomerFacingIPhone.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "film",
    },
    "united_watch_complications": {
        "name": "United - Watch Complications",
        "description": "Trip summary data shared with Apple Watch complications.",
        "author": "James Habben",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-15",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Source: group.com.united.UnitedCustomerFacingIPhone.plist key "
            "WatchComplicationsData.WatchData (complicationData / reservations JSON)."
        ),
        "paths": (
            "*/group.com.united.UnitedCustomerFacingIPhone/Library/Preferences/"
            "group.com.united.UnitedCustomerFacingIPhone.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "watch",
    },
    "united_imessage_recipients": {
        "name": "United - iMessage Recipients",
        "description": (
            "Phone numbers cached for the United Airlines iMessage balloon plugin."
        ),
        "author": "James Habben",
        "creation_date": "2026-07-16",
        "last_update_date": "2026-07-16",
        "requirements": "none",
        "category": "United Airlines",
        "notes": (
            "Source: MobileSMS PluginMetaDataCache plist for "
            "com.united.UnitedCustomerFacingIPhone.UnitedCustomerFacingIMessageExtension. "
            "Shows handles the plugin has been used with; not full message content. "
            "Prefer the AppDomain-com.apple.MobileSMS copy over the notification-extension stub."
        ),
        "paths": (
            "*/Library/SMS/PluginMetaDataCache/*/com.apple.messages."
            "MSMessageExtensionBalloonPlugin:*:"
            "com.united.UnitedCustomerFacingIPhone.UnitedCustomerFacingIMessageExtension.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
}

import json
import os
import re
import sqlite3
from datetime import date, datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    get_plist_file_content,
    get_sqlite_db_path,
    logfunc,
)


def _is_core_data_db(path):
    name = os.path.basename(path).lower()
    if not name.startswith("unitediphonecoredata.sqlite"):
        return False
    return not (name.endswith("-wal") or name.endswith("-shm") or name.endswith("-journal"))


def _prefer_app_group_dbs(files_found):
    """Return unique Core Data DB paths, preferring the app-group copy."""
    dbs = []
    for path in files_found:
        path = str(path)
        if _is_core_data_db(path):
            dbs.append(path)
    if not dbs:
        return []
    app_group = [p for p in dbs if "group.com.united.UnitedCustomerFacingIPhone" in p]
    chosen = app_group if app_group else dbs
    # Deduplicate by resolved path
    seen = set()
    out = []
    for p in chosen:
        rp = os.path.realpath(p)
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def _open_sqlite(path):
    """Open SQLite read-only; fall back to immutable=1 for Core Data without WAL."""
    uri_path = get_sqlite_db_path(path)
    for query in ("mode=ro", "immutable=1"):
        try:
            db = sqlite3.connect(f"file:{uri_path}?{query}", uri=True)
            db.row_factory = sqlite3.Row
            db.execute("SELECT 1 FROM sqlite_master LIMIT 1").fetchone()
            return db
        except sqlite3.Error:
            continue
    logfunc(f"Unable to open SQLite database: {path}")
    return None


def _table_exists(db, table_name):
    row = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(db, table_name):
    return {c[1] for c in db.execute(f"PRAGMA table_info({table_name})")}


def _row_get(row, key, default=""):
    keys = row.keys()
    if key not in keys:
        return default
    value = row[key]
    return default if value is None else value


def _cocoa_ts(value):
    if value in (None, ""):
        return None
    try:
        return convert_cocoa_core_data_ts_to_utc(float(value))
    except (TypeError, ValueError):
        return value


def _loads_json(value):
    if value in (None, ""):
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or value.lower() == "null":
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def _parse_mbp_additional(additional):
    """Parse MBP ZADDITIONALDATA key=value~key=value string."""
    out = {}
    if not additional or not isinstance(additional, str):
        return out
    for part in additional.split("~"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def _append_trip_segment_rows(data_list, status_label, segments, record_locator, relative):
    for seg in segments:
        data_list.append((
            status_label,
            _row_get(seg, "ZRECORDLOCATOR", record_locator),
            "",
            _row_get(seg, "ZORIGIN"),
            "",
            _row_get(seg, "ZDESTINATION"),
            "",
            _row_get(seg, "ZSCHEDULEDDEPARTUREDATETIMESTR"),
            "",
            "",
            "",
            "",
            "",
            "",
            _cocoa_ts(_row_get(seg, "ZSORTDATE", None)),
            _cocoa_ts(_row_get(seg, "ZLASTREFRESHED", None)),
            _row_get(seg, "ZFLIGHTNUMBER"),
            _row_get(seg, "ZTRIPNUMBER"),
            _row_get(seg, "ZDISPLAYDEPARTUREDATETIME"),
            _row_get(seg, "ZDISPLAYARRIVALDATETIME"),
            _row_get(seg, "ZPASSENGERSEATS"),
            relative,
        ))


def _passenger_name(passenger):
    name = passenger.get("passengerName") or {}
    if isinstance(name, dict):
        parts = [name.get("title"), name.get("first"), name.get("middle"), name.get("last"), name.get("suffix")]
        return " ".join(p for p in parts if p).strip()
    return str(name) if name else ""


def _mileage_plus_id(passenger):
    mp = passenger.get("mileagePlus")
    if isinstance(mp, dict):
        return mp.get("mileagePlusId") or mp.get("key") or ""
    if isinstance(mp, str):
        return mp
    return ""


def _iter_concat_json_objects(text):
    decoder = json.JSONDecoder()
    idx = 0
    length = len(text)
    while idx < length:
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break
        try:
            obj, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError:
            break
        yield obj
        idx = end


def _parse_mdy_date(value):
    """Parse United MM/DD/YYYY (or M/D/YYYY) date strings to datetime.date."""
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return None
    parsed = _parse_mdy_datetime(text)
    if isinstance(parsed, datetime):
        return parsed.date()
    return text


def _parse_mdy_datetime(value):
    """Parse United MM/DD/YYYY [H:MM AM/PM] strings to datetime."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if not isinstance(value, str):
        return value
    # Normalize unicode spaces (e.g. narrow no-break before AM/PM in ZBIRTHDATE)
    text = " ".join(value.replace("\u202f", " ").replace("\xa0", " ").split())
    if not text:
        return None
    for fmt in (
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return text


def _title_from_asset_key(key):
    """Best-effort human title from IFE resume key fragments."""
    base = key
    for suffix in ("-subtitle-date", "-subtitle", "-date"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    base = re.sub(r"\.(mpd|mp4|m3u8)$", "", base, flags=re.I)
    base = base.split("/")[-1]
    # Strip common pack prefixes like UWMay21_PT_
    base = re.sub(r"^[0-9A-Za-z]*_", "", base)
    base = re.sub(r"_(En|Th|TH|PT|BV|SN)_?", " ", base)
    base = base.replace("_", " ").strip()
    return base or key


@artifact_processor
def united_account(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db or not _table_exists(db, "ZUACDUSER"):
            if db:
                db.close()
            continue
        source_path = db_path
        rows = db.execute("SELECT * FROM ZUACDUSER").fetchall()
        for row in rows:
            keys = row.keys()
            saved = _loads_json(row["ZSAVEDTRAVELERSJSON"]) if "ZSAVEDTRAVELERSJSON" in keys else None
            owner_ktn = ""
            if isinstance(saved, dict):
                owner_ktn = saved.get("ktnNumber") or ""
            data_list.append((
                row["ZFIRSTNAME"] if "ZFIRSTNAME" in keys else "",
                row["ZMIDDLENAME"] if "ZMIDDLENAME" in keys else "",
                row["ZLASTNAME"] if "ZLASTNAME" in keys else "",
                row["ZTITLE"] if "ZTITLE" in keys else "",
                row["ZMILEAGEPLUSNUMBER"] if "ZMILEAGEPLUSNUMBER" in keys else "",
                row["ZELITESTATUSDESCRIPTION"] if "ZELITESTATUSDESCRIPTION" in keys else "",
                row["ZELITESTATUSCODE"] if "ZELITESTATUSCODE" in keys else "",
                row["ZMILEAGEBALANCE"] if "ZMILEAGEBALANCE" in keys else "",
                row["ZMILLIONMILERINDICATOR"] if "ZMILLIONMILERINDICATOR" in keys else "",
                row["ZSTARELITEDESCRIPTION"] if "ZSTARELITEDESCRIPTION" in keys else "",
                row["ZISCLUBMEMBER"] if "ZISCLUBMEMBER" in keys else "",
                row["ZCLUBDESCRIPTION"] if "ZCLUBDESCRIPTION" in keys else "",
                _parse_mdy_date(row["ZCLUBEXPIRATIONDATESTR"]) if "ZCLUBEXPIRATIONDATESTR" in keys else None,
                owner_ktn,
                _parse_mdy_date(row["ZBIRTHDATE"]) if "ZBIRTHDATE" in keys else None,
                row["ZCUSTOMERID"] if "ZCUSTOMERID" in keys else "",
                row["ZBILLINGCOUNTRY"] if "ZBILLINGCOUNTRY" in keys else "",
                _cocoa_ts(row["ZLASTLOGINDATETIME"]) if "ZLASTLOGINDATETIME" in keys else None,
                row["ZSESSIONID"] if "ZSESSIONID" in keys else "",
                context.get_relative_path(db_path),
            ))
        db.close()
        break

    data_headers = (
        "First Name",
        "Middle Name",
        "Last Name",
        "Title",
        "MileagePlus Number",
        "Elite Status",
        "Elite Status Code",
        "Mileage Balance",
        "Million Miler Indicator",
        "Star Elite Description",
        "Club Member",
        "Club Description",
        ("Club Expiration", "date"),
        "Known Traveler Number",
        ("Birth Date", "date"),
        "Customer ID",
        "Billing Country",
        ("Last Login", "datetime"),
        "Session ID",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_saved_travelers(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db or not _table_exists(db, "ZUACDUSER"):
            if db:
                db.close()
            continue
        if "ZSAVEDTRAVELERSJSON" not in [c[1] for c in db.execute("PRAGMA table_info(ZUACDUSER)")]:
            db.close()
            continue
        source_path = db_path
        for row in db.execute(
            "SELECT ZMILEAGEPLUSNUMBER, ZSAVEDTRAVELERSJSON FROM ZUACDUSER"
        ):
            payload = _loads_json(row["ZSAVEDTRAVELERSJSON"])
            if not isinstance(payload, dict):
                continue
            profile_mp = payload.get("mileagePlusNumber") or row["ZMILEAGEPLUSNUMBER"] or ""
            profile_ktn = payload.get("ktnNumber") or ""
            for traveler in payload.get("simplifiedTravelers") or []:
                if not isinstance(traveler, dict):
                    continue
                is_owner = bool(traveler.get("isProfileOwner"))
                data_list.append((
                    traveler.get("firstName") or "",
                    traveler.get("lastName") or "",
                    traveler.get("prefix") or "",
                    traveler.get("birthDate") or "",
                    traveler.get("age") if traveler.get("age") is not None else "",
                    traveler.get("paxTypeID") or "",
                    is_owner,
                    profile_mp if is_owner else "",
                    profile_ktn if is_owner else "",
                    traveler.get("travelerKey") or "",
                    context.get_relative_path(db_path),
                ))
        db.close()
        break

    data_headers = (
        "First Name",
        "Last Name",
        "Prefix",
        "Birth Date",
        "Age",
        "Passenger Type",
        "Profile Owner",
        "MileagePlus Number",
        "Known Traveler Number",
        "Traveler Key",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_trips(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db:
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)

        # Active reservations
        if _table_exists(db, "ZUACDWALLETRESERVATION"):
            for row in db.execute("SELECT * FROM ZUACDWALLETRESERVATION"):
                record_locator = _row_get(row, "ZRECORDLOCATOR")
                data_list.append((
                    "Active",
                    record_locator,
                    _row_get(row, "ZFIRSTNAME"),
                    _row_get(row, "ZORIGIN"),
                    _row_get(row, "ZORIGINCITY"),
                    _row_get(row, "ZDESTINATION"),
                    _row_get(row, "ZDESTINATIONCITY"),
                    _row_get(row, "ZFLIGHTDATESTR"),
                    _row_get(row, "ZTRIPDATE"),
                    _row_get(row, "ZCARRIERCODE"),
                    _row_get(row, "ZNUMBEROFTRAVELERS"),
                    _row_get(row, "ZMILEAGEPLUSACCOUNT"),
                    _row_get(row, "ZCHECKINELIGIBLE"),
                    _row_get(row, "ZIRROPS"),
                    _cocoa_ts(_row_get(row, "ZSORTFLIGHTDATE", None)),
                    _cocoa_ts(_row_get(row, "ZLASTREFRESHED", None)),
                    "",
                    "",
                    "",
                    "",
                    "",
                    relative,
                ))
                if _table_exists(db, "ZUACDWALLETRESERVATIONSEGMENT"):
                    segments = db.execute(
                        """
                        SELECT * FROM ZUACDWALLETRESERVATIONSEGMENT
                        WHERE ZWALLETRESERVATION = ?
                        ORDER BY ZSORTDATE
                        """,
                        (row["Z_PK"],),
                    ).fetchall()
                    _append_trip_segment_rows(
                        data_list, "Active Segment", segments, record_locator, relative
                    )

        # Past reservations (older schemas often have column data but empty ZJSON)
        if _table_exists(db, "ZUACDWALLETPASTRESERVATION"):
            for row in db.execute("SELECT * FROM ZUACDWALLETPASTRESERVATION"):
                record_locator = _row_get(row, "ZRECORDLOCATOR")
                if not record_locator and _row_get(row, "ZJSON"):
                    payload = _loads_json(row["ZJSON"])
                    if isinstance(payload, dict):
                        pnr = payload.get("pnr") if isinstance(payload.get("pnr"), dict) else {}
                        record_locator = (
                            payload.get("recordLocator")
                            or pnr.get("uaRecordLocator")
                            or ""
                        )
                data_list.append((
                    "Past",
                    record_locator,
                    " ".join(
                        p for p in (
                            _row_get(row, "ZFIRSTNAME"),
                            _row_get(row, "ZLASTNAME"),
                        ) if p
                    ),
                    _row_get(row, "ZORIGIN"),
                    _row_get(row, "ZORIGINCITY"),
                    _row_get(row, "ZDESTINATION"),
                    _row_get(row, "ZDESTINATIONCITY"),
                    _row_get(row, "ZFLIGHTDATESTR") or _row_get(row, "ZFLIGHTDATE"),
                    "",
                    _row_get(row, "ZCARRIERCODE"),
                    _row_get(row, "ZNUMBEROFTRAVELERS"),
                    _row_get(row, "ZMILEAGEPLUSACCOUNT"),
                    _row_get(row, "ZCHECKINELIGIBLE"),
                    _row_get(row, "ZIRROPS"),
                    _cocoa_ts(_row_get(row, "ZSORTFLIGHTDATE", None)),
                    _cocoa_ts(_row_get(row, "ZLASTREFRESHED", None)),
                    "",
                    "",
                    "",
                    "",
                    "",
                    relative,
                ))
                if _table_exists(db, "ZUACDWALLETPASTRESERVATIONSEGMENT"):
                    segments = db.execute(
                        """
                        SELECT * FROM ZUACDWALLETPASTRESERVATIONSEGMENT
                        WHERE ZWALLETRESERVATION = ?
                        ORDER BY ZSORTDATE
                        """,
                        (row["Z_PK"],),
                    ).fetchall()
                    _append_trip_segment_rows(
                        data_list, "Past Segment", segments, record_locator, relative
                    )

        db.close()
        break

    data_headers = (
        "Record Type",
        "Record Locator",
        "Traveler / Name",
        "Origin",
        "Origin City",
        "Destination",
        "Destination City",
        "Flight Date",
        "Trip Dates",
        "Carrier",
        "Travelers",
        "MileagePlus Account",
        "Check-In Eligible",
        "Irrops",
        ("Sort Flight Date", "datetime"),
        ("Last Refreshed", "datetime"),
        "Flight Number",
        "Trip Number",
        "Display Departure",
        "Display Arrival",
        "Passenger Seats",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_trip_passengers(context):
    data_list = []
    source_path = ""
    seen = set()
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db:
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)

        reservation_tables = []
        if _table_exists(db, "ZUACDWALLETRESERVATION"):
            reservation_tables.append(("Active", "ZUACDWALLETRESERVATION"))
        if _table_exists(db, "ZUACDWALLETPASTRESERVATION"):
            reservation_tables.append(("Past", "ZUACDWALLETPASTRESERVATION"))

        for status, table in reservation_tables:
            cols = _table_columns(db, table)
            select_cols = ["Z_PK", "ZJSON"]
            if "ZRECORDLOCATOR" in cols:
                select_cols.insert(1, "ZRECORDLOCATOR")
            for row in db.execute(f"SELECT {', '.join(select_cols)} FROM {table}"):
                payload = _loads_json(_row_get(row, "ZJSON", None))
                if not isinstance(payload, dict):
                    continue
                pnr = payload.get("pnr") if isinstance(payload.get("pnr"), dict) else payload
                record_locator = (
                    _row_get(row, "ZRECORDLOCATOR")
                    or payload.get("recordLocator")
                    or (pnr.get("uaRecordLocator") if isinstance(pnr, dict) else "")
                    or ""
                )
                passengers = []
                if isinstance(pnr, dict):
                    passengers = pnr.get("passengers") or []
                if not passengers and isinstance(payload.get("passengers"), list):
                    passengers = payload.get("passengers")
                for passenger in passengers:
                    if not isinstance(passenger, dict):
                        continue
                    name = _passenger_name(passenger)
                    mp = _mileage_plus_id(passenger)
                    ktn = passenger.get("knownTravelerNumber") or ""
                    dedupe = (status, record_locator, name, mp, ktn)
                    if dedupe in seen:
                        continue
                    seen.add(dedupe)
                    data_list.append((
                        status,
                        record_locator,
                        name,
                        _parse_mdy_date(passenger.get("birthDate") or ""),
                        passenger.get("travelerTypeCode") or passenger.get("paxTypeID") or "",
                        mp,
                        ktn,
                        passenger.get("redressNumber") or "",
                        passenger.get("isProfileOwner"),
                        "Reservation JSON",
                        relative,
                    ))

        # Older app versions often keep passenger identity on mobile boarding passes
        # instead of wallet reservation JSON.
        if _table_exists(db, "ZUACDWALLETMBP"):
            for row in db.execute("SELECT * FROM ZUACDWALLETMBP"):
                extra = _parse_mbp_additional(_row_get(row, "ZADDITIONALDATA"))
                record_locator = _row_get(row, "ZPNR")
                name = _row_get(row, "ZCUSTOMERNAME")
                mp = _row_get(row, "ZMILEAGEPLUSNUMBER")
                dob = _parse_mdy_date(extra.get("dob", ""))
                dedupe = ("Boarding Pass", record_locator, name, mp, "")
                if dedupe in seen:
                    continue
                seen.add(dedupe)
                data_list.append((
                    "Boarding Pass",
                    record_locator,
                    name,
                    dob,
                    "",
                    mp,
                    "",
                    "",
                    "",
                    "Mobile Boarding Pass",
                    relative,
                ))

        db.close()
        break

    data_headers = (
        "Trip Status",
        "Record Locator",
        "Passenger Name",
        ("Birth Date", "date"),
        "Traveler Type",
        "MileagePlus ID",
        "Known Traveler Number",
        "Redress Number",
        "Profile Owner",
        "Source Type",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_boarding_passes(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db or not _table_exists(db, "ZUACDWALLETMBP"):
            if db:
                db.close()
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)
        for row in db.execute("SELECT * FROM ZUACDWALLETMBP"):
            extra = _parse_mbp_additional(_row_get(row, "ZADDITIONALDATA"))
            data_list.append((
                _row_get(row, "ZPNR"),
                _row_get(row, "ZCUSTOMERNAME"),
                _row_get(row, "ZMILEAGEPLUSNUMBER"),
                extra.get("dob", ""),
                _row_get(row, "ZFLIGHTINFO"),
                _row_get(row, "ZORIGIN"),
                _row_get(row, "ZDEPARTURECITY"),
                _row_get(row, "ZDESTINATION"),
                _row_get(row, "ZARRIVALCITY"),
                _row_get(row, "ZFLIGHTDATESTR"),
                _row_get(row, "ZDEPARTURETIME"),
                _row_get(row, "ZARRIVALTIME"),
                _row_get(row, "ZGATE"),
                _row_get(row, "ZTERMINAL"),
                _row_get(row, "ZSEATNO"),
                _row_get(row, "ZBOARDTIME"),
                _row_get(row, "ZBOARDENDTIME"),
                _row_get(row, "ZLEGSTATUS"),
                _row_get(row, "ZPREMIERSTATUS"),
                _row_get(row, "ZTSAPRECHECK"),
                _row_get(row, "ZONEPASS"),
                _row_get(row, "ZSEQUENCENUMBER"),
                _row_get(row, "ZCOS"),
                _cocoa_ts(_row_get(row, "ZSORTFLIGHTDATE", None)),
                _cocoa_ts(_row_get(row, "ZLASTREFRESHED", None)),
                relative,
            ))
        db.close()
        break

    data_headers = (
        "Record Locator",
        "Passenger Name",
        "MileagePlus Number",
        "Birth Date",
        "Flight",
        "Origin",
        "Departure City",
        "Destination",
        "Arrival City",
        "Flight Date",
        "Departure Time",
        "Arrival Time",
        "Gate",
        "Terminal",
        "Seat",
        "Boarding Time",
        "Boarding End Time",
        "Leg Status",
        "Premier Status",
        "TSA PreCheck",
        "OnePass",
        "Sequence Number",
        "Cabin / Class",
        ("Sort Flight Date", "datetime"),
        ("Last Refreshed", "datetime"),
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_pnr_documents(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db:
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)

        if _table_exists(db, "ZUACDPNRDOCUMENT"):
            for row in db.execute("SELECT * FROM ZUACDPNRDOCUMENT"):
                payload = _loads_json(_row_get(row, "ZJSONRESPONSE", None))
                is_cancelled = ""
                creation_date = None
                sequence = ""
                if isinstance(payload, dict):
                    is_cancelled = payload.get("isCancelled")
                    creation_date = _parse_mdy_datetime(
                        payload.get("reservationCreationDate") or ""
                    )
                    if payload.get("sequenceNumber") is not None:
                        sequence = payload.get("sequenceNumber")
                data_list.append((
                    "PNR Document",
                    _row_get(row, "ZRECORDLOCATOR"),
                    _row_get(row, "ZLASTNAME"),
                    _row_get(row, "ZMPNUMBER"),
                    _row_get(row, "ZCREATEDON"),
                    creation_date,
                    is_cancelled,
                    sequence,
                    _row_get(row, "ZBUCKETTYPE", None),
                    _cocoa_ts(_row_get(row, "ZCLIENTTTL", None)),
                    "",
                    "",
                    relative,
                ))

        # Older / alternate cache of reservation summaries
        if _table_exists(db, "ZUACDRESERVATIONRESPONSEJSON"):
            for row in db.execute("SELECT * FROM ZUACDRESERVATIONRESPONSEJSON"):
                payload = _loads_json(_row_get(row, "ZRESPONSEJSON", None))
                reservations = []
                if isinstance(payload, dict):
                    reservations = payload.get("Reservations") or []
                if not isinstance(reservations, list):
                    continue
                for reservation in reservations:
                    if not isinstance(reservation, dict):
                        continue
                    dep = reservation.get("CurrentTripDeparture") or {}
                    arr = reservation.get("CurrentTripArrival") or {}
                    trips = reservation.get("Trips") or []
                    flight_summary = ", ".join(
                        f"UA {t.get('FlightNumber')}" for t in trips
                        if isinstance(t, dict) and t.get("FlightNumber")
                    )
                    data_list.append((
                        "Reservation Response",
                        reservation.get("RecordLocator") or "",
                        "",
                        reservation.get("MileagePlusNumber") or _row_get(row, "ZMPNUMBER"),
                        _row_get(row, "ZCREATEDON"),
                        _parse_mdy_datetime(reservation.get("ReservationCreationDate") or ""),
                        "",
                        "",
                        "",
                        None,
                        f"{dep.get('Code', '')}-{arr.get('Code', '')}".strip("-"),
                        flight_summary,
                        relative,
                    ))

        db.close()
        break

    data_headers = (
        "Source Type",
        "Record Locator",
        "Last Name",
        "MileagePlus Number",
        "Created On",
        ("Reservation Creation Date", "datetime"),
        "Cancelled",
        "Sequence Number",
        "Bucket Type",
        ("Client TTL", "datetime"),
        "Route",
        "Flights",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_booking_searches(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db or not _table_exists(db, "ZUACDBOOKINGRECENTSEARCH"):
            if db:
                db.close()
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)
        for row in db.execute(
            """
            SELECT ZAIRPORTORIGCODE, ZAIRPORTDESTCODE, ZDATEDEPART, ZDATERETURN,
                   ZDATEINSERT, ZISAWARDTRAVEL, ZTAG, ZTRAVELERSINFO, ZCABININFO,
                   ZPOINTOFSALECOUNTRYCODE
            FROM ZUACDBOOKINGRECENTSEARCH
            ORDER BY ZDATEINSERT DESC
            """
        ):
            data_list.append((
                _cocoa_ts(row["ZDATEINSERT"]),
                row["ZAIRPORTORIGCODE"] or "",
                row["ZAIRPORTDESTCODE"] or "",
                _cocoa_ts(row["ZDATEDEPART"]),
                _cocoa_ts(row["ZDATERETURN"]),
                row["ZISAWARDTRAVEL"],
                row["ZTAG"] or "",
                row["ZTRAVELERSINFO"] or "",
                row["ZCABININFO"] or "",
                row["ZPOINTOFSALECOUNTRYCODE"] or "",
                relative,
            ))
        db.close()
        break

    data_headers = (
        ("Search Inserted", "datetime"),
        "Origin",
        "Destination",
        ("Depart Date", "datetime"),
        ("Return Date", "datetime"),
        "Award Travel",
        "Tag",
        "Travelers Info",
        "Cabin Info",
        "Point of Sale Country",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_flight_status_searches(context):
    data_list = []
    source_path = ""
    for db_path in _prefer_app_group_dbs(context.get_files_found()):
        db = _open_sqlite(db_path)
        if not db or not _table_exists(db, "ZUACDFLIFORECENTSEARCH"):
            if db:
                db.close()
            continue
        source_path = db_path
        relative = context.get_relative_path(db_path)
        for row in db.execute(
            """
            SELECT ZCARRIERCODE, ZFLIGHTNUMBER, ZORIGIN, ZORIGINNAME, ZDESTINATION,
                   ZDESTINATIONNAME, ZSCHEDULEDDEPARTURE, ZSCHEDULEDARRIVAL,
                   ZLASTUPDATED, ZEXPIRYDATE, ZTYPE
            FROM ZUACDFLIFORECENTSEARCH
            ORDER BY ZLASTUPDATED DESC
            """
        ):
            data_list.append((
                _cocoa_ts(row["ZLASTUPDATED"]),
                row["ZCARRIERCODE"] or "",
                row["ZFLIGHTNUMBER"] or "",
                row["ZORIGIN"] or "",
                row["ZORIGINNAME"] or "",
                row["ZDESTINATION"] or "",
                row["ZDESTINATIONNAME"] or "",
                _cocoa_ts(row["ZSCHEDULEDDEPARTURE"]),
                _cocoa_ts(row["ZSCHEDULEDARRIVAL"]),
                _cocoa_ts(row["ZEXPIRYDATE"]),
                row["ZTYPE"] or "",
                relative,
            ))
        db.close()
        break

    data_headers = (
        ("Last Updated", "datetime"),
        "Carrier",
        "Flight Number",
        "Origin",
        "Origin Name",
        "Destination",
        "Destination Name",
        ("Scheduled Departure", "datetime"),
        ("Scheduled Arrival", "datetime"),
        ("Expiry", "datetime"),
        "Type",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Core Data database found"


@artifact_processor
def united_boarding_status_log(context):
    data_list = []
    source_path = ""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != "logFile.txt":
            continue
        if not os.path.isfile(file_found):
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        try:
            text = open(file_found, "r", encoding="utf-8", errors="ignore").read()
        except OSError as err:
            logfunc(f"Unable to read United boarding log {file_found}: {err}")
            continue
        for obj in _iter_concat_json_objects(text):
            if not isinstance(obj, dict):
                continue
            data_list.append((
                obj.get("lastUpdatedTime") or "",
                obj.get("activationTime") or "",
                obj.get("recordLocator") or "",
                obj.get("lastName") or "",
                obj.get("flightNumber") or "",
                obj.get("origin") or "",
                obj.get("originCity") or "",
                obj.get("destination") or "",
                obj.get("destinationCity") or "",
                obj.get("scheduledDepartureTime") or "",
                obj.get("scheduledArrivalTime") or "",
                obj.get("boardingTime") or "",
                obj.get("boardingEndTime") or "",
                obj.get("departureGate") or "",
                obj.get("arrivalGate") or "",
                obj.get("seatNumber") or "",
                obj.get("flightStatus") or "",
                obj.get("boardingStatus") or "",
                obj.get("boardingPassKey") or "",
                obj.get("tripNumber") or "",
                relative,
            ))
        break

    data_headers = (
        "Last Updated",
        "Activation Time",
        "Record Locator",
        "Last Name",
        "Flight Number",
        "Origin",
        "Origin City",
        "Destination",
        "Destination City",
        "Scheduled Departure",
        "Scheduled Arrival",
        "Boarding Time",
        "Boarding End Time",
        "Departure Gate",
        "Arrival Gate",
        "Seat",
        "Flight Status",
        "Boarding Status",
        "Boarding Pass Key",
        "Trip Number",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United boarding log found"


@artifact_processor
def united_ife_watch_history(context):
    data_list = []
    source_paths = []
    files_found = [str(p) for p in context.get_files_found()]

    # Core Data IFE table
    for db_path in _prefer_app_group_dbs(files_found):
        db = _open_sqlite(db_path)
        if not db:
            continue
        if _table_exists(db, "ZUACDINFLIGHTMEDIA"):
            source_paths.append(db_path)
            relative = context.get_relative_path(db_path)
            for row in db.execute(
                """
                SELECT ZTITLE, ZMEDIAIDSTRING, ZMEDIAID, ZPOSITION, ZTIMESTAMP, ZSUBTITLE
                FROM ZUACDINFLIGHTMEDIA
                """
            ):
                data_list.append((
                    _cocoa_ts(row["ZTIMESTAMP"]),
                    "Core Data",
                    row["ZTITLE"] or "",
                    row["ZMEDIAIDSTRING"] or "",
                    row["ZMEDIAID"] if row["ZMEDIAID"] is not None else "",
                    "",
                    row["ZPOSITION"] if row["ZPOSITION"] is not None else "",
                    row["ZSUBTITLE"] or "",
                    relative,
                ))
        db.close()
        break

    # Preferences resume keys
    for file_found in files_found:
        base = os.path.basename(file_found)
        # Do not match group.com.united...plist (same suffix as the app prefs file).
        if base != "com.united.UnitedCustomerFacingIPhone.plist":
            continue
        if "Library/Preferences/" not in file_found.replace("\\", "/"):
            continue
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue
        source_paths.append(file_found)
        relative = context.get_relative_path(file_found)

        # Pair MOV_* / asset keys with optional -date siblings
        date_map = {}
        for key, value in plist.items():
            if isinstance(key, str) and key.endswith("-date") and isinstance(value, datetime):
                date_map[key[:-5]] = value if value.tzinfo else value.replace(tzinfo=timezone.utc)

        for key, value in plist.items():
            if not isinstance(key, str):
                continue
            if key.endswith(("-date", "-subtitle", "-subtitle-date")):
                continue
            is_resume = key.endswith((".mpd", ".mp4")) or key.startswith("MOV_")
            if not is_resume:
                continue
            position = value
            timestamp = date_map.get(key)
            data_list.append((
                timestamp,
                "Preferences",
                _title_from_asset_key(key),
                key,
                "",
                position if position is not None else "",
                "",
                "",
                relative,
            ))

        # Explicit stream-accessed URL flags (corroboration only)
        for key, value in plist.items():
            if not isinstance(key, str):
                continue
            if value is True and (".m3u8" in key.lower() or "inflytxp.net/media" in key.lower()):
                data_list.append((
                    None,
                    "Stream URL Flag",
                    _title_from_asset_key(key),
                    key,
                    "",
                    "",
                    "",
                    "",
                    relative,
                ))
        break

    data_headers = (
        ("Timestamp", "datetime"),
        "Source Type",
        "Title",
        "Asset / Media ID",
        "Media ID (int)",
        "Position (seconds)",
        "Position (raw)",
        "Subtitle",
        "Source File",
    )
    source_path = "\n".join(source_paths) if source_paths else "No United IFE artifacts found"
    return data_headers, data_list, source_path


@artifact_processor
def united_watch_complications(context):
    data_list = []
    source_path = ""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith("group.com.united.UnitedCustomerFacingIPhone.plist"):
            continue
        if "group.com.united.UnitedCustomerFacingIPhone" not in file_found.replace("\\", "/"):
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue
        watch = plist.get("WatchComplicationsData") or {}
        raw = watch.get("WatchData") if isinstance(watch, dict) else None
        payload = None
        if isinstance(raw, (bytes, bytearray)):
            try:
                payload = json.loads(raw.decode("utf-8", errors="ignore"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = None
        elif isinstance(raw, str):
            payload = _loads_json(raw)
        elif isinstance(raw, dict):
            payload = raw

        if not isinstance(payload, dict):
            continue

        items = payload.get("complicationData") or []
        if not items:
            # Older payloads may only populate reservations[]
            items = payload.get("reservations") or []

        for item in items:
            if not isinstance(item, dict):
                continue
            data_list.append((
                item.get("recordLocator") or item.get("RecordLocator") or "",
                item.get("flightNumber") or item.get("FlightNumber") or "",
                item.get("departure") or item.get("Departure") or "",
                item.get("arrival") or item.get("Arrival") or "",
                item.get("scheduledDepartureDate") or "",
                item.get("scheduledDepartureTime") or "",
                item.get("scheduledDepartureDateTime")
                or item.get("ScheduledDepartureDateTime")
                or "",
                item.get("scheduledArrivalDate") or "",
                item.get("scheduledArrivalTime") or "",
                item.get("scheduledArrivalDateTime")
                or item.get("ScheduledArrivalDateTime")
                or "",
                item.get("statusShort") or item.get("status") or "",
                relative,
            ))
        break

    data_headers = (
        "Record Locator",
        "Flight Number",
        "Departure",
        "Arrival",
        "Scheduled Departure Date",
        "Scheduled Departure Time",
        "Scheduled Departure DateTime",
        "Scheduled Arrival Date",
        "Scheduled Arrival Time",
        "Scheduled Arrival DateTime",
        "Status",
        "Source File",
    )
    return data_headers, data_list, source_path or "No United Watch complications plist found"


@artifact_processor
def united_imessage_recipients(context):
    """Parse United iMessage plugin recipient cache from SMS PluginMetaDataCache."""
    data_list = []
    source_paths = []
    imessage_prefix = "iMessage;-;"
    plugin_suffix = (
        "com.united.UnitedCustomerFacingIPhone.UnitedCustomerFacingIMessageExtension.plist"
    )

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(plugin_suffix):
            continue
        if "PluginMetaDataCache" not in file_found.replace("\\", "/"):
            continue
        if not os.path.isfile(file_found):
            continue

        plist = get_plist_file_content(file_found)
        if not isinstance(plist, dict):
            continue

        relative = context.get_relative_path(file_found)
        local_id = plist.get("localID") or ""

        # Collapse bare +E.164 and iMessage;-;+E.164 keys into one row per number.
        by_number = {}
        for key, value in plist.items():
            if key == "localID" or not isinstance(key, str):
                continue
            handle_type = "Phone"
            number = key
            if key.startswith(imessage_prefix):
                handle_type = "iMessage"
                number = key[len(imessage_prefix):]
            if not number.startswith("+"):
                continue
            entry = by_number.setdefault(
                number,
                {
                    "phone": number,
                    "has_phone": False,
                    "has_imessage": False,
                    "phone_uuid": "",
                    "imessage_uuid": "",
                },
            )
            cache_id = value if isinstance(value, str) else str(value) if value is not None else ""
            if handle_type == "iMessage":
                entry["has_imessage"] = True
                entry["imessage_uuid"] = cache_id
            else:
                entry["has_phone"] = True
                entry["phone_uuid"] = cache_id

        if not by_number:
            # Notification-extension stubs often only have localID — skip empty noise.
            continue

        source_paths.append(relative)
        for number in sorted(by_number):
            entry = by_number[number]
            handle_types = []
            if entry["has_phone"]:
                handle_types.append("Phone")
            if entry["has_imessage"]:
                handle_types.append("iMessage")
            data_list.append((
                entry["phone"],
                ", ".join(handle_types),
                entry["phone_uuid"],
                entry["imessage_uuid"],
                local_id,
                relative,
            ))

    data_headers = (
        ("Phone Number", "phonenumber"),
        "Handle Types",
        "Phone Cache ID",
        "iMessage Cache ID",
        "Local ID",
        "Source File",
    )
    source_path = "\n".join(source_paths) if source_paths else (
        "No United iMessage plugin recipient cache found"
    )
    return data_headers, data_list, source_path
