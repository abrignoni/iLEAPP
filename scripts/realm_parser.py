# ---------------------------------------------------------------------------
# Vendored into iLEAPP from crush-forensics (github.com/kalink0/crush-forensics)
# by Marco Neumann (kalink0), Apache-2.0, unchanged except:
#   * the two crush framework imports below are replaced with minimal local
#     shims so the module is self-contained (iLEAPP has no crush.core.vfs /
#     crush.parsers.base); the RealmParser class is kept verbatim but iLEAPP
#     calls the module-level parse_realm_file() helper appended at the end
#     instead, which reads a plain file path and returns decoded tables.
# The upstream author's copyright and SPDX header above are preserved.
#
# This is vendored third-party code kept faithful to upstream, so it is not
# held to iLEAPP's own lint rules; the file-level disable below silences the
# warnings its upstream style and pylint's type inference raise (broad excepts
# and deliberately-unused signature args in the on-disk decoders, plus a few
# not-an-iterable / no-member / import-error false positives). Do not add a
# blanket disable like this to iLEAPP's own artifact code.
# pylint: disable=unused-argument,broad-exception-caught,not-an-iterable,no-member,import-error
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 - now Marco Neumann (kalink0)
"""Realm database parser — header + array structure decoding.

Column value decoding is dispatched deterministically from each column's
declared type/nullable/collection flags, read directly off its ColKey
(spec child[5], the colkeys array) — not inferred by trying multiple
candidate shapes and seeing which one "looks right". The on-disk formats
implemented here (Cluster/ClusterTree, ArrayIntNull, ArrayBool[Null],
ArrayString/ArrayBinary in all three sub-formats, ArrayTimestamp,
ArrayFixedBytes, ArrayDecimal128, ArrayKey, BasicArray<float/double>) are
taken from the Realm Core C++ source (github.com/realm/realm-core,
Apache-2.0): spec.hpp, keys.hpp, column_type.hpp, cluster.hpp/.cpp,
cluster_tree.cpp, array_integer.hpp, array_bool.hpp, array_string*.hpp,
array_blobs_*.hpp, array_timestamp.hpp/.cpp, array_fixed_bytes.hpp,
array_decimal128.hpp, array_key.hpp, array_basic*.hpp,
column_type_traits.hpp, bplustree.hpp/.cpp, collection_parent.hpp,
list.hpp, lnklst.hpp, array_typed_link.hpp, array_mixed.hpp/.cpp,
data_type.hpp, dictionary.hpp/.cpp. File-relative citations are in each
function's docstring.

List and Set columns (including LinkList — Realm's on-disk type code 13,
a pre-Collections marker that predates the modern ColumnType enum but
still appears in real colkeys) are decoded by walking each row's own
BPlusTree<T> (a differently-laid-out inner node than ClusterNodeInner —
see _walk_bplustree_leaves) and reusing the same per-type leaf decoders
as regular columns.

Mixed and TypedLink are decoded too (_read_array_mixed,
_read_array_typed_link), including as a List/Set element type. A Mixed
value that itself holds a nested List/Set/Dictionary is also expanded,
not shown as a placeholder (array_mixed.hpp's m_refs slot, DataType
type_List=19/type_Set=20/type_Dictionary=21 — see _read_array_mixed,
_read_collection_at_ref, _read_dictionary_at_ref), recursing back into
this same dispatch with a depth cap (_MIXED_MAX_NEST_DEPTH) against a
corrupt/malicious reference chain. Only a data_type this dispatch
genuinely doesn't recognise (e.g. Geospatial, which turns out to have no
case in array_mixed.cpp's store() at all) falls through to a clearly
labelled "<mixed: unsupported type_N>" marker — never silently.

Dictionary<K,Mixed> columns (_read_dictionary_column) are decoded too: a
per-row 2-slot "dictionary top" array whose slot 0/1 are BPlusTree roots
for keys and values respectively, paired by identical index position
(dictionary.cpp); the key's declared type is read from the spec's
m_types array rather than the colkey (spec.hpp/.cpp
get_dictionary_key_type — see _extract_column_info) for a top-level
Dictionary column, or hardcoded to String for a Dictionary nested inside
a Mixed value (dictionary.cpp's ref-only constructor initializes
`m_key_type(type_String)` unconditionally — there is no Spec column to
consult in that case).

None of the above has a confirming real-world sample in this project's
test data (only hand-built synthetic fixtures matching the on-disk
format spec) — everything is dispatched from the declared type either
way, never guessed from shape, but "spec-derived" and "cross-checked
against a real Realm-produced file" are different claims. Where a
detail could not be pinned down by the C++ source itself, the exact gap
is documented at the point it was needed (e.g. _decode_bid's caveat
about its own BID-decode arithmetic, not about Realm's file layout).
"""
from __future__ import annotations

import decimal
import math
import re
import struct
import uuid as _uuid_mod
from datetime import datetime, timedelta, timezone
from typing import Any

# --- iLEAPP vendoring shims (replaces: from crush.core.vfs import VFS, VFSNode
#                                       from crush.parsers.base import AbstractParser, ParseResult) ---
class VFS:  # pragma: no cover - shim, real reads go through parse_realm_file()
    pass


class VFSNode:  # pragma: no cover
    pass


class AbstractParser:  # pragma: no cover
    pass


class ParseResult:  # pragma: no cover
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
# --- end iLEAPP vendoring shims ---

_HEADER_SIZE = 24
_MNEMONIC = b"T-DB"

# width_ndx (bits [2:0] of array flags byte) → element width value
# Scheme 0: width is in bits.  Scheme 1: width is in bytes.
_WIDTH_TABLE = [0, 1, 2, 4, 8, 16, 32, 64]

# Realm ColumnType codes stored in the low 6 bits of each ColKey (keys.hpp
# ColKey::get_type, column_type.hpp ColumnType::Type).
_REALM_COL_TYPES: dict[int, str] = {
    0: "int",
    1: "bool",
    2: "string",
    4: "data",
    6: "mixed",
    8: "date",
    9: "float",
    10: "double",
    11: "decimal128",
    12: "link",
    13: "linklist",
    14: "backlink",
    15: "objectId",
    16: "typedlink",
    17: "uuid",
}

# Column types that are hidden (no user-visible name) and must be skipped.
# BackLink columns exist only as the reverse side of a Link and are not
# part of Table's public column set (mirrors Spec::get_public_column_count).
_HIDDEN_COL_TYPES: frozenset[int] = frozenset({14})  # BackLink

# ColumnAttr bits packed into ColKey bits [22:30) (column_type.hpp).
_COL_ATTR_NULLABLE = 0x10
_COL_ATTR_LIST = 0x20
_COL_ATTR_DICTIONARY = 0x40
_COL_ATTR_SET = 0x80


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _read_at(vfs: VFS, node: VFSNode, offset: int, size: int) -> bytes:
    if offset < 0:
        return b""
    try:
        with vfs.open(node) as src:
            try:
                src.seek(offset)
                return src.read(size)
            except Exception:
                data = src.read()
        return data[offset : offset + size]
    except Exception:
        return b""


# ---------------------------------------------------------------------------
# File header (24 bytes)
# ---------------------------------------------------------------------------

def _parse_realm_header(data: bytes) -> dict[str, Any] | None:
    if len(data) < _HEADER_SIZE:
        return None

    mnemonic = data[16:20]
    if mnemonic != _MNEMONIC:
        return None

    top_ref0 = int.from_bytes(data[0:8], "little")
    top_ref1 = int.from_bytes(data[8:16], "little")
    fmt0 = data[20]
    fmt1 = data[21]
    reserved = data[22]
    flags = data[23]
    active = 1 if (flags & 0x01) else 0

    return {
        "Top reference 0": f"{top_ref0} (0x{top_ref0:x})",
        "Top reference 1": f"{top_ref1} (0x{top_ref1:x})",
        "Mnemonic": mnemonic.decode("ascii", errors="replace"),
        "File format (top ref 0)": fmt0,
        "File format (top ref 1)": fmt1,
        "Reserved": reserved,
        "Flags": f"0x{flags:02x}",
        "Active top reference": active,
    }


# ---------------------------------------------------------------------------
# Array header (8 bytes)
# ---------------------------------------------------------------------------

def _parse_array_header(data: bytes, offset: int = 0) -> dict[str, Any] | None:
    """Parse a Realm 8-byte array header at *offset* inside *data*.

    Array header layout:
        [0:4]  checksum   — always 0x41414141 ("AAAA")
        [4]    flags      — 5 bit-groups (see below)
        [5:8]  size       — big-endian uint24: number of elements in payload

    Flags byte (MSB = bit 7):
        bit 7       is_inner_bptree_node
        bit 6       has_refs  (1 = Reference Array; payload = file offsets)
        bit 5       context_flag  (purpose unclear)
        bits [4:3]  width_scheme  (0=bits, 1=bytes, 2=size-only)
        bits [2:0]  width_ndx  → _WIDTH_TABLE lookup

    Payload size formulas (before 8-byte alignment):
        scheme 0:  ceil(width_bits * size / 8)
        scheme 1:  width_bytes * size
        scheme 2:  size
    """
    if offset < 0 or len(data) < offset + 8:
        return None
    chunk = data[offset : offset + 8]
    if chunk[0:4] != b"\x41\x41\x41\x41":
        return None

    flags = chunk[4]
    size = int.from_bytes(chunk[5:8], "big")

    is_inner = bool((flags >> 7) & 1)
    has_refs = bool((flags >> 6) & 1)
    context_flag = bool((flags >> 5) & 1)
    width_scheme = (flags >> 3) & 3
    width_ndx = flags & 7
    width = _WIDTH_TABLE[width_ndx]

    if width_scheme == 0:
        payload_bytes = (width * size + 7) // 8 if width > 0 else 0
    elif width_scheme == 1:
        payload_bytes = width * size
    else:
        payload_bytes = size

    payload_bytes_aligned = (payload_bytes + 7) & ~7

    return {
        "Checksum": "AAAA (0x41414141)",
        "Flags (raw)": f"0x{flags:02x} (0b{flags:08b})",
        "is_inner_bptree_node": is_inner,
        "has_refs": has_refs,
        "context_flag": context_flag,
        "width_scheme": width_scheme,
        "width_ndx": width_ndx,
        "width": width,
        "Element count (size)": size,
        "Payload bytes (raw)": payload_bytes,
        "Payload bytes (aligned)": payload_bytes_aligned,
        "Total array bytes": 8 + payload_bytes_aligned,
    }


def _elem_bytes(arr_hdr: dict[str, Any]) -> int:
    """Return element size in bytes for an already-decoded array header."""
    scheme = arr_hdr["width_scheme"]
    width = arr_hdr["width"]
    if scheme == 0:
        return width // 8 if width >= 8 else 0
    if scheme == 1:
        return int(width)
    return 0  # scheme 2: variable / size-only


