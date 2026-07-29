__artifacts_v2__ = {
    "iosFileSystemEvents": {
        "name": "FSEvents",
        "description": "Path-level file-system event records from the fseventsd disk log stream",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "FSEvents records do not contain per-event timestamps. Event IDs provide sequence, "
            "not time. Notifications can be coalesced, paths can be truncated, and a record "
            "does not establish which process or user caused an event. Interpret flags as file-"
            "system notifications and correlate them with other evidence. Supports gzip-wrapped "
            "1SLD, 2SLD, and 3SLD streams. Format and flag research: Joachim Metz/libyal and "
            "Yogesh Khatri/mac_apt. References: https://github.com/libyal/dtformats/blob/main/"
            "documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format."
            "asciidoc and https://github.com/ydkhatri/mac_apt/blob/master/plugins/fsevents.py"
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file-search",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 11939 rows",
        },
    },
    "iosFileSystemEventsCommunications": {
        "name": "FSEvents - Communications & Accounts",
        "description": "FSEvents paths associated with communications, contacts, calls, and accounts",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This is a path-based subset of iOS File System Events. A matching path shows a "
            "file-system notification, not message content or proof of a user communication. "
            "Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "messages",
        "sample_data": {},
    },
    "iosFileSystemEventsUpdates": {
        "name": "FSEvents - Updates & Mobile Assets",
        "description": (
            "FSEvents paths associated with system updates, installation, and MobileAsset activity"
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This is a path-based subset. MobileAsset rows can represent many kinds of downloaded "
            "Apple assets and are not necessarily operating-system updates. Matching notifications "
            "do not, alone, prove completion or identify an actor. Rows can overlap other Items of "
            "Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile-up",
        "sample_data": {},
    },
    "iosFileSystemEventsAppContainers": {
        "name": "FSEvents - App Containers",
        "description": "FSEvents paths within application and shared application containers",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "Container UUIDs should be mapped to bundle identifiers using container metadata. "
            "A container-path notification does not establish application execution or user "
            "interaction. Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "apps",
        "sample_data": {},
    },
    "iosFileSystemEventsLocation": {
        "name": "FSEvents - Location Services",
        "description": "FSEvents paths associated with location and routing services",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This is a path-based service-activity subset. It does not contain coordinates and "
            "does not establish the device's location. Rows can overlap other Items of Interest "
            "reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin",
        "sample_data": {},
    },
    "iosFileSystemEventsSecurity": {
        "name": "FSEvents - Security",
        "description": "FSEvents paths associated with keychains, keybags, trust, and access control",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This path-based subset does not expose credentials, prove authentication, or identify "
            "an actor. Interpret notifications with the underlying artifacts and system logs. "
            "Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield-lock",
        "sample_data": {},
    },
    "iosFileSystemEventsRestoreBackup": {
        "name": "FSEvents - Restore & Backup",
        "description": "FSEvents paths specifically associated with restore, erase, and backup services",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This conservative path-based subset excludes generic 'no backup' preference names. "
            "A matching notification is not, by itself, proof that a restore, erase, or backup "
            "completed. Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "restore",
        "sample_data": {},
    },
    "iosFileSystemEventsWeb": {
        "name": "FSEvents - Web",
        "description": "FSEvents paths associated with Safari, WebKit, and browser storage",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "This is a path-based subset and does not contain browsing content or prove a website "
            "visit. Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "world",
        "sample_data": {},
    },
    "iosFileSystemEventsPackageManagement": {
        "name": "FSEvents - APT & dpkg",
        "description": "FSEvents paths associated with APT, dpkg, Cydia, Sileo, and Zebra",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "These paths can support investigation of nonstandard package-management activity. "
            "They are not labeled as proof of jailbreak status and should be correlated with "
            "other device evidence. Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {},
    },
    "iosFileSystemEventsRemoved": {
        "name": "FSEvents - Removed Paths",
        "description": "FSEvents records carrying the Removed event flag",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-29",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "File System",
        "notes": (
            "The Removed flag is a file-system notification, not proof of intentional user "
            "deletion. Events can be coalesced and can carry Created and Removed together. "
            "Rows can overlap other Items of Interest reports."
        ),
        "paths": ("*/private/var/.fseventsd/*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "trash",
        "sample_data": {},
    },
}

import atexit
import os
import sqlite3
import struct
import tempfile
import zlib

from scripts.ilapfuncs import artifact_processor, logfunc


_FLAGS = (
    (0x00000001, "Created"),
    (0x00000002, "Removed"),
    (0x00000004, "Inode metadata modified"),
    (0x00000008, "Renamed or moved"),
    (0x00000010, "Content modified"),
    (0x00000020, "Exchanged"),
    (0x00000040, "Finder information modified"),
    (0x00000080, "Directory created"),
    (0x00000100, "Permissions changed"),
    (0x00000200, "Extended attribute modified"),
    (0x00000400, "Extended attribute removed"),
    (0x00000800, "Document ID created"),
    (0x00001000, "Document revision"),
    (0x00002000, "Unmount pending"),
    (0x00004000, "Item cloned"),
    (0x00010000, "Clone notification"),
    (0x00020000, "Path truncated"),
    (0x00040000, "Remote directory event"),
    (0x00080000, "Last hard link removed"),
    (0x00100000, "Hard link"),
    (0x00400000, "Symbolic link"),
    (0x00800000, "File"),
    (0x01000000, "Directory"),
    (0x02000000, "Mount"),
    (0x04000000, "Unmount"),
    (0x20000000, "End of transaction"),
)
_KNOWN_FLAG_MASK = sum(value for value, _name in _FLAGS)
_RECORD_STRUCTS = {
    b"1SLD": struct.Struct("<QI"),
    b"2SLD": struct.Struct("<QIQ"),
    b"3SLD": struct.Struct("<QIQI"),
}
_COMMUNICATIONS = 1 << 0
_UPDATES = 1 << 1
_APP_CONTAINERS = 1 << 2
_LOCATION = 1 << 3
_SECURITY = 1 << 4
_RESTORE_BACKUP = 1 << 5
_WEB = 1 << 6
_PACKAGE_MANAGEMENT = 1 << 7
_REMOVED = 1 << 8
_REPORT_HEADERS = (
    "Event ID",
    "Path",
    "Event Flags",
    "Event Flags (Hex)",
    "Item Type",
    "Node ID",
    "Record Extra",
    "Format Version",
    "Source File",
)
_CACHE = {"key": None, "path": None}


def _path_has_component(path, names):
    components = set(path.replace("\\", "/").casefold().split("/"))
    return bool(components.intersection(names))


def _interest_mask(path, flags):
    normalized = path.replace("\\", "/").casefold()
    mask = 0

    if any(marker in normalized for marker in (
        "/sms/", "sms.db", "sms-temp.db", "imagent", "callhistory", "addressbook",
        "/accounts/", "accounts3", "/mail/", "mobilemail", "com.apple.messages",
        "activitymessagesapp", "icloud.apps.messages.business", "facetime",
    )):
        mask |= _COMMUNICATIONS

    if any(marker in normalized for marker in (
        "mobilesoftwareupdate", "softwareupdate", "mobile_installation",
        "mobileinstallation", "/installd/", "installcoordination", "mobileasset",
        "launchservices", "containermanagerd/staging",
    )):
        mask |= _UPDATES

    if any(marker in normalized for marker in (
        "containers/data/application/", "containers/bundle/application/",
        "containers/shared/appgroup/",
    )):
        mask |= _APP_CONTAINERS

    if any(marker in normalized for marker in (
        "locationd", "routined", "geoservices", "corelocation", "trackingavoidance",
    )) or _path_has_component(normalized, {"maps"}):
        mask |= _LOCATION

    if any(marker in normalized for marker in (
        "keychain", "keybags", "/lockdown", "passcode", "/tcc/", "trustd",
        "protectedcloudstorage",
    )):
        mask |= _SECURITY

    if (
        any(marker in normalized for marker in (
            "mobilesoftwareupdate/restore.log", "mobilebackup", "backupd",
            ".obliterated", "erase_install", "erase-install",
        ))
        or _path_has_component(normalized, {"backup", "backups"})
    ):
        mask |= _RESTORE_BACKUP

    if any(marker in normalized for marker in (
        "safari", "/webkit/", "browserstate", "safaritabs", "/cookies/",
    )):
        mask |= _WEB

    if _path_has_component(normalized, {"apt", "dpkg", "cydia", "sileo", "zebra"}) or any(
        marker in normalized for marker in ("dpkg-", "dpkg.", "apt-", "apt.")
    ):
        mask |= _PACKAGE_MANAGEMENT

    if flags & 0x00000002:
        mask |= _REMOVED

    return mask


def _remove_cache():
    if _CACHE["path"]:
        try:
            os.unlink(_CACHE["path"])
        except FileNotFoundError:
            pass
    _CACHE["key"] = None
    _CACHE["path"] = None


atexit.register(_remove_cache)


def _decode_flags(flags):
    names = [name for value, name in _FLAGS if flags & value]
    unknown = flags & ~_KNOWN_FLAG_MASK
    if unknown:
        names.append(f"Unknown flag bits 0x{unknown:08X}")
    return " | ".join(names) if names else "None"


def _item_type(flags):
    types = []
    for value, label in (
        (0x00800000, "File"),
        (0x01000000, "Directory"),
        (0x00400000, "Symbolic link"),
        (0x00100000, "Hard link"),
    ):
        if flags & value:
            types.append(label)
    return " | ".join(types)


def _decompress_members(compressed):
    remaining = compressed
    while remaining:
        decompressor = zlib.decompressobj(31)
        try:
            member = decompressor.decompress(remaining)
            member += decompressor.flush()
        except zlib.error:
            return
        if member:
            yield member
        if not decompressor.unused_data:
            return
        remaining = decompressor.unused_data


def _parse_stream(stream):
    offset = 0
    stream_length = len(stream)

    while offset + 12 <= stream_length:
        signature, _unknown, page_size = struct.unpack_from("<4sII", stream, offset)
        record_struct = _RECORD_STRUCTS.get(signature)
        if record_struct is None or page_size < 12:
            return

        page_end = offset + page_size
        if page_end > stream_length:
            return
        position = offset + 12

        while position < page_end:
            terminator = stream.find(b"\x00", position, page_end)
            if terminator < 0:
                break
            path = stream[position:terminator].decode("utf-8", errors="backslashreplace")
            position = terminator + 1
            if position + record_struct.size > page_end:
                break

            values = record_struct.unpack_from(stream, position)
            position += record_struct.size
            event_id, flags = values[:2]
            node_id = values[2] if len(values) >= 3 else None
            record_extra = values[3] if len(values) == 4 else None
            yield (
                event_id,
                path,
                _decode_flags(flags),
                f"0x{flags:08X}",
                _item_type(flags),
                node_id,
                record_extra,
                signature[:1].decode("ascii"),
                flags,
            )

        offset = page_end


def _cache_key(files_found):
    key = []
    for file_found in sorted(str(path) for path in files_found):
        try:
            stat_result = os.stat(file_found)
            key.append((file_found, stat_result.st_size, stat_result.st_mtime_ns))
        except OSError:
            key.append((file_found, None, None))
    return tuple(key)


def _cache_integer(value):
    if value is None or -(1 << 63) <= value < (1 << 63):
        return value
    return str(value)


def _build_cache(context):
    files_found = context.get_files_found()
    key = _cache_key(files_found)
    if key == _CACHE["key"] and _CACHE["path"] and os.path.exists(_CACHE["path"]):
        return _CACHE["path"]

    _remove_cache()
    descriptor, cache_path = tempfile.mkstemp(prefix="ileapp_fsevents_", suffix=".sqlite")
    os.close(descriptor)

    database = sqlite3.connect(cache_path)
    try:
        database.execute("""
            CREATE TABLE events (
                event_id,
                path TEXT,
                event_flags TEXT,
                event_flags_hex TEXT,
                item_type TEXT,
                node_id,
                record_extra INTEGER,
                format_version TEXT,
                source_file TEXT,
                interest_mask INTEGER
            )
        """)
        insert_query = "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        pending = []

        for file_found in files_found:
            file_found = str(file_found)
            relative_path = context.get_relative_path(file_found)
            try:
                with open(file_found, "rb") as event_file:
                    compressed = event_file.read()
            except OSError as ex:
                logfunc(f"Failed to read FSEvents file {relative_path}: {ex}")
                continue

            for member in _decompress_members(compressed):
                for row in _parse_stream(member):
                    event_id, path, flags_text, flags_hex, item_type, node_id, record_extra, \
                        format_version, raw_flags = row
                    pending.append((
                        _cache_integer(event_id),
                        path,
                        flags_text,
                        flags_hex,
                        item_type,
                        _cache_integer(node_id),
                        record_extra,
                        format_version,
                        relative_path,
                        _interest_mask(path, raw_flags),
                    ))
                    if len(pending) >= 10000:
                        database.executemany(insert_query, pending)
                        pending.clear()

        if pending:
            database.executemany(insert_query, pending)
        database.execute("CREATE INDEX events_interest_mask ON events(interest_mask)")
        database.commit()
    except (OSError, sqlite3.Error):
        database.close()
        try:
            os.unlink(cache_path)
        except FileNotFoundError:
            pass
        raise
    database.close()

    _CACHE["key"] = key
    _CACHE["path"] = cache_path
    return cache_path


def _report_rows(context, interest_mask=None):
    cache_path = _build_cache(context)
    query = """
        SELECT event_id, path, event_flags, event_flags_hex, item_type, node_id,
               record_extra, format_version, source_file
        FROM events
    """
    parameters = ()
    if interest_mask is not None:
        query += " WHERE (interest_mask & ?) != 0"
        parameters = (interest_mask,)
    query += " ORDER BY rowid"

    with sqlite3.connect(f"file:{cache_path}?mode=ro", uri=True) as database:
        data_list = list(database.execute(query, parameters))
    sources = "\n".join(dict.fromkeys(row[-1] for row in data_list))
    return _REPORT_HEADERS, data_list, sources


@artifact_processor
def iosFileSystemEvents(context):
    return _report_rows(context)


@artifact_processor
def iosFileSystemEventsCommunications(context):
    return _report_rows(context, _COMMUNICATIONS)


@artifact_processor
def iosFileSystemEventsUpdates(context):
    return _report_rows(context, _UPDATES)


@artifact_processor
def iosFileSystemEventsAppContainers(context):
    return _report_rows(context, _APP_CONTAINERS)


@artifact_processor
def iosFileSystemEventsLocation(context):
    return _report_rows(context, _LOCATION)


@artifact_processor
def iosFileSystemEventsSecurity(context):
    return _report_rows(context, _SECURITY)


@artifact_processor
def iosFileSystemEventsRestoreBackup(context):
    return _report_rows(context, _RESTORE_BACKUP)


@artifact_processor
def iosFileSystemEventsWeb(context):
    return _report_rows(context, _WEB)


@artifact_processor
def iosFileSystemEventsPackageManagement(context):
    return _report_rows(context, _PACKAGE_MANAGEMENT)


@artifact_processor
def iosFileSystemEventsRemoved(context):
    return _report_rows(context, _REMOVED)
