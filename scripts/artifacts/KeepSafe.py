__artifacts_v2__ = {
    "keepsafe_vault_items": {
        "name": "KeepSafe - Vault Items",
        "description": (
            "Media items recorded in KeepSafe's RocksDB store (Documents/rdb), matched "
            "to the encrypted file each item's id names under Documents/<table>/. "
            "Reports the item's name, timestamps, album, GPS, and SHA-1/dimensions as "
            "KeepSafe itself recorded them for the original file, before encryption."
        ),
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-08-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "RocksDB *.sst tables are not read (see module docstring); only what is "
            "still in the write-ahead log(s) is reported, so a count here is a floor, "
            "not a ceiling, on what the vault has ever held. 'breakin_alert' and 'fake' "
            "were empty directories with no live records in the validation image, so "
            "their field mapping is unexercised - see module docstring for the tier of "
            "each claim."
        ),
        "paths": (
            "*/mobile/Containers/Data/Application/*/Documents/rdb/*",
            "*/mobile/Containers/Data/Application/*/Documents/rdb_backups/*/*",
            "*/mobile/Containers/Data/Application/*/Documents/primary/*/*",
            "*/mobile/Containers/Data/Application/*/Documents/breakin_alert/*/*",
            "*/mobile/Containers/Data/Application/*/Documents/fake/*/*",
            "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.keepsafe.KeepSafe.plist",
        ),
        "output_types": "all",
        "artifact_icon": "photo",
        "sample_data": {
            "hickman_ios14": (
                "iOS 14.3 | KeepSafe 10.2.4 | 5 rows, all from the 'primary' table; "
                "'breakin_alert' and 'fake' present as empty directories, 0 rows"
            ),
        },
    },
    "keepsafe_albums": {
        "name": "KeepSafe - Albums",
        "description": (
            "Albums (KeepSafe calls them folders) decoded from the NSKeyedArchiver "
            "'shared-folders' value in the AppGroup's group.com.keepsafe.KeepSafe.plist."
        ),
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-08-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": "Cover Image Bytes is the size of the embedded cover thumbnail, not exported here.",
        "paths": (
            "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.keepsafe.KeepSafe.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | KeepSafe 10.2.4 | 5 rows: Main Album, Videos, Cards & ID, Significant Other, My Private Album",
        },
    },
    "keepsafe_account_security": {
        "name": "KeepSafe - Account & PIN Security",
        "description": (
            "App-level account, install and PIN-security state from "
            "com.keepsafe.KeepSafe.plist (app container) and "
            "group.com.keepsafe.KeepSafe.plist (AppGroup, keyed by tracking id)."
        ),
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-08-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "The PIN and invalid-PIN-count/timeout keys in group.com.keepsafe.KeepSafe.plist "
            "are stored under a '<tracking-id>.' prefix; this module reads shared-pin/"
            "shared-pin-type directly and the two '<tid>.'-prefixed keys by pattern match "
            "since the tracking id varies per install. In the image tested the PIN was "
            "stored in plain text, not hashed - report it exactly as stored, whatever the value."
        ),
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Preferences/com.keepsafe.KeepSafe.plist",
            "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.keepsafe.KeepSafe.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "shield-lock",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | KeepSafe 10.2.4 | 1 row",
        },
    },
}


import os
import pathlib
import re
import struct
import plistlib

from scripts.ccl_leveldb import LogFile
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc

# ---------------------------------------------------------------------------
# Minimal MessagePack decoder (nil/bool/int/float/str/array/map only).
# See module docstring for why this is hand-rolled rather than a dependency.
# ---------------------------------------------------------------------------

class _MsgpackError(ValueError):
    pass


