"""ewfprobe: a read-only reader for EnCase/EWF (.E01) forensic images.

One file, pure Python, standard library only. No compiler, no network, and
nothing to install. It opens an EWF-E01 or SMART (.s01) acquisition, joins its
segments, and presents the original disk as an ordinary seekable file object,
so anything that can read a raw image can read an E01 without changing how it
reads. It also reads Ex01 (EWF2), the format EnCase 7 introduced, and AFF, the
Advanced Forensic Format that AFFLIB and FTK Imager write, as a single .aff file or
as an AFD directory of them. From an L01, EnCase's logical evidence, it lists the
files collected and reads each one's content.

    with ewfprobe.open_ewf("evidence.E01") as img:
        img.seek(0)
        boot = img.read(512)

The object answers ``seek``, ``tell``, ``read`` and ``close`` and works as a
context manager, which is the whole interface a volume or filesystem parser
needs.

Written from the public format documentation: Joachim Metz, "Expert Witness
Compression Format (EWF)" and "Expert Witness Compression Format 2 (EWF2)", in
the libyal/libewf repository under ``documentation/``. No code is taken from
libewf, which is LGPL, or from any other EWF implementation. This file is MIT,
and reimplementing a documented format is what keeps it that way. The AFF
reader is written from AFFLIB's own documentation, the segment names and flag
values in its public header, include/afflib/afflib.h, and, for AFD, how
lib/vnode_afd.cpp finds and joins the files of one (sshock/AFFLIBv3); no AFFLIB
code is copied.

Scope. This reads EWF-E01, the format EnCase 6 and 7 and FTK Imager write and
by far the most common one in the field, EWF-S01, the variant ASR Data's SMART
writes, EWF2-Ex01, which EnCase 7 and later write, AFF, including AFD, and
EWF-L01 logical evidence. It does not read Lx01 logical evidence, encrypted Ex01
images (the encryption is not publicly documented), Ex01 images compressed with
bzip2 (no sample exists to validate against), encrypted AFF, or AFM (AFF metadata
beside split raw files), and it never writes.

An image whose content is encrypted at rest, by BitLocker or FileVault or an
encrypted APFS volume, reads back as the ciphertext that was acquired: the
reader is working, there is simply nothing plain in there to find.
"""

from __future__ import annotations

import argparse
import bisect
import errno
import hashlib
import io
import os
import re
import struct
import sys
import zlib
from collections import OrderedDict

__version__ = "0.2.0"

# ---------------------------------------------------------------- constants

SIGNATURE = b"EVF\x09\x0d\x0a\xff\x00"

FILE_HEADER_SIZE = 13
_FILE_HEADER = struct.Struct("<8sBHH")          # signature, 0x01, segment number, 0x0000

SECTION_SIZE = 76
_SECTION = struct.Struct("<16sQQ40sI")          # type, next offset, size, padding, checksum

_TABLE_HEADER = struct.Struct("<IIQII")         # count, pad, base offset, pad, checksum
TABLE_HEADER_SIZE = 24

_COMPRESSED_BIT = 0x80000000
_OFFSET_MASK = 0x7FFFFFFF

MEDIA_TYPES = {0x00: "removable", 0x01: "fixed", 0x03: "optical", 0x0E: "logical"}
COMPRESSION_LEVELS = {0x00: "none", 0x01: "good", 0x02: "best"}

# SMART (EWF-S01) writes the same EVF segment files as EnCase, with lowercase
# segment names and the original 94-byte volume section, which carries this
# string at offset 85 where EnCase's longer volume section has other fields.
# That volume section records neither the media type nor the compression level;
# the level is in the header section's "r" value instead.
SMART_SIGNATURE = b"SMART"
SMART_COMPRESSION = {"n": "none", "f": "fast", "b": "best"}

FORMAT_E01 = "EWF-E01"
FORMAT_S01 = "EWF-S01"
FORMAT_EX01 = "EWF2-Ex01"
FORMAT_L01 = "EWF-L01"

# EWF2 (Ex01). A 32-byte file header, then sections whose 64-byte descriptor sits
# AFTER the section's data and points back at the previous descriptor, so a
# segment is walked from its end towards its start.
SIGNATURE_V2 = b"EVF2\r\n\x81\x00"
FILE_HEADER_V2_SIZE = 32
_FILE_HEADER_V2 = struct.Struct("<8sBBHI16s")    # signature, major, minor,
                                                 # compression, segment, set GUID
SECTION_V2_SIZE = 64
_SECTION_V2 = struct.Struct("<IIQQII")           # type, flags, previous, data size,
                                                 # descriptor size, padding size
_TABLE_V2_HEADER = struct.Struct("<QIII")        # first chunk, count, pad, checksum
TABLE_V2_HEADER_SIZE = 32                        # 20 bytes and 12 of alignment
_TABLE_V2_ENTRY = struct.Struct("<QII")          # offset or pattern, size, flags

V2_DEVICE_INFORMATION = 0x01
V2_CASE_DATA = 0x02
V2_SECTOR_TABLE = 0x04
V2_MD5 = 0x08
V2_SHA1 = 0x09
V2_ENCRYPTION_KEYS = 0x0B
V2_NEXT = 0x0D
V2_DONE = 0x0F
V2_SECTION_ENCRYPTED = 0x02

V2_CHUNK_COMPRESSED = 0x01
V2_CHUNK_CHECKSUMED = 0x02
V2_CHUNK_PATTERN_FILL = 0x04

V2_COMPRESSION_METHODS = {0: "none", 1: "deflate", 2: "bzip2"}
V2_DRIVE_TYPES = {"a": "RAM disk", "c": "optical", "f": "fixed", "l": "logical",
                  "m": "memory", "p": "PALM", "r": "removable"}

# The device information and case data sections name their values with short
# identifiers, as the EWF1 header does. Target time and actual time keep the
# specification's names and are reported as stored, seconds since 1970 in UTC.
_V2_FIELDS = {
    "nm": "description",
    "cn": "case_number",
    "en": "evidence_number",
    "ex": "examiner",
    "nt": "notes",
    "av": "acquiry_software_version",
    "os": "operating_system",
    "tt": "target_time",
    "at": "actual_time",
    "sn": "drive_serial_number",
    "md": "drive_model",
    "lb": "drive_label",
}

# AFF (Advanced Forensic Format). A file header, then named segments one after
# another, each "AFF\0", name length, data length and a 32-bit argument (all
# big-endian), the name, the data, and a tail "ATT\0" plus the segment's length.
# The disk is cut into equal pages held in segments named page0, page1 and on.
# Names and flag values are AFFLIB's, from include/afflib/afflib.h.
AF_HEADER = b"AFF10\r\n\x00"
_AF_SEGHEAD = struct.Struct(">4sIII")            # "AFF\0", name len, data len, arg
_AF_SEGTAIL = struct.Struct(">4sI")              # "ATT\0", segment length
AF_PAGE_COMPRESSED = 0x0001
AF_PAGE_COMP_ALG_MASK = 0x00F0
AF_PAGE_COMP_ALG_ZLIB = 0x0000
AF_PAGE_COMP_ALG_BZIP = 0x0010                   # AFFLIB never implemented it
AF_PAGE_COMP_ALG_LZMA = 0x0020
AF_PAGE_COMP_ALG_ZERO = 0x0030                   # data is a 4-byte count of NULs
AF_AES256_SUFFIX = "/aes256"
AF_SIG256_SUFFIX = "/sha256"
_AF_PAGE_NAME = re.compile(r"(?:page|seg)(\d+)")
_AF_PAGE_HASH_NAME = re.compile(r"(?:page|seg)\d+_(?:md5|sha1|sha256)")
_AF_STRUCTURAL = {"pagesize", "segsize", "imagesize", "sectorsize", "badflag",
                  "badsectors", "blanksectors", "md5", "sha1", "sha256", "image_gid",
                  "devicesectors", "aff_file_type"}
# AFF segments with the same meaning as an EWF header value are reported under that
# value's name; every other text segment keeps the name it is stored under.
_AFF_FIELDS = {
    "case_num": "case_number",
    "acquisition_notes": "notes",
    "acquisition_tecnician": "examiner",   # AFFLIB's own spelling
    "acquisition_date": "acquisition_date",
}
FORMAT_AFF = "AFF"
_AFF_MAX_SMALL = 1 << 16                         # non-page segments read into memory
# AFD: one AFF image kept as a directory whose name ends .afd, holding ordinary AFF
# files. AFFLIB (lib/vnode_afd.cpp) opens every .aff file in the directory, reads a
# segment from the first file that holds it, and names the files it writes
# file_000.aff, file_001.aff and on, numbered by how many it already has.
FORMAT_AFD = "AFD"
_AFD_MEMBER_NAME = re.compile(r"file_(\d+)\.aff", re.IGNORECASE)
# Segments the files of an AFD must agree on when more than one of them holds one.
_AFD_MUST_AGREE = {"pagesize", "segsize", "sectorsize", "badflag", "md5", "sha1", "sha256"}

