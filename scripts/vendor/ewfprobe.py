"""ewfprobe: a read-only reader for EnCase/EWF (.E01) forensic images.

One file, pure Python, standard library only. No compiler, no network, and
nothing to install. It opens an EWF-E01 or SMART (.s01) acquisition, joins its
segments, and presents the original disk as an ordinary seekable file object,
so anything that can read a raw image can read an E01 without changing how it
reads. It also reads Ex01 (EWF2), the format EnCase 7 introduced, and AFF, the
Advanced Forensic Format that AFFLIB and FTK Imager write, as a single .aff file or
as an AFD directory of them, and Apple disk images: UDIF (.dmg), compressed with
zlib, bzip2, LZMA or ADC or stored, including one split into .dmgpart segments,
sparse images (.sparseimage) and sparse bundles (.sparsebundle). An LZFSE .dmg
(ULFO) needs the optional pyliblzfse package. From an L01, EnCase's logical
evidence, it lists the files collected and reads each one's content.

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
code is copied. The Apple disk image readers follow Joachim Metz, "Mac OS disk
image types" (libyal/libmodi documentation) and "ADC compressed data format"
(libyal/libfmos documentation), with the checksum rules, the sparse image's
continuation headers and the layout of a segmented .dmg measured on images
hdiutil wrote; no libmodi code is copied.

Scope. This reads EWF-E01, the format EnCase 6 and 7 and FTK Imager write and
by far the most common one in the field, EWF-S01, the variant ASR Data's SMART
writes, EWF2-Ex01, which EnCase 7 and later write, AFF, including AFD, and
EWF-L01 logical evidence, and UDIF, sparse image and sparse bundle Apple disk
images. It does not read Lx01 logical evidence, encrypted Apple disk images,
encrypted Ex01 images (the encryption is not publicly documented), Ex01 images
compressed with bzip2 (no sample exists to validate against), encrypted AFF, or AFM
(AFF metadata beside split raw files), and it never writes.

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
import plistlib
import re
import struct
import sys
import zlib
from collections import OrderedDict

try:                    # standard library, but a Python built without them lacks them
    import bz2
except ImportError:
    bz2 = None
try:
    import lzma
except ImportError:
    lzma = None

__version__ = "0.4.0"

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

# Apple disk images. A UDIF image (.dmg) keeps a 512-byte "koly" trailer at the
# very end of the file; its XML property list lists block tables ("mish"), each a
# run of chunks that are stored raw, compressed, or not stored at all (zeros).
# From Joachim Metz, "Mac OS disk image types", libyal/libmodi documentation, and
# the block-table rules libmodi's own code applies (libmodi_handle.c at 8fc5088);
# the checksum rules were measured on images hdiutil wrote. An uncompressed
# read-write image (UDRW) is plain disk bytes with no trailer and needs no reader.
#
# A chunk sits at its block table's data offset (the mish header, offset 24) plus
# the offset its entry records. hdiutil convert writes a data offset of 0 and full
# offsets in the entries; hdiutil segment writes the table's own base there and
# entry offsets relative to it, even when the image fits in one file. libmodi
# reads the table's data offset only to print it; libdmg-hfsplus seeks to
# dataStart + compOffset (dmg/io.c:166 at 7ac55ec) and 7-Zip adds StartPackPos,
# read from the same offset 24 (CPP/7zip/Archive/DmgHandler.cpp:658 and 1909 at
# 0766b73). Every image measured had a data fork offset of 0 in its trailer.
#
# A segmented image (hdiutil segment) is a .dmg and .dmgpart files beside it,
# named like image.002.dmgpart, each ending in its own trailer. Measured: every
# segment records the same segment identifier (offset 64), the segment count
# (offset 60) and its own number (offset 56, from 1), and at offset 16 where its
# data fork starts in the data fork of the whole set. Only the first segment
# carries the block tables, whose offsets address that joined data fork: the
# segments' data forks laid end to end are byte for byte the data fork of the
# same image left in one file, and a chunk can run from one segment into the next.
# Each segment's data checksum covers that segment's own data fork.
UDIF_TRAILER_SIGNATURE = b"koly"
UDIF_TRAILER_SIZE = 512
_UDIF_TRAILER = struct.Struct(">4sIIIQQQQQII")  # through the segment count
_UDIF_SEGMENT_ID = slice(64, 80)
_UDIF_ZERO = 0x00000000
_UDIF_RAW = 0x00000001
_UDIF_IGNORE = 0x00000002                       # not stored, reads as zeros
_UDIF_COMMENT = 0x7FFFFFFE
_UDIF_END = 0xFFFFFFFF
_UDIF_CODECS = {0x80000004: "ADC", 0x80000005: "zlib", 0x80000006: "bzip2",
                0x80000007: "LZFSE", 0x80000008: "LZMA"}
_UDIF_MAX_COMPRESSED_SECTORS = 2048             # libmodi refuses a larger chunk
# Checksum types, as the trailer and each block table record them.
_UDIF_CHECKSUMS = {2: "CRC32", 4: "MD5"}
FORMAT_UDIF = "UDIF"
# A sparse image (.sparseimage) is a 4096-byte header listing which 1 MiB bands of
# the disk are stored, in the order they were written, then the bands. Measured on
# images hdiutil wrote, beyond what the libmodi documentation covers: the sector
# count is 64-bit at offset 28 (the 32-bit field at 16 holds its low half), and
# once a header's 1,008 slots are used, the header at offset 20 names a
# continuation header written after them, which holds 1,010 slots from offset 56
# and names the next one at offset 12.
SPARSEIMAGE_SIGNATURE = b"sprs"
FORMAT_SPARSEIMAGE = "SPARSEIMAGE"
_SPARSE_HEADER_SIZE = 4096
# A sparse bundle (.sparsebundle) is a directory: Info.plist, whose band-size is
# the size of each band in bytes and whose size is the disk's size in bytes, and a
# bands folder of files named by band number in lowercase hexadecimal, 0 for the
# first. From the libmodi documentation; measured on bundles hdiutil wrote: a band
# with no file reads as zeros, a band file shorter than a band reads as zeros past
# its end (so does one left short in the middle of the disk when the image grew),
# and the last band's file ends where the disk does. hdiutil attach reads only a
# band's first band-size bytes and ignores a band file numbered past the end;
# ewfprobe does the same and lists both in info(). An encrypted bundle's token file
# begins with the encrcdsa header.
SPARSEBUNDLE_TYPE = "com.apple.diskimage.sparsebundle"
FORMAT_SPARSEBUNDLE = "SPARSEBUNDLE"
_SPARSEBUNDLE_PLIST_MAX = 1 << 20               # an Info.plist is a few hundred bytes
# An encrypted Apple disk image begins with this; it needs its password.
DMG_ENCRYPTED_SIGNATURE = b"encrcdsa"
# Chunks of a UDIF or sparse image are served in fixed virtual chunks of this size.
_APPLE_VIRTUAL_CHUNK = 1 << 20
_APPLE_RUN_CACHE = 8                            # decompressed UDIF chunks kept

try:                                            # optional, for LZFSE (ULFO) images only
    import liblzfse                             # the pyliblzfse package
except ImportError:
    liblzfse = None

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
    EWF, EWF2 or AFF signature, an AFD directory holding AFF files, or an Apple
    UDIF (.dmg), sparse image (.sparseimage) or sparse bundle (.sparsebundle). An
    L01 holds files rather than a disk; is_logical_evidence answers for it. An
    encrypted Apple disk image is not one: it needs its password."""
    if os.path.isdir(path):
        if apple_image_kind(path) == FORMAT_SPARSEBUNDLE:
            return True
        afd = _afd_directory(path)
        try:
            return bool(afd) and any(_is_aff(os.path.join(afd, name))
                                     for name in os.listdir(afd)
                                     if name.lower().endswith(".aff"))
        except OSError:
            return False
    try:
        with open(path, "rb") as fh:
            if fh.read(8) in (SIGNATURE, SIGNATURE_V2, AF_HEADER):
                return True
    except OSError:
        return False
    return apple_image_kind(path) in (FORMAT_UDIF, FORMAT_SPARSEIMAGE)


