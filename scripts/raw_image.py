"""Raw disk image and E01 acquisition input: the seeker behind ``-t raw``.

A raw image (``.img``, ``.dd``, ``.bin``, a numbered ``.001`` segment of a split
set) or an EnCase/EWF acquisition (``.E01`` and its segments) is read in place,
without mounting and without administrator rights, through the reader vendored
in ``scripts/vendor/`` (qnxprobe, with ewfprobe beside it for EWF). The reader
finds the partitions, identifies each volume by its own on-disk structure and
walks its directory tree; this module turns that into the same contract the zip
seeker offers: a list of member names to match artifact patterns against, and a
copy of each matched file staged under the report's data folder.

Only matched files are ever read. The volumes are walked for their names when
the seeker is built, and a file's bytes leave the image only when an artifact's
pattern selects it, so a few hundred files come out of a 250 GiB acquisition
without the rest being touched. Measured before this was written: whole-disk
staging of a 238.5 GiB Windows acquisition would have written 103 GiB of live
files to a temporary folder to satisfy patterns that select 694 MiB.

Every member is named ``<volume>/<path>``, the volume being the directory name
the reader's own extraction uses (``p3_lba239616_basic_data_partition``,
``lba0``): the partition's LBA is the identity, so two volumes cannot collide,
and a label rides along as a suffix. Artifact patterns begin with ``*`` and
``*`` crosses ``/`` in fnmatch, so the prefix costs them nothing, and it is what
the report's source path shows for each file.

This file is shared by iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP and is kept
byte-identical across them. It names nothing specific to a platform; the
platform is in the artifacts.
"""

import os
import sys
import time as timex
from fnmatch import _compile_pattern

from scripts.ilapfuncs import logfunc, sanitize_file_path
from scripts.search_files import FileInfo, FileSeekerBase, normcase

# qnxprobe reaches its EWF reader with a bare ``import ewfprobe``, falling back to
# a sys.path insert of its own directory when that fails. Importing the vendored
# copy through the package first and registering it under the bare name makes
# the fallback unnecessary, which matters in a frozen (PyInstaller) build where
# the vendored files are modules of the bundle rather than files on a path.
from scripts.vendor import ewfprobe as _ewfprobe   # noqa: E402  (order matters)
sys.modules.setdefault('ewfprobe', _ewfprobe)
from scripts.vendor import qnxprobe  # noqa: E402

# Extensions conventionally given to a raw disk image, plus the one an
# EnCase/EWF acquisition carries. Everything a raw image run needs is decided by
# reading the image, so this list only has to get the file past type selection
# in the GUI; an image named anything else is still reachable from the command
# line with -t raw. An .E01 is the first segment of its set and the reader joins
# the rest, and so is a .001.
RAW_IMAGE_SUFFIXES = ('img', 'bin', 'dd', 'raw', '001', 'e01')

# What the vendored reader walks, for the file dialog and the -t help. A test
# asserts each entry here has a walker in the vendored copy, so the two cannot
# drift apart quietly.
RAW_IMAGE_FILESYSTEMS = ('QNX6, QNX4, ETFS, EFS, ext2/3/4, FAT32, exFAT, NTFS, '
                         'HFS+, APFS, QNX IFS')
RAW_IMAGE_LABEL = f'Raw disk image or acquisition ({RAW_IMAGE_FILESYSTEMS})'

# A directory this deep in a walk is a loop in the tree, not a directory.
_MAX_DEPTH = 64


def split_image_sibling(image_path):
    """The next segment of a split image, when this file is one segment of it.

    FTK Imager and its peers write a raw image as numbered segments (.001, .002,
    ...) unless told to write one file. The reader joins every segment of the
    set beside the one it is given, so this only decides whether the run log
    says that a set is being read. Returns the path of the next segment, or
    None when the suffix is not a number or no next segment is beside this file.
    """
    stem, dot, suffix = os.path.basename(image_path).rpartition('.')
    if not dot or not stem or not (suffix.isascii() and suffix.isdigit()):
        return None
    following = str(int(suffix) + 1).zfill(len(suffix))
    candidate = os.path.join(os.path.dirname(image_path), f'{stem}.{following}')
    return candidate if os.path.isfile(candidate) else None


def _reading_as_local_instant(reading):
    """A FAT or exFAT wall-clock reading placed in this machine's zone.

    Those filesystems store no zone, so the reader hands their times back as
    text and records no instant. The zip seeker gives a staged copy the mtime
    of the member's DOS stamp through time.mktime, which is the same reading
    read in the same local zone; this does the same for the staged copy's own
    mtime, and nothing more. The FileInfo the run records keeps 0, so no report
    field carries a zone the evidence never had. Returns 0 for an unset or
    malformed reading.
    """
    if not reading:
        return 0
    try:
        parsed = timex.strptime(reading[:19], '%Y-%m-%d %H:%M:%S')
        return timex.mktime(parsed[:8] + (-1,))
    except (ValueError, OverflowError):
        return 0