def _read_ref(data: bytes, payload_start: int, index: int, elem_bytes: int) -> int:
    """Read one little-endian integer from an array payload at *index*."""
    off = payload_start + index * elem_bytes
    if elem_bytes < 1 or off + elem_bytes > len(data):
        return -1
    return int.from_bytes(data[off : off + elem_bytes], "little")


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def _read_uint_array(data: bytes, offset: int) -> list[int]:
    """Read all unsigned integer values from a Realm integer array at *offset*."""
    hdr = _parse_array_header(data, offset)
    if not hdr:
        return []
    count = hdr["Element count (size)"]
    width = hdr["width"]
    scheme = hdr["width_scheme"]
    if count == 0 or width == 0:
        return []
    payload = data[offset + 8:]
    vals: list[int] = []
    if scheme == 0:
        # bit-packed
        for i in range(count):
            bit_off = i * width
            byte_off = bit_off // 8
            eb = (width + 7) // 8
            if byte_off + eb > len(payload):
                break
            v = int.from_bytes(payload[byte_off : byte_off + eb], "little")
            mask = (1 << width) - 1
            vals.append((v >> (bit_off % 8)) & mask)
    elif scheme == 1:
        eb = width
        for i in range(count):
            if (i + 1) * eb > len(payload):
                break
            vals.append(int.from_bytes(payload[i * eb : (i + 1) * eb], "little"))
    return vals


def _extract_free_list(
    data: bytes, root_offset: int, file_size: int
) -> list[dict[str, Any]]:
    """Extract the Realm free-space list from a root reference array.

    Realm's Group node stores three parallel arrays at child indices 3/4/5:
      child[3] — file positions of freed blocks
      child[4] — byte sizes of freed blocks
      child[5] — database version when each block was freed

    Returns a list of dicts with keys:
      offset, size, version, array_header (or None), strings (list[str]), bytes
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return []
    ref_eb = _elem_bytes(root_hdr)
    if ref_eb < 1 or root_hdr["Element count (size)"] < 6:
        return []
    payload_start = root_offset + 8
    pos_off = _read_ref(data, payload_start, 3, ref_eb)
    sz_off  = _read_ref(data, payload_start, 4, ref_eb)
    ver_off = _read_ref(data, payload_start, 5, ref_eb)

    positions = _read_uint_array(data, pos_off)
    sizes     = _read_uint_array(data, sz_off)
    versions  = _read_uint_array(data, ver_off)

    entries: list[dict[str, Any]] = []
    for i, (pos, sz) in enumerate(zip(positions, sizes)):
        if pos <= 0 or sz <= 0 or pos + sz > len(data):
            continue
        block = data[pos : pos + sz]
        arr_hdr = _parse_array_header(data, pos)
        strings: list[str] = []
        if arr_hdr is None:
            # Raw heap — extract null-separated printable strings (≥4 chars)
            for chunk in block.split(b"\x00"):
                try:
                    s = chunk.decode("utf-8")
                    if len(s) >= 4 and s.isprintable():
                        strings.append(s)
                except Exception:
                    pass
        entries.append({
            "index": i,
            "offset": pos,
            "size": sz,
            "version": versions[i] if i < len(versions) else None,
            "array_header": arr_hdr,
            "strings": strings,
            "bytes": block,
        })
    return entries


def _extract_root_children(
    data: bytes, root_offset: int, file_size: int
) -> list[dict[str, Any]]:
    """Return the child entries of a root Reference Array.

    For each of the N references stored in the root array, returns a dict with
    the child's file offset and its decoded array header (if readable).
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return []

    ref_elem_bytes = _elem_bytes(root_hdr)
    if ref_elem_bytes < 1:
        return []

    size = root_hdr["Element count (size)"]
    payload_start = root_offset + 8
    children: list[dict[str, Any]] = []
    for i in range(size):
        offset = _read_ref(data, payload_start, i, ref_elem_bytes)
        child: dict[str, Any] = {"index": i, "offset": offset}
        if 0 < offset < file_size:
            child["array_header"] = _parse_array_header(data, offset)
        else:
            child["array_header"] = None
        children.append(child)
    return children