def _sparsebundle_info(path):
    """The Info.plist of the sparse bundle directory ``path`` as a dict, else None.
    A directory is a sparse bundle when its Info.plist names the sparse bundle type,
    whatever the directory is called."""
    plist = os.path.join(path, "Info.plist")
    try:
        if not os.path.isdir(path) or os.path.getsize(plist) > _SPARSEBUNDLE_PLIST_MAX:
            return None
        with open(plist, "rb") as fh:
            info = plistlib.load(fh)
    except Exception:                           # pylint: disable=broad-except
        return None
    if isinstance(info, dict) and info.get("diskimage-bundle-type") == SPARSEBUNDLE_TYPE:
        return info
    return None


def apple_image_kind(path):
    """``"UDIF"``, ``"SPARSEIMAGE"``, ``"SPARSEBUNDLE"`` or ``"ENCRYPTED"`` for an
    Apple disk image, else None. A sparse bundle is a directory. A UDIF image is
    recognised by its trailer, so an uncompressed read-write image, which has none,
    is None here: it is plain disk bytes."""
    if os.path.isdir(path):
        if _sparsebundle_info(path) is None:
            return None
        try:
            with open(os.path.join(path, "token"), "rb") as fh:
                if fh.read(8) == DMG_ENCRYPTED_SIGNATURE:
                    return "ENCRYPTED"
        except OSError:
            pass
        return FORMAT_SPARSEBUNDLE
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            head = fh.read(8)
            if head == DMG_ENCRYPTED_SIGNATURE:
                return "ENCRYPTED"
            if head[:4] == SPARSEIMAGE_SIGNATURE:
                return FORMAT_SPARSEIMAGE
            if size >= UDIF_TRAILER_SIZE:
                fh.seek(size - UDIF_TRAILER_SIZE)
                if fh.read(4) == UDIF_TRAILER_SIGNATURE:
                    return FORMAT_UDIF
    except OSError:
        return None
    return None


def _udif_trailer(path):
    """The 512-byte trailer at the end of ``path``, else None."""
    try:
        size = os.path.getsize(path)
        if size < UDIF_TRAILER_SIZE:
            return None
        with open(path, "rb") as fh:
            fh.seek(size - UDIF_TRAILER_SIZE)
            trailer = fh.read(UDIF_TRAILER_SIZE)
    except OSError:
        return None
    return trailer if trailer[:4] == UDIF_TRAILER_SIGNATURE else None