# Logical evidence files share the section machinery but hold files, not a disk.
# An L01 keeps the content of the files it collected back to back in its chunks,
# the "media data", and describes them in an ltree section: a 48-byte header (the
# MD5 of the text, its size, and an Adler-32 of the header) and UTF-16LE text in
# categories, of which "rec" gives the media data size (tb) and "entry" the file
# tree. From the EWF-L01 parts of the EWF specification.
LVF_SIGNATURE = b"LVF\x09\x0d\x0a\xff\x00"
LEF2_SIGNATURE = b"LEF2\r\n\x81\x00"
LOGICAL_SIGNATURES = (LVF_SIGNATURE, LEF2_SIGNATURE)
_LTREE_HEADER = struct.Struct("<16sQI20s")      # MD5 of the text, text size, Adler-32
L01_FLAG_FOLDER = 0x02000000                    # the opr (flags) values the reader uses
L01_FLAG_SPARSE = 0x04000000
_L01_TIMES = ("cr", "ac", "wr", "mo", "dl", "aq")

# How many decompressed chunks and open segment handles to keep. A chunk is
# normally 32 KiB, so the cache is a couple of megabytes at the default.
CHUNK_CACHE = 64
# The cache is bounded in bytes as well, because an AFF page is 16 MiB by default.
CHUNK_CACHE_BYTES = CHUNK_CACHE * 32768
MAX_OPEN = 8

# The header sections name their fields with one or two letter identifiers.
_HEADER_FIELDS = {
    "c": "case_number",
    "n": "evidence_number",
    "a": "description",
    "e": "examiner",
    "t": "notes",
    "av": "acquiry_software_version",
    "ov": "operating_system",
    "m": "acquisition_date",
    "u": "system_date",
    "p": "password_hash",
    "pid": "process_identifier",
    "dc": "unknown_dc",
    "ext": "extents",
    "r": "compression_level",
}


class EwfError(Exception):
    """Base for everything this module raises."""


class EwfFormatError(EwfError):
    """The bytes are not a valid EWF image, or carry something unsupported."""


class EwfIncompleteSetError(EwfError):
    """A segment of a multi-segment acquisition is missing.

    Raised rather than reading the segments that are present, because a partial
    set reads as a small clean image and reports its missing data as empty.
    """


# ------------------------------------------------------------- segment names

def _extension_sequence(first="E"):
    """The segment extensions of one family, in order.

    EnCase sets run E01 to E99, then EAA to ZZZ. SMART sets run s01 to s99, then
    saa to zzz. The specification lists saa to szz and then gives faa, which reads
    as a slip: taa onward is what the E sequence does after EZZ, and it is what
    libewf's SMART writer produces.
    """
    last, low = ("z", "a") if first.islower() else ("Z", "A")
    for i in range(1, 100):
        yield f"{first}{i:02d}"
    for lead in range(ord(first), ord(last) + 1):
        for second in range(ord(low), ord(last) + 1):
            for third in range(ord(low), ord(last) + 1):
                yield chr(lead) + chr(second) + chr(third)


def _extension_sequence_v2():
    """Ex01 to Ex99, then ExAA to EzZZ, as the EWF2 specification lists them."""
    for i in range(1, 100):
        yield f"Ex{i:02d}"
    for lead in "xyz":
        for second in range(ord("A"), ord("Z") + 1):
            for third in range(ord("A"), ord("Z") + 1):
                yield "E" + lead + chr(second) + chr(third)


def _family(ext):
    """The segment family an extension belongs to: "E", "s", "L", "Ex" or "Lx"."""
    low = ext.lower()
    if len(ext) == 4 and low[:1] in "el" and low[1:2] in "xyz":
        return low[:1].upper() + "x"
    if low[:1] == "l":
        return "L"
    return "s" if low[:1] == "s" else "E"


def is_image(path) -> bool:
    """True when ``path`` is a disk image ewfprobe reads: a file beginning with the
    EWF, EWF2 or AFF signature, or an AFD directory holding AFF files. An L01 holds
    files rather than a disk; is_logical_evidence answers for it."""
    if os.path.isdir(path):
        afd = _afd_directory(path)
        try:
            return bool(afd) and any(_is_aff(os.path.join(afd, name))
                                     for name in os.listdir(afd)
                                     if name.lower().endswith(".aff"))
        except OSError:
            return False
    try:
        with open(path, "rb") as fh:
            return fh.read(8) in (SIGNATURE, SIGNATURE_V2, AF_HEADER)
    except OSError:
        return False


def is_logical_evidence(path) -> bool:
    """True when the file begins with the L01 signature, logical evidence ewfprobe
    reads as a tree of files."""
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == LVF_SIGNATURE
    except OSError:
        return False


def _is_aff(path):
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == AF_HEADER
    except OSError:
        return False


def _afd_directory(path):
    """The AFD directory ``path`` names, as the directory itself or as one of the .aff
    files in it, else None. AFFLIB takes a directory whose name ends .afd as an AFD
    (afd_identify_file in lib/vnode_afd.cpp). Given one file of an AFD, the whole
    directory is opened, because one file holds only some of the image's pages."""
    full = os.path.abspath(path)
    if os.path.isdir(full):
        return full if full.lower().endswith(".afd") else None
    parent = os.path.dirname(full)
    if full.lower().endswith(".aff") and parent.lower().endswith(".afd"):
        return parent
    return None


def _natural(name):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", name)]


def _afd_members(directory):
    """The .aff files of an AFD directory, in numbered order.

    AFFLIB numbers the files it writes from file_000.aff, so when every file carries
    such a name, a gap in the numbering is a file that is missing, and the set is
    refused as an EWF set with a missing segment is.
    """
    label = os.path.basename(directory)
    names = sorted((n for n in os.listdir(directory)
                    if n.lower().endswith(".aff")
                    and os.path.isfile(os.path.join(directory, n))), key=_natural)
    if not names:
        raise EwfFormatError(f"{label} is an AFD directory with no .aff file in it")
    numbers = [_AFD_MEMBER_NAME.fullmatch(n) for n in names]
    if all(numbers):
        have = {int(m.group(1)) for m in numbers}
        gaps = [f"file_{k:03d}.aff" for k in range(max(have) + 1) if k not in have]
        if gaps:
            raise EwfIncompleteSetError(
                f"{label} is missing {', '.join(gaps[:5])}"
                f"{f' and {len(gaps) - 5} more' if len(gaps) > 5 else ''}; AFFLIB "
                f"numbers the files of an AFD in order, so a gap is a file that is "
                f"not there")
    return [os.path.join(directory, n) for n in names]


def is_ewf(path) -> bool:
    """True when the file begins with the EWF or EWF2 (Ex01) signature."""
    try:
        with open(path, "rb") as fh:
            return fh.read(8) in (SIGNATURE, SIGNATURE_V2)
    except OSError:
        return False


def _stem_and_dir(path):
    folder, name = os.path.split(os.path.abspath(path))
    stem, dot, ext = name.rpartition(".")
    if not dot:
        raise EwfFormatError(f"{name} has no EWF extension")
    return folder, stem, ext


def ewf_segments(path) -> list[str]:
    """Every segment file of the acquisition ``path`` belongs to, in order.

    The set is built from the first segment onward, following the documented
    extension sequence, and stops at the first extension that is not on disk.
    Matching ignores case, because a set written on Windows and copied to a
    case-sensitive volume can arrive as .e01. The returned paths are the names
    as they actually sit on disk.
    """
    folder, stem, ext = _stem_and_dir(path)
    try:
        present = {e.lower(): e for e in os.listdir(folder)}
    except OSError as exc:
        raise EwfFormatError(f"cannot list the folder holding the image: {exc}") from exc

    segments = []
    family = _family(ext)
    if family == "Lx":
        raise EwfFormatError(
            f"{os.path.basename(path)} has an Lx01 name; Lx01 logical evidence is not "
            f"read")
    sequence = _extension_sequence_v2() if family == "Ex" else _extension_sequence(family)
    for seg_ext in sequence:
        want = f"{stem}.{seg_ext}".lower()
        actual = present.get(want)
        if actual is None:
            break
        segments.append(os.path.join(folder, actual))
    if not segments:
        raise EwfFormatError(
            f"{os.path.basename(path)} is not the first segment of an EWF set; "
            f"the set is opened from its .E01, its .Ex01, its .L01, or its .s01 for "
            f"SMART")
    return segments


# ------------------------------------------------------------------ sections

def _read_exactly(fh, n):
    data = fh.read(n)
    if len(data) != n:
        raise EwfFormatError(f"short read: wanted {n} bytes, got {len(data)}")
    return data


def _sections(fh, segment_path):
    """Yield (type, data_offset, data_size, next_offset) for one segment file."""
    fh.seek(0)
    head = _read_exactly(fh, FILE_HEADER_SIZE)
    signature, one, segment_number, zero = _FILE_HEADER.unpack(head)
    if signature not in (SIGNATURE, LVF_SIGNATURE):
        raise EwfFormatError(f"{os.path.basename(segment_path)} is not an EWF file")
    if one != 1 or zero != 0:
        raise EwfFormatError(
            f"{os.path.basename(segment_path)} has an unexpected file header")

    offset = FILE_HEADER_SIZE
    seen = set()
    while True:
        if offset in seen:                       # a self-referencing chain
            raise EwfFormatError(
                f"{os.path.basename(segment_path)} has a section loop at {offset}")
        seen.add(offset)
        fh.seek(offset)
        raw = _read_exactly(fh, SECTION_SIZE)
        stype, next_offset, size, _pad, _checksum = _SECTION.unpack(raw)
        name = stype.split(b"\x00", 1)[0].decode("ascii", "replace")
        data_offset = offset + SECTION_SIZE
        if offset < next_offset:
            # The next section's offset bounds this one exactly, which is not
            # sensitive to whether the size field counts the descriptor.
            data_size = max(0, next_offset - data_offset)
        else:
            data_size = max(0, size - SECTION_SIZE)
        yield segment_number, name, data_offset, data_size, next_offset
        # "next" and "done" both point at themselves and end the segment.
        if name in ("next", "done") or next_offset == offset or next_offset == 0:
            return
        offset = next_offset


