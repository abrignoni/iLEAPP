# ---------------------------------------------------------------------------
# Vendored into iLEAPP from crush-forensics (github.com/kalink0/crush-forensics)
# by Marco Neumann (kalink0), Apache-2.0, unchanged except:
#   * upstream commit fc280180f1d592aecdb53e0c90e31d9629942e65 (2026-09-02, pre-Cluster row support).
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
# not-an-iterable / no-member / import-error false positives, and two
# possibly-used-before-assignment on the per-top-ref format variables, which
# are assigned and used under the same `if header_info:` condition that
# pylint does not correlate). Do not add a
# blanket disable like this to iLEAPP's own artifact code.
# pylint: disable=unused-argument,broad-exception-caught,not-an-iterable,no-member,import-error,possibly-used-before-assignment
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
import os
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

# Realm's "streaming form" (alloc_slab.hpp/.cpp SlabAlloc::is_file_on_streaming_form
# / StreamingFooter, verified against realm-core v5.23.9 source): Group::write()
# — used by e.g. Realm Studio's file-export feature, not the normal
# SharedGroup-driven form an app leaves on disk — writes top_ref[0] as this
# sentinel with the select-bit flag left unset, and puts the real top ref in a
# 16-byte footer at the very end of the file (8 bytes top ref, then 8 bytes
# magic cookie). See issue #55 follow-up: a streaming-form file was silently
# decoding to schema: [] because top_ref[0]'s literal value (the sentinel) was
# being read as an offset.
_STREAMING_SENTINEL = 0xFFFFFFFFFFFFFFFF
_STREAMING_FOOTER_MAGIC = 0x3034125237E526C8

# File format 10 introduced the Cluster/ClusterTree row layout this module's
# row/table decoders are written against; older formats use a structurally
# different layout they can't read. See issue #55.
_MIN_CLUSTER_FORMAT_VERSION = 10

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