def _extract_schema(data: bytes, root_offset: int, file_size: int) -> list[str]:
    """Extract class/table names from the Realm schema group array.

    B+ tree path followed:
        root_offset  →  root Reference Array
        entry[0]     →  schema group Data Array
        each entry   →  null-terminated ASCII class name (padded to *width* bytes)
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return []

    ref_elem_bytes = _elem_bytes(root_hdr)
    if ref_elem_bytes < 1:
        return []

    payload_start = root_offset + 8
    schema_offset = _read_ref(data, payload_start, 0, ref_elem_bytes)
    if schema_offset <= 0 or schema_offset >= file_size:
        return []

    schema_hdr = _parse_array_header(data, schema_offset)
    if schema_hdr is None:
        return []

    entry_bytes = _elem_bytes(schema_hdr)
    count = schema_hdr["Element count (size)"]
    if entry_bytes < 1 or count == 0:
        return []

    payload_start = schema_offset + 8
    names: list[str] = []
    for i in range(count):
        entry_off = payload_start + i * entry_bytes
        if entry_off + entry_bytes > len(data):
            break
        entry = data[entry_off : entry_off + entry_bytes]
        null_pos = entry.find(b"\x00")
        raw = entry[:null_pos] if null_pos >= 0 else entry
        try:
            name = raw.decode("ascii")
        except Exception:
            continue
        if name:
            names.append(name)

    return names


# ---------------------------------------------------------------------------
# ClusterTree traversal
# ---------------------------------------------------------------------------
#
# Realm's Cluster leaf (cluster.hpp) stores: child[0] = key array (tagged
# integer -> compact sequential keys, row count = raw >> 1; or a ref to an
# explicit ArrayUnsigned of local key values), child[1..] = column data,
# one slot per column at index (colkey.index + 1) (s_first_col_index=1).
#
# Once a table outgrows one leaf, its ClusterTree root becomes a
# ClusterNodeInner (cluster_tree.cpp) with a *fixed* layout:
#   child[0] = key-offsets ref, or 0 for "compact" (uniformly-sized) children
#   child[1] = tagged sub_tree_depth
#   child[2] = tagged sub_tree_size (total row count of this subtree)
#   child[3..] = child node refs (each may itself be a leaf or inner node —
#                determined by that child's own is_inner_bptree_node flag)
# Child key-space offsets: explicit (child[0] ref) values are absolute
# per-child offsets; compact form computes offset = child_index << shift,
# shift = sub_tree_depth * node_shift_factor. node_shift_factor is 8 for the
# default REALM_MAX_BPNODE_SIZE > 256 build (true for all mainstream Realm
# SDKs); the alternate value (2) is a debug-only build config and is not
# handled here.

_NODE_SHIFT_FACTOR = 8


def _walk_cluster_leaves(
    data: bytes,
    root_ref: int,
    file_size: int,
    _visited: set[int] | None = None,
    _depth: int = 0,
    _base_offset: int = 0,
) -> list[tuple[int, int]]:
    """Recursively resolve a ClusterTree root to its ordered leaf Clusters.

    Returns a list of (leaf_ref, key_offset) pairs, in key order. key_offset
    is the absolute base to add to each leaf row's local key value to
    recover its real ObjKey (cluster.hpp Cluster::get_real_key).
    """
    if _depth > 32 or root_ref <= 0 or root_ref >= file_size:
        return []
    if _visited is None:
        _visited = set()
    if root_ref in _visited:
        return []
    _visited.add(root_ref)

    hdr = _parse_array_header(data, root_ref)
    if hdr is None or not hdr["has_refs"]:
        return []
    if not hdr["is_inner_bptree_node"]:
        return [(root_ref, _base_offset)]

    eb = _elem_bytes(hdr)
    if eb < 1:
        return []
    count = hdr["Element count (size)"]

    keys_ref = _read_ref(data, root_ref + 8, 0, eb)
    explicit_offsets: list[int] | None = _read_uint_array(data, keys_ref) if keys_ref > 0 else None

    depth_raw = _read_ref(data, root_ref + 8, 1, eb)
    sub_tree_depth = (depth_raw >> 1) if depth_raw >= 0 else 1
    shift = max(sub_tree_depth, 0) * _NODE_SHIFT_FACTOR

    leaves: list[tuple[int, int]] = []
    for i in range(3, count):
        child_ref = _read_ref(data, root_ref + 8, i, eb)
        if child_ref <= 0 or child_ref >= file_size:
            continue
        child_idx = i - 3
        if explicit_offsets is not None and child_idx < len(explicit_offsets):
            child_rel_offset = explicit_offsets[child_idx]
        else:
            child_rel_offset = child_idx << shift
        leaves.extend(
            _walk_cluster_leaves(
                data, child_ref, file_size, _visited, _depth + 1,
                _base_offset + child_rel_offset,
            )
        )
    return leaves


def _read_cluster_key_info(
    data: bytes, cluster_ref: int, cluster_eb: int, file_size: int,
) -> tuple[int | None, list[int] | None]:
    """Decode a leaf Cluster's child[0] key slot.

    Returns (row_count, local_key_values). child[0] is either a tagged
    integer (RefOrTagged compact form — row count = raw >> 1, local keys are
    implicitly 0..row_count-1) or a ref to a real ArrayUnsigned of explicit
    local key values (cluster.hpp Cluster::init, node_size_from_header).
    """
    raw = _read_ref(data, cluster_ref + 8, 0, cluster_eb)
    if raw < 0:
        return None, None
    if raw & 1:
        count = raw >> 1
        return count, list(range(count))
    if raw == 0 or raw >= file_size:
        return None, None
    hdr = _parse_array_header(data, raw)
    if hdr is None or hdr["has_refs"]:
        return None, None
    count = hdr["Element count (size)"]
    values = _read_scalar_leaf(data, raw, file_size)
    if values is None:
        return count, None
    return count, [v if v is not None else 0 for v in values]


def _derive_row_count(
    data: bytes,
    col_data_ref: int,
    num_cols: int,
    cd_eb: int,
    file_size: int,
) -> int | None:
    """Corruption-recovery fallback, used only when a leaf's key slot
    (child[0], handled by _read_cluster_key_info) cannot be read at all —
    e.g. a corrupt or partially-overwritten file; the primary, spec-driven
    read has already failed by the time this runs.

    This is not shape-guessing: in a well-formed Cluster leaf every scalar
    column array holds exactly one entry per row, so all of them share the
    same declared Element count — that equality is a real structural
    invariant of cluster.hpp, not an assumption about what the data
    "usually" looks like. Taking the most common count is a vote across
    those redundant, independently-stored copies to recover the true count
    even if corruption skewed a minority of them — the same logic as
    reconstructing a value from redundant/parity copies. The caller flags
    the affected table's row_count as estimated (row_count_estimated) so
    this is never presented to the analyst as an authoritative figure.
    """
    from collections import Counter
    counts: list[int] = []
    for c_idx in range(num_cols):
        col_ref = _read_ref(data, col_data_ref + 8, c_idx, cd_eb)
        if col_ref <= 0 or col_ref >= file_size:
            continue
        hdr = _parse_array_header(data, col_ref)
        if hdr and not hdr["has_refs"]:
            counts.append(hdr["Element count (size)"])
    if not counts:
        return None
    return Counter(counts).most_common(1)[0][0]


# ---------------------------------------------------------------------------
# BPlusTree traversal — List / Set (and LinkList) columns
# ---------------------------------------------------------------------------
#
# Each row of a List/Set column owns an *independent* BPlusTree<T> holding
# its elements (list.hpp: Lst<T>::m_tree; collection_parent.hpp:
# CollectionParent::get_collection_ref — a plain ref per row, 0 = empty
# collection, read directly from the cluster's column-data array like any
# other flat ref array).
#
# BPlusTree<T>'s own inner-node layout (bplustree.cpp: BPlusTreeInner) is
# *not* the same as ClusterNodeInner:
#   element[0]        = tagged "elements per child" (compact form), or a
#                        ref to an m_offsets array of per-child start
#                        offsets (general form) — distinguished by the
#                        RefOrTagged tag bit, not by zero/nonzero
#   element[1..N]      = child node refs (get_bp_node_ref(ndx)=get(ndx+1))
#   element[N+1] (last) = tagged total subtree size (get_tree_size=back()>>1)
# i.e. get_node_size() = Array::size() - 2 (2 bookkeeping slots, not 3).

def _walk_bplustree_leaves(
    data: bytes,
    root_ref: int,
    file_size: int,
    _visited: set[int] | None = None,
    _depth: int = 0,
    _base_offset: int = 0,
) -> list[tuple[int, int]]:
    """Recursively resolve a BPlusTree<T> root to its ordered leaf arrays.

    Returns (leaf_ref, offset) pairs; leaf_ref points directly to a leaf
    array in the *same* per-type format used for regular cluster columns
    (e.g. ArrayKey for a List<Link>'s elements), so leaves are decoded by
    reusing _decode_column_values with the collection's element type.
    """
    if _depth > 32 or root_ref <= 0 or root_ref >= file_size:
        return []
    if _visited is None:
        _visited = set()
    if root_ref in _visited:
        return []
    _visited.add(root_ref)

    hdr = _parse_array_header(data, root_ref)
    if hdr is None:
        return []
    if not hdr["is_inner_bptree_node"]:
        return [(root_ref, _base_offset)]

    eb = _elem_bytes(hdr)
    if eb < 1:
        return []
    count = hdr["Element count (size)"]
    if count < 2:
        return []
    num_children = count - 2

    elem0_raw = _read_ref(data, root_ref + 8, 0, eb)
    is_compact = elem0_raw >= 0 and (elem0_raw & 1) != 0
    elems_per_child = (elem0_raw >> 1) if is_compact else 0
    explicit_offsets: list[int] | None = None
    if not is_compact and elem0_raw > 0:
        explicit_offsets = _read_uint_array(data, elem0_raw)

    leaves: list[tuple[int, int]] = []
    for i in range(num_children):
        child_ref = _read_ref(data, root_ref + 8, i + 1, eb)
        if child_ref <= 0 or child_ref >= file_size:
            continue
        if explicit_offsets is not None:
            child_rel_offset = explicit_offsets[i - 1] if i > 0 and (i - 1) < len(explicit_offsets) else 0
        else:
            child_rel_offset = i * elems_per_child
        leaves.extend(
            _walk_bplustree_leaves(
                data, child_ref, file_size, _visited, _depth + 1,
                _base_offset + child_rel_offset,
            )
        )
    return leaves


def _read_collection_column(
    data: bytes,
    col_ref: int,
    file_size: int,
    element_type: int,
    nullable: bool,
) -> list[list[Any]] | None:
    """Decode a List/Set column: a flat ref array, one ref per row, each
    pointing to that row's own BPlusTree<T> root (0 = empty collection).
    Each row's elements are decoded by reusing _decode_column_values on
    every leaf of that row's tree, with the collection's element type.
    """
    hdr = _parse_array_header(data, col_ref)
    if hdr is None or not hdr["has_refs"]:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None
    count = hdr["Element count (size)"]

    element_info = {
        "type_code": element_type,
        "nullable": nullable,
        "is_list": False,
        "is_dictionary": False,
        "is_set": False,
    }

    results: list[list[Any]] = []
    for i in range(count):
        row_ref = _read_ref(data, col_ref + 8, i, eb)
        if row_ref <= 0 or row_ref >= file_size:
            results.append([])
            continue
        values: list[Any] = []
        for leaf_ref, _off in _walk_bplustree_leaves(data, row_ref, file_size):
            leaf_vals = _decode_column_values(data, leaf_ref, file_size, element_info)
            if leaf_vals:
                values.extend(leaf_vals)
        results.append(values)
    return results


def _read_dictionary_column(
    data: bytes,
    col_ref: int,
    file_size: int,
    key_type: int | None,
) -> list[dict[Any, Any]] | None:
    """Decode a Dictionary<K,Mixed> column: a flat ref array, one ref per
    row (0 = empty/no dictionary), each pointing directly to that row's own
    2-slot "dictionary top" array — no indirection (dictionary.cpp:
    `if (ref) { m_dictionary_top->init_from_ref(ref); m_keys->init_from_parent();
    m_values->init_from_parent(); }`).

    Slot 0 of that array is a BPlusTree<K> root for the keys, slot 1 a
    BPlusTree<Mixed> root for the values (dictionary.cpp constructor:
    `m_keys->set_parent(m_dictionary_top.get(), 0);
    m_values->set_parent(m_dictionary_top.get(), 1);` — values are always
    Mixed-typed regardless of the declared key type). The two trees are
    paired by identical index position, not an explicit key->value link
    (dictionary.cpp: `REALM_ASSERT(m_keys->size() == m_values->size())`).

    *key_type* is the DataType read from the spec's m_types array by the
    caller (_extract_column_info) — dispatched through the same
    _decode_column_values used for regular columns, since DataType and
    ColumnType share the same integer values for scalar types. Returns
    None (not a per-row failure) if the key type could not be determined,
    since keys cannot be decoded at all without it. Per-instance decoding
    (the 2-slot top array itself) is shared with Dictionaries nested
    inside a Mixed value via _read_dictionary_at_ref.
    """
    if key_type is None:
        return None
    hdr = _parse_array_header(data, col_ref)
    if hdr is None or not hdr["has_refs"]:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None
    count = hdr["Element count (size)"]

    results: list[dict[Any, Any]] = []
    for i in range(count):
        top_ref = _read_ref(data, col_ref + 8, i, eb)
        results.append(_read_dictionary_at_ref(data, top_ref, file_size, key_type))
    return results


# ---------------------------------------------------------------------------
# Spec / column metadata
# ---------------------------------------------------------------------------

def _extract_column_names(
    data: bytes,
    table_ref: int,
    table_eb: int,
    file_size: int,
) -> list[str]:
    """Read public column names from the spec at child[0] of the table node.

    Path: table_ref → child[0] (spec) → child[1] (names Data Array).
    The names array holds one fixed-width null-terminated ASCII entry per
    *public* column only (spec.hpp s_names_ndx=1; hidden BackLink columns
    have no name slot — confirmed empirically: a table with N declared
    columns has fewer name entries than colkey/type entries whenever it is
    the target of a Link elsewhere in the schema).
    Returns an empty list on any failure.
    """
    spec_ref = _read_ref(data, table_ref + 8, 0, table_eb)
    if spec_ref <= 0 or spec_ref >= file_size:
        return []
    spec_hdr = _parse_array_header(data, spec_ref)
    if spec_hdr is None or not spec_hdr["has_refs"] or spec_hdr["Element count (size)"] < 2:
        return []
    spec_eb = _elem_bytes(spec_hdr)
    if spec_eb < 1:
        return []

    names_ref = _read_ref(data, spec_ref + 8, 1, spec_eb)
    if names_ref <= 0 or names_ref >= file_size:
        return []
    names_hdr = _parse_array_header(data, names_ref)
    if names_hdr is None or names_hdr["has_refs"]:
        return []

    entry_bytes = _elem_bytes(names_hdr)
    count = names_hdr["Element count (size)"]
    if entry_bytes < 1 or count == 0:
        return []

    payload_start = names_ref + 8
    names: list[str] = []
    for i in range(count):
        entry_off = payload_start + i * entry_bytes
        if entry_off + entry_bytes > len(data):
            break
        entry = data[entry_off : entry_off + entry_bytes]
        null_pos = entry.find(b"\x00")
        raw = entry[:null_pos] if null_pos >= 0 else entry
        try:
            name = raw.decode("ascii").strip()
        except Exception:
            name = f"col_{i}"
        names.append(name if name else f"col_{i}")
    return names


def _extract_column_info(
    data: bytes,
    table_ref: int,
    table_eb: int,
    file_size: int,
) -> list[dict[str, Any]] | None:
    """Build the per-user-column decode plan directly from the colkeys array
    (spec child[5]) — the single source of truth for column dispatch.

    Each 64-bit ColKey packs index[0:16) | type[16:22) | attrs[22:30) |
    tag[30:62) (keys.hpp ColKey::get_index/get_type/get_attrs). attrs bit
    0x10=nullable, 0x20=list, 0x40=dictionary, 0x80=set (column_type.hpp
    ColumnAttr). This replaces separately reading and cross-referencing the
    spec's type-code array — the type is already embedded in the colkey.

    For Dictionary columns, the *key* type isn't in the colkey at all —
    it's packed into the upper 16 bits of the matching entry in the spec's
    m_types array (spec child[0]), one entry per column in the same full
    index space as colkeys (including hidden BackLink columns), set by
    Spec::set_dictionary_key_type / read by Spec::get_dictionary_key_type
    (spec.hpp/.cpp): `(type & 0xFFFF) + (int64_t(key_type) << 16)`.
    DataType and ColumnType share the same integer values for the basic
    scalar types (data_type.hpp: "Value assignments must be kept in sync
    with column_type.h"), so the extracted key type can be dispatched with
    the same type_code machinery used for regular columns.

    Hidden BackLink columns (type 14) are skipped, matching the public
    column order used by _extract_column_names. Returns None on failure.
    """
    spec_ref = _read_ref(data, table_ref + 8, 0, table_eb)
    if spec_ref <= 0 or spec_ref >= file_size:
        return None
    spec_hdr = _parse_array_header(data, spec_ref)
    if spec_hdr is None or not spec_hdr["has_refs"] or spec_hdr["Element count (size)"] < 6:
        return None
    spec_eb = _elem_bytes(spec_hdr)
    if spec_eb < 1:
        return None

    colkeys_ref = _read_ref(data, spec_ref + 8, 5, spec_eb)
    if colkeys_ref <= 0 or colkeys_ref >= file_size:
        return None
    colkeys = _read_scalar_leaf(data, colkeys_ref, file_size)
    if not colkeys:
        return None

    types_ref = _read_ref(data, spec_ref + 8, 0, spec_eb)
    raw_types = _read_scalar_leaf(data, types_ref, file_size) if 0 < types_ref < file_size else None

    infos: list[dict[str, Any]] = []
    user_col_idx = 0
    for spec_idx, colkey in enumerate(colkeys):
        if colkey is None:
            continue
        colkey = int(colkey)
        type_code = (colkey >> 16) & 0x3F
        if type_code in _HIDDEN_COL_TYPES:
            continue
        attrs = (colkey >> 22) & 0xFF
        is_dictionary = bool(attrs & _COL_ATTR_DICTIONARY)
        dictionary_key_type = None
        if is_dictionary and raw_types and spec_idx < len(raw_types):
            raw_type_val = raw_types[spec_idx]
            if raw_type_val is not None:
                dictionary_key_type = (int(raw_type_val) >> 16) & 0xFFFF
        infos.append({
            "user_col_idx": user_col_idx,
            "col_index": colkey & 0xFFFF,
            "cluster_idx": (colkey & 0xFFFF) + 1,
            "type_code": type_code,
            "nullable": bool(attrs & _COL_ATTR_NULLABLE),
            "is_list": bool(attrs & _COL_ATTR_LIST),
            "is_dictionary": is_dictionary,
            "is_set": bool(attrs & _COL_ATTR_SET),
            "dictionary_key_type": dictionary_key_type,
        })
        user_col_idx += 1
    return infos if infos else None


# TableKey::null_value (keys.hpp) — "no opposite table" sentinel.
_TABLE_KEY_NULL = 0x7FFFFFFF


def _read_table_own_key(
    data: bytes, table_ref: int, table_eb: int, file_size: int,
) -> int | None:
    """Read a table's own TableKey (table.hpp top_position_for_key=3, a
    tagged RefOrTagged value — Table::get_key_direct)."""
    raw = _read_ref(data, table_ref + 8, 3, table_eb)
    if raw < 0 or not (raw & 1):
        return None
    return raw >> 1


def _build_table_key_map(
    data: bytes, root_offset: int, schema: list[str], file_size: int,
) -> dict[int, str]:
    """Map each table's own TableKey to its schema name, so Link/LinkList
    columns can resolve which table they point to (table.hpp
    top_position_for_key / top_position_for_opposite_table — see
    _read_opposite_table_keys). TableKeys are stable identifiers assigned
    at table-creation time, not necessarily the same as the physical
    index into the Group's table-refs array, so this mapping is required
    rather than assuming table_key == schema index.
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return {}
    root_eb = _elem_bytes(root_hdr)
    if root_eb < 1:
        return {}
    table_refs_off = _read_ref(data, root_offset + 8, 1, root_eb)
    if table_refs_off <= 0 or table_refs_off >= file_size:
        return {}
    tr_hdr = _parse_array_header(data, table_refs_off)
    if tr_hdr is None or not tr_hdr["has_refs"]:
        return {}
    tr_eb = _elem_bytes(tr_hdr)
    num_tables = tr_hdr["Element count (size)"]

    mapping: dict[int, str] = {}
    for t_idx in range(num_tables):
        table_ref = _read_ref(data, table_refs_off + 8, t_idx, tr_eb)
        if table_ref <= 0 or table_ref >= file_size:
            continue
        t_hdr = _parse_array_header(data, table_ref)
        if t_hdr is None or not t_hdr["has_refs"] or t_hdr["Element count (size)"] < 4:
            continue
        t_eb = _elem_bytes(t_hdr)
        table_key = _read_table_own_key(data, table_ref, t_eb, file_size)
        if table_key is not None:
            mapping[table_key] = schema[t_idx] if t_idx < len(schema) else f"table[{t_idx}]"
    return mapping


def _read_opposite_table_keys(
    data: bytes, table_ref: int, table_eb: int, file_size: int,
) -> list[int | bool | None] | None:
    """Read table.hpp's m_opposite_table array (top_position_for_opposite_table
    = 7): one raw TableKey per column, in the same full index space as the
    colkeys/types/attrs arrays (including hidden BackLink columns) — used
    to resolve a Link/LinkList column's target table
    (Table::get_opposite_table_key)."""
    ref = _read_ref(data, table_ref + 8, 7, table_eb)
    if ref <= 0 or ref >= file_size:
        return None
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    return _read_scalar_leaf(data, ref, file_size)


# ---------------------------------------------------------------------------
# Primitive value decoders — each implements exactly one real Realm Array
# class. No structural guessing: the caller already knows which one to call
# from the column's declared type (see _extract_column_info / _decode_column_values).
# ---------------------------------------------------------------------------

def _read_scalar_leaf(
    data: bytes,
    col_offset: int,
    file_size: int,
) -> list[int | bool | None] | None:
    """Parse a flat, non-nullable Realm scalar array (ArrayInteger / boolean
    bit-packed / any plain has_refs=False integer array — also reused as the
    generic reader for colkeys, type codes, offsets, and key arrays).

        width=1, scheme=0  → 1 bit per row (0/1)
        width=2/4, scheme=0 → packed sub-byte unsigned integers
        width=8/16/32/64, scheme=0 or scheme=1 → little-endian integers
          (byte-aligned widths are reinterpreted as signed int64_t, matching
          Realm's actual column storage, so values stay within qlonglong
          range for Qt)

    Returns a list of values (``None`` where data is unreadable), or ``None``
    if the node does not look like a scalar leaf.
    """
    hdr = _parse_array_header(data, col_offset)
    if hdr is None:
        return None

    count = hdr["Element count (size)"]
    width = hdr["width"]
    scheme = hdr["width_scheme"]
    payload_start = col_offset + 8

    if count == 0:
        return []

    if scheme == 0:
        if width == 0:
            return [0] * count
        payload = data[payload_start : payload_start + hdr["Payload bytes (raw)"]]
        if width == 1:
            result: list[int | bool | None] = []
            for i in range(count):
                byte_i, bit_i = divmod(i, 8)
                if byte_i < len(payload):
                    result.append(bool((payload[byte_i] >> bit_i) & 1))
                else:
                    result.append(None)
            return result
        if width in (2, 4, 8, 16, 32, 64):
            mask = (1 << width) - 1
            sign_bit = (1 << (width - 1)) if width >= 8 else 0
            result = []
            for i in range(count):
                bit_pos = i * width
                byte_pos = bit_pos // 8
                bit_off = bit_pos % 8
                needed = (bit_off + width + 7) // 8
                if byte_pos + needed > len(payload):
                    result.append(None)
                    continue
                raw = 0
                for b in range(needed):
                    raw |= payload[byte_pos + b] << (b * 8)
                val = (raw >> bit_off) & mask
                if sign_bit and val >= sign_bit:
                    val -= (1 << width)
                result.append(val)
            return result

    elif scheme == 1:
        eb = int(width)
        if eb < 1 or eb > 8:
            return None
        result = []
        for i in range(count):
            off = payload_start + i * eb
            if off + eb > len(data):
                result.append(None)
            else:
                # signed=True: Realm uses int64_t for all integer columns
                result.append(int.from_bytes(data[off : off + eb], "little", signed=True))
        return result

    return None


def _read_array_int_null(
    data: bytes, ref: int, file_size: int,
) -> list[int | None] | None:
    """Decode a Realm ArrayIntNull: a flat array of N+1 values where slot[0]
    is a file-chosen null sentinel and slots[1..N] are the row values;
    value == sentinel means NULL (array_integer.hpp: null_value() reads
    slot 0 directly — it is not a fixed/assumed constant like INT_MAX).
    Also used to decode the nullable "seconds" sub-array of a Timestamp.
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    count = hdr["Element count (size)"]
    if count == 0:
        return []
    vals = _read_scalar_leaf(data, ref, file_size)
    if not vals:
        return None
    sentinel = vals[0]
    return [None if v == sentinel else v for v in vals[1:]]


def _read_array_bool(
    data: bytes, ref: int, file_size: int, nullable: bool,
) -> list[bool | None] | None:
    """Decode a Realm ArrayBool/ArrayBoolNull: a flat array; for the
    nullable variant, NULL is signalled by the value being *exactly* 3,
    not "any value >= 2" (array_bool.hpp: null_value = 3).
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    count = hdr["Element count (size)"]
    if count == 0:
        return []
    vals = _read_scalar_leaf(data, ref, file_size)
    if vals is None:
        return None
    if nullable:
        return [None if v == 3 else bool(v) for v in vals]
    return [bool(v) for v in vals]


def _read_array_string_short(
    data: bytes, ref: int, hdr: dict[str, Any], *, is_string: bool, nullable: bool,
) -> list[Any]:
    """ArrayStringShort: fixed W-byte slots; last byte of each slot is a pad
    count. pad == W → NULL, else content length = (W-1) - pad
    (array_string_short.hpp: get()/get(header,...)).
    """
    width = hdr["width"]
    count = hdr["Element count (size)"]
    empty: Any = "" if is_string else b""
    if width == 0:
        return [None if nullable else empty] * count
    payload_start = ref + 8
    results: list[Any] = []
    for i in range(count):
        off = payload_start + i * width
        entry = data[off : off + width]
        if len(entry) < width:
            results.append(None)
            continue
        pad = entry[width - 1]
        if pad == width:
            results.append(None if nullable else empty)
            continue
        length = (width - 1) - pad
        raw = entry[:length] if length > 0 else b""
        results.append(raw.decode("utf-8", errors="replace") if is_string else bytes(raw))
    return results


def _read_array_small_blobs(
    data: bytes, ref: int, hdr: dict[str, Any], file_size: int, *, is_string: bool,
) -> list[Any] | None:
    """ArraySmallBlobs: 3-entry [offsets, blob, nulls]. offsets[i] is the
    cumulative END position of row i's bytes in blob (begin = offsets[i-1],
    or 0 for i=0) — not a start-offset with a NUL-terminator scan. nulls[i]
    nonzero means row i is NULL (a plain int array, not necessarily 1-bit
    wide). String rows carry a trailing '\\0' in blob that is stripped;
    Binary rows do not (array_blobs_small.hpp).
    """
    if hdr["Element count (size)"] != 3:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None
    offs_ref = _read_ref(data, ref + 8, 0, eb)
    blob_ref = _read_ref(data, ref + 8, 1, eb)
    nulls_ref = _read_ref(data, ref + 8, 2, eb)

    offsets = _read_uint_array(data, offs_ref)
    nulls = _read_uint_array(data, nulls_ref)

    blob_hdr = _parse_array_header(data, blob_ref)
    blob = b""
    if blob_hdr is not None:
        blob_size = blob_hdr["Element count (size)"]
        blob = data[blob_ref + 8 : blob_ref + 8 + blob_size]

    results: list[Any] = []
    prev = 0
    for i, end in enumerate(offsets):
        is_null = nulls[i] != 0 if i < len(nulls) else False
        if is_null:
            results.append(None)
        else:
            chunk = blob[prev:end]
            if is_string:
                if chunk.endswith(b"\x00"):
                    chunk = chunk[:-1]
                results.append(chunk.decode("utf-8", errors="replace"))
            else:
                results.append(bytes(chunk))
        prev = end
    return results


def _read_array_big_blobs(
    data: bytes, ref: int, hdr: dict[str, Any], file_size: int, *, is_string: bool,
) -> list[Any]:
    """ArrayBigBlobs: a flat ref array; each element is a ref to its own
    standalone blob array elsewhere in the file, or 0 for NULL
    (array_blobs_big.hpp: get()/get(header,...)). Used once a value is too
    large for the shared small-blobs layout (e.g. long email bodies).
    """
    eb = _elem_bytes(hdr)
    count = hdr["Element count (size)"]
    results: list[Any] = []
    if eb < 1:
        return [None] * count
    for i in range(count):
        blob_ref = _read_ref(data, ref + 8, i, eb)
        if blob_ref <= 0 or blob_ref >= file_size:
            results.append(None)
            continue
        blob_hdr = _parse_array_header(data, blob_ref)
        if blob_hdr is None:
            results.append(None)
            continue
        size = blob_hdr["Element count (size)"]
        chunk = data[blob_ref + 8 : blob_ref + 8 + size]
        if is_string:
            if chunk.endswith(b"\x00"):
                chunk = chunk[:-1]
            results.append(chunk.decode("utf-8", errors="replace"))
        else:
            results.append(bytes(chunk))
    return results


def _read_array_string_or_binary(
    data: bytes,
    ref: int,
    file_size: int,
    *,
    is_string: bool,
    nullable: bool,
) -> list[Any] | None:
    """Decode a Realm String or Binary column leaf.

    String and Binary share *identical* on-disk storage (ArrayString::get,
    array_string.hpp:146-161) — the only real distinguishing signal is the
    column's declared type, not the array's shape. Dispatch is purely on
    the array header's own flags (already decoded by _parse_array_header):

        has_refs=False                → ArrayStringShort (inline)
        has_refs=True, context=False  → ArraySmallBlobs (offsets/blob/nulls)
        has_refs=True, context=True   → ArrayBigBlobs (per-row ref to a blob)
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None:
        return None
    if not hdr["has_refs"]:
        return _read_array_string_short(data, ref, hdr, is_string=is_string, nullable=nullable)
    if not hdr["context_flag"]:
        return _read_array_small_blobs(data, ref, hdr, file_size, is_string=is_string)
    return _read_array_big_blobs(data, ref, hdr, file_size, is_string=is_string)


def _read_array_timestamp(data: bytes, ref: int, file_size: int) -> list[str | None] | None:
    """Decode a Realm ArrayTimestamp: 2-entry [seconds_ref, nanoseconds_ref].
    seconds is itself an ArrayIntNull; nanoseconds is a plain non-nullable
    array (array_timestamp.cpp: create()/init_from_mem()).
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or not hdr["has_refs"] or hdr["Element count (size)"] != 2:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None
    secs_ref = _read_ref(data, ref + 8, 0, eb)
    nanos_ref = _read_ref(data, ref + 8, 1, eb)

    secs = _read_array_int_null(data, secs_ref, file_size)
    if secs is None:
        return None

    nanos: list[int | None] | None = None
    nanos_hdr = _parse_array_header(data, nanos_ref)
    if nanos_hdr is not None and not nanos_hdr["has_refs"]:
        nanos = _read_scalar_leaf(data, nanos_ref, file_size)

    result: list[str | None] = []
    for i, s in enumerate(secs):
        if s is None:
            result.append(None)
            continue
        ns = nanos[i] if nanos and i < len(nanos) and nanos[i] else 0
        result.append(_decode_timestamp(int(s + (ns / 1_000_000_000 if ns else 0))))
    return result


def _read_array_fixed_bytes(
    data: bytes, ref: int, file_size: int, elem_size: int,
) -> list[bytes | None] | None:
    """Decode a Realm ArrayFixedBytes[Null] leaf: elements are packed in
    blocks of 8, with 1 extra null-bitvector byte prefixing each block
    (array_fixed_bytes.hpp: Pos::get_pos/is_null, s_block_size). Used for
    ObjectId (elem_size=12) and UUID (elem_size=16); nullability is encoded
    the same way regardless of whether the column itself is nullable.
    Returns raw per-element bytes (or None); callers format them.
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    total_bytes = hdr["Element count (size)"]
    if total_bytes <= 0:
        return []
    block_size = elem_size * 8 + 1
    data_bytes = total_bytes - -(-total_bytes // block_size)  # total - ceil(total/block_size)
    n = max(data_bytes // elem_size, 0)
    payload = data[ref + 8 : ref + 8 + total_bytes]
    results: list[bytes | None] = []
    for i in range(n):
        block_idx, offset = divmod(i, 8)
        base = block_idx * block_size
        if base >= len(payload):
            results.append(None)
            continue
        bitvec = payload[base]
        if bitvec & (1 << offset):
            results.append(None)
            continue
        start = base + 1 + offset * elem_size
        val = payload[start : start + elem_size]
        results.append(val if len(val) == elem_size else None)
    return results


def _format_uuid(raw: bytes) -> str:
    try:
        return str(_uuid_mod.UUID(bytes=raw))
    except Exception:
        return raw.hex()


def _decode_bid(raw_int: int, total_bits: int) -> str:
    """Decode an IEEE 754-2008 BID (binary integer decimal) value — the
    encoding Realm's Decimal128 uses (array_decimal128.hpp: Bid64/Bid128).

    Combination-field decode per IEEE 754-2008 §3.5.2: the coefficient's
    leading decimal digit (0-9) is folded into the 5 most-significant bits
    of the combination field alongside 2 exponent bits, so the full
    coefficient reconstructs as msd * 2**t_width + trailing_significand.

    NOTE: this is a hand-implementation of the public IEEE 754-2008 BID
    arithmetic itself (combination-field/exponent/coefficient decode), not
    something Realm's own source needs to define -- the *storage* format
    (word order, low/high placement) is confirmed from Realm Core source
    (see _read_array_mixed), but this function's own arithmetic has not
    been run against known IEEE 754-2008 BID test vectors. Treat output
    with appropriate care until that verification happens.
    """
    if total_bits == 64:
        g_width, t_width, bias = 13, 50, 398
    elif total_bits == 128:
        g_width, t_width, bias = 17, 110, 6176
    else:
        return f"<decimal128 unsupported width {total_bits}b>"

    sign = (raw_int >> (total_bits - 1)) & 1
    g = (raw_int >> t_width) & ((1 << g_width) - 1)
    t = raw_int & ((1 << t_width) - 1)

    g_top5 = g >> (g_width - 5)
    exp_low_bits = g & ((1 << (g_width - 5)) - 1)

    if (g_top5 >> 3) != 0b11:
        msd = (g_top5 >> 2) & 0b111
        exp_high2 = g_top5 & 0b11
    else:
        g2g3 = (g_top5 >> 1) & 0b11
        if g2g3 == 0b11:
            g4 = g_top5 & 1
            if g4:
                return "NaN"
            return "-Infinity" if sign else "Infinity"
        msd = 8 | (g_top5 & 1)
        exp_high2 = g2g3

    biased_exponent = (exp_high2 << (g_width - 5)) | exp_low_bits
    coefficient = msd * (1 << t_width) + t
    exponent = biased_exponent - bias

    value = decimal.Decimal(coefficient).scaleb(exponent)
    if sign:
        value = -value
    return str(value)


def _read_array_decimal128(data: bytes, ref: int, file_size: int) -> list[str | None] | None:
    """Decode a Realm ArrayDecimal128 leaf: element width 0/4/8/16 bytes
    selects null/Bid32/Bid64/Bid128 (array_decimal128.hpp: get()). Bid64 and
    Bid128 (the common cases) are decoded via _decode_bid; Bid32 is rare
    enough that it is surfaced as labeled raw bytes rather than a from-memory
    guess at its (differently-sized) combination field.
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    width = hdr["width"]
    count = hdr["Element count (size)"]
    if width == 0:
        return [None] * count
    payload_start = ref + 8
    results: list[str | None] = []
    for i in range(count):
        off = payload_start + i * width
        raw = data[off : off + width]
        if len(raw) < width:
            results.append(None)
            continue
        if width == 16:
            results.append(_decode_bid(int.from_bytes(raw, "little"), 128))
        elif width == 8:
            results.append(_decode_bid(int.from_bytes(raw, "little"), 64))
        else:
            results.append(f"<decimal128 raw {width}B: {raw.hex()}>")
    return results


def _read_array_link(data: bytes, ref: int, file_size: int) -> list[int | None] | None:
    """Decode a Realm ArrayKey (single Link column): a flat array where the
    stored value is the target ObjKey + 1, so that 0 can represent NULL
    (array_key.hpp: ArrayKeyBase<1>::get/set — adj=1 for cluster-leaf storage).
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    vals = _read_scalar_leaf(data, ref, file_size)
    if vals is None:
        return None
    return [None if v is None or v == 0 else v - 1 for v in vals]


def _read_array_float(data: bytes, ref: int, file_size: int) -> list[float | None] | None:
    """Decode a Realm BasicArray<float|double>: a flat array of native
    IEEE754 values (array_basic_tpl.hpp: get() = reinterpret_cast<T*>).
    NULL is represented as NaN, matching all real Float/Double values
    (null.hpp: is_null_float / array_basic.hpp: is_null()).
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"] or hdr["width"] not in (4, 8):
        return None
    count = hdr["Element count (size)"]
    if count == 0:
        return []
    fmt = "<f" if hdr["width"] == 4 else "<d"
    elem_size = hdr["width"]
    payload_start = ref + 8
    results: list[float | None] = []
    for i in range(count):
        off = payload_start + i * elem_size
        chunk = data[off : off + elem_size]
        if len(chunk) < elem_size:
            results.append(None)
            continue
        val = struct.unpack(fmt, chunk)[0]
        results.append(None if math.isnan(val) else val)
    return results


def _read_array_typed_link(data: bytes, ref: int, file_size: int) -> list[str | None] | None:
    """Decode a Realm ArrayTypedLink: a flat array of (table_key+1,
    obj_key+1) int64 pairs — 2*size elements total, table_key==0 means NULL
    (array_typed_link.hpp: ArrayTypedLink::get/is_null). TableKey is not
    resolved to a table name here (that requires the Group's table-key
    array, not yet mapped from source) — shown as the raw numeric key.
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or hdr["has_refs"]:
        return None
    vals = _read_scalar_leaf(data, ref, file_size)
    if not vals or len(vals) % 2 != 0:
        return None
    results: list[str | None] = []
    for i in range(0, len(vals), 2):
        tk, ok = vals[i], vals[i + 1]
        if not tk:
            results.append(None)
            continue
        table_key = (int(tk) - 1) & 0x7FFFFFFF
        obj_key = int(ok) - 1 if ok is not None else None
        results.append(f"Obj(table_key={table_key}, key={obj_key})")
    return results


# Mixed's composite-value encoding (array_mixed.hpp): each m_composite
# entry packs (payload_or_inline_value << 8) | (payload_idx << 5) | (data_type+1).
_MIXED_DATA_TYPE_MASK = 0b0001_1111
_MIXED_PAYLOAD_IDX_MASK = 0b1110_0000
_MIXED_DATA_SHIFT = 8


_MIXED_MAX_NEST_DEPTH = 16  # guard against a corrupt/malicious Mixed<->collection reference chain


def _read_array_mixed(
    data: bytes, ref: int, file_size: int, _nest_depth: int = 0,
) -> list[Any] | None:
    """Decode a Realm ArrayMixed leaf (array_mixed.hpp/.cpp).

    Outer array slots: [0]=m_composite (one packed int64 per row — see the
    _MIXED_* constants above), [1]=m_ints (single-int64 payloads: Int
    overflow/Float/Double bit patterns/Link), [2]=m_int_pairs (2 int64s per
    payload: Timestamp secs+nanos, Decimal128 low+high 64-bit words,
    TypedLink table+obj key), [3]=m_strings (String/Binary/ObjectId/UUID
    raw bytes, ArrayString-shaped so the trailing zero-terminator is
    stripped the same way a real string column strips it), [4]=m_refs
    (List/Set/Dictionary held *inside* a Mixed — array_mixed.hpp's
    payload_idx enum: payload_idx_ref=4 selects this array; data_type.hpp
    defines type_List=19/type_Set=20/type_Dictionary=21 as regular
    DataType values beyond the scalar ones, which is exactly what lands in
    this dispatch's data_type field).

    List/Set-in-Mixed always has Mixed-typed elements (no static element
    type exists once nested in a Mixed) and its ref points directly at a
    BPlusTree<Mixed> root — the same shape _read_collection_column decodes
    per-row for a top-level List/Set column, just entered directly since
    here there is exactly one collection per Mixed value.

    Dictionary-in-Mixed is always String-keyed: dictionary.cpp's ref-only
    constructor (`Dictionary(Allocator&, ColKey, ref_type)`, used when
    there is no owning Spec column to consult) initializes
    `m_key_type(type_String)` unconditionally — confirmed from that
    constructor's body, not assumed.

    Geospatial (type_Geospatial=22) has no case in array_mixed.cpp's
    store() at all — it isn't a distinct low-level Mixed payload here, so
    any occurrence falls through to the same "unsupported type" marker as
    a genuinely unknown value, never silently.

    NOTE: no Mixed-typed column or list has appeared in a real file this
    parser has been run against yet, only hand-built synthetic fixtures
    matching the on-disk format spec — dispatch here is still entirely
    from the format spec, not guessed. The Decimal128 word order
    (w[0]=low, w[1]=high) is confirmed, not assumed: array_mixed.cpp's
    write path does `m_int_pairs.add(t.raw()->w[0]); m_int_pairs.add(t.raw()->w[1]);`,
    and decimal128.hpp's own accessors read `get_coefficient_low()` from
    w[0] and `get_coefficient_high()` from w[1].
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or not hdr["has_refs"] or hdr["Element count (size)"] < 4:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None

    composite_ref = _read_ref(data, ref + 8, 0, eb)
    ints_ref = _read_ref(data, ref + 8, 1, eb)
    pairs_ref = _read_ref(data, ref + 8, 2, eb)
    strings_ref = _read_ref(data, ref + 8, 3, eb)
    refs_ref = _read_ref(data, ref + 8, 4, eb) if hdr["Element count (size)"] >= 5 else 0

    composite = _read_scalar_leaf(data, composite_ref, file_size)
    if composite is None:
        return None

    ints = _read_scalar_leaf(data, ints_ref, file_size) if 0 < ints_ref < file_size else None
    pairs = _read_scalar_leaf(data, pairs_ref, file_size) if 0 < pairs_ref < file_size else None
    refs = _read_scalar_leaf(data, refs_ref, file_size) if 0 < refs_ref < file_size else None
    raw_strings: list[Any] | None = None
    if 0 < strings_ref < file_size:
        raw_strings = _read_array_string_or_binary(
            data, strings_ref, file_size, is_string=False, nullable=False,
        )

    def ref_payload(idx: int) -> int | None:
        if not refs or idx >= len(refs):
            return None
        v = refs[idx]
        return int(v) if v is not None else None

    def string_payload(idx: int) -> bytes | None:
        if not raw_strings or idx >= len(raw_strings):
            return None
        raw = raw_strings[idx]
        if not isinstance(raw, (bytes, bytearray)):
            return None
        # The shared m_strings array always stores values the same way a
        # real string column does (trailing zero-terminator included).
        return bytes(raw[:-1]) if raw.endswith(b"\x00") else bytes(raw)

    def pair_payload(idx: int) -> tuple[int, int] | None:
        if not pairs or idx * 2 + 1 >= len(pairs):
            return None
        a, b = pairs[idx * 2], pairs[idx * 2 + 1]
        return (0 if a is None else int(a), 0 if b is None else int(b))

    def int_payload(idx: int) -> int | None:
        if not ints or idx >= len(ints):
            return None
        v = ints[idx]
        return int(v) if v is not None else None

    results: list[Any] = []
    for val in composite:
        if not val:
            results.append(None)
            continue
        val = int(val)
        data_type = (val & _MIXED_DATA_TYPE_MASK) - 1
        payload_idx_flag = (val & _MIXED_PAYLOAD_IDX_MASK) >> 5
        payload_val = val >> _MIXED_DATA_SHIFT

        if data_type == 0:  # Int
            if payload_idx_flag == 0:
                results.append(payload_val)
            else:
                results.append(int_payload(payload_val))
        elif data_type == 1:  # Bool
            results.append(payload_val != 0)
        elif data_type == 9:  # Float
            iv = int_payload(payload_val)
            results.append(struct.unpack("<f", (iv & 0xFFFFFFFF).to_bytes(4, "little"))[0] if iv is not None else None)
        elif data_type == 10:  # Double
            iv = int_payload(payload_val)
            results.append(struct.unpack("<d", (iv & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little"))[0] if iv is not None else None)
        elif data_type == 2:  # String
            raw = string_payload(payload_val)
            results.append(raw.decode("utf-8", errors="replace") if raw is not None else None)
        elif data_type == 4:  # Binary
            raw = string_payload(payload_val)
            results.append(raw if raw is not None else None)
        elif data_type == 8:  # Timestamp
            pair = pair_payload(payload_val)
            results.append(
                _decode_timestamp(int(pair[0] + (pair[1] / 1_000_000_000 if pair[1] else 0)))
                if pair else None
            )
        elif data_type == 15:  # ObjectId
            raw = string_payload(payload_val)
            results.append(raw.hex() if raw is not None else None)
        elif data_type == 11:  # Decimal128
            pair = pair_payload(payload_val)
            if pair:
                low, high = pair[0] & 0xFFFFFFFFFFFFFFFF, pair[1] & 0xFFFFFFFFFFFFFFFF
                results.append(_decode_bid(low | (high << 64), 128))
            else:
                results.append(None)
        elif data_type == 12:  # Link
            results.append(int_payload(payload_val))
        elif data_type == 16:  # TypedLink
            pair = pair_payload(payload_val)
            if pair:
                results.append(f"Obj(table_key={pair[0]}, key={pair[1]})")
            else:
                results.append(None)
        elif data_type == 17:  # UUID
            raw = string_payload(payload_val)
            results.append(_format_uuid(raw) if raw is not None else None)
        elif data_type in (19, 20):  # List, Set (elements are always Mixed once nested)
            r = ref_payload(payload_val)
            if r is None:
                results.append(None)
            elif _nest_depth >= _MIXED_MAX_NEST_DEPTH:
                results.append(f"<mixed: nesting depth limit ({_MIXED_MAX_NEST_DEPTH}) reached>")
            else:
                results.append(_read_collection_at_ref(data, r, file_size, _nest_depth + 1))
        elif data_type == 21:  # Dictionary (always String-keyed -- see docstring)
            r = ref_payload(payload_val)
            if r is None:
                results.append(None)
            elif _nest_depth >= _MIXED_MAX_NEST_DEPTH:
                results.append(f"<mixed: nesting depth limit ({_MIXED_MAX_NEST_DEPTH}) reached>")
            else:
                results.append(_read_dictionary_at_ref(data, r, file_size, 2, _nest_depth + 1))
        else:
            results.append(f"<mixed: unsupported type_{data_type}>")
    return results


def _read_collection_at_ref(
    data: bytes, row_ref: int, file_size: int, _nest_depth: int,
) -> list[Any]:
    """Decode one List/Set instance held inside a Mixed value, from its
    BPlusTree<Mixed> root ref. Same on-disk shape as a top-level List/Set
    column's per-row ref (_read_collection_column) — entered directly here
    since there is exactly one collection per Mixed value, not one per
    Cluster row.
    """
    if row_ref <= 0 or row_ref >= file_size:
        return []
    element_info = {
        "type_code": 6, "nullable": False, "is_list": False,
        "is_dictionary": False, "is_set": False,
    }
    values: list[Any] = []
    for leaf_ref, _off in _walk_bplustree_leaves(data, row_ref, file_size):
        leaf_vals = _decode_column_values(data, leaf_ref, file_size, element_info, _nest_depth)
        if leaf_vals:
            values.extend(leaf_vals)
    return values


def _read_dictionary_at_ref(
    data: bytes, top_ref: int, file_size: int, key_type: int, _nest_depth: int = 0,
) -> dict[Any, Any]:
    """Decode one Dictionary instance from its 2-slot "dictionary top" ref
    (dictionary.cpp: slot 0 = keys BPlusTree root, slot 1 = values
    BPlusTree<Mixed> root, paired by index). Shared by top-level Dictionary
    columns (_read_dictionary_column, key type read from the spec's
    m_types) and Dictionaries held inside a Mixed value (_read_array_mixed,
    key type always String — see its docstring).
    """
    if top_ref <= 0 or top_ref >= file_size:
        return {}
    top_hdr = _parse_array_header(data, top_ref)
    if top_hdr is None or not top_hdr["has_refs"] or top_hdr["Element count (size)"] < 2:
        return {}
    top_eb = _elem_bytes(top_hdr)
    if top_eb < 1:
        return {}
    keys_root = _read_ref(data, top_ref + 8, 0, top_eb)
    values_root = _read_ref(data, top_ref + 8, 1, top_eb)

    key_info = {
        "type_code": key_type, "nullable": False, "is_list": False,
        "is_dictionary": False, "is_set": False,
    }
    value_info = {
        "type_code": 6, "nullable": False, "is_list": False,
        "is_dictionary": False, "is_set": False,
    }

    keys: list[Any] = []
    if 0 < keys_root < file_size:
        for leaf_ref, _off in _walk_bplustree_leaves(data, keys_root, file_size):
            leaf_vals = _decode_column_values(data, leaf_ref, file_size, key_info)
            if leaf_vals:
                keys.extend(leaf_vals)

    values: list[Any] = []
    if 0 < values_root < file_size:
        for leaf_ref, _off in _walk_bplustree_leaves(data, values_root, file_size):
            leaf_vals = _decode_column_values(data, leaf_ref, file_size, value_info, _nest_depth)
            if leaf_vals:
                values.extend(leaf_vals)

    return {
        (key if key is not None else f"<null key {j}>"): (values[j] if j < len(values) else None)
        for j, key in enumerate(keys)
    }


_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _decode_timestamp(val: int) -> str:
    """Convert a Realm Timestamp value (whole seconds since the Unix epoch)
    to a readable UTC string.

    array_timestamp.hpp always stores a Timestamp as a separate (seconds,
    nanoseconds) pair; both call sites already combine that pair into whole
    seconds before calling this, so the unit is known from the spec, not
    guessed from magnitude. Negative values (dates before 1970) are valid
    and decoded the same way, not just positive/"plausible" ones.

    Computed via epoch + timedelta rather than datetime.fromtimestamp():
    fromtimestamp() delegates to the platform C library (gmtime/localtime),
    and Windows' CRT rejects negative and far-future timestamps that glibc
    accepts fine (OSError: [Errno 22] Invalid argument) — pure Python
    date arithmetic gives the same, platform-independent result everywhere.
    Falls back to the raw integer string only if it's outside what
    datetime can represent at all (year 1 - 9999).
    """
    try:
        dt = _UNIX_EPOCH_UTC + timedelta(seconds=val)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OverflowError, ValueError):
        return str(val)


def _decode_column_values(
    data: bytes,
    col_ref: int,
    file_size: int,
    info: dict[str, Any],
    _nest_depth: int = 0,
) -> list[Any] | None:
    """Dispatch to the exact decoder for one column's leaf array, based on
    its declared (type, nullable, collection) from the colkey — no
    structural guessing. *_nest_depth* only matters for Mixed columns: it
    is threaded through to _read_array_mixed, which increments it each
    time it descends into a List/Set/Dictionary held *inside* a Mixed
    value, so a corrupt or maliciously crafted chain of
    Mixed-holding-collection-holding-Mixed-... cannot recurse unbounded
    (see _MIXED_MAX_NEST_DEPTH).
    """
    if info["is_dictionary"]:
        return _read_dictionary_column(data, col_ref, file_size, info.get("dictionary_key_type"))

    type_code = info["type_code"]
    nullable = info["nullable"]

    # type_code 13 is Realm's on-disk LinkList marker — not a named constant
    # in the modern ColumnType enum (it predates unified Collections) but
    # still the real value stored in the colkey; always paired with the
    # List attribute bit in practice. Verified against poczta.realm.
    if info["is_list"] or info["is_set"] or type_code == 13:
        element_type = 12 if type_code == 13 else type_code
        return _read_collection_column(data, col_ref, file_size, element_type, nullable)

    if type_code == 0:  # Int
        if nullable:
            return _read_array_int_null(data, col_ref, file_size)
        return _read_scalar_leaf(data, col_ref, file_size)
    if type_code == 1:  # Bool
        return _read_array_bool(data, col_ref, file_size, nullable)
    if type_code in (2, 4):  # String, Binary
        return _read_array_string_or_binary(
            data, col_ref, file_size, is_string=(type_code == 2), nullable=nullable,
        )
    if type_code == 8:  # Timestamp
        return _read_array_timestamp(data, col_ref, file_size)
    if type_code in (9, 10):  # Float, Double
        return _read_array_float(data, col_ref, file_size)
    if type_code == 11:  # Decimal128
        return _read_array_decimal128(data, col_ref, file_size)
    if type_code == 12:  # Link (single)
        return _read_array_link(data, col_ref, file_size)
    if type_code == 15:  # ObjectId
        raw = _read_array_fixed_bytes(data, col_ref, file_size, 12)
        return None if raw is None else [None if v is None else v.hex() for v in raw]
    if type_code == 17:  # UUID
        raw = _read_array_fixed_bytes(data, col_ref, file_size, 16)
        return None if raw is None else [None if v is None else _format_uuid(v) for v in raw]
    if type_code == 6:  # Mixed
        return _read_array_mixed(data, col_ref, file_size, _nest_depth)
    if type_code == 16:  # TypedLink
        return _read_array_typed_link(data, col_ref, file_size)
    return None  # unknown type code


# ---------------------------------------------------------------------------
# Table data extraction
# ---------------------------------------------------------------------------

def _extract_table_data(
    data: bytes,
    root_offset: int,
    schema: list[str],
    file_size: int,
    table_key_map: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    """Walk each table's ClusterTree and decode its rows.

    Path: root_offset → child[1] (table refs) → table_node → child[2]
    (ClusterTree root) → (recursively, via _walk_cluster_leaves) leaf
    Cluster(s) → column data arrays → decoded values, per column dispatched
    by its declared (type, nullable, collection) from the colkeys array
    (_extract_column_info / _decode_column_values) — not by shape-guessing.
    A table whose ClusterTree spans multiple leaves (more rows than fit in
    one Cluster) has its leaves' column values concatenated in key order.

    *table_key_map* (from _build_table_key_map), if given, is used to
    resolve each Link/LinkList column's target table name via
    _read_opposite_table_keys — exposed per table as "column_target_tables".

    Returns a list of dicts {name, row_count, columns, column_names,
    column_types, column_target_tables, obj_keys} where columns is
    {user_col_idx: [values]}.
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return []

    root_eb = _elem_bytes(root_hdr)
    if root_eb < 1 or root_hdr["Element count (size)"] < 2:
        return []

    table_refs_off = _read_ref(data, root_offset + 8, 1, root_eb)
    if table_refs_off <= 0 or table_refs_off >= file_size:
        return []

    tr_hdr = _parse_array_header(data, table_refs_off)
    if tr_hdr is None or not tr_hdr["has_refs"]:
        return []
    tr_eb = _elem_bytes(tr_hdr)
    num_tables = tr_hdr["Element count (size)"]

    tables: list[dict[str, Any]] = []

    for t_idx in range(num_tables):
        table_ref = _read_ref(data, table_refs_off + 8, t_idx, tr_eb)
        if table_ref <= 0 or table_ref >= file_size:
            continue

        t_hdr = _parse_array_header(data, table_ref)
        if t_hdr is None or not t_hdr["has_refs"] or t_hdr["Element count (size)"] < 3:
            continue
        t_eb = _elem_bytes(t_hdr)

        cluster_root_ref = _read_ref(data, table_ref + 8, 2, t_eb)
        if cluster_root_ref <= 0 or cluster_root_ref >= file_size:
            continue

        col_names = _extract_column_names(data, table_ref, t_eb, file_size)
        col_infos = _extract_column_info(data, table_ref, t_eb, file_size)
        if not col_infos:
            continue
        col_infos_by_idx = sorted(col_infos, key=lambda info: info["user_col_idx"])
        col_type_names = []
        for info in col_infos_by_idx:
            base_type = _REALM_COL_TYPES.get(info["type_code"], f"type_{info['type_code']}")
            # Dictionary is a ColumnAttr bit on top of a base type_code (usually
            # Mixed), not its own type_code -- without this, a Dictionary<K,V>
            # column is unlabelled and looks identical to a plain Mixed column
            # in the Schema tab. Values are always Mixed (dictionary.cpp); the
            # key type comes from the spec's m_types array (see
            # _extract_column_info) and is shown when it was readable.
            if info["is_dictionary"]:
                key_type_code = info.get("dictionary_key_type")
                key_type_name = (
                    _REALM_COL_TYPES.get(key_type_code, f"type_{key_type_code}")
                    if key_type_code is not None else "?"
                )
                col_type_names.append(f"dictionary<{key_type_name}, mixed>")
            else:
                col_type_names.append(base_type)
        col_target_tables: list[str | None] = [None] * len(col_infos_by_idx)
        if table_key_map and any(info["type_code"] in (12, 13) for info in col_infos_by_idx):
            opposite_keys = _read_opposite_table_keys(data, table_ref, t_eb, file_size)
            if opposite_keys:
                for pos, info in enumerate(col_infos_by_idx):
                    if info["type_code"] not in (12, 13):  # Link, LinkList
                        continue
                    idx = info["col_index"]
                    if idx >= len(opposite_keys):
                        continue
                    tk = opposite_keys[idx]
                    if tk is None or tk == _TABLE_KEY_NULL:
                        continue
                    col_target_tables[pos] = table_key_map.get(int(tk))
        key_map: dict[int, dict[str, Any]] = {info["cluster_idx"]: info for info in col_infos}

        leaves = _walk_cluster_leaves(data, cluster_root_ref, file_size)
        if not leaves:
            continue

        columns: dict[int, list[Any]] = {info["user_col_idx"]: [] for info in col_infos}
        obj_keys: list[Any] = []
        row_count_total = 0
        row_count_estimated = False

        for leaf_ref, key_offset in leaves:
            leaf_hdr = _parse_array_header(data, leaf_ref)
            if leaf_hdr is None or not leaf_hdr["has_refs"]:
                continue
            leaf_eb = _elem_bytes(leaf_hdr)
            num_cluster = leaf_hdr["Element count (size)"]

            leaf_row_count, leaf_local_keys = _read_cluster_key_info(
                data, leaf_ref, leaf_eb, file_size
            )
            if leaf_row_count is None:
                row_count_estimated = True
                leaf_row_count = _derive_row_count(
                    data, leaf_ref, num_cluster, leaf_eb, file_size
                ) or 0

            for c_idx in range(1, num_cluster):
                col_info = key_map.get(c_idx)
                if col_info is None:
                    continue  # BackLink or otherwise-unmapped cluster slot
                col_ref = _read_ref(data, leaf_ref + 8, c_idx, leaf_eb)
                values: list[Any] | None
                if col_ref <= 0 or col_ref >= file_size:
                    values = None
                else:
                    values = _decode_column_values(data, col_ref, file_size, col_info)
                if values is None:
                    values = [None] * leaf_row_count
                elif len(values) < leaf_row_count:
                    values = values + [None] * (leaf_row_count - len(values))
                elif len(values) > leaf_row_count:
                    values = values[:leaf_row_count]
                columns[col_info["user_col_idx"]].extend(values)

            if leaf_local_keys is not None:
                obj_keys.extend(key_offset + k for k in leaf_local_keys)
            else:
                obj_keys.extend([None] * leaf_row_count)
            row_count_total += leaf_row_count

        tables.append(
            {
                "name": schema[t_idx] if t_idx < len(schema) else f"table[{t_idx}]",
                "row_count": row_count_total,
                "row_count_estimated": row_count_estimated,
                "columns": columns,
                "column_names": col_names,
                "column_types": col_type_names,
                "column_target_tables": col_target_tables,
                "obj_keys": obj_keys,
            }
        )

    return tables


# ---------------------------------------------------------------------------
# String scanner
# ---------------------------------------------------------------------------

# Matches runs of printable ASCII and UTF-8 2-/3-byte sequences (Latin, Greek, …).
# This surfaces human-readable content stored in Data Arrays without requiring
# full B+ tree traversal or column-type knowledge.
_STRING_RUN = re.compile(
    rb"(?:[\x20-\x7E]|[\xC2-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}){8,}"
)


def _scan_strings(data: bytes, min_len: int = 20) -> list[str]:
    """Return unique printable strings (ASCII + UTF-8) found in *data*."""
    results: list[str] = []
    seen: set[str] = set()
    for m in _STRING_RUN.finditer(data):
        try:
            s = m.group().decode("utf-8", errors="replace").strip()
        except Exception:
            continue
        if len(s) >= min_len and s not in seen:
            seen.add(s)
            results.append(s)
    return results


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class RealmParser(AbstractParser):
    SUPPORTED_EXTENSIONS = [".realm"]
    DISPLAY_NAME = "Realm Database"
    SUPPORTS_PASSWORD = True

    def can_parse(self, path: str, peek_bytes: bytes) -> bool:
        if len(peek_bytes) >= _HEADER_SIZE and peek_bytes[16:20] == _MNEMONIC:
            return True
        return self._ext_match(path)

    # Cap for the hex-preview panel; full file is read separately for structure analysis
    _HEX_PREVIEW_BYTES = 1024 * 256  # 256 KB

    def parse(self, node: VFSNode, vfs: VFS, password: str | None = None) -> ParseResult:
        # Read the full file so columns near the end of large Realm files are not missed.
        # A separate 256 KB slice is kept for the HexViewer tab.
        with vfs.open(node) as src:
            full_data = src.read()

        if password is not None:
            # Explicit "Open as Realm DB (Encrypted)…" path only -- the normal
            # open flow never passes a password, since a header that doesn't
            # decode is equally consistent with "encrypted" and "corrupt/
            # non-standard", and only the explicit action means the caller
            # actually has a key to try (see WrongPasswordError below for the
            # retry loop that action drives).
            from crush.core.realm_crypto import decrypt_realm_file, parse_hex_key

            key = parse_hex_key(password)
            full_data = decrypt_realm_file(full_data, key)
            if len(full_data) < _HEADER_SIZE or full_data[16:20] != _MNEMONIC:
                from crush.core.passwords import WrongPasswordError

                raise WrongPasswordError(
                    "Decrypted data doesn't look like a Realm file (wrong key?)"
                )

        # Not node.size: after decryption full_data is the plaintext buffer,
        # shorter than the on-disk encrypted file (metadata pages stripped
        # out) -- every offset bounds-check below must be against the
        # buffer that's actually being read, not the physical file size.
        file_size = len(full_data)

        preview = full_data[: self._HEX_PREVIEW_BYTES]

        header_info = _parse_realm_header(full_data)

        top_refs: dict[str, Any] = {}
        schema: list[str] = []
        inactive_schema: list[str] = []
        inactive_ref_idx: int = 0
        active_idx = 0

        if header_info:
            top_ref0_val = int.from_bytes(full_data[0:8], "little")
            top_ref1_val = int.from_bytes(full_data[8:16], "little")
            active_idx = header_info["Active top reference"]

            hdr0 = _parse_array_header(full_data, top_ref0_val)
            hdr1 = _parse_array_header(full_data, top_ref1_val)
            children0 = _extract_root_children(full_data, top_ref0_val, file_size)
            children1 = _extract_root_children(full_data, top_ref1_val, file_size)

            top_refs = {
                "top_ref_0": {
                    "offset": top_ref0_val,
                    "active": active_idx == 0,
                    "array_header": hdr0,
                    "children": children0,
                },
                "top_ref_1": {
                    "offset": top_ref1_val,
                    "active": active_idx == 1,
                    "array_header": hdr1,
                    "children": children1,
                },
                "active_index": active_idx,
            }

            active_offset = top_ref1_val if active_idx == 1 else top_ref0_val
            inactive_offset = top_ref0_val if active_idx == 1 else top_ref1_val
            inactive_ref_idx = 0 if active_idx == 1 else 1
            schema = _extract_schema(full_data, active_offset, file_size)
            inactive_schema = _extract_schema(full_data, inactive_offset, file_size)

        strings = _scan_strings(full_data)

        tables: list[dict[str, Any]] = []
        if header_info and schema:
            table_key_map = _build_table_key_map(full_data, active_offset, schema, file_size)
            tables = _extract_table_data(
                full_data, active_offset, schema, file_size, table_key_map
            )

        inactive_tables: list[dict[str, Any]] = []
        if header_info and inactive_schema:
            inactive_table_key_map = _build_table_key_map(
                full_data, inactive_offset, inactive_schema, file_size
            )
            inactive_tables = _extract_table_data(
                full_data, inactive_offset, inactive_schema, file_size, inactive_table_key_map
            )

        # Inject schema-level diff into top_refs so the viewer can display it.
        if top_refs and (schema or inactive_schema):
            active_set = set(schema)
            inactive_set = set(inactive_schema)
            active_rows = {t["name"]: t.get("row_count", 0) for t in tables}
            inactive_rows = {t["name"]: t.get("row_count", 0) for t in inactive_tables}
            changed: dict[str, str] = {}
            for name in active_set & inactive_set:
                ar = active_rows.get(name, 0) or 0
                ir = inactive_rows.get(name, 0) or 0
                if ar != ir:
                    changed[name] = f"active={ar}  vs  inactive={ir}"
            top_refs["schema_diff"] = {
                "only_in_active": sorted(active_set - inactive_set),
                "only_in_inactive": sorted(inactive_set - active_set),
                "row_count_changed": changed,
            }

        # Free-list extraction from both refs — merged with source tagging.
        freed_blocks: list[dict[str, Any]] = []
        if header_info:
            active_fl  = _extract_free_list(full_data, active_offset,   file_size)
            inactive_fl = _extract_free_list(full_data, inactive_offset, file_size)
            # Merge: prefer the entry object from whichever ref has it;
            # "both" wins over individual, active-only appears last (most recently freed)
            seen: dict[tuple[int, int], dict[str, Any]] = {}
            for entry in inactive_fl:
                k = (entry["offset"], entry["size"])
                entry["source"] = "inactive"
                seen[k] = entry
            for entry in active_fl:
                k = (entry["offset"], entry["size"])
                if k in seen:
                    seen[k] = dict(seen[k])
                    seen[k]["source"] = "both"
                else:
                    entry["source"] = "active"
                    seen[k] = entry
            freed_blocks = sorted(seen.values(), key=lambda e: e["offset"])

        data: dict[str, Any] = {
            "header": header_info,
            "preview": preview,
            "top_refs": top_refs,
            "schema": schema,
            "tables": tables,
            "inactive_schema": inactive_schema,
            "inactive_tables": inactive_tables,
            "inactive_ref_index": inactive_ref_idx if header_info else None,
            "strings": strings,
            "freed_blocks": freed_blocks,
        }

        meta: dict[str, Any] = {
            "Format": "Realm Database",
            "File size": f"{node.size:,} B",
        }
        if password is not None:
            meta["Encrypted"] = "Yes (AES-256, key supplied)"
            meta["Decrypted size"] = f"{file_size:,} B"
        if header_info:
            meta["Header mnemonic"] = header_info.get("Mnemonic", "?")
            meta["File format"] = (
                f"{header_info['File format (top ref 0)']}/"
                f"{header_info['File format (top ref 1)']}"
            )
            meta["Active top ref"] = str(active_idx)
            if schema:
                meta["Tables found"] = str(len(schema))
        else:
            meta["Header"] = "Not detected (corrupt or non-standard)"
            meta["Possibly Encrypted"] = "Try Open as → Realm DB (Encrypted)…"

        text_parts: list[str] = []
        for t in tables:
            for vals in t.get("columns", {}).values():
                for v in vals:
                    if isinstance(v, str) and v.strip() and not v.startswith("<blob"):
                        text_parts.append(v)
        text_parts.extend(strings[:500])

        return ParseResult(
            viewer_type="realm",
            data=data,
            metadata=meta,
            text_index=" ".join(text_parts[:2000]),
        )


# ---------------------------------------------------------------------------
# iLEAPP entry point (added during vendoring; not part of the upstream file)
# ---------------------------------------------------------------------------
def parse_realm_file(path):
    """Parse an unencrypted Realm file at ``path``.

    Returns a dict with 'active' and 'inactive' (deleted/older schema) sections,
    each mapping a table name to {'column_names', 'column_types', 'columns',
    'row_count'}. 'columns' is keyed by positional index; column_names[i] gives
    the property name for column i. Returns {'header': None, ...} when the file
    is not a decodable (e.g. encrypted or corrupt) Realm file.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    file_size = len(data)
    header = _parse_realm_header(data)
    result = {"header": header, "active": {}, "inactive": {}}
    if not header:
        return result
    top0 = int.from_bytes(data[0:8], "little")
    top1 = int.from_bytes(data[8:16], "little")
    active_index = header["Active top reference"]
    active_off = top1 if active_index == 1 else top0
    inactive_off = top0 if active_index == 1 else top1
    for label, offset in (("active", active_off), ("inactive", inactive_off)):
        schema = _extract_schema(data, offset, file_size)
        if not schema:
            continue
        key_map = _build_table_key_map(data, offset, schema, file_size)
        for table in _extract_table_data(data, offset, schema, file_size, key_map):
            result[label][table["name"]] = {
                "column_names": table.get("column_names", []),
                "column_types": table.get("column_types", []),
                "columns": table.get("columns", {}),
                "row_count": table.get("row_count", 0),
            }
    return result


def realm_rows(path, class_name, section="active"):
    """Yield each row of ``class_name`` as a {column_name: value} dict.

    Convenience wrapper over parse_realm_file() for iLEAPP artifacts. ``section``
    is 'active' (live objects) or 'inactive' (the other top-ref: older/removed
    schema state). Missing table or file yields nothing.
    """
    table = parse_realm_file(path).get(section, {}).get(class_name)
    if not table:
        return
    names = table["column_names"]
    columns = table["columns"]
    row_count = table["row_count"]
    for i in range(row_count):
        row = {}
        for j, name in enumerate(names):
            values = columns.get(j)
            row[name] = values[i] if values is not None and i < len(values) else None
        yield row
