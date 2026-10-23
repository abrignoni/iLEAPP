__artifacts_v2__ = {
    "keepsafe_vault_items": {
        "name": "KeepSafe - Vault Items",
        "description": (
            "KeepSafe item files and resolved item records in the write-ahead logs under "
            "Documents/rdb and Documents/rdb_backups/<timestamp>. Files are matched by item id "
            "to decoded records. Log-only items are retained with a blank Source File. "
            "Numbered fields are reported under this module's labels; their meanings are not "
            "established by KeepSafe source. Records held only in .sst tables are not read."
        ),
        "author": "@Gear-I, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "RocksDB *.sst tables are not read. A row is produced for each item file, with "
            "its matching resolved WAL fields when present; an item found only in the resolved "
            "WAL state also produces a row, with no linked item file. This is not a complete "
            "count of what the vault holds or has held. On hickman_ios14, hickman_ios15 and "
            "iphone11_ios17 "
            "'breakin_alert' and 'fake' held no item files, and their 3 and 2 live records were "
            "only in the logs, so those rows are log-only and their field mapping has no item file "
            "to check it against. The column labels (Original Filename, Album, GPS Latitude and Longitude, "
            "SHA-1, Dimensions and the rest) "
            "were assigned by this module to numbered keys of the log values; no KeepSafe source "
            "for them is cited, and how each was identified and on which image is not recorded "
            "here. Keys 21 and 22 are retained as stored text without assigning a unit or epoch. On the iOS 17.3 image each table is sharded "
            "into two-letter folders (primary/<xx>/<item-id>_100); the folder entries the file "
            "search returns beside the files, and the rdb_backups/<timestamp> folder itself, are "
            "skipped. The KeepSafe version recorded in sample_data is the app's own "
            "initialVersionInstalled preference, the version first installed rather than the one "
            "running at acquisition. On cookbook_ios1751 (iOS 17.5.1) the container held no table "
            "directory, so all 7 rows are log-only: they come from the log in "
            "rdb_backups/<timestamp>, since the live rdb log held no records and its .sst table is "
            "not read. No item had a :100 record there, so MIME Type, Dimensions (WxH), Dominant "
            "Color (as recorded), Recorded Byte Count (of original file), Recorded Byte Count (of "
            "preview), Encrypted File Size on Disk (bytes), GPS Latitude, GPS Longitude and "
            "Original Photos Asset ID are empty on all 7 rows. Key 30 was null, so SHA-1 (of "
            "original file, as recorded) is empty; key 6 was an empty string, so Account Tracking "
            "ID is empty; and key 32 held the boolean true, so Album shows 'True' on all 7 rows "
            "and does not name an album on that version. Key 21 (as stored) and Key 22 (as "
            "stored) held one value on all 7 rows, and Vault Deleted (tombstoned) was 'No' on all "
            "7. That image's 25 vault file documents are in the photovault store, reported by "
            "KeepSafe - Photo Vault Files."
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
                "iOS 14.3 | KeepSafe 10.2.4 | 13 rows: 'primary' 8 (5 with an item file, 3 log-only), "
                "'breakin_alert' 3 and 'fake' 2, all log-only"
            ),
            "hickman_ios15": (
                "iOS 15.3.1 | KeepSafe 11.7.3 (initial install version) | 14 rows: 'primary' 9 (7 with an "
                "item file and no log record, 2 log-only), 'breakin_alert' 3 and 'fake' 2, all log-only"
            ),
            "iphone11_ios17": (
                "iOS 17.3 | KeepSafe 11.10.1 (initial install version) | 20 rows: 'primary' 15 (9 with an "
                "item file, sharded into two-letter folders, 6 log-only), 'breakin_alert' 3 and 'fake' 2, "
                "all log-only"
            ),
            "cookbook_ios1751": (
                "iOS 17.5.1 | KeepSafe 11.13.1 (initial install version) | 7 rows, all log-only from "
                "rdb_backups: 2 'primary', 2 'fake', 3 'breakin_alert'; no table directory"
            ),
        },
    },
    "keepsafe_albums": {
        "name": "KeepSafe - Albums",
        "description": (
            "Albums decoded from the NSKeyedArchiver 'shared-folders' value in the AppGroup's "
            "group.com.keepsafe.KeepSafe.plist."
        ),
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-08-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": "Cover Image Bytes is the length of the album's cover_data value. The bytes are "
                 "not exported here and their format was not checked.",
        "paths": (
            "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.keepsafe.KeepSafe.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | KeepSafe 10.2.4 | 5 rows: Main Album, Videos, Cards & ID, Significant Other, My Private Album",
            "hickman_ios15": "iOS 15.3.1 | KeepSafe 11.7.3 (initial install version) | 5 rows",
            "iphone11_ios17": "iOS 17.3 | KeepSafe 11.10.1 (initial install version) | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | KeepSafe 11.13.1 (initial install version) | 1 row",
        },
    },
    "keepsafe_account_security": {
        "name": "KeepSafe - Account & PIN Security",
        "description": (
            "Account, install and security fields from app-container and AppGroup preferences. "
            "Exactly one matching app plist and one matching group plist are combined into one row; "
            "other nonempty combinations produce separate unpaired rows. "
            "The group plist own tid selects its invalid-count and timeout keys."
        ),
        "author": "@Gear-I, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-23",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "In group.com.keepsafe.KeepSafe.plist the shared-pin and shared-pin-type values are "
            "read directly. The invalid-PIN count and the timeout are read from "
            "<tid>.consecutiveInvalidPinCount and <tid>.pinTimeoutTimeRemaining, where <tid> is "
            "the value of the plist's own tid key; when the plist has no tid those two columns "
            "are blank. The app plist and the group plist are reported in one row only when "
            "exactly one of each is found; otherwise each plist is reported in its own row and no "
            "pairing is made. The shared-pin value is reported as stored. Whether it is the PIN "
            "itself or a value derived from it is not established here. Initial App Version Installed "
            "is read from KeepsafeAppInitialAppVersion.initialVersionInstalled, or from the same "
            "name prefixed as (KeepsafeAppInitialAppVersion in _<hex>).initialVersionInstalled, "
            "the form found on cookbook_ios1751; if both are present, every distinct value is "
            "listed."
        ),
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Preferences/com.keepsafe.KeepSafe.plist",
            "*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.com.keepsafe.KeepSafe.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "shield-lock",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | KeepSafe 10.2.4 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | KeepSafe 11.7.3 (initial install version) | 1 row",
            "iphone11_ios17": "iOS 17.3 | KeepSafe 11.10.1 (initial install version) | 1 row",
            "cookbook_ios1751": "iOS 17.5.1 | KeepSafe 11.13.1 (initial install version) | 1 row",
        },
    },
    "keepsafe_photovault_files": {
        "name": "KeepSafe - Photo Vault Files",
        "description": (
            "Vault file documents from the Couchbase Lite store "
            "Library/Application Support/photovault/photovault.cblite2, with the vault's copy of the "
            "file shown in line when one is present. Document bodies are Fleece, decoded with the "
            "SharedKeys record in the store's kv_info table; deleted-document tombstones are "
            "reported by id."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-23",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "One row per document whose modelType is 'file', plus any document whose body could "
            "not be decoded and any tombstone in kv_del_default (Document State says which). "
            "The -wal is read: without it the cookbook_ios1751 store reads at an older state "
            "(highest sequence 252 instead of 256). "
            "Media: the vault's copy is matched by the recorded localHash of the item's own "
            "rendition, as Documents/com.getkeepsafe.userMedia/<localHash>_<type>. When that file "
            "is absent the Library/Caches/com.getkeepsafe.userMedia/<localHash>_preview, then "
            "_thumbnail, file is shown instead, and Rendition Shown names which one; the thumbnail "
            "fallback is unexercised. Booleans are shown as Yes or No, whole-number floats as "
            "integers, and lists joined with commas. On "
            "cookbook_ios1751 all 25 photo files were present, the SHA-1 of each file equalled its "
            "localHash, and Recorded Size (bytes) and Size of File Shown (bytes) were identical on all "
            "25 rows. Format of File "
            "Shown is read from the file's bytes; MIME Type is the stored value. Imported At and "
            "Created At On Device are read as Unix seconds: on cookbook_ios1751 the modification "
            "time of each of the 25 photo files equalled Created At On Device to the second. What "
            "event each field records is taken from its stored name only; no KeepSafe source is "
            "cited for it. Identifier On Device has the shape of an iOS Photos local identifier, but "
            "none of the 25 UUIDs were in that image's Photos.sqlite ZASSET table, so that link is "
            "unexercised. Pushed to Server is bit 0x08 of the LiteCore flags column, defined as "
            "kSynced in couchbase-lite-core LiteCore/Storage/Record.hh line 25 at commit "
            "3f90f2e97b9a07ca84af6ea56a8b1b0d25860e1f. On cookbook_ios1751 these columns held one "
            "value on every row: Item Type 'photo', Rendition Shown 'photo', Duration '0', In Trash "
            "'No', Is Deleted 'No', Backup State 'backedUp', Pushed to Server (LiteCore flag) 'Yes', "
            "Document State "
            "'live', and Owner ID one account id. kv_del_default was empty there and no document was "
            "a video, so tombstone rows and video items are unexercised, as is the LiteCore 2.x "
            "layout, where the body column "
            "holds a revision tree (read here by the same path that decoded 7,194 documents of "
            "another app's 2.x stores on ctf2020_ios12 without error). Not reported: "
            "Documents/com.keepsafe.user-metadata.cblite2 (no documents on cookbook_ios1751), the "
            "replication checkpoint and cookie records, the token value in "
            "Documents/com.getkeepsafe.userSession/couchbase.json, and image files in the "
            "container's tmp folder, which no document names. Earlier document versions left in "
            "the -wal are not recovered."
        ),
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/photovault/photovault.cblite2/db.sqlite3*",
            "*/mobile/Containers/Data/Application/*/Documents/com.getkeepsafe.userMedia/*",
            "*/mobile/Containers/Data/Application/*/Library/Caches/com.getkeepsafe.userMedia/*",
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "cookbook_ios1751": "iOS 17.5.1 | KeepSafe 11.13.1 (initial install version) | 25 rows, 25 with media",
            "ctf2020_ios12": "iOS 12.4 | no KeepSafe container | 0 rows",
        },
    },
    "keepsafe_photovault_albums": {
        "name": "KeepSafe - Photo Vault Albums",
        "description": (
            "Album documents from the Couchbase Lite store "
            "Library/Application Support/photovault/photovault.cblite2, with the number of file "
            "documents in the same store that name each album."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-23",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "One row per document whose modelType is 'album'. Booleans are shown as Yes or No and "
            "lists joined with commas. File Documents Naming This Album "
            "counts the file documents in the same store whose albumId is the album's document id. "
            "Created At is read as Unix seconds, the same scale as the file documents' times. Album "
            "Type and Special Type are reported as stored; what each value means in the app is not "
            "established from KeepSafe source. Pushed to Server is bit 0x08 of the LiteCore flags "
            "column (kSynced, couchbase-lite-core LiteCore/Storage/Record.hh line 25 at commit "
            "3f90f2e97b9a07ca84af6ea56a8b1b0d25860e1f). On cookbook_ios1751 File Sort Mode held "
            "'byImportedAt', Available Offline 'No', Is Deleted 'No', Pushed to Server (LiteCore "
            "flag) 'Yes' and "
            "Document State 'live' on all 5 rows, Owner ID held one account id, and Shared With "
            "was an empty list on every row, so shared albums are unexercised. A tombstone with no "
            "body cannot be told apart as an album or a file, and is reported in KeepSafe - Photo "
            "Vault Files."
        ),
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/photovault/photovault.cblite2/db.sqlite3*",
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
        ),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "cookbook_ios1751": "iOS 17.5.1 | KeepSafe 11.13.1 (initial install version) | 5 rows",
            "ctf2020_ios12": "iOS 12.4 | no KeepSafe container | 0 rows",
        },
    },
}