def _resolve_streaming_form(
    data: bytes, top_ref0: int, active_idx: int,
) -> dict[str, Any] | None:
    """Detect and resolve Realm's "streaming form" top ref, if this file is one.

    Only meaningful when active_idx == 0 (slot_selector == 0) and top_ref0 is
    the sentinel — a streaming file has no second/inactive top ref at all
    (SlabAlloc::init_streaming_header sets top_ref[1]=0, format[1]=0, so
    top_ref1 is not a real alternative version, just padding).

    Returns None when the file is not in streaming form. Otherwise returns
    {"top_ref": int | None, "footer_valid": bool} — footer_valid is False
    when the file is too short for a 16-byte footer or the magic cookie
    doesn't match (corrupt/truncated), which must not be treated the same
    as "zero tables" (see feedback_explicit_unsupported_marking).
    """
    if not (active_idx == 0 and top_ref0 == _STREAMING_SENTINEL):
        return None
    if len(data) < _HEADER_SIZE + 16:
        return {"top_ref": None, "footer_valid": False}
    footer = data[-16:]
    top_ref = int.from_bytes(footer[0:8], "little")
    magic = int.from_bytes(footer[8:16], "little")
    if magic != _STREAMING_FOOTER_MAGIC:
        return {"top_ref": None, "footer_valid": False}
    return {"top_ref": top_ref, "footer_valid": True}


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
    """Extract class/table names from the Group's table-names array
    (m_table_names, group.hpp: child[0] of the Group top array).

    B+ tree path: root_offset → Group top Reference Array → child[0] →
    m_table_names array.

    m_table_names is `ArrayStringShort`-only in current realm-core (format
    10+), but pre-rewrite realm-core (format 9 and earlier) declares it as
    the full polymorphic `ArrayString`, which can also use the
    SmallBlobs/BigBlobs on-disk forms. Dispatching through
    _read_array_string_or_binary (the same decoder used for real
    String/Binary columns) handles all three forms instead of assuming the
    inline one — see issue #55.
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

    raw_names = _read_array_string_or_binary(
        data, schema_offset, file_size, is_string=True, nullable=False
    )
    if not raw_names:
        return []
    return [name for name in raw_names if isinstance(name, str) and name]


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

    # A LinkList/Set<Link>'s elements are NOT the same on-disk shape as a
    # top-level Link column's own cluster-slot value: the +1/0=null "adj"
    # trick (array_key.hpp, ArrayKeyBase<1>) exists specifically to let a
    # ref-shaped cluster slot distinguish "empty" from "target ObjKey 0" --
    # inside a LinkList's own dedicated BPlusTree<ObjKey> there is no such
    # ambiguity, so elements are plain 0-based ObjKeys with no adjustment
    # (mirrors the pre-Cluster LinkList finding: link_view.hpp's per-element
    # storage is unadjusted even though LinkColumnBase's own is). Routing
    # element_type==12 through _decode_column_values would wrongly apply
    # the single-Link decoder's -1/null-at-0 logic here -- confirmed wrong
    # against a real realm-js-produced file (issue #55 follow-up testing).
    is_link_element = element_type == 12

    results: list[list[Any]] = []
    for i in range(count):
        row_ref = _read_ref(data, col_ref + 8, i, eb)
        if row_ref <= 0 or row_ref >= file_size:
            results.append([])
            continue
        values: list[Any] = []
        for leaf_ref, _off in _walk_bplustree_leaves(data, row_ref, file_size):
            if is_link_element:
                leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
            else:
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
) -> list[int | None] | None:
    """Parse a flat, non-nullable Realm scalar array (ArrayInteger / boolean
    bit-packed / any plain has_refs=False integer array — also reused as the
    generic reader for colkeys, type codes, offsets, and key arrays).

        width=1, scheme=0  → 1 bit per row, returned as plain int (0/1) --
          width is a storage-size detail (Realm sizes an array from the
          largest value it ever held), not the column's declared type, so
          an Int column can legitimately end up 1-bit wide too. Callers
          that want real Bool semantics convert explicitly themselves
          (see type_code == 1 in _decode_column_values /
          _decode_pre_cluster_column_values) -- this function never
          decides that on the caller's behalf (issue #55: a 1-bit-wide
          Int column was decoding as True/False, found on a real file).
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
            # Width is a storage detail, not the column's declared type --
            # Realm sizes an integer array from the largest value it has
            # ever had to hold, so an Int column whose values all happen
            # to fit in one bit gets a 1-bit array too. Returning bool()
            # here unconditionally used to make every 1-bit-wide Int
            # column decode as True/False instead of 1/0 (found on a real
            # Houseparty app file, issue #55 -- e.g. a minute-counter
            # column silently becoming "True"). Callers that actually want
            # bool (the real Bool column dispatch) already wrap the
            # result in bool() themselves; this stays a plain int so every
            # *other* caller isn't silently mistyped.
            result: list[int | None] = []
            for i in range(count):
                byte_i, bit_i = divmod(i, 8)
                if byte_i < len(payload):
                    result.append((payload[byte_i] >> bit_i) & 1)
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
) -> list[bytes | str | None] | None:
    """Decode a Realm ArrayFixedBytes[Null] leaf: elements are packed in
    blocks of 8, with 1 extra null-bitvector byte prefixing each block
    (array_fixed_bytes.hpp: Pos::get_pos/is_null, s_block_size). Used for
    ObjectId (elem_size=12) and UUID (elem_size=16); nullability is encoded
    the same way regardless of whether the column itself is nullable.
    Returns raw per-element bytes, `None` for a genuine null (the
    null-bitvector bit set), or a "<...>" marker string when the payload
    is simply too short to hold this element (truncated/corrupt data) --
    that case must not look like a real null, so callers must not blindly
    treat every non-bytes entry as one; they pass the marker through as-is.
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
    results: list[bytes | str | None] = []
    truncated = "<fixed_bytes: truncated>"
    for i in range(n):
        block_idx, offset = divmod(i, 8)
        base = block_idx * block_size
        if base >= len(payload):
            results.append(truncated)
            continue
        bitvec = payload[base]
        if bitvec & (1 << offset):
            results.append(None)
            continue
        start = base + 1 + offset * elem_size
        val = payload[start : start + elem_size]
        results.append(val if len(val) == elem_size else truncated)
    return results


def _format_uuid(raw: bytes) -> str:
    try:
        return str(_uuid_mod.UUID(bytes=raw))
    except Exception:
        return raw.hex()


def _decode_bid(raw_int: int, total_bits: int) -> str:
    """Decode an IEEE 754-2008 BID (binary integer decimal) value — the
    encoding Realm's Decimal128 uses (array_decimal128.hpp: Bid64/Bid128).

    Per IEEE 754-2008 §3.5.2, the g_width bits after the sign are NOT laid
    out as "5-bit combination field, then exponent-continuation field"
    contiguously -- two earlier versions of this function assumed that and
    were both wrong. The real layout (confirmed 2026-09-01 by brute-force
    solving against two real realm-js-produced Bid64 values after neither
    prior version reproduced them): combination-field bits G0 and G1 sit at
    the very top (right after sign), then the exponent-continuation field,
    then combination-field bits G2/G3/G4 sit at the *bottom*, immediately
    adjacent to the trailing significand T -- i.e. G0G1 and G2G3G4 are not
    contiguous with each other. So in the common case (G0G1 != 11):
    `biased_exponent = g >> 3` (the top g_width-3 bits, i.e. G0G1 directly
    followed by the continuation field) and the coefficient's top 3 bits
    are simply `g & 0b111` (G2G3G4, concatenated with T) -- no separate
    "MSD lookup" needed. When G0G1 == 11 (not the inf/nan case), the
    exponent is `(g >> 1) & 0x3FF` and the coefficient's top nibble is the
    fixed prefix "100" + G4 (giving MSD 8 or 9).

    Verified: decoded two real Bid64 values from a realm-js-produced file
    ("12345.6789" and "-99.99", format 24) byte-for-byte against the SDK's
    own Decimal128.toString() -- both earlier versions produced garbage
    (e.g. "3.377699843984661E-303" for the first), this version reproduces
    both exactly. Also verified against an MSD-8/9 value
    ("89999999999999.5") and a 34-significant-digit value forcing the full
    Bid128 (16-byte) form. The *storage* format (word order, low/high
    word placement for Bid128) is confirmed from Realm Core source
    separately (see _read_array_mixed).
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

    top4 = (g >> (g_width - 4)) & 0b1111  # G0 G1 G2 G3
    if top4 == 0b1111:
        g4 = (g >> (g_width - 5)) & 1
        if g4:
            return "NaN"
        return "-Infinity" if sign else "Infinity"

    top2 = g >> (g_width - 2)  # G0 G1
    if top2 != 0b11:
        biased_exponent = g >> 3
        msd = g & 0b111
    else:
        biased_exponent = (g >> 1) & ((1 << (g_width - 3)) - 1)
        g4 = g & 1
        msd = 8 | g4

    coefficient = msd * (1 << t_width) + t
    exponent = biased_exponent - bias

    # decimal128's coefficient needs up to 34 significant digits -- Python's
    # ambient decimal context defaults to 28 and .scaleb() is a
    # context-rounded operation, which silently truncated Bid128 values
    # past 28 digits until this was caught against a real 34-digit
    # realm-js-produced value. Build the Decimal directly from its
    # (sign, digits, exponent) tuple instead, which is exact and ignores
    # context precision entirely.
    digits = tuple(int(d) for d in str(coefficient)) if coefficient else (0,)
    value = decimal.Decimal((sign, digits, exponent))
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

        # By this point `val` is non-zero (the genuine-null case was already
        # handled by `if not val` above), so a payload helper returning None
        # from here on can only mean its index couldn't be resolved (a
        # corrupt/out-of-range payload_idx) -- never a legitimate null. Each
        # branch below must say so explicitly rather than silently emitting
        # None, which would be indistinguishable from a real null value.
        missing = f"<mixed: unresolved payload index for type_{data_type}>"

        if data_type == 0:  # Int
            if payload_idx_flag == 0:
                results.append(payload_val)
            else:
                iv = int_payload(payload_val)
                results.append(iv if iv is not None else missing)
        elif data_type == 1:  # Bool
            results.append(payload_val != 0)
        elif data_type == 9:  # Float
            iv = int_payload(payload_val)
            results.append(
                struct.unpack("<f", (iv & 0xFFFFFFFF).to_bytes(4, "little"))[0]
                if iv is not None else missing
            )
        elif data_type == 10:  # Double
            iv = int_payload(payload_val)
            results.append(
                struct.unpack("<d", (iv & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little"))[0]
                if iv is not None else missing
            )
        elif data_type == 2:  # String
            raw = string_payload(payload_val)
            results.append(raw.decode("utf-8", errors="replace") if raw is not None else missing)
        elif data_type == 4:  # Binary
            raw = string_payload(payload_val)
            results.append(raw if raw is not None else missing)
        elif data_type == 8:  # Timestamp
            pair = pair_payload(payload_val)
            results.append(
                _decode_timestamp(int(pair[0] + (pair[1] / 1_000_000_000 if pair[1] else 0)))
                if pair else missing
            )
        elif data_type == 15:  # ObjectId
            raw = string_payload(payload_val)
            results.append(raw.hex() if raw is not None else missing)
        elif data_type == 11:  # Decimal128
            pair = pair_payload(payload_val)
            if pair:
                low, high = pair[0] & 0xFFFFFFFFFFFFFFFF, pair[1] & 0xFFFFFFFFFFFFFFFF
                results.append(_decode_bid(low | (high << 64), 128))
            else:
                results.append(missing)
        elif data_type == 12:  # Link
            iv = int_payload(payload_val)
            results.append(iv if iv is not None else missing)
        elif data_type == 16:  # TypedLink
            pair = pair_payload(payload_val)
            if pair:
                results.append(f"Obj(table_key={pair[0]}, key={pair[1]})")
            else:
                results.append(missing)
        elif data_type == 17:  # UUID
            raw = string_payload(payload_val)
            results.append(_format_uuid(raw) if raw is not None else missing)
        elif data_type in (19, 20):  # List, Set (elements are always Mixed once nested)
            r = ref_payload(payload_val)
            if r is None:
                results.append(missing)
            elif _nest_depth >= _MIXED_MAX_NEST_DEPTH:
                results.append(f"<mixed: nesting depth limit ({_MIXED_MAX_NEST_DEPTH}) reached>")
            else:
                results.append(_read_collection_at_ref(data, r, file_size, _nest_depth + 1))
        elif data_type == 21:  # Dictionary (always String-keyed -- see docstring)
            r = ref_payload(payload_val)
            if r is None:
                results.append(missing)
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

    # keys/values are two independently-walked BPlusTrees paired by index
    # position (see docstring above) -- if they come out mismatched in
    # length (corruption, a partially-failed leaf decode), that's a real
    # structural problem and must not look like this key's value simply
    # decoded to a legitimate null.
    return {
        (key if key is not None else f"<null key {j}>"): (
            values[j] if j < len(values) else "<dictionary: value tree shorter than keys tree>"
        )
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
        return None if raw is None else [v.hex() if isinstance(v, bytes) else v for v in raw]
    if type_code == 17:  # UUID
        raw = _read_array_fixed_bytes(data, col_ref, file_size, 16)
        return None if raw is None else [_format_uuid(v) if isinstance(v, bytes) else v for v in raw]
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
) -> tuple[list[dict[str, Any]], str | None]:
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

    Returns (tables, reason) -- tables is a list of dicts {name, row_count,
    columns, column_names, column_types, column_target_tables, obj_keys}
    (columns is {user_col_idx: [values]}); reason is None only when every
    table in *schema* decoded, otherwise a "class_name: specific cause"
    string per failed table (semicolon-joined) -- mirrors the pre-Cluster
    path's own (result, reason) contract (see
    _extract_pre_cluster_tables_data) so a genuine structural failure here
    is never left as a silent, unexplained empty table list either
    (feedback_explicit_unsupported_marking).
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return [], "Group top array is malformed or has no references"

    root_eb = _elem_bytes(root_hdr)
    if root_eb < 1 or root_hdr["Element count (size)"] < 2:
        return [], "Group top array has no table-refs slot (fewer than 2 children)"

    table_refs_off = _read_ref(data, root_offset + 8, 1, root_eb)
    if table_refs_off <= 0 or table_refs_off >= file_size:
        return [], "Table-refs reference is invalid or points outside the file"

    tr_hdr = _parse_array_header(data, table_refs_off)
    if tr_hdr is None or not tr_hdr["has_refs"]:
        return [], "Table-refs array is malformed or has no references"
    tr_eb = _elem_bytes(tr_hdr)
    num_tables = tr_hdr["Element count (size)"]

    tables: list[dict[str, Any]] = []
    failures: list[str] = []

    for t_idx in range(num_tables):
        table_name = schema[t_idx] if t_idx < len(schema) else f"table[{t_idx}]"
        table_ref = _read_ref(data, table_refs_off + 8, t_idx, tr_eb)
        if table_ref <= 0 or table_ref >= file_size:
            failures.append(f"{table_name}: table reference is invalid or points outside the file")
            continue

        t_hdr = _parse_array_header(data, table_ref)
        if t_hdr is None or not t_hdr["has_refs"] or t_hdr["Element count (size)"] < 3:
            failures.append(
                f"{table_name}: Table top array is malformed or missing its ClusterTree slot"
            )
            continue
        t_eb = _elem_bytes(t_hdr)

        cluster_root_ref = _read_ref(data, table_ref + 8, 2, t_eb)
        if cluster_root_ref <= 0 or cluster_root_ref >= file_size:
            failures.append(f"{table_name}: ClusterTree reference is invalid or points outside the file")
            continue

        col_names = _extract_column_names(data, table_ref, t_eb, file_size)
        col_infos = _extract_column_info(data, table_ref, t_eb, file_size)
        if not col_infos:
            failures.append(f"{table_name}: Spec/colkeys array has no columns (empty or malformed)")
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
            failures.append(f"{table_name}: ClusterTree root is malformed or has no leaves")
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
                "name": table_name,
                "row_count": row_count_total,
                "row_count_estimated": row_count_estimated,
                "columns": columns,
                "column_names": col_names,
                "column_types": col_type_names,
                "column_target_tables": col_target_tables,
                "obj_keys": obj_keys,
            }
        )

    if num_tables == 0 and schema:
        # Class names resolved from Group.m_table_names, but the table-refs
        # array itself is empty -- a real mismatch, not "nothing to report".
        return [], f"Table-refs array has 0 entries, but {len(schema)} class name(s) in schema"
    return tables, ("; ".join(failures) if failures else None)


