"""Pin the raw image seeker (scripts/raw_image.py) against independent readings.

FileSeekerRaw reads a disk image or an acquisition in place through the
vendored qnxprobe and stages only the files an artifact's pattern selects. The
fixtures under admin/test/data/raw_images/ each come with a list of their files
and SHA-256 written by a different reader (see the README there), so a staged
copy is checked against what an independent reader saw, not against the reader
under test.

The E01, AFF, AFD, Apple disk image and split-segment paths are exercised by
wrapping the same NTFS fixture at test time: small EWF, AFF, UDIF and sparse image
writers live in this file (copied from ewfprobe's own test suite, MIT), and a split
set is the raw image cut into numbered pieces. FTK Imager's AD encryption is written
here too, around a raw set and an E01 set, with the cipher library's CTR mode.
The expected values are the fixture's, written out, never read back from the
seeker.
"""
import contextlib
import gzip
import hashlib
import os
import pathlib
import plistlib
import re
import shutil
import struct
import sys
import tempfile
import time
import unittest
import zlib
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position
from scripts.raw_image import (  # pylint: disable=wrong-import-position
    RAW_IMAGE_FILESYSTEMS, RAW_IMAGE_SUFFIXES, FileSeekerRaw, names_a_stream,
    names_an_image_folder, names_deleted, names_free_space, split_image_sibling)
from scripts.vendor import ewfprobe, qnxprobe  # pylint: disable=wrong-import-position

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'