class _Entry:
    """Where one member lives in the image: enough to read it on demand."""

    __slots__ = ('walker', 'node', 'size', 'mtime', 'reading')

    def __init__(self, walker, node, size, mtime, reading=''):
        self.walker = walker
        self.node = node
        self.size = size
        self.mtime = mtime
        self.reading = reading


class FileSeekerRaw(FileSeekerBase):
    """Search a raw disk image or E01 acquisition and stage the files that match.

    Built the way FileSeekerZip is, and used the same way by the run: ``search``
    matches a pattern against every member name, copies each match under the
    data folder once, records a FileInfo for it and returns the staged paths.
    The differences are where the bytes come from (the vendored reader, on
    demand) and that the member list is built by walking the volumes rather than
    read out of a central directory.

    A member that is a directory is listed with a trailing slash, as a zip's
    directory entries are, so a pattern that names a directory returns one here
    too. Symbolic links and special files are not members: they hold no bytes to
    stage, and the seekers stage bytes.
    """

    def __init__(self, image_path, data_folder):
        FileSeekerBase.__init__(self)
        self.image_path = image_path
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self.name_list = []
        self.volumes = []
        self._entries = {}
        self._image = None
        try:
            self._open()
        except BaseException:
            # A failed or interrupted (Ctrl-C on a slow walk) build never binds an
            # object for the run's cleanup() to reach, so release the image here.
            self.cleanup()
            raise
        self._init_dest_guard(self.data_folder)

    # ---- building the member list -------------------------------------------

    def _open(self):
        name = os.path.basename(self.image_path)
        logfunc(f'Reading {name} in place with the vendored qnxprobe '
                f'{qnxprobe.QNXPROBE_VERSION}; only the files an artifact asks for '
                f'leave the image.')
        sibling = split_image_sibling(self.image_path)
        if sibling:
            logfunc(f'{name} is one segment of a split image: '
                    f'{os.path.basename(sibling)} sits beside it. The reader joins '
                    f'every segment of the set in order.')
        # A set with a hole in its numbering raises SplitImageError here, by
        # name, and the run stops with that message rather than reading half a
        # disk as though it were whole.
        segments = qnxprobe.split_segments(self.image_path)
        self._image = qnxprobe.open_image(self.image_path, segments)
        size = qnxprobe.image_size(self._image)
        parts = list(getattr(self._image, 'paths', []) or [])
        if segments:
            logfunc(f'  {len(segments):,} segments joined in order, '
                    f'{os.path.basename(segments[0])} .. '
                    f'{os.path.basename(segments[-1])}')
        elif len(parts) > 1:
            logfunc(f'  an EWF acquisition of {len(parts):,} segments, joined by the '
                    f'reader: {os.path.basename(parts[0])} .. '
                    f'{os.path.basename(parts[-1])}')
        elif parts:
            logfunc('  an EWF acquisition of one segment')
        logfunc(f'  {size:,} bytes ({qnxprobe.human(size)})')

        self.volumes = qnxprobe.volumes(self._image, size)
        if not self.volumes:
            logfunc('  no partition table and no filesystem the reader knows: '
                    'nothing to search')
        for vol in self.volumes:
            note = vol.get('note')
            line = (f"  {vol['name'] or vol['label']:<40} {vol['kind']:<16} "
                    f"{qnxprobe.human(vol['size'] or 0):>10}")
            if vol['label'] and vol['name']:
                line += f"   {vol['label']}"
            if note:
                line += f'   ({note})'
            logfunc(line)

        # A partition table describes a whole disk and the file may hold only
        # the front of it: a lone first segment of a split image reads this way,
        # its boot volumes whole and the volume holding the user data cut. Say
        # so before any of its files is staged.
        short = [v for v in self.volumes if v.get('missing_past_end')]
        if short:
            logfunc('WARNING: the image is shorter than the volumes it describes. '
                    'Rows from these volumes come from an incomplete read:')
            for vol in short:
                logfunc(f"  {vol['name'] or vol['label']}: reaches "
                        f"{vol['missing_past_end']:,} bytes past the end of the image")
            logfunc('  If this is a numbered segment of a split image, the rest of the '
                    'set is not beside it: the reader joins every segment it finds in '
                    'the same folder.')

        for vol in self.volumes:
            walker = vol.get('walker')
            if walker is None:
                continue
            started = timex.monotonic()
            files, dirs = self._walk(walker, vol['name'])
            logfunc(f"  walked {vol['name']}: {files:,} files, {dirs:,} directories "
                    f"in {timex.monotonic() - started:.1f}s")
        logfunc(f'File listing complete - {len(self.name_list):,} members')

    def _walk(self, walker, prefix):
        """Register every file and directory under a volume's root. Returns counts."""
        files = dirs = 0
        seen = set()
        stack = [(walker.root, prefix, 0)]
        while stack:
            node, path, depth = stack.pop()
            if depth > _MAX_DEPTH or node in seen:
                continue
            seen.add(node)
            try:
                if hasattr(walker, 'listdir_records'):
                    # FAT and exFAT keep wall-clock readings rather than instants;
                    # the reader hands them back as text beside each entry.
                    listing = [(name, child, (recorded or {}).get('modified', ''))
                               for name, child, recorded in walker.listdir_records(node)]
                else:
                    listing = [(name, child, '') for name, child in walker.listdir(node)]
                listing.sort(key=lambda item: item[0])
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logfunc(f'Could not list {path}/ in the image: {exc}')
                continue
            for child_name, child, reading in listing:
                try:
                    ent = walker.entry(child)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logfunc(f'Could not read the entry for {path}/{child_name}: {exc}')
                    continue
                if not ent:
                    continue
                mode, size, mtime = ent
                member = f'{path}/{child_name}'
                if mode & qnxprobe.S_IFDIR:
                    self.name_list.append(member + '/')
                    self._entries[member + '/'] = None
                    dirs += 1
                    stack.append((child, member, depth + 1))
                elif (mode & 0o170000) == 0o100000:          # regular files only
                    self.name_list.append(member)
                    self._entries[member] = _Entry(walker, child, size or 0, mtime or 0, reading)
                    files += 1
        return files, dirs

    # ---- searching and staging ----------------------------------------------

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self.name_list:
            if pat(root + normcase(member)) is None:
                continue
            if member not in self.copied or force:
                try:
                    staged = self._stage(member)
                except OSError as ex:
                    logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                    continue
                if staged is None:
                    continue
                self.copied[member] = staged
            else:
                staged = self.copied[member]
            pathlist.append(staged)
            if return_on_first_hit:
                self.searched[filepattern] = pathlist
                return staged
        self.searched[filepattern] = pathlist
        return pathlist

    def _intended_path(self, member):
        clean_member = sanitize_file_path(member)
        parts = [part for part in clean_member.replace('\\', '/').split('/')
                 if part not in ('', '.', '..')]
        if not parts:
            return self.data_folder
        return os.path.join(self.data_folder, *parts)

    def _stage(self, member):
        """Copy one member out of the image. Returns the staged path, or None.

        None means the member is listed but could not be handed to an artifact:
        the reader refused it (an encrypted NTFS file), it raised part way, or
        the image ends before the file does. Each case is logged by name; a
        partial or empty copy is never left where a pattern could find it,
        because a truncated database parses as a smaller one, not as an error.
        """
        intended = self._intended_path(member)
        if member.endswith('/'):
            # Case-variant directories fold into one on a case-insensitive
            # volume; their files disambiguate individually, so directory
            # members take no guard. The zip seeker records a directory member
            # it returns, so the run cites it; do the same.
            os.makedirs(intended, exist_ok=True)
            self.file_infos[intended] = FileInfo(member, 0, 0)
            return intended
        entry = self._entries[member]
        dest_path = self._unique_data_path(intended, member)
        parent = os.path.dirname(dest_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        # A read past the end of the image comes back short, and a walker fills
        # the gap with zeros rather than raising, so the copy's length says
        # nothing about whether the file was all there. The reader counts every
        # byte it fell short by; sampling that count around the read is how its
        # own extractor tells a whole file from one the image was cut through.
        shortfall_before = qnxprobe.EOF_SHORTFALL['bytes']
        got = 0
        try:
            with open(dest_path, 'wb') as fout:
                for chunk in entry.walker.read_file(entry.node, entry.size):
                    fout.write(chunk)
                    got += len(chunk)
        except qnxprobe.NtfsUnreadable as exc:
            self._discard(dest_path)
            logfunc(f'Not staged, {member}: {exc}')
            return None
        except OSError:
            self._discard(dest_path)
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # One file the reader cannot decode must not end the run; the
            # other matches still reach the artifact.
            self._discard(dest_path)
            logfunc(f'Not staged, {member}: the reader raised {type(exc).__name__}: {exc}')
            return None
        cut_by = qnxprobe.EOF_SHORTFALL['bytes'] - shortfall_before
        if cut_by:
            self._discard(dest_path)
            present = max(min(got, entry.size - cut_by), 0)
            logfunc(f'Not staged, {member}: only {present:,} of {entry.size:,} bytes are in '
                    f'the image (the image ends before the file does)')
            return None
        if got != entry.size:
            # The image holds the whole file and the reader still returned a
            # different length: that is the reader's, and a copy of the wrong
            # length must not reach an artifact, because a database cut short
            # parses as a smaller one rather than as an error.
            self._discard(dest_path)
            logfunc(f'Not staged, {member}: the reader returned {got:,} bytes for a '
                    f'{entry.size:,} byte file')
            return None

        modified = entry.mtime or 0
        stamp = modified or _reading_as_local_instant(entry.reading)
        if stamp:
            os.utime(dest_path, (stamp, stamp))
        created = 0
        stamps = getattr(entry.walker, 'stamps', None)
        if stamps is not None:
            try:
                created = stamps(entry.node)[0] or 0
            except Exception:  # pylint: disable=broad-exception-caught
                created = 0
        self.file_infos[dest_path] = FileInfo(member, created, modified)
        return dest_path

    @staticmethod
    def _discard(path):
        try:
            os.remove(path)
        except OSError:
            pass

    def cleanup(self):
        image, self._image = self._image, None
        if image is not None:
            try:
                image.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