# ---------------------------------------------------------------------------
# Pre-Cluster (file format < 10) row/table data — old Table/Spec layout
# ---------------------------------------------------------------------------
#
# Everything above this point in the file (Cluster/ClusterTree, ColKey/Spec)
# is written against the storage layout introduced at file format 10
# (realm-core v6.0.0, ~2019). Files at format 9 and earlier (last written by
# realm-core <= v5.23.9 / realm-java 5.6.0-6.1.0) used a structurally
# different, older layout: each Table has its own Spec (types/names/attrs
# arrays, table.hpp slot 0/1 = spec ref/columns ref) and each column is an
# independent top-level B+-tree, rather than rows being grouped into
# Clusters. Confirmed against the real v5.23.9 source (table.hpp, spec.hpp,
# column_type.hpp, bptree.hpp, column_timestamp.hpp, column_mixed.hpp,
# column_string_enum.hpp, column_linkbase.hpp, column_linklist.hpp) — see
# issue #55. The low-level Array primitives (leaf formats for
# String/Binary/Bool/Float/Double/Int) are unchanged across both eras and
# reused as-is; only the row/column aggregation structure is new here.

# Old ColumnType (column_type.hpp @ v5.23.9) -- NOT the same numeric meanings
# as the modern _REALM_COL_TYPES above for several values (3/5/7/11 differ:
# e.g. 11 is Reserved4/unused here vs. decimal128 in the modern enum).
_PRE_CLUSTER_COL_TYPES: dict[int, str] = {
    0: "int",
    1: "bool",
    2: "string",
    3: "string_enum",
    4: "data",
    5: "table",   # subtable
    6: "mixed",
    7: "date",    # OldDateTime
    8: "date",    # Timestamp
    9: "float",
    10: "double",
    12: "link",
    13: "linklist",
    14: "backlink",
}

# Old ColumnAttr (column_type.hpp @ v5.23.9): a plain bitmask read directly
# from Spec's m_attr array -- unlike modern ColKey, it is not bit-packed
# into a key.
_PRE_CLUSTER_COL_ATTR_INDEXED = 0x01
_PRE_CLUSTER_COL_ATTR_NULLABLE = 0x10


def _extract_pre_cluster_spec(
    data: bytes, spec_ref: int, file_size: int,
) -> list[dict[str, Any]] | None:
    """Decode a pre-Cluster Spec array (spec.hpp @ v5.23.9): m_top slots
    0=m_types (ArrayInteger, one old ColumnType per column), 1=m_names
    (ArrayString), 2=m_attr (ArrayInteger, one ColumnAttr bitmask per
    column), 3=m_subspecs (optional). m_subspecs is resolved here too
    (spec.cpp get_subspec_ndx_after/get_subspec_entries_for_col_type,
    confirmed against real source, not guessed): a sparse array with 1
    entry for each Table/Link/LinkList column and 2 for each BackLink
    column (origin table + origin column index), indexed by a running
    count over prior columns of those types. For Link/LinkList, the entry
    is a tagged integer (`value >> 1`) giving the target table's index in
    the Group's tables array; for Table (subtable), it's a direct ref to
    the shared nested Spec every row's subtable uses.

    Returns one dict per column: {col_index, name, type_code, nullable,
    indexed, target_table_index, subtable_spec_ref}, or None on failure.
    """
    spec_hdr = _parse_array_header(data, spec_ref)
    if spec_hdr is None or not spec_hdr["has_refs"] or spec_hdr["Element count (size)"] < 3:
        return None
    spec_eb = _elem_bytes(spec_hdr)
    if spec_eb < 1:
        return None

    types_ref = _read_ref(data, spec_ref + 8, 0, spec_eb)
    names_ref = _read_ref(data, spec_ref + 8, 1, spec_eb)
    attr_ref = _read_ref(data, spec_ref + 8, 2, spec_eb)
    if types_ref <= 0 or types_ref >= file_size:
        return None

    types = _read_scalar_leaf(data, types_ref, file_size)
    if not types:
        return None
    names = (
        _read_pre_cluster_string_or_binary(data, names_ref, file_size, is_string=True, nullable=False)
        if 0 < names_ref < file_size else None
    )
    attrs = (
        _read_scalar_leaf(data, attr_ref, file_size)
        if 0 < attr_ref < file_size else None
    )

    # m_subspecs (slot 3, spec.cpp @ v5.23.9): one entry per Table/Link/
    # LinkList column (get_subspec_entries_for_col_type: 1 each), two per
    # BackLink (origin table index + origin column index), zero for
    # everything else -- "sparse", indexed by a running count over prior
    # columns, not by plain column index (Spec::get_subspec_ndx_after).
    subspecs_ref = (
        _read_ref(data, spec_ref + 8, 3, spec_eb) if spec_hdr["Element count (size)"] > 3 else 0
    )
    subspecs = (
        _read_scalar_leaf(data, subspecs_ref, file_size)
        if 0 < subspecs_ref < file_size else None
    )

    # m_enumkeys (slot 4): one ref per StringEnum column, indexed by a
    # running count over *only* prior StringEnum columns (spec.cpp
    # Spec::get_enumkeys_ndx) -- a separate counter from m_subspecs above.
    enumkeys_ref = (
        _read_ref(data, spec_ref + 8, 4, spec_eb) if spec_hdr["Element count (size)"] > 4 else 0
    )
    enumkeys_hdr = _parse_array_header(data, enumkeys_ref) if enumkeys_ref > 0 else None
    enumkeys_eb = _elem_bytes(enumkeys_hdr) if enumkeys_hdr else 0

    columns: list[dict[str, Any]] = []
    subspec_ndx = 0
    enumkeys_ndx = 0
    for i, type_val in enumerate(types):
        if type_val is None:
            continue
        type_code = int(type_val)
        attr_raw = attrs[i] if attrs and i < len(attrs) else None
        attr_val = int(attr_raw) if attr_raw is not None else 0
        col: dict[str, Any] = {
            "col_index": i,
            "name": names[i] if names and i < len(names) else f"column[{i}]",
            "type_code": type_code,
            "nullable": bool(attr_val & _PRE_CLUSTER_COL_ATTR_NULLABLE),
            "indexed": bool(attr_val & _PRE_CLUSTER_COL_ATTR_INDEXED),
            "target_table_index": None,
            "subtable_spec_ref": None,
            "enum_keys_ref": None,
        }
        if type_code in (5, 12, 13) and subspecs is not None and subspec_ndx < len(subspecs):
            raw = subspecs[subspec_ndx]
            if raw is not None:
                raw = int(raw)
                if type_code == 5:  # Table (subtable): direct ref to a nested Spec
                    col["subtable_spec_ref"] = raw
                elif raw & 1:  # Link/LinkList: tagged target-table index (>>1)
                    col["target_table_index"] = raw >> 1
        if type_code == 3 and enumkeys_hdr is not None and enumkeys_eb >= 1:
            col["enum_keys_ref"] = _read_ref(data, enumkeys_ref + 8, enumkeys_ndx, enumkeys_eb)
        if type_code == 5:
            subspec_ndx += 1
        elif type_code in (12, 13):
            subspec_ndx += 1
        elif type_code == 14:
            subspec_ndx += 2
        if type_code == 3:
            enumkeys_ndx += 1
        columns.append(col)
    return columns if columns else None


