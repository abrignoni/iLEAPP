__artifacts_v2__ = {
    "containerManagerState": {
        "name": "Container Manager State",
        "description": "Container records with a directory entry in the container manager state (iOS 27 sysdiagnose logs/ContainerManager/state.json), with the stored directory times",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-17",
        "last_update_date": "2026-10-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "The iOS 27.0 sysdiagnose tested carries logs/ContainerManager/state.json and not the "
                 "MobileContainerManager and appinstallation text logs. The folder and file name point to the "
                 "container manager; what writes the file and when is not established. A row is a container "
                 "record that has a directory entry (node) in the file, with the birthtime, ctime, mtime and "
                 "lastSeen values stored for it, converted to UTC. A numeric time value is not converted, "
                 "because its epoch and unit are not established; the cell is left blank and the raw value "
                 "is given in Notes. birthtime, ctime and mtime are named like the file system's directory "
                 "time fields; how the daemon fills them is not established. lastSeen is converted to UTC "
                 "like the other three times; what sets it is not established. A birth time need not be the "
                 "first install of the app, and none of these times shows who installed the app or when it "
                 "was opened. Container Class is the class folder the file's class table names for the "
                 "record's group. When the table has no entry, a table held by this parser supplies the "
                 "folder name. Data/Application holds an app's data container and Bundle/Application its "
                 "bundle, per Apple's File System Programming Guide; Data/PluginKitPlugin and Shared/AppGroup "
                 "are the folder names as stored. Host App is the parent identifier the file's childParentMap "
                 "pairs with the identifier; it is filled only for Data/PluginKitPlugin records. State is "
                 "'present' when the record has a node object, 'corrupt' or 'ignored' when the file's corrupt "
                 "or ignore flag is true, and 'invalid' when the record or node has an unexpected shape. "
                 "Path is built by this parser from the class folder and the directory name; the container "
                 "record does not carry a path field. In the tested sysdiagnose the directory name matched "
                 "the UUID that mobile_installation.log names for the directory. Container UUID is the "
                 "record's uuid value. In the tested sysdiagnose it differed from the directory name. "
                 "Generation is the record's generation value read as an integer; its meaning is not "
                 "established. Owner is the stored ownership string. Scope is the file's top-level key as "
                 "stored. A record can be absent for reasons outside this file, so an empty result is not "
                 "evidence that no app was present. Not reported here: the records with no directory (see "
                 "'Container Manager State - No Directory'), the code-signing registrations (see 'Container "
                 "Manager State - Registrations'), the daemon's recent client processes, the container class "
                 "folder table, the persona tables and the entitlement values, none of which is a container "
                 "record. Observed on one iOS 27.0 (24A437) sysdiagnose: 1,738 containers with a directory, "
                 "419 without, 1,799 registrations. A copy with the identifiers replaced and the times shifted by one offset is the "
                 "test case case_ios27_sanitized. The "
                 "iOS 26 (23G71) sysdiagnose tested has no ContainerManager folder. Other versions are not "
                 "checked.",
        "paths": (
            '*/ContainerManager/state.json',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "hc_ios26_sysdiag": "iOS 26 (23G71) | 0 rows; the archive carries no ContainerManager folder",
        }
    },
    "containerManagerStateNoDirectory": {
        "name": "Container Manager State - No Directory",
        "description": "Container records with no directory entry in the container manager state (iOS 27 sysdiagnose logs/ContainerManager/state.json)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-17",
        "last_update_date": "2026-10-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A row is a container record whose directory entry (node) is null in the file. In the "
                 "tested sysdiagnose these records carry no directory times, and 418 of the 419 carry a "
                 "generation of -1. The "
                 "file does not say why the entry is null: the container may have been removed, replaced "
                 "by a new directory, or not yet created, and these cannot be told apart from this file "
                 "alone. This file alone does not show an uninstall. Directory Name is the record's pathIdentifier "
                 "value as stored. Host App is the parent identifier the file's childParentMap pairs with "
                 "the identifier; it is filled only for Data/PluginKitPlugin records. Generation is the "
                 "record's generation value read as an integer; its meaning is not established. Scope is the "
                 "file's top-level key as stored. An empty result is not evidence that nothing was removed. Observed on one iOS "
                 "27.0 (24A437) sysdiagnose: 419 containers without a directory (1,738 with a directory, "
                 "1,799 registrations). A copy with the identifiers replaced and the times shifted by one offset is the "
                 "test case case_ios27_sanitized. Other versions are "
                 "not checked.",
        "paths": (
            '*/ContainerManager/state.json',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package-off",
        "sample_data": {
            "hc_ios26_sysdiag": "iOS 26 (23G71) | 0 rows; the archive carries no ContainerManager folder",
        }
    },
    "containerManagerStateRegistrations": {
        "name": "Container Manager State - Registrations",
        "description": "Code-signing registrations cached by the container manager (iOS 27 sysdiagnose logs/ContainerManager/state.json)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-17",
        "last_update_date": "2026-10-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "One row per entry of the daemon's ordered code-signing registration cache: the identifier, "
                 "the container class number stored for it, shown as the class folder when the file's class "
                 "table names one and as the number otherwise, and the flags the file stores (invalid, "
                 "placeholder, registeredByCaller, advanceCopy, registeredByKernel; only the true ones are "
                 "listed). State is 'invalid' or 'placeholder' when the file's flag of that name is true; "
                 "otherwise blank. Position in Cache is the entry's place in the stored order within its "
                 "scope; the file does not state what the order means. A cache entry is not proof that an "
                 "app is or was installed: it lists identifiers the daemon registered; in the tested "
                 "sysdiagnose these included extension and group identifiers. The entitlement values are "
                 "not copied; only the number of entitlement keys is reported. Scope is the file's top-level key as stored. An empty result is not "
                 "evidence that nothing was registered. Observed on one "
                 "iOS 27.0 (24A437) sysdiagnose: 1,799 registrations (1,738 containers with a directory, "
                 "419 without). A copy with the identifiers replaced and the times shifted by one offset is the "
                 "test case case_ios27_sanitized. Other versions are not "
                 "checked.",
        "paths": (
            '*/ContainerManager/state.json',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "certificate",
        "sample_data": {
            "hc_ios26_sysdiag": "iOS 26 (23G71) | 0 rows; the archive carries no ContainerManager folder",
        }
    }
}

"""Pure-Python core for the iOS 27 ``logs/ContainerManager/state.json`` sysdiagnose file.

No I/O assumptions: the input is raw bytes/str or an already parsed JSON object, the output is a
list of rows (dicts) with a fixed set of columns (``COLUMNS``). Nothing here prints, opens files or
raises on malformed input; problems are reported through the ``warn`` callback and, per row, in the
``notes`` column. Unknown keys are kept as JSON text in the ``other`` column.

What the file is (observed on iOS 27.0 build 24A437; see the contribution notes for what is fact
and what is inference): a dump of the container manager daemon's in-memory state, one section per
scope (``"<system>"`` and one per user id), each holding

* ``containers``       -> {group: {identifier: record}}; group is ``<kind>-<persona>[-T]`` such as
                          ``appData-501``; record has uuid, pathIdentifier, generation, ``node``
                          (birthtime/ctime/mtime/lastSeen, or null when no directory node exists)
* ``codesignCache``    -> ``orderedEntries``: cached code-signing registrations (an ordered cache)
* ``childParentMap``   -> {extension identifier: host application identifier}
* ``clientCache``      -> ``mru``: recent client processes that called the daemon
* ``containerClassPaths`` -> class number -> on-disk class directory for each persona
* ``personas``         -> persona / managed-path tables

The rows are evidence of what the daemon knew when the snapshot was taken, not of what the user did.
"""


import json
import logging
import math
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

try:  # Python 3.11+
    from datetime import UTC
except ImportError:  # pragma: no cover - Python 3.10
    UTC = timezone(timedelta(0), "UTC")

CORE_VERSION = "1.0"
LOGGER = logging.getLogger(__name__)

COLUMNS: tuple[str, ...] = (
    "record_type",  # one of RECORD_TYPES
    "scope",  # "system" or "uid:<n>"
    "timestamp_utc",  # ISO-8601 UTC with milliseconds, '' when the row has no time
    "timestamp_desc",  # what timestamp_utc means
    "container_class",  # group name without persona suffix (appData, pluginData, ...) or source table
    "class_id",  # numeric container class where known, else ''
    "class_label",  # class directory leaf (Data/Application, ...) where known
    "persona",  # persona id from the group suffix / table key
    "identifier",  # app, extension, group, process or class identifier (raw)
    "path",  # derived directory (class directory + pathIdentifier) or a path from the file
    "uuid",  # container uuid (daemon identity; NOT the directory name)
    "path_identifier",  # directory name of the container
    "state",  # present | no_node | corrupt | ignored | invalid | placeholder | ...
    "generation",
    "schema_version",
    "owner",  # posixOwnership / owner string
    "birthtime",
    "ctime",
    "mtime",
    "last_seen",
    "parent_identifier",  # host application for an extension container
    "flags",  # comma separated true flags
    "source_file",
    "row_index",  # position within the source list/dict (file order)
    "notes",
    "other",  # JSON text of keys this core does not know
)

RECORD_TYPES: tuple[str, ...] = (
    "container",
    "codesign",
    "child_parent",
    "client",
    "class_path",
    "persona",
    "managed_path",
    "unknown_section",
)

# MCM container class numbers, validated against containerClassPaths in the sample (see notes).
GROUP_CLASS_IDS: dict[str, int] = {
    "app": 1,
    "appData": 2,
    "pluginData": 4,
    "appGroup": 7,
    "daemon": 10,
    "systemData": 12,
    "systemGroup": 13,
    "perUserApp": 14,
    "protectedSystem": 15,
}
CLASS_LABELS: dict[int, str] = {
    1: "Bundle/Application",
    2: "Data/Application",
    3: "Bundle/PluginKitPlugin",
    4: "Data/PluginKitPlugin",
    5: "Bundle/VPNPlugin",
    7: "Shared/AppGroup",
    8: "Bundle/Framework",
    10: "Data/InternalDaemon",
    12: "Data/System",
    13: "Shared/SystemGroup",
    14: "Bundle/Application",
    15: "Data/ProtectedSystem",
}

_CONTAINER_KEYS = {
    "corrupt",
    "generation",
    "ignore",
    "node",
    "pathIdentifier",
    "posixOwnership",
    "schemaVersion",
    "uuid",
}
_NODE_KEYS = {"birthtime", "ctime", "lastSeen", "mtime"}
_CODESIGN_KEYS = {
    "advanceCopy",
    "containerClass",
    "entitlements",
    "identifier",
    "invalid",
    "placeholder",
    "registeredByCaller",
    "registeredByKernel",
}
_CODESIGN_FLAGS = ("advanceCopy", "invalid", "placeholder", "registeredByCaller", "registeredByKernel")
_CLIENT_KEYS = {
    "entitlements",
    "identifier",
    "isPlatformBinary",
    "isSandboxed",
    "isSignatureValid",
    "isSigned",
    "launchPersona",
    "persona",
    "pid",
    "platform",
    "proximate",
    "sandboxContainer",
    "user",
}
_CLIENT_FLAGS = ("isPlatformBinary", "isSandboxed", "isSignatureValid", "isSigned")
_CLASS_PATH_KEYS = {
    "base",
    "caseSensitive",
    "caseSensitiveDetermined",
    "category",
    "categoryOwner",
    "class",
    "classOwner",
    "exists",
    "persona",
    "supportsDP",
    "supportsDPDetermined",
}
_PERSONA_KEYS = {
    "homeDirectory",
    "identifier",
    "kernelPersonaID",
    "kernelPersonaType",
    "personaType",
    "personaUniqueString",
    "posixUser",
}
_SCOPE_KEYS = {"childParentMap", "clientCache", "codesignCache", "containerClassPaths", "containers", "personas"}

# 1990-01-01 .. 2100-01-01 UTC: anything else is reported as a bad timestamp instead of a date.
_MIN_EPOCH = 631152000.0
_MAX_EPOCH = 4102444800.0
_INT64_MAX = 2**63 - 1
_OTHER_CAP = 2000

Warn = Callable[[str], None]


def _default_warn(message: str) -> None:
    LOGGER.warning(message)


class _Ctx:
    """Per-run state: warning sink, source file label and the running row counters."""

    def __init__(self, source_file: str, warn: Warn | None) -> None:
        self.source_file = source_file
        self.warn = warn or _default_warn
        self.counters: dict[str, int] = {}
        self.rows: list[dict[str, Any]] = []

    def add(self, row: dict[str, Any]) -> None:
        kind = row["record_type"]
        index = self.counters.get(kind, 0)
        self.counters[kind] = index + 1
        row["row_index"] = index if row.get("row_index") in (None, "") else row["row_index"]
        row["source_file"] = self.source_file
        self.rows.append(row)


def _blank(record_type: str, scope: str) -> dict[str, Any]:
    row: dict[str, Any] = dict.fromkeys(COLUMNS, "")
    row["record_type"] = record_type
    row["scope"] = scope
    return row


def _text(value: Any) -> str:
    """Scalar -> str; containers and None -> ''."""
    if value is None or isinstance(value, (dict, list)):
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _number(value: Any, notes: list[str], name: str) -> Any:
    """Integer-like -> int (or str when it does not fit 64 bits); anything else -> '' + a note."""
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        notes.append(f"{name}: unexpected boolean")
        return ""
    try:
        if isinstance(value, float):
            if not math.isfinite(value):
                notes.append(f"{name}: non-finite number")
                return ""
            if abs(value) > _INT64_MAX:
                notes.append(f"{name}: number outside 64-bit range")
                return ""
            value = int(value)
        elif isinstance(value, str):
            value = int(value.strip())
        elif not isinstance(value, int):
            notes.append(f"{name}: unexpected type {type(value).__name__}")
            return ""
    except (ValueError, OverflowError):
        notes.append(f"{name}: not a number")
        return ""
    if abs(value) > _INT64_MAX:
        notes.append(f"{name}: integer outside 64-bit range kept as text")
        return str(value)
    return value


def parse_timestamp(value: Any) -> tuple[str, str]:
    """Return (normalised UTC ISO text with milliseconds, '') or ('', reason).

    Strings: ISO-8601 (``...Z`` or with an offset; a missing zone is taken as UTC and said so).
    Numbers: not converted. A number's epoch and unit cannot be told from its magnitude (a
    Cocoa-epoch second count also falls inside the Unix range), so the raw value is returned in
    the reason instead of a date.
    """
    if value is None or value == "":
        return "", ""
    if isinstance(value, bool):
        return "", "boolean is not a timestamp"
    moment: datetime | None = None
    reason = ""
    try:
        if isinstance(value, str):
            text = value.strip()
            if text.endswith(("Z", "z")):
                text = text[:-1] + "+00:00"
            moment = datetime.fromisoformat(text)
            if moment.tzinfo is None:
                moment = moment.replace(tzinfo=UTC)
                reason = "no zone, taken as UTC"
            moment = moment.astimezone(UTC)
        elif isinstance(value, (int, float)):
            return "", f"numeric value {value!r} not converted; its epoch and unit are not established"
        else:
            return "", f"unsupported timestamp type {type(value).__name__}"
    except (ValueError, OverflowError, OSError):
        return "", "unparseable timestamp"
    if not (_MIN_EPOCH <= moment.timestamp() <= _MAX_EPOCH):
        return "", "timestamp out of range"
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z"), reason


def _other(extra: dict[str, Any]) -> str:
    if not extra:
        return ""
    try:
        text = json.dumps(extra, sort_keys=True, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = repr(extra)
    return text if len(text) <= _OTHER_CAP else text[:_OTHER_CAP] + "...[truncated]"


def _extra(record: dict[str, Any], known: set[str]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in known}


def _scope_name(key: str) -> str:
    if key == "<system>":
        return "system"
    return f"uid:{key}"


def parse_group(group: str) -> tuple[str, str, bool]:
    """'appData-501' -> ('appData', '501', False); 'perUserApp-501-T' -> (..., True)."""
    text = group
    transient = False
    if text.endswith("-T"):
        transient = True
        text = text[:-2]
    kind, _, persona = text.rpartition("-")
    if not kind:
        return group, "", transient
    return kind, persona, transient


def load_json(data: Any, warn: Warn | None = None) -> Any:
    """bytes/str -> parsed JSON; dict/list passes through. Returns None (and warns) on failure."""
    warn = warn or _default_warn
    if isinstance(data, (dict, list)):
        return data
    if isinstance(data, (bytes, bytearray, memoryview)):
        raw = bytes(data)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", "replace")
            warn("state file is not valid UTF-8; undecodable bytes were replaced")
    elif isinstance(data, str):
        text = data
    else:
        warn(f"state input has unsupported type {type(data).__name__}")
        return None
    if not text.strip():
        warn("state file is empty")
        return None
    try:
        return json.loads(text)
    except (ValueError, RecursionError) as exc:
        warn(f"state file is not valid JSON (truncated or damaged): {type(exc).__name__}")
        return None


def _class_tables(scope_data: dict[str, Any]) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    """containerClassPaths -> {table: {persona: {class_id: entry}}} (tolerant of bad shapes)."""
    out: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    tables = scope_data.get("containerClassPaths")
    if not isinstance(tables, dict):
        return out
    for table, personas in tables.items():
        if not isinstance(personas, dict):
            continue
        for persona, classes in personas.items():
            if not isinstance(classes, dict):
                continue
            for class_id, entry in classes.items():
                if isinstance(entry, dict):
                    out.setdefault(str(table), {}).setdefault(str(persona), {})[str(class_id)] = entry
    return out


def _label_for(class_id: Any, persona: str, tables: dict[str, dict[str, dict[str, dict[str, Any]]]]) -> str:
    entry = tables.get("MCMContainerClassPath", {}).get(persona, {}).get(str(class_id))
    if entry:
        category = _text(entry.get("category")).rstrip("/").rsplit("/", 1)[-1]
        leaf = _text(entry.get("class")).rstrip("/").rsplit("/", 1)[-1]
        if category and leaf:
            return f"{category}/{leaf}"
    try:
        return CLASS_LABELS.get(int(class_id), "")
    except (TypeError, ValueError):
        return ""


def _container_rows(ctx: _Ctx, scope: str, data: dict[str, Any], tables: dict, parents: dict[str, str]) -> None:
    containers = data.get("containers")
    if containers is None:
        return
    if not isinstance(containers, dict):
        ctx.warn(f"{scope}: containers is {type(containers).__name__}, expected an object")
        return
    for group, members in containers.items():
        kind, persona, transient = parse_group(str(group))
        class_id = GROUP_CLASS_IDS.get(kind)
        label = _label_for(class_id, persona, tables) if class_id is not None else ""
        if not isinstance(members, dict):
            ctx.warn(f"{scope}: container group has an unexpected shape ({type(members).__name__})")
            continue
        if class_id is None:
            ctx.warn(f"{scope}: unknown container group kind '{kind}' kept without a class")
        table = "MCMContainerClassTransientPath" if transient else "MCMContainerClassPath"
        class_entry = tables.get(table, {}).get(persona, {}).get(str(class_id), {}) if class_id is not None else {}
        class_dir = _text(class_entry.get("class")).rstrip("/")
        for position, (identifier, record) in enumerate(members.items()):
            row = _blank("container", scope)
            row.update(
                container_class=kind + ("-T" if transient else ""),
                class_id=class_id if class_id is not None else "",
                class_label=label,
                persona=persona,
                identifier=str(identifier),
                row_index=position,
            )
            notes: list[str] = []
            if class_id is None:
                notes.append("unknown container group")
            if not isinstance(record, dict):
                row.update(state="invalid", other=_other({"value": record}))
                notes.append("record is not an object")
                row["notes"] = "; ".join(notes)
                ctx.add(row)
                continue
            path_identifier = _text(record.get("pathIdentifier"))
            row.update(
                uuid=_text(record.get("uuid")),
                path_identifier=path_identifier,
                generation=_number(record.get("generation"), notes, "generation"),
                schema_version=_number(record.get("schemaVersion"), notes, "schemaVersion"),
                owner=_text(record.get("posixOwnership")),
            )
            if class_dir and path_identifier:
                row["path"] = f"{class_dir}/{path_identifier}"
            flags = [name for name, key in (("corrupt", "corrupt"), ("ignored", "ignore")) if record.get(key) is True]
            for key in ("corrupt", "ignore"):
                if key in record and not isinstance(record[key], bool):
                    notes.append(f"{key}: unexpected type {type(record[key]).__name__}")
            row["flags"] = ",".join(flags)
            node = record.get("node")
            extra = _extra(record, _CONTAINER_KEYS)
            if node is None:
                state = "no_node"
            elif isinstance(node, dict):
                state = "present"
                for field, column in (
                    ("birthtime", "birthtime"),
                    ("ctime", "ctime"),
                    ("mtime", "mtime"),
                    ("lastSeen", "last_seen"),
                ):
                    stamp, why = parse_timestamp(node.get(field))
                    row[column] = stamp
                    if why:
                        notes.append(f"{field}: {why}")
                node_extra = _extra(node, _NODE_KEYS)
                if node_extra:
                    extra["node"] = node_extra
                missing = [name for name in sorted(_NODE_KEYS) if name not in node]
                if missing:
                    notes.append("node missing: " + ",".join(missing))
            else:
                state = "invalid"
                notes.append(f"node has unexpected type {type(node).__name__}")
            if "corrupt" in flags:
                state = "corrupt"
            elif "ignored" in flags:
                state = "ignored"
            row["state"] = state
            if row["birthtime"]:
                row["timestamp_utc"] = row["birthtime"]
                row["timestamp_desc"] = "container directory birth time"
            parent = parents.get(str(identifier)) if kind == "pluginData" else None
            if parent:
                row["parent_identifier"] = parent
            for key in sorted(_CONTAINER_KEYS):
                if key not in record:
                    notes.append(f"missing {key}")
            row["notes"] = "; ".join(notes)
            row["other"] = _other(extra)
            ctx.add(row)


def _codesign_rows(ctx: _Ctx, scope: str, data: dict[str, Any], tables: dict) -> None:
    cache = data.get("codesignCache")
    if cache is None:
        return
    if not isinstance(cache, dict):
        ctx.warn(f"{scope}: codesignCache has an unexpected shape")
        return
    entries = cache.get("orderedEntries")
    extra_cache = _extra(cache, {"orderedEntries"})
    if extra_cache:
        ctx.warn(f"{scope}: codesignCache has unknown keys: {', '.join(sorted(map(str, extra_cache)))[:200]}")
    if not isinstance(entries, list):
        if entries is not None:
            ctx.warn(f"{scope}: codesignCache.orderedEntries is not a list")
        return
    persona = "" if scope == "system" else scope.split(":", 1)[-1]
    for position, entry in enumerate(entries):
        row = _blank("codesign", scope)
        row["row_index"] = position
        notes: list[str] = []
        if not isinstance(entry, dict):
            row.update(state="invalid", other=_other({"value": entry}), notes="entry is not an object")
            ctx.add(row)
            continue
        class_id = _number(entry.get("containerClass"), notes, "containerClass")
        row.update(
            identifier=_text(entry.get("identifier")),
            class_id=class_id,
            persona=persona,
            class_label=_label_for(class_id, persona, tables) if class_id != "" else "",
        )
        row["flags"] = ",".join(name for name in _CODESIGN_FLAGS if entry.get(name) is True)
        row["state"] = (
            "invalid"
            if entry.get("invalid") is True
            else "placeholder"
            if entry.get("placeholder") is True
            else ""
        )
        entitlements = entry.get("entitlements")
        if isinstance(entitlements, dict):
            notes.append(f"entitlements={len(entitlements)}")
        elif entitlements is not None:
            notes.append("entitlements: unexpected type")
        if "identifier" not in entry:
            notes.append("missing identifier")
        row["notes"] = "; ".join(notes)
        row["other"] = _other(_extra(entry, _CODESIGN_KEYS))
        ctx.add(row)


def _child_parent_rows(ctx: _Ctx, scope: str, data: dict[str, Any]) -> None:
    mapping = data.get("childParentMap")
    if mapping is None:
        return
    if not isinstance(mapping, dict):
        ctx.warn(f"{scope}: childParentMap has an unexpected shape")
        return
    for position, (child, parent) in enumerate(mapping.items()):
        row = _blank("child_parent", scope)
        row.update(identifier=str(child), parent_identifier=_text(parent), row_index=position, state="mapped")
        if not isinstance(parent, str):
            row["notes"] = "parent is not a string"
            row["other"] = _other({"value": parent})
        ctx.add(row)


def _client_rows(ctx: _Ctx, scope: str, data: dict[str, Any]) -> None:
    cache = data.get("clientCache")
    if cache is None:
        return
    if not isinstance(cache, dict):
        ctx.warn(f"{scope}: clientCache has an unexpected shape")
        return
    entries = cache.get("mru")
    if entries is not None and not isinstance(entries, list):
        ctx.warn(f"{scope}: clientCache.mru is not a list")
        return
    for position, entry in enumerate(entries or []):
        row = _blank("client", scope)
        row["row_index"] = position
        notes: list[str] = []
        if not isinstance(entry, dict):
            row.update(state="invalid", other=_other({"value": entry}), notes="entry is not an object")
            ctx.add(row)
            continue
        user = entry.get("user") if isinstance(entry.get("user"), dict) else {}
        row.update(
            identifier=_text(entry.get("identifier")),
            path=_text(entry.get("sandboxContainer")),
            persona=_text(entry.get("persona")),
            owner=_text(user.get("name")),
            state="client",
            generation=_number(entry.get("pid"), notes, "pid"),
            flags=",".join(name for name in _CLIENT_FLAGS if entry.get(name) is True),
        )
        platform = _number(entry.get("platform"), notes, "platform")
        if platform != "":
            notes.append(f"platform={platform}")
        entitlements = entry.get("entitlements")
        if isinstance(entitlements, dict):
            notes.append(f"entitlements={len(entitlements)}")
        row["notes"] = "; ".join(notes)
        row["other"] = _other(_extra(entry, _CLIENT_KEYS))
        ctx.add(row)


def _class_path_rows(ctx: _Ctx, scope: str, tables: dict) -> None:
    position = 0
    for table, personas in tables.items():
        for persona, classes in personas.items():
            for class_id, entry in classes.items():
                row = _blank("class_path", scope)
                notes: list[str] = []
                cid = _number(class_id, notes, "class id")
                class_dir = _text(entry.get("class"))
                row.update(
                    container_class=table,
                    class_id=cid,
                    persona=persona,
                    path=class_dir,
                    class_label=_label_for(cid, persona, tables)
                    if table == "MCMContainerClassPath"
                    else class_dir.rsplit("/", 1)[-1],
                    identifier=class_dir.rsplit("/", 1)[-1],
                    owner=_text(entry.get("classOwner")),
                    state="exists"
                    if entry.get("exists") is True
                    else "missing"
                    if entry.get("exists") is False
                    else "unknown",
                    row_index=position,
                    notes="; ".join(notes),
                    other=_other(_extra(entry, _CLASS_PATH_KEYS)),
                )
                ctx.add(row)
                position += 1


def _persona_rows(ctx: _Ctx, scope: str, data: dict[str, Any]) -> None:
    personas = data.get("personas")
    if personas is None:
        return
    if not isinstance(personas, dict):
        ctx.warn(f"{scope}: personas has an unexpected shape")
        return
    position = 0
    managed = 0
    for table, value in personas.items():
        identities: list[tuple[str, Any]] = []
        if table in ("identityForPersonal", "identityForUnspecific"):
            identities.append((str(table), value))
        elif table in ("personaIDToIdentityMap", "personaToIdentityMap"):
            if isinstance(value, dict):
                identities.extend((f"{table}", item) for item in value.values())
            elif value is not None:
                ctx.warn(f"{scope}: {table} has an unexpected shape")
        elif table == "identityToManagedPathMap":
            if not isinstance(value, dict):
                if value is not None:
                    ctx.warn(f"{scope}: {table} has an unexpected shape")
                continue
            for key, item in value.items():
                paths = item.get("paths") if isinstance(item, dict) else None
                if paths is not None and not isinstance(paths, list):
                    ctx.warn(f"{scope}: managed paths entry is not a list")
                daemon = (
                    item.get("daemonUser")
                    if isinstance(item, dict) and isinstance(item.get("daemonUser"), dict)
                    else {}
                )
                for path in paths if isinstance(paths, list) else []:
                    row = _blank("managed_path", scope)
                    row.update(
                        container_class=table,
                        persona=str(key),
                        path=_text(path),
                        owner=_text(daemon.get("name")),
                        state="managed",
                        row_index=managed,
                    )
                    ctx.add(row)
                    managed += 1
            continue
        else:
            row = _blank("unknown_section", scope)
            row.update(
                container_class="personas",
                identifier=str(table),
                state="unknown",
                row_index=position,
                notes="unknown personas table",
                other=_other({"value": value}),
            )
            ctx.add(row)
            position += 1
            continue
        for source, item in identities:
            row = _blank("persona", scope)
            row.update(container_class=source, row_index=position)
            position += 1
            if not isinstance(item, dict):
                row.update(state="invalid", notes="identity is not an object", other=_other({"value": item}))
                ctx.add(row)
                continue
            notes: list[str] = []
            posix = item.get("posixUser") if isinstance(item.get("posixUser"), dict) else {}
            row.update(
                identifier=_text(item.get("identifier")),
                path=_text(item.get("homeDirectory")),
                uuid=_text(item.get("personaUniqueString")),
                state=_text(item.get("personaType")),
                owner=_text(posix.get("name")),
                generation=_number(item.get("kernelPersonaID"), notes, "kernelPersonaID"),
                schema_version=_number(item.get("kernelPersonaType"), notes, "kernelPersonaType"),
                persona=_text(item.get("identifier")),
                notes="; ".join(notes),
                other=_other(_extra(item, _PERSONA_KEYS)),
            )
            ctx.add(row)


def parse_state(obj: Any, *, source_file: str = "", warn: Warn | None = None) -> list[dict[str, Any]]:
    """Parsed JSON -> rows. Never raises on bad input; returns [] for non-object roots."""
    ctx = _Ctx(source_file, warn)
    if not isinstance(obj, dict):
        ctx.warn(f"state root is {type(obj).__name__}, expected an object")
        return []
    if not obj:
        ctx.warn("state root is an empty object")
        return []
    for key, scope_data in obj.items():
        scope = _scope_name(str(key))
        if not isinstance(scope_data, dict):
            row = _blank("unknown_section", scope)
            row.update(
                identifier=str(key),
                state="unknown",
                notes="top-level value is not an object",
                other=_other({"value": scope_data}),
            )
            ctx.add(row)
            ctx.warn(f"top-level key has an unexpected shape ({type(scope_data).__name__})")
            continue
        unknown = [str(name) for name in scope_data if name not in _SCOPE_KEYS]
        if unknown:
            ctx.warn(f"{scope}: unknown sections kept: {', '.join(sorted(unknown))[:200]}")
            for name in unknown:
                row = _blank("unknown_section", scope)
                row.update(
                    identifier=name,
                    state="unknown",
                    notes="section not known to this parser",
                    other=_other({"value": scope_data[name]}),
                )
                ctx.add(row)
        tables = _class_tables(scope_data)
        mapping = scope_data.get("childParentMap")
        parents = {str(k): v for k, v in mapping.items() if isinstance(v, str)} if isinstance(mapping, dict) else {}
        _container_rows(ctx, scope, scope_data, tables, parents)
        _codesign_rows(ctx, scope, scope_data, tables)
        _child_parent_rows(ctx, scope, scope_data)
        _client_rows(ctx, scope, scope_data)
        _class_path_rows(ctx, scope, tables)
        _persona_rows(ctx, scope, scope_data)
    return ctx.rows


def parse_state_bytes(data: Any, *, source_file: str = "", warn: Warn | None = None) -> list[dict[str, Any]]:
    """Raw bytes/str (or parsed JSON) -> rows. Empty, truncated or non-JSON input gives []."""
    obj = load_json(data, warn)
    if obj is None:
        return []
    return parse_state(obj, source_file=source_file, warn=warn)


def count_by_type(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["record_type"]] = counts.get(row["record_type"], 0) + 1
    return counts


def expected_counts(obj: Any) -> dict[str, int]:
    """Independent count of the records present in a parsed state object (used to cross-check the rows)."""
    counts = dict.fromkeys(RECORD_TYPES, 0)
    if not isinstance(obj, dict):
        return counts
    for scope_data in obj.values():
        if not isinstance(scope_data, dict):
            counts["unknown_section"] += 1
            continue
        counts["unknown_section"] += sum(1 for name in scope_data if name not in _SCOPE_KEYS)
        containers = scope_data.get("containers")
        if isinstance(containers, dict):
            counts["container"] += sum(len(m) for m in containers.values() if isinstance(m, dict))
        cache = scope_data.get("codesignCache")
        if isinstance(cache, dict) and isinstance(cache.get("orderedEntries"), list):
            counts["codesign"] += len(cache["orderedEntries"])
        if isinstance(scope_data.get("childParentMap"), dict):
            counts["child_parent"] += len(scope_data["childParentMap"])
        client = scope_data.get("clientCache")
        if isinstance(client, dict) and isinstance(client.get("mru"), list):
            counts["client"] += len(client["mru"])
        tables = scope_data.get("containerClassPaths")
        if isinstance(tables, dict):
            for personas in tables.values():
                if isinstance(personas, dict):
                    for classes in personas.values():
                        if isinstance(classes, dict):
                            counts["class_path"] += sum(1 for e in classes.values() if isinstance(e, dict))
        personas = scope_data.get("personas")
        if isinstance(personas, dict):
            for table, value in personas.items():
                if table in ("identityForPersonal", "identityForUnspecific"):
                    counts["persona"] += 1
                elif table in ("personaIDToIdentityMap", "personaToIdentityMap") and isinstance(value, dict):
                    counts["persona"] += len(value)
                elif table == "identityToManagedPathMap" and isinstance(value, dict):
                    counts["managed_path"] += sum(
                        len(i["paths"])
                        for i in value.values()
                        if isinstance(i, dict) and isinstance(i.get("paths"), list)
                    )
                elif table not in ("personaIDToIdentityMap", "personaToIdentityMap", "identityToManagedPathMap"):
                    counts["unknown_section"] += 1
    return counts

# ---------------------------------------------------------------------------------------------
# iLEAPP adapters. Everything above this line is the reader for the file.
# ---------------------------------------------------------------------------------------------
import re as _re

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_STATE_PATH = _re.compile(r'(?:^|[/\\])ContainerManager[/\\]state\.json$')
_STATE_NAME = _re.compile(r'state\.json$')
_ENTITLEMENTS = _re.compile(r'entitlements=(\d+)')
_SCOPE_LABEL = {'system': '<system>'}


def _when(text):
    '''ISO text from the shared reader -> aware UTC datetime, or None.'''
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00'))
    except ValueError:
        return None


def _scope(scope):
    return _SCOPE_LABEL.get(scope, scope.split(':', 1)[-1])


def _rows(context):
    '''Yield (rows, relative source) for every ContainerManager/state.json found, standalone or in a sysdiagnose.'''
    for stream, source in get_sysdiagnose_files(context.get_files_found(), _STATE_NAME, text_mode=False):
        if not _STATE_PATH.search(source):
            continue
        rows = parse_state_bytes(stream.read(), source_file=source, warn=logfunc)
        yield rows, source


def _collect(context, keep, build):
    data_list, sources = [], []
    for rows, source in _rows(context):
        sources.append(source)
        relative = context.get_relative_path(source)
        for row in rows:
            if keep(row):
                data_list.append(build(row) + (relative,))
    return data_list, '\n'.join(sorted(set(sources)))


def _has_directory(row):
    return row['record_type'] == 'container' and row['state'] != 'no_node'


@artifact_processor
def containerManagerState(context):
    ''' See artifact description '''
    data_headers = (
        ('Directory birthtime (UTC)', 'datetime'), ('Directory ctime (UTC)', 'datetime'),
        ('Directory mtime (UTC)', 'datetime'), ('lastSeen (UTC)', 'datetime'), 'Container Class', 'Identifier',
        'Host App', 'State', 'Path', 'Directory Name', 'Container UUID', 'Generation',
        'Owner (as stored)', 'Scope (as stored)', 'Notes', 'Source File')

    def build(row):
        return (_when(row['birthtime']), _when(row['ctime']), _when(row['mtime']), _when(row['last_seen']),
                row['class_label'] or row['container_class'], row['identifier'], row['parent_identifier'],
                row['state'], row['path'], row['path_identifier'], row['uuid'], row['generation'],
                row['owner'], _scope(row['scope']), row['notes'])

    data_list, source = _collect(context, _has_directory, build)
    return data_headers, data_list, source


@artifact_processor
def containerManagerStateNoDirectory(context):
    ''' See artifact description '''
    data_headers = (
        'Container Class', 'Identifier', 'Host App', 'Directory Name', 'Container UUID', 'Generation',
        'Owner (as stored)', 'Scope (as stored)', 'Notes', 'Source File')

    def build(row):
        return (row['class_label'] or row['container_class'], row['identifier'], row['parent_identifier'],
                row['path_identifier'], row['uuid'], row['generation'], row['owner'], _scope(row['scope']),
                row['notes'])

    data_list, source = _collect(
        context, lambda row: row['record_type'] == 'container' and row['state'] == 'no_node', build)
    return data_headers, data_list, source


@artifact_processor
def containerManagerStateRegistrations(context):
    ''' See artifact description '''
    data_headers = (
        'Identifier', 'Container Class', 'State', 'Flags', 'Entitlement Keys', 'Position in Cache', 'Scope (as stored)',
        'Notes', 'Source File')

    def build(row):
        match = _ENTITLEMENTS.search(row['notes'])
        notes = '; '.join(part for part in row['notes'].split('; ') if part and not _ENTITLEMENTS.match(part))
        return (row['identifier'], row['class_label'] or row['class_id'], row['state'], row['flags'],
                int(match.group(1)) if match else None, row['row_index'], _scope(row['scope']), notes)

    data_list, source = _collect(context, lambda row: row['record_type'] == 'codesign', build)
    return data_headers, data_list, source