def _hash_list(path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            continue
        digest, _, rel = line.partition('  ')
        if rel:
            out[rel.strip()] = digest.strip()
    return out


def _sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# ---- a minimal EWF writer, from ewfprobe's test suite ------------------------

def _section(out, name, payload, last=False):
    start = out.tell()
    size = ewfprobe.SECTION_SIZE + len(payload)
    nxt = start if last else start + size
    head = struct.pack("<16sQQ40s", name.encode("ascii").ljust(16, b"\x00"), nxt, size,
                       b"\x00" * 40)
    out.write(head + struct.pack("<I", zlib.adler32(head) & 0xFFFFFFFF) + payload)


def _volume(chunk_count, sectors_per_chunk, sector_size, sector_count):
    data = bytearray(1052)
    data[0] = 0x01
    struct.pack_into("<III", data, 4, chunk_count, sectors_per_chunk, sector_size)
    struct.pack_into("<Q", data, 16, sector_count)
    data[52] = 0x01
    return bytes(data)


def _pack_chunks(chunks, compress, cut=()):
    blob = bytearray()
    entries = []
    for number, chunk in enumerate(chunks):
        rel = len(blob)
        if number in cut:
            # stored compressed whatever it gains, and only the first half of the
            # stream kept, so the chunk's data runs out before its end marker
            packed = zlib.compress(chunk, 6)
            entries.append(rel | ewfprobe._COMPRESSED_BIT)  # pylint: disable=protected-access
            blob += packed[:len(packed) // 2]
            continue
        if compress:
            packed = zlib.compress(chunk, 6)
            if len(packed) < len(chunk):
                entries.append(rel | ewfprobe._COMPRESSED_BIT)  # pylint: disable=protected-access
                blob += packed
                continue
        entries.append(rel)
        blob += chunk + struct.pack("<I", zlib.adler32(chunk) & 0xFFFFFFFF)
    return bytes(blob), entries


def _table_payload(entries, base):
    head = struct.pack("<IIQI", len(entries), 0, base, 0)
    payload = head + struct.pack("<I", zlib.adler32(head) & 0xFFFFFFFF)
    body = b"".join(struct.pack("<I", e) for e in entries)
    return payload + body + struct.pack("<I", zlib.adler32(body) & 0xFFFFFFFF)


def write_ewf(folder, stem, data, chunk_size=32768, sector_size=512, chunks_per_segment=None,
              cut=()):
    """Write data as an EWF-E01 set and return the segment paths in order. Each chunk
    numbered in ``cut`` is stored as half of its compressed stream."""
    data = data + b"\x00" * (-len(data) % sector_size)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] or [b""]
    per_segment = chunks_per_segment or len(chunks)
    groups = [chunks[i:i + per_segment] for i in range(0, len(chunks), per_segment)]
    paths = []
    for index, group in enumerate(groups):
        path = os.path.join(folder, f"{stem}.E{index + 1:02d}")
        paths.append(path)
        with open(path, "wb") as out:
            out.write(struct.pack("<8sBHH", ewfprobe.SIGNATURE, 1, index + 1, 0))
            if index == 0:
                _section(out, "header", zlib.compress(b"1\nmain\nc\n\n"))
                _section(out, "volume", _volume(len(chunks), chunk_size // sector_size,
                                                sector_size, len(data) // sector_size))
            first = index * per_segment
            blob, entries = _pack_chunks(group, True, {n - first for n in cut})
            base = out.tell() + ewfprobe.SECTION_SIZE
            _section(out, "sectors", blob)
            _section(out, "table", _table_payload(entries, base))
            if index == len(groups) - 1:
                _section(out, "hash", hashlib.md5(data).digest() + b"\x00" * 16)
                _section(out, "done", b"", last=True)
            else:
                _section(out, "next", b"", last=True)
    return paths


# ---- a minimal AFF writer, from ewfprobe's test suite -------------------------

def _aff_segment(out, name, data=b"", arg=0):
    raw = name.encode("utf-8")
    out.write(struct.pack(">4sIII", b"AFF\x00", len(raw), len(data), arg) + raw + data)
    out.write(struct.pack(">4sI", b"ATT\x00", 16 + len(raw) + len(data) + 8))


def write_aff(path, data, pages, page_size, image_size=None):
    """Write the listed pages of data as an AFF file from AFFLIB's documented
    layout: deflated pages, the sector and page size, and the image size when
    given (AFFLIB writes it into one file of an AFD)."""
    with open(path, "wb") as out:
        out.write(b"AFF10\r\n\x00")
        _aff_segment(out, "sectorsize", b"", 512)
        _aff_segment(out, "pagesize", b"", page_size)
        for n in pages:
            page = data[n * page_size:(n + 1) * page_size]
            _aff_segment(out, f"page{n}", zlib.compress(page, 6), 0x01)
        if image_size is not None:
            _aff_segment(out, "imagesize",
                         struct.pack(">II", image_size & 0xFFFFFFFF, image_size >> 32), 2)
    return path


# ---- minimal Apple disk image writers, from ewfprobe's test suite -------------

def _udif_checksum(value):
    return struct.pack(">II", 2, 32) + struct.pack(">I", value) + bytes(124)


def write_udif(path, data, chunk_sectors=2048):
    """Write data as a UDIF (.dmg) image of zlib chunks, the form hdiutil's UDZO
    uses, with its block table in the property list and the koly trailer."""
    sectors = len(data) // 512
    fork, entries, at = bytearray(), [], 0
    while at < sectors:
        count = min(chunk_sectors, sectors - at)
        blob = zlib.compress(data[at * 512:(at + count) * 512])
        entries.append((0x80000005, 0, at, count, len(fork), len(blob)))
        fork += blob
        at += count
    entries.append((0xFFFFFFFF, 0, at, 0, len(fork), 0))
    crc = zlib.crc32(data[:sectors * 512])
    mish = struct.pack(">4sIQQQII24x", b"mish", 1, 0, sectors, 0, 0, len(entries))
    mish += _udif_checksum(crc) + struct.pack(">I", len(entries))
    mish += b"".join(struct.pack(">IIQQQQ", *e) for e in entries)
    body = plistlib.dumps({"resource-fork": {"blkx": [{"Name": "whole disk", "Data": mish}]}})
    with open(path, "wb") as out:
        out.write(fork)
        xml_offset = out.tell()
        out.write(body)
        trailer = struct.pack(">4sIIIQQQQQII", b"koly", 4, 512, 1, 0, 0, len(fork), 0, 0, 1, 1)
        trailer += bytes(16) + _udif_checksum(zlib.crc32(fork))
        trailer += struct.pack(">QQ", xml_offset, len(body)) + bytes(120)
        trailer += _udif_checksum(zlib.crc32(struct.pack(">I", crc)))
        trailer += struct.pack(">IQ", 1, sectors) + bytes(12)
        out.write(trailer)
    return path


def write_sparseimage(path, data, band_sectors=2048):
    """Write data as a sparse image (.sparseimage): a 4096-byte header listing the
    stored 1 MiB bands, then the bands, zero bands left out, as hdiutil writes one
    that fits a single header."""
    band = band_sectors * 512
    sectors = len(data) // 512
    stored = [b for b in range(-(-sectors // band_sectors))
              if any(data[b * band:(b + 1) * band])]
    assert len(stored) <= 1008
    head = bytearray(4096)
    struct.pack_into(">4sIIII", head, 0, b"sprs", 3, band_sectors, 1, sectors)
    struct.pack_into(">QQ", head, 20, 0, sectors)
    struct.pack_into(f">{len(stored)}I", head, 64, *[b + 1 for b in stored])
    with open(path, "wb") as out:
        out.write(head)
        for b in stored:
            out.write(data[b * band:(b + 1) * band].ljust(band, b"\x00"))
    return path


def write_segmented_udif(folder, stem, data, part_size, chunk_sectors=2048):
    """Write data as a UDIF image split the way hdiutil segment splits one: the
    data of all the segments laid end to end, the block table only in the first
    (stem.dmg), and a trailer on every segment carrying one identifier, the segment
    count, the segment's own number and where its data starts in the whole."""
    sectors = len(data) // 512
    fork, entries, at = bytearray(), [], 0
    while at < sectors:
        count = min(chunk_sectors, sectors - at)
        blob = zlib.compress(data[at * 512:(at + count) * 512])
        entries.append((0x80000005, 0, at, count, len(fork), len(blob)))
        fork += blob
        at += count
    entries.append((0xFFFFFFFF, 0, at, 0, len(fork), 0))
    crc = zlib.crc32(data[:sectors * 512])
    mish = struct.pack(">4sIQQQII24x", b"mish", 1, 0, sectors, 0, 0, len(entries))
    mish += _udif_checksum(crc) + struct.pack(">I", len(entries))
    mish += b"".join(struct.pack(">IIQQQQ", *e) for e in entries)
    tables = plistlib.dumps({"resource-fork": {"blkx": [{"Name": "whole disk", "Data": mish}]}})
    pieces = [bytes(fork[i:i + part_size]) for i in range(0, len(fork), part_size)]
    paths, running = [], 0
    for number, piece in enumerate(pieces, 1):
        path = os.path.join(folder, f"{stem}.dmg" if number == 1
                            else f"{stem}.{number:03d}.dmgpart")
        body = tables if number == 1 else plistlib.dumps({"resource-fork": {}})
        with open(path, "wb") as out:
            out.write(piece)
            xml_offset = out.tell()
            out.write(body)
            trailer = struct.pack(">4sIIIQQQQQII", b"koly", 4, 512, 1, running, 0,
                                  len(piece), 0, 0, number, len(pieces))
            trailer += b"\x5a" * 16 + _udif_checksum(zlib.crc32(piece))
            trailer += struct.pack(">QQ", xml_offset, len(body)) + bytes(120)
            trailer += _udif_checksum(zlib.crc32(struct.pack(">I", crc)))
            trailer += struct.pack(">IQ", 1, sectors) + bytes(12)
            out.write(trailer)
        paths.append(path)
        running += len(piece)
    return paths


def write_sparsebundle(folder, data, band=1 << 20, token=b""):
    """Write data as an Apple sparse bundle: Info.plist, a token file, and bands/
    holding each band that is not all zeros, named in lowercase hexadecimal."""
    os.makedirs(os.path.join(folder, "bands"))
    info = {"CFBundleInfoDictionaryVersion": "6.0", "band-size": band,
            "bundle-backingstore-version": 1,
            "diskimage-bundle-type": "com.apple.diskimage.sparsebundle",
            "size": len(data)}
    with open(os.path.join(folder, "Info.plist"), "wb") as out:
        plistlib.dump(info, out)
    with open(os.path.join(folder, "token"), "wb") as out:
        out.write(token)
    for number in range(-(-len(data) // band)):
        piece = data[number * band:(number + 1) * band]
        if any(piece):
            with open(os.path.join(folder, "bands", format(number, "x")), "wb") as out:
                out.write(piece)
    return folder


ENC_PASSWORD = 'raw-image-test-password'


def _encrcdsa_parts(key_bits=128, seed=7):
    """AES and HMAC keys and a password item wrapping them, laid out as hdiutil
    writes an encrypted image (encrcdsa version 2, keys wrapped with AES-192)."""
    import hmac as _hmac  # pylint: disable=import-outside-toplevel,unused-import
    from Crypto.Cipher import AES  # pylint: disable=import-outside-toplevel
    rng = __import__('random').Random(seed)
    aes_key, hmac_key = rng.randbytes(key_bits // 8), rng.randbytes(20)
    salt, iv = rng.randbytes(20), rng.randbytes(8)
    keydata = aes_key + hmac_key + b'CKIE\x00'
    pad = 16 - len(keydata) % 16
    keydata += bytes([pad]) * pad
    derived = hashlib.pbkdf2_hmac('sha1', ENC_PASSWORD.encode(), salt, 1000, 32)
    blob = AES.new(derived[:24], AES.MODE_CBC, iv=iv + bytes(8)).encrypt(keydata)
    item = struct.pack('>LQL32sL32s5L', 0x67, 1000, 20, salt, 8, iv, 192, 0x80000001,
                       7, 6, len(blob)) + blob
    return aes_key, hmac_key, item


def _encrypt_blocks(aes_key, hmac_key, data):
    import hmac  # pylint: disable=import-outside-toplevel
    from Crypto.Cipher import AES  # pylint: disable=import-outside-toplevel
    data += bytes(-len(data) % 512)
    return b''.join(
        AES.new(aes_key, AES.MODE_CBC,
                iv=hmac.new(hmac_key, struct.pack('>L', n), 'sha1').digest()[:16])
        .encrypt(data[n * 512:(n + 1) * 512]) for n in range(len(data) // 512))


def _encrcdsa_header(item, data_length, data_start=4096):
    head = (struct.pack('>8s7L16sLQQL', b'encrcdsa', 2, 16, 5, 0x80000001, 128, 0x5B,
                        160, bytes(16), 512, data_length, data_start, 1)
            + struct.pack('>LQQ', 1, 0x60, len(item)) + item)
    return head.ljust(data_start, b'\0')


def write_encrypted(path, data):
    """``data`` in an encrypted Apple disk image that opens with ENC_PASSWORD."""
    aes_key, hmac_key, item = _encrcdsa_parts()
    with open(path, 'wb') as handle:
        handle.write(_encrcdsa_header(item, len(data)) + _encrypt_blocks(aes_key, hmac_key, data))
    return path


def write_encrypted_sparsebundle(folder, data, band=1 << 20):
    """``data`` in an encrypted sparse bundle: the token holds the header, and each
    band is encrypted on its own from its first byte, its block numbers from 0."""
    aes_key, hmac_key, item = _encrcdsa_parts(seed=8)
    bands = {}
    for number in range(-(-len(data) // band)):
        piece = data[number * band:(number + 1) * band]
        if any(piece):
            bands[format(number, 'x')] = _encrypt_blocks(aes_key, hmac_key, piece)
    os.makedirs(os.path.join(folder, 'bands'))
    info = {'CFBundleInfoDictionaryVersion': '6.0', 'band-size': band,
            'bundle-backingstore-version': 1,
            'diskimage-bundle-type': 'com.apple.diskimage.sparsebundle', 'size': len(data)}
    with open(os.path.join(folder, 'Info.plist'), 'wb') as handle:
        plistlib.dump(info, handle)
    with open(os.path.join(folder, 'token'), 'wb') as handle:
        handle.write(_encrcdsa_header(item, 0))
    for name, content in bands.items():
        with open(os.path.join(folder, 'bands', name), 'wb') as handle:
            handle.write(content)
    return folder


AD_PASSWORD = 'raw-image-ad-password'


def write_adcrypt(plain_files, out_files, password=AD_PASSWORD):
    """Each of ``plain_files`` encrypted into ``out_files`` as FTK Imager's AD
    encryption writes a set: one AES-256 key, the 512-byte header in the first file
    only, file i in CTR mode from counter i << 64, the counter little endian, and the
    key encrypted under PBKDF2-HMAC-SHA1 of the password's SHA-512."""
    import hmac  # pylint: disable=import-outside-toplevel
    from Crypto.Cipher import AES  # pylint: disable=import-outside-toplevel
    from Crypto.Util import Counter  # pylint: disable=import-outside-toplevel

    def ctr(key, data, first):
        counter = Counter.new(128, initial_value=first, little_endian=True)
        return AES.new(key, AES.MODE_CTR, counter=counter).encrypt(data)

    rng = __import__('random').Random(9)
    file_key, salt = rng.randbytes(32), rng.randbytes(16)
    made = hashlib.pbkdf2_hmac('sha1', hashlib.sha512(password.encode()).digest(), salt,
                               1000, 32)
    wrapped = ctr(made, file_key, 0)
    header = (struct.pack('<8sIIhhh2sIIIIII', b'ADCRYPT\x00', 1, 512, -1, -1, -1,
                          b'\x00\x00', 3, 2, 1000, 16, 32, 64)
              + salt + wrapped + hmac.new(made, wrapped, 'sha512').digest()).ljust(512, b'\0')
    for index, (src, dst) in enumerate(zip(plain_files, out_files)):
        with open(src, 'rb') as handle:
            body = ctr(file_key, handle.read(), index << 64)
        with open(dst, 'wb') as handle:
            handle.write((header if index == 0 else b'') + body)
    return out_files


def with_mbr(volume_bytes, start_lba=2048):
    """The volume behind an MBR whose one entry covers it in full, as a disk carries it."""
    entry = bytearray(16)
    entry[4] = 0x07                                        # NTFS/exFAT type byte
    struct.pack_into("<II", entry, 8, start_lba, len(volume_bytes) // 512)
    mbr = bytearray(start_lba * 512)
    mbr[446:462] = entry
    mbr[510:512] = b"\x55\xaa"
    return bytes(mbr) + volume_bytes


class _Recorder:
    """Stands in for logfunc so a test can read what the seeker said."""

    def __init__(self):
        self.lines = []

    def __call__(self, message=''):
        self.lines.append(str(message))

    def text(self):
        return '\n'.join(self.lines)


class RawImageSeekerTest(unittest.TestCase):
    """Staged bytes against an independent reader, on NTFS, FAT32, exFAT, E01 and split sets."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_test_')
        for stem in ('ntfs-fixture', 'fat32-deleted', 'exfat-deleted', 'apfs-fixture',
                     'ntfs-streams'):
            with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, \
                    open(os.path.join(cls.work, f'{stem}.img'), 'wb') as dst:
                shutil.copyfileobj(src, dst)
        cls.ntfs = os.path.join(cls.work, 'ntfs-fixture.img')
        cls.fat32 = os.path.join(cls.work, 'fat32-deleted.img')
        cls.exfat = os.path.join(cls.work, 'exfat-deleted.img')
        cls.apfs = os.path.join(cls.work, 'apfs-fixture.img')
        cls.streams = os.path.join(cls.work, 'ntfs-streams.img')
        cls.ntfs_hashes = _hash_list(FIXTURES / 'ntfs-fixture.sha256')
        cls.fat32_hashes = _hash_list(FIXTURES / 'fat32-deleted.live.sha256')
        cls.exfat_hashes = _hash_list(FIXTURES / 'exfat-deleted.live.sha256')
        cls.apfs_hashes = _hash_list(FIXTURES / 'apfs-fixture.sha256')
        cls.stream_hashes = _hash_list(FIXTURES / 'ntfs-streams.sha256')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _seeker(self, image):
        seeker = FileSeekerRaw(image, self.data)
        self.addCleanup(seeker.cleanup)
        return seeker

    def _staged_by_source(self, seeker, volume):
        """{path within the volume: staged path} for every file the seeker staged."""
        out = {}
        for staged, info in seeker.file_infos.items():
            prefix = volume + '/'
            if info.source_path.startswith(prefix) and not info.source_path.endswith('/'):
                out[info.source_path[len(prefix):]] = staged
        return out

    def _check_volume(self, image, expected):
        # each seeker gets its own data folder: two volumes holding a file of the
        # same name would otherwise meet in one folder and exercise the
        # case-collision guard, which is not what this checks
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        seeker = self._seeker(image)
        self.assertEqual([v['name'] for v in seeker.volumes], ['lba0'])
        found = seeker.search('*')
        self.assertTrue(found)
        staged = self._staged_by_source(seeker, 'lba0')
        missing = sorted(set(expected) - set(staged))
        self.assertEqual(missing, [], 'files the independent reader saw and the seeker did not stage')
        differ = [rel for rel, digest in expected.items() if _sha256(staged[rel]) != digest]
        self.assertEqual(differ, [])
        return seeker, staged

    # ---- bytes -----------------------------------------------------------------

    def test_every_ntfs_file_matches_the_independent_hash_list(self):
        seeker, staged = self._check_volume(self.ntfs, self.ntfs_hashes)
        self.assertEqual(len(self.ntfs_hashes), 475)
        self.assertGreaterEqual(len(staged), 475)
        # every staged member is one the run can name back to the image
        for path, info in seeker.file_infos.items():
            self.assertTrue(info.source_path.startswith('lba0/'), info.source_path)
            if info.source_path.endswith('/'):
                self.assertTrue(os.path.isdir(path))
            else:
                self.assertTrue(os.path.isfile(path))

    def test_a_pattern_matches_an_ntfs_fat_or_exfat_name_whatever_its_case(self):
        """Those filesystems look names up whatever their case by default, so the pattern does too."""
        for image, pattern, member in ((self.ntfs, '*/ADS.TXT', 'lba0/ads.txt'),
                                       (self.fat32, '*/A.Bin', 'lba0/a.bin'),
                                       (self.exfat, '*/c.BIN', 'lba0/c.bin')):
            with self.subTest(image=os.path.basename(image)):
                self.data = tempfile.mkdtemp(prefix='raw_image_data_')
                self.addCleanup(shutil.rmtree, self.data, True)
                seeker = self._seeker(image)
                found = seeker.search(pattern)
                self.assertEqual([seeker.file_infos[p].source_path for p in found], [member])

    @unittest.skipIf(os.path.normcase('A') == 'a', 'normcase folds every name on this platform')
    def test_a_pattern_matches_an_apfs_name_only_in_its_own_case(self):
        """The seeker matches an APFS name exactly whatever the volume's own rule, so a pattern in
        another case finds nothing."""
        seeker = self._seeker(self.apfs)
        self.assertEqual(seeker.search('*/qnxprobe/small.txt'), [])
        found = seeker.search('*/QNXPROBE/small.txt')
        self.assertEqual([seeker.file_infos[p].source_path for p in found],
                         ['lba0/QNXPROBE/small.txt'])

    def test_fat32_and_exfat_files_match_the_macos_driver(self):
        self._check_volume(self.fat32, self.fat32_hashes)
        self._check_volume(self.exfat, self.exfat_hashes)

    def test_every_apfs_file_matches_the_independent_hash_list(self):
        # The container's one volume is named QNXPROBE, and a container's volumes
        # are the first level of the walk, so every file sits beneath it.
        seeker = self._seeker(self.apfs)
        self.assertEqual([v['name'] for v in seeker.volumes], ['lba0'])
        self.assertTrue(seeker.search('*'))
        staged = self._staged_by_source(seeker, 'lba0/QNXPROBE')
        self.assertEqual(len(self.apfs_hashes), 411)
        missing = sorted(set(self.apfs_hashes) - set(staged))
        self.assertEqual(missing, [], 'files the independent reader saw and the seeker did not stage')
        differ = [rel for rel, digest in self.apfs_hashes.items()
                  if _sha256(staged[rel]) != digest]
        self.assertEqual(differ, [])

    def test_only_matched_files_are_staged(self):
        import fnmatch
        pattern = '*/many/file_00[0-4]?.txt'
        expected = [rel for rel in self.ntfs_hashes if fnmatch.fnmatch('lba0/' + rel, pattern)]
        self.assertTrue(20 < len(expected) < 475)
        seeker = self._seeker(self.ntfs)
        found = seeker.search(pattern)
        self.assertEqual(len(found), len(expected))
        self.assertEqual(len(seeker.copied), len(expected))
        staged_files = sum(len(files) for _r, _d, files in os.walk(self.data))
        self.assertEqual(staged_files, len(expected))

    def test_a_pattern_is_matched_once_and_cached(self):
        seeker = self._seeker(self.ntfs)
        first = seeker.search('*/many/file_0001.txt')
        again = seeker.search('*/many/file_0001.txt')
        self.assertEqual(first, again)
        self.assertEqual(seeker.search('*/many/file_0001.txt', return_on_first_hit=True), first[0])

    # ---- the one-pass routes ----------------------------------------------------
    #
    # NTFS is listed from one pass over $MFT and APFS from one pass over its
    # catalog, rather than directory by directory. The member list is the order
    # search() hands an artifact its files in, so each route has to produce the
    # directory-by-directory walk's list exactly, order and all, and not merely
    # the same set. The walk that each is compared against is the same seeker
    # with the faster route taken away.

    def _members(self, image, **patches):
        """(member list, {member: (node, size, mtime, reading)}, stream list) from
        a fresh seeker."""
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        with contextlib.ExitStack() as stack:
            for walker_class, key in ((qnxprobe.NtfsWalker, 'ntfs'),
                                      (qnxprobe.ApfsWalker, 'apfs')):
                if patches.get(key):
                    stack.enter_context(mock.patch.multiple(walker_class, **patches[key]))
            seeker = self._seeker(image)
        entries = {member: None if entry is None else
                   (repr(entry.node), entry.size, entry.mtime, entry.reading)
                   for member, entry in seeker._entries.items()}  # pylint: disable=protected-access
        return list(seeker.name_list), entries, list(seeker.stream_list)

    def test_ntfs_is_listed_in_one_pass_and_matches_the_tree_walk(self):
        fast = self._members(self.ntfs)
        self.assertIn('(one pass over $MFT)', self.log.text())
        slow = self._members(self.ntfs, ntfs={'listing': None})
        self.assertIn('(directory by directory)', self.log.text())
        self.assertGreater(len(fast[0]), 475)
        self.assertEqual(fast[0], slow[0])
        self.assertEqual(fast[1], slow[1])

    def test_apfs_is_listed_in_one_pass_and_matches_the_tree_walk(self):
        fast = self._members(self.apfs)
        self.assertIn('(one pass over the catalog)', self.log.text())
        slow = self._members(self.apfs, apfs={'prime_records': None})
        self.assertIn('(directory by directory)', self.log.text())
        self.assertGreater(len(fast[0]), 411)
        self.assertEqual(fast[0], slow[0])
        self.assertEqual(fast[1], slow[1])

    def test_the_ntfs_route_reads_no_directory_index(self):
        # Were the one-pass route quietly abandoned, the list above would still
        # match and only be slower, so nothing would notice. A walker that cannot
        # read a directory index at all must still list the whole volume.
        whole = self._members(self.ntfs)
        refused = mock.Mock(side_effect=AssertionError('a directory index was read'))
        blind = self._members(self.ntfs, ntfs={'listdir': refused})
        refused.assert_not_called()
        self.assertEqual(blind[0], whole[0])
        self.assertNotIn('Could not list', self.log.text())

    def test_a_one_pass_listing_that_fails_falls_back_to_the_tree_walk(self):
        whole = self._members(self.ntfs)
        real = qnxprobe.NtfsWalker.listing

        def cut_short(walker):
            for count, row in enumerate(real(walker)):
                if count == 50:
                    raise ValueError('the pass stopped part way')
                yield row

        fallen = self._members(self.ntfs, ntfs={'listing': cut_short})
        self.assertIn('the one-pass listing failed (ValueError', self.log.text())
        self.assertIn('(directory by directory)', self.log.text())
        self.assertEqual(fallen[0], whole[0])
        self.assertEqual(fallen[1], whole[1])

    def test_a_name_two_records_claim_is_listed_once(self):
        # A volume whose records disagree can have two records name one file in
        # one directory. Listing it twice would hand an artifact the same staged
        # copy twice, which reads it twice and reports its rows twice.
        real = qnxprobe.NtfsWalker.listing

        def doubled(walker):
            for row in real(walker):
                yield row
                if row[0] == 'many/file_0001.txt':
                    yield ('many/file_0001.txt', row[1] + 100000) + row[2:]

        names, entries, _streams = self._members(self.ntfs, ntfs={'listing': doubled})
        self.assertEqual(names.count('lba0/many/file_0001.txt'), 1)
        self.assertNotEqual(entries['lba0/many/file_0001.txt'][0], repr(100000))
        self.assertIn('claimed by more than one record', self.log.text())

    # ---- NTFS alternate data streams --------------------------------------------
    #
    # ntfs-streams.img holds streams in each shape the reader has a rule for, and its
    # hash list is The Sleuth Kit's reading of each stream from its first stored
    # cluster, which is what the reader returns (see the README beside it). A
    # stream is a member only a pattern naming a stream can reach, so every
    # pattern written before streams were members is handed exactly what it was.

    def _staged_streams(self, seeker, pattern):
        """{path:stream within the volume: staged path} for a stream pattern."""
        found = seeker.search(pattern)
        out = {}
        for staged in found:
            source = seeker.file_infos[staged].source_path
            self.assertTrue(source.startswith('lba0/'), source)
            out[source[len('lba0/'):]] = staged
        return out

    def test_every_ntfs_stream_matches_the_independent_hash_list(self):
        seeker = self._seeker(self.streams)
        self.assertEqual(len(self.stream_hashes), 28)
        staged = self._staged_streams(seeker, '*:*')
        self.assertEqual(sorted(staged), sorted(self.stream_hashes))
        differ = [rel for rel, digest in self.stream_hashes.items()
                  if _sha256(staged[rel]) != digest]
        self.assertEqual(differ, [])
        self.assertEqual(len(seeker.stream_list), 28)

    # ---- NTFS directory indexes --------------------------------------------------
    #
    # A directory whose file name index has grown into an $INDEX_ALLOCATION attribute
    # gives it as ``<directory>:$I30``. It is not a stream: only a pattern that ends
    # ``:$I30`` reaches it, so ``*:*`` above still stages exactly the 28 streams.

    def test_directory_indexes_are_staged_only_for_a_pattern_that_ends_in_their_name(self):
        seeker = self._seeker(self.ntfs)
        self.assertEqual(len(seeker.index_list), 5)
        self.assertTrue(all(name.endswith(':$I30') for name in seeker.index_list))
        self.assertIn('lba0/:$I30', seeker.index_list)
        self.assertIn('lba0/many:$I30', seeker.index_list)
        self.assertTrue(set(seeker.index_list).isdisjoint(seeker.name_list))
        self.assertTrue(set(seeker.index_list).isdisjoint(seeker.stream_list))
        for pattern in ('*', '*:*', '*/many*', '*:$I3*'):
            sources = [seeker.file_infos[path].source_path for path in seeker.search(pattern)]
            self.assertEqual([s for s in sources if s.endswith(':$I30')], [], pattern)
        staged = seeker.search('*:$I30')
        self.assertEqual(sorted(seeker.file_infos[path].source_path for path in staged),
                         sorted(seeker.index_list))
        for path in staged:
            self.assertNotIn(':', os.path.basename(path))
            with open(path, 'rb') as handle:
                data = handle.read()
            self.assertTrue(data and len(data) % 4096 == 0, path)
            self.assertEqual({data[offset:offset + 4] for offset in range(0, len(data), 4096)}, {b'INDX'})
        one = seeker.search('*/many:$I30')
        self.assertEqual([seeker.file_infos[path].source_path for path in one], ['lba0/many:$I30'])
        self.assertEqual(os.path.getsize(one[0]), 94208)
        self.assertIn('5 directories can give their index, to a pattern that asks for it (*:$I30)',
                      self.log.text())

    def test_a_stream_named_like_an_index_is_still_reached(self):
        # A pattern that ends ':$I30' is handed the indexes besides the streams it names.
        seeker = self._seeker(self.streams)
        self.assertEqual(seeker.index_list, ['lba0/:$I30'])
        real = next(name for name in seeker.stream_list if name.endswith(':rootstream'))
        seeker.stream_list.append('lba0/odd:$I30')
        seeker._entries['lba0/odd:$I30'] = seeker._entries[real]      # pylint: disable=protected-access
        found = sorted(seeker.file_infos[path].source_path for path in seeker.search('*:$I30'))
        self.assertEqual(found, ['lba0/:$I30', 'lba0/odd:$I30'])

    def test_a_reader_without_directory_indexes_lists_none(self):
        with mock.patch.object(raw_image.qnxprobe.NtfsWalker, 'directory_index', None):
            seeker = self._seeker(self.ntfs)
        self.assertEqual(seeker.index_list, [])
        self.assertEqual(seeker.search('*:$I30'), [])
        self.assertNotIn('can give their index', self.log.text())

    def test_a_pattern_that_names_no_stream_is_never_handed_one(self):
        seeker = self._seeker(self.streams)
        everything = seeker.search('*')
        self.assertTrue(everything)
        sources = [seeker.file_infos[path].source_path for path in everything]
        self.assertEqual([s for s in sources if ':' in s], [])
        downloads = seeker.search('*/downloads/*')
        self.assertEqual(sorted(seeker.file_infos[p].source_path for p in downloads),
                         ['lba0/downloads/', 'lba0/downloads/report.pdf',
                          'lba0/downloads/setup.exe'])
        self.assertTrue(set(seeker.name_list).isdisjoint(seeker.stream_list))

    def test_zone_identifier_streams_are_staged_under_a_name_without_the_colon(self):
        seeker = self._seeker(self.streams)
        staged = self._staged_streams(seeker, '*:Zone.Identifier')
        self.assertEqual(sorted(staged), ['downloads/report.pdf:Zone.Identifier',
                                          'downloads/setup.exe:Zone.Identifier'])
        for rel, path in staged.items():
            self.assertEqual(_sha256(path), self.stream_hashes[rel])
            self.assertNotIn(':', os.path.basename(path))
        with open(staged['downloads/setup.exe:Zone.Identifier'], 'rb') as handle:
            self.assertTrue(handle.read().startswith(b'[ZoneTransfer]\r\nZoneId=3\r\n'))

    def test_a_stream_carries_its_file_s_dates(self):
        seeker = self._seeker(self.streams)
        stream = seeker.search('*/downloads/setup.exe:Zone.Identifier')[0]
        host = seeker.search('*/downloads/setup.exe')[0]
        self.assertGreater(seeker.file_infos[stream].modification_date, 1_600_000_000)
        self.assertEqual(seeker.file_infos[stream].creation_date,
                         seeker.file_infos[host].creation_date)
        self.assertEqual(seeker.file_infos[stream].modification_date,
                         seeker.file_infos[host].modification_date)

    def test_the_journal_is_staged_from_its_first_stored_cluster(self):
        # journal.bin:$J is the shape of $Extend/$UsnJrnl:$J: 1 MiB of hole, then
        # records in 365 runs whose run list continues in a second MFT record.
        # Its recorded size is 2,859,008 bytes; what is stored is 1,810,432.
        seeker = self._seeker(self.streams)
        staged = self._staged_streams(seeker, '*/journal.bin:$J')
        self.assertEqual(list(staged), ['journal.bin:$J'])
        path = staged['journal.bin:$J']
        self.assertEqual(os.path.getsize(path), 1_810_432)
        self.assertEqual(_sha256(path), self.stream_hashes['journal.bin:$J'])

    def test_a_stream_that_stores_nothing_is_not_a_member(self):
        seeker = self._seeker(self.streams)
        self.assertNotIn('lba0/$BadClus:$Bad', seeker.stream_list)
        self.assertNotIn('lba0/hollow.bin:nothing-stored', seeker.stream_list)
        self.assertEqual(seeker.search('*:$Bad'), [])
        self.assertIn('lba0/empty.txt:empty', seeker.stream_list)
        self.assertEqual(os.path.getsize(seeker.search('*/empty.txt:empty')[0]), 0)

    def test_streams_on_directories_and_the_root_are_members(self):
        seeker = self._seeker(self.streams)
        self.assertIn('lba0/folder:dirstream', seeker.stream_list)
        self.assertIn('lba0/:rootstream', seeker.stream_list)
        root = seeker.search('*/:rootstream')
        self.assertEqual(len(root), 1)
        self.assertEqual(_sha256(root[0]), self.stream_hashes[':rootstream'])

    def test_streams_are_the_same_by_both_routes(self):
        fast = self._members(self.streams)
        slow = self._members(self.streams, ntfs={'listing': None})
        self.assertEqual(len(fast[2]), 28)
        self.assertEqual(fast, slow)

    def test_the_run_log_counts_the_streams(self):
        self._seeker(self.streams)
        self.assertIn('and 28 alternate data streams, matched only by a pattern', self.log.text())
        self.assertIn('members and 28 streams', self.log.text())

    def test_a_reader_without_streams_leaves_the_members_as_they_were(self):
        # a vendored qnxprobe older than 1.37 has no streams(); the seeker then
        # lists exactly the members it did, and no stream
        with_streams = self._members(self.streams)
        without = self._members(self.streams, ntfs={'streams': None})
        self.assertEqual(without[2], [])
        self.assertEqual(without[0], with_streams[0])
        self.assertNotIn('alternate data streams', self.log.text().split('Reading ')[-1])

    def test_the_stream_on_the_file_fixture(self):
        # the fixture every other NTFS test reads carries one stream of its own
        seeker = self._seeker(self.ntfs)
        found = seeker.search('*/ads.txt:hidden')
        self.assertEqual(len(found), 1)
        with open(found[0], 'rb') as handle:
            self.assertEqual(handle.read(), b'the hidden stream\n')

    # A volume's free space is a member only a pattern that asks for it can reach.
    # The expected bytes are read from the image file directly, at the offsets the
    # staged map gives, and the expected total is the fixture's free cluster count.

    def _free_space(self, image):
        seeker = self._seeker(image)
        listed = list(seeker.name_list)
        staged = seeker.search('*.unallocated.bin')
        return seeker, listed, staged

    def test_free_space_is_staged_for_a_pattern_that_asks_for_it(self):
        for image in (self.ntfs, self.fat32, self.exfat, self.apfs):
            with self.subTest(image=os.path.basename(image)):
                seeker, listed, staged = self._free_space(image)
                self.assertEqual(len(staged), 1)
                self.assertEqual(seeker.name_list, listed)
                name = os.path.basename(image)
                self.assertEqual(
                    seeker.file_infos[staged[0]].source_path,
                    f'lba0/$Unallocated/{name}.lba0.unallocated.bin')
                with open(image, 'rb') as handle:
                    disk = handle.read()
                with open(staged[0], 'rb') as handle:
                    free = handle.read()
                with open(staged[0][:-4] + '.tsv', encoding='utf-8') as handle:
                    rows = [line.split('\t') for line in handle.read().splitlines()[1:]]
                self.assertTrue(rows)
                covered = 0
                for in_file, in_image, length in ((int(a), int(b), int(c))
                                                  for a, b, c in rows):
                    self.assertEqual(in_file, covered)
                    self.assertEqual(free[in_file:in_file + length],
                                     disk[in_image:in_image + length])
                    covered += length
                self.assertEqual(covered, len(free))

    def test_fat32_free_space_is_the_fixture_s_free_clusters(self):
        # fat32-deleted.img: 512-byte sectors, one sector per cluster, and the FAT
        # read here by hand, not through the reader under test
        with open(self.fat32, 'rb') as handle:
            disk = handle.read()
        sector, per_cluster, reserved = struct.unpack_from('<HBH', disk, 11)
        fats = disk[16]
        fat_sectors = struct.unpack_from('<I', disk, 36)[0]
        total = struct.unpack_from('<I', disk, 32)[0]
        clusters = (total - reserved - fats * fat_sectors) // per_cluster
        fat = disk[reserved * sector:(reserved + fat_sectors) * sector]
        free = sum(1 for n in range(2, clusters + 2)
                   if struct.unpack_from('<I', fat, 4 * n)[0] & 0x0FFFFFFF == 0)
        _seeker, _listed, staged = self._free_space(self.fat32)
        self.assertEqual(os.path.getsize(staged[0]), free * per_cluster * sector)

    def test_a_pattern_that_does_not_ask_is_never_handed_free_space(self):
        seeker = self._seeker(self.fat32)
        for pattern in ('*', '*.bin', '*/$Unallocated/*', '*unallocated*'):
            with self.subTest(pattern=pattern):
                self.assertFalse(
                    [path for path in seeker.search(pattern) if 'unallocated' in path])
        self.assertFalse(os.path.isdir(os.path.join(seeker.data_folder, 'lba0',
                                                    '$Unallocated')))

    def test_free_space_is_staged_once(self):
        seeker = self._seeker(self.fat32)
        first = seeker.search('*.unallocated.bin')
        stamp = os.path.getmtime(first[0])
        self.assertEqual(seeker.search('*.unallocated.bin', force=True), first)
        self.assertEqual(os.path.getmtime(first[0]), stamp)

    def test_what_names_free_space(self):
        self.assertTrue(names_free_space('*.unallocated.bin'))
        self.assertTrue(names_free_space('*/$Unallocated/*.UNALLOCATED.BIN'))
        self.assertFalse(names_free_space('*'))
        self.assertFalse(names_free_space('*.bin'))
        self.assertFalse(names_free_space('*/x.unallocated.bin/*'))

    def test_the_run_log_says_free_space_can_be_asked_for(self):
        log = _Recorder()
        with mock.patch.object(raw_image, 'logfunc', log):
            seeker = FileSeekerRaw(self.fat32, tempfile.mkdtemp(dir=self.work))
            self.addCleanup(seeker.cleanup)
        self.assertTrue(any('free space' in line for line in log.lines))

    # ---- deleted files a reader can recover ----------------------------------------

    def _with_deleted(self, entries):
        """A seeker over the FAT32 fixture with one more volume, whose reader
        recovers `entries`. No fixture here is a flash filesystem, so the reader
        is a stand-in with the two methods the seeker asks for."""
        seeker = FileSeekerRaw(self.fat32, tempfile.mkdtemp(dir=self.work))
        self.addCleanup(seeker.cleanup)
        seeker.volumes.append({'name': 'flash0', 'walker': _FakeFlashWalker(entries)})
        return seeker

    def test_deleted_files_are_staged_for_a_pattern_that_names_the_folder(self):
        entries = [
            _FakeDeleted('gps.dat', 'var/sysinfo', b'first version', mtime=1700000000),
            _FakeDeleted('gps.dat', None, b'second version'),
            _FakeDeleted('', None, b'no name'),
            _FakeDeleted('lost.dat', 'var', b'', recoverable=False),
            _FakeDeleted('raises.dat', 'var', None),
        ]
        log = _Recorder()
        with mock.patch.object(raw_image, 'logfunc', log):
            seeker = self._with_deleted(entries)
            staged = seeker.search('*/$Deleted/*')
        by_member = {seeker.file_infos[path].source_path: path for path in staged}
        self.assertEqual(sorted(by_member), [
            'flash0/$Deleted/$NoFolder/$NoName.deleted-000002',
            'flash0/$Deleted/$NoFolder/gps.dat.deleted-000001',
            'flash0/$Deleted/var/sysinfo/gps.dat.deleted-000000'])
        first = by_member['flash0/$Deleted/var/sysinfo/gps.dat.deleted-000000']
        with open(first, 'rb') as handle:
            self.assertEqual(handle.read(), b'first version')
        self.assertEqual(seeker.file_infos[first].modification_date, 1700000000)
        with open(by_member['flash0/$Deleted/$NoFolder/gps.dat.deleted-000001'], 'rb') as handle:
            self.assertEqual(handle.read(), b'second version')
        # the one the reader calls unreadable is counted, the one it fails on is named
        self.assertTrue(any('4 files outside the live tree can be read, 1 are named and cannot' in line
                            for line in log.lines), log.lines)
        self.assertTrue(any('Not staged' in line and 'raises.dat' in line
                            for line in log.lines), log.lines)
        self.assertFalse(any(name.startswith('raises.dat')
                             for _root, _dirs, names in os.walk(seeker.data_folder)
                             for name in names))

    def test_a_pattern_that_does_not_name_the_folder_never_reaches_a_deleted_file(self):
        seeker = self._with_deleted([_FakeDeleted('gps.dat', 'var', b'x')])
        for pattern in ('*', '*gps.dat*', '*/var/*', '*.deleted-*'):
            for path in seeker.search(pattern):
                self.assertNotIn('$Deleted', seeker.file_infos[path].source_path, pattern)
        # and the reader was never asked
        self.assertIsNone(seeker.deleted_list)
        self.assertEqual(seeker.volumes[-1]['walker'].asked, 0)
        self.assertEqual(len(seeker.search('*/$Deleted/*gps.dat*')), 1)
        seeker.search('*/$Deleted/*')
        self.assertEqual(seeker.volumes[-1]['walker'].asked, 1)

    def test_what_names_deleted(self):
        for pattern in ('*/$Deleted/*', '*/$Deleted/*/gps.dat*', '$Deleted/x', '*\\$Deleted\\*'):
            self.assertTrue(names_deleted(pattern), pattern)
        for pattern in ('*', '*Deleted*', '*/x$Deleted/*', '*/$Deleted.bak/*', '*.deleted-*'):
            self.assertFalse(names_deleted(pattern), pattern)

    def test_what_names_a_stream(self):
        for pattern in ('*:Zone.Identifier', '*/$Extend/$UsnJrnl:$J', '*/:rootstream', '*:*',
                        '*\\x.exe:Zone.Identifier'):
            self.assertTrue(names_a_stream(pattern), pattern)
        for pattern in ('*', '*/Recent/*', '*/c:/Users/*/NTUSER.DAT', '*/Windows/Prefetch/*.pf'):
            self.assertFalse(names_a_stream(pattern), pattern)

    # ---- members and metadata ---------------------------------------------------

    def test_directories_are_members_with_a_trailing_slash(self):
        seeker = self._seeker(self.ntfs)
        dirs = [m for m in seeker.name_list if m.endswith('/')]
        self.assertIn('lba0/many/', dirs)
        found = seeker.search('*/many/')
        self.assertEqual(len(found), 1)
        self.assertTrue(os.path.isdir(found[0]))
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'lba0/many/')

    def test_ntfs_instants_reach_file_info_and_the_staged_copy(self):
        seeker = self._seeker(self.ntfs)
        path = seeker.search('*/many/file_0001.txt')[0]
        info = seeker.file_infos[path]
        self.assertGreater(info.creation_date, 1_600_000_000)
        self.assertGreater(info.modification_date, 1_600_000_000)
        self.assertEqual(int(os.path.getmtime(path)), int(info.modification_date))

    def test_fat_readings_stamp_the_copy_and_record_no_instant(self):
        seeker = self._seeker(self.fat32)
        path = seeker.search('*/a.bin')[0]
        info = seeker.file_infos[path]
        self.assertEqual((info.creation_date, info.modification_date), (0, 0))
        entry = seeker._entries['lba0/a.bin']  # pylint: disable=protected-access
        self.assertTrue(entry.reading)
        expected = time.mktime(time.strptime(entry.reading[:19], '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(int(os.path.getmtime(path)), int(expected))

    def test_the_run_log_names_the_volumes(self):
        self._seeker(self.ntfs)
        text = self.log.text()
        self.assertIn('lba0', text)
        self.assertIn('ntfs', text)
        self.assertRegex(text, r'walked lba0: 4\d\d files')
        self.assertNotIn('WARNING', text)

    # ---- containers -------------------------------------------------------------

    def test_an_e01_set_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_e01_', dir=self.work)
        paths = write_ewf(folder, 'ntfs', data, chunks_per_segment=200)
        self.assertGreater(len(paths), 1)
        seeker = self._seeker(paths[0])
        self.assertIn('an EWF acquisition of', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_an_aff_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        page = 1 << 20
        pages = range(-(-len(data) // page))
        folder = tempfile.mkdtemp(prefix='raw_image_aff_', dir=self.work)
        path = write_aff(os.path.join(folder, 'ntfs.aff'), data, pages, page, len(data))
        seeker = self._seeker(path)
        self.assertIn('an AFF acquisition of one file', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_an_afd_is_read_whole_from_any_one_file_in_it(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        page = 1 << 20
        count = -(-len(data) // page)
        folder = os.path.join(tempfile.mkdtemp(prefix='raw_image_afd_', dir=self.work),
                              'ntfs.afd')
        os.mkdir(folder)
        groups = [range(0, count // 2), range(count // 2, count)]
        for index, pages in enumerate(groups):
            write_aff(os.path.join(folder, f'file_{index:03d}.aff'), data, pages, page,
                      len(data) if index == len(groups) - 1 else None)
        seeker = self._seeker(os.path.join(folder, 'file_001.aff'))
        self.assertIn('an AFD acquisition of 2 files', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_a_dmg_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_dmg_', dir=self.work)
        path = write_udif(os.path.join(folder, 'ntfs.dmg'), data)
        seeker = self._seeker(path)
        self.assertIn('an Apple disk image of one file', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_a_sparseimage_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_sparse_', dir=self.work)
        path = write_sparseimage(os.path.join(folder, 'ntfs.sparseimage'), data)
        seeker = self._seeker(path)
        self.assertIn('an Apple sparse image of one file', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_a_segmented_dmg_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_dmgpart_', dir=self.work)
        paths = write_segmented_udif(folder, 'ntfs', data, part_size=16 * 1024)
        self.assertGreater(len(paths), 2)
        seeker = self._seeker(paths[0])
        self.assertIn(f'an Apple disk image of {len(paths)} files, joined by the reader: '
                      f'ntfs.dmg .. {os.path.basename(paths[-1])}', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_a_dmgpart_on_its_own_names_the_dmg_to_open(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_dmgpart_', dir=self.work)
        paths = write_segmented_udif(folder, 'ntfs', data, part_size=16 * 1024)
        with self.assertRaises(Exception) as caught:
            FileSeekerRaw(paths[1], self.data)
        self.assertIn('open its first segment, the .dmg file', str(caught.exception))
        os.remove(paths[2])
        with self.assertRaises(Exception) as caught:
            FileSeekerRaw(paths[0], self.data)
        self.assertIn('segment 3 is not beside it', str(caught.exception))

    def test_a_sparse_bundle_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_bundle_', dir=self.work)
        bundle = write_sparsebundle(os.path.join(folder, 'ntfs.sparsebundle'), data)
        stored = len(os.listdir(os.path.join(bundle, 'bands')))
        self.assertTrue(names_an_image_folder(bundle))
        seeker = self._seeker(bundle)
        self.assertIn(f'an Apple sparse bundle of {stored} stored band files',
                      self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_an_encrypted_sparse_bundle_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_bundle_enc_', dir=self.work)
        bundle = write_encrypted_sparsebundle(os.path.join(folder, 'locked.sparsebundle'),
                                              data)
        self.assertTrue(names_an_image_folder(bundle))
        self.assertTrue(raw_image.needs_password(bundle))
        with self.assertRaises(qnxprobe.ImagePasswordError):
            FileSeekerRaw(bundle, self.data)
        seeker = FileSeekerRaw(bundle, self.data, password=ENC_PASSWORD)
        self.addCleanup(seeker.cleanup)
        self.assertIn('encrypted (AES-128) and opened with its password', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(seeker.name_list, self._seeker(self.ntfs).name_list)

    def test_a_damaged_encrypted_header_is_refused_by_the_reader(self):
        folder = tempfile.mkdtemp(prefix='raw_image_bundle_bad_', dir=self.work)
        bundle = write_sparsebundle(os.path.join(folder, 'locked.sparsebundle'),
                                    b'\x01' * 4096, token=b'encrcdsa' + bytes(1000))
        self.assertTrue(names_an_image_folder(bundle))
        with self.assertRaises(ewfprobe.EwfFormatError) as caught:
            FileSeekerRaw(bundle, self.data, password=ENC_PASSWORD)
        self.assertIn('encrcdsa version 0', str(caught.exception))

    def test_only_an_image_folder_is_named_one(self):
        folder = tempfile.mkdtemp(prefix='raw_image_folders_', dir=self.work)
        plain = os.path.join(folder, 'extraction')
        os.makedirs(os.path.join(plain, 'private', 'var'))
        afd = os.path.join(folder, 'set.afd')
        os.makedirs(afd)
        with open(os.path.join(afd, 'file_000.aff'), 'wb') as handle:
            handle.write(b'AFF10\r\n\x00' + bytes(64))
        self.assertFalse(names_an_image_folder(plain))
        self.assertTrue(names_an_image_folder(afd))
        self.assertFalse(names_an_image_folder(os.path.join(afd, 'file_000.aff')))

    def _encrypted_ntfs(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_enc_', dir=self.work)
        return write_encrypted(os.path.join(folder, 'locked.dmg'), data)

    def test_an_encrypted_dmg_reads_with_its_password(self):
        path = self._encrypted_ntfs()
        self.assertTrue(raw_image.needs_password(path))
        self.assertFalse(raw_image.needs_password(self.ntfs))
        seeker = FileSeekerRaw(path, self.data, password=ENC_PASSWORD)
        self.addCleanup(seeker.cleanup)
        self.assertIn('encrypted (AES-128) and opened with its password', self.log.text())
        self.assertEqual(seeker.name_list, self._seeker(self.ntfs).name_list)
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertNotIn(ENC_PASSWORD, repr(vars(seeker)))

    def test_an_encrypted_dmg_without_its_password_is_refused_as_such(self):
        path = self._encrypted_ntfs()
        with self.assertRaises(qnxprobe.ImagePasswordError) as caught:
            FileSeekerRaw(path, self.data)
        self.assertFalse(caught.exception.wrong)
        with self.assertRaises(qnxprobe.ImagePasswordError) as caught:
            FileSeekerRaw(path, self.data, password='not it')
        self.assertTrue(caught.exception.wrong)
        self.assertTrue(raw_image.password_opens(path, ENC_PASSWORD))
        self.assertFalse(raw_image.password_opens(path, 'not it'))

    def test_the_command_line_password_comes_from_a_file_a_variable_or_a_terminal(self):
        path = self._encrypted_ntfs()
        self.assertIsNone(raw_image.cli_image_keys(self.ntfs).password)
        pw_file = os.path.join(self.work, 'pw.txt')
        with open(pw_file, 'wb') as handle:
            handle.write(ENC_PASSWORD.encode() + b'\r\nsecond line\n')
        self.assertEqual(raw_image.cli_image_keys(path, password_file=pw_file).password,
                         ENC_PASSWORD.encode())
        with mock.patch.dict(os.environ, {'RAW_IMAGE_TEST_PW': ENC_PASSWORD}):
            self.assertEqual(raw_image.cli_image_keys(
                path, password_env='RAW_IMAGE_TEST_PW').password, ENC_PASSWORD)
        with mock.patch.dict(os.environ, {'RAW_IMAGE_TEST_PW': 'not it'}):
            with self.assertRaisesRegex(ValueError, 'the password does not open locked.dmg'):
                raw_image.cli_image_keys(path, password_env='RAW_IMAGE_TEST_PW')
        with self.assertRaisesRegex(ValueError, 'RAW_IMAGE_TEST_UNSET_42 is not set'):
            raw_image.cli_image_keys(path, password_env='RAW_IMAGE_TEST_UNSET_42')
        with mock.patch.object(raw_image.sys, 'stdin', None):
            with self.assertRaisesRegex(ValueError, '--image_password_file or --image_password_env'):
                raw_image.cli_image_keys(path)

        class Terminal:
            @staticmethod
            def isatty():
                return True
        answers = iter(['wrong', ENC_PASSWORD])
        with mock.patch.object(raw_image.sys, 'stdin', Terminal()), \
                mock.patch.object(raw_image.getpass, 'getpass', lambda prompt: next(answers)), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            self.assertEqual(raw_image.cli_image_keys(path).password, ENC_PASSWORD)
        self.assertIn('That password does not open the image', err.getvalue())

    def test_a_damaged_encrypted_dmg_is_reported_not_asked_about_again(self):
        folder = tempfile.mkdtemp(prefix='raw_image_enc_bad_', dir=self.work)
        path = os.path.join(folder, 'damaged.dmg')
        with open(path, 'wb') as handle:
            handle.write(b'encrcdsa' + b'\x00' * 8192)
        # the reader is asked what the image opens with, and it refuses a damaged
        # header outright, so no password is asked for first
        self.assertFalse(raw_image.needs_password(path))
        with self.assertRaisesRegex(ValueError, 'damaged.dmg could not be opened: .*version 0'):
            with mock.patch.dict(os.environ, {'RAW_IMAGE_TEST_PW': ENC_PASSWORD}):
                raw_image.cli_image_keys(path, password_env='RAW_IMAGE_TEST_PW')

    def _ad_raw_set(self):
        """The NTFS fixture as a raw set of two files FTK Imager encrypted."""
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_ad_', dir=self.work)
        half = len(data) // 2 // 512 * 512
        plain = []
        for index, piece in enumerate((data[:half], data[half:]), start=1):
            plain.append(os.path.join(folder, f'plain.{index:03d}'))
            with open(plain[-1], 'wb') as handle:
                handle.write(piece)
        out = [os.path.join(folder, f'evidence.{index:03d}') for index in (1, 2)]
        return write_adcrypt(plain, out)

    def test_an_ad_encrypted_raw_set_reads_with_its_password_from_either_file(self):
        first, second = self._ad_raw_set()
        self.assertTrue(raw_image.needs_password(first))
        self.assertTrue(raw_image.needs_password(second))
        seeker = FileSeekerRaw(second, self.data, password=AD_PASSWORD)
        self.addCleanup(seeker.cleanup)
        text = self.log.text()
        self.assertIn('a raw (dd) image of 2 segments, joined by the reader: evidence.001 '
                      '.. evidence.002, encrypted (AES-256-CTR) and opened with its password',
                      text)
        self.assertNotIn('one segment of a split image', text)
        self.assertNotIn('segments joined in order', text)
        self.assertEqual(seeker.name_list, self._seeker(self.ntfs).name_list)
        for rel in ('many/file_0007.txt', 'many/file_0400.txt'):
            found = seeker.search(f'*/{rel}')
            self.assertEqual(_sha256(found[0]), self.ntfs_hashes[rel])
        self.assertNotIn(AD_PASSWORD, repr(vars(seeker)))

    def test_an_ad_encrypted_e01_set_reads_with_its_password(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_ad_e01_', dir=self.work)
        plain = write_ewf(folder, 'plain', data, chunks_per_segment=200)
        self.assertGreater(len(plain), 1)
        out = write_adcrypt(plain, [p.replace('plain.', 'evidence.') for p in plain])
        self.assertTrue(raw_image.needs_password(out[0]))
        seeker = FileSeekerRaw(out[0], self.data, password=AD_PASSWORD)
        self.addCleanup(seeker.cleanup)
        self.assertIn(f'an EWF acquisition of {len(out)} segments', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])

    def test_an_ad_encrypted_set_without_its_password_is_refused_as_such(self):
        first, _second = self._ad_raw_set()
        with self.assertRaises(qnxprobe.ImagePasswordError) as caught:
            FileSeekerRaw(first, self.data)
        self.assertFalse(caught.exception.wrong)
        with self.assertRaises(qnxprobe.ImagePasswordError) as caught:
            FileSeekerRaw(first, self.data, password='not it')
        self.assertTrue(caught.exception.wrong)
        with mock.patch.object(raw_image.sys, 'stdin', None):
            with self.assertRaisesRegex(ValueError, 'evidence.001 is an acquisition FTK Imager '
                                        'encrypted with AD encryption and opens only'):
                raw_image.cli_image_keys(first)
        with mock.patch.dict(os.environ, {'RAW_IMAGE_TEST_PW': AD_PASSWORD}):
            self.assertEqual(raw_image.cli_image_keys(
                first, password_env='RAW_IMAGE_TEST_PW').password, AD_PASSWORD)

    def test_a_damaged_l01_is_refused_by_the_logical_reader_not_read_as_a_disk(self):
        folder = tempfile.mkdtemp(prefix='raw_image_l01_', dir=self.work)
        path = os.path.join(folder, 'evidence.L01')
        with open(path, 'wb') as handle:
            handle.write(b'LVF\t\r\n\xff\x00' + b'\x00' * 4096)
        with self.assertRaises(ewfprobe.EwfError):
            FileSeekerRaw(path, self.data)

    def test_a_split_set_is_joined_from_any_one_segment(self):
        folder = tempfile.mkdtemp(prefix='raw_image_split_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        piece = 3 * 1024 * 1024
        for index, offset in enumerate(range(0, len(data), piece), start=1):
            with open(os.path.join(folder, f'ntfs.img.{index:03d}'), 'wb') as out:
                out.write(data[offset:offset + piece])
        first = os.path.join(folder, 'ntfs.img.001')
        self.assertEqual(split_image_sibling(first), os.path.join(folder, 'ntfs.img.002'))
        seeker = self._seeker(first)
        self.assertIn('segments joined in order', self.log.text())
        found = seeker.search('*/many/file_0400.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0400.txt'])

    def test_a_partitioned_disk_names_its_volume_by_partition_and_lba(self):
        folder = tempfile.mkdtemp(prefix='raw_image_mbr_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            disk = with_mbr(handle.read())
        image = os.path.join(folder, 'disk.img')
        with open(image, 'wb') as out:
            out.write(disk)
        seeker = self._seeker(image)
        self.assertEqual([v['name'] for v in seeker.volumes], ['p1_lba2048'])
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'p1_lba2048/many/file_0007.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertNotIn('WARNING', self.log.text())

    def test_a_lone_first_segment_warns_and_does_not_stage_a_cut_file(self):
        folder = tempfile.mkdtemp(prefix='raw_image_cut_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            disk = with_mbr(handle.read())
        cut = os.path.join(folder, 'disk.img.001')
        with open(cut, 'wb') as out:
            out.write(disk[:len(disk) // 2])
        seeker = self._seeker(cut)
        text = self.log.text()
        self.assertIn('WARNING: the image is shorter than the volumes it describes', text)
        self.assertIn('bytes past the end of the image', text)
        found = seeker.search('*')
        self.assertTrue(found)
        # whatever was staged is whole and correct; a file the cut runs through is
        # named in the log and never handed over
        for path in found:
            if os.path.isfile(path):
                rel = seeker.file_infos[path].source_path[len('p1_lba2048/'):]
                if rel in self.ntfs_hashes:
                    self.assertEqual(_sha256(path), self.ntfs_hashes[rel], rel)
        self.assertIn('Not staged', self.log.text())
        self.assertIn('the image ends before the file does', self.log.text())

    def test_a_file_whose_cluster_chain_ends_early_is_named_and_not_staged(self):
        # a.bin is two clusters stored as one run (NoFatChain). Clearing that
        # flag hands its allocation to the FAT, and one FAT entry marking the
        # end of the chain leaves it one cluster where its size needs two.
        # c.bin is untouched and is the control: it must still stage whole.
        with open(self.exfat, 'rb') as handle:
            volume = bytearray(handle.read())
        boot = struct.unpack_from('<IIIII', volume, 80)
        fat_offset, _fat_length, heap_offset, _clusters, root = boot
        sector = 1 << volume[108]
        cluster = sector << volume[109]
        at = heap_offset * sector + (root - 2) * cluster
        streams = [at + i for i in range(0, cluster, 32)
                   if volume[at + i] == 0xC0
                   and struct.unpack_from('<I', volume, at + i + 20)[0] == 13
                   and struct.unpack_from('<Q', volume, at + i + 24)[0] == 8192]
        self.assertEqual(len(streams), 1)
        stream = streams[0]
        self.assertEqual(volume[stream + 1], 0x03)
        volume[stream + 1] = 0x01
        struct.pack_into('<I', volume, fat_offset * sector + 13 * 4, 0xFFFFFFFF)
        # the set's checksum covers the flag, so it is written again
        first = stream - 32
        self.assertEqual(volume[first], 0x85)
        entries = volume[first:first + 32 * (volume[first + 1] + 1)]
        checksum = 0
        for index, byte in enumerate(entries):
            if index not in (2, 3):
                checksum = (((checksum << 15) | (checksum >> 1)) + byte) & 0xFFFF
        struct.pack_into('<H', volume, first + 2, checksum)
        folder = tempfile.mkdtemp(prefix='raw_image_chain_', dir=self.work)
        image = os.path.join(folder, 'exfat-cut-chain.img')
        with open(image, 'wb') as out:
            out.write(volume)
        seeker = self._seeker(image)
        seeker.search('*')
        staged = self._staged_by_source(seeker, 'lba0')
        self.assertNotIn('a.bin', staged)
        self.assertEqual(_sha256(staged['c.bin']), self.exfat_hashes['c.bin'])
        text = self.log.text()
        self.assertIn('Not staged, lba0/a.bin: the volume records 8,192 bytes for it and a '
                      'cluster chain that ends after 1 of the 2 clusters that size needs '
                      '(4,096 bytes read)', text)
        self.assertNotIn('the reader returned', text)
        self.assertEqual(text.count('Not staged'), 1)

    # ---- edges -------------------------------------------------------------------

    def test_an_image_the_reader_cannot_place_has_no_members(self):
        blank = os.path.join(self.work, 'blank.img')
        with open(blank, 'wb') as out:
            out.write(b'\x00' * (2 * 1024 * 1024))
        seeker = self._seeker(blank)
        self.assertEqual(seeker.name_list, [])
        self.assertEqual([v['kind'] for v in seeker.volumes], ['not recognised'])
        self.assertEqual(seeker.search('*'), [])

    def test_a_failed_build_releases_the_image(self):
        closed = []
        real_open = qnxprobe.open_image

        def spy_open(path, segments=None, password=None, private_key=None):
            handle = real_open(path, segments, password=password, private_key=private_key)
            original = handle.close
            handle.close = lambda: (closed.append(True), original())
            return handle

        with mock.patch.object(qnxprobe, 'open_image', spy_open), \
                mock.patch.object(qnxprobe, 'volumes', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                FileSeekerRaw(self.ntfs, self.data)
        self.assertEqual(closed, [True])

    def test_cleanup_closes_the_image(self):
        seeker = FileSeekerRaw(self.ntfs, self.data)
        seeker.cleanup()
        self.assertIsNone(seeker._image)  # pylint: disable=protected-access
        seeker.cleanup()  # a second call is harmless

    def test_the_reader_finds_its_ewf_module_when_imported_as_a_package(self):
        self.assertIs(sys.modules['ewfprobe'], ewfprobe)
        self.assertIs(qnxprobe.ewfprobe, ewfprobe)

    def test_a_socket_or_block_device_is_not_walked_as_a_directory(self):
        # S_IFDIR is 0o040000, and a socket (0o140000) and a block device
        # (0o060000) both carry that bit. Tested alone it lists them as
        # directories and descends into them; on a macOS APFS volume that was
        # 47 sockets under private/var listed as directories.
        class _Walker:
            root = 1
            children = {1: [('d', 2), ('sock', 3), ('blk', 4), ('f', 5)],
                        2: [('inner', 6)], 3: [('ghost', 7)], 4: [('ghost', 8)]}
            modes = {2: 0o040755, 3: 0o140755, 4: 0o060660, 5: 0o100644,
                     6: 0o100644, 7: 0o100644, 8: 0o100644}

            def listdir(self, node):
                return list(self.children.get(node, ()))

            def entry(self, node):
                return self.modes[node], 3, 0

        seeker = FileSeekerRaw.__new__(FileSeekerRaw)
        seeker.name_list, seeker._entries = [], {}  # pylint: disable=protected-access
        files, dirs, _streams, _route = seeker._walk(_Walker(), 'v')  # pylint: disable=protected-access
        self.assertEqual(sorted(seeker.name_list), ['v/d/', 'v/d/inner', 'v/f'])
        self.assertEqual((files, dirs), (2, 1))

    def test_the_filesystem_list_names_only_kinds_the_reader_walks(self):
        walkers = {'QNX6': qnxprobe.Qnx6Walker, 'QNX4': qnxprobe.Qnx4Walker,
                   'ETFS': qnxprobe.EtfsWalker, 'EFS': qnxprobe.EfsWalker,
                   'ext2/3/4': qnxprobe.ExtWalker, 'F2FS': qnxprobe.F2fsWalker,
                   'FAT32': qnxprobe.Fat32Walker, 'FAT16': qnxprobe.Fat16Walker,
                   'FAT12': qnxprobe.Fat12Walker,
                   'exFAT': qnxprobe.ExfatWalker, 'NTFS': qnxprobe.NtfsWalker,
                   'HFS+': qnxprobe.HfsPlusWalker, 'APFS': qnxprobe.ApfsWalker,
                   'SquashFS': qnxprobe.SquashfsWalker, 'JFFS2': qnxprobe.Jffs2Walker,
                   'UBI': qnxprobe.UbiWalker, 'UBIFS': qnxprobe.UbifsWalker,
                   'YAFFS': qnxprobe.YaffsWalker,
                   'QNX IFS': qnxprobe.IfsWalker,
                   'U-Boot environment': qnxprobe.ConfigStoreWalker,
                   'Belkin NVRM': qnxprobe.ConfigStoreWalker}
        names = [name.strip() for name in RAW_IMAGE_FILESYSTEMS.split(',')]
        self.assertEqual(sorted(names), sorted(walkers))
        for cls in walkers.values():
            for method in ('listdir', 'entry', 'read_file'):
                self.assertTrue(callable(getattr(cls, method)), f'{cls.__name__}.{method}')

    def test_gui_suffixes_cover_the_conventional_names(self):
        for suffix in ('img', 'dd', 'bin', 'raw', '001', 'e01', 's01', 'ex01', 'aff', 'dmg',
                       'sparseimage'):
            self.assertIn(suffix, RAW_IMAGE_SUFFIXES)
        self.assertNotIn('zip', RAW_IMAGE_SUFFIXES)


class SplitImageSiblingTest(unittest.TestCase):
    """A numbered suffix with the next number beside it is a split image."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='raw_image_sibling_')
        self.addCleanup(shutil.rmtree, self.folder, True)

    def touch(self, name):
        path = os.path.join(self.folder, name)
        with open(path, 'wb') as handle:
            handle.write(b'x')
        return path

    def test_first_segment_with_its_successor(self):
        first = self.touch('image.001')
        second = self.touch('image.002')
        self.assertEqual(split_image_sibling(first), second)

    def test_first_segment_alone_is_an_image(self):
        self.assertIsNone(split_image_sibling(self.touch('image.001')))

    def test_a_gap_is_not_a_successor(self):
        first = self.touch('image.001')
        self.touch('image.003')
        self.assertIsNone(split_image_sibling(first))

    def test_width_is_kept_across_the_carry(self):
        ninth = self.touch('image.009')
        tenth = self.touch('image.010')
        self.assertEqual(split_image_sibling(ninth), tenth)

    def test_a_conventional_extension_is_not_a_segment(self):
        image = self.touch('image.img')
        self.touch('image.002')
        self.assertIsNone(split_image_sibling(image))

    def test_an_e01_is_not_a_numbered_segment(self):
        self.assertIsNone(split_image_sibling(self.touch('image.E01')))

    def test_segments_of_unequal_size_are_refused_saying_what_to_do(self):
        # a middle segment cut short puts every byte after it at the wrong offset;
        # qnxprobe refuses the set and this tool, which has no option to join it
        # anyway, says to join the segments by hand
        for n, size in ((1, 4096), (2, 4096 - 512), (3, 1000)):
            with open(os.path.join(self.folder, f'disk.{n:03d}'), 'wb') as handle:
                handle.write(bytes(size))
        data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, data, True)
        with mock.patch.object(raw_image, 'logfunc', lambda *_a, **_k: None):
            with self.assertRaises(qnxprobe.SplitImageError) as caught:
                FileSeekerRaw(os.path.join(self.folder, 'disk.001'), data)
        message = str(caught.exception)
        self.assertIn('disk.002 is 3,584 bytes', message)
        self.assertIn('join the segments into one file in order', message)
        self.assertNotIn('--allow-unequal-segments', message)



# The files squashfs.src.sha256 lists for qnxprobe's SquashFS fixture, which its
# bitlocker-xts128 volume holds: 612 of them, and two of their SHA-256 written out
# (qnxprobe tests/fixtures/squashfs.src.sha256 at 2149e20).
BITLOCKER_FILES = 612
BITLOCKER_KNOWN = {
    'dir/holes.bin': 'f2d3dc968959b715c6abcbadb09ae78fdf1e3e24c73c19a54d148364e65149da',
    'dir/sub/deeper/deep.txt': '30cf6f2de471343739bcc1dde393c0c0771814ac3ad798f68c8a74495174521a',
}
BITLOCKER_PASSWORD = 'qnxprobe-bde-test'
BITLOCKER_RECOVERY = '111111-222222-333333-444444-555555-666666-000011-000022'
# qnxprobe's apfs-converted fixture (tools/make_apfs_converted_fixture.sh at a45821b):
# an APFS volume macOS encrypted in place, its password and the hint it stores, test
# values made for it.
APFS_PASSWORD = 'qnxprobe-apfs-convert'
APFS_HINT = 'the qnxprobe conversion test'
LUKS_PASSPHRASE = 'correct horse battery staple'     # the test value tools/make_luks_fixtures.sh in qnxprobe gives

try:
    import tkinter  # noqa: F401  pylint: disable=unused-import
    _HAS_TK = True
except ImportError:
    _HAS_TK = False


class _FakeDeleted:
    """What a flash reader's recover_deleted() yields, as far as the seeker reads it."""

    def __init__(self, name, parent_path, data, mtime=None, recoverable=True):
        self.name, self.parent_path, self.data = name, parent_path, data
        self.mtime, self.recoverable = mtime, recoverable


class _FakeFlashWalker:
    """A reader with the two methods the seeker asks a flash filesystem for."""

    def __init__(self, entries):
        self.entries, self.asked = entries, 0

    def recover_deleted(self):
        self.asked += 1
        yield from self.entries

    @staticmethod
    def read_deleted(entry):
        if entry.data is None:
            raise ValueError('the extent chain no longer resolves')
        yield entry.data


class _FakeLogicalEntry:
    """An L01 entry as ewfprobe gives it, for a folder that holds data too, which no
    small L01 fixture carries."""

    def __init__(self, path, data=b'', folder=False):
        self.names = tuple(path.split('/'))
        self.path = path
        self.name = self.names[-1]
        self.data = data
        self.size = len(data)
        self.is_folder = folder
        self.times = {'cr': 1_600_000_000, 'wr': 1_600_000_100}


class _FakeAd1Entry(_FakeLogicalEntry):
    """An AD1 entry with the type record FTK Imager stores."""

    def __init__(self, path, code, data=b'', folder=False, deleted=False, parent=None):
        super().__init__(path, data, folder)
        self.type_code = code
        self.is_deleted = deleted
        self.parent = parent
        self.times = {'created': 1_600_000_000, 'modified': 1_600_000_100}


class _FakeL01:
    format = ewfprobe.FORMAT_L01
    encryption = None

    def __init__(self, entries):
        self.logical_entries = entries

    @staticmethod
    def open_entry(entry):
        import io  # pylint: disable=import-outside-toplevel
        return io.BytesIO(entry.data)

    def close(self):
        pass


class KeysAndLogicalEvidenceTest(unittest.TestCase):
    """Logical evidence read as its files, and what opens encrypted images and
    BitLocker volumes, against readings written by other tools."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_keys_')
        cls.bitlocker = os.path.join(cls.work, 'bitlocker-xts128.img')
        with gzip.open(FIXTURES / 'bitlocker-xts128.img.gz', 'rb') as src, \
                open(cls.bitlocker, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        cls.bek = str(FIXTURES / 'bitlocker-xts128.BEK')
        cls.apfs = os.path.join(cls.work, 'apfs-converted.sparseimage')
        with gzip.open(FIXTURES / 'apfs-converted.sparseimage.gz', 'rb') as src, \
                open(cls.apfs, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        cls.apfs_hashes = _hash_list(FIXTURES / 'apfs-converted.sha256')
        # an RSA key of no certificate here, for the wrong-key cases
        from Crypto.PublicKey import RSA  # pylint: disable=import-outside-toplevel
        cls.stranger = os.path.join(cls.work, 'stranger.pem')
        with open(cls.stranger, 'wb') as handle:
            handle.write(RSA.generate(1024).export_key())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _seeker(self, image, keys=None):
        seeker = FileSeekerRaw(image, self.data, password=keys)
        self.addCleanup(seeker.cleanup)
        return seeker

    @staticmethod
    def _md5(path):
        with open(path, 'rb') as handle:
            return hashlib.md5(handle.read()).hexdigest()

    def test_the_file_dialog_patterns_cover_every_suffix(self):
        patterns = {p[2:].lower() for p in raw_image.RAW_IMAGE_FILE_PATTERNS.split()}
        self.assertEqual(patterns, set(RAW_IMAGE_SUFFIXES))

    def test_an_ad1_is_read_as_the_files_ftk_imager_listed(self):
        """Every live file and the alternate data stream in FTK Imager's own listing of
        the image (its .ad1.csv, stored MD5s) stages with that MD5; the entry it lists
        as deleted is not a member."""
        seeker = self._seeker(str(FIXTURES / 'lean-multi-ntfs-c9.ad1'))
        rows = (FIXTURES / 'lean-multi-ntfs-c9.ad1.csv').read_text(encoding='utf-16').splitlines()
        header = rows[0].strip().split('\t')
        listed = [dict(zip(header, row.strip().split('\t'))) for row in rows[1:] if row.strip()]
        files = [r for r in listed if r.get('Stored MD5 Hash')]
        self.assertEqual(len(files), 9)
        for row in files:
            name = row['Filename']
            if row['Full Path'].endswith(f'readme.txt\\{name}'):
                pattern = f'*readme.txt:{name}'           # the stream FTK lists under its file
            else:
                pattern = f'*/{name}'
            staged = seeker.search(pattern)
            if row['Is Deleted'] == 'yes':
                self.assertEqual(staged, [], name)
                continue
            self.assertEqual(len(staged), 1, name)
            self.assertEqual(self._md5(staged[0]), row['Stored MD5 Hash'], name)
        self.assertEqual(len(seeker.stream_list), 1)
        self.assertIn('  not searched: 1 deleted entries', self.log.text())

    def test_an_l01_folder_that_holds_data_stages_the_data_beside_its_children(self):
        entries = [_FakeLogicalEntry('Raw Data', folder=True),
                   _FakeLogicalEntry('Raw Data/prefs.plist', b'the plist itself', folder=True),
                   _FakeLogicalEntry('Raw Data/prefs.plist/Parsed', folder=True),
                   _FakeLogicalEntry('Raw Data/prefs.plist/Parsed/Date', b'2012-07-05')]
        with mock.patch.object(raw_image, 'open_logical', lambda path, keys=None: _FakeL01(entries)):
            seeker = self._seeker(os.path.join(self.work, 'evidence.L01'))
        self.assertIn('Raw Data/prefs.plist', seeker.name_list)
        self.assertIn('Raw Data/prefs.plist/', seeker.name_list)
        child = seeker.search('*/Parsed/Date')
        data = seeker.search('*/Raw Data/prefs.plist')
        self.assertEqual(open(child[0], 'rb').read(), b'2012-07-05')
        self.assertEqual(open(data[0], 'rb').read(), b'the plist itself')
        self.assertNotEqual(os.path.dirname(child[0]), data[0])
        self.assertEqual(seeker.file_infos[child[0]].creation_date, 1_600_000_000)
        self.assertEqual(os.path.getmtime(child[0]), 1_600_000_100)
        # the data asked for first still leaves room for the folder's children
        data_folder = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, data_folder, True)
        with mock.patch.object(raw_image, 'open_logical', lambda path, keys=None: _FakeL01(entries)):
            first = FileSeekerRaw(os.path.join(self.work, 'evidence.L01'), data_folder)
        self.addCleanup(first.cleanup)
        data = first.search('*/Raw Data/prefs.plist')
        child = first.search('*/Parsed/Date')
        self.assertEqual(open(data[0], 'rb').read(), b'the plist itself')
        self.assertEqual(open(child[0], 'rb').read(), b'2012-07-05')

    def test_two_l01_entries_at_one_path_both_reach_an_artifact(self):
        entries = [_FakeLogicalEntry('Root', folder=True),
                   _FakeLogicalEntry('Root/dir', folder=True),
                   _FakeLogicalEntry('Root/dir/a.db', b'FIRST-COPY'),
                   _FakeLogicalEntry('Root/dir/a.db', b'SECOND-COPY-X')]
        with mock.patch.object(raw_image, 'open_logical', lambda path, keys=None: _FakeL01(entries)):
            seeker = self._seeker(os.path.join(self.work, 'evidence.L01'))
        staged = seeker.search('*a.db')
        self.assertEqual(len(staged), 2)
        held = {os.path.basename(p): open(p, 'rb').read() for p in staged}
        # the later entry keeps the name, as before; the earlier is staged beside it
        self.assertEqual(held, {'a.db': b'SECOND-COPY-X', 'a~entry-2.db': b'FIRST-COPY'})
        self.assertEqual({seeker.file_infos[p].source_path for p in staged}, {'Root/dir/a.db'})
        self.assertIn('1 entries share their path with a later entry', self.log.text())

    def test_an_ad1_leaves_out_only_the_kinds_that_hold_no_file(self):
        """Measured on a 316,682-entry AD1: type 6 is file slack, F is $I30, 10 is $DSC
        and $TXF_DATA and 61 holds no data. Type 11 (OneDrive files among them) and a
        kind never measured are members, so a new kind is searched rather than lost."""
        root = _FakeAd1Entry('src', '3', folder=True)
        doc = _FakeAd1Entry('src/doc.pdf', '11', b'placeholder file', parent=root)
        entries = [root, doc,
                   _FakeAd1Entry('src/doc.pdf/Zone.Identifier', 'D', b'[ZoneTransfer]', parent=doc),
                   _FakeAd1Entry('src/new-kind.bin', '99', b'unmeasured', parent=root),
                   _FakeAd1Entry('src/doc.pdf.FileSlack', '6', b'slack', parent=root),
                   _FakeAd1Entry('src/$I30', 'F', b'index', parent=root),
                   _FakeAd1Entry('src/doc.pdf/$DSC', '10', b'dsc', parent=doc),
                   _FakeAd1Entry('src/gone.cat', '61', parent=root),
                   _FakeAd1Entry('src/deleted.txt', '1', b'x', deleted=True, parent=root)]
        image = _FakeL01(entries)
        image.format = ewfprobe.FORMAT_AD1
        with mock.patch.object(raw_image, 'open_logical', lambda path, keys=None: image):
            seeker = self._seeker(os.path.join(self.work, 'evidence.ad1'))
        self.assertEqual(seeker.name_list, ['src/', 'src/doc.pdf', 'src/new-kind.bin'])
        self.assertEqual(seeker.stream_list, ['src/doc.pdf:Zone.Identifier'])
        text = self.log.text()
        for left_out in ('1 file slack entries (type 6)', '1 NTFS directory index records',
                         '1 NTFS attribute records', '1 index entries that hold no data',
                         '1 deleted entries'):
            self.assertIn(f'not searched: {left_out}', text)

    def test_an_ad1_sealed_to_a_certificate_opens_with_its_private_key(self):
        image = str(FIXTURES / 'ftk-ad-cert-ad1.ad1')
        key = str(FIXTURES / 'ad-cert-test-key-2048.pem')
        self.assertTrue(raw_image.needs_private_key(image))
        self.assertFalse(raw_image.needs_password(image))
        with self.assertRaises(qnxprobe.ImagePasswordError) as caught:
            self._seeker(image)
        self.assertEqual(caught.exception.needs, 'private key')
        with self.assertRaisesRegex(ValueError, '--image_private_key'):
            raw_image.cli_image_keys(image)
        with self.assertRaisesRegex(ValueError, 'could not be read as an RSA key'):
            raw_image.cli_image_keys(image, private_key=str(FIXTURES / 'ftk-ad-cert-ad1.sha256'))
        with self.assertRaisesRegex(ValueError, '^the private key does not open'):
            raw_image.cli_image_keys(image, private_key=self.stranger)
        keys = raw_image.cli_image_keys(image, private_key=key)
        self.assertEqual(keys.private_key, key)
        seeker = self._seeker(image, keys)
        for name, digest in _hash_list(FIXTURES / 'ftk-ad-cert-ad1.sha256').items():
            staged = seeker.search(f'*/{name}')
            self.assertEqual(len(staged), 1, name)
            self.assertEqual(_sha256(staged[0]), digest, name)

    def _bitlocker_members(self, keys):
        data = tempfile.mkdtemp(prefix='raw_image_data_')     # one folder per seeker
        self.addCleanup(shutil.rmtree, data, True)
        seeker = FileSeekerRaw(self.bitlocker, data, password=keys)
        self.addCleanup(seeker.cleanup)
        files = [m for m in seeker.name_list if not m.endswith('/')]
        return seeker, files

    def test_a_bitlocker_volume_opens_with_its_password_recovery_password_or_startup_key(self):
        seeker, files = self._bitlocker_members(None)
        self.assertEqual(files, [])
        self.assertIn('BitLocker-encrypted and not read', self.log.text())
        listings = []
        for keys in (raw_image.ImageKeys(password=BITLOCKER_PASSWORD),
                     raw_image.ImageKeys(bitlocker_secrets=[BITLOCKER_RECOVERY]),
                     raw_image.ImageKeys(bitlocker_keys=[self.bek])):
            seeker, files = self._bitlocker_members(keys)
            self.assertEqual(len(files), BITLOCKER_FILES)
            for path, digest in BITLOCKER_KNOWN.items():
                staged = seeker.search(f'*/{path}')
                self.assertEqual(len(staged), 1, path)
                self.assertEqual(_sha256(staged[0]), digest, path)
            listings.append(files)
        self.assertEqual(listings[0], listings[1])
        self.assertEqual(listings[0], listings[2])
        _seeker, files = self._bitlocker_members(raw_image.ImageKeys(password='not it'))
        self.assertEqual(files, [])

    def test_the_command_line_takes_bitlocker_keys_and_says_what_stays_locked(self):
        recovery = os.path.join(self.work, 'recovery.txt')
        with open(recovery, 'w', encoding='utf-8') as handle:
            handle.write(BITLOCKER_RECOVERY + '\n')
        with mock.patch.object(raw_image.sys, 'stdin', None), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(self.bitlocker)
        self.assertIn('stays locked and its files are not searched', err.getvalue())
        self.assertIn('--bitlocker_key', err.getvalue())
        self.assertEqual(self._bitlocker_members(keys)[1], [])
        for kwargs in ({'password_file': recovery}, {'bitlocker_keys': [self.bek]}):
            with mock.patch.object(raw_image.sys, 'stdin', None), \
                    contextlib.redirect_stderr(__import__('io').StringIO()) as err:
                keys = raw_image.cli_image_keys(self.bitlocker, **kwargs)
            self.assertEqual(err.getvalue(), '')
            self.assertEqual(len(self._bitlocker_members(keys)[1]), BITLOCKER_FILES)

        class Terminal:
            @staticmethod
            def isatty():
                return True
        answers = iter(['not it', BITLOCKER_RECOVERY])
        with mock.patch.object(raw_image.sys, 'stdin', Terminal()), \
                mock.patch.object(raw_image.getpass, 'getpass', lambda prompt: next(answers)), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(self.bitlocker)
        self.assertEqual(keys.bitlocker_secrets, [BITLOCKER_RECOVERY])
        self.assertIn('That does not open it.', err.getvalue())

    def _apfs_members(self, keys):
        data = tempfile.mkdtemp(prefix='raw_image_data_')     # one folder per seeker
        self.addCleanup(shutil.rmtree, data, True)
        seeker = FileSeekerRaw(self.apfs, data, password=keys)
        self.addCleanup(seeker.cleanup)
        files = [m for m in seeker.name_list if not m.endswith('/')]
        return seeker, files

    def _assert_apfs_files(self, seeker):
        for rel, digest in self.apfs_hashes.items():
            staged = seeker.search(f'*/CONVVOL/{rel}')
            self.assertEqual(len(staged), 1, rel)
            self.assertEqual(_sha256(staged[0]), digest, rel)

    def test_an_encrypted_apfs_volume_opens_with_its_password(self):
        """Every file macOS recorded stages with its hash once the password is given,
        as the image's password or as an APFS one; without it, or with a wrong one, the
        volume is named locked with its hint and holds no members."""
        _seeker, files = self._apfs_members(None)
        self.assertEqual(files, [])
        self.assertIn('CONVVOL is encrypted, and its blocks are ciphertext', self.log.text())
        self.assertIn(f'its passphrase hint, as stored: "{APFS_HINT}"', self.log.text())
        for keys in (raw_image.ImageKeys(password=APFS_PASSWORD),
                     raw_image.ImageKeys(apfs_secrets=[APFS_PASSWORD])):
            seeker, files = self._apfs_members(keys)
            self.assertTrue(set(f'CONVVOL/{rel}' for rel in self.apfs_hashes)
                            <= {m.split('/', 1)[1] for m in files})
            self._assert_apfs_files(seeker)
        self.assertIn('CONVVOL is encrypted and was opened with a password', self.log.text())
        _seeker, files = self._apfs_members(raw_image.ImageKeys(password='not it'))
        self.assertEqual(files, [])

    def test_the_command_line_takes_an_apfs_password_and_says_what_stays_locked(self):
        password = os.path.join(self.work, 'apfs-password.txt')
        with open(password, 'w', encoding='utf-8') as handle:
            handle.write(APFS_PASSWORD + '\n')
        with mock.patch.object(raw_image.sys, 'stdin', None), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(self.apfs)
        self.assertIn('CONVVOL in ', err.getvalue())
        self.assertIn('stays locked and its files are not searched', err.getvalue())
        self.assertIn(APFS_HINT, err.getvalue())
        self.assertIn('--image_password_file', err.getvalue())
        self.assertEqual(self._apfs_members(keys)[1], [])
        with mock.patch.object(raw_image.sys, 'stdin', None), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(self.apfs, password_file=password)
        self.assertEqual(err.getvalue(), '')
        self._assert_apfs_files(self._apfs_members(keys)[0])

        class Terminal:
            @staticmethod
            def isatty():
                return True
        answers = iter(['not it', APFS_PASSWORD])
        prompts = []

        def getpass(prompt):
            prompts.append(prompt)
            return next(answers)
        with mock.patch.object(raw_image.sys, 'stdin', Terminal()), \
                mock.patch.object(raw_image.getpass, 'getpass', getpass), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(self.apfs)
        self.assertEqual(keys.apfs_secrets, [APFS_PASSWORD])
        self.assertIn('That does not open it.', err.getvalue())
        self.assertIn(APFS_HINT, prompts[0])

    @unittest.skipUnless(_HAS_TK, 'the GUI prompts need tkinter')
    def test_the_gui_asks_for_an_apfs_password(self):
        from tkinter import simpledialog  # pylint: disable=import-outside-toplevel
        answers = iter(['not it', APFS_PASSWORD])
        prompts = []

        def askstring(_title, prompt, **_kw):
            prompts.append(prompt)
            return next(answers)
        with mock.patch.object(simpledialog, 'askstring', askstring):
            keys = raw_image.ask_image_keys(None, self.apfs)
        self.assertEqual(keys.apfs_secrets, [APFS_PASSWORD])
        self.assertIn(APFS_HINT, prompts[0])
        self.assertTrue(prompts[1].startswith('That does not open it.'))
        with mock.patch.object(simpledialog, 'askstring', lambda *a, **kw: None):
            keys = raw_image.ask_image_keys(None, self.apfs)
        self.assertEqual(keys.apfs_secrets, [])

    def _luks_members(self, keys):
        data = tempfile.mkdtemp(prefix='raw_image_data_')     # one folder per seeker
        self.addCleanup(shutil.rmtree, data, True)
        image = os.path.join(self.work, 'luks1-cbc.img')
        if not os.path.exists(image):
            with gzip.open(FIXTURES / 'luks1-cbc.img.gz', 'rb') as src, open(image, 'wb') as dst:
                shutil.copyfileobj(src, dst)
        seeker = FileSeekerRaw(image, data, password=keys)
        self.addCleanup(seeker.cleanup)
        return seeker, image, [m for m in seeker.name_list if not m.endswith('/')]

    def test_a_luks_container_opens_with_its_passphrase(self):
        """A LUKS1 container cryptsetup wrote (qnxprobe's tests/fixtures): with its
        passphrase, as the image's password or as a LUKS one, every file of the ext4
        inside stages with the hash sha256sum recorded over the tree; without it, or
        with a wrong one, the container is named locked and holds no members."""
        hashes = _hash_list(FIXTURES / 'luks-fixture.sha256')
        _seeker, _image, files = self._luks_members(None)
        self.assertEqual(files, [])
        self.assertIn('LUKS-encrypted and not read: give its passphrase', self.log.text())
        for keys in (raw_image.ImageKeys(password=LUKS_PASSPHRASE),
                     raw_image.ImageKeys(luks_secrets=[LUKS_PASSPHRASE])):
            seeker, _image, files = self._luks_members(keys)
            for rel, digest in hashes.items():
                staged = seeker.search(f'*/{rel}')
                self.assertEqual(len(staged), 1, rel)
                self.assertEqual(_sha256(staged[0]), digest, rel)
        _seeker, _image, files = self._luks_members(raw_image.ImageKeys(password='not it'))
        self.assertEqual(files, [])

    def test_the_command_line_takes_a_luks_passphrase_and_says_what_stays_locked(self):
        _seeker, image, _files = self._luks_members(None)
        with mock.patch.object(raw_image.sys, 'stdin', None), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(image)
        self.assertIn('stays locked and its files are not searched', err.getvalue())
        self.assertIn('Give its passphrase with --image_password_file', err.getvalue())

        class Terminal:
            @staticmethod
            def isatty():
                return True
        answers = iter(['not it', LUKS_PASSPHRASE])
        prompts = []

        def getpass(prompt):
            prompts.append(prompt)
            return next(answers)
        with mock.patch.object(raw_image.sys, 'stdin', Terminal()), \
                mock.patch.object(raw_image.getpass, 'getpass', getpass), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            keys = raw_image.cli_image_keys(image)
        self.assertEqual(keys.luks_secrets, [LUKS_PASSPHRASE])
        self.assertIn('That does not open it.', err.getvalue())
        self.assertIn('is a LUKS container', prompts[0])

    # ---- what the command line says once something was given ----------------
    # As qnxprobe 1.72 does, which option takes what opens a volume is said only when
    # nothing was given; when something was and the volume stays locked, the reader's
    # own reason stands alone.

    def _cli_err(self, image, secret, **patches):
        wrong = os.path.join(self.work, 'wrong-secret.txt')
        with open(wrong, 'w', encoding='utf-8') as handle:
            handle.write(secret + '\n')
        with mock.patch.object(raw_image.sys, 'stdin', None), \
                contextlib.redirect_stderr(__import__('io').StringIO()) as err:
            if patches:
                with mock.patch.multiple(raw_image.qnxprobe, **patches):
                    raw_image.cli_image_keys(image, password_file=wrong)
            else:
                raw_image.cli_image_keys(image, password_file=wrong)
        return err.getvalue()

    def test_a_wrong_bitlocker_password_gives_the_reason_without_the_hint(self):
        err = self._cli_err(self.bitlocker, 'not it')
        self.assertIn('stays locked and its files are not searched', err)
        self.assertIn('none of the passwords or key files given opens it', err)
        self.assertNotIn('--bitlocker_key', err)
        self.assertNotIn('Give its', err)

    def test_a_wrong_apfs_password_gives_the_reason_without_the_hint(self):
        err = self._cli_err(self.apfs, 'not it')
        self.assertIn('stays locked and its files are not searched', err)
        self.assertIn('none of the passwords given opens it', err)
        self.assertNotIn('Give its', err)

    def test_a_wrong_luks_passphrase_gives_the_reason_without_the_hint(self):
        _seeker, image, _files = self._luks_members(None)
        err = self._cli_err(image, 'not it')
        self.assertIn('LUKS-encrypted and not read: no passphrase given opens a keyslot', err)
        self.assertNotIn('Give its', err)

    def test_a_luks_passphrase_that_cannot_be_tried_says_why(self):
        # Without pycryptodome the reader knows before any passphrase is tried that the
        # container cannot be read: given one, the command line says so, with no hint.
        _seeker, image, _files = self._luks_members(None)
        err = self._cli_err(image, LUKS_PASSPHRASE, _BDE_AES=None)
        self.assertIn('stays locked and its files are not searched (LUKS-encrypted and not '
                      'read: reading it needs the optional pycryptodome package', err)
        self.assertNotIn('Give its', err)

    @unittest.skipUnless(_HAS_TK, 'the GUI prompts need tkinter')
    def test_the_gui_asks_for_a_luks_passphrase(self):
        from tkinter import simpledialog  # pylint: disable=import-outside-toplevel
        _seeker, image, _files = self._luks_members(None)
        answers = iter(['not it', LUKS_PASSPHRASE])
        prompts = []

        def askstring(_title, prompt, **_kw):
            prompts.append(prompt)
            return next(answers)
        with mock.patch.object(simpledialog, 'askstring', askstring):
            keys = raw_image.ask_image_keys(None, image)
        self.assertEqual(keys.luks_secrets, [LUKS_PASSPHRASE])
        self.assertTrue(prompts[1].startswith('That does not open it.'))

    def test_an_lvm_physical_volume_offers_its_unallocated_extents(self):
        """A disk lvm2 made one whole physical volume (qnxprobe's tests/fixtures), whose
        extents start 3 MiB in, 1 MiB each, the one logical volume holding the first 8 of
        its 13: the other 5 are its free space, and staged they are those bytes of the
        disk."""
        image = os.path.join(self.work, 'lvm-wholedisk.img')
        with gzip.open(FIXTURES / 'lvm-wholedisk.img.gz', 'rb') as src, open(image, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        seeker = self._seeker(image)
        self.assertEqual(seeker.free_list,
                         ['lba0/$Unallocated/lvm-wholedisk.img.lba0.unallocated.bin'])
        staged = seeker.search('*.unallocated.bin')
        self.assertEqual(len(staged), 1)
        mib = 1 << 20
        with open(image, 'rb') as disk, open(staged[0], 'rb') as got:
            disk.seek(11 * mib)
            self.assertEqual(got.read(), disk.read(5 * mib))

    @unittest.skipUnless(_HAS_TK, 'the GUI prompts need tkinter')
    def test_a_password_given_for_one_of_several_images_is_tried_on_their_volumes(self):
        other = os.path.join(self.work, 'other.img')
        with open(other, 'wb') as handle:
            handle.write(b'\0' * 65536)
        keys = raw_image.ImageKeys()
        keys.per_image = {other: (BITLOCKER_PASSWORD, None), self.bitlocker: (None, None)}
        self.assertIn(BITLOCKER_PASSWORD, keys.bitlocker_passwords())
        data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, data, True)
        seeker = FileSeekerRaw([self.bitlocker, other], data, password=keys)
        self.addCleanup(seeker.cleanup)
        self.assertTrue([m for m in seeker.name_list if m.startswith('bitlocker_xts128_img_')])

    def test_the_gui_asks_for_a_private_key_and_a_bitlocker_startup_key(self):
        from tkinter import filedialog, messagebox, simpledialog  # pylint: disable=import-outside-toplevel
        image = str(FIXTURES / 'ftk-ad-cert-ad1.ad1')
        key = str(FIXTURES / 'ad-cert-test-key-2048.pem')
        picked = iter([str(FIXTURES / 'ftk-ad-cert-ad1.sha256'), self.stranger, key])
        errors = []
        with mock.patch.object(filedialog, 'askopenfilename', lambda **kw: next(picked)), \
                mock.patch.object(messagebox, 'showerror', lambda *a, **kw: errors.append(a)):
            keys = raw_image.ask_image_keys(None, image)
        self.assertEqual(keys.private_key, key)
        # the first file is not a key and the second is another certificate's; both
        # are said, and asked again
        self.assertEqual(len(errors), 2)
        self.assertIn('could not be read as an RSA key', errors[0][1])
        self.assertIn('That key does not open', errors[1][1])
        answers = iter(['not it', ''])
        with mock.patch.object(simpledialog, 'askstring', lambda *a, **kw: next(answers)), \
                mock.patch.object(filedialog, 'askopenfilename', lambda **kw: self.bek):
            keys = raw_image.ask_image_keys(None, self.bitlocker)
        self.assertEqual(keys.bitlocker_keys, [self.bek])
        with mock.patch.object(simpledialog, 'askstring', lambda *a, **kw: None):
            keys = raw_image.ask_image_keys(None, self.bitlocker)
        self.assertEqual((keys.bitlocker_keys, keys.bitlocker_secrets), ([], []))


# The volume Windows 11 wrote (qnxprobe tools/make_ntfs_windows_fixture.cmd) and what
# Windows reported for each of its files. The folder names are the script's: five files
# under each of wof/xpress4k, wof/xpress8k, wof/xpress16k and wof/lzx, and four under
# CloudRoot, three of them placeholders written through the Cloud Files API.
WINDOWS_VOLUME = 'p1_lba128'
WINDOWS_FILES = 35
WINDOWS_HASHED = 27
WINDOWS_PLACEHOLDERS = ('CloudRoot/online_only_doc.pdf', 'CloudRoot/online_only_photo.jpg',
                        'CloudRoot/online_only_video.mp4')


def _windows_known(path):
    """{path: (length, size on disk, sha256 or '-', 'read' or 'refused')}."""
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        rel, length, _attributes, disk, digest, windows = line.split('\t')
        out[rel] = (int(length), int(disk), digest, windows)
    return out


class WindowsWrittenVolumeTest(unittest.TestCase):
    """What the image does not hold is not staged, and what it holds compressed is read."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_windows_')
        cls.image = os.path.join(cls.work, 'ntfs-windows.img')
        with gzip.open(FIXTURES / 'ntfs-windows.img.gz', 'rb') as src, \
                open(cls.image, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        cls.known = _windows_known(FIXTURES / 'ntfs-windows.known.tsv')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.seeker = FileSeekerRaw(self.image, self.data)
        self.addCleanup(self.seeker.cleanup)

    def _staged(self):
        prefix = WINDOWS_VOLUME + '/'
        return {info.source_path[len(prefix):]: path
                for path, info in self.seeker.file_infos.items()
                if info.source_path.startswith(prefix) and not info.source_path.endswith('/')}

    def _files_on_disk(self):
        return sum(len(files) for _root, _dirs, files in os.walk(self.data))

    def test_the_manifest_is_the_one_windows_wrote(self):
        self.assertEqual([v['name'] for v in self.seeker.volumes], [WINDOWS_VOLUME])
        self.assertEqual(len(self.known), WINDOWS_FILES)
        refused = sorted(rel for rel, row in self.known.items() if row[3] == 'refused')
        self.assertEqual(refused, sorted(WINDOWS_PLACEHOLDERS))

    def test_every_file_windows_hashed_is_staged_to_the_same_bytes(self):
        # plain, resident, sparse, NTFS compressed, a cloud file that is all there, and
        # the fifteen overlay-compressed with XPRESS, which were zeros before 1.56
        self.seeker.search('*')
        staged = self._staged()
        hashed = {rel: row for rel, row in self.known.items()
                  if row[3] == 'read' and not rel.startswith('wof/lzx/')}
        self.assertEqual(len(hashed), WINDOWS_HASHED)
        self.assertEqual(sorted(set(hashed) - set(staged)), [])
        differ = [rel for rel, row in hashed.items()
                  if os.path.getsize(staged[rel]) != row[0] or _sha256(staged[rel]) != row[2]]
        self.assertEqual(differ, [])
        xpress = [rel for rel in hashed if rel.startswith('wof/xpress')]
        self.assertEqual(len(xpress), 15)
        for rel in xpress:
            with open(staged[rel], 'rb') as handle:
                self.assertTrue(any(handle.read()), f'{rel} was staged as zeros')

    def test_a_cloud_placeholder_is_not_staged_and_the_log_says_why(self):
        # a name with a dot in it: the folder itself is a member too, and is not wanted
        found = self.seeker.search('*/CloudRoot/*.*')
        self.assertEqual([self.seeker.file_infos[path].source_path for path in found],
                         [f'{WINDOWS_VOLUME}/CloudRoot/hydrated_100000.txt'])
        self.assertEqual(self._files_on_disk(), 1)
        text = self.log.text()
        for rel in WINDOWS_PLACEHOLDERS:
            self.assertIn(f'Not staged, {WINDOWS_VOLUME}/{rel}: ', text)
            self.assertFalse(os.path.exists(os.path.join(self.data, WINDOWS_VOLUME, rel)))
        self.assertEqual(text.count('online-only placeholder'), 3)
        # the size Windows recorded for the largest, and that none of it is stored
        self.assertIn('it records 52,428,800 bytes and the volume stores 0 of them', text)

    def test_a_placeholder_matched_by_a_media_pattern_writes_nothing(self):
        # the shape of the patterns that reach a photo or a video anywhere on a volume
        self.assertEqual(self.seeker.search('*.[mM][pP]4'), [])
        self.assertEqual(self.seeker.search('*/online_only_photo.[jJ][pP][gG]'), [])
        self.assertEqual(self._files_on_disk(), 0)

    def test_a_file_compressed_with_lzx_is_not_staged_as_zeros(self):
        self.assertEqual(self.seeker.search('*/wof/lzx/*.*'), [])
        self.assertEqual(self._files_on_disk(), 0)
        self.assertEqual(self.log.text().count('overlay-compressed with LZX'), 5)

    def test_a_sparse_file_is_staged_at_its_recorded_size(self):
        # holes are written as zeros: the copy is the file Windows read, and larger on
        # disk than the 131,072 bytes the volume stores for it
        found = self.seeker.search('*/sparse/both_ends.bin')
        self.assertEqual(len(found), 1)
        length, disk, digest, _windows = self.known['sparse/both_ends.bin']
        self.assertEqual((length, disk), (8388608, 131072))
        self.assertEqual(os.path.getsize(found[0]), length)
        self.assertEqual(_sha256(found[0]), digest)

    def test_the_reader_says_what_each_file_stores(self):
        entries = self.seeker._entries           # pylint: disable=protected-access
        report = {}
        for rel in self.known:
            entry = entries[f'{WINDOWS_VOLUME}/{rel}']
            report[rel] = qnxprobe.allocation(entry.walker, entry.node)
        self.assertEqual(sorted(rel for rel, got in report.items() if got['placeholder']),
                         sorted(WINDOWS_PLACEHOLDERS))
        self.assertEqual(report['sparse/both_ends.bin']['stored'], 131072)
        self.assertEqual(report['sparse/all_hole.bin']['stored'], 0)
        self.assertFalse(report['sparse/all_hole.bin']['placeholder'])
        self.assertEqual(report['wof/xpress8k/text_100000.txt']['compression'], 'wof-xpress8k')
        self.assertEqual(report['lznt1/text_100000.txt']['compression'], 'lznt1')
        self.assertFalse(report['CloudRoot/hydrated_100000.txt']['placeholder'])


class CompressionUnitThatStopsEarlyTest(unittest.TestCase):
    """An NTFS-compressed file is staged whole when one of its units ends early."""

    # lznt1/text_100000.txt on the Windows-written volume is two compression units, each
    # stored in two clusters. The second begins at cluster 1548 of the volume, and the
    # volume at byte 65,536 of the image. Windows wrote f7 b1 there, the unit's first
    # chunk header.
    SECOND_UNIT = 65536 + 1548 * 4096
    # The file with its second unit read as zeros: its first 65,536 bytes, then 34,464
    # zeros. The Sleuth Kit 4.15.0 (icat) read the same changed image to this digest.
    EXPECTED = '2178bd1ed448997552310b525dd2f83a6049978b291fe6afd0f8cb4ee2cc40b1'

    def setUp(self):
        self.work = tempfile.mkdtemp(prefix='raw_image_lznt1_')
        self.addCleanup(shutil.rmtree, self.work, True)
        with gzip.open(FIXTURES / 'ntfs-windows.img.gz', 'rb') as src:
            image = bytearray(src.read())
        self.assertEqual(bytes(image[self.SECOND_UNIT:self.SECOND_UNIT + 2]), b'\xf7\xb1')
        image[self.SECOND_UNIT:self.SECOND_UNIT + 2] = b'\x00\x00'
        self.image = os.path.join(self.work, 'ntfs-windows-short-unit.img')
        with open(self.image, 'wb') as dst:
            dst.write(image)
        self.data = os.path.join(self.work, 'data')
        os.makedirs(self.data)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.seeker = FileSeekerRaw(self.image, self.data)
        self.addCleanup(self.seeker.cleanup)

    def test_a_unit_that_ends_at_a_zero_header_is_staged_as_zeros_to_its_end(self):
        found = self.seeker.search('*/lznt1/text_100000.txt')
        self.assertEqual(len(found), 1, self.log.text())
        self.assertEqual(os.path.getsize(found[0]), 100000)
        self.assertEqual(_sha256(found[0]), self.EXPECTED)


if __name__ == '__main__':
    unittest.main()


# ---- several images read together: the members of a RAID set --------------------

RAID_FIXTURES = FIXTURES / 'raid'
# Each set's member images, and the tree its array was built from (raid-trees.sha256,
# hashed from the files before mdadm or lvm2 held them).
RAID_SETS = {'md-r1': 2, 'md-r1-090': 2, 'md-r5-ls': 4, 'md-r5ls-090': 4, 'lvm-raid-multi': 5}
LVM_TREES = {'lvm_qpraid2_r5': 'lvm-raid-multi-r5', 'lvm_qpraid2_r6': 'lvm-raid-multi-r6',
             'lvm_qpraid2_r10': 'lvm-raid-multi-r10'}


def _raid_trees():
    """{tree: {path within the tree: sha256}} from raid-trees.sha256."""
    trees = {}
    for rel, digest in _hash_list(RAID_FIXTURES / 'raid-trees.sha256').items():
        tree, _slash, inner = rel.partition('/')
        trees.setdefault(tree, {})[inner] = digest
    return trees


class RaidMembersTest(unittest.TestCase):
    """Several images read together as the RAID arrays they are members of, against
    the trees the arrays were built from; the members found beside one of them; and
    one ordinary image read exactly as before."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_raid_')
        cls.sets = {}
        for stem, count in RAID_SETS.items():
            folder = os.path.join(cls.work, stem)
            os.makedirs(folder)
            cls.sets[stem] = []
            for number in range(count):
                path = os.path.join(folder, f'{stem}-{number}.img')
                with gzip.open(RAID_FIXTURES / f'{stem}-{number}.img.gz', 'rb') as src, \
                        open(path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                cls.sets[stem].append(path)
        cls.trees = _raid_trees()
        cls.ntfs = os.path.join(cls.work, 'ntfs-fixture.img')
        with gzip.open(FIXTURES / 'ntfs-fixture.img.gz', 'rb') as src, \
                open(cls.ntfs, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _seeker(self, paths, found=None):
        seeker = FileSeekerRaw(paths, self.data, found=found)
        self.addCleanup(seeker.cleanup)
        return seeker

    @staticmethod
    def _files_of(seeker, name):
        """{path within the volume: sha256} of every file staged from the volumes whose
        name starts with ``name``_."""
        out = {}
        for staged, info in seeker.file_infos.items():
            volume, _slash, rel = info.source_path.partition('/')
            if volume.startswith(name + '_') and rel and not rel.endswith('/'):
                out[rel] = _sha256(staged)
        return out

    def _arrays_read(self, seeker):
        return [arr for arr in seeker.raid.arrays if arr.image is not None]

    def test_each_set_reads_to_the_tree_its_array_was_built_from(self):
        for stem in ('md-r1', 'md-r5-ls', 'md-r5ls-090', 'lvm-raid-multi'):
            with self.subTest(stem):
                self.data = tempfile.mkdtemp(prefix='raw_image_data_')
                self.addCleanup(shutil.rmtree, self.data, True)
                seeker = self._seeker(self.sets[stem])
                self.assertTrue(seeker.search('*'))
                arrays = self._arrays_read(seeker)
                self.assertEqual(len(arrays), 3 if stem.startswith('lvm') else 1)
                for arr in arrays:
                    tree = LVM_TREES.get(arr.safe_name, stem)
                    self.assertEqual(self._files_of(seeker, arr.safe_name), self.trees[tree])

    def test_a_raid5_missing_one_member_is_rebuilt_from_parity(self):
        paths = [path for number, path in enumerate(self.sets['md-r5-ls']) if number != 2]
        seeker = self._seeker(paths)
        seeker.search('*')
        (arr,) = self._arrays_read(seeker)
        self.assertEqual(arr.missing, [2])
        self.assertEqual(self._files_of(seeker, arr.safe_name), self.trees['md-r5-ls'])

    def test_a_raid1_member_that_starts_with_the_filesystem_is_read_once_from_itself(self):
        # metadata 0.90 keeps its superblock at the end, so each member starts with the
        # filesystem itself. The reader marks such an array "not read again"; the first
        # member's own volume is read, the second member's copy is not, the array is not
        seeker = self._seeker(self.sets['md-r1-090'])
        (arr,) = self._arrays_read(seeker)
        self.assertEqual(arr.same_as, 'md-r1-090-0.img')
        walked = sorted({member.split('/', 1)[0] for member in seeker.name_list})
        self.assertEqual(walked, ['md_r1_090_0_img_lba0_md_r1_090'])
        copy = [vol for vol in seeker.volumes if vol['name'].startswith('md_r1_090_1_img_')]
        self.assertIsNone(copy[0]['walker'])
        self.assertIn('of what md-r1-090-0.img holds, which is read there', copy[0]['note'])
        self.assertNotIn(f'Volumes of {arr.label}', self.log.text())
        seeker.search('*')
        self.assertEqual(self._files_of(seeker, 'md_r1_090_0_img'), self.trees['md-r1-090'])

    def test_a_raid1_member_that_starts_with_the_filesystem_alone_reads_as_before(self):
        seeker = self._seeker(self.sets['md-r1-090'][1])
        self.assertIsNotNone(seeker.raid)
        self.assertEqual([vol['name'] for vol in seeker.volumes], ['lba0_md_r1_090'])
        seeker.search('*')
        self.assertEqual(self._files_of(seeker, 'lba0'), self.trees['md-r1-090'])

    def test_one_member_alone_reads_what_its_level_allows(self):
        seeker = self._seeker(self.sets['md-r1'][0])
        (arr,) = self._arrays_read(seeker)
        seeker.search('*')
        self.assertEqual(self._files_of(seeker, arr.safe_name), self.trees['md-r1'])
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        lone = self._seeker(self.sets['md-r5-ls'][0])
        self.assertEqual(self._arrays_read(lone), [])
        self.assertEqual(lone.name_list, [])
        self.assertIn('not read from the images given', self.log.text())

    def test_the_raid_report_names_no_option_this_tool_does_not_have(self):
        # One RAID5 member alone: the reader's heading counts no array as assembled, and
        # its hint, which names its own --find-members, is not given (this tool's own
        # search beside one image runs before the read unless turned off).
        self._seeker(self.sets['md-r5-ls'][0])
        text = self.log.text()
        self.assertIn('RAID: 1 array(s) or spanned volume(s) found in the images given, '
                      '0 of them assembled', text)
        self.assertIn('not read from the images given', text)
        self.assertNotIn('--find-members', text)

    def test_two_images_that_share_a_file_name_are_told_apart_in_the_raid_report(self):
        # Two members of one RAID5 under one file name in two folders: the reader's
        # RAID section names each by the folder that tells them apart, the array reads
        # to its tree, and the volume names keep the file name, told apart by number.
        paths = list(self.sets['md-r5-ls'])
        for side, member in (('left', 0), ('right', 1)):
            folder = os.path.join(self.work, f'share-{side}')
            os.makedirs(folder, exist_ok=True)
            paths[member] = os.path.join(folder, 'member.img')
            shutil.copy(self.sets['md-r5-ls'][member], paths[member])
        seeker = self._seeker(paths)
        text = self.log.text()
        for role, side in enumerate(('left', 'right')):
            self.assertIn(f"role {role}: {os.path.join(f'share-{side}', 'member.img')} (", text)
        (arr,) = self._arrays_read(seeker)
        self.assertEqual(arr.missing, [])
        seeker.search('*')
        self.assertEqual(self._files_of(seeker, arr.safe_name), self.trees['md-r5-ls'])
        names = [vol['name'] for vol in seeker.volumes]
        self.assertTrue(any(name.startswith('member_img_lba') for name in names), names)
        self.assertTrue(any(name.startswith('member_img_2_lba') for name in names), names)

    def test_a_split_set_whose_segments_begin_as_disks_is_warned_about(self):
        # Four RAID5 member images named like one split image are joined as one image by
        # their names; the run log carries the reader's warning that its later segments
        # begin as disks do.
        folder = os.path.join(self.work, 'numbered-members')
        os.makedirs(folder, exist_ok=True)
        numbered = []
        for number, member in enumerate(self.sets['md-r5-ls'], start=1):
            numbered.append(os.path.join(folder, f'm.{number:03d}'))
            shutil.copy(member, numbered[-1])
        self._seeker(numbered[0])
        text = self.log.text()
        self.assertIn('WARNING  later segments of this split set begin as a disk does: '
                      'm.002 (an md superblock)', text)
        self.assertIn('give copies named otherwise (such as m-1.img, m-2.img)', text)

    def test_a_partial_array_read_without_the_search_says_how_to_give_the_rest(self):
        # One RAID5 member with the search turned off (as --no-find-members, or the
        # window's "Only the file I picked"): the run log names the roles not given and
        # how to give them; with two members given, member finding is not named.
        self._seeker(self.sets['md-r5-ls'][0])
        text = self.log.text()
        self.assertIn('qp:qp21: role(s) 1, 2, 3 of 4 are not in the images given. Give the '
                      'other member images with it (several paths to -i, or several files '
                      'picked together), or leave member finding on to look for them beside '
                      'the image given.', text)
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log.lines.clear()
        self._seeker(self.sets['md-r5-ls'][:2])
        text = self.log.text()
        self.assertIn('role(s) 2, 3 of 4 are not in the images given. Give the other member '
                      'images with it (several paths to -i, or several files picked '
                      'together).', text)
        self.assertNotIn('member finding', text)
        # the members found beside it and not taken ("Only the file I picked")
        search = raw_image.find_members(self.sets['md-r5-ls'][0])
        search.used = False
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log.lines.clear()
        self._seeker(self.sets['md-r5-ls'][0], found=search)
        self.assertIn('or leave member finding on to look for them beside the image given.',
                      self.log.text())

    def test_an_ordinary_image_is_read_exactly_as_before(self):
        seeker = self._seeker(self.ntfs)
        self.assertIsNone(seeker.raid)
        self.assertEqual([v['name'] for v in seeker.volumes], ['lba0'])
        self.assertTrue(all(member.startswith('lba0/') for member in seeker.name_list))
        self.assertNotIn('RAID', self.log.text())
        self.assertTrue(self.log.lines[0].startswith('Reading ntfs-fixture.img in place'))

    def test_the_run_log_names_each_image_and_marks_the_ones_found(self):
        paths = self.sets['md-r5-ls']
        self._seeker(paths, found=paths[1:])
        text = self.log.text()
        self.assertIn(f'Image 1 of 4: md-r5-ls-0.img (given), {paths[0]}', text)
        self.assertIn(f'Image 4 of 4: md-r5-ls-3.img (found automatically), {paths[3]}', text)
        self.assertIn('read below as md_qp_qp21_3090d8cb', text)

    def test_volume_names_start_with_what_holds_them_and_never_collide(self):
        seeker = self._seeker(self.sets['lvm-raid-multi'])
        names = [vol['name'] for vol in seeker.volumes]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn('lvm_qpraid2_r5_lba0_lvm_raid_multi_r', names)
        self.assertIn('lvm_raid_multi_0_img_lba0', names)
        # the free space of each physical volume is named after its image
        self.assertIn('lvm_raid_multi_0_img_lba0/$Unallocated/lvm-raid-multi-0.img.'
                      'lvm_raid_multi_0_img_lba0.unallocated.bin', seeker.free_list)

    def test_a_physical_volume_s_line_says_where_its_group_is_read(self):
        self._seeker(self.sets['lvm-raid-multi'])
        lines = [line for line in self.log.lines if line.startswith('  lvm_raid_multi_0_img_lba0 ')]
        self.assertEqual(len(lines), 1)
        self.assertIn('lvm2 pv', lines[0])
        self.assertTrue(lines[0].endswith('; read across the images given: r5 as lvm_qpraid2_r5, '
                                          'r6 as lvm_qpraid2_r6, r10 as lvm_qpraid2_r10)'),
                        lines[0])
        # read alone, the same image's line is the reader's note as before
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log.lines.clear()
        self._seeker(self.sets['lvm-raid-multi'][0])
        self.assertNotIn('read across the images given', self.log.text())

    # ---- one disk given twice -------------------------------------------------

    def _ntfs_entries(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        return list(self._seeker(self.ntfs).name_list)

    def _read_once(self, paths, kept, said='Given twice: '):
        alone = self._ntfs_entries()
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log.lines.clear()
        seeker = self._seeker(paths)
        self.assertEqual(seeker.image_paths, [kept])
        self.assertEqual(seeker.name_list, alone)
        self.assertIn(said, self.log.text())
        return seeker

    def test_the_same_file_given_twice_or_by_two_names_is_read_once(self):
        folder = tempfile.mkdtemp(prefix='raw_image_twice_', dir=self.work)
        link = os.path.join(folder, 'hard.img')
        os.link(self.ntfs, link)
        soft = os.path.join(folder, 'soft.img')
        os.symlink(self.ntfs, soft)
        relative = os.path.relpath(self.ntfs)
        for paths in ([self.ntfs, self.ntfs], [self.ntfs, link], [self.ntfs, soft],
                      [self.ntfs, relative]):
            with self.subTest(paths=[os.path.basename(p) for p in paths]):
                self._read_once(paths, self.ntfs)

    def test_two_segments_of_one_split_set_are_read_once(self):
        folder = tempfile.mkdtemp(prefix='raw_image_split_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        half = len(data) // 2
        for number, piece in ((1, data[:half]), (2, data[half:])):
            with open(os.path.join(folder, f'disk.img.{number:03d}'), 'wb') as handle:
                handle.write(piece)
        first, second = (os.path.join(folder, f'disk.img.{n:03d}') for n in (1, 2))
        # a later file of the set is named as a segment of it, not as the same disk
        self._read_once([first, second], first,
                        f'Given too: {second} is read as a segment of the split set opened '
                        f'from {first}, not on its own.')
        # and one image cut in two is not warned about as separate disks
        self.assertNotIn('later segments of this split set', self.log.text())

    def test_two_segments_of_one_ewf_set_are_read_once(self):
        folder = tempfile.mkdtemp(prefix='raw_image_ewf_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            segments = write_ewf(folder, 'disk', handle.read(), chunks_per_segment=200)
        self.assertGreater(len(segments), 1)
        alone = self._ntfs_entries()
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        seeker = self._seeker(segments[:2])
        self.assertEqual(seeker.image_paths, [segments[0]])
        self.assertEqual(seeker.name_list, alone)
        self.assertIn(f'Given too: {segments[1]} is read as a segment of the EWF set opened '
                      f'from {segments[0]}, not on its own.', self.log.text())

    def test_the_command_line_says_an_image_given_twice_and_the_report_names_it(self):
        said = []
        raw = raw_image.cli_raw_input([self.ntfs, self.ntfs], say=said.append)
        self.assertEqual((raw.paths, raw.input_path), ([self.ntfs], self.ntfs))
        self.assertEqual(said, [f'Given twice: {self.ntfs} is the same disk as {self.ntfs}, '
                                'read once.'])
        self.assertIn('is the same disk as', raw_image.input_text(raw.input_path, raw))
        self._seeker(raw.input_path, found=raw)
        self.assertIn('Given twice: ', self.log.lines[0])

    def test_the_window_says_an_image_picked_twice(self):
        from tkinter import messagebox  # pylint: disable=import-outside-toplevel
        shown = []
        with mock.patch.object(messagebox, 'showinfo', lambda *a, **kw: shown.append(a)):
            raw = raw_image.ask_raw_input(None, [self.ntfs, self.ntfs])
        self.assertEqual(raw.paths, [self.ntfs])
        self.assertIn('is the same disk as', shown[0][1])

    def test_two_different_disks_with_one_name_get_their_own_prefixes(self):
        paths = []
        for side in ('one', 'two'):
            folder = os.path.join(self.work, f'same-name-{side}')
            os.makedirs(folder, exist_ok=True)
            paths.append(os.path.join(folder, 'disk.img'))
            shutil.copy(self.ntfs, paths[-1])
        alone = self._ntfs_entries()
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        seeker = self._seeker(paths)
        self.assertEqual([vol['name'] for vol in seeker.volumes], ['disk_img_lba0', 'disk_img_2_lba0'])
        self.assertEqual(len(seeker.name_list), 2 * len(alone))
        self.assertEqual(len(set(seeker.name_list)), 2 * len(alone))

    # ---- when the search runs, and what it leaves on record ---------------------

    def test_a_one_disk_volume_group_is_not_searched_beside(self):
        image = os.path.join(self.work, 'lvm-wholedisk.img')
        with gzip.open(FIXTURES / 'lvm-wholedisk.img.gz', 'rb') as src, open(image, 'wb') as dst:
            shutil.copyfileobj(src, dst)
        said = []
        self.assertIsNone(raw_image.find_members(image))
        raw = raw_image.cli_raw_input(image, say=said.append)
        self.assertEqual((raw.paths, raw.search, said), ([image], None, []))

    def test_the_examiner_s_choice_reaches_the_run_log_and_the_report(self):
        folder = self._decoyed_folder()
        start = os.path.join(folder, 'md-r5-ls-0.img')
        raw = raw_image.ask_raw_input(None, start, confirm=lambda _parent, _search: 'only')
        self._seeker(raw.input_path, found=raw)
        text = self.log.text()
        self.assertIn('the examiner chose to read only md-r5-ls-0.img', text)
        self.assertIn('not used  other-array.img', text)
        self.assertIn('the examiner chose to read only md-r5-ls-0.img',
                      raw_image.input_text(raw.input_path, raw))

    def test_a_search_that_finds_nothing_is_on_record(self):
        folder = tempfile.mkdtemp(prefix='raw_image_alone_', dir=self.work)
        start = os.path.join(folder, 'md-r1-0.img')
        shutil.copy(self.sets['md-r1'][0], start)
        said = []
        raw = raw_image.cli_raw_input(start, say=said.append)
        self.assertEqual(raw.paths, [start])
        self.assertIn('no other member was found beside it', said[-1])
        self._seeker(raw.input_path, found=raw)
        self.assertIn('no other member was found beside it', self.log.text())
        self.assertIn('no other member was found beside it', raw_image.input_text(start, raw))

    def test_several_images_given_are_not_searched_beside(self):
        folder = self._decoyed_folder()
        paths = [os.path.join(folder, f'md-r5-ls-{n}.img') for n in (0, 1)]
        said = []
        raw = raw_image.cli_raw_input(paths, say=said.append)
        self.assertEqual((raw.paths, raw.search, said), (paths, None, []))

    def test_logical_evidence_is_refused_before_anything_is_read(self):
        ad1 = str(FIXTURES / 'lean-multi-ntfs-c9.ad1')
        self.assertEqual(raw_image.logical_among([self.ntfs, ad1]), ad1)
        self.assertIsNone(raw_image.logical_among([ad1]))
        with self.assertRaisesRegex(ValueError, 'is logical evidence'):
            raw_image.cli_raw_input([self.ntfs, ad1], say=lambda _line: None)

    def test_two_volume_groups_with_one_name_are_told_apart_on_each_physical_volume(self):
        # the same five disks again under another volume group id, as qnxprobe's own
        # self-test makes them (1.71): every checksum good, the group name unchanged
        first = self.sets['lvm-raid-multi']
        pv0 = qnxprobe._lvm_pv(open(first[0], 'rb'), 0, None)  # pylint: disable=protected-access
        group = pv0.vg[1]
        ids = [group['id']] + [rec['id'] for rec in group['physical_volumes'].values()]

        def flip(text):
            return ('B' if text[0] != 'B' else 'C') + text[1:]

        def renamed(text):
            for one in ids:
                text = text.replace(one, flip(one))
            return text

        folder = tempfile.mkdtemp(prefix='raw_image_twin_groups_', dir=self.work)
        second = []
        for number, path in enumerate(first):
            with open(path, 'rb') as handle:
                data = bytearray(qnxprobe._lvm_text_change(handle.read(), renamed))  # pylint: disable=protected-access
            pv = qnxprobe._lvm_pv(__import__('io').BytesIO(bytes(data)), 0, None)  # pylint: disable=protected-access
            at = pv.label_sector * qnxprobe.SECTOR
            off, = struct.unpack_from('<I', data, at + 20)
            data[at + off:at + off + 32] = flip(data[at + off:at + off + 32].decode()).encode()
            struct.pack_into('<I', data, at + 16, qnxprobe.lvm_crc(bytes(data[at + 20:at + qnxprobe.SECTOR])))
            second.append(os.path.join(folder, f'twin-{number}.img'))
            with open(second[-1], 'wb') as handle:
                handle.write(data)
        seeker = self._seeker(first + second)
        read = sorted(arr.safe_name for arr in self._arrays_read(seeker))
        self.assertEqual(len(read), 6)
        mine = [line for line in self.log.lines if line.startswith('  lvm_raid_multi_0_img_lba0 ')]
        theirs = [line for line in self.log.lines if line.startswith('  twin_0_img_lba0 ')]
        names_in = [re.findall(r' as (lvm_\w+)', line) for line in (mine[0], theirs[0])]
        self.assertEqual([len(found) for found in names_in], [3, 3])
        self.assertFalse(set(names_in[0]) & set(names_in[1]))
        self.assertEqual(sorted(names_in[0] + names_in[1]), read)

    def _decoyed_folder(self):
        """The four RAID5 members beside decoys: a member of another array, a copy of a
        member in a subfolder, a symbolic link to a member, a text file, and an NTFS
        image."""
        folder = tempfile.mkdtemp(prefix='raw_image_siblings_', dir=self.work)
        for path in self.sets['md-r5-ls']:
            shutil.copy(path, folder)
        shutil.copy(self.sets['md-r1'][0], os.path.join(folder, 'other-array.img'))
        os.makedirs(os.path.join(folder, 'sub'))
        shutil.copy(self.sets['md-r5-ls'][1], os.path.join(folder, 'sub', 'copy.img'))
        os.symlink(os.path.join(folder, 'md-r5-ls-1.img'), os.path.join(folder, 'link.img'))
        with open(os.path.join(folder, 'notes.txt'), 'w', encoding='utf-8') as handle:
            handle.write('case notes, not a disk\n' * 200)
        shutil.copy(self.ntfs, folder)
        return folder

    def test_the_other_members_are_found_beside_one_by_what_they_record(self):
        folder = self._decoyed_folder()
        start = os.path.join(folder, 'md-r5-ls-0.img')
        search = raw_image.find_members(start)
        self.assertEqual(sorted(os.path.basename(p) for p in search.added),
                         ['md-r5-ls-1.img', 'md-r5-ls-2.img', 'md-r5-ls-3.img'])
        codes = {os.path.basename(r['path']): r['code'] for r in search.result.rejected}
        self.assertEqual(codes['other-array.img'], 'different-array')
        self.assertEqual(codes['sub'], 'directory')
        self.assertEqual(codes['link.img'], 'symlink')
        self.assertIn(codes['notes.txt'], ('no-raid-metadata', 'too-small'))
        self.assertEqual(codes['ntfs-fixture.img'], 'no-raid-metadata')
        said = []
        raw = raw_image.cli_raw_input(start, say=said.append)
        self.assertEqual(raw.paths[0], start)
        self.assertEqual(sorted(raw.found), sorted(search.added))
        self.assertTrue(said[0].startswith('md-r5-ls-0.img holds a member of md array '
                                           '3090d8cb:464811e5:ec463b0f:41afd66f (qp:qp21), and '
                                           'not every member is in it.'))
        self.assertTrue(any('not used' in line and 'other-array.img' in line for line in said))
        self.assertEqual(said[-1], 'Reading 4 images together: md-r5-ls-0.img, '
                                   'md-r5-ls-1.img, md-r5-ls-2.img, md-r5-ls-3.img')
        seeker = self._seeker(raw.paths, found=raw.search)
        (arr,) = self._arrays_read(seeker)
        seeker.search('*')
        self.assertEqual(self._files_of(seeker, arr.safe_name), self.trees['md-r5-ls'])
        self.assertIn('(found automatically)', self.log.text())
        self.assertIn('not used  other-array.img', self.log.text())

    def test_no_search_reads_only_the_file_given(self):
        folder = self._decoyed_folder()
        start = os.path.join(folder, 'md-r5-ls-0.img')
        said = []
        raw = raw_image.cli_raw_input(start, look_beside=False, say=said.append)
        self.assertEqual((raw.paths, raw.found, said), ([start], [], []))

    def test_an_lvm_physical_volume_finds_the_others_of_its_group(self):
        search = raw_image.find_members(self.sets['lvm-raid-multi'][0])
        self.assertEqual(sorted(search.added), sorted(self.sets['lvm-raid-multi'][1:]))

    def test_an_ordinary_image_looks_for_nothing_and_says_nothing(self):
        said = []
        self.assertIsNone(raw_image.find_members(self.ntfs))
        raw = raw_image.cli_raw_input(self.ntfs, say=said.append)
        self.assertEqual((raw.paths, raw.found, raw.input_path, said),
                         ([self.ntfs], [], self.ntfs, []))

    def test_the_window_asks_only_when_the_search_adds_files(self):
        folder = self._decoyed_folder()
        start = os.path.join(folder, 'md-r5-ls-0.img')
        asked = []

        def answer(value):
            def confirm(_parent, search):
                asked.append(search)
                return value
            return confirm

        raw = raw_image.ask_raw_input(None, start, confirm=answer('use'))
        self.assertEqual(len(raw.paths), 4)
        self.assertEqual(len(raw.found), 3)
        raw = raw_image.ask_raw_input(None, start, confirm=answer('only'))
        self.assertEqual((raw.paths, raw.found), ([start], []))
        self.assertIn('the examiner chose to read only md-r5-ls-0.img',
                      '\n'.join(raw.search.lines()))
        self.assertIsNone(raw_image.ask_raw_input(None, start, confirm=answer(None)))
        self.assertEqual(len(asked), 3)
        text = raw_image.found_members_text(asked[0])
        self.assertIn('md-r5-ls-1.img: ', text)
        self.assertIn('other-array.img: ', text)
        # nothing to add, nothing asked
        raw = raw_image.ask_raw_input(None, self.ntfs, confirm=answer('use'))
        self.assertEqual((raw.paths, len(asked)), ([self.ntfs], 3))
        raw = raw_image.ask_raw_input(None, self.sets['md-r5-ls'], confirm=answer('use'))
        self.assertEqual((len(raw.paths), len(asked)), (4, 3))

    def test_what_the_input_is_called(self):
        self.assertEqual(raw_image.input_text('/x/disk.img'), '/x/disk.img')
        self.assertEqual(raw_image.input_text(['/x/a.img', '/x/b.img'], ['/x/b.img']),
                         '/x/a.img; /x/b.img (found automatically)')
        self.assertEqual(raw_image.selection_text(['/x/a.img']), '/x/a.img')
        self.assertEqual(raw_image.selection_text(['/x/a.img', '/x/b.img', '/x/c.img']),
                         '/x/a.img and 2 more')
        picked = ['/x/a.img', '/x/b.img']
        self.assertEqual(raw_image.selected_paths('/x/a.img and 1 more', picked), picked)
        self.assertEqual(raw_image.selected_paths('/y/typed.img', picked), ['/y/typed.img'])
        self.assertEqual(raw_image.selected_paths('/x/a.img', []), ['/x/a.img'])
        self.assertTrue(raw_image.names_raw_images(['/x/a.img', '/x/b.E01', '/x/c.002']))
        self.assertFalse(raw_image.names_raw_images(['/x/a.img', '/x/b.zip']))
        self.assertEqual(raw_image.image_paths('/x/a.img'), ['/x/a.img'])
        self.assertEqual(raw_image.image_paths(('/x/a.img', '/x/b.img')), ['/x/a.img', '/x/b.img'])

    def test_logical_evidence_is_not_read_with_other_images(self):
        ad1 = str(FIXTURES / 'lean-multi-ntfs-c9.ad1')
        with self.assertRaisesRegex(ValueError, 'is logical evidence'):
            FileSeekerRaw([ad1, self.ntfs], self.data)


def _macos_read(stem):
    """{path in the volume: (decmpfs method, SHA-256 of what macOS read)} from a decmpfs
    fixture's listing, written when macOS read every file back (see the README)."""
    out = {}
    for line in (FIXTURES / f'{stem}.sha256').read_text(encoding='utf-8').splitlines():
        if line.startswith('#') or not line.strip():
            continue
        digest, method, rel = line.split(None, 2)
        out[rel.strip()] = (int(method), digest)
    return out


class CompressedFilesAndImageDamageTest(unittest.TestCase):
    """What qnxprobe 1.74 and ewfprobe 0.14.0 report while reading, and what the run
    log says of it: macOS compressed files staged as macOS reads them, LZBITMAP files
    not staged with the reason, a compression attribute on an unflagged file named as
    damage with its member, and an E01 chunk whose data ran out named with the file
    that read it."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_decmpfs_')
        cls.images = {}
        for stem in ('decmpfs-apfs', 'decmpfs-hfsplus', 'ntfs-fixture'):
            cls.images[stem] = os.path.join(cls.work, f'{stem}.img')
            with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, \
                    open(cls.images[stem], 'wb') as dst:
                shutil.copyfileobj(src, dst)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)

    def seeker(self, path):
        seeker = FileSeekerRaw(path, self.data)
        self.addCleanup(seeker.cleanup)
        return seeker

    def check_volume(self, stem, prefix):
        seeker = self.seeker(self.images[stem])
        known = _macos_read(stem)
        refused = {rel for rel, (method, _d) in known.items() if method in (13, 14)}
        self.assertEqual(len(refused), 2)
        for rel, (method, digest) in sorted(known.items()):
            staged = seeker.search(f'*/{prefix}{rel}')
            if rel in refused:
                self.assertEqual(staged, [], rel)
                self.assertTrue(any(
                    line.startswith(f'Not staged, lba0/{prefix}{rel}: the file is compressed '
                                    f'with method {method} (LZBITMAP, ')
                    for line in self.log.lines), (rel, self.log.lines))
                continue
            self.assertEqual(len(staged), 1, rel)
            self.assertEqual(_sha256(staged[0]), digest, rel)
        # the two files that carry an attribute and no UF_COMPRESSED flag, each named
        said = [line.strip() for line in self.log.lines]
        self.assertIn('damage the reader recorded in lba0: 2 entries', said)
        for rel in ('unflagged/empty.txt', 'unflagged/small.txt'):
            self.assertTrue(any(line.startswith(f'lba0/{prefix}{rel}: ') and
                                'not flagged compressed (UF_COMPRESSED clear)' in line
                                for line in said), (rel, said))

    def test_apfs_compressed_files(self):
        self.check_volume('decmpfs-apfs', 'DECMPFS/')

    def test_hfsplus_compressed_files(self):
        self.check_volume('decmpfs-hfsplus', '')

    def test_damage_is_said_once(self):
        seeker = self.seeker(self.images['decmpfs-apfs'])
        seeker.search('*/unflagged/*')
        seeker.search('*/unflagged/*', force=True)
        headings = [line for line in self.log.lines if 'damage the reader recorded' in line]
        self.assertEqual(len(headings), 1, self.log.lines)

    def test_a_chunk_whose_data_ran_out_is_named_with_the_file(self):
        with open(self.images['ntfs-fixture'], 'rb') as handle:
            data = handle.read()
        known = _hash_list(FIXTURES / 'ntfs-fixture.sha256')
        # medium.bin is stored in one run; its first chunk is the one cut
        clean = self.seeker(self.images['ntfs-fixture'])
        staged = clean.search('*/medium.bin')[0]
        self.assertEqual(_sha256(staged), known['medium.bin'])
        with open(staged, 'rb') as handle:
            at = data.find(handle.read())
        self.assertGreater(at, 0)
        chunk = at // 32768
        folder = tempfile.mkdtemp(dir=self.work)
        whole = write_ewf(folder, 'whole', data)[0]
        cut = write_ewf(folder, 'cut', data, cut=(chunk,))[0]

        self.log.lines.clear()
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        staged = self.seeker(whole).search('*/medium.bin')
        self.assertEqual(_sha256(staged[0]), known['medium.bin'])
        self.assertFalse([line for line in self.log.lines if 'ran out' in line])

        self.log.lines.clear()
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        seeker = self.seeker(cut)
        self.assertFalse([line for line in self.log.lines if 'ran out' in line])
        staged = seeker.search('*/medium.bin')
        self.assertEqual(len(staged), 1)
        self.assertNotEqual(_sha256(staged[0]), known['medium.bin'])
        warned = [line for line in self.log.lines if line.startswith('WARNING: reading ')]
        self.assertEqual(len(warned), 1, self.log.lines)
        self.assertTrue(warned[0].startswith(
            'WARNING: reading lba0/medium.bin met 1 chunk of cut.E01 whose stored data ran '
            'out before the bytes it covers (1 with a compressed stream cut before its end), '
            'and the reader read '), warned[0])
        self.assertTrue(warned[0].endswith(', so what was staged for it can hold those zeros'))
        self.assertIn(f'  chunk {chunk:,} at byte {chunk * 32768:,}: ', '\n'.join(self.log.lines))
        # said once, however often the chunk is read again
        seeker.search('*/medium.bin', force=True)
        self.assertEqual(len([line for line in self.log.lines
                              if line.startswith('WARNING: reading ')]), 1)
        # but each file read through it is named, the second read (from the reader's
        # cache) as well as the first (ewfprobe 0.15.0's padded_zeros_read)
        named = [line for line in self.log.lines
                 if line.startswith('WARNING: lba0/medium.bin was read through')]
        self.assertEqual(len(named), 2, self.log.lines)
        self.assertGreater(seeker.padded_files[staged[0]], 0)

    def test_a_clean_acquisition_names_no_file_as_padded(self):
        with open(self.images['ntfs-fixture'], 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(dir=self.work)
        seeker = self.seeker(write_ewf(folder, 'whole', data)[0])
        seeker.search('*/medium.bin')
        self.assertEqual(seeker.padded_files, {})
        self.assertFalse([line for line in self.log.lines if 'was read through' in line])

    def test_directories_past_the_depth_limit_are_said(self):
        with mock.patch.object(raw_image, '_MAX_DEPTH', 0):
            self.seeker(self.images['ntfs-fixture'])
        said = [line for line in self.log.lines if 'levels deep' in line]
        self.assertEqual(len(said), 1, self.log.lines)
        self.assertIn('more than 0 levels deep', said[0])

    def test_a_folder_is_refused_by_name(self):
        folder = tempfile.mkdtemp(dir=self.work)
        with self.assertRaisesRegex(ValueError, 'is a folder, not a disk image'):
            raw_image.cli_raw_input(folder, say=lambda _line: None)