def udif_segments(path) -> list[str]:
    """Every file of the UDIF image ``path`` names, in order: the one file, or for
    an image hdiutil segment split, the .dmg and the .dmgpart files beside it.

    The other segments are the .dmgpart files in the same folder whose trailers
    carry the first segment's identifier; each records which segment it is, so the
    set is found from what the files record, not from how they are named. Raises
    EwfIncompleteSetError when a segment is missing, and EwfFormatError for a
    .dmgpart, which is not where a set is opened from.
    """
    first = os.path.abspath(path)
    name = os.path.basename(first)
    trailer = _udif_trailer(first)
    if trailer is None:
        raise EwfFormatError(f"{name} has no UDIF trailer")
    number, count = struct.unpack_from(">II", trailer, 56)
    if number > 1:
        raise EwfFormatError(
            f"{name} is segment {number} of {count} of a segmented Apple disk image; "
            f"open its first segment, the .dmg file, which holds the block tables")
    if count <= 1:
        return [first]
    ident = trailer[_UDIF_SEGMENT_ID]
    folder = os.path.dirname(first)
    found = {1: first}
    for entry in sorted(os.listdir(folder)):
        part = os.path.join(folder, entry)
        if not entry.lower().endswith(".dmgpart") or not os.path.isfile(part):
            continue
        other = _udif_trailer(part)
        if other is None or other[_UDIF_SEGMENT_ID] != ident:
            continue
        number, total = struct.unpack_from(">II", other, 56)
        if total != count:
            raise EwfFormatError(
                f"{entry} says it is segment {number} of {total}, where {name} says "
                f"the image has {count}")
        if number in found:
            raise EwfFormatError(
                f"{os.path.basename(found[number])} and {entry} both say they are "
                f"segment {number} of {name}")
        if not 1 < number <= count:
            raise EwfFormatError(f"{entry} says it is segment {number} of {count}")
        found[number] = part
    missing = [k for k in range(2, count + 1) if k not in found]
    if missing:
        stem = name[:-4] if name.lower().endswith(".dmg") else name
        shown = ", ".join(str(k) for k in missing[:5])
        more = f" and {len(missing) - 5} more" if len(missing) > 5 else ""
        raise EwfIncompleteSetError(
            f"{name} is the first of {count} segments and segment {shown}{more} is "
            f"not beside it (hdiutil names them like {stem}.002.dmgpart). Put every "
            f"segment in one folder before opening it; reading only the segments "
            f"present would report the missing data as empty.")
    return [found[k] for k in range(1, count + 1)]


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


class _Crc32:
    """zlib.crc32 behind the hashlib interface, as a UDIF image's type 2 checksum."""

    def __init__(self):
        self.value = 0

    def update(self, data):
        self.value = zlib.crc32(data, self.value)

    def hexdigest(self):
        return f"{self.value & 0xFFFFFFFF:08x}"