def _msgpack_unpack(data):
    """Decode a single top-level MessagePack value. Raises _MsgpackError on any
    tag outside {nil, bool, (u)int8/16/32/64, fixint, float32/64, str, array, map}."""
    pos = 0
    length = len(data)

    def read(n):
        nonlocal pos
        if pos + n > length:
            raise _MsgpackError(f"Truncated msgpack data at offset {pos}")
        chunk = data[pos:pos + n]
        pos += n
        return chunk

    def unpack_value():
        tag = read(1)[0]
        if tag <= 0x7F:
            return tag
        if tag >= 0xE0:
            return tag - 0x100
        if 0x80 <= tag <= 0x8F:
            return unpack_map(tag & 0x0F)
        if 0x90 <= tag <= 0x9F:
            return unpack_array(tag & 0x0F)
        if 0xA0 <= tag <= 0xBF:
            return read(tag & 0x1F).decode("utf-8", "replace")
        if tag == 0xC0:
            return None
        if tag == 0xC2:
            return False
        if tag == 0xC3:
            return True
        if tag == 0xCA:
            return struct.unpack(">f", read(4))[0]
        if tag == 0xCB:
            return struct.unpack(">d", read(8))[0]
        if tag == 0xCC:
            return read(1)[0]
        if tag == 0xCD:
            return struct.unpack(">H", read(2))[0]
        if tag == 0xCE:
            return struct.unpack(">I", read(4))[0]
        if tag == 0xCF:
            return struct.unpack(">Q", read(8))[0]
        if tag == 0xD0:
            return struct.unpack(">b", read(1))[0]
        if tag == 0xD1:
            return struct.unpack(">h", read(2))[0]
        if tag == 0xD2:
            return struct.unpack(">i", read(4))[0]
        if tag == 0xD3:
            return struct.unpack(">q", read(8))[0]
        if tag == 0xD9:
            return read(read(1)[0]).decode("utf-8", "replace")
        if tag == 0xDA:
            str_len = struct.unpack(">H", read(2))[0]
            return read(str_len).decode("utf-8", "replace")
        if tag == 0xDB:
            str_len = struct.unpack(">I", read(4))[0]
            return read(str_len).decode("utf-8", "replace")
        if tag == 0xDC:
            return unpack_array(struct.unpack(">H", read(2))[0])
        if tag == 0xDD:
            return unpack_array(struct.unpack(">I", read(4))[0])
        if tag == 0xDE:
            return unpack_map(struct.unpack(">H", read(2))[0])
        if tag == 0xDF:
            return unpack_map(struct.unpack(">I", read(4))[0])
        raise _MsgpackError(f"Unsupported msgpack tag 0x{tag:02x} at offset {pos - 1}")

    def unpack_array(count):
        return [unpack_value() for _ in range(count)]

    def unpack_map(count):
        result = {}
        for _ in range(count):
            key = unpack_value()
            result[key] = unpack_value()
        return result

    return unpack_value()


# ---------------------------------------------------------------------------
# RocksDB WAL merge across the live store and any rdb_backups/<ts>/ snapshots.
# ---------------------------------------------------------------------------

def _rdb_store_dirs(files_found):
    """Group files_found into rdb store directories, ordered oldest-to-newest,
    live store last (so it wins ties when layering resolved state)."""
    live_dirs = set()
    backup_dirs = {}
    for path in files_found:
        norm = str(path).replace("\\", "/")
        parent = os.path.dirname(norm)
        if "/Documents/rdb_backups/" in norm:
            marker = "/Documents/rdb_backups/"
            after = norm.split(marker, 1)[1]
            ts_name = after.split("/", 1)[0]
            store_dir = parent
            while os.path.basename(store_dir) != ts_name and store_dir:
                store_dir = os.path.dirname(store_dir)
            if store_dir:
                try:
                    ts_val = int(ts_name)
                except ValueError:
                    ts_val = 0
                backup_dirs[store_dir] = ts_val
        elif "/Documents/rdb/" in norm or norm.endswith("/Documents/rdb"):
            marker = "/Documents/rdb"
            store_dir = norm.split(marker, 1)[0] + "/Documents/rdb"
            live_dirs.add(store_dir)

    ordered = [d for d, _ts in sorted(backup_dirs.items(), key=lambda kv: kv[1])]
    ordered.extend(sorted(live_dirs))
    return ordered


def _resolve_rdb_state(files_found):
    """Layer every store directory's resolved (key -> value|None-for-deleted) state,
    oldest first, live last, so a later instance always wins. Returns dict of
    key -> (decoded_value_or_None, is_deleted, source_dir)."""
    state = {}
    for store_dir in _rdb_store_dirs(files_found):
        try:
            log_names = sorted(
                name for name in os.listdir(store_dir) if name.endswith(".log")
            )
        except OSError as ex:
            logfunc(f"KeepSafe: could not list {store_dir}: {ex}")
            continue

        per_dir_records = []
        for log_name in log_names:
            log_path = pathlib.Path(store_dir) / log_name
            try:
                for record in LogFile(log_path):
                    per_dir_records.append(record)
            except (OSError, ValueError, struct.error) as ex:
                logfunc(f"KeepSafe: error reading {log_path}: {ex}")

        per_dir_records.sort(key=lambda rec: rec.seq)
        for record in per_dir_records:
            key = record.key.decode("latin1")
            if record.state.name == "Deleted":
                state[key] = (None, True, store_dir)
            else:
                try:
                    value = _msgpack_unpack(record.value) if record.value else None
                except _MsgpackError as ex:
                    logfunc(f"KeepSafe: undecoded value for key {key!r} in {store_dir}: {ex}")
                    value = None
                state[key] = (value, False, store_dir)

    return state


