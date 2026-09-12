#!/usr/bin/env python3
#
# qnxprobe - decide whether an extraction holds a QNX6 filesystem
# Copyright (c) 2026 Alexis Brignoni
# SPDX-License-Identifier: MIT
#
"""
Is this extraction QNX?

Every constant and every field offset below is read out of the Linux kernel's
own qnx6 driver, not assumed:

  QNX6_SUPER_MAGIC   0x68191122   include/uapi/linux/magic.h:55
  QNX6_BOOTBLOCK_SIZE    0x2000   include/linux/qnx6_fs.h:23
  QNX6_SUPERBLOCK_SIZE    0x200   include/linux/qnx6_fs.h:21
  struct qnx6_super_block          include/linux/qnx6_fs.h:94

fs/qnx6/inode.c reads the first superblock at QNX6_BOOTBLOCK_SIZE and, if the
magic is wrong there, retries at offset 0. It tries little endian first, then
big endian, so both are live in the wild.

A bare 4-byte magic match is NOT a finding: across a 256 MiB scan you expect
about one hit by chance. Each candidate is therefore parsed as a superblock and
its fields checked for internal consistency before it is reported CONFIRMED.

Read-only throughout. Never writes to the image.
"""
import os, re, struct, sys, datetime, json, time, uuid, zipfile, bisect, collections
import array

# ewfprobe is vendored beside this file (see vendored.json) so an EnCase/EWF
# .E01 acquisition can be read as an ordinary image. It is optional: without it
# everything else works exactly as before, and an .E01 is refused with a message
# saying what is missing rather than being read as raw bytes, which would find
# no filesystem and look like an empty image.
try:
    import ewfprobe
except ImportError:                  # not on sys.path when imported as a module
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import ewfprobe
    except ImportError:
        ewfprobe = None

QNXPROBE_VERSION = "1.27"

QNX6_MAGIC     = 0x68191122
BOOTBLOCK_SIZE = 0x2000
SECTOR         = 512
# How many FAT entries free_extents() reads at once. Four bytes each, so a
# megabyte a pass, which keeps one read per 262,144 clusters instead of one
# per cluster.
FAT_SCAN_ENTRIES = 262144

MBR_QNX_TYPES = {   # util-linux include/pt-mbr-partnames.h v2.40
    0x4d: "QNX4.x", 0x4e: "QNX4.x 2nd part", 0x4f: "QNX4.x 3rd part",
}

# offsets into struct qnx6_super_block, in declaration order
F = dict(magic=0, checksum=4, serial=8, ctime=16, atime=20, flags=24,
         version1=28, version2=30, volumeid=32, blocksize=48,
         num_inodes=52, free_inodes=56, num_blocks=60, free_blocks=64,
         allocgroup=68)

# A filesystem created before QNX6 existed or far in the future is not real.
T_MIN = int(datetime.datetime(1995, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
T_MAX = int(datetime.datetime(2050, 1, 1, tzinfo=datetime.timezone.utc).timestamp())



def sb_slots(fh, base, label, sized_regions):
    """Every offset in this region that could hold a superblock copy.

    Measured on a Ford Sync G4 image: the 0x1000 area reserved for a superblock
    holds TWO 512-byte slots, 0xE00 apart, carrying the current and the previous
    committed generation. Documentation/filesystems/qnx6.rst puts one reserved
    area at 0x2000 (after the bootblock) and a second near the end of the
    filesystem, so both are probed. Yields (absolute offset, offset-in-region).
    """
    rels = [BOOTBLOCK_SIZE, BOOTBLOCK_SIZE + 0xE00, 0, 0xE00]

    # The trailing reserved area. Measured on a Ford Sync G4 image it sits at
    # (partition size - 0x1000), not at (num_blocks * blocksize - 0x1000), so
    # the declared partition size is tried first and the filesystem's own size
    # second.
    ends = []
    for rlabel, rbase, rsize in sized_regions:
        if rbase == base and rsize:
            ends.append(rsize)
    head = check(fh, base + BOOTBLOCK_SIZE) or check(fh, base)
    if head and not head[2]:
        total = head[1]["num_blocks"] * head[1]["blocksize"]
        if 0 < total < (1 << 42):
            ends.append(total)
            # Where the kernel itself reads the second superblock: block
            # sb_num_blocks + (QNX6_BOOTBLOCK_SIZE + QNX6_SUPERBLOCK_AREA) /
            # blocksize, fs/qnx6/inode.c qnx6_fill_super, with the area 0x1000
            # from include/linux/qnx6_fs.h. The region-size candidates above
            # reach the same place only when the partition is exactly
            # BOOTBLOCK + area + volume + area long; this reaches it when the
            # partition is larger, or when there is no partition at all.
            second = BOOTBLOCK_SIZE + 0x1000 + total
            rels += [second, second + 0xE00]
    for e in ends:
        rels += [e - 0x1000, e - 0x200]

    seen = set()
    for rel in rels:
        if rel < 0 or rel in seen:
            continue
        seen.add(rel)
        yield base + rel, rel


def report_generations(copies, sized_regions, how_of):
    """copies: list of (off, how, endian, sb). Group by serial and diff."""
    gens = {}
    for off, how, endian, sb in copies:
        gens.setdefault(sb["serial"], {"sb": sb, "endian": endian, "at": []})
        gens[sb["serial"]]["at"].append(off)
    order = sorted(gens, reverse=True)
    return order, gens


# read_at() is the only path from a walker to the image, so a short answer from
# it is the one signal that a read reached past the end of the file. The walkers
# pad a short block with zeros, which is right for a sector an acquisition could
# not read and hides a cut image completely; this tally lets extract_to_zip()
# tell the two apart, per file, without each walker having to know.
EOF_SHORTFALL = {"bytes": 0}


def read_at(fh, off, n):
    try:
        fh.seek(off); data = fh.read(n)
    except OSError:
        return b""
    if len(data) < n:
        EOF_SHORTFALL["bytes"] += n - len(data)
    return data


class ImageUnreadable(Exception):
    """This tool cannot open the image, and the message says why."""


EWF_SIGNATURE = b"EVF\x09\x0d\x0a\xff\x00"


def _ewf_refused_by_reader(path):
    """True when the vendored reader rejects a damaged acquisition rather than
    returning something that would be walked as though it were an image."""
    if ewfprobe is None:
        return True
    try:
        ewfprobe.open_ewf(path)
    except ewfprobe.EwfError:
        return True
    except Exception:
        return False
    return False


def looks_like_ewf(path):
    """True when the file begins with the EWF signature.

    Checked here rather than in ewfprobe so an .E01 is still recognised, and
    refused with a useful message, when the vendored reader is absent.
    """
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == EWF_SIGNATURE
    except OSError:
        return False


class SplitImageError(Exception):
    """A numbered segment set that cannot be joined as it stands: a hole in
    the numbering, no first segment beside the file given, or segments of the
    same stem numbered with a different width."""


def split_segments(path):
    """The segment files of the split raw image that path belongs to, in order.

    FTK Imager and its peers write a raw image as numbered segments (.001,
    .002, ...) unless told to write one file. Handed any one of them, this finds
    the rest beside it: same directory, same stem, a suffix of the same number
    of digits. Returns [] when path is not that (the suffix is not all digits,
    or no other segment of the set is beside it), so a lone first segment is
    still read as the one file it is, and the short-image warning in main() is
    what says so.

    A set is joined only when it is whole from its first segment. A hole in the
    numbering, a set whose lowest segment is not .000 or .001, and segments of
    the same stem numbered with a different width are each refused with
    SplitImageError naming what is missing or odd, rather than joined around:
    a join with a gap reads every volume past it at the wrong offset and
    answers wrong, not empty.
    """
    folder, name = os.path.split(os.path.abspath(path))
    stem, dot, suffix = name.rpartition(".")
    if not dot or not stem or not (suffix.isascii() and suffix.isdigit()):
        return []
    width = len(suffix)
    present, other_width = {}, []
    for entry in os.listdir(folder):
        s, d, n = entry.rpartition(".")
        if not (d and s == stem and n.isascii() and n.isdigit()):
            continue
        if not os.path.isfile(os.path.join(folder, entry)):
            continue
        if len(n) == width:
            present[int(n)] = os.path.join(folder, entry)
        else:
            other_width.append(entry)
    if len(present) < 2 and not other_width:
        return []
    if other_width:
        raise SplitImageError(
            f"{name} sits beside segments of the same stem numbered with a "
            f"different number of digits ({', '.join(sorted(other_width)[:3])}"
            f"{', ...' if len(other_width) > 3 else ''}). Not joined: check the "
            f"numbering and rename the set to one width.")
    first = min(present)
    if first > 1:
        raise SplitImageError(
            f"{name} is one segment of a split image and the first segment, "
            f"{stem}.{1:0{width}d}, is not beside it (the lowest here is "
            f"{stem}.{first:0{width}d}). Put the whole set in one folder.")
    run, n = [], first
    while n in present:
        run.append(present[n])
        n += 1
    if len(run) < len(present):
        raise SplitImageError(
            f"{name} is one segment of a split image with a hole in it: "
            f"{stem}.{n:0{width}d} is missing while {stem}.{max(present):0{width}d} "
            f"is here. Put the whole set in one folder; a set joined around a "
            f"hole reads every volume past it at the wrong offset.")
    return run


class SegmentedImage:
    """The numbered segments of a split raw image, read as one file.

    Every walker reaches the image through read_at(), which only seeks and
    reads, so this stands in for the file object: a byte offset is mapped onto
    the segment that holds it and a read that crosses a segment boundary is
    served from both sides. A read past the end of the last segment comes back
    short, exactly as it does from one file, so read_at()'s shortfall tally and
    the short-image warning keep their meaning on a set whose last segments are
    missing (which no numbering check can see: the set simply ends early).

    At most MAX_OPEN segment files are held open at once, least recently used
    closed first, so a set of hundreds of segments does not exhaust the
    process's file descriptors.
    """
    MAX_OPEN = 16

    def __init__(self, paths):
        self.paths = [os.fspath(p) for p in paths]
        self.sizes = [os.path.getsize(p) for p in self.paths]
        self.starts, total = [], 0
        for s in self.sizes:
            self.starts.append(total)
            total += s
        self.size = total
        self.name = self.paths[0]
        self._pos = 0
        self._open = collections.OrderedDict()

    def _handle(self, i):
        fh = self._open.get(i)
        if fh is None:
            fh = open(self.paths[i], "rb")
            self._open[i] = fh
            while len(self._open) > self.MAX_OPEN:
                self._open.popitem(last=False)[1].close()
        else:
            self._open.move_to_end(i)
        return fh

    def seek(self, offset, whence=0):
        if whence == 0:
            pos = offset
        elif whence == 1:
            pos = self._pos + offset
        elif whence == 2:
            pos = self.size + offset
        else:
            raise ValueError(f"invalid whence ({whence!r}, should be 0, 1 or 2)")
        if pos < 0:
            raise OSError(22, "Invalid argument")
        self._pos = pos
        return pos

    def tell(self):
        return self._pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = max(self.size - self._pos, 0)
        out, pos = [], self._pos
        while n > 0 and pos < self.size:
            # bisect_right lands on the last segment starting at or before pos,
            # which steps over any zero-length segment sharing that start
            i = bisect.bisect_right(self.starts, pos) - 1
            fh = self._handle(i)
            fh.seek(pos - self.starts[i])
            chunk = fh.read(min(n, self.starts[i] + self.sizes[i] - pos))
            if not chunk:
                break                  # the segment is shorter on disk than when measured
            out.append(chunk)
            pos += len(chunk)
            n -= len(chunk)
        self._pos = pos
        return b"".join(out)

    def close(self):
        for fh in self._open.values():
            fh.close()
        self._open.clear()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def image_size(fh):
    """Byte length of the image behind fh, one file or a joined segment set."""
    size = getattr(fh, "size", None)
    if size is not None:
        return size
    try:
        return os.fstat(fh.fileno()).st_size
    except (AttributeError, OSError, ValueError):
        # No file descriptor behind it. Anything seekable can still say where
        # its end is, which is what a reader over a container answers to.
        here = fh.tell()
        try:
            fh.seek(0, os.SEEK_END)
            return fh.tell()
        finally:
            fh.seek(here)


def open_image(path, segments=None):
    """Open an image read-only: the one file, or every segment of the split
    image it belongs to, joined. segments is split_segments(path) when the
    caller already has it."""
    if looks_like_ewf(path):
        if ewfprobe is None:
            raise ImageUnreadable(
                f"{os.path.basename(path)} is an EnCase/EWF (.E01) acquisition. "
                f"Reading one needs ewfprobe.py beside this script; it is "
                f"normally vendored here (see vendored.json) and is missing. "
                f"Export the image to raw, or put ewfprobe.py back.")
        # ewfprobe joins the segments of the set itself, from the format's own
        # records rather than from the file names, and refuses an incomplete set.
        return ewfprobe.open_ewf(path)
    if segments is None:
        segments = split_segments(path)
    if segments:
        return SegmentedImage(segments)
    return open(path, "rb")


def describe_segment_sizes(sizes):
    """'19 x 1,572,864,000 bytes, then 1,384,120,320 bytes' for the shape an
    imaging tool writes; every size listed when they do not follow it."""
    if len(sizes) > 1 and len(set(sizes[:-1])) == 1:
        return f"{len(sizes) - 1} x {sizes[0]:,} bytes, then {sizes[-1]:,} bytes"
    return ", ".join(f"{s:,}" for s in sizes) + " bytes"


def short_regions(size, sized_regions, skip=()):
    """Regions the partition table describes that the file does not hold in full.

    Returns [(label, start, region_size, missing)] for every region whose end
    lies past the end of the file, missing being how many of its bytes are not
    here; missing == region_size means the region begins past the end of the
    file. A file that holds only the first segment of a split acquisition has
    this shape, and nothing else in a probe can tell that case from a small disk.
    """
    out = []
    for label, start, rsize in sized_regions:
        if not rsize or label in skip:
            continue
        end = start + rsize
        if end > size:
            out.append((label, start, rsize, min(rsize, end - size)))
    return out


def ts(v):
    if not (T_MIN <= v <= T_MAX):
        return None
    return datetime.datetime.fromtimestamp(v, datetime.timezone.utc)


def duration(sec):
    """Largest two sensible units, e.g. '3 days 4 hours', '2 seconds'."""
    sec = abs(int(sec))
    if sec == 0:
        return "0 seconds"
    units = (("year", 31557600), ("day", 86400), ("hour", 3600),
             ("minute", 60), ("second", 1))
    parts, rem = [], sec
    for name, size in units:
        if rem >= size:
            n, rem = divmod(rem, size)
            parts.append(f"{n:,} {name}{'' if n == 1 else 's'}")
            if len(parts) == 2:
                break
    return " ".join(parts)


def delta_line(label, new, old):
    """One line describing how a stored time changed between two commits.

    A value outside the plausible range is an unset placeholder, not a date,
    so the difference against it is not a duration and is not reported as one.
    Measured on a Ford Sync G4 image: the previous generation of dps_os holds
    sb_atime 1, which naively differs from the active value by 54 years.
    """
    if new == old:
        return f"        {label:<12} unchanged"
    new_ok, old_ok = ts(new) is not None, ts(old) is not None
    if not old_ok and new_ok:
        return (f"        {label:<12} was unset (raw {old}), now "
                f"{ts(new):%Y-%m-%d %H:%M:%S} UTC   (not a duration)")
    if old_ok and not new_ok:
        return (f"        {label:<12} was {ts(old):%Y-%m-%d %H:%M:%S} UTC, "
                f"now unset (raw {new})   (not a duration)")
    if not new_ok and not old_ok:
        return f"        {label:<12} raw {old} -> raw {new}   (neither is a date)"
    d = new - old
    return (f"        {label:<12} {d:+,} s   ({'forward' if d > 0 else 'back'} "
            f"{duration(d)})")


def stamp(v):
    d = ts(v)
    return (f"{d:%Y-%m-%d %H:%M:%S} UTC" if d
            else f"raw {v}  (no valid clock when written)")


def parse_sb(buf, endian):
    """Parse a candidate superblock. Returns (dict, [reasons it failed])."""
    e = "<" if endian == "little endian" else ">"
    g32 = lambda k: struct.unpack_from(e + "I", buf, F[k])[0]
    g16 = lambda k: struct.unpack_from(e + "H", buf, F[k])[0]
    sb = dict(
        checksum=g32("checksum"),
        serial=struct.unpack_from(e + "Q", buf, F["serial"])[0],
        ctime=g32("ctime"), atime=g32("atime"), flags=g32("flags"),
        version1=g16("version1"), version2=g16("version2"),
        volumeid=buf[F["volumeid"]:F["volumeid"] + 16],
        blocksize=g32("blocksize"), num_inodes=g32("num_inodes"),
        free_inodes=g32("free_inodes"), num_blocks=g32("num_blocks"),
        free_blocks=g32("free_blocks"), allocgroup=g32("allocgroup"),
    )
    bad = []
    bs = sb["blocksize"]
    if not (512 <= bs <= 65536 and (bs & (bs - 1)) == 0):
        bad.append(f"blocksize {bs} not a power of two in 512..65536")
    # An embedded filesystem is often built on a host with no clock, so ctime
    # legitimately reads as a few seconds past the epoch. Measured on a Ford
    # Sync G4 dps_os partition: ctime 308, atime 2024-04-04, everything else
    # consistent and the volume size an exact match for its GPT entry.
    # Requiring BOTH timestamps rejected a real filesystem, so require one.
    if ts(sb["ctime"]) is None and ts(sb["atime"]) is None:
        bad.append(f"neither ctime ({sb['ctime']}) nor atime ({sb['atime']}) "
                   f"is a plausible date")
    if sb["free_blocks"] > sb["num_blocks"]:
        bad.append("free_blocks > num_blocks")
    if sb["free_inodes"] > sb["num_inodes"]:
        bad.append("free_inodes > num_inodes")
    if sb["num_blocks"] == 0:
        bad.append("num_blocks is zero")
    if sb["num_inodes"] == 0:
        bad.append("num_inodes is zero")
    return sb, bad


def check(fh, off):
    """Return (endian, sb, bad) if magic is at off, else None."""
    buf = read_at(fh, off, 512)
    if len(buf) < 512:
        return None
    for e, pk in (("little endian", "<I"), ("big endian", ">I")):
        if struct.unpack_from(pk, buf, 0)[0] == QNX6_MAGIC:
            sb, bad = parse_sb(buf, e)
            return e, sb, bad
    return None


def parse_mbr(fh):
    mbr = read_at(fh, 0, 512)
    if len(mbr) < 512 or mbr[510:512] != b"\x55\xaa":
        return None
    # A FAT, exFAT or NTFS boot sector also ends in 0x55AA, and its boot code
    # sits where MBR partition entries would be, so it parses as four nonsense
    # partitions. Its own type string at bytes 3..11 (exFAT, NTFS) or 82..90
    # (FAT32) says it is a filesystem, not a partition table.
    if (mbr[3:11] in (b"EXFAT   ", b"NTFS    ")
            or mbr[82:90] == b"FAT32   " or mbr[54:62] == b"FAT16   "):
        return None
    # A QNX4 boot block can also end in 0x55AA (the dinit boot sector does).
    # The QNX4 superblock is the NEXT sector: its first entry is the root
    # directory inode, di_fname "/" and a directory mode, fs/qnx4/inode.c
    # qnx4_checkroot() and qnx4_iget(). If that is what follows, this sector
    # is a filesystem's boot block, not a partition table.
    nxt = read_at(fh, 512, 64)
    if (len(nxt) == 64 and nxt[0:2] == b"/\x00"
            and (struct.unpack_from("<H", nxt, 50)[0] & 0o170000) == S_IFDIR):
        return None
    # A qnx6 boot block can end in 0x55AA as well. On qnxmount's qnx6
    # reference image sector 0 is x86 boot code, and bytes 446..478 of that
    # code parse as two partitions starting 1.5 and 1.8 TB into a 400 KB file.
    # Accepting them costs the whole filesystem: the qnx6 at offset 0 then has
    # no region to be listed or extracted from, and the end-of-volume
    # superblock, the active generation, is never probed. The Linux driver
    # never reads sector 0; it reads the superblock at QNX6_BOOTBLOCK_SIZE
    # (fs/qnx6/inode.c qnx6_fill_super). A consistent superblock there means
    # this sector is that filesystem's boot block, not a partition table.
    q6 = check(fh, BOOTBLOCK_SIZE)
    if q6 and not q6[2]:
        return None
    out = []
    for i in range(4):
        ent = mbr[446 + i * 16: 446 + (i + 1) * 16]
        t = ent[4]
        start, cnt = struct.unpack("<II", ent[8:16])
        if t and cnt:
            out.append((i + 1, t, start, cnt))
    # Whatever else ends in 0x55AA: a table none of whose partitions begins
    # inside the image is not describing this image, so the bytes at 446 are
    # code or data. The boot indicator byte is deliberately not a test: neither
    # util-linux's libfdisk nor The Sleuth Kit rejects a table on its value.
    try:
        size = image_size(fh)
    except (OSError, AttributeError, ValueError):
        size = None
    if out and size and all(start * SECTOR >= size for _, _, start, _ in out):
        return None
    return out


def parse_gpt(fh):
    """Parse the GPT at LBA 1. Returns list of (idx, name, type_guid, start, end)."""
    hdr = read_at(fh, SECTOR, 92)
    if len(hdr) < 92 or hdr[0:8] != b"EFI PART":
        return None
    ent_lba, n_ent, ent_sz = struct.unpack_from("<QII", hdr, 72)
    out = []
    for i in range(min(n_ent, 256)):
        raw = read_at(fh, ent_lba * SECTOR + i * ent_sz, ent_sz)
        if len(raw) < 56:
            break
        tguid = raw[0:16]
        if tguid == b"\x00" * 16:
            continue
        first, last = struct.unpack_from("<QQ", raw, 32)
        name = raw[56:ent_sz].decode("utf-16-le", "replace").rstrip("\x00").strip()
        g = uuid.UUID(bytes_le=tguid)
        out.append((i + 1, name, str(g), first, last))
    return out


# ---------------------------------------------------------------------------
# What is actually in a partition, when it is not qnx6.
#
# A partition type byte is a label, not a fact. The BMW MGU image carries
# twelve partitions marked 0x83 "Linux"; ten hold ext4, one holds an ipk
# container with a Linux bzImage inside it, and one is the extended-partition
# container itself. So the type byte is reported, and then the bytes are read.
#
# ext offsets below were derived from struct ext4_super_block in the kernel's
# fs/ext4/ext4.h and cross-checked against that header's own /*NN*/ offset
# markers, all 15 of which agreed, with the struct totalling 1024 bytes.
# EXT2_SUPER_MAGIC 0xEF53 is from include/uapi/linux/magic.h:24.
# ---------------------------------------------------------------------------
EXT_SB_OFF   = 1024
EXT_MAGIC    = 0xEF53
EXT_F = dict(inodes_count=0, blocks_count=4, free_blocks=12, first_data_block=20,
             log_block_size=24, inodes_per_group=40, mtime=44, wtime=48,
             mnt_count=52, magic=56, state=58, lastcheck=64, inode_size=88,
             feature_compat=92, feature_incompat=96, uuid=104, volume_name=120,
             last_mounted=136, desc_size=254, mkfs_time=264, kbytes_written=376,
             error_count=404)
EXT_INCOMPAT_EXTENTS  = 0x0040   # ext4.h
EXT_COMPAT_HAS_JOURNAL = 0x0004  # ext4.h
EXT_VALID_FS = 0x0001            # ext4.h


def _e(sb, k, n=4):
    o = EXT_F[k]
    return int.from_bytes(sb[o:o + n], "little")


# ---------------------------------------------------------------------------
# Directory listing (--list)
#
# qnx6 block resolution follows fs/qnx6/inode.c qnx6_block_map():
#   ptrbits  = ilog2(blocksize / 4)                          inode.c:431
#   blks_off = (0x2000 >> bits) + (0x1000 >> bits)            inode.c:374
#   devblock = stored_block + blks_off                        inode.c:68
# Structure layouts are struct qnx6_inode_entry, qnx6_dir_entry,
# qnx6_long_dir_entry and qnx6_root_node in include/linux/qnx6_fs.h.
#
# ext4 layouts are struct ext4_super_block, ext4_group_desc, ext4_inode and
# ext4_dir_entry_2 in fs/ext4/ext4.h, plus the extent structures in
# fs/ext4/ext4_extents.h (EXT4_EXT_MAGIC 0xf30a).
# ---------------------------------------------------------------------------
QNX6_INODE_SIZE  = 0x80
QNX6_DIRENT_SIZE = 0x20
QNX6_ROOT_INO    = 1
QNX6_ROOTNODE    = dict(Inode=72, Longfile=232)   # offsets inside the superblock
S_IFDIR, S_IFLNK = 0o040000, 0o120000


def _fmt_time(v):
    """Per-file mtime. Unlike a superblock stamp, an epoch-era value here is
    ordinary on an embedded image (files staged before the clock was set), so
    it is shown rather than suppressed."""
    try:
        return datetime.datetime.fromtimestamp(
            v, datetime.timezone.utc).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return "-"


def _fmt_reading(recorded):
    """A file's modified reading from a walker that keeps readings, as text.

    FAT32 and exFAT store a wall clock and no zone, so ``entry()`` gives them an
    mtime of 0 and the readings arrive through listdir_records() instead. A
    listing prints the reading as stored, marked so it cannot be read as an
    instant, and prints nothing rather than 1970-01-01 when there is none. exFAT
    also stores a UTC offset beside each stamp; it is shown and not applied, the
    stance GLEAPP takes on the same field, since one writer has been measured
    and a listing should not assert an instant from it.
    """
    when = (recorded or {}).get("modified")
    if not when:
        return ""
    off = recorded.get("modified utc offset")
    return f"modified {when} (as stored, {'offset ' + off + ' not applied' if off else 'no zone'})"


class Qnx6Walker:
    def __init__(self, fh, base, sb_off):
        self.fh, self.base = fh, base
        sb = read_at(fh, base + sb_off, 512)
        self.bs = struct.unpack_from("<I", sb, 48)[0]
        bits = self.bs.bit_length() - 1
        self.ptrbits = (self.bs // 4).bit_length() - 1
        self.blks_off = (0x2000 >> bits) + (0x1000 >> bits)
        self.inode_rn = self._rn(sb, QNX6_ROOTNODE["Inode"])
        self.long_rn = self._rn(sb, QNX6_ROOTNODE["Longfile"])

    @staticmethod
    def _rn(sb, o):
        return dict(ptr=list(struct.unpack_from("<16I", sb, o + 8)), levels=sb[o + 72])

    def _blk(self, b):
        return read_at(self.fh, self.base + b * self.bs, self.bs)

    def _map(self, ptrs, levels, n):
        bitdelta = self.ptrbits * levels
        mask = (1 << self.ptrbits) - 1
        lp = n >> bitdelta
        if lp > 15:
            return None
        blk = ptrs[lp] + self.blks_off
        for _ in range(levels):
            buf = self._blk(blk)
            if len(buf) < self.bs:
                return None
            bitdelta -= self.ptrbits
            ptr = struct.unpack_from("<I", buf, ((n >> bitdelta) & mask) * 4)[0]
            if ptr in (0, 0xFFFFFFFF):
                return None
            blk = ptr + self.blks_off
        return blk

    def _tree(self, rn, logical):
        b = self._map(rn["ptr"], rn["levels"], logical)
        return self._blk(b) if b is not None else None

    def inode(self, num):
        byte = (num - 1) * QNX6_INODE_SIZE
        buf = self._tree(self.inode_rn, byte // self.bs)
        if not buf:
            return None
        raw = buf[byte % self.bs:][:QNX6_INODE_SIZE]
        if len(raw) < QNX6_INODE_SIZE:
            return None
        return dict(size=struct.unpack_from("<Q", raw, 0)[0],
                    mtime=struct.unpack_from("<I", raw, 20)[0],
                    mode=struct.unpack_from("<H", raw, 32)[0],
                    ptr=list(struct.unpack_from("<16I", raw, 36)),
                    levels=raw[100])

    def _longname(self, blk):
        buf = self._tree(self.long_rn, blk)
        if not buf:
            return "<longname unreadable>"
        n = struct.unpack_from("<H", buf, 0)[0]
        return buf[2:2 + min(n, 510)].decode("utf-8", "replace")

    def listdir(self, num):
        ino = self.inode(num)
        if not ino or not (ino["mode"] & S_IFDIR):
            return []
        out = []
        for lb in range((ino["size"] + self.bs - 1) // self.bs):
            b = self._map(ino["ptr"], ino["levels"], lb)
            if b is None:
                continue
            buf = self._blk(b)
            for p in range(0, len(buf) - QNX6_DIRENT_SIZE + 1, QNX6_DIRENT_SIZE):
                de_ino = struct.unpack_from("<I", buf, p)[0]
                de_size = buf[p + 4]
                if not de_ino or not de_size:
                    continue
                if de_size == 0xFF:
                    name = self._longname(struct.unpack_from("<I", buf, p + 8)[0])
                else:
                    name = buf[p + 5:p + 5 + min(de_size, 27)].decode("utf-8", "replace")
                if name not in (".", ".."):
                    out.append((name, de_ino))
        return sorted(out)

    def entry(self, num):
        ino = self.inode(num)
        if not ino:
            return None
        return ino["mode"], ino["size"], ino["mtime"]

    def read_file(self, num, size):
        """Yield the file's bytes a block at a time. An unmapped block is a
        hole and is emitted as zeros, so offsets stay correct."""
        ino = self.inode(num)
        if not ino:
            return
        left = size
        for lb in range((size + self.bs - 1) // self.bs):
            b = self._map(ino["ptr"], ino["levels"], lb)
            buf = self._blk(b) if b is not None else bytes(self.bs)
            if len(buf) < self.bs:
                buf = buf + bytes(self.bs - len(buf))
            take = min(self.bs, left)
            yield buf[:take]
            left -= take
            if left <= 0:
                return

    root = QNX6_ROOT_INO


class ExtUnreadable(Exception):
    """An ext file this reader cannot hand back whole; the message says why."""


class ExtWalker:
    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        sb = read_at(fh, base + EXT_SB_OFF, 1024)
        self.bs = 1024 << _e(sb, "log_block_size")
        self.ipg = _e(sb, "inodes_per_group")
        self.fdb = _e(sb, "first_data_block")
        self.isz = _e(sb, "inode_size", 2)
        is64 = bool(_e(sb, "feature_incompat") & 0x80)
        self.dsz = _e(sb, "desc_size", 2) if is64 else 32
        self.is64 = is64

    def _blk(self, b):
        return read_at(self.fh, self.base + b * self.bs, self.bs)

    def inode(self, num):
        g, idx = divmod(num - 1, self.ipg)
        gd = read_at(self.fh, self.base + (self.fdb + 1) * self.bs + g * self.dsz, self.dsz)
        if len(gd) < 12:
            return None
        it = int.from_bytes(gd[8:12], "little")
        if self.is64 and self.dsz >= 44:
            it |= int.from_bytes(gd[40:44], "little") << 32
        raw = read_at(self.fh, self.base + it * self.bs + idx * self.isz, self.isz)
        if len(raw) < 60:
            return None
        return raw

    def _runs(self, raw):
        """[(logical block, block count, physical block or None)] in logical order.

        A file's content is addressed by logical block; where a run's physical
        block is None the run is an extent the kernel wrote as uninitialized,
        which reads as zeros, and a logical range no run covers is a hole, which
        also reads as zeros. Returns None for a file whose data lives inline in
        the inode. Two layouts are read:

        - the extent tree (EXT4_EXTENTS_FL), each leaf carrying its own logical
          start (ee_block) and length, with bit 15 of the length marking an
          uninitialized extent: linux/fs/ext4/ext4_extents.h;
        - the classic block map of ext2 and ext3, twelve direct pointers then a
          single, double and triple indirect block, a zero pointer being a
          hole: linux/fs/ext2/ext2.h (i_block), linux/fs/ext4/ext4.h EXT4_*_BLOCK.

        Reading the extents as a flat list of physical blocks, which this did
        before, dropped every hole: a 32 KiB SQLite shared-memory file with two
        written pages came back as 8 KiB, and its bytes in the wrong order.
        """
        flags = int.from_bytes(raw[32:36], "little")
        if flags & 0x10000000:                                 # EXT4_INLINE_DATA_FL
            return None
        runs = []
        if flags & 0x80000:                                    # EXT4_EXTENTS_FL
            def walk(buf, off, depth_left=8):
                if depth_left <= 0 or len(buf) < off + 12:
                    return
                if struct.unpack_from("<H", buf, off)[0] != 0xF30A:
                    return
                ent = struct.unpack_from("<H", buf, off + 2)[0]
                depth = struct.unpack_from("<H", buf, off + 6)[0]
                for i in range(ent):
                    o = off + 12 + i * 12
                    if len(buf) < o + 12:
                        return
                    if depth == 0:
                        lblk = struct.unpack_from("<I", buf, o)[0]
                        raw_len = struct.unpack_from("<H", buf, o + 4)[0]
                        st = (struct.unpack_from("<I", buf, o + 8)[0]
                              | struct.unpack_from("<H", buf, o + 6)[0] << 32)
                        if raw_len > 0x8000:                   # uninitialized extent
                            runs.append((lblk, raw_len - 0x8000, None))
                        elif raw_len:
                            runs.append((lblk, raw_len, st))
                    else:
                        leaf = (struct.unpack_from("<I", buf, o + 4)[0]
                                | struct.unpack_from("<H", buf, o + 8)[0] << 32)
                        walk(self._blk(leaf), 0, depth_left - 1)
            walk(raw, 40)
            runs.sort()
            return runs

        per = self.bs // 4                                      # pointers per indirect block

        def add(lblk, phys):
            if not phys:                                        # a zero pointer is a hole
                return
            if runs and runs[-1][2] is not None:
                l0, n0, p0 = runs[-1]
                if l0 + n0 == lblk and p0 + n0 == phys:
                    runs[-1] = (l0, n0 + 1, p0)
                    return
            runs.append((lblk, 1, phys))

        def indirect(block, level, lbase):
            if not block:
                return
            buf = self._blk(block)
            span = per ** (level - 1)                           # logical blocks per pointer
            for i in range(min(per, len(buf) // 4)):
                ptr = struct.unpack_from("<I", buf, 4 * i)[0]
                if level == 1:
                    add(lbase + i * span, ptr)
                elif ptr:
                    indirect(ptr, level - 1, lbase + i * span)

        for i in range(12):
            add(i, struct.unpack_from("<I", raw, 40 + 4 * i)[0])
        indirect(struct.unpack_from("<I", raw, 88)[0], 1, 12)
        indirect(struct.unpack_from("<I", raw, 92)[0], 2, 12 + per)
        indirect(struct.unpack_from("<I", raw, 96)[0], 3, 12 + per + per * per)
        return runs

    def _blocks(self, raw):
        """The physical blocks holding a directory's entries, in logical order.

        Directories have no holes, so a run that reads as zeros is skipped.
        """
        runs = self._runs(raw)
        if not runs:
            return []
        out = []
        for _lblk, count, phys in runs:
            if phys is not None:
                out.extend(range(phys, phys + count))
        return out

    def listdir(self, num):
        raw = self.inode(num)
        if not raw:
            return []
        out = []
        for b in self._blocks(raw):
            buf = self._blk(b)
            p = 0
            while p < len(buf) - 8:
                i = struct.unpack_from("<I", buf, p)[0]
                rec = struct.unpack_from("<H", buf, p + 4)[0]
                nl = buf[p + 6]
                if rec < 8 or p + rec > len(buf):
                    break
                if i and nl:
                    nm = buf[p + 8:p + 8 + nl].decode("utf-8", "replace")
                    if nm not in (".", ".."):
                        out.append((nm, i))
                p += rec
        return sorted(out)

    def entry(self, num):
        raw = self.inode(num)
        if not raw:
            return None
        mode = struct.unpack_from("<H", raw, 0)[0]
        size = (struct.unpack_from("<I", raw, 4)[0]
                | struct.unpack_from("<I", raw, 108)[0] << 32)
        return mode, size, struct.unpack_from("<I", raw, 16)[0]

    def read_file(self, num, size):
        """Yield the file's bytes, exactly ``size`` of them, holes and all."""
        raw = self.inode(num)
        if not raw:
            return
        runs = self._runs(raw)
        if runs is None:
            # Inline data keeps the first 60 bytes in the inode's block field and
            # the rest in the system.data extended attribute, which is not read
            # here. A short file is whole; a longer one is refused rather than
            # handed back cut, because a cut file parses as a smaller one.
            if size <= 60:
                yield raw[40:40 + size]
                return
            raise ExtUnreadable(f"{size:,} bytes of inline data, of which only the 60 "
                                "in the inode are read")
        left = size
        pos = 0                                                 # next logical block to deliver
        for lblk, count, phys in runs:
            if left <= 0:
                return
            if lblk > pos:                                      # a hole reads as zeros
                for chunk in self._zeros(min(lblk - pos, -(-left // self.bs)) * self.bs, left):
                    yield chunk
                    left -= len(chunk)
                pos = lblk
            skip = pos - lblk                                   # an overlapping run, never expected
            for i in range(skip, count):
                if left <= 0:
                    return
                if phys is None:
                    buf = bytes(self.bs)
                else:
                    buf = self._blk(phys + i)
                    if len(buf) < self.bs:
                        buf = buf + bytes(self.bs - len(buf))
                take = min(self.bs, left)
                yield buf[:take]
                left -= take
                pos += 1
        if left > 0:                                            # a trailing hole
            for chunk in self._zeros(left, left):
                yield chunk
                left -= len(chunk)

    @staticmethod
    def _zeros(n, cap):
        """Zero bytes for a hole, at most cap, in pieces that do not sit in memory at once."""
        n = min(n, cap)
        while n > 0:
            piece = min(n, 1 << 20)
            yield bytes(piece)
            n -= piece

    root = 2


# ---------------------------------------------------------------------------
# FAT32 and exFAT.
#
# FAT is the file system of removable media and of many embedded devices, so a
# vehicle image can carry one beside its QNX and ext volumes. Both are read
# here directly, no mounting.
#
# Field offsets are from Microsoft's own specifications: the FAT32 BPB from the
# "Microsoft Extensible Firmware Initiative FAT32 File System Specification"
# v1.03, and the exFAT structures from the "exFAT file system specification"
# (Microsoft, 2019). Long file names on FAT are the VFAT scheme (UTF-16 across
# 0x0F entries); exFAT names are UTF-16 in a chain of file-name directory
# entries. Only the fields needed to list and read files are parsed.
# ---------------------------------------------------------------------------

class FatDeletedFile:
    """One deleted FAT32 or exFAT directory entry that still describes a file.

    ``recoverable`` says whether the content can be read back: the entry keeps
    its first cluster and size, so the data is readable while those clusters
    are still free. ``assumed_contiguous`` is True when the chain that said
    where the rest of the file lay is gone (FAT32 zeroes it on delete; exFAT
    keeps one only for a fragmented file) and the read assumes the file was
    laid out in one run, which is how a driver writes a fresh file onto a
    card with room but is not something the volume can confirm. ``times`` are
    the readings as stored, text with no zone, the same as listdir_records().
    """

    __slots__ = ("name", "parent", "is_dir", "size", "first_cluster",
                 "recoverable", "reason", "assumed_contiguous", "times",
                 "in_deleted_dir", "_node")

    def __init__(self, name, parent, is_dir, size, first_cluster, recoverable,
                 reason, assumed_contiguous, times, in_deleted_dir, node):
        self.name, self.parent, self.is_dir = name, parent, is_dir
        self.size, self.first_cluster = size, first_cluster
        self.recoverable, self.reason = recoverable, reason
        self.assumed_contiguous, self.times = assumed_contiguous, times
        self.in_deleted_dir = in_deleted_dir
        self._node = node

    def __repr__(self):
        state = "recoverable" if self.recoverable else f"not recoverable ({self.reason})"
        extra = ", contiguity assumed" if self.assumed_contiguous else ""
        return (f"FatDeletedFile(name={self.name!r}, size={self.size}, "
                f"cluster={self.first_cluster}, {state}{extra})")


class Fat32Walker:
    """List and read files from a FAT32 volume. inode() takes a (cluster, size,
    is_dir) tuple, so the shared collect()/extract_to_zip() work unchanged; the
    root is that tuple for the root cluster."""

    def __init__(self, fh, base):
        self.fh = fh
        self.base = base
        bpb = read_at(fh, base, 512)
        self.bps = struct.unpack_from("<H", bpb, 11)[0]
        self.spc = bpb[13]
        self.reserved = struct.unpack_from("<H", bpb, 14)[0]
        self.nfats = bpb[16]
        self.spf = struct.unpack_from("<I", bpb, 36)[0]
        # BPB_TotSec16 is zero on FAT32 and the count lives in BPB_TotSec32, but
        # read both: a volume small enough to use the 16-bit field is still a
        # legal FAT32, and free_extents needs the count to size the cluster area.
        self.total_sectors = (struct.unpack_from("<H", bpb, 19)[0]
                              or struct.unpack_from("<I", bpb, 32)[0])
        self.root_clus = struct.unpack_from("<I", bpb, 44)[0]
        self.fat_start = base + self.reserved * self.bps
        self.data_start = self.fat_start + self.nfats * self.spf * self.bps
        self.cluster_bytes = self.spc * self.bps
        self.root = (self.root_clus, 0, True)

    def _fat_next(self, clus):
        off = self.fat_start + clus * 4
        raw = read_at(self.fh, off, 4)
        if len(raw) < 4:
            # Past the end of the image, which is what the first segment of a
            # split acquisition looks like. That is the end of the chain, not a
            # reason to raise: the volume is truncated, not unreadable.
            return 0x0FFFFFFF
        return struct.unpack_from("<I", raw, 0)[0] & 0x0FFFFFFF

    def _chain(self, clus):
        seen = set()
        while 0x2 <= clus < 0x0FFFFFF8 and clus not in seen:
            seen.add(clus)
            yield clus
            clus = self._fat_next(clus)

    def _cluster_off(self, clus):
        return self.data_start + (clus - 2) * self.cluster_bytes

    def _read_chain(self, clus, size=None):
        out = bytearray()
        for c in self._chain(clus):
            out += read_at(self.fh, self._cluster_off(c), self.cluster_bytes)
            if size is not None and len(out) >= size:
                break
        return bytes(out[:size]) if size is not None else bytes(out)

    def free_extents(self, min_bytes=0):
        """[(byte offset, length)] for the runs of space the volume says are free.

        FAT keeps no separate allocation bitmap. The file allocation table is
        both the chain of every file and the record of what is in use, and an
        entry of zero is a free cluster. Numbering starts at 2, so entry n
        addresses the data area at (n - 2) cluster widths in, and entries 0 and
        1 are the media descriptor and the end-of-chain marker rather than
        clusters.

        Offsets are into the image rather than the volume, so a caller reading
        the whole disk can use them directly. ``min_bytes`` drops runs too short
        to hold anything worth recovering.

        The table is read a megabyte at a time and unpacked as machine words,
        because reading four bytes per cluster through the image would be one
        seek per cluster.
        """
        cluster = self.cluster_bytes
        if not cluster or not self.total_sectors:
            return []
        data_sectors = self.total_sectors - (self.reserved + self.nfats * self.spf)
        count = data_sectors // self.spc if self.spc else 0
        if count <= 0:
            return []
        last = count + 2                             # entries 0 .. count + 1

        runs, run_start, pos = [], None, 0
        while pos < last:
            want = min(FAT_SCAN_ENTRIES, last - pos)
            raw = read_at(self.fh, self.fat_start + pos * 4, want * 4)
            if len(raw) < want * 4:                  # a truncated image stops here
                raw += b"\x00" * (want * 4 - len(raw))
            words = array.array("I")
            words.frombytes(raw)
            if sys.byteorder != "little":
                words.byteswap()
            for i, val in enumerate(words):
                num = pos + i
                if num < 2:
                    continue
                if val & 0x0FFFFFFF:
                    if run_start is not None:
                        runs.append((run_start, num - run_start))
                        run_start = None
                elif run_start is None:
                    run_start = num
            pos += want
        if run_start is not None:
            runs.append((run_start, last - run_start))

        out = []
        for first, n in runs:
            length = n * cluster
            if length >= min_bytes:
                out.append((self._cluster_off(first), length))
        return out

    def inode(self, node):
        return node    # (cluster, size, is_dir) already carries what entry() needs

    def entry(self, node):
        clus, size, is_dir = node
        mode = 0o040000 if is_dir else 0o100000
        return (mode, size, 0)

    def listdir_records(self, node):
        """(name, node, recorded times as stored) for every entry.

        FAT records a wall-clock reading and no zone, so the times are text.
        """
        clus = node[0]
        raw = self._read_chain(clus)
        out, lfn = [], []
        for i in range(0, len(raw), 32):
            e = raw[i:i + 32]
            if len(e) < 32 or e[0] == 0x00:
                break
            if e[0] == 0xE5:
                lfn = []; continue
            attr = e[11]
            if attr == 0x0F:                       # VFAT long-name fragment
                seq = e[0] & 0x3F
                chars = e[1:11] + e[14:26] + e[28:32]
                lfn.append((seq, chars)); continue
            if attr & 0x08:                        # volume label
                lfn = []; continue
            name = _vfat_name(lfn) if lfn else _fat_short_name(e)
            lfn = []
            hi = struct.unpack_from("<H", e, 20)[0]
            lo = struct.unpack_from("<H", e, 26)[0]
            first = (hi << 16) | lo
            sz = struct.unpack_from("<I", e, 28)[0]
            is_sub = bool(attr & 0x10)
            if name in (".", ".."):
                continue
            node = (first or 2, sz, is_sub)
            out.append((name, node, {
                "modified": _dos_stamp(struct.unpack_from("<H", e, 24)[0],
                                       struct.unpack_from("<H", e, 22)[0]),
                "created": _dos_stamp(struct.unpack_from("<H", e, 16)[0],
                                      struct.unpack_from("<H", e, 14)[0], e[13]),
                "accessed date": _dos_date(struct.unpack_from("<H", e, 18)[0]),
            }))
        return out

    def _deleted_in(self, node, in_deleted_dir):
        """Deleted entries in one directory, in the driver's own order."""
        clus = node[0]
        raw = self._read_chain(clus)
        out, lfn = [], []
        for i in range(0, len(raw), 32):
            e = raw[i:i + 32]
            if len(e) < 32 or e[0] == 0x00:
                break
            attr = e[11]
            if attr == 0x0F:
                # A long-name fragment. Deletion overwrites its sequence byte
                # with 0xE5 too, so the ordinal is gone; fragments are stored
                # last-first, so disk order in reverse rebuilds the name.
                lfn.append((e[0] == 0xE5, e[1:11] + e[14:26] + e[28:32]))
                continue
            if attr & 0x08:
                lfn = []
                continue
            if e[0] != 0xE5:
                lfn = []
                continue                            # a live entry; the walk lists it
            hi = struct.unpack_from("<H", e, 20)[0]
            lo = struct.unpack_from("<H", e, 26)[0]
            first = (hi << 16) | lo
            sz = struct.unpack_from("<I", e, 28)[0]
            is_dir = bool(attr & 0x10)
            dead = [chars for was_deleted, chars in lfn if was_deleted]
            lfn = []
            if dead:
                name = "".join(c.decode("utf-16-le", "replace")
                               for c in reversed(dead)).split("\uffff")[0].rstrip("\x00")
            else:
                # the 0xE5 mark sat on the first character; "_" stands in for
                # it, the same placeholder The Sleuth Kit shows for these
                name = _fat_short_name(b"_" + e[1:])
            times = {
                "modified": _dos_stamp(struct.unpack_from("<H", e, 24)[0],
                                       struct.unpack_from("<H", e, 22)[0]),
                "created": _dos_stamp(struct.unpack_from("<H", e, 16)[0],
                                      struct.unpack_from("<H", e, 14)[0], e[13]),
                "accessed date": _dos_date(struct.unpack_from("<H", e, 18)[0]),
            }
            out.append((name, first, sz, is_dir, times))
        return out

    def deleted_files(self, *, min_size=0, max_depth=32):
        """Yield the deleted directory entries of the whole volume.

        A FAT32 delete writes 0xE5 over the first byte of the entry and frees
        its clusters in the FAT; everything else stays. So the name (rebuilt
        from the long-name fragments, whose ordinals the same 0xE5 destroys),
        the first cluster, the size and the recorded times are all still
        there. What is gone is the chain: the FAT entries that said where the
        second cluster onward lay are zeroed. Reading a file longer than one
        cluster therefore assumes it was written in one run, and the result
        says so in ``assumed_contiguous``, because the volume cannot confirm it.
        A file is ``recoverable`` only while every cluster that read would
        touch is still free; a cluster since handed to a live file means the
        assumption is already false, and the file is reported as having
        existed rather than read.

        Live directories are walked to find deleted files inside them, and a
        deleted directory whose first cluster is still free and still parses
        as a directory (it opens with "." and "..") is walked too, since a
        deleted folder of photographs is the common case on a card. A parent
        that was itself deleted is flagged with ``in_deleted_dir``.
        """
        seen = set()

        def walk(node, depth, in_deleted):
            if depth > max_depth or node[0] in seen:
                return
            seen.add(node[0])
            for name, first, sz, is_dir, times in self._deleted_in(node, in_deleted):
                if is_dir:
                    ok_dir = first >= 2 and self._fat_next(first) == 0 and self._looks_like_dir(first)
                    yield FatDeletedFile(name, node[0], True, 0, first, False,
                                         "directory", False, times, in_deleted, None)
                    if ok_dir:
                        yield from walk((first, 0, True), depth + 1, True)
                    continue
                if sz < min_size:
                    continue
                if first < 2 or not sz:
                    yield FatDeletedFile(name, node[0], False, sz, first, False,
                                         "no cluster recorded" if first < 2 else "empty",
                                         False, times, in_deleted, None)
                    continue
                need = (sz + self.cluster_bytes - 1) // self.cluster_bytes
                ok, reason = True, ""
                for k in range(need):
                    if self._fat_next(first + k) != 0:
                        # a cluster in the assumed run belongs to a live file:
                        # either this file was fragmented or it has since been
                        # overwritten, and either way the run cannot be read as it
                        ok, reason = False, ("the run its size would need crosses a live "
                                             "file, so it was fragmented or is overwritten")
                        break
                yield FatDeletedFile(name, node[0], False, sz, first, ok, reason,
                                     need > 1, times, in_deleted, (first, sz, False))
            # deleted files can sit in any live subdirectory too
            for _nm, child, _t in self.listdir_records(node):
                if child[2]:
                    yield from walk(child, depth + 1, in_deleted)

        yield from walk(self.root, 0, False)

    def _looks_like_dir(self, clus):
        """A FAT directory opens with its "." and ".." entries."""
        raw = read_at(self.fh, self._cluster_off(clus), 64)
        return len(raw) == 64 and raw[:11] == b".          " and raw[32:43] == b"..         "

    def read_deleted(self, entry, size=None):
        """The content of a recoverable deleted file, read from its first
        cluster on for its recorded size. Refuses one whose clusters have been
        reused, so overwritten bytes are never presented as the file."""
        if not entry.recoverable or entry._node is None:
            raise NtfsUnreadable(
                f"deleted file {entry.name!r} is not recoverable: {entry.reason}")
        first, sz, _ = entry._node
        want = sz if size is None else min(size, sz)
        need = (want + self.cluster_bytes - 1) // self.cluster_bytes
        out = bytearray()
        for k in range(need):
            out += read_at(self.fh, self._cluster_off(first + k), self.cluster_bytes)
        yield bytes(out[:want])

    def listdir(self, node):
        return [(name, child) for name, child, _times in self.listdir_records(node)]

    def read_file(self, node, size):
        clus, sz, _ = node
        yield self._read_chain(clus, sz)


def _dos_stamp(date, time_, tenths=0):
    """A FAT date and time pair as text, exactly as stored, or "" if unset.

    FAT keeps a wall-clock reading and no zone at all, so this is a reading and
    not an instant, and it is returned as text so that nothing downstream can
    give it one. Seconds are stored in units of two, with an optional tenths
    byte carrying the odd second and hundredths on creation times.
    """
    if not date:
        return ""
    year = 1980 + ((date >> 9) & 0x7F)
    month = (date >> 5) & 0x0F
    day = date & 0x1F
    hour = (time_ >> 11) & 0x1F
    minute = (time_ >> 5) & 0x3F
    second = (time_ & 0x1F) * 2 + (tenths // 100)
    if not (1 <= month <= 12 and 1 <= day <= 31) or hour > 23 or minute > 59 or second > 59:
        return ""
    out = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    hundredths = tenths % 100
    return f"{out}.{hundredths:02d}" if hundredths else out


def _dos_date(date):
    """A FAT date as text, with no time on it.

    FAT records a last-access DATE and no time of day. Rendering it as midnight
    would assert a reading the entry does not carry, so only the date is given.
    """
    if not date:
        return ""
    year = 1980 + ((date >> 9) & 0x7F)
    month = (date >> 5) & 0x0F
    day = date & 0x1F
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return ""
    return f"{year:04d}-{month:02d}-{day:02d}"


def _exfat_stamp(value, tenths=0):
    """An exFAT timestamp as text, exactly as stored. Same packing as FAT."""
    if not value:
        return ""
    return _dos_stamp(value >> 16, value & 0xFFFF, tenths)


def _exfat_offset(byte):
    """An exFAT UTC offset byte as text, exactly as stored, or "" if not set.

    The low seven bits are a signed count of fifteen minute steps and the top
    bit says whether the field was written at all. This is reported rather than
    applied: on the one exFAT volume measured here the stored reading was not
    the writing machine's local clock and this field was the negation of its
    zone, so applying it would assert an instant the evidence does not support.
    """
    if not byte & 0x80:
        return ""
    quarters = byte & 0x7F
    if quarters & 0x40:
        quarters -= 0x80
    minutes = quarters * 15
    sign = "-" if minutes < 0 else "+"
    minutes = abs(minutes)
    return f"{sign}{minutes // 60:02d}:{minutes % 60:02d}"


def _fat_short_name(e):
    # Byte 12 carries Windows NT's case flags for a short name that had no long
    # entry: 0x08 lowercases the base, 0x10 the extension. Honouring them keeps
    # the recorded case of an 8.3 name, which a filename in evidence should hold.
    nt = e[12]
    base = e[0:8].decode("ascii", "replace").rstrip(" ")
    ext = e[8:11].decode("ascii", "replace").rstrip(" ")
    if nt & 0x08:
        base = base.lower()
    if nt & 0x10:
        ext = ext.lower()
    return f"{base}.{ext}" if ext else base


def _vfat_name(lfn):
    parts = sorted(lfn, key=lambda x: x[0])
    raw = b"".join(chunk for _, chunk in parts)
    name = raw.decode("utf-16-le", "replace")
    end = name.find("\uffff")
    if end != -1:
        name = name[:end]
    return name.split("\x00")[0]


class ExfatWalker:
    """List and read files from an exFAT volume, same interface as Fat32Walker.
    A node is (cluster, size, is_dir, fat_chain_flag)."""

    def __init__(self, fh, base):
        self.fh = fh
        self.base = base
        b = read_at(fh, base, 512)
        self.bps = 1 << b[108]
        self.spc = 1 << b[109]
        self.fat_off = struct.unpack_from("<I", b, 80)[0]
        self.heap_off = struct.unpack_from("<I", b, 88)[0]
        self.root_clus = struct.unpack_from("<I", b, 96)[0]
        self.cluster_count = struct.unpack_from("<I", b, 92)[0]
        self.cluster_bytes = self.bps * self.spc
        self.fat_start = base + self.fat_off * self.bps
        self.heap_start = base + self.heap_off * self.bps
        self.root = (self.root_clus, 0, True, False)

    def _fat_next(self, clus):
        raw = read_at(self.fh, self.fat_start + clus * 4, 4)
        if len(raw) < 4:
            return 0xFFFFFFFF                        # truncated image, end of chain
        return struct.unpack_from("<I", raw, 0)[0]

    def _cluster_off(self, clus):
        return self.heap_start + (clus - 2) * self.cluster_bytes

    def _read(self, clus, size, contiguous):
        out = bytearray()
        if contiguous:
            need = size if size else self.cluster_bytes
            n = (need + self.cluster_bytes - 1) // self.cluster_bytes
            for i in range(n):
                out += read_at(self.fh, self._cluster_off(clus + i), self.cluster_bytes)
        else:
            seen = set()
            c = clus
            while 0x2 <= c < 0xFFFFFFF7 and c not in seen:
                seen.add(c)
                out += read_at(self.fh, self._cluster_off(c), self.cluster_bytes)
                if size and len(out) >= size:
                    break
                c = self._fat_next(c)
        return bytes(out[:size]) if size else bytes(out)

    def inode(self, node):
        return node

    def entry(self, node):
        _, size, is_dir, _ = node
        return (0o040000 if is_dir else 0o100000, size, 0)

    def listdir_records(self, node):
        """(name, node, recorded times as stored) for every entry.

        exFAT carries a UTC offset beside each timestamp, unlike FAT. It is
        reported as stored rather than applied, so no instant is asserted.
        """
        clus, _, _, contig = node
        raw = self._read(clus, 0, contig)
        out = []
        i = 0
        while i < len(raw):
            etype = raw[i]
            if etype == 0x00:
                break
            if etype == 0x85:                       # File directory entry
                secs = raw[i + 1]
                s2 = raw[i + 32:i + 64]             # Stream extension (next entry)
                flags = s2[1]
                name_len = s2[3]
                first = struct.unpack_from("<I", s2, 20)[0]
                data_len = struct.unpack_from("<Q", s2, 24)[0]
                is_dir = bool(raw[i + 4] & 0x10)
                contiguous = bool(flags & 0x02)
                # name entries follow, 0xC1, 15 UTF-16 chars each
                name = ""
                for k in range(2, secs + 1):
                    ent = raw[i + 32 * k:i + 32 * k + 32]
                    if not ent or ent[0] != 0xC1:
                        break
                    name += ent[2:32].decode("utf-16-le", "replace")
                name = name[:name_len]
                if name not in (".", ".."):
                    cre, mod, acc = struct.unpack_from("<III", raw, i + 8)
                    out.append((name, (first, data_len, is_dir, contiguous), {
                        "modified": _exfat_stamp(mod, raw[i + 21]),
                        "created": _exfat_stamp(cre, raw[i + 20]),
                        "accessed": _exfat_stamp(acc),
                        "modified utc offset": _exfat_offset(raw[i + 23]),
                        "created utc offset": _exfat_offset(raw[i + 22]),
                        "accessed utc offset": _exfat_offset(raw[i + 24]),
                    }))
                i += 32 * (secs + 1)
            else:
                i += 32
        return out

    def _cluster_in_use(self, clus):
        """True when the Allocation Bitmap marks this cluster used. Read once."""
        bits = getattr(self, "_alloc_bits", None)
        if bits is None:
            bits = b""
            clus_r, _, _, contig = self.root
            raw = self._read(clus_r, 0, contig)
            for i in range(0, len(raw), 32):
                if raw[i] == 0x81:                   # Allocation Bitmap entry
                    first = struct.unpack_from("<I", raw, i + 20)[0]
                    length = struct.unpack_from("<Q", raw, i + 24)[0]
                    bits = self._read(first, length, True)
                    break
            self._alloc_bits = bits
        idx = clus - 2
        if idx < 0 or (idx >> 3) >= len(bits):
            return True                              # off the bitmap: treat as used
        return bool(bits[idx >> 3] & (1 << (idx & 7)))

    def _deleted_in(self, node, in_deleted_dir):
        clus, _, _, contig = node
        raw = self._read(clus, 0, contig)
        out = []
        i = 0
        while i < len(raw):
            etype = raw[i]
            if etype == 0x00:
                break
            if etype == 0x05:                        # File entry with the in-use bit cleared
                secs = raw[i + 1]
                s2 = raw[i + 32:i + 64]
                if len(s2) < 32 or s2[0] not in (0x40, 0xC0):
                    i += 32
                    continue
                flags = s2[1]
                name_len = s2[3]
                first = struct.unpack_from("<I", s2, 20)[0]
                data_len = struct.unpack_from("<Q", s2, 24)[0]
                is_dir = bool(raw[i + 4] & 0x10)
                contiguous = bool(flags & 0x02)
                name = ""
                for k in range(2, secs + 1):
                    ent = raw[i + 32 * k:i + 32 * k + 32]
                    if not ent or ent[0] not in (0x41, 0xC1):
                        break
                    name += ent[2:32].decode("utf-16-le", "replace")
                name = name[:name_len]
                cre, mod, acc = struct.unpack_from("<III", raw, i + 8)
                times = {
                    "modified": _exfat_stamp(mod, raw[i + 21]),
                    "created": _exfat_stamp(cre, raw[i + 20]),
                    "accessed": _exfat_stamp(acc),
                    "modified utc offset": _exfat_offset(raw[i + 23]),
                    "created utc offset": _exfat_offset(raw[i + 22]),
                    "accessed utc offset": _exfat_offset(raw[i + 24]),
                }
                out.append((name, first, data_len, is_dir, contiguous, times))
                i += 32 * (secs + 1)
            else:
                i += 32
        return out

    def deleted_files(self, *, min_size=0, max_depth=32):
        """Yield the deleted directory entries of the whole volume.

        An exFAT delete clears the in-use bit of the entry's type byte (0x85,
        0xC0 and 0xC1 become 0x05, 0x40 and 0x41) and clears the file's bits in
        the Allocation Bitmap; every field survives, including the stream's
        NoFatChain flag, first cluster and length. A file the driver wrote in
        one run carries NoFatChain and is read exactly from its first cluster
        for its length. A fragmented file kept its chain in the FAT; if that
        chain is still intact it is followed, and if it has been cleared the
        file is reported as not recoverable rather than read on an assumption
        the entry itself contradicts. Either way a file is ``recoverable`` only
        while every cluster the read would touch is still free.

        Live directories are walked for deleted files inside them, and a
        deleted directory whose first cluster is still free and still parses
        as a directory is walked too, flagged with ``in_deleted_dir``.
        """
        seen = set()

        def walk(node, depth, in_deleted):
            if depth > max_depth or node[0] in seen:
                return
            seen.add(node[0])
            for name, first, size, is_dir, contiguous, times in self._deleted_in(node, in_deleted):
                if is_dir:
                    ok_dir = (first >= 2 and not self._cluster_in_use(first)
                              and self._looks_like_dir(first))
                    yield FatDeletedFile(name, node[0], True, 0, first, False,
                                         "directory", False, times, in_deleted, None)
                    if ok_dir:
                        yield from walk((first, 0, True, contiguous), depth + 1, True)
                    continue
                if size < min_size:
                    continue
                if first < 2 or not size:
                    yield FatDeletedFile(name, node[0], False, size, first, False,
                                         "no cluster recorded" if first < 2 else "empty",
                                         False, times, in_deleted, None)
                    continue
                need = (size + self.cluster_bytes - 1) // self.cluster_bytes
                ok, reason, chain = True, "", None
                if contiguous:
                    chain = list(range(first, first + need))
                else:
                    chain, c, s2 = [], first, set()
                    while 0x2 <= c < 0xFFFFFFF7 and c not in s2 and len(chain) < need:
                        chain.append(c); s2.add(c); c = self._fat_next(c)
                    if len(chain) < need:
                        ok, reason, chain = False, "the FAT chain was cleared on delete", None
                if ok and any(self._cluster_in_use(c) for c in chain):
                    ok, reason = False, "clusters reused by a later file"
                yield FatDeletedFile(name, node[0], False, size, first, ok, reason,
                                     False, times, in_deleted,
                                     (chain, size) if ok else None)
            for _nm, child, _t in self.listdir_records(node):
                if child[2]:
                    yield from walk(child, depth + 1, in_deleted)

        yield from walk(self.root, 0, False)

    def _looks_like_dir(self, clus):
        """An exFAT directory's first entry is a real entry type (a set or a
        cleared in-use bit over the file, stream, name or bitmap kinds)."""
        raw = read_at(self.fh, self._cluster_off(clus), 32)
        return len(raw) == 32 and (raw[0] & 0x7F) in (0x05, 0x40, 0x41, 0x01, 0x02, 0x03)

    def read_deleted(self, entry, size=None):
        """The content of a recoverable deleted file, cluster by cluster along
        the chain that was kept or the run the entry declared. Refuses one whose
        clusters have been reused, so overwritten bytes are never presented as
        the file."""
        if not entry.recoverable or entry._node is None:
            raise NtfsUnreadable(
                f"deleted file {entry.name!r} is not recoverable: {entry.reason}")
        chain, sz = entry._node
        want = sz if size is None else min(size, sz)
        out = bytearray()
        for c in chain:
            out += read_at(self.fh, self._cluster_off(c), self.cluster_bytes)
            if len(out) >= want:
                break
        yield bytes(out[:want])

    def listdir(self, node):
        return [(name, child) for name, child, _times in self.listdir_records(node)]

    def free_extents(self, min_bytes=0):
        """[(byte offset, length)] for the runs of space the volume says are free.

        exFAT does not use its FAT to say what is in use, the way FAT32 does. It
        keeps an Allocation Bitmap, one bit per cluster, and finds it through a
        directory entry of type 0x81 in the root directory. A set bit means the
        cluster is not available, so what is left is where deleted content
        survives until something overwrites it.

        Field offsets are from Microsoft's exFAT specification: the bitmap entry
        gives FirstCluster at 20 and DataLength at 24 (section 7.1), the boot
        sector gives ClusterCount at 92 (section 3.1), and the first bit of the
        bitmap is the lowest bit of the first byte and stands for cluster 2.

        Offsets are into the image rather than the volume, so a caller reading
        the whole disk can use them directly. ``min_bytes`` drops runs too short
        to hold anything worth recovering. An empty list means the bitmap was not
        found, which a caller must not read as "nothing is free".
        """
        cluster = self.cluster_bytes
        if not cluster or not self.cluster_count:
            return []
        first_clus = length = 0
        raw = self._read(self.root_clus, 0, False)
        for i in range(0, len(raw) - 31, 32):
            if raw[i] == 0x00:                       # end of the directory
                break
            if raw[i] != 0x81:
                continue
            if raw[i + 1] & 0x01:                    # the second TexFAT bitmap
                continue
            first_clus = struct.unpack_from("<I", raw, i + 20)[0]
            length = struct.unpack_from("<Q", raw, i + 24)[0]
            break
        if not first_clus or not length:
            return []
        bits = self._read(first_clus, length, False)
        total = min(len(bits) * 8, self.cluster_count)

        runs, run_start, pos = [], None, 0
        while pos < total:
            byte = bits[pos >> 3]
            if not (pos & 7) and pos + 8 <= total and byte in (0x00, 0xFF):
                if byte == 0x00:                     # eight free clusters
                    if run_start is None:
                        run_start = pos
                elif run_start is not None:          # eight used ones
                    runs.append((run_start, pos - run_start))
                    run_start = None
                pos += 8
                continue
            if byte & (1 << (pos & 7)):
                if run_start is not None:
                    runs.append((run_start, pos - run_start))
                    run_start = None
            elif run_start is None:
                run_start = pos
            pos += 1
        if run_start is not None:
            runs.append((run_start, total - run_start))

        out = []
        for first, n in runs:
            size = n * cluster
            if size >= min_bytes:
                out.append((self._cluster_off(first + 2), size))
        return out

    def read_file(self, node, size):
        clus, sz, _, contig = node
        yield self._read(clus, sz, contig)


# ---------------------------------------------------------------------------
# QNX4 (the QNX 4 filesystem, distinct from the qnx6 this tool is named for).
#
# QNX 4 shipped from 1990 and its filesystem is still met on older embedded
# and industrial systems. Every constant and field offset below is read out of
# the Linux kernel's own read-only qnx4 driver, the same sourcing as the qnx6
# code above:
#
#   QNX4_SUPER_MAGIC 0x002f          include/uapi/linux/magic.h:54
#   struct qnx4_inode_entry           include/uapi/linux/qnx4_fs.h:44
#   struct qnx4_link_info             include/uapi/linux/qnx4_fs.h:63
#   struct qnx4_xblk                  include/uapi/linux/qnx4_fs.h:71
#   field widths (le16/le32/u8)       include/uapi/linux/qnxtypes.h
#   union qnx4_directory_entry        fs/qnx4/qnx4.h:75
#
# The layout, in one paragraph. Blocks are 512 bytes and every block number
# stored on disk is 1-based: block 1 is the boot block at offset 0, block 2
# the superblock at offset 512. The superblock is four 64-byte inode entries,
# RootDir/Inode/Boot/AltBoot; RootDir's name "/" doubles as the 0x002f magic
# (fs/qnx4/inode.c qnx4_checkroot(), which also refuses to mount unless the
# root directory carries a ".bitmap" entry). A directory's data is a run of
# 64-byte entries: a name of up to 16 bytes is a full inode entry stored
# inline, a longer name (up to 48) is a qnx4_link_info pointing at the real
# inode entry by (block, index), conventionally inside the ".inodes" file
# (fs/qnx4/dir.c, fs/qnx4/namei.c; the status byte at offset 63 says which:
# 0x08 QNX4_FILE_LINK, else 0x01 QNX4_FILE_USED inline). A file's data is a
# run of extents: the first lives in the inode, extents 2..n in a chain of
# xblk blocks whose signature is "IamXblk" (fs/qnx4/inode.c qnx4_block_map()).
# The kernel addresses an inode entry as ino = block * 8 + index, and the same
# convention is used for the walker's node numbers, so root is inode 8
# (QNX4_ROOT_INO * QNX4_INODES_PER_BLOCK, fs/qnx4/inode.c:233).
#
# Validated by round-trip against the Linux kernel driver itself: a fixture
# populated with nested directories, a multi-extent file, a long name, a
# symlink, an empty file and distinct modes, owners and mtimes was mounted
# read-only with fs/qnx4 (kernel 7.0.0) and every name, mode, owner, size,
# mtime, symlink target and byte of content the kernel reported was required
# to match what this walker reads. The fixture generator is a separate
# program, not this parser, and its skeleton follows Peter Waechtler's dinit
# 0.1 (the Linux-side QNX4 formatter, GPL-2), a second, independent statement
# of the same layout. Synthetic-only validation: no confirmed real QNX4
# volume exists in the test corpus.
# ---------------------------------------------------------------------------
QNX4_BLOCK = 512
QNX4_DIRENT = 64
QNX4_ROOT_NODE = 8            # QNX4_ROOT_INO(1) * QNX4_INODES_PER_BLOCK(8)
QNX4_F_USED, QNX4_F_LINK = 0x01, 0x08
QNX4_XBLK_SIG = b"IamXblk"    # fs/qnx4/inode.c:110 checks these 7 bytes


# ---------------------------------------------------------------- NTFS
# Field offsets and structure layouts below come from the Linux-NTFS project's
# published NTFS documentation (Richard Russon and Yuval Fledel, "NTFS
# Documentation", https://flatcap.github.io/linux-ntfs/ntfs/), which describes
# the on-disk format independently of any implementation, and are confirmed
# against a volume written by mkntfs. No NTFS implementation's source was read
# for this: ntfs-3g and The Sleuth Kit are both under licences this file is not.

NTFS_OEM = b"NTFS    "
NTFS_ROOT = 5                       # the root directory is always MFT record 5
NTFS_FILE = b"FILE"
NTFS_INDX = b"INDX"

# attribute types this walker reads
NTFS_STANDARD_INFORMATION = 0x10
NTFS_ATTRIBUTE_LIST       = 0x20
NTFS_FILE_NAME            = 0x30
NTFS_DATA                 = 0x80
NTFS_INDEX_ROOT           = 0x90
NTFS_INDEX_ALLOCATION     = 0xA0
NTFS_END                  = 0xFFFFFFFF

NTFS_ATTR_COMPRESSED = 0x0001
NTFS_ATTR_ENCRYPTED  = 0x4000
NTFS_ATTR_SPARSE     = 0x8000

NTFS_BITMAP       = 6            # $Bitmap: one bit per cluster, set when in use
NTFS_MFT_IN_USE   = 0x0001
NTFS_MFT_IS_DIR   = 0x0002

# FILETIME counts 100 ns ticks from 1601-01-01 UTC; this is the gap to the Unix epoch.
NTFS_EPOCH_DELTA = 11644473600


class NtfsUnreadable(Exception):
    """A file whose bytes this walker will not guess at (encrypted, or an
    attribute shape it does not implement). Raised rather than returning short
    data, because a short read here would be indistinguishable from a small file."""


def ntfs_time(v):
    """A FILETIME as Unix seconds, or 0 when it is unset or out of range."""
    if not v:
        return 0
    sec = v / 10_000_000 - NTFS_EPOCH_DELTA
    return sec if -12219292800 < sec < 253402300799 else 0


def _ntfs_std_times(attrs):
    """(created, modified, accessed) from a record's $STANDARD_INFORMATION, as
    Unix seconds, each 0 where the attribute is absent or too short to hold it.

    The attribute holds four FILETIMEs: created at 0, last written at 8, the
    record's own last change at 16, last read at 24. $FILE_NAME carries a second
    set of the same four, and the two are not kept in step: on the committed
    fixture a file's accessed time here is fifteen seconds later than the one its
    $FILE_NAME holds, which is what an examiner asking when a file was last read
    means. Every reader of the attribute goes through this one function so the
    three offsets cannot drift apart between a listing, a live file and a deleted
    record. Each field is guarded on its own length, so a short attribute yields
    the fields it does hold rather than nothing.
    """
    for a in attrs:
        if a.type == NTFS_STANDARD_INFORMATION and a.resident:
            v = a.value
            created = ntfs_time(struct.unpack_from("<Q", v, 0)[0]) if len(v) >= 8 else 0
            modified = ntfs_time(struct.unpack_from("<Q", v, 8)[0]) if len(v) >= 16 else 0
            accessed = ntfs_time(struct.unpack_from("<Q", v, 24)[0]) if len(v) >= 32 else 0
            return created, modified, accessed
    return 0, 0, 0


def _ntfs_fixup(buf, per, name):
    """Apply the update sequence array to a multi-sector record.

    NTFS stamps the last two bytes of every sector of a record with one value
    and keeps the real bytes in an array in the header, so a torn write is
    detectable. The record cannot be parsed until they are put back.
    """
    if len(buf) < 8:
        return None
    if buf[0:4] != name:
        return None
    off, count = struct.unpack_from("<HH", buf, 4)
    if count < 1 or off + count * 2 > len(buf):
        return None
    usn = buf[off:off + 2]
    out = bytearray(buf)
    for i in range(count - 1):
        end = (i + 1) * per
        if end > len(out):
            break
        if bytes(out[end - 2:end]) != usn:
            return None                 # a sector that was not written with the rest
        out[end - 2:end] = buf[off + 2 + i * 2: off + 4 + i * 2]
    return bytes(out)


def _ntfs_runs(data, offset, cluster_count):
    """Decode a mapping-pair list into [(lcn or None, clusters)], in VCN order.

    Each pair is a header byte giving the width of a length field and of an
    offset field, then those two fields. The offset is signed and relative to
    the previous run's start, and a zero-width offset means the run is sparse:
    it occupies VCNs and no clusters, and reads as zeros.
    """
    runs, pos, lcn, seen = [], offset, 0, 0
    while pos < len(data):
        head = data[pos]
        if head == 0:
            break
        len_size, off_size = head & 0x0F, head >> 4
        pos += 1
        if len_size == 0 or pos + len_size + off_size > len(data):
            return None
        length = int.from_bytes(data[pos:pos + len_size], "little", signed=False)
        pos += len_size
        if off_size:
            delta = int.from_bytes(data[pos:pos + off_size], "little", signed=True)
            pos += off_size
            lcn += delta
            runs.append((lcn, length))
        else:
            runs.append((None, length))     # sparse
        seen += length
        if cluster_count and seen > cluster_count + 1:
            return None                      # the list describes more than the attribute holds
    return runs


class _NtfsAttr:
    """One attribute of an MFT record, resident or not."""

    __slots__ = ("type", "name", "flags", "resident", "value", "runs",
                 "data_size", "alloc_size", "init_size", "comp_unit", "start_vcn")

    def __init__(self, type_, name, flags, resident):
        self.type, self.name, self.flags, self.resident = type_, name, flags, resident
        self.value = b""
        self.runs = []
        self.data_size = self.alloc_size = self.init_size = 0
        self.comp_unit = 0
        self.start_vcn = 0

    @property
    def compressed(self):
        return bool(self.flags & NTFS_ATTR_COMPRESSED) and self.comp_unit

    @property
    def encrypted(self):
        return bool(self.flags & NTFS_ATTR_ENCRYPTED)


class NtfsDeletedFile:
    """One file whose MFT record is free but still describes it.

    ``recoverable`` says whether the content can still be read: a resident file
    always (its bytes are in the record), a non-resident one only while every
    cluster it used is still free. ``reason`` names why not, when it is False.
    """

    __slots__ = ("record", "name", "parent", "is_dir", "size", "resident",
                 "recoverable", "reason", "created", "modified", "accessed",
                 "has_attribute_list", "_data")

    def __init__(self, record, name, parent, is_dir, size, resident,
                 recoverable, reason, created, modified, accessed,
                 has_attribute_list, data):
        self.record, self.name, self.parent = record, name, parent
        self.is_dir, self.size = is_dir, size
        self.resident, self.recoverable, self.reason = resident, recoverable, reason
        self.created, self.modified, self.accessed = created, modified, accessed
        self.has_attribute_list = has_attribute_list
        self._data = data

    def __repr__(self):
        state = "recoverable" if self.recoverable else f"not recoverable ({self.reason})"
        return (f"NtfsDeletedFile(rec={self.record}, name={self.name!r}, "
                f"size={self.size}, {'resident' if self.resident else 'non-resident'}, "
                f"{state})")


class NtfsWalker:
    """List and read files from an NTFS volume, same interface as the walkers
    above. A node is the MFT record number, which is what a directory index
    stores and what makes two names for one file resolve to one record.

    What it reads: resident and non-resident $DATA, sparse runs, LZNT1
    compressed data, attributes that overflow into other records through
    $ATTRIBUTE_LIST, and directory indexes in both their resident ($INDEX_ROOT)
    and allocated ($INDEX_ALLOCATION) forms, with the sector fixups applied.

    What it does not read: an encrypted file's content, which needs a key the
    volume does not hold. Those are listed with their recorded size and refuse
    to be read rather than yielding the ciphertext as though it were the file.
    Only the unnamed $DATA stream is the file's content; a named stream is
    reported through named_streams() and never as a file of its own.
    """

    root = NTFS_ROOT

    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        boot = read_at(fh, base, 512)
        if len(boot) < 512 or boot[3:11] != NTFS_OEM:
            raise ValueError("not an NTFS boot sector")
        self.bps = struct.unpack_from("<H", boot, 11)[0]
        self.spc = boot[13]
        if not self.bps or not self.spc:
            raise ValueError("NTFS boot sector gives a zero sector or cluster size")
        self.cluster = self.bps * self.spc
        self.total_sectors = struct.unpack_from("<Q", boot, 40)[0]
        self.mft_lcn = struct.unpack_from("<Q", boot, 48)[0]
        self.mftmirr_lcn = struct.unpack_from("<Q", boot, 56)[0]
        self.rec_size = self._sized(struct.unpack_from("<b", boot, 64)[0])
        self.idx_size = self._sized(struct.unpack_from("<b", boot, 68)[0])
        self.serial = struct.unpack_from("<Q", boot, 72)[0]
        self.volume_size = self.total_sectors * self.bps
        self._records = {}                       # record number -> attributes
        self._alloc_bitmap = None                # $Bitmap bytes, read on first need
        self._mft_runs = None
        self._mft_runs = self._read_mft_runs()

    def _sized(self, raw):
        """A size field that is a cluster count when positive and a power of two
        byte count when negative, which is how a 1 KiB record fits a 4 KiB cluster."""
        return raw * self.cluster if raw > 0 else 1 << (-raw)

    # -- raw access --------------------------------------------------------
    def _read_runs(self, runs, want, start=0):
        """Bytes from a run list, sparse runs reading as the zeros they stand for."""
        out = bytearray()
        pos = 0
        for lcn, count in runs:
            span = count * self.cluster
            if pos + span <= start:
                pos += span
                continue
            skip = max(0, start - pos)
            take = min(span - skip, want - len(out))
            if lcn is None:
                out += b"\x00" * take
            else:
                out += read_at(self.fh, self.base + lcn * self.cluster + skip, take)
            pos += span
            if len(out) >= want:
                break
        return bytes(out[:want])

    def _read_mft_runs(self):
        """The $MFT's own data runs, read from record 0, which sits at a cluster
        the boot sector names. Every other record is then found through them."""
        off = self.base + self.mft_lcn * self.cluster
        raw = _ntfs_fixup(read_at(self.fh, off, self.rec_size), self.bps, NTFS_FILE)
        if raw is None:
            raise ValueError("the MFT's own record is unreadable")
        attrs = self._parse_attrs(raw, follow_list=False)
        for a in attrs:
            if a.type == NTFS_DATA and not a.name and not a.resident:
                return a.runs
        raise ValueError("the MFT record carries no non-resident data attribute")

    def _record(self, num):
        """The attributes of one MFT record, cached."""
        got = self._records.get(num)
        if got is None:
            off = num * self.rec_size
            raw = self._read_runs(self._mft_runs, self.rec_size, off) if self._mft_runs \
                else read_at(self.fh, self.base + self.mft_lcn * self.cluster + off,
                             self.rec_size)
            fixed = _ntfs_fixup(raw, self.bps, NTFS_FILE)
            got = self._parse_attrs(fixed, self_ref=num) if fixed else []
            self._records[num] = got
        return got

    def _parse_attrs(self, raw, follow_list=True, self_ref=None):
        """Every attribute in one record, plus those its $ATTRIBUTE_LIST points at.

        A record that runs out of room moves attributes into other records and
        leaves a list saying where they went. Following it is what makes a very
        fragmented file readable, since its run list is what overflowed.
        """
        if not raw or len(raw) < 0x30:
            return []
        seq = struct.unpack_from("<H", raw, 0x10)[0]
        first, flags = struct.unpack_from("<HH", raw, 0x14)
        used = struct.unpack_from("<I", raw, 0x18)[0]
        if not flags & NTFS_MFT_IN_USE:
            return []
        out, pos, limit = [], first, min(used or len(raw), len(raw))
        while pos + 4 <= limit:
            type_ = struct.unpack_from("<I", raw, pos)[0]
            if type_ == NTFS_END:
                break
            if pos + 16 > limit:
                break
            length = struct.unpack_from("<I", raw, pos + 4)[0]
            if length < 16 or pos + length > limit:
                break
            attr = self._parse_one(raw, pos, length)
            if attr:
                out.append(attr)
            pos += length
        marker = _NtfsAttr(-1, "", flags, True)          # carries the record flags
        marker.data_size = seq                           # and its sequence number
        out.append(marker)
        if follow_list:
            out.extend(self._follow_attribute_list(out, self_ref))
        return out

    def _parse_one(self, raw, pos, length):
        type_ = struct.unpack_from("<I", raw, pos)[0]
        nonres = raw[pos + 8]
        name_len = raw[pos + 9]
        name_off = struct.unpack_from("<H", raw, pos + 10)[0]
        flags = struct.unpack_from("<H", raw, pos + 12)[0]
        name = ""
        if name_len:
            end = pos + name_off + name_len * 2
            if end <= pos + length:
                name = raw[pos + name_off:end].decode("utf-16-le", "replace")
        attr = _NtfsAttr(type_, name, flags, not nonres)
        if not nonres:
            vlen, voff = struct.unpack_from("<IH", raw, pos + 16)
            if pos + voff + vlen > pos + length:
                return None
            attr.value = raw[pos + voff:pos + voff + vlen]
            attr.data_size = vlen
            return attr
        start_vcn, last_vcn = struct.unpack_from("<QQ", raw, pos + 16)
        run_off, comp = struct.unpack_from("<HH", raw, pos + 32)
        alloc, real, init = struct.unpack_from("<QQQ", raw, pos + 40)
        attr.start_vcn, attr.comp_unit = start_vcn, comp
        attr.alloc_size, attr.data_size, attr.init_size = alloc, real, init
        if run_off >= length:
            return None
        attr.runs = _ntfs_runs(raw[pos:pos + length], run_off,
                               last_vcn - start_vcn + 1) or []
        return attr

    def _follow_attribute_list(self, attrs, self_ref=None):
        """Attributes this record delegated to others, read from those records.

        The list names every attribute of the file, including the ones that
        stayed put, so it points back at this record too. Reading that one again
        would count its attributes twice: measured on a 333-run file, the data
        runs came out at 537 and the file read long and wrong.
        """
        extra, seen = [], set()
        for a in attrs:
            if a.type != NTFS_ATTRIBUTE_LIST:
                continue
            data = a.value if a.resident else self._read_runs(a.runs, a.data_size)
            pos = 0
            while pos + 26 <= len(data):
                rec_len = struct.unpack_from("<H", data, pos + 4)[0]
                if rec_len < 26 or pos + rec_len > len(data):
                    break
                ref = struct.unpack_from("<Q", data, pos + 16)[0] & 0xFFFFFFFFFFFF
                if ref and ref != self_ref and ref not in seen:
                    seen.add(ref)
                pos += rec_len
        for ref in seen:
            off = ref * self.rec_size
            raw = self._read_runs(self._mft_runs, self.rec_size, off)
            fixed = _ntfs_fixup(raw, self.bps, NTFS_FILE)
            if fixed:
                extra.extend(a for a in self._parse_attrs(fixed, follow_list=False)
                             if a.type not in (-1, NTFS_ATTRIBUTE_LIST))
        return extra

    # -- the walker surface ------------------------------------------------
    def _data_attr(self, num, name=""):
        """The named (or unnamed) $DATA attribute, with the runs of every piece
        joined: a file whose run list overflowed carries one $DATA per VCN span."""
        parts = [a for a in self._record(num)
                 if a.type == NTFS_DATA and a.name == name]
        if not parts:
            return None
        resident = [a for a in parts if a.resident]
        if resident:
            return resident[0]
        parts.sort(key=lambda a: a.start_vcn)
        head = parts[0]
        joined = _NtfsAttr(NTFS_DATA, name, head.flags, False)
        joined.comp_unit = head.comp_unit
        joined.alloc_size = max(a.alloc_size for a in parts)
        joined.data_size = max(a.data_size for a in parts)
        joined.init_size = max(a.init_size for a in parts)
        for a in parts:
            joined.runs.extend(a.runs)
        return joined

    def _cluster_in_use(self, lcn):
        """True when this cluster is marked allocated in $Bitmap. The bitmap is
        read once and kept: a deleted-file sweep asks about many clusters."""
        bits = self._alloc_bitmap
        if bits is None:
            attr = self._data_attr(NTFS_BITMAP)
            size = (len(attr.value) if attr.resident else attr.data_size) if attr else 0
            bits = b"".join(self.read_file(NTFS_BITMAP, size)) if size else b""
            self._alloc_bitmap = bits
        byte = lcn >> 3
        if byte >= len(bits):
            return True                              # off the end of the bitmap: treat as used
        return bool(bits[byte] & (1 << (lcn & 7)))

    def _parse_deleted(self, raw):
        """Attributes of one record, ignoring the in-use flag and NOT following
        its $ATTRIBUTE_LIST.

        The live parser stops at a record not in use; a deleted file is exactly
        such a record, so that guard is dropped here. The list is not followed
        on purpose: for a deleted record it points at other records that may
        since have been reused, so following it would splice a live file's
        attributes into this one.
        """
        if not raw or len(raw) < 0x30:
            return None
        first, flags = struct.unpack_from("<HH", raw, 0x14)
        used = struct.unpack_from("<I", raw, 0x18)[0]
        out, pos, limit = [], first, min(used or len(raw), len(raw))
        while pos + 16 <= limit:
            type_ = struct.unpack_from("<I", raw, pos)[0]
            if type_ == NTFS_END:
                break
            length = struct.unpack_from("<I", raw, pos + 4)[0]
            if length < 16 or pos + length > limit:
                break
            attr = self._parse_one(raw, pos, length)
            if attr:
                out.append(attr)
            pos += length
        return flags, out

    def _record_raw(self, num):
        off = num * self.rec_size
        raw = self._read_runs(self._mft_runs, self.rec_size, off) if self._mft_runs \
            else read_at(self.fh, self.base + self.mft_lcn * self.cluster + off,
                         self.rec_size)
        return _ntfs_fixup(raw, self.bps, NTFS_FILE)

    def deleted_files(self, *, include_system=False, min_size=0):
        """Yield the files whose MFT record is free but still names them.

        A deleted file whose record has not yet been handed to another file can
        be recovered from the record: its name, size, dates, and, when the data
        has not been overwritten, its content. This is the only route to a file
        whose data was **resident**, small enough to live inside the record and
        so never occupying a cluster a carver could find.

        Each result carries ``recoverable``: True when the bytes are still there
        (resident always; non-resident only while every cluster it used is still
        free), False when they have been reused, in which case the record is
        reported as evidence the file existed rather than its content offered.
        ``$ATTRIBUTE_LIST`` is not followed (see ``_parse_deleted``), so a file
        whose attributes overflowed its record is reported not recoverable rather
        than reconstructed from records that may now belong elsewhere.

        ``include_system`` keeps the ``$``-named metadata files; by default only
        ordinary files are yielded. ``min_size`` drops anything smaller.
        """
        data_attr = self._data_attr(0)              # $MFT's own $DATA
        if data_attr is None:
            return
        count = data_attr.data_size // self.rec_size
        for num in range(count):
            if num < 16 and not include_system:
                continue                            # 0-15 are the reserved metafiles
            raw = self._record_raw(num)
            if not raw or raw[:4] != NTFS_FILE:
                continue
            parsed = self._parse_deleted(raw)
            if parsed is None:
                continue
            flags, attrs = parsed
            if flags & NTFS_MFT_IN_USE:
                continue                            # a live file; the walk lists it
            names = []
            for a in attrs:
                if a.type == NTFS_FILE_NAME and a.resident and len(a.value) > 0x42:
                    nlen, ns = a.value[0x40], a.value[0x41]
                    parent = struct.unpack_from("<Q", a.value, 0)[0] & 0xFFFFFFFFFFFF
                    nm = a.value[0x42:0x42 + nlen * 2].decode("utf-16-le", "replace")
                    names.append((ns, nm, parent))
            if not names:
                continue                            # nothing names it
            names.sort(key=lambda n: n[0] == 2)     # prefer a long name over the 8.3 alias
            _ns, name, parent = names[0]
            if not include_system and name.startswith("$"):
                continue
            is_dir = bool(flags & NTFS_MFT_IS_DIR)
            has_list = any(a.type == NTFS_ATTRIBUTE_LIST for a in attrs)
            created, modified, accessed = _ntfs_std_times(attrs)
            data = next((a for a in attrs if a.type == NTFS_DATA and a.name == ""), None)
            if is_dir or data is None:
                yield NtfsDeletedFile(num, name, parent, is_dir, 0, True, False,
                                      "directory" if is_dir else "no data attribute",
                                      created, modified, accessed, has_list, None)
                continue
            size = len(data.value) if data.resident else data.data_size
            if size < min_size:
                continue
            if data.resident:
                yield NtfsDeletedFile(num, name, parent, is_dir, size, True, True, "",
                                      created, modified, accessed, has_list, data)
                continue
            reason, ok = "", True
            if data.encrypted:
                reason, ok = "encrypted", False
            elif has_list:
                reason, ok = "attributes overflowed the record", False
            else:
                for lcn, run in data.runs:
                    if lcn is None:
                        continue                    # a sparse run holds no data to lose
                    if any(self._cluster_in_use(lcn + i) for i in range(run)):
                        reason, ok = "clusters reused by a later file", False
                        break
            yield NtfsDeletedFile(num, name, parent, is_dir, size, False, ok, reason,
                                  created, modified, accessed, has_list, data)

    def read_deleted(self, entry, size=None):
        """Yield the content of a recoverable deleted file. Refuses one whose
        clusters have been reused, so overwritten data is never presented as the
        file. Reading is otherwise the same as for a live file."""
        if not entry.recoverable or entry._data is None:
            raise NtfsUnreadable(
                f"deleted file {entry.name!r} is not recoverable: {entry.reason}")
        data = entry._data
        want = entry.size if size is None else min(size, entry.size)
        if data.resident:
            yield data.value[:want]
            return
        if data.compressed:
            yield from self._read_compressed(data, want)
            return
        real = min(want, data.init_size) if data.init_size else 0
        done = 0
        while done < real:
            chunk = self._read_runs(data.runs, min(1 << 20, real - done), done)
            if not chunk:
                break
            yield chunk
            done += len(chunk)
        while done < want:
            take = min(1 << 20, want - done)
            yield b"\x00" * take
            done += take

    def volume_label(self):
        """The volume label, from the $VOLUME_NAME attribute of record 3, or None
        when the record cannot be read. An empty string means the volume has none."""
        for a in self._record(3):
            if a.type == 0x60 and a.resident:
                return a.value.decode("utf-16-le", "replace")
        return "" if self._record(3) else None

    def _flags(self, num):
        for a in self._record(num):
            if a.type == -1:
                return a.flags
        return 0

    def _seq(self, num):
        """This record's sequence number, or None if the record is not in use.

        NTFS bumps it every time a record is freed and handed out again, so it
        is what tells a live directory entry from one naming a record that has
        since become something else."""
        for a in self._record(num):
            if a.type == -1:
                return a.data_size
        return None

    def inode(self, num):
        return num

    def entry(self, num):
        attrs = self._record(num)
        if not attrs:
            return None
        is_dir = bool(self._flags(num) & NTFS_MFT_IS_DIR)
        mtime = _ntfs_std_times(attrs)[1]
        if is_dir:
            return (S_IFDIR | 0o755, 0, mtime)
        data = self._data_attr(num)
        size = 0 if data is None else (len(data.value) if data.resident else data.data_size)
        return (0o100644, size, mtime)

    def stamps(self, num):
        """The instants a live file's $STANDARD_INFORMATION holds, as
        (created, modified, accessed) in Unix seconds, 0 where unset.

        ``entry`` returns only the modified time, which is what a listing needs.
        A caller carrying a file's dates into a record wants all three, and they
        are instants rather than readings: FILETIME counts from a UTC epoch, so
        unlike a FAT or exFAT stamp these can be placed on a timeline. The record
        is cached, so asking after ``entry`` reads nothing more from the image.
        """
        return _ntfs_std_times(self._record(num))

    def free_extents(self, min_bytes=0):
        """[(byte offset, length)] for the runs of space the volume says are free.

        NTFS records one bit per cluster in $Bitmap, the unnamed $DATA of MFT
        record 6, set when the cluster is in use. What is left is where deleted
        content survives until something overwrites it, and it is the only part
        of a volume a carver can tell apart from a live file: a signature found
        inside an allocated run belongs to a file the tree already names.

        Offsets are into the image rather than the volume, so a caller reading
        the whole disk can use them directly. ``min_bytes`` drops runs too short
        to hold anything worth recovering.

        Whole bytes of the bitmap are tested before their bits are, because a
        volume of this size has tens of millions of clusters and almost all of
        them sit in runs: on a 237.6 GiB volume that is 62,289,344 clusters, and
        looking at each one individually is not worth doing.
        """
        attr = self._data_attr(NTFS_BITMAP)
        if attr is None:
            return []
        size = len(attr.value) if attr.resident else attr.data_size
        if not size:
            return []
        bits = b"".join(self.read_file(NTFS_BITMAP, size))
        clusters = (self.total_sectors * self.bps) // self.cluster
        total = min(len(bits) * 8, clusters or len(bits) * 8)

        runs, run_start = [], None
        pos = 0
        while pos < total:
            byte = bits[pos >> 3]
            if not (pos & 7) and pos + 8 <= total and byte in (0x00, 0xFF):
                if byte == 0x00:                     # eight free clusters
                    if run_start is None:
                        run_start = pos
                else:                                # eight used ones
                    if run_start is not None:
                        runs.append((run_start, pos - run_start))
                        run_start = None
                pos += 8
                continue
            if byte & (1 << (pos & 7)):
                if run_start is not None:
                    runs.append((run_start, pos - run_start))
                    run_start = None
            elif run_start is None:
                run_start = pos
            pos += 1
        if run_start is not None:
            runs.append((run_start, total - run_start))

        out = []
        for first, count in runs:
            length = count * self.cluster
            if length >= min_bytes:
                out.append((self.base + first * self.cluster, length))
        return out

    def named_streams(self, num):
        """[(name, size)] for every alternate data stream on this record. A named
        stream is content the file's own size does not account for, so it is worth
        reporting; it is not listed as a file, because it has no name of its own."""
        out = []
        for a in self._record(num):
            if a.type == NTFS_DATA and a.name:
                out.append((a.name, len(a.value) if a.resident else a.data_size))
        return out

    def listdir(self, num):
        """(name, record) for every entry of a directory index.

        The index lives in $INDEX_ROOT while it is small and moves into
        $INDEX_ALLOCATION blocks when it grows; both hold the same entry shape,
        so both are walked with one reader.
        """
        out, seen = [], set()
        root = alloc = None
        for a in self._record(num):
            if a.type == NTFS_INDEX_ROOT and a.name == "$I30":
                root = a
            elif a.type == NTFS_INDEX_ALLOCATION and a.name == "$I30":
                alloc = a
        if root is None:
            return out
        # $INDEX_ROOT: a small header, then the index header at 0x10
        if len(root.value) >= 0x20:
            self._index_entries(root.value, 0x10, out, seen)
        if alloc is not None and alloc.runs:
            total = alloc.data_size or alloc.alloc_size
            step = self.idx_size
            for off in range(0, total, step):
                block = _ntfs_fixup(self._read_runs(alloc.runs, step, off),
                                    self.bps, NTFS_INDX)
                if block and len(block) >= 0x28:
                    self._index_entries(block, 0x18, out, seen)
        return out

    def _index_entries(self, buf, header_off, out, seen):
        """Append the entries of one index header. Entry offsets are relative to
        the header, not to the record, which is why the caller passes its offset."""
        if header_off + 16 > len(buf):
            return
        first, total = struct.unpack_from("<II", buf, header_off)
        pos = header_off + first
        end = min(header_off + total, len(buf))
        while pos + 0x52 <= end:
            ref, elen, klen, eflags = struct.unpack_from("<QHHH", buf, pos)
            if elen < 0x10 or pos + elen > end:
                break
            if eflags & 0x02:                       # the last entry holds no name
                break
            rec = ref & 0xFFFFFFFFFFFF
            want_seq = ref >> 48
            if klen >= 0x42:
                name_len = buf[pos + 0x50]
                namespace = buf[pos + 0x51]
                nstart = pos + 0x52
                nend = nstart + name_len * 2
                if nend <= pos + elen:
                    name = buf[nstart:nend].decode("utf-16-le", "replace")
                    # Namespace 2 is the 8.3 name of a file that also has a long
                    # one, indexed beside it. Reporting both would list every such
                    # file twice under two names. The root's index also carries an
                    # entry for the root itself, which is a loop, not a child.
                    # The top 16 bits of the reference are the generation the
                    # entry was written for. A record that has since been freed
                    # and reused carries a different one, and following it
                    # attaches whatever the record became to this name: on one
                    # Windows volume that put a 501 KB update installer, and the
                    # directory holding it, under a browser cache folder.
                    # A zero means the writer asked for no check.
                    got_seq = self._seq(rec)
                    stale = (want_seq and got_seq is not None and want_seq != got_seq)
                    if (namespace != 2 and name not in (".", "..") and not stale
                            and (rec, name) not in seen):
                        seen.add((rec, name))
                        out.append((name, rec))
            pos += elen

    def read_file(self, num, size):
        data = self._data_attr(num)
        if data is None:
            return
        if data.resident:
            yield data.value[:size] if size else data.value
            return
        if data.encrypted:
            raise NtfsUnreadable("the file is encrypted and the volume holds no key")
        want = size if size is not None else data.data_size
        want = min(want, data.data_size) if data.data_size else want
        if data.compressed:
            yield from self._read_compressed(data, want)
            return
        # Everything past the initialized size reads as zero even though the
        # clusters are allocated and still hold whatever was there before. A
        # database that preallocates its file is the common case: two on this
        # Windows volume differed from The Sleuth Kit's reading by exactly that
        # tail until it was honoured. The stale bytes are slack, not content.
        real = min(want, data.init_size) if data.init_size else 0
        done = 0
        while done < real:
            chunk = self._read_runs(data.runs, min(1 << 20, real - done), done)
            if not chunk:
                break
            yield chunk
            done += len(chunk)
        while done < want:
            take = min(1 << 20, want - done)
            yield b"\x00" * take
            done += take

    def _read_compressed(self, data, want):
        """A compressed $DATA is stored in units of 2**comp_unit clusters. A unit
        whose runs are shorter than the unit is compressed and inflated with
        LZNT1; one stored at full length was left uncompressed."""
        unit = (1 << data.comp_unit) * self.cluster
        vcn_per_unit = 1 << data.comp_unit
        produced = 0
        # index the run list by VCN so a unit's clusters can be found
        table, vcn = [], 0
        for lcn, count in data.runs:
            table.append((vcn, lcn, count))
            vcn += count
        total_vcn = vcn
        for start in range(0, total_vcn, vcn_per_unit):
            if produced >= want:
                break
            raw = self._unit_bytes(table, start, vcn_per_unit)
            if raw is None:                       # wholly sparse unit
                out = b"\x00" * unit
            elif len(raw) >= unit:
                out = raw[:unit]
            else:
                out = _lznt1_decompress(raw, unit)
            take = min(len(out), want - produced)
            yield out[:take]
            produced += take

    def _unit_bytes(self, table, start_vcn, count):
        """The stored bytes of one compression unit, or None if it is all sparse.
        A compressed unit occupies fewer clusters than the unit, and the rest of
        its VCN span is a sparse run, so the stored length is what says so."""
        out, any_real = bytearray(), False
        for vcn, lcn, span in table:
            lo, hi = max(vcn, start_vcn), min(vcn + span, start_vcn + count)
            if lo >= hi:
                continue
            if lcn is None:
                continue
            any_real = True
            out += read_at(self.fh, self.base + (lcn + (lo - vcn)) * self.cluster,
                           (hi - lo) * self.cluster)
        return bytes(out) if any_real else None


def _lznt1_decompress(src, limit):
    """Inflate an LZNT1 stream, the compression NTFS applies to a $DATA unit.

    The format is a series of chunks, each a 16-bit header giving its stored
    length and whether it is compressed, then either the literal bytes or a
    stream of flag bytes where each bit says whether the next item is a literal
    or a back reference. The split of a back reference into length and offset
    bits widens as the output grows, which is what the shifting below tracks.
    Described in the Linux-NTFS documentation, "Compressed files".
    """
    out = bytearray()
    pos = 0
    while pos + 2 <= len(src) and len(out) < limit:
        header = struct.unpack_from("<H", src, pos)[0]
        pos += 2
        if header == 0:
            break
        size = (header & 0x0FFF) + 1
        if pos + size > len(src):
            break
        chunk, pos = src[pos:pos + size], pos + size
        if not header & 0x8000:                    # stored, not compressed
            out += chunk
            continue
        start = len(out)
        i = 0
        while i < len(chunk) and len(out) - start < 4096:
            flags = chunk[i]
            i += 1
            for bit in range(8):
                if i >= len(chunk) or len(out) - start >= 4096:
                    break
                if not flags & (1 << bit):
                    out.append(chunk[i])
                    i += 1
                    continue
                if i + 2 > len(chunk):
                    i = len(chunk)
                    break
                pair = struct.unpack_from("<H", chunk, i)[0]
                i += 2
                produced = len(out) - start
                shift = 12
                while shift > 4 and produced > (1 << (16 - shift)):
                    shift -= 1
                length = (pair & ((1 << shift) - 1)) + 3
                delta = (pair >> shift) + 1
                if delta > produced:
                    return bytes(out)
                src_pos = len(out) - delta
                for _ in range(length):
                    out.append(out[src_pos])
                    src_pos += 1
    return bytes(out[:limit])


# ---------------------------------------------------------------- APFS
# Field offsets and structure layouts below come from Apple's published "Apple
# File System Reference". No APFS implementation's source was read for this.

APFS_NX_MAGIC   = b"NXSB"
APFS_VOL_MAGIC  = b"APSB"
APFS_OBJ_HDR    = 32            # every object begins with obj_phys_t
APFS_ROOT_INO   = 2             # ROOT_DIR_INO_NUM
# A container holds several volumes and the walker interface above is one tree
# per region, so the container itself is presented as a directory whose children
# are its volumes. A node is the volume's index in the high bits and the
# file-system object id in the low ones; the container is a value no volume can
# produce.
# A file-system object id is 60 bits, because the record type takes the top
# four of the 64-bit key field. The sealed system volume of macOS 11 and later
# uses ids near the top of that range (0x0FFFFFFF...), so a narrower field
# silently drops every one of its directory entries. A walker node is a plain
# Python integer with no width to run out of, so the volume index simply sits
# above the full 60 bits, and the container sentinel is put where no volume and
# object id can reach it.
APFS_VOL_SHIFT  = 60
APFS_OID_MASK   = (1 << APFS_VOL_SHIFT) - 1
APFS_CONTAINER  = 1 << 127
APFS_BTREE_INFO = 40            # a root node carries btree_info_t at its end

APFS_OBJ_TYPE_MASK = 0x0000FFFF
APFS_OBJECT_TYPE_NX_SUPERBLOCK = 0x0001
APFS_OBJECT_TYPE_SPACEMAN      = 0x0005
APFS_OBJECT_TYPE_CHECKPOINT_MAP = 0x000C
APFS_NX_SPACEMAN_OID_OFF = 152   # nx_spaceman_oid in the container superblock
APFS_SM_DEV_MAIN_OFF     = 48    # sm_dev[SD_MAIN] in spaceman_phys_t
APFS_CI_SIZE             = 32    # sizeof(chunk_info_t)
APFS_CPM_SIZE            = 40    # sizeof(checkpoint_mapping_t)
APFS_OBJECT_TYPE_BTREE_NODE    = 0x0003
APFS_OBJECT_TYPE_OMAP          = 0x000B
APFS_OBJECT_TYPE_FS            = 0x000D

APFS_BTNODE_ROOT     = 0x0001
APFS_BTNODE_LEAF     = 0x0002
APFS_BTNODE_FIXED_KV = 0x0004

# btree_info sits in the last 40 bytes of a root node and declares the tree's
# own shape. BTREE_HASHED marks the integrity-checked tree of a sealed volume,
# where an index node's value carries a hash after the child pointer.
APFS_BTREE_INFO      = 40
APFS_BTREE_HASHED    = 0x00000080
APFS_BTREE_PHYSICAL  = 0x00000010

# A sealed volume keeps its file extents in a tree of its own, keyed by the
# stream id and the offset within the file, instead of as records in the
# file-system tree. The volume superblock names it; the offset below was found
# by looking for the field that resolves to a physical B-tree root, and the
# reader checks that it is one before using it rather than trusting the offset.
APFS_FEXT_TREE_OFF   = 1032

# record types, the high four bits of a file-system key's object id
APFS_TYPE_INODE       = 3
APFS_TYPE_XATTR       = 4
APFS_TYPE_DSTREAM_ID  = 6
APFS_TYPE_FILE_EXTENT = 8
APFS_TYPE_DIR_REC     = 9

APFS_INCOMPAT_CASE_INSENSITIVE          = 0x0000000000000001
APFS_INCOMPAT_NORMALIZATION_INSENSITIVE = 0x0000000000000008

APFS_INO_EXT_TYPE_DSTREAM = 8   # the extended field holding a file's size

APFS_XATTR_DATA_STREAM = 0x0001
APFS_XATTR_DATA_EMBEDDED = 0x0002

APFS_DECMPFS = "com.apple.decmpfs"
APFS_SYMLINK = "com.apple.fs.symlink"
APFS_RESOURCE_FORK = "com.apple.ResourceFork"

# APFS timestamps are nanoseconds since the Unix epoch.
APFS_NANO = 1_000_000_000


class ApfsUnreadable(Exception):
    """A file whose bytes this walker will not guess at: encrypted, or a
    compression this reader does not implement."""


def apfs_time(v):
    """A nanosecond APFS timestamp as Unix seconds, or 0 when unset."""
    if not v:
        return 0
    sec = v // APFS_NANO
    return sec if 0 < sec < 4102444800 else 0


def _apfs_fletcher_ok(block):
    """True when a block's Fletcher-64 checksum is the one it carries.

    The checksum is the first eight bytes of the object header and covers
    everything after it, in 32-bit words. Checking it is what makes "the newest
    checkpoint" a decision rather than a guess: a half-written checkpoint is
    still on disk and still carries a high transaction id.
    """
    if len(block) < APFS_OBJ_HDR:
        return False
    lo = hi = 0
    for off in range(8, len(block) - 3, 4):
        lo = (lo + struct.unpack_from("<I", block, off)[0]) % 0xFFFFFFFF
        hi = (hi + lo) % 0xFFFFFFFF
    c1 = (0xFFFFFFFF - ((lo + hi) % 0xFFFFFFFF)) % 0xFFFFFFFF
    c2 = (0xFFFFFFFF - ((lo + c1) % 0xFFFFFFFF)) % 0xFFFFFFFF
    return struct.unpack_from("<Q", block, 0)[0] == ((c2 << 32) | c1)


class _ApfsBtree:
    """One B-tree, read through whatever resolves an object id to a block."""

    def __init__(self, vol, root_block, physical=False, base_oid=0):
        # An object map's own tree points at blocks; the file-system tree points
        # at virtual object ids that the volume's map has to turn into blocks.
        # Reading the map itself therefore cannot go through the map.
        #
        # base_oid is for the sealed system volume of macOS 11 and later, whose
        # tree stores each child pointer relative to the tree's own root id
        # rather than as the id itself. Left at zero the arithmetic is a no-op,
        # so an ordinary tree is unaffected.
        self.vol, self.root_block, self.physical = vol, root_block, physical
        self.base_oid = base_oid
        self._leaves_cache = None
        self._leaf_keys = []

    @staticmethod
    def _layout(node, node_size):
        flags, _level, nkeys = struct.unpack_from("<HHI", node, APFS_OBJ_HDR)
        toc_off, toc_len = struct.unpack_from("<HH", node, APFS_OBJ_HDR + 8)
        keys_at = APFS_OBJ_HDR + 24 + toc_off + toc_len
        ends_at = node_size - (APFS_BTREE_INFO if flags & APFS_BTNODE_ROOT else 0)
        return flags, nkeys, APFS_OBJ_HDR + 24 + toc_off, keys_at, ends_at

    def records(self, node):
        """[(key bytes, value bytes)] for one node, in key order."""
        size = len(node)
        flags, nkeys, toc_at, keys_at, ends_at = self._layout(node, size)
        fixed = bool(flags & APFS_BTNODE_FIXED_KV)
        leaf = bool(flags & APFS_BTNODE_LEAF)
        step = 4 if fixed else 8
        out = []
        for i in range(nkeys):
            at = toc_at + i * step
            if at + step > size:
                break
            if fixed:
                k, v = struct.unpack_from("<HH", node, at)
                klen = self.vol.fixed_key_size
                vlen = 8 if not leaf else self.vol.fixed_val_size
            else:
                k, klen, v, vlen = struct.unpack_from("<HHHH", node, at)
            ks, vs = keys_at + k, ends_at - v
            if not (0 <= ks <= size - klen and 0 <= vs <= size - vlen):
                continue
            out.append((node[ks:ks + klen], node[vs:vs + vlen]))
        return flags, out

    def leaves(self, key_of):
        """[(first key, block)] for every leaf, in key order, worked out once.

        APFS does not chain its leaves the way HFS+ does, so a reader either
        descends afresh for every lookup or writes the order down. Descending
        each time turns a walk of N files into N walks of the tree; this walks it
        once and every later lookup is a search of the list.
        """
        if self._leaves_cache is None:
            out = []
            self._collect_leaves(self.root_block, key_of, out, 0)
            self._leaves_cache = out
            # The first keys are kept separately because every lookup bisects
            # them: rebuilding that list per lookup makes the walk quadratic in
            # the number of leaves, which is what it was until this was split out.
            self._leaf_keys = [k for k, _b in out]
        return self._leaves_cache

    def _collect_leaves(self, block, key_of, out, depth):
        if depth > 32 or len(out) > 1 << 20:
            return
        node = self.vol.block(block)
        flags, recs = self.records(node)
        if flags & APFS_BTNODE_LEAF:
            if recs:
                out.append((key_of(recs[0][0]), block))
            return
        for _key, val in recs:
            oid = struct.unpack_from("<Q", val, 0)[0]
            # A sealed volume's index value is the child pointer followed by a
            # hash, so it is longer than eight bytes; the pointer itself still
            # sits at the front, and base_oid is what makes it an object id.
            child = oid if self.physical else self.vol.resolve(oid + self.base_oid)
            if child is not None:
                self._collect_leaves(child, key_of, out, depth + 1)

    def search(self, want, key_of):
        """Every leaf record from the first one not less than ``want`` onward."""
        leaves = self.leaves(key_of)
        if not leaves:
            return
        # Start at the last leaf whose first key is strictly less than what is
        # wanted. The run can begin part way through that leaf, so starting at
        # the first leaf whose first key equals the target misses whatever sits
        # at the tail of the one before it. Measured on a 400-entry directory:
        # 387 children found instead of 400.
        i = bisect.bisect_left(self._leaf_keys, want) - 1
        if i < 0:
            i = 0
        for _first, block in leaves[i:]:
            _flags, recs = self.records(self.vol.block(block))
            for key, val in recs:
                k = key_of(key)
                if k is None or k < want:
                    continue
                yield key, val


class ApfsWalker:
    """List and read files from an APFS volume, same interface as the walkers
    above. A node is the file-system object id, which is what a directory record
    stores and what an inode is keyed by.

    An APFS container holds one or more volumes. This walker reads one of them,
    chosen by index, because the walker interface above is per filesystem; the
    identification lines say how many the container holds and name each.

    What it reads: the container's newest checkpoint, its object map, the
    volume's own object map and file-system B-tree, directory records, inodes
    and their extended fields, file extents including sparse ones, symbolic
    links, and files compressed with the decmpfs attribute in its zlib forms.

    What it does not read: an encrypted volume, and a file compressed with LZVN
    or LZFSE, which are not in the standard library. Both are reported rather
    than guessed at.
    """

    root = APFS_CONTAINER

    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        self.fixed_key_size, self.fixed_val_size = 16, 16      # the omap's shape
        head = read_at(fh, base, 4096)
        if len(head) < 4096 or head[32:36] != APFS_NX_MAGIC:
            raise ValueError("not an APFS container superblock")
        self.block_size = struct.unpack_from("<I", head, 36)[0]
        if not self.block_size or self.block_size & (self.block_size - 1):
            raise ValueError("the container superblock gives an impossible block size")
        nx = self._newest_checkpoint(head)
        self._nx = nx
        self.block_count = struct.unpack_from("<Q", nx, 40)[0]
        self.container_size = self.block_count * self.block_size
        self.uuid = uuid.UUID(bytes=nx[72:88])
        omap_oid = struct.unpack_from("<Q", nx, 160)[0]
        max_fs = struct.unpack_from("<I", nx, 180)[0]
        fs_oids = [struct.unpack_from("<Q", nx, 184 + i * 8)[0]
                   for i in range(min(max_fs, 100))]
        self.volume_oids = [o for o in fs_oids if o]
        self._omap_cache = {}
        self._container_omap = self._read_omap(omap_oid)
        self.volumes = []
        for oid in self.volume_oids:
            block = self._container_omap.get(oid)
            if block is None:
                continue
            sb = self.block(block)
            if sb[32:36] != APFS_VOL_MAGIC:
                continue
            self.volumes.append((oid, block, _apfs_volume_name(sb),
                                 struct.unpack_from("<Q", sb, 56)[0]))
        if not self.volumes:
            raise ValueError("the container names no readable volume")
        self._state = {}
        self._current = None
        self._fext = None
        self._open_volume(0)

    # -- volumes -----------------------------------------------------------
    def _open_volume(self, index):
        """Make one volume of the container the current one, reading its object
        map and file-system tree the first time it is asked for."""
        if self._current == index:
            return
        got = self._state.get(index)
        if got is None:
            _oid, block, _name, incompat = self.volumes[index]
            sb = self.block(block)
            vol_omap_oid, root_oid = struct.unpack_from("<QQ", sb, 128)
            # Reading the volume's own map has to happen while nothing else is
            # current, because resolve() consults whatever is.
            self._current, self._volume_omap = None, {}
            omap = self._read_omap(vol_omap_oid)
            root_block = omap.get(root_oid)
            if root_block is None:
                raise ValueError(f"volume {index}'s file-system tree is not in its map")
            # A sealed system volume declares its tree hashed, in the
            # btree_info that sits in the last 40 bytes of the root node, and
            # stores its child pointers relative to the tree's own root id.
            # Reading that declaration is what decides it: the alternative is
            # keying on a macOS version, which the volume does not carry.
            root_node = self.block(root_block)
            sealed = False
            if len(root_node) >= APFS_BTREE_INFO:
                bt_flags = struct.unpack_from(
                    "<I", root_node, len(root_node) - APFS_BTREE_INFO)[0]
                sealed = bool(bt_flags & APFS_BTREE_HASHED)
            got = {
                "omap": omap,
                "tree": None,
                "root_block": root_block,
                "base_oid": root_oid if sealed else 0,
                "sealed": sealed,
                "fext": self._read_fext(sb) if sealed else None,
                # A directory record's key carries the name's length alone, or a
                # length and a hash together, and the volume decides which.
                # Reading the wrong shape puts bytes of hash on the front of
                # every name, which is what it did until this was sourced.
                "hashed": bool(incompat & (APFS_INCOMPAT_CASE_INSENSITIVE
                                           | APFS_INCOMPAT_NORMALIZATION_INSENSITIVE)),
                "case_insensitive": bool(incompat & APFS_INCOMPAT_CASE_INSENSITIVE),
                "inodes": {},
            }
            self._state[index] = got
        self._current = index
        self._volume_omap = got["omap"]
        if got["tree"] is None:
            got["tree"] = _ApfsBtree(self, got["root_block"],
                                     base_oid=got["base_oid"])
        self._tree = got["tree"]
        self._inodes = got["inodes"]
        self._hashed_names = got["hashed"]
        self.case_insensitive = got["case_insensitive"]
        self.volume_name = self.volumes[index][2]
        self.fs_root_block = got["root_block"]
        self.sealed = got["sealed"]
        self._fext = got["fext"]

    def _split(self, node):
        """(volume index, object id) for a walker node."""
        return node >> APFS_VOL_SHIFT, node & APFS_OID_MASK

    def _select(self, node):
        vol, oid = self._split(node)
        if vol >= len(self.volumes):
            return None
        self._open_volume(vol)
        return oid

    # -- blocks and object maps -------------------------------------------
    def block(self, n):
        return read_at(self.fh, self.base + n * self.block_size, self.block_size)

    def resolve(self, oid):
        """A child pointer inside the file-system tree is a virtual object id,
        which the volume's object map turns into a block. An id the map does not
        hold is not a block number to fall back on: guessing there would read
        whatever happens to sit at that offset and call it a node."""
        return self._volume_omap.get(oid)

    def _newest_checkpoint(self, head):
        """The container superblock with the highest transaction id that checks out.

        Block zero is a copy that can be older than the newest checkpoint, so the
        checkpoint descriptor area is scanned and the best one taken. Block zero
        stands in when nothing there is usable.
        """
        best, best_xid = head, struct.unpack_from("<Q", head, 16)[0]
        base = struct.unpack_from("<Q", head, 112)[0]
        blocks = struct.unpack_from("<I", head, 104)[0]
        for i in range(min(blocks, 512)):
            raw = self.block(base + i)
            if len(raw) < 40 or raw[32:36] != APFS_NX_MAGIC:
                continue
            otype = struct.unpack_from("<I", raw, 24)[0] & APFS_OBJ_TYPE_MASK
            if otype != APFS_OBJECT_TYPE_NX_SUPERBLOCK:
                continue
            xid = struct.unpack_from("<Q", raw, 16)[0]
            if xid > best_xid and _apfs_fletcher_ok(raw):
                best, best_xid = raw, xid
        self.xid = best_xid
        return best

    def _ephemeral(self, oid):
        """The block an ephemeral object sits in, or None.

        An ephemeral object is not in the object map. It is written into the
        checkpoint data area and located through the checkpoint map blocks that
        share its checkpoint, so the descriptor area is scanned for maps carrying
        this walker's transaction id and their entries are read.
        """
        desc_base = struct.unpack_from("<Q", self._nx, 112)[0]
        desc_blocks = struct.unpack_from("<I", self._nx, 104)[0]
        for i in range(min(desc_blocks, 4096)):
            raw = self.block(desc_base + i)
            if len(raw) < 40:
                continue
            if (struct.unpack_from("<I", raw, 24)[0] & APFS_OBJ_TYPE_MASK
                    != APFS_OBJECT_TYPE_CHECKPOINT_MAP):
                continue
            if struct.unpack_from("<Q", raw, 16)[0] != self.xid:
                continue
            count = struct.unpack_from("<I", raw, 36)[0]
            for k in range(min(count, (len(raw) - 40) // APFS_CPM_SIZE)):
                at = 40 + k * APFS_CPM_SIZE
                cpm_oid, cpm_paddr = struct.unpack_from("<QQ", raw, at + 24)
                if cpm_oid == oid:
                    return cpm_paddr
        return None

    def free_extents(self, min_bytes=0):
        """[(byte offset, length)] for the runs of space the container says are free.

        APFS tracks free space per container rather than per volume, in the space
        manager. The space manager is an ephemeral object, so it is found through
        the checkpoint map rather than the object map, and it points at chunk-info
        blocks. Each chunk covers a fixed run of blocks and carries a bitmap
        address; a chunk with no bitmap is entirely free.

        **The bits run least significant first**, the same way round as NTFS and
        the opposite of HFS+. A count of free blocks cannot tell the two orders
        apart, because a byte holds the same number of zero bits either way. What
        tells them apart is position: read the other way round, this container
        reports its own superblock at block zero as free.

        Offsets are into the image rather than the container, so a caller reading
        the whole disk can use them directly. ``min_bytes`` drops runs too short
        to hold anything worth recovering. An empty list means the space manager
        could not be read, which a caller must not read as "nothing is free".
        """
        block = self.block_size
        oid = struct.unpack_from("<Q", self._nx, APFS_NX_SPACEMAN_OID_OFF)[0]
        at = self._ephemeral(oid) if oid else None
        if not at:
            return []
        sm = self.block(at)
        if len(sm) < 96 or (struct.unpack_from("<I", sm, 24)[0] & APFS_OBJ_TYPE_MASK
                            != APFS_OBJECT_TYPE_SPACEMAN):
            return []
        dev = APFS_SM_DEV_MAIN_OFF
        cib_count, cab_count = struct.unpack_from("<II", sm, dev + 16)
        addr_off = struct.unpack_from("<I", sm, dev + 32)[0]
        count = cab_count or cib_count
        if not count or addr_off + count * 8 > len(sm):
            return []
        addrs = list(struct.unpack_from(f"<{count}Q", sm, addr_off))
        if cab_count:                                # one more level of indirection
            cibs = []
            for a in addrs:
                cab = self.block(a)
                if len(cab) < 40:
                    continue
                n = struct.unpack_from("<I", cab, 36)[0]
                n = min(n, (len(cab) - 40) // 8)
                cibs += list(struct.unpack_from(f"<{n}Q", cab, 40))
            addrs = cibs

        runs = []
        for a in addrs:
            cib = self.block(a)
            if len(cib) < 40:
                continue
            n = struct.unpack_from("<I", cib, 36)[0]
            for k in range(min(n, (len(cib) - 40) // APFS_CI_SIZE)):
                o = 40 + k * APFS_CI_SIZE
                ci_addr = struct.unpack_from("<Q", cib, o + 8)[0]
                ci_blocks, ci_free = struct.unpack_from("<II", cib, o + 16)
                ci_bitmap = struct.unpack_from("<Q", cib, o + 24)[0]
                if ci_addr >= self.block_count or not ci_blocks:
                    continue
                ci_blocks = min(ci_blocks, self.block_count - ci_addr)
                if not ci_bitmap:                    # no bitmap means wholly free
                    if ci_free:
                        runs.append((ci_addr, ci_blocks))
                    continue
                bits = self.block(ci_bitmap)
                total = min(len(bits) * 8, ci_blocks)
                start, pos = None, 0
                while pos < total:
                    byte = bits[pos >> 3]
                    if not (pos & 7) and pos + 8 <= total and byte in (0x00, 0xFF):
                        if byte == 0x00:
                            if start is None:
                                start = pos
                        elif start is not None:
                            runs.append((ci_addr + start, pos - start))
                            start = None
                        pos += 8
                        continue
                    if byte & (1 << (pos & 7)):
                        if start is not None:
                            runs.append((ci_addr + start, pos - start))
                            start = None
                    elif start is None:
                        start = pos
                    pos += 1
                if start is not None:
                    runs.append((ci_addr + start, total - start))

        runs.sort()
        merged = []
        for first, n in runs:                        # chunks abut, so their runs do
            if merged and merged[-1][0] + merged[-1][1] == first:
                merged[-1] = (merged[-1][0], merged[-1][1] + n)
            else:
                merged.append((first, n))
        out = []
        for first, n in merged:
            length = n * block
            if length >= min_bytes:
                out.append((self.base + first * block, length))
        return out

    def _read_omap(self, oid):
        """An object map as a plain dict: every virtual id it holds, to a block.

        The map of a volume this size is small, and reading it once removes a
        tree descent from every block lookup on the walk.
        """
        got = self._omap_cache.get(oid)
        if got is not None:
            return got
        raw = self.block(oid)
        if len(raw) < 56:
            raise ValueError("the object map is unreadable")
        tree_oid = struct.unpack_from("<Q", raw, 48)[0]
        out = {}
        self._omap_cache[oid] = out
        tree = _ApfsBtree(self, tree_oid, physical=True)
        for key, val in tree.search((0, 0), _apfs_omap_key):
            if len(key) < 16 or len(val) < 16:
                continue
            o, xid = struct.unpack_from("<QQ", key, 0)
            _flags, _size, paddr = struct.unpack_from("<IIQ", val, 0)
            prev = out.get(o)
            if prev is None or xid >= prev[0]:
                out[o] = (xid, paddr)
        out = {o: p for o, (_x, p) in out.items()}
        self._omap_cache[oid] = out
        return out

    # -- records -----------------------------------------------------------
    def _records(self, oid, rtype):
        """Every file-system record of one object id and one record type."""
        want = (oid, rtype)
        for key, val in self._tree.search(want, _apfs_fs_key):
            k = _apfs_fs_key(key)
            if k is None or k < want:
                continue
            if k != want:
                if k > want:
                    return
                continue
            yield key, val

    def _inode(self, oid):
        got = self._inodes.get(oid)
        if got is None:
            for _key, val in self._records(oid, APFS_TYPE_INODE):
                got = val
                break
            self._inodes[oid] = got
        return got

    def _dstream(self, oid):
        """(size, private id) for a file, from the inode's extended fields.

        The size lives in an extended field rather than in the inode's fixed
        part, and the private id is what the file's extents are keyed by, which
        is not always the object id itself.
        """
        val = self._inode(oid)
        if not val or len(val) < 92:
            return 0, oid
        private = struct.unpack_from("<Q", val, 8)[0]
        fields = _apfs_xfields(val, 92)
        blob = fields.get(APFS_INO_EXT_TYPE_DSTREAM)
        size = struct.unpack_from("<Q", blob, 0)[0] if blob and len(blob) >= 8 else 0
        return size, (private or oid)

    def _read_fext(self, sb):
        """{stream id: [(logical, block, length)]} from a sealed volume's own
        extent tree, or None when the field does not name one.

        The tree is keyed by (stream id, offset within the file) and its value
        is a length with flags and a physical block, the same pair a file
        extent record carries in an ordinary volume. It is read once: a sealed
        system volume has a few hundred thousand extents and a descent per file
        would walk the tree once per file.
        """
        if len(sb) < APFS_FEXT_TREE_OFF + 8:
            return None
        oid = struct.unpack_from("<Q", sb, APFS_FEXT_TREE_OFF)[0]
        if not oid:
            return None
        try:
            node = self.block(oid)
        except Exception:                            # pylint: disable=broad-except
            return None
        if len(node) < self.block_size:
            return None
        flags = struct.unpack_from("<H", node, APFS_OBJ_HDR)[0]
        info = struct.unpack_from("<I", node, len(node) - APFS_BTREE_INFO)[0]
        # The field is only believed when what it points at is a physical
        # B-tree root. Anything else and the offset is wrong for this volume,
        # which must read as "no extent tree" rather than as whatever sits there.
        if not (flags & APFS_BTNODE_ROOT) or not (info & APFS_BTREE_PHYSICAL):
            return None
        out = {}
        tree = _ApfsBtree(self, oid, physical=True)
        for key, val in tree.search(
                (0, 0), lambda k: struct.unpack_from("<QQ", k, 0)
                if len(k) >= 16 else (0, 0)):
            if len(key) < 16 or len(val) < 16:
                continue
            stream, logical = struct.unpack_from("<QQ", key, 0)
            len_flags, phys = struct.unpack_from("<QQ", val, 0)
            out.setdefault(stream, []).append(
                (logical, phys, len_flags & 0x00FFFFFFFFFFFFFF))
        for runs in out.values():
            runs.sort()
        return out

    def _extents(self, private_id):
        """[(logical offset, block, length)] for a stream, in order."""
        if self._fext is not None:
            return self._fext.get(private_id, [])
        out = []
        for key, val in self._records(private_id, APFS_TYPE_FILE_EXTENT):
            if len(key) < 16 or len(val) < 16:
                continue
            logical = struct.unpack_from("<Q", key, 8)[0]
            len_flags, phys = struct.unpack_from("<QQ", val, 0)
            out.append((logical, phys, len_flags & 0x00FFFFFFFFFFFFFF))
        out.sort()
        return out

    def _xattr(self, oid, name):
        """One extended attribute: its bytes when it is embedded, or the stream
        it names when it is not."""
        for key, val in self._records(oid, APFS_TYPE_XATTR):
            if len(key) < 12 or len(val) < 4:
                continue
            nlen = struct.unpack_from("<H", key, 8)[0]
            got = key[10:10 + nlen].split(b"\x00")[0].decode("utf-8", "replace")
            if got != name:
                continue
            flags, xlen = struct.unpack_from("<HH", val, 0)
            body = val[4:4 + xlen]
            if flags & APFS_XATTR_DATA_EMBEDDED:
                return ("data", body)
            if flags & APFS_XATTR_DATA_STREAM and len(body) >= 16:
                stream_id = struct.unpack_from("<Q", body, 0)[0]
                size = struct.unpack_from("<Q", body, 8)[0]
                return ("stream", (stream_id, size))
        return None

    def _read_stream(self, private_id, want, size_cap=None):
        """Bytes of a stream, sparse extents reading as the zeros they stand for."""
        out = bytearray()
        for logical, phys, length in self._extents(private_id):
            if len(out) >= want:
                break
            if logical > len(out):
                out += b"\x00" * min(logical - len(out), want - len(out))
            take = min(length, want - len(out))
            if take <= 0:
                continue
            if phys == 0:
                out += b"\x00" * take
            else:
                out += read_at(self.fh, self.base + phys * self.block_size, take)
        if size_cap is not None:
            return bytes(out[:size_cap])
        return bytes(out[:want])

    # -- the walker surface ------------------------------------------------
    def inode(self, node):
        return node

    def entry(self, node):
        if node == APFS_CONTAINER:
            return (S_IFDIR | 0o755, 0, 0)
        oid = self._select(node)
        if oid is None:
            return None
        val = self._inode(oid)
        if not val or len(val) < 82:
            return None
        mode = struct.unpack_from("<H", val, 80)[0]
        mtime = apfs_time(struct.unpack_from("<Q", val, 24)[0])
        if mode & S_IFDIR == S_IFDIR:
            return (mode, 0, mtime)
        size, _private = self._dstream(oid)
        blob = self._xattr(oid, APFS_DECMPFS)
        if blob:
            head = blob[1] if blob[0] == "data" else self._read_stream(blob[1][0], 16)
            if len(head) >= 16 and head[0:4] == b"fpmc":
                size = struct.unpack_from("<Q", head, 8)[0]
        return (mode or 0o100644, size, mtime)

    def listdir(self, node):
        if node == APFS_CONTAINER:
            # The container's children are its volumes, so every one of them is
            # reachable from a single walk and lands under its own name.
            return [(name or f"volume{i}", (i << APFS_VOL_SHIFT) | APFS_ROOT_INO)
                    for i, (_o, _b, name, _f) in enumerate(self.volumes)]
        vol, _ = self._split(node)
        oid = self._select(node)
        if oid is None:
            return []
        out = []
        for key, val in self._records(oid, APFS_TYPE_DIR_REC):
            if len(val) < 8:
                continue
            if self._hashed_names:
                if len(key) < 12:
                    continue
                nlen = struct.unpack_from("<I", key, 8)[0] & 0x3FF
                name = key[12:12 + nlen]
            else:
                if len(key) < 10:
                    continue
                nlen = struct.unpack_from("<H", key, 8)[0]
                name = key[10:10 + nlen]
            name = name.split(b"\x00")[0].decode("utf-8", "replace")
            child = struct.unpack_from("<Q", val, 0)[0]
            if child > APFS_OID_MASK:
                continue                        # an id too large to carry a volume
            if name and name not in (".", ".."):
                out.append((name, (vol << APFS_VOL_SHIFT) | child))
        return out

    def named_streams(self, node):
        """[(name, size)] for every extended attribute held in its own stream.
        Those are bytes the file's own size does not account for."""
        if node == APFS_CONTAINER:
            return []
        oid = self._select(node)
        if oid is None:
            return []
        out = []
        for key, val in self._records(oid, APFS_TYPE_XATTR):
            if len(key) < 12 or len(val) < 4:
                continue
            nlen = struct.unpack_from("<H", key, 8)[0]
            name = key[10:10 + nlen].split(b"\x00")[0].decode("utf-8", "replace")
            flags, xlen = struct.unpack_from("<HH", val, 0)
            if flags & APFS_XATTR_DATA_STREAM and xlen >= 16:
                size = struct.unpack_from("<Q", val, 12)[0]
                if name != APFS_RESOURCE_FORK or size:
                    out.append((name, size))
        return out

    def read_file(self, node, size):
        if node == APFS_CONTAINER:
            return
        oid = self._select(node)
        if oid is None:
            return
        val = self._inode(oid)
        if not val:
            return
        # A symbolic link keeps its target in an attribute rather than in a
        # stream, so a link has no extents to read and the target is the content.
        if len(val) >= 82 and (struct.unpack_from("<H", val, 80)[0] & 0o170000) == S_IFLNK:
            link = self._xattr(oid, APFS_SYMLINK)
            if link and link[0] == "data":
                yield link[1].split(b"\x00")[0]
            return
        blob = self._xattr(oid, APFS_DECMPFS)
        if blob:
            yield from self._read_compressed(oid, blob)
            return
        stream_size, private = self._dstream(oid)
        want = stream_size if size is None else min(size, stream_size or size)
        # A file that says it holds bytes and has no extent anywhere must not
        # read as an empty file. On a sealed volume the extents live in their
        # own tree, and if that tree is not found this is the shape the failure
        # takes: every uncompressed file comes back zero bytes, which an
        # extraction would write out as a real empty file and nothing would say
        # otherwise.
        if want and private and not self._extents(private):
            raise ApfsUnreadable(
                f"the file says it holds {want:,} bytes and no extent records "
                f"for it were found" + (", which is what a sealed volume looks "
                "like when its extent tree was not read" if self.sealed else ""))
        done = 0
        while done < want:
            chunk = self._read_stream(private, want)[done:done + (1 << 20)]
            if not chunk:
                break
            yield chunk
            done += len(chunk)

    def _read_compressed(self, oid, blob):
        """A file whose data is held by the decmpfs attribute.

        The attribute's header names the method and the size the file reports.
        Types 3 and 4 are zlib, in the attribute itself or in the resource fork
        behind a table of block offsets; the rest are LZVN and LZFSE, which the
        standard library cannot inflate.
        """
        import zlib
        kind, payload = blob
        header = payload if kind == "data" else self._read_stream(payload[0], 32)
        if len(header) < 16 or header[0:4] != b"fpmc":
            raise ApfsUnreadable("the compression attribute is not one this reader knows")
        method, size = struct.unpack_from("<IQ", header, 4)
        if method in (3, 5):
            body = payload[16:] if kind == "data" else \
                self._read_stream(payload[0], payload[1])[16:]
            yield (body[1:1 + size] if body[:1] == b"\xff" else zlib.decompress(body)[:size])
            return
        if method == 4:
            fork = self._xattr(oid, APFS_RESOURCE_FORK)
            if not fork or fork[0] != "stream":
                raise ApfsUnreadable("the compressed resource fork is not there")
            stream_id, fork_size = fork[1]
            raw = self._read_stream(stream_id, fork_size)
            if len(raw) < 4:
                raise ApfsUnreadable("the compressed resource fork is unreadable")
            data_off = struct.unpack_from(">I", raw, 0)[0]
            count = struct.unpack_from("<I", raw, data_off)[0]
            produced = 0
            for i in range(count):
                off, blen = struct.unpack_from("<II", raw, data_off + 4 + i * 8)
                piece = raw[data_off + off:data_off + off + blen]
                out = piece[1:] if piece[:1] == b"\xff" else zlib.decompress(piece)
                take = min(len(out), size - produced)
                yield out[:take]
                produced += take
                if produced >= size:
                    return
            return
        raise ApfsUnreadable(
            f"the file is compressed with method {method}, which needs LZVN or "
            f"LZFSE and is not read here")



def _apfs_omap_key(key):
    return struct.unpack_from("<QQ", key, 0) if len(key) >= 16 else None


def _apfs_fs_key(key):
    """(object id, record type) for a file-system tree key, which is the order
    the tree is sorted in: the id first, then the kind of record."""
    if len(key) < 8:
        return None
    raw = struct.unpack_from("<Q", key, 0)[0]
    return (raw & ((1 << 60) - 1), raw >> 60)


def _apfs_volume_name(sb):
    return sb[704:768].split(b"\x00")[0].decode("utf-8", "replace")


def _apfs_xfields(blob, off):
    """{type: bytes} for an inode's extended fields.

    A count and a used length, then one descriptor per field, then the values
    one after another, each padded up to eight bytes.
    """
    out = {}
    if off + 4 > len(blob):
        return out
    count, _used = struct.unpack_from("<HH", blob, off)
    if count > 64:
        return out
    data = off + 4 + count * 4
    for i in range(count):
        at = off + 4 + i * 4
        if at + 4 > len(blob):
            break
        x_type, _flags, size = struct.unpack_from("<BBH", blob, at)
        if data + size > len(blob):
            break
        out[x_type] = blob[data:data + size]
        data += size + (-size % 8)
    return out


# ---------------------------------------------------------------- HFS+
# Field offsets and structure layouts below come from Apple's Technical Note
# TN1150, "HFS Plus Volume Format", which is the published description of the
# format. No HFS implementation's source was read for this.

HFSP_SIG    = 0x482B          # 'H+', HFS Plus
HFSX_SIG    = 0x4858          # 'HX', HFSX, which differs only in case handling
HFSP_VH_OFF = 1024            # the volume header sits 1024 bytes into the volume
HFSP_ROOT   = 2               # kHFSRootFolderID
HFSP_ALLOC  = 6               # kHFSAllocationFileID
HFSP_ALLOC_FORK = 112         # the allocation file's fork record in the volume header

# B-tree node kinds, TN1150 "B-Trees"
HFSP_LEAF, HFSP_INDEX, HFSP_HEADER, HFSP_MAP = -1, 0, 1, 2

# catalog record types
HFSP_FOLDER, HFSP_FILE, HFSP_FOLDER_THREAD, HFSP_FILE_THREAD = 1, 2, 3, 4

# HFS+ counts seconds from 1904-01-01; this is the gap to the Unix epoch.
HFSP_EPOCH_DELTA = 2082844800

# A hard link is a file whose Finder type and creator say so; the number of the
# indirect node it points at is in the BSD info's special field.
HFSP_HARD_LINK_TYPE    = b"hlnk"
HFSP_HARD_LINK_CREATOR = b"hfs+"
HFSP_PRIVATE_DATA = "\x00\x00\x00\x00HFS+ Private Data"

HFSP_DECMPFS = "com.apple.decmpfs"
HFSP_DECMPFS_MAGIC = b"fpmc"


class HfsUnreadable(Exception):
    """A file whose bytes this walker will not guess at: a compression this
    reader does not implement. Raised rather than returning short data, because
    a short read would be indistinguishable from a small file."""


def hfs_time(v):
    """An HFS+ date as Unix seconds, or 0 when unset or out of range."""
    if not v:
        return 0
    sec = v - HFSP_EPOCH_DELTA
    return sec if -2208988800 < sec < 4102444800 else 0


def _hfs_fork(buf, off):
    """(logical size, [(start block, block count)]) from an 80-byte fork record.

    The eight descriptors here are the whole fork for most files; a file with
    more fragments than that keeps the rest in the extents overflow tree.
    """
    size, _clump, _blocks = struct.unpack_from(">QII", buf, off)
    extents = []
    for i in range(8):
        start, count = struct.unpack_from(">II", buf, off + 16 + i * 8)
        if count:
            extents.append((start, count))
    return size, extents


def _hfs_name(buf, off):
    """An HFSUniStr255: a length in UTF-16 units, then that many big-endian units."""
    n = struct.unpack_from(">H", buf, off)[0]
    if n > 255:
        return "", off + 2
    end = off + 2 + n * 2
    return buf[off + 2:end].decode("utf-16-be", "replace"), end


class _HfsTree:
    """One B-tree of the volume, addressed by node number through its own fork."""

    def __init__(self, vol, size, extents, name):
        self.vol, self.size, self.extents, self.name = vol, size, extents, name
        head = self._raw(0, 512)
        if len(head) < 120:
            raise ValueError(f"the {name} tree has no header node")
        (depth, root, _leaf_recs, first_leaf, _last_leaf, node_size,
         self.max_key, _total, _free) = struct.unpack_from(">HIIIIHHII", head, 14)
        self.depth, self.root, self.first_leaf = depth, root, first_leaf
        self.node_size = node_size or 4096
        self.key_compare = head[14 + 33] if len(head) > 47 else 0

    def _raw(self, offset, count):
        """Bytes at a byte offset within the tree's fork."""
        out, pos = bytearray(), 0
        block = self.vol.block_size
        for start, blocks in self.extents:
            span = blocks * block
            if pos + span <= offset:
                pos += span
                continue
            skip = max(0, offset - pos)
            take = min(span - skip, count - len(out))
            out += read_at(self.vol.fh,
                           self.vol.base + start * block + skip, take)
            pos += span
            if len(out) >= count:
                break
        return bytes(out)

    def node(self, number):
        return self._raw(number * self.node_size, self.node_size)

    @staticmethod
    def records(node):
        """[(key, data)] for one node, plus its descriptor.

        A node keeps an array of record offsets at its very end, one per record
        and one more for the free space, counted backwards from the end.
        """
        if len(node) < 14:
            return None, []
        f_link, _b_link, kind, _height, count = struct.unpack_from(">IIbBH", node, 0)
        out = []
        for i in range(count):
            at = len(node) - 2 * (i + 1)
            end_at = len(node) - 2 * (i + 2)
            if end_at < 0:
                break
            start = struct.unpack_from(">H", node, at)[0]
            end = struct.unpack_from(">H", node, end_at)[0]
            if not 14 <= start < end <= len(node):
                continue
            rec = node[start:end]
            klen = struct.unpack_from(">H", rec, 0)[0]
            key = rec[2:2 + klen]
            data_at = 2 + klen + ((2 + klen) & 1)     # records are word aligned
            out.append((key, rec[data_at:]))
        return (kind, f_link), out

    def find(self, want, key_of):
        """Walk down to the first leaf record whose key is not less than ``want``.

        ``key_of`` turns a raw key into something comparable, and the comparison
        is deliberately strict. Every record of one directory shares a parent id,
        so several index entries can carry that id with different names; taking
        the last one that is not GREATER would land on the last leaf of the run
        and lose everything before it. Measured on a 400-entry directory: 10
        children found instead of 400. Taking the last entry strictly less lands
        at or before the first of them, and the caller skips what comes early.
        """
        node_no = self.root
        for _ in range(max(self.depth, 1) + 8):
            node = self.node(node_no)
            desc, recs = self.records(node)
            if not desc or not recs:
                return None
            kind = desc[0]
            if kind == HFSP_LEAF:
                return node_no
            if kind != HFSP_INDEX:
                # Only an index node carries pointers to follow. A tree that is
                # allocated but empty says root 0, depth 0, and node 0 is its
                # own header, so a descent lands here and would otherwise read
                # the header's records as pointers. Every HFS+ volume with no
                # extended attributes and no fragmented file has that shape.
                return None
            nxt = struct.unpack_from(">I", recs[0][1], 0)[0]
            for key, data in recs:
                if key_of(key) is None:
                    continue
                if key_of(key) < want:
                    nxt = struct.unpack_from(">I", data, 0)[0]
                else:
                    break
            if nxt == node_no:
                return None
            node_no = nxt
        return None

    def walk_from(self, node_no):
        """Leaf records from this node onward, following the leaf chain."""
        seen = 0
        while node_no and seen < 1 << 20:
            node = self.node(node_no)
            desc, recs = self.records(node)
            if not desc or desc[0] != HFSP_LEAF:
                return
            for key, data in recs:
                yield key, data
                seen += 1
            node_no = desc[1]


class HfsPlusWalker:
    """List and read files from an HFS+ or HFSX volume, same interface as the
    walkers above. A node is the catalog node id, which is what the catalog
    indexes children by and what makes two names for one file resolve to one
    record.

    What it reads: the catalog B-tree in both its index and leaf forms, forks
    whose fragments outgrew the eight descriptors a catalog record holds and
    continue in the extents overflow tree, symbolic links, hard links through
    the private directory the volume keeps them in, and files compressed with
    the decmpfs attribute in its zlib forms.

    What it does not read: a file compressed with LZVN or LZFSE, which are not
    in the standard library. Those are listed with their recorded size and
    refuse to be read rather than yielding the compressed bytes as though they
    were the file.
    """

    root = HFSP_ROOT

    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        vh = read_at(fh, base + HFSP_VH_OFF, 512)
        if len(vh) < 512:
            raise ValueError("no HFS+ volume header")
        sig, self.version = struct.unpack_from(">HH", vh, 0)
        if sig not in (HFSP_SIG, HFSX_SIG):
            raise ValueError("not an HFS+ volume header")
        self.case_sensitive = sig == HFSX_SIG
        (self.create_date, self.modify_date, _backup, _checked,
         self.file_count, self.folder_count, self.block_size,
         self.total_blocks, self.free_blocks) = struct.unpack_from(">IIIIIIIII", vh, 16)
        if not self.block_size or self.block_size & (self.block_size - 1):
            raise ValueError("the volume header gives an impossible block size")
        self.volume_size = self.total_blocks * self.block_size
        self._catalog = _HfsTree(self, *_hfs_fork(vh, 272), "catalog")
        self._extents = _HfsTree(self, *_hfs_fork(vh, 192), "extents overflow")
        try:
            self._attrs = _HfsTree(self, *_hfs_fork(vh, 352), "attributes")
        except (ValueError, struct.error):
            self._attrs = None                 # a volume with no attributes tree
        self.catalog_node_size = self._catalog.node_size
        self.catalog_depth = self._catalog.depth
        self._cache = {}
        self._private = None

    # -- catalog -----------------------------------------------------------
    @staticmethod
    def _cat_parent(key):
        return struct.unpack_from(">I", key, 0)[0] if len(key) >= 4 else None

    def _children(self, cnid):
        """[(name, child cnid, record)] for one folder, from the catalog."""
        node = self._catalog.find(cnid, self._cat_parent)
        if node is None:
            return []
        out = []
        for key, data in self._catalog.walk_from(node):
            parent = self._cat_parent(key)
            if parent is None or parent < cnid:
                continue
            if parent > cnid:
                break
            if len(data) < 2:
                continue
            kind = struct.unpack_from(">H", data, 0)[0]
            if kind not in (HFSP_FOLDER, HFSP_FILE):
                continue                        # thread records are not children
            name, _ = _hfs_name(key, 4)
            if not name:
                continue
            child = struct.unpack_from(">I", data, 8)[0]
            self._cache[child] = data
            out.append((name, child, data))
        return out

    def _record(self, cnid):
        """One catalog record by node id, through its thread record when the
        walk has not already passed it."""
        got = self._cache.get(cnid)
        if got is not None:
            return got
        node = self._catalog.find(cnid, self._cat_parent)
        if node is None:
            return None
        for key, data in self._catalog.walk_from(node):
            parent = self._cat_parent(key)
            if parent is None or parent < cnid:
                continue
            if parent > cnid:
                break
            if len(data) >= 2 and struct.unpack_from(">H", data, 0)[0] in (
                    HFSP_FOLDER_THREAD, HFSP_FILE_THREAD):
                owner = struct.unpack_from(">I", data, 4)[0]
                name, _ = _hfs_name(data, 8)
                for child_name, child, rec in self._children(owner):
                    if child_name == name and child == cnid:
                        return rec
        return None

    def _private_dir(self):
        """The node id of the directory a hard link's indirect nodes live in."""
        if self._private is None:
            self._private = 0
            for name, cnid, _rec in self._children(HFSP_ROOT):
                if name == HFSP_PRIVATE_DATA:
                    self._private = cnid
                    break
        return self._private

    def _resolve(self, cnid, rec):
        """A hard link's indirect node, or the record as it stands.

        A hard link is a catalog file carrying the Finder type and creator that
        say so; the file it names lives under the private directory as
        iNode<number>, and the number is in the BSD info.
        """
        if len(rec) < 128 or struct.unpack_from(">H", rec, 0)[0] != HFSP_FILE:
            return cnid, rec
        user_info = rec[48:64]
        if user_info[0:4] != HFSP_HARD_LINK_TYPE or user_info[4:8] != HFSP_HARD_LINK_CREATOR:
            return cnid, rec
        inode = struct.unpack_from(">I", rec, 44)[0]        # permissions.special
        parent = self._private_dir()
        if not parent:
            return cnid, rec
        for name, child, child_rec in self._children(parent):
            if name == f"iNode{inode}":
                return child, child_rec
        return cnid, rec

    # -- forks -------------------------------------------------------------
    def _overflow(self, cnid, resource=False):
        """The extents a fork continues into, from the extents overflow tree."""
        want = (0xFF if resource else 0x00, cnid, 0)

        def key_of(key):
            if len(key) < 10:
                return None
            fork_type = key[0]
            file_id, start = struct.unpack_from(">II", key, 2)
            return (fork_type, file_id, start)

        node = self._extents.find(want, key_of)
        if node is None:
            return []
        out = []
        for key, data in self._extents.walk_from(node):
            k = key_of(key)
            if k is None or k < want:
                continue
            if k[0] != want[0] or k[1] != cnid:
                break
            for i in range(8):
                if 8 * i + 8 > len(data):
                    break
                start, count = struct.unpack_from(">II", data, i * 8)
                if count:
                    out.append((start, count))
        return out

    def _fork(self, cnid, rec, resource=False):
        """(size, extents) for a file's data or resource fork, overflow included."""
        off = 168 if resource else 88
        if len(rec) < off + 80:
            return 0, []
        size, extents = _hfs_fork(rec, off)
        covered = sum(c for _s, c in extents)
        need = -(-size // self.block_size) if self.block_size else 0
        if covered < need:
            extents += self._overflow(cnid, resource)
        return size, extents

    def _read_extents(self, extents, want, start=0):
        out, pos = bytearray(), 0
        for first, count in extents:
            span = count * self.block_size
            if pos + span <= start:
                pos += span
                continue
            skip = max(0, start - pos)
            take = min(span - skip, want - len(out))
            out += read_at(self.fh,
                           self.base + first * self.block_size + skip, take)
            pos += span
            if len(out) >= want:
                break
        return bytes(out[:want])

    # -- attributes --------------------------------------------------------
    def _xattr(self, cnid, name):
        """One extended attribute's bytes, or None. Only the inline form is
        read: an attribute large enough to need its own fork is not one this
        walker consumes."""
        if self._attrs is None:
            return None

        def key_of(key):
            if len(key) < 8:
                return None
            return struct.unpack_from(">I", key, 2)[0]

        node = self._attrs.find(cnid, key_of)
        if node is None:
            return None
        for key, data in self._attrs.walk_from(node):
            k = key_of(key)
            if k is None or k < cnid:
                continue
            if k > cnid:
                break
            # HFSPlusAttrKey with its length word already stripped: pad, file
            # id, start block, then the name's length in UTF-16 units at 10 and
            # the name itself at 12.
            got, _ = _hfs_name(key, 10)
            if got != name or len(data) < 16:
                continue
            if struct.unpack_from(">I", data, 0)[0] != 0x10:    # inline data
                continue
            size = struct.unpack_from(">I", data, 12)[0]
            return data[16:16 + size]
        return None

    # -- the walker surface ------------------------------------------------
    def free_extents(self, min_bytes=0):
        """[(byte offset, length)] for the runs of space the volume says are free.

        HFS+ keeps an allocation file, one bit per allocation block, set when the
        block is in use. Its fork record sits in the volume header, so it is read
        the same way any other fork is, and it continues into the extents
        overflow tree if it outgrew its eight descriptors.

        **The bits run most significant first**, which is the opposite of NTFS
        and exFAT: the first bit of the bitmap is the top bit of the first byte
        (Apple TN1150). A count of free blocks cannot tell the two orders apart,
        because a byte holds the same number of zero bits either way. What tells
        them apart is position, and reading this volume the wrong way round
        reports blocks that live files occupy as free.

        Offsets are into the image rather than the volume, so a caller reading
        the whole disk can use them directly. ``min_bytes`` drops runs too short
        to hold anything worth recovering.
        """
        block = self.block_size
        if not block or not self.total_blocks:
            return []
        vh = read_at(self.fh, self.base + HFSP_VH_OFF, 512)
        if len(vh) < 512:
            return []
        size, extents = _hfs_fork(vh, HFSP_ALLOC_FORK)
        need = (self.total_blocks + 7) // 8
        if sum(c for _s, c in extents) * block < min(size or need, need):
            try:
                extents = extents + self._overflow(HFSP_ALLOC)
            except (ValueError, struct.error):
                pass                             # what the header holds is all there is
        bits = self._read_extents(extents, need, 0)
        if not bits:
            return []
        total = min(len(bits) * 8, self.total_blocks)

        runs, run_start, pos = [], None, 0
        while pos < total:
            byte = bits[pos >> 3]
            if not (pos & 7) and pos + 8 <= total and byte in (0x00, 0xFF):
                if byte == 0x00:                 # eight free blocks
                    if run_start is None:
                        run_start = pos
                elif run_start is not None:      # eight used ones
                    runs.append((run_start, pos - run_start))
                    run_start = None
                pos += 8
                continue
            if byte & (0x80 >> (pos & 7)):
                if run_start is not None:
                    runs.append((run_start, pos - run_start))
                    run_start = None
            elif run_start is None:
                run_start = pos
            pos += 1
        if run_start is not None:
            runs.append((run_start, total - run_start))

        out = []
        for first, n in runs:
            length = n * block
            if length >= min_bytes:
                out.append((self.base + first * block, length))
        return out

    def inode(self, cnid):
        return cnid

    def entry(self, cnid):
        rec = self._record(cnid)
        if not rec or len(rec) < 2:
            return None
        kind = struct.unpack_from(">H", rec, 0)[0]
        if kind == HFSP_FOLDER:
            mtime = hfs_time(struct.unpack_from(">I", rec, 16)[0])
            mode = struct.unpack_from(">H", rec, 42)[0] or (S_IFDIR | 0o755)
            return (mode | S_IFDIR, 0, mtime)
        if kind != HFSP_FILE:
            return None
        target, rec = self._resolve(cnid, rec)
        mtime = hfs_time(struct.unpack_from(">I", rec, 16)[0])
        mode = struct.unpack_from(">H", rec, 42)[0]
        size, _extents = self._fork(target, rec)
        blob = self._xattr(target, HFSP_DECMPFS)
        if blob and len(blob) >= 16:
            size = struct.unpack_from("<Q", blob, 8)[0]
        return (mode or 0o100644, size, mtime)

    def listdir(self, cnid):
        out = []
        for name, child, _rec in self._children(cnid):
            out.append((name, child))
        return out

    def named_streams(self, cnid):
        """[(name, size)] for a resource fork carrying anything. A resource fork
        is content the file's own size does not account for, so it is worth
        saying it is there; it is not listed as a file of its own."""
        rec = self._record(cnid)
        if not rec or len(rec) < 2 or struct.unpack_from(">H", rec, 0)[0] != HFSP_FILE:
            return []
        target, rec = self._resolve(cnid, rec)
        size, _extents = self._fork(target, rec, resource=True)
        return [("rsrc", size)] if size else []

    def read_file(self, cnid, size):
        rec = self._record(cnid)
        if not rec or len(rec) < 2 or struct.unpack_from(">H", rec, 0)[0] != HFSP_FILE:
            return
        target, rec = self._resolve(cnid, rec)
        blob = self._xattr(target, HFSP_DECMPFS)
        if blob:
            yield from self._read_compressed(target, rec, blob)
            return
        fork_size, extents = self._fork(target, rec)
        want = fork_size if size is None else min(size, fork_size)
        done = 0
        while done < want:
            chunk = self._read_extents(extents, min(1 << 20, want - done), done)
            if not chunk:
                break
            yield chunk
            done += len(chunk)

    def _read_compressed(self, cnid, rec, blob):
        """A file whose data lives in the decmpfs attribute or its resource fork.

        The attribute's header gives the method and the size the file reports.
        Type 3 keeps a zlib stream in the attribute itself; type 4 keeps one
        zlib stream per 64 KiB block in the resource fork, behind a table of
        offsets. The other methods are LZVN and LZFSE, which the standard
        library cannot inflate.
        """
        if len(blob) < 16 or blob[0:4] != HFSP_DECMPFS_MAGIC:
            raise HfsUnreadable("the compression attribute is not one this reader knows")
        method, size = struct.unpack_from("<IQ", blob, 4)
        import zlib                              # only decmpfs and IFS need it
        if method in (3, 5):
            body = blob[16:]
            if body[:1] == b"\xff":
                yield body[1:1 + size]
                return
            yield zlib.decompress(body)[:size]
            return
        if method == 4:
            _rsize, extents = self._fork(cnid, rec, resource=True)
            head = self._read_extents(extents, 512)
            if len(head) < 4:
                raise HfsUnreadable("the compressed resource fork is unreadable")
            data_off = struct.unpack_from(">I", head, 0)[0]
            table = self._read_extents(extents, 4, data_off)
            if len(table) < 4:
                raise HfsUnreadable("the compressed resource fork has no block table")
            count = struct.unpack_from("<I", table, 0)[0]
            if count > 1 << 20:
                raise HfsUnreadable("the compressed resource fork's block table is absurd")
            entries = self._read_extents(extents, count * 8, data_off + 4)
            produced = 0
            for i in range(count):
                off, blen = struct.unpack_from("<II", entries, i * 8)
                piece = self._read_extents(extents, blen, data_off + off)
                out = piece[1:] if piece[:1] == b"\xff" else zlib.decompress(piece)
                take = min(len(out), size - produced)
                yield out[:take]
                produced += take
                if produced >= size:
                    return
            return
        raise HfsUnreadable(
            f"the file is compressed with method {method}, which needs LZVN or "
            f"LZFSE and is not read here")


class Qnx4Walker:
    """List and read files from a QNX4 filesystem, same interface as the
    walkers above. A node is the kernel's inode number: block * 8 + index of
    the 64-byte inode entry, blocks counted from the partition start."""

    root = QNX4_ROOT_NODE

    def __init__(self, fh, base):
        self.fh, self.base = fh, base

    def _raw(self, num):
        blk, ndx = divmod(num, 8)
        raw = read_at(self.fh,
                      self.base + blk * QNX4_BLOCK + ndx * QNX4_DIRENT,
                      QNX4_DIRENT)
        return raw if len(raw) == QNX4_DIRENT else None

    def inode(self, num):
        return self._raw(num)

    def entry(self, num):
        raw = self._raw(num)
        if not raw:
            return None
        mode = struct.unpack_from("<H", raw, 50)[0]      # di_mode
        size = struct.unpack_from("<I", raw, 16)[0]      # di_size
        mtime = struct.unpack_from("<I", raw, 36)[0]     # di_mtime
        return mode, size, mtime

    def _extents(self, raw):
        """Yield (first_block_1based, size_in_blocks) per extent, following
        the xblk chain exactly as fs/qnx4/inode.c qnx4_block_map() does."""
        first_blk, first_sz = struct.unpack_from("<II", raw, 20)
        nx = struct.unpack_from("<H", raw, 48)[0]        # di_num_xtnts
        if nx >= 1 and first_blk and first_sz:
            yield first_blk, first_sz
        left = nx - 1
        xblk = struct.unpack_from("<I", raw, 28)[0]      # di_xblk
        seen = set()
        while left > 0 and xblk and xblk not in seen:
            seen.add(xblk)
            buf = read_at(self.fh, self.base + (xblk - 1) * QNX4_BLOCK,
                          QNX4_BLOCK)
            if len(buf) < QNX4_BLOCK or buf[496:503] != QNX4_XBLK_SIG:
                return                                   # not a valid xblk
            for i in range(min(buf[8], 60)):             # xblk_num_xtnts
                if left <= 0:
                    return
                b, s = struct.unpack_from("<II", buf, 16 + i * 8)
                if b and s:
                    yield b, s
                left -= 1
            xblk = struct.unpack_from("<I", buf, 0)[0]   # xblk_next_xblk

    def listdir(self, num):
        raw = self._raw(num)
        if not raw:
            return []
        if (struct.unpack_from("<H", raw, 50)[0] & 0o170000) != S_IFDIR:
            return []
        size = struct.unpack_from("<I", raw, 16)[0]
        out, done = [], 0
        for blk, nblks in self._extents(raw):
            for j in range(nblks):
                if done >= size:
                    break
                sbnum = blk - 1 + j
                buf = read_at(self.fh, self.base + sbnum * QNX4_BLOCK,
                              QNX4_BLOCK)
                if len(buf) < QNX4_BLOCK:
                    break
                for ix in range(8):
                    e = buf[ix * QNX4_DIRENT:(ix + 1) * QNX4_DIRENT]
                    if e[0] == 0 or not (e[63] & (QNX4_F_USED | QNX4_F_LINK)):
                        continue                         # fs/qnx4/qnx4.h:94-97
                    if e[63] & QNX4_F_LINK:
                        name = e[0:48].split(b"\x00")[0]
                        iblk = struct.unpack_from("<I", e, 48)[0]
                        child = (iblk - 1) * 8 + e[52]   # fs/qnx4/namei.c:103
                    else:
                        name = e[0:16].split(b"\x00")[0]
                        child = sbnum * 8 + ix
                    name = name.decode("utf-8", "replace")
                    if name not in (".", ".."):
                        out.append((name, child))
                done += QNX4_BLOCK
        return out

    def read_file(self, num, size):
        raw = self._raw(num)
        if not raw:
            return
        left = size
        for blk, nblks in self._extents(raw):
            if left <= 0:
                return
            off = self.base + (blk - 1) * QNX4_BLOCK
            avail = min(nblks * QNX4_BLOCK, left)
            pos = 0
            while pos < avail:
                take = min(1 << 20, avail - pos)
                buf = read_at(self.fh, off + pos, take)
                if len(buf) < take:
                    buf += bytes(take - len(buf))
                yield buf
                pos += take
            left -= avail


def identify_qnx4(fh, base, size=None):
    """Return ("qnx4", lines) if a QNX4 filesystem starts at base, else None.

    Mirrors what the kernel itself requires to mount (fs/qnx4/inode.c
    qnx4_checkroot and qnx4_iget): the superblock's RootDir entry must be
    named "/" with a directory mode and a sane first extent, and the root
    directory's first extent must carry a ".bitmap" entry. Two bytes of "/"
    alone would be a coincidence; the resolved .bitmap name is not.
    """
    sb = read_at(fh, base + QNX4_BLOCK, QNX4_DIRENT)
    if len(sb) < QNX4_DIRENT or sb[0:2] != b"/\x00":
        return None
    if (struct.unpack_from("<H", sb, 50)[0] & 0o170000) != S_IFDIR:
        return None
    first_blk, first_sz = struct.unpack_from("<II", sb, 20)
    if not (1 <= first_blk and 1 <= first_sz <= 65536):
        return None
    bitmap = None
    for j in range(first_sz):
        buf = read_at(fh, base + (first_blk - 1 + j) * QNX4_BLOCK, QNX4_BLOCK)
        if len(buf) < QNX4_BLOCK:
            break
        for ix in range(8):
            e = buf[ix * QNX4_DIRENT:(ix + 1) * QNX4_DIRENT]
            if e[0:8] == b".bitmap\x00":                 # strcmp in checkroot
                bitmap = e
                break
        if bitmap:
            break
    if bitmap is None:
        return None
    bsize = struct.unpack_from("<I", bitmap, 16)[0]      # .bitmap di_size, bytes
    total = bsize * 8         # one bit per block, fs/qnx4/inode.c:142 (statfs)
    mtime = struct.unpack_from("<I", sb, 36)[0]          # RootDir di_mtime
    return "qnx4", [
        f"root dir     block {first_blk:,}, {first_sz} block(s), "
        f"modified {stamp(mtime)}",
        f"volume       {total:,} blocks of 512 ({human(total * QNX4_BLOCK)}) "
        f"per the .bitmap",
        "layout       64-byte inode entries inline in directories; names over "
        "16 bytes linked via .inodes",
    ]


# ---------------------------------------------------------------------------
# QNX flash filesystems: ETFS and EFS.
#
# These are QNX's two on-flash filesystems, the kind a head unit stores its
# manufacturing and configuration data on. QNX does not publish either byte
# layout. Both structures below are transcribed from the Kaitai .ksy specs in
# NetherlandsForensicInstitute/qnxmount (Apache-2.0), a peer institute's
# vehicle-forensics reader. Its ETFS spec cross-references QNX's own fs/etfs.h
# and its EFS spec fs/f3s_spec.h, the same way the qnx6 code above is sourced
# to the Linux driver. The Kaitai runtime is NOT taken as a dependency; only
# the field layouts are transcribed, into the same hand-written struct style,
# so this stays standard library only.
#
# Validated by round-trip against qnxmount's own committed test images: every
# file name, mode, owner, mtime, symlink target and byte of file content
# matched the tar archive built from the same live filesystem, ETFS 32 of 32
# entries and EFS 31 of 31. The tar archives were produced by qnxmount's build
# scripts on QNX, an implementation independent of this one.
#
# Both are typically imaged bare, with no partition table, so they arrive as
# the whole-image region and are read at base 0.
#
# ETFS is transaction based. The flash is a run of fixed-size pages, each
# holding <pagesize> bytes of user data followed by a 16-byte transaction
# record, which on real NAND lives in the spare/out-of-band area:
#     fid u4, cluster u4, nclusters u2, tacode u1, dacode u1, sequence u4
# The live state is rebuilt by keeping, for every (fid, cluster), the record
# with the highest sequence number, and ignoring pages whose transaction code
# is not "ok" or "ecc" (erased and 0xFF-filler pages carry a junk cluster).
# Files are addressed by a fixed file-id scheme from fs/etfs.h: root 0,
# .filetable 1, .badblks 2, .counts 3, .lost+found 4, .reserved 5, first real
# file 6. The .filetable (fid 1) is itself a file whose data is 64-byte entries
# indexed by fid, each carrying a file's parent id, mode, owner, times, size
# and short name; a name longer than 32 bytes is continued in an extension
# entry the short entry points at.
# Source: qnxmount/etfs/parser.ksy and qnxmount/etfs/interface.py, fs/etfs.h.
# ---------------------------------------------------------------------------
ETFS_TRANS_SIZE = 16
ETFS_ENTRY_SIZE = 64
ETFS_FID_ROOT, ETFS_FID_FTABLE = 0, 1
ETFS_RESERVED = {1: ".filetable", 2: ".badblks", 3: ".counts",
                 4: ".lost+found", 5: ".reserved"}
ETFS_PAGE_SIZES = (512, 1024, 2048, 4096, 8192, 16384)


def _etfs_scan_transactions(fh, base, pagesize, n, want_fid=None, cap=None):
    """Yield (page_index, fid, cluster, tacode, sequence) for pages whose
    transaction code is ok or ecc. Reads in blocks to avoid a syscall per page.
    Stops after cap pages if given, and filters to want_fid if given."""
    unit = pagesize + ETFS_TRANS_SIZE
    limit = n if cap is None else min(n, cap)
    BLK = 4096
    start = 0
    while start < limit:
        count = min(BLK, limit - start)
        buf = read_at(fh, base + start * unit, count * unit)
        if len(buf) < count * unit:
            count = len(buf) // unit
        for k in range(count):
            t = buf[k * unit + pagesize: k * unit + unit]
            if len(t) < ETFS_TRANS_SIZE:
                break
            fid, cluster = struct.unpack_from("<II", t, 0)
            if fid == 0xFFFFFFFF:
                continue
            if (t[10] & 0x0F) not in (0, 1):     # keep only ok / ecc pages
                continue
            if want_fid is not None and fid != want_fid:
                continue
            seq = struct.unpack_from("<I", t, 12)[0]
            yield start + k, fid, cluster, t[10], seq
        start += count
        if count == 0:
            break


def _etfs_parse_entry(raw):
    """One 64-byte .filetable entry, or None."""
    if len(raw) < ETFS_ENTRY_SIZE:
        return None
    efid, pfid = struct.unpack_from("<HH", raw, 0)
    is_ext = efid == 0x8000
    no_parent = pfid == 0xFFFF
    etype = int(is_ext) + int(no_parent) * 2
    e = dict(efid=efid, pfid=pfid, is_ext=is_ext, is_solo=efid == 0x0000,
             is_valid=efid != 0xFFFF, body=None, full=None)
    if etype == 0:                                # file entry
        mode, uid, gid, atime, mtime, ctime, size = struct.unpack_from("<7I", raw, 4)
        name = raw[32:64].split(b"\x00", 1)[0].decode("utf-8", "replace")
        e["body"] = dict(mode=mode, uid=uid, gid=gid, mtime=mtime,
                         ctime=ctime, size=size, name=name)
    elif etype == 1:                              # extension-name entry
        e["body"] = dict(name=raw[4:63].split(b"\x00", 1)[0].decode("utf-8", "replace"))
    return e


class EtfsWalker:
    """Reconstruct an ETFS filesystem by replaying its transactions, then walk
    it through the shared collect()/extract interface. A node is a file id."""

    root = ETFS_FID_ROOT

    def __init__(self, fh, base, size, pagesize):
        self.fh, self.base, self.bs = fh, base, pagesize
        self.unit = pagesize + ETFS_TRANS_SIZE
        self.n = size // self.unit
        # current page for every (fid, cluster): the highest sequence wins, and
        # for equal sequences the later physical page, matching qnxmount.
        cur = {}
        for pi, fid, cluster, ta, seq in _etfs_scan_transactions(fh, base, pagesize, self.n):
            d = cur.setdefault(fid, {})
            if cluster not in d or seq >= d[cluster][0]:
                d[cluster] = (seq, pi)
        self.cur = cur
        self.ftable = self._build_ftable()
        self._resolve_names()
        self.kids = self._build_children()

    def _page_data(self, page_index):
        return read_at(self.fh, self.base + page_index * self.unit, self.bs)

    def _build_ftable(self):
        per = self.bs // ETFS_ENTRY_SIZE
        pages = self.cur.get(ETFS_FID_FTABLE, {})
        if not pages:
            return []
        ftable = []
        for cluster in range(max(pages) + 1):
            if cluster not in pages:
                ftable.extend([None] * per)
                continue
            data = self._page_data(pages[cluster][1])
            for k in range(per):
                ftable.append(_etfs_parse_entry(data[k * ETFS_ENTRY_SIZE:
                                                     (k + 1) * ETFS_ENTRY_SIZE]))
        return ftable

    def _resolve_names(self):
        ft = self.ftable
        for e in ft:
            if e is None or e["body"] is None:
                continue
            if e["is_ext"] or not e["is_valid"]:
                e["full"] = None
            elif e["is_solo"]:
                e["full"] = e["body"]["name"]
            else:
                ext = ft[e["efid"]] if e["efid"] < len(ft) else None
                if ext is not None and ext["is_ext"] and ext["body"]:
                    e["full"] = e["body"]["name"] + ext["body"]["name"]
                else:
                    e["full"] = e["body"]["name"]

    def _build_children(self):
        """parent fid -> [(name, fid)]. An entry whose parent id no longer
        resolves to a real named entry (its page was lost, or the slot is
        unallocated) is an orphan; qnxmount routes those to /recovered_files, so
        they are attached to the root under that name rather than dropped."""
        kids = {}
        ft = self.ftable
        self.orphans = []
        for fid, e in enumerate(ft):
            if fid == ETFS_FID_ROOT or e is None or e["full"] is None:
                continue
            pf = e["pfid"]
            parent_ok = (0 <= pf < len(ft) and ft[pf] is not None
                         and ft[pf]["full"] is not None)
            if parent_ok:
                kids.setdefault(pf, []).append((e["full"], fid))
            else:
                self.orphans.append((e["full"], fid))
        return kids

    def listdir(self, fid):
        if fid == -1:                             # synthetic recovered_files dir
            return sorted(self.orphans)
        out = list(self.kids.get(fid, []))
        if fid == ETFS_FID_ROOT and self.orphans:
            out.append(("recovered_files", -1))
        return sorted(out)

    def entry(self, fid):
        if fid == -1:                             # synthetic recovered_files dir
            return (S_IFDIR | 0o755, 0, 0)
        e = self.ftable[fid] if 0 <= fid < len(self.ftable) else None
        if e is None or e["body"] is None:
            return None
        b = e["body"]
        return (b["mode"], b["size"], b["mtime"])

    def read_file(self, fid, size):
        if fid == -1:
            return
        pages = self.cur.get(fid, {})
        left = size
        if not pages:
            return
        for cluster in range(max(pages) + 1):
            if left <= 0:
                return
            if cluster in pages:
                buf = self._page_data(pages[cluster][1])
            else:
                buf = b"\xff" * self.bs           # a hole reads as 0xFF on flash
            if len(buf) < self.bs:
                buf = buf + bytes(self.bs - len(buf))
            take = min(self.bs, left)
            yield buf[:take]
            left -= take


# ---------------------------------------------------------------------------
# EFS is QNX's other flash filesystem, the F3S "flash 3" format. It is not
# transaction based: the flash is divided into erase units, each unit carries a
# growing-downward array of 32-byte extent headers at its end and the extent
# data (text) packed from the front. An extent header names the data's offset
# and size, a "next" pointer chaining the extents of one object, and a "super"
# pointer to a newer version that supersedes it, which is how EFS does its
# copy-on-write. Physical units are mapped to logical numbers through a per-unit
# logi record, so a pointer is (logical unit, extent index).
#
# A directory's first extent points at its first child; each child extent's
# "next" chains to the following sibling, and each child's own "first" descends
# into it. A file's extents chained by "next" are its data. The partition is
# found by its boot record, an extent whose text begins with the ASCII
# signature "QSSL_F3S"; the unit size is read from the unit_info at the start of
# the first unit. Source: qnxmount/efs/parser.ksy and interface.py, fs/f3s_spec.h.
# ---------------------------------------------------------------------------
EFS_SIG = b"QSSL_F3S"
EFS_EXTHDR = 32


def _efs_boot(fh, base, scan_bytes):
    """Find the QSSL_F3S boot record in the first scan_bytes of the region and
    return its parsed boot_info, or None. The boot_info starts 4 bytes before
    the signature (struct_size u2, rev_major u1, rev_minor u1, then the sig)."""
    chunk = read_at(fh, base, scan_bytes)
    at = chunk.find(EFS_SIG)
    if at < 4:
        return None
    o = at - 4
    struct_size = struct.unpack_from("<H", chunk, o)[0]
    rev_major, rev_minor = chunk[o + 2], chunk[o + 3]
    if struct_size != 0x18 or rev_major != 3 or rev_minor != 0:
        return None
    unit_index, unit_total, unit_spare, align_pow2 = struct.unpack_from("<HHHH", chunk, o + 12)
    root = struct.unpack_from("<HH", chunk, o + 20)
    return dict(unit_index=unit_index, unit_total=unit_total, unit_spare=unit_spare,
                align_pow2=align_pow2, root=root, sig_at=at)


def _efs_unit_size(fh, base):
    """The unit size from the unit_info at the start of the first unit. reserve
    bytes must read 0xFF for this to be a plausible EFS unit header."""
    b = read_at(fh, base, 16)
    if len(b) < 16 or b[3] != 0xFF or b[6:8] != b"\xff\xff":
        return None
    unit_pow2 = struct.unpack_from("<H", b, 4)[0]
    if not (9 <= unit_pow2 <= 30):
        return None
    return 1 << unit_pow2


class EfsWalker:
    """Reconstruct an EFS (F3S) filesystem and walk it through the shared
    interface. A node is a parsed directory entry (a dict)."""

    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        self.unit_size = _efs_unit_size(fh, base)
        boot = _efs_boot(fh, base, min(self.unit_size * 4, 1 << 24))
        self.boot = boot
        self.align = boot["align_pow2"]
        self.units = [read_at(fh, base + u * self.unit_size, self.unit_size)
                      for u in range(boot["unit_total"])]
        self.logi_map = self._logi_map()
        self.root = self._as_node(self._get_ext(boot["root"]))[1]

    def _ext_header(self, unit, i):
        off = self.unit_size - EFS_EXTHDR * (i + 1)
        if off < 0 or off + EFS_EXTHDR > len(unit):
            return None
        h = unit[off:off + EFS_EXTHDR]
        s0 = struct.unpack_from("<I", h, 0)[0]
        return dict(no_next=bool((s0 >> 1) & 1), no_super=bool((s0 >> 2) & 1),
                    ext_last=bool((s0 >> 7) & 1), type=(s0 >> 8) & 3,
                    status1=struct.unpack_from("<I", h, 4)[0],
                    toff_hi=h[19], toff_lo=struct.unpack_from("<H", h, 20)[0],
                    tsize=struct.unpack_from("<H", h, 22)[0],
                    next=struct.unpack_from("<HH", h, 24),
                    super=struct.unpack_from("<HH", h, 28))

    def _extents(self, unit):
        exts, i = [], 0
        while True:
            h = self._ext_header(unit, i)
            if h is None:
                break
            exts.append(h)
            if h["ext_last"] or i > 4096:
                break
            i += 1
        return exts

    def _text(self, unit, hdr):
        off = ((hdr["toff_hi"] << 16) + hdr["toff_lo"]) << self.align
        return unit[off:off + hdr["tsize"]]

    @staticmethod
    def _is_spare(exts):
        return (len(exts) == 1
                or (len(exts) == 2 and exts[1]["status1"] == 0xFFFFFFFF))

    def _logi_map(self):
        logi = {}
        for unit in self.units:
            exts = self._extents(unit)
            if len(exts) < 2 or self._is_spare(exts):   # no logi record to read
                continue
            t = self._text(unit, exts[1])            # unit_logi: struct_size, logi
            logi[struct.unpack_from("<H", t, 2)[0]] = (unit, exts)
        return logi

    def _get_ext(self, ptr):
        unit, exts = self.logi_map[ptr[0]]
        hdr = exts[ptr[1]]
        while not hdr["no_super"]:                   # follow to the current version
            ptr = hdr["super"]
            unit, exts = self.logi_map[ptr[0]]
            hdr = exts[ptr[1]]
        return unit, hdr

    def _as_node(self, ext):
        """A directory entry, as the hashable node (first_logi, first_index,
        mode, mtime) the shared walker interface passes around. It stays hashable
        so collect()'s cycle-guard set can hold it; first uniquely identifies the
        object, so it doubles as identity. The name is returned by listdir, not
        carried in the node."""
        unit, hdr = ext
        t = self._text(unit, hdr)
        namelen = t[3]
        first = struct.unpack_from("<HH", t, 4)
        name = t[8:8 + namelen].split(b"\x00", 1)[0].decode("utf-8", "replace")
        so = 8 + ((namelen + 3) & 0xFC)              # name+pad is 4-byte aligned
        mode = struct.unpack_from("<H", t, so + 2)[0]
        mtime = struct.unpack_from("<I", t, so + 12)[0]
        return name, (first[0], first[1], mode, mtime)

    def _chain(self, node):
        first = (node[0], node[1])
        unit, hdr = self._get_ext(first)
        yield unit, hdr
        while not hdr["no_next"]:
            unit, hdr = self._get_ext(hdr["next"])
            yield unit, hdr

    def listdir(self, node):
        out = []
        for unit, hdr in self._chain(node):
            if not hdr["tsize"]:
                break
            out.append(self._as_node((unit, hdr)))
        return out

    def _size(self, node):
        return sum(hdr["tsize"] for _, hdr in self._chain(node))

    def entry(self, node):
        mode = node[2]
        size = self._size(node) if (mode & 0o170000) in (0o100000, 0o120000) else 0
        return (mode, size, node[3])

    def read_file(self, node, size):
        out = bytearray()
        for unit, hdr in self._chain(node):
            out += self._text(unit, hdr)
        yield bytes(out[:size]) if size else bytes(out)


def print_tree(w, num, depth, maxdepth, budget, indent=0, pad=6):
    # A walker that keeps readings rather than instants (FAT32, exFAT) is listed
    # through listdir_records(), so the reading is printed and not the 0 that
    # entry() returns for its mtime, which _fmt_time() shows as 1970-01-01.
    readings = hasattr(w, "listdir_records")
    listing = w.listdir_records(num) if readings else [(n, i, None) for n, i in w.listdir(num)]
    for name, ino, recorded in listing:
        if budget[0] <= 0:
            print(f"{' '*pad}{'  '*indent}... listing truncated, raise --list-max")
            return
        budget[0] -= 1
        ent = w.entry(ino)
        if not ent:
            continue
        mode, size, mtime = ent
        isdir = bool(mode & S_IFDIR)
        kind = "dir " if isdir else ("link" if mode & S_IFLNK == S_IFLNK else "file")
        col = max(12, 44 - 2 * indent)
        shown = "" if isdir else f"{human(size):>11}"
        when = _fmt_reading(recorded) if readings else _fmt_time(mtime)
        print(f"{' '*pad}{'  '*indent}{kind} {name:<{col}} {shown}  {when}")
        # A file can carry content its own size does not account for. NTFS calls
        # those alternate data streams; the walker that has them says so here,
        # because nothing else in the listing would show that the bytes exist.
        for sname, ssize in (getattr(w, "named_streams", lambda _n: [])(ino) or []):
            print(f"{' '*pad}{'  '*indent}     stream {sname:<{max(6, col - 7)}} "
                  f"{human(ssize):>11}")
        if isdir and depth < maxdepth:
            print_tree(w, ino, depth + 1, maxdepth, budget, indent + 1, pad)


# ---------------------------------------------------------------------------
# QNX IFS boot images.
#
# An IFS is not a mountable filesystem, it is a bootable image: a startup
# header, the startup code, then the image filesystem, usually compressed.
# Constants and field order from sys/startup.h:
#     STARTUP_HDR_SIGNATURE 0x00ff7eeb   startup.h:88
#     STARTUP_HDR_VERSION   1            startup.h:89
# and QNX's own "The startup header" page, which lists the same fields in the
# same order. Summing those field widths gives 256 bytes, which the header's
# own header_size field confirms on every image tested.
#
# machine is documented as "Machine type from sys/elf.h", so it is reported
# through the ELF constants (EM_AARCH64 183, EM_ARM 40, EM_386 3, EM_X86_64 62
# from linux/include/uapi/linux/elf-em.h).
#
# The image filesystem begins at startup_size. flags1 carries the compression
# method (COMPRESS_MASK 0x1c: none 0x00, zlib 0x04, lzo 0x08, ucl 0x0c;
# startup.h:73-80). When compressed, the imagefs is a run of blocks, each a
# 2-byte big-endian compressed length followed by that many bytes, decompressing
# to at most 64 KiB, terminated by a zero length. dumpifs.c:563-595. All real
# evidence to hand is UCL, and there is no UCL decompressor in the standard
# library, so a small one is carried below rather than taking a dependency: this
# tool's whole point is that it installs nothing. zlib is handled through the
# standard library. lzo and the Harman Becker HBCIFS container are recognised but
# not decompressed here, because no sample exists to validate a reader against.
# ---------------------------------------------------------------------------
QNX_IFS_SIG = 0x00FF7EEB
QNX_IFS_VER = 1
IFS_F = dict(signature=0, version=4, flags1=6, flags2=7, header_size=8,
             machine=10, startup_vaddr=12, paddr_bias=16, image_paddr=20,
             ram_paddr=24, ram_size=28, startup_size=32, stored_size=36,
             imagefs_paddr=40, imagefs_size=44, preboot_size=48)
IFS_HDR_SIZE = 256
ELF_MACHINE = {3: "x86", 40: "ARM 32 bit", 62: "x86-64", 183: "ARM 64 bit"}

# startup_header flags1, sys/startup.h:73-80. dumpifs.c:533 switches on the
# masked value directly, so the names below are the masked constants, not shifted.
IFS_COMPRESS_MASK  = 0x1c
IFS_COMPRESS = {0x00: "none", 0x04: "zlib", 0x08: "lzo", 0x0c: "ucl"}
IFS_FLAG_BIGENDIAN = 0x02

# image_header, the "imagefs" filesystem header, sys/image.h:42-56. Every field
# is a 4-byte unsigned long (32-bit target, ILP32; dumpifs.c byte-swaps each with
# ENDIAN_RET32). image_size runs from this header to the end of the trailer;
# dir_offset is the first directory entry, hdr_dir_size the byte past the last.
IMG_SIG = b"imagefs"
IMGH = dict(flags=7, image_size=8, hdr_dir_size=12, dir_offset=16,
            boot_ino=20, script_ino=36, chain_paddr=40, mountflags=84)

# union image_dirent, sys/image.h:75-108. A flat, contiguous table of variable
# length records; each starts with the 24-byte image_attr, then a type-specific
# tail keyed on mode & S_IFMT, then the entry's full path relative to the image
# root (no leading slash). attr.size is the whole record's length and steps to
# the next entry; size 0 ends the table. attr.ino 0 means skip. There is no
# per-directory child list: the tree is carried entirely in the path strings.
IFS_ATTR = dict(size=0, extattr_offset=2, ino=4, mode=8, gid=12, uid=16, mtime=20)
IFS_ATTR_LEN = 24
# QNX sys/stat.h:210-218. S_IFNAM 0x5000 is QNX specific; the rest match Unix,
# so the shared collect()/print_tree() read dir, regular and link modes as usual.
IFS_S_IFMT, IFS_S_IFREG, IFS_S_IFDIR, IFS_S_IFLNK = 0xF000, 0x8000, 0x4000, 0xA000


def ucl_nrv2b_decompress(src):
    """Decompress one UCL NRV2B block. This is the _8 (byte at a time, MSB first)
    variant that dumpifs links as ucl_nrv2b_decompress_8. Ported field for field
    from Markus Oberhumer's UCL, src/n2b_d.c and src/getbit.h (getbit_8). The bit
    stream and the literal and offset bytes share one input cursor.

    A wrong port almost never lands on the exact target length, so the caller
    checks the concatenated output against the header's imagefs_size and the
    image trailer checksum rather than trusting this in isolation.
    """
    out = bytearray()
    ilen = 0
    bb = 0
    bits = 0
    last_m_off = 1

    def getbit():
        nonlocal bb, bits, ilen
        if bits == 0:
            bb = src[ilen]
            ilen += 1
            bits = 8
        bits -= 1
        return (bb >> bits) & 1

    while True:
        while getbit():                         # literal run
            out.append(src[ilen])
            ilen += 1
        m_off = 1                               # match offset, high part
        while True:
            m_off = m_off * 2 + getbit()
            if getbit():
                break
        if m_off == 2:                          # reuse the previous offset
            m_off = last_m_off
        else:
            m_off = (m_off - 3) * 256 + src[ilen]
            ilen += 1
            if m_off == 0xFFFFFFFF:             # end of stream
                break
            m_off += 1
            last_m_off = m_off
        m_len = getbit() * 2 + getbit()         # match length
        if m_len == 0:
            m_len = 1
            while True:
                m_len = m_len * 2 + getbit()
                if getbit():
                    break
            m_len += 2
        if m_off > 0xd00:
            m_len += 1
        pos = len(out) - m_off
        out.append(out[pos])                    # copy m_len + 1 bytes, forward,
        pos += 1                                # so overlapping runs work
        for _ in range(m_len):
            out.append(out[pos])
            pos += 1
    return bytes(out)


def ifs_decompress_blocks(stored, decompress):
    """Concatenate the decompressed blocks. Each block is a 2-byte big-endian
    compressed length then that many bytes; a zero length ends the run.
    dumpifs.c:563-595."""
    out = bytearray()
    pos = 0
    while pos + 2 <= len(stored):
        ln = struct.unpack_from(">H", stored, pos)[0]
        if ln == 0:
            break
        out += decompress(stored[pos + 2:pos + 2 + ln])
        pos += 2 + ln
    return bytes(out)


class IfsUnsupported(Exception):
    """Raised when an IFS is recognised but its contents cannot be read here,
    for example an lzo-compressed image or the HBCIFS container. The header is
    still reported; only the walk is declined, and the reason is said out loud."""


class IfsWalker:
    """List and read files from a QNX IFS boot image. The whole image filesystem
    is decompressed into memory once (a compressed block cannot be seeked into),
    then the flat directory table is parsed and a tree is built from the full
    path strings. Same interface as the other walkers, so collect(), print_tree()
    and extract_to_zip() drive it unchanged. A node is the entry's full path."""

    root = ""

    def __init__(self, fh, base):
        self.fh, self.base = fh, base
        hdr = read_at(fh, base, IFS_HDR_SIZE)
        if len(hdr) < IFS_HDR_SIZE or \
                struct.unpack_from("<I", hdr, IFS_F["signature"])[0] != QNX_IFS_SIG:
            raise IfsUnsupported("not a startup header")
        flags1 = hdr[IFS_F["flags1"]]
        if flags1 & IFS_FLAG_BIGENDIAN:
            # No big-endian IFS is to hand to validate the swap against, so the
            # walk is declined rather than guessed. The header still reports.
            raise IfsUnsupported("big-endian image, not read here")
        self.compress = IFS_COMPRESS.get(flags1 & IFS_COMPRESS_MASK, "unknown")
        ss = struct.unpack_from("<I", hdr, IFS_F["startup_size"])[0]
        st = struct.unpack_from("<I", hdr, IFS_F["stored_size"])[0]
        isz = struct.unpack_from("<I", hdr, IFS_F["imagefs_size"])[0]
        stored = read_at(fh, base + ss, st - ss)
        if self.compress == "none":
            img = stored[:isz]
        elif self.compress == "ucl":
            img = ifs_decompress_blocks(stored, ucl_nrv2b_decompress)
        elif self.compress == "zlib":
            import zlib
            img = zlib.decompress(stored)       # a single gzip stream, dumpifs.c:534
        else:
            raise IfsUnsupported(f"{self.compress} compression not read here")
        if img[:len(IMG_SIG)] != IMG_SIG:
            raise IfsUnsupported("no imagefs header after decompression")
        self.img = img
        self.image_size = struct.unpack_from("<I", img, IMGH["image_size"])[0]
        self.hdr_dir_size = struct.unpack_from("<I", img, IMGH["hdr_dir_size"])[0]
        self.dir_offset = struct.unpack_from("<I", img, IMGH["dir_offset"])[0]
        self.decompressed = len(img)
        # A byte-exact self-check that does not depend on this reader: the image
        # trailer holds a 32-bit checksum such that the 32-bit words from the
        # header to the end of the trailer sum to zero (image.h:110, and observed
        # to hold on every Sync G4 volume). A single wrong byte breaks it.
        n = self.image_size // 4
        if n * 4 <= len(img):
            total = sum(struct.unpack_from("<%dI" % n, img, 0)) & 0xFFFFFFFF
            self.cksum_ok = total == 0
        else:
            self.cksum_ok = None
        self._parse_dir()

    def _parse_dir(self):
        img = self.img
        root_mode, root_mtime = IFS_S_IFDIR, 0
        self.nodes = {}                          # path -> (mode, size, mtime)
        self.files = {}                          # path -> (offset, size)
        self.links = {}                          # path -> target string
        self.kids = {"": []}                     # path -> [(name, childpath)]
        dpos = self.dir_offset
        while dpos + IFS_ATTR_LEN <= self.hdr_dir_size:
            size = struct.unpack_from("<H", img, dpos)[0]
            if size < IFS_ATTR_LEN:              # 0 ends the table; <24 is invalid
                break
            ino = struct.unpack_from("<I", img, dpos + IFS_ATTR["ino"])[0]
            mode = struct.unpack_from("<I", img, dpos + IFS_ATTR["mode"])[0]
            mtime = struct.unpack_from("<I", img, dpos + IFS_ATTR["mtime"])[0]
            rec = img[dpos:dpos + size]
            dpos += size
            if ino == 0:
                continue
            typ = mode & IFS_S_IFMT
            if typ == IFS_S_IFREG:
                foff, fsize = struct.unpack_from("<II", rec, IFS_ATTR_LEN)
                path = rec[IFS_ATTR_LEN + 8:].split(b"\x00")[0]
                self._add(path, mode, fsize, mtime)
                self.files[path.decode("utf-8", "replace")] = (foff, fsize)
            elif typ == IFS_S_IFDIR:
                path = rec[IFS_ATTR_LEN:].split(b"\x00")[0]
                self._add(path, mode, 0, mtime)
                if path:
                    self.kids.setdefault(path.decode("utf-8", "replace"), [])
                else:
                    root_mode, root_mtime = mode, mtime
            elif typ == IFS_S_IFLNK:
                soff, ssize = struct.unpack_from("<HH", rec, IFS_ATTR_LEN)
                nb = IFS_ATTR_LEN + 4                 # name and target follow the two u16
                path = rec[nb:].split(b"\x00")[0]
                self.links[path.decode("utf-8", "replace")] = \
                    rec[nb + soff:nb + soff + ssize].decode("utf-8", "replace")
                self._add(path, mode, 0, mtime)
            else:                                # device, fifo, or QNX name special
                path = rec[IFS_ATTR_LEN + 8:].split(b"\x00")[0]
                self._add(path, mode, 0, mtime)
        self.nodes[""] = (root_mode, 0, root_mtime)

    def _add(self, path_b, mode, size, mtime):
        """Place one entry, materialising any parent directories the flat table
        left implicit (a file at a/b/c with no dirent for a or a/b)."""
        path = path_b.decode("utf-8", "replace")
        if path == "":
            return
        parts = path.split("/")
        parent = ""
        for i in range(len(parts) - 1):
            ap = "/".join(parts[:i + 1])
            if ap not in self.nodes:
                self.nodes[ap] = (IFS_S_IFDIR, 0, mtime)
                self.kids.setdefault(parent, [])
                self.kids[parent].append((parts[i], ap))
                self.kids.setdefault(ap, [])
            parent = ap
        if path not in self.nodes:
            self.kids.setdefault(parent, [])
            self.kids[parent].append((parts[-1], path))
        self.nodes[path] = (mode, size, mtime)

    def inode(self, node):
        return self.nodes.get(node)

    def listdir(self, node):
        return sorted(self.kids.get(node, []))

    def entry(self, node):
        return self.nodes.get(node)

    def read_file(self, node, size):
        off, fsize = self.files.get(node, (None, None))
        if off is None:
            return
        yield self.img[off:off + fsize]


# ---------------------------------------------------------------------------
# Extraction (--extract)
#
# Mounting a qnx6 volume is a Linux-only trick. macOS ships no qnx6 driver,
# the WSL2 kernel is built with CONFIG_QNX6FS_FS unset, and the FUSE options
# are Linux-tested. So rather than mount, the same readers that back --list
# copy the logical files straight out into a zip. Pure standard library, so it
# behaves the same on macOS, Windows and Linux, needs no administrator rights,
# and cannot write to the evidence.
# ---------------------------------------------------------------------------
def _zip_time(v):
    d = None
    try:
        d = datetime.datetime.fromtimestamp(v, datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        pass
    if d is None or d.year < 1980:      # the zip format cannot hold earlier
        return (1980, 1, 1, 0, 0, 0)
    return (d.year, d.month, d.day, d.hour, d.minute, d.second)


def collect(w, num, prefix="", depth=0, seen=None, out=None, times=None):
    """Every regular file under this inode, as (path, inode, size, mtime).

    Pass a dict as ``times`` to also receive each path's recorded times, as the
    filesystem stores them, from walkers that keep readings rather than instants.
    FAT and exFAT are those: they hold a wall-clock reading and no zone, so
    ``mtime`` above stays zero for them and the readings arrive here as text
    instead, where nothing downstream can put a zone on them.
    """
    if seen is None:
        seen, out = set(), []
    if depth > 64 or num in seen:
        return out
    seen.add(num)
    if times is not None and hasattr(w, "listdir_records"):
        listing = w.listdir_records(num)
    else:
        listing = [(name, ino, None) for name, ino in w.listdir(num)]
    for name, ino, recorded in listing:
        ent = w.entry(ino)
        if not ent:
            continue
        mode, size, mtime = ent
        path = f"{prefix}/{name}" if prefix else name
        if times is not None and recorded:
            kept = {k: v for k, v in recorded.items() if v}
            if kept:
                times[path] = kept
        if mode & S_IFDIR:
            collect(w, ino, path, depth + 1, seen, out, times)
        elif (mode & 0o170000) == 0o100000:          # regular files only
            out.append((path, ino, size, mtime))
        else:
            out.append((path, ino, None, mtime))     # symlink or special
    return out


def apply_exclude(entries, exclude):
    """Drop entries whose path contains any excluded substring."""
    if not exclude:
        return entries, 0
    keep = [e for e in entries if not any(x in e[0] for x in exclude)]
    return keep, len(entries) - len(keep)


class ProgressEmitter:
    """Throttled machine-readable extraction progress, one JSON object per line.

    Extraction of a head unit volume runs for minutes with nothing on stdout
    until the volume finishes, which reads as a hang to anything driving this
    as a subprocess. --progress emits to STDERR so the human report on stdout
    is untouched and a caller can consume one stream without parsing the other.

    Each line carries exact counts for the volume being written, not estimates:

        {"volume": "@13168672", "files": 1234, "total_files": 1629,
         "bytes": 123456789, "total_bytes": 297023717}

    Throttled to one line per interval, plus a final line per volume so a
    consumer always sees the completed state whatever the timing.
    """

    def __init__(self, stream=None, interval=1.0, clock=time.monotonic):
        self.stream = stream if stream is not None else sys.stderr
        self.interval = interval
        self.clock = clock
        self.last = 0.0

    def __call__(self, volume, files, written, total_files, total_bytes):
        now = self.clock()
        done = total_files and files >= total_files
        if not done and now - self.last < self.interval:
            return
        self.last = now
        self.stream.write(json.dumps({
            "volume": volume, "files": files, "total_files": total_files,
            "bytes": written, "total_bytes": total_bytes,
        }) + "\n")
        self.stream.flush()


def extract_to_zip(zf, w, volume, entries, log, progress=None, may_be_short=False):
    """Stream each regular file into the open zipfile. Returns a tally.

    Returns (files, written, skipped, failed, short). progress, when given, is
    called after each file with (volume, files_done, written_bytes,
    total_files, total_bytes). The totals are exact rather than estimated:
    entries is already the full list for this volume, so both are known before
    the first file is written.

    A file whose blocks lie past the end of the image is a SHORT read: read_at()
    answers a seek past the end of the file with empty bytes, so the walker
    hands back fewer bytes than the inode says and raises nothing. Such a file
    is counted in short, not in files, and logged. With may_be_short, which the
    caller passes when it already knows this volume reaches past the end of the
    image, each file is spooled before it is written so a short one can be
    stored under a name that says how much of it is here. On a volume with no
    reason to expect it the file streams straight into the zip; a short one
    then keeps its name, and the count and the log still say it was short.
    """
    import shutil
    import tempfile
    total_files = sum(1 for _, _, size, _ in entries if size is not None)
    total_bytes = sum(size for _, _, size, _ in entries if size is not None)
    files = written = skipped = failed = short = 0
    for path, ino, size, mtime in entries:
        arc = f"{volume}/{path}"
        if size is None:
            skipped += 1
            continue
        try:
            info = zipfile.ZipInfo(arc, date_time=_zip_time(mtime))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            got = 0
            before = EOF_SHORTFALL["bytes"]
            if may_be_short:
                with tempfile.SpooledTemporaryFile(max_size=32 << 20) as spool:
                    for chunk in w.read_file(ino, size):
                        spool.write(chunk)
                        got += len(chunk)
                    got = min(got, max(size - (EOF_SHORTFALL["bytes"] - before), 0))
                    if got < size:
                        info.filename = f"{arc}.SHORT-{got}-of-{size}-bytes"
                    spool.seek(0)
                    with zf.open(info, "w") as dst:
                        shutil.copyfileobj(spool, dst)
            else:
                with zf.open(info, "w") as dst:
                    for chunk in w.read_file(ino, size):
                        dst.write(chunk)
                        got += len(chunk)
                got = min(got, max(size - (EOF_SHORTFALL["bytes"] - before), 0))
            # A walker pads a block the image ends inside with zeros, so the bytes
            # it handed back are not the bytes that were there; the shortfall
            # read_at() tallied while this file was read is.
            if got < size:
                short += 1
                written += got
                log.append(f"        SHORT {arc}: {got:,} of {size:,} bytes are in the "
                           f"image, the rest lies past its end")
            else:
                files += 1
                written += size
        except Exception as exc:
            failed += 1
            log.append(f"        could not extract {arc}: {exc}")
        if progress is not None:
            progress(volume, files, written, total_files, total_bytes)
    return files, written, skipped, failed, short


# ---------------------------------------------------------------------------
# Triage (--triage)
#
# A head unit can run to tens of gigabytes and most of it is not evidence.
# This ranks what was found so an examiner can decide what to pull first,
# using only what the probe already read.
#
# Two axes, because they disagree and that is the point:
#   ACTIVITY  how much the volume has been written. qnx6 exposes a commit
#             counter in the superblock serial; ext exposes mount count and
#             lifetime kilobytes written. This finds the user-data volume.
#   DENSITY   value per byte. A 4 MiB manufacturing volume holding the unit's
#             addresses, serials and keys outranks 25 GiB of map data on any
#             question an examiner is likely to ask.
#
# Ranking on size alone gets this backwards, which is why both are printed
# rather than combined into one score.
# ---------------------------------------------------------------------------
ENCRYPTED_NAME_MARKERS = ("ECRYPTFS_FNEK_ENCRYPTED",)


def sample_encryption(w, limit=400):
    """Fraction of sampled names that look like encrypted filenames."""
    from collections import deque
    seen = enc = 0
    queue = deque([w.root])
    while queue and seen < limit:
        num = queue.popleft()
        try:
            kids = w.listdir(num)
        except Exception:
            continue
        for name, ino in kids:
            seen += 1
            if any(mk in name for mk in ENCRYPTED_NAME_MARKERS):
                enc += 1
            if seen >= limit:
                break
            ent = w.entry(ino)
            if ent and ent[0] & S_IFDIR and len(queue) < 512:
                queue.append(ino)
    return enc, seen


def triage_row(label, kind, size, used, activity, act_note, when, enc):
    return dict(label=label, kind=kind, size=size, used=used,
                activity=activity, act_note=act_note, when=when, enc=enc)


def print_triage(rows):
    if not rows:
        return
    print("\n" + "=" * 78)
    print("  TRIAGE  what to pull first")
    print("=" * 78)
    print("  Ranked by how much each volume has been written. Read the density")
    print("  column too: a small volume can outrank a large one.\n")
    rows = sorted(rows, key=lambda r: -(r["activity"] or 0))
    print(f"  {'volume':<26}{'type':<10}{'used':>11}{'activity':>14}  last write")
    print("  " + "-" * 74)
    for r in rows:
        act = f"{r['activity']:,}" if r["activity"] is not None else "-"
        print(f"  {r['label'][:25]:<26}{r['kind'][:9]:<10}{human(r['used']):>11}"
              f"{act:>14}  {r['when']}")
        notes = []
        if r["act_note"]:
            notes.append(r["act_note"])
        if r["enc"] and r["enc"][1]:
            e, t = r["enc"]
            if e:
                notes.append(f"{100*e//t}% of sampled names are ENCRYPTED, "
                             f"so contents are not parseable without keys")
        if r["size"]:
            pct = 100.0 * (r["used"] or 0) / r["size"]
            notes.append(f"{pct:.0f}% full of {human(r['size'])}")
        for nline in notes:
            print(f"  {'':<26}{nline}")
    print()
    print("  Pull the top of this list first, then any small volume whose name")
    print("  suggests manufacturing, identity or configuration. Skip volumes")
    print("  that are mostly empty bulk, and do not spend time on encrypted")
    print("  ones until you have the keys.")
    print()


def identify_ifs(fh, base):
    """Return detail lines if a QNX IFS boot image starts here, else None."""
    h = read_at(fh, base, IFS_HDR_SIZE)
    if len(h) < IFS_HDR_SIZE:
        return None
    g32 = lambda k: struct.unpack_from("<I", h, IFS_F[k])[0]
    g16 = lambda k: struct.unpack_from("<H", h, IFS_F[k])[0]
    if g32("signature") != QNX_IFS_SIG:
        return None
    hsz, ver, mach = g16("header_size"), g16("version"), g16("machine")
    ss, st, ifs_sz = g32("startup_size"), g32("stored_size"), g32("imagefs_size")
    flags1 = h[IFS_F["flags1"]]
    method = IFS_COMPRESS.get(flags1 & IFS_COMPRESS_MASK, "unknown")
    endian = "big" if flags1 & IFS_FLAG_BIGENDIAN else "little"

    lines = [f"version      {ver}" + ("" if ver == QNX_IFS_VER
                                      else f"   (STARTUP_HDR_VERSION is {QNX_IFS_VER})"),
             f"header_size  {hsz}" + ("   agrees with the 256-byte struct"
                                      if hsz == IFS_HDR_SIZE else
                                      "   DOES NOT match the 256-byte struct"),
             f"machine      {mach}  ({ELF_MACHINE.get(mach, 'unrecognised ELF machine')})",
             f"flags        0x{flags1:02x} 0x{h[IFS_F['flags2']]:02x}"
             f"   {endian} endian, {method} compression"
             f"   startup_vaddr 0x{g32('startup_vaddr'):08x}",
             f"startup      {human(ss)} of startup code, image filesystem begins at "
             f"0x{ss:x}"]

    stored_ifs = st - ss
    if stored_ifs == ifs_sz:
        how = "stored uncompressed"
    elif 0 < stored_ifs < ifs_sz:
        how = f"stored {method} compressed, {human(ifs_sz)} into {human(stored_ifs)}"
    else:
        how = "stored size and imagefs size disagree"
    lines.append(f"imagefs      {human(ifs_sz)} uncompressed, {how}")
    lines.append(f"total        {human(st)} stored on the partition")

    if method in ("ucl", "zlib", "none") and endian == "little":
        lines.append("contents     listed and extracted with --list and --extract")
    elif endian == "big":
        lines.append("contents     big-endian image, header reported but not walked here")
    elif method == "lzo":
        lines.append("contents     lzo compressed, not read here (no sample to "
                     "validate a reader), see --help")
    else:
        lines.append(f"contents     {method} compression, not read here, see --help")
    return lines


def walker_for(kind, fh, base, size=None):
    """The walker class for a filesystem kind, or None if it has no walker.

    ETFS needs the region size (to page the flash) and its detected page size,
    so callers that want an ETFS walker must pass size.
    """
    if kind and kind.startswith("ext"):
        return ExtWalker(fh, base)
    if kind == "fat32":
        return Fat32Walker(fh, base)
    if kind == "exfat":
        return ExfatWalker(fh, base)
    if kind == "ntfs":
        return NtfsWalker(fh, base)
    if kind in ("hfs+", "hfsx"):
        return HfsPlusWalker(fh, base)
    if kind == "apfs":
        return ApfsWalker(fh, base)
    if kind == "efs":
        return EfsWalker(fh, base)
    if kind == "qnx4":
        return Qnx4Walker(fh, base)
    if kind == "etfs" and size is not None:
        P = etfs_pagesize(fh, base, size)
        return EtfsWalker(fh, base, size, P) if P else None
    if kind == "QNX IFS boot image":
        return IfsWalker(fh, base)
    return None


def _etfs_reserved_match(fh, base, pagesize, n, need=3):
    """True if a fid==1 cluster-0 page parses into a .filetable carrying the
    fixed reserved names at their fixed ids and a directory at the root id.

    The reserved-name check is what makes ETFS detection specific: ETFS has no
    magic number, so a bare page-count match would be a coincidence, but the
    names .filetable/.badblks/.counts at fixed file ids are not.
    """
    per = pagesize // ETFS_ENTRY_SIZE
    if per < 6:                                      # too small to hold fids 0..5
        return False
    unit = pagesize + ETFS_TRANS_SIZE
    for pi, fid, cluster, ta, seq in _etfs_scan_transactions(
            fh, base, pagesize, n, want_fid=ETFS_FID_FTABLE, cap=min(n, 200000)):
        if cluster != 0:
            continue
        data = read_at(fh, base + pi * unit, pagesize)
        r = _etfs_parse_entry(data[0:ETFS_ENTRY_SIZE])
        if not (r and r["body"] and (r["body"]["mode"] & 0o170000) == S_IFDIR):
            continue
        hits = 0
        for rid, name in ETFS_RESERVED.items():
            e = _etfs_parse_entry(data[rid * ETFS_ENTRY_SIZE:(rid + 1) * ETFS_ENTRY_SIZE])
            if e and e["body"] and e["body"].get("name") == name:
                hits += 1
        if hits >= need:
            return True
    return False


def etfs_pagesize(fh, base, size):
    """The ETFS page size for the region, or None. A candidate is accepted only
    when the region divides evenly into (pagesize + 16)-byte pages AND the
    .filetable carries its reserved names, so a chance size match is rejected.
    """
    for P in ETFS_PAGE_SIZES:
        unit = P + ETFS_TRANS_SIZE
        if size < unit or size % unit != 0:
            continue
        if _etfs_reserved_match(fh, base, P, size // unit):
            return P
    return None


def identify_etfs(fh, base, size):
    """Return ("etfs", lines) if an ETFS filesystem fills this region, else None."""
    P = etfs_pagesize(fh, base, size)
    if P is None:
        return None
    return "etfs", [
        f"page size    {P:,} bytes data + {ETFS_TRANS_SIZE} bytes transaction",
        f"pages        {size // (P + ETFS_TRANS_SIZE):,}",
        "layout       transaction based, live state replayed from the spare area",
        "reserved     .filetable/.badblks/.counts/.lost+found/.reserved present",
    ]


def identify_efs(fh, base, size):
    """Return ("efs", lines) if an EFS (F3S) filesystem starts at base, else None."""
    us = _efs_unit_size(fh, base)
    if us is None:
        return None
    boot = _efs_boot(fh, base, min(us * 4, 1 << 24))
    if boot is None:
        return None
    if boot["unit_total"] < 1 or boot["unit_total"] * us > size:
        return None
    return "efs", [
        f"unit size    {human(us)}   {boot['unit_total']} units, "
        f"{boot['unit_spare']} spare",
        f"alignment    text offsets shifted left by {boot['align_pow2']}",
        f"boot record  QSSL_F3S at +0x{boot['sig_at']:x}",
        f"root         logical unit {boot['root'][0]}, extent {boot['root'][1]}",
    ]


def identify_apfs(fh, base):
    """Return ("apfs", lines) for an APFS container at base, else None.

    A container is claimed by the NXSB magic in the first block's object header
    together with a block size that is a power of two, and it is only reported
    once its newest checkpoint and object map have been read far enough to name
    the volumes inside it. A container that cannot get that far is not one this
    tool can offer to walk.
    """
    head = read_at(fh, base, 4096)
    if len(head) < 4096 or head[32:36] != APFS_NX_MAGIC:
        return None
    block = struct.unpack_from("<I", head, 36)[0]
    if not block or block & (block - 1) or block > (1 << 24):
        return None
    try:
        w = ApfsWalker(fh, base)
    except (ValueError, OSError, struct.error) as exc:
        return "apfs", [f"container    {human(struct.unpack_from('<Q', head, 40)[0] * block)}",
                        f"walk         not possible: {exc}"]
    lines = [
        f"block size   {w.block_size:,}",
        f"container    {human(w.container_size)}   uuid {w.uuid}",
        f"checkpoint   transaction {w.xid:,}",
        f"volumes      {len(w.volumes)}",
    ]
    for i, (_oid, blk, name, incompat) in enumerate(w.volumes):
        sb = w.block(blk)
        used = struct.unpack_from("<Q", sb, 88)[0] * w.block_size
        lines.append(f"  {i}  {name or '(unnamed)'}   {human(used)} used"
                     + ("   case sensitive"
                        if not incompat & APFS_INCOMPAT_CASE_INSENSITIVE else ""))
    return "apfs", lines


def identify_hfsplus(fh, base):
    """Return ("hfs+", lines) for an HFS+ or HFSX volume at base, else None.

    The signature sits 1024 bytes in, where a partition's boot blocks leave it,
    and the geometry that follows has to be self-consistent for the volume to be
    readable at all, so both are required rather than the signature alone.
    """
    vh = read_at(fh, base + HFSP_VH_OFF, 512)
    if len(vh) < 512:
        return None
    sig, version = struct.unpack_from(">HH", vh, 0)
    if sig not in (HFSP_SIG, HFSX_SIG):
        return None
    block, total, free = struct.unpack_from(">III", vh, 40)
    if not block or block & (block - 1) or block > (1 << 24) or not total:
        return None
    files, folders = struct.unpack_from(">II", vh, 32)
    # The header records creation in local time and modification in GMT,
    # TN1150 "Volume Header", so only the second can be shown as an instant.
    modified = struct.unpack_from(">I", vh, 20)[0]
    kind = "hfsx" if sig == HFSX_SIG else "hfs+"
    used = (total - free) * block
    lines = [
        f"format       {'HFSX, case sensitive' if sig == HFSX_SIG else 'HFS+'}"
        f"   version {version}",
        f"block size   {block:,}",
        f"volume       {human(total * block)}",
        f"used         {human(used)} of {human(total * block)}"
        + (f" ({100.0 * used / (total * block):.1f}%)" if total else ""),
        f"counts       {files:,} files, {folders:,} folders",
        f"last write   {stamp(hfs_time(modified))}",
    ]
    try:
        w = HfsPlusWalker(fh, base)
    except (ValueError, OSError, struct.error) as exc:
        lines.append(f"walk         not possible: {exc}")
        return kind, lines
    lines.append(f"catalog      node size {w.catalog_node_size:,}, "
                 f"depth {w.catalog_depth}")
    return kind, lines


def identify_ntfs(fh, base):
    """Return ("ntfs", lines) for an NTFS volume at base, else None.

    NTFS names itself in bytes 3..11 of its boot sector, and the geometry that
    follows has to be self-consistent for the volume to be readable at all, so
    both are required rather than the name alone.
    """
    b = read_at(fh, base, 512)
    if len(b) < 512 or b[3:11] != NTFS_OEM or b[510:512] != b"\x55\xaa":
        return None
    bps = struct.unpack_from("<H", b, 11)[0]
    spc = b[13]
    if bps not in (512, 1024, 2048, 4096) or spc not in (1, 2, 4, 8, 16, 32, 64, 128):
        return None
    sectors = struct.unpack_from("<Q", b, 40)[0]
    mft = struct.unpack_from("<Q", b, 48)[0]
    mirr = struct.unpack_from("<Q", b, 56)[0]
    serial = struct.unpack_from("<Q", b, 72)[0]
    if not sectors or not mft:
        return None
    lines = [
        f"bytes/sector {bps}   sectors/cluster {spc}",
        f"volume       {human(sectors * bps)} ({sectors:,} sectors)",
        f"$MFT         cluster {mft:,}   $MFTMirr cluster {mirr:,}",
        f"serial       {serial:016x}",
    ]
    try:
        w = NtfsWalker(fh, base)
    except (ValueError, OSError, struct.error) as exc:
        lines.append(f"walk         not possible: {exc}")
        return "ntfs", lines
    lines.append(f"record size  {w.rec_size} bytes   index block {w.idx_size} bytes")
    label = w.volume_label()
    if label is not None:
        lines.append(f"label        {label or '(none)'}")
    return "ntfs", lines


def identify_fat(fh, base):
    """Return (kind, lines) for a FAT32 or exFAT volume at base, else None.

    exFAT names itself in bytes 3..11 of the boot sector. FAT32 is recognised
    by its "FAT32   " filesystem-type string at offset 82 together with a 0x55AA
    boot signature, rather than by the OEM name, which is set by whatever tool
    wrote the volume.
    """
    b = read_at(fh, base, 512)
    if len(b) < 512 or b[510:512] != b"\x55\xaa":
        if b[3:11] != b"EXFAT   ":
            return None
    if b[3:11] == b"EXFAT   ":
        bps = 1 << b[108]
        spc = 1 << b[109]
        clusters = struct.unpack_from("<I", b, 92)[0]
        vol = struct.unpack_from("<Q", b, 72)[0] * bps
        return "exfat", [
            f"bytes/sector {bps}   sectors/cluster {spc}",
            f"clusters     {clusters:,}",
            f"volume       {human(vol)}",
        ]
    if b[82:90] == b"FAT32   ":
        bps = struct.unpack_from("<H", b, 11)[0]
        spc = b[13]
        total = struct.unpack_from("<I", b, 32)[0] * bps
        label = b[71:82].decode("ascii", "replace").rstrip(" ")
        return "fat32", [
            f"label        {label or '(none)'}",
            f"bytes/sector {bps}   sectors/cluster {spc}",
            f"volume       {human(total)}",
        ]
    return None


def identify_fs(fh, base, size=None):
    """Return (name, [detail lines]) for whatever sits at this partition.

    size is the region's byte length, needed by the flash filesystems (ETFS/EFS)
    which have no header at a fixed offset and are sized by the region. When it
    is not given it is taken as the rest of the file from base.
    """
    if size is None:
        try:
            size = image_size(fh) - base
        except OSError:
            size = 0

    # QNX4 first: its acceptance is structural (root inode "/", directory
    # mode, a resolved .bitmap entry), while the ext test below is a bare
    # 2-byte magic at offset 1080, which on a QNX4 volume falls inside
    # .bitmap data where any bit pattern can occur. The more specific test
    # runs first so a chance pattern cannot shadow the real format.
    q4 = identify_qnx4(fh, base, size)
    if q4:
        return q4

    sb = read_at(fh, base + EXT_SB_OFF, 1024)
    if len(sb) == 1024 and _e(sb, "magic", 2) == EXT_MAGIC:
        bs = 1024 << _e(sb, "log_block_size")
        total = _e(sb, "blocks_count") * bs
        free = _e(sb, "free_blocks") * bs
        inc, cmp_ = _e(sb, "feature_incompat"), _e(sb, "feature_compat")
        kind = ("ext4" if inc & EXT_INCOMPAT_EXTENTS
                else "ext3" if cmp_ & EXT_COMPAT_HAS_JOURNAL else "ext2")
        label = sb[EXT_F["volume_name"]:EXT_F["volume_name"] + 16]
        label = label.split(b"\x00")[0].decode("utf-8", "replace")
        lastm = sb[EXT_F["last_mounted"]:EXT_F["last_mounted"] + 64]
        lastm = lastm.split(b"\x00")[0].decode("utf-8", "replace")
        uid = sb[EXT_F["uuid"]:EXT_F["uuid"] + 16].hex()
        st = _e(sb, "state", 2)
        used = total - free
        lines = [
            f"label        {label or '(none)'}",
            f"last mounted {lastm or '(none)'}",
            f"uuid         {uid}",
            f"made         {stamp(_e(sb, 'mkfs_time'))}",
            f"last mount   {stamp(_e(sb, 'mtime'))}   mount count "
            f"{_e(sb, 'mnt_count', 2):,}",
            f"last write   {stamp(_e(sb, 'wtime'))}",
            f"used         {human(used)} of {human(total)} "
            f"({100.0*used/total:.1f}%)" if total else "used         unknown",
            f"written      {_e(sb, 'kbytes_written', 8)/1048576:,.1f} GiB over its life",
            f"state        0x{st:04x}  "
            + ("cleanly unmounted" if st & EXT_VALID_FS
               else "NOT cleanly unmounted, so it may have been live at acquisition"),
        ]
        ec = _e(sb, "error_count")
        if ec:
            lines.append(f"errors       {ec:,} recorded")
        return kind, lines

    ifs = identify_ifs(fh, base)
    if ifs:
        return "QNX IFS boot image", ifs

    apfs = identify_apfs(fh, base)
    if apfs:
        return apfs

    hfs = identify_hfsplus(fh, base)
    if hfs:
        return hfs

    ntfs = identify_ntfs(fh, base)
    if ntfs:
        return ntfs

    fat = identify_fat(fh, base)
    if fat:
        return fat

    efs = identify_efs(fh, base, size)
    if efs:
        return efs

    etfs = identify_etfs(fh, base, size)
    if etfs:
        return etfs

    # Not ext, not qnx6, not IFS, not FAT, not a QNX flash filesystem. Report
    # the leading bytes so there is a lead to follow, rather than inventing a
    # signature for it.
    head = read_at(fh, base, 16)
    if not head:
        return None, []
    printable = "".join(chr(c) if 32 <= c < 127 else "." for c in head)
    ascii_magic = ""
    run = bytes(c for c in head[:8] if 32 <= c < 127)
    if len(run) >= 3:
        ascii_magic = f'   leading ascii "{run.decode()}"'
    return None, [f"first 16 bytes  {head.hex(' ')}",
                  f"                |{printable}|{ascii_magic}"]


def human(n):
    if abs(n) < 1024:
        return f"{n:,.0f} B"
    n /= 1024
    for u in ("KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024:
            return f"{n:,.1f} {u}"
        n /= 1024
    return f"{n:,.1f} PiB"


def scan(fh, limit, size, cap=400):
    hits, step = [], 1 << 22
    pats = ((struct.pack("<I", QNX6_MAGIC), 1), (struct.pack(">I", QNX6_MAGIC), 1))
    off = 0
    while off < min(limit, size) and len(hits) < cap:
        buf = read_at(fh, off, step + 4)
        if not buf:
            break
        for pat, _ in pats:
            p = buf.find(pat)
            while p != -1 and len(hits) < cap:
                hits.append(off + p)
                p = buf.find(pat, p + 1)
        off += step
    return sorted(set(hits))


def sanitize_volume_label(label, max_len=24):
    """A partition or filesystem label, reduced to zip-and-shell-safe form."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").lower()
    return cleaned[:max_len].rstrip("_")


def volume_name(part_idx, lba, label=""):
    """The canonical directory name a volume extracts under.

    Built from the partition table, not from the filesystem: the LBA is a
    physical fact about the image that any partition tool reproduces, so it is
    the identity, and it cannot collide because two volumes cannot share a
    start sector. The index gives readability where a table provides one, and
    a label rides along as a suffix, never as the identity, so two partitions
    labelled alike still extract into distinct directories.

        p2_lba65536                   MBR primary 2
        p5_lba4259872                 first logical volume (numbered from 5,
                                      as operating systems do)
        p9_lba737280_storage          GPT partition with its name
        lba0                          no partition table at all: a whole-disk
                                      filesystem or a bare region, which is
                                      how ETFS commonly arrives

    The earlier scheme took the last word of the display label, which made
    "...System Partition" and "...Data Partition" extract into the same
    directory and silently merge.
    """
    stem = f"p{part_idx}_lba{lba}" if part_idx is not None else f"lba{lba}"
    suffix = sanitize_volume_label(label) if label else ""
    return f"{stem}_{suffix}" if suffix else stem


# The MBR type bytes that mark an extended partition container. main() keeps
# the same tuple as a local; a consumer of volumes() needs it by name.
EXT_PARTITION_TYPES = (0x05, 0x0f, 0x85)


def partition_regions(fh, size):
    """(regions, names, containers, protective) for an image, as main() sees them.

    regions is [(label, base, size)] in report order: MBR primaries, then the
    logical volumes found by walking the EBR chain, then GPT entries, or the
    whole image as one region when no table is present. names maps a region's
    byte offset to the directory an extraction uses (volume_name); containers
    holds the labels of extended partition containers, which hold the logical
    volumes and are not themselves volumes; protective holds the 0xEE entry a
    GPT disk carries in its MBR.
    """
    regions, names = [], {}
    containers, protective = set(), set()
    parts = parse_mbr(fh)
    if parts:
        for idx, t, st, cnt in parts:
            regions.append((f"MBR part {idx}", st * SECTOR, cnt * SECTOR))
            names[st * SECTOR] = volume_name(idx, st)
            if t in EXT_PARTITION_TYPES:
                containers.add(f"MBR part {idx}")
            if t == 0xEE:
                protective.add(f"MBR part {idx}")
        logical_idx = 4               # logical volumes number from 5, as OSes do
        for idx, t, st, cnt in parts:
            if t not in EXT_PARTITION_TYPES:
                continue
            base, cur, n = st, st, 0
            while cur and n < 64:
                ebr = read_at(fh, cur * SECTOR, 512)
                if len(ebr) < 512 or ebr[510:512] != b"\x55\xaa":
                    break
                e1, e2 = ebr[446:462], ebr[462:478]
                lst, lcnt = struct.unpack("<II", e1[8:16])
                if lcnt:
                    astart = cur + lst
                    regions.append((f"logical @{astart}", astart * SECTOR, lcnt * SECTOR))
                    logical_idx += 1
                    names[astart * SECTOR] = volume_name(logical_idx, astart)
                nxt = struct.unpack("<I", e2[8:12])[0]
                cur = (base + nxt) if nxt else 0
                n += 1
    gpt = parse_gpt(fh)
    if gpt:
        for idx, name, _g, first, last in gpt:
            sz = (last - first + 1) * SECTOR
            regions.append((f"GPT part {idx} {name[:20]}", first * SECTOR, sz))
            names[first * SECTOR] = volume_name(idx, first, name)
    if not regions:
        regions.append(("whole image", 0, size))
        names[0] = volume_name(None, 0)
    return regions, names, containers, protective


def _ext_label(fh, base):
    """An ext volume's label, or its last mount point when it has no label."""
    sb = read_at(fh, base + EXT_SB_OFF, 1024)
    lab = sb[EXT_F["volume_name"]:EXT_F["volume_name"] + 16]
    lab = lab.split(b"\x00")[0].decode("utf-8", "replace")
    mnt = sb[EXT_F["last_mounted"]:EXT_F["last_mounted"] + 64]
    mnt = mnt.split(b"\x00")[0].decode("utf-8", "replace")
    return lab or mnt.strip("/").replace("/", "_")


def volumes(fh, size=None):
    """Every volume main() would list or extract, in report order, as dicts.

    This is the callable form of the discovery main() does while it prints.
    The window's Contents pane and the LEAPP tools read images through it, so
    a volume here is a volume in the report: `qnxprobe_gui.py --check-discovery
    IMAGE` proves that against the report text for any image.

    Each dict carries:
        label       the region as the report names it ("GPT part 3 storage")
        base, size  byte offset and byte length of the region
        lba         base in sectors, the identity an extraction is named by
        kind        "qnx6", "ext4", "fat32", "ntfs", ..., "extended container",
                    or "not recognised"
        name        the directory the volume extracts under (volume_name)
        detail      a short description from the identifier
        missing_past_end
                    bytes of the region that lie past the end of the image; a
                    positive value means the file holds only part of this
                    volume (a lone first segment of a split image reads so)
        walker      an object with root, listdir, entry and read_file, when the
                    kind is one this reads; else
        note        why there is no walker

    Brute-scan finds are report-only in main() too (they have no region and so
    no base to walk), so they are not here either. fh is what open_image()
    returns; size defaults to image_size(fh).
    """
    if size is None:
        size = image_size(fh)
    regions, names, containers, protective = partition_regions(fh, size)
    missing = {start: gap for _lab, start, _rs, gap in
               short_regions(size, regions, skip=protective)}
    out, qnx6_labels = [], set()

    for label, base, rsize in regions:
        best = None
        for off, _rel in sb_slots(fh, base, label, regions):
            r = check(fh, off)
            if r and not r[2] and (best is None or r[1]["serial"] > best[1]["serial"]):
                best = (off, r[1])
        if best is None:
            continue
        qnx6_labels.add(label)
        vol = dict(label=label, base=base, size=rsize, lba=base // SECTOR, kind="qnx6",
                   name=names.get(base) or f"lba{base // SECTOR}",
                   detail=f"serial {best[1]['serial']:,}, "
                          f"volumeid {best[1]['volumeid'].hex()} (as stored)",
                   missing_past_end=missing.get(base, 0))
        try:
            vol["walker"] = Qnx6Walker(fh, base, best[0] - base)
        except Exception as exc:                        # report it, do not hide it
            vol["note"] = f"could not walk this filesystem: {exc}"
        out.append(vol)

    for label, base, rsize in regions:
        if label in qnx6_labels or label in protective:
            continue
        if label in containers:
            out.append(dict(label=label, base=base, size=rsize, lba=base // SECTOR,
                            kind="extended container", name="", detail="",
                            missing_past_end=missing.get(base, 0),
                            note="holds the logical volumes, nothing to walk"))
            continue
        kind, lines = identify_fs(fh, base, rsize)
        stem = names.get(base) or f"lba{base // SECTOR}"
        vol = dict(label=label, base=base, size=rsize, lba=base // SECTOR,
                   kind=kind or "not recognised", name=stem,
                   detail="; ".join(lines[:2]), missing_past_end=missing.get(base, 0))
        try:
            if kind and kind.startswith("ext"):
                ext_name = _ext_label(fh, base)
                suffix = sanitize_volume_label(ext_name) if ext_name else ""
                if suffix and not stem.endswith(f"_{suffix}"):
                    vol["name"] = f"{stem}_{suffix}"
                vol["walker"] = ExtWalker(fh, base)
            elif kind == "QNX IFS boot image":
                vol["walker"] = IfsWalker(fh, base)
            elif kind:
                vol["walker"] = walker_for(kind, fh, base, rsize)
                if vol["walker"] is None:
                    vol["note"] = "recognised, but no walker for this kind"
            else:
                vol["note"] = "not a filesystem this tool reads"
        except IfsUnsupported as exc:
            vol["note"] = f"contents not read: {exc}"
        except Exception as exc:
            vol["note"] = f"could not walk this filesystem: {exc}"
        out.append(vol)
    return out


def main(path, scan_limit_mib=256, do_list=False, list_depth=2, list_max=400,
         extract=None, only=None, zf=None, do_triage=False, exclude=None,
         reporter=None, manifest=None):
    segments = split_segments(path)      # a set that is not whole raises SplitImageError
    image = open_image(path, segments)
    size = image_size(image)
    print("=" * 78)
    print(path)
    ewf_parts = [] if segments else list(getattr(image, "paths", []) or [])
    if segments:
        print(f"  one segment of a split image: {len(segments)} segments joined, "
              f"{os.path.basename(segments[0])} .. {os.path.basename(segments[-1])}")
        print(f"    {describe_segment_sizes(image.sizes)}")
    elif len(ewf_parts) > 1:
        print(f"  an EWF acquisition of {len(ewf_parts)} segments, joined by the "
              f"reader: {os.path.basename(ewf_parts[0])} .. "
              f"{os.path.basename(ewf_parts[-1])}")
    elif ewf_parts:
        print("  an EWF acquisition of one segment")
    print(f"  {size:,} bytes ({human(size)})")
    print("=" * 78)
    # what volumes.json ties each volume to: the one file, or the first
    # segment of the set, with every segment and its size beside it
    image_rec = {"image": os.path.basename(segments[0] if segments else path)}
    if segments or ewf_parts:
        # A joined raw set records its own segment sizes; a reader over a
        # container need not, so they are measured here rather than required.
        parts = list(image.paths)
        part_sizes = getattr(image, "sizes", None)
        if part_sizes is None:
            part_sizes = [os.path.getsize(q) for q in parts]
        image_rec["image_segments"] = [{"name": os.path.basename(q), "bytes": s}
                                       for q, s in zip(parts, part_sizes)]

    candidates, regions, sized_regions, triage = [], [], [], []
    containers, protective = set(), set()
    vol_names = {}                    # byte offset -> canonical extract name
    with image as fh:
        parts = parse_mbr(fh)
        if parts is None:
            print("  MBR      none (no 0x55AA signature at offset 510, or "
                  "sector 0 is a filesystem's own boot sector)")
        else:
            gpt_prot = any(t == 0xEE for _, t, _, _ in parts)
            print(f"  MBR      valid, {len(parts)} entries"
                  + ("  (0xEE = GPT protective)" if gpt_prot else ""))
            for idx, t, st, cnt in parts:
                tag = f"   <- {MBR_QNX_TYPES[t]}" if t in MBR_QNX_TYPES else ""
                print(f"    {idx}  type 0x{t:02x}  LBA {st:<12,} {human(cnt*SECTOR):>10}{tag}")
                regions.append((f"MBR part {idx}", st * SECTOR))
                sized_regions.append((f"MBR part {idx}", st * SECTOR, cnt * SECTOR))
                vol_names[st * SECTOR] = volume_name(idx, st)
                if t in (0x05, 0x0f, 0x85):
                    containers.add(f"MBR part {idx}")
                if t == 0xEE:
                    protective.add(f"MBR part {idx}")

        # An extended partition holds the logical volumes; walk the EBR chain,
        # or the largest region of the image is never probed at all.
        EXT = (0x05, 0x0f, 0x85)
        logical_idx = 4               # logical volumes number from 5, as OSes do
        for idx, t, st, cnt in (parts or []):
            if t not in EXT:
                continue
            base, cur, n = st, st, 0
            while cur and n < 64:
                ebr = read_at(fh, cur * SECTOR, 512)
                if len(ebr) < 512 or ebr[510:512] != b"\x55\xaa":
                    break
                e1 = ebr[446:462]; e2 = ebr[462:478]
                lt = e1[4]; lst, lcnt = struct.unpack("<II", e1[8:16])
                if lcnt:
                    astart = cur + lst
                    tag = f"   <- {MBR_QNX_TYPES[lt]}" if lt in MBR_QNX_TYPES else ""
                    print(f"      logical  type 0x{lt:02x}  LBA {astart:<12,}"
                          f" {human(lcnt*SECTOR):>10}{tag}")
                    regions.append((f"logical @{astart}", astart * SECTOR))
                    sized_regions.append((f"logical @{astart}", astart * SECTOR,
                                          lcnt * SECTOR))
                    logical_idx += 1
                    vol_names[astart * SECTOR] = volume_name(logical_idx, astart)
                nxt = struct.unpack("<I", e2[8:12])[0]
                cur = (base + nxt) if nxt else 0
                n += 1

        gpt = parse_gpt(fh)
        if gpt:
            print(f"\n  GPT      valid, {len(gpt)} partition entries")
            for idx, name, g, first, last in gpt:
                sz = (last - first + 1) * SECTOR
                print(f"    {idx:>3}  {name[:26]:<26} {human(sz):>10}  LBA {first:,}")
                regions.append((f"GPT part {idx} {name[:20]}", first * SECTOR))
                sized_regions.append((f"GPT part {idx} {name[:20]}", first * SECTOR, sz))
                vol_names[first * SECTOR] = volume_name(idx, first, name)

        # No partition table at all (a whole-disk filesystem, or a bare region
        # such as an ETFS flash dump) means no regions were recorded. Treat the
        # whole image as one region so it still reaches identify_fs and the
        # walkers, named lba0 by the volume_name fallback.
        if not sized_regions:
            sized_regions.append(("whole image", 0, size))
            regions.append(("whole image", 0))
            vol_names[0] = volume_name(None, 0)

        # A partition table describes a whole disk and the file may hold only
        # the front of it. FTK Imager and its peers split a raw image into
        # numbered segments (.001, .002, ...) and the first segment carries the
        # table and the boot volumes, so it identifies cleanly and its front
        # volumes read correctly while the volume holding the user data ends
        # past the cut, where every read answers empty. Measured on a Ford Sync
        # G4 image cut at 1,500 MB: the boot partitions extracted in full and
        # the 28.8 GiB storage volume walked to 0 files with nothing raised.
        # Say so here, before any volume is reported as empty.
        short_by = {}                 # region start -> bytes past the end of the file
        short = short_regions(size, sized_regions, skip=protective)
        if short:
            reach = max(st + rs for lab, st, rs in sized_regions if lab not in protective)
            print("\n  IMAGE IS SHORTER THAN ITS PARTITION TABLE")
            print(f"    the file holds {human(size)}; the partitions it describes "
                  f"reach {human(reach)}")
            for label, st, rs, missing in short:
                short_by[st] = missing
                if missing >= rs:
                    where = "begins past the end of the file  (none of it is here)"
                else:
                    where = f"ends {human(missing)} past the end of the file  (partly here)"
                print(f"    {label:<28} {where}")
            print("    A raw image split into numbered segments (.001, .002, ...) has to be")
            print("    joined before it is read; its first segment alone looks like this.")
            print("    Each volume above is marked INCOMPLETE below, and a file on it that")
            print("    reaches past the end is counted SHORT and stored under a name that")
            print("    says how much of it is here, not as an extracted file.")

        def missing_past_end(base, declared_end=None):
            """Bytes of the volume at base that lie past the end of the file."""
            missing = short_by.get(base, 0)
            if declared_end is not None:
                missing = max(missing, declared_end - size)
            return max(missing, 0)

        # the two offsets the kernel itself probes, per region and whole-image
        print()
        for label, base in [("image start", 0)] + regions:
            for off, rel in sb_slots(fh, base, label, sized_regions):
                r = check(fh, off)
                if r:
                    candidates.append((off, f"{label} +0x{rel:x}", *r))

        if not candidates:
            print(f"  no superblock at the kernel's offsets; brute scanning first"
                  f" {scan_limit_mib} MiB ...")
            for off in scan(fh, scan_limit_mib << 20, size):
                r = check(fh, off)
                if r:
                    candidates.append((off, "brute scan", *r))

        print()
        # A candidate whose volume id, blocksize and block count match an
        # already-confirmed superblock in the SAME region is another copy of
        # that filesystem, not a chance 4-byte hit. Measured on a Ford Sync G4
        # image: the previous generation of dps_os carries ctime 308 and
        # atime 1, both unset because the build host had no clock, so a
        # timestamp heuristic rejects a genuine superblock. Recorded identity
        # is the stronger signal, so it wins.
        def region(h):
            return h.rsplit(" +0x", 1)[0]
        good = {}
        for off, how, endian, sb, bad in candidates:
            if not bad:
                good.setdefault(region(how), []).append(sb)
        promoted = 0
        for i, (off, how, endian, sb, bad) in enumerate(candidates):
            if not bad:
                continue
            for ref in good.get(region(how), []):
                if (sb["volumeid"] == ref["volumeid"]
                        and sb["blocksize"] == ref["blocksize"]
                        and sb["num_blocks"] == ref["num_blocks"]):
                    candidates[i] = (off, how, endian, sb, [])
                    promoted += 1
                    break

        confirmed = [c for c in candidates if not c[4]]
        rejected  = [c for c in candidates if c[4]]
        if promoted:
            print(f"  {promoted} further cop{'y' if promoted==1 else 'ies'} "
                  f"confirmed by matching volume id, blocksize and block count\n")

        print(f"  {len(candidates)} magic match(es): "
              f"{len(confirmed)} CONFIRMED, {len(rejected)} rejected as coincidence\n")

        # Group the copies by volume, then by serial. The highest serial is
        # the active generation; the one below it is the previous committed
        # state, still on disk.
        vols = {}
        for off, how, endian, sb, _ in confirmed:
            key = how.rsplit(" +0x", 1)[0]
            vols.setdefault(key, []).append((off, endian, sb))

        if vols:
            print("  HOW TO READ THE TIMESTAMPS  (see --help for the sourcing)")
            print("    sb_ctime is written once when the filesystem is made.")
            print("    sb_atime moves when the filesystem is COMMITTED, not when a file")
            print("    is read. Do not read it as when the device was last used by a")
            print("    person. serial counts commits and is the better measure of how")
            print("    much a volume has been written.")
            print()

        for key, copies in vols.items():
            gens = {}
            for off, endian, sb in copies:
                g = gens.setdefault(sb["serial"], {"sb": sb, "endian": endian, "at": []})
                g["at"].append(off)
            serials = sorted(gens, reverse=True)
            act = gens[serials[0]]
            sb, endian = act["sb"], act["endian"]
            total = sb["num_blocks"] * sb["blocksize"]

            print(f"  CONFIRMED qnx6 filesystem on {key}  [{endian}]")
            print(f"      {len(copies)} superblock cop{'y' if len(copies)==1 else 'ies'}, "
                  f"{len(serials)} generation{'' if len(serials)==1 else 's'}\n")

            match = ""
            for rlabel, rbase, rsize in sized_regions:
                if key.startswith(rlabel) and rsize:
                    match = (f"   <- {100.0*total/rsize:.1f}% of the "
                             f"{human(rsize)} partition it sits in")
                    break

            print(f"      ACTIVE   serial {sb['serial']:,}   at "
                  + ", ".join(f"0x{o:x}" for o in sorted(act["at"])))
            print(f"        sb_ctime   {stamp(sb['ctime'])}")
            print(f"        sb_atime   {stamp(sb['atime'])}")
            print(f"        version    {sb['version1']}.{sb['version2']}   "
                  f"blocksize {sb['blocksize']:,}   flags 0x{sb['flags']:08x}")
            print(f"        volume     {human(total)}  ({sb['num_blocks']:,} blocks, "
                  f"{sb['free_blocks']:,} free){match}")
            print(f"        inodes     {sb['num_inodes']:,} total, "
                  f"{sb['free_inodes']:,} free, "
                  f"{sb['num_inodes']-sb['free_inodes']:,} used")
            print(f"        volumeid   {sb['volumeid'].hex()}  (as stored)")

            if len(serials) > 1:
                prev = gens[serials[1]]
                pb = prev["sb"]
                print(f"\n      PREVIOUS serial {pb['serial']:,}   at "
                      + ", ".join(f"0x{o:x}" for o in sorted(prev["at"]))
                      + "   (still on disk)")
                print(f"        sb_ctime   {stamp(pb['ctime'])}")
                print(f"        sb_atime   {stamp(pb['atime'])}")

                print(f"\n      WHAT CHANGED between the two generations")
                d_ser = sb['serial'] - pb['serial']
                print(f"        serial       +{d_ser:,}"
                      f"   ({'one commit' if d_ser==1 else str(d_ser)+' commits'})")
                print(delta_line("sb_ctime", sb['ctime'], pb['ctime']))
                print(delta_line("sb_atime", sb['atime'], pb['atime']))
                for f, lab in (("free_blocks","block"), ("free_inodes","inode")):
                    d = sb[f] - pb[f]
                    if d == 0:
                        print(f"        {f:<12} unchanged")
                    else:
                        word = lab + ("" if abs(d) == 1 else "s")
                        verb = "freed" if d > 0 else "allocated"
                        print(f"        {f:<12} {d:+,}  ({abs(d):,} {word} {verb})")

            base = next((b for lab, b, _ in sized_regions
                         if key.startswith(lab)), None)
            wanted = only is None or only.lower() in key.lower()

            if do_triage and base is not None:
                encf = (0, 0)
                try:
                    tw = Qnx6Walker(fh, base, sorted(act["at"])[0] - base)
                    encf = sample_encryption(tw)
                except Exception:
                    pass
                used = (sb["num_blocks"] - sb["free_blocks"]) * sb["blocksize"]
                triage.append(triage_row(
                    key.split("part", 1)[-1].strip() if "part" in key else key,
                    "qnx6", sb["num_blocks"] * sb["blocksize"], used,
                    sb["serial"], f"{sb['serial']:,} commits, "
                    f"{sb['num_inodes'] - sb['free_inodes']:,} inodes used",
                    stamp(sb["atime"]).replace(" UTC", ""), encf))

            if do_list and base is not None and wanted:
                print(f"\n      CONTENTS  (depth {list_depth})")
                try:
                    w = Qnx6Walker(fh, base, sorted(act["at"])[0] - base)
                    print_tree(w, w.root, 1, list_depth, [list_max])
                except Exception as exc:
                    print(f"        could not walk this filesystem: {exc}")

            if zf is not None and base is not None and wanted:
                vol = vol_names.get(base) or f"lba{base // SECTOR}"
                print(f"\n      EXTRACTING to {extract}  as {vol}/")
                try:
                    w = Qnx6Walker(fh, base, sorted(act["at"])[0] - base)
                    ents = collect(w, w.root)
                    ents, dropped = apply_exclude(ents, exclude)
                    log = []
                    miss = missing_past_end(base, base + total)
                    f_, wr, sk, fa, sh = extract_to_zip(zf, w, vol, ents, log, reporter,
                                                            may_be_short=bool(miss))
                    if manifest is not None:
                        rsize = next((r[2] for r in sized_regions if r[1] == base), None)
                        manifest.append({
                            "volume": vol, **image_rec,
                            "lba": base // SECTOR, "offset_bytes": base,
                            "partition_size_bytes": rsize,
                            "filesystem": "qnx6",
                            "volume_id_as_stored": sb["volumeid"].hex(),
                            "superblock_serial": sb["serial"],
                            "files": f_, "bytes": wr,
                            "symlinks_or_special_skipped": sk,
                            "failed": fa, "short": sh, "excluded": dropped,
                        })
                    print(f"        {f_:,} files, {human(wr)}"
                          + (f", {sk:,} symlinks or special files skipped" if sk else "")
                          + (f", {fa:,} FAILED" if fa else "")
                          + (f", {sh:,} SHORT" if sh else "")
                          + (f", {dropped:,} excluded" if dropped else ""))
                    for line in log[:5]:
                        print(line)
                    if miss:
                        print(f"        INCOMPLETE: this volume reaches {human(miss)} past the end of the file")
                        if manifest is not None:
                            manifest[-1]["extends_past_image_by_bytes"] = miss
                except Exception as exc:
                    print(f"        could not extract this filesystem: {exc}")
            print()

        # A type byte is a label, not a fact, so read the partitions that did
        # not turn out to be qnx6 rather than trusting what they claim to be.
        others = [(lab, b, sz) for lab, b, sz in sized_regions
                  if lab not in vols and lab not in protective]
        if others:
            print("  WHAT IS IN THE OTHER PARTITIONS")
            for lab, b, sz in others:
                if lab in containers:
                    print(f"    {lab}   {human(sz)}   ->  extended partition "
                          f"container, holds the logical volumes below")
                    print()
                    continue
                kind, lines = identify_fs(fh, b, sz)
                print(f"    {lab}   {human(sz)}   ->  {kind or 'not recognised'}")
                for line in lines:
                    print(f"        {line}")
                ext_name = ""
                if kind and kind.startswith("ext"):
                    _sb = read_at(fh, b + EXT_SB_OFF, 1024)
                    _l = _sb[EXT_F["volume_name"]:EXT_F["volume_name"] + 16]
                    _l = _l.split(b"\x00")[0].decode("utf-8", "replace")
                    _m = _sb[EXT_F["last_mounted"]:EXT_F["last_mounted"] + 64]
                    _m = _m.split(b"\x00")[0].decode("utf-8", "replace")
                    ext_name = _l or _m.strip("/").replace("/", "_")
                wanted = (only is None or only.lower() in lab.lower()
                          or (ext_name and only.lower() in ext_name.lower()))

                if do_triage and kind and kind.startswith("ext"):
                    esb = read_at(fh, b + EXT_SB_OFF, 1024)
                    ebs = 1024 << _e(esb, "log_block_size")
                    etot = _e(esb, "blocks_count") * ebs
                    eused = etot - _e(esb, "free_blocks") * ebs
                    kb = _e(esb, "kbytes_written", 8)
                    lbl = esb[EXT_F["volume_name"]:EXT_F["volume_name"] + 16]
                    lbl = lbl.split(b"\x00")[0].decode("utf-8", "replace")
                    mnt = esb[EXT_F["last_mounted"]:EXT_F["last_mounted"] + 64]
                    mnt = mnt.split(b"\x00")[0].decode("utf-8", "replace")
                    encf = (0, 0)
                    try:
                        encf = sample_encryption(ExtWalker(fh, b))
                    except Exception:
                        pass
                    triage.append(triage_row(
                        lbl or mnt or lab, kind, etot, eused, kb,
                        f"{kb/1048576:,.0f} GiB written over its life, "
                        f"{_e(esb, 'mnt_count', 2):,} mounts"
                        + (f", mounts at {mnt}" if mnt else ""),
                        stamp(_e(esb, "mtime")).replace(" UTC", ""), encf))

                if do_list and kind and kind.startswith("ext") and wanted:
                    print(f"        CONTENTS  (depth {list_depth})")
                    try:
                        w = ExtWalker(fh, b)
                        print_tree(w, w.root, 1, list_depth, [list_max], pad=8)
                    except Exception as exc:
                        print(f"        could not walk this filesystem: {exc}")
                if zf is not None and kind and kind.startswith("ext") and wanted:
                    stem = vol_names.get(b) or f"lba{b // SECTOR}"
                    suffix = sanitize_volume_label(ext_name) if ext_name else ""
                    vol = (f"{stem}_{suffix}"
                           if suffix and not stem.endswith(f"_{suffix}") else stem)
                    print(f"        EXTRACTING to {extract}  as {vol}/")
                    try:
                        w = ExtWalker(fh, b)
                        ents = collect(w, w.root)
                        ents, dropped = apply_exclude(ents, exclude)
                        log = []
                        miss = missing_past_end(b)
                        f_, wr, sk, fa, sh = extract_to_zip(zf, w, vol, ents, log, reporter,
                                                                may_be_short=bool(miss))
                        if manifest is not None:
                            _u = read_at(fh, b + EXT_SB_OFF, 1024)
                            manifest.append({
                                "volume": vol, **image_rec,
                                "lba": b // SECTOR, "offset_bytes": b,
                                "partition_size_bytes": sz,
                                "filesystem": kind,
                                "uuid": _u[EXT_F["uuid"]:EXT_F["uuid"] + 16].hex(),
                                "label": ext_name,
                                "files": f_, "bytes": wr,
                                "symlinks_or_special_skipped": sk,
                                "failed": fa, "short": sh, "excluded": dropped,
                            })
                        print(f"            {f_:,} files, {human(wr)}"
                              + (f", {sk:,} symlinks or special files skipped" if sk else "")
                              + (f", {fa:,} FAILED" if fa else "")
                              + (f", {sh:,} SHORT" if sh else "")
                              + (f", {dropped:,} excluded" if dropped else ""))
                        for line in log[:5]:
                            print(line)
                        if miss:
                            print(f"            INCOMPLETE: this volume reaches {human(miss)} past the end of the file")
                            if manifest is not None:
                                manifest[-1]["extends_past_image_by_bytes"] = miss
                    except Exception as exc:
                        print(f"        could not extract: {exc}")

                if kind in ("fat32", "exfat", "ntfs", "hfs+", "hfsx", "apfs",
                            "etfs", "efs", "qnx4") and wanted:
                    if do_list:
                        print(f"        CONTENTS  (depth {list_depth})")
                        try:
                            w = walker_for(kind, fh, b, sz)
                            print_tree(w, w.root, 1, list_depth, [list_max], pad=8)
                        except Exception as exc:
                            print(f"        could not walk this filesystem: {exc}")
                    if zf is not None:
                        vol = vol_names.get(b) or f"lba{b // SECTOR}"
                        print(f"        EXTRACTING to {extract}  as {vol}/")
                        try:
                            w = walker_for(kind, fh, b, sz)
                            ents = collect(w, w.root)
                            ents, dropped = apply_exclude(ents, exclude)
                            log = []
                            miss = missing_past_end(b)
                            f_, wr, sk, fa, sh = extract_to_zip(zf, w, vol, ents, log, reporter,
                                                                    may_be_short=bool(miss))
                            if manifest is not None:
                                manifest.append({
                                    "volume": vol, **image_rec,
                                    "lba": b // SECTOR, "offset_bytes": b,
                                    "partition_size_bytes": sz, "filesystem": kind,
                                    "files": f_, "bytes": wr,
                                    "symlinks_or_special_skipped": sk,
                                    "failed": fa, "short": sh, "excluded": dropped,
                                })
                            print(f"            {f_:,} files, {human(wr)}"
                                  + (f", {sk:,} symlinks or special files skipped" if sk else "")
                                  + (f", {fa:,} FAILED" if fa else "")
                                  + (f", {sh:,} SHORT" if sh else "")
                                  + (f", {dropped:,} excluded" if dropped else ""))
                            for line in log[:5]:
                                print(line)
                            if miss:
                                print(f"            INCOMPLETE: this volume reaches {human(miss)} past the end of the file")
                                if manifest is not None:
                                    manifest[-1]["extends_past_image_by_bytes"] = miss
                        except Exception as exc:
                            print(f"        could not extract: {exc}")

                if (kind == "QNX IFS boot image" and wanted
                        and (do_list or zf is not None)):
                    w = None
                    try:
                        w = IfsWalker(fh, b)
                    except IfsUnsupported as exc:
                        print(f"        contents not read: {exc}")
                    except Exception as exc:
                        print(f"        could not read this image filesystem: {exc}")
                    if w is not None:
                        ck = ("image checksum balances" if w.cksum_ok
                              else "IMAGE CHECKSUM DOES NOT BALANCE" if w.cksum_ok is False
                              else "image checksum not checked")
                        print(f"        decoded {human(w.decompressed)} imagefs "
                              f"({w.compress}), {ck}")
                        if do_list:
                            print(f"        CONTENTS  (depth {list_depth})")
                            try:
                                print_tree(w, w.root, 1, list_depth, [list_max], pad=8)
                            except Exception as exc:
                                print(f"        could not walk this filesystem: {exc}")
                        if zf is not None:
                            vol = vol_names.get(b) or f"lba{b // SECTOR}"
                            print(f"        EXTRACTING to {extract}  as {vol}/")
                            try:
                                ents = collect(w, w.root)
                                ents, dropped = apply_exclude(ents, exclude)
                                log = []
                                miss = missing_past_end(b)
                                f_, wr, sk, fa, sh = extract_to_zip(zf, w, vol, ents, log, reporter,
                                                                        may_be_short=bool(miss))
                                if manifest is not None:
                                    manifest.append({
                                        "volume": vol, **image_rec,
                                        "lba": b // SECTOR, "offset_bytes": b,
                                        "partition_size_bytes": sz,
                                        "filesystem": "qnx_ifs",
                                        "compression": w.compress,
                                        "imagefs_size_bytes": w.decompressed,
                                        "image_checksum_balances": w.cksum_ok,
                                        "files": f_, "bytes": wr,
                                        "symlinks_or_special_skipped": sk,
                                        "failed": fa, "short": sh, "excluded": dropped,
                                    })
                                print(f"            {f_:,} files, {human(wr)}"
                                      + (f", {sk:,} symlinks or special files skipped"
                                         if sk else "")
                                      + (f", {fa:,} FAILED" if fa else "")
                                      + (f", {sh:,} SHORT" if sh else "")
                                      + (f", {dropped:,} excluded" if dropped else ""))
                                for line in log[:5]:
                                    print(line)
                                if miss:
                                    print(f"            INCOMPLETE: this volume reaches {human(miss)} past the end of the file")
                                    if manifest is not None:
                                        manifest[-1]["extends_past_image_by_bytes"] = miss
                            except Exception as exc:
                                print(f"        could not extract: {exc}")
                print()

        if rejected:
            print(f"  rejected (magic present, fields inconsistent):")
            for off, how, endian, sb, bad in rejected[:6]:
                print(f"    0x{off:<10x} {how:<28} {bad[0]}")
            if len(rejected) > 6:
                print(f"    ... and {len(rejected)-6} more")
            print()

        if do_triage:
            print_triage(triage)

        if confirmed:
            print("  VERDICT: QNX6 filesystem present.")
        elif candidates:
            print("  VERDICT: magic bytes seen but no valid superblock. Not QNX6"
                  " on this evidence.")
        else:
            print("  VERDICT: no QNX6 superblock found.")
    print()


def _apfs_fixture_check(image_gz, listing):
    """Walk the committed APFS fixture and compare every file against the hashes
    an independent reader recorded from the same image.

    Returns (matched, expected, missing, different). The paths in the listing are
    relative to the volume, and the walk presents the container's volumes as
    directories, so the volume name is dropped before comparing.
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, path = line.split("  ", 1)
            want[path] = digest
    w = ApfsWalker(img, 0)
    have = {}
    for path, node, size, _mtime in collect(w, w.root):
        if size is None:
            continue                      # a symbolic link, which has no stream
        have[path.split("/", 1)[1] if "/" in path else path] = (node, size)
    matched = missing = different = 0
    for path, digest in want.items():
        got = have.get(path)
        if got is None:
            missing += 1
            continue
        h = hashlib.sha256()
        read = 0
        try:
            for chunk in w.read_file(got[0], got[1]):
                h.update(chunk)
                read += len(chunk)
        except ApfsUnreadable:
            different += 1
            continue
        if read == got[1] and h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return matched, len(want), missing, different


def _hfs_fixture_check(image_gz, listing):
    """Walk the committed HFS+ fixture and compare every file against the hashes
    an independent reader recorded from the same image.

    Returns (matched, expected, missing, different). The image is decompressed in
    memory, so no temporary file is written and nothing outside this process is
    touched.
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, path = line.split("  ", 1)
            want[path] = digest
    w = HfsPlusWalker(img, 0)
    have = {}
    for path, cnid, size, _mtime in collect(w, w.root):
        if "HFS+ Private" in path:
            continue
        have[path] = (cnid, size)
    matched = missing = different = 0
    for path, digest in want.items():
        got = have.get(path)
        if got is None:
            missing += 1
            continue
        h = hashlib.sha256()
        read = 0
        try:
            for chunk in w.read_file(got[0], got[1]):
                h.update(chunk)
                read += len(chunk)
        except HfsUnreadable:
            different += 1
            continue
        if (got[1] is None or read == got[1]) and h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return matched, len(want), missing, different


def _fat_deleted_check(image_gz, listing, walker_cls):
    """Recover the deleted files a FAT32 or exFAT fixture builder created and
    then removed, and compare each against the sha256 recorded from its bytes
    before deletion. The listing names a file by its last path component; a
    FAT32 short-name-only entry loses its first character to the 0xE5 mark, so
    a listed name is also matched with that character replaced by "_".
    Returns (matched, expected, missing, different).
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, rest = line.split("  ", 1)
            want[rest.rsplit("/", 1)[-1]] = digest
    w = walker_cls(img, 0)
    have = {}
    for e in w.deleted_files():
        if e.recoverable and not e.is_dir:
            have[e.name] = e
    matched = missing = different = 0
    for name, digest in want.items():
        e = have.get(name) or have.get("_" + name[1:])
        if e is None:
            missing += 1
            continue
        h = hashlib.sha256()
        for chunk in w.read_deleted(e):
            h.update(chunk)
        if h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return matched, len(want), missing, different


def _ntfs_deleted_check(image_gz, listing):
    """Recover the deleted files the fixture builder created and then removed,
    and compare each against the sha256 recorded from its bytes before deletion.

    The expected hashes come from what was written, not from this reader, and
    the same files were confirmed recoverable by The Sleuth Kit's icat at build
    time. Returns (matched, expected, missing, different).
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            want[name] = digest
    w = NtfsWalker(img, 0)
    have = {e.name: e for e in w.deleted_files() if e.recoverable and not e.is_dir}
    matched = missing = different = 0
    for name, digest in want.items():
        e = have.get(name)
        if e is None:
            missing += 1
            continue
        h = hashlib.sha256()
        for chunk in w.read_deleted(e):
            h.update(chunk)
        if h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return matched, len(want), missing, different


def _ext_fixture_check(image_gz, listing):
    """Walk a committed ext fixture and compare every file against the hashes
    sha256sum recorded over the tree the image was built from.

    Returns (kind, matched, expected, missing, different). The fixtures hold
    sparse files of every shape (a hole first, a hole in the middle, a trailing
    hole past the last block, a file that is nothing but hole, and a 3 MiB one
    whose data sits at both ends), so a reader that drops holes or loses the
    logical position of an extent fails here; the ext2 image reaches the same
    files through the classic block map instead of an extent tree.
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    size = img.getbuffer().nbytes
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, path = line.split("  ", 1)
            want[path] = digest
    kind = (identify_fs(img, 0, size) or (None,))[0]
    w = walker_for(kind, img, 0, size) if kind else None
    if w is None:
        return kind, 0, len(want), len(want), 0
    have = {path: (ino, sz) for path, ino, sz, _mtime in collect(w, w.root) if sz is not None}
    matched = missing = different = 0
    for path, digest in want.items():
        got = have.get(path)
        if got is None:
            missing += 1
            continue
        h = hashlib.sha256()
        read = 0
        try:
            for chunk in w.read_file(got[0], got[1]):
                h.update(chunk)
                read += len(chunk)
        except ExtUnreadable:
            different += 1
            continue
        if read == got[1] and h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return kind, matched, len(want), missing, different


def _ntfs_fixture_check(image_gz, listing):
    """Walk the committed NTFS fixture and compare every file against the
    hashes an independent reader recorded from the same image.

    Returns (matched, expected, missing, different). The image is decompressed
    in memory: the walker takes anything with seek and read, so no temporary
    file is written and nothing outside this process is touched.
    """
    import gzip, hashlib, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    want = {}
    with open(listing, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            digest, path = line.split("  ", 1)
            want[path] = digest
    w = NtfsWalker(img, 0)
    matched = missing = different = 0
    have = {}
    for path, ino, size, _mtime in collect(w, w.root):
        have[path] = (ino, size)
    for path, digest in want.items():
        got = have.get(path)
        if got is None:
            missing += 1
            continue
        h = hashlib.sha256()
        read = 0
        try:
            for chunk in w.read_file(got[0], got[1]):
                h.update(chunk)
                read += len(chunk)
        except NtfsUnreadable:
            different += 1
            continue
        if read == got[1] and h.hexdigest() == digest:
            matched += 1
        else:
            different += 1
    return matched, len(want), missing, different


def _ntfs_times_check(image_gz):
    """Compare the instants the walker reads for live and deleted NTFS files
    against what The Sleuth Kit's istat printed for the same records.

    The pins are istat's $STANDARD_INFORMATION block, not the $FILE_NAME block it
    prints beneath: on this fixture the two differ, most on the accessed time,
    so a reader that took the wrong attribute fails on the field that matters.
    Recorded 2026-09-12 with ``TZ=UTC istat -o 0 ntfs-fixture.img <record>`` on
    sleuthkit 4.x; the fixture is committed and never rewritten, so these values
    are fixed. Each is compared within a microsecond, which is below the
    precision a Unix-seconds float keeps at this epoch and above istat's 100 ns.

    Returns (failures, live files checked).
    """
    import gzip, io
    from datetime import datetime, timezone
    live = {
        "dir/mid.txt": ("2026-09-11 04:22:40.133550800", "2026-09-11 04:22:40.133580100",
                        "2026-09-11 04:22:55.233196100"),
        "many/file_0001.txt": ("2026-09-11 04:22:40.136710000", "2026-09-11 04:22:40.136739400",
                               "2026-09-11 04:22:55.279657800"),
    }
    deleted = {
        "h_9.bin": ("2026-09-11 04:22:40.754156700", "2026-09-11 04:22:40.754286000",
                    "2026-09-11 04:22:40.754156700"),
        "h_11.bin": ("2026-09-11 04:22:40.766373400", "2026-09-11 04:22:40.766531400",
                     "2026-09-11 04:22:40.766373400"),
    }

    def epoch(text):
        base, frac = text.split(".")
        dt = datetime.strptime(base, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.timestamp() + int(frac) / 10 ** len(frac)

    def matches(got, want):
        return all(abs(g - epoch(w)) < 1e-6 for g, w in zip(got, want))

    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    w = NtfsWalker(img, 0)
    failures, checked, seen = [], 0, set()
    for path, ino, size, mtime in collect(w, w.root):
        if size is None:
            continue
        got = w.stamps(ino)
        checked += 1
        if got[1] != mtime:
            failures.append(f"{path}: stamps() modified {got[1]} is not entry()'s {mtime}")
        if path in live:
            seen.add(path)
            if not matches(got, live[path]):
                failures.append(f"{path}: stamps() {got} is not istat's {live[path]}")
    for e in w.deleted_files():
        if e.name in deleted:
            seen.add(e.name)
            got = (e.created, e.modified, e.accessed)
            if not matches(got, deleted[e.name]):
                failures.append(f"deleted {e.name}: {got} is not istat's {deleted[e.name]}")
    for name in (set(live) | set(deleted)) - seen:
        failures.append(f"{name}: not found in the fixture, so nothing was compared")
    return failures, checked


def _fat_listing_check(image_gz, wcls):
    """print_tree() on a FAT32 or exFAT fixture prints each file's modified
    reading as stored and never 1970-01-01, which is what the zero mtime
    entry() returns for those walkers formats to. The zero is asserted first,
    so the check proves the substitution and not the absence of a zero.
    Returns (ok, detail)."""
    import contextlib, gzip, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    w = wcls(img, 0)
    files = [(n, i, r) for n, i, r in w.listdir_records(w.root) if not (w.entry(i)[0] & S_IFDIR)]
    if not files:
        return False, "no files in the fixture"
    if any(w.entry(i)[2] != 0 for _n, i, _r in files):
        return False, "premise failed: entry() mtime is not 0, so the check proves nothing"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_tree(w, w.root, 1, 3, [1000])
    out = buf.getvalue()
    if "1970-01-01" in out:
        return False, "a zero mtime was printed as 1970-01-01"
    missing = [n for n, _i, r in files
               if r.get("modified") and f"modified {r['modified']} (as stored" not in out]
    if missing:
        return False, f"reading not printed for {missing[:3]}"
    return True, f"{len(files)} files, readings printed as stored"


def _ntfs_listing_check(image_gz):
    """The control: an NTFS listing, whose times are instants, still prints a
    date for a file. Returns (ok, detail)."""
    import contextlib, gzip, io
    with gzip.open(image_gz, "rb") as gz:
        img = io.BytesIO(gz.read())
    w = NtfsWalker(img, 0)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_tree(w, w.root, 1, 2, [5000])
    line = next((l for l in buf.getvalue().splitlines() if " mid.txt" in l), "")
    return ("2026-09-11" in line), (line.strip() or "dir/mid.txt not listed")


def self_test():
    """Prove the detector reports BOTH ways before you trust a run.

    Builds three throwaway images in a temp directory, checks them, and removes
    the directory. Nothing outside that directory is touched.
    """
    import tempfile, shutil

    # These two literals are deliberately NOT QNX6_MAGIC. A self-test that
    # builds its fixtures from the constant it is verifying is circular: it
    # passes even when the constant is wrong. Measured 2026-08-26, an earlier
    # version of this function passed with QNX6_MAGIC set to 0x68191123.
    # If you change these, change them to the value in
    # linux/include/uapi/linux/magic.h and nowhere else.
    TRUE_MAGIC_LE = b"\x22\x11\x19\x68"   # 0x68191122, little endian on disk
    TRUE_MAGIC_BE = b"\x68\x19\x11\x22"   # 0x68191122, big endian on disk

    d = tempfile.mkdtemp(prefix="qnxprobe_selftest_")
    try:
        ok = True
        if struct.pack("<I", QNX6_MAGIC) != TRUE_MAGIC_LE:
            print(f"  [FAIL] QNX6_MAGIC is 0x{QNX6_MAGIC:08x}, expected 0x68191122")
            print("\n  SELF-TEST FAILED. Do not trust results from this build.")
            return 1

        # positive 1: MBR, little endian, superblock at partition + 0x2000,
        # with fully consistent fields
        img = bytearray(SECTOR * 2048 + 6 * 1024 * 1024)
        ent = bytearray(16)
        ent[4] = 0xb1
        struct.pack_into("<II", ent, 8, 2048, 8192)
        img[446:462] = ent
        img[510:512] = b"\x55\xaa"
        o = 2048 * SECTOR + BOOTBLOCK_SIZE
        img[o:o + 4] = TRUE_MAGIC_LE
        struct.pack_into("<I", img, o + 16, 1521471625)   # ctime 2018-03-19
        struct.pack_into("<I", img, o + 20, 1712222868)   # atime 2024-04-04
        struct.pack_into("<H", img, o + 28, 4)
        struct.pack_into("<H", img, o + 30, 3)
        struct.pack_into("<I", img, o + 48, 4096)         # blocksize
        struct.pack_into("<I", img, o + 52, 20000)        # num_inodes
        struct.pack_into("<I", img, o + 56, 15000)        # free_inodes
        struct.pack_into("<I", img, o + 60, 1020)         # num_blocks
        struct.pack_into("<I", img, o + 64, 966)          # free_blocks
        a = os.path.join(d, "positive_le.img")
        open(a, "wb").write(img)

        # positive 2: no partition table, big endian, superblock at offset 0
        img2 = bytearray(64 * 1024)
        img2[0:4] = TRUE_MAGIC_BE
        struct.pack_into(">I", img2, 16, 1521471625)
        struct.pack_into(">I", img2, 20, 1712222868)
        struct.pack_into(">I", img2, 48, 4096)
        struct.pack_into(">I", img2, 52, 128)
        struct.pack_into(">I", img2, 56, 101)
        struct.pack_into(">I", img2, 60, 1020)
        struct.pack_into(">I", img2, 64, 966)
        b = os.path.join(d, "positive_be.img")
        open(b, "wb").write(img2)

        # negative: deterministic bytes that provably do not contain the magic
        neg = bytes(((i * 7 + 13) & 0xFF) for i in range(2 * 1024 * 1024))
        assert TRUE_MAGIC_LE not in neg and TRUE_MAGIC_BE not in neg
        c = os.path.join(d, "negative.img")
        open(c, "wb").write(neg)

        for path, want, label in ((a, True,  "positive, little endian, MBR +0x2000"),
                                  (b, True,  "positive, big endian, no MBR, +0"),
                                  (c, False, "negative, no magic anywhere")):
            with open(path, "rb") as fh:
                hit = None
                for base in (0, 2048 * SECTOR):
                    for rel in (BOOTBLOCK_SIZE, 0):
                        r = check(fh, base + rel)
                        if r and not r[2]:
                            hit = r
                            break
                    if hit:
                        break
            got = hit is not None
            mark = "PASS" if got == want else "FAIL"
            if got != want:
                ok = False
            print(f"  [{mark}] {label}: detected={got}, expected={want}")

        # positive 3: no partition table, but sector 0 is boot code ending in
        # 0x55AA, the shape of qnxmount's qnx6 reference image. Two superblock
        # copies: serial 1 at 0x2000 and serial 2 where the kernel puts the
        # second copy, 0x2000 + 0x1000 + num_blocks * blocksize (fs/qnx6/inode.c
        # qnx6_fill_super). The junk at 446..510 is deterministic and parses as
        # entries with non-zero type and count starting far past the image.
        img3 = bytearray(64 * 1024)
        img3[0:446] = bytes(((i * 11 + 5) & 0xFF) for i in range(446))
        img3[446:510] = bytes(((i * 13 + 7) & 0xFF) for i in range(64))
        img3[510:512] = b"\x55\xaa"

        def q6sb(o, serial, free_inodes):
            img3[o:o + 4] = TRUE_MAGIC_LE
            struct.pack_into("<Q", img3, o + 8, serial)
            struct.pack_into("<I", img3, o + 16, 1521471625)
            struct.pack_into("<I", img3, o + 20, 1712222868)
            struct.pack_into("<H", img3, o + 28, 4)
            struct.pack_into("<H", img3, o + 30, 3)
            struct.pack_into("<I", img3, o + 48, 1024)        # blocksize
            struct.pack_into("<I", img3, o + 52, 48)          # num_inodes
            struct.pack_into("<I", img3, o + 56, free_inodes)
            struct.pack_into("<I", img3, o + 60, 48)          # num_blocks, 48 KiB
            struct.pack_into("<I", img3, o + 64, 40)          # free_blocks
        q6sb(0x2000, 1, 46)
        q6sb(0x2000 + 0x1000 + 48 * 1024, 2, 30)              # 0xF000
        p3 = os.path.join(d, "qnx6_bootblock.img"); open(p3, "wb").write(img3)

        # and the same junk sector on an image holding no filesystem at all
        junk = bytearray(64 * 1024)
        junk[0:512] = img3[0:512]
        pj = os.path.join(d, "junk_mbr.img"); open(pj, "wb").write(junk)

        import io, contextlib
        with open(p3, "rb") as fh:
            got3 = parse_mbr(fh)
        with open(a, "rb") as fh:
            gota = parse_mbr(fh)
        with open(pj, "rb") as fh:
            gotj = parse_mbr(fh)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(p3)
        rep = buf.getvalue()
        listed = ("CONFIRMED qnx6 filesystem on whole image" in rep
                  and "ACTIVE   serial 2" in rep and "PREVIOUS serial 1" in rep)
        for label, cond in (
                ("qnx6 boot block ending in 0x55AA is not read as a partition table",
                 got3 is None),
                ("the real MBR on the positive_le image still parses",
                 gota == [(1, 0xb1, 2048, 8192)]),
                ("a 0x55AA sector whose entries all start past the image end is declined",
                 gotj is None),
                ("the boot-block image reports as a whole-image volume, serial 2 active",
                 listed)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # FAT and exFAT detection, both ways, from synthetic boot sectors. The
        # type strings are written as literals here, deliberately not by
        # reference to identify_fat's own comparisons, for the same circularity
        # reason as TRUE_MAGIC_LE above: Microsoft's specifications spell them
        # "FAT32   " at offset 82 and "EXFAT   " at offset 3.
        fat = bytearray(64 * 1024)
        fat[82:90] = b"FAT32   "
        struct.pack_into("<H", fat, 11, 512); fat[13] = 1
        struct.pack_into("<I", fat, 32, 96)
        fat[510:512] = b"\x55\xaa"
        fp = os.path.join(d, "fat32.img"); open(fp, "wb").write(fat)

        exf = bytearray(64 * 1024)
        exf[3:11] = b"EXFAT   "
        exf[108] = 9; exf[109] = 0
        struct.pack_into("<Q", exf, 72, 128)
        struct.pack_into("<I", exf, 92, 16)
        exf[510:512] = b"\x55\xaa"
        xp = os.path.join(d, "exfat.img"); open(xp, "wb").write(exf)

        for path, want_kind, label in (
                (fp, "fat32", "fat32 boot sector recognised"),
                (xp, "exfat", "exfat boot sector recognised"),
                (c, None, "no filesystem claimed on the empty image")):
            with open(path, "rb") as fh:
                r = identify_fat(fh, 0)
            got = r[0] if r else None
            mark = "PASS" if got == want_kind else "FAIL"
            if got != want_kind:
                ok = False
            print(f"  [{mark}] {label}: got={got}")

        # A FAT boot sector must not parse as an MBR: its boot code sits where
        # partition entries would be and yields nonsense regions otherwise.
        for path, label in ((fp, "fat32"), (xp, "exfat")):
            with open(path, "rb") as fh:
                r = parse_mbr(fh)
            mark = "PASS" if r is None else "FAIL"
            if r is not None:
                ok = False
            print(f"  [{mark}] parse_mbr declines the {label} boot sector")

        # ETFS and EFS, the QNX flash filesystems. The reserved names and the
        # F3S signature are spelled here as independent literals, deliberately
        # NOT read from ETFS_RESERVED or EFS_SIG, for the same circularity
        # reason as TRUE_MAGIC_LE above: a fixture built from the constant under
        # test cannot go red when that constant is wrong. Break a name or the
        # signature and this self-test exits 1. Change these only to the values
        # in QNX's fs/etfs.h and fs/f3s_spec.h.
        TRUE_RESERVED = {1: ".filetable", 2: ".badblks", 3: ".counts",
                         4: ".lost+found", 5: ".reserved"}
        TRUE_F3S_SIG = b"QSSL_F3S"
        if ETFS_RESERVED != TRUE_RESERVED:
            print(f"  [FAIL] ETFS_RESERVED {ETFS_RESERVED} != {TRUE_RESERVED}")
            ok = False
        if EFS_SIG != TRUE_F3S_SIG:
            print(f"  [FAIL] EFS_SIG {EFS_SIG!r} != {TRUE_F3S_SIG!r}")
            ok = False

        # A synthetic ETFS image: 1024-byte pages, each with a 16-byte spare
        # transaction. One .filetable page (fid 1) carries the reserved entries
        # and a test file at fid 6; a second page carries that file's data.
        Pz = 1024

        def _tr(fid, cluster, seq):               # an "ok" transaction record
            return struct.pack("<IIHBBI", fid, cluster, 1, 0, 0, seq)

        def _fe(pfid, mode, mtime, size, name):    # a 64-byte file-table entry
            return (struct.pack("<HH", 0x0000, pfid)
                    + struct.pack("<7I", mode, 0, 0, 0, mtime, 0, size)
                    + name.encode("utf-8")[:32].ljust(32, b"\x00"))

        payload = b"ETFS self-test payload\n"
        ftbl = bytearray()
        ftbl += _fe(0x0000, S_IFDIR | 0o755, 0, 0, "")                # fid 0 root
        for fid in range(1, 6):
            m = (S_IFDIR | 0o755) if fid == 4 else 0o100444
            ftbl += _fe(0x0000, m, 0, 0, TRUE_RESERVED[fid])          # fids 1..5
        ftbl += _fe(0x0000, 0o100644, 1712000000, len(payload), "selftest.txt")
        ftbl += b"\xff" * (Pz - len(ftbl))         # remaining entries invalid
        etfs_img = (bytes(ftbl) + _tr(ETFS_FID_FTABLE, 0, 5)
                    + payload.ljust(Pz, b"\x00") + _tr(6, 0, 6))
        ep = os.path.join(d, "etfs.bin"); open(ep, "wb").write(etfs_img)

        with open(ep, "rb") as fh:
            det = identify_etfs(fh, 0, len(etfs_img))
            kind = det[0] if det else None
            got = b""
            if kind == "etfs":
                w = walker_for("etfs", fh, 0, len(etfs_img))
                kids = dict(w.listdir(w.root))
                node = kids.get("selftest.txt")
                if node is not None:
                    got = b"".join(w.read_file(node, w.entry(node)[1]))
        mark = "PASS" if (kind == "etfs" and got == payload) else "FAIL"
        if kind != "etfs" or got != payload:
            ok = False
        print(f"  [{mark}] synthetic ETFS recognised and one file round-tripped: "
              f"kind={kind}")

        # A synthetic EFS image: one erase unit whose unit_info sizes it and
        # whose boot record carries the QSSL_F3S signature. Detection only, the
        # same depth as the FAT legs above; the full walk is proven by the
        # round-trip against qnxmount's committed images.
        us_pow2 = 16
        efs_img = bytearray(b"\xff" * (1 << us_pow2))
        struct.pack_into("<H", efs_img, 0, 0x10)          # unit_info struct_size
        efs_img[2] = 0x00                                 # endian
        efs_img[3] = 0xFF                                 # pad
        struct.pack_into("<H", efs_img, 4, us_pow2)       # unit_pow2
        efs_img[6:8] = b"\xff\xff"                        # reserve
        struct.pack_into("<I", efs_img, 8, 0)             # erase_count
        bo = 0x100                                        # boot_info offset
        struct.pack_into("<HBB", efs_img, bo, 0x18, 3, 0)
        efs_img[bo + 4:bo + 12] = TRUE_F3S_SIG
        struct.pack_into("<HHHH", efs_img, bo + 12, 0, 1, 0, 2)   # idx,total,spare,align
        struct.pack_into("<HH", efs_img, bo + 20, 1, 0)          # root ptr
        efp = os.path.join(d, "efs.bin"); open(efp, "wb").write(bytes(efs_img))
        with open(efp, "rb") as fh:
            det = identify_efs(fh, 0, len(efs_img))
        got_kind = det[0] if det else None
        mark = "PASS" if got_kind == "efs" else "FAIL"
        if got_kind != "efs":
            ok = False
        print(f"  [{mark}] synthetic EFS boot record recognised: kind={got_kind}")

        # Neither flash detector may fire on data that is not its filesystem.
        for path, label in ((c, "random"), (fp, "fat32"), (xp, "exfat")):
            sz = os.path.getsize(path)
            with open(path, "rb") as fh:
                e1 = identify_etfs(fh, 0, sz)
                e2 = identify_efs(fh, 0, sz)
            mark = "PASS" if (e1 is None and e2 is None) else "FAIL"
            if e1 is not None or e2 is not None:
                ok = False
            print(f"  [{mark}] ETFS and EFS decline the {label} image")

        # QNX IFS. The UCL decompressor and the imagefs layout are proven byte
        # for byte against real Ford Sync G4 images; these legs are the both-ways
        # regression guard, built from synthetic bytes so no evidence travels.
        #
        # The UCL stream below is a fixed synthetic block that exercises a literal
        # run, a back reference, a reuse of the last offset, a gamma-coded length
        # and the end marker. The expected output is written out by hand rather
        # than taken from the decoder, so a regression fails against a fixed
        # target instead of against itself. It reads: literals "abcXYZ", copy 3
        # from 6 back ("abc"), then copy 7 from 6 back ("XYZabcX").
        UCL_BLOCK = bytes.fromhex("fd61626358595ac40510000000000048ff")
        UCL_WANT = b"abcXYZabcXYZabcX"
        try:
            got = ucl_nrv2b_decompress(UCL_BLOCK)
        except Exception:
            got = None
        mark = "PASS" if got == UCL_WANT else "FAIL"
        if got != UCL_WANT:
            ok = False
        print(f"  [{mark}] UCL NRV2B decompresses a known block to {got!r}")

        broken = bytearray(UCL_BLOCK); broken[1] ^= 0xFF
        try:
            bad = ucl_nrv2b_decompress(bytes(broken))
        except Exception:
            bad = None
        mark = "PASS" if bad != UCL_WANT else "FAIL"
        if bad == UCL_WANT:
            ok = False
        print(f"  [{mark}] a corrupted UCL block does not reproduce it")

        framed = (struct.pack(">H", len(UCL_BLOCK)) + UCL_BLOCK) * 2 + b"\x00\x00"
        try:
            got = ifs_decompress_blocks(framed, ucl_nrv2b_decompress)
        except Exception:
            got = None
        mark = "PASS" if got == UCL_WANT * 2 else "FAIL"
        if got != UCL_WANT * 2:
            ok = False
        print(f"  [{mark}] block framing concatenates two blocks and stops at 0")

        # A small uncompressed imagefs: root dir, a top-level file, a file in an
        # implicit subdirectory, and a symlink. Built from the image.h structs so
        # the walker's dirent parse, implicit-directory synthesis, file read and
        # trailer checksum are all exercised. The trailer is set over the clean
        # image; the sabotaged copy flips one data byte afterwards, so its stored
        # checksum can no longer balance.
        def _ifs_image(corrupt=False):
            f2, f1, tgt = b"second file\n", b"hello d/f1\n", b"/etc/target"
            def attr(size, ino, mode):
                return struct.pack("<HHIIIII", size, 0, ino, mode, 0, 0, 0x5000)
            def d_dir(p, ino):
                t = p + b"\x00"; return attr(24 + len(t), ino, IFS_S_IFDIR | 0o755) + t
            def d_file(p, ino, off, sz):
                t = struct.pack("<II", off, sz) + p + b"\x00"
                return attr(24 + len(t), ino, IFS_S_IFREG | 0o644) + t
            def d_link(p, target, ino):
                nm = p + b"\x00"; t = nm + target + b"\x00"
                return (attr(24 + 4 + len(t), ino, IFS_S_IFLNK | 0o777)
                        + struct.pack("<HH", len(nm), len(target)) + t)
            def table(o2, o1):
                return (d_dir(b"", 1) + d_file(b"f2", 2, o2, len(f2))
                        + d_file(b"d/f1", 3, o1, len(f1))
                        + d_link(b"d/l1", tgt, 4) + struct.pack("<H", 0))
            dir_off = 92
            hdr_dir = dir_off + len(table(0, 0)) - 2
            data = (dir_off + len(table(0, 0)) + 3) & ~3
            o2, o1 = data, data + len(f2)
            img = bytearray(88)
            img[0:7] = b"imagefs"
            struct.pack_into("<I", img, 16, dir_off)
            img += b"/\x00\x00\x00"
            img += table(o2, o1)
            img += b"\x00" * (o2 - len(img))
            img += f2 + f1
            while len(img) % 4:
                img.append(0)
            struct.pack_into("<I", img, 8, len(img) + 4)
            struct.pack_into("<I", img, 12, hdr_dir)
            body = sum(struct.unpack_from("<%dI" % (len(img) // 4), img, 0))
            img += struct.pack("<I", (-body) & 0xFFFFFFFF)
            if corrupt:
                img[o2 + 1] ^= 0xFF
            hdr = bytearray(256)
            struct.pack_into("<I", hdr, 0, QNX_IFS_SIG)
            struct.pack_into("<H", hdr, 4, 1); hdr[6] = 0x01
            struct.pack_into("<H", hdr, 8, 256)
            struct.pack_into("<H", hdr, 10, 183)
            struct.pack_into("<I", hdr, 32, 512)
            struct.pack_into("<I", hdr, 36, 512 + len(img))
            struct.pack_into("<I", hdr, 44, len(img))
            return bytes(hdr) + b"\x00" * (512 - 256) + bytes(img)

        ip = os.path.join(d, "ifs_ok.img"); open(ip, "wb").write(_ifs_image())
        try:
            with open(ip, "rb") as fh:
                det = identify_ifs(fh, 0)
                w = IfsWalker(fh, 0)
                files = {p: (node, sz) for p, node, sz, _ in collect(w, w.root)}
                f2ok = b"".join(w.read_file(*files.get("f2", (None, 0)))) == b"second file\n"
                f1ok = b"".join(w.read_file(*files.get("d/f1", (None, 0)))) == b"hello d/f1\n"
                good = (det is not None and w.compress == "none" and w.cksum_ok is True
                        and f2ok and f1ok and "d" in w.nodes
                        and w.links.get("d/l1") == "/etc/target")
        except Exception:
            good = False
        mark = "PASS" if good else "FAIL"
        if not good:
            ok = False
        print(f"  [{mark}] synthetic IFS: header, tree, subdir, files, symlink, checksum")

        cp = os.path.join(d, "ifs_bad.img"); open(cp, "wb").write(_ifs_image(corrupt=True))
        try:
            with open(cp, "rb") as fh:
                balanced = IfsWalker(fh, 0).cksum_ok
        except Exception:
            balanced = None
        mark = "PASS" if balanced is False else "FAIL"
        if balanced is not False:
            ok = False
        print(f"  [{mark}] a flipped imagefs byte breaks the image checksum")

        # QNX4. The root name, the .bitmap name and the xblk signature are
        # spelled here as independent literals, deliberately NOT read from the
        # code under test, for the same circularity reason as TRUE_MAGIC_LE
        # above. Change these only to the values in the Linux kernel's
        # fs/qnx4 driver and include/uapi/linux/qnx4_fs.h.
        TRUE_QNX4_ROOT = b"/\x00"          # fs/qnx4/inode.c qnx4_checkroot
        TRUE_QNX4_BITMAP = b".bitmap"      # fs/qnx4/inode.c QNX4_BMNAME
        TRUE_QNX4_XBLK = b"IamXblk"        # fs/qnx4/inode.c:110
        if QNX4_XBLK_SIG != TRUE_QNX4_XBLK:
            print(f"  [FAIL] QNX4_XBLK_SIG {QNX4_XBLK_SIG!r} != {TRUE_QNX4_XBLK!r}")
            ok = False

        # A synthetic QNX4 image: superblock at block 2, root dir at block 3
        # carrying .bitmap, a short-named file, a long name linked through
        # .inodes, and a two-extent file resolved through an "IamXblk" block.
        def _q4_ino(name, size, xblk1, xsz1, xblk, nx, mode, mtime, status):
            e = bytearray(64)
            e[0:16] = name[:16].ljust(16, b"\x00")
            struct.pack_into("<I", e, 16, size)
            struct.pack_into("<II", e, 20, xblk1, xsz1)
            struct.pack_into("<I", e, 28, xblk)
            struct.pack_into("<I", e, 36, mtime)
            struct.pack_into("<H", e, 48, nx)
            struct.pack_into("<H", e, 50, mode)
            e[63] = status
            return bytes(e)

        q4_pay = b"qnx4 self-test payload\n"
        q4_long = b"content behind a link entry\n"
        q4_multi = bytes(((i * 31 + 7) & 0xFF) for i in range(700))
        q4 = bytearray(512 * 12)
        # block 2: RootDir "/" (dir at block 3, 1 block) + .inodes entry
        q4[512:512 + 64] = _q4_ino(TRUE_QNX4_ROOT.rstrip(b"\x00"), 512, 3, 1,
                                   0, 1, S_IFDIR | 0o755, 1712000000, 0x21)
        q4[512 + 64:512 + 128] = _q4_ino(b"", 512, 4, 1, 0, 1,
                                         0o100444, 1712000000, 0x11)
        # block 3: the root directory
        root = bytearray(512)
        root[0:64] = _q4_ino(TRUE_QNX4_BITMAP, 64, 5, 1, 0, 1,
                             0o100444, 1712000000, 0x01)
        root[64:128] = _q4_ino(b"selftest.txt", len(q4_pay), 6, 1, 0, 1,
                               0o100644, 1712000001, 0x01)
        lnk = bytearray(64)
        lnk[0:48] = b"a_longer_name_than_sixteen.txt".ljust(48, b"\x00")
        struct.pack_into("<I", lnk, 48, 4)     # inode at block 4, index 1
        lnk[52] = 1
        lnk[63] = 0x08                          # QNX4_FILE_LINK
        root[128:192] = bytes(lnk)
        root[192:256] = _q4_ino(b"multi.bin", len(q4_multi), 8, 1, 9, 2,
                                0o100644, 1712000003, 0x01)
        q4[1024:1536] = bytes(root)
        # block 4: .inodes (signature slot, then the long name's inode)
        q4[1536:1536 + 16] = b"IamTHE.inodeFILE"
        q4[1536 + 64:1536 + 128] = _q4_ino(b"a_longer_name_th", len(q4_long),
                                           7, 1, 0, 1, 0o100600, 1712000002,
                                           0x01)
        # blocks 5..8: bitmap bytes, two file payloads, first half of multi
        q4[2048:2048 + 64] = b"\xff" * 3 + b"\x00" * 61
        q4[2560:2560 + len(q4_pay)] = q4_pay
        q4[3072:3072 + len(q4_long)] = q4_long
        q4[3584:3584 + 512] = q4_multi[:512]
        # block 9: the xblk carrying the second extent (block 10)
        xb = bytearray(512)
        xb[8] = 1
        struct.pack_into("<I", xb, 12, 1)
        struct.pack_into("<II", xb, 16, 10, 1)
        xb[496:496 + 7] = TRUE_QNX4_XBLK
        q4[4096:4608] = bytes(xb)
        q4[4608:4608 + len(q4_multi) - 512] = q4_multi[512:]
        qp = os.path.join(d, "qnx4.img")
        open(qp, "wb").write(bytes(q4))

        with open(qp, "rb") as fh:
            det = identify_qnx4(fh, 0, len(q4))
            kind = det[0] if det else None
            got = got_long = got_multi = b""
            if kind == "qnx4":
                w = walker_for("qnx4", fh, 0, len(q4))
                kids = dict(w.listdir(w.root))
                for nm, dest in (("selftest.txt", "got"),
                                 ("a_longer_name_than_sixteen.txt", "got_long"),
                                 ("multi.bin", "got_multi")):
                    node = kids.get(nm)
                    if node is not None:
                        data = b"".join(w.read_file(node, w.entry(node)[1]))
                        if dest == "got":
                            got = data
                        elif dest == "got_long":
                            got_long = data
                        else:
                            got_multi = data
        good = (kind == "qnx4" and got == q4_pay and got_long == q4_long
                and got_multi == q4_multi)
        mark = "PASS" if good else "FAIL"
        if not good:
            ok = False
        print(f"  [{mark}] synthetic QNX4: root, .bitmap, link entry, "
              f"two-extent xblk file all read: kind={kind}")

        # Sabotage: break the .bitmap name and detection must refuse, exactly
        # as the kernel refuses to mount without it (qnx4_checkroot).
        sab = bytearray(q4)
        sab[1024:1024 + 7] = b".botmap"
        sp_ = os.path.join(d, "qnx4_sab.img")
        open(sp_, "wb").write(bytes(sab))
        with open(sp_, "rb") as fh:
            det = identify_qnx4(fh, 0, len(sab))
        mark = "PASS" if det is None else "FAIL"
        if det is not None:
            ok = False
        print(f"  [{mark}] a broken .bitmap name is declined, as the kernel "
              f"declines it")

        # A QNX4 boot block ending 0x55AA must not parse as an MBR (the same
        # shared-magic hazard as FAT above), and must still identify as qnx4.
        mbrish = bytearray(q4)
        mbrish[446 + 4] = 0x83
        struct.pack_into("<II", mbrish, 446 + 8, 1, 8)
        mbrish[510:512] = b"\x55\xaa"
        mp = os.path.join(d, "qnx4_mbr.img")
        open(mp, "wb").write(bytes(mbrish))
        with open(mp, "rb") as fh:
            r = parse_mbr(fh)
            det = identify_qnx4(fh, 0, len(mbrish))
        goodm = r is None and det is not None
        mark = "PASS" if goodm else "FAIL"
        if not goodm:
            ok = False
        print(f"  [{mark}] parse_mbr declines a QNX4 boot block ending 0x55AA")

        # Mutual declines: qnx4 fires on none of the other synthetic images,
        # and none of the other detectors fires on the qnx4 image.
        for path, label in ((c, "random"), (fp, "fat32"), (xp, "exfat"),
                            (ep, "etfs"), (efp, "efs"), (a, "qnx6 le"),
                            (b, "qnx6 be"), (ip, "ifs")):
            sz = os.path.getsize(path)
            with open(path, "rb") as fh:
                det = identify_qnx4(fh, 0, sz)
            mark = "PASS" if det is None else "FAIL"
            if det is not None:
                ok = False
            print(f"  [{mark}] QNX4 declines the {label} image")
        with open(qp, "rb") as fh:
            others = (identify_fat(fh, 0), identify_etfs(fh, 0, len(q4)),
                      identify_efs(fh, 0, len(q4)), identify_ifs(fh, 0))
        mark = "PASS" if all(o is None for o in others) else "FAIL"
        if not all(o is None for o in others):
            ok = False
        print(f"  [{mark}] FAT, exFAT, ETFS, EFS and IFS all decline the "
              f"qnx4 image")

        # A cut image. The first segment of a split acquisition (.001 of an
        # FTK Imager raw set) carries the partition table and the boot volumes,
        # so it identifies cleanly, and every volume past the cut reads as empty
        # because read_at() answers a seek past the end of the file with empty
        # bytes. Measured 2026-09-04 on a Ford Sync G4 image cut at 1,500 MB: the
        # boot partitions extracted in full and the 28.8 GiB storage volume
        # walked to 0 files with nothing raised. The probe has to say the file is
        # shorter than its table, and a file whose blocks lie past the cut has to
        # be counted SHORT and stored under a name that says so.
        cut = os.path.join(d, "positive_le_cut.img.001")
        with open(a, "rb") as src, open(cut, "wb") as dst:
            dst.write(src.read(3 * 1024 * 1024))
        reps = {}
        for name, path in (("cut", cut), ("full", a)):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main(path)
            reps[name] = buf.getvalue()
        after = reps["cut"].split("IMAGE IS SHORTER THAN ITS PARTITION TABLE", 1)
        warned = len(after) == 2 and "MBR part 1" in after[1][:600]
        quiet = "SHORTER THAN" not in reps["full"]
        for label, cond in (
                ("a 3 MiB cut of the 7 MiB positive image is reported shorter than "
                 "its partition table, naming MBR part 1", warned),
                ("the full positive image draws no such warning", quiet)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # The qnx4 fixture behind an MBR whose partition reaches past the cut.
        # multi.bin's second extent is qnx4 block 10 (offset 4608); the image
        # ends there, after the xblk that points to it, so the walk still finds
        # the file and its tail is past the end.
        mimg = bytearray(2048 * SECTOR + 4608)
        ent = bytearray(16)
        ent[4] = 0x4d
        struct.pack_into("<II", ent, 8, 2048, 32)      # 16 KiB declared, 4.5 KiB here
        mimg[446:462] = ent
        mimg[510:512] = b"\x55\xaa"
        mimg[2048 * SECTOR:] = q4[:4608]
        q4cut = os.path.join(d, "qnx4_behind_mbr_cut.img")
        open(q4cut, "wb").write(bytes(mimg))
        q4zip = os.path.join(d, "qnx4_cut.zip")
        man = []
        buf = io.StringIO()
        with zipfile.ZipFile(q4zip, "w") as zf, contextlib.redirect_stdout(buf):
            main(q4cut, extract=q4zip, zf=zf, manifest=man)
        rep_q4 = buf.getvalue()
        names = zipfile.ZipFile(q4zip).namelist()
        vol = "p1_lba2048"
        short_named = [n for n in names
                       if n.startswith(f"{vol}/multi.bin.SHORT-512-of-700")]
        entry = man[0] if man else {}
        for label, cond in (
                ("a file reaching past the cut is counted SHORT in the report and "
                 "the manifest, beside the 3 whole files",
                 "1 SHORT" in rep_q4 and entry.get("short") == 1
                 and entry.get("files") == 3
                 and entry.get("extends_past_image_by_bytes", 0) > 0),
                ("the short file is stored under a name saying how much of it is "
                 "here, and the whole files keep theirs",
                 len(short_named) == 1 and f"{vol}/selftest.txt" in names
                 and f"{vol}/multi.bin" not in names)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # A split image, joined by the reader. FTK Imager and its peers write a
        # raw image as numbered segments, and since 1.13 a run on any one of
        # them reads the whole set. The qnx4 fixture behind an MBR, cut into
        # three unequal, unaligned segments (one cut inside the gap before the
        # partition, one inside a file's extent), must report and extract
        # exactly as the one file does, from the .001 and from the .002, with
        # no short-image warning. The byte level check comes first, reads at
        # and across every boundary against the same slice of the one file
        # through one open handle at a time, so the join is proven
        # independently of any walker. A hole in the numbering, a set with no
        # first segment and a set numbered at two widths are refused by name,
        # and a lone first segment is still read as the one file it is.
        whole = bytearray(2048 * SECTOR + len(q4))
        ent = bytearray(16)
        ent[4] = 0x4d
        struct.pack_into("<II", ent, 8, 2048, -(-len(q4) // SECTOR))
        whole[446:462] = ent
        whole[510:512] = b"\x55\xaa"
        whole[2048 * SECTOR:] = q4
        whole = bytes(whole)
        cuts = (1000 * SECTOR + 7, 2048 * SECTOR + 4700)
        bounds = (0,) + cuts + (len(whole),)
        seg = [os.path.join(d, f"qnx4_split.img.{i + 1:03d}") for i in range(3)]
        for i, sp in enumerate(seg):
            open(sp, "wb").write(whole[bounds[i]:bounds[i + 1]])
        wp = os.path.join(d, "qnx4_split_whole.img")
        open(wp, "wb").write(whole)
        probes = [(c + k, 4096) for c in cuts for k in (-4096, -1, 0, 1)]
        probes += [(off, n) for off in range(0, len(whole), 1234 * 7)
                   for n in (1, 512, 4096)]
        with SegmentedImage(seg) as si:
            si.MAX_OPEN = 1                            # every crossing reopens
            byte_exact = (si.size == len(whole)
                          and all(read_at(si, off, n) == whole[off:off + n]
                                  for off, n in probes)
                          and read_at(si, len(whole) - 10, 100) == whole[-10:]
                          and read_at(si, len(whole) + 5, 10) == b"")
        whole_set = split_segments(seg[1]) == seg

        def run_extract(path, tag):
            zp = os.path.join(d, f"{tag}.zip")
            man, buf = [], io.StringIO()
            with zipfile.ZipFile(zp, "w") as zf, contextlib.redirect_stdout(buf):
                main(path, extract="split.zip", zf=zf, manifest=man)
            with zipfile.ZipFile(zp) as z:
                files = {n: z.read(n) for n in z.namelist()}
            rep = buf.getvalue()
            return rep.split("=" * 78)[2], files, man, rep   # body after the header

        w_body, w_files, w_man, _ = run_extract(wp, "split_whole")
        s1_body, s1_files, s1_man, s1_rep = run_extract(seg[0], "split_first")
        s2_body, s2_files, s2_man, s2_rep = run_extract(seg[1], "split_second")
        os.remove(wp)                        # the three segments stay as the fixture
        names = [os.path.basename(p) for p in seg]
        sizes = [bounds[i + 1] - bounds[i] for i in range(3)]

        def refusal(path):
            try:
                main(path)
            except SplitImageError as exc:
                return str(exc)
            return ""
        gap = [os.path.join(d, f"qnx4_gap.img.{n:03d}") for n in (1, 3)]
        nofirst = [os.path.join(d, f"qnx4_nofirst.img.{n:03d}") for n in (2, 3)]
        widths = [os.path.join(d, n) for n in ("qnx4_width.img.001", "qnx4_width.img.0002")]
        for p in gap + nofirst + widths:
            open(p, "wb").write(whole[:SECTOR])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gap_msg, nofirst_msg, width_msg = (refusal(gap[0]), refusal(nofirst[0]),
                                               refusal(widths[0]))
        for p in gap + nofirst + widths:
            os.remove(p)
        for label, cond in (
                ("reads at and across every segment boundary equal the one file, "
                 "through one open handle at a time, and past the end read empty",
                 byte_exact),
                ("any segment names the whole set, in order", whole_set),
                ("the split set reports and extracts exactly as the one file, from "
                 "the .001 and from the .002",
                 w_body == s1_body == s2_body and w_files == s1_files == s2_files
                 and len(w_files) >= 3),
                ("the joined run draws no short-image warning and names its segments",
                 "SHORTER THAN" not in s1_rep and "SHORTER THAN" not in s2_rep
                 and "3 segments joined" in s1_rep and "3 segments joined" in s2_rep),
                ("volumes.json names the first segment as the image and lists every "
                 "segment with its size; the one file carries no segment list",
                 bool(s1_man) and bool(s2_man)
                 and all(m["image"] == names[0]
                         and [e["name"] for e in m["image_segments"]] == names
                         and [e["bytes"] for e in m["image_segments"]] == sizes
                         for m in s1_man + s2_man)
                 and bool(w_man) and all("image_segments" not in m for m in w_man)),
                ("a hole in the numbering is refused naming the missing segment",
                 "qnx4_gap.img.002 is missing" in gap_msg),
                ("a set with no first segment is refused naming it",
                 "qnx4_nofirst.img.001" in nofirst_msg),
                ("segments numbered at two widths are refused",
                 "different number of digits" in width_msg),
                ("a lone first segment is read as the one file it is",
                 split_segments(cut) == [])):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # An EnCase/EWF acquisition is read through the vendored ewfprobe. The
        # case that matters is the negative one: an .E01 must never be opened as
        # raw bytes, because a container read that way holds no filesystem the
        # walkers can see and the run would report an empty image rather than
        # say it could not read the container.
        # This literal is deliberately NOT EWF_SIGNATURE. A fixture built from
        # the constant it is meant to verify moves with it, so the check passes
        # on a build whose signature is wrong. It is the EWF file signature from
        # the format documentation, written out again here on purpose.
        TRUE_EWF_SIG = b"\x45\x56\x46\x09\x0d\x0a\xff\x00"    # "EVF\t\r\n\xff\0"
        if EWF_SIGNATURE != TRUE_EWF_SIG:
            ok = False
            print(f"  [FAIL] EWF_SIGNATURE is {EWF_SIGNATURE!r}, "
                  f"expected {TRUE_EWF_SIG!r}")
        ewf_fake = os.path.join(d, "fake.E01")
        with open(ewf_fake, "wb") as fh:
            fh.write(TRUE_EWF_SIG + b"\x01\x01\x00\x00\x00" + b"\x00" * 4096)
        # Deliberately not named *.img: this is not an image, and the build
        # workflow harvests the self-test's synthetic images by that glob to
        # smoke-test the frozen executables.
        not_ewf = os.path.join(d, "not_an_acquisition.dat")
        with open(not_ewf, "wb") as fh:
            fh.write(b"PK\x03\x04not an acquisition" + b"\x00" * 512)

        def _opened_as_raw(path):
            """True when open_image handed back a plain file over the container."""
            try:
                handle = open_image(path)
            except Exception:
                return False
            try:
                return isinstance(handle, io.IOBase) and not hasattr(handle, "media_size")
            finally:
                try:
                    handle.close()
                except Exception:
                    pass

        saved_reader = ewfprobe
        try:
            globals()["ewfprobe"] = None
            try:
                open_image(ewf_fake)
                refused_without_reader = False
            except ImageUnreadable as exc:
                refused_without_reader = "ewfprobe" in str(exc)
            except Exception:
                refused_without_reader = False
        finally:
            globals()["ewfprobe"] = saved_reader

        for label, cond in (
                ("the EWF signature is recognised, and other bytes are not",
                 looks_like_ewf(ewf_fake) and not looks_like_ewf(not_ewf)),
                ("an .E01 is never opened as raw bytes",
                 not _opened_as_raw(ewf_fake)),
                ("a file that is not an acquisition still opens normally",
                 _opened_as_raw(not_ewf)),
                ("without the vendored reader an .E01 is refused, saying what "
                 "is missing", refused_without_reader),
                ("with the reader present a damaged acquisition is refused by "
                 "it, not read",
                 saved_reader is None or _ewf_refused_by_reader(ewf_fake))):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # ---- APFS ----------------------------------------------------
        # A container superblock built by hand, so identification is tested
        # against bytes this file did not read from a container it also wrote.
        apfs_head = bytearray(4096)
        struct.pack_into("<Q", apfs_head, 16, 7)                  # transaction id
        struct.pack_into("<I", apfs_head, 24, APFS_OBJECT_TYPE_NX_SUPERBLOCK)
        apfs_head[32:36] = APFS_NX_MAGIC
        struct.pack_into("<I", apfs_head, 36, 4096)               # block size
        struct.pack_into("<Q", apfs_head, 40, 256)                # block count
        apfs_img = os.path.join(d, "apfs_head.img")
        open(apfs_img, "wb").write(bytes(apfs_head) + b"\x00" * (1 << 20))
        with open(apfs_img, "rb") as ah:
            apfs_named = identify_apfs(ah, 0)
        apfs_bad = bytearray(apfs_head)
        struct.pack_into("<I", apfs_bad, 36, 3000)                # not a power of two
        apfs_bad_img = os.path.join(d, "apfs_bad.img")
        open(apfs_bad_img, "wb").write(bytes(apfs_bad) + b"\x00" * 4096)
        with open(apfs_bad_img, "rb") as ah:
            apfs_refused = identify_apfs(ah, 0) is None

        # A file-system key is the object id in its low sixty bits and the record
        # type in its high four, and the tree is sorted by the id first.
        fs_key_ok = (_apfs_fs_key(struct.pack("<Q", (APFS_TYPE_DIR_REC << 60) | 4242))
                     == (4242, APFS_TYPE_DIR_REC))

        # The checksum covers everything after itself, in 32-bit words. A block
        # whose checksum is right must pass and one byte later must not.
        good = bytearray(4096)
        struct.pack_into("<Q", good, 8, 1234)
        lo = hi = 0
        for off in range(8, len(good) - 3, 4):
            lo = (lo + struct.unpack_from("<I", good, off)[0]) % 0xFFFFFFFF
            hi = (hi + lo) % 0xFFFFFFFF
        c1 = (0xFFFFFFFF - ((lo + hi) % 0xFFFFFFFF)) % 0xFFFFFFFF
        c2 = (0xFFFFFFFF - ((lo + c1) % 0xFFFFFFFF)) % 0xFFFFFFFF
        struct.pack_into("<Q", good, 0, (c2 << 32) | c1)
        torn = bytearray(good)
        torn[100] ^= 0x01
        checksum_ok = _apfs_fletcher_ok(bytes(good)) and not _apfs_fletcher_ok(bytes(torn))

        # A sealed system volume's tree, built by hand: a root that declares
        # itself hashed and a leaf under it, with the child pointer stored
        # RELATIVE to the tree's root id the way macOS 11 and later write it.
        # The root id, the relative pointer and the id they must add up to are
        # written out separately here on purpose, so the test cannot agree with
        # the code by sharing its arithmetic.
        SEALED_ROOT_OID = 437419        # the tree's own id
        SEALED_REL      = 3108          # what the index node stores
        SEALED_CHILD    = 440527        # 437419 + 3108, stated, not computed
        if SEALED_ROOT_OID + SEALED_REL != SEALED_CHILD:
            raise AssertionError("the sealed-tree test constants disagree")

        def _apfs_node(level, flags, records, root_info=None):
            """One B-tree node laid out the way records() reads it."""
            node = bytearray(4096)
            struct.pack_into("<HHI", node, APFS_OBJ_HDR, flags, level, len(records))
            struct.pack_into("<HH", node, APFS_OBJ_HDR + 8, 0, len(records) * 8)
            toc_at = APFS_OBJ_HDR + 24
            keys_at = toc_at + len(records) * 8
            ends_at = 4096 - (APFS_BTREE_INFO if flags & APFS_BTNODE_ROOT else 0)
            koff, voff = 0, 0
            for i, (k, v) in enumerate(records):
                voff += len(v)
                struct.pack_into("<HHHH", node, toc_at + i * 8,
                                 koff, len(k), voff, len(v))
                node[keys_at + koff:keys_at + koff + len(k)] = k
                node[ends_at - voff:ends_at - voff + len(v)] = v
                koff += len(k)
            if root_info is not None:
                struct.pack_into("<I", node, 4096 - APFS_BTREE_INFO, root_info)
            return bytes(node)

        leaf_key = struct.pack("<Q", (APFS_TYPE_DIR_REC << 60) | 7)
        leaf = _apfs_node(0, APFS_BTNODE_LEAF, [(leaf_key, b"leafvalue")])
        # An index value in a hashed tree is the child pointer and then a hash,
        # so it is forty bytes where an ordinary one is eight.
        index_val = struct.pack("<Q", SEALED_REL) + bytes(range(32))
        root = _apfs_node(1, APFS_BTNODE_ROOT | 0x0008 | 0x0010,
                          [(struct.pack("<Q", 0), index_val)],
                          root_info=APFS_BTREE_HASHED)

        class _SealedVol:
            """Only what a B-tree asks of a volume: blocks, and id to block."""
            fixed_key_size = fixed_val_size = 0

            def block(self, n):
                return {10: root, 20: leaf}.get(n, bytes(4096))

            def resolve(self, oid):
                return {SEALED_CHILD: 20}.get(oid)

        _sv = _SealedVol()
        sealed_found = _ApfsBtree(_sv, 10, base_oid=SEALED_ROOT_OID).leaves(_apfs_fs_key)
        sealed_blind = _ApfsBtree(_sv, 10).leaves(_apfs_fs_key)
        # Read as a plain tree the pointer names an id the map does not hold, so
        # nothing is found. That is the shape of the defect this guards.
        sealed_ok = (sealed_found == [((7, APFS_TYPE_DIR_REC), 20)]
                     and sealed_blind == [])

        # The declaration is what marks the tree, and it is read from the
        # btree_info in the root node's last forty bytes.
        plain_root = _apfs_node(1, APFS_BTNODE_ROOT, [(struct.pack("<Q", 0), b"")],
                                root_info=0x00000042)
        sealed_flag_ok = (
            struct.unpack_from("<I", root, 4096 - APFS_BTREE_INFO)[0] & APFS_BTREE_HASHED
            and not struct.unpack_from("<I", plain_root, 4096 - APFS_BTREE_INFO)[0]
            & APFS_BTREE_HASHED)

        # A sealed volume's object ids run to sixty bits, so a walker node has
        # to carry one whole beside its volume index.
        _big = (5 << APFS_VOL_SHIFT) | 0x0FFFFFFF00001234
        wide_oid_ok = (_big >> APFS_VOL_SHIFT == 5
                       and _big & APFS_OID_MASK == 0x0FFFFFFF00001234
                       and _big != APFS_CONTAINER)

        # The space manager, built by hand. It is an ephemeral object, so it is
        # reached through a checkpoint map rather than the object map. The
        # descriptor area carries a superblock copy first and a STALE map second,
        # so both the type check and the transaction check have something to
        # reject, and the first chunk does not start at block zero, so a run's
        # base has to come from its chunk. The used blocks are one statement and
        # the runs they leave are another, and the check is on run positions,
        # because a free-block count cannot tell one bit order from the other.
        SM_BLOCK, SM_XID, SM_OID = 4096, 9, 1024
        SM_TOTAL = 48
        SM_USED = {0, 1, 2, 3, 4, 5, 6, 7, 9, 20, 21, 22, 23}
        # by hand: chunk one covers blocks 0..23 with a bitmap, chunk two 24..45
        # with a bitmap and nothing used, chunk three has no bitmap and so is
        # wholly free. Chunk three claims eight blocks from 46 where the
        # container has only two left, which is what a corrupt or truncated
        # container looks like, and the answer must stop at the container's own
        # block count rather than running past the end of the image. Free runs
        # are 8, 10..19, and 24..47 once the last two chunks' runs are joined.
        SM_WANT = [(8, 1), (10, 10), (24, 24)]
        _sb = bytearray(64 * SM_BLOCK)

        def _obj(at, xid, otype):
            struct.pack_into("<Q", _sb, at + 16, xid)
            struct.pack_into("<I", _sb, at + 24, otype)

        _obj(0, SM_XID, APFS_OBJECT_TYPE_NX_SUPERBLOCK)
        _sb[32:36] = APFS_NX_MAGIC
        struct.pack_into("<I", _sb, 36, SM_BLOCK)
        struct.pack_into("<Q", _sb, 40, SM_TOTAL)
        struct.pack_into("<I", _sb, 104, 3)          # nx_xp_desc_blocks
        struct.pack_into("<Q", _sb, 112, 1)          # nx_xp_desc_base, block 1
        struct.pack_into("<Q", _sb, APFS_NX_SPACEMAN_OID_OFF, SM_OID)

        # block 1: a superblock copy carrying this transaction id, with bytes
        # that would read as a mapping to a decoy if its type went unchecked
        _obj(1 * SM_BLOCK, SM_XID, APFS_OBJECT_TYPE_NX_SUPERBLOCK)
        struct.pack_into("<I", _sb, 1 * SM_BLOCK + 36, SM_BLOCK)   # its block size
        struct.pack_into("<QQ", _sb, 1 * SM_BLOCK + 40 + 24, SM_OID, 50)

        def _cpmap(block_no, xid, oid, paddr):
            at = block_no * SM_BLOCK
            _obj(at, xid, APFS_OBJECT_TYPE_CHECKPOINT_MAP)
            struct.pack_into("<I", _sb, at + 36, 1)  # one mapping
            struct.pack_into("<QQ", _sb, at + 40 + 24, oid, paddr)

        _cpmap(2, SM_XID - 1, SM_OID, 50)            # stale, names a decoy
        _cpmap(3, SM_XID, SM_OID, 4)                 # current

        def _spaceman(block_no, cib_block):
            at = block_no * SM_BLOCK
            _obj(at, SM_XID, APFS_OBJECT_TYPE_SPACEMAN)
            dev = at + APFS_SM_DEV_MAIN_OFF
            struct.pack_into("<II", _sb, dev + 16, 1, 0)   # one cib, no cab
            struct.pack_into("<I", _sb, dev + 32, 200)     # sm_addr_offset
            struct.pack_into("<Q", _sb, at + 200, cib_block)

        _spaceman(4, 7)                              # the real one, cib at block 7
        _spaceman(50, 51)                            # the decoy, outside the container

        def _cib(block_no, chunks):
            at = block_no * SM_BLOCK
            struct.pack_into("<I", _sb, at + 36, len(chunks))
            for i, (addr, count, free, bm) in enumerate(chunks):
                o = at + 40 + i * APFS_CI_SIZE
                struct.pack_into("<Q", _sb, o + 8, addr)
                struct.pack_into("<II", _sb, o + 16, count, free)
                struct.pack_into("<Q", _sb, o + 24, bm)

        _cib(7, [(0, 24, 11, 5), (24, 22, 22, 6), (46, 8, 8, 0)])
        _cib(51, [(0, 48, 48, 0)])                   # the decoy says everything is free
        for _b in SM_USED:                           # least significant bit first
            if _b < 24:
                _sb[5 * SM_BLOCK + (_b >> 3)] |= 1 << (_b & 7)
            elif _b < 46:
                _i = _b - 24
                _sb[6 * SM_BLOCK + (_i >> 3)] |= 1 << (_i & 7)

        class _SpacemanOnly:
            """Only what free_extents asks of an APFS walker."""
            free_extents = ApfsWalker.free_extents   # pylint: disable=protected-access
            _ephemeral = ApfsWalker._ephemeral       # pylint: disable=protected-access
            base = 0
            block_size = SM_BLOCK
            block_count = SM_TOTAL
            xid = SM_XID

            def __init__(self, buf):
                self._buf = bytes(buf)
                self._nx = self._buf[0:SM_BLOCK]

            def block(self, n):
                return self._buf[n * SM_BLOCK:(n + 1) * SM_BLOCK]

        _smgot = _SpacemanOnly(_sb).free_extents()
        apfs_free_ok = _smgot == [(c * SM_BLOCK, n * SM_BLOCK) for c, n in SM_WANT]
        apfs_free_floor_ok = (_SpacemanOnly(_sb).free_extents(min_bytes=11 * SM_BLOCK)
                              == [(24 * SM_BLOCK, 24 * SM_BLOCK)])
        # a container whose space manager cannot be found says nothing rather
        # than saying nothing is free
        _nosm = bytearray(_sb)
        struct.pack_into("<Q", _nosm, APFS_NX_SPACEMAN_OID_OFF, 0)
        apfs_no_spaceman_ok = _SpacemanOnly(_nosm).free_extents() == []
        # nor may it read whatever the checkpoint map happens to point at: a
        # mapping that names a block which is not a space manager is refused
        _wrongobj = bytearray(_sb)
        struct.pack_into("<I", _wrongobj, 4 * SM_BLOCK + 24,
                         APFS_OBJECT_TYPE_CHECKPOINT_MAP)
        apfs_wrong_object_ok = _SpacemanOnly(_wrongobj).free_extents() == []

        for label, cond in (
                ("an APFS container superblock is identified by its own geometry",
                 bool(apfs_named) and apfs_named[0] == "apfs"),
                ("a container superblock with an impossible block size is refused",
                 apfs_refused),
                ("a file-system key splits into an object id and a record type",
                 fs_key_ok),
                ("a block's Fletcher-64 checksum is checked, and a torn one fails",
                 checksum_ok),
                ("a sealed volume's tree declares itself hashed in its btree_info",
                 bool(sealed_flag_ok)),
                ("a sealed volume's child pointer is followed relative to the "
                 "tree's root id", sealed_ok),
                ("a walker node carries a whole sixty-bit object id beside its "
                 "volume index", wide_oid_ok),
                ("the space manager is found through the current checkpoint map "
                 "and reads back as the runs of free space it describes",
                 apfs_free_ok),
                ("an APFS free-space floor drops the short runs",
                 apfs_free_floor_ok),
                ("a container whose space manager cannot be found reports "
                 "nothing rather than nothing free", apfs_no_spaceman_ok),
                ("a checkpoint mapping naming something that is not a space "
                 "manager is refused rather than read", apfs_wrong_object_ok)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        apfs_fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "tests", "fixtures", "apfs-fixture.img.gz")
        apfs_want = apfs_fix[:-len(".img.gz")] + ".sha256"
        if os.path.isfile(apfs_fix) and os.path.isfile(apfs_want):
            try:
                got, want, missing, differ = _apfs_fixture_check(apfs_fix, apfs_want)
                broke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                # A reader that raises on a volume it cannot parse must fail this
                # check, not take the whole self-test down with it: a run that
                # stops early prints no FAIL line and reads as a pass.
                got = want = missing = differ = 0
                broke = f"; the walk raised {type(exc).__name__}: {exc}"
            cond = got and not missing and not differ and not broke
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] every file of the APFS "
                  f"fixture matches what an independent reader recorded "
                  f"({got} of {want}"
                  + (f", {missing} missing" if missing else "")
                  + (f", {differ} different" if differ else "") + ")" + broke)
        else:
            print("  [SKIP] the APFS fixture is not beside this script, so the "
                  "walk was not compared against it")

        # ---- HFS+ ----------------------------------------------------
        # A volume header built by hand, so identification is tested against
        # bytes this file did not read from a volume it also wrote.
        def _hfs_header(sig, block_size=4096, total=6144):
            vh = bytearray(512)
            struct.pack_into(">HH", vh, 0, sig, 4)
            struct.pack_into(">II", vh, 16, 3900000000, 3900000000)   # created, modified
            struct.pack_into(">II", vh, 32, 413, 6)                   # files, folders
            struct.pack_into(">III", vh, 40, block_size, total, 100)
            return bytes(vh)

        hfs_img = os.path.join(d, "hfs_header.img")
        open(hfs_img, "wb").write(b"\x00" * HFSP_VH_OFF + _hfs_header(HFSP_SIG)
                                  + b"\x00" * (1 << 20))
        hfsx_img = os.path.join(d, "hfsx_header.img")
        open(hfsx_img, "wb").write(b"\x00" * HFSP_VH_OFF + _hfs_header(HFSX_SIG)
                                   + b"\x00" * (1 << 20))
        hfs_bad = os.path.join(d, "hfs_bad.img")
        open(hfs_bad, "wb").write(b"\x00" * HFSP_VH_OFF
                                  + _hfs_header(HFSP_SIG, block_size=3000)
                                  + b"\x00" * 4096)
        with open(hfs_img, "rb") as hh:
            hfs_named = identify_hfsplus(hh, 0)
        with open(hfsx_img, "rb") as hh:
            hfsx_named = identify_hfsplus(hh, 0)
        with open(hfs_bad, "rb") as hh:
            hfs_refused = identify_hfsplus(hh, 0) is None

        # A fork record: a size, a clump, a block count, then eight extent
        # descriptors of which only the used ones count.
        fork = bytearray(80)
        struct.pack_into(">QII", fork, 0, 12345, 0, 4)
        struct.pack_into(">II", fork, 16, 100, 3)
        struct.pack_into(">II", fork, 24, 200, 1)
        fork_ok = _hfs_fork(bytes(fork), 0) == (12345, [(100, 3), (200, 1)])

        # A name is a count of UTF-16 units and then that many, big endian.
        name_bytes = struct.pack(">H", 3) + "abc".encode("utf-16-be")
        name_ok = _hfs_name(name_bytes, 0) == ("abc", 8)

        # One B-tree node: a descriptor, two records, and the offset array at the
        # very end that says where they are, counted backwards.
        node = bytearray(512)
        struct.pack_into(">IIbBH", node, 0, 7, 0, HFSP_LEAF, 1, 2)
        r1 = struct.pack(">H", 4) + b"KEY1" + b"DATA-ONE"
        r2 = struct.pack(">H", 4) + b"KEY2" + b"DATA-TWO"
        node[14:14 + len(r1)] = r1
        node[14 + len(r1):14 + len(r1) + len(r2)] = r2
        struct.pack_into(">H", node, 510, 14)
        struct.pack_into(">H", node, 508, 14 + len(r1))
        struct.pack_into(">H", node, 506, 14 + len(r1) + len(r2))
        desc, recs = _HfsTree.records(bytes(node))
        node_ok = (desc == (HFSP_LEAF, 7) and len(recs) == 2
                   and recs[0] == (b"KEY1", b"DATA-ONE")
                   and recs[1] == (b"KEY2", b"DATA-TWO"))

        # HFS+ keeps an allocation file, one bit per block, and the bits run
        # MOST significant first, the opposite way round from NTFS and exFAT.
        # A count of free blocks cannot tell the two orders apart, because a
        # byte holds the same number of zero bits either way, so the fixture is
        # built with the used blocks in one statement and the runs they leave in
        # another, and the check is on the run POSITIONS.
        HFS_BLOCK = 4096
        HFS_TOTAL = 38                              # not a multiple of eight
        HFS_USED = {0, 1, 2, 9, 20, 21, 22, 23}
        # by hand from that set, over blocks 0 to 37: free runs are 3..8,
        # 10..19, 24..37
        HFS_WANT = [(3, 6), (10, 10), (24, 14)]
        _hbits = bytearray((HFS_TOTAL + 7) // 8)
        for _b in HFS_USED:
            _hbits[_b >> 3] |= 0x80 >> (_b & 7)     # most significant bit first
        _hbuf = bytearray(4 * HFS_BLOCK)
        _hvh = bytearray(512)
        struct.pack_into(">HH", _hvh, 0, HFSP_SIG, 4)
        struct.pack_into(">III", _hvh, 40, HFS_BLOCK, HFS_TOTAL, len(HFS_USED))
        struct.pack_into(">QII", _hvh, HFSP_ALLOC_FORK, len(_hbits), 0, 1)
        struct.pack_into(">II", _hvh, HFSP_ALLOC_FORK + 16, 1, 1)   # one extent, block 1
        _hbuf[HFSP_VH_OFF:HFSP_VH_OFF + 512] = _hvh
        _hbuf[HFS_BLOCK:HFS_BLOCK + len(_hbits)] = _hbits

        class _AllocOnly:
            """Only what free_extents asks of an HFS+ walker."""
            free_extents = HfsPlusWalker.free_extents    # pylint: disable=protected-access
            _read_extents = HfsPlusWalker._read_extents  # pylint: disable=protected-access
            base = 0
            block_size = HFS_BLOCK
            total_blocks = HFS_TOTAL

            def __init__(self):
                self.fh = io.BytesIO(bytes(_hbuf))

            def _overflow(self, _cnid, _resource=False):
                return []                            # the header holds the whole fork

        _hgot = _AllocOnly().free_extents()
        hfs_free_ok = _hgot == [(c * HFS_BLOCK, n * HFS_BLOCK) for c, n in HFS_WANT]
        # the same bitmap read the other way round must NOT give this answer,
        # which is what a free-block count alone can never establish
        _lsb = bytearray((HFS_TOTAL + 7) // 8)
        for _b in HFS_USED:
            _lsb[_b >> 3] |= 1 << (_b & 7)
        hfs_bit_order_ok = bytes(_lsb) != bytes(_hbits) and sum(
            bin(x).count("1") for x in _lsb) == sum(bin(x).count("1") for x in _hbits)
        hfs_free_floor_ok = (_AllocOnly().free_extents(min_bytes=11 * HFS_BLOCK)
                             == [(24 * HFS_BLOCK, 14 * HFS_BLOCK)])

        # A B-tree that is allocated but holds nothing says root 0, depth 0 in
        # its header, and node 0 is that header rather than a leaf. Every HFS+
        # volume with no extended attributes and no fragmented file has exactly
        # that shape, so this is the ordinary case: nps-2009-hfsjtest1 has it,
        # and descending into the header read its own records as index pointers
        # and raised. Two fixtures, because two separate guards stand here and
        # one fixture would let either of them look load-bearing on its own.
        class _TinyVol:
            block_size = 4096
            base = 0

            def __init__(self, buf):
                self.fh = io.BytesIO(bytes(buf))

        def _hfs_node(buf, at, kind, records):
            """One B-tree node: a descriptor, the records, and the offset array."""
            struct.pack_into(">bBH", buf, at + 8, kind, 0, len(records))
            pos, offs = 14, []
            for rec in records:
                offs.append(pos)
                buf[at + pos:at + pos + len(rec)] = rec
                pos += len(rec)
            offs.append(pos)
            for i, off in enumerate(offs):
                struct.pack_into(">H", buf, at + 4096 - 2 * (i + 1), off)

        # empty tree: header node only, root 0 and depth 0, and its first record
        # carries no four byte pointer, which is what raised on the real volume
        # the real shape, read off nps-2009-hfsjtest1: three records, the last
        # of them carrying a long key and NO data, which is the one the descent
        # tried to read a node pointer out of
        _empty = bytearray(2 * 4096)
        # the last record's key length swallows the whole record, so its data
        # is empty, exactly as the real header node's third record is
        _hfs_node(_empty, 0, HFSP_HEADER,
                  [struct.pack(">H", 0) + bytes(102),
                   struct.pack(">H", 0) + bytes(124),
                   struct.pack(">H", 200) + bytes(198)])
        struct.pack_into(">HI", _empty, 14, 0, 0)        # depth 0, root 0
        struct.pack_into(">H", _empty, 14 + 16, 4096)    # node size
        _t_empty = _HfsTree(_TinyVol(_empty), len(_empty), [(0, 1)], "attributes")

        # a tree whose root points at a map node, which is neither index nor leaf
        _mapped = bytearray(3 * 4096)
        _hfs_node(_mapped, 0, HFSP_HEADER, [b""])
        struct.pack_into(">HI", _mapped, 14, 1, 1)       # depth 1, root node 1
        struct.pack_into(">H", _mapped, 14 + 16, 4096)
        _hfs_node(_mapped, 4096, HFSP_MAP, [b"\x00\x00"])
        _t_mapped = _HfsTree(_TinyVol(_mapped), len(_mapped), [(0, 1), (1, 1)], "attributes")

        def _finds_nothing(tree):
            # key_of answers below the wanted key for every record, the way the
            # real attribute keys do for a file id that is not in the tree, so
            # the descent walks the whole record list and reaches the last one
            try:
                return tree.find(1, lambda key: 0) is None
            except Exception:                            # pylint: disable=broad-except
                return False                             # raising is the defect

        empty_tree_ok = (_t_empty.root == 0 and _t_empty.depth == 0
                         and _finds_nothing(_t_empty))
        odd_node_ok = _t_mapped.root == 1 and _finds_nothing(_t_mapped)

        for label, cond in (
                ("an HFS+ volume header is identified by its own geometry",
                 bool(hfs_named) and hfs_named[0] == "hfs+"),
                ("HFSX is recognised as the case-sensitive variant it is",
                 bool(hfsx_named) and hfsx_named[0] == "hfsx"),
                ("a volume header with an impossible block size is refused",
                 hfs_refused),
                ("a fork record yields its size and only its used extents", fork_ok),
                ("a catalog name decodes from UTF-16 big endian", name_ok),
                ("a B-tree node's records are found through its offset array",
                 node_ok),
                ("the allocation file reads back as the runs of free space it "
                 "describes, most significant bit first", hfs_free_ok),
                ("the two bit orders hold the same number of free blocks, so a "
                 "count cannot tell them apart", hfs_bit_order_ok),
                ("an HFS+ free-space floor drops the short runs",
                 hfs_free_floor_ok),
                ("a B-tree that is allocated but empty is read as holding "
                 "nothing, not descended into", empty_tree_ok),
                ("a descent that reaches a node which is neither index nor leaf "
                 "stops rather than reading it as a pointer", odd_node_ok)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        hfs_fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "tests", "fixtures", "hfsplus-fixture.img.gz")
        hfs_want = hfs_fix[:-len(".img.gz")] + ".sha256"
        if os.path.isfile(hfs_fix) and os.path.isfile(hfs_want):
            try:
                got, want, missing, differ = _hfs_fixture_check(hfs_fix, hfs_want)
                broke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                # A reader that raises on a volume it cannot parse must fail this
                # check, not take the whole self-test down with it: a run that
                # stops early prints no FAIL line and reads as a pass.
                got = want = missing = differ = 0
                broke = f"; the walk raised {type(exc).__name__}: {exc}"
            cond = got and not missing and not differ and not broke
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] every file of the HFS+ "
                  f"fixture matches what an independent reader recorded "
                  f"({got} of {want}"
                  + (f", {missing} missing" if missing else "")
                  + (f", {differ} different" if differ else "") + ")" + broke)
        else:
            print("  [SKIP] the HFS+ fixture is not beside this script, so the "
                  "walk was not compared against it")

        # ---- NTFS ----------------------------------------------------
        # A boot sector built by hand, so identification is tested against bytes
        # this file did not read from a volume it also wrote.
        ntfs_boot = bytearray(512)
        ntfs_boot[3:11] = b"NTFS    "
        struct.pack_into("<H", ntfs_boot, 11, 512)        # bytes per sector
        ntfs_boot[13] = 8                                 # sectors per cluster
        struct.pack_into("<Q", ntfs_boot, 40, 100000)     # total sectors
        struct.pack_into("<Q", ntfs_boot, 48, 4)          # $MFT cluster
        struct.pack_into("<Q", ntfs_boot, 56, 2)          # $MFTMirr cluster
        struct.pack_into("<b", ntfs_boot, 64, -10)        # 1024-byte records
        struct.pack_into("<b", ntfs_boot, 68, -12)        # 4096-byte index blocks
        ntfs_boot[510:512] = b"\x55\xaa"
        ntfs_img = os.path.join(d, "ntfs_boot.img")
        open(ntfs_img, "wb").write(bytes(ntfs_boot) + b"\x00" * (1 << 20))
        with open(ntfs_img, "rb") as nfh:
            ntfs_named = identify_ntfs(nfh, 0)
            ntfs_declined_by_mbr = parse_mbr(nfh) is None
        bad_boot = bytearray(ntfs_boot)
        bad_boot[13] = 7                                  # not a power of two
        bad_img = os.path.join(d, "ntfs_bad.img")
        open(bad_img, "wb").write(bytes(bad_boot) + b"\x00" * 4096)
        with open(bad_img, "rb") as nfh:
            ntfs_refused = identify_ntfs(nfh, 0) is None

        # A mapping-pair list worked out by hand from the documented encoding.
        # 0x31: a one-byte length and a three-byte offset, so 8 clusters at LCN
        # 0x0C0000. 0x11: one and one, length 4 and offset 0xF8, which is -8
        # SIGNED, so the next run starts BEFORE the last one, at 786,424. Read
        # unsigned it would land at 786,680, which is the whole point of the
        # case. 0x01: a length and no offset at all, which is a sparse run.
        run_bytes = (
            "3108" + "00000c"      # 8 clusters at LCN 0x0c0000
            + "1104" + "f8"        # 4 more, offset -8, so LCN 786,424
            + "0105"               # 5 clusters with no offset at all: sparse
            + "00")                # end of list
        runs = _ntfs_runs(bytes.fromhex(run_bytes), 0, 0)
        runs_ok = runs == [(786432, 8), (786424, 4), (None, 5)]

        # A real LZNT1 chunk lifted out of a volume written by mkntfs and
        # ntfs-3g, with the plaintext it has to produce written out here rather
        # than taken from the decoder.
        lz_hex = (
            "62b10061206c696e6520740068617420726570650061747320616e642000736f"
            "20636f6d7072006573736573207765f86c6c0affab5f055f055f055f05ff5f05"
            "5f055f055f055f055f055f055f05ff5f055f055f055f055f055f055f055f05ff"
            "5f055f055f055f055f055f055f055f05ff5f05af02af02af02af02af02af02af"
            "02ffaf02af02af02af02af02af02af02af02ffaf02af02af02af02af02af02af"
            "02af02ffaf02af02af02af02af02af02af02af02ffaf02af02af02af02af02af"
            "02af02af02ffaf02af02af02af02af02af02af02af02ffaf02af02af02af02af"
            "02af02af02af02ffaf02af02af02af02af02af02af02af02ffaf02af02af02af"
            "02af02af02af02af02ffaf02af02af02af02af02af02af02af02ffaf02af02af"
            "02af02af02af02af02af02ffaf02af02af02af02af02af02af02af02ffaf02af"
            "02af02af02af02af02af02af02ffaf02af02af02af02af02af02af02af0207af"
            "02af02a402")
        lz_chunk = bytes.fromhex(lz_hex)
        lz_line = b"a line that repeats and so compresses well\n"
        lz_ok = (_lznt1_decompress(lz_chunk, 4096)
                 == (lz_line * (4096 // len(lz_line) + 2))[:4096])

        # A record whose last sector was not written with the rest must be
        # refused rather than parsed with the stamp still in it.
        rec = bytearray(1024)
        rec[0:4] = b"FILE"
        struct.pack_into("<HH", rec, 4, 0x30, 3)          # usa at 0x30, two sectors
        rec[0x30:0x32] = b"\xaa\x55"                      # the stamp
        rec[0x32:0x36] = b"\x01\x02\x03\x04"             # what the sectors really hold
        rec[510:512] = b"\xaa\x55"
        rec[1022:1024] = b"\xaa\x55"
        fixed = _ntfs_fixup(bytes(rec), 512, NTFS_FILE)
        torn = bytearray(rec)
        torn[1022:1024] = b"\x00\x00"                     # one sector missed the write
        fixup_ok = (fixed is not None and fixed[510:512] == b"\x01\x02"
                    and fixed[1022:1024] == b"\x03\x04"
                    and _ntfs_fixup(bytes(torn), 512, NTFS_FILE) is None)

        # A directory index whose entry names a record that has since been freed
        # and handed out again. The reference carries the generation the entry
        # was written for, in its top 16 bits, so the two can be told apart.
        # Built by hand here, with the generation numbers written out rather
        # than taken from the code under test.
        def _idx_entry(rec, seq, name):
            nm = name.encode("utf-16-le")
            elen = 0x52 + len(nm)
            elen += (-elen) % 8
            e = bytearray(elen)
            struct.pack_into("<Q", e, 0, (seq << 48) | rec)   # the file reference
            struct.pack_into("<HHH", e, 8, elen, 0x42 + len(nm), 0)
            struct.pack_into("<Q", e, 0x10, 5)                # parent, unused here
            e[0x50] = len(name)
            e[0x51] = 1                                       # a long name, not 8.3
            e[0x52:0x52 + len(nm)] = nm
            return bytes(e)

        live = _idx_entry(70, 3, "live.txt")          # generation 3, and the record is 3
        stale = _idx_entry(71, 9, "stale.txt")        # generation 9, the record is 4
        last = bytearray(0x18)                        # the end marker carries no name
        struct.pack_into("<HHH", last, 8, 0x18, 0, 0x02)
        body = live + stale + bytes(last)
        idx = bytearray(16) + body
        struct.pack_into("<II", idx, 0, 16, 16 + len(body))

        # The index reader is exercised as it ships, on a stub that answers only
        # the one question it asks of a walker.
        class _SeqOnly:
            """Only what _index_entries asks of a walker: each record's generation."""
            _index_entries = NtfsWalker._index_entries  # pylint: disable=protected-access

            def _seq(self, num):
                return {70: 3, 71: 4}.get(num)

        found = []
        _SeqOnly()._index_entries(bytes(idx), 0, found, set())  # pylint: disable=protected-access
        stale_ok = found == [("live.txt", 70)]

        # $Bitmap read back as free runs. The bitmap is built here bit by bit and
        # the runs it must produce are written out separately as literals, so the
        # test cannot agree with the code by sharing its arithmetic. The last
        # cluster is deliberately FREE, so the run reaching the end of the volume
        # is exercised; a reader that only closes a run when it meets a used
        # cluster loses it, and a fixture ending in a used cluster never notices.
        # The bits past the volume's last cluster are left free here, which real
        # NTFS does not do, so that a reader failing to stop at the volume's end
        # runs off it and is caught.
        FREE_CLUSTER_SIZE = 4096
        FREE_TOTAL = 40                      # clusters the volume has
        FREE_USED = {0, 1, 2, 9, 20, 21, 22, 23}
        # by hand from that set: free runs are 3..8, 10..19, 24..39
        FREE_WANT_CLUSTERS = [(3, 6), (10, 10), (24, 16)]
        FREE_BASE = 1 << 20

        _bm = bytearray((FREE_TOTAL + 7) // 8 + 2)     # spare bytes, left free
        for _c in FREE_USED:
            _bm[_c >> 3] |= 1 << (_c & 7)

        class _BitmapOnly:
            """Only what free_extents asks of a walker."""
            free_extents = NtfsWalker.free_extents  # pylint: disable=protected-access
            base = FREE_BASE
            cluster = FREE_CLUSTER_SIZE
            bps = 512
            total_sectors = FREE_TOTAL * FREE_CLUSTER_SIZE // 512

            def _data_attr(self, _num):
                attr = _NtfsAttr(NTFS_DATA, "", 0, False)
                attr.data_size = len(_bm)
                return attr

            def read_file(self, _num, _size):
                yield bytes(_bm)

        _got = _BitmapOnly().free_extents()
        _want = [(FREE_BASE + c * FREE_CLUSTER_SIZE, n * FREE_CLUSTER_SIZE)
                 for c, n in FREE_WANT_CLUSTERS]
        _volume_end = FREE_BASE + FREE_TOTAL * FREE_CLUSTER_SIZE
        free_ok = (_got == _want
                   and all(at + n <= _volume_end for at, n in _got))
        # a floor drops the runs too short to hold anything worth recovering
        free_floor_ok = (_BitmapOnly().free_extents(min_bytes=11 * FREE_CLUSTER_SIZE)
                         == [(FREE_BASE + 24 * FREE_CLUSTER_SIZE, 16 * FREE_CLUSTER_SIZE)])

        # FAT32 says what is free in the file allocation table itself: an entry
        # of zero is a free cluster. A volume is built here by hand, small
        # enough that the answer can be written out rather than computed, and
        # the used clusters and the runs they leave are two separate statements
        # so the test cannot agree with the code by construction.
        FAT_BPS, FAT_SPC, FAT_RSVD, FAT_NFATS = 512, 1, 32, 1
        FAT_DATA_CLUSTERS = 40
        FAT_USED = {2, 3, 4, 11, 22, 23, 24, 25}
        # by hand from that set: free runs are 5..10, 12..21, 26..41
        FAT_WANT = [(5, 6), (12, 10), (26, 16)]
        FAT_SPF = 4                                  # 4 sectors holds 512 entries
        _fatbuf = bytearray(FAT_RSVD * FAT_BPS + FAT_NFATS * FAT_SPF * FAT_BPS
                            + FAT_DATA_CLUSTERS * FAT_SPC * FAT_BPS)
        struct.pack_into("<H", _fatbuf, 11, FAT_BPS)
        _fatbuf[13] = FAT_SPC
        struct.pack_into("<H", _fatbuf, 14, FAT_RSVD)
        _fatbuf[16] = FAT_NFATS
        struct.pack_into("<I", _fatbuf, 32,
                         FAT_RSVD + FAT_NFATS * FAT_SPF + FAT_DATA_CLUSTERS * FAT_SPC)
        struct.pack_into("<I", _fatbuf, 36, FAT_SPF)
        struct.pack_into("<I", _fatbuf, 44, 2)       # root cluster
        _fat_at = FAT_RSVD * FAT_BPS
        struct.pack_into("<I", _fatbuf, _fat_at, 0x0FFFFFF8)      # media descriptor
        struct.pack_into("<I", _fatbuf, _fat_at + 4, 0x0FFFFFFF)  # end of chain
        for _c in FAT_USED:
            struct.pack_into("<I", _fatbuf, _fat_at + _c * 4, 0x0FFFFFFF)
        # one 8.3 entry in the root, so collect() has something to carry times
        # for. The date and time words are written out here rather than built by
        # the code under test, and the reading they encode is stated separately.
        _de = _fat_at + FAT_NFATS * FAT_SPF * FAT_BPS      # cluster 2's data
        _fatbuf[_de:_de + 11] = b"HELLO   TXT"
        _fatbuf[_de + 11] = 0x20                           # an ordinary file
        struct.pack_into("<H", _fatbuf, _de + 24, (2023 - 1980) << 9 | (6 << 5) | 1)
        struct.pack_into("<H", _fatbuf, _de + 22, (12 << 11) | (30 << 5) | 15)
        struct.pack_into("<H", _fatbuf, _de + 26, 11)      # first cluster, a used one
        struct.pack_into("<I", _fatbuf, _de + 28, 512)     # size
        FAT_ENTRY_WRITTEN = "2023-06-01 12:30:30"
        # and a subdirectory holding one file, so the walk down carries the
        # readings too rather than only reporting the root's
        _fatbuf[_de + 32:_de + 43] = b"SUB        "
        _fatbuf[_de + 43] = 0x10                           # a directory
        struct.pack_into("<H", _fatbuf, _de + 32 + 26, 22) # first cluster, a used one
        _sub = _de + (22 - 2) * FAT_BPS
        _fatbuf[_sub:_sub + 11] = b"DEEP    TXT"
        _fatbuf[_sub + 11] = 0x20
        struct.pack_into("<H", _fatbuf, _sub + 24, (1999 - 1980) << 9 | (12 << 5) | 31)
        struct.pack_into("<H", _fatbuf, _sub + 22, (23 << 11) | (59 << 5) | 29)
        struct.pack_into("<H", _fatbuf, _sub + 26, 23)     # first cluster, a used one
        struct.pack_into("<I", _fatbuf, _sub + 28, 64)
        FAT_DEEP_WRITTEN = "1999-12-31 23:59:58"

        _fatw = Fat32Walker(io.BytesIO(bytes(_fatbuf)), 0)
        _fat_data = _fat_at + FAT_NFATS * FAT_SPF * FAT_BPS
        fat_free_ok = (_fatw.free_extents()
                       == [(_fat_data + (c - 2) * FAT_BPS, n * FAT_BPS)
                           for c, n in FAT_WANT])
        fat_floor_ok = (_fatw.free_extents(min_bytes=11 * FAT_BPS)
                        == [(_fat_data + 24 * FAT_BPS, 16 * FAT_BPS)])

        # Entries 0 and 1 are the media descriptor and the end-of-chain marker,
        # not clusters, and a volume whose table has been wiped holds zero in
        # both. Read as clusters they would be reported free at offsets that
        # land two clusters before the data area, which is inside the table
        # itself, so a carve would scan the allocation table as free space.
        _wiped = bytearray(_fatbuf)
        struct.pack_into("<I", _wiped, _fat_at, 0)
        struct.pack_into("<I", _wiped, _fat_at + 4, 0)
        _wiped_runs = Fat32Walker(io.BytesIO(bytes(_wiped)), 0).free_extents()
        fat_reserved_ok = bool(_wiped_runs) and all(at >= _fat_data
                                                    for at, _n in _wiped_runs)

        # exFAT does not use its FAT for this. It keeps an allocation bitmap and
        # names it with a 0x81 entry in the root directory, so the entry has to
        # be found before a bit can be read. Same shape of volume, built by hand.
        EX_BPS_SHIFT, EX_SPC_SHIFT = 9, 0            # 512 byte clusters
        # 38, not a multiple of eight, so the bitmap's last byte carries two
        # padding bits. They are zero, and a reader that trusts the bitmap's
        # length instead of the volume's cluster count reports them as two free
        # clusters sitting past the end of the heap.
        EX_CLUSTERS = 38
        EX_HEAP_SECTOR = 8
        EX_BITMAP_CLUS, EX_ROOT_CLUS = 2, 3
        EX_USED = {2, 3, 4, 11, 22, 23, 24, 25}      # bitmap, root, and files
        # by hand from that set, over clusters 2 to 39: free runs are 5..10,
        # 12..21, 26..39
        EX_WANT = [(5, 6), (12, 10), (26, 14)]
        _exbuf = bytearray((EX_HEAP_SECTOR + EX_CLUSTERS + 2) * 512)
        _exbuf[3:11] = b"EXFAT   "
        struct.pack_into("<I", _exbuf, 80, 4)        # FatOffset, sector 4
        struct.pack_into("<I", _exbuf, 88, EX_HEAP_SECTOR)
        struct.pack_into("<I", _exbuf, 92, EX_CLUSTERS)
        struct.pack_into("<I", _exbuf, 96, EX_ROOT_CLUS)
        _exbuf[108] = EX_BPS_SHIFT
        _exbuf[109] = EX_SPC_SHIFT
        _exbuf[510:512] = b"\x55\xaa"
        _ex_heap = EX_HEAP_SECTOR * 512
        _ex_root = _ex_heap + (EX_ROOT_CLUS - 2) * 512
        # A TexFAT volume carries two bitmaps and the first entry in the root can
        # be the second of them, flagged in BitmapFlags bit 0. It describes the
        # other allocation, so a reader that takes the first 0x81 it meets reads
        # the wrong one. This one points at a cluster holding all-ones.
        _exbuf[_ex_root] = 0x81
        _exbuf[_ex_root + 1] = 0x01                               # the second bitmap
        struct.pack_into("<I", _exbuf, _ex_root + 20, EX_CLUSTERS + 1)
        struct.pack_into("<Q", _exbuf, _ex_root + 24, (EX_CLUSTERS + 7) // 8)
        _ex_decoy = _ex_heap + (EX_CLUSTERS + 1 - 2) * 512
        for _b in range((EX_CLUSTERS + 7) // 8):
            _exbuf[_ex_decoy + _b] = 0xFF
        _ex_root += 32                                            # the real one next
        _exbuf[_ex_root] = 0x81                                   # allocation bitmap
        struct.pack_into("<I", _exbuf, _ex_root + 20, EX_BITMAP_CLUS)
        struct.pack_into("<Q", _exbuf, _ex_root + 24, (EX_CLUSTERS + 7) // 8)
        _ex_bits = _ex_heap + (EX_BITMAP_CLUS - 2) * 512
        for _c in EX_USED:
            _exbuf[_ex_bits + ((_c - 2) >> 3)] |= 1 << ((_c - 2) & 7)
        _exw = ExfatWalker(io.BytesIO(bytes(_exbuf)), 0)
        exfat_free_ok = (_exw.free_extents()
                         == [(_ex_heap + (c - 2) * 512, n * 512) for c, n in EX_WANT])
        # a volume whose root names no bitmap must say nothing, not say nothing is free
        _nobm = bytearray(_exbuf)
        _nobm[_ex_root] = 0x85                       # an ordinary file entry instead
        _nobm[_ex_root - 32] = 0x85                  # and the TexFAT one with it
        exfat_no_bitmap_ok = ExfatWalker(io.BytesIO(bytes(_nobm)), 0).free_extents() == []

        # The first segment of a split acquisition holds the boot sector and
        # stops. Both FAT readers follow a chain by reading four bytes per
        # cluster, and past the end of the file that read comes back short, so
        # each must answer rather than raise.
        # collect() carries the readings only when asked, and its own result is
        # unchanged either way, because four other call sites read that tuple.
        _times = {}
        _with = collect(_fatw, _fatw.root, times=_times)
        _without = collect(_fatw, _fatw.root)
        # neither entry carries a creation time or an access date, and a reading
        # the entry does not hold must be absent rather than present and empty
        collect_times_ok = (_times.get("HELLO.TXT", {}).get("modified") == FAT_ENTRY_WRITTEN
                            and _times.get("SUB/DEEP.TXT", {}).get("modified") == FAT_DEEP_WRITTEN
                            and set(_times.get("HELLO.TXT", {})) == {"modified"}
                            and _with == _without
                            and all(len(e) == 4 for e in _with)
                            and len(_with) == 2)

        # Cut each image so the read of the next FAT entry falls off the end.
        try:
            _cut_fat = Fat32Walker(io.BytesIO(bytes(_fatbuf)[:_fat_at + 8]), 0)
            _cut_ex = ExfatWalker(io.BytesIO(bytes(_exbuf)[:1024]), 0)
            fat_truncated_ok = (list(_cut_fat._chain(2)) == [2]      # pylint: disable=protected-access
                                and _cut_ex.free_extents() == []
                                and isinstance(_cut_fat.free_extents(), list))
        except Exception:                            # pylint: disable=broad-except
            fat_truncated_ok = False

        # FAT keeps a wall-clock reading and no zone. The expected strings are
        # written out here rather than built from the same packing the code
        # uses, so the test cannot agree with the decoder by construction.
        stamp_ok = (_dos_stamp((2023 - 1980) << 9 | (6 << 5) | 1, (12 << 11) | (30 << 5) | 15)
                    == "2023-06-01 12:30:30"
                    and _dos_stamp((1980 - 1980) << 9 | (1 << 5) | 1, 0) == "1980-01-01 00:00:00"
                    and _dos_stamp(0, 0) == ""
                    and _dos_stamp((2024 - 1980) << 9 | (2 << 5) | 29,
                                   (23 << 11) | (59 << 5) | 29, 199)
                    == "2024-02-29 23:59:59.99")
        stamp_date_ok = (_dos_date((2021 - 1980) << 9 | (5 << 5) | 5) == "2021-05-05"
                         and _dos_date(0) == "")
        # month 0 and day 0 are what an unwritten or damaged entry holds
        stamp_junk_ok = (_dos_stamp((2023 - 1980) << 9, 0) == ""
                         and _dos_stamp((2023 - 1980) << 9 | (13 << 5) | 1, 0) == ""
                         and _dos_date((2023 - 1980) << 9 | (1 << 5)) == "")
        # 0x80 says the field was written, the low seven bits are signed steps
        # of fifteen minutes: +4 is 16 steps, -5 is 108 as two's complement
        offset_ok = (_exfat_offset(0x80 | 16) == "+04:00"
                     and _exfat_offset(0x80 | 108) == "-05:00"
                     and _exfat_offset(0x80) == "+00:00"
                     and _exfat_offset(0x00) == ""
                     and _exfat_offset(0x10) == "")

        for label, cond in (
                ("an NTFS boot sector is identified by its own geometry",
                 bool(ntfs_named) and ntfs_named[0] == "ntfs"),
                ("an NTFS boot sector is not read as a partition table",
                 ntfs_declined_by_mbr),
                ("a boot sector naming NTFS with impossible geometry is refused",
                 ntfs_refused),
                ("a run list decodes, including a run that steps backwards and "
                 "a sparse one", runs_ok),
                ("an LZNT1 chunk inflates to the bytes it was made from", lz_ok),
                ("a record's sector fixups are applied, and a torn one is "
                 "refused", fixup_ok),
                ("an index entry naming a record of a different generation is "
                 "not followed", stale_ok),
                ("the cluster bitmap reads back as the runs of free space it "
                 "describes", free_ok),
                ("a free-space floor drops the runs too short to be worth "
                 "carving", free_floor_ok),
                ("a FAT32 volume reads its free clusters out of the allocation "
                 "table", fat_free_ok),
                ("a FAT32 free-space floor drops the short runs", fat_floor_ok),
                ("the two reserved FAT entries are not reported as free space "
                 "inside the allocation table", fat_reserved_ok),
                ("an exFAT volume finds its allocation bitmap and reads the free "
                 "clusters out of it", exfat_free_ok),
                ("an exFAT volume whose root names no bitmap reports nothing "
                 "rather than nothing free", exfat_no_bitmap_ok),
                ("a FAT or exFAT volume cut short by a split acquisition answers "
                 "rather than raising", fat_truncated_ok),
                ("a FAT date and time decode to the reading they store, with no "
                 "zone put on them", stamp_ok),
                ("a FAT last-access date is given as a date, not as midnight",
                 stamp_date_ok),
                ("an impossible FAT date is reported as nothing rather than as "
                 "a wrong reading", stamp_junk_ok),
                ("an exFAT UTC offset decodes both ways from its stored steps, "
                 "and an unset one says nothing", offset_ok),
                ("collect carries the recorded readings when asked, and returns "
                 "the same tuples either way", collect_times_ok)):
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

        # ext: sparse files and the classic block map. Both fixtures were built
        # from one tree with mke2fs -d, so one hash list serves both, and it was
        # written by sha256sum over that tree, not by any reader of the image.
        ext_want = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "tests", "fixtures", "ext-sparse.sha256")
        for stem, want_kind in (("ext4-sparse", "ext4"), ("ext2-sparse", "ext2")):
            ext_fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "tests", "fixtures", stem + ".img.gz")
            if not (os.path.isfile(ext_fix) and os.path.isfile(ext_want)):
                print(f"  [SKIP] the {stem} fixture is not beside this script, so the "
                      "walk was not compared against it")
                continue
            try:
                ekind, egot, ewant, emiss, ediff = _ext_fixture_check(ext_fix, ext_want)
                ebroke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                ekind, egot, ewant, emiss, ediff = None, 0, 0, 0, 0
                ebroke = f"; the walk raised {type(exc).__name__}: {exc}"
            econd = (ekind == want_kind and egot and egot == ewant and not emiss
                     and not ediff and not ebroke)
            if not econd:
                ok = False
            print(f"  [{'PASS' if econd else 'FAIL'}] every file of the {stem} fixture, "
                  f"holes included, matches what sha256sum recorded over its source tree "
                  f"({egot} of {ewant}, identified as {ekind}"
                  + (f", {emiss} missing" if emiss else "")
                  + (f", {ediff} different" if ediff else "") + ")" + ebroke)

        ntfs_fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "tests", "fixtures", "ntfs-fixture.img.gz")
        ntfs_want = ntfs_fix[:-len(".img.gz")] + ".sha256"
        if os.path.isfile(ntfs_fix) and os.path.isfile(ntfs_want):
            try:
                got, want, missing, differ = _ntfs_fixture_check(ntfs_fix, ntfs_want)
                broke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                # A reader that raises on a volume it cannot parse must fail this
                # check, not take the whole self-test down with it: a run that
                # stops early prints no FAIL line and reads as a pass.
                got = want = missing = differ = 0
                broke = f"; the walk raised {type(exc).__name__}: {exc}"
            cond = got and not missing and not differ and not broke
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] every file of the NTFS "
                  f"fixture matches what an independent reader recorded "
                  f"({got} of {want}"
                  + (f", {missing} missing" if missing else "")
                  + (f", {differ} different" if differ else "") + ")" + broke)
        else:
            # Said plainly rather than silently: a check that did not run is not
            # a check that passed. The frozen executable carries no fixtures.
            print("  [SKIP] the NTFS fixture is not beside this script, so the "
                  "walk was not compared against it")

        ntfs_del = ntfs_fix[:-len(".img.gz")] + ".deleted.sha256"
        if os.path.isfile(ntfs_fix) and os.path.isfile(ntfs_del):
            try:
                dgot, dwant, dmiss, ddiff = _ntfs_deleted_check(ntfs_fix, ntfs_del)
                dbroke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                dgot = dwant = dmiss = ddiff = 0
                dbroke = f"; the sweep raised {type(exc).__name__}: {exc}"
            dcond = dgot and dgot == dwant and not dmiss and not ddiff and not dbroke
            if not dcond:
                ok = False
            print(f"  [{'PASS' if dcond else 'FAIL'}] deleted files recovered "
                  f"from the MFT match the bytes written before deletion "
                  f"({dgot} of {dwant}"
                  + (f", {dmiss} missing" if dmiss else "")
                  + (f", {ddiff} different" if ddiff else "") + ")" + dbroke)
        elif os.path.isfile(ntfs_fix):
            print("  [SKIP] the NTFS deleted-files listing is not beside this "
                  "script, so recovery was not compared against it")

        if os.path.isfile(ntfs_fix):
            try:
                tfail, tchecked = _ntfs_times_check(ntfs_fix)
            except Exception as exc:                 # pylint: disable=broad-except
                tfail, tchecked = [f"the check raised {type(exc).__name__}: {exc}"], 0
            tcond = tchecked and not tfail
            if not tcond:
                ok = False
            print(f"  [{'PASS' if tcond else 'FAIL'}] created, modified and accessed of "
                  f"live and deleted NTFS files match what istat recorded "
                  f"({tchecked} live files checked"
                  + (f"; {tfail[0]}" if tfail else "") + ")")

        for label, stem, wcls in (("FAT32", "fat32-deleted", Fat32Walker),
                                  ("exFAT", "exfat-deleted", ExfatWalker)):
            fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "tests", "fixtures", stem + ".img.gz")
            lst = fix[:-len(".img.gz")] + ".deleted.sha256"
            if not (os.path.isfile(fix) and os.path.isfile(lst)):
                print(f"  [SKIP] the {label} deleted-files fixture is not beside this "
                      "script, so recovery was not compared against it")
                continue
            try:
                fgot, fwant, fmiss, fdiff = _fat_deleted_check(fix, lst, wcls)
                fbroke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                fgot = fwant = fmiss = fdiff = 0
                fbroke = f"; the sweep raised {type(exc).__name__}: {exc}"
            fcond = fgot and fgot == fwant and not fmiss and not fdiff and not fbroke
            if not fcond:
                ok = False
            print(f"  [{'PASS' if fcond else 'FAIL'}] deleted files recovered from the "
                  f"{label} directory entries match the bytes written before deletion "
                  f"({fgot} of {fwant}"
                  + (f", {fmiss} missing" if fmiss else "")
                  + (f", {fdiff} different" if fdiff else "") + ")" + fbroke)

        for label, stem, wcls in (("FAT32", "fat32-deleted", Fat32Walker),
                                  ("exFAT", "exfat-deleted", ExfatWalker)):
            fix = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "tests", "fixtures", stem + ".img.gz")
            if not os.path.isfile(fix):
                print(f"  [SKIP] the {label} fixture is not beside this script, so "
                      "its listing was not checked")
                continue
            try:
                lok, ldetail = _fat_listing_check(fix, wcls)
            except Exception as exc:                 # pylint: disable=broad-except
                lok, ldetail = False, f"the check raised {type(exc).__name__}: {exc}"
            if not lok:
                ok = False
            print(f"  [{'PASS' if lok else 'FAIL'}] a {label} listing prints each file's "
                  f"modified reading as stored and never 1970-01-01 ({ldetail})")
        if os.path.isfile(ntfs_fix):
            try:
                nok, ndetail = _ntfs_listing_check(ntfs_fix)
            except Exception as exc:                 # pylint: disable=broad-except
                nok, ndetail = False, f"the check raised {type(exc).__name__}: {exc}"
            if not nok:
                ok = False
            print(f"  [{'PASS' if nok else 'FAIL'}] an NTFS listing still prints an "
                  f"instant's date ({ndetail})")

        # volumes(): the callable form of the report's discovery. The names and
        # kinds below are written out, not read back from volume_name() or from
        # main(), so a wrong region, a wrong kind or a missing walker each fails.
        def _vol_view(path):
            with open(path, "rb") as fh:
                return [(v["kind"], v["name"], "walker" in v, v["missing_past_end"])
                        for v in volumes(fh, os.path.getsize(path))]
        vol_checks = (
            ("volumes() names the qnx6 behind an MBR by its partition and LBA",
             a, [("qnx6", "p1_lba2048", True, 0)]),
            ("volumes() names a whole-image big-endian qnx6 lba0",
             b, [("qnx6", "lba0", True, 0)]),
            ("volumes() reports an unrecognised image as one region without a walker",
             c, [("not recognised", "lba0", False, 0)]),
            ("volumes() recognises a synthetic FAT32 boot sector",
             fp, [("fat32", "lba0", True, 0)]),
            ("volumes() recognises a synthetic exFAT boot sector",
             xp, [("exfat", "lba0", True, 0)]),
        )
        for label, path, want in vol_checks:
            try:
                got = _vol_view(path)
                vbroke = ""
            except Exception as exc:                 # pylint: disable=broad-except
                got, vbroke = None, f"; raised {type(exc).__name__}: {exc}"
            cond = got == want and not vbroke
            if not cond:
                ok = False
            print(f"  [{'PASS' if cond else 'FAIL'}] {label}"
                  + ("" if cond else f"  (got {got}{vbroke})"))
        # A region the file does not hold in full reports how much is missing:
        # the first segment of a split image has exactly this shape.
        try:
            with open(cut, "rb") as fh:
                cut_vols = volumes(fh, os.path.getsize(cut))
            cut_cond = (len(cut_vols) == 1 and cut_vols[0]["kind"] == "qnx6"
                        and cut_vols[0]["missing_past_end"] > 0)
            cut_detail = (f"{cut_vols[0]['missing_past_end']:,} bytes past the end"
                          if cut_vols else "no volume found")
        except Exception as exc:                     # pylint: disable=broad-except
            cut_cond, cut_detail = False, f"raised {type(exc).__name__}: {exc}"
        if not cut_cond:
            ok = False
        print(f"  [{'PASS' if cut_cond else 'FAIL'}] volumes() reports a volume the "
              f"image is too short for as missing bytes ({cut_detail})")

        print()
        print("  SELF-TEST PASSED. The detector reports positives and negatives"
              if ok else
              "  SELF-TEST FAILED. Do not trust results from this build.")
        return 0 if ok else 1
    finally:
        shutil.rmtree(d, ignore_errors=True)


EPILOG = """\
examples:
  # one image
  qnxprobe.py Dodge.img

  # several at once
  qnxprobe.py *.img *.bin

  # a single partition already carved out
  qnxprobe.py partition2.dd

  # prove the detector works before you trust a negative result
  qnxprobe.py --self-test

  # widen the fallback brute scan for an image with an odd layout
  qnxprobe.py --scan-limit 2048 mmcblk0.img

  # list what is inside every filesystem it finds
  qnxprobe.py --list mmcblk0.img

  # copy the logical files out into a zip, ready for a LEAPP tool
  qnxprobe.py --extract sync_g4.zip mmcblk0.img

  # a split acquisition: name any one segment, the set beside it is joined
  qnxprobe.py --extract sync_g4.zip mmcblk0.img.001

  # just one partition, by name or label
  qnxprobe.py --extract storage.zip --only storage mmcblk0.img

  # go deeper, and raise the per-filesystem entry cap
  qnxprobe.py --list --depth 4 --list-max 3000 mmcblk0.img

deciding what to pull first:
  --triage ranks every volume it found by how much each has been written, and
  flags the ones that are not worth your time. It uses only what the probe
  already read: the qnx6 superblock serial is a commit counter, and ext
  exposes mount count and lifetime kilobytes written.

  It also samples filenames and says so when they are encrypted, because a
  volume whose names are encrypted will not yield to any parser without the
  keys. Measured on a 2024 BMW MGU: the busiest volume on the disk, /var/opt,
  is 36% encrypted names in a sample.

  Read the fill percentage alongside the ranking rather than sorting on size.
  On a Ford Sync G4 the 4 MiB manufacturing volume, last in the ranking with
  16 commits, is the one holding the unit's Bluetooth and WiFi addresses,
  serials and TLS keys. Activity finds the user data; it does not measure
  value per byte.

getting the files out, without mounting:
  --extract writes every regular file from every filesystem it identified into
  a zip, which is the shape a LEAPP tool expects. Directories are implied by
  the paths; symlinks and special files are counted and skipped. Entries are
  stamped with the file's own mtime, clamped to 1980 where the stored time
  predates what the zip format can hold.

  This exists because mounting is a Linux-only answer. macOS ships no qnx6
  driver, the WSL2 kernel is built with CONFIG_QNX6FS_FS unset, and the FUSE
  options are Linux-tested. --extract is standard library only, so it behaves
  the same on macOS, Windows and Linux, needs no administrator rights, no loop
  device and no virtual machine, and cannot write to the evidence.

  --only restricts --list and --extract to partitions whose name or label
  contains the text given, which matters because a whole head unit can run to
  tens of gigabytes.

  It refuses to overwrite an existing output file.

listing contents:
  --list walks each filesystem it identified and prints the tree. It handles
  qnx6, QNX4, ext2/3/4, FAT32, exFAT, NTFS, HFS+, APFS, the QNX flash
  filesystems ETFS and EFS, and QNX IFS boot images, follows qnx6 long filenames
  and ext4 extent trees, and reads only. --depth sets how far down it goes and
  --list-max caps the number of entries per filesystem so a large volume cannot
  flood the terminal. An NTFS or APFS listing also names anything held in a
  stream beside the file, and an HFS+ one names a resource fork that carries
  anything. An APFS container is listed as a directory of its volumes, so every
  volume in it is walked.

what it reports:
  Every superblock copy it can find, grouped into generations by serial. The
  highest serial is the active one; the generation below it is the previous
  committed state, still on disk. It then diffs the two, so you can see what
  one commit actually changed.

  Measured on a Ford Sync G4 image, a qnx6 filesystem carries FOUR copies, not
  two: the 0x1000 area reserved at 0x2000 holds slots at +0x2000 and +0x2e00,
  and a second reserved area near the end of the volume mirrors both. So the
  previous committed state is usually recoverable.

  A copy whose volume id, blocksize and block count match an already-confirmed
  superblock in the same partition is accepted as another copy of that
  filesystem even if its timestamps look wrong, and the run says how many were
  accepted that way. Recorded identity is a stronger signal than a date: on the
  Sync G4 image the previous generation of dps_os carries ctime 308 and atime 1,
  both unset because the build host had no clock, and a timestamp test alone
  rejects a genuine superblock.

  Time differences between generations are printed in whole units, seconds
  through years. Where one side is an unset placeholder rather than a date the
  difference is NOT a duration, and it is reported as the change it is instead
  of a meaningless span of years.

  After the qnx6 volumes it reports WHAT IS IN THE OTHER PARTITIONS, because a
  partition type byte is a label and not a fact. ext2, ext3 and ext4 are read
  in full: label, last mount point, UUID, creation and mount and write times,
  mount count, usage, lifetime bytes written, and whether the volume was
  cleanly unmounted. QNX IFS boot images report their startup header (version,
  target machine, startup code size, compression method), then the image
  filesystem is decompressed and listed and extracted like any other, with the
  image checksum reported as a decode self-check. The QNX flash filesystems
  ETFS and EFS are recognised too, and listed and extracted in full, and so is
  QNX4, the filesystem of QNX 4 systems, which the MBR type bytes 0x4d/0x4e/
  0x4f announce but never prove. Anything
  else is reported as its leading bytes plus any ASCII magic,
  so there is a lead to follow rather than a guess. On a 2024 BMW
  MGU image that turned twelve partitions all marked 0x83 "Linux" into ten
  ext4 volumes, one extended container, and one holding an ipk container with
  a Linux bzImage inside it.

  ETFS and EFS are usually imaged bare, with no partition table, so they arrive
  as the whole image and extract under the lba0 name. ETFS has no superblock, so
  its live state is rebuilt by replaying the transaction records in the spare
  area of every page, keeping the highest sequence number for each block; its
  extraction also carries the internal .filetable, .badblks, .counts and
  .reserved bookkeeping files, which are real entries in the filesystem. EFS is
  found by its QSSL_F3S boot record and walked through its extent chains, each
  file resolved to its current version through the superseding-extent pointers.

  sb_ctime is written once, when the filesystem is made. sb_atime moves when
  the filesystem is COMMITTED, not when a file is read, so do not report it as
  when a person last used the device. serial counts commits and is the better
  measure of how much a volume has been written. Measured across three volumes
  of a Ford Sync G4 image: 15 commits on manufacturing data, 1,713 on the OS,
  411,711 on user storage.

  The field names sb_ctime and sb_atime come from comments in the Linux
  header. QNX does not publish the on-disk superblock layout, so treat the
  names as labels and report what moved rather than what someone did.

what it checks, and where the constants come from:
  QNX6_SUPER_MAGIC   0x68191122   linux/include/uapi/linux/magic.h:55
  QNX6_BOOTBLOCK_SIZE    0x2000   linux/include/linux/qnx6_fs.h:23
  struct qnx6_super_block          linux/include/linux/qnx6_fs.h:94

  fs/qnx6/inode.c reads superblock #1 at +0x2000 from the start of the
  partition and retries at +0 if the magic is wrong. Little endian is tried
  first, then big endian. This tool does the same, for the whole image, for
  every MBR primary, every logical volume in the extended chain, and every
  GPT partition.

  A bare 4-byte magic match is not a finding: expect roughly one by chance
  per 256 MiB scanned. Every candidate is parsed as a superblock and its
  fields checked for consistency before it is reported CONFIRMED.

  For the ext side:
  EXT2_SUPER_MAGIC       0xEF53   linux/include/uapi/linux/magic.h:24
  struct ext4_super_block         linux/fs/ext4/ext4.h
  struct ext4_group_desc          linux/fs/ext4/ext4.h
  struct ext4_inode               linux/fs/ext4/ext4.h
  struct ext4_dir_entry_2         linux/fs/ext4/ext4.h
  EXT4_EXT_MAGIC         0xf30a   linux/fs/ext4/ext4_extents.h

  The ext field offsets were derived from that header and cross-checked
  against its own /*NN*/ offset markers, all fifteen of which agreed, with the
  struct totalling the expected 1024 bytes.

  For QNX IFS boot images:
  STARTUP_HDR_SIGNATURE  0x00ff7eeb   qnx sys/startup.h:88
  STARTUP_HDR_VERSION             1   qnx sys/startup.h:89
  struct startup_header               qnx sys/startup.h, and QNX's own
                                      "The startup header" documentation page,
                                      which lists the same fields in the same
                                      order

  Those field widths sum to 256 bytes, which each image's own header_size
  field confirms. The machine field is documented as an ELF machine type and
  is reported through EM_386 3, EM_ARM 40, EM_X86_64 62 and EM_AARCH64 183
  from linux/include/uapi/linux/elf-em.h. The image filesystem begins at
  startup_size, and stored_size minus startup_size against imagefs_size says
  whether it is stored compressed.

  The image filesystem and its compression come from QNX's own dumpifs and
  sys/image.h. startup_header flags1 carries the method (none, zlib, lzo or
  ucl). A compressed imagefs is a run of blocks, each a 2-byte big-endian
  compressed length then that many bytes, decompressing to at most 64 KiB and
  ending at a zero length. Each ucl block is UCL NRV2B, the _8 variant dumpifs
  links as ucl_nrv2b_decompress_8; it is carried here as a small pure-Python
  decoder ported from Markus Oberhumer's UCL (src/n2b_d.c, src/getbit.h), so
  nothing has to be installed. The decompressed image is walked from its
  image_header and a flat table of image_dirent records: each carries an inode,
  mode, mtime and a full path, and a file points at an offset and size inside
  the image. zlib images are read through the standard library.

  This is proven byte for byte against the Ford Sync G4 ifs_a, ifs_b and
  ifs_recovery volumes. Each decompressed to exactly the imagefs_size its own
  header records, the 32-bit words from the header through the image_trailer
  summed to zero (the trailer holds a checksum), and the extracted files were
  valid, including the AArch64 ELF kernel whose machine matched the startup
  header. That checksum is printed on every run as a decode self-check.

  lzo-compressed images and the Harman Becker HBCIFS container are recognised
  but not read here, since no sample exists to validate a reader against, and a
  big-endian image is declined the same way. In each case the header is still
  reported and the walk is declined out loud. Nothing is invented.

  For the QNX flash filesystems ETFS and EFS:
  struct etfs_trans, the fid scheme, ftable and directory entry layouts, and
  the F3S extent, unit and boot structures are transcribed from the Kaitai
  .ksy specs in NetherlandsForensicInstitute/qnxmount (Apache-2.0), whose ETFS
  spec cross-references QNX's own fs/etfs.h and whose EFS spec fs/f3s_spec.h.
  The Kaitai runtime is not a dependency; only the field layouts are copied,
  into the same hand-written struct style as everything above, so this stays
  standard library only. Both readers were validated by extracting qnxmount's
  own committed test images and comparing every name, mode, owner, timestamp,
  symlink target and byte of file content against the tar archive built from
  the same live filesystem, which qnxmount produced on QNX independently of
  this implementation: ETFS matched 32 of 32 entries and EFS 31 of 31.

  ETFS has no magic number. It is claimed only when the region divides evenly
  into (page + 16)-byte pages AND its .filetable carries the fixed reserved
  names .filetable/.badblks/.counts/.lost+found/.reserved at their fixed file
  ids, so a chance page-count match cannot pass. EFS is claimed by its
  QSSL_F3S boot record with a valid F3S revision. Neither fired on the u-boot,
  boot_fs or ext partitions of the two vehicle images tested.

  For QNX4, the filesystem of QNX 4 (distinct from qnx6):
  QNX4_SUPER_MAGIC       0x002f   linux/include/uapi/linux/magic.h:54
  struct qnx4_inode_entry         linux/include/uapi/linux/qnx4_fs.h:44
  struct qnx4_link_info           linux/include/uapi/linux/qnx4_fs.h:63
  struct qnx4_xblk ("IamXblk")    linux/include/uapi/linux/qnx4_fs.h:71
  field widths                    linux/include/uapi/linux/qnxtypes.h
  directory entry union           linux/fs/qnx4/qnx4.h:75

  The 0x002f magic is simply the "/" name of the root directory inode at the
  start of the superblock, which is block 1, 512 bytes into the volume. The
  walk follows the kernel's own read-only driver: inline 64-byte inode
  entries for names up to 16 bytes, link entries resolving longer names
  (up to 48) through the .inodes file, and extents 2..n of a file through
  the "IamXblk" chain that fs/qnx4/inode.c qnx4_block_map() follows.
  Detection requires what the kernel itself requires to mount: the "/" root
  inode with a directory mode, and a ".bitmap" entry in the root directory
  (fs/qnx4/inode.c qnx4_checkroot). A QNX4 boot block can end in 0x55AA, so
  the MBR parser declines a sector whose following sector is a QNX4 root
  superblock, the same shared-magic rule applied to FAT above.

  The QNX4 reader was validated by round-trip against the Linux kernel
  driver itself: a fixture populated with nested directories, a multi-extent
  file, a name over 16 bytes, a symlink, an empty file and distinct modes,
  owners and mtimes was mounted read-only with fs/qnx4 on kernel 7.0.0, and
  every path, type, permission, owner, size, mtime, symlink target and byte
  of file content the kernel reported matched what this walker reads, 15 of
  15 entries. The fixture was written by a separate generator program, not
  by this parser, so the two sides are independent. Synthetic-only
  validation: no confirmed real QNX4 volume exists in the test corpus, and
  the one candidate partition (a Ford Sync G4 slot named boot_fs) turned out
  to carry a RAW0 container, not QNX4.

  --list walks qnx6 through the same block resolution the kernel uses in
  qnx6_block_map(), including multi-level indirect trees and long filenames
  held out of line in the Longfile tree, and walks ext through its extent
  trees. Both are read-only.

note:
  The image is opened read-only and is never written to. The Linux qnx6 driver
  has no write path at all, so mounting a qnx6 volume on Linux cannot alter
  these timestamps either.
"""


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        prog="qnxprobe.py",
        description="Read QNX6, QNX4, ETFS, EFS, ext2/3/4, FAT32, exFAT, NTFS, HFS+ and APFS "
                    "filesystems, and QNX IFS boot images, out of raw disk "
                    "images: identify each by its own on-disk structure rather "
                    "than trusting a partition type byte, list, and extract to a "
                    "zip with a provenance manifest. No mounting, no admin "
                    "rights, standard library only.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="*",
                    help="disk image, partition image, or raw dump to examine")
    ap.add_argument("--scan-limit", type=int, default=256, metavar="MiB",
                    help="how far to brute scan when no superblock sits at the "
                         "offsets the kernel checks (default: 256)")
    ap.add_argument("--self-test", action="store_true",
                    help="build throwaway positive and negative images, confirm "
                         "the detector reports both ways, then delete them")
    ap.add_argument("--list", action="store_true",
                    help="walk each filesystem found and list its contents "
                         "(qnx6, qnx4, ext2/3/4, FAT32, exFAT, NTFS, HFS+, APFS, ETFS and EFS)")
    ap.add_argument("--depth", type=int, default=2, metavar="N",
                    help="how deep to walk with --list (default: 2)")
    ap.add_argument("--list-max", type=int, default=400, metavar="N",
                    help="stop after this many entries per filesystem (default: 400)")
    ap.add_argument("--extract", metavar="OUT.zip",
                    help="copy the logical files out of every filesystem found "
                         "into a zip, ready for a LEAPP tool. No mounting, no "
                         "administrator rights, same on macOS, Windows and Linux")
    ap.add_argument("--exclude", metavar="TEXT", action="append",
                    help="skip any path containing TEXT when extracting. "
                         "Repeatable. Use it to leave out encrypted subtrees "
                         "and bulk payloads that no parser can read")
    ap.add_argument("--only", metavar="TEXT",
                    help="restrict --list and --extract to partitions whose "
                         "name or label contains TEXT")
    ap.add_argument("--triage", action="store_true",
                    help="rank the volumes found by how much each has been "
                         "written, and flag encrypted or bulk ones, so you know "
                         "what to extract first")
    ap.add_argument("--progress", action="store_true",
                    help="while extracting, emit one JSON progress object per line on "
                         "stderr, for a caller driving this as a subprocess. stdout, "
                         "the human readable report, is unchanged")
    ap.add_argument("--version", action="version",
                    version=f"qnxprobe {QNXPROBE_VERSION}")
    args = ap.parse_args()

    if args.self_test:
        print("\nqnxprobe self-test\n")
        sys.exit(self_test())

    if not args.image:
        ap.print_help()
        sys.exit(2)

    missing = [p for p in args.image if not os.path.exists(p)]
    if missing:
        sys.exit("not found: " + ", ".join(missing))

    reporter = ProgressEmitter() if args.progress else None
    manifest = []
    zf = None
    if args.extract:
        if os.path.exists(args.extract):
            sys.exit(f"refusing to overwrite an existing file: {args.extract}")
        zf = zipfile.ZipFile(args.extract, "w", zipfile.ZIP_DEFLATED,
                             allowZip64=True)
    refused = []
    try:
        for p in args.image:
            try:
                main(p, scan_limit_mib=args.scan_limit, do_list=args.list,
                     list_depth=args.depth, list_max=args.list_max,
                     extract=args.extract, only=args.only, zf=zf,
                     do_triage=args.triage, exclude=args.exclude,
                     reporter=reporter, manifest=manifest)
            except (SplitImageError, ImageUnreadable) as exc:
                # a segment set that is not whole, or an image this tool cannot open: said out loud and left
                # unread, never joined around, and the exit status says so
                print("=" * 78)
                print(p)
                print(f"  REFUSED: {exc}")
                print("=" * 78)
                refused.append(p)
    finally:
        if zf is not None:
            # The provenance record. For a standalone image the directory names
            # are otherwise the only statement of where a file came from; this
            # ties every volume back to the image by LBA and recorded volume id,
            # so the extraction can be checked against any partition tool
            # without trusting the names.
            if manifest:
                zf.writestr("volumes.json", json.dumps(
                    {"written_by": f"qnxprobe {QNXPROBE_VERSION}",
                     "volumes": manifest}, indent=2) + "\n")
            zf.close()
            print(f"\nwrote {args.extract}  "
                  f"({os.path.getsize(args.extract):,} bytes)")
    if refused:
        sys.exit(1)