def _adc_decompress(data, size):
    """Apple Data Compression, from Joachim Metz, "ADC compressed data format"
    (libyal/libfmos documentation). A byte with the high bit set starts a literal
    run of (low 7 bits + 1) bytes; otherwise a back-reference copies earlier
    output: with bit 6 set, (low 6 bits + 4) bytes from a 16-bit distance in the
    next two bytes, else ((bits 2 to 5) + 3) bytes from a 10-bit distance made of
    the low 2 bits and the next byte. A distance of 0 is the last byte written."""
    out = bytearray()
    i, n = 0, len(data)
    while i < n and len(out) < size:
        b = data[i]
        if b & 0x80:
            count = (b & 0x7F) + 1
            if i + 1 + count > n:
                raise EwfFormatError("an ADC literal runs past the end of its chunk")
            out += data[i + 1:i + 1 + count]
            i += 1 + count
            continue
        if b & 0x40:
            if i + 2 >= n:
                raise EwfFormatError("an ADC back-reference is cut short")
            count = (b & 0x3F) + 4
            distance = (data[i + 1] << 8) | data[i + 2]
            i += 3
        else:
            if i + 1 >= n:
                raise EwfFormatError("an ADC back-reference is cut short")
            count = ((b >> 2) & 0x0F) + 3
            distance = ((b & 0x03) << 8) | data[i + 1]
            i += 2
        start = len(out) - distance - 1
        if start < 0:
            raise EwfFormatError("an ADC back-reference points before the chunk's start")
        for k in range(count):              # the source may overlap what is written
            out.append(out[start + k])
    return bytes(out)


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
        elif _is_aff(path) or apple_image_kind(path):
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
        # Apple disk images: the runs a UDIF image's block tables map, where each
        # stretch of its data fork lies (one entry per segment file), the sparse
        # image's stored bands, and what the UDIF image or sparse bundle records
        # about itself.
        self._runs: list[tuple[int, int, int, int, int]] = []
        self._run_starts: list[int] = []
        self._run_cache: OrderedDict[int, bytes] = OrderedDict()
        self._forks: list[tuple[int, int, int, int]] = []
        self._fork_starts: list[int] = []
        self._bands: dict[int, int] = {}
        self._band_handles: OrderedDict[int, object] = OrderedDict()
        self.udif = None
        self.sparsebundle = None

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
        kind = apple_image_kind(self.paths[0])
        magic = b""
        if not os.path.isdir(self.paths[0]):
            with open(self.paths[0], "rb") as fh:
                magic = fh.read(8)
        if kind == "ENCRYPTED":
            what = ("an encrypted sparse bundle (its token file holds the encrcdsa "
                    "header)" if os.path.isdir(self.paths[0]) else
                    "an encrypted Apple disk image (encrcdsa)")
            raise EwfFormatError(
                f"{os.path.basename(self.paths[0])} is {what}; it needs its password "
                f"and ewfprobe does not read it")
        if kind == FORMAT_SPARSEBUNDLE:
            self._index_sparsebundle()
            return
        if kind == FORMAT_SPARSEIMAGE:
            self._index_sparseimage()
            return
        if kind == FORMAT_UDIF:
            self._index_udif()
            return
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
            if lzma is None:
                raise EwfFormatError(
                    f"page {n} is LZMA-compressed and this Python has no lzma module")
            try:
                decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
                return decoder.decompress(raw, max_length=self.chunk_size)
            except lzma.LZMAError as exc:
                raise EwfFormatError(f"cannot decompress LZMA page {n}: {exc}") from exc
        raise EwfFormatError(f"page {n} uses compression algorithm {algorithm:#06x}, "
                             f"which ewfprobe does not read")

    # -- Apple disk images ----------------------------------------------------

    def _apple_finish(self, sectors, fmt, sizes=None):
        """Fields every reader of the stream relies on, for an Apple disk image."""
        self.format = fmt
        self.sector_size = 512
        self.sector_count = sectors
        self.media_size = sectors * 512
        self.size = self.media_size
        self.sizes = sizes if sizes is not None else [os.path.getsize(p)
                                                      for p in self.paths]
        if fmt in (FORMAT_UDIF, FORMAT_SPARSEBUNDLE):
            self.chunk_size = _APPLE_VIRTUAL_CHUNK
        self.sectors_per_chunk = self.chunk_size // 512
        self.chunk_count = self._needed_chunks()
        self._indexed_chunks = self.chunk_count

    def _index_udif(self):
        """Read the trailer and the block tables of a UDIF image into runs."""
        path = self.paths[0]
        name = os.path.basename(path)
        size = os.path.getsize(path)
        trailer = _udif_trailer(path)
        if trailer is None:
            raise EwfFormatError(f"{name} has no UDIF trailer")
        (_sig, version, header_size, flags, running, fork_offset, fork_size,
         _rsrc_offset, _rsrc_size, segment_number,
         segment_count) = _UDIF_TRAILER.unpack_from(trailer)
        if header_size != UDIF_TRAILER_SIZE:
            raise EwfFormatError(f"{name}: the UDIF trailer says it is {header_size} "
                                 f"bytes, not {UDIF_TRAILER_SIZE}")
        if segment_number > 1:
            udif_segments(path)                 # raises, naming the file to open
        if fork_offset + fork_size > size - UDIF_TRAILER_SIZE:
            raise EwfIncompleteSetError(
                f"{name}: the data the trailer describes runs past the end of the file; "
                f"the image is cut short")
        xml_offset, xml_size = struct.unpack_from(">QQ", trailer, 216)
        variant, sectors = struct.unpack_from(">IQ", trailer, 488)

        def checksum(data, at):
            kind, bits = struct.unpack_from(">II", data, at)
            value = data[at + 8:at + 8 + bits // 8] if bits else b""
            return {"type": _UDIF_CHECKSUMS.get(kind, f"type {kind}"),
                    "code": kind, "value": value.hex()}

        segments = []
        if segment_count > 1:
            if running:
                raise EwfFormatError(f"{name}: the first segment says its data starts "
                                     f"at {running} in the image's data, not at 0")
            self.paths = udif_segments(path)
            joined = 0
            for index, part in enumerate(self.paths):
                part_name = os.path.basename(part)
                part_size = os.path.getsize(part)
                t = trailer if index == 0 else _udif_trailer(part)
                (_s, _v, part_header, _f, part_running, part_offset, part_fork,
                 _ro, _rs, _n, _c) = _UDIF_TRAILER.unpack_from(t)
                if part_header != UDIF_TRAILER_SIZE:
                    raise EwfFormatError(f"{part_name}: the UDIF trailer says it is "
                                         f"{part_header} bytes, not {UDIF_TRAILER_SIZE}")
                if struct.unpack_from(">Q", t, 492)[0] != sectors:
                    raise EwfFormatError(f"{part_name} gives a different disk size from "
                                         f"{name}")
                if part_running != joined:
                    raise EwfFormatError(
                        f"{part_name} says its data starts at {part_running} in the "
                        f"image's data, where the segments before it end at {joined}")
                if part_offset + part_fork > part_size - UDIF_TRAILER_SIZE:
                    raise EwfIncompleteSetError(
                        f"{part_name}: the data its trailer describes runs past the end "
                        f"of the file; the segment is cut short")
                self._forks.append((index, joined, part_offset, part_fork))
                segments.append({"file": part_name, "number": index + 1,
                                 "data_fork": (part_offset, part_fork),
                                 "data_checksum": checksum(t, 80)})
                joined += part_fork
            low, high = 0, joined
        else:
            # One file: a chunk's position is an offset into the file, the way
            # libmodi and libdmg-hfsplus read it.
            self._forks.append((0, 0, 0, fork_offset + fork_size))
            low, high = fork_offset, fork_offset + fork_size
        self._fork_starts = [f[1] for f in self._forks]

        if not xml_size:
            raise EwfFormatError(
                f"{name} carries no XML property list (an older image whose block "
                f"tables are only in a resource fork), which is not read")
        if xml_offset + xml_size > size:
            raise EwfIncompleteSetError(f"{name}: the property list runs past the end "
                                        f"of the file; the image is cut short")
        fh = self._handle(0)
        fh.seek(xml_offset)
        try:
            plist = plistlib.loads(_read_exactly(fh, xml_size))
            tables = plist["resource-fork"]["blkx"]
        except Exception as exc:                # pylint: disable=broad-except
            raise EwfFormatError(f"{name}: the property list could not be read: "
                                 f"{exc}") from exc

        runs, partitions, codecs = [], [], set()
        expected = 0
        for t, table in enumerate(tables):
            data = table.get("Data", b"") if isinstance(table, dict) else b""
            if data[:4] != b"mish" or len(data) < 204:
                raise EwfFormatError(f"{name}: block table {t} is not a mish table")
            start, count, base = struct.unpack_from(">QQQ", data, 8)
            if start != expected:
                raise EwfFormatError(
                    f"{name}: block table {t} starts at sector {start} where the one "
                    f"before it ended at {expected}")
            entries = struct.unpack_from(">I", data, 200)[0]
            if len(data) < 204 + 40 * entries:
                raise EwfFormatError(f"{name}: block table {t} is shorter than the "
                                     f"{entries} entries it declares")
            first_run = len(runs)
            for e in range(entries):
                kind, _comment, rel, sectors_here, offset, length = struct.unpack_from(
                    ">IIQQQQ", data, 204 + 40 * e)
                if kind == _UDIF_COMMENT:
                    continue
                if kind == _UDIF_END:
                    break
                if start + rel != expected:
                    raise EwfFormatError(
                        f"{name}: block table {t} entry {e} starts at sector "
                        f"{start + rel} where the previous entry ended at {expected}")
                if not sectors_here:
                    raise EwfFormatError(f"{name}: block table {t} entry {e} covers "
                                         f"no sectors")
                offset += base
                if kind in (_UDIF_ZERO, _UDIF_IGNORE):
                    pass
                elif kind == _UDIF_RAW or kind in _UDIF_CODECS:
                    if kind == _UDIF_RAW and length != sectors_here * 512:
                        raise EwfFormatError(
                            f"{name}: block table {t} entry {e} stores {length} bytes "
                            f"for {sectors_here} uncompressed sectors")
                    if kind in _UDIF_CODECS:
                        if sectors_here > _UDIF_MAX_COMPRESSED_SECTORS:
                            raise EwfFormatError(
                                f"{name}: block table {t} entry {e} is a compressed "
                                f"chunk of {sectors_here} sectors, more than "
                                f"{_UDIF_MAX_COMPRESSED_SECTORS}")
                        codecs.add(_UDIF_CODECS[kind])
                    if offset < low or offset + length > high:
                        raise EwfFormatError(
                            f"{name}: block table {t} entry {e} points outside the "
                            f"image's data")
                else:
                    raise EwfFormatError(
                        f"{name}: block table {t} entry {e} has chunk type "
                        f"0x{kind:08x}, which is not one ewfprobe knows")
                runs.append((expected * 512, sectors_here * 512, kind, offset, length))
                expected += sectors_here
            if expected != start + count:
                raise EwfFormatError(
                    f"{name}: block table {t} declares {count} sectors and its entries "
                    f"cover {expected - start}")
            partitions.append({
                "name": str(table.get("Name") or table.get("CFName") or ""),
                "start_sector": start, "sector_count": count,
                "checksum": checksum(data, 64), "runs": (first_run, len(runs)),
            })
        if expected != sectors:
            raise EwfFormatError(
                f"{name}: the block tables cover {expected} sectors and the trailer "
                f"says the disk is {sectors}")
        if "LZFSE" in codecs and liblzfse is None:
            raise EwfFormatError(
                f"{name} is compressed with LZFSE (an ULFO image), which needs the "
                f"pyliblzfse package; install it, or convert the image with "
                f"hdiutil convert -format UDZO")
        self._runs = runs
        self._run_starts = [r[0] for r in runs]
        self.compression_level = ", ".join(sorted(codecs)) if codecs else "none"
        self.udif = {
            "version": version, "flags": flags, "variant": variant,
            "data_fork": (fork_offset, fork_size),
            "data_checksum": checksum(trailer, 80),
            "master_checksum": checksum(trailer, 352),
            "segments": segments,
            "partitions": partitions,
            "codecs": sorted(codecs),
        }
        self._apple_finish(sectors, FORMAT_UDIF)

    def _fork_read(self, pos, n):
        """``n`` bytes of a UDIF image's data fork from ``pos``, across segment files."""
        out = bytearray()
        i = bisect.bisect_right(self._fork_starts, pos) - 1
        while n:
            if i < 0 or i >= len(self._forks):
                raise EwfFormatError(f"offset {pos} is outside the image's data")
            index, start, base, span = self._forks[i]
            take = min(n, start + span - pos)
            if take <= 0:
                i += 1
                continue
            fh = self._handle(index)
            fh.seek(base + pos - start)
            out += _read_exactly(fh, take)
            pos += take
            n -= take
            i += 1
        return bytes(out)

    def _decoded_run(self, i):
        """The bytes a compressed UDIF chunk decodes to, cached."""
        cached = self._run_cache.get(i)
        if cached is not None:
            self._run_cache.move_to_end(i)
            return cached
        start, length, kind, offset, stored = self._runs[i]
        blob = self._fork_read(offset, stored)
        codec = _UDIF_CODECS[kind]
        missing = {"bzip2": bz2, "LZMA": lzma}.get(codec, True)
        if missing is None:
            raise EwfFormatError(f"this Python has no {codec} module, which the chunk at "
                                 f"sector {start // 512:,} needs")
        try:
            if codec == "zlib":
                data = zlib.decompress(blob)
            elif codec == "bzip2":
                data = bz2.decompress(blob)
            elif codec == "LZMA":
                data = lzma.decompress(blob)
            elif codec == "LZFSE":
                data = liblzfse.decompress(blob)
            else:
                data = _adc_decompress(blob, length)
        except Exception as exc:                # pylint: disable=broad-except
            raise EwfFormatError(
                f"the {codec} chunk at sector {start // 512:,} could not be "
                f"decompressed: {exc}") from exc
        if len(data) != length:
            raise EwfFormatError(
                f"the {codec} chunk at sector {start // 512:,} decompressed to "
                f"{len(data)} bytes where its block table says {length}")
        if len(self._run_cache) >= _APPLE_RUN_CACHE:
            self._run_cache.popitem(last=False)
        self._run_cache[i] = data
        return data

    def _run_bytes(self, i, a, b):
        """Bytes a to b (relative to the run's start) of UDIF run i."""
        _start, _length, kind, offset, _stored = self._runs[i]
        if kind in (_UDIF_ZERO, _UDIF_IGNORE):
            return bytes(b - a)
        if kind == _UDIF_RAW:
            return self._fork_read(offset + a, b - a)
        return self._decoded_run(i)[a:b]

    def _chunk_data_udif(self, n):
        start = n * self.chunk_size
        end = min(start + self.chunk_size, self.media_size)
        out = bytearray()
        i = bisect.bisect_right(self._run_starts, start) - 1
        pos = start
        while pos < end:
            run_start, run_length = self._runs[i][0], self._runs[i][1]
            upto = min(end, run_start + run_length)
            out += self._run_bytes(i, pos - run_start, upto - run_start)
            pos = upto
            i += 1
        return bytes(out)

    def _index_sparseimage(self):
        """Read the header chain of a sparse image into a map of stored bands."""
        path = self.paths[0]
        name = os.path.basename(path)
        fh = self._handle(0)
        size = os.path.getsize(path)
        head = _read_exactly(fh, _SPARSE_HEADER_SIZE)
        version, per_band, _unknown, low = struct.unpack_from(">IIII", head, 4)
        following, sectors = struct.unpack_from(">QQ", head, 20)
        if version != 3:
            raise EwfFormatError(f"{name} is a version {version} sparse image; only "
                                 f"version 3, which hdiutil writes, is read")
        if not per_band:
            raise EwfFormatError(f"{name}: the sparse image header gives no band size")
        if sectors & 0xFFFFFFFF != low:
            raise EwfFormatError(
                f"{name}: the sparse image header gives the disk as {sectors} sectors "
                f"in one field and {low} in the other")
        band = per_band * 512
        count = -(-sectors // per_band)
        bands: dict[int, int] = {}

        def take(slots, base):
            for slot, number in enumerate(slots):
                if not number:
                    continue
                if number > count:
                    raise EwfFormatError(f"{name}: a stored band is numbered {number} "
                                         f"of a disk of {count} bands")
                if number - 1 in bands:
                    raise EwfFormatError(f"{name}: band {number} is stored twice")
                offset = base + slot * band
                want = min(band, sectors * 512 - (number - 1) * band)
                if offset + want > size:
                    raise EwfIncompleteSetError(
                        f"{name} ends inside band {number}; the file is cut short")
                bands[number - 1] = offset

        take(struct.unpack_from(">1008I", head, 64), _SPARSE_HEADER_SIZE)
        seen, sequence = set(), 0
        while following:
            if following in seen or following + _SPARSE_HEADER_SIZE > size:
                raise EwfFormatError(f"{name}: the sparse image's header chain points "
                                     f"to offset {following}, which cannot be a header")
            seen.add(following)
            fh.seek(following)
            more = _read_exactly(fh, _SPARSE_HEADER_SIZE)
            if more[:4] != SPARSEIMAGE_SIGNATURE:
                raise EwfFormatError(f"{name}: no sparse image header at offset "
                                     f"{following}, where the chain points")
            number, _unknown, nxt = struct.unpack_from(">IIQ", more, 4)
            if number != sequence:
                raise EwfFormatError(f"{name}: continuation header {number} found where "
                                     f"{sequence} was expected")
            take(struct.unpack_from(">1010I", more, 56), following + _SPARSE_HEADER_SIZE)
            following, sequence = nxt, sequence + 1
        self._bands = bands
        self.compression_level = "none"
        self.chunk_size = band
        self._apple_finish(sectors, FORMAT_SPARSEIMAGE)

    def _index_sparsebundle(self):
        """Read a sparse bundle's Info.plist and list its band files."""
        directory = self.paths[0]
        name = os.path.basename(directory)
        info = _sparsebundle_info(directory)
        if info is None:
            raise EwfFormatError(f"{name}: its Info.plist could not be read")
        version = info.get("bundle-backingstore-version")
        if version != 1:
            raise EwfFormatError(f"{name} is a version {version} sparse bundle; only "
                                 f"version 1, which hdiutil writes, is read")
        band, size = info.get("band-size"), info.get("size")
        for key, value in (("band-size", band), ("size", size)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise EwfFormatError(f"{name}: Info.plist gives {key} as {value!r}")
        if not band:
            raise EwfFormatError(f"{name}: Info.plist gives a band size of 0")
        if size % 512:
            raise EwfFormatError(f"{name}: Info.plist gives the disk as {size} bytes, "
                                 f"which is not a whole number of 512-byte sectors")
        folder = os.path.join(directory, "bands")
        if not os.path.isdir(folder):
            raise EwfIncompleteSetError(
                f"{name} has no bands folder, which is where its data is; reading it "
                f"without one would report the whole disk as empty")
        count = -(-size // band)
        bands, beyond, oversized, other = {}, [], [], []
        stored = 0
        for entry in sorted(os.listdir(folder), key=_natural):
            path = os.path.join(folder, entry)
            number = (int(entry, 16) if re.fullmatch(r"[0-9a-f]+", entry)
                      and format(int(entry, 16), "x") == entry else None)
            if number is None or not os.path.isfile(path):
                other.append(entry)
                continue
            length = os.path.getsize(path)
            stored += length
            if number >= count:
                beyond.append(entry)
                continue
            if length > band:
                oversized.append(entry)
            bands[number] = (entry, min(length, band))
        backup = os.path.join(directory, "Info.bckup")
        try:
            with open(os.path.join(directory, "Info.plist"), "rb") as fh:
                plist_bytes = fh.read()
            with open(backup, "rb") as fh:
                backup_matches = fh.read() == plist_bytes
        except OSError:
            backup_matches = None
        self._bands = bands
        self.compression_level = "none"
        self.sparsebundle = {
            "band_size": band, "band_count": count, "bands_stored": len(bands),
            "bands_past_end": beyond, "bands_longer_than_a_band": oversized,
            "other_entries": other, "backup_matches": backup_matches,
        }
        self._apple_finish(size // 512, FORMAT_SPARSEBUNDLE, sizes=[stored])

    def _band_handle(self, number):
        fh = self._band_handles.get(number)
        if fh is None:
            if len(self._band_handles) >= MAX_OPEN:
                _old, stale = self._band_handles.popitem(last=False)
                stale.close()
            fh = open(os.path.join(self.paths[0], "bands", self._bands[number][0]), "rb")
            self._band_handles[number] = fh
        else:
            self._band_handles.move_to_end(number)
        return fh

    def _chunk_data_bundle(self, n):
        band = self.sparsebundle["band_size"]
        pos = n * self.chunk_size
        end = min(pos + self.chunk_size, self.media_size)
        out = bytearray()
        while pos < end:
            number, inside = divmod(pos, band)
            take = min(end - pos, band - inside)
            stored = self._bands[number][1] if number in self._bands else 0
            if inside < stored:
                have = min(take, stored - inside)
                fh = self._band_handle(number)
                fh.seek(inside)
                out += _read_exactly(fh, have)
                out += bytes(take - have)
            else:
                out += bytes(take)
            pos += take
        return bytes(out)

    def _chunk_data_sparse(self, n):
        offset = self._bands.get(n)
        want = min(self.chunk_size, self.media_size - n * self.chunk_size)
        if offset is None:
            return bytes(want)
        fh = self._handle(0)
        fh.seek(offset)
        return _read_exactly(fh, want)

    def _verify_udif(self, block, progress):
        """Recompute what a UDIF image records about itself: the checksum of its
        stored data, each block table's checksum over the chunks it stores, and the
        master checksum over the checksums the tables record. Measured on hdiutil's own images: CRC32 (type 2)
        or MD5 (type 4), and a block table's checksum leaves out the chunks that
        are not stored."""
        def hasher(code):
            return (_Crc32() if code == 2 else hashlib.md5()) if code in (2, 4) else None

        checks = []
        # each segment's data checksum covers its own data fork
        forks = [(0, "data", self.udif["data_fork"], self.udif["data_checksum"])]
        if self.udif["segments"]:
            forks = [(n, f"data of {seg['file']}", seg["data_fork"], seg["data_checksum"])
                     for n, seg in enumerate(self.udif["segments"])]
        for index, label, (fork_offset, fork_size), want in forks:
            h = hasher(want["code"])
            if h is None:
                continue
            fh = self._handle(index)
            fh.seek(fork_offset)
            left = fork_size
            while left:
                piece = _read_exactly(fh, min(block, left))
                h.update(piece)
                left -= len(piece)
            checks.append((label, want["type"], want["value"], h.hexdigest()))
        parts = []
        for part in self.udif["partitions"]:
            want = part["checksum"]
            h = hasher(want["code"])
            if h is None:
                continue
            first, last = part["runs"]
            for i in range(first, last):
                kind = self._runs[i][2]
                if kind in (_UDIF_ZERO, _UDIF_IGNORE):
                    continue
                length = self._runs[i][1]
                for a in range(0, length, block):
                    h.update(self._run_bytes(i, a, min(length, a + block)))
            got = h.hexdigest()
            # the master checksum covers the checksums the tables record, so it
            # says whether the tables are intact, apart from the data they describe
            parts.append((want["code"], bytes.fromhex(want["value"])))
            checks.append((f"block table {part['name'] or part['start_sector']}",
                           want["type"], want["value"], got))
            if progress:
                progress(part["start_sector"] * 512 + part["sector_count"] * 512,
                         self.media_size)
        want = self.udif["master_checksum"]
        h = hasher(want["code"])
        if h is not None and parts and all(code == want["code"] for code, _ in parts):
            for _code, value in parts:
                h.update(value)
            checks.append(("master", want["type"], want["value"], h.hexdigest()))
        return [{"what": what, "algorithm": algo, "stored": stored,
                 "computed": got, "match": stored == got}
                for what, algo, stored, got in checks]

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
        if self.format == FORMAT_UDIF:
            return self._keep(n, self._chunk_data_udif(n), want)
        if self.format == FORMAT_SPARSEIMAGE:
            return self._keep(n, self._chunk_data_sparse(n), want)
        if self.format == FORMAT_SPARSEBUNDLE:
            return self._keep(n, self._chunk_data_bundle(n), want)

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
        for fh in self._band_handles.values():
            try:
                fh.close()
            except OSError:
                pass
        self._handles.clear()
        self._band_handles.clear()
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
        container = self._verify_udif(block, None) if self.format == FORMAT_UDIF else []
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
            "container_checks": container,
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
            "udif": None if self.udif is None else {
                key: value for key, value in self.udif.items() if key != "partitions"},
            "udif_partitions": [] if self.udif is None else [
                {key: value for key, value in part.items() if key != "runs"}
                for part in self.udif["partitions"]],
            "stored_bands": len(self._bands) if self.format == FORMAT_SPARSEIMAGE else None,
            "sparsebundle": None if self.sparsebundle is None else dict(self.sparsebundle),
        }


def open_ewf(path, segments=None) -> EwfImage:
    """Open an acquisition ewfprobe reads: an EWF, EWF2 or L01 set from any path in
    it, an AFF file, an AFD directory from the directory or any file in it, an Apple
    .dmg (a segmented one from its .dmg) or .sparseimage, or a sparse bundle from its
    folder."""
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
            if d["format"] == FORMAT_UDIF:
                u = d["udif"]
                print(f"block tables    {len(d['udif_partitions'])}")
                for part in d["udif_partitions"]:
                    print(f"  {part['start_sector']:>14,} +{part['sector_count']:<14,} "
                          f"{_shown(part['name'])}")
                shown = [("data checksum", u["data_checksum"], "")]
                if u["segments"]:
                    shown = [("data checksum", seg["data_checksum"],
                              f" ({_shown(seg['file'])})") for seg in u["segments"]]
                shown.append(("master checksum", u["master_checksum"], ""))
                for label, c, where in shown:
                    print(f"{label:<16}{c['type']} {c['value'] or 'not recorded'}{where}")
            elif d["format"] == FORMAT_SPARSEIMAGE:
                print(f"band size       {d['chunk_size']:,} bytes")
                print(f"bands stored    {d['stored_bands']:,} of {d['chunk_count']:,}")
            elif d["format"] == FORMAT_SPARSEBUNDLE:
                b = d["sparsebundle"]
                print(f"band size       {b['band_size']:,} bytes")
                print(f"bands stored    {b['bands_stored']:,} of {b['band_count']:,}")
                for key, text in (
                        ("bands_past_end", "band files numbered past the disk's end, "
                                           "not read"),
                        ("bands_longer_than_a_band", "band files longer than a band, "
                                                     "read to the band's end only"),
                        ("other_entries", "other entries in bands, not read")):
                    if b[key]:
                        names = ", ".join(_shown(x) for x in b[key][:8])
                        more = f" and {len(b[key]) - 8:,} more" if len(b[key]) > 8 else ""
                        text = text.replace("band files", "band file", 1).replace(
                            "entries", "entry", 1) if len(b[key]) == 1 else text
                        print(f"  {len(b[key]):,} {text}: {names}{more}")
                if b["backup_matches"] is False:
                    print("Info.bckup      differs from Info.plist; Info.plist was used")
            else:
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
        failed = [c for c in result["container_checks"] if not c["match"]]
        for c in result["container_checks"]:
            verdict = "matches" if c["match"] else f"DOES NOT MATCH stored {c['stored']}"
            print(f"{c['algorithm']:<6}{c['computed']}   {verdict}  ({_shown(c['what'])})")
        if failed:
            return 1
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
            if result["container_checks"]:
                print("the image recorded no hash of the disk; the checksums it records "
                      "of its own data all match")
                return 0
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
                    ".afd) forensic image, an Apple disk image (.dmg, .sparseimage, "
                    ".sparsebundle), or EnCase logical evidence (.L01). Read only.")
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