# ---------------------------------------------------------------------------
# NSKeyedArchiver walk for the AppGroup's "shared-folders" album list.
# ---------------------------------------------------------------------------

def _walk_nska(node, objects, seen):
    if isinstance(node, plistlib.UID):
        idx = node.data
        if idx in seen:
            return None
        if idx >= len(objects):
            return None
        return _walk_nska(objects[idx], objects, seen | {idx})
    if isinstance(node, dict):
        return {k: _walk_nska(v, objects, seen) for k, v in node.items() if k != "$class"}
    if isinstance(node, list):
        return [_walk_nska(v, objects, seen) for v in node]
    return node


def _resolve_album_names(files_found):
    """Returns (album_id -> name dict, list of (album_id, name, cover_bytes, source_file))
    decoded from every group.com.keepsafe.KeepSafe.plist found."""
    names = {}
    rows = []
    for path in files_found:
        if not str(path).endswith("group.com.keepsafe.KeepSafe.plist"):
            continue
        try:
            with open(path, "rb") as file_obj:
                plist = plistlib.load(file_obj)
        except (OSError, ValueError) as ex:
            logfunc(f"KeepSafe: error reading {path}: {ex}")
            continue

        blob = plist.get("shared-folders")
        if not isinstance(blob, (bytes, bytearray)):
            continue
        try:
            archive = plistlib.loads(bytes(blob))
        except (ValueError, plistlib.InvalidFileException) as ex:
            logfunc(f"KeepSafe: error decoding shared-folders NSKeyedArchiver blob in {path}: {ex}")
            continue

        objects = archive.get("$objects", [])
        root_uid = archive.get("$top", {}).get("root")
        if root_uid is None:
            continue
        resolved = _walk_nska(root_uid, objects, frozenset())
        for album in (resolved or {}).get("NS.objects", []):
            if not isinstance(album, dict):
                continue
            album_id = album.get("id")
            album_name = album.get("name")
            cover = album.get("cover_data")
            cover_bytes = len(cover) if isinstance(cover, (bytes, bytearray)) else ""
            if album_id is not None:
                names[album_id] = album_name
                rows.append((album_id, album_name, cover_bytes, path))
    return names, rows


# ---------------------------------------------------------------------------
# Vault item extraction.
# ---------------------------------------------------------------------------

_VAULT_TABLES = ("primary", "breakin_alert", "fake")

# The encrypted content file for an item is named "<item-id>:100" on disk (matching
# the ":100" RocksDB record suffix documented above). ":" is the classic Mac OS path
# separator, and several real-world extraction paths -- confirmed against a real
# device extraction, not just the raw tar used to build/validate this module --
# sanitize it to "_" when the file is written back out to a modern filesystem, so the
# same item shows up as "<item-id>_100" instead. Both forms are stripped here; if
# neither pattern matches, the full filename is kept as a best-effort item id (rather
# than the row being silently dropped) and the mismatch is logged so it's visible in
# the run's console/log output instead of just vanishing.
_ITEM_ID_SUFFIX_RE = re.compile(r"[:_]\d+$")


def _item_files(files_found):
    """Yields (table, item_id, encrypted_file_path) for each on-disk vault content
    file (excludes .thumb/.preview/.md sidecars)."""
    for path in files_found:
        norm = str(path).replace("\\", "/")
        for table in _VAULT_TABLES:
            marker = f"/Documents/{table}/"
            if marker not in norm:
                continue
            filename = os.path.basename(norm)
            if filename.endswith((".thumb", ".preview", ".md")):
                continue
            item_id, n_subs = _ITEM_ID_SUFFIX_RE.subn("", filename)
            if not item_id:
                continue
            if not n_subs:
                logfunc(
                    f"KeepSafe: vault content file '{filename}' does not match the "
                    "expected '<item-id>:100' / '<item-id>_100' naming pattern; using "
                    "the full filename as the item id, so RocksDB-derived fields for "
                    "this row will likely be blank."
                )
            yield table, item_id, path
            break


def _first_nonzero(*values):
    for value in values:
        if value not in (None, 0, 0.0):
            return value
    return ""


