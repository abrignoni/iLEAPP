#!/usr/bin/env python3
"""Build a SYNTHETIC ContainerManager ``state.json`` fixture (fabricated names, paths and UUIDs).

The structure mirrors the iOS 27 file (scopes, container groups, caches, class paths, personas) so the
parser can be tested without any real casework data. Every identifier is ``com.example.*`` or
``group.example.*`` and every UUID is derived from a fixed namespace, so the output is reproducible.

    python make_synthetic_state.py [output.json]      # default: print nothing, write the fixture

``build_state()`` returns the clean structure; ``edge_cases()`` returns {name: bytes} of damaged or
unusual inputs (empty file, truncated JSON, bad timestamps, huge numbers, missing/unknown keys).
"""

from __future__ import annotations

import copy
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone

_UTC = timezone(timedelta(0), "UTC")
_NS = uuid.UUID("12345678-1234-5678-1234-567812345678")
_BASE = datetime(2026, 3, 1, 12, 0, 0, tzinfo=_UTC)
_SNAPSHOT = datetime(2026, 9, 29, 19, 0, 0, tzinfo=_UTC)

FIXTURE_NAME = "state.synthetic.json"


def _uid(label: str) -> str:
    return str(uuid.uuid5(_NS, label)).upper()


def _ts(offset_minutes: int) -> str:
    return (_BASE + timedelta(minutes=offset_minutes)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _node(index: int, *, touched: bool = False) -> dict:
    born = index * 977
    return {
        "birthtime": _ts(born),
        "ctime": _ts(born + (5 if touched else 0)),
        "lastSeen": _SNAPSHOT.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "mtime": _ts(born + (3 if touched else 0)),
    }


def _group(
    prefix: str,
    count: int,
    owner: str,
    schema: int,
    *,
    generation: int = 1000,
    null_every: int = 7,
    base_index: int = 0,
) -> dict:
    out = {}
    for i in range(count):
        name = f"{prefix}.synth{i:03d}"
        gone = null_every and i % null_every == 3
        out[name] = {
            "corrupt": False,
            "generation": -1 if gone else generation + (i % 2),
            "ignore": False,
            "node": None if gone else _node(base_index + i, touched=i % 3 == 0),
            "pathIdentifier": _uid(f"path:{prefix}:{i}"),
            "posixOwnership": owner,
            "schemaVersion": schema,
            "uuid": _uid(f"uuid:{prefix}:{i}"),
        }
    return out


def _class_entry(base: str, category: str, leaf: str, owner: str, persona: str, exists: bool = True) -> dict:
    return {
        "base": base,
        "caseSensitive": True,
        "caseSensitiveDetermined": True,
        "category": f"{base}/{category}",
        "categoryOwner": owner,
        "class": f"{base}/{category}/{leaf}",
        "classOwner": owner,
        "exists": exists,
        "persona": persona,
        "supportsDP": False,
        "supportsDPDetermined": False,
    }


def _identity(persona_id: str, kind: str) -> dict:
    return {
        "homeDirectory": "/private/var/mobile",
        "identifier": persona_id,
        "kernelPersonaID": 1000,
        "kernelPersonaType": 5,
        "personaType": kind,
        "personaUniqueString": _uid("persona"),
        "posixUser": {
            "homeDirectory": "/private/var/mobile",
            "isRoleUser": False,
            "name": "mobile",
            "primaryGID": 501,
            "root": False,
            "uid": 501,
            "usableHomeDirectory": True,
        },
    }


def _client(i: int, container: str | None) -> dict:
    return {
        "entitlements": {"com.example.entitlement.a": True, "com.example.entitlement.b": ["x"]},
        "identifier": f"com.example.client{i:02d}",
        "isPlatformBinary": i % 2 == 0,
        "isSandboxed": i % 3 == 0,
        "isSignatureValid": True,
        "isSigned": True,
        "launchPersona": "501",
        "persona": "501",
        "pid": 100 + i,
        "platform": 2,
        "proximate": None,
        "sandboxContainer": container,
        "user": {
            "homeDirectory": "/private/var/mobile",
            "isRoleUser": False,
            "name": "mobile",
            "primaryGID": 501,
            "root": False,
            "uid": 501,
            "usableHomeDirectory": True,
        },
    }


def _sandbox(mobile: str, i: int) -> str:
    return f"{mobile}/Data/Application/{_uid(f'path:com.example.app:{i}')}"


def _codesign(identifiers: list[str], class_id: int) -> list[dict]:
    out = []
    for i, name in enumerate(identifiers):
        out.append(
            {
                "advanceCopy": False,
                "containerClass": class_id,
                "entitlements": {"application-identifier": f"EXAMPLE.{name}", "com.example.flag": i % 2 == 0},
                "identifier": name,
                "invalid": i % 25 == 24,
                "placeholder": i % 9 == 8,
                "registeredByCaller": class_id == 0,
                "registeredByKernel": False,
            }
        )
    return out


def build_state() -> dict:
    app_data = _group("com.example.app", 40, "{501:501:u+rwx,g+rx,o+rx}", 1, base_index=100)
    # some app data containers were re-created: generation 1001
    plugin_data = _group("com.example.app.ext", 80, "{501:501:u+rwx,g+rx,o+rx}", 1, generation=1007, base_index=300)
    plugin_children = list(plugin_data)
    parents = list(app_data)
    child_parent = {child: parents[i % len(parents)] for i, child in enumerate(plugin_children)}
    app_group = _group("group.example", 30, "{501:501:u+rwx,g+rx,o+rx}", 2, base_index=500)
    daemon = _group("com.example.daemon", 5, "{501:501:u+rwx,g+rx,o+rx}", 1, base_index=600)

    mobile = "/private/var/mobile/Containers"
    system_base = "/private/var/containers"
    user_scope = {
        "childParentMap": child_parent,
        "clientCache": {"mru": [_client(i, _sandbox(mobile, i) if i % 3 == 0 else None) for i in range(6)]},
        "codesignCache": {
            "orderedEntries": (
                _codesign(list(app_data), 2)
                + _codesign(plugin_children, 4)
                + _codesign(["group.example.synth000", "com.example.daemon.synth000"], 0)
            )
        },
        "containerClassPaths": {
            "MCMContainerClassPath": {
                "501": {
                    "2": _class_entry(mobile, "Data", "Application", "{501:501:u+rwx,g+rx,o+rx}", "501"),
                    "4": _class_entry(mobile, "Data", "PluginKitPlugin", "{501:501:u+rwx,g+rx,o+rx}", "501"),
                    "7": _class_entry(mobile, "Shared", "AppGroup", "{501:501:u+rwx,g+rx,o+rx}", "501"),
                    "10": _class_entry(mobile, "Data", "InternalDaemon", "{501:501:u+rwx,g+rx,o+rx}", "501"),
                    "14": _class_entry(
                        mobile, "Bundle", "Application", "{501:501:u+rwx,g+rx,o+rx}", "501", exists=False
                    ),
                }
            },
            "MCMContainerClassTransientPath": {
                "501": {
                    "14": _class_entry(
                        mobile, "Temp", "Bundle/Application", "{501:501:u+rwx,g+rx,o+rx}", "501", exists=False
                    ),
                }
            },
        },
        "containers": {
            "appData-501": app_data,
            "appGroup-501": app_group,
            "daemon-501": daemon,
            "perUserApp-501": {},
            "perUserApp-501-T": {},
            "pluginData-501": plugin_data,
        },
        "personas": {
            "identityForPersonal": _identity("501", "personal"),
            "identityForUnspecific": _identity("501", "unspecific"),
            "identityToManagedPathMap": {
                "501": {
                    "daemonUser": {
                        "homeDirectory": "/private/var/root",
                        "isRoleUser": True,
                        "name": "root",
                        "primaryGID": 0,
                        "root": True,
                        "uid": 0,
                        "usableHomeDirectory": True,
                    },
                    "paths": ["/private/var/root", "/private/var/root/Library/Example/Pending"],
                }
            },
            "personaIDToIdentityMap": {"0": _identity("501", "unspecific"), "1": _identity("501", "personal")},
            "personaToIdentityMap": {_uid("persona"): _identity("501", "personal")},
        },
    }
    system_scope = {
        "clientCache": {"mru": [_client(50 + i, None) for i in range(4)]},
        "containerClassPaths": {
            "MCMContainerClassPath": {
                "0": {
                    "12": _class_entry(system_base, "Data", "System", "{0:0:u+rwx,g+rx,o+rx}", "0"),
                    "13": _class_entry(system_base, "Shared", "SystemGroup", "{0:0:u+rwx,g+rx,o+rx}", "0"),
                    "15": _class_entry(system_base, "Data", "ProtectedSystem", "{0:0:u+rwx,g+rx,o+rx}", "0"),
                },
                "33": {"1": _class_entry(system_base, "Bundle", "Application", "{33:33:u+rwx,g+rx,o+rx}", "33")},
            },
            "MCMContainerClassStagingPath": {
                "33": {
                    "1": {
                        **_class_entry(system_base, "Bundle", "Application", "{33:33:u+rwx,g+rx,o+rx}", "33"),
                        "class": "Library/Caches/example/Staging",
                    }
                }
            },
        },
        "containers": {
            "app-33": _group("com.example.system", 30, "{33:33:u+rwx,g+rx,o+rx}", 0, base_index=10),
            "app-33-T": {},
            "protectedSystem-0": _group("com.example.protected", 2, "{0:0:u+rwx}", 1, null_every=0, base_index=40),
            "systemData-0": _group("com.example.sysdata", 6, "{0:0:u+rwx,g+rx,o+rx}", 1, base_index=50),
            "systemGroup-0": _group("systemgroup.example", 8, "{0:0:u+rwx,g+rx,o+rx}", 2, base_index=60),
        },
        "personas": {
            "identityForPersonal": _identity("501", "unspecific"),
            "identityForUnspecific": _identity("501", "unspecific"),
            "identityToManagedPathMap": {
                "0": {
                    "daemonUser": {
                        "homeDirectory": "/private/var/root",
                        "isRoleUser": True,
                        "name": "root",
                        "primaryGID": 0,
                        "root": True,
                        "uid": 0,
                        "usableHomeDirectory": True,
                    },
                    "paths": ["/private/var/root/Containers"],
                }
            },
            "personaIDToIdentityMap": {},
            "personaToIdentityMap": {},
        },
    }
    return {"<system>": system_scope, "501": user_scope}


def to_bytes(state: dict) -> bytes:
    return json.dumps(state, sort_keys=True, indent=1).encode("utf-8")


def edge_cases() -> dict[str, bytes]:
    """Damaged or unusual inputs. Values are bytes so the loader is exercised too."""
    out: dict[str, bytes] = {}
    clean = build_state()
    full = to_bytes(clean)
    out["empty_file"] = b""
    out["whitespace_only"] = b"  \n\t "
    out["empty_object"] = b"{}"
    out["root_is_list"] = b"[1, 2, 3]"
    out["root_is_scalar"] = b"42"
    out["truncated_json"] = full[: len(full) // 2]
    out["not_json"] = b"\x00\x01 this is not json"
    out["bom_prefixed"] = b"\xef\xbb\xbf" + full
    out["invalid_utf8_tail"] = full[:-2] + b"\xff\xfe}"

    def variant(edit) -> bytes:
        data = copy.deepcopy(clean)
        edit(data)
        return json.dumps(data, sort_keys=True).encode("utf-8")

    def first(data: dict, group: str = "appData-501") -> tuple[str, dict]:
        members = data["501"]["containers"][group]
        name = next(iter(members))
        return name, members[name]

    def bad_timestamps(data: dict) -> None:
        members = list(data["501"]["containers"]["appData-501"].values())
        members[0]["node"] = {"birthtime": "not a time", "ctime": 1.0e30, "lastSeen": -5, "mtime": True}
        members[1]["node"] = {
            "birthtime": "3999-01-01T00:00:00.000Z",
            "ctime": 1788000000,
            "lastSeen": 1788000000000,
            "mtime": "2026-03-01T12:00:00",
        }
        members[2]["node"] = {"birthtime": "2026-03-01T14:00:00.000+02:00", "ctime": [], "lastSeen": {}, "mtime": ""}

    def huge_numbers(data: dict) -> None:
        _, record = first(data)
        record["generation"] = 10**30
        record["schemaVersion"] = "12"
        data["501"]["clientCache"]["mru"][0]["pid"] = 1.5e300

    def missing_fields(data: dict) -> None:
        members = list(data["501"]["containers"]["appData-501"].values())
        del members[0]["uuid"]
        del members[1]["pathIdentifier"]
        del members[2]["node"]
        members[3]["node"] = {"birthtime": _ts(5)}
        del data["501"]["codesignCache"]["orderedEntries"][0]["identifier"]
        del data["501"]["clientCache"]["mru"][0]["user"]

    def unknown_keys(data: dict) -> None:
        _, record = first(data)
        record["futureField"] = {"a": 1}
        record["node"]["futureNodeField"] = "x"
        data["501"]["codesignCache"]["orderedEntries"][0]["futureFlag"] = True
        data["501"]["futureSection"] = {"k": [1, 2, 3]}
        data["501"]["containers"]["futureKind-501"] = {
            "com.example.new.synth": {"uuid": _uid("n"), "pathIdentifier": _uid("m"), "node": None, "generation": 1}
        }
        data["777"] = {"containers": {}}

    def wrong_types(data: dict) -> None:
        data["501"]["containers"]["appData-501"]["com.example.badrecord"] = "not an object"
        _, record = first(data)
        record["node"] = "oops"
        data["501"]["containers"]["appGroup-501"] = [1, 2]
        data["501"]["childParentMap"]["com.example.child.bad"] = 5
        data["501"]["codesignCache"]["orderedEntries"].append("junk")
        data["501"]["clientCache"]["mru"].append(None)
        data["501"]["containerClassPaths"]["MCMContainerClassPath"]["501"]["99"] = "junk"
        data["501"]["personas"]["identityForPersonal"] = []
        data["501"]["personas"]["identityToManagedPathMap"]["501"]["paths"] = "single string"
        data["501"]["personas"]["personaToIdentityMap"] = 3
        data["<system>"] = ["not", "an", "object"]

    def flags_and_dupes(data: dict) -> None:
        members = list(data["501"]["containers"]["appData-501"].values())
        members[0]["corrupt"] = True
        members[1]["ignore"] = True
        members[2]["corrupt"] = "yes"

    out["bad_timestamps"] = variant(bad_timestamps)
    out["huge_numbers"] = variant(huge_numbers)
    out["missing_fields"] = variant(missing_fields)
    out["unknown_keys"] = variant(unknown_keys)
    out["wrong_types"] = variant(wrong_types)
    out["flags"] = variant(flags_and_dupes)
    out["json_infinity_literal"] = full.replace(b'"pid": 100', b'"pid": Infinity', 1)
    return out


def main(argv: list[str]) -> int:
    target = argv[1] if len(argv) > 1 else FIXTURE_NAME
    with open(target, "wb") as handle:
        handle.write(to_bytes(build_state()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