def _sections_v2(fh, segment_path):
    """The file header and the sections of one Ex01 segment, first to last.

    Returns (segment number, compression method, set identifier, sections), where
    each section is (type, data flags, data offset, data size).
    """
    name = os.path.basename(segment_path)
    fh.seek(0, os.SEEK_END)
    end = fh.tell()
    fh.seek(0)
    (signature, major, minor, method, segment_number,
     set_id) = _FILE_HEADER_V2.unpack(_read_exactly(fh, FILE_HEADER_V2_SIZE))
    if signature != SIGNATURE_V2:
        raise EwfFormatError(f"{name} is not an Ex01 file")
    if major != 2:
        raise EwfFormatError(f"{name} has EWF2 version {major}.{minor}, not 2.x")

    sections = []
    offset = end - SECTION_V2_SIZE
    seen = set()
    while True:
        if offset < FILE_HEADER_V2_SIZE or offset in seen:
            raise EwfFormatError(f"{name} has a broken section chain at {offset}")
        seen.add(offset)
        fh.seek(offset)
        raw = _read_exactly(fh, SECTION_V2_SIZE)
        if zlib.adler32(raw[:60]) & 0xFFFFFFFF != struct.unpack_from("<I", raw, 60)[0]:
            raise EwfFormatError(f"{name}: the section descriptor at {offset} fails "
                                 f"its checksum")
        stype, flags, previous, size, _dsize, _pad = _SECTION_V2.unpack_from(raw)
        data_offset = offset - size
        if data_offset < FILE_HEADER_V2_SIZE:
            raise EwfFormatError(f"{name}: the section at {offset} claims more data "
                                 f"than precedes it")
        sections.append((stype, flags, data_offset, size))
        if previous == 0:
            break
        if previous >= offset:
            raise EwfFormatError(f"{name} has a section chain that does not go back")
        offset = previous
    sections.reverse()
    return segment_number, method, set_id, sections


def _parse_serialized(raw, method):
    """A device information or case data section: one object's tags and values.

    The string is compressed with the segment's compression method and is UTF-16
    with a byte-order mark. Values escape line feed, carriage return and tab as
    0x0001, 0x0002 and 0x0003.
    """
    if method == 1:
        raw = _inflate(raw)
    elif method != 0:
        raise EwfFormatError(f"compression method {method} is not supported")
    text = raw.decode("utf-16", "replace")
    lines = text.split("\n")
    if len(lines) < 4:
        return {}
    tags, values = lines[2].split("\t"), lines[3].split("\t")
    table = str.maketrans({"\x01": "\n", "\x02": "\r", "\x03": "\t"})
    return {tag.strip(): value.translate(table)
            for tag, value in zip(tags, values) if tag.strip()}