import os
import pathlib
import re
import struct
import plistlib
import sqlite3
from datetime import timezone

from scripts.ccl_leveldb import LogFile
from scripts.ilapfuncs import (
    artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc, open_sqlite_db_readonly,
)

# ---------------------------------------------------------------------------
# Minimal MessagePack decoder (nil/bool/int/float/str/array/map only).
# This decoder supports only the MessagePack tags listed below.
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
        if os.path.isdir(path):
            # the seekers hand back a matched directory (rdb_backups/<ts> itself) as well as
            # its files; a directory entry has no store to contribute and, walked upward,
            # never meets its own name
            continue
        norm = str(path).replace("\\", "/")
        parent = os.path.dirname(norm)
        if "/Documents/rdb_backups/" in norm:
            marker = "/Documents/rdb_backups/"
            after = norm.split(marker, 1)[1]
            ts_name = after.split("/", 1)[0]
            store_dir = parent
            while store_dir and os.path.basename(store_dir) != ts_name:
                up = os.path.dirname(store_dir)
                if up == store_dir:
                    # reached the filesystem root without meeting the backup name
                    store_dir = ""
                    break
                store_dir = up
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
# the ":100" RocksDB record suffix used for the item metadata). ":" is the classic Mac OS path
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
        if os.path.isdir(path):
            # newer builds shard a table into two-letter folders (primary/5z/5zxGR_100) and the
            # seekers return those folders too; a folder is not an item
            continue
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

    items = list(_item_files(files_found))
    file_ids = {(table, item_id) for table, item_id, _path in items}
    log_ids = set()
    for key in state:
        match = re.fullmatch(r'tb#(primary|breakin_alert|fake)##k~\|([^:]+)(?::100)?', key)
        if match:
            log_ids.add(match.groups())
    items.extend((table, item_id, '') for table, item_id in sorted(log_ids - file_ids))

    for table, item_id, enc_path in items:
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

        if enc_path:
            source_files.add(enc_path)
        for extra_src in (base_src, exif_src):
            if extra_src:
                source_files.add(extra_src)

        data_list.append((
            item_id,
            original_name,
            table,
            album_name or album_id,
            str(content_ts) if content_ts is not None else "",
            str(added_ts) if added_ts is not None else "",
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
            context.get_relative_path(enc_path) if enc_path else "",
        ))

    data_headers = (
        "Item ID",
        "Original Filename",
        "Vault Table",
        "Album",
        "Key 21 (as stored)",
        "Key 22 (as stored)",
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

    order = (4, 5, 0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)
    data_headers = tuple(data_headers[i] for i in order)
    data_list = [tuple(row[i] for i in order) for row in data_list]
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

def _plist_date_to_epoch(value):
    """Unix seconds for a plist <date>, or None.

    A plist date is UTC, but plistlib returns a NAIVE datetime (the aware_datetime
    keyword only exists from 3.12, and CI runs 3.10). datetime.timestamp() reads a
    naive value as local time, so without pinning UTC the reported time shifts by
    the offset of whoever ran the tool: measured 21,600 seconds against this
    artifact on a UTC-6 host.
    """
    if not hasattr(value, "timestamp"):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.timestamp()


def _load_plist(path):
    try:
        with open(path, "rb") as file_obj:
            return plistlib.load(file_obj)
    except (OSError, ValueError) as ex:
        logfunc(f"KeepSafe: error reading {path}: {ex}")
        return {}


# Older builds write "KeepsafeAppInitialAppVersion.initialVersionInstalled"; on the iOS 17.5.1
# image the same preference carries a type prefix, "(KeepsafeAppInitialAppVersion in
# _<32 hex>).initialVersionInstalled".
_INITIAL_VERSION_KEY = "KeepsafeAppInitialAppVersion.initialVersionInstalled"
_INITIAL_VERSION_KEY_RE = re.compile(
    r"\(KeepsafeAppInitialAppVersion in _[0-9A-Fa-f]+\)\.initialVersionInstalled")


def _initial_version_installed(app_prefs):
    values = [app_prefs[_INITIAL_VERSION_KEY]] if _INITIAL_VERSION_KEY in app_prefs else []
    values += [value for key, value in sorted(app_prefs.items())
               if isinstance(key, str) and _INITIAL_VERSION_KEY_RE.fullmatch(key)]
    values = list(dict.fromkeys(str(value) for value in values))
    if len(values) > 1:
        logfunc(f"KeepSafe: {len(values)} different initialVersionInstalled values; all are reported")
    return ", ".join(values)


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

        join_date = _plist_date_to_epoch(app_prefs.get("preference-join-date"))
        close_time = _plist_date_to_epoch(app_prefs.get("preference-close-time"))

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
            _initial_version_installed(app_prefs),
            app_prefs.get("preference-app-previous-version-name", ""),
            convert_unix_ts_to_utc(join_date) if join_date is not None else "",
            convert_unix_ts_to_utc(close_time) if close_time is not None else "",
            app_prefs.get("preference-launch-count", ""),
            app_prefs.get("preference-launch-count-since-update", ""),
            app_prefs.get("com.keepsafe.switchboard.properties.installId", ""),
            context.get_relative_path(app_plist_path) if app_plist_path else "",
            context.get_relative_path(group_plist_path) if group_plist_path else "",
        ))

    data_headers = (
        "Account Tracking ID",
        "shared-pin (as stored)",
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

    order = (7, 8, 0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13)
    data_headers = tuple(data_headers[i] for i in order)
    data_list = [tuple(row[i] for i in order) for row in data_list]
    return data_headers, data_list, "\n".join(sorted(source_files))

# ---------------------------------------------------------------------------
# Couchbase Lite (LiteCore) store reader for photovault.cblite2.
#
# Document bodies are Fleece. The decoder follows couchbase/fleece at commit
# 8ce5f690480b77c0f93d03f456a29828b5a55d66: Fleece.md, Fleece/Core/Value.cc,
# Fleece/Core/Array.cc and Fleece/Core/Pointer.hh. Dict keys that are integers index
# the store's SharedKeys array, kept in kv_info under the key 'SharedKeys'.
# A kv_default table without an 'extra' column is the LiteCore 2.x layout, where 'body'
# is a revision tree holding the Fleece body of each revision
# (couchbase-lite-core LiteCore/RevTrees/RawRevTree.hh at 3f90f2e97b9a07ca84af6ea56a8b1b0d25860e1f);
# the current revision is first.
# ---------------------------------------------------------------------------

class _FleeceError(ValueError):
    pass


_FLEECE_UNDEFINED = object()


def _fleece_uvarint(buf, pos):
    result = shift = 0
    for i in range(10):
        if pos + i >= len(buf):
            raise _FleeceError("varint runs past the end of the data")
        byte = buf[pos + i]
        result |= (byte & 0x7F) << shift
        if byte < 0x80:
            return result, i + 1
        shift += 7
    raise _FleeceError("varint is too long")


def _fleece_deref(buf, pos, wide):
    if wide:
        if pos + 4 > len(buf):
            raise _FleeceError("wide pointer runs past the end of the data")
        raw = struct.unpack_from(">I", buf, pos)[0]
        external, offset = raw & 0x40000000, (raw & 0x3FFFFFFF) << 1
    else:
        raw = struct.unpack_from(">H", buf, pos)[0]
        external, offset = raw & 0x4000, (raw & 0x3FFF) << 1
    if external:
        # Pointer.cc derefExtern / carefulDeref (couchbase/fleece 8ce5f690): with no base
        # document to resolve against, a narrow pointer is read as a legacy pointer from before
        # the extern flag existed, whose offset is fifteen bits, and kept only if it lands
        # inside the data. A wide one is refused.
        legacy = (raw & 0x7FFF) << 1
        if wide or legacy == 0 or legacy > pos:
            raise _FleeceError("external pointer")
        return pos - legacy
    if offset == 0 or offset > pos:
        raise _FleeceError(f"pointer at {pos} has an invalid offset {offset}")
    return pos - offset


def _fleece_slot(buf, pos, wide, shared_keys, depth):
    if pos + 2 > len(buf):
        raise _FleeceError("collection slot runs past the end of the data")
    if buf[pos] & 0x80:
        pos = _fleece_deref(buf, pos, wide)
    return _fleece_value(buf, pos, shared_keys, depth + 1)


def _fleece_value(buf, pos, shared_keys, depth):
    if depth > 200:
        raise _FleeceError("values are nested too deeply")
    if pos + 2 > len(buf):
        raise _FleeceError("value runs past the end of the data")
    b0, b1 = buf[pos], buf[pos + 1]
    tag = b0 >> 4
    if tag == 0:
        small = ((b0 & 0x0F) << 8) | b1
        return small - 0x1000 if small & 0x800 else small
    if tag == 1:
        size = (b0 & 0x07) + 1
        data = buf[pos + 1:pos + 1 + size]
        if len(data) != size:
            raise _FleeceError("integer runs past the end of the data")
        return int.from_bytes(data, "little", signed=not b0 & 0x08)
    if tag == 2:
        fmt, size = ("<d", 8) if b0 & 0x08 else ("<f", 4)
        if pos + 2 + size > len(buf):
            raise _FleeceError("float runs past the end of the data")
        return struct.unpack_from(fmt, buf, pos + 2)[0]
    if tag == 3:
        return {0x00: None, 0x04: False, 0x08: True, 0x0C: _FLEECE_UNDEFINED}[b0 & 0x0C]
    if tag in (4, 5):
        size, start = b0 & 0x0F, pos + 1
        if size == 0x0F:
            size, used = _fleece_uvarint(buf, start)
            start += used
        data = buf[start:start + size]
        if len(data) != size:
            raise _FleeceError("string runs past the end of the data")
        return data.decode("utf-8", "replace") if tag == 4 else bytes(data)
    if tag in (6, 7):
        wide = bool(b0 & 0x08)
        width = 4 if wide else 2
        count = ((b0 & 0x07) << 8) | b1
        first = pos + 2
        if count == 0x7FF:
            # the long count is 2047 plus a varint, padded to an even length (Array.cc)
            extra, used = _fleece_uvarint(buf, first)
            count += extra
            first += used + (used & 1)
        if tag == 6:
            return [_fleece_slot(buf, first + i * width, wide, shared_keys, depth) for i in range(count)]
        result = {}
        for i in range(count):
            key_pos = first + 2 * i * width
            key = _fleece_slot(buf, key_pos, wide, None, depth)
            value = _fleece_slot(buf, key_pos + width, wide, shared_keys, depth)
            if key == -2048:
                # dict inheritance: the value is the parent dict, overridden by the keys after it
                if isinstance(value, dict):
                    result.update(value)
                continue
            if isinstance(key, int) and shared_keys and 0 <= key < len(shared_keys):
                key = shared_keys[key]
            if value is _FLEECE_UNDEFINED:
                result.pop(key, None)
            else:
                result[key] = value
        return result
    raise _FleeceError(f"unexpected pointer at {pos}")


def _fleece_decode(data, shared_keys=None):
    """Return the root value of a Fleece document. Raises _FleeceError on data it cannot read."""
    buf = bytes(data)
    if len(buf) < 2 or len(buf) % 2:
        raise _FleeceError(f"length {len(buf)} is not a positive even number")
    pos = len(buf) - 2
    if buf[pos] & 0x80:
        pos = _fleece_deref(buf, pos, False)
        if buf[pos] & 0x80:
            pos = _fleece_deref(buf, pos, True)
    return _fleece_value(buf, pos, shared_keys, 0)


def _revtree_current_body(data):
    """Body of the first (current) revision in a LiteCore 2.x RawRevTree, or None when that
    revision carries no body."""
    buf = bytes(data)
    if len(buf) < 12:
        raise _FleeceError("revision tree is too short")
    size = struct.unpack_from(">I", buf, 0)[0]
    _parent, flags, rev_id_len = struct.unpack_from(">HBB", buf, 4)
    if size < 8 + rev_id_len or size > len(buf):
        raise _FleeceError(f"revision size {size} does not fit the data")
    if not flags & 0x80:  # RawRevision::kHasData
        return None
    _sequence, used = _fleece_uvarint(buf, 8 + rev_id_len)
    return buf[8 + rev_id_len + used:size]


def _read_cblite(db_path):
    """Yields (table, key, sequence, flags, document or None, error or None) for every row of
    kv_default and kv_del_default. Returns nothing when the store cannot be opened."""
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        shared_keys = None
        if "kv_info" in tables:
            row = db.execute("SELECT body FROM kv_info WHERE key='SharedKeys'").fetchone()
            if row and row[0]:
                try:
                    shared_keys = _fleece_decode(row[0])
                except _FleeceError as ex:
                    logfunc(f"KeepSafe: SharedKeys in {db_path} could not be decoded ({ex}); "
                            "document keys are reported as integers")
        if not isinstance(shared_keys, list):
            shared_keys = None
        for table in ("kv_default", "kv_del_default"):
            if table not in tables:
                continue
            columns = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
            rev_tree_layout = "extra" not in columns
            for key, sequence, flags, body in db.execute(
                    f'SELECT key, sequence, flags, body FROM "{table}" ORDER BY sequence'):
                document, error = None, None
                if body:
                    try:
                        fleece = _revtree_current_body(body) if rev_tree_layout else body
                        document = _fleece_decode(fleece, shared_keys) if fleece else None
                    except (_FleeceError, KeyError, struct.error) as ex:
                        error = str(ex)
                        logfunc(f"KeepSafe: document {key} in {db_path} could not be decoded: {ex}")
                yield table, key, sequence, flags, document, error
    except sqlite3.Error as ex:
        logfunc(f"KeepSafe: error reading {db_path}: {ex}")
    finally:
        db.close()


_APP_CONTAINER_RE = re.compile(r"^(.*/Containers/Data/Application/[^/]+)/")


def _app_container(path):
    match = _APP_CONTAINER_RE.match(str(path).replace("\\", "/"))
    return match.group(1) if match else None


def _photovault_stores(files_found):
    """Photovault db.sqlite3 paths, skipping any container whose metadata plist names
    another app."""
    bundle_ids = {}
    for path in files_found:
        norm = str(path).replace("\\", "/")
        if norm.endswith("/.com.apple.mobile_container_manager.metadata.plist"):
            bundle_ids[_app_container(norm)] = _load_plist(path).get("MCMMetadataIdentifier")
    stores = []
    for path in files_found:
        norm = str(path).replace("\\", "/")
        if not norm.endswith("/photovault/photovault.cblite2/db.sqlite3") or os.path.isdir(path):
            continue
        bundle_id = bundle_ids.get(_app_container(norm))
        if bundle_id and bundle_id != "com.keepsafe.KeepSafe":
            logfunc(f"KeepSafe: skipping {path}, its container belongs to {bundle_id}")
            continue
        stores.append(path)
    return sorted(stores)


def _sniff_format(path):
    try:
        with open(path, "rb") as file_obj:
            head = file_obj.read(32)
    except OSError:
        return ""
    if head.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "WebP"
    if head[4:8] == b"ftyp":
        return f"ISO BMFF, brand '{head[8:12].decode('latin-1').strip()}'"
    return f"unrecognised (first bytes {head[:8].hex()})"


def _as_stored(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return value


def _document_state(table, flags, error):
    if error:
        return "body not decoded"
    if table == "kv_del_default":
        return "deleted (tombstone)"
    if flags and flags & 0x01:
        return "deleted"
    return "live"


@artifact_processor
def keepsafe_photovault_files(context):
    files_found = [str(f) for f in context.get_files_found()]
    media_index = {}
    for path in files_found:
        norm = path.replace("\\", "/")
        for area in ("/Documents/com.getkeepsafe.userMedia/", "/Library/Caches/com.getkeepsafe.userMedia/"):
            if area in norm and not os.path.isdir(path):
                media_index[(_app_container(norm), area, os.path.basename(norm))] = path

    data_list = []
    source_files = []
    for db_path in _photovault_stores(files_found):
        container = _app_container(db_path)
        rows = list(_read_cblite(db_path))
        source_files.append(db_path)
        albums = {key: doc.get("name") for _t, key, _s, _f, doc, _e in rows
                  if isinstance(doc, dict) and doc.get("modelType") == "album"}
        for table, key, _sequence, flags, doc, error in rows:
            if isinstance(doc, dict) and doc.get("modelType") != "file":
                if doc.get("modelType") != "album":  # albums are reported by keepsafe_photovault_albums
                    logfunc(f"KeepSafe: document {key} in {db_path} has modelType "
                            f"{doc.get('modelType')!r} and is not reported")
                continue
            if doc is not None and not isinstance(doc, dict):
                logfunc(f"KeepSafe: document {key} in {db_path} decoded to a "
                        f"{type(doc).__name__}, not a dict; reported with empty fields")
                error = error or f"body decoded to a {type(doc).__name__}"
            doc = doc if isinstance(doc, dict) else {}
            media = [m for m in doc.get("media") or [] if isinstance(m, dict)]
            primary = next((m for m in media if m.get("type") == doc.get("type")), None) or next(
                (m for m in media if m.get("type") not in ("thumbnail", "preview")), {})
            local_hash = primary.get("localHash") or ""
            # the vault's copy is named <localHash>_<media type>; the preview and thumbnail
            # in Caches carry the same <localHash>, the primary rendition's
            candidates = []
            if local_hash:
                candidates = [
                    (primary.get("type") or "", "/Documents/com.getkeepsafe.userMedia/",
                     f"{local_hash}_{primary.get('type')}"),
                    ("preview", "/Library/Caches/com.getkeepsafe.userMedia/", f"{local_hash}_preview"),
                    ("thumbnail", "/Library/Caches/com.getkeepsafe.userMedia/", f"{local_hash}_thumbnail"),
                ]
            shown, media_path = "", ""
            for rendition, area, name in candidates:
                found = media_index.get((container, area, name))
                if found:
                    shown, media_path = rendition, found
                    break
            media_ref = ""
            if media_path:
                media_ref = check_in_media(media_path, doc.get("originalFilename") or "") or ""
                source_files.append(media_path)
            try:
                size_on_disk = os.path.getsize(media_path) if media_path else ""
            except OSError:
                size_on_disk = ""
            album_id = doc.get("albumId") or ""
            data_list.append((
                convert_unix_ts_to_utc(doc.get("importedAt")),
                convert_unix_ts_to_utc(doc.get("createdAtOnDevice")),
                media_ref,
                doc.get("originalFilename") or "",
                albums.get(album_id) or album_id,
                doc.get("vaultType") or "",
                doc.get("type") or "",
                shown,
                _sniff_format(media_path) if media_path else "",
                primary.get("mimeType") or "",
                _as_stored(primary.get("dataSize")),
                size_on_disk,
                _as_stored(primary.get("width")),
                _as_stored(primary.get("height")),
                _as_stored(primary.get("duration")),
                local_hash,
                doc.get("identifierOnDevice") or "",
                _as_stored(doc.get("isInTrash")),
                _as_stored(doc.get("isDeleted")),
                doc.get("backupState") or "",
                "Yes" if flags and flags & 0x08 else "No",
                _document_state(table, flags, error),
                key,
                doc.get("ownerId") or "",
                context.get_relative_path(media_path) if media_path else "",
            ))

    data_headers = (
        ("Imported At", "datetime"),
        ("Created At On Device", "datetime"),
        ("Media", "media"),
        "Original Filename",
        "Album",
        "Vault Type",
        "Item Type",
        "Rendition Shown",
        "Format of File Shown (sniffed)",
        "MIME Type (as stored)",
        "Recorded Size (bytes)",
        "Size of File Shown (bytes)",
        "Width",
        "Height",
        "Duration",
        "Local Hash (as stored)",
        "Identifier On Device (as stored)",
        "In Trash",
        "Is Deleted",
        "Backup State (as stored)",
        "Pushed to Server (LiteCore flag)",
        "Document State",
        "Document ID",
        "Owner ID",
        "File Shown",
    )
    return data_headers, data_list, "\n".join(dict.fromkeys(source_files))


@artifact_processor
def keepsafe_photovault_albums(context):
    files_found = [str(f) for f in context.get_files_found()]
    data_list = []
    source_files = []
    for db_path in _photovault_stores(files_found):
        rows = list(_read_cblite(db_path))
        source_files.append(db_path)
        file_counts = {}
        for _t, _k, _s, _f, doc, _e in rows:
            if isinstance(doc, dict) and doc.get("modelType") == "file":
                file_counts[doc.get("albumId")] = file_counts.get(doc.get("albumId"), 0) + 1
        for table, key, _sequence, flags, doc, error in rows:
            if not isinstance(doc, dict) or doc.get("modelType") != "album":
                continue
            data_list.append((
                convert_unix_ts_to_utc(doc.get("createdAt")),
                doc.get("name") or "",
                doc.get("type") or "",
                doc.get("specialType") or "",
                file_counts.get(key, 0),
                doc.get("fileSortMode") or "",
                _as_stored(doc.get("sharedWith")),
                _as_stored(doc.get("isAvailableOffline")),
                _as_stored(doc.get("isDeleted")),
                "Yes" if flags and flags & 0x08 else "No",
                _document_state(table, flags, error),
                key,
                doc.get("ownerId") or "",
            ))

    data_headers = (
        ("Created At", "datetime"),
        "Album Name",
        "Album Type (as stored)",
        "Special Type (as stored)",
        "File Documents Naming This Album",
        "File Sort Mode (as stored)",
        "Shared With",
        "Available Offline",
        "Is Deleted",
        "Pushed to Server (LiteCore flag)",
        "Document State",
        "Document ID",
        "Owner ID",
    )
    return data_headers, data_list, "\n".join(source_files)