@artifact_processor
def keepsafe_vault_items(context):
    files_found = [str(f) for f in context.get_files_found()]
    state = _resolve_rdb_state(files_found)
    album_names, _album_rows = _resolve_album_names(files_found)

    data_list = []
    source_files = set()

    for table, item_id, enc_path in _item_files(files_found):
        base_key = f"tb#{table}##k~|{item_id}"
        exif_key = f"tb#{table}##k~|{item_id}:100"

        base_value, base_deleted, base_src = state.get(base_key, (None, False, None))
        exif_value, _exif_deleted, exif_src = state.get(exif_key, (None, False, None))

        base = base_value.get(3, {}) if isinstance(base_value, dict) else {}
        exif = exif_value.get(3, {}) if isinstance(exif_value, dict) else {}
        photos_asset_id = ""
        if isinstance(base_value, dict) and isinstance(base_value.get(7), dict):
            candidate = base_value[7].get(31)
            if isinstance(candidate, str) and candidate:
                photos_asset_id = candidate

        original_name = base.get(20) or ""
        album_id = base.get(32) or ""
        album_name = album_names.get(album_id, "") or ""
        account_id = base.get(6) or ""
        content_ts = base.get(21)
        added_ts = base.get(22)
        lat = _first_nonzero(base.get(51))
        lon = _first_nonzero(base.get(52))

        sha1_hash = exif.get(30) or base.get(30) or ""
        width = exif.get(34) or ""
        height = exif.get(35) or ""
        dims = f"{width}x{height}" if width and height else ""
        mime_type = exif.get(10) or base.get(10) or ""
        dominant_color = exif.get(39) or ""
        # Field 31 is the original file's recorded byte count; field 41 is the
        # preview sidecar's. Confirmed by matching both against the actual
        # on-disk :100 and :100.preview file sizes for all 5 validation items
        # (each recorded value is a few bytes below the on-disk file - consistent
        # with a short encryption header the recorded count does not include).
        recorded_bytes = _first_nonzero(exif.get(31))
        recorded_preview_bytes = _first_nonzero(exif.get(41))

        try:
            on_disk_bytes = os.path.getsize(enc_path)
        except OSError:
            on_disk_bytes = ""

        source_files.add(enc_path)
        for extra_src in (base_src, exif_src):
            if extra_src:
                source_files.add(extra_src)

        data_list.append((
            item_id,
            original_name,
            table,
            album_name or album_id,
            convert_unix_ts_to_utc(content_ts) if content_ts else "",
            convert_unix_ts_to_utc(added_ts) if added_ts else "",
            mime_type,
            dims,
            dominant_color,
            sha1_hash,
            recorded_bytes,
            recorded_preview_bytes,
            on_disk_bytes,
            lat,
            lon,
            photos_asset_id,
            account_id,
            "Yes" if base_deleted else "No",
            context.get_relative_path(enc_path),
        ))

    data_headers = (
        "Item ID",
        "Original Filename",
        "Vault Table",
        "Album",
        ("Content Date", "datetime"),
        ("Date Added to Vault", "datetime"),
        "MIME Type",
        "Dimensions (WxH)",
        "Dominant Color (as recorded)",
        "SHA-1 (of original file, as recorded)",
        "Recorded Byte Count (of original file)",
        "Recorded Byte Count (of preview)",
        "Encrypted File Size on Disk (bytes)",
        "GPS Latitude",
        "GPS Longitude",
        "Original Photos Asset ID",
        "Account Tracking ID",
        "Vault Deleted (tombstoned)",
        "Source File",
    )

    return data_headers, data_list, "\n".join(sorted(source_files))


@artifact_processor
def keepsafe_albums(context):
    files_found = [str(f) for f in context.get_files_found()]
    _names, rows = _resolve_album_names(files_found)

    data_list = []
    source_files = set()
    for album_id, album_name, cover_bytes, path in rows:
        source_files.add(path)
        data_list.append((
            album_id,
            album_name or "",
            "Yes" if cover_bytes not in ("", 0) else "No",
            cover_bytes,
            context.get_relative_path(path),
        ))

    data_headers = (
        "Album ID",
        "Album Name",
        "Has Cover Image",
        "Cover Image Bytes",
        "Source File",
    )

    return data_headers, data_list, "\n".join(sorted(source_files))


# ---------------------------------------------------------------------------
# Account / PIN security state.
# ---------------------------------------------------------------------------