def _compressed_bound(size):
    """The most bytes a zlib stream of ``size`` bytes can occupy.

    Deflate falls back to stored blocks when nothing compresses, which costs five
    bytes per 65,535-byte block, on top of the zlib header and the Adler-32. The
    margin is deliberately generous: a few bytes short would truncate a chunk, and a
    few kilobytes long costs one short read.
    """
    return size + 5 * (size // 65535 + 1) + 1024


def _inflate(data):
    """Inflate a zlib stream, tolerating trailing bytes after its end."""
    obj = zlib.decompressobj()
    try:
        out = obj.decompress(data)
    except zlib.error as exc:
        raise EwfFormatError(f"cannot inflate section data: {exc}") from exc
    return out


def _parse_header_text(text):
    """The tab-delimited header section into a dict of friendly names."""
    lines = [ln for ln in text.replace("\r\n", "\n").split("\n")]
    fields = None
    for i, line in enumerate(lines):
        parts = line.split("\t")
        if len(parts) > 2 and all(p.strip() in _HEADER_FIELDS for p in parts if p.strip()):
            fields = [p.strip() for p in parts]
            values = lines[i + 1].split("\t") if i + 1 < len(lines) else []
            break
    if not fields:
        return {}
    out = {}
    for key, value in zip(fields, values):
        value = value.strip()
        if not value:
            continue
        out[_HEADER_FIELDS.get(key, key)] = value
    return out


# ---------------------------------------------------------------- the reader

def _af_number(entry):
    """A number AFFLIB keeps in a segment's argument. FTK Imager writes some of them,
    the sector size among them, as decimal text in the data instead."""
    arg, data = entry
    text = data.strip(b"\x00 ")
    return int(text) if not arg and text.isdigit() else arg


def _af_meaning(key, entry):
    """What a segment says, for comparing two files' copies of it: the same sector
    size can be stored as text in one file of an AFD and as an argument in another."""
    return _af_number(entry) if key in ("pagesize", "segsize", "sectorsize") else entry[1]


def _af_quad(entry):
    """An AFF 64-bit value, stored as its low 32 bits then its high 32 bits."""
    if entry is None or len(entry[1]) != 8:
        return None
    low, high = struct.unpack(">II", entry[1])
    return (high << 32) | low


class _Table:
    """One table section: a run of chunk offsets sharing a base offset.

    ``entries`` stays as the raw little-endian bytes the file holds and each
    offset is unpacked on demand. Reading them through ``array("I")`` instead
    would take the item size from the host's C unsigned int and need a byteswap
    on a big-endian host, so it would depend on the machine rather than on the
    format, and a wrong item size would misparse the table silently.
    """

    __slots__ = ("segment", "base", "entries", "first_chunk", "limit")

    def __init__(self, segment, base, entries, first_chunk, limit):
        self.segment = segment
        self.base = base
        self.entries = entries
        self.first_chunk = first_chunk
        self.limit = limit


class LogicalEntry:
    """One entry of an L01's file tree, with its values as the ltree stores them.

    ``names`` is the path from the root as a tuple; a name can itself hold "/" or
    "\\", so ``path``, the names joined by "/", is for display. ``values`` holds
    every column exactly as stored, and the rest are read from it: ``size`` (ls),
    ``extents`` ((offset, size) runs in the media data, from be), ``flags`` (opr),
    ``duplicate_offset`` (du), ``md5`` and ``sha1`` (ha and sha, None when unset),
    and ``times`` (the POSIX times among cr, ac, wr, mo, dl and aq that are set).
    An entry can be a folder and hold data of its own at once.
    """

    __slots__ = ("names", "values", "parent", "children", "size", "extents",
                 "extent_types", "flags", "duplicate_offset", "md5", "sha1", "times")

    def __init__(self, names, values, parent):
        self.names = names
        self.values = values
        self.parent = parent
        self.children = []
        where = self.path or "the root entry"
        self.size = _l01_int(values.get("ls"), 10, where, "file size") or 0
        self.flags = _l01_int(values.get("opr"), 10, where, "flags") or 0
        self.duplicate_offset = _l01_int(values.get("du"), 10, where,
                                         "duplicate data offset")
        self.extents, self.extent_types = _l01_extents(values.get("be", ""), where)
        self.md5 = _l01_digest(values.get("ha"), 32)
        self.sha1 = _l01_digest(values.get("sha"), 40)
        self.times = {k: int(values[k]) for k in _L01_TIMES
                      if values.get(k, "").lstrip("-").isdigit()}

    @property
    def name(self):
        return self.names[-1] if self.names else self.values.get("n", "")

    @property
    def path(self):
        return "/".join(self.names)

    @property
    def is_folder(self):
        """True when the entry is marked as a parent (p) or carries the folder flag."""
        return self.values.get("p") == "1" or bool(self.flags & L01_FLAG_FOLDER)

    def __repr__(self):
        return f"<LogicalEntry {self.path!r} size={self.size}>"


def _l01_int(text, base, where, what):
    if text is None or text == "":
        return None
    try:
        return int(text, base)
    except ValueError:
        raise EwfFormatError(f"L01 entry {where}: its {what} {text!r} is not a number") from None


def _l01_digest(text, width):
    text = (text or "").strip().lower()
    if len(text) == width and text.strip("0") and all(c in "0123456789abcdef" for c in text):
        return text
    return None


def _l01_extents(text, where):
    """The be value: a count, then per extent an optional type, a hexadecimal offset
    into the media data and a hexadecimal size."""
    tokens = text.split()
    if not tokens:
        return [], []
    count = _l01_int(tokens[0], 10, where, "extent count")
    rest = tokens[1:]
    if len(rest) == 2 * count:
        types = []
        pairs = [(rest[2 * k], rest[2 * k + 1]) for k in range(count)]
    elif len(rest) == 3 * count:
        types = [rest[3 * k] for k in range(count)]
        pairs = [(rest[3 * k + 1], rest[3 * k + 2]) for k in range(count)]
    else:
        raise EwfFormatError(f"L01 entry {where}: its extents {text!r} do not hold "
                             f"{count} offset and size pairs")
    extents = [(_l01_int(o, 16, where, "extent offset"),
                _l01_int(n, 16, where, "extent size")) for o, n in pairs]
    return extents, types


def _parse_ltree_text(text):
    """The media data size (rec tb) and the root entry of an L01's ltree text."""
    lines = text.split("\n")
    categories = {}
    root = None
    i = 1                                   # line 1 is the number of categories
    while i < len(lines):
        name = lines[i]
        if not name:
            i += 1
            continue
        if name == "entry" and root is None:
            root, i = _parse_l01_entries(lines, i + 1)
            continue
        j = i + 1
        while j < len(lines) and lines[j]:
            j += 1
        categories.setdefault(name, lines[i + 1:j])
        i = j
    rec = categories.get("rec", [])
    record = dict(zip(rec[0].split("\t"), rec[1].split("\t"))) if len(rec) >= 2 else {}
    media_size = _l01_int(record.get("tb"), 10, "records", "total size")
    if media_size is None:
        raise EwfFormatError("the L01 ltree records no total size (rec tb), which is "
                             "how much file content its chunks hold")
    if root is None:
        raise EwfFormatError("the L01 ltree has no entry category, which is where its "
                             "files are described")
    return media_size, root


def _parse_l01_entries(lines, start):
    """The entry category's tree. Each entry is a line giving its number of child
    entries, a line of tab-separated values in the order of the category's column
    line, and then its children, each the same way."""
    if start + 1 >= len(lines):
        raise EwfFormatError("the L01 ltree ends inside its entry category")
    columns = lines[start + 1].split("\t")

    def read(pos):
        try:
            _first, count = lines[pos].split("\t")
            count = int(count)
            values = lines[pos + 1].split("\t")
        except (IndexError, ValueError):
            raise EwfFormatError(f"the L01 ltree entry list is malformed or cut short at "
                                 f"line {pos + 1}") from None
        return dict(zip(columns, values)), count, pos + 2

    values, count, pos = read(start + 2)
    root = LogicalEntry((), values, None)
    stack = [[root, count]]
    while stack:
        node, remaining = stack[-1]
        if not remaining:
            stack.pop()
            continue
        stack[-1][1] -= 1
        values, count, pos = read(pos)
        child = LogicalEntry(node.names + (values.get("n", ""),), values, node)
        node.children.append(child)
        stack.append([child, count])
    return root, pos


class _LogicalFile(io.RawIOBase):
    """An L01 entry's content as a seekable file object, read from the image's
    media data through the runs the entry's values describe."""

    def __init__(self, image, runs, size):
        super().__init__()
        self._image = image
        self._runs = runs                   # (media offset or None, length, fill byte)
        self._starts = []
        at = 0
        for _offset, length, _fill in runs:
            self._starts.append(at)
            at += length
        self._size = size
        self._pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self._pos

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            pos = offset
        elif whence == os.SEEK_CUR:
            pos = self._pos + offset
        elif whence == os.SEEK_END:
            pos = self._size + offset
        else:
            raise ValueError(f"invalid whence {whence}")
        if pos < 0:
            raise ValueError("negative seek position")
        self._pos = pos
        return pos

    def readinto(self, buffer):
        view = memoryview(buffer).cast("B")
        done = 0
        while done < len(view) and self._pos < self._size:
            k = bisect.bisect_right(self._starts, self._pos) - 1
            offset, length, fill = self._runs[k]
            within = self._pos - self._starts[k]
            take = min(len(view) - done, length - within)
            if offset is None:
                view[done:done + take] = bytes([fill]) * take
            else:
                self._image.seek(offset + within)
                view[done:done + take] = self._image.read(take)
            done += take
            self._pos += take
        return done


class EwfImage:
    """An EWF-E01, EWF-S01, EWF2-Ex01, AFF or AFD acquisition, read as one seekable stream,
    or an EWF-L01, read as its media data with its entries in ``logical_entries``.

    ``media_size`` is the size of the disk that was acquired, which is what
    ``seek`` and ``read`` address. The segment files themselves are an
    implementation detail and their sizes are not it.
    """

    def __init__(self, path, segments=None):
        self._afd = None if segments else _afd_directory(path)
        if segments:
            self.paths = list(segments)
        elif self._afd:
            self.paths = _afd_members(self._afd)
        elif _is_aff(path):
            self.paths = [os.path.abspath(path)]
        else:
            self.paths = ewf_segments(path)
        self._handles: OrderedDict[int, object] = OrderedDict()
        self._cache: OrderedDict[int, bytes] = OrderedDict()
        self._pos = 0
        self._closed = False

        self.sector_size = 0
        self.sectors_per_chunk = 0
        self.sector_count = 0
        self.chunk_count = 0
        self.format = FORMAT_E01
        self.media_type = None
        self.compression_level = None
        self.metadata: dict[str, str] = {}
        self.stored_hashes: dict[str, str] = {}
        self.checksum_errors: list[int] = []
        self.chunk_size = 0
        self.media_size = 0
        self.size = 0
        self.sizes: list[int] = []
        self._indexed_chunks = 0
        self.missing_page_ranges: list[tuple[int, int]] = []
        self.missing_page_count = 0
        self.bad_sectors = None
        self._aff_pages: dict[int, tuple[int, int, int, int]] = {}
        self._aff_badflag = b""
        self.logical_root = None
        self.logical_entries: list[LogicalEntry] = []
        self._l01_media_size = None

        self._tables: list[_Table] = []
        self._table_starts: list[int] = []
        self._index()

    # -- construction ------------------------------------------------------

    def _handle(self, i):
        fh = self._handles.get(i)
        if fh is None:
            if len(self._handles) >= MAX_OPEN:
                _old, stale = self._handles.popitem(last=False)
                stale.close()
            fh = open(self.paths[i], "rb")
            self._handles[i] = fh
        else:
            self._handles.move_to_end(i)
        return fh

    def _index(self):
        """Walk every segment once and build the chunk offset index."""
        with open(self.paths[0], "rb") as fh:
            magic = fh.read(8)
        if magic == LEF2_SIGNATURE:
            raise EwfFormatError(
                f"{os.path.basename(self.paths[0])} is Lx01 logical evidence, which "
                f"ewfprobe does not read")
        logical = magic == LVF_SIGNATURE
        if magic == SIGNATURE_V2:
            self._index_v2()
            return
        if magic == AF_HEADER:
            self._index_aff()
            return
        chunks = 0
        volume_seen = False
        last_name = None
        for i, path in enumerate(self.paths):
            fh = self._handle(i)
            size_on_disk = os.path.getsize(path)
            expect_segment = i + 1
            for segno, name, offset, size, _next in _sections(fh, path):
                if segno != expect_segment:
                    raise EwfFormatError(
                        f"{os.path.basename(path)} says it is segment {segno}, "
                        f"but it sits at position {expect_segment} of the set")
                last_name = name
                if name in ("header", "header2") and not self.metadata:
                    fh.seek(offset)
                    raw = _inflate(_read_exactly(fh, size))
                    if name == "header2":
                        text = raw.decode("utf-16-le", "replace")
                    else:
                        text = raw.decode("latin-1", "replace")
                    self.metadata = _parse_header_text(text)
                elif name in ("volume", "disk") and not volume_seen:
                    fh.seek(offset)
                    self._parse_volume(_read_exactly(fh, min(size, 1052)))
                    volume_seen = True
                elif name == "table":
                    chunks += self._parse_table(fh, i, offset, size, chunks, size_on_disk)
                elif name in ("hash", "digest"):
                    fh.seek(offset)
                    self._parse_hashes(name, _read_exactly(fh, size))
                elif name == "ltree" and logical and self.logical_root is None:
                    fh.seek(offset)
                    self._parse_ltree(_read_exactly(fh, size))

            if last_name == "next" and i == len(self.paths) - 1:
                raise EwfIncompleteSetError(
                    f"{os.path.basename(path)} ends with a 'next' section, so the "
                    f"acquisition continues in a further segment that is not beside "
                    f"it. Put every segment of the set in one folder before opening "
                    f"it; reading only the segments present would report the missing "
                    f"data as empty.")

        if not volume_seen:
            raise EwfFormatError("the image carries no volume section")
        if logical:
            self.format = FORMAT_L01
            if self.logical_root is None:
                raise EwfFormatError(
                    "the L01 carries no ltree section, which is where its files are "
                    "described")
        if self.format == FORMAT_S01:
            level = self.metadata.get("compression_level")
            if level is not None:
                self.compression_level = SMART_COMPRESSION.get(level, f"unknown ({level})")
        if not self._tables:
            raise EwfFormatError("the image carries no chunk table")
        self._finish_index(chunks)

    def _finish_index(self, chunks):
        self.chunk_size = self.sectors_per_chunk * self.sector_size
        if self.format == FORMAT_L01:
            # An L01's volume section does not describe its data: the sector count
            # times the sector size is not the content's size, the ltree's tb is.
            self.media_size = self._l01_media_size
        else:
            self.media_size = self.sector_count * self.sector_size
        # ``size`` is the byte length of the acquired disk, which is what seek
        # and read address. A consumer that already handles a joined set of raw
        # segments asks an image object for exactly this, so answering it here
        # lets such a consumer take an E01 without a special case.
        self.size = self.media_size
        # The size each segment FILE occupies on disk. These sum to the size of
        # the acquisition on disk, not to media_size, because the chunks in them
        # are usually compressed.
        self.sizes = [os.path.getsize(p) for p in self.paths]
        self._indexed_chunks = chunks
        if chunks < self._needed_chunks():
            raise EwfIncompleteSetError(
                f"the chunk tables cover {chunks} chunks but the volume section "
                f"describes {self._needed_chunks()}; the segment set is incomplete")

    def _index_v2(self):
        """The EWF2 counterpart of ``_index``."""
        self.format = FORMAT_EX01
        device, case = None, None
        set_id = None
        chunks = 0
        for i, path in enumerate(self.paths):
            fh = self._handle(i)
            name = os.path.basename(path)
            segno, method, this_set, sections = _sections_v2(fh, path)
            if segno != i + 1:
                raise EwfFormatError(f"{name} says it is segment {segno}, but it sits "
                                     f"at position {i + 1} of the set")
            if set_id is None:
                set_id = this_set
            elif this_set != set_id:
                raise EwfFormatError(f"{name} belongs to a different acquisition than "
                                     f"{os.path.basename(self.paths[0])}")
            if method == 2:
                raise EwfFormatError(
                    f"{name} is compressed with bzip2. ewfprobe does not read bzip2 "
                    f"Ex01 images: no sample was available to validate a reader against")
            if method not in (0, 1):
                raise EwfFormatError(f"{name} names compression method {method}")
            self.compression_level = V2_COMPRESSION_METHODS[method]
            for stype, flags, offset, size in sections:
                if flags & V2_SECTION_ENCRYPTED or stype == V2_ENCRYPTION_KEYS:
                    raise EwfFormatError(
                        f"{name} is encrypted. Ex01 encryption is not publicly "
                        f"documented, so ewfprobe cannot read it")
                if stype in (V2_DEVICE_INFORMATION, V2_CASE_DATA):
                    parsed = None
                    if (stype == V2_DEVICE_INFORMATION and device is None) or \
                            (stype == V2_CASE_DATA and case is None):
                        fh.seek(offset)
                        parsed = _parse_serialized(_read_exactly(fh, size), method)
                    if stype == V2_DEVICE_INFORMATION and device is None:
                        device = parsed
                    elif stype == V2_CASE_DATA and case is None:
                        case = parsed
                elif stype == V2_SECTOR_TABLE:
                    chunks += self._parse_table_v2(fh, i, offset, chunks)
                elif stype in (V2_MD5, V2_SHA1):
                    fh.seek(offset)
                    self._parse_hashes_v2(stype, _read_exactly(fh, size))
            if sections and sections[-1][0] == V2_NEXT and i == len(self.paths) - 1:
                raise EwfIncompleteSetError(
                    f"{name} ends with a 'next' section, so the acquisition continues "
                    f"in a further segment that is not beside it. Put every segment "
                    f"of the set in one folder before opening it; reading only the "
                    f"segments present would report the missing data as empty.")

        if not device or not case:
            raise EwfFormatError("the image carries no device information or case data")
        try:
            self.sector_count = int(device["ts"])
            self.sector_size = int(device["bp"])
            self.sectors_per_chunk = int(case["sb"])
        except (KeyError, ValueError) as exc:
            raise EwfFormatError(f"the image does not record its geometry: {exc}") from exc
        if not self.sector_count or not self.sector_size or not self.sectors_per_chunk:
            raise EwfFormatError(
                "the image gives a zero sector size, chunk size or sector count")
        try:
            self.chunk_count = int(case.get("tb") or 0)
        except ValueError:
            self.chunk_count = 0
        drive = device.get("dt", "")
        self.media_type = (V2_DRIVE_TYPES.get(drive, f"unknown ({drive})")
                           if drive else None)
        for source in (case, device):
            for tag, value in source.items():
                if tag in _V2_FIELDS and value.strip():
                    self.metadata[_V2_FIELDS[tag]] = value.strip()
        if not self._tables:
            raise EwfFormatError("the image carries no chunk table")
        self._finish_index(chunks)

    def _parse_ltree(self, data):
        """The ltree section: check its header and text, then read the file tree."""
        if len(data) < _LTREE_HEADER.size:
            raise EwfFormatError("the L01 ltree section is too short for its header")
        digest, size, adler, _reserved = _LTREE_HEADER.unpack_from(data)
        head = bytearray(data[:_LTREE_HEADER.size])
        head[24:28] = b"\x00" * 4
        if zlib.adler32(bytes(head)) & 0xFFFFFFFF != adler:
            raise EwfFormatError("the L01 ltree header does not match its checksum")
        text = data[_LTREE_HEADER.size:_LTREE_HEADER.size + size]
        if len(text) != size:
            raise EwfFormatError(f"the L01 ltree holds {len(text)} bytes of text where its "
                                 f"header says {size}")
        if hashlib.md5(text).digest() != digest:
            raise EwfFormatError("the L01 ltree text does not match the MD5 its header "
                                 "records")
        # The specification notes names can hold unpaired surrogates, which a strict
        # decoder refuses; they are kept as they are.
        self._l01_media_size, root = _parse_ltree_text(
            text.decode("utf-16-le", "surrogatepass"))
        self.logical_root = root
        order = []
        stack = list(reversed(root.children))
        while stack:
            entry = stack.pop()
            order.append(entry)
            stack.extend(reversed(entry.children))
        self.logical_entries = order

    def _entry_runs(self, entry):
        """Where an L01 entry's content lies in the media data, as (offset, length,
        fill) runs covering its size."""
        where = entry.path or "the root entry"
        if entry.extent_types:
            raise EwfFormatError(f"L01 entry {where}: its extents carry the type "
                                 f"{entry.extent_types[0]!r}, which ewfprobe does not read")
        size = entry.size
        if entry.flags & L01_FLAG_SPARSE:
            # The data is one stored byte, repeated, unless a duplicate data offset
            # says where the full content is stored instead.
            if entry.duplicate_offset is not None:
                runs = [(entry.duplicate_offset, size, 0)]
            elif entry.extents and entry.extents[0][1] >= 1:
                self.seek(entry.extents[0][0])
                byte = self.read(1)
                if len(byte) != 1:
                    raise EwfFormatError(f"L01 entry {where}: its data lies past the media "
                                         f"data")
                return [(None, size, byte[0])] if size else []
            else:
                raise EwfFormatError(f"L01 entry {where}: it is marked sparse and stores "
                                     f"no data")
        elif entry.duplicate_offset is not None:
            raise EwfFormatError(f"L01 entry {where}: it has a duplicate data offset "
                                 f"without the sparse flag, which ewfprobe does not read")
        else:
            runs, need = [], size
            for offset, length in entry.extents:
                if need <= 0:
                    break
                runs.append((offset, min(length, need), 0))
                need -= length
            if need > 0:
                raise EwfFormatError(f"L01 entry {where}: its extents hold "
                                     f"{size - need:,} of its {size:,} bytes")
        for offset, length, _fill in runs:
            if offset < 0 or offset + length > self.media_size:
                raise EwfFormatError(f"L01 entry {where}: its data lies past the media "
                                     f"data")
        return runs

    def open_entry(self, entry):
        """An L01 entry's content as a seekable, read-only file object."""
        if self.format != FORMAT_L01:
            raise EwfFormatError("only an L01 holds entries")
        return io.BufferedReader(_LogicalFile(self, self._entry_runs(entry), entry.size),
                                 buffer_size=1 << 16)

    def read_entry(self, entry):
        """An L01 entry's content, whole."""
        with self.open_entry(entry) as fh:
            return fh.read()

    def find_entry(self, path):
        """The L01 entry whose path (its names joined by "/") is ``path``."""
        path = path.strip("/")
        for entry in self.logical_entries:
            if entry.path == path:
                return entry
        raise EwfFormatError(f"no L01 entry has the path {path!r}")

    def _walk_aff(self, i):
        """One AFF file's segments, walked once: where each page is, and the content
        of every small segment."""
        path = self.paths[i]
        name_of_file = os.path.basename(path)
        fh = self._handle(i)
        end = os.path.getsize(path)
        fh.seek(0)
        if _read_exactly(fh, len(AF_HEADER)) != AF_HEADER:
            raise EwfFormatError(f"{name_of_file} is not an AFF file")
        pages: dict[int, tuple[int, int, int]] = {}
        small: dict[str, tuple[int, bytes]] = {}
        offset = len(AF_HEADER)
        while offset < end:
            if offset + _AF_SEGHEAD.size > end:
                raise EwfIncompleteSetError(
                    f"{name_of_file} ends inside a segment header at {offset}; the file "
                    f"is truncated")
            fh.seek(offset)
            magic, name_len, data_len, arg = _AF_SEGHEAD.unpack(
                _read_exactly(fh, _AF_SEGHEAD.size))
            if magic != b"AFF\x00":
                raise EwfFormatError(f"{name_of_file} has no segment header at {offset}")
            data_offset = offset + _AF_SEGHEAD.size + name_len
            tail = data_offset + data_len
            if tail + _AF_SEGTAIL.size > end:
                raise EwfIncompleteSetError(
                    f"{name_of_file} ends inside the segment at {offset}; the file is "
                    f"truncated")
            name = _read_exactly(fh, name_len).decode("utf-8", "replace")
            fh.seek(tail)
            tail_magic, seg_len = _AF_SEGTAIL.unpack(_read_exactly(fh, _AF_SEGTAIL.size))
            if tail_magic != b"ATT\x00" or seg_len != tail + _AF_SEGTAIL.size - offset:
                raise EwfFormatError(f"{name_of_file}: the segment at {offset} has no "
                                     f"matching tail")
            if name.endswith(AF_AES256_SUFFIX) or name.startswith("affkey"):
                raise EwfFormatError(
                    f"{name_of_file} is encrypted. ewfprobe does not read encrypted AFF")
            page = _AF_PAGE_NAME.fullmatch(name)
            if page:
                pages[int(page.group(1))] = (data_offset, data_len, arg)
            elif name and data_len <= _AFF_MAX_SMALL:
                fh.seek(data_offset)
                small[name] = (arg, _read_exactly(fh, data_len))
            offset = tail + _AF_SEGTAIL.size
        return pages, small, end

    def _same_page(self, n, first, second):
        """A page stored in two files of an AFD has to be the same page twice."""
        def stored(location):
            i, offset, length, arg = location
            fh = self._handle(i)
            fh.seek(offset)
            return arg, _read_exactly(fh, length)
        if stored(first) != stored(second):
            raise EwfFormatError(
                f"page {n} is stored in both {os.path.basename(self.paths[first[0]])} and "
                f"{os.path.basename(self.paths[second[0]])} with different contents; "
                f"AFFLIB reads it from whichever file the directory lists first, so the "
                f"image has no single reading")

    def _index_aff(self):
        """Walk an AFF file's segments once, or each file of an AFD, keeping page
        locations and metadata.

        An AFD's files are merged the way AFFLIB merges them: a segment is read from
        the first file that holds it, in numbered order, and the image size is the
        largest any file records (afd_get_seg and afd_vstat in lib/vnode_afd.cpp).
        AFFLIB takes the files in the order the directory lists them, which differs
        between filesystems, so a page or a hash that two files record differently
        is refused rather than resolved by that order.
        """
        self.format = FORMAT_AFD if (self._afd or len(self.paths) > 1) else FORMAT_AFF
        label = os.path.basename(self._afd or self.paths[0])
        small: dict[str, tuple[int, bytes]] = {}
        holder: dict[str, int] = {}
        image_sizes = []
        for i, path in enumerate(self.paths):
            pages, seen, end = self._walk_aff(i)
            self.sizes.append(end)
            for key, value in seen.items():
                if key == "imagesize" and _af_quad(value) is not None:
                    image_sizes.append(_af_quad(value))
                if key not in small:
                    small[key], holder[key] = value, i
                elif (key in _AFD_MUST_AGREE
                      and _af_meaning(key, small[key]) != _af_meaning(key, value)):
                    raise EwfFormatError(
                        f"{label}: {os.path.basename(self.paths[holder[key]])} and "
                        f"{os.path.basename(path)} record different {key} values")
            for n, (offset, length, arg) in pages.items():
                if n in self._aff_pages:
                    self._same_page(n, self._aff_pages[n], (i, offset, length, arg))
                else:
                    self._aff_pages[n] = (i, offset, length, arg)

        page_size = _af_number(small.get("pagesize") or small.get("segsize") or (0, b""))
        if not page_size:
            raise EwfFormatError(f"{label} records no page size")
        if not image_sizes:
            where = (", in an AFD into one of its files," if self.format == FORMAT_AFD
                     else "")
            raise EwfIncompleteSetError(
                f"{label} records no image size, which AFFLIB writes{where} when an "
                f"acquisition finishes; reading it would report missing data as empty")
        image_size = max(image_sizes)
        sector_arg = _af_number(small.get("sectorsize", (0, b"")))
        self._aff_badflag = small.get("badflag", (0, b""))[1]
        self.bad_sectors = _af_quad(small.get("badsectors"))
        for key, algo, width in (("md5", "MD5", 16), ("sha1", "SHA1", 20),
                                 ("sha256", "SHA256", 32)):
            digest = small.get(key, (0, b""))[1]
            if len(digest) == width and any(digest):
                self.stored_hashes[algo] = digest.hex()
        gid = small.get("image_gid", (0, b""))[1]
        if gid:
            self.metadata["image_gid"] = gid.hex()
        for key, (arg, data) in small.items():
            if (key in _AF_STRUCTURAL or _AF_PAGE_HASH_NAME.fullmatch(key)
                    or key.endswith(AF_SIG256_SUFFIX)):
                continue
            try:
                value = data.decode("utf-8").strip("\x00").strip()
            except UnicodeDecodeError:
                continue
            if not value and arg:
                value = str(arg)
            if value and value.isprintable():
                self.metadata[_AFF_FIELDS.get(key, key)] = value

        self.chunk_size = page_size
        self.media_size = image_size
        self.size = image_size
        self.sector_size = sector_arg
        self.sector_count = image_size // sector_arg if sector_arg else 0
        self.sectors_per_chunk = page_size // sector_arg if sector_arg else 0
        self.compression_level = None
        needed = self._needed_chunks()
        self.chunk_count = needed
        self._indexed_chunks = sum(1 for n in self._aff_pages if n < needed)
        # Built from the pages present, never by counting up to the image size: the
        # size is read from the file, and a damaged one can claim petabytes.
        expect = 0
        for n in sorted(p for p in self._aff_pages if p < needed):
            if n > expect:
                self.missing_page_ranges.append((expect, n - 1))
            expect = n + 1
        if expect < needed:
            self.missing_page_ranges.append((expect, needed - 1))
        self.missing_page_count = sum(b - a + 1 for a, b in self.missing_page_ranges)

    def _chunk_data_aff(self, n):
        location = self._aff_pages.get(n)
        if location is None:
            # AFFLIB fills a page that is not in the file with the image's bad-sector
            # marker (af_get_page in lib/afflib_pages.cpp); so does this reader, and
            # the page is counted in missing_page_ranges.
            if not self._aff_badflag:
                raise EwfFormatError(f"page {n} is not in the file, and the image records "
                                     f"no bad-sector marker to stand in for it")
            flag = self._aff_badflag
            return (flag * (self.chunk_size // len(flag) + 1))[:self.chunk_size]
        i, offset, length, arg = location
        fh = self._handle(i)
        fh.seek(offset)
        raw = _read_exactly(fh, length)
        if not arg & AF_PAGE_COMPRESSED:
            return raw
        algorithm = arg & AF_PAGE_COMP_ALG_MASK
        if algorithm == AF_PAGE_COMP_ALG_ZERO:
            if length != 4:
                raise EwfFormatError(f"page {n} is a zero page with {length} bytes, not 4")
            return b"\x00" * min(struct.unpack(">I", raw)[0], self.chunk_size)
        if algorithm == AF_PAGE_COMP_ALG_ZLIB:
            try:
                return zlib.decompressobj().decompress(raw, self.chunk_size)
            except zlib.error as exc:
                raise EwfFormatError(f"cannot inflate page {n}: {exc}") from exc
        if algorithm == AF_PAGE_COMP_ALG_LZMA:
            try:
                import lzma  # pylint: disable=import-outside-toplevel
            except ImportError as exc:
                raise EwfFormatError(
                    f"page {n} is LZMA-compressed and this Python has no lzma module"
                ) from exc
            try:
                decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
                return decoder.decompress(raw, max_length=self.chunk_size)
            except lzma.LZMAError as exc:
                raise EwfFormatError(f"cannot decompress LZMA page {n}: {exc}") from exc
        raise EwfFormatError(f"page {n} uses compression algorithm {algorithm:#06x}, "
                             f"which ewfprobe does not read")

    def _parse_table_v2(self, fh, segment_index, offset, first_expected):
        fh.seek(offset)
        header = _read_exactly(fh, TABLE_V2_HEADER_SIZE)
        first, count, _pad, checksum = _TABLE_V2_HEADER.unpack_from(header)
        if zlib.adler32(header[:16]) & 0xFFFFFFFF != checksum:
            raise EwfFormatError(f"the chunk table at {offset} fails its header checksum")
        if count == 0:
            return 0
        if first != first_expected:
            raise EwfFormatError(
                f"the chunk table at {offset} starts at chunk {first}, where {first_expected} "
                f"was expected; ewfprobe reads only contiguous chunk tables")
        raw = _read_exactly(fh, count * _TABLE_V2_ENTRY.size)
        footer = struct.unpack("<I", _read_exactly(fh, 4))[0]
        if zlib.adler32(raw) & 0xFFFFFFFF != footer:
            raise EwfFormatError(f"the chunk table at {offset} fails its entry checksum")
        self._table_starts.append(first)
        self._tables.append(_Table(segment_index, 0, raw, first, 0))
        return count

    def _parse_hashes_v2(self, stype, data):
        n = 16 if stype == V2_MD5 else 20
        if len(data) < n + 4:
            return
        digest = data[:n]
        if zlib.adler32(digest) & 0xFFFFFFFF != struct.unpack_from("<I", data, n)[0]:
            raise EwfFormatError("a stored hash section fails its checksum")
        if any(digest):
            self.stored_hashes["MD5" if stype == V2_MD5 else "SHA1"] = digest.hex()

    def _chunk_data_v2(self, n):
        i = bisect.bisect_right(self._table_starts, n) - 1
        if i < 0:
            raise EwfFormatError(f"chunk {n} is before the first table")
        table = self._tables[i]
        k = n - table.first_chunk
        if (k + 1) * _TABLE_V2_ENTRY.size > len(table.entries):
            raise EwfFormatError(f"chunk {n} is past the end of the chunk tables")
        offset, size, flags = _TABLE_V2_ENTRY.unpack_from(table.entries,
                                                          k * _TABLE_V2_ENTRY.size)
        if flags & V2_CHUNK_COMPRESSED and flags & V2_CHUNK_PATTERN_FILL:
            # The offset field holds an eight-byte pattern that fills the chunk.
            pattern = struct.pack("<Q", offset)
            return (pattern * (self.chunk_size // 8 + 1))[:self.chunk_size]
        if size > _compressed_bound(self.chunk_size) + 4:
            raise EwfFormatError(f"chunk {n} claims {size:,} bytes, more than a chunk "
                                 f"of {self.chunk_size:,} bytes can occupy")
        fh = self._handle(table.segment)
        fh.seek(offset)
        raw = _read_exactly(fh, size)
        if flags & V2_CHUNK_COMPRESSED:
            return _inflate(raw)
        if flags & V2_CHUNK_CHECKSUMED:
            data, stored = raw[:-4], struct.unpack("<I", raw[-4:])[0]
            if zlib.adler32(data) & 0xFFFFFFFF != stored and n not in self.checksum_errors:
                self.checksum_errors.append(n)
            return data
        return raw

    def _needed_chunks(self):
        if not self.chunk_size:
            return 0
        return (self.media_size + self.chunk_size - 1) // self.chunk_size

    def _parse_volume(self, data):
        if len(data) < 24:
            raise EwfFormatError("the volume section is too short")
        if data[85:85 + len(SMART_SIGNATURE)] == SMART_SIGNATURE:
            # The original layout: byte 0 is a reserved 1, not a media type, and
            # the sector count is 32 bits followed by 20 reserved bytes.
            self.format = FORMAT_S01
            (chunk_count, sectors_per_chunk, bytes_per_sector,
             sector_count) = struct.unpack_from("<IIII", data, 4)
        else:
            self.media_type = MEDIA_TYPES.get(data[0], f"unknown ({data[0]:#04x})")
            (chunk_count, sectors_per_chunk,
             bytes_per_sector) = struct.unpack_from("<III", data, 4)
            sector_count = struct.unpack_from("<Q", data, 16)[0]
            if len(data) >= 56:
                level = data[52]
                self.compression_level = COMPRESSION_LEVELS.get(
                    level, f"unknown ({level:#04x})")
        if not bytes_per_sector or not sectors_per_chunk or not sector_count:
            raise EwfFormatError(
                "the volume section gives a zero sector size, chunk size or sector count")
        self.chunk_count = chunk_count
        self.sectors_per_chunk = sectors_per_chunk
        self.sector_size = bytes_per_sector
        self.sector_count = sector_count

    def _parse_table(self, fh, segment_index, offset, size, first_chunk, size_on_disk):
        fh.seek(offset)
        header = _read_exactly(fh, TABLE_HEADER_SIZE)
        count, _pad1, base, _pad2, _checksum = _TABLE_HEADER.unpack(header)
        if self.format == FORMAT_S01:
            # The original table header is a count and 16 bytes of padding, with
            # no base offset: the entries count from the start of the file.
            base = 0
        if count == 0:
            return 0
        raw = _read_exactly(fh, count * 4)
        table = _Table(segment_index, base, raw, first_chunk, size_on_disk)
        self._table_starts.append(first_chunk)
        self._tables.append(table)
        return count

    def _parse_hashes(self, name, data):
        if name == "hash" and len(data) >= 16:
            self.stored_hashes["MD5"] = data[:16].hex()
        elif name == "digest" and len(data) >= 36:
            md5, sha1 = data[:16], data[16:36]
            if any(md5):
                self.stored_hashes["MD5"] = md5.hex()
            if any(sha1):
                self.stored_hashes["SHA1"] = sha1.hex()

    # -- chunk access ------------------------------------------------------

    def _chunk_location(self, n):
        i = bisect.bisect_right(self._table_starts, n) - 1
        if i < 0:
            raise EwfFormatError(f"chunk {n} is before the first table")
        table = self._tables[i]
        k = n - table.first_chunk
        if (k + 1) * 4 > len(table.entries):
            raise EwfFormatError(f"chunk {n} is past the end of the chunk tables")
        entry = struct.unpack_from("<I", table.entries, k * 4)[0]
        start = table.base + (entry & _OFFSET_MASK)
        compressed = bool(entry & _COMPRESSED_BIT)
        if (k + 2) * 4 <= len(table.entries):
            nxt = struct.unpack_from("<I", table.entries, (k + 1) * 4)[0]
            end = table.base + (nxt & _OFFSET_MASK)
        else:
            end = table.limit
        if end <= start:
            end = table.limit
        # The last entry of a table has no next entry to bound it, so the fallback is
        # the end of the segment file. On a real acquisition that is most of a gigabyte
        # read and allocated to produce one 32 KiB chunk: measured on a 232.9 GiB FTK
        # Imager set of 15 segments, 471 tables whose last-chunk spans summed to 364 GB,
        # the worst single one 1.47 GB. A chunk holds chunk_size bytes, so its stored
        # form cannot be longer than deflate can make of that, whatever the section
        # boundary says.
        end = min(end, start + _compressed_bound(self.chunk_size))
        return table.segment, start, end, compressed

    def _chunk(self, n):
        cached = self._cache.get(n)
        if cached is not None:
            self._cache.move_to_end(n)
            return cached

        want = self.chunk_size
        if n == self._needed_chunks() - 1:
            tail = self.media_size % self.chunk_size
            if tail:
                want = tail

        if self.format == FORMAT_EX01:
            data = self._chunk_data_v2(n)
            return self._keep(n, data, want)
        if self.format in (FORMAT_AFF, FORMAT_AFD):
            data = self._chunk_data_aff(n)
            return self._keep(n, data, want)

        segment, start, end, compressed = self._chunk_location(n)
        fh = self._handle(segment)
        fh.seek(start)
        if compressed:
            # zlib stops at the end of its own stream, so the slice only has to
            # be long enough, which sidesteps the format not recording sizes.
            raw = fh.read(max(0, end - start))
            data = _inflate(raw)
        else:
            data = fh.read(want)
            stored = fh.read(4)
            if len(stored) == 4:
                if zlib.adler32(data) & 0xFFFFFFFF != struct.unpack("<I", stored)[0]:
                    if n not in self.checksum_errors:
                        self.checksum_errors.append(n)
        return self._keep(n, data, want)

    def _keep(self, n, data, want):
        """Fit a decoded chunk to the size it covers and cache it."""
        if len(data) < want:
            data = data + b"\x00" * (want - len(data))
        elif len(data) > want:
            data = data[:want]

        if len(self._cache) >= max(2, min(CHUNK_CACHE,
                                          CHUNK_CACHE_BYTES // max(self.chunk_size, 1))):
            self._cache.popitem(last=False)
        self._cache[n] = data
        return data

    # -- the file-like surface --------------------------------------------

    def seek(self, offset, whence=os.SEEK_SET):
        if self._closed:
            raise ValueError("seek on a closed image")
        if whence == os.SEEK_SET:
            pos = offset
        elif whence == os.SEEK_CUR:
            pos = self._pos + offset
        elif whence == os.SEEK_END:
            pos = self.media_size + offset
        else:
            raise ValueError(f"invalid whence: {whence}")
        if pos < 0:
            raise ValueError("negative seek position")
        self._pos = pos
        return self._pos

    def tell(self):
        return self._pos

    def read(self, n=-1):
        if self._closed:
            raise ValueError("read on a closed image")
        if self._pos >= self.media_size:
            return b""
        remaining = self.media_size - self._pos
        if n is None or n < 0 or n > remaining:
            n = remaining
        out = bytearray()
        pos = self._pos
        while n > 0:
            index = pos // self.chunk_size
            within = pos % self.chunk_size
            chunk = self._chunk(index)
            take = min(n, len(chunk) - within)
            if take <= 0:
                break
            out += chunk[within:within + take]
            pos += take
            n -= take
        self._pos = pos
        return bytes(out)

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return False

    def close(self):
        if self._closed:
            return
        for fh in self._handles.values():
            try:
                fh.close()
            except OSError:
                pass
        self._handles.clear()
        self._cache.clear()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    # -- verification ------------------------------------------------------

    def verify(self, progress=None, block=1 << 22):
        """Recompute the media hashes and compare them with the stored ones.

        Returns a dict with the computed digests, the stored digests, and a
        ``match`` value that is True, False, or None when the acquisition
        recorded no hash to compare against.
        """
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256() if "SHA256" in self.stored_hashes else None
        self.seek(0)
        done = 0
        while True:
            data = self.read(block)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            if sha256 is not None:
                sha256.update(data)
            done += len(data)
            if progress:
                progress(done, self.media_size)
        computed = {"MD5": md5.hexdigest(), "SHA1": sha1.hexdigest()}
        if sha256 is not None:
            computed["SHA256"] = sha256.hexdigest()
        match = None
        for name, value in self.stored_hashes.items():
            if name in computed:
                match = (computed[name] == value) if match in (None, True) else False
        checked, mismatched = 0, []
        for entry in self.logical_entries:
            if entry.md5 is None:
                continue
            digest = hashlib.md5()
            with self.open_entry(entry) as fh:
                while True:
                    piece = fh.read(block)
                    if not piece:
                        break
                    digest.update(piece)
            checked += 1
            if digest.hexdigest() != entry.md5:
                mismatched.append(entry.path)
        return {
            "computed": computed,
            "stored": dict(self.stored_hashes),
            "match": match,
            "bytes": done,
            "checksum_errors": list(self.checksum_errors),
            "missing_page_count": self.missing_page_count,
            "missing_page_ranges": list(self.missing_page_ranges),
            "entry_md5_checked": checked,
            "entry_md5_mismatched": mismatched,
        }

    def info(self):
        """Everything worth printing about the acquisition, as a dict."""
        return {
            "segments": [os.path.basename(p) for p in self.paths],
            "segment_count": len(self.paths),
            "format": self.format,
            "media_type": self.media_type,
            "media_size": self.media_size,
            "sector_size": self.sector_size,
            "sector_count": self.sector_count,
            "sectors_per_chunk": self.sectors_per_chunk,
            "chunk_size": self.chunk_size,
            "chunk_count": self.chunk_count,
            "indexed_chunks": self._indexed_chunks,
            "compression_level": self.compression_level,
            "stored_hashes": dict(self.stored_hashes),
            "missing_page_count": self.missing_page_count,
            "missing_page_ranges": list(self.missing_page_ranges),
            "bad_sectors": self.bad_sectors,
            "entry_count": len(self.logical_entries),
            "entry_md5_count": sum(1 for e in self.logical_entries if e.md5),
            "metadata": dict(self.metadata),
        }


def open_ewf(path, segments=None) -> EwfImage:
    """Open an acquisition ewfprobe reads: an EWF, EWF2 or L01 set from any path in
    it, an AFF file, or an AFD directory from the directory or any file in it."""
    return EwfImage(path, segments=segments)


open_image = open_ewf


# --------------------------------------------------------------------- CLI

def _size(n):
    v = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if v < 1024 or unit == "TiB":
            return f"{v:,.1f} {unit}" if unit != "B" else f"{int(v)} B"
        v /= 1024
    return f"{v} B"


def _cmd_info(args):
    with open_ewf(args.image) as img:
        d = img.info()
        print(f"image           {os.path.basename(args.image)}")
        print(f"segments        {d['segment_count']} ({d['segments'][0]}"
              f"{' .. ' + d['segments'][-1] if d['segment_count'] > 1 else ''})")
        print(f"format          {d['format']}")
        print(f"media type      {d['media_type'] or 'not recorded'}")
        if d["format"] == FORMAT_L01:
            print(f"media data      {d['media_size']:,} bytes ({_size(d['media_size'])}), "
                  f"the content of its entries")
            print(f"entries         {d['entry_count']:,}, {d['entry_md5_count']:,} with a "
                  f"stored MD5")
            print(f"chunk size      {d['chunk_size']:,} bytes")
        else:
            print(f"media size      {d['media_size']:,} bytes ({_size(d['media_size'])})")
        if d["format"] == FORMAT_L01:
            # An L01's volume section declares no chunks; its tables list them.
            print(f"chunks          {d['indexed_chunks']:,}")
        else:
            if d["sector_size"]:
                print(f"sector size     {d['sector_size']:,} bytes")
                print(f"sectors         {d['sector_count']:,}")
            else:
                print("sector size     not recorded")
            unit = "page size " if d["format"] in (FORMAT_AFF, FORMAT_AFD) else "chunk size"
            print(f"{unit}      {d['chunk_size']:,} bytes "
                  f"({d['sectors_per_chunk']} sectors)")
            print(f"chunks          {d['indexed_chunks']:,} indexed, "
                  f"{d['chunk_count']:,} declared")
        print(f"compression     {d['compression_level'] or 'not recorded'}")
        if d["bad_sectors"] is not None:
            print(f"bad sectors     {d['bad_sectors']:,} recorded")
        if d["missing_page_count"]:
            print(f"missing pages   {d['missing_page_count']:,}, read as the "
                  f"bad-sector marker")
        for name, value in d["stored_hashes"].items():
            print(f"stored {name:<9}{value}")
        if d["metadata"]:
            print("metadata")
            for key, value in d["metadata"].items():
                print(f"  {key:<26}{value}")
    return 0


def _progress(done, total):
    if not total:
        return
    pct = 100.0 * done / total
    sys.stderr.write(f"\r  {pct:5.1f}%  {_size(done)} of {_size(total)}")
    sys.stderr.flush()


def _cmd_verify(args):
    with open_ewf(args.image) as img:
        result = img.verify(progress=None if args.quiet else _progress)
        if not args.quiet:
            sys.stderr.write("\r" + " " * 48 + "\r")
        for name, value in result["computed"].items():
            stored = result["stored"].get(name)
            if stored is None:
                print(f"{name:<6}{value}   (none stored)")
            elif stored == value:
                print(f"{name:<6}{value}   matches the stored hash")
            else:
                print(f"{name:<6}{value}   DOES NOT MATCH stored {stored}")
        if result["checksum_errors"]:
            print(f"chunk checksum mismatches: {len(result['checksum_errors'])}")
        if result["missing_page_count"]:
            print(f"pages not in the file, read as the bad-sector marker: "
                  f"{result['missing_page_count']:,}")
        if result["entry_md5_checked"]:
            bad = result["entry_md5_mismatched"]
            print(f"entry MD5s      {result['entry_md5_checked']:,} checked, "
                  f"{len(bad):,} DO NOT MATCH" if bad else
                  f"entry MD5s      {result['entry_md5_checked']:,} checked, all match")
            for path in bad:
                print(f"  mismatch      {_shown(path)}")
            if bad:
                return 1
        if result["match"] is None:
            print("the acquisition recorded no hash, so nothing could be compared")
            return 0
        return 0 if result["match"] else 1


def _shown(text):
    """A name as printable text; an L01 name can hold unpaired surrogates."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


def _cmd_files(args):
    with open_ewf(args.image) as img:
        if img.format != FORMAT_L01:
            raise EwfFormatError(f"{os.path.basename(args.image)} is a disk image, not "
                                 f"logical evidence; it holds no entry list")
        # The listing is data, so it is UTF-8 wherever it goes; on Windows a pipe or
        # file would otherwise get the ANSI code page, which cannot hold every name.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        print("kind\tsize\tmd5\tpath")
        for entry in img.logical_entries:
            kind = "folder" if entry.is_folder else "file"
            print(f"{kind}\t{entry.size}\t{entry.md5 or '-'}\t{_shown(entry.path)}")
    return 0


def _cmd_export(args):
    if args.entry is not None:
        return _export_entry(args)
    with open_ewf(args.image) as img:
        total = img.media_size
        img.seek(args.offset)
        remaining = total - args.offset if args.length is None else args.length
        out = sys.stdout.buffer if args.output == "-" else open(args.output, "wb")
        try:
            done = 0
            while remaining > 0:
                data = img.read(min(1 << 22, remaining))
                if not data:
                    break
                out.write(data)
                done += len(data)
                remaining -= len(data)
                if not args.quiet and args.output != "-":
                    _progress(done, total - args.offset)
        finally:
            if out is not sys.stdout.buffer:
                out.close()
        if not args.quiet and args.output != "-":
            sys.stderr.write("\r" + " " * 48 + "\r")
    return 0


def _export_entry(args):
    with open_ewf(args.image) as img:
        with img.open_entry(img.find_entry(args.entry)) as fh:
            out = sys.stdout.buffer if args.output == "-" else open(args.output, "wb")
            try:
                while True:
                    data = fh.read(1 << 22)
                    if not data:
                        break
                    out.write(data)
            finally:
                if out is not sys.stdout.buffer:
                    out.close()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="ewfprobe",
        description="Read an EnCase/EWF (.E01, .Ex01), SMART (.s01) or AFF (.aff, "
                    ".afd) forensic image, or EnCase logical evidence (.L01). Read only.")
    ap.add_argument("--version", action="version", version=f"ewfprobe {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("info", help="print the acquisition's geometry and metadata")
    s.add_argument("image")
    s.set_defaults(func=_cmd_info)

    s = sub.add_parser("verify", help="recompute the media hash and compare it "
                                      "with the one the acquisition stored")
    s.add_argument("image")
    s.add_argument("-q", "--quiet", action="store_true", help="no progress output")
    s.set_defaults(func=_cmd_verify)

    s = sub.add_parser("files", help="list the entries of an L01, tab separated")
    s.add_argument("image")
    s.set_defaults(func=_cmd_files)

    s = sub.add_parser("export", help="write the acquired disk out as a raw image, or "
                                      "one L01 entry's content with --entry")
    s.add_argument("image")
    s.add_argument("--entry", default=None,
                   help="the path of an L01 entry, as the files command lists it")
    s.add_argument("-o", "--output", default="-", help="output file, or - for stdout")
    s.add_argument("--offset", type=int, default=0, help="start at this byte offset")
    s.add_argument("--length", type=int, default=None, help="write this many bytes")
    s.add_argument("-q", "--quiet", action="store_true", help="no progress output")
    s.set_defaults(func=_cmd_export)

    args = ap.parse_args(argv)
    try:
        status = args.func(args)
        sys.stdout.flush()              # a closed pipe shows here, not at exit
        return status
    except EwfError as exc:
        print(f"ewfprobe: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        # Whatever was reading the output (head, a pager) stopped; so does this.
        # POSIX reports a broken pipe; Windows reports EINVAL on the write, which
        # carries no file name, unlike an EINVAL from opening a bad path.
        if not (isinstance(exc, BrokenPipeError) or (
                os.name == "nt" and exc.errno == errno.EINVAL and exc.filename is None)):
            raise
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