def _resolve_pre_cluster_column_refs(
    data: bytes, columns_ref: int, spec_columns: list[dict[str, Any]], file_size: int,
) -> dict[int, int]:
    """Map each column's spec index to its ref in the Table's m_columns
    array. m_columns holds one ref per column *plus* a search-index ref
    immediately after any indexed column's own ref (table.hpp: "A search
    index ref always occurs immediately after the ref of the column to
    which the search index belongs") -- so the mapping is not a plain
    1:1 index and has to walk Spec's `indexed` flags in step with it.
    """
    hdr = _parse_array_header(data, columns_ref)
    if hdr is None or not hdr["has_refs"]:
        return {}
    eb = _elem_bytes(hdr)
    if eb < 1:
        return {}

    refs: dict[int, int] = {}
    slot = 0
    for col in spec_columns:
        refs[col["col_index"]] = _read_ref(data, columns_ref + 8, slot, eb)
        slot += 1
        if col["indexed"]:
            slot += 1  # skip this column's search-index ref
    return refs


def _decode_pre_cluster_timestamp_column(
    data: bytes, col_ref: int, file_size: int,
) -> list[str | None] | None:
    """Decode an old-format Timestamp column. Unlike the modern
    ArrayTimestamp cell (a small 2-slot [secs_ref, nanos_ref] array bounded
    by one Cluster leaf's row count), a pre-Cluster TimestampColumn is a
    *table-wide* column: its own top-level ref is still a 2-slot
    [m_seconds root, m_nanoseconds root] array (column_timestamp.hpp), but
    each of those two roots is independently a full B+-tree that can span
    many leaves for a large table -- so each side must be leaf-walked on
    its own rather than assumed to fit in a single leaf.
    """
    hdr = _parse_array_header(data, col_ref)
    if hdr is None or not hdr["has_refs"] or hdr["Element count (size)"] != 2:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None
    secs_root = _read_ref(data, col_ref + 8, 0, eb)
    nanos_root = _read_ref(data, col_ref + 8, 1, eb)

    secs: list[int | None] = []
    if secs_root > 0:
        for leaf_ref, _offset in (_walk_bplustree_leaves(data, secs_root, file_size) or [(secs_root, 0)]):
            leaf_vals = _read_array_int_null(data, leaf_ref, file_size)
            if leaf_vals is None:
                return None
            secs.extend(leaf_vals)

    nanos: list[int] = []
    if nanos_root > 0:
        for leaf_ref, _offset in (_walk_bplustree_leaves(data, nanos_root, file_size) or [(nanos_root, 0)]):
            leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
            if leaf_vals is None:
                return None
            nanos.extend(v if v is not None else 0 for v in leaf_vals)

    result: list[str | None] = []
    for i, s in enumerate(secs):
        if s is None:
            result.append(None)
            continue
        ns = nanos[i] if i < len(nanos) else 0
        result.append(_decode_timestamp(int(s + (ns / 1_000_000_000 if ns else 0))))
    return result


