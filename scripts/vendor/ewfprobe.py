"""ewfprobe: a read-only reader for EnCase/EWF (.E01) forensic images.

One file, pure Python, standard library only. No compiler, no network, and
nothing to install. It opens an EWF-E01 or SMART (.s01) acquisition, joins its
segments, and presents the original disk as an ordinary seekable file object,
so anything that can read a raw image can read an E01 without changing how it
reads. It also reads Ex01 (EWF2), the format EnCase 7 introduced, AFF, the
Advanced Forensic Format that AFFLIB and FTK Imager write, as a single .aff file or
as an AFD directory of them, AFF4 (.aff4), including one striped across several
files, and Apple disk images: UDIF (.dmg), compressed with
zlib, bzip2, LZMA or ADC or stored, including one split into .dmgpart segments,
sparse images (.sparseimage) and sparse bundles (.sparsebundle). An LZFSE .dmg
(ULFO) needs the optional pyliblzfse package. An Apple disk image encrypted with a
password (hdiutil -encryption, AES-128 or AES-256) opens with that password and
needs the optional pycryptodome package, and so does an E01, SMART or raw (dd) set
FTK Imager encrypted with AD encryption. From an L01, EnCase's logical evidence, and
an AD1, FTK Imager's (AD-encrypted or not), it lists the files collected and reads
each one's content. It also reads the disks virtual machines keep: VHD and VHDX,
VMDK and QCOW (versions 1 to 3), including a differencing disk, delta or overlay
read through its parent.

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
code is copied. The AFF4 reader follows the AFF4 Standard v1.0a (aff4/Standard,
inprogress/AFF4StandardSpecification-v1.0a.md), with what the standard leaves open
taken from pyaff4 and c-aff4 (both Apache-2.0) and the Snappy and LZ4 decoders from
Google's format_description.txt and lz4's doc/lz4_Block_format.md; no code from
any of them is copied. The Apple disk image readers follow Joachim Metz, "Mac OS disk
image types" (libyal/libmodi documentation) and "ADC compressed data format"
(libyal/libfmos documentation), with the checksum rules, the sparse image's
continuation headers and the layout of a segmented .dmg measured on images
hdiutil wrote; no libmodi code is copied. The encrypted container (encrcdsa) is
read from the layout two MIT-licensed readers publish, nlitsme/encrypteddmg and
kev365/xways-imageio-dmg, with what differs on current macOS measured on images
hdiutil wrote; no code from either is copied. AD encryption follows the "AD
encryption" section of the EWF documentation, with what it leaves open measured on
sets FTK Imager wrote. The AD1 reader follows Petter Chr. Bjelland's notes and reader
(pcbje/pyad1, Apache-2.0) and the structures of al3ks1s/AD1-tools, with what the time
records and item types mean measured on images FTK Imager wrote; no code from either
is copied. The virtual disk readers follow Microsoft's "Virtual Hard Disk Image Format
Specification" (2006) and [MS-VHDX], VMware's "Virtual Disk Format 5.0" technical note,
and QEMU's docs/interop/qcow2.rst and block/qcow.c, with what they leave open measured on
disks Windows, VMware's tools and qemu-img wrote; no code from any of them is copied.

Scope. This reads EWF-E01, the format EnCase 6 and 7 and FTK Imager write and
by far the most common one in the field, EWF-S01, the variant ASR Data's SMART
writes, EWF2-Ex01, which EnCase 7 and later write, AFF, including AFD and AFM, and
EWF-L01 logical evidence, FTK Imager's AD1 (version 4), and UDIF, sparse image and
sparse bundle Apple disk images, encrypted with a password or not, AD-encrypted E01,
SMART, raw and AD1 sets, AFF4 containers, standard and pre-standard, striped or
not, and VHD, VHDX, VMDK and QCOW virtual disks. It does not read Lx01 logical evidence, encrypted AFF4 or AFF4-L, an AD1 other
than version 4, an Apple disk
image unlocked by a keybag rather than a password or a certificate, or one in the
older version 1 encrypted format (cdsaencr), an encrypted QCOW, a VMDK SESPARSE
extent, a VHD split into .v01 files, encrypted Ex01 images (the encryption
is not publicly documented), or Ex01 images compressed with bzip2 (no sample exists to
validate against), and it never writes.
An encrypted AFF opens with its passphrase or with the private key of a certificate
it is sealed to, and an Apple disk image or an AD-encrypted set sealed to a
certificate with that certificate's private key.

An image whose content is encrypted at rest, by BitLocker or FileVault or an
encrypted APFS volume, reads back as the ciphertext that was acquired: the
reader is working, there is simply nothing plain in there to find.
"""

from __future__ import annotations

import argparse
import bisect
import datetime
import errno
import getpass
import hashlib
import hmac
import io
import os
import plistlib
import re
import struct
import sys
import urllib.parse
import uuid
import zipfile
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

__version__ = "0.12.0"

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
FORMAT_AD1 = "AD1"
FORMAT_VHD = "VHD"
FORMAT_VHDX = "VHDX"
FORMAT_VMDK = "VMDK"
FORMAT_QCOW = "QCOW"

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
# An encrypted AFF (lib/crypto.cpp and af_update_segf in lib/afflib.cpp): a segment
# is stored as <name>/aes256 (all but a few AFFLIB leaves clear), AES-256-CBC with an
# IV of the segment's own name (at most 15 bytes of it, then zeros). The data is
# padded to whole blocks and the stored length is the padded length plus the
# original length's remainder mod 16, which is how a reader recovers it. The one
# AES-256 key is kept in affkey_aes256, encrypted (ECB, two blocks) with the SHA-256
# of the passphrase beside an encrypted block of zeros that proves the passphrase,
# and, for each certificate it is sealed to, in affkey_evp<N>: an OpenSSL envelope
# (RSA PKCS#1 v1.5 for a random session key, AES-256-CBC for the file key).
_AF_AFFKEY = "affkey_aes256"
_AF_AFFKEY_EVP = re.compile(r"affkey_evp(\d+)")
_AF_PAGE_NAME = re.compile(r"(?:page|seg)(\d+)")
_AF_PAGE_HASH_NAME = re.compile(r"(?:page|seg)\d+_(?:md5|sha1|sha256)")
_AF_STRUCTURAL = {"pagesize", "segsize", "imagesize", "sectorsize", "badflag",
                  "badsectors", "blanksectors", "md5", "sha1", "sha256", "image_gid",
                  "devicesectors", "aff_file_type", _AF_AFFKEY}
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
# AFM: an AFF file holding only the metadata (its aff_file_type is "AFM") beside the
# disk kept as plain raw files, named after it with the extension it records
# (raw_image_file_extension, "000" by default) and counted up the way split raw files
# are: 000 to 999, then A00 to ZZZ in base 36 (lib/vnode_afm.cpp and
# split_raw_increment_fname in lib/vnode_split_raw.cpp). AFFLIB joins the files while
# the next one exists, every one but the last the size of the first, and requires the
# total to be the image size the metadata records.
FORMAT_AFM = "AFM"
# AFF4: see the AFF4 section above EwfImage.
FORMAT_AFF4 = "AFF4"
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
# An encrypted Apple disk image (hdiutil -encryption) begins with this: the
# encrcdsa container, version 2. Its layout is from nlitsme/encrypteddmg,
# readencrcdsa.py (EncrCdsaFile and PassphraseWrappedKey,
# https://github.com/nlitsme/encrypteddmg/blob/626dac30710140ac488ea199cd14b5c450f2760b/readencrcdsa.py#L125-L198
# and #L283-L417) and kev365/xways-imageio-dmg, encrypted_source.cpp
# (https://github.com/kev365/xways-imageio-dmg/blob/406e738d1a43dfcb9d8f421d33a31d43078fb4b5/encrypted_source.cpp#L30-L98),
# both MIT. The header records the cipher (AES-CBC, 128 or 256 bits), the size of
# an encrypted block (512 bytes), how long the decrypted data is, where the
# encrypted data starts, and key items. A password item holds the AES key and an
# HMAC-SHA1 key, together, encrypted under a key made from the password with
# PBKDF2-HMAC-SHA1; unwrapped they end "CKIE\0". Each block is decrypted on its
# own, AES-CBC with the IV HMAC-SHA1(HMAC key, the block's number as 32 bits big
# endian) cut to 16 bytes. Measured on images hdiutil wrote on macOS 26.6.2,
# where the sources differ or say nothing: the key items are wrapped with
# AES-192-CBC (algorithm 0x80000001, 192 key bits), the stored 8-byte IV padded
# with zeros to 16, where both sources read 3DES (0x11), so both are read; each
# band of an encrypted sparse bundle is encrypted on its own from its first byte,
# the block number starting again at 0, and the token holds only the header; each
# file of an encrypted segmented image is an encrcdsa container of its own; and
# the password is used as the bytes given, with no Unicode normalisation. The
# decrypted data is a UDIF image (its trailer ends it), a sparse image, or, for an
# encrypted read-write image, the disk itself.
DMG_ENCRYPTED_SIGNATURE = b"encrcdsa"
_ENCRCDSA_HEADER = struct.Struct(">8s7L16sLQQL")  # through the count of key items
_ENCRCDSA_ITEM = struct.Struct(">LQQ")             # unlock type, offset, size
_ENCRCDSA_PASSWORD = struct.Struct(">LQL32sL32s5L")  # a password item, to its key blob
_ENCRCDSA_HEAD_READ = 1 << 16                    # key items sit in the first bytes
_ENCRCDSA_UNLOCK = {1: "password", 2: "certificate", 3: "keybag"}
_ENCRCDSA_KEY_END = b"CKIE\x00"
# A certificate item (unlock type 2), as nlitsme's readencrcdsa.py reads it
# (CertificateWrappedKey) and as measured on images hdiutil wrote with -certificate:
# the length of a key id (20) and the id, the SHA-1 of the certificate's RSA public
# key in its PKCS#1 form, in a 32-byte field; the wrapping algorithm (42, RSA) and
# padding (10, PKCS#1), a zero, the wrapped key's length (256 bytes for a 2048-bit
# key, 512 for a 4096-bit one), then the wrapped key in a 512-byte field. RSA PKCS#1
# v1.5 unwraps it to the same AES and HMAC keys and "CKIE\0" a password item holds.
_ENCRCDSA_CERT = struct.Struct(">L32sLLLL")
_CSSM_RSA = 42
_CSSM_PADDING_PKCS1 = 10
# the CSSM identifiers the header and its items record
_CSSM_AES = 0x80000001
_CSSM_3DES_3KEY = 0x11
_CSSM_SHA1HMAC = 0x5B
_CSSM_PBKDF2 = 0x67
_CSSM_PADDING_PKCS7 = 7
_CSSM_MODE_CBC_IV8 = 5
_CSSM_MODE_CBC_PAD_IV8 = 6
# The hdiutil images measured use 344,827 to 588,235 PBKDF2 rounds; far more than this
# is a damaged or hostile header, refused rather than left to run for hours.
_ENCRCDSA_MAX_ROUNDS = 50_000_000
_ENCRCDSA_BLOCK_NUMBER = struct.Struct(">L")
# The older version 1 container (cdsaencr) keeps its header at the end of the file,
# which ends with the version, 1, and the signature (readencrcdsa.py, CdsaEncrFile,
# #L465-L472). ewfprobe recognises it, to refuse it, and does not read it.
_CDSAENCR_V1_END = b"\x00\x00\x00\x01cdsaencr"
# An encrypted read-write image decrypts to the disk itself; hdiutil imageinfo
# calls that format UDRW.
FORMAT_UDRW = "UDRW"
# FTK Imager's AD encryption wraps every file of an acquisition in one container.
# The layout is from Joachim Metz, "Expert Witness Compression Format (EWF)",
# section "AD encryption" (libyal/libewf documentation, from AccessData's own
# white paper): a header of its own size (512 bytes) in the first file only, then
# the file encrypted with AES in CTR mode, the IV the file's index (from 0)
# shifted left 64 bits and the counter little endian. The header holds a salt,
# the file key encrypted with a key made from the password, and an HMAC of that
# encrypted key. Measured on images FTK Imager 4.7.3.81 wrote (the test images of
# fox-it/dissect.evidence, read as data only), where the documentation says
# nothing: the key made from the password is PBKDF2-HMAC-SHA1 of the header's
# hash (SHA-512 on every image seen) of the password, the file key is encrypted
# with AES-CTR from counter 0 under it, the HMAC uses the header's hash, and the
# password is its UTF-8 bytes. Also measured, on sets FTK Imager 4.7.3.61 wrote:
# E01, SMART and raw (dd) output can be AD-encrypted (AFF has its own, different
# encryption), every file of a set is encrypted, and only the first carries the
# header, so a raw set's first file is its first fragment's bytes plus 512.
# Sealed to a certificate instead of a password, measured on four images FTK Imager
# 4.7.3.61 wrote (E01, raw, SMART and AD1; 2048 and 4096-bit RSA keys given to it as a
# PEM certificate): the salt, 16 bytes, is wrapped with the certificate's RSA public
# key (PKCS#1 v1.5), so the header's salt field holds one RSA block (256 or 512 bytes;
# the header grows to 1,024 bytes for the larger), and the key made from it is
# PBKDF2-HMAC-SHA1 of the empty password, not of its hash. FTK Imager offers a
# password or a certificate, not both. The password images seen (7) carry the 16-byte
# salt as is, and all three kinds of image read -1 in the header's three counts, so
# the salt's length is what tells a sealed image from a password one.
ADCRYPT_SIGNATURE = b"ADCRYPT\x00"
_ADCRYPT_HEADER = struct.Struct("<8sIIhhh2sIIIIII")  # through the HMAC length
_ADCRYPT_CIPHERS = {1: 128, 2: 192, 3: 256}
_ADCRYPT_HASHES = {1: "sha256", 2: "sha512"}
_ADCRYPT_MAX_ITERATIONS = 50_000_000            # the images seen use 4,000
_ADCRYPT_SEALED_SALT = 64                       # a salt this long is an RSA block (512-bit
                                                # RSA and up); a plain one is 16 bytes
AD1_SIGNATURE = b"ADSEGMENTEDFILE\x00"
# An AD-encrypted raw (dd) image decrypts to the disk itself, in numbered files.
FORMAT_RAW = "RAW"
# Chunks of a UDIF or sparse image are served in fixed virtual chunks of this size.
_APPLE_VIRTUAL_CHUNK = 1 << 20
_APPLE_RUN_CACHE = 8                            # decompressed UDIF chunks kept

try:                                            # optional, for LZFSE (ULFO) images only
    import liblzfse                             # the pyliblzfse package
except ImportError:
    liblzfse = None
try:                                            # optional, for encrypted images only
    from Crypto.Cipher import AES as _AES, DES3 as _DES3        # pycryptodome
except ImportError:
    try:
        from Cryptodome.Cipher import AES as _AES, DES3 as _DES3    # pycryptodomex
    except ImportError:
        _AES = _DES3 = None
try:                                            # optional, for AFF sealed to a certificate
    from Crypto.PublicKey import RSA as _RSA
    from Crypto.Cipher import PKCS1_v1_5 as _PKCS1
except ImportError:
    try:
        from Cryptodome.PublicKey import RSA as _RSA
        from Cryptodome.Cipher import PKCS1_v1_5 as _PKCS1
    except ImportError:
        _RSA = _PKCS1 = None

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


class EwfPasswordError(EwfFormatError):
    """An encrypted image (an Apple disk image, or an AD-encrypted acquisition) was
    opened without its password, or with one
    that does not open it. The two subclasses tell those apart, so a caller that
    asks for the password can say which happened and ask again."""


class EwfPasswordRequiredError(EwfPasswordError):
    """The image is encrypted and no password was given. ``needs`` is "password", or
    "private key" for an AFF, an Apple disk image or an AD-encrypted set sealed only
    to a certificate."""

    def __init__(self, message, needs="password"):
        super().__init__(message)
        self.needs = needs


class EwfWrongPasswordError(EwfPasswordError):
    """The password given does not open the image."""


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
    EWF, EWF2 or AFF signature (or an AFF whose header an in-place encryption
    overwrote; an encrypted AFF counts, and opening one needs its passphrase or key,
    which EwfPasswordRequiredError's ``needs`` names), an AFF4 container, an AFD
    directory holding AFF files,
    an Apple UDIF (.dmg), sparse image (.sparseimage) or sparse bundle
    (.sparsebundle), or a virtual disk virtual_disk_kind names (VHD, VHDX, VMDK,
    QCOW). An L01 holds files rather than a disk; is_logical_evidence answers for it. An
    encrypted Apple disk image is not counted, because it opens only with its
    password; apple_image_kind reports it as ENCRYPTED."""
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
    return (_is_aff(path) or is_aff4(path) or apple_image_kind(path) in (FORMAT_UDIF, FORMAT_SPARSEIMAGE)
            or virtual_disk_kind(path) is not None)


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


# ------------------------------------------------------------ encrypted images

class _EncrcdsaKey:
    """What opens one encrcdsa file: its AES and HMAC keys, the size of an encrypted
    block, where its encrypted data starts and how long the decrypted data is, and,
    for info(), the cipher, the key wrap and the PBKDF2 rounds."""

    __slots__ = ("aes", "hmac", "block", "start", "length", "key_bits", "wrap", "rounds")

    def __init__(self, aes, hmac_key, block, start, length, key_bits, wrap, rounds):
        self.aes = aes
        self.hmac = hmac_key
        self.block = block
        self.start = start
        self.length = length
        self.key_bits = key_bits
        self.wrap = wrap
        self.rounds = rounds

    def __repr__(self):                         # never the keys
        return f"<encrcdsa AES-{self.key_bits}, {self.length} bytes>"


def _encrcdsa_v1(path):
    """True when ``path`` ends the way a version 1 encrypted image (cdsaencr) does."""
    try:
        size = os.path.getsize(path)
        if os.path.isdir(path) or size < len(_CDSAENCR_V1_END):
            return False
        with open(path, "rb") as fh:
            fh.seek(size - len(_CDSAENCR_V1_END))
            return fh.read(len(_CDSAENCR_V1_END)) == _CDSAENCR_V1_END
    except OSError:
        return False


def _cbc_decrypt(ecb, iv, data, unit):
    """CBC decryption of whole cipher blocks, done by an ECB cipher object and one
    XOR with the IV and the ciphertext shifted by a block."""
    chain = iv + data[:-unit]
    return (int.from_bytes(ecb.decrypt(data), "big")
            ^ int.from_bytes(chain, "big")).to_bytes(len(data), "big")


def _encrcdsa_unlock(fh, name, password, private_key=None):
    """The keys of the encrcdsa (version 2) file open in ``fh``, unwrapped with
    ``password`` (a str, used as UTF-8, or bytes) from a password item, or with
    ``private_key`` (an RSA key: a path, or PEM or DER bytes) from a certificate item.

    Raises EwfPasswordRequiredError when neither that opens it is given (its
    ``needs`` says which), and EwfWrongPasswordError when what is given opens none of
    its items; a wrong password or key is recognised by the padding and the "CKIE"
    mark the unwrapped keys end with, which a wrong key does not produce.
    EwfFormatError for a layout that is not read, and for an image that is opened
    only with a keybag.
    """
    fh.seek(0)
    head = fh.read(_ENCRCDSA_HEAD_READ)
    if len(head) < _ENCRCDSA_HEADER.size or head[:8] != DMG_ENCRYPTED_SIGNATURE:
        raise EwfFormatError(f"{name} has no encrcdsa header")
    (_sig, version, block_iv, mode, algorithm, key_bits, iv_algorithm, iv_bits, _guid,
     block, length, start, count) = _ENCRCDSA_HEADER.unpack_from(head)
    if version != 2:
        raise EwfFormatError(f"{name} is encrcdsa version {version}; only version 2, "
                             f"which hdiutil writes, is read")
    if (algorithm, mode, block_iv) != (_CSSM_AES, _CSSM_MODE_CBC_IV8, 16) \
            or key_bits not in (128, 256):
        raise EwfFormatError(f"{name} is encrypted with algorithm {algorithm:#x}, mode "
                             f"{mode}, a {key_bits}-bit key; only AES-CBC with a 128 or "
                             f"256-bit key is read")
    if (iv_algorithm, iv_bits) != (_CSSM_SHA1HMAC, 160):
        raise EwfFormatError(f"{name} makes its block IVs with algorithm "
                             f"{iv_algorithm:#x} ({iv_bits} bits); only HMAC-SHA1 is read")
    if not block or block % 16:
        raise EwfFormatError(f"{name}: an encrypted block of {block} bytes is not a "
                             f"whole number of AES blocks")
    if length > (1 << 32) * block:
        raise EwfFormatError(f"{name}: its data runs past what a 32-bit block number "
                             f"reaches, which is not read")
    end = _ENCRCDSA_HEADER.size + count * _ENCRCDSA_ITEM.size
    if not 0 < count <= 64 or end > len(head):
        raise EwfFormatError(f"{name}: the encrcdsa header lists {count} key items")
    items = [_ENCRCDSA_ITEM.unpack_from(head, _ENCRCDSA_HEADER.size + i * _ENCRCDSA_ITEM.size)
             for i in range(count)]
    passwords = [(offset, size) for kind, offset, size in items if kind == 1]
    certificates = [(offset, size) for kind, offset, size in items if kind == 2]
    if not passwords and not certificates:
        kinds = " or ".join(sorted({_ENCRCDSA_UNLOCK.get(kind, f"key item of type {kind}")
                                    for kind, _offset, _size in items}))
        raise EwfFormatError(f"{name} is an encrypted Apple disk image opened with a "
                             f"{kinds}, not a password or a certificate; ewfprobe does "
                             f"not read it")
    if _AES is None:
        raise EwfFormatError(f"{name} is an encrypted Apple disk image; reading one needs "
                             f"the optional pycryptodome package (pip install "
                             f"pycryptodome), which this Python does not have")
    tried = []
    if private_key is not None and certificates:
        key = _encrcdsa_unlock_certificate(head, name, certificates, private_key,
                                           key_bits, iv_bits, block, start, length)
        if key is not None:
            return key
        tried.append("the private key opens none of its certificate items")
    if password is None or not passwords:
        if tried:
            raise EwfWrongPasswordError(f"{name}: {tried[0]}")
        # a password for an image sealed only to a certificate asks for the key, as an
        # encrypted AFF does, rather than for another password
        opens = (["its password"] if passwords else []) + (
            ["the private key of the certificate it was made with"] if certificates else [])
        raise EwfPasswordRequiredError(f"{name} is an encrypted Apple disk image and "
                                       f"opens only with {' or '.join(opens)}",
                                       needs="password" if passwords else "private key")
    secret = password.encode("utf-8") if isinstance(password, str) else bytes(password)
    for offset, size in passwords:
        if size < _ENCRCDSA_PASSWORD.size or offset + size > len(head):
            raise EwfFormatError(f"{name}: a password key item of {size} bytes at offset "
                                 f"{offset} lies outside the header")
        item = head[offset:offset + size]
        (kdf, rounds, salt_length, salt, iv_length, iv, wrap_bits, wrap_algorithm,
         padding, wrap_mode, blob_length) = _ENCRCDSA_PASSWORD.unpack_from(item)
        if wrap_algorithm == _CSSM_AES and wrap_bits in (128, 192, 256):
            cipher, wrap, unit = _AES, f"AES-{wrap_bits}", 16
        elif wrap_algorithm == _CSSM_3DES_3KEY and wrap_bits == 192:
            cipher, wrap, unit = _DES3, "3DES", 8
        else:
            raise EwfFormatError(f"{name}: a password key item is wrapped with algorithm "
                                 f"{wrap_algorithm:#x} and a {wrap_bits}-bit key, which "
                                 f"is not read")
        blob = item[_ENCRCDSA_PASSWORD.size:_ENCRCDSA_PASSWORD.size + blob_length]
        if (kdf, padding, wrap_mode) != (_CSSM_PBKDF2, _CSSM_PADDING_PKCS7,
                                         _CSSM_MODE_CBC_PAD_IV8) \
                or salt_length > 32 or iv_length > unit or not blob_length \
                or blob_length % unit or len(blob) != blob_length:
            raise EwfFormatError(f"{name}: a password key item is laid out in a way "
                                 f"ewfprobe does not read")
        if not 0 < rounds <= _ENCRCDSA_MAX_ROUNDS:
            raise EwfFormatError(f"{name}: a password key item asks for {rounds:,} PBKDF2 "
                                 f"rounds, which is not read")
        derived = hashlib.pbkdf2_hmac("sha1", secret, salt[:salt_length], rounds, 32)
        try:
            ecb = cipher.new(derived[:wrap_bits // 8], cipher.MODE_ECB)
        except ValueError:                      # a 3DES key that reduces to single DES
            continue
        plain = _cbc_decrypt(ecb, iv[:iv_length].ljust(unit, b"\0"), blob, unit)
        pad = plain[-1]
        if not 1 <= pad <= unit or plain[-pad:] != bytes([pad]) * pad:
            continue
        keys = plain[:-pad]
        if not keys.endswith(_ENCRCDSA_KEY_END):
            continue
        keys = keys[:-len(_ENCRCDSA_KEY_END)]
        if len(keys) != key_bits // 8 + iv_bits // 8:
            raise EwfFormatError(f"{name}: the password opens a key item holding "
                                 f"{len(keys)} bytes of keys, where AES-{key_bits} and "
                                 f"HMAC-SHA1 need {key_bits // 8 + iv_bits // 8}")
        return _EncrcdsaKey(keys[:key_bits // 8], keys[key_bits // 8:], block, start,
                            length, key_bits, wrap, rounds)
    raise EwfWrongPasswordError("; ".join(tried + [f"the password does not open {name}"]))


def _rsa_public_key_id(rsa):
    """The SHA-1 of an RSA key's public half in its PKCS#1 form (SEQUENCE of the
    modulus and exponent), as an encrcdsa certificate item names the key."""
    def der_int(value):
        raw = value.to_bytes(value.bit_length() // 8 + 1, "big")
        return b"\x02" + der_length(len(raw)) + raw

    def der_length(n):
        if n < 128:
            return bytes([n])
        raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
        return bytes([0x80 | len(raw)]) + raw

    body = der_int(rsa.n) + der_int(rsa.e)
    return hashlib.sha1(b"\x30" + der_length(len(body)) + body).digest()


def _encrcdsa_unlock_certificate(head, name, certificates, private_key, key_bits,
                                 iv_bits, block, start, length):
    """The keys a certificate item unwraps with ``private_key``, else None."""
    rsa = _private_key(private_key)
    own_id = _rsa_public_key_id(rsa)
    for offset, size in certificates:
        if size < _ENCRCDSA_CERT.size or offset + size > len(head):
            raise EwfFormatError(f"{name}: a certificate key item of {size} bytes at "
                                 f"offset {offset} lies outside the header")
        item = head[offset:offset + size]
        (id_length, key_id, algorithm, padding, _zero,
         wrapped_length) = _ENCRCDSA_CERT.unpack_from(item)
        if (algorithm, padding) != (_CSSM_RSA, _CSSM_PADDING_PKCS1) or id_length > 32 \
                or not wrapped_length \
                or _ENCRCDSA_CERT.size + wrapped_length > len(item):
            raise EwfFormatError(f"{name}: a certificate key item is laid out in a way "
                                 f"ewfprobe does not read (algorithm {algorithm}, "
                                 f"padding {padding})")
        if key_id[:id_length] != own_id:
            continue                            # sealed to another certificate
        wrapped = item[_ENCRCDSA_CERT.size:_ENCRCDSA_CERT.size + wrapped_length]
        try:
            keys = _PKCS1.new(rsa).decrypt(wrapped, None)
        except (ValueError, TypeError):
            keys = None
        if not keys or not keys.endswith(_ENCRCDSA_KEY_END):
            continue
        keys = keys[:-len(_ENCRCDSA_KEY_END)]
        if len(keys) != key_bits // 8 + iv_bits // 8:
            raise EwfFormatError(f"{name}: the private key opens a key item holding "
                                 f"{len(keys)} bytes of keys, where AES-{key_bits} and "
                                 f"HMAC-SHA1 need {key_bits // 8 + iv_bits // 8}")
        return _EncrcdsaKey(keys[:key_bits // 8], keys[key_bits // 8:], block, start,
                            length, key_bits, "RSA PKCS#1 v1.5", None)
    return None


class _EncryptedFile:
    """The decrypted content of an encrcdsa file, or of one band of an encrypted
    sparse bundle, as a read-only file object: seek, tell, read, close. Only the
    blocks a read covers are decrypted."""

    def __init__(self, path, key, start, length, name):
        self._fh = open(path, "rb")
        self._ecb = _AES.new(key.aes, _AES.MODE_ECB)
        self._hmac = key.hmac
        self._block = key.block
        self._start = start
        self._name = name
        self.size = length
        self._pos = 0

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            pos = offset
        elif whence == os.SEEK_CUR:
            pos = self._pos + offset
        elif whence == os.SEEK_END:
            pos = self.size + offset
        else:
            raise ValueError(f"invalid whence ({whence})")
        if pos < 0:
            raise ValueError("negative seek position")
        self._pos = pos
        return pos

    def tell(self):
        return self._pos

    def read(self, n=-1):
        end = self.size if n is None or n < 0 else min(self.size, self._pos + n)
        if end <= self._pos:
            return b""
        block = self._block
        first = self._pos // block
        count = (end - 1) // block - first + 1
        self._fh.seek(self._start + first * block)
        data = self._fh.read(count * block)
        if len(data) != count * block:
            raise EwfIncompleteSetError(f"{self._name} ends inside its encrypted data; "
                                        f"the file is cut short")
        # each block's IV is HMAC-SHA1 of its number, cut to 16 bytes; the chain a
        # CBC decryption XORs with is that IV, then the block's own ciphertext
        chain = b"".join(
            hmac.digest(self._hmac, _ENCRCDSA_BLOCK_NUMBER.pack(first + i), "sha1")[:16]
            + data[i * block:(i + 1) * block - 16] for i in range(count))
        plain = (int.from_bytes(self._ecb.decrypt(data), "big")
                 ^ int.from_bytes(chain, "big")).to_bytes(len(data), "big")
        out = plain[self._pos - first * block:end - first * block]
        self._pos = end
        return out

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class _AdcryptKey:
    """What opens an AD-encrypted acquisition: the file key, where the first file's
    data starts, what the header recorded about how it was made, and whether a
    certificate's private key (``sealed``) or a password opened it."""

    def __init__(self, key, start, key_bits, hash_name, iterations, sealed=False):
        self.key = key
        self.start = start
        self.key_bits = key_bits
        self.hash_name = hash_name
        self.iterations = iterations
        self.sealed = sealed