def _load_plist(path):
    try:
        with open(path, "rb") as file_obj:
            return plistlib.load(file_obj)
    except (OSError, ValueError) as ex:
        logfunc(f"KeepSafe: error reading {path}: {ex}")
        return {}


@artifact_processor
def keepsafe_account_security(context):
    files_found = [str(f) for f in context.get_files_found()]

    # Match the full meaningful suffix, not just the bare filename: a device with
    # iCloud sync enabled also carries an unrelated
    # ".../CloudDocs/session/containers/iCloud.com.keepsafe.KeepSafe.plist" file
    # whose name also ends in "com.keepsafe.KeepSafe.plist" and would otherwise
    # collide with the app-container preferences file this is looking for.
    app_plist_paths = [
        p for p in files_found
        if str(p).replace("\\", "/").endswith(
            "/Library/Preferences/com.keepsafe.KeepSafe.plist")
        and "/Data/Application/" in str(p).replace("\\", "/")
    ]
    group_plist_paths = [
        p for p in files_found
        if str(p).replace("\\", "/").endswith(
            "/Library/Preferences/group.com.keepsafe.KeepSafe.plist")
    ]

    # The ordinary case, and the only one exercised against real data, is exactly
    # one app-container install and one AppGroup, which this device had, and is the
    # only case paired into one row: there is no key shared between the two plists
    # to pair them by, so with more than one of either this reports every plist
    # found as its own separate, unpaired row rather than guess a pairing that
    # could attribute one install's PIN to a different install's account fields.
    if len(app_plist_paths) == 1 and len(group_plist_paths) == 1:
        pairs = [(app_plist_paths[0], group_plist_paths[0])]
    elif not app_plist_paths and not group_plist_paths:
        pairs = [(None, None)]
    else:
        if app_plist_paths and group_plist_paths:
            logfunc(
                f"KeepSafe: {len(app_plist_paths)} app-container plist(s) and "
                f"{len(group_plist_paths)} AppGroup plist(s) found; more than one "
                "install is present or the counts do not match 1-to-1, so each is "
                "reported in its own row rather than paired by guesswork."
            )
        pairs = [(p, None) for p in app_plist_paths] + [(None, p) for p in group_plist_paths]

    data_list = []
    source_files = set()
    for app_plist_path, group_plist_path in pairs:
        app_prefs = _load_plist(app_plist_path) if app_plist_path else {}
        group_prefs = _load_plist(group_plist_path) if group_plist_path else {}

        tracking_id = group_prefs.get("tid", "")
        invalid_pin_count = ""
        pin_timeout_remaining = ""
        if tracking_id:
            invalid_pin_count = group_prefs.get(f"{tracking_id}.consecutiveInvalidPinCount", "")
            pin_timeout_remaining = group_prefs.get(f"{tracking_id}.pinTimeoutTimeRemaining", "")

        join_date = app_prefs.get("preference-join-date")
        close_time = app_prefs.get("preference-close-time")

        if app_plist_path:
            source_files.add(app_plist_path)
        if group_plist_path:
            source_files.add(group_plist_path)

        data_list.append((
            tracking_id,
            group_prefs.get("shared-pin", ""),
            group_prefs.get("shared-pin-type", ""),
            invalid_pin_count,
            pin_timeout_remaining,
            app_prefs.get("KeepsafeAppInitialAppVersion.initialVersionInstalled", ""),
            app_prefs.get("preference-app-previous-version-name", ""),
            convert_unix_ts_to_utc(join_date.timestamp()) if hasattr(join_date, "timestamp") else "",
            convert_unix_ts_to_utc(close_time.timestamp()) if hasattr(close_time, "timestamp") else "",
            app_prefs.get("preference-launch-count", ""),
            app_prefs.get("preference-launch-count-since-update", ""),
            app_prefs.get("com.keepsafe.switchboard.properties.installId", ""),
            context.get_relative_path(app_plist_path) if app_plist_path else "",
            context.get_relative_path(group_plist_path) if group_plist_path else "",
        ))

    data_headers = (
        "Account Tracking ID",
        "PIN (as stored)",
        "PIN Type (as stored)",
        "Consecutive Invalid PIN Count",
        "PIN Timeout Remaining (seconds)",
        "Initial App Version Installed",
        "Previous App Version",
        ("Account Join Date", "datetime"),
        ("Last App Close Time", "datetime"),
        "Launch Count",
        "Launch Count Since Update",
        "Install ID",
        "Source File (App Prefs)",
        "Source File (Group Prefs)",
    )

    return data_headers, data_list, "\n".join(sorted(source_files))