def _read_pre_cluster_medium_string_or_binary(
    data: bytes, ref: int, file_size: int, *, is_string: bool,
) -> list[Any] | None:
    """Decode the pre-Cluster "medium" String/Binary leaf form -- named
    ArrayStringLong for strings, ArrayBinary for binary (array_string_long.hpp
    / array_binary.hpp @ v5.23.9) -- confirmed via source to be genuinely
    different from the modern ArraySmallBlobs this parser's regular
    _read_array_string_or_binary otherwise dispatches to: 2 slots
    [offsets, blob] when the column is non-nullable, 3 slots [offsets, blob,
    nulls] when nullable (nullability is inferred from the array's own slot
    count -- array_string_long.hpp: `m_nullable = (Array::size() == 3)`),
    rather than modern's fixed 3-slot layout regardless of nullability.

    String vs Binary differ in two ways confirmed against source: strings
    store an implicit trailing NUL in the blob (subtracted from the decoded
    length: array_string_long.hpp get()'s `--end`), binary does not
    (array_binary.hpp get(): no such subtraction); and the null-flag sense
    is inverted between the two (`m_nulls.get(ndx) == 0` means NULL for
    strings, but `m_nulls.get(ndx) != 0` means NULL for binary) -- easy to
    get backwards, so kept as two explicit branches rather than one shared
    boolean flip.
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None or not hdr["has_refs"] or hdr["context_flag"]:
        return None
    count = hdr["Element count (size)"]
    if count not in (2, 3):
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None

    offsets_ref = _read_ref(data, ref + 8, 0, eb)
    blob_ref = _read_ref(data, ref + 8, 1, eb)
    nulls_ref = _read_ref(data, ref + 8, 2, eb) if count == 3 else 0

    offsets = _read_uint_array(data, offsets_ref)
    nulls = _read_uint_array(data, nulls_ref) if nulls_ref > 0 else None

    blob_hdr = _parse_array_header(data, blob_ref)
    blob = b""
    if blob_hdr is not None:
        blob_size = blob_hdr["Element count (size)"]
        blob = data[blob_ref + 8 : blob_ref + 8 + blob_size]

    results: list[Any] = []
    prev = 0
    for i, end in enumerate(offsets):
        if nulls is not None and i < len(nulls):
            is_null = (nulls[i] == 0) if is_string else (nulls[i] != 0)
        else:
            is_null = False
        if is_null:
            results.append(None)
            prev = end
            continue
        chunk_end = end - 1 if is_string else end  # strings: discount trailing NUL
        chunk = blob[prev:chunk_end]
        results.append(chunk.decode("utf-8", errors="replace") if is_string else bytes(chunk))
        prev = end
    return results


def _read_pre_cluster_string_or_binary(
    data: bytes, ref: int, file_size: int, *, is_string: bool, nullable: bool,
) -> list[Any] | None:
    """Dispatch a pre-Cluster String/Binary column leaf to the right
    on-disk sub-form. has_refs=False is the inline Short form, confirmed
    identical to the modern one (already reused via _read_array_string_short
    for the issue #55 schema-name fix); has_refs=True + context_flag=True is
    ArrayBigBlobs, whose file (array_blobs_big.hpp) already exists unchanged
    in the v5.23.9 source tree -- reused as-is, though this specific
    boundary condition (context_flag distinguishing BigBlobs from the medium
    form in the *old* era) has not been directly confirmed against a real
    BigBlobs-form old column, unlike the medium form below which was
    verified against real data (issue #55, IFTTT sample). has_refs=True +
    context_flag=False is the medium form (_read_pre_cluster_medium_string_or_binary).
    """
    hdr = _parse_array_header(data, ref)
    if hdr is None:
        return None
    if not hdr["has_refs"]:
        return _read_array_string_short(data, ref, hdr, is_string=is_string, nullable=nullable)
    if hdr["context_flag"]:
        return _read_array_big_blobs(data, ref, hdr, file_size, is_string=is_string)
    return _read_pre_cluster_medium_string_or_binary(data, ref, file_size, is_string=is_string)


def _walk_pre_cluster_int_column(
    data: bytes, col_ref: int, file_size: int,
) -> list[int | None] | None:
    """Walk a plain old-format IntegerColumn's own top-level B+-tree and
    concatenate its leaves (no nullable-sentinel handling -- used for
    Mixed's m_types/m_data sub-columns, which are never themselves null)."""
    if col_ref <= 0 or col_ref >= file_size:
        return None
    leaves = _walk_bplustree_leaves(data, col_ref, file_size)
    if not leaves:
        leaves = [(col_ref, 0)]
    values: list[int | None] = []
    for leaf_ref, _offset in leaves:
        leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
        if leaf_vals is None:
            return None
        values.extend(leaf_vals)
    return values


_U64_MASK = (1 << 64) - 1
_BIT63 = 1 << 63


def _decode_pre_cluster_mixed_column(
    data: bytes, col_ref: int, file_size: int,
) -> list[Any] | None:
    """Decode an old-format Mixed column. Top-array slot assignment
    confirmed against MixedColumn::create() (column_mixed.cpp @ v5.23.8 --
    the exact realm-core version realm-java 6.1.0, the last release the
    issue #55 reporter says wrote format 9, bundled): 0=m_types
    (IntegerColumn of MixedColType), 1=m_data (RefsColumn, tagged --
    get_value() = raw_uint64 >> 1), 2=m_binary_data (one shared
    BinaryColumn holding every row's String/Binary payload, addressed by
    row index), 3=m_timestamp_data (one shared TimestampColumn, same
    addressing).

    Per-type decode of get_value() (column_mixed_tpl.hpp @ v5.23.8):
    Int/IntNeg store the 63-bit magnitude with the sign bit stripped (freed
    up for the tag bit) and OR'd back in for the Neg variant; Double/
    DoubleNeg the same trick then type-punned; Float type-punned from the
    low 32 bits directly (no Neg variant needed -- a 32-bit float's own
    sign bit at bit31 never collides with the tag scheme); String/Binary/
    Timestamp store a row index into the shared sub-column rather than an
    in-place value.

    Table-typed Mixed cells (a subtable value nested inside a Mixed) and
    the reserved/unused mixcol_Mixed(6) tag are not handled -- get_value()
    for those does not use the same tag-shift scheme as everything else
    verified above, and this hasn't been independently confirmed, so they
    surface as a visible "<mixed: unsupported type_N>" marker per cell
    (same precedent as the modern _read_array_mixed's own marker for a
    data_type it doesn't recognise) rather than a guess.
    """
    hdr = _parse_array_header(data, col_ref)
    if hdr is None or not hdr["has_refs"] or hdr["Element count (size)"] < 3:
        return None
    eb = _elem_bytes(hdr)
    if eb < 1:
        return None

    types_ref = _read_ref(data, col_ref + 8, 0, eb)
    data_ref = _read_ref(data, col_ref + 8, 1, eb)
    binary_ref = _read_ref(data, col_ref + 8, 2, eb)
    timestamp_ref = _read_ref(data, col_ref + 8, 3, eb) if hdr["Element count (size)"] > 3 else 0

    types = _walk_pre_cluster_int_column(data, types_ref, file_size)
    raw_data = _walk_pre_cluster_int_column(data, data_ref, file_size)
    if types is None or raw_data is None:
        return None

    binary_rows = (
        _read_pre_cluster_string_or_binary(data, binary_ref, file_size, is_string=False, nullable=False)
        if binary_ref > 0 else None
    )
    timestamp_rows = (
        _decode_pre_cluster_timestamp_column(data, timestamp_ref, file_size)
        if timestamp_ref > 0 else None
    )

    results: list[Any] = []
    for i, t in enumerate(types):
        raw_val = raw_data[i] if i < len(raw_data) else None
        if t is None or raw_val is None:
            results.append(None)
            continue
        mixtype = int(t)
        raw_u64 = int(raw_val) & _U64_MASK
        value = raw_u64 >> 1

        if mixtype == 0:  # Int
            results.append(value)
        elif mixtype == 12:  # IntNeg
            signed_u64 = (value | _BIT63) & _U64_MASK
            results.append(signed_u64 - (1 << 64))
        elif mixtype == 1:  # Bool
            results.append(value != 0)
        elif mixtype == 9:  # Float
            results.append(struct.unpack("<f", struct.pack("<I", value & 0xFFFFFFFF))[0])
        elif mixtype == 10:  # Double (positive)
            results.append(struct.unpack("<d", struct.pack("<Q", value))[0])
        elif mixtype == 11:  # DoubleNeg
            results.append(struct.unpack("<d", struct.pack("<Q", (value | _BIT63) & _U64_MASK))[0])
        elif mixtype == 7:  # OldDateTime
            results.append(_decode_timestamp(value))
        elif mixtype == 8:  # Timestamp -- value is a row index into m_timestamp_data
            if timestamp_rows is not None and value < len(timestamp_rows):
                results.append(timestamp_rows[value])
            else:
                # Distinct from a genuine null entry (which the reader itself
                # would report) -- this is the index resolution failing.
                results.append(f"<mixed: timestamp index {value} out of range>")
        elif mixtype in (2, 4):  # String/Binary -- value is a row index into m_binary_data
            if binary_rows is None or value >= len(binary_rows):
                results.append(f"<mixed: binary index {value} out of range>")
                continue
            chunk = binary_rows[value]
            if chunk is None:
                results.append(None)
            elif mixtype == 2:
                if chunk.endswith(b"\x00"):
                    chunk = chunk[:-1]
                results.append(chunk.decode("utf-8", errors="replace"))
            else:
                results.append(bytes(chunk))
        else:
            results.append(f"<mixed: unsupported type_{mixtype}>")
    return results


def _decode_pre_cluster_string_enum_column(
    data: bytes, col_ref: int, enum_keys_ref: int | None, file_size: int,
) -> list[str | None] | None:
    """Decode a pre-Cluster StringEnum column (column_string_enum.hpp @
    v5.23.9): a shared keys StringColumn (referenced from Spec's
    m_enumkeys, resolved by the caller) holding each unique string once,
    plus a per-row plain integer index into that keys array -- decoded
    the same way as a regular Int column since the index storage itself
    is an ordinary IntegerColumn, not a special leaf format.
    """
    if not enum_keys_ref:
        return None
    keys = _read_pre_cluster_string_or_binary(
        data, enum_keys_ref, file_size, is_string=True, nullable=False
    )
    if keys is None:
        return None

    leaves = _walk_bplustree_leaves(data, col_ref, file_size)
    if not leaves:
        leaves = [(col_ref, 0)]

    indices: list[int | None] = []
    for leaf_ref, _offset in leaves:
        leaf_hdr = _parse_array_header(data, leaf_ref)
        if leaf_hdr is not None and leaf_hdr["width"] == 0:
            indices.extend([0] * leaf_hdr["Element count (size)"])
            continue
        leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
        if leaf_vals is None:
            return None
        indices.extend(leaf_vals)

    results: list[str | None] = []
    for ix in indices:
        if ix is None:
            results.append(None)
        elif 0 <= int(ix) < len(keys):
            results.append(keys[int(ix)])
        else:
            # Distinct from a genuine null row (ix is None, handled above) --
            # this is the index resolution itself failing.
            results.append(f"<string_enum: index {int(ix)} out of range>")
    return results


def _decode_pre_cluster_table_column(
    data: bytes, col_ref: int, file_size: int, subtable_spec_ref: int | None,
) -> list[list[dict[str, Any]]] | None:
    """Decode a pre-Cluster Table-typed (subtable) column. Each row's own
    value in the column's top-level B+-tree is a plain ref: 0 = a
    degenerate/not-yet-materialized empty subtable (table.hpp: "a subtable
    ... always starts out in a degenerate form ... a null 'ref' is
    stored"), otherwise a ref to that row's own m_columns array -- subtable
    rows share one Spec (spec_ref resolved by the caller via
    _extract_pre_cluster_spec's subtable_spec_ref, spec.cpp
    Spec::get_subspec_by_ndx) rather than each row's subtable carrying its
    own independent spec.

    Each row's decoded value is a list of sub-row dicts ({column_name:
    value}), recursively expanded rather than shown as a placeholder --
    same "expand, don't stub out" precedent as _read_array_mixed's nested
    List/Set/Dictionary handling.
    """
    if not subtable_spec_ref:
        return None
    subtable_spec = _extract_pre_cluster_spec(data, subtable_spec_ref, file_size)
    if not subtable_spec:
        return None
    visible = [c for c in subtable_spec if c["type_code"] != 14]

    leaves = _walk_bplustree_leaves(data, col_ref, file_size)
    if not leaves:
        leaves = [(col_ref, 0)]

    refs: list[int] = []
    for leaf_ref, _offset in leaves:
        leaf_hdr = _parse_array_header(data, leaf_ref)
        if leaf_hdr is None or not leaf_hdr["has_refs"]:
            return None
        count = leaf_hdr["Element count (size)"]
        if leaf_hdr["width"] == 0:
            refs.extend([0] * count)
            continue
        eb = _elem_bytes(leaf_hdr)
        if eb < 1:
            return None
        for i in range(count):
            refs.append(_read_ref(data, leaf_ref + 8, i, eb))

    values: list[list[dict[str, Any]]] = []
    for row_ref in refs:
        if row_ref <= 0 or row_ref >= file_size:
            values.append([])
            continue
        sub_col_refs = _resolve_pre_cluster_column_refs(data, row_ref, subtable_spec, file_size)
        sub_columns: dict[int, list[Any]] = {}
        sub_unsupported: list[int] = []
        sub_row_count: int | None = None
        for idx, col in enumerate(visible):
            cref = sub_col_refs.get(col["col_index"], 0)
            vals = _decode_pre_cluster_column_values(data, cref, file_size, col)
            if vals is None:
                sub_unsupported.append(idx)
            sub_columns[idx] = vals if vals is not None else []
            if vals is not None and sub_row_count is None:
                sub_row_count = len(vals)
        n = sub_row_count or 0
        # Same explicit marker as the top-level table decode -- a column
        # this dispatch can't handle yet must not look like an empty/null
        # value once nested inside a nested subtable's rows.
        for idx in sub_unsupported:
            type_name = _PRE_CLUSTER_COL_TYPES.get(
                visible[idx]["type_code"], f"type_{visible[idx]['type_code']}"
            )
            sub_columns[idx] = [f"<unsupported: {type_name}>"] * n
        values.append([
            {
                col["name"]: (sub_columns[idx][r] if r < len(sub_columns[idx]) else None)
                for idx, col in enumerate(visible)
            }
            for r in range(n)
        ])
    return values


def _decode_pre_cluster_linklist_column(
    data: bytes, col_ref: int, file_size: int,
) -> list[list[int]] | None:
    """Decode an old-format LinkList column. Confirmed against source
    (column_linklist.hpp/link_view.hpp @ v5.23.9): the column's own
    top-level B+-tree holds one *ref* per row (0 = empty list, matching the
    modern LinkList shape), each pointing to that row's own flat Array of
    plain 0-based target row indices (LinkView::get() -- no null/+1 encoding
    at this level, unlike single Link columns, since a list element can't
    itself be null).
    """
    leaves = _walk_bplustree_leaves(data, col_ref, file_size)
    if not leaves:
        leaves = [(col_ref, 0)]

    values: list[list[int]] = []
    for leaf_ref, _offset in leaves:
        leaf_hdr = _parse_array_header(data, leaf_ref)
        if leaf_hdr is None or not leaf_hdr["has_refs"]:
            return None
        count = leaf_hdr["Element count (size)"]
        if leaf_hdr["width"] == 0:
            # Realm's all-zero compact encoding: every ref in this leaf is
            # implicitly 0 (empty list), no payload bytes are stored at all.
            values.extend([] for _ in range(count))
            continue
        eb = _elem_bytes(leaf_hdr)
        if eb < 1:
            return None
        for i in range(count):
            row_ref = _read_ref(data, leaf_ref + 8, i, eb)
            if row_ref <= 0 or row_ref >= file_size:
                values.append([])
                continue
            targets = _read_scalar_leaf(data, row_ref, file_size)
            values.append([int(t) for t in targets if t is not None] if targets else [])
    return values


def _decode_pre_cluster_column_values(
    data: bytes,
    col_ref: int,
    file_size: int,
    col_info: dict[str, Any],
) -> list[Any] | None:
    """Decode one old-format column's full value list, dispatched purely
    from its Spec-declared old ColumnType (never guessed from shape). The
    per-type leaf primitives are the same ones already used for modern
    columns -- only the top-level walk (_walk_bplustree_leaves, confirmed
    against bptree.hpp @ v5.23.9 to share the modern BPlusTree<T>'s
    inner-node layout) and the dispatch table are new for this era.

    Every old ColumnType is dispatched here now; a genuinely undecodable
    per-cell value (e.g. a Mixed cell holding a nested subtable) still
    returns an explicit marker rather than silently wrong data -- see
    _decode_pre_cluster_mixed_column. BackLink columns are hidden entirely
    by the caller (_extract_pre_cluster_table_data), not dispatched here.
    """
    if col_ref <= 0 or col_ref >= file_size:
        return None
    type_code = col_info["type_code"]
    nullable = col_info["nullable"]

    if type_code == 8:  # Timestamp
        return _decode_pre_cluster_timestamp_column(data, col_ref, file_size)
    if type_code == 13:  # LinkList
        return _decode_pre_cluster_linklist_column(data, col_ref, file_size)
    if type_code == 5:  # Table (subtable)
        return _decode_pre_cluster_table_column(
            data, col_ref, file_size, col_info.get("subtable_spec_ref")
        )
    if type_code == 3:  # StringEnum
        return _decode_pre_cluster_string_enum_column(
            data, col_ref, col_info.get("enum_keys_ref"), file_size
        )
    if type_code == 6:  # Mixed
        return _decode_pre_cluster_mixed_column(data, col_ref, file_size)

    leaves = _walk_bplustree_leaves(data, col_ref, file_size)
    if not leaves:
        leaves = [(col_ref, 0)]

    values: list[Any] = []
    for leaf_ref, _offset in leaves:
        leaf_vals: list[Any] | None
        if type_code == 0:  # int
            leaf_vals = (
                _read_array_int_null(data, leaf_ref, file_size) if nullable
                else _read_scalar_leaf(data, leaf_ref, file_size)
            )
        elif type_code == 1:  # bool
            leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
            if leaf_vals is not None:
                leaf_vals = [None if v is None else bool(v) for v in leaf_vals]
        elif type_code in (2, 4):  # string, binary
            leaf_vals = _read_pre_cluster_string_or_binary(
                data, leaf_ref, file_size, is_string=(type_code == 2), nullable=nullable,
            )
        elif type_code in (9, 10):  # float, double
            leaf_vals = _read_array_float(data, leaf_ref, file_size)
        elif type_code == 7:  # OldDateTime -- plain epoch-seconds int leaf
            leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
            if leaf_vals is not None:
                leaf_vals = [
                    None if v is None else _decode_timestamp(int(v)) for v in leaf_vals
                ]
        elif type_code == 12:  # Link -- LinkColumn::get_link (column_link.hpp):
            # raw 0 = null, raw N (N>0) = target row index N-1.
            leaf_vals = _read_scalar_leaf(data, leaf_ref, file_size)
            if leaf_vals is not None:
                leaf_vals = [
                    None if v is None or v == 0 else int(v) - 1 for v in leaf_vals
                ]
        else:
            return None  # not yet implemented -- see docstring
        if leaf_vals is None:
            return None
        values.extend(leaf_vals)
    return values


def _extract_pre_cluster_table_data(
    data: bytes, table_ref: int, table_name: str, file_size: int, schema: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    """Decode one pre-Cluster Table (table.hpp @ v5.23.9: m_top slot 0 =
    spec ref, slot 1 = columns ref). Row count is taken from the first
    successfully-decoded column's value count (every column in a
    well-formed old Table has exactly one entry per row); a table with no
    decodable columns returns a 0-row result rather than None, so it is
    still listed rather than silently dropped.

    Returns (table, reason) -- reason is None on success, otherwise a
    specific, human-readable description of the exact structural check
    that failed (never just "could not be decoded"), so the caller can
    surface *why*, not only *that* this table didn't decode
    (feedback_explicit_unsupported_marking).
    """
    t_hdr = _parse_array_header(data, table_ref)
    if t_hdr is None or not t_hdr["has_refs"] or t_hdr["Element count (size)"] < 2:
        return None, "Table top array is malformed or missing its spec/columns slots"
    t_eb = _elem_bytes(t_hdr)
    if t_eb < 1:
        return None, "Table top array has a zero element width"

    spec_ref = _read_ref(data, table_ref + 8, 0, t_eb)
    columns_ref = _read_ref(data, table_ref + 8, 1, t_eb)
    if spec_ref <= 0 or spec_ref >= file_size:
        return None, "Spec reference is invalid or points outside the file"

    spec_columns = _extract_pre_cluster_spec(data, spec_ref, file_size)
    if not spec_columns:
        return None, "Spec array has no columns (empty or malformed)"
    col_refs = (
        _resolve_pre_cluster_column_refs(data, columns_ref, spec_columns, file_size)
        if 0 < columns_ref < file_size else {}
    )

    columns: dict[int, list[Any]] = {}
    column_names: list[str] = []
    column_types: list[str] = []
    unsupported_columns: list[str] = []
    row_count = 0
    row_count_known = False

    # BackLink columns are auto-generated reverse-link bookkeeping, not user
    # data -- hidden from the visible column list here too (matching the
    # modern path's _HIDDEN_COL_TYPES), but still kept in spec_columns above
    # for _resolve_pre_cluster_column_refs's slot-position math, which needs
    # every Spec entry in order to stay aligned with the real m_columns array.
    visible_cols = [col for col in spec_columns if col["type_code"] != 14]

    for user_idx, col in enumerate(visible_cols):
        column_names.append(col["name"])
        column_types.append(_PRE_CLUSTER_COL_TYPES.get(col["type_code"], f"type_{col['type_code']}"))
        col_ref = col_refs.get(col["col_index"], 0)
        values = _decode_pre_cluster_column_values(data, col_ref, file_size, col)
        if values is None:
            # Type not yet implemented, or genuinely undecodable -- flagged
            # explicitly below rather than shown as a silent empty column.
            unsupported_columns.append(col["name"])
        columns[user_idx] = values if values is not None else []
        if values is not None and not row_count_known:
            row_count = len(values)
            row_count_known = True

    # Undecoded columns still get one marker per row once the row count is
    # known from a sibling column -- a visible "<unsupported...>" placeholder
    # (same pattern as _read_array_mixed's own marker for a data_type it
    # doesn't recognise), not None, so it can't be mistaken for real NULL data.
    if row_count_known:
        for user_idx, col in enumerate(visible_cols):
            if col["name"] in unsupported_columns:
                type_name = _PRE_CLUSTER_COL_TYPES.get(col["type_code"], f"type_{col['type_code']}")
                columns[user_idx] = [f"<unsupported: {type_name}>"] * row_count

    column_target_tables: list[str | None] = []
    for col in visible_cols:
        tt_idx = col.get("target_table_index")
        column_target_tables.append(
            schema[tt_idx] if tt_idx is not None and 0 <= tt_idx < len(schema) else None
        )

    return {
        "name": table_name,
        "row_count": row_count,
        "row_count_estimated": not row_count_known,
        "columns": columns,
        "column_names": column_names,
        "column_types": column_types,
        "column_target_tables": column_target_tables,
        "unsupported_columns": unsupported_columns,
        "obj_keys": list(range(row_count)),
    }, None


def _extract_pre_cluster_tables_data(
    data: bytes, root_offset: int, schema: list[str], file_size: int,
) -> tuple[list[dict[str, Any]], str | None]:
    """Pre-Cluster equivalent of _extract_table_data: same Group -> tables
    array walk (root_offset -> child[1], stable across all file-format
    versions -- group.hpp s_table_refs_ndx=1 predates even the earliest
    documented format changes), but dispatches each table through
    _extract_pre_cluster_table_data instead of the Cluster-based path.

    Returns (tables, reason) -- reason is None only when every table in
    *schema* decoded; otherwise a "class_name: specific cause" string per
    failed table (semicolon-joined), so the caller can show the parser's
    own concrete diagnosis instead of a generic "could not be decoded"
    (feedback_explicit_unsupported_marking) -- e.g. a Group top array with
    no table-refs slot at all (root_hdr["Element count (size)"] < 2) is a
    structurally different, more specific problem than one single table's
    Spec being unreadable, and both should say so distinctly.
    """
    root_hdr = _parse_array_header(data, root_offset)
    if root_hdr is None or not root_hdr["has_refs"]:
        return [], "Group top array is malformed or has no references"
    root_eb = _elem_bytes(root_hdr)
    if root_eb < 1 or root_hdr["Element count (size)"] < 2:
        return [], "Group top array has no table-refs slot (fewer than 2 children)"

    table_refs_off = _read_ref(data, root_offset + 8, 1, root_eb)
    if table_refs_off <= 0 or table_refs_off >= file_size:
        return [], "Table-refs reference is invalid or points outside the file"
    tr_hdr = _parse_array_header(data, table_refs_off)
    if tr_hdr is None or not tr_hdr["has_refs"]:
        return [], "Table-refs array is malformed or has no references"
    tr_eb = _elem_bytes(tr_hdr)
    num_tables = tr_hdr["Element count (size)"]

    tables: list[dict[str, Any]] = []
    failures: list[str] = []
    for t_idx in range(num_tables):
        table_name = schema[t_idx] if t_idx < len(schema) else f"table[{t_idx}]"
        table_ref = _read_ref(data, table_refs_off + 8, t_idx, tr_eb)
        if table_ref <= 0 or table_ref >= file_size:
            failures.append(f"{table_name}: table reference is invalid or points outside the file")
            continue
        table, reason = _extract_pre_cluster_table_data(data, table_ref, table_name, file_size, schema)
        if table is not None:
            tables.append(table)
        else:
            failures.append(f"{table_name}: {reason}")

    if num_tables == 0 and schema:
        # Class names resolved from Group.m_table_names, but the table-refs
        # array itself is empty -- a real mismatch, not "nothing to report".
        return [], f"Table-refs array has 0 entries, but {len(schema)} class name(s) in schema"
    return tables, ("; ".join(failures) if failures else None)


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
        streaming_form: dict[str, Any] | None = None

        if header_info:
            top_ref0_val = int.from_bytes(full_data[0:8], "little")
            top_ref1_val = int.from_bytes(full_data[8:16], "little")
            active_idx = header_info["Active top reference"]

            streaming_form = _resolve_streaming_form(full_data, top_ref0_val, active_idx)

            if streaming_form is not None:
                # Group::write() streaming form: no second/inactive version
                # exists (top_ref1 is unused padding, always 0), and the real
                # top ref lives in the footer, not in top_ref0's literal value.
                resolved_ref = streaming_form["top_ref"]
                footer_valid = streaming_form["footer_valid"]
                display_offset = resolved_ref if footer_valid else top_ref0_val
                hdr0 = _parse_array_header(full_data, display_offset) if footer_valid else None
                children0 = (
                    _extract_root_children(full_data, display_offset, file_size)
                    if footer_valid else []
                )
                top_refs = {
                    "top_ref_0": {
                        "offset": display_offset,
                        "active": True,
                        "array_header": hdr0,
                        "children": children0,
                    },
                    "top_ref_1": {
                        "offset": top_ref1_val,
                        "active": False,
                        "array_header": None,
                        "children": [],
                    },
                    "active_index": 0,
                    "streaming_form": streaming_form,
                }

                active_offset = display_offset if footer_valid else -1
                inactive_offset = -1
                inactive_ref_idx = 0
                active_format = header_info["File format (top ref 0)"]
                inactive_format = 0
                schema = _extract_schema(full_data, active_offset, file_size) if footer_valid else []
                inactive_schema = []
            else:
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
                # Each top ref carries its own format byte (fmt0/fmt1) rather
                # than a single file-wide value: mid-upgrade, Realm briefly
                # writes the new format to one ref while the other still
                # reads the old one.
                active_format = (
                    header_info["File format (top ref 1)"] if active_idx == 1
                    else header_info["File format (top ref 0)"]
                )
                inactive_format = (
                    header_info["File format (top ref 0)"] if active_idx == 1
                    else header_info["File format (top ref 1)"]
                )
                schema = _extract_schema(full_data, active_offset, file_size)
                inactive_schema = _extract_schema(full_data, inactive_offset, file_size)

        strings = _scan_strings(full_data)

        # Row/table data below _MIN_CLUSTER_FORMAT_VERSION uses the
        # pre-Cluster Table/Spec layout (_extract_pre_cluster_tables_data)
        # instead of the Cluster-based path. unsupported_row_format now
        # only means "this file format predates format 10 and used the old
        # layout" (informational, not a decode failure) -- a handful of old
        # column types still can't be decoded per-column; those are flagged
        # per-table via each table's "unsupported_columns" instead.
        unsupported_row_format: int | None = None
        pre_cluster_reason: str | None = None
        cluster_reason: str | None = None

        tables: list[dict[str, Any]] = []
        if header_info and schema:
            if active_format < _MIN_CLUSTER_FORMAT_VERSION:
                unsupported_row_format = active_format
                tables, pre_cluster_reason = _extract_pre_cluster_tables_data(
                    full_data, active_offset, schema, file_size
                )
            else:
                table_key_map = _build_table_key_map(full_data, active_offset, schema, file_size)
                tables, cluster_reason = _extract_table_data(
                    full_data, active_offset, schema, file_size, table_key_map
                )

        inactive_tables: list[dict[str, Any]] = []
        if header_info and inactive_schema:
            if inactive_format < _MIN_CLUSTER_FORMAT_VERSION:
                if unsupported_row_format is None:
                    unsupported_row_format = inactive_format
                inactive_tables, inactive_pre_cluster_reason = _extract_pre_cluster_tables_data(
                    full_data, inactive_offset, inactive_schema, file_size
                )
                if pre_cluster_reason is None:
                    pre_cluster_reason = inactive_pre_cluster_reason
            else:
                inactive_table_key_map = _build_table_key_map(
                    full_data, inactive_offset, inactive_schema, file_size
                )
                inactive_tables, inactive_cluster_reason = _extract_table_data(
                    full_data, inactive_offset, inactive_schema, file_size, inactive_table_key_map
                )
                if cluster_reason is None:
                    cluster_reason = inactive_cluster_reason

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
            "unsupported_row_format": unsupported_row_format,
            "streaming_form": streaming_form,
            "cluster_reason": cluster_reason,
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
            if streaming_form is not None:
                # Group::write() "streaming" form (e.g. a Realm Studio file
                # export) — top_ref[0] is a sentinel, not an offset; see
                # _resolve_streaming_form. Always state this explicitly,
                # since a corrupt footer must not read the same as "decoded,
                # zero tables".
                if streaming_form["footer_valid"]:
                    meta["Streaming form"] = (
                        f"Yes — top ref resolved from end-of-file footer "
                        f"(offset {streaming_form['top_ref']})"
                    )
                else:
                    meta["Streaming form"] = (
                        "Yes — but the footer is missing or its magic cookie "
                        "doesn't match; top ref could not be resolved "
                        "(truncated or corrupt file)"
                    )
            if schema:
                meta["Tables found"] = str(len(schema))
            elif streaming_form is not None and not streaming_form["footer_valid"]:
                meta["Tables found"] = "Unresolved (see Streaming form)"
            if unsupported_row_format is not None:
                # File format is already shown above ("File format"); this
                # message adds the parser's own concrete diagnosis, not a
                # restated format number (feedback_explicit_unsupported_marking:
                # say *why*, not just *that* something didn't decode).
                pc_tables = tables + inactive_tables
                gaps = {
                    t["name"]: t["unsupported_columns"]
                    for t in pc_tables
                    if t.get("unsupported_columns")
                }
                reasons: list[str] = []
                if pre_cluster_reason:
                    reasons.append(pre_cluster_reason)
                if gaps:
                    n_cols = sum(len(v) for v in gaps.values())
                    reasons.append(
                        f"{n_cols} column(s) across {len(gaps)} table(s) not yet decoded "
                        "(unimplemented old column type)"
                    )
                if reasons:
                    meta["Row data"] = "Pre-Cluster layout — " + "; ".join(reasons)
                else:
                    meta["Row data"] = "Decoded via legacy pre-Cluster layout"
            elif cluster_reason:
                # Same principle for format >=10: schema/class names may
                # have resolved from Group.m_table_names while the
                # Cluster/ClusterTree structure itself didn't -- say why,
                # not just leave "tables" silently empty.
                meta["Row data"] = cluster_reason
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
    'row_count', 'unsupported_columns'}. 'columns' is keyed by positional index;
    column_names[i] gives the property name for column i.

    Also returns 'pre_cluster_format' (the file format byte when the store uses
    the pre-Cluster layout Realm used before file format 10, else None) and
    'reason' (the parser's own explanation when a table did not decode, else
    None). Upstream spells the first of these 'unsupported_row_format'; it kept
    that name after gaining pre-Cluster row support, so it no longer means the
    rows are unreadable. Renamed here so artifacts are not misled by it.

    Returns {'header': None, ...} when the file is not a decodable (e.g.
    encrypted or corrupt) Realm file.

    This helper re-implements RealmParser.parse()'s walk rather than calling it,
    so any dispatch upstream adds to parse() has to be mirrored here by hand.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    file_size = len(data)
    header = _parse_realm_header(data)
    result = {
        "header": header,
        "active": {},
        "inactive": {},
        "pre_cluster_format": None,
        "reason": None,
    }
    if not header:
        return result

    top0 = int.from_bytes(data[0:8], "little")
    top1 = int.from_bytes(data[8:16], "little")
    active_index = header["Active top reference"]

    # Group::write() output puts the real top ref in a footer rather than in
    # the header, and carries no second version at all.
    streaming = _resolve_streaming_form(data, top0, active_index)
    if streaming is not None:
        if not streaming["footer_valid"]:
            result["reason"] = "streaming-form file whose footer could not be read"
            return result
        sections = (("active", streaming["top_ref"], header["File format (top ref 0)"]),)
    else:
        active_off = top1 if active_index == 1 else top0
        inactive_off = top0 if active_index == 1 else top1
        active_fmt = (header["File format (top ref 1)"] if active_index == 1
                      else header["File format (top ref 0)"])
        inactive_fmt = (header["File format (top ref 0)"] if active_index == 1
                        else header["File format (top ref 1)"])
        sections = (("active", active_off, active_fmt),
                    ("inactive", inactive_off, inactive_fmt))

    reasons = []
    for label, offset, file_format in sections:
        schema = _extract_schema(data, offset, file_size)
        if not schema:
            continue
        if file_format < _MIN_CLUSTER_FORMAT_VERSION:
            if result["pre_cluster_format"] is None:
                result["pre_cluster_format"] = file_format
            tables, reason = _extract_pre_cluster_tables_data(
                data, offset, schema, file_size)
        else:
            key_map = _build_table_key_map(data, offset, schema, file_size)
            tables, reason = _extract_table_data(
                data, offset, schema, file_size, key_map)
        if reason:
            reasons.append(f"{label}: {reason}")
        for table in tables:
            result[label][table["name"]] = {
                "column_names": table.get("column_names", []),
                "column_types": table.get("column_types", []),
                "columns": table.get("columns", {}),
                "row_count": table.get("row_count", 0),
                "unsupported_columns": table.get("unsupported_columns", []),
            }
    if reasons:
        result["reason"] = "; ".join(reasons)
    return result


def realm_rows(path, class_name, section="active"):
    """Yield each row of ``class_name`` as a {column_name: value} dict.

    Convenience wrapper over parse_realm_file() for iLEAPP artifacts. ``section``
    is 'active' (live objects) or 'inactive' (the other top-ref: older/removed
    schema state). Missing table or file yields nothing.
    """
    if not path or not os.path.isfile(path):
        # Artifacts pass '' when the app's Realm is not in the extraction. The
        # docstring above promises nothing rather than an exception, so honour it.
        return
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