class _AdcryptSegment:
    """One file of an AD-encrypted set: the set's key and the file's index."""

    def __init__(self, key, index):
        self.key = key
        self.index = index
        self.start = key.start if index == 0 else 0


def _ctr_le(ecb, data, counter):
    """AES-CTR with a 128-bit little-endian counter, from ``counter``."""
    blocks = -(-len(data) // 16)
    stream = ecb.encrypt(b"".join((counter + i).to_bytes(16, "little")
                                  for i in range(blocks)))[:len(data)]
    return (int.from_bytes(data, "big")
            ^ int.from_bytes(stream, "big")).to_bytes(len(data), "big")


def is_adcrypt(path) -> bool:
    """True when ``path`` begins with FTK Imager's AD encryption header."""
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == ADCRYPT_SIGNATURE
    except OSError:
        return False


def _numbered_set(path):
    """The files of the numbered set (.001, .002, ...) ``path`` belongs to, from its
    lowest number, with the same stem and number of digits; stops at the first
    number that is not on disk. [] when the suffix is not all digits."""
    folder, name = os.path.split(os.path.abspath(path))
    stem, dot, suffix = name.rpartition(".")
    if not dot or not stem or not (suffix.isascii() and suffix.isdigit()):
        return []
    width = len(suffix)
    try:
        present = {entry for entry in os.listdir(folder)}
    except OSError as exc:
        raise EwfFormatError(f"cannot list the folder holding the image: {exc}") from exc
    first = 0 if f"{stem}.{0:0{width}d}" in present else 1
    out = []
    number = first
    while f"{stem}.{number:0{width}d}" in present:
        out.append(os.path.join(folder, f"{stem}.{number:0{width}d}"))
        number += 1
    return out


def _ewf_named(name):
    """True when ``name`` has an EWF, SMART or EWF2 segment extension (E01, s01,
    Ex01 and on), not a numbered raw one (001)."""
    ext = name.rpartition(".")[2] if "." in name else ""
    return (len(ext) in (3, 4) and ext[:1].isascii() and ext[:1].isalpha()
            and _family(ext) in ("E", "s", "Ex") and ext[-2:].isalnum())


def adcrypt_set(path):
    """The files of the AD-encrypted set ``path`` belongs to, first file first, or
    None when it is not one. Only the first file carries the header, so a later
    numbered segment of a raw set is recognised by its first sibling; an EWF set
    (E01, SMART, Ex01) is joined by its extension sequence from its first file, and
    an AD1 set by its .ad1, .ad2, ... names, from any of them."""
    if os.path.isdir(path):
        return None
    name = os.path.basename(path)
    if _ad1_named(name):
        try:
            files = ad1_segments(path)
        except EwfFormatError:
            files = []
        return files if files and is_adcrypt(files[0]) else None
    if is_adcrypt(path):
        ext = name.rpartition(".")[2] if "." in name else ""
        if ext.isascii() and ext.isdigit():
            return _numbered_set(path) or [os.path.abspath(path)]
        if _ewf_named(name):
            try:
                return ewf_segments(path)
            except EwfFormatError:
                return [os.path.abspath(path)]
        return [os.path.abspath(path)]
    numbered = _numbered_set(path)
    if numbered and is_adcrypt(numbered[0]):
        return numbered
    return None


def _adcrypt_unlock(fh, name, password, private_key=None):
    """The key of the AD-encrypted set whose first file is open in ``fh``: from its
    password, or, for a set sealed to a certificate, from that certificate's RSA
    private key (``private_key``, a path or PEM or DER bytes)."""
    head = fh.read(_ADCRYPT_HEADER.size)
    if len(head) != _ADCRYPT_HEADER.size or not head.startswith(ADCRYPT_SIGNATURE):
        raise EwfFormatError(f"{name} has no AD encryption header")
    (_sig, version, header_size, _passwords, _raw_keys, _certificates, _reserved,
     cipher, hash_id, iterations, salt_len, key_len, hmac_len) = _ADCRYPT_HEADER.unpack(head)
    if version != 1:
        raise EwfFormatError(f"{name} is AD encryption version {version}; only version 1 "
                             f"is read")
    key_bits = _ADCRYPT_CIPHERS.get(cipher)
    hash_name = _ADCRYPT_HASHES.get(hash_id)
    if key_bits is None or hash_name is None:
        raise EwfFormatError(f"{name}: the AD encryption header names cipher {cipher} "
                             f"and hash {hash_id}, which are not AES and SHA-2")
    if key_len != key_bits // 8 or hmac_len != hashlib.new(hash_name).digest_size:
        raise EwfFormatError(f"{name}: the AD encryption header's key or HMAC length "
                             f"does not fit AES-{key_bits} and {hash_name.upper()}")
    if not 0 < iterations <= _ADCRYPT_MAX_ITERATIONS:
        raise EwfFormatError(f"{name}: the AD encryption header asks for {iterations:,} "
                             f"PBKDF2 iterations")
    end = _ADCRYPT_HEADER.size + salt_len + key_len + hmac_len
    if not 0 < salt_len <= 512 or header_size < end:
        raise EwfFormatError(f"{name}: the AD encryption header's lengths do not fit its "
                             f"{header_size}-byte size")
    rest = fh.read(salt_len + key_len + hmac_len)
    if len(rest) != salt_len + key_len + hmac_len:
        raise EwfIncompleteSetError(f"{name} ends inside its AD encryption header")
    salt, wrapped = rest[:salt_len], rest[salt_len:salt_len + key_len]
    stored_hmac = rest[salt_len + key_len:]
    if _AES is None:
        raise EwfFormatError(f"{name} is encrypted with FTK Imager's AD encryption; "
                             f"reading it needs the pycryptodome package")
    if isinstance(password, str):
        password = password.encode("utf-8")

    def opens(secret, plain_salt):
        made = hashlib.pbkdf2_hmac("sha1", secret, plain_salt, iterations, key_len)
        if hmac.compare_digest(hmac.digest(made, wrapped, hash_name), stored_hmac):
            return made
        return None

    sealed = salt_len >= _ADCRYPT_SEALED_SALT
    made = None
    if sealed:
        if private_key is None:
            raise EwfPasswordRequiredError(f"{name} is encrypted with FTK Imager's AD "
                                           f"encryption and sealed to a certificate; it "
                                           f"opens with that certificate's private key",
                                           needs="private key")
        rsa = _private_key(private_key)
        plain = None
        if rsa.size_in_bytes() == salt_len:
            try:
                plain = _PKCS1.new(rsa).decrypt(salt, None)
            except (ValueError, TypeError):
                plain = None
        if plain:
            made = opens(b"", plain)
            if made is None and password is not None:
                # the white paper makes the key from the password's hash when one is
                # given beside the certificate; FTK Imager offers one or the other,
                # so no image seen does this
                made = opens(hashlib.new(hash_name, password).digest(), plain)
        if made is None:
            raise EwfWrongPasswordError(f"the private key does not open {name}")
    else:
        if password is None:
            raise EwfPasswordRequiredError(f"{name} is encrypted with FTK Imager's AD "
                                           f"encryption and opens only with its "
                                           f"password")
        made = opens(hashlib.new(hash_name, password).digest(), salt)
        if made is None:
            raise EwfWrongPasswordError(f"the password does not open {name}")
    key = _ctr_le(_AES.new(made, _AES.MODE_ECB), wrapped, 0)
    return _AdcryptKey(key, header_size, key_bits, hash_name, iterations, sealed)


class _AdcryptFile:
    """One decrypted file of an AD-encrypted set, as a read-only file object."""

    def __init__(self, path, segment):
        self._fh = open(path, "rb")
        self._ecb = _AES.new(segment.key.key, _AES.MODE_ECB)
        self._start = segment.start
        self._base = segment.index << 64
        self.size = os.path.getsize(path) - segment.start
        self._pos = 0

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            pos = offset
        elif whence == os.SEEK_CUR:
            pos = self._pos + offset
        elif whence == os.SEEK_END:
            pos = self.size + offset
        else:
            raise ValueError(f"invalid whence ({whence})")
        if pos < 0:
            raise ValueError("negative seek position")
        self._pos = pos
        return pos

    def tell(self):
        return self._pos

    def read(self, n=-1):
        end = self.size if n is None or n < 0 else min(self.size, self._pos + n)
        if end <= self._pos:
            return b""
        first = self._pos // 16
        self._fh.seek(self._start + first * 16)
        data = self._fh.read(end - first * 16)
        plain = _ctr_le(self._ecb, data, self._base + first)
        out = plain[self._pos - first * 16:]
        self._pos = end
        return out

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _open_content(path, password=None, keys=None, private_key=None):
    """``path``'s content as (a file object, its size): the file itself, or, for an
    encrypted Apple disk image, what it decrypts to. ``keys`` keeps each file's
    unwrapped keys by path, so a file is unlocked once."""
    keys = {} if keys is None else keys
    key = keys.get(path, False)
    if key is False:
        name = os.path.basename(path)
        with open(path, "rb") as fh:
            key = (_encrcdsa_unlock(fh, name, password, private_key)
                   if fh.read(8) == DMG_ENCRYPTED_SIGNATURE else None)
        if key is not None and os.path.getsize(path) < key.start + -(
                -key.length // key.block) * key.block:
            raise EwfIncompleteSetError(f"{name} ends inside its encrypted data; the "
                                        f"file is cut short")
        keys[path] = key
    if key is None:
        return open(path, "rb"), os.path.getsize(path)
    if isinstance(key, _AdcryptSegment):
        fh = _AdcryptFile(path, key)
        return fh, fh.size
    return (_EncryptedFile(path, key, key.start, key.length, os.path.basename(path)),
            key.length)


def apple_image_kind(path):
    """``"UDIF"``, ``"SPARSEIMAGE"``, ``"SPARSEBUNDLE"`` or ``"ENCRYPTED"`` for an
    Apple disk image, else None. A sparse bundle is a directory. A UDIF image is
    recognised by its trailer, so an uncompressed read-write image, which has none,
    is None here: it is plain disk bytes. ``"ENCRYPTED"`` is any encrypted image,
    a file or a sparse bundle, including one in the older version 1 format, which
    is recognised in order to be refused; open_ewf opens a version 2 one with its
    password."""
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
    return "ENCRYPTED" if _encrcdsa_v1(path) else None


def _udif_trailer(path, password=None, keys=None, private_key=None):
    """The 512-byte trailer at the end of ``path``'s content (what it decrypts to,
    for an encrypted image), else None."""
    try:
        fh, size = _open_content(path, password, keys, private_key)
    except OSError:
        return None
    with fh:
        if size < UDIF_TRAILER_SIZE:
            return None
        fh.seek(size - UDIF_TRAILER_SIZE)
        trailer = fh.read(UDIF_TRAILER_SIZE)
    return trailer if trailer[:4] == UDIF_TRAILER_SIGNATURE else None


def udif_segments(path, password=None, _keys=None, private_key=None) -> list[str]:
    """Every file of the UDIF image ``path`` names, in order: the one file, or for
    an image hdiutil segment split, the .dmg and the .dmgpart files beside it.

    The other segments are the .dmgpart files in the same folder whose trailers
    carry the first segment's identifier; each records which segment it is, so the
    set is found from what the files record, not from how they are named. Raises
    EwfIncompleteSetError when a segment is missing, and EwfFormatError for a
    .dmgpart, which is not where a set is opened from. The files of an encrypted
    image are each encrypted on their own, so ``password`` is needed to read their
    trailers.
    """
    keys = {} if _keys is None else _keys
    first = os.path.abspath(path)
    name = os.path.basename(first)
    trailer = _udif_trailer(first, password, keys, private_key)
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
    unopened = []
    for entry in sorted(os.listdir(folder)):
        part = os.path.join(folder, entry)
        if not entry.lower().endswith(".dmgpart") or not os.path.isfile(part):
            continue
        try:
            other = _udif_trailer(part, password, keys, private_key)
        except EwfPasswordError:
            unopened.append(entry)              # encrypted, and not with this password
            continue
        except EwfError:
            continue
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
        locked = (f" {len(unopened)} encrypted .dmgpart file"
                  f"{'s' if len(unopened) != 1 else ''} beside it did not open with the "
                  f"password given, so could not be matched." if unopened else "")
        raise EwfIncompleteSetError(
            f"{name} is the first of {count} segments and segment {shown}{more} is "
            f"not beside it (hdiutil names them like {stem}.002.dmgpart). Put every "
            f"segment in one folder before opening it; reading only the segments "
            f"present would report the missing data as empty.{locked}")
    return [found[k] for k in range(1, count + 1)]


def is_logical_evidence(path) -> bool:
    """True when the file begins with the L01 or AD1 signature, logical evidence
    ewfprobe reads as a tree of files. An AD-encrypted AD1 is not counted, because it
    opens only with its password; is_adcrypt reports it."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(len(AD1_SIGNATURE))
    except OSError:
        return False
    return head[:8] == LVF_SIGNATURE or head == AD1_SIGNATURE


def _aff_start(fh, size):
    """Where an AFF file's first segment begins: 8, after the header; 0 when a segment
    stands where the header belongs and its tail is where its lengths put it, which is
    how AFFLIB 3.7.22's affcrypto -e leaves a file it encrypts in place (it rewrote the
    first segment over the header, on macOS and Linux alike, and AFFLIB cannot open
    the result); else None."""
    fh.seek(0)
    head = fh.read(8)
    if head == AF_HEADER:
        return 8
    if head[:4] != b"AFF\x00" or size < _AF_SEGHEAD.size + _AF_SEGTAIL.size:
        return None
    fh.seek(0)
    _magic, name_len, data_len, _arg = _AF_SEGHEAD.unpack(fh.read(_AF_SEGHEAD.size))
    tail = _AF_SEGHEAD.size + name_len + data_len
    if name_len > 1024 or tail + _AF_SEGTAIL.size > size:
        return None
    fh.seek(tail)
    tail_magic, seg_len = _AF_SEGTAIL.unpack(fh.read(_AF_SEGTAIL.size))
    return 0 if tail_magic == b"ATT\x00" and seg_len == tail + _AF_SEGTAIL.size else None


def _is_aff(path):
    try:
        with open(path, "rb") as fh:
            return _aff_start(fh, os.path.getsize(path)) is not None
    except OSError:
        return False


def _aff_decrypt(cipher_key, name, data):
    """An encrypted AFF segment's data (af_aes_decrypt in lib/afflib.cpp), ``name``
    being the segment's name without /aes256."""
    extra = len(data) % 16
    if extra and len(data) < 16:
        raise EwfFormatError(f"the encrypted segment {name} holds {len(data)} bytes, "
                             f"fewer than one block")
    body = data[:len(data) - extra]
    iv = name.encode("utf-8")[:15].ljust(16, b"\x00")
    plain = _AES.new(cipher_key, _AES.MODE_CBC, iv).decrypt(body) if body else b""
    return plain[:len(plain) - (16 - extra) % 16]


def _aff_key_from_passphrase(label, stored, password):
    """The file key from affkey_aes256 and a passphrase, or None when the passphrase
    does not open it (af_get_aes_key_from_passphrase in lib/crypto.cpp)."""
    if len(stored) not in (52, 56):
        raise EwfFormatError(f"{label}: its key segment holds {len(stored)} bytes, not the "
                             f"52 AFFLIB writes (or 56, from builds that padded it)")
    if struct.unpack_from(">I", stored)[0] != 1:
        raise EwfFormatError(f"{label}: its key segment is version "
                             f"{struct.unpack_from('>I', stored)[0]}, not 1")
    secret = password.encode("utf-8") if isinstance(password, str) else bytes(password)
    ecb = _AES.new(hashlib.sha256(secret).digest(), _AES.MODE_ECB)
    if any(ecb.decrypt(stored[36:52])):
        return None
    return ecb.decrypt(stored[4:36])


def _aff_key_from_seal(stored, rsa):
    """The file key from one affkey_evp segment and an RSA private key, or None when
    the key does not open it (af_get_affkey_using_keyfile in lib/crypto.cpp)."""
    if len(stored) < 28:
        return None
    version, ek_size, sealed_size = struct.unpack_from(">III", stored)
    if version != 1 or 28 + ek_size + sealed_size != len(stored) or sealed_size % 16:
        return None
    iv, ek = stored[12:28], stored[28:28 + ek_size]
    try:
        session = _PKCS1.new(rsa).decrypt(ek, None)
    except (ValueError, TypeError):
        return None
    if session is None or len(session) != 32:
        return None
    plain = _AES.new(session, _AES.MODE_CBC, iv).decrypt(stored[28 + ek_size:])
    pad = plain[-1] if plain else 0
    if not 1 <= pad <= 16 or plain[-pad:] != bytes([pad]) * pad or len(plain) - pad < 32:
        return None
    return plain[:32]


def _private_key(given):
    """An RSA private key from a PEM or DER file, or its bytes."""
    if _RSA is None:
        raise EwfFormatError("reading a private key needs the optional pycryptodome "
                             "package (pip install pycryptodome), which this Python does "
                             "not have")
    if isinstance(given, (bytes, bytearray)):
        data = bytes(given)
    else:
        try:
            with open(given, "rb") as fh:
                data = fh.read(1 << 20)
        except OSError as exc:
            raise EwfFormatError(f"the private key file could not be read: "
                                 f"{exc.strerror or exc}") from None
    try:
        return _RSA.import_key(data)
    except (ValueError, IndexError, TypeError) as exc:
        raise EwfFormatError(f"the private key could not be read as an RSA key ({exc}); "
                             f"give it unencrypted, as PEM or DER") from None


def _afm_next_extension(ext):
    """The extension after ``ext`` in AFFLIB's split raw naming, else None."""
    if len(ext) != 3:
        return None
    if ext.isascii() and ext.isdigit():
        return "A00" if ext == "999" else f"{int(ext) + 1:03d}"
    lower = ext[0].islower()
    chars = list(ext.upper())
    for i in (2, 1, 0):
        c = chars[i]
        if c == "Z":
            chars[i] = "0"                      # and carry
            continue
        chars[i] = "A" if c == "9" else chr(ord(c) + 1)
        out = "".join(chars)
        return out.lower() if lower else out
    return None


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


# ---------------------------------------------------------------- AFF4

def _snappy_decompress(data):
    """A raw Snappy block (google/snappy, format_description.txt): the decoded length
    as a varint, then literals and back-references. Raises on anything the format
    rules out rather than returning a short or padded block."""
    size = shift = i = 0
    while True:
        if i >= len(data) or shift > 28:
            raise EwfFormatError("a Snappy chunk has no valid length")
        b = data[i]
        i += 1
        size |= (b & 0x7F) << shift
        if b < 0x80:
            break
        shift += 7
    out = bytearray()
    end = len(data)
    while i < end:
        tag = data[i]
        i += 1
        kind = tag & 3
        if kind == 0:
            length = tag >> 2
            if length >= 60:                      # 60 to 63: 1 to 4 length bytes follow
                extra = length - 59
                length = int.from_bytes(data[i:i + extra], "little")
                i += extra
            length += 1
            if i + length > end:
                raise EwfFormatError("a Snappy literal runs past its chunk")
            out += data[i:i + length]
            i += length
            continue
        if kind == 1:
            length = 4 + ((tag >> 2) & 7)
            offset = ((tag >> 5) << 8) | data[i]
            i += 1
        elif kind == 2:
            length = 1 + (tag >> 2)
            offset = int.from_bytes(data[i:i + 2], "little")
            i += 2
        else:
            length = 1 + (tag >> 2)
            offset = int.from_bytes(data[i:i + 4], "little")
            i += 4
        _copy_back(out, offset, length, "Snappy")
    if len(out) != size:
        raise EwfFormatError(f"a Snappy chunk decoded to {len(out):,} bytes, not the "
                             f"{size:,} it declares")
    return bytes(out)


def _copy_back(out, offset, length, codec):
    """Append ``length`` bytes copied from ``offset`` bytes back; a copy longer than
    its offset repeats the last ``offset`` bytes, as both LZ77 formats define."""
    if offset == 0 or offset > len(out):
        raise EwfFormatError(f"an {codec} back-reference points outside its chunk")
    start = len(out) - offset
    if length <= offset:
        out += out[start:start + length]
    else:
        piece = bytes(out[start:])
        whole, rest = divmod(length, offset)
        out += piece * whole + piece[:rest]


def _lz4_block_decompress(data):
    """An LZ4 block (lz4/lz4, doc/lz4_Block_format.md): sequences of a token, literals,
    a two-byte offset and a match, the last sequence holding literals only."""
    out = bytearray()
    i, end = 0, len(data)
    while i < end:
        token = data[i]
        i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                if i >= end:
                    raise EwfFormatError("an LZ4 literal length runs past its chunk")
                b = data[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if i + lit > end:
            raise EwfFormatError("an LZ4 literal runs past its chunk")
        out += data[i:i + lit]
        i += lit
        if i >= end:
            break                                 # the last sequence: literals only
        if i + 2 > end:
            raise EwfFormatError("an LZ4 sequence stops inside its offset")
        offset = data[i] | data[i + 1] << 8
        i += 2
        match = token & 15
        if match == 15:
            while True:
                if i >= end:
                    raise EwfFormatError("an LZ4 match length runs past its chunk")
                b = data[i]
                i += 1
                match += b
                if b != 255:
                    break
        _copy_back(out, offset, match + 4, "LZ4")
    return bytes(out)


def _aff4_lz4(data, chunk_size):
    """An AFF4 LZ4 chunk. c-aff4 writes a raw block (LZ4_compress_default in
    aff4/aff4_image.cc); pyaff4 writes python-lz4's default, the same block after a
    4-byte little-endian length, which pyaff4 itself then fails to read. The raw form
    is tried first, the prefixed one when the first four bytes are the chunk size."""
    try:
        return _lz4_block_decompress(data)
    except (IndexError, EwfFormatError):
        if len(data) > 4 and int.from_bytes(data[:4], "little") == chunk_size:
            out = _lz4_block_decompress(data[4:])
            if len(out) == chunk_size:
                return out
        raise


def _aff4_inflate(data):
    """An AFF4 zlib or deflate chunk. c-aff4 writes a zlib stream, header and all,
    for both (deflateInit and compress2 in aff4/aff4_image.cc) and leaves spare bytes
    after a deflate one; the header decides which is tried first, and bytes after the
    end of the stream are ignored."""
    zlib_header = len(data) >= 2 and data[0] & 0x0F == 8 and (data[0] << 8 | data[1]) % 31 == 0
    for wbits in ((15, -15) if zlib_header else (-15, 15)):
        d = zlib.decompressobj(wbits)
        try:
            out = d.decompress(data)
        except zlib.error:
            continue
        if d.eof:
            return out
    raise EwfFormatError("the chunk is neither a zlib nor a raw deflate stream")


def _aff4_unescape(text):
    return re.sub(r"\\u([0-9A-Fa-f]{4})|\\U([0-9A-Fa-f]{8})|\\(.)",
                  lambda m: (chr(int(m.group(1) or m.group(2), 16)) if m.group(3) is None
                             else {"t": "\t", "n": "\n", "r": "\r", "b": "\b",
                                   "f": "\f"}.get(m.group(3), m.group(3))), text)


_TURTLE_TOKEN = re.compile(r'''
    (?P<skip>\s+|\#[^\n]*)
  | (?P<iri><[^<>"{}|^`\\\x00-\x20]*>)
  | (?P<long>"""(?:[^"\\]|\\.|"(?!""))*"""|\'\'\'(?:[^'\\]|\\.|'(?!''))*\'\'\')
  | (?P<str>"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')
  | (?P<dt>\^\^)
  | (?P<at>@[A-Za-z]+(?:-[A-Za-z0-9]+)*)
  | (?P<num>[+-]?(?:\d+\.\d+|\.\d+|\d+)(?:[eE][+-]?\d+)?)
  | (?P<bnode>_:[A-Za-z0-9_](?:[\w.-]*[\w-])?)
  | (?P<pname>(?:[A-Za-z][\w.-]*)?:(?:[\w:%-](?:[\w.:%-]*[\w:%-])?)?)
  | (?P<word>[A-Za-z]+)
  | (?P<punct>[;,.\[\]()])
''', re.X | re.S)


def _turtle(text, prefixes_out=None):
    """Parse RDF written in Turtle into {subject: {predicate: [object, ...]}}, in the
    order the text states them. An IRI object is ("iri", iri); a literal is ("lit",
    text, datatype IRI or "@language" or None); a collection is ("list", [...]).
    Enough of the W3C Turtle grammar for what AFF4 writers produce: prefixes and base
    in both spellings, typed and language-tagged literals, numbers and booleans,
    blank nodes and collections."""
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TURTLE_TOKEN.match(text, pos)
        if not m:
            raise EwfFormatError(f"information.turtle cannot be read at character "
                                 f"{pos:,}: {text[pos:pos + 40]!r}")
        pos = m.end()
        if m.lastgroup != "skip":
            tokens.append((m.lastgroup, m.group()))
    prefixes, base = {}, ""
    graph: dict = {}
    blank = [0]
    at = [0]

    def peek():
        return tokens[at[0]] if at[0] < len(tokens) else (None, None)

    def take(kind=None, value=None):
        tok = peek()
        if tok[0] is None or (kind and tok[0] != kind) or (value and tok[1] != value):
            raise EwfFormatError(f"information.turtle: expected {value or kind}, found "
                                 f"{tok[1]!r}")
        at[0] += 1
        return tok

    def iri(tok):
        kind, value = tok
        if kind == "iri":
            ref = _aff4_unescape(value[1:-1])
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", ref):
                return ref
            if not ref:
                return base
            return base + ref if ref.startswith("#") else base.rstrip("/") + "/" + ref
        prefix, _, local = value.partition(":")
        if prefix not in prefixes:
            raise EwfFormatError(f"information.turtle uses the undeclared prefix "
                                 f"{prefix or '(empty)'}:")
        return prefixes[prefix] + re.sub(r"\\(.)", r"\1", local)

    def add(subject, predicate, obj):
        graph.setdefault(subject, {}).setdefault(predicate, []).append(obj)

    def term():
        tok = peek()
        kind, value = tok
        if kind in ("iri", "pname"):
            take()
            return ("iri", iri(tok))
        if kind == "bnode":
            take()
            return ("iri", value)
        if kind in ("str", "long"):
            take()
            q = 3 if kind == "long" else 1
            lit = _aff4_unescape(value[q:-q])
            nxt = peek()
            if nxt[0] == "dt":
                take()
                return ("lit", lit, iri(take()))
            if nxt[0] == "at":
                take()
                return ("lit", lit, nxt[1])
            return ("lit", lit, None)
        if kind == "num":
            take()
            dtype = ("integer" if re.fullmatch(r"[+-]?\d+", value) else
                     "decimal" if "e" not in value.lower() else "double")
            return ("lit", value, "http://www.w3.org/2001/XMLSchema#" + dtype)
        if kind == "word" and value in ("true", "false"):
            take()
            return ("lit", value, "http://www.w3.org/2001/XMLSchema#boolean")
        if value == "[":
            take()
            node = f"_:b{blank[0]}"
            blank[0] += 1
            if peek()[1] != "]":
                pairs(node)
            take("punct", "]")
            return ("iri", node)
        if value == "(":
            take()
            items = []
            while peek()[1] != ")":
                items.append(term())
            take("punct", ")")
            return ("list", items)
        raise EwfFormatError(f"information.turtle: unexpected {value!r}")

    def pairs(subject):
        while True:
            tok = peek()
            if tok[0] == "word" and tok[1] == "a":
                take()
                predicate = _RDF_TYPE
            else:
                predicate = iri(take())
            while True:
                add(subject, predicate, term())
                if peek()[1] != ",":
                    break
                take()
            if peek()[1] != ";":
                return
            while peek()[1] == ";":
                take()
            if peek()[1] in (".", "]", None):
                return

    while at[0] < len(tokens):
        kind, value = peek()
        if value in ("@prefix", "@base") or (kind == "word" and value.upper() in
                                             ("PREFIX", "BASE")):
            take()
            if value.lower().endswith("prefix"):
                name = take("pname")[1]
                prefixes[name[:-1]] = iri(take("iri"))
            else:
                base = iri(take("iri"))
            if value.startswith("@"):
                take("punct", ".")
            continue
        subj = term()
        if subj[0] != "iri":
            raise EwfFormatError("information.turtle: a statement has no subject")
        if peek()[1] != ".":
            pairs(subj[1])
        take("punct", ".")
    if prefixes_out is not None:
        prefixes_out.update(prefixes)
    return graph


_RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_XSD = "http://www.w3.org/2001/XMLSchema#"
# AFF4 Standard v1.0 names; the pre-standard images Evimetry 2.0 and 2.1 wrote use the
# older namespace and some older names, listed after the standard one.
_AFF4_NS = "http://aff4.org/Schema#"
_AFF4_LEGACY_NS = "http://afflib.org/2009/aff4#"
_AFF4_LEGACY_SYMBOLIC = "http://afflib.org/2012/SymbolicStream#"
_AFF4_NAMES = {
    "chunkSize": ("chunkSize", "chunk_size"),
    "chunksInSegment": ("chunksInSegment", "chunks_in_segment"),
    "compressionMethod": ("compressionMethod", "CompressionMethod"),
    "ImageStream": ("ImageStream", "stream"),
    "Map": ("Map", "map"),
}
_AFF4_HASHES = {"MD5": "md5", "SHA1": "sha1", "SHA256": "sha256", "SHA512": "sha512",
                "blake2b": "blake2b"}
_AFF4_MAP_ENTRY = struct.Struct("<QQQI")        # mapped offset, length, target offset,
                                                # target id
_AFF4_INDEX_ENTRY = struct.Struct("<QI")        # chunk offset in the bevy, stored length
_AFF4_TILE = 1 << 20                            # UnknownData, UnreadableData repeat per MiB
_AFF4_VIRTUAL_CHUNK = 1 << 16                   # served to EwfImage in chunks of this size
_AFF4_STREAM_CACHE = 64                         # decompressed stream chunks kept
_AFF4_INDEX_CACHE = 16                          # bevy indexes kept
_AFF4_SIBLINGS = (".aff4", ".af4")
_AFF4_BLOCK_ORDER = ("md5", "sha1", "sha256", "sha512", "blake2b")   # AFF4 Standard 6.2
# What an acquisition records about itself, by the local names Evimetry, pyaff4 and
# the pre-standard images use, under the names ewfprobe gives an E01's header.
_AFF4_METADATA = {
    "caseName": "case_name", "caseNumber": "case_number",
    "caseDescription": "description", "evidenceNumber": "evidence_number",
    "examiner": "examiner", "notes": "notes",
    "diskMake": "drive_make", "make": "drive_make",
    "diskModel": "drive_model", "model": "drive_model",
    "diskSerial": "drive_serial_number", "serial": "drive_serial_number",
    "diskFirmware": "drive_firmware", "firmwareString": "drive_firmware",
    "diskDeviceName": "device_name", "deviceName": "device_name",
    "diskInterfaceType": "drive_interface",
    "acquisitionCompletionState": "acquisition_state",
    "startTime": "acquisition_start", "StartTime": "acquisition_start",
    "endTime": "acquisition_end", "EndTime": "acquisition_end",
}


def _aff4_hash_kind(datatype):
    """(label, hashlib name) for a linear hash datatype, ("block map", name) for an
    aff4:blockMapHashSHA512 or SHA256 one, else None."""
    local = (datatype or "").rsplit("#", 1)[-1].lower()
    if local in _AFF4_BLOCK_ORDER:
        return local.upper(), local
    m = re.fullmatch(r"blockmaphash(sha256|sha512)", local)
    if m:
        return "block map", m.group(1)
    return None


def _aff4_codec(uri):
    """The compression an ImageStream's aff4:compressionMethod names, as stored,
    snappy, lz4, zlib or deflate. None means stored (AFF4 Standard 3.3)."""
    low = "" if uri is None else uri.lower()
    if uri is None or low.endswith(("nullcompressor", "compression/stored")):
        return "stored"                           # c-aff4 spells the legacy one nullCompressor
    if "snappy" in low:
        # pyaff4 (lexicon.py) names Scudette's early writer github.com/google/snappy,
        # which compressed every chunk, stored-length ones included.
        return "snappy-always" if "github.com/google/snappy" in low else "snappy"
    if "lz4" in low:
        return "lz4"
    if "rfc1950" in low:
        return "zlib"
    if "rfc1951" in low:
        return "deflate"
    raise EwfFormatError(f"the image stream uses compression {uri}, which ewfprobe "
                         f"does not read")


def _aff4_zip_comment(fh):
    """The ZIP comment, from the end-of-central-directory record in the last 64 KiB."""
    fh.seek(0, os.SEEK_END)
    size = fh.tell()
    fh.seek(max(0, size - 65536 - 22))
    tail = fh.read()
    at = tail.rfind(b"PK\x05\x06")
    if at < 0 or at + 22 > len(tail):
        return None
    length = struct.unpack_from("<H", tail, at + 20)[0]
    return tail[at + 22:at + 22 + length]


def is_aff4(path) -> bool:
    """True when the file is an AFF4 ZIP container: a ZIP whose comment starts with
    the volume's aff4:// URI or whose first member is container.description, the two
    places the AFF4 Standard (5.4) says a producer stores it. Neither check reads the
    central directory, so a large ordinary ZIP is turned away cheaply."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(30)
            if head[:4] != b"PK\x03\x04":
                return False
            name_len = struct.unpack_from("<H", head, 26)[0]
            if fh.read(name_len) == b"container.description":
                return True
            comment = _aff4_zip_comment(fh)
            return bool(comment) and comment.startswith(b"aff4://")
    except (OSError, struct.error):
        return False


class _Aff4Volume:
    """One AFF4 ZIP file: its members by name (percent-escapes decoded), its volume
    URI and its information.turtle."""

    def __init__(self, path, index):
        self.path = path
        self.index = index
        try:
            with zipfile.ZipFile(path) as z:
                infos = z.infolist()
                comment = z.comment
        except (zipfile.BadZipFile, OSError) as exc:
            raise EwfFormatError(f"{os.path.basename(path)} is not a readable ZIP: "
                                 f"{exc}") from exc
        self.members = {}
        for info in infos:
            self.members.setdefault(urllib.parse.unquote(info.filename), info)
        self._starts: dict = {}
        urn = comment.split(b"\x00", 1)[0].decode("utf-8", "replace").strip()
        if "container.description" in self.members:
            urn = self.read_whole("container.description").decode("utf-8",
                                                                   "replace").strip()
        self.urn = urn
        if "information.turtle" not in self.members:
            raise EwfFormatError(f"{os.path.basename(path)} has no information.turtle, "
                                 f"so it is not an AFF4 container ewfprobe reads")
        self.prefixes: dict = {}
        self.graph = _turtle(self.read_whole("information.turtle").decode("utf-8"),
                             self.prefixes)
        version = self.members.get("version.txt")
        self.version = {}
        if version is not None:
            for line in re.split(r"\r\n|\r|\n", self.read_whole("version.txt").decode(
                    "utf-8", "replace")):
                key, sep, value = line.partition("=")
                if sep:
                    self.version[key.strip()] = value.strip()

    def name_of(self, urn):
        """The member name an object's URI maps to (AFF4 Standard 5.1): relative to
        the volume when it starts with the volume URI, else the whole URI."""
        if self.urn and urn.startswith(self.urn + "/"):
            return urn[len(self.urn) + 1:]
        return urn

    def find(self, urn):
        return self.members.get(self.name_of(urn))

    def read_whole(self, name):
        with zipfile.ZipFile(self.path) as z:
            return z.read(self.members[name])

    def data_start(self, info, fh):
        """Where a stored member's bytes begin: after its local header, whose name and
        extra field lengths can differ from the central directory's."""
        start = self._starts.get(info.filename)
        if start is None:
            fh.seek(info.header_offset)
            head = _read_exactly(fh, 30)
            if head[:4] != b"PK\x03\x04":
                raise EwfFormatError(f"the ZIP entry for {info.filename} has no local "
                                     f"header where the directory says")
            name_len, extra_len = struct.unpack_from("<HH", head, 26)
            start = info.header_offset + 30 + name_len + extra_len
            self._starts[info.filename] = start
        return start


class _Aff4Symbolic:
    """A symbolic stream (AFF4 Standard 4.4): one byte repeated, or a string repeated
    in 1 MiB tiles (UnknownData, UnreadableData), read at the offset asked."""

    def __init__(self, name, byte=None, text=None):
        self.name = name
        self.byte = byte
        if text is not None:
            tile = text * (_AFF4_TILE // len(text))
            self.tile = tile + text[:_AFF4_TILE - len(tile)]
        else:
            self.tile = None

    def read_at(self, offset, n):
        if self.tile is None:
            return self.byte * n
        out = bytearray()
        while len(out) < n:
            at = (offset + len(out)) % _AFF4_TILE
            out += self.tile[at:at + n - len(out)]
        return bytes(out)


def _aff4_symbolic(uri):
    """The symbolic stream a URI names, in the standard or the pre-standard spelling
    (the latter as pyaff4's stream_factory.py lists them), else None."""
    for ns in (_AFF4_NS, _AFF4_LEGACY_NS):
        if not uri.startswith(ns):
            continue
        local = uri[len(ns):]
        if local == "Zero":
            return _Aff4Symbolic("Zero", byte=b"\x00")
        if local == "UnknownData":
            return _Aff4Symbolic("UnknownData", text=b"UNKNOWN")
        if local == "UnreadableData":
            return _Aff4Symbolic("UnreadableData", text=b"UNREADABLEDATA")
        m = re.fullmatch(r"(?:SymbolicStream)?([0-9A-Fa-f]{2})", local)
        if m:
            return _Aff4Symbolic(f"SymbolicStream{m.group(1).upper()}",
                                 byte=bytes.fromhex(m.group(1)))
    if uri.startswith(_AFF4_LEGACY_SYMBOLIC):
        local = uri[len(_AFF4_LEGACY_SYMBOLIC):]
        if re.fullmatch(r"[0-9A-Fa-f]{2}", local):
            return _Aff4Symbolic(f"SymbolicStream{local.upper()}",
                                 byte=bytes.fromhex(local))
    return None


class _Aff4Container:
    """Resolve AFF4 objects by URI across the ZIP files of one acquisition, and build
    a reader for any stream: an ImageStream, a Map, or a symbolic stream."""

    def __init__(self, image, path):
        self.image = image                         # the EwfImage, for its file handles
        self.volumes = [_Aff4Volume(path, 0)]
        self._candidates = None                    # sibling files, opened on demand
        self.graph: dict = {}
        self.prefixes: dict = {}
        self._merge(self.volumes[0])
        self.readers: dict = {}

    def _merge(self, volume):
        for name, iri in volume.prefixes.items():
            self.prefixes.setdefault(name, iri)
        for subject, props in volume.graph.items():
            mine = self.graph.setdefault(subject, {})
            for predicate, objs in props.items():
                have = mine.setdefault(predicate, [])
                have.extend(o for o in objs if o not in have)

    def _siblings(self):
        """The other AFF4 files beside the first, where a striped acquisition (AFF4
        Standard 7.1) keeps the rest of its image streams. They are opened once, and
        one joins the image only when it holds a segment the image needs, so an
        unrelated container in the same folder is never read as part of it."""
        if self._candidates is None:
            self._candidates = []
            first = os.path.abspath(self.volumes[0].path)
            folder = os.path.dirname(first)
            for name in sorted(os.listdir(folder)):
                full = os.path.join(folder, name)
                if (full != first and name.lower().endswith(_AFF4_SIBLINGS)
                        and os.path.isfile(full) and is_aff4(full)):
                    try:
                        self._candidates.append(_Aff4Volume(full, -1))
                    except EwfFormatError:
                        continue
        return self._candidates

    def member(self, urn, needed=True):
        """(volume, ZipInfo) for the segment a URI names, from the first file or,
        failing that, from a sibling file, which then joins the image."""
        for volume in self.volumes:
            info = volume.find(urn)
            if info is not None:
                return volume, info
        for volume in self._siblings():
            info = volume.find(urn)
            if info is not None:
                self._candidates.remove(volume)
                volume.index = len(self.volumes)
                self.volumes.append(volume)
                self.image.paths.append(volume.path)
                self._merge(volume)
                return volume, info
        if needed:
            raise EwfIncompleteSetError(
                f"the segment {urn} is in none of the AFF4 files beside "
                f"{os.path.basename(self.volumes[0].path)}; a striped acquisition "
                f"keeps its image streams in several files, and every one has to be "
                f"in the same folder")
        return None

    def read_member(self, urn, offset=0, n=None):
        volume, info = self.member(urn)
        if n is None:
            n = info.file_size - offset
        if offset + n > info.file_size:
            raise EwfFormatError(f"a read of {urn} runs past its end")
        if info.compress_type != zipfile.ZIP_STORED:
            return volume.read_whole(volume.name_of(urn))[offset:offset + n]
        fh = self.image._handle(volume.index)
        fh.seek(volume.data_start(info, fh) + offset)
        return _read_exactly(fh, n)

    def props(self, subject):
        return self.graph.get(subject, {})

    def values(self, subject, name):
        """The objects of a subject's AFF4 property, in either namespace and under any
        of its known spellings."""
        found = []
        for local in _AFF4_NAMES.get(name, (name,)):
            for ns in (_AFF4_NS, _AFF4_LEGACY_NS):
                found.extend(self.props(subject).get(ns + local, ()))
        return found

    def one(self, subject, name):
        found = self.values(subject, name)
        return found[0] if found else None

    def number(self, subject, name):
        obj = self.one(subject, name)
        if obj is None or obj[0] != "lit":
            return None
        try:
            return int(obj[1])
        except ValueError:
            raise EwfFormatError(f"{name} of {subject} is {obj[1]!r}, not a number") from None

    def is_a(self, subject, name):
        kinds = {o[1] for o in self.props(subject).get(_RDF_TYPE, ()) if o[0] == "iri"}
        return any(ns + local in kinds for local in _AFF4_NAMES.get(name, (name,))
                   for ns in (_AFF4_NS, _AFF4_LEGACY_NS))

    def reader(self, urn):
        if urn in self.readers:
            found = self.readers[urn]
            if found is None:                      # still being built: a map loop
                raise EwfFormatError(f"the map {urn} refers back to itself")
            return found
        symbolic = _aff4_symbolic(urn)
        if symbolic is not None:
            found = symbolic
        elif self.is_a(urn, "EncryptedStream"):
            raise EwfFormatError("the image is an encrypted AFF4 stream, which ewfprobe "
                                 "does not read")
        elif self.is_a(urn, "Map"):
            self.readers[urn] = None
            try:
                found = _Aff4Map(self, urn)
            finally:
                del self.readers[urn]
        elif self.is_a(urn, "ImageStream") or self.values(urn, "chunkSize"):
            found = _Aff4ImageStream(self, urn)
        elif self.member(f"{urn}/00000000", needed=False) is not None and (
                self.is_a(urn, "ImageStream") or self.values(urn, "chunkSize")):
            # a striped file can name another file's stream only in its map; finding
            # the stream's first segment brought that file, and its description, in
            found = _Aff4ImageStream(self, urn)
        elif any(o == ("iri", urn) for subject in self.graph
                 for o in self.values(subject, "dependentStream")):
            raise EwfIncompleteSetError(
                f"the image stream {urn} is in none of the AFF4 files beside "
                f"{os.path.basename(self.volumes[0].path)}; a striped acquisition keeps "
                f"its image streams in several files, and every one has to be in the "
                f"same folder")
        else:
            raise EwfFormatError(f"the image refers to {urn}, which the container does "
                                 f"not describe as a map or an image stream")
        self.readers[urn] = found
        return found


class _Aff4ImageStream:
    """An aff4:ImageStream: chunks of chunkSize bytes, chunksInSegment of them to a
    bevy segment, each bevy with an index of where its chunks lie (AFF4 Standard 3).
    A chunk whose stored length is chunkSize is stored, anything shorter compressed."""

    def __init__(self, container, urn):
        self.c = container
        self.urn = urn
        self.name = urn
        # In a striped set each file describes the other files' streams only in part,
        # so the file holding this stream's first bevy is found, and its description
        # merged, before the stream's properties are read.
        container.member(self.bevy(0))
        self.size = container.number(urn, "size")
        self.chunk_size = container.number(urn, "chunkSize")
        self.per_bevy = container.number(urn, "chunksInSegment")
        method = container.one(urn, "compressionMethod")
        self.method = None if method is None else method[1]
        self.codec = _aff4_codec(self.method)
        if self.size is None or not self.chunk_size:
            raise EwfFormatError(f"the image stream {urn} records no size or chunk size")
        if not self.per_bevy:
            raise EwfFormatError(f"the image stream {urn} records no chunks in segment")
        self.chunk_count = -(-self.size // self.chunk_size)
        self.bevy_count = -(-self.chunk_count // self.per_bevy)
        self._index: OrderedDict = OrderedDict()
        self._cache: OrderedDict = OrderedDict()
        for b in range(self.bevy_count):          # a missing bevy is a missing file
            container.member(self.bevy(b))

    def bevy(self, b):
        return f"{self.urn}/{b:08d}"

    def index_segment(self, b):
        """The URI of bevy b's index, in the file that holds the bevy: <bevy>.index in
        AFF4 Standard v1.0, <bevy>/index in the pre-standard images."""
        volume, _info = self.c.member(self.bevy(b))
        std = self.bevy(b) + ".index"
        return std if volume.find(std) is not None else self.bevy(b) + "/index"

    def bevy_index(self, b):
        found = self._index.get(b)
        if found is not None:
            self._index.move_to_end(b)
            return found
        name = self.index_segment(b)
        raw = self.c.read_member(name)
        if name.endswith(".index"):
            if len(raw) % _AFF4_INDEX_ENTRY.size:
                raise EwfFormatError(f"the index {name} is not whole 12-byte entries")
            entries = list(_AFF4_INDEX_ENTRY.iter_unpack(raw))
        else:
            # Pre-standard: 32-bit offsets. As pyaff4 (aff4_image.py, _parse_bevy_index)
            # reads them, Evimetry lists where each chunk ends, so the first chunk
            # starts at 0; a list that starts at 0 lists where each chunk begins, and
            # the last chunk runs to the end of the bevy.
            offsets = [o for (o,) in struct.iter_unpack("<I", raw[:len(raw) // 4 * 4])]
            bevy_size = self.c.member(self.bevy(b))[1].file_size
            if offsets and offsets[0] != 0:
                starts = [0] + offsets[:-1]
                entries = [(s, e - s) for s, e in zip(starts, offsets)]
            else:
                ends = offsets[1:] + [bevy_size]
                entries = [(s, e - s) for s, e in zip(offsets, ends)]
        if len(self._index) >= _AFF4_INDEX_CACHE:
            self._index.popitem(last=False)
        self._index[b] = entries
        return entries

    def chunk(self, k):
        found = self._cache.get(k)
        if found is not None:
            self._cache.move_to_end(k)
            return found
        b, i = divmod(k, self.per_bevy)
        entries = self.bevy_index(b)
        if i >= len(entries):
            raise EwfFormatError(f"chunk {k:,} of {self.urn} is past the end of its "
                                 f"bevy's index")
        offset, length = entries[i]
        stored = self.c.read_member(self.bevy(b), offset, length)
        data = self._decode(stored, k)
        want = min(self.chunk_size, self.size - k * self.chunk_size)
        data = data[:want]
        if len(data) < want:
            raise EwfFormatError(f"chunk {k:,} of {self.urn} decodes to {len(data):,} "
                                 f"bytes, not {want:,}")
        if len(self._cache) >= _AFF4_STREAM_CACHE:
            self._cache.popitem(last=False)
        self._cache[k] = data
        return data

    def _decode(self, stored, k):
        if self.codec == "stored" or (len(stored) == self.chunk_size
                                      and self.codec != "snappy-always"):
            return stored                         # AFF4 Standard 3.2: a stored chunk
        try:
            if self.codec in ("snappy", "snappy-always"):
                return _snappy_decompress(stored)
            if self.codec == "lz4":
                return _aff4_lz4(stored, self.chunk_size)
            return _aff4_inflate(stored)
        except (IndexError, EwfFormatError) as exc:
            if self.codec == "snappy-always" and len(stored) == self.chunk_size:
                return stored                     # not Snappy after all: stored
            raise EwfFormatError(f"chunk {k:,} of {self.urn} does not decompress as "
                                 f"{self.codec}: {exc}") from exc

    def read_at(self, offset, n):
        out = bytearray()
        end = min(offset + n, self.size)
        while offset < end:
            k, within = divmod(offset, self.chunk_size)
            piece = self.chunk(k)[within:within + end - offset]
            out += piece
            offset += len(piece)
        if len(out) < n:
            raise EwfFormatError(f"a map entry reads past the end of {self.urn}")
        return bytes(out)


class _Aff4Map:
    """An aff4:Map: ranges of the image, each pointing at a stream and an offset in it,
    the streams named line by line in idx. What no range covers reads from
    aff4:mapGapDefaultStream, else aff4:Zero (AFF4 Standard 4)."""

    def __init__(self, container, urn):
        self.c = container
        self.urn = urn
        self.name = urn
        self.size = container.number(urn, "size")
        raw = container.read_member(urn + "/map")
        if len(raw) % _AFF4_MAP_ENTRY.size:
            raise EwfFormatError(f"the map {urn} is not whole 28-byte entries")
        # The standard says \n separates the lines; Evimetry's pre-standard images use
        # \r\n, and pyaff4 (aff4_map.py) splits on either.
        names = container.read_member(urn + "/idx").decode("utf-8").splitlines()
        self.target_names = names
        self.targets = [container.reader(name) for name in names]
        entries = sorted(e for e in _AFF4_MAP_ENTRY.iter_unpack(raw) if e[1])
        for a, b in zip(entries, entries[1:]):
            if a[0] + a[1] > b[0]:
                raise EwfFormatError(f"the map {urn} has overlapping ranges at "
                                     f"{b[0]:,}, which ewfprobe does not resolve")
        for e in entries:
            if e[3] >= len(self.targets):
                raise EwfFormatError(f"the map {urn} names target {e[3]}, which its idx "
                                     f"does not list")
        if self.size is None:
            self.size = max((e[0] + e[1] for e in entries), default=0)
        self.entries = entries
        self.starts = [e[0] for e in entries]
        gap = container.one(urn, "mapGapDefaultStream")
        self.gap = container.reader(gap[1]) if gap else _aff4_symbolic(_AFF4_NS + "Zero")
        self.gap_uri = gap[1] if gap else None

    def read_at(self, offset, n):
        out = bytearray()
        end = min(offset + n, self.size)
        i = max(0, bisect.bisect_right(self.starts, offset) - 1)
        while offset < end:
            entry = self.entries[i] if i < len(self.entries) else None
            if entry is None or offset < entry[0]:
                stop = end if entry is None else min(end, entry[0])
                out += self.gap.read_at(offset, stop - offset)
                offset = stop
                continue
            start, length, target_offset, target = entry
            if offset < start + length:
                take = min(end, start + length) - offset
                out += self.targets[target].read_at(target_offset + offset - start, take)
                offset += take
            i += 1
        return bytes(out)

    def coverage(self):
        """Bytes of the image by where they come from: each target's name, and the
        gaps."""
        totals: dict = {}
        for _start, length, _to, target in self.entries:
            key = getattr(self.targets[target], "name", self.target_names[target])
            totals[key] = totals.get(key, 0) + length
        covered = sum(e[1] for e in self.entries)
        if self.size > covered:
            totals["(in no map range; read from " + (
                self.gap.name if isinstance(self.gap, _Aff4Symbolic) else self.gap_uri)
                   + ")"] = self.size - covered
        return totals


# ---------------------------------------------------------------- AD1

# AD1 is FTK Imager's logical image. The layout follows Petter Chr. Bjelland's
# "AccessData Format (AD1)" notes (pcbje/pyad1, documentation/) and the structures
# of al3ks1s/AD1-tools (libad1/libad1_definitions.h); no code from either is
# copied. What they leave open or label with a question mark was measured on images
# FTK Imager 3.4.3.3 and 4.7.3.61 wrote, as the README records.
#
# Every file of a set (.ad1, .ad2, ...) begins with a 512-byte margin: a
# signature, two fields that held 1 and 2 on every image here, the file's number
# from 1, the number of files, the size of every file but the last, and the
# margin's own size. The data
# of the files with their margins left out, back to back, is the logical space the
# image's addresses point into.
_AD1_SEGMENT = struct.Struct("<16sIIIIQI")
_AD1_MARGIN = 512
AD1_LOGICAL_SIGNATURE = b"ADLOGICALIMAGE\x00\x00"
# The logical header, version 4: signature, version, a field that held 1, the chunk size,
# the address of the image's own metadata records, of the first item, the length
# and address of the source's name (after "AD\0\0"), and the address where the
# footer begins, a zero, and a second footer address.
_AD1_HEADER = struct.Struct("<16sIIIQQI4sQQQQ")
# An item: its next sibling, first child, first metadata record, chunk table,
# decompressed size, type and name length; then the name and its parent's address.
_AD1_ITEM = struct.Struct("<QQQQQII")
# A metadata record: the next record, a category, a key and the value's length,
# then the value as text.
_AD1_RECORD = struct.Struct("<QIII")
# A footer block: its tag (ATTRGUID or LOCSGUID), a zero and a count of entries, each
# a 4-byte number and a 16-byte GUID.
_AD1_FOOTER_BLOCK = struct.Struct("<8sII")
_AD1_FOOTER_ENTRY = 20
_AD1_FOLDER = 5                                # item types: a folder, and an entry
_AD1_DELETED = 2                                # FTK Imager's listing marks deleted
# The records an entry keeps: its hashes, its type record and its times.
_AD1_KEPT = {(1, 0x5001), (1, 0x5002), (2, 0x2), (5, 0x07), (5, 0x08), (5, 0x09)}
# The time records' keys, named as FTK Imager 4.7.3.61's own directory listing
# names the same values (Created, Modified, Accessed). They hold UTC.
_AD1_TIMES = {0x08: "created", 0x09: "modified", 0x07: "accessed"}
_AD1_TIME = re.compile(r"(\d{4})(\d\d)(\d\d)T(\d\d)(\d\d)(\d\d)(?:\.(\d{1,6}))?")
_AD1_MAX_NAME = 1 << 16
_AD1_WINDOW = 1 << 18                           # logical bytes read at a time for items
_AD1_MAX_VALUE = 1 << 24
_AD1_EXT = re.compile(r"ad([1-9][0-9]*)", re.IGNORECASE)


def is_ad1(path) -> bool:
    """True when the file begins with the AD1 segment signature."""
    try:
        with open(path, "rb") as fh:
            return fh.read(len(AD1_SIGNATURE)) == AD1_SIGNATURE
    except OSError:
        return False


def _ad1_named(name):
    ext = name.rpartition(".")[2] if "." in name else ""
    return bool(_AD1_EXT.fullmatch(ext))


def ad1_segments(path) -> list[str]:
    """The files of the AD1 set ``path`` belongs to, from its .ad1 through every
    consecutive .ad2, .ad3 ... beside it, matched without regard to case."""
    folder, name = os.path.split(os.path.abspath(path))
    stem, dot, ext = name.rpartition(".")
    if not dot or not _AD1_EXT.fullmatch(ext):
        raise EwfFormatError(f"{name} is not named as a file of an AD1 set (.ad1, "
                             f".ad2, ...)")
    try:
        present = {entry.lower(): entry for entry in os.listdir(folder)}
    except OSError as exc:
        raise EwfFormatError(f"cannot list the folder holding the image: {exc}") from exc
    out = []
    while f"{stem}.ad{len(out) + 1}".lower() in present:
        out.append(os.path.join(folder, present[f"{stem}.ad{len(out) + 1}".lower()]))
    if not out:
        raise EwfFormatError(f"{name} belongs to an AD1 set whose first file, "
                             f"{stem}.ad1, is not beside it")
    return out


def _ad1_time(text):
    """A time record's POSIX time (UTC), or None when it is not one."""
    m = _AD1_TIME.fullmatch(text.strip())
    if not m:
        return None
    *parts, frac = m.groups()
    try:
        when = datetime.datetime(*map(int, parts), tzinfo=datetime.timezone.utc)
    except ValueError:
        return None
    return when.timestamp() + (int(frac.ljust(6, "0")) / 1e6 if frac else 0)


class Ad1Entry:
    """One item of an AD1's file tree.

    ``names`` is the path from the top as a tuple, and ``path`` the names joined by
    "/", for display: a name can itself hold "\\" or ":", and in an image of several
    sources the top items are named for their sources. ``item_type`` is the type the
    item stores (5 is a folder, 2 an entry FTK Imager lists as deleted), ``type_code``
    the text of its metadata record 2/0x2 (None when absent), ``size`` the
    decompressed size, ``md5`` and ``sha1`` the digests its records store (None when
    absent), and ``times`` the "created", "modified" and "accessed" records as POSIX
    times. ``metadata`` reads every metadata record from the image, as
    {(category, key): text}; an entry imaged from NTFS carries dozens, so they are
    read when asked for rather than kept. Paths can repeat: a deleted file can appear
    as more than one entry.
    """

    __slots__ = ("names", "parent", "children", "address", "header_length",
                 "item_type", "size", "chunk_table", "metadata_address", "md5", "sha1",
                 "type_code", "times", "_image")

    def __init__(self, names, parent, address=0, header_length=0, item_type=None,
                 size=0, chunk_table=0, kept=None, metadata_address=0, image=None):
        self.names = names
        self.parent = parent
        self.children = []
        self.address = address
        self.header_length = header_length
        self.item_type = item_type
        self.size = size
        self.chunk_table = chunk_table
        self.metadata_address = metadata_address
        self._image = image
        kept = kept or {}
        self.md5 = _l01_digest(kept.get((1, 0x5001)), 32)
        self.sha1 = _l01_digest(kept.get((1, 0x5002)), 40)
        self.type_code = kept.get((2, 0x2))
        self.times = {}
        for key, label in _AD1_TIMES.items():
            value = _ad1_time(kept.get((5, key), ""))
            if value is not None:
                self.times[label] = value

    @property
    def metadata(self):
        if self._image is None:
            return {}
        if self._image._closed:
            raise ValueError("the image this entry belongs to is closed")
        out = {}
        for _addr, _length, category, key, value in self._image._ad1_records(
                self.metadata_address, f"AD1 entry {self.path}"):
            out.setdefault((category, key), value)
        return out

    @property
    def values(self):
        return self.metadata

    @property
    def name(self):
        return self.names[-1] if self.names else ""

    @property
    def path(self):
        return "/".join(self.names)

    @property
    def is_folder(self):
        return self.item_type == _AD1_FOLDER

    @property
    def is_deleted(self):
        return self.item_type == _AD1_DELETED

    def __repr__(self):
        return f"<Ad1Entry {self.path!r} size={self.size}>"


class _Ad1File(io.RawIOBase):
    """An AD1 entry's content as a seekable file object, inflated chunk by chunk
    through its chunk table."""

    def __init__(self, image, entry, addresses):
        super().__init__()
        self._image = image
        self._entry = entry
        self._addresses = addresses
        self._chunk_size = image.ad1["chunk_size"]
        self._size = entry.size
        self._pos = 0
        self._k = None
        self._data = b""

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

    def _piece(self, k):
        if k != self._k:
            a, b = self._addresses[k], self._addresses[k + 1]
            want = min(self._chunk_size, self._size - k * self._chunk_size)
            try:
                data = zlib.decompress(self._image._ad1_read(a, b - a))
            except zlib.error as exc:
                raise EwfFormatError(f"AD1 entry {self._entry.path}: chunk {k} does not "
                                     f"inflate ({exc})") from None
            if len(data) != want:
                raise EwfFormatError(f"AD1 entry {self._entry.path}: chunk {k} inflates "
                                     f"to {len(data):,} bytes where {want:,} were "
                                     f"expected")
            self._k, self._data = k, data
        return self._data

    def readinto(self, buffer):
        view = memoryview(buffer).cast("B")
        done = 0
        while done < len(view) and self._pos < self._size:
            k, within = divmod(self._pos, self._chunk_size)
            data = self._piece(k)
            take = min(len(view) - done, len(data) - within)
            view[done:done + take] = data[within:within + take]
            done += take
            self._pos += take
        return done


# -- virtual disks --------------------------------------------------------------
# VHD, from Microsoft's "Virtual Hard Disk Image Format Specification" (version 1.0,
# October 2006): big-endian throughout; a 512-byte footer whose cookie is "conectix"
# at the end of the file (511 bytes in images older than Virtual PC 2004), its
# checksum the one's complement of the sum of its bytes with the checksum field left
# out; a fixed disk is the disk's data followed by the footer; a dynamic or
# differencing disk starts with a copy of the footer, has a 1,024-byte "cxsparse"
# header at the footer's data offset, and a block allocation table of 32-bit sector
# offsets, 0xFFFFFFFF where no block is stored. A stored block is a sector bitmap,
# padded to 512 bytes, then the block's data. In a differencing disk a set bit means
# the sector is in this file and a clear one that it is in the parent.
VHD_COOKIE = b"conectix"
_VHD_FOOTER = struct.Struct(">8sIIQI4sI4sQQIII16sB")
_VHD_DYNAMIC = struct.Struct(">8sQQIIII16sI4x")    # then the parent's name, locators
_VHD_LOCATOR = struct.Struct(">4sIIIQ")
_VHD_TYPES = {2: "fixed", 3: "dynamic", 4: "differencing"}
_VHD_UNUSED = 0xFFFFFFFF
_VHD_EPOCH = 946684800                              # 2000-01-01 00:00:00 UTC
# A virtual disk's blocks can be large (a VHD's are 2 MiB by default), so it is read
# in pieces of at most this size, each inside one block.
_VIRTUAL_CHUNK = 1 << 20
_VIRTUAL_MAX_PARENTS = 32
_opening_parents: list[str] = []                     # the chain being opened, for loops


def _vhd_checksum(data, at):
    """The one's complement of the sum of ``data``'s bytes, leaving out the four at
    ``at``, as the VHD specification's appendix computes a footer's and a dynamic
    disk header's checksum."""
    return ~(sum(data) - sum(data[at:at + 4])) & 0xFFFFFFFF


def _vhd_footer(data):
    """A VHD footer's fields, or None when ``data`` (512 bytes, or the 511 of an image
    older than Virtual PC 2004) does not begin with one whose checksum matches."""
    if len(data) < 511 or data[:8] != VHD_COOKIE:
        return None
    (_cookie, features, version, data_offset, stamp, app, app_version, host, original,
     current, geometry, disk_type, checksum, unique_id, saved) = _VHD_FOOTER.unpack_from(data)
    if _vhd_checksum(data[:512], 64) != checksum:
        return None
    return {"features": features, "version": version, "data_offset": data_offset,
            "timestamp": stamp, "creator": app, "creator_version": app_version,
            "host": host, "original_size": original, "current_size": current,
            "geometry": (geometry >> 16, (geometry >> 8) & 0xFF, geometry & 0xFF),
            "type": disk_type, "unique_id": unique_id, "saved_state": saved}


def virtual_disk_kind(path):
    """The virtual disk format of ``path``, judged from its own bytes: "VHDX" when the
    file begins with "vhdxfile"; "VMDK" for a VMDK descriptor file or a sparse extent
    ("KDMV" or "COWD"); "QCOW" for QEMU's qcow of version 1, 2 or 3; "VHD" when it
    ends in a VHD footer's cookie ("conectix") or begins with a copy of one;
    otherwise None."""
    if os.path.isdir(path):
        return None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            head = fh.read(512)
            fh.seek(max(0, size - 512))
            tail = fh.read(512)
    except OSError:
        return None
    if head[:8] == VHDX_SIGNATURE:
        return FORMAT_VHDX
    if head[:4] in (VMDK_SPARSE_MAGIC, VMDK_COWD_MAGIC) or _is_vmdk_descriptor(head):
        return FORMAT_VMDK
    if head[:4] == QCOW_MAGIC and head[4:8] in (b"\0\0\0\1", b"\0\0\0\2", b"\0\0\0\3"):
        return FORMAT_QCOW
    # The cookie alone names a VHD, so one whose footer fails its checksum is refused
    # as a damaged VHD rather than read as something else.
    if VHD_COOKIE in (tail[:8], tail[1:9], head[:8]):
        return FORMAT_VHD
    return None


# VHDX, from Microsoft's [MS-VHDX] (Open Specifications): little-endian; "vhdxfile"
# at the start; two 4-KB headers at 64 KB and 128 KB, each with a CRC-32C, the one with
# the greater sequence number current; two copies of a 64-KB region table at 192 KB and
# 256 KB naming the BAT and the metadata region; a log that has to be replayed, in
# memory for a reader, when the current header's LogGuid is not zero; and a BAT of
# 64-bit entries, the state in the low 3 bits and the file offset in MiB in the top 44,
# with one sector bitmap entry after each chunk's payload entries.
VHDX_SIGNATURE = b"vhdxfile"
_VHDX_HEADER = struct.Struct("<4sIQ16s16s16sHHIQ")
_VHDX_REGION_BAT = uuid.UUID("2DC27766-F623-4200-9D64-115E9BFD4A08").bytes_le
_VHDX_REGION_METADATA = uuid.UUID("8B7CA206-4790-4B9A-B8FE-575F050F886E").bytes_le
_VHDX_FILE_PARAMETERS = uuid.UUID("CAA16737-FA36-4D43-B3B6-33F0AA44E76B").bytes_le
_VHDX_DISK_SIZE = uuid.UUID("2FA54224-CD1B-4876-B211-5DBED83BF4B8").bytes_le
_VHDX_DISK_ID = uuid.UUID("BECA12AB-B2E6-4523-93EF-C309E000C746").bytes_le
_VHDX_LOGICAL_SECTOR = uuid.UUID("8141BF1D-A96F-4709-BA47-F233A8FAAB5F").bytes_le
_VHDX_PHYSICAL_SECTOR = uuid.UUID("CDA348C7-445D-4471-9CC9-E9885251C556").bytes_le
_VHDX_PARENT_LOCATOR = uuid.UUID("A8D35F2D-B30B-454D-ABF7-D3D84834AB0C").bytes_le
_VHDX_LOCATOR_VHDX = uuid.UUID("B04AEFB7-D19E-4A81-B789-25B8E9445913").bytes_le
_VHDX_KNOWN_ITEMS = {_VHDX_FILE_PARAMETERS, _VHDX_DISK_SIZE, _VHDX_DISK_ID,
                     _VHDX_LOGICAL_SECTOR, _VHDX_PHYSICAL_SECTOR, _VHDX_PARENT_LOCATOR}
# Payload block states, and the sector bitmap block's present state.
_VHDX_NOT_PRESENT, _VHDX_UNDEFINED, _VHDX_ZERO, _VHDX_UNMAPPED = 0, 1, 2, 3
_VHDX_FULLY_PRESENT, _VHDX_PARTIALLY_PRESENT = 6, 7
_VHDX_STATE_NAMES = {0: "not present", 1: "undefined", 2: "zero", 3: "unmapped",
                     6: "fully present", 7: "partially present"}
_VHDX_SB_PRESENT = 6
_MIB = 1 << 20


# VMDK, from VMware's "Virtual Disk Format 5.0" technical note (2011): a text
# descriptor, in its own file or embedded in the first sparse extent, lists the
# extents in order (FLAT, SPARSE, ZERO, VMFS, VMFSSPARSE), the disk's content id and
# its parent's. A hosted sparse extent ("KDMV", little-endian) maps the disk through a
# grain directory of 32-bit sector offsets of grain tables, each of 512 32-bit grain
# offsets, 0 where no grain is stored and 1 for a grain of zeros (version 2); a
# stream-optimized one compresses each grain behind a 12-byte marker holding its LBA
# and length. An ESXi sparse extent ("COWD") has 4,096-entry grain tables.
VMDK_SPARSE_MAGIC = b"KDMV"
VMDK_COWD_MAGIC = b"COWD"
_VMDK_DESCRIPTOR_START = b"# Disk DescriptorFile"
_VMDK_SPARSE = struct.Struct("<4sIIQQQQIQQQB4sH")
_VMDK_COWD = struct.Struct("<4sIIIIIII")
_VMDK_GD_AT_END = 0xFFFFFFFFFFFFFFFF
_VMDK_EXTENT = re.compile(
    r'^\s*(RW|RDONLY|NOACCESS)\s+(\d+)\s+([A-Za-z]+)(?:\s+"([^"]*)"(?:\s+(\d+))?)?\s*$',
    re.I)
_VMDK_MAX_DESCRIPTOR = 1 << 20


def _vmdk_descriptor_text(raw):
    """A VMDK descriptor's text, NUL padding and a byte-order mark removed."""
    text = raw.split(b"\0")[0]
    if text.startswith(b"\xef\xbb\xbf"):
        text = text[3:]
    try:
        return text.decode("utf-8")
    except UnicodeDecodeError:
        return text.decode("latin-1")


def _is_vmdk_descriptor(head):
    start = head[3:] if head.startswith(b"\xef\xbb\xbf") else head
    return start[:len(_VMDK_DESCRIPTOR_START)].lower() == _VMDK_DESCRIPTOR_START.lower()


# QCOW, from QEMU's own documents: docs/interop/qcow2.rst for versions 2 and 3, and
# block/qcow.c for version 1 (both at QEMU commit 81ce3a8). Big-endian; a two-level
# map, an L1 table of L2 table offsets and L2 tables of cluster descriptors, 0 where a
# cluster is not stored (read from the backing file, or zeros); version 3 adds a
# zeros flag (bit 0), extended L2 entries of 32 subclusters each, and zstd as a second
# compression. Compressed clusters are raw deflate, without zlib's header.
QCOW_MAGIC = b"QFI\xfb"
_QCOW1_HEADER = struct.Struct(">4sIQIIQBBxxIQ")
_QCOW2_HEADER = struct.Struct(">4sIQIIQIIQQIIQ")
_QCOW_COPIED = 1 << 63
_QCOW_COMPRESSED = 1 << 62
_QCOW1_COMPRESSED = 1 << 63
_QCOW_OFFSET = ((1 << 56) - 1) & ~0x1FF        # bits 9 to 55
_QCOW_BACKING_FORMAT = 0xE2792ACA
_QCOW_EXTERNAL_DATA = 0x44415441
_QCOW_KNOWN_INCOMPATIBLE = 0x1F


def _zstd_decompressor():
    """A zstd decompressor factory, from the standard library (Python 3.14) or the
    backports.zstd or zstandard package; None when none is installed."""
    try:
        from compression import zstd                    # Python 3.14
        return lambda: zstd.ZstdDecompressor()
    except ImportError:
        pass
    try:
        from backports import zstd as backport          # type: ignore
        return lambda: backport.ZstdDecompressor()
    except ImportError:
        pass
    try:
        import zstandard                                # type: ignore
        return lambda: zstandard.ZstdDecompressor().decompressobj()
    except ImportError:
        return None


class _RawParent:
    """A backing file that is a plain raw disk, read as it is."""

    def __init__(self, path):
        self.paths = [path]
        self.media_size = os.path.getsize(path)
        self._fh = open(path, "rb")

    def seek(self, offset):
        self._fh.seek(offset)

    def read(self, n):
        return self._fh.read(n)

    def close(self):
        self._fh.close()


def _crc32c_table():
    table = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0x82F63B78 if c & 1 else c >> 1
        table.append(c)
    return table


_CRC32C = _crc32c_table()


def _crc32c(data):
    """CRC-32C (Castagnoli), which VHDX uses for its headers, region tables and log
    entries; the standard library has only the other CRC-32."""
    crc = 0xFFFFFFFF
    table = _CRC32C
    for byte in data:
        crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def _crc32c_zeroed(data, at=4):
    """The CRC-32C of ``data`` with its four checksum bytes at ``at`` taken as zero."""
    return _crc32c(bytes(data[:at]) + b"\0\0\0\0" + bytes(data[at + 4:]))


def _vhd_split(path):
    """True when ``path`` is part of a VHD that Virtual PC 2004 or earlier split into
    files (name.vhd, then name.v01, name.v02 and on, the footer at the end of the last,
    per the VHD specification)."""
    base, ext = os.path.splitext(path)
    if re.fullmatch(r"\.v\d\d", ext, re.I):
        return True
    return ext.lower() == ".vhd" and any(os.path.exists(base + e) for e in (".v01", ".V01"))


def _uuid_text(raw):
    """A 16-byte identifier as the usual hyphenated text, big-endian as stored."""
    h = raw.hex()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


class EwfImage:
    """An EWF-E01, EWF-S01, EWF2-Ex01, AFF or AFD acquisition, read as one seekable stream,
    or an EWF-L01, read as its media data with its entries in ``logical_entries``.

    ``media_size`` is the size of the disk that was acquired, which is what
    ``seek`` and ``read`` address. The segment files themselves are an
    implementation detail and their sizes are not it.

    ``password`` opens an encrypted Apple disk image; it is used while the image is
    indexed, to unwrap each file's keys, and is not kept. The unwrapped keys stay
    in memory while the image is open, since every read needs them.
    """

    def __init__(self, path, segments=None, password=None, private_key=None):
        self._password = password
        self._private_key = private_key
        self._keys: dict[str, object] = {}      # path -> _EncrcdsaKey, or None
        self._band_key = None
        self.encryption = None
        self._afd = None if segments else _afd_directory(path)
        if segments:
            self.paths = list(segments)
        elif self._afd:
            self.paths = _afd_members(self._afd)
        elif _is_aff(path) or is_aff4(path) or apple_image_kind(path):
            self.paths = [os.path.abspath(path)]
        elif _vhd_split(path):
            raise EwfFormatError(f"{os.path.basename(path)} is part of a VHD split into "
                                 f"files by Virtual PC 2004 or earlier (.vhd, .v01 and "
                                 f"on), which ewfprobe does not read")
        elif virtual_disk_kind(path):
            self.paths = [os.path.abspath(path)]
        elif adcrypt_set(path):
            self.paths = adcrypt_set(path)
        elif _ad1_named(os.path.basename(path)):
            self.paths = ad1_segments(path)
        elif is_ad1(path):                      # an AD1 file named otherwise
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
        self._aff_pages: dict[int, tuple[int, int, int, int, str | None]] = {}
        self._aff_badflag = b""
        self._aff_key = None
        self.aff_header_lost: list[str] = []
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
        self.aff4 = None
        self._aff4 = None
        self._aff4_reader = None
        # Virtual disks: what the file records about itself, the block table, and
        # the disk it depends on, for a differencing disk.
        self.vhd = None
        self._vhd_bat: list[int] = []
        self._vhd_bitmaps: OrderedDict[int, bytes] = OrderedDict()
        self.parent = None
        self.vhdx = None
        self._vhdx_bat: list[int] = []
        self._vhdx_overlay: dict[int, bytes | None] = {}
        self.vmdk = None
        self._vmdk_extents: list[dict] = []
        self.qcow = None
        # AD1: what the image records about itself, and how its logical space maps
        # onto its files.
        self.ad1 = None
        self._ad1_usable = 0
        self._ad1_total = 0
        self._ad1_sizes: list[int] = []
        self._ad1_window = (0, b"")

        self._tables: list[_Table] = []
        self._table_starts: list[int] = []
        try:
            self._index()
        finally:
            self._password = None               # every file's keys are unwrapped by now

    # -- construction ------------------------------------------------------

    def _handle(self, i):
        fh = self._handles.get(i)
        if fh is None:
            if len(self._handles) >= MAX_OPEN:
                _old, stale = self._handles.popitem(last=False)
                stale.close()
            fh = (open(self.paths[i], "rb") if self.encryption is None
                  else self._content(self.paths[i])[0])
            self._handles[i] = fh
        else:
            self._handles.move_to_end(i)
        return fh

    def _content(self, path):
        """``path``'s content as (a file object, its size), decrypted when the file is
        an encrypted Apple disk image; each file is unlocked once."""
        return _open_content(path, self._password, self._keys, self._private_key)

    def _content_size(self, path):
        fh, size = self._content(path)
        fh.close()
        return size

    def _index(self):
        """Walk every segment once and build the chunk offset index."""
        kind = apple_image_kind(self.paths[0])
        magic = b""
        if not os.path.isdir(self.paths[0]):
            with open(self.paths[0], "rb") as fh:
                magic = fh.read(8)
        if kind == "ENCRYPTED":
            self._index_encrypted()
            return
        if kind == FORMAT_SPARSEBUNDLE:
            self._index_sparsebundle()
            return
        if kind == FORMAT_SPARSEIMAGE:
            self._index_sparseimage()
            return
        if kind == FORMAT_UDIF:
            self._index_udif()
            return
        if virtual_disk_kind(self.paths[0]) == FORMAT_VHD:
            self._index_vhd()
            return
        if virtual_disk_kind(self.paths[0]) == FORMAT_VHDX:
            self._index_vhdx()
            return
        if virtual_disk_kind(self.paths[0]) == FORMAT_VMDK:
            self._index_vmdk()
            return
        if virtual_disk_kind(self.paths[0]) == FORMAT_QCOW:
            self._index_qcow()
            return
        if magic == ADCRYPT_SIGNATURE:
            magic = self._unlock_adcrypt()
            if magic is None:
                self._index_adcrypt_raw()
                return
        if magic == AD1_SIGNATURE[:8]:
            self._index_ad1()
            return
        if magic == LEF2_SIGNATURE:
            raise EwfFormatError(
                f"{os.path.basename(self.paths[0])} is Lx01 logical evidence, which "
                f"ewfprobe does not read")
        logical = magic == LVF_SIGNATURE
        if magic == SIGNATURE_V2:
            self._index_v2()
            return
        if magic == AF_HEADER or (magic[:4] == b"AFF\x00" and _is_aff(self.paths[0])):
            self._index_aff()
            return
        if magic[:4] == b"PK\x03\x04" and is_aff4(self.paths[0]):
            self._index_aff4()
            return
        chunks = 0
        volume_seen = False
        last_name = None
        for i, path in enumerate(self.paths):
            fh = self._handle(i)
            size_on_disk = (os.path.getsize(path) if self.encryption is None
                            else self._content_size(path))
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
        """An L01 or AD1 entry's content as a seekable, read-only file object."""
        if self.format == FORMAT_AD1:
            return io.BufferedReader(_Ad1File(self, entry, self._ad1_chunks(entry)),
                                     buffer_size=1 << 16)
        if self.format != FORMAT_L01:
            raise EwfFormatError("only an L01 or AD1 holds entries")
        return io.BufferedReader(_LogicalFile(self, self._entry_runs(entry), entry.size),
                                 buffer_size=1 << 16)

    def read_entry(self, entry):
        """An L01 or AD1 entry's content, whole."""
        with self.open_entry(entry) as fh:
            return fh.read()

    def find_entry(self, path):
        """The first L01 or AD1 entry, in tree order, whose path (its names joined by
        "/") is ``path``."""
        path = path.strip("/")
        for entry in self.logical_entries:
            if entry.path == path:
                return entry
        kind = "AD1" if self.format == FORMAT_AD1 else "L01"
        raise EwfFormatError(f"no {kind} entry has the path {path!r}")

    def _walk_aff(self, i):
        """One AFF file's segments, walked once: where each page is, and the content
        of every small segment."""
        path = self.paths[i]
        name_of_file = os.path.basename(path)
        fh = self._handle(i)
        end = os.path.getsize(path)
        offset = _aff_start(fh, end)
        if offset is None:
            raise EwfFormatError(f"{name_of_file} is not an AFF file")
        if offset == 0:
            self.aff_header_lost.append(name_of_file)
        # A page or segment stored both in the clear and encrypted (a copy the
        # encryption left behind) is read encrypted, as AFFLIB reads it.
        pages: dict[int, tuple[int, int, int, str | None]] = {}
        small: dict[str, tuple[int, bytes]] = {}
        sealed: dict[str, tuple[int, bytes]] = {}
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
            encrypted = name.endswith(AF_AES256_SUFFIX)
            base = name[:-len(AF_AES256_SUFFIX)] if encrypted else name
            page = _AF_PAGE_NAME.fullmatch(base)
            if page:
                n = int(page.group(1))
                if encrypted or n not in pages or pages[n][3] is None:
                    pages[n] = (data_offset, data_len, arg, base if encrypted else None)
            elif base and data_len <= _AFF_MAX_SMALL:
                fh.seek(data_offset)
                (sealed if encrypted else small)[base] = (arg, _read_exactly(fh, data_len))
            offset = tail + _AF_SEGTAIL.size
        return pages, small, sealed, end

    def _index_afm(self, label, small, page_size, image_size):
        """Find an AFM's raw files and check them against its metadata; its pages
        are read from them, never from the metadata file."""
        ext = small.get("raw_image_file_extension", (0, b""))[1].rstrip(b"\x00")
        try:
            ext = ext.decode("ascii")
        except UnicodeDecodeError:
            ext = ""
        if len(ext) != 3 or not ext.isalnum():
            raise EwfFormatError(f"{label} is an AFM whose raw file extension is "
                                 f"{ext!r}, not three letters or digits")
        stem, dot, own = self.paths[0].rpartition(".")
        if not dot or len(own) != 3:
            raise EwfFormatError(f"{label} is an AFM, and AFFLIB finds its raw files only "
                                 f"from a name ending in a three-letter extension (.afm)")
        raw = [f"{stem}.{ext}"]
        if not os.path.isfile(raw[0]):
            raise EwfIncompleteSetError(f"{label} is an AFM, and its disk is kept in "
                                        f"{os.path.basename(raw[0])} and the files after "
                                        f"it, which is not beside it")
        while True:
            nxt = _afm_next_extension(raw[-1][-3:])
            if nxt is None or not os.path.isfile(f"{stem}.{nxt}"):
                break
            raw.append(f"{stem}.{nxt}")
        sizes = [os.path.getsize(p) for p in raw]
        if len(raw) > 1 and any(size != sizes[0] for size in sizes[1:-1]):
            raise EwfFormatError(f"{label}: its raw files are not all the size of the "
                                 f"first but the last, which AFFLIB requires")
        per_file = _af_quad(small.get("pages_per_raw_image_file")) or 0
        if len(raw) > 1 and per_file and sizes[0] != per_file * page_size:
            raise EwfFormatError(
                f"{label}: its raw files are {sizes[0]:,} bytes each, and it records "
                f"{per_file:,} pages of {page_size:,} bytes per file")
        if sum(sizes) != image_size:
            error = EwfIncompleteSetError if sum(sizes) < image_size else EwfFormatError
            raise error(f"{label} records an image of {image_size:,} bytes, and its raw "
                        f"files ({os.path.basename(raw[0])} .. "
                        f"{os.path.basename(raw[-1])}) hold {sum(sizes):,}")
        self.format = FORMAT_AFM
        self.paths = [self.paths[0]] + raw
        self.sizes = self.sizes[:1] + sizes
        self._aff_pages = {}
        self._afm_starts = [0]
        for size in sizes[:-1]:
            self._afm_starts.append(self._afm_starts[-1] + size)

    def _chunk_data_afm(self, n):
        start = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - start)
        out = []
        i = bisect.bisect_right(self._afm_starts, start) - 1
        at = start
        while want > 0:
            fh = self._handle(i + 1)
            fh.seek(at - self._afm_starts[i])
            piece = _read_exactly(fh, min(want, self.sizes[i + 1]
                                          - (at - self._afm_starts[i])))
            out.append(piece)
            at += len(piece)
            want -= len(piece)
            i += 1
        return b"".join(out)

    def _aff_unlock(self, label, keys):
        """The file key of an encrypted AFF, from the passphrase or the private key
        given, and what opened it recorded in ``encryption``."""
        wrapped = keys.get(_AF_AFFKEY, (0, b""))[1]
        seals = sorted((int(m.group(1)), data) for name, (_arg, data) in keys.items()
                       if (m := _AF_AFFKEY_EVP.fullmatch(name)))
        which = ("a certificate" if len(seals) == 1
                 else f"one of the {len(seals)} certificates")
        opens = (["its passphrase"] if wrapped else []) + (
            [f"the private key of {which} it is sealed to"] if seals else [])
        if not opens:
            raise EwfFormatError(f"{label} has encrypted segments and no key segment to "
                                 f"open them with")
        if _AES is None:
            raise EwfFormatError(f"{label} is an encrypted AFF; reading one needs the "
                                 f"optional pycryptodome package (pip install "
                                 f"pycryptodome), which this Python does not have")
        tried = []
        if self._password is not None and wrapped:
            key = _aff_key_from_passphrase(label, wrapped, self._password)
            if key is not None:
                self.encryption = {"container": "AFF (AFFLIB)", "cipher": "AES-256-CBC",
                                   "key_wrap": "AES-256-ECB", "kdf": "SHA-256",
                                   "opened_with": "passphrase"}
                return key
            tried.append("the password given is not its passphrase")
        if self._private_key is not None and seals:
            rsa = _private_key(self._private_key)
            for number, stored in seals:
                key = _aff_key_from_seal(stored, rsa)
                if key is not None:
                    self.encryption = {"container": "AFF (AFFLIB)", "cipher": "AES-256-CBC",
                                       "key_wrap": "RSA PKCS#1 v1.5 and AES-256-CBC",
                                       "opened_with": f"private key (affkey_evp{number})"}
                    return key
            tried.append(f"the private key opens none of the {len(seals)} sealed "
                         f"key{'' if len(seals) == 1 else 's'}")
        if tried:
            raise EwfWrongPasswordError(f"{label} is an encrypted AFF: {'; '.join(tried)}")
        needs = "password" if wrapped else "private key"
        raise EwfPasswordRequiredError(
            f"{label} is an encrypted AFF and opens only with {' or '.join(opens)}",
            needs=needs)

    def _same_page(self, n, first, second):
        """A page stored in two files of an AFD has to be the same page twice."""
        def stored(location):
            i, offset, length, arg, _encrypted = location
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
        walked = [self._walk_aff(i) for i in range(len(self.paths))]
        # The key segments are read from the first file that holds each, as every
        # other segment is; an image with any encrypted segment needs the key.
        keys: dict[str, tuple[int, bytes]] = {}
        for _pages, seen, _sealed, _end in walked:
            for key, value in seen.items():
                if key == _AF_AFFKEY or _AF_AFFKEY_EVP.fullmatch(key):
                    keys.setdefault(key, value)
        if any(w[2] or any(p[3] for p in w[0].values()) for w in walked):
            self._aff_key = self._aff_unlock(label, keys)
        for i, (pages, seen, sealed, end) in enumerate(walked):
            path = self.paths[i]
            self.sizes.append(end)
            if self._aff_key is not None:
                seen = dict(seen)
                for key, (arg, data) in sealed.items():
                    seen[key] = (arg, _aff_decrypt(self._aff_key, key, data))
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
            for n, (offset, length, arg, encrypted) in pages.items():
                if n in self._aff_pages:
                    self._same_page(n, self._aff_pages[n],
                                    (i, offset, length, arg, encrypted))
                else:
                    self._aff_pages[n] = (i, offset, length, arg, encrypted)

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
        if small.get("aff_file_type", (0, b""))[1] == b"AFM" and self.format == FORMAT_AFF:
            self._index_afm(label, small, page_size, image_size)
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
                    or _AF_AFFKEY_EVP.fullmatch(key) or key.endswith(AF_SIG256_SUFFIX)):
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
        if self.format == FORMAT_AFM:           # every page is in the raw files
            self._indexed_chunks = needed
            return
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
        i, offset, length, arg, encrypted = location
        fh = self._handle(i)
        fh.seek(offset)
        raw = _read_exactly(fh, length)
        if encrypted:
            raw = _aff_decrypt(self._aff_key, encrypted, raw)
        if not arg & AF_PAGE_COMPRESSED:
            return raw
        algorithm = arg & AF_PAGE_COMP_ALG_MASK
        if algorithm == AF_PAGE_COMP_ALG_ZERO:
            if len(raw) != 4:
                raise EwfFormatError(f"page {n} is a zero page with {len(raw)} bytes, "
                                     f"not 4")
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

    def _index_aff4(self):
        """Open an AFF4 container: find the image it describes, the map or image
        stream that holds its bytes, and what it records about itself."""
        c = _Aff4Container(self, self.paths[0])
        self._aff4 = c
        images = [s for s in c.graph if c.is_a(s, "Image")]
        image = images[0] if images else None
        data = None
        if image is not None:
            ds = c.one(image, "dataStream")
            data = ds[1] if ds else (image if c.is_a(image, "Map") else None)
        if data is None:
            maps = [s for s in c.graph if c.is_a(s, "Map")]
            streams = [s for s in c.graph if c.is_a(s, "ImageStream")]
            data = (maps or streams or [None])[0]
        if data is None:
            raise EwfFormatError(
                f"{os.path.basename(self.paths[0])} describes no image, map or image "
                f"stream; an AFF4-L container of logical files is not read")
        reader = c.reader(data)
        self._aff4_reader = reader
        self.format = FORMAT_AFF4
        self.media_size = self.size = reader.size
        self.chunk_size = _AFF4_VIRTUAL_CHUNK
        self.chunk_count = self._indexed_chunks = -(-self.media_size // self.chunk_size)
        self.sector_size = (c.number(image, "blockSize") if image else None) or 512
        self.sector_count = self.media_size // self.sector_size
        self.sectors_per_chunk = self.chunk_size // self.sector_size
        maps, streams = self._aff4_parts()
        self.compression_level = ", ".join(sorted({s.codec for s in streams})) or "none"
        for subject in (image, data):
            for obj in (c.values(subject, "hash") if subject else ()):
                kind = _aff4_hash_kind(obj[2]) if obj[0] == "lit" else None
                if kind and kind[0] != "block map":
                    self.stored_hashes.setdefault(kind[0], obj[1].lower())
        related = [image, data] + [s for s in c.graph if any(
            o[1] in (image, data) for o in c.values(s, "target") if o[0] == "iri")]
        for subject in (s for s in related if s):
            for predicate, objs in c.props(subject).items():
                local = predicate.rsplit("#", 1)[-1]
                key = _AFF4_METADATA.get(local)
                if key is None or not predicate.startswith((_AFF4_NS, _AFF4_LEGACY_NS)):
                    continue
                for obj in objs:
                    if obj[0] == "lit" and obj[1].strip():
                        have = self.metadata.get(key)
                        if have is None:
                            self.metadata[key] = obj[1].strip()
                        elif obj[1].strip() not in have.split("; "):
                            self.metadata[key] = have + "; " + obj[1].strip()
        version = c.volumes[0].version
        if version.get("tool"):
            self.metadata.setdefault("acquiry_software_version", version["tool"])

        def short(iri):
            for name, base in sorted(c.prefixes.items(), key=lambda kv: -len(kv[1])):
                if iri.startswith(base) and base:
                    return f"{name}:{iri[len(base):]}"
            return iri

        vendor = []
        for predicate, objs in (c.props(image).items() if image else ()):
            if predicate.startswith((_AFF4_NS, _AFF4_LEGACY_NS, _RDF_TYPE)):
                continue
            for obj in objs:
                vendor.append((short(predicate), short(obj[1]) if obj[0] == "iri"
                               else obj[1]))
        self.aff4 = {
            "volume": c.volumes[0].urn,
            "version": (f"{version['major']}.{version['minor']}"
                        if "major" in version and "minor" in version else None),
            "tool": version.get("tool"),
            "image": image,
            "images": len(images),
            "image_types": [short(o[1]) for o in (c.props(image).get(_RDF_TYPE, ())
                                                  if image else ()) if o[0] == "iri"],
            "data_stream": data,
            "streams": [{"urn": st.urn, "compression": st.codec, "method": st.method,
                         "chunk_size": st.chunk_size, "chunks_in_segment": st.per_bevy,
                         "size": st.size,
                         "file": os.path.basename(c.member(st.bevy(0))[0].path)}
                        for st in streams],
            "coverage": (list(reader.coverage().items()) if isinstance(reader, _Aff4Map)
                         else [(reader.name, reader.size)]),
            "vendor_properties": vendor,
        }

    def _aff4_parts(self, readers=None):
        """The maps and image streams an AFF4 image reads through, each once."""
        maps, streams, seen = [], [], set()
        todo = list(readers or [self._aff4_reader])
        while todo:
            r = todo.pop(0)
            if id(r) in seen:
                continue
            seen.add(id(r))
            if isinstance(r, _Aff4Map):
                maps.append(r)
                todo.extend(r.targets)
            elif isinstance(r, _Aff4ImageStream):
                streams.append(r)
        return maps, streams

    def _chunk_data_aff4(self, n):
        start = n * self.chunk_size
        return self._aff4_reader.read_at(start, min(self.chunk_size,
                                                    self.media_size - start))

    def _verify_aff4(self, progress):
        """Recompute what an AFF4 container records about its own data (AFF4 Standard
        6): each image stream's linear hashes, each chunk's block hash and the hash of
        each stream's block hashes, each map's segment hashes, the block map hash of
        each map with its stream, and the image's hash over those. The orderings are
        pyaff4's (block_hasher.py), which the reference images agree with."""
        c = self._aff4
        image = self.aff4["image"]
        roots = [self._aff4_reader]
        if image is not None:                     # a striped image names a map per file
            for obj in c.values(image, "dataStream"):
                if obj[0] == "iri" and obj[1] != self.aff4["data_stream"]:
                    roots.append(c.reader(obj[1]))
        maps, streams = self._aff4_parts(roots)
        checks = []
        outer: dict = {}                          # stream urn -> {algo: digest of block hashes}
        total = sum(st.size for st in streams) or 1
        done = 0
        for st in streams:
            volume = c.member(st.bevy(0))[0]
            standard = volume.find(st.bevy(0) + ".index") is not None

            def segment(b, algo, st=st, standard=standard):
                return f"{st.bevy(b)}{'.' if standard else '/'}blockHash.{algo}"

            algos = [a for a in _AFF4_BLOCK_ORDER
                     if c.member(segment(0, a), needed=False) is not None]
            linear = []
            for obj in c.values(st.urn, "hash"):
                kind = _aff4_hash_kind(obj[2]) if obj[0] == "lit" else None
                if kind and kind[0] != "block map":
                    linear.append((kind[0], obj[1].lower(), hashlib.new(kind[1])))
            # the hash kept of each algorithm's block hashes: the BlockHashes object's
            # own datatype in the standard, the block algorithm itself before it
            wraps = {}
            for a in algos:
                if standard:
                    obj = c.one(f"{st.urn}/blockhash.{a}", "hash")
                    kind = _aff4_hash_kind(obj[2]) if obj and obj[0] == "lit" else None
                    if kind and kind[0] != "block map":
                        wraps[a] = (kind[0], obj[1].lower(), hashlib.new(kind[1]))
                else:
                    for obj in c.values(st.urn, "blockHashesHash"):
                        kind = _aff4_hash_kind(obj[2]) if obj[0] == "lit" else None
                        if kind and kind[1] == a:
                            wraps[a] = (kind[0], obj[1].lower(), hashlib.new(a))
            bad = {a: 0 for a in algos}
            stored_blocks: dict = {}
            for k in range(st.chunk_count):
                data = st.chunk(k)
                for _name, _want, h in linear:
                    h.update(data)
                b, i = divmod(k, st.per_bevy)
                for a in algos:
                    raw = stored_blocks.get((a, b))
                    if raw is None:
                        if len(stored_blocks) > 16:
                            stored_blocks.clear()
                        raw = c.read_member(segment(b, a))
                        stored_blocks[(a, b)] = raw
                    digest = hashlib.new(a, data).digest()
                    size = len(digest)
                    if raw[i * size:(i + 1) * size] != digest:
                        bad[a] += 1
                    if a in wraps:
                        wraps[a][2].update(digest)
                done += len(data)
                if progress:
                    progress(done, total)
            for name, want, h in linear:
                checks.append((f"image stream {st.urn}", name, want, h.hexdigest()))
            for a in algos:
                n = st.chunk_count
                checks.append((f"chunk hashes of {st.urn}", a.upper(),
                               f"{n:,} of {n:,} agree", f"{n - bad[a]:,} of {n:,} agree"))
            outer[st.urn] = {}
            for a, (name, want, h) in wraps.items():
                checks.append((f"block hashes of {st.urn}", name, want, h.hexdigest()))
                outer[st.urn][a] = h.digest()
        block_map: dict = {}
        for m in maps:
            parts = {"map": c.read_member(m.urn + "/map"), "idx": c.read_member(m.urn + "/idx")}
            if c.member(m.urn + "/mapPath", needed=False) is not None:
                parts["mapPath"] = c.read_member(m.urn + "/mapPath")
            computed = {}
            for prop, pieces in (("mapIdxHash", ["idx"]), ("mapPointHash", ["map"]),
                                 ("mapPathHash", ["mapPath"]),
                                 ("mapHash", ["map", "idx", "mapPath"])):
                obj = c.one(m.urn, prop)
                kind = _aff4_hash_kind(obj[2]) if obj and obj[0] == "lit" else None
                if kind is None or kind[0] == "block map":
                    continue
                h = hashlib.new(kind[1])
                for piece in pieces:
                    h.update(parts.get(piece, b""))
                checks.append((f"{prop} of map {m.urn}", kind[0], obj[1].lower(),
                               h.hexdigest()))
                computed[prop] = h.digest()
            # the pre-standard images call a map's block map hash blockHashesHash
            stored = c.one(m.urn, "blockMapHash") or c.one(m.urn, "blockHashesHash")
            kind = _aff4_hash_kind(stored[2]) if stored and stored[0] == "lit" else None
            home = c.member(m.urn + "/map")[0]
            local = [st for st in streams if c.member(st.bevy(0))[0] is home]
            if kind is None or len(local) != 1:
                continue
            h = hashlib.new(kind[1])
            for a in _AFF4_BLOCK_ORDER:
                if a in outer.get(local[0].urn, {}):
                    h.update(outer[local[0].urn][a])
            for prop in ("mapPointHash", "mapIdxHash", "mapPathHash"):
                if prop in computed:
                    h.update(computed[prop])
            checks.append((f"block map hash of map {m.urn}", kind[1].upper(),
                           stored[1].lower(), h.hexdigest()))
            block_map[m.urn] = h.digest()
        for obj in (c.values(image, "hash") if image else ()):
            kind = _aff4_hash_kind(obj[2]) if obj[0] == "lit" else None
            if not kind or kind[0] != "block map" or not block_map:
                continue
            if len(block_map) == 1:
                got = next(iter(block_map.values())).hex()
            else:                                 # one level up, by map URI (pyaff4)
                h = hashlib.new(kind[1])
                for urn in sorted(block_map):
                    h.update(block_map[urn])
                got = h.hexdigest()
            checks.append((f"image {image}, over its block map hashes", kind[1].upper(),
                           obj[1].lower(), got))
        return [{"what": what, "algorithm": algo, "stored": want, "computed": got,
                 "match": want == got} for what, algo, want, got in checks]

    def _apple_finish(self, sectors, fmt, sizes=None):
        """Fields every reader of the stream relies on, for an Apple disk image."""
        self.format = fmt
        self.sector_size = 512
        self.sector_count = sectors
        self.media_size = sectors * 512
        self.size = self.media_size
        self.sizes = sizes if sizes is not None else [os.path.getsize(p)
                                                      for p in self.paths]
        if fmt in (FORMAT_UDIF, FORMAT_SPARSEBUNDLE, FORMAT_UDRW, FORMAT_RAW):
            self.chunk_size = _APPLE_VIRTUAL_CHUNK
        self.sectors_per_chunk = self.chunk_size // 512
        self.chunk_count = self._needed_chunks()
        self._indexed_chunks = self.chunk_count

    def _index_encrypted(self):
        """Unlock an encrypted Apple disk image and index what it decrypts to: a UDIF
        image, a sparse image, or the disk itself (an encrypted read-write image), or,
        for a sparse bundle, what its bands decrypt to."""
        path = self.paths[0]
        name = os.path.basename(path)
        if os.path.isdir(path):
            with open(os.path.join(path, "token"), "rb") as fh:
                self._band_key = _encrcdsa_unlock(fh, name, self._password,
                                                  self._private_key)
            self._note_encryption(self._band_key)
            self._index_sparsebundle()
            return
        with open(path, "rb") as fh:
            version_2 = fh.read(8) == DMG_ENCRYPTED_SIGNATURE
        if not version_2:                       # apple_image_kind saw a version 1 end
            raise EwfFormatError(f"{name} is an encrypted Apple disk image in the older "
                                 f"version 1 format (cdsaencr), which ewfprobe does not "
                                 f"read")
        fh, size = self._content(path)
        self._note_encryption(self._keys[path])
        with fh:
            head = fh.read(4)
            tail = b""
            if size >= UDIF_TRAILER_SIZE:
                fh.seek(size - UDIF_TRAILER_SIZE)
                tail = fh.read(4)
        if head == SPARSEIMAGE_SIGNATURE:
            self._index_sparseimage()
        elif tail == UDIF_TRAILER_SIGNATURE:
            self._index_udif()
        else:
            if size % 512:
                raise EwfFormatError(f"{name} decrypts to {size:,} bytes, not a whole "
                                     f"number of 512-byte sectors")
            self.compression_level = "none"
            self._apple_finish(size // 512, FORMAT_UDRW)

    def _unlock_adcrypt(self):
        """Unlock an acquisition FTK Imager encrypted with AD encryption, so every
        segment reads decrypted, and return the signature of what it holds."""
        path = self.paths[0]
        name = os.path.basename(path)
        with open(path, "rb") as fh:
            key = _adcrypt_unlock(fh, name, self._password, self._private_key)
        for i, segment in enumerate(self.paths):
            self._keys[segment] = _AdcryptSegment(key, i)
        self.encryption = {"container": "AD encryption (FTK Imager)",
                           "cipher": f"AES-{key.key_bits}-CTR",
                           "key_wrap": f"AES-{key.key_bits}-CTR",
                           "kdf": f"PBKDF2-HMAC-SHA1 of {key.hash_name.upper()}",
                           "kdf_rounds": key.iterations}
        if key.sealed:
            self.encryption.update(kdf="PBKDF2-HMAC-SHA1 of an empty password",
                                   salt_wrap="RSA PKCS#1 v1.5",
                                   opened_with="private key of its certificate")
        fh, _size = self._content(path)
        with fh:
            inner = fh.read(len(AD1_SIGNATURE))
        if inner == AD1_SIGNATURE:
            return inner[:8]
        if inner[:8] in (SIGNATURE, SIGNATURE_V2, LVF_SIGNATURE, LEF2_SIGNATURE):
            return inner[:8]
        if _ad1_named(name):                    # before EWF: .ad1 fits its pattern too
            raise EwfFormatError(f"{name} is named as a file of an AD1 set and decrypts "
                                 f"to something that is not AD1")
        if _ewf_named(name):
            raise EwfFormatError(f"{name} is named as an EWF segment and decrypts to "
                                 f"something that is not EWF")
        return None                             # a raw (dd) image: the disk itself

    def _index_adcrypt_raw(self):
        """An AD-encrypted raw image: its files, decrypted and joined, are the disk."""
        sizes = [self._content_size(p) for p in self.paths]
        starts, total = [], 0
        for size in sizes:
            starts.append(total)
            total += size
        if total % 512:
            raise EwfFormatError(f"{os.path.basename(self.paths[0])} decrypts to "
                                 f"{total:,} bytes, not a whole number of 512-byte "
                                 f"sectors")
        self._raw_starts = starts
        self._raw_sizes = sizes
        self.compression_level = "none"
        self._apple_finish(total // 512, FORMAT_RAW)

    def _chunk_data_raw(self, n):
        """Chunk ``n`` of a decrypted raw set, read across its files."""
        pos = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - pos)
        out = bytearray()
        i = bisect.bisect_right(self._raw_starts, pos) - 1
        while len(out) < want:
            fh = self._handle(i)
            fh.seek(pos + len(out) - self._raw_starts[i])
            piece = fh.read(min(want - len(out),
                                self._raw_starts[i] + self._raw_sizes[i] - pos - len(out)))
            if not piece:
                raise EwfIncompleteSetError(f"{os.path.basename(self.paths[i])} is "
                                            f"shorter than the set needs")
            out += piece
            if pos + len(out) >= self._raw_starts[i] + self._raw_sizes[i]:
                i += 1
        return bytes(out)

    # -- AD1 ---------------------------------------------------------------

    def _index_ad1(self):
        """An AD1: check its files' margins, read its logical header and walk its
        item tree. The image's stream is its logical space."""
        self.format = FORMAT_AD1
        first = os.path.basename(self.paths[0])
        sizes = [self._content_size(p) if self.encryption else os.path.getsize(p)
                 for p in self.paths]
        count = segment_size = None
        for i, path in enumerate(self.paths):
            name = os.path.basename(path)
            fh = self._handle(i)
            fh.seek(0)
            head = fh.read(_AD1_SEGMENT.size)
            if len(head) != _AD1_SEGMENT.size or not head.startswith(AD1_SIGNATURE):
                raise EwfFormatError(f"{name} does not begin with the AD1 signature")
            _sig, _one, _two, number, files, size, margin = _AD1_SEGMENT.unpack(head)
            if margin != _AD1_MARGIN:
                raise EwfFormatError(f"{name} records a {margin:,}-byte margin; only "
                                     f"{_AD1_MARGIN} is read")
            if count is None:
                count, segment_size = files, size
            elif (files, size) != (count, segment_size):
                raise EwfFormatError(f"{name} records a set of {files:,} files of "
                                     f"{size:,} bytes where {first} records {count:,} "
                                     f"of {segment_size:,}")
            if number != i + 1:
                raise EwfFormatError(f"{name} says it is file {number} of the AD1 set, "
                                     f"but it sits at position {i + 1}")
        if len(self.paths) < count:
            raise EwfIncompleteSetError(
                f"{first} records {count:,} files in its set and {len(self.paths):,} "
                f"{'is' if len(self.paths) == 1 else 'are'} beside it. Put every file "
                f"of the set in one folder before opening it.")
        if len(self.paths) > count:
            raise EwfFormatError(f"{first} records {count:,} files in its set and "
                                 f"{len(self.paths):,} are numbered as its files")
        if segment_size <= _AD1_MARGIN:
            raise EwfFormatError(f"{first} records a segment size of {segment_size:,} "
                                 f"bytes, which holds no data")
        for i, (path, size) in enumerate(zip(self.paths, sizes)):
            last = i == len(sizes) - 1
            if (size < segment_size and not last) or size <= _AD1_MARGIN:
                raise EwfIncompleteSetError(
                    f"{os.path.basename(path)} is {size:,} bytes where every file of "
                    f"the set but the last is {segment_size:,}; the file is cut short")
            if size > segment_size:
                raise EwfFormatError(f"{os.path.basename(path)} is {size:,} bytes, "
                                     f"longer than the set's {segment_size:,}")
        self._ad1_usable = segment_size - _AD1_MARGIN
        self._ad1_sizes = [size - _AD1_MARGIN for size in sizes]
        total = self._ad1_total = sum(self._ad1_sizes)
        head = self._ad1_read(0, min(_AD1_HEADER.size, total))
        if not head.startswith(AD1_LOGICAL_SIGNATURE):
            raise EwfFormatError(f"{first} has no AD1 logical header after its margin")
        version = struct.unpack_from("<I", head, 16)[0] if len(head) >= 20 else None
        if version != 4:
            raise EwfFormatError(f"{first} is AD1 version {version}; only version 4, "
                                 f"which FTK Imager 3.4 and 4.7 write, is read")
        if len(head) < _AD1_HEADER.size:
            raise EwfFormatError(f"{first} ends inside its AD1 logical header")
        (_sig, _version, _one, chunk_size, meta_addr, first_item, name_length, tag,
         name_addr, footer, _zero, footer2) = _AD1_HEADER.unpack(head)
        if tag != b"AD\x00\x00":
            raise EwfFormatError(f"{first}'s AD1 logical header lacks its AD tag")
        if not 0 < chunk_size <= _AD1_MAX_VALUE:
            raise EwfFormatError(f"{first} records a chunk size of {chunk_size:,} bytes")
        for what, addr in (("first item", first_item), ("footer", footer),
                           ("source name", name_addr), ("metadata", meta_addr)):
            if addr >= total:
                raise EwfFormatError(f"{first} places its {what} at logical offset "
                                     f"{addr:,}, past the end of its data")
        if footer:
            self._ad1_check_footer(first, footer, footer2, total)
        if name_length > _AD1_MAX_NAME:
            raise EwfFormatError(f"{first} records a {name_length:,}-byte source name")
        source = self._ad1_read(name_addr, name_length).decode("utf-8", "surrogateescape")
        image_metadata = {}
        for _addr, _length, category, key, value in self._ad1_records(meta_addr,
                                                                      "the image"):
            image_metadata.setdefault((category, key), value)
        self.ad1 = {"version": version, "chunk_size": chunk_size,
                    "segment_size": segment_size, "segment_count": count,
                    "data_source": source, "first_item": first_item,
                    "footer": footer, "logical_size": total,
                    "image_metadata": image_metadata, "log": None}
        self.metadata = {"data_source": source}

        root = Ad1Entry((), None)
        order = []
        seen = set()
        work = [(first_item, root)]
        while work:
            addr, parent = work.pop()
            if not addr:
                continue
            if addr in seen:
                raise EwfFormatError(f"the AD1 item at logical offset {addr:,} is reached "
                                     f"twice; its tree loops")
            seen.add(addr)
            entry, next_item, child = self._ad1_item(addr, parent, total)
            parent.children.append(entry)
            order.append(entry)
            work.append((next_item, parent))
            work.append((child, entry))         # children before the next sibling
        self.logical_root = root
        self.logical_entries = order
        self._ad1_log()

        # The stream is the logical space, read through virtual chunks.
        self.sector_size = 0
        self.sector_count = 0
        self.media_size = self.size = total
        self.chunk_size = _APPLE_VIRTUAL_CHUNK
        self.sizes = [os.path.getsize(p) for p in self.paths]
        self.chunk_count = self._needed_chunks()
        self._indexed_chunks = self.chunk_count

    def _ad1_check_footer(self, first, footer, footer2, total):
        """The footer is two blocks, ATTRGUID at the address the logical header gives
        and LOCSGUID at its second footer address, each a tag, a zero and a count of
        20-byte entries, and the second ends where the image's data ends, on every
        AD1 in the README's validation. So its computed end shows a last file cut
        short, which no other address would reach, or bytes after it."""
        last = os.path.basename(self.paths[-1])
        end = footer
        for label in (b"ATTRGUID", b"LOCSGUID"):
            if label == b"LOCSGUID" and end != footer2:
                raise EwfFormatError(f"{first}'s AD1 footer places its second block at "
                                     f"logical offset {footer2:,}, where its first ends "
                                     f"at {end:,}")
            if end + _AD1_FOOTER_BLOCK.size > total:
                raise EwfIncompleteSetError(f"{last} ends inside its AD1 footer; the "
                                            f"file is cut short")
            tag, _zero, count = _AD1_FOOTER_BLOCK.unpack(
                self._ad1_read(end, _AD1_FOOTER_BLOCK.size))
            if tag != label:
                raise EwfFormatError(f"{first}'s AD1 footer has no {label.decode()} "
                                     f"block at logical offset {end:,}")
            end += _AD1_FOOTER_BLOCK.size + _AD1_FOOTER_ENTRY * count
        if end > total:
            missing = end - total
            raise EwfIncompleteSetError(f"{last} ends {missing:,} byte"
                                        f"{'' if missing == 1 else 's'} before the end "
                                        f"of its AD1 footer; the file is cut short")
        if end < total:
            extra = total - end
            raise EwfFormatError(f"{last} holds {extra:,} byte{'' if extra == 1 else 's'} "
                                 f"after its AD1 footer")

    def _ad1_read(self, offset, n):
        """``n`` bytes at ``offset`` of an AD1's logical space: its files with their
        margins left out, back to back. Small reads are served from a window of the
        space, since an item's header and records lie together."""
        start, window = self._ad1_window
        if start <= offset and offset + n <= start + len(window):
            return window[offset - start:offset + n - start]
        if n < _AD1_WINDOW:
            i, within = divmod(offset, self._ad1_usable)
            if i < len(self.paths) and within < self._ad1_sizes[i]:
                span = min(_AD1_WINDOW, self._ad1_sizes[i] - within)
                if span >= n:
                    self._ad1_window = (offset, self._ad1_span(offset, span))
                    return self._ad1_window[1][:n]
        return self._ad1_span(offset, n)

    def _ad1_span(self, offset, n):
        out = bytearray()
        while n > 0:
            i, within = divmod(offset, self._ad1_usable)
            if i >= len(self.paths) or within >= self._ad1_sizes[i]:
                raise EwfFormatError(f"the AD1 refers to logical offset {offset:,}, past "
                                     f"the end of its data")
            take = min(n, self._ad1_sizes[i] - within)
            fh = self._handle(i)
            fh.seek(_AD1_MARGIN + within)
            piece = fh.read(take)
            if len(piece) != take:
                raise EwfIncompleteSetError(f"{os.path.basename(self.paths[i])} ends "
                                            f"early; the file is cut short")
            out += piece
            offset += take
            n -= take
        return bytes(out)

    def _ad1_records(self, addr, where, keep=None):
        """The metadata records chained from ``addr``: (address, length, category,
        key, text) each, the text only for the (category, key) pairs in ``keep`` when
        that is given."""
        out = []
        seen = set()
        total = self._ad1_total
        while addr:
            if addr in seen:
                raise EwfFormatError(f"the metadata records of {where} loop")
            if addr >= total:
                raise EwfFormatError(f"a metadata record of {where} lies past the end "
                                     f"of the data")
            seen.add(addr)
            nxt, category, key, length = _AD1_RECORD.unpack(
                self._ad1_read(addr, _AD1_RECORD.size))
            if length > _AD1_MAX_VALUE:
                raise EwfFormatError(f"{where} has a {length:,}-byte metadata value")
            value = None
            if keep is None or (category, key) in keep:
                value = self._ad1_read(addr + _AD1_RECORD.size, length).decode(
                    "utf-8", "surrogateescape")
            elif addr + _AD1_RECORD.size + length > total:
                raise EwfFormatError(f"a metadata record of {where} lies past the end "
                                     f"of the data")
            out.append((addr, _AD1_RECORD.size + length, category, key, value))
            addr = nxt
        return out

    def _ad1_item(self, addr, parent, total):
        """The item at ``addr``: its entry, and the addresses of its next sibling and
        its first child."""
        next_item, child, meta, table, size, item_type, name_length = _AD1_ITEM.unpack(
            self._ad1_read(addr, _AD1_ITEM.size))
        if name_length > _AD1_MAX_NAME:
            raise EwfFormatError(f"the AD1 item at logical offset {addr:,} has a "
                                 f"{name_length:,}-byte name")
        tail = self._ad1_read(addr + _AD1_ITEM.size, name_length + 8)
        name = tail[:name_length].decode("utf-8", "surrogateescape")
        parent_addr = struct.unpack_from("<Q", tail, name_length)[0]
        names = parent.names + (name,)
        where = f"AD1 entry {'/'.join(names)}"
        if parent_addr != parent.address:
            raise EwfFormatError(f"{where} names its parent at logical offset "
                                 f"{parent_addr:,} but sits under the one at "
                                 f"{parent.address:,}")
        if size and not table:
            raise EwfFormatError(f"{where} holds {size:,} bytes and no chunk table")
        if table >= total:
            raise EwfFormatError(f"{where} places its chunk table past the end of the data")
        kept = {}
        for _raddr, _length, category, key, value in self._ad1_records(meta, where,
                                                                       _AD1_KEPT):
            if value is not None:
                kept.setdefault((category, key), value)
        entry = Ad1Entry(names, parent, addr, _AD1_ITEM.size + name_length + 8,
                         item_type, size, table, kept, meta, self)
        return entry, next_item, child

    def _ad1_chunks(self, entry):
        """The addresses bounding an AD1 entry's compressed chunks, in order."""
        if not entry.chunk_table:
            return [0]
        where = f"AD1 entry {entry.path}"
        count = struct.unpack("<Q", self._ad1_read(entry.chunk_table, 8))[0]
        need = -(-entry.size // self.ad1["chunk_size"])
        if count != need:
            raise EwfFormatError(f"{where}: its chunk table lists {count:,} chunks where "
                                 f"its {entry.size:,} bytes take {need:,}")
        addresses = struct.unpack(f"<{count + 1}Q",
                                  self._ad1_read(entry.chunk_table + 8, 8 * (count + 1)))
        if any(b < a for a, b in zip(addresses, addresses[1:])) or \
                addresses[-1] > self.ad1["logical_size"]:
            raise EwfFormatError(f"{where}: its chunk table's addresses are out of order "
                                 f"or past the end of the data")
        return list(addresses)

    def _ad1_log(self):
        """The image MD5 and SHA-1 FTK Imager records in its log beside the image
        (<first file>.txt), under Computed Hashes, when that log is there."""
        log = self.paths[0] + ".txt"
        try:
            with open(log, "rb") as fh:
                text = fh.read(1 << 20).decode("utf-8-sig", "replace")
        except OSError:
            return
        found, inside = {}, False
        for line in text.splitlines():
            if line.strip() == "[Computed Hashes]":
                inside = True
                continue
            if inside:
                m = re.match(r"\s*(MD5|SHA1) checksum:\s*([0-9a-fA-F]+)\s*$", line)
                if not m:
                    break
                found[m.group(1)] = m.group(2).lower()
        found = {k: v for k, v in found.items() if len(v) == (32 if k == "MD5" else 40)}
        if found:
            self.stored_hashes = found
            self.ad1["log"] = os.path.basename(log)

    def _chunk_data_ad1(self, n):
        pos = n * self.chunk_size
        return self._ad1_read(pos, min(self.chunk_size, self.media_size - pos))

    def _verify_ad1(self, block, progress):
        """FTK Imager's image hash of an AD1, and every entry's stored MD5 and SHA-1
        checked against its content.

        The image hash is taken over the logical header up to the first item, then
        the footer (from the address the header gives to the end of the data), then
        each item's header and metadata records in the order they lie in the image,
        and last the digest of all the items' content in that order; chunk tables and
        compressed chunks are not in it. The scheme is pyad1's reader, followed through
        the image's own addresses; it reproduces the hashes in FTK Imager's log on
        every image in the README's validation."""
        algos = ("MD5", "SHA1")
        image = {a: hashlib.new(a.lower()) for a in algos}
        content = {a: hashlib.new(a.lower()) for a in algos}
        total = self.ad1["logical_size"]
        head = self._ad1_read(0, self.ad1["first_item"])
        footer = self._ad1_read(self.ad1["footer"], total - self.ad1["footer"]) \
            if self.ad1["footer"] else b""
        for h in image.values():
            h.update(head)
            h.update(footer)
        wanted = sum(e.size for e in self.logical_entries)
        done = 0
        checked = {"md5": 0, "sha1": 0}
        mismatched = {"md5": [], "sha1": []}
        for entry in sorted(self.logical_entries, key=lambda e: e.address):
            item = self._ad1_read(entry.address, entry.header_length)
            for h in image.values():
                h.update(item)
            own = {"md5": hashlib.md5(), "sha1": hashlib.sha1()}
            if entry.size:
                try:
                    with self.open_entry(entry) as fh:
                        while True:
                            piece = fh.read(block)
                            if not piece:
                                break
                            for h in (*content.values(), *own.values()):
                                h.update(piece)
                            done += len(piece)
                            if progress:
                                progress(done, wanted)
                except EwfFormatError:
                    # A chunk that does not inflate: what was read of the entry fails
                    # its stored hashes, and the image hash fails with it.
                    pass
            for addr, length, *_rest in self._ad1_records(entry.metadata_address,
                                                          entry.path, keep=()):
                data = self._ad1_read(addr, length)
                for h in image.values():
                    h.update(data)
            for algo, stored in (("md5", entry.md5), ("sha1", entry.sha1)):
                if stored is not None:
                    checked[algo] += 1
                    if own[algo].hexdigest() != stored:
                        mismatched[algo].append(entry.path)
        for algo in algos:
            image[algo].update(content[algo].digest())
        return ({a: h.hexdigest() for a, h in image.items()}, done, checked, mismatched)

    def _note_encryption(self, key):
        if key.rounds is None:                  # opened with a certificate's private key
            self.encryption = {"container": "encrcdsa version 2",
                               "cipher": f"AES-{key.key_bits}", "key_wrap": key.wrap,
                               "opened_with": "private key of its certificate"}
            return
        self.encryption = {"container": "encrcdsa version 2",
                           "cipher": f"AES-{key.key_bits}", "key_wrap": key.wrap,
                           "kdf": "PBKDF2-HMAC-SHA1", "kdf_rounds": key.rounds}

    def _chunk_data_udrw(self, n):
        want = min(self.chunk_size, self.media_size - n * self.chunk_size)
        fh = self._handle(0)
        fh.seek(n * self.chunk_size)
        return _read_exactly(fh, want)

    def _index_udif(self):
        """Read the trailer and the block tables of a UDIF image into runs."""
        path = self.paths[0]
        name = os.path.basename(path)
        size = self._content_size(path)
        trailer = _udif_trailer(path, self._password, self._keys, self._private_key)
        if trailer is None:
            raise EwfFormatError(f"{name} has no UDIF trailer")
        (_sig, version, header_size, flags, running, fork_offset, fork_size,
         _rsrc_offset, _rsrc_size, segment_number,
         segment_count) = _UDIF_TRAILER.unpack_from(trailer)
        if header_size != UDIF_TRAILER_SIZE:
            raise EwfFormatError(f"{name}: the UDIF trailer says it is {header_size} "
                                 f"bytes, not {UDIF_TRAILER_SIZE}")
        if segment_number > 1:
            udif_segments(path, self._password, self._keys,  # raises, naming the file
                          self._private_key)
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
            self.paths = udif_segments(path, self._password, self._keys, self._private_key)
            joined = 0
            for index, part in enumerate(self.paths):
                part_name = os.path.basename(part)
                part_size = self._content_size(part)
                t = trailer if index == 0 else _udif_trailer(part, self._password,
                                                             self._keys, self._private_key)
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
            # One file: a chunk's position counts from the start of the data fork,
            # which the trailer places. hdiutil writes the fork at 0, where this is
            # also the file offset libmodi and libdmg-hfsplus read. Measured with a
            # copy moved 512 bytes into the file: hdiutil attach reads it when the
            # positions are left as they were and calls it corrupt when they are
            # shifted by 512, so it adds the fork's offset, as 7-Zip and dmgwiz do.
            self._forks.append((0, 0, fork_offset, fork_size))
            low, high = 0, fork_size
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
        xml = _read_exactly(fh, xml_size)
        # Some images count a byte or two past the end of the property list
        # (citruz/dmgwiz issue 19); hdiutil attach reads such an image, measured
        # with NUL and text bytes added, so what follows </plist> is not read.
        end = xml.rfind(b"</plist>")
        if end >= 0:
            xml = xml[:end + len(b"</plist>")]
        try:
            plist = plistlib.loads(xml)
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

    def _index_vhd(self):
        """Read a VHD's footer (or, when it fails its checksum, the copy at the start
        of a dynamic disk), and for a dynamic or differencing disk its header and
        block allocation table; open a differencing disk's parent."""
        path = self.paths[0]
        name = os.path.basename(path)
        size = os.path.getsize(path)
        fh = self._handle(0)
        fh.seek(max(0, size - 512))
        tail = fh.read(512)
        fh.seek(0)
        head = fh.read(512)
        footer, source, end = _vhd_footer(tail), "the footer at the end of the file", size - 512
        if footer is None and _vhd_footer(tail[1:]):
            footer, source, end = _vhd_footer(tail[1:]), "a 511-byte footer at the end", size - 511
        if footer is None:
            footer = _vhd_footer(head)
            if footer is None or footer["type"] == 2:
                raise EwfFormatError(f"{name} has no VHD footer whose checksum matches")
            source = ("the copy at the start of the file; the footer at the end does "
                      "not match its checksum")
        if footer["version"] >> 16 != 1:
            raise EwfFormatError(f"{name} is VHD format version "
                                 f"{footer['version'] >> 16}.{footer['version'] & 0xFFFF}; "
                                 f"only 1.0 is read")
        kind = _VHD_TYPES.get(footer["type"])
        if kind is None:
            raise EwfFormatError(f"{name} records VHD disk type {footer['type']}, which is "
                                 f"not a fixed, dynamic or differencing disk")
        disk = footer["current_size"]
        if disk % 512:
            raise EwfFormatError(f"{name} records a disk of {disk:,} bytes, not a whole "
                                 f"number of 512-byte sectors")
        stamp = datetime.datetime.fromtimestamp(_VHD_EPOCH + footer["timestamp"],
                                                datetime.timezone.utc)
        self.vhd = {
            "disk_type": kind, "footer": source,
            "creator": footer["creator"].decode("latin-1").rstrip("\0 "),
            "creator_version": f"{footer['creator_version'] >> 16}."
                               f"{footer['creator_version'] & 0xFFFF}",
            "creator_host": footer["host"].decode("latin-1").rstrip("\0 "),
            "created": stamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "original_size": footer["original_size"], "disk_size": disk,
            "geometry": footer["geometry"], "unique_id": _uuid_text(footer["unique_id"]),
            "saved_state": bool(footer["saved_state"]),
            "block_size": None, "blocks": None, "blocks_stored": None,
            "bitmap_bytes": 0, "data_after_disk": 0, "parent": None}
        self._vhd_unique_id = footer["unique_id"]
        self.compression_level = "none"
        if kind == "fixed":
            if end < disk:
                raise EwfIncompleteSetError(
                    f"{name} holds {end:,} bytes of disk data where its footer records a "
                    f"disk of {disk:,}; the file is cut short")
            self.vhd["data_after_disk"] = end - disk
            self.chunk_size = _VIRTUAL_CHUNK
            self._apple_finish(disk // 512, FORMAT_VHD)
            return

        offset = footer["data_offset"]
        fh.seek(offset)
        dyn = fh.read(1024)
        if len(dyn) < 1024 or dyn[:8] != b"cxsparse":
            raise EwfFormatError(f"{name} has no dynamic disk header at offset {offset:,}, "
                                 f"where its footer points")
        (_cookie, _next, table, version, entries, block, checksum, parent_id,
         parent_stamp) = _VHD_DYNAMIC.unpack_from(dyn)
        if _vhd_checksum(dyn, 36) != checksum:
            raise EwfFormatError(f"{name}'s dynamic disk header does not match its "
                                 f"checksum")
        if version >> 16 != 1:
            raise EwfFormatError(f"{name}'s dynamic disk header is version "
                                 f"{version >> 16}.{version & 0xFFFF}; only 1.0 is read")
        if block < 512 or block & (block - 1):
            raise EwfFormatError(f"{name} records a block size of {block:,} bytes, not a "
                                 f"power of two of at least 512")
        needed = -(-disk // block)
        if entries < needed:
            raise EwfFormatError(f"{name}'s block table has {entries:,} entries for a disk "
                                 f"of {needed:,} blocks")
        if table + 4 * needed > size:
            raise EwfIncompleteSetError(f"{name} ends inside its block table; the file is "
                                        f"cut short")
        fh.seek(table)
        bat = list(struct.unpack(f">{needed}I", _read_exactly(fh, 4 * needed)))
        bitmap = -(-(block // 512) // 8)
        bitmap = -(-bitmap // 512) * 512
        stored = []
        for i, entry in enumerate(bat):
            if entry == _VHD_UNUSED:
                continue
            start = entry * 512
            want = bitmap + min(block, disk - i * block)
            if start + want > end:
                raise EwfIncompleteSetError(f"{name} ends inside block {i:,}; the file is "
                                            f"cut short")
            stored.append((start, start + want, i))
        stored.sort()
        for (a0, a1, i), (b0, _b1, j) in zip(stored, stored[1:]):
            if b0 < a1:
                raise EwfFormatError(f"{name} stores blocks {i:,} and {j:,} in bytes that "
                                     f"overlap")
        self._vhd_bat = bat
        self.vhd.update(block_size=block, blocks=needed, blocks_stored=len(stored),
                        bitmap_bytes=bitmap)
        self.chunk_size = min(block, _VIRTUAL_CHUNK)
        if kind == "differencing":
            self._vhd_open_parent(name, dyn, parent_id, parent_stamp)
        self._apple_finish(disk // 512, FORMAT_VHD)

    def _vhd_open_parent(self, name, dyn, parent_id, parent_stamp):
        """Open the disk a differencing VHD was made from. It is looked for where the
        disk's parent locators say, relative first, then by its file name beside this
        one; it must be a VHD whose identifier is the one this disk records."""
        here = os.path.dirname(self.paths[0])
        parent_name = dyn[64:576].decode("utf-16-be", "replace").split("\0")[0]
        candidates, locators = [], []
        fh = self._handle(0)
        for n in range(8):
            code, _space, length, _reserved, offset = _VHD_LOCATOR.unpack_from(
                dyn, 576 + 24 * n)
            if code == b"\0\0\0\0" or not length or length > 65536:
                continue
            fh.seek(offset)
            data = fh.read(length)
            if code in (b"W2ru", b"W2ku"):
                text = data.decode("utf-16-le", "replace").split("\0")[0]
                locators.append((code.decode(), text))
                if code == b"W2ru":
                    candidates.append(os.path.join(here, *[part for part in
                                      re.split(r"[\\/]", text) if part not in ("", ".")]))
                else:
                    candidates.append(text)
                    candidates.append(os.path.join(here, re.split(r"[\\/]", text)[-1]))
            elif code == b"MacX":
                text = data.decode("utf-8", "replace").split("\0")[0]
                locators.append((code.decode(), text))
                local = urllib.parse.unquote(urllib.parse.urlparse(text).path)
                candidates.append(local)
                candidates.append(os.path.join(here, os.path.basename(local)))
        if parent_name:
            candidates.append(os.path.join(here, re.split(r"[\\/]", parent_name)[-1]))
        self.vhd["parent"] = {
            "unique_id": _uuid_text(parent_id), "name": parent_name, "locators": locators,
            "file": None,
            # The spec calls this the parent's modification time; the parent's own
            # footer records its creation time, so the two are not compared.
            # Windows 11 writes 0 here, which records nothing.
            "timestamp": datetime.datetime.fromtimestamp(
                _VHD_EPOCH + parent_stamp, datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S UTC") if parent_stamp else None}
        if len(_opening_parents) >= _VIRTUAL_MAX_PARENTS:
            raise EwfFormatError(f"{name} is more than {_VIRTUAL_MAX_PARENTS} differencing "
                                 f"disks deep")
        mine = os.path.realpath(self.paths[0])
        wrong = []
        seen = set()
        _opening_parents.append(mine)
        try:
            for path in candidates:
                real = os.path.realpath(path)
                if real in seen or not os.path.isfile(real):
                    continue
                seen.add(real)
                if real in _opening_parents:
                    raise EwfFormatError(f"{name}'s chain of parent disks loops back to "
                                         f"{os.path.basename(real)}")
                if virtual_disk_kind(real) != FORMAT_VHD:
                    wrong.append(f"{os.path.basename(real)} is not a VHD")
                    continue
                parent = EwfImage(real)
                if parent._vhd_unique_id != parent_id:
                    wrong.append(f"{os.path.basename(real)} is disk "
                                 f"{parent.vhd['unique_id']}")
                    parent.close()
                    continue
                self.parent = parent
                self.vhd["parent"]["file"] = os.path.basename(real)
                return
        finally:
            _opening_parents.pop()
        wanted = parent_name or (locators[0][1] if locators else "not recorded")
        if wrong:
            raise EwfFormatError(
                f"{name} is a differencing disk whose parent is disk "
                f"{_uuid_text(parent_id)} ({_shown(wanted)}); "
                f"{'; '.join(wrong)}, so its parent is not beside it")
        raise EwfIncompleteSetError(
            f"{name} is a differencing disk; its parent, {_shown(wanted)}, is not "
            f"beside it. Put the parent disk in the same folder.")

    def _chunk_data_vhd(self, n):
        start = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - start)
        fh = self._handle(0)
        if self.vhd["disk_type"] == "fixed":
            fh.seek(start)
            return _read_exactly(fh, want)
        block = self.vhd["block_size"]
        i, within = divmod(start, block)
        entry = self._vhd_bat[i]
        if entry == _VHD_UNUSED:
            return self._parent_read(start, want) if self.parent else bytes(want)
        fh.seek(entry * 512 + self.vhd["bitmap_bytes"] + within)
        data = _read_exactly(fh, want)
        if self.parent is None:
            return data
        bitmap = self._vhd_bitmap(i, entry)
        first = within // 512
        out = bytearray(data)
        count = want // 512
        s = 0
        while s < count:
            bit = (bitmap[(first + s) >> 3] >> (7 - ((first + s) & 7))) & 1
            e = s + 1
            while e < count and (bitmap[(first + e) >> 3] >> (7 - ((first + e) & 7))) & 1 == bit:
                e += 1
            if not bit:
                out[s * 512:e * 512] = self._parent_read(start + s * 512, (e - s) * 512)
            s = e
        return bytes(out)

    def _vhd_bitmap(self, i, entry):
        cached = self._vhd_bitmaps.get(i)
        if cached is None:
            fh = self._handle(0)
            fh.seek(entry * 512)
            cached = _read_exactly(fh, self.vhd["bitmap_bytes"])
            if len(self._vhd_bitmaps) >= 64:
                self._vhd_bitmaps.popitem(last=False)
            self._vhd_bitmaps[i] = cached
        return cached

    def _parent_read(self, offset, n):
        """``n`` bytes of the parent disk at ``offset``; past its end, zeros."""
        have = max(0, min(n, self.parent.media_size - offset))
        data = b""
        if have:
            self.parent.seek(offset)
            data = self.parent.read(have)
        return data + bytes(n - len(data))

    def _index_qcow(self):
        """Read a QCOW header (version 1, 2 or 3), its L1 table, its header extensions
        and snapshot table, and open its backing file and external data file."""
        path = self.paths[0]
        name = os.path.basename(path)
        size = os.path.getsize(path)
        fh = self._handle(0)
        fh.seek(0)
        head = fh.read(4096)
        version = struct.unpack_from(">I", head, 4)[0]
        extensions, features = {}, []
        snapshots = []
        if version == 1:
            (_m, _v, backing_at, backing_len, mtime, disk, cluster_bits, l2_bits, crypt,
             l1_at) = _QCOW1_HEADER.unpack_from(head)
            if not 9 <= cluster_bits <= 16 or not 6 <= l2_bits <= 13:
                raise EwfFormatError(f"{name} records {cluster_bits} cluster bits and "
                                     f"{l2_bits} L2 bits, which QEMU's qcow does not allow")
            l1_size = -(-disk // (1 << (cluster_bits + l2_bits)))
            entry_bytes = 8
            l2_entries = 1 << l2_bits
            incompatible = 0
        else:
            (_m, _v, backing_at, backing_len, cluster_bits, disk, crypt, l1_size, l1_at,
             _rc_at, _rc_clusters, nb_snapshots, snapshots_at) = _QCOW2_HEADER.unpack_from(head)
            mtime = None
            incompatible = compatible = 0
            header_length, compression = 72, 0
            if version == 3:
                incompatible, compatible, _auto, _order, header_length = struct.unpack_from(
                    ">QQQII", head, 72)
                if header_length > 104:
                    compression = head[104]
            if incompatible & ~_QCOW_KNOWN_INCOMPATIBLE:
                raise EwfFormatError(f"{name} sets incompatible feature bits "
                                     f"{incompatible & ~_QCOW_KNOWN_INCOMPATIBLE:#x}, which "
                                     f"this reader does not know")
            if not 9 <= cluster_bits <= 21:
                raise EwfFormatError(f"{name} records {cluster_bits} cluster bits")
            entry_bytes = 16 if incompatible & 16 else 8
            l2_entries = (1 << cluster_bits) // entry_bytes
            at = header_length if version == 3 else 72
            while at + 8 <= min(len(head), 1 << cluster_bits):
                kind, length = struct.unpack_from(">II", head, at)
                if kind == 0:
                    break
                extensions[kind] = head[at + 8:at + 8 + length]
                at += 8 + -(-length // 8) * 8
            for flag, label in ((1, "dirty"), (2, "marked corrupt"),
                                (4, "external data file"), (8, "zstd" if
                                compression == 1 else "compression type"),
                                (16, "extended L2 entries")):
                if incompatible & flag:
                    features.append(label)
            if compatible & 1:
                features.append("lazy refcounts")
            if nb_snapshots:
                fh.seek(snapshots_at)
                table = fh.read(min(nb_snapshots * 1024 + 65536, max(0, size - snapshots_at)))
                pos = 0
                for _ in range(nb_snapshots):
                    if pos + 40 > len(table):
                        break
                    (_l1, _l1n, id_len, name_len, sec, _nsec, _vm_ns, vm_state,
                     extra_len) = struct.unpack_from(">QIHHIIQII", table, pos)
                    q = pos + 40 + extra_len
                    snap_id = table[q:q + id_len].decode("utf-8", "replace")
                    snap_name = table[q + id_len:q + id_len + name_len].decode(
                        "utf-8", "replace")
                    snapshots.append({"id": snap_id, "name": snap_name,
                                      "taken": datetime.datetime.fromtimestamp(
                                          sec, datetime.timezone.utc).strftime(
                                          "%Y-%m-%d %H:%M:%S UTC"),
                                      "vm_state": bool(vm_state)})
                    pos = q + id_len + name_len
                    pos += -pos % 8
        if crypt:
            raise EwfFormatError(f"{name} is encrypted ({'AES' if crypt == 1 else 'LUKS' if crypt == 2 else crypt}), "
                                 f"which this reader does not decrypt")
        cluster = 1 << cluster_bits
        needed = -(-disk // (cluster * l2_entries))
        if l1_size < needed:
            raise EwfFormatError(f"{name}'s L1 table has {l1_size:,} entries for a disk "
                                 f"that needs {needed:,}")
        if l1_at + 8 * needed > size:
            raise EwfIncompleteSetError(f"{name} ends inside its L1 table; the file is cut "
                                        f"short")
        fh.seek(l1_at)
        l1 = list(struct.unpack(f">{needed}Q", _read_exactly(fh, 8 * needed)))
        compression_name = "deflate"                   # QEMU's default codec
        if version > 1 and incompatible & 8 and compression == 1:
            compression_name = "zstd"
        elif version > 1 and incompatible & 8:
            raise EwfFormatError(f"{name} records compression type {compression}; deflate "
                                 f"(0) and zstd (1) are read")
        self.qcow = {"version": version, "cluster_size": cluster, "disk_size": disk,
                     "features": features, "snapshots": snapshots,
                     "backing_file": None, "backing_format": None, "backing_opened": None,
                     "external_data_file": None, "compression": compression_name,
                     "modified": (datetime.datetime.fromtimestamp(
                         mtime, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                         if mtime else None)}
        self._qcow_l1 = l1
        self._qcow_l2 = OrderedDict()
        self._qcow_clusters = OrderedDict()
        self._qcow_l2_entries = l2_entries
        self._qcow_entry_bytes = entry_bytes
        self._qcow_data = 0
        self._qcow_zstd = None
        if compression_name == "zstd":
            self._qcow_zstd = _zstd_decompressor()
            if self._qcow_zstd is None:
                raise EwfFormatError(f"{name} compresses its clusters with zstd, which "
                                     f"needs Python 3.14 or the optional backports.zstd "
                                     f"package")
        here = os.path.dirname(path)
        if version > 1 and incompatible & 4:
            data_name = extensions.get(_QCOW_EXTERNAL_DATA, b"").decode("utf-8", "replace")
            self.qcow["external_data_file"] = data_name or None
            data_path = os.path.join(here, os.path.basename(data_name)) if data_name else ""
            if not data_name or not os.path.isfile(data_path):
                raise EwfIncompleteSetError(
                    f"{name} keeps its data in an external file"
                    f"{', ' + _shown(data_name) + ',' if data_name else ''} which is not "
                    f"beside it")
            self.paths.append(data_path)
            self._qcow_data = len(self.paths) - 1
        if backing_at and backing_len:
            if backing_len > 1023 or backing_at + backing_len > size:
                raise EwfFormatError(f"{name}'s backing file name does not fit its header")
            fh.seek(backing_at)
            backing = fh.read(backing_len).decode("utf-8", "replace")
            fmt = extensions.get(_QCOW_BACKING_FORMAT, b"").decode("utf-8", "replace")
            self.qcow["backing_file"] = backing
            self.qcow["backing_format"] = fmt or None
            self._qcow_open_backing(name, here, backing, fmt)
        self.compression_level = (f"{'zstd' if compression_name == 'zstd' else 'deflate'}"
                                  f" for any cluster stored compressed")
        self.chunk_size = _VIRTUAL_CHUNK
        self._apple_finish(-(-disk // 512), FORMAT_QCOW,
                           sizes=[os.path.getsize(p) for p in self.paths])
        self.media_size = self.size = disk              # need not be whole sectors
        self.chunk_count = self._indexed_chunks = self._needed_chunks()

    def _qcow_open_backing(self, name, here, backing, fmt):
        """Open a QCOW's backing file by its recorded name, relative to this file or
        (when absolute and present) where it names, then by file name beside it. QCOW
        records no identity for its backing file, so only the name ties them."""
        parts = [part for part in re.split(r"[\\/]", backing) if part not in ("", ".")]
        candidates = []
        if os.path.isabs(backing):
            candidates.append(backing)
        elif not re.match(r"^[A-Za-z]:", backing) and not re.match(r"^[a-z]+:", backing):
            candidates.append(os.path.join(here, *parts))
        if parts:
            candidates.append(os.path.join(here, parts[-1]))
        if len(_opening_parents) >= _VIRTUAL_MAX_PARENTS:
            raise EwfFormatError(f"{name} is more than {_VIRTUAL_MAX_PARENTS} backing files "
                                 f"deep")
        mine = os.path.realpath(self.paths[0])
        _opening_parents.append(mine)
        try:
            for path in candidates:
                real = os.path.realpath(path)
                if not os.path.isfile(real):
                    continue
                if real in _opening_parents:
                    raise EwfFormatError(f"{name}'s chain of backing files loops back to "
                                         f"{os.path.basename(real)}")
                if fmt == "raw" or (not fmt and virtual_disk_kind(real) is None
                                    and not is_image(real)):
                    self.parent = _RawParent(real)
                else:
                    self.parent = EwfImage(real)
                self.qcow["backing_opened"] = os.path.basename(real)
                return
        finally:
            _opening_parents.pop()
        raise EwfIncompleteSetError(f"{name} has a backing file, {_shown(backing)}, which "
                                    f"is not beside it. Put it in the same folder.")

    def _qcow_l2_table(self, index):
        table = self._qcow_l2.get(index)
        if table is None:
            entry = self._qcow_l1[index]
            offset = entry & _QCOW_OFFSET if self.qcow["version"] > 1 else entry
            if not offset:
                return None
            count = self._qcow_l2_entries * (self._qcow_entry_bytes // 8)
            fh = self._handle(0)
            fh.seek(offset)
            raw = fh.read(8 * count)
            if len(raw) < 8 * count:
                raise EwfIncompleteSetError(f"{os.path.basename(self.paths[0])} ends inside "
                                            f"an L2 table; the file is cut short")
            table = struct.unpack(f">{count}Q", raw)
            if len(self._qcow_l2) >= 64:
                self._qcow_l2.popitem(last=False)
            self._qcow_l2[index] = table
        return table

    def _qcow_compressed(self, entry, cluster_index):
        cached = self._qcow_clusters.get(cluster_index)
        if cached is not None:
            return cached
        cluster = self.qcow["cluster_size"]
        bits = cluster.bit_length() - 1
        if self.qcow["version"] == 1:
            offset = entry & ((1 << (63 - bits)) - 1)
            length = (entry >> (63 - bits)) & (cluster - 1)
        else:
            x = 62 - (bits - 8)
            offset = entry & ((1 << x) - 1)
            sectors = (entry >> x) & ((1 << (62 - x)) - 1)
            length = (sectors + 1) * 512 - (offset & 511)
        fh = self._handle(0)
        fh.seek(offset)
        blob = fh.read(length)
        try:
            if self._qcow_zstd is not None:
                data = self._qcow_zstd().decompress(blob)
            else:
                data = zlib.decompressobj(-15).decompress(blob, cluster)
        except Exception as exc:                            # zlib.error, zstd errors
            raise EwfFormatError(f"{os.path.basename(self.paths[0])}: cluster "
                                 f"{cluster_index:,} does not decompress ({exc})") from None
        data = data[:cluster] + bytes(max(0, cluster - len(data)))
        if len(self._qcow_clusters) >= 32:
            self._qcow_clusters.popitem(last=False)
        self._qcow_clusters[cluster_index] = data
        return data

    def _chunk_data_qcow(self, n):
        start = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - start)
        cluster = self.qcow["cluster_size"]
        version = self.qcow["version"]
        out = bytearray()
        at = start
        while at < start + want:
            index, within = divmod(at, cluster)
            take = min(cluster - within, start + want - at)
            l1_index, l2_index = divmod(index, self._qcow_l2_entries)
            table = self._qcow_l2_table(l1_index) if l1_index < len(self._qcow_l1) else None
            entry = bitmap = 0
            if table is not None:
                if self._qcow_entry_bytes == 16:
                    entry, bitmap = table[2 * l2_index], table[2 * l2_index + 1]
                else:
                    entry = table[l2_index]
            out += self._qcow_piece(entry, bitmap, index, within, take, at, version)
            at += take
        return bytes(out)

    def _qcow_piece(self, entry, bitmap, index, within, take, at, version):
        """``take`` bytes of cluster ``index`` from ``within``, by its L2 entry."""
        cluster = self.qcow["cluster_size"]
        if version == 1:
            if not entry:
                return self._qcow_absent(at, take)
            if entry & _QCOW1_COMPRESSED:
                return self._qcow_compressed(entry, index)[within:within + take]
            return self._qcow_stored(entry, within, take)
        if entry & _QCOW_COMPRESSED:
            return self._qcow_compressed(entry & ~(_QCOW_COPIED | _QCOW_COMPRESSED),
                                         index)[within:within + take]
        offset = entry & _QCOW_OFFSET
        allocated = bool(offset) or (bool(entry & _QCOW_COPIED) and self._qcow_data)
        if self._qcow_entry_bytes == 16:
            sub = cluster // 32
            out = bytearray()
            while take > 0:
                k, inside = divmod(within, sub)
                part = min(sub - inside, take)
                if bitmap >> k & 1:
                    out += self._qcow_stored(offset, within, part)
                elif bitmap >> (32 + k) & 1:
                    out += bytes(part)
                else:
                    out += self._qcow_absent(at, part)
                within += part
                at += part
                take -= part
            return bytes(out)
        if version == 3 and entry & 1:
            return bytes(take)
        if not allocated:
            return self._qcow_absent(at, take)
        return self._qcow_stored(offset, within, take)

    def _qcow_stored(self, offset, within, take):
        fh = self._handle(self._qcow_data)
        fh.seek(offset + within)
        data = fh.read(take)
        if len(data) < take:
            raise EwfIncompleteSetError(f"{os.path.basename(self.paths[self._qcow_data])} "
                                        f"ends inside a cluster; the file is cut short")
        return data

    def _qcow_absent(self, at, take):
        return self._parent_read(at, take) if self.parent is not None else bytes(take)

    def _vmdk_find_descriptor(self, path, name):
        """The descriptor file beside a VMDK extent opened on its own: the one text
        descriptor in the same folder whose extent lines name it."""
        here = os.path.dirname(path)
        base = os.path.basename(path)
        found = []
        for entry in sorted(os.listdir(here)):
            other = os.path.join(here, entry)
            if other == path or not os.path.isfile(other):
                continue
            if os.path.getsize(other) > _VMDK_MAX_DESCRIPTOR:
                continue
            with open(other, "rb") as fh:
                raw = fh.read(_VMDK_MAX_DESCRIPTOR)
            if not _is_vmdk_descriptor(raw):
                continue
            for line in _vmdk_descriptor_text(raw).splitlines():
                m = _VMDK_EXTENT.match(line)
                if m and m.group(4) and os.path.basename(
                        m.group(4).replace("\\", "/")) == base:
                    found.append(other)
                    break
        if len(found) == 1:
            return found[0]
        raise EwfIncompleteSetError(
            f"{name} is one extent of a VMDK and holds no descriptor of its own; "
            f"{'no descriptor file beside it lists it' if not found else 'several descriptor files beside it list it'}"
            f". Open the descriptor .vmdk instead.")

    def _index_vmdk(self):
        """Read a VMDK's descriptor, open each extent it lists, and for a delta link its
        parent."""
        path = self.paths[0]
        name = os.path.basename(path)
        with open(path, "rb") as fh:
            head = fh.read(_VMDK_SPARSE.size)
        if head[:4] == VMDK_COWD_MAGIC:
            path = self._vmdk_find_descriptor(path, name)
        elif head[:4] == VMDK_SPARSE_MAGIC:
            fields = _VMDK_SPARSE.unpack_from(head)
            embedded = ""
            if fields[5]:
                with open(path, "rb") as fh:
                    fh.seek(fields[5] * 512)
                    embedded = _vmdk_descriptor_text(fh.read(min(fields[6] * 512,
                                                                 _VMDK_MAX_DESCRIPTOR)))
            # An extent of a multi-extent disk carries no descriptor, or (as qemu-img
            # writes it) an empty one; its descriptor is a file beside it.
            if not any(_VMDK_EXTENT.match(line.strip()) for line in embedded.splitlines()):
                path = self._vmdk_find_descriptor(path, name)
        name = os.path.basename(path)
        here = os.path.dirname(path)
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            head = fh.read(_VMDK_SPARSE.size)
            if head[:4] == VMDK_SPARSE_MAGIC:
                fields = _VMDK_SPARSE.unpack_from(head)
                fh.seek(fields[5] * 512)
                raw = fh.read(min(fields[6] * 512, _VMDK_MAX_DESCRIPTOR))
                where = f"embedded in {name}"
            else:
                if size > _VMDK_MAX_DESCRIPTOR:
                    raise EwfFormatError(f"{name} is too large to be a VMDK descriptor")
                fh.seek(0)
                raw = fh.read()
                where = name
        text = _vmdk_descriptor_text(raw)
        header, ddb, extents = {}, {}, []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            m = _VMDK_EXTENT.match(stripped)
            if m:
                extents.append((m.group(1).upper(), int(m.group(2)), m.group(3).upper(),
                                m.group(4), int(m.group(5) or 0)))
                continue
            if "=" in stripped:
                key, value = stripped.split("=", 1)
                key, value = key.strip(), value.strip().strip('"')
                if key.lower().startswith("ddb."):
                    ddb[key[4:]] = value
                else:
                    header[key.lower()] = value
        if not extents:
            raise EwfFormatError(f"the VMDK descriptor {where} lists no extents")
        create = header.get("createtype", "")
        if create.lower() in ("fulldevice", "partitioneddevice", "vmfsraw", "vmfsrdm",
                              "vmfsrdmp", "vmfsrawdevicemap",
                              "vmfspassthroughrawdevicemap"):
            raise EwfFormatError(f"{name} is a {create} VMDK, whose extents are a physical "
                                 f"device rather than files, so there is nothing in it to "
                                 f"read")
        self.paths = [path]
        start = 0
        listed = []
        # A descriptor embedded in a sparse extent that lists one sparse extent is
        # describing the file it sits in, whatever name it recorded: VMware's OVF tool
        # writes "generated-stream.vmdk" there.
        embedded_self = (where.startswith("embedded") and len(extents) == 1
                         and extents[0][2] == "SPARSE")
        for access, sectors, kind, file_name, offset in extents:
            length = sectors * 512
            extent = {"start": start, "length": length, "type": kind, "file": file_name,
                      "offset": offset * 512, "index": None}
            if access == "NOACCESS":
                raise EwfFormatError(f"{name} lists an extent marked NOACCESS")
            if kind != "ZERO":
                if not file_name:
                    raise EwfFormatError(f"{name} lists a {kind} extent with no file")
                extent_path = path if embedded_self else os.path.join(
                    here, *[part for part in re.split(r"[\\/]", file_name)
                            if part not in ("", ".")])
                if not os.path.isfile(extent_path):
                    raise EwfIncompleteSetError(
                        f"{name} lists the extent {_shown(file_name)}, which is not beside "
                        f"it. Put every file of the disk in one folder.")
                if extent_path not in self.paths:
                    self.paths.append(extent_path)
                extent["index"] = self.paths.index(extent_path)
                extent_size = os.path.getsize(extent_path)
                if kind in ("FLAT", "VMFS", "VMFSTHIN"):
                    if extent["offset"] + length > extent_size:
                        raise EwfIncompleteSetError(
                            f"{_shown(file_name)} is {extent_size:,} bytes where the "
                            f"descriptor places {length:,} bytes of disk in it from "
                            f"offset {extent['offset']:,}; the file is cut short")
                elif kind == "SPARSE":
                    self._vmdk_open_sparse(extent, extent_path, sectors, extent_size)
                elif kind == "VMFSSPARSE":
                    self._vmdk_open_cowd(extent, extent_path, sectors, extent_size)
                else:
                    raise EwfFormatError(f"{name} lists a {kind} extent, which this reader "
                                         f"does not read")
            listed.append({"type": kind, "file": file_name, "sectors": sectors,
                           "access": access, "this_file": embedded_self})
            self._vmdk_extents.append(extent)
            start += length
        self.vmdk = {"create_type": create, "descriptor": where,
                     "cid": header.get("cid"), "parent_cid": header.get("parentcid"),
                     "parent_hint": header.get("parentfilenamehint"), "extents": listed,
                     "ddb": ddb, "parent": None,
                     "compressed": any(e.get("compressed") for e in self._vmdk_extents)}
        self.compression_level = "deflate" if self.vmdk["compressed"] else "none"
        parent_cid = (header.get("parentcid") or "ffffffff").lower()
        if parent_cid != "ffffffff":
            self._vmdk_open_parent(name, here, parent_cid, header.get("parentfilenamehint"))
        self.chunk_size = _VIRTUAL_CHUNK
        self._vmdk_grain_cache = OrderedDict()
        self._apple_finish(start // 512, FORMAT_VMDK, sizes=[os.path.getsize(p)
                                                             for p in self.paths])

    def _vmdk_open_sparse(self, extent, path, sectors, size):
        label = os.path.basename(path)
        with open(path, "rb") as fh:
            head = fh.read(_VMDK_SPARSE.size)
            if head[:4] != VMDK_SPARSE_MAGIC:
                raise EwfFormatError(f"{label} is listed as a SPARSE extent but is not a "
                                     f"hosted sparse extent")
            (_magic, version, flags, capacity, grain, _doff, _dsize, per_gt, _rgd, gd,
             _over, _unclean, _chars, compress) = _VMDK_SPARSE.unpack_from(head)
            if version not in (1, 2, 3):
                raise EwfFormatError(f"{label} is a version {version} sparse extent; "
                                     f"versions 1 to 3 are read")
            if gd == _VMDK_GD_AT_END:
                fh.seek(max(0, size - 1024))
                foot = fh.read(_VMDK_SPARSE.size)
                if foot[:4] != VMDK_SPARSE_MAGIC:
                    raise EwfFormatError(f"{label} keeps its grain directory at its end, "
                                         f"but has no footer there")
                (_m, _v, flags, capacity, grain, _do, _ds, per_gt, _r, gd, _o, _u, _c,
                 compress) = _VMDK_SPARSE.unpack_from(foot)
            if grain < 1 or grain & (grain - 1) or not per_gt or per_gt > 65536:
                raise EwfFormatError(f"{label} records a grain of {grain:,} sectors and "
                                     f"{per_gt:,} entries to a grain table")
            compressed = bool(flags & (1 << 16))
            if compressed and compress != 1:
                raise EwfFormatError(f"{label} records compression algorithm {compress}; "
                                     f"only deflate (1) is read")
            coverage = per_gt * grain * 512
            count = -(-capacity * 512 // coverage)
            if gd * 512 + 4 * count > size:
                raise EwfIncompleteSetError(f"{label} ends inside its grain directory; "
                                            f"the file is cut short")
            fh.seek(gd * 512)
            directory = list(struct.unpack(f"<{count}I", _read_exactly(fh, 4 * count)))
        if capacity < sectors:
            raise EwfFormatError(f"{label} holds {capacity:,} sectors where the descriptor "
                                 f"lists {sectors:,}")
        extent.update(grain=grain * 512, per_gt=per_gt, table_bytes=4, directory=directory,
                      compressed=compressed, zero_grains=bool(flags & 4),
                      tables=OrderedDict(), file_size=size)

    def _vmdk_open_cowd(self, extent, path, sectors, size):
        label = os.path.basename(path)
        with open(path, "rb") as fh:
            head = fh.read(_VMDK_COWD.size)
            if head[:4] != VMDK_COWD_MAGIC:
                raise EwfFormatError(f"{label} is listed as a VMFSSPARSE extent but is not "
                                     f"an ESXi sparse extent")
            (_magic, version, _flags, total, grain, gd, count,
             _free) = _VMDK_COWD.unpack_from(head)
            if version != 1:
                raise EwfFormatError(f"{label} is a version {version} ESXi sparse extent; "
                                     f"only version 1 is read")
            if grain < 1 or not count or gd * 512 + 4 * count > size:
                raise EwfFormatError(f"{label}'s grain directory does not fit the file")
            fh.seek(gd * 512)
            directory = list(struct.unpack(f"<{count}I", _read_exactly(fh, 4 * count)))
        if total < sectors:
            raise EwfFormatError(f"{label} holds {total:,} sectors where the descriptor "
                                 f"lists {sectors:,}")
        extent.update(grain=grain * 512, per_gt=4096, table_bytes=4, directory=directory,
                      compressed=False, zero_grains=False, tables=OrderedDict(),
                      file_size=size)

    def _vmdk_open_parent(self, name, here, parent_cid, hint):
        """Open the parent link of a VMDK delta by its parentFileNameHint (by file name
        beside this one when the hint names another machine's path); its descriptor's
        content id must be the parentCID this link records."""
        self.vmdk["parent"] = {"cid": parent_cid, "hint": hint, "file": None}
        if not hint:
            raise EwfFormatError(f"{name} is a delta link with no parentFileNameHint")
        candidates = []
        parts = [part for part in re.split(r"[\\/]", hint) if part not in ("", ".")]
        if not os.path.isabs(hint) and not re.match(r"^[A-Za-z]:", hint):
            candidates.append(os.path.join(here, *parts))
        elif os.path.isabs(hint):
            candidates.append(hint)
        candidates.append(os.path.join(here, parts[-1] if parts else hint))
        if len(_opening_parents) >= _VIRTUAL_MAX_PARENTS:
            raise EwfFormatError(f"{name} is more than {_VIRTUAL_MAX_PARENTS} delta links "
                                 f"deep")
        mine = os.path.realpath(self.paths[0])
        wrong, seen = [], set()
        _opening_parents.append(mine)
        try:
            for path in candidates:
                real = os.path.realpath(path)
                if real in seen or not os.path.isfile(real):
                    continue
                seen.add(real)
                if real in _opening_parents:
                    raise EwfFormatError(f"{name}'s chain of parent disks loops back to "
                                         f"{os.path.basename(real)}")
                if virtual_disk_kind(real) != FORMAT_VMDK:
                    wrong.append(f"{os.path.basename(real)} is not a VMDK")
                    continue
                parent = EwfImage(real)
                if (parent.vmdk["cid"] or "").lower() != parent_cid:
                    wrong.append(f"{os.path.basename(real)} has content id "
                                 f"{parent.vmdk['cid']}")
                    parent.close()
                    continue
                self.parent = parent
                self.vmdk["parent"]["file"] = os.path.basename(real)
                return
        finally:
            _opening_parents.pop()
        if wrong:
            raise EwfFormatError(f"{name} is a delta link whose parent has content id "
                                 f"{parent_cid} ({_shown(hint)}); {'; '.join(wrong)}, so "
                                 f"its parent is not beside it")
        raise EwfIncompleteSetError(f"{name} is a delta link; its parent, {_shown(hint)}, "
                                    f"is not beside it. Put the parent disk in the same "
                                    f"folder.")

    def _chunk_data_vmdk(self, n):
        start = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - start)
        out = bytearray()
        at = start
        for extent in self._vmdk_extents:
            if at >= start + want:
                break
            e0, e1 = extent["start"], extent["start"] + extent["length"]
            if e1 <= at:
                continue
            take = min(e1, start + want) - at
            out += self._vmdk_extent_read(extent, at - e0, take, at)
            at += take
        return bytes(out) + bytes(want - len(out))

    def _vmdk_extent_read(self, extent, rel, n, disk_offset):
        kind = extent["type"]
        if kind == "ZERO":
            return bytes(n)
        fh = self._handle(extent["index"])
        if kind in ("FLAT", "VMFS", "VMFSTHIN"):
            fh.seek(extent["offset"] + rel)
            return _read_exactly(fh, n)
        grain = extent["grain"]
        out = bytearray()
        while n > 0:
            g, within = divmod(rel, grain)
            take = min(n, grain - within)
            entry = self._vmdk_grain_entry(extent, g)
            if entry == 0:
                out += (self._parent_read(disk_offset, take) if self.parent is not None
                        else bytes(take))
            elif entry == 1 and extent["zero_grains"]:
                out += bytes(take)
            elif extent["compressed"]:
                out += self._vmdk_compressed_grain(extent, g, entry)[within:within + take]
            else:
                if entry * 512 + within + take > extent["file_size"]:
                    raise EwfIncompleteSetError(
                        f"{_shown(extent['file'])} ends inside grain {g:,}; the file is "
                        f"cut short")
                fh.seek(entry * 512 + within)
                out += _read_exactly(fh, take)
            rel += take
            disk_offset += take
            n -= take
        return bytes(out)

    def _vmdk_grain_entry(self, extent, g):
        per_gt = extent["per_gt"]
        t, k = divmod(g, per_gt)
        if t >= len(extent["directory"]):
            return 0
        table_at = extent["directory"][t]
        if not table_at:
            return 0
        table = extent["tables"].get(t)
        if table is None:
            if table_at * 512 + 4 * per_gt > extent["file_size"]:
                raise EwfIncompleteSetError(f"{_shown(extent['file'])} ends inside a grain "
                                            f"table; the file is cut short")
            fh = self._handle(extent["index"])
            fh.seek(table_at * 512)
            table = struct.unpack(f"<{per_gt}I", _read_exactly(fh, 4 * per_gt))
            if len(extent["tables"]) >= 256:
                extent["tables"].popitem(last=False)
            extent["tables"][t] = table
        return table[k]

    def _vmdk_compressed_grain(self, extent, g, entry):
        key = (id(extent), g)
        cached = self._vmdk_grain_cache.get(key)
        if cached is not None:
            return cached
        fh = self._handle(extent["index"])
        fh.seek(entry * 512)
        head = _read_exactly(fh, 12)
        lba, size = struct.unpack("<QI", head)
        if lba * 512 != g * extent["grain"]:
            raise EwfFormatError(f"{_shown(extent['file'])}: the grain marker at sector "
                                 f"{entry:,} records sector {lba:,}, not the start of grain "
                                 f"{g:,}")
        blob = _read_exactly(fh, size)
        try:
            data = zlib.decompress(blob)
        except zlib.error:
            try:
                data = zlib.decompressobj(-15).decompress(blob)
            except zlib.error as exc:
                raise EwfFormatError(f"{_shown(extent['file'])}: grain {g:,} does not "
                                     f"decompress ({exc})") from None
        if len(data) < extent["grain"]:
            data += bytes(extent["grain"] - len(data))
        if len(self._vmdk_grain_cache) >= 32:
            self._vmdk_grain_cache.popitem(last=False)
        self._vmdk_grain_cache[key] = data
        return data

    def _vhdx_read(self, offset, n):
        """``n`` bytes of a VHDX file at ``offset``, with the log's replayed updates laid
        over them in memory; past the end of the file, zeros (a replayed log can extend
        the file)."""
        fh = self._handle(0)
        fh.seek(offset)
        data = bytearray(fh.read(n))
        data.extend(bytes(n - len(data)))
        if self._vhdx_overlay:
            first = offset - offset % 4096
            for sector in range(first, offset + n, 4096):
                if sector in self._vhdx_overlay:
                    content = self._vhdx_overlay[sector] or bytes(4096)
                    a, b = max(sector, offset), min(sector + 4096, offset + n)
                    data[a - offset:b - offset] = content[a - sector:b - sector]
        return bytes(data)

    def _vhdx_replay(self, name, log_guid, log_offset, log_length, size):
        """Find the active log sequence (MS-VHDX 2.3.3) and lay its updates over the
        file in memory. Returns the number of log entries replayed."""
        fh = self._handle(0)
        if log_length % _MIB or log_offset % _MIB or log_offset + log_length > size:
            raise EwfFormatError(f"{name}'s log is recorded at offset {log_offset:,}, "
                                 f"{log_length:,} bytes, which the file cannot hold")
        fh.seek(log_offset)
        # The log is a ring, so an entry can run past its end and continue at its start;
        # two copies end to end let every entry be read as one run of bytes.
        log = _read_exactly(fh, log_length) * 2

        def entry(at):
            """The entry at ``at`` in the log, as (sequence, tail, length, flushed,
            last, updates), or None when it is not a valid entry."""
            if log[at:at + 4] != b"loge":
                return None
            (_sig, checksum, length, tail, seq, count, _res, guid, flushed,
             last) = struct.unpack_from("<4sIIIQII16sQQ", log, at)
            if (guid != log_guid or not seq or length % 4096 or not length
                    or length > log_length or tail % 4096 or tail >= log_length):
                return None
            if _crc32c_zeroed(log[at:at + length]) != checksum:
                return None
            desc_sectors = -(-(64 + 32 * count) // 4096) if count else 1
            data_at = at + 4096 * desc_sectors
            updates = []
            for k in range(count):
                d = at + 64 + 32 * k
                sig = log[d:d + 4]
                if sig == b"zero":
                    _z, _r, length_z, file_off, dseq = struct.unpack_from("<4sIQQQ", log, d)
                    if dseq != seq or length_z % 4096 or file_off % 4096:
                        return None
                    updates.append((file_off, length_z, None))
                elif sig == b"desc":
                    _d, trailing, leading, file_off, dseq = struct.unpack_from(
                        "<4s4s8sQQ", log, d)
                    if dseq != seq or file_off % 4096 or data_at + 4096 > at + length:
                        return None
                    sector = log[data_at:data_at + 4096]
                    high, low = struct.unpack_from("<I", sector, 4)[0], struct.unpack_from(
                        "<I", sector, 4092)[0]
                    if sector[:4] != b"data" or (high << 32 | low) != seq:
                        return None
                    updates.append((file_off, 4096, leading + sector[8:4092] + trailing))
                    data_at += 4096
                else:
                    return None
            return seq, tail, length, flushed, last, updates

        best, best_seq = None, 0
        tail = old = 0
        while True:
            sequence, head, seq = [], tail, 0
            while True:
                found = entry(head)
                if found is None or (sequence and found[0] != seq + 1):
                    break
                sequence.append((head, found))
                seq = found[0]
                head = (head + found[2]) % log_length
                if len(sequence) > log_length // 4096:
                    break
            valid = bool(sequence) and any(
                start == sequence[-1][1][1] for start, _found in sequence)
            if valid and seq > best_seq:
                best, best_seq = sequence, seq
            tail = (tail + 4096) % log_length if not valid else head
            if tail < old or tail == old:
                break
            old = tail
        if best is None:
            raise EwfFormatError(f"{name}'s log is not empty but holds no complete, valid "
                                 f"sequence of entries, so the file is corrupt")
        head_entry = best[-1][1]
        if size < head_entry[3]:
            raise EwfIncompleteSetError(f"{name} is {size:,} bytes where its log records "
                                        f"it was at least {head_entry[3]:,}; the file is "
                                        f"cut short")
        start = next(i for i, (at, _f) in enumerate(best) if at == head_entry[1])
        for _at, (_seq, _tail, _len, _flushed, _last, updates) in best[start:]:
            for file_off, length, content in updates:
                for k in range(0, length, 4096):
                    self._vhdx_overlay[file_off + k] = (
                        content[k:k + 4096] if content is not None else None)
        return len(best) - start

    def _index_vhdx(self):
        """Read a VHDX: its current header, the log replayed in memory when it holds
        entries, the region table, the metadata the disk is described by, and the BAT;
        open a differencing disk's parent."""
        path = self.paths[0]
        name = os.path.basename(path)
        size = os.path.getsize(path)
        fh = self._handle(0)
        fh.seek(0)
        ident = _read_exactly(fh, 520)
        creator = ident[8:520].decode("utf-16-le", "replace").split("\0")[0]
        headers = []
        for at in (64 << 10, 128 << 10):
            fh.seek(at)
            raw = fh.read(4096)
            if len(raw) < 4096 or raw[:4] != b"head":
                continue
            fields = _VHDX_HEADER.unpack_from(raw)
            if _crc32c_zeroed(raw) != fields[1]:
                continue
            headers.append(fields)
        if not headers:
            raise EwfFormatError(f"{name} has no VHDX header whose checksum matches")
        (_sig, _ck, sequence, _file_guid, data_guid, log_guid, log_version, version,
         log_length, log_offset) = max(headers, key=lambda h: h[2])
        if version != 1:
            raise EwfFormatError(f"{name} is VHDX version {version}; only version 1 is read")
        replayed = 0
        if log_guid != bytes(16):
            if log_version != 0:
                raise EwfFormatError(f"{name}'s log is version {log_version} and holds "
                                     f"entries; only version 0 is replayed")
            replayed = self._vhdx_replay(name, log_guid, log_offset, log_length, size)
        regions = None
        for at in (192 << 10, 256 << 10):
            table = self._vhdx_read(at, 65536)
            if table[:4] != b"regi" or _crc32c_zeroed(table) != struct.unpack_from(
                    "<I", table, 4)[0]:
                continue
            count = struct.unpack_from("<I", table, 8)[0]
            if count > 2047:
                continue
            regions = {}
            for k in range(count):
                guid, offset, length, required = struct.unpack_from("<16sQII", table,
                                                                    16 + 32 * k)
                if guid in (_VHDX_REGION_BAT, _VHDX_REGION_METADATA):
                    regions[guid] = (offset, length)
                elif required & 1:
                    raise EwfFormatError(f"{name} holds a region marked required, "
                                         f"{uuid.UUID(bytes_le=guid)}, which this reader "
                                         f"does not know")
            break
        if regions is None:
            raise EwfFormatError(f"{name} has no region table whose checksum matches")
        if len(regions) != 2:
            raise EwfFormatError(f"{name}'s region table lacks the "
                                 f"{'BAT' if _VHDX_REGION_BAT not in regions else 'metadata'}"
                                 f" region")
        meta_off, meta_len = regions[_VHDX_REGION_METADATA]
        meta = self._vhdx_read(meta_off, meta_len)
        if meta[:8] != b"metadata":
            raise EwfFormatError(f"{name} has no metadata table at offset {meta_off:,}, "
                                 f"where its region table points")
        count = struct.unpack_from("<H", meta, 10)[0]
        if count > 2047:
            raise EwfFormatError(f"{name}'s metadata table lists {count:,} entries")
        items = {}
        for k in range(count):
            guid, offset, length, flags = struct.unpack_from("<16sIII", meta, 32 + 32 * k)
            if guid in _VHDX_KNOWN_ITEMS and not flags & 1:
                if offset + length > meta_len:
                    raise EwfFormatError(f"{name}'s metadata item "
                                         f"{uuid.UUID(bytes_le=guid)} runs past the "
                                         f"metadata region")
                items[guid] = meta[offset:offset + length]
            elif flags & 4:
                raise EwfFormatError(f"{name} holds a metadata item marked required, "
                                     f"{uuid.UUID(bytes_le=guid)}, which this reader does "
                                     f"not know")
        for guid, label, width in ((_VHDX_FILE_PARAMETERS, "file parameters", 8),
                                   (_VHDX_DISK_SIZE, "virtual disk size", 8),
                                   (_VHDX_LOGICAL_SECTOR, "logical sector size", 4)):
            if len(items.get(guid, b"")) < width:
                raise EwfFormatError(f"{name}'s metadata lacks its {label}")
        block, flags = struct.unpack_from("<II", items[_VHDX_FILE_PARAMETERS])
        disk = struct.unpack_from("<Q", items[_VHDX_DISK_SIZE])[0]
        logical = struct.unpack_from("<I", items[_VHDX_LOGICAL_SECTOR])[0]
        physical = (struct.unpack_from("<I", items[_VHDX_PHYSICAL_SECTOR])[0]
                    if len(items.get(_VHDX_PHYSICAL_SECTOR, b"")) >= 4 else None)
        has_parent = bool(flags & 2)
        if block < _MIB or block > 256 * _MIB or block & (block - 1):
            raise EwfFormatError(f"{name} records a block size of {block:,} bytes, not a "
                                 f"power of two from 1 to 256 MiB")
        if logical not in (512, 4096):
            raise EwfFormatError(f"{name} records a logical sector size of {logical:,} "
                                 f"bytes; 512 and 4,096 are the sizes VHDX allows")
        if disk % logical:
            raise EwfFormatError(f"{name} records a disk of {disk:,} bytes, not a whole "
                                 f"number of its {logical:,}-byte sectors")
        ratio = (1 << 23) * logical // block
        payload = -(-disk // block)
        bitmaps = -(-payload // ratio)
        entries = bitmaps * (ratio + 1) if has_parent else payload + (payload - 1) // ratio
        bat_off, bat_len = regions[_VHDX_REGION_BAT]
        if bat_len < 8 * entries:
            raise EwfFormatError(f"{name}'s BAT holds {bat_len // 8:,} entries for a disk "
                                 f"that needs {entries:,}")
        raw_bat = self._vhdx_read(bat_off, 8 * entries)
        bat = list(struct.unpack(f"<{entries}Q", raw_bat))
        states = {}
        for i in range(payload):
            state = bat[i + i // ratio] & 7
            if state in (4, 5) or (state == _VHDX_PARTIALLY_PRESENT and not has_parent):
                raise EwfFormatError(f"{name} records block {i:,} in state {state}, which "
                                     f"is not valid for this disk")
            states[state] = states.get(state, 0) + 1
            if state in (_VHDX_FULLY_PRESENT, _VHDX_PARTIALLY_PRESENT):
                at = (bat[i + i // ratio] >> 20) * _MIB
                want = min(block, disk - i * block)
                if at < _MIB:
                    raise EwfFormatError(f"{name} places block {i:,} inside its header "
                                         f"section")
                if at + want > size:
                    raise EwfIncompleteSetError(f"{name} ends inside block {i:,}; the "
                                                f"file is cut short")
        self._vhdx_bat = bat
        disk_id = items.get(_VHDX_DISK_ID, b"")
        self.vhdx = {
            "disk_type": ("differencing" if has_parent else
                          "fixed" if flags & 1 else "dynamic"),
            "creator": creator, "block_size": block, "logical_sector_size": logical,
            "physical_sector_size": physical, "disk_size": disk,
            "disk_id": str(uuid.UUID(bytes_le=disk_id)) if len(disk_id) == 16 else None,
            "data_write_guid": str(uuid.UUID(bytes_le=data_guid)),
            "header_sequence": sequence, "log_entries_replayed": replayed,
            "chunk_ratio": ratio, "blocks": payload,
            "block_states": {_VHDX_STATE_NAMES[k]: v for k, v in sorted(states.items())},
            "parent": None}
        self._vhdx_data_guid = data_guid
        self._vhdx_bitmaps = OrderedDict()
        self.compression_level = "none"
        self.chunk_size = _VIRTUAL_CHUNK
        if has_parent:
            self._vhdx_open_parent(name, items.get(_VHDX_PARENT_LOCATOR, b""))
        self._apple_finish(disk // 512, FORMAT_VHDX)
        if logical != 512:
            self.sector_size = logical
            self.sector_count = disk // logical
            self.sectors_per_chunk = self.chunk_size // logical

    def _vhdx_open_parent(self, name, locator):
        """Open the disk a differencing VHDX was made from, by its relative path, then
        its volume and absolute paths (by file name beside this one when those name
        another machine's drive); the parent's DataWriteGuid must be one of the
        parent_linkage values the locator records."""
        if len(locator) < 20 or locator[:16] != _VHDX_LOCATOR_VHDX:
            raise EwfFormatError(f"{name} is a differencing disk whose parent locator is "
                                 f"not the VHDX locator type")
        pairs = {}
        count = struct.unpack_from("<H", locator, 18)[0]
        for k in range(count):
            ko, vo, kl, vl = struct.unpack_from("<IIHH", locator, 20 + 12 * k)
            key = locator[ko:ko + kl].decode("utf-16-le", "replace")
            pairs[key] = locator[vo:vo + vl].decode("utf-16-le", "replace")
        # An all-zero value (Windows writes parent_linkage2 so) names no parent.
        linkage = {pairs[k].strip("{}").lower() for k in ("parent_linkage",
                                                         "parent_linkage2") if k in pairs}
        linkage.discard(str(uuid.UUID(int=0)))
        here = os.path.dirname(self.paths[0])
        candidates = []
        if "relative_path" in pairs:
            candidates.append(os.path.join(here, *[part for part in re.split(
                r"[\\/]", pairs["relative_path"]) if part not in ("", ".")]))
        for key in ("volume_path", "absolute_win32_path"):
            if key in pairs:
                text = pairs[key]
                if os.name == "nt":
                    candidates.append(text)
                candidates.append(os.path.join(here, re.split(r"[\\/]", text)[-1]))
        self.vhdx["parent"] = {"linkage": sorted(linkage), "locator": dict(pairs),
                               "file": None}
        if len(_opening_parents) >= _VIRTUAL_MAX_PARENTS:
            raise EwfFormatError(f"{name} is more than {_VIRTUAL_MAX_PARENTS} differencing "
                                 f"disks deep")
        mine = os.path.realpath(self.paths[0])
        wrong, seen = [], set()
        _opening_parents.append(mine)
        try:
            for path in candidates:
                real = os.path.realpath(path)
                if real in seen or not os.path.isfile(real):
                    continue
                seen.add(real)
                if real in _opening_parents:
                    raise EwfFormatError(f"{name}'s chain of parent disks loops back to "
                                         f"{os.path.basename(real)}")
                if virtual_disk_kind(real) != FORMAT_VHDX:
                    wrong.append(f"{os.path.basename(real)} is not a VHDX")
                    continue
                parent = EwfImage(real)
                if str(uuid.UUID(bytes_le=parent._vhdx_data_guid)) not in linkage:
                    wrong.append(f"{os.path.basename(real)} has DataWriteGuid "
                                 f"{parent.vhdx['data_write_guid']}")
                    parent.close()
                    continue
                if parent.vhdx["logical_sector_size"] != self.vhdx["logical_sector_size"]:
                    parent.close()
                    raise EwfFormatError(f"{name} and its parent have different logical "
                                         f"sector sizes")
                self.parent = parent
                self.vhdx["parent"]["file"] = os.path.basename(real)
                return
        finally:
            _opening_parents.pop()
        wanted = pairs.get("relative_path") or pairs.get("absolute_win32_path") or \
            pairs.get("volume_path") or "not recorded"
        if wrong:
            raise EwfFormatError(f"{name} is a differencing disk whose parent has "
                                 f"DataWriteGuid {' or '.join(sorted(linkage))} "
                                 f"({_shown(wanted)}); {'; '.join(wrong)}, so its parent "
                                 f"is not beside it")
        raise EwfIncompleteSetError(f"{name} is a differencing disk; its parent, "
                                    f"{_shown(wanted)}, is not beside it. Put the parent "
                                    f"disk in the same folder.")

    def _chunk_data_vhdx(self, n):
        start = n * self.chunk_size
        want = min(self.chunk_size, self.media_size - start)
        v = self.vhdx
        block, ratio = v["block_size"], v["chunk_ratio"]
        i, within = divmod(start, block)
        entry = self._vhdx_bat[i + i // ratio]
        state = entry & 7
        if state == _VHDX_FULLY_PRESENT or state == _VHDX_PARTIALLY_PRESENT:
            fh = self._handle(0)
            fh.seek((entry >> 20) * _MIB + within)
            data = fh.read(want)
            data += bytes(want - len(data))
            if state == _VHDX_FULLY_PRESENT:
                return data
            return self._vhdx_merge(start, want, data)
        if self.parent is not None and state == _VHDX_NOT_PRESENT:
            return self._parent_read(start, want)
        return bytes(want)

    def _vhdx_merge(self, start, want, data):
        """A partially present block's bytes: sectors whose bit in the sector bitmap is
        set from this file, the rest from the parent. Bit 0 of byte 0 is the first
        sector (MS-VHDX 2.4)."""
        logical = self.vhdx["logical_sector_size"]
        ratio = self.vhdx["chunk_ratio"]
        per_chunk = 1 << 23
        out = bytearray(data)
        count = want // logical
        first = start // logical
        s = 0
        while s < count:
            sector = first + s
            chunk, bit = divmod(sector, per_chunk)
            bitmap = self._vhdx_bitmap(chunk, ratio)
            present = (bitmap[bit >> 3] >> (bit & 7)) & 1
            e = s + 1
            while e < count:
                c2, b2 = divmod(first + e, per_chunk)
                if c2 != chunk or ((bitmap[b2 >> 3] >> (b2 & 7)) & 1) != present:
                    break
                e += 1
            if not present:
                out[s * logical:e * logical] = self._parent_read(start + s * logical,
                                                                 (e - s) * logical)
            s = e
        return bytes(out)

    def _vhdx_bitmap(self, chunk, ratio):
        cached = self._vhdx_bitmaps.get(chunk)
        if cached is None:
            entry = self._vhdx_bat[chunk * (ratio + 1) + ratio]
            if entry & 7 != _VHDX_SB_PRESENT:
                raise EwfFormatError(f"{os.path.basename(self.paths[0])} holds a partly "
                                     f"present block whose sector bitmap is not stored")
            cached = self._vhdx_read((entry >> 20) * _MIB, _MIB)
            if len(self._vhdx_bitmaps) >= 8:
                self._vhdx_bitmaps.popitem(last=False)
            self._vhdx_bitmaps[chunk] = cached
        return cached

    def _index_sparseimage(self):
        """Read the header chain of a sparse image into a map of stored bands."""
        path = self.paths[0]
        name = os.path.basename(path)
        fh = self._handle(0)
        size = self._content_size(path)
        fh.seek(0)
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
            if self._band_key is not None and length % self._band_key.block:
                raise EwfIncompleteSetError(
                    f"{name}: band file {entry} ends inside an encrypted block of "
                    f"{self._band_key.block} bytes; the file is cut short")
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
            entry = self._bands[number][0]
            path = os.path.join(self.paths[0], "bands", entry)
            if self._band_key is None:
                fh = open(path, "rb")
            else:
                # each band is encrypted on its own, its block numbers from 0
                fh = _EncryptedFile(path, self._band_key, 0, os.path.getsize(path),
                                    f"band {entry} of {os.path.basename(self.paths[0])}")
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
        if self.format == FORMAT_AFM:
            return self._keep(n, self._chunk_data_afm(n), want)
        if self.format == FORMAT_UDIF:
            return self._keep(n, self._chunk_data_udif(n), want)
        if self.format == FORMAT_SPARSEIMAGE:
            return self._keep(n, self._chunk_data_sparse(n), want)
        if self.format == FORMAT_SPARSEBUNDLE:
            return self._keep(n, self._chunk_data_bundle(n), want)
        if self.format == FORMAT_UDRW:
            return self._keep(n, self._chunk_data_udrw(n), want)
        if self.format == FORMAT_AFF4:
            return self._keep(n, self._chunk_data_aff4(n), want)
        if self.format == FORMAT_RAW:
            return self._keep(n, self._chunk_data_raw(n), want)
        if self.format == FORMAT_AD1:
            return self._keep(n, self._chunk_data_ad1(n), want)
        if self.format == FORMAT_VHD:
            return self._keep(n, self._chunk_data_vhd(n), want)
        if self.format == FORMAT_VHDX:
            return self._keep(n, self._chunk_data_vhdx(n), want)
        if self.format == FORMAT_VMDK:
            return self._keep(n, self._chunk_data_vmdk(n), want)
        if self.format == FORMAT_QCOW:
            return self._keep(n, self._chunk_data_qcow(n), want)

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
        # The pieces are joined once at the end: growing one bytearray to the size of
        # a large read and copying it out held about 1 GB at peak for 16 MiB reads
        # on macOS, against under 50 MB this way.
        parts = []
        pos = self._pos
        while n > 0:
            index = pos // self.chunk_size
            within = pos % self.chunk_size
            chunk = self._chunk(index)
            take = min(n, len(chunk) - within)
            if take <= 0:
                break
            parts.append(chunk[within:within + take] if within or take < len(chunk)
                         else chunk)
            pos += take
            n -= take
        self._pos = pos
        return b"".join(parts)

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
        if self.parent is not None:
            self.parent.close()

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
        names = ["MD5", "SHA1"] + [n for n in ("SHA256", "SHA512", "BLAKE2B")
                                   if n in self.stored_hashes]
        hashers = {n: hashlib.new(n.lower()) for n in names}
        done = 0
        # An AFF4 image that recorded no hash of the disk is checked through what it
        # did record about its own streams; hashing a disk that is mostly unrecorded
        # space would take long and compare with nothing.
        if self.format == FORMAT_AFF4 and not self.stored_hashes:
            hashers = {}
        # An AD1's hash is FTK Imager's, taken over its structure and its entries'
        # content rather than over its data as stored; its entries are checked in the
        # same pass.
        ad1 = self._verify_ad1(block, progress) if self.format == FORMAT_AD1 else None
        if ad1:
            hashers = {}
        self.seek(0)
        while hashers:
            data = self.read(block)
            if not data:
                break
            for h in hashers.values():
                h.update(data)
            done += len(data)
            if progress:
                progress(done, self.media_size)
        computed = {n: h.hexdigest() for n, h in hashers.items()}
        if ad1:
            computed, done = ad1[0], ad1[1]
        match = None
        for name, value in self.stored_hashes.items():
            if name in computed:
                match = (computed[name] == value) if match in (None, True) else False
        checked, mismatched = 0, []
        sha1_checked, sha1_mismatched = 0, []
        if ad1:
            checked, mismatched = ad1[2]["md5"], ad1[3]["md5"]
            sha1_checked, sha1_mismatched = ad1[2]["sha1"], ad1[3]["sha1"]
        for entry in [] if ad1 else self.logical_entries:
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
        container = (self._verify_udif(block, None) if self.format == FORMAT_UDIF else
                     self._verify_aff4(progress) if self.format == FORMAT_AFF4 else [])
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
            "entry_sha1_checked": sha1_checked,
            "entry_sha1_mismatched": sha1_mismatched,
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
            "encryption": None if self.encryption is None else dict(self.encryption),
            "aff_header_lost": list(self.aff_header_lost),
            "aff4": None if self.aff4 is None else dict(self.aff4),
            "vhd": None if self.vhd is None else dict(self.vhd),
            "vhdx": None if self.vhdx is None else dict(self.vhdx),
            "vmdk": None if self.vmdk is None else dict(self.vmdk),
            "qcow": None if self.qcow is None else dict(self.qcow),
            "ad1": None if self.ad1 is None else {
                key: value for key, value in self.ad1.items()
                if key not in ("first_item", "footer")},
        }


def open_ewf(path, segments=None, password=None, private_key=None) -> EwfImage:
    """Open an acquisition ewfprobe reads: an EWF, EWF2 or L01 set from any path in
    it, an AFF file, an AFM from its .afm with its raw files beside it, an AFD
    directory from the directory or any file in it, an AFF4
    container (a striped one from any of its files), an Apple
    .dmg (a segmented one from its .dmg) or .sparseimage, or a sparse bundle from its
    folder, an AD1 set from any of its files, or an AD-encrypted E01, SMART or raw set
    from its first file (a raw or AD1 set from any of its files), or a VHD, VHDX,
    VMDK or QCOW virtual disk from its file (a VMDK from its descriptor or any of its
    extents). An encrypted Apple disk image or AD-encrypted set opens
    with ``password`` (a str, used as UTF-8, or bytes); without one it raises
    EwfPasswordRequiredError, and with one that does not open it
    EwfWrongPasswordError. An encrypted AFF opens with its passphrase as
    ``password``. An AFF, Apple disk image or AD-encrypted set sealed to a
    certificate opens with ``private_key`` (a path, or the bytes, of an unencrypted
    PEM or DER RSA key); without it the error's ``needs`` is "private key"."""
    return EwfImage(path, segments=segments, password=password, private_key=private_key)


open_image = open_ewf


# --------------------------------------------------------------------- CLI

def _size(n):
    v = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if v < 1024 or unit == "TiB":
            return f"{v:,.1f} {unit}" if unit != "B" else f"{int(v)} B"
        v /= 1024
    return f"{v} B"


def _cli_password(args):
    """The password the command line names, from a file or an environment variable,
    else None. Never an argument's value: that would show in the process list and in
    shell history."""
    if args.password_file:
        try:
            with open(args.password_file, "rb") as fh:
                line = fh.read().split(b"\n", 1)[0]
        except OSError as exc:
            raise EwfFormatError(f"the password file could not be read: "
                                 f"{exc.strerror or exc}") from None
        return line[:-1] if line.endswith(b"\r") else line
    if args.password_env:
        if args.password_env not in os.environ:
            raise EwfFormatError(f"the environment variable {args.password_env} is not set")
        return os.environ[args.password_env]
    return None


def _open_cli(args):
    """open_ewf for a command: an encrypted image opens with the password given by
    --password-file or --password-env, or, at a terminal, one asked for (three
    tries)."""
    password = _cli_password(args)
    asked = 0
    while True:
        try:
            return open_ewf(args.image, password=password, private_key=args.private_key)
        except EwfPasswordError as exc:
            if getattr(exc, "needs", "password") == "private key":
                if args.private_key:
                    raise
                raise EwfPasswordRequiredError(f"{exc}; give that key with --private-key",
                                               needs="private key") from None
            given = args.password_file or args.password_env
            if given or not sys.stdin.isatty() or asked == 3:
                if isinstance(exc, EwfPasswordRequiredError) and not given:
                    raise EwfPasswordRequiredError(
                        f"{exc}; give it with --password-file or --password-env, or run "
                        f"ewfprobe at a terminal to be asked for it") from None
                raise
            if isinstance(exc, EwfWrongPasswordError):
                print("ewfprobe: that password does not open the image", file=sys.stderr)
            asked += 1
            password = getpass.getpass(f"password for {os.path.basename(args.image)}: ")


def _cmd_info(args):
    with _open_cli(args) as img:
        d = img.info()
        print(f"image           {os.path.basename(args.image)}")
        print(f"segments        {d['segment_count']} ({d['segments'][0]}"
              f"{' .. ' + d['segments'][-1] if d['segment_count'] > 1 else ''})")
        print(f"format          {d['format']}")
        print(f"media type      {d['media_type'] or 'not recorded'}")
        if d["format"] == FORMAT_AD1:
            a = d["ad1"]
            print(f"data source     {_shown(a['data_source'])}")
            print(f"AD1 version     {a['version']}")
            print(f"logical data    {d['media_size']:,} bytes ({_size(d['media_size'])}), "
                  f"the files' data with their margins left out")
            print(f"segment size    {a['segment_size']:,} bytes as recorded, the size of "
                  f"every file of the set but the last")
            print(f"chunk size      {a['chunk_size']:,} bytes")
            print(f"entries         {d['entry_count']:,}, {d['entry_md5_count']:,} with a "
                  f"stored MD5")
            if a["log"]:
                print(f"log             {_shown(a['log'])}, FTK Imager's, which holds the "
                      f"stored hashes below")
        elif d["format"] == FORMAT_L01:
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
        elif d["format"] == FORMAT_AD1:
            pass                                # no sectors: its entries are the content
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
            elif d["format"] == FORMAT_VMDK:
                v = d["vmdk"]
                print(f"create type     {_shown(v['create_type']) or 'not recorded'}")
                print(f"descriptor      {_shown(v['descriptor'])}")
                for ext in v["extents"]:
                    where = (f" in this file, recorded as {_shown(ext['file'])}"
                             if ext.get("this_file") else
                             f" in {_shown(ext['file'])}" if ext["file"] else "")
                    print(f"extent          {ext['access']} {ext['type']} "
                          f"{ext['sectors'] * 512:,} bytes{where}")
                print(f"content id      {v['cid'] or 'not recorded'}")
                if v["parent"]:
                    par = v["parent"]
                    print(f"parent          {_shown(par['file']) if par['file'] else 'not opened'}"
                          f", content id {par['cid']}"
                          f"{', named ' + _shown(par['hint']) if par['hint'] else ''}")
                for key, value in v["ddb"].items():
                    print(f"ddb.{_shown(key):<22}{_shown(value)}")
            elif d["format"] == FORMAT_QCOW:
                q = d["qcow"]
                print(f"qcow version    {q['version']}")
                print(f"cluster size    {q['cluster_size']:,} bytes")
                if q["features"]:
                    print(f"features        {', '.join(q['features'])}")
                if q["modified"]:
                    print(f"modified        {q['modified']}")
                if q["backing_file"]:
                    print(f"backing file    {_shown(q['backing_file'])}"
                          f"{' (' + _shown(q['backing_format']) + ')' if q['backing_format'] else ''}"
                          f", opened as {_shown(q['backing_opened'])}; qcow records no "
                          f"identity for it, so only its name ties them")
                if q["external_data_file"]:
                    print(f"external data   {_shown(q['external_data_file'])}")
                for snap in q["snapshots"]:
                    print(f"snapshot        {_shown(snap['name'])} (id {_shown(snap['id'])}), "
                          f"taken {snap['taken']}{', with VM state' if snap['vm_state'] else ''}"
                          f"; not read, the active disk is")
            elif d["format"] == FORMAT_VHDX:
                v = d["vhdx"]
                print(f"disk type       {v['disk_type']}")
                print(f"block size      {v['block_size']:,} bytes")
                states = ", ".join(f"{count:,} {state}" for state, count in
                                   v["block_states"].items())
                print(f"blocks          {v['blocks']:,}: {states}")
                if v["physical_sector_size"]:
                    print(f"physical sector {v['physical_sector_size']:,} bytes")
                print(f"creator         {_shown(v['creator']) or 'not recorded'}")
                print(f"disk id         {v['disk_id'] or 'not recorded'}")
                print(f"data write id   {v['data_write_guid']}")
                if v["log_entries_replayed"]:
                    print(f"log             {v['log_entries_replayed']:,} entries replayed "
                          f"in memory; the file itself is not changed")
                else:
                    print("log             empty")
                if v["parent"]:
                    par = v["parent"]
                    print(f"parent disk     {_shown(par['file']) if par['file'] else 'not opened'}"
                          f", data write id {' or '.join(par['linkage'])}")
                    for key, value in par["locator"].items():
                        if key.startswith("parent_linkage"):
                            continue
                        print(f"parent locator  {_shown(key)} {_shown(value)}")
            elif d["format"] == FORMAT_VHD:
                v = d["vhd"]
                print(f"disk type       {v['disk_type']}")
                if v["block_size"]:
                    print(f"block size      {v['block_size']:,} bytes")
                    print(f"blocks stored   {v['blocks_stored']:,} of {v['blocks']:,}")
                c, h, s_ = v["geometry"]
                print(f"geometry        {c:,} cylinders, {h} heads, {s_} sectors per "
                      f"track ({c * h * s_ * 512:,} bytes)")
                print(f"original size   {v['original_size']:,} bytes")
                print(f"created         {v['created']}")
                print(f"creator         {_shown(v['creator'])} {v['creator_version']} on "
                      f"{_shown(v['creator_host'])}")
                print(f"disk id         {v['unique_id']}")
                if v["saved_state"]:
                    print("saved state     set: the virtual machine was saved while "
                          "running")
                if v["data_after_disk"]:
                    print(f"                {v['data_after_disk']:,} bytes between the "
                          f"disk's data and the footer are not part of the disk")
                print(f"footer          {v['footer']}")
                if v["parent"]:
                    par = v["parent"]
                    print(f"parent disk     {par['unique_id']}, "
                          f"{_shown(par['file']) if par['file'] else 'not opened'}")
                    if par["name"]:
                        print(f"parent name     {_shown(par['name'])}")
                    for code, text in par["locators"]:
                        print(f"parent locator  {code} {_shown(text)}")
                    if par["timestamp"]:
                        print(f"parent time     {par['timestamp']}, the parent's "
                              f"modification time as this disk records it")
            elif d["format"] in (FORMAT_UDRW, FORMAT_RAW):
                pass                            # the disk itself: no chunks or bands
            elif d["format"] == FORMAT_AFF4:
                a = d["aff4"]
                print(f"AFF4 version    {a['version'] or 'not recorded (pre-standard)'}"
                      f"{', written by ' + a['tool'] if a['tool'] else ''}")
                if a["image"]:
                    print(f"AFF4 image      {a['image']}"
                          f"{' (' + ', '.join(a['image_types']) + ')' if a['image_types'] else ''}")
                if a["images"] > 1:
                    print(f"                the container describes {a['images']} images; "
                          f"this is the first")
                for st in a["streams"]:
                    print(f"image stream    {st['urn']} in {_shown(st['file'])}")
                    print(f"                {st['size']:,} bytes, {st['compression']}, "
                          f"{st['chunk_size']:,}-byte chunks, {st['chunks_in_segment']:,} "
                          f"to a segment")
                print("where the bytes come from")
                for name, count in a["coverage"]:
                    print(f"  {count:>22,}  {_shown(name)}")
                for key, value in a["vendor_properties"]:
                    print(f"{_shown(key):<26}{_shown(value)}")
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
        if d["encryption"] and "opened_with" in d["encryption"]:
            e = d["encryption"]                 # an encrypted AFF
            print(f"encryption      {e['cipher']}, {e['container']}; its key opened "
                  f"with the {e['opened_with']}")
        elif d["encryption"]:
            e = d["encryption"]
            print(f"encryption      {e['cipher']}, {e['container']}; key wrapped with "
                  f"{e['key_wrap']}, {e['kdf']}, {e['kdf_rounds']:,} rounds")
        if d.get("aff_header_lost"):
            print(f"AFF header      overwritten by a segment in "
                  f"{', '.join(d['aff_header_lost'])}, as AFFLIB 3.7.22's affcrypto -e "
                  f"leaves a file it encrypts in place; read from the segments, which "
                  f"AFFLIB cannot do")
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
    with _open_cli(args) as img:
        result = img.verify(progress=None if args.quiet else _progress)
        if not args.quiet:
            sys.stderr.write("\r" + " " * 48 + "\r")
        if img.format == FORMAT_AD1:
            where = (f"stored: {_shown(img.ad1['log'])}" if img.ad1["log"] else
                     "no log beside it holds a stored one")
            print(f"FTK Imager's image hash, over the AD1's structure and its entries' "
                  f"content ({where})")
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
            algo = c["algorithm"] if len(c["algorithm"]) < 6 else c["algorithm"] + " "
            print(f"{algo:<6}{c['computed']}   {verdict}  ({_shown(c['what'])})")
        if failed:
            return 1
        any_bad = False
        for label, key in (("entry MD5s", "md5"), ("entry SHA-1s", "sha1")):
            if not result[f"entry_{key}_checked"]:
                continue
            bad = result[f"entry_{key}_mismatched"]
            count = result[f"entry_{key}_checked"]
            print(f"{label:<16}{count:,} checked, {len(bad):,} DO NOT MATCH" if bad
                  else f"{label:<16}{count:,} checked, all match")
            for path in bad:
                print(f"  mismatch      {_shown(path)}")
            any_bad = any_bad or bool(bad)
        if any_bad:
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
    with _open_cli(args) as img:
        if img.format not in (FORMAT_L01, FORMAT_AD1):
            raise EwfFormatError(f"{os.path.basename(args.image)} is a disk image, not "
                                 f"logical evidence; it holds no entry list")
        # The listing is data, so it is UTF-8 wherever it goes; on Windows a pipe or
        # file would otherwise get the ANSI code page, which cannot hold every name.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        if img.format == FORMAT_AD1:
            # An AD1 entry also carries its item type and its type record, as stored,
            # so a deleted entry or an alternate data stream can be told apart.
            print("kind\tsize\tmd5\titem_type\ttype_code\tpath")
            for entry in img.logical_entries:
                kind = "folder" if entry.is_folder else "file"
                print(f"{kind}\t{entry.size}\t{entry.md5 or '-'}\t{entry.item_type}\t"
                      f"{_shown(entry.type_code) if entry.type_code else '-'}\t"
                      f"{_shown(entry.path)}")
            return 0
        print("kind\tsize\tmd5\tpath")
        for entry in img.logical_entries:
            kind = "folder" if entry.is_folder else "file"
            print(f"{kind}\t{entry.size}\t{entry.md5 or '-'}\t{_shown(entry.path)}")
    return 0


def _cmd_export(args):
    if args.entry is not None:
        return _export_entry(args)
    with _open_cli(args) as img:
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
    with _open_cli(args) as img:
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
        description="Read an EnCase/EWF (.E01, .Ex01), SMART (.s01), AFF (.aff, "
                    ".afd) or AFF4 (.aff4) forensic image, an Apple disk image (.dmg, .sparseimage, "
                    ".sparsebundle), a virtual machine disk (.vhd, .vhdx, .vmdk, .qcow2), "
                    "an E01, SMART or raw set FTK Imager encrypted "
                    "with AD encryption, or logical evidence: EnCase's (.L01) or "
                    "FTK Imager's (.ad1). Read only.")
    ap.add_argument("--version", action="version", version=f"ewfprobe {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("info", help="print the acquisition's geometry and metadata")
    s.add_argument("image")
    s.set_defaults(func=_cmd_info)

    s = sub.add_parser("verify", help="recompute the media hash and compare it "
                                      "with the one the acquisition stored (for an "
                                      "AD1, the one in FTK Imager's log beside it)")
    s.add_argument("image")
    s.add_argument("-q", "--quiet", action="store_true", help="no progress output")
    s.set_defaults(func=_cmd_verify)

    s = sub.add_parser("files", help="list the entries of an L01 or AD1, tab separated")
    s.add_argument("image")
    s.set_defaults(func=_cmd_files)

    s = sub.add_parser("export", help="write the acquired disk out as a raw image, or "
                                      "one L01 or AD1 entry's content with --entry")
    s.add_argument("image")
    s.add_argument("--entry", default=None,
                   help="the path of an L01 or AD1 entry, as the files command "
                        "lists it")
    s.add_argument("-o", "--output", default="-", help="output file, or - for stdout")
    s.add_argument("--offset", type=int, default=0, help="start at this byte offset")
    s.add_argument("--length", type=int, default=None, help="write this many bytes")
    s.add_argument("-q", "--quiet", action="store_true", help="no progress output")
    s.set_defaults(func=_cmd_export)

    for s in sub.choices.values():
        s.add_argument("--password-file", metavar="FILE", default=None,
                       help="for an encrypted Apple disk image, AD-encrypted set or "
                            "encrypted AFF: read its password from the first line of FILE")
        s.add_argument("--password-env", metavar="NAME", default=None,
                       help="for an encrypted Apple disk image, AD-encrypted set or "
                            "encrypted AFF: take its password from the environment "
                            "variable NAME. "
                            "Without either, ewfprobe asks for it at a terminal")
        s.add_argument("--private-key", metavar="FILE", default=None,
                       help="for an encrypted AFF, Apple disk image or AD-encrypted "
                            "set sealed to a certificate: the certificate's RSA "
                            "private key, "
                            "unencrypted, as PEM or DER")
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
