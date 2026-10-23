"""Raw disk image and acquisition input: the seeker behind ``-t raw``.

A raw image (``.img``, ``.dd``, ``.bin``, a numbered ``.001`` segment of a split
set) or an acquisition (EnCase/EWF ``.E01``, SMART ``.s01``, EWF2 ``.Ex01``, AFF
``.aff``, an AFM ``.afm`` with its raw files, or an AFD folder of AFF files, each
with the segments or files beside it, an AFF4 ``.aff4``, an Apple disk image,
``.dmg``, ``.sparseimage`` or ``.sparsebundle``, or a virtual machine's disk,
``.vhd``, ``.vhdx``, ``.vmdk`` or ``.qcow2``) is read in place, without mounting and
without administrator rights, through the reader vendored in ``scripts/vendor/``
(qnxprobe, with ewfprobe beside it for the acquisitions). The reader finds the
partitions, identifies each volume by its own on-disk structure and walks its
directory tree; this module turns that into the same contract the zip seeker
offers: a list of member names to match artifact patterns against, and a copy of
each matched file staged under the report's data folder.

Logical evidence, EnCase's ``.L01`` and FTK Imager's ``.ad1``, holds copies of
files rather than a disk. Its file tree is read through ewfprobe instead, and each
entry is a member under its path in the evidence: live files, folders and NTFS
alternate data streams. An AD1's deleted entries and the file slack and index
records FTK Imager keeps beside a file are not members, as a disk's deleted records
are not.

An encrypted image opens with what it was locked with: an Apple disk image or an
encrypted AFF with its password, an E01, SMART, raw or AD1 set FTK Imager encrypted
with AD encryption with its password, and any of them sealed to a certificate with
that certificate's RSA private key. A BitLocker volume inside an image opens with
its password, its recovery password or its startup key (``.BEK``) file, and an APFS
volume macOS encrypted in software with its password or personal recovery key, and a
LUKS container with its passphrase. The GUI asks for each; the command line takes a
password from ``--image_password_file`` or ``--image_password_env`` (tried on the image
and on any BitLocker, encrypted APFS or LUKS volume in it), a private key from
``--image_private_key`` and startup keys from ``--bitlocker_key``, or asks at a
terminal. What is given is checked against the image before the run and never stored;
a BitLocker, APFS or LUKS volume left locked is reported and its files are not searched.

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

An NTFS alternate data stream is a member too, named ``<file>:<stream>`` as
Windows names it (``.../Downloads/setup.exe:Zone.Identifier``,
``.../$Extend/$UsnJrnl:$J``), and ``:<stream>`` on the root directory. A stream
is matched only by a pattern whose last segment names one, that is, holds a
``:``. A pattern without one is handed exactly what it was before: ``*/Recent/*``
still returns the shortcuts in Recent and not their ``Zone.Identifier`` streams,
which a shortcut parser would misread. A pattern that holds a ``:`` because the
file name it looks for does (a few in the cores do) still matches every file it
did, and also any stream whose ``<file>:<stream>`` name fits it.
The reader decides what a stream holds: it starts at the first stored cluster, so
``$J`` comes out at the size of its records rather than of the gigabytes of hole
Windows leaves in front of them, and a stream that stores nothing
(``$BadClus:$Bad``) is not listed at all. Streams need qnxprobe 1.37 or later;
with an older vendored copy there are simply none.

A directory's file name index that has grown into an ``$INDEX_ALLOCATION``
attribute is a member as well, named ``<directory>:$I30`` and ``:$I30`` on the
root directory, unless the record also holds a ``$DATA`` stream of that name,
which then reads as the stream. It is not an alternate data stream and is kept apart from them, in
``index_list``: it is matched only by a pattern whose last segment ends ``:$I30``,
which is handed the indexes besides what it was handed before, so a pattern that
does not end that way, ``*:*`` included, is handed exactly what it was.
What is staged is the attribute as the volume stores it, one index block after
another with their update sequence arrays not applied. Directory indexes need
qnxprobe 1.63 or later; with an older vendored copy there are none.

Several images can be read together, the members of a RAID set, one image per disk:
Linux md arrays and LVM2 logical volumes spread over several images are assembled by
the vendored reader (qnxprobe 1.69 or later) and each array is read as a disk of its
own. One image that holds an md member is read with its arrays too. Given one such
image, the command line and the GUI look in its folder for the other members, by what
each file records about itself (qnxprobe.raid_siblings, 1.70 or later), say what they
found and what they left out and why, and read the set; FileSeekerRaw's docstring says
how its volumes are named.

What the reader finds wrong while it reads is written to the run log as it is met.
A volume's damage (a record that fails its check, and since qnxprobe 1.74 a file on
APFS or HFS+ that carries a compression attribute without being flagged compressed,
read as stored, as macOS reads it) is said after the volume is walked, and damage met
while a file is staged is said with that file. A chunk, grain or cluster of an
acquisition whose stored data ran out before the bytes it covers, which ewfprobe
(0.14.0 or later) reads with zeros in its place, is said when the listing or a staged
file first reads it. A file the reader will not decode (a macOS file compressed with
LZBITMAP, since 1.74) is listed and not staged, and the run log gives the reason.

This file is shared by iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP and is kept
byte-identical across them. It names nothing specific to a platform; the
platform is in the artifacts.
"""

import getpass
import os
import re
import sys
import time as timex
from fnmatch import _compile_pattern

from scripts.ilapfuncs import logfunc, sanitize_file_path
from scripts.search_files import FileInfo, FileSeekerBase, normcase

# qnxprobe reaches its acquisition reader with a bare ``import ewfprobe``,
# falling back to a sys.path insert of its own directory when that fails.
# Importing the vendored copy through the package first and registering it
# under the bare name makes the fallback unnecessary, which matters in a frozen
# (PyInstaller) build where the vendored files are modules of the bundle rather
# than files on a path.
from scripts.vendor import ewfprobe as _ewfprobe   # noqa: E402  (order matters)
sys.modules.setdefault('ewfprobe', _ewfprobe)
from scripts.vendor import qnxprobe  # noqa: E402

# Extensions conventionally given to a raw disk image, plus those the
# acquisitions the reader opens carry. Everything a raw image run needs is
# decided by reading the image, so this list only has to get the file past type
# selection in the GUI; an image named anything else is still reachable from the
# command line with -t raw. An .E01, .s01 or .Ex01 is the first segment of its set
# and the reader joins the rest, and so is a .001; an .aff inside a folder whose
# name ends .afd brings every file of that folder, and an .afm the raw files beside
# it. A .dmg is one file, or the first of the .dmgpart files hdiutil segment splits
# it into. A .sparseimage is one file, and a .sparsebundle is a folder, which a
# Mac's file dialog lists as one item. An .aff4 can be one of several files a
# striped image is split across; a .vmdk can be the descriptor or an extent, and a
# difference disk is read through the disks under it. An .L01 or .ad1 is the first
# file of its logical evidence.
RAW_IMAGE_SUFFIXES = ('img', 'bin', 'dd', 'raw', '001', 'e01', 's01', 'ex01', 'aff',
                      'afm', 'aff4', 'dmg', 'sparseimage', 'sparsebundle', 'vhd', 'vhdx',
                      'vmdk', 'qcow', 'qcow2', 'l01', 'ad1')

# The same, as the file dialog's pattern list: the conventional spelling of each
# extension, since a dialog on Linux matches the case it is given.
RAW_IMAGE_FILE_PATTERNS = ('*.img *.bin *.dd *.raw *.001 *.E01 *.s01 *.Ex01 *.aff *.afm '
                           '*.aff4 *.dmg *.sparseimage *.sparsebundle *.vhd *.vhdx *.vmdk '
                           '*.qcow *.qcow2 *.L01 *.ad1')

# What the vendored reader walks, for the file dialog and the -t help. A test
# asserts each entry here has a walker in the vendored copy, so the two cannot
# drift apart quietly.
RAW_IMAGE_FILESYSTEMS = ('QNX6, QNX4, ETFS, EFS, ext2/3/4, F2FS, FAT32, FAT16, FAT12, exFAT, '
                         'NTFS, HFS+, APFS, SquashFS, JFFS2, UBI, UBIFS, YAFFS, QNX IFS, '
                         'U-Boot environment, Belkin NVRM')
RAW_IMAGE_LABEL = f'Raw disk image or acquisition ({RAW_IMAGE_FILESYSTEMS})'

# qnxprobe's names for logical evidence, and for an AD-encrypted set, which can hold
# logical evidence or a disk. ewfprobe opens all three and says which it holds.
_MAYBE_LOGICAL = ('L01', 'AD1', 'AD_ENCRYPTED')
_LOGICAL_FORMATS = (_ewfprobe.FORMAT_L01, _ewfprobe.FORMAT_AD1)
# What a BitLocker volume can be opened with here: a password, a recovery
# password or a startup key file. Its clear key needs nothing, and a TPM cannot be
# reached from an image.
_BITLOCKER_ASKABLE = ('password', 'recovery password', 'startup key')
# The kinds of AD1 entry that hold no file's content, by the type record FTK Imager
# stores, as measured on the AD1s at hand: each is left out and counted. Any other
# kind is a member, so an entry of a kind not measured is searched rather than lost.
_AD1_NOT_FILES = {
    '6': 'file slack entries (type 6)',
    'F': 'NTFS directory index records, $I30 (type F)',
    '10': 'NTFS attribute records, $DSC and $TXF_DATA (type 10)',
    '61': 'index entries that hold no data (type 61)',
}

# A directory this deep in a walk is a loop in the tree, not a directory.
_MAX_DEPTH = 64


def names_an_image_folder(path):
    """True when ``path`` is a folder the reader opens as one disk image: an Apple
    sparse bundle, recognised by its Info.plist whatever the folder is called, or an
    AFD folder of AFF files. Chosen with a folder dialog, such a folder is not an
    extraction whose files are the evidence, so the GUI reads it as a raw image.
    An encrypted sparse bundle counts too, so that it is opened with its password
    rather than the run walking its band files."""
    return (os.path.isdir(path) and
            qnxprobe.acquisition_format(path) in ('SPARSEBUNDLE', 'AFD', 'DMG_ENCRYPTED'))


class ImageKeys:
    """What opens an encrypted image and the encrypted volumes in it, for one run.

    ``password`` is the image's password (a str, or bytes as read from a file), and is
    also tried on each BitLocker volume as a password and as a recovery password, and
    on each encrypted APFS volume as a password and as a personal recovery key;
    ``private_key`` is the path of an unencrypted PEM or DER RSA key, for an image
    sealed to a certificate; ``bitlocker_secrets`` are further passwords or recovery
    passwords and ``bitlocker_keys`` the paths of startup key (.BEK) files, for
    BitLocker; ``apfs_secrets`` are further passwords or personal recovery keys, for
    APFS; ``luks_secrets`` are further passphrases, for LUKS. Nothing here is written
    anywhere; it lasts as long as the run.
    """

    __slots__ = ('password', 'private_key', 'bitlocker_secrets', 'bitlocker_keys',
                 'apfs_secrets', 'luks_secrets', 'per_image')

    def __init__(self, password=None, private_key=None, bitlocker_secrets=(),
                 bitlocker_keys=(), apfs_secrets=(), luks_secrets=()):
        self.password = password
        self.private_key = private_key
        self.bitlocker_secrets = list(bitlocker_secrets)
        self.bitlocker_keys = list(bitlocker_keys)
        self.apfs_secrets = list(apfs_secrets)
        self.luks_secrets = list(luks_secrets)
        # When several images are read together, each can open with its own:
        # {path: (password, private key)}. An image not named here opens with
        # ``password`` and ``private_key``.
        self.per_image = {}

    def password_for(self, path):
        """The password that opens the image at ``path``."""
        return self.per_image.get(path, (self.password, self.private_key))[0]

    def private_key_for(self, path):
        """The private key that opens the image at ``path``."""
        return self.per_image.get(path, (self.password, self.private_key))[1]

    def _image_secrets(self):
        """The image's password, then the password of each image read with it, once each:
        as for one image, what opened an image is tried on the volumes inside."""
        out = [self.password] if self.password else []
        for password, _key in self.per_image.values():
            if password and password not in out:
                out.append(password)
        return out

    def bitlocker_passwords(self):
        """Every secret to try on a BitLocker volume, the image's password first."""
        return self._image_secrets() + self.bitlocker_secrets

    def apfs_passwords(self):
        """Every secret to try on an encrypted APFS volume, the image's password first."""
        return self._image_secrets() + self.apfs_secrets

    def luks_passwords(self):
        """Every passphrase to try on a LUKS container, the image's password first."""
        return self._image_secrets() + self.luks_secrets


def needs_password(path):
    """True when ``path`` is an image the reader opens only with its password: an
    encrypted Apple disk image, an encrypted AFF, or an E01, SMART, raw or AD1 set FTK
    Imager encrypted with AD encryption (a raw set from any of its numbered files). An
    image with a password and a certificate as well counts; one sealed only to a
    certificate does not (see needs_private_key)."""
    return qnxprobe.needs_password(path)


def needs_private_key(path):
    """True when ``path`` is an image sealed only to a certificate, which opens with
    that certificate's RSA private key rather than a password."""
    return qnxprobe.needs_private_key(path)


def _encrypted_kind(path):
    """What an encrypted image is, as a sentence names it."""
    kind = qnxprobe.acquisition_format(path)
    if kind == 'AD_ENCRYPTED':
        return 'an acquisition FTK Imager encrypted with AD encryption'
    if kind in ('AFF', 'AFD'):
        return 'an encrypted AFF'
    return 'an encrypted Apple disk image'


def _open_errors():
    """What stops an image opening for a reason other than its password: asking
    again would not help, so it is reported rather than asked about."""
    return (qnxprobe.ImageUnreadable, OSError, _ewfprobe.EwfError)


def _opens(path, password=None, private_key=None):
    """True when ``password`` or ``private_key`` opens the image at ``path``, False when
    it does not. Anything else that stops it opening (no cipher package, a damaged
    image) is raised. Logical evidence is opened by ewfprobe, which reads it; qnxprobe
    reads disks and refuses it."""
    try:
        if qnxprobe.acquisition_format(path) in _MAYBE_LOGICAL:
            _ewfprobe.open_ewf(path, password=password, private_key=private_key).close()
        else:
            qnxprobe.open_image(path, password=password, private_key=private_key).close()
    except (qnxprobe.ImagePasswordError, _ewfprobe.EwfPasswordError):
        return False
    return True


def password_opens(path, password):
    """True when ``password`` opens the encrypted image at ``path``, False when it
    does not. Anything else that stops it opening is raised."""
    return _opens(path, password=password)


def open_logical(path, keys=None):
    """The ewfprobe image of logical evidence, an L01 or an AD1 (AD-encrypted or not),
    opened with ``keys``; None for anything else, which is read as a disk."""
    if qnxprobe.acquisition_format(path) not in _MAYBE_LOGICAL:
        return None
    keys = keys or ImageKeys()
    try:
        image = _ewfprobe.open_ewf(path, password=keys.password_for(path),
                                   private_key=keys.private_key_for(path))
    except _ewfprobe.EwfPasswordError as exc:
        # raised as the disk route raises it, so a caller handles one kind
        raise qnxprobe.ImagePasswordError(
            str(exc), isinstance(exc, _ewfprobe.EwfWrongPasswordError),
            needs=getattr(exc, 'needs', 'password')) from None
    if image.format in _LOGICAL_FORMATS:
        return image
    image.close()
    return None


def _askable(bitlocker):
    """True when a BitLocker volume that is still locked could open with a password, a
    recovery password or a startup key, so asking for one could help."""
    return (bitlocker.fvek is None and not bitlocker.why
            and any(kind in _BITLOCKER_ASKABLE for kind, _id in bitlocker.protectors))


def _in_image(path, keys, look):
    """``look(image)`` over the image at ``path`` opened with ``keys``, or [] for
    logical evidence, which holds no volumes."""
    logical = open_logical(path, keys)
    if logical is not None:
        logical.close()
        return []
    with qnxprobe.open_image(path, password=keys.password_for(path),
                             private_key=keys.private_key_for(path)) as image:
        return look(image)


def _unlock_bitlocker(path, keys, ask):
    """Try ``keys`` on each BitLocker volume in the image at ``path`` and offer every
    volume they leave locked to ``ask(bitlocker, wrong)`` until it opens: ``ask``
    returns ('secret', text) for a password or recovery password, ('key', path) for a
    startup key file, or None to leave it locked. What opens a volume is added to
    ``keys``. Returns the volumes still locked as _Locked records. Logical evidence
    holds no volumes."""
    return _in_image(path, keys, lambda image: _unlock_bitlocker_in(image, keys, ask))


class _Locked:
    """An encrypted volume left locked: ``label``, the reader's ``note`` on why,
    ``askable`` (a secret could still open it) and ``tried`` (something given was tried
    on it and did not open it)."""

    __slots__ = ('label', 'note', 'askable', 'tried')

    def __init__(self, label, note, askable, tried):
        self.label, self.note, self.askable, self.tried = label, note, askable, bool(tried)


def _unlock_bitlocker_in(image, keys, ask):
    """_unlock_bitlocker over an image already open (an assembled RAID array)."""
    left = []
    _fh, found = qnxprobe.unlock_bitlocker(image, qnxprobe.image_size(image),
                                           keys.bitlocker_passwords(), keys.bitlocker_keys)
    for bitlocker in found:
        wrong = False
        while _askable(bitlocker):
            answer = ask(bitlocker, wrong)
            if answer is None:
                break
            kind, value = answer
            if kind == 'key':
                if bitlocker.unlock((), [value]):
                    keys.bitlocker_keys.append(value)
            elif bitlocker.unlock([value], ()):
                keys.bitlocker_secrets.append(value)
            wrong = bitlocker.fvek is None
        if bitlocker.fvek is None:
            left.append(_Locked(bitlocker.label, bitlocker.locked_note(),
                                _askable(bitlocker), bitlocker.tried))
    return left


def _unlock_apfs(path, keys, ask):
    """Try ``keys`` on each encrypted APFS volume in the image at ``path`` whose blocks
    are ciphertext there, and offer every volume they leave locked to ``ask(lock,
    wrong)`` until it opens: ``ask`` returns a password or personal recovery key, or
    None to leave it locked. What opens a volume is added to ``keys``. Returns the
    volumes still locked as _Locked records, the name saying which volume of which
    region. Logical evidence holds no volumes."""
    return _in_image(path, keys, lambda image: _unlock_apfs_in(image, keys, ask))


def _unlock_apfs_in(image, keys, ask):
    """_unlock_apfs over an image already open (an assembled RAID array)."""
    left = []
    _fh, found = qnxprobe.unlock_apfs(image, qnxprobe.image_size(image), keys.apfs_passwords())
    for lock in found:
        wrong = False
        while lock.vek is None and not lock.why:
            answer = ask(lock, wrong)
            if not answer:
                break
            if lock.unlock([answer]):
                keys.apfs_secrets.append(answer)
            wrong = lock.vek is None
        if lock.vek is None:
            left.append(_Locked(f'{lock.name} in {lock.label}', lock.locked_note(),
                                not lock.why, lock.tried))
    return left


def _unlock_luks(path, keys, ask):
    """Try ``keys`` on each LUKS container in the image at ``path`` and offer every
    container they leave locked to ``ask(luks, wrong)`` until it opens: ``ask`` returns a
    passphrase, or None to leave it locked. What opens a container is added to ``keys``.
    Returns the containers still locked as _Locked records. Logical evidence holds no
    volumes."""
    return _in_image(path, keys, lambda image: _unlock_luks_in(image, keys, ask))


def _unlock_luks_in(image, keys, ask):
    """_unlock_luks over an image already open (an assembled RAID array)."""
    left = []
    _fh, found = qnxprobe.unlock_luks(image, qnxprobe.image_size(image), keys.luks_passwords())
    for luks in found:
        wrong = False
        while luks.mk is None and not luks.why:
            answer = ask(luks, wrong)
            if not answer:
                break
            if luks.unlock([answer]):
                keys.luks_secrets.append(answer)
            wrong = luks.mk is None
        if luks.mk is None:
            left.append(_Locked(luks.label, luks.locked_note(), not luks.why, luks.tried))
    return left


def _apfs_prompt(lock, name, wrong):
    """What an encrypted APFS volume's prompt says, the hint it stores included."""
    return (('That does not open it. ' if wrong else '')
            + f'{lock.name} in {lock.label} of {name} is an encrypted APFS volume. '
            f'Its password or personal recovery key'
            + (f' (its hint, as stored: "{lock.hint}")' if lock.hint else ''))


def _secret_given(password_file=None, password_env=None):
    """The first line of ``password_file``, else the variable ``password_env``, else
    None. A secret is never taken as an argument's value, which would show in the
    process list and the shell history."""
    if password_file:
        with open(password_file, 'rb') as fh:
            first = fh.read().split(b'\n', 1)[0]
        return first[:-1] if first.endswith(b'\r') else first
    if password_env:
        if password_env not in os.environ:
            raise ValueError(f'the environment variable {password_env} is not set')
        return os.environ[password_env]
    return None


def image_paths(input_path):
    """The images of a run as a list: one path, or the several images read together
    (the members of a RAID set) given as a list or tuple."""
    if isinstance(input_path, (list, tuple)):
        return [str(path) for path in input_path]
    return [input_path]


def _image_name(path):
    return os.path.basename(os.path.normpath(path))


def _for_each_source(paths, keys, look):
    """``look(name, image)`` for every image a run reads volumes from: the one image
    given, or, when several are read together or the one image holds RAID members,
    each image and then each array or volume read across them (see FileSeekerRaw).
    Logical evidence holds no volumes and is passed over."""
    opened, opened_paths = [], []
    try:
        for path in paths:
            logical = open_logical(path, keys)
            if logical is not None:
                logical.close()
                continue
            opened.append((_image_name(path), qnxprobe.open_image(
                path, password=keys.password_for(path),
                private_key=keys.private_key_for(path))))
            opened_paths.append(path)
        raid = (_raid_members(list(zip(_raid_names(opened_paths),
                                       (image for _name, image in opened))))
                if opened else None)
        for name, image in opened:
            look(name, image)
        for arr in (raid.arrays if raid is not None else ()):
            if arr.image is not None:
                look(arr.label, arr.image)
    finally:
        for _name, image in opened:
            try:
                image.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass


def _cli_image_key(path, given, private_key, at_terminal):
    """(password, private key) that open the image at ``path``, for the command line:
    see cli_image_keys."""
    name = _image_name(path)
    if needs_private_key(path):
        if private_key is None:
            raise ValueError(f'{name} is sealed to a certificate and opens only with '
                             f"that certificate's private key; give it with "
                             f'--image_private_key')
        if not _opens(path, given, private_key):
            raise ValueError(f'the private key does not open {name}')
        return given, private_key
    if needs_password(path):
        if private_key is not None and _opens(path, None, private_key):
            return None, private_key                # sealed to a certificate as well
        if given is not None:
            if not _opens(path, given):
                raise ValueError(f'the password does not open {name}')
            return given, None
        if at_terminal:
            for _ in range(3):
                password = getpass.getpass(f'Password for {name}: ')
                if _opens(path, password):
                    return password, None
                print('That password does not open the image.', file=sys.stderr)
            raise ValueError(f'the password does not open {name}')
        raise ValueError(f'{name} is {_encrypted_kind(path)} and opens only '
                         f'with its password; give it with --image_password_file '
                         f'or --image_password_env, or run at a terminal to be '
                         f'asked for it')
    return given, private_key           # the password can still open a BitLocker volume


def _cli_volume_keys(name, image, keys, at_terminal):
    """Ask at a terminal for what opens each BitLocker, APFS and LUKS volume in
    ``image`` that ``keys`` leave locked, and say on stderr what stays locked. As the
    vendored reader does (qnxprobe 1.72), which option takes what opens it is said only
    when nothing was given or tried for that kind of volume; when something was, the
    reader's reason stands alone, and a volume no secret could open is named too."""
    tries = {}
    # what was given before anything is asked, for each kind of volume
    given_bitlocker = bool(keys.bitlocker_passwords() or keys.bitlocker_keys)
    given_apfs = bool(keys.apfs_passwords())
    given_luks = bool(keys.luks_passwords())

    def say_locked(lock, given, hint):
        if not (lock.askable or given):
            return            # nothing given, and nothing would open it: the run log says why
        line = f'{lock.label} of {name} stays locked and its files are not searched ({lock.note}).'
        if lock.askable and not given and not lock.tried:
            line += f' {hint}'
        print(line, file=sys.stderr)

    def ask(bitlocker, wrong):
        if not at_terminal:
            return None
        if wrong:
            print('That does not open it.', file=sys.stderr)
        tries[bitlocker.base] = tries.get(bitlocker.base, 0) + 1
        if tries[bitlocker.base] > 3:
            return None
        answer = getpass.getpass(f'{bitlocker.label} of {name} is BitLocker-encrypted. '
                                 f'Its password or recovery password (empty leaves it '
                                 f'locked): ')
        return ('secret', answer) if answer else None

    for lock in _unlock_bitlocker_in(image, keys, ask):
        say_locked(lock, given_bitlocker,
                   'Give its password or recovery password with --image_password_file or '
                   '--image_password_env, or its startup key with --bitlocker_key.')
    apfs_tries = {}

    def ask_apfs(lock, wrong):
        if not at_terminal:
            return None
        if wrong:
            print('That does not open it.', file=sys.stderr)
        key = (lock.container_uuid, lock.uuid)
        apfs_tries[key] = apfs_tries.get(key, 0) + 1
        if apfs_tries[key] > 3:
            return None
        return getpass.getpass(_apfs_prompt(lock, name, False)
                               + ' (empty leaves it locked): ') or None

    for lock in _unlock_apfs_in(image, keys, ask_apfs):
        say_locked(lock, given_apfs,
                   'Give its password or personal recovery key with --image_password_file '
                   'or --image_password_env.')
    luks_tries = {}

    def ask_luks(luks, wrong):
        if not at_terminal:
            return None
        if wrong:
            print('That does not open it.', file=sys.stderr)
        luks_tries[luks.base] = luks_tries.get(luks.base, 0) + 1
        if luks_tries[luks.base] > 3:
            return None
        return getpass.getpass(f'{luks.label} of {name} is a LUKS container. Its '
                               f'passphrase (empty leaves it locked): ') or None

    for lock in _unlock_luks_in(image, keys, ask_luks):
        say_locked(lock, given_luks,
                   'Give its passphrase with --image_password_file or --image_password_env.')
    if given_luks:
        # A LUKS container inside a logical volume read through a map is not opened,
        # whatever is given: the reader places such a volume past the image's end
        # (lvm_image), after the containers are tried, and its note says so.
        size = qnxprobe.image_size(image)
        mapped = getattr(qnxprobe.lvm_image(image, size), 'lvm_virtual', None)
        for vol in (qnxprobe.volumes(image, size) if mapped else ()):
            if vol.get('kind') == 'luks' and (vol.get('base') or 0) >= size:
                print(f"{vol.get('label') or vol.get('name')} of {name} stays locked and its "
                      f"files are not searched ({vol.get('note')}), so the passphrase given "
                      f'was not tried on it.', file=sys.stderr)


def cli_image_keys(path, password_file=None, password_env=None, private_key=None,
                   bitlocker_keys=()):
    """What opens the image at ``path`` and the encrypted volumes in it, for the
    command line, as ImageKeys. ``path`` can also be a list of images read together
    (the members of a RAID set): each is opened with what opens it, and the volumes
    of each image and of each array read from them are asked about in turn.

    A password comes from the first line of ``password_file``, else the environment
    variable ``password_env``; it opens an encrypted image, and it is tried on each
    BitLocker volume in the image as a password and as a recovery password, and on
    each encrypted APFS volume as a password and as a personal recovery key, and on
    each LUKS container as a passphrase. ``private_key`` opens an image sealed to a
    certificate and ``bitlocker_keys`` are startup key (.BEK) files. At a terminal, what
    is missing is asked for (three tries each); a BitLocker, APFS or LUKS volume nothing
    opens is reported on stderr and left locked.

    Raises ValueError, saying why, when the image itself cannot be opened with what was
    given.
    """
    return cli_raw_input(path, password_file, password_env, private_key, bitlocker_keys,
                         look_beside=False).keys


def _gui_image_key(parent, path):
    """(password, private key) that open the image at ``path``, asked for in dialogs
    over ``parent``, or None when the examiner cancels: see ask_image_keys."""
    from tkinter import filedialog, messagebox, simpledialog  # pylint: disable=import-outside-toplevel
    name = _image_name(path)
    if needs_private_key(path):
        title = f'{name} is sealed to a certificate: its RSA private key'
        while True:
            key = filedialog.askopenfilename(
                parent=parent, title=title,
                filetypes=[('Private key', '*.pem *.key *.der'), ('All files', '*')])
            if not key:
                return None
            try:
                if _opens(path, private_key=key):
                    return None, key
                why = f'That key does not open {name}.'
            except _ewfprobe.EwfError as exc:        # not a key it can read
                why = str(exc)
            messagebox.showerror('Encrypted disk image', why, parent=parent)
    if needs_password(path):
        prompt = f'{name} is {_encrypted_kind(path)}. Its password:'
        while True:
            password = simpledialog.askstring('Encrypted disk image', prompt, show='*',
                                              parent=parent)
            if password is None:
                return None
            if _opens(path, password=password):
                return password, None
            prompt = f'That password does not open {name}. Its password:'
    return None, None


def _gui_volume_keys(parent, name, image, keys):
    """Ask in dialogs over ``parent`` for what opens each BitLocker, APFS and LUKS
    volume in ``image`` that ``keys`` leave locked. Cancelling leaves it locked."""
    from tkinter import filedialog, simpledialog  # pylint: disable=import-outside-toplevel

    def ask(bitlocker, wrong):
        prompt = (('That does not open it. ' if wrong else '')
                  + f'{bitlocker.label} of {name} is BitLocker-encrypted. Its password or '
                  f'recovery password (leave empty to choose a startup key .BEK file):')
        answer = simpledialog.askstring('BitLocker volume', prompt, show='*',
                                        parent=parent)
        if answer is None:
            return None
        if answer:
            return ('secret', answer)
        key = filedialog.askopenfilename(
            parent=parent, title='BitLocker startup key',
            filetypes=[('BitLocker startup key', '*.BEK *.bek'), ('All files', '*')])
        return ('key', key) if key else None

    _unlock_bitlocker_in(image, keys, ask)

    def ask_apfs(lock, wrong):
        return simpledialog.askstring('Encrypted APFS volume',
                                      _apfs_prompt(lock, name, wrong) + ':',
                                      show='*', parent=parent)

    _unlock_apfs_in(image, keys, ask_apfs)

    def ask_luks(luks, wrong):
        return simpledialog.askstring(
            'LUKS container', ('That does not open it. ' if wrong else '')
            + f'{luks.label} of {name} is a LUKS container. Its passphrase:',
            show='*', parent=parent)

    _unlock_luks_in(image, keys, ask_luks)


def ask_image_keys(parent, path):
    """What opens the image at ``path`` and the encrypted volumes in it, asked for in
    dialogs over ``parent``, as ImageKeys: its password, or the private key file of the
    certificate it is sealed to, until one opens it, then for each BitLocker volume
    inside, its password or recovery password, or left empty, its startup key (.BEK)
    file, and for each encrypted APFS volume, its password or personal recovery key.
    Cancelling a volume's prompt leaves it locked. None when the examiner cancels the
    image's own prompt, or when the image will not open for another reason, which is
    shown. ``path`` can also be a list of images read together (the members of a RAID
    set): each that needs it is asked for in turn, then the volumes of each image and of
    each array read from them."""
    raw = ask_raw_input(parent, path, look_beside=False)
    return None if raw is None else raw.keys


# ---- several images read together: the members of a RAID set -------------------

FOUND_AUTOMATICALLY = 'found automatically'


class MemberSearch:
    """What a search beside one image found (qnxprobe.raid_siblings): the other
    members of the md arrays and LVM2 volume groups that image holds members of, found
    in its folder by what each file records about itself, never by its name; and
    whether the examiner chose to read them (``used``)."""

    def __init__(self, given, result, used=True):
        self.given = given
        self.result = result
        self.used = used

    @property
    def added(self):
        """The files the search would add, in the order it looked at them."""
        return [record['path'] for record in self.result.added]

    @property
    def found(self):
        """The files added to the run: none when the examiner chose only the file given."""
        return self.added if self.used else []

    def paths(self):
        """The image given, then each file the run reads with it."""
        return [self.given] + self.found

    def holds(self):
        """What the image given holds that sent the search looking, in words."""
        words = []
        for ident in self.result.identities:
            if ident.get('kind') == 'md':
                words.append(f"a member of md array {ident.get('array_uuid')}"
                             + (f" ({ident['name']})" if ident.get('name') else ''))
            else:
                words.append(f"a physical volume of LVM2 volume group {ident.get('vg_name')}, "
                             f"which spans other disks")
        return ' and '.join(words) or 'RAID members'

    def outcome(self):
        """The search's result and the examiner's choice, in one sentence."""
        name = _image_name(self.given)
        if not self.added:
            return (f'{name} holds {self.holds()}; no other member was found beside it, '
                    f'so it is read alone')
        if not self.used:
            return (f'{name} holds {self.holds()}; {len(self.added)} other member file(s) '
                    f'were found beside it and not read: the examiner chose to read only {name}')
        return (f'{name} holds {self.holds()}; {len(self.added)} other member file(s) were '
                f'found beside it and read with it')

    def lines(self):
        """What the search did and found, for the run log and the command line: what the
        image given holds, the folder, what was looked for, every other file in it with
        what became of it and why, the members no file holds, and what is read."""
        name = _image_name(self.given)
        out = [f'{name} holds {self.holds()}, and not every member is in it. The other '
               f'members were looked for beside it, by what each file records about itself, '
               f'not by its name:']
        out += [f'  {line}' for line in self.result.lines()]
        out.append(f'  Result: {self.outcome()}.')
        return out


def find_members(path, keys=None):
    """A MemberSearch for the image at ``path``, or None when it holds no member of an
    md array or an LVM2 volume group (or is logical evidence, or does not open, which
    the run says when it reads it). Only the image's own folder is looked in; see
    qnxprobe's README, "Finding the other members from one of them"."""
    keys = keys or ImageKeys()
    try:
        if qnxprobe.acquisition_format(path) in _MAYBE_LOGICAL:
            return None
    except _open_errors():
        return None
    password = keys.password_for(path)
    private_key = keys.private_key_for(path)
    passwords = [password] if password else []
    private_keys = [private_key] if private_key else []
    try:
        # First what the image holds, opening no other file: an image that holds every
        # member of its arrays and volume groups (a one-disk LVM2 image, or a disk whose
        # own partitions form an array) needs no search, and nothing is said.
        held = qnxprobe.raid_siblings(path, passwords=passwords, private_keys=private_keys,
                                      max_candidates=0)
        if held.error or not held.identities or not held.missing:
            return None
        result = qnxprobe.raid_siblings(path, passwords=passwords, private_keys=private_keys)
    except Exception:  # pylint: disable=broad-exception-caught
        # The search is said never to raise for a file it cannot read; anything else
        # leaves the run to the images given, whose RAID members the log still names.
        return None
    if result.error or not result.identities:
        return None
    return MemberSearch(path, result)


def _image_files(path):
    """Every file the image at ``path`` is read from, as far as its name tells without
    opening it: the segments of an EWF or AD1 set or of a split raw set, else the file."""
    try:
        kind = qnxprobe.acquisition_format(path)
    except _open_errors():
        kind = None
    files = []
    try:
        if kind in ('EWF', 'EWF2'):
            files = _ewfprobe.ewf_segments(path)
        elif kind == 'AD1':
            files = _ewfprobe.ad1_segments(path)
        elif kind in (None, 'AD_ENCRYPTED'):
            files = qnxprobe.split_segments(path)
    except Exception:  # pylint: disable=broad-exception-caught
        # a set the reader refuses is said, by name, when the run opens it
        files = []
    return files or [path]


def _identity(path):
    """The files of the image at ``path`` by device and inode, so two names of one file
    (a link, a relative and an absolute path) are one."""
    out = set()
    for one in _image_files(path):
        try:
            info = os.stat(one)
            out.add((info.st_dev, info.st_ino))
        except OSError:
            out.add(os.path.realpath(one))
    return out


def distinct_images(paths):
    """The images ``paths`` name, each disk once: (kept, repeats), ``repeats`` being
    [(path, the kept path it is the same disk as)]. Two paths are one disk when they
    share a file: the same file given twice or by two names, or two segments of one
    split, EWF or AD1 set."""
    kept, identities, repeats = [], [], []
    for path in paths:
        mine = _identity(path)
        for other, theirs in zip(kept, identities):
            if mine & theirs:
                repeats.append((path, other))
                break
        else:
            kept.append(path)
            identities.append(mine)
    return kept, repeats


def repeat_note(path, other):
    """What is said of ``path``, not read because it opens the disk ``other`` opens, in
    the vendored reader's words (qnxprobe.same_disk_note, 1.72 or later): the same file
    (the same path, a link, another spelling) is "the same disk as" the other, and a
    later file of a set the other opens is "read as a segment of" that set."""
    return qnxprobe.same_disk_note(path, other)


def repeat_lines(repeats):
    """What the run says about each image given twice, or given beside another file of
    its own set."""
    lines = []
    for path, other in repeats:
        note = repeat_note(path, other)
        given = 'Given twice' if note.startswith('the same disk') else 'Given too'
        lines.append(f'{given}: {path} is {note}.')
    return lines


def logical_among(paths):
    """The first of several paths that is logical evidence (an L01 or an AD1), which
    holds files rather than a disk and is read on its own, or None."""
    if len(paths) < 2:
        return None
    for path in paths:
        try:
            if qnxprobe.acquisition_format(path) in ('L01', 'Lx01', 'AD1'):
                return path
        except _open_errors():
            continue
    return None


def logical_refusal(path):
    """Why several images that include logical evidence are not read together."""
    return (f'{_image_name(path)} is logical evidence (an L01 or AD1), which holds files '
            f'rather than a disk and is read on its own, not together with other images.')


def _what_was_given(found):
    """(search, found paths, repeats) from what a run is handed beside its images: a
    RawInput, a MemberSearch, or the paths found."""
    if isinstance(found, RawInput):
        return found.search, list(found.found), list(found.repeats)
    if isinstance(found, MemberSearch):
        return found, list(found.found), []
    return None, list(found or ()), []


def input_text(input_path, found=()):
    """The input as the report, the run log and LAVA name it: the path itself for one
    image (or anything else), and for several images read together each path, with
    the ones found beside the image given marked as found automatically. ``found`` is
    those paths, or the MemberSearch that found them, or the RawInput. When a search
    ran and read nothing more (none found, or the examiner chose the file given alone),
    or an image was given twice, a sentence in brackets says so."""
    paths = image_paths(input_path)
    search, found_paths, repeats = _what_was_given(found)
    if len(paths) == 1 and not isinstance(input_path, (list, tuple)):
        text = input_path
    else:
        found_paths = set(found_paths)
        text = '; '.join(path + (f' ({FOUND_AUTOMATICALLY})' if path in found_paths else '')
                         for path in paths)
    notes = []
    if search is not None and not search.found:
        notes.append(search.outcome())
    notes += [f'{path} was given too and is {repeat_note(path, other)}'
              for path, other in repeats]
    return text + ''.join(f' ({note})' for note in notes)


def selection_text(paths):
    """What the window's input field shows for the files picked: the path for one,
    the first path and how many more for several."""
    paths = list(paths)
    if len(paths) <= 1:
        return paths[0] if paths else ''
    return f'{paths[0]} and {len(paths) - 1} more'


def selected_paths(entry_text, selection):
    """The input the window's field stands for: the files picked together when the
    field still shows them, otherwise whatever was typed or chosen since, as one path."""
    selection = list(selection or ())
    if len(selection) > 1 and entry_text == selection_text(selection):
        return selection
    return [entry_text]


def names_raw_images(paths):
    """True when every path is something the raw image input reads by its name: an
    image folder, a conventional image extension, or a numbered segment. Several
    files are read together only as disk images."""
    for path in paths:
        if names_an_image_folder(path):
            continue
        suffix = os.path.basename(path).rpartition('.')[2].lower()
        if suffix in RAW_IMAGE_SUFFIXES or (suffix.isascii() and suffix.isdigit()):
            continue
        return False
    return True


class RawInput:
    """The images a raw run reads and what opens them: ``paths`` (the images given,
    then any found beside the one given), ``found`` (those found), ``keys`` (ImageKeys)
    and ``search`` (the MemberSearch, or None when no search was made or the image
    given holds no RAID member)."""

    def __init__(self, paths, keys, search=None, repeats=()):
        self.paths = list(paths)
        self.keys = keys
        self.search = search
        self.found = list(search.found) if search is not None else []
        # [(path, the path of the same disk that is read)] for each image given twice
        self.repeats = list(repeats)

    @property
    def input_path(self):
        """What the run is handed: the one path, or the list of images."""
        return self.paths[0] if len(self.paths) == 1 else list(self.paths)


def cli_raw_input(input_path, password_file=None, password_env=None, private_key=None,
                  bitlocker_keys=(), look_beside=True, say=print):
    """The images a command line raw run reads, and what opens them, as RawInput.

    Each image is opened with what opens it (see cli_image_keys). One image that holds
    a member of an md array or an LVM2 volume group then has the other members looked
    for beside it (``look_beside``, on unless the examiner turned it off), and what the
    search did is said through ``say`` before anything is read: every file it adds and
    every one it does not, with why. Several images given are read as given. Last, the
    BitLocker, APFS and LUKS volumes of each image, and of each array read from them,
    are asked about. Raises ValueError, as cli_image_keys does."""
    paths, repeats = distinct_images(image_paths(input_path))
    for line in repeat_lines(repeats):
        say(line)
    logical = logical_among(paths)
    if logical is not None:
        raise ValueError(logical_refusal(logical))
    keys = ImageKeys(private_key=private_key, bitlocker_keys=bitlocker_keys)
    at_terminal = sys.stdin is not None and sys.stdin.isatty()
    search = None
    name = _image_name(paths[0])
    try:
        given = _secret_given(password_file, password_env)
        opened = {}
        for one in paths:
            name = _image_name(one)
            opened[one] = _cli_image_key(one, given, private_key, at_terminal)
        if look_beside and len(paths) == 1:
            name = _image_name(paths[0])
            first = ImageKeys(*opened[paths[0]])
            search = find_members(paths[0], first)
            if search is not None:
                for line in search.lines():
                    say(line)
                for one in search.found:
                    name = _image_name(one)
                    opened[one] = _cli_image_key(one, given, private_key, at_terminal)
                if search.found:
                    paths = search.paths()
                    say(f'Reading {len(paths)} images together: '
                        + ', '.join(_image_name(one) for one in paths))
        if len(paths) == 1:
            keys.password, keys.private_key = opened[paths[0]]
        else:
            keys.password = given
            keys.per_image = {one: opened[one] for one in paths}
        name = _image_name(paths[0])

        def look(source, image):
            nonlocal name
            name = source
            _cli_volume_keys(source, image, keys, at_terminal)

        _for_each_source(paths, keys, look)
    except _open_errors() as exc:
        raise ValueError(f'{name} could not be opened: {exc}') from None
    return RawInput(paths, keys, search, repeats)


def found_members_text(search):
    """What the window shows before a run when the search beside the image picked
    found other members: each file it would add and why, each it would not and why,
    and the members no file holds."""
    name = _image_name(search.given)
    out = [f'{name} holds RAID members. These files beside it hold the other members, '
           f'found by what each records about itself, not by its name:', '']
    for record in search.result.added:
        out.append(f"  {_image_name(record['path'])}: {record['why']}")
    rejected = search.result.rejected
    if rejected:
        out += ['', 'Not used:']
        out += [f"  {_image_name(record['path'])}: {record['why']}" for record in rejected]
    for warning in search.result.warnings:
        out += ['', f'WARNING: {warning}']
    for missing in search.result.missing:
        out += ['', f"Missing: {missing['why']}"]
    out += ['', f'Read them with {name}?']
    return '\n'.join(out)


def confirm_found_members(parent, search):
    """Ask the examiner, in a dialog over ``parent``, whether to read the files the
    search found with the image picked. Returns 'use' (the default button, "Use
    them"), 'only' ("Only the file I picked") or None ("Cancel", or the window
    closed)."""
    import tkinter as tk  # pylint: disable=import-outside-toplevel
    from tkinter import ttk  # pylint: disable=import-outside-toplevel
    dialog = tk.Toplevel(parent)
    dialog.title('RAID members found')
    dialog.transient(parent)
    choice = {'value': None}
    text = tk.Text(dialog, wrap='word', width=90, height=18)
    text.insert('1.0', found_members_text(search))
    text.config(state='disabled')
    text.pack(padx=10, pady=(10, 4), fill='both', expand=True)
    buttons = ttk.Frame(dialog)
    buttons.pack(padx=10, pady=(4, 10), anchor='e')

    def close(value):
        choice['value'] = value
        dialog.destroy()

    use = ttk.Button(buttons, text='Use them', default='active', command=lambda: close('use'))
    use.pack(side='left', padx=4)
    ttk.Button(buttons, text='Only the file I picked',
               command=lambda: close('only')).pack(side='left', padx=4)
    ttk.Button(buttons, text='Cancel', command=lambda: close(None)).pack(side='left', padx=4)
    dialog.bind('<Return>', lambda _event: close('use'))
    dialog.bind('<Escape>', lambda _event: close(None))
    dialog.protocol('WM_DELETE_WINDOW', lambda: close(None))
    use.focus_set()
    dialog.grab_set()
    dialog.wait_window()
    return choice['value']


def ask_raw_input(parent, input_path, look_beside=True, confirm=None):
    """The images a raw run from the window reads, and what opens them, as RawInput,
    or None when the examiner cancels or an image will not open (which is shown).

    Each image picked that needs it is asked for what opens it (see ask_image_keys).
    One image picked that holds a member of an md array or an LVM2 volume group then
    has the other members looked for beside it (``look_beside``). When the search adds
    files, ``confirm(parent, search)`` (confirm_found_members unless given) asks
    whether to read them: 'use' reads them, 'only' reads the file picked alone, None
    cancels the run. Nothing is asked when the image holds no member or the search adds
    nothing. Several images picked are read as picked. Last, the BitLocker, APFS and
    LUKS volumes of each image, and of each array read from them, are asked about."""
    from tkinter import messagebox  # pylint: disable=import-outside-toplevel
    paths, repeats = distinct_images(image_paths(input_path))
    if repeats:
        messagebox.showinfo('The same disk picked twice', '\n'.join(repeat_lines(repeats)),
                            parent=parent)
    logical = logical_among(paths)
    if logical is not None:
        messagebox.showerror('Error', logical_refusal(logical), parent=parent)
        return None
    keys = ImageKeys()
    search = None
    name = _image_name(paths[0])
    try:
        opened = {}
        for one in paths:
            name = _image_name(one)
            opened[one] = _gui_image_key(parent, one)
            if opened[one] is None:
                return None
        if look_beside and len(paths) == 1:
            name = _image_name(paths[0])
            search = find_members(paths[0], ImageKeys(*opened[paths[0]]))
            if search is not None and search.added:
                answer = (confirm or confirm_found_members)(parent, search)
                if answer is None:
                    return None
                search.used = answer == 'use'
                for one in search.found:
                    name = _image_name(one)
                    opened[one] = _gui_image_key(parent, one)
                    if opened[one] is None:
                        return None
                paths = search.paths()
        if len(paths) == 1:
            keys.password, keys.private_key = opened[paths[0]]
        else:
            keys.per_image = {one: opened[one] for one in paths}
        name = _image_name(paths[0])

        def look(source, image):
            nonlocal name
            name = source
            _gui_volume_keys(parent, source, image, keys)

        _for_each_source(paths, keys, look)
    except _open_errors() as exc:
        messagebox.showerror('Error', f'{name} could not be opened:\n{exc}', parent=parent)
        return None
    return RawInput(paths, keys, search, repeats)


class PathsTooltip:
    """A tooltip over ``widget`` listing the paths ``paths()`` returns, shown while the
    pointer is over it and there is more than one path."""

    def __init__(self, widget, paths):
        self.widget = widget
        self.paths = paths
        self.tip = None
        widget.bind('<Enter>', self.show, add='+')
        widget.bind('<Leave>', self.hide, add='+')

    def text(self):
        paths = list(self.paths() or ())
        if len(paths) < 2:
            return ''
        return f'{len(paths)} images, read together:\n' + '\n'.join(paths)

    def show(self, _event=None):
        import tkinter as tk  # pylint: disable=import-outside-toplevel
        text = self.text()
        if not text or self.tip is not None:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f'+{self.widget.winfo_rootx()}+'
                             f'{self.widget.winfo_rooty() + self.widget.winfo_height() + 2}')
        tk.Label(self.tip, text=text, justify='left', relief='solid', borderwidth=1,
                 padx=6, pady=4).pack()

    def hide(self, _event=None):
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


def names_a_stream(filepattern):
    """True when a pattern's last segment holds a ``:``, which is how a pattern
    asks for an NTFS alternate data stream (``*:Zone.Identifier``,
    ``*/$Extend/$UsnJrnl:$J``). Only such a pattern is matched against streams."""
    return ':' in filepattern.replace('\\', '/').rpartition('/')[2]


def names_a_directory_index(filepattern):
    """True when a pattern's last segment ends ``:$I30``, which is how a pattern asks
    for a directory's index allocation (``*:$I30``). Only such a pattern is matched
    against directory indexes."""
    return filepattern.replace('\\', '/').rpartition('/')[2].endswith(':$I30')


FREE_SPACE_FOLDER = '$Unallocated'
FREE_SPACE_SUFFIX = '.unallocated.bin'


DELETED_FOLDER = '$Deleted'


def names_deleted(filepattern):
    """True when a pattern asks for the deleted files a reader can recover.

    They are members of a ``$Deleted`` folder in their volume, and only a pattern
    with that folder name as one of its segments is matched against them. A broad
    pattern such as ``*`` or ``*/gps.dat*`` never reaches a deleted file, so an
    artifact gets one only by naming the folder.
    """
    return DELETED_FOLDER in filepattern.replace('\\', '/').split('/')


def names_free_space(filepattern):
    """True when a pattern's last segment ends in ``.unallocated.bin``, which is how a
    pattern asks for a volume's free space (``*.unallocated.bin``). Only such a
    pattern is matched against the free space members: a volume's free space can
    run to many gigabytes, and a broad pattern must never stage it by accident."""
    last = filepattern.replace('\\', '/').rpartition('/')[2]
    return last.lower().endswith(FREE_SPACE_SUFFIX)


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


def _raid_names(paths):
    """The name the reader's RAID report gives each image path: its file name, or, when
    two images share a file name, as many of its parent folders as tell them apart
    (qnxprobe.raid_display_names, 1.72 or later)."""
    return qnxprobe.raid_display_names(paths)


def _raid_members(images):
    """qnxprobe.raid_assemble over ``images``, [(name, open image)], or None when they
    are one image that holds no md member: such an image is read exactly as before.
    Several images always give a RaidSet, whatever they hold."""
    try:
        raid = qnxprobe.raid_assemble(images)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if len(images) == 1:
            return None
        raid = qnxprobe.RaidSet()
        raid.foreign.append(('', f'RAID members were not assembled ({type(exc).__name__}: '
                                 f'{exc})'))
        return raid
    if len(images) > 1 or raid.arrays or raid.members:
        return raid
    raid.close()
    return None


def _safe_source_name(name):
    """An image's file name made safe to start a volume name with."""
    return qnxprobe.sanitize_volume_label(name, 48) or 'image'


def _read_elsewhere(vol, covers, spans):
    """Where a volume of an image is read instead of from the image, or None: inside
    a member of an array read here, or another copy of a RAID1 member read from the
    first (``covers``, [(start, end, where)]), or a logical volume read across the
    images (``spans``, {label: volume})."""
    if vol.get('label') in spans:
        return f"read across the images as {spans[vol['label']].safe_name}"
    base = vol.get('base')
    if vol.get('lvm_map') is not None or base is None:
        return None
    for start, end, where in covers:
        if start <= base < end:
            return where
    return None


# How the reader names, in its RAID report, a physical volume of a volume group spread
# over several images: "<image> <region>: LVM2 physical volume of volume group <name>",
# with "... so this one is shown as <name>@<id>)" when two groups share the name (1.71).
_SPANNED_PV = re.compile(r'^(?P<where>.+): LVM2 physical volume of volume group (?P<name>.+?)'
                         r'(?: \(id [^;]+; .* shown as (?P<shown>[^)]+)\))?, which spans several '
                         r'images$')


def _spanned_groups(raid, image_name):
    """{region label: the group's name as its volumes' labels show it} for each
    physical volume on ``image_name`` whose volume group is read across the images,
    from the reader's own RAID report, so a group is told from another of its name by
    its id."""
    out = {}
    prefix = f'{image_name} '
    for line in raid.members.get(image_name, ()):
        found = _SPANNED_PV.match(line)
        if found and found.group('where').startswith(prefix):
            out[found.group('where')[len(prefix):]] = found.group('shown') or found.group('name')
    return out


def _as_read_here(vol, prefix, covers, spans, groups=None):
    """A copy of ``vol`` named with ``prefix``. One that an array read here covers keeps
    its line in the log and loses its walker and free space, with a note saying where
    its bytes are read, so no file is listed twice."""
    vol = dict(vol)
    if prefix and vol.get('name'):
        vol['name'] = prefix + vol['name']
    elsewhere = _read_elsewhere(vol, covers, spans)
    if elsewhere and (vol.get('walker') is not None or vol.get('free_extents') is not None):
        vol['walker'] = None
        vol['free_extents'] = None
        vol['note'] = elsewhere
    across = _group_read_across(vol, spans, groups or {})
    if across:
        # The reader's note on a physical volume says which of its group's volumes this
        # image alone cannot read; say where they are read instead.
        vol['note'] = (f"{vol['note']}; " if vol.get('note') else '') + across
    return vol


def _group_read_across(vol, spans, groups):
    """For an LVM2 physical volume whose volume group has volumes read across the
    images (``spans``), the words saying where each is read; else None. ``groups`` maps
    a region to its group as the reader shows it (see _spanned_groups)."""
    if vol.get('kind') != 'lvm2 pv' or not spans:
        return None
    group = groups.get(vol.get('label'))
    if group is None:
        return None
    read = [(label[len(f'LVM {group}/'):], arr.safe_name) for label, arr in spans.items()
            if label.startswith(f'LVM {group}/')]
    if not read:
        return None
    return ('read across the images given: '
            + ', '.join(f'{volume} as {name}' for volume, name in read))


# How many lines of a reader's damage or padding list the run log shows at once.
_SHOWN = 5

# What a file's read can raise that names its own reason, which the run log gives
# as it is: an encrypted NTFS file, and since qnxprobe 1.74 a macOS compressed file
# whose compression the reader does not decode (LZBITMAP) or whose compressed
# stream is damaged.
_REFUSALS = (qnxprobe.NtfsUnreadable, qnxprobe.ApfsUnreadable, qnxprobe.HfsUnreadable)


# The two damage lines of the reader that name a file by its record rather than by
# its path: APFS names the object id within its volume, HFS+ the catalog id.
_DAMAGE_RECORD = re.compile(r'^(object|catalog id) (\d+):')


def _acquisitions(image):
    """The images ewfprobe opened that ``image`` is read through, nearest first: the
    image itself and, for a difference disk, the disks under it. Only those keep
    ``padded_chunks`` (ewfprobe 0.14.0 or later); [] for anything else."""
    out = []
    while image is not None and len(out) < 64:
        if getattr(type(image), 'padded_chunks', None) is not None:
            out.append(image)
        image = getattr(image, 'parent', None)
    return out


def padding_lines(name, units):
    """The run log's lines for ``units``, entries of ewfprobe's ``padded_chunks``
    first met in the acquisition ``name``: how many, the zeros read in their place,
    and the first few by where they sit on the disk. The first line is a clause the
    caller starts its sentence with."""
    unit = units[0]['unit']
    zeros = sum(u['zeros'] for u in units)
    cut = sum(1 for u in units if u['cut'])
    one = len(units) == 1
    lines = [f'{len(units):,} {unit}{"" if one else "s"} of {name} whose stored data ran '
             f'out before the bytes {"it covers" if one else "they cover"} ({cut:,} with a '
             f'compressed stream cut before its end), and the reader read {zeros:,} zero '
             f'bytes in place of the data that is not there']
    for one in units[:_SHOWN]:
        where = f" of {one['file']}" if 'file' in one else ''
        lines.append(f"  {one['unit']} {one['index']:,}{where} at byte {one['offset']:,}: "
                     f"{one['decoded']:,} of {one['length']:,} bytes"
                     + (', stream cut' if one['cut'] else ''))
    if len(units) > _SHOWN:
        lines.append(f'  and {len(units) - _SHOWN:,} more')
    return lines


class _Entry:
    """Where one member lives in the image: enough to read it on demand. ``folder``
    marks the data of a logical evidence entry that is a folder as well, whose
    children are staged under the same path."""

    __slots__ = ('walker', 'node', 'size', 'mtime', 'reading', 'folder')

    def __init__(self, walker, node, size, mtime, reading='', folder=False):
        self.walker = walker
        self.node = node
        self.size = size
        self.mtime = mtime
        self.reading = reading
        self.folder = folder


class _LogicalReader:
    """Reads logical evidence entries the way a volume walker reads files, so staging
    does not need to know which it has. A node is one ewfprobe entry."""

    _CHUNK = 1 << 20

    def __init__(self, image):
        self.image = image

    def read_file(self, entry, size):
        with self.image.open_entry(entry) as fh:
            left = size
            while left > 0:
                chunk = fh.read(min(self._CHUNK, left))
                if not chunk:
                    break
                left -= len(chunk)
                yield chunk

    @staticmethod
    def stamps(entry):
        """(created, modified) as POSIX times, 0 where the evidence records none: an
        AD1 keeps "created" and "modified", an L01 cr and wr."""
        times = entry.times or {}
        return (times.get('created', times.get('cr', 0)) or 0,
                times.get('modified', times.get('wr', 0)) or 0)


class FileSeekerRaw(FileSeekerBase):
    """Search a raw disk image or an acquisition and stage the files that match.

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

    NTFS alternate data streams are members kept apart, in ``stream_list``, and
    matched only by a pattern that names a stream (see ``names_a_stream``).
    ``name_list`` is exactly what it was without them, order included.

    A volume's free space is a member too, kept apart in ``free_list`` and matched
    only by a pattern that asks for it (see ``names_free_space``). It is named
    ``<volume>/$Unallocated/<image>.<volume>.unallocated.bin``, the name the
    reader's own free space writer gives the file, and nothing is read for it until
    a pattern matches. Staging it writes the free runs one after another, with a
    ``.tsv`` beside the copy that maps each run back to its offset in the image.

    The files a reader recovers outside the live tree (a flash filesystem's deleted
    files, exFAT's orphan entries) are members of a
    ``$Deleted`` folder in their volume, listed and matched only for a pattern that
    names that folder (see ``names_deleted``).

    ``password`` is what opens the image and the encrypted volumes in it: ImageKeys,
    or a bare password, as earlier callers passed.

    ``image_path`` can also be a list of images read together, the members of a RAID
    set, and one image that holds an md member is read the same way. The images are
    assembled as the vendored reader assembles them (qnxprobe.raid_assemble): Linux md
    arrays, and LVM2 logical volumes spread over several images. Then each image is read
    as before, except its volumes that an array read here covers, and each array read
    is read as one disk of its own, so its volumes are named as any disk's are
    (``lba0``, ``p<idx>_lba<start>``). When more than one image or array is read, each
    volume name starts with the name of what holds it, so two cannot collide: the
    image's file name made safe (``disk0_img_p1_lba2048``), or the array's own name
    (``md_<name>_<first eight hex digits of its uuid>_lba0`` for an md array,
    ``lvm_<group>_<volume>_lba0`` for an LVM2 volume read across images), the name the
    reader's own extraction gives it. That name also replaces the image's file name in
    the array's free space members. ``found`` is a MemberSearch, or the paths found
    beside the image given, which the run log marks as found automatically.
    """

    def __init__(self, image_path, data_folder, password=None, found=None):
        FileSeekerBase.__init__(self)
        self.member_search, self.found, self.repeats = _what_was_given(found)
        given = image_paths(image_path)
        if len(given) > 1:
            # one disk given twice (two names, two segments of one set) is read once
            given, repeats = distinct_images(given)
            self.repeats += repeats
        self.image_paths = given
        self.image_path = self.image_paths[0]
        # the RaidSet when several images, or one image's RAID members, are read
        self.raid = None
        self._owned = []
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self.name_list = []
        self.stream_list = []
        self.index_list = []
        self.free_list = []
        self.volumes = []
        self._free = {}
        # deleted files a reader can recover, listed on the first pattern that asks
        self.deleted_list = None
        self._deleted = {}
        self._size = 0
        self._entries = {}
        # a member staged under another name than its path in the evidence: an
        # earlier entry of logical evidence that shares its path with a later one
        self._member_source = {}
        self._too_deep = 0
        self._renamed = 0
        # staged path: zero bytes read in place of acquisition data that ran out
        self.padded_files = {}
        self._image = None
        # what the run log has said of each reader's damage and of each
        # acquisition's padded units, so each is said once, when first met
        self._acquired = []
        self._padding_said = {}
        self._damage_said = {}
        self._walker_names = {}
        try:
            # the password opens an encrypted image and is not kept
            self._open(password)
        except BaseException:
            # A failed or interrupted (Ctrl-C on a slow walk) build never binds an
            # object for the run's cleanup() to reach, so release the image here.
            self.cleanup()
            raise
        self._init_dest_guard(self.data_folder)

    # ---- building the member list -------------------------------------------

    def _open(self, password=None):
        keys = password if isinstance(password, ImageKeys) else ImageKeys(password=password)
        for line in repeat_lines(self.repeats):
            logfunc(line)
        if len(self.image_paths) > 1:
            self._open_several(keys)
            return
        name = os.path.basename(self.image_path)
        logical = open_logical(self.image_path, keys)
        if logical is not None:
            self._image = logical
            self._acquired += [(name, one) for one in _acquisitions(logical)]
            self._open_logical(name, logical)
            return
        logfunc(f'Reading {name} in place with the vendored qnxprobe '
                f'{qnxprobe.QNXPROBE_VERSION}; only the files an artifact asks for '
                f'leave the image.')
        if self.member_search is not None:
            # the search beside it ran, and found nothing or was not taken up
            for line in self.member_search.lines():
                logfunc(line)
        self._image, size = self._open_one(self.image_path, keys)
        self._size = size
        # One image that holds a member of an md array (a disk of a RAID set, or a
        # disk whose own partitions form one) is read with its arrays; any other
        # image is read exactly as before.
        raid = _raid_members([(_raid_names([self.image_path])[0], self._image)])
        if raid is not None:
            self._open_raid([(self.image_path, name, self._image, size)], raid, keys)
            return
        self._image = self._read_source(self._image, size, name, keys)
        self._listing_complete()

    def _open_one(self, path, keys):
        """Open one image (raw, split, or an acquisition) and say what it is. Returns
        (image, size)."""
        name = os.path.basename(path)
        # an acquisition's reader joins its own files; a raw set FTK Imager encrypted
        # is numbered like a split image and its files are ciphertext until then
        acquisition = qnxprobe.acquisition_format(path)
        sibling = None if acquisition else split_image_sibling(path)
        if sibling:
            logfunc(f'{name} is one segment of a split image: '
                    f'{os.path.basename(sibling)} sits beside it. The reader joins '
                    f'every segment of the set in order.')
        # A set with a hole in its numbering raises SplitImageError here, by
        # name, and the run stops with that message rather than reading half a
        # disk as though it were whole.
        try:
            segments = [] if acquisition else qnxprobe.split_segments(path)
        except qnxprobe.SplitSegmentSizeError as exc:
            # qnxprobe's own advice names an option of its command line; this tool
            # has none, so say what to do here instead
            odd = ', '.join(f'{os.path.basename(exc.segments[i])} is {exc.sizes[i]:,} '
                            f'bytes' for i in exc.odd[:3])
            raise qnxprobe.SplitImageError(
                f'{name} is one segment of a split image whose segments are not one '
                f'size: {os.path.basename(exc.segments[0])} is {exc.sizes[0]:,} bytes '
                f'and {odd}. Not read: a segment cut short or padded would put every '
                f'byte after it at the wrong offset. Compare the segments with the '
                f"acquisition's own record. If the set is whole as it is, join the "
                f'segments into one file in order and give that file.') from None
        image = qnxprobe.open_image(path, segments, password=keys.password_for(path),
                                    private_key=keys.private_key_for(path))
        size = qnxprobe.image_size(image)
        self._acquired += [(name, one) for one in _acquisitions(image)]
        if segments:
            logfunc(f'  {len(segments):,} segments joined in order, '
                    f'{os.path.basename(segments[0])} .. '
                    f'{os.path.basename(segments[-1])}')
            # later segments that begin as a disk does may be separate disks named
            # like one split image (qnxprobe.split_structure_warning, 1.72 or later)
            warning = qnxprobe.split_structure_warning(segments)
            if warning:
                logfunc(f'  {warning}')
        elif getattr(image, 'paths', None):
            # the container and its segment or file count, as the reader reports it
            logfunc(f'  {qnxprobe.describe_acquisition(image)}')
        logfunc(f'  {size:,} bytes ({qnxprobe.human(size)})')
        return image, size

    def _open_several(self, keys):
        """Open each of several images, say which were given and which found, and
        read them together (_open_raid)."""
        count = len(self.image_paths)
        logfunc(f'Reading {count} images together in place with the vendored qnxprobe '
                f'{qnxprobe.QNXPROBE_VERSION}, as the members of the RAID arrays and LVM2 '
                f'volume groups they hold; only the files an artifact asks for leave them.')
        if self.member_search is not None:
            for line in self.member_search.lines():
                logfunc(line)
        given = []
        for number, path in enumerate(self.image_paths, start=1):
            name = os.path.basename(path)
            logical = open_logical(path, keys)
            if logical is not None:
                logical.close()
                raise ValueError(f'{name} is logical evidence (an L01 or AD1), which holds '
                                 f'files rather than a disk and is read on its own, not '
                                 f'with other images')
            how = FOUND_AUTOMATICALLY if path in self.found else 'given'
            logfunc(f'Image {number} of {count}: {name} ({how}), {path}')
            image, size = self._open_one(path, keys)
            self._owned.append(image)
            given.append((path, name, image, size))
        self._image, self._size = given[0][2], given[0][3]
        named = zip(_raid_names([path for path, _n, _i, _s in given]),
                    (image for _p, _n, image, _s in given))
        self._open_raid(given, _raid_members(list(named)), keys)

    def _open_raid(self, given, raid, keys):
        """Read images that hold RAID members, ``given`` as [(path, name, image, size)]:
        what assembly found, then each image's volumes, except those an array read here
        covers, then each array or volume read across the images, as a disk of its own."""
        self.raid = raid
        # find_members=True: the reader's own hint names its --find-members option,
        # which this tool does not have; its own search beside one image (see
        # find_members) runs before this unless turned off, and says what it found.
        qnxprobe.raid_report(raid, say=logfunc, images_given=len(given), find_members=True)
        for line in self._partial_array_lines(raid, len(given)):
            logfunc(line)
        # A RAID1 array whose data starts at the first byte of its first member (metadata
        # 0.90 or 1.0) is not read again, as the reader's own run does not read it: that
        # member's own volume is the same bytes and is read, and the other members'
        # copies are not, so no file is listed twice.
        read = [arr for arr in raid.arrays
                if arr.image is not None and not getattr(arr, 'same_as', None)]
        covered = {}
        for arr in read:
            for member in getattr(arr, 'members', None) or ():
                covered.setdefault(id(member['fh']), []).append(
                    (member['base'], member['base'] + member['size'],
                     f'inside a member of {arr.label}, read as {arr.safe_name}'))
        for arr in raid.arrays:
            if arr.image is None or not getattr(arr, 'same_as', None):
                continue
            first = min(arr.members, key=lambda member: member['role'])
            for member in arr.members:
                if member is not first:
                    covered.setdefault(id(member['fh']), []).append(
                        (member['base'], member['base'] + member['size'],
                         f"a copy in {arr.label} of what {first['where']} holds, which is "
                         f'read there'))
        across = {arr.label: arr for arr in read if isinstance(arr, qnxprobe.LvmSpanned)}
        # the report names each image as it was assembled (_raid_names); the volume
        # names keep the file name
        shown = _raid_names([path for path, _n, _i, _s in given])
        sources = [(name, _safe_source_name(name), image, size, name,
                    covered.get(id(image), ()), across, _spanned_groups(raid, raid_name))
                   for (_path, name, image, size), raid_name in zip(given, shown)]
        sources += [(f'{arr.label} ({arr.safe_name})', arr.safe_name, arr.image,
                     arr.image.size, arr.safe_name, (), {}, {}) for arr in read]
        several = len(sources) > 1
        taken = set()
        for title, stem, image, size, image_name, covers, spans, groups in sources:
            # two images whose names make the same safe name are told apart by number
            unique, number = stem, 1
            while unique in taken:
                number += 1
                unique = f'{stem}_{number}'
            taken.add(unique)
            prefix = f'{unique}_' if several else ''
            logfunc(f'Volumes of {title}' + (f', each named {unique}_<volume>:' if several
                                              else ':'))
            unlocked = self._read_source(image, size, image_name, keys, prefix, covers, spans,
                                         groups)
            if unlocked is not image:
                self._owned.append(unlocked)
        self._listing_complete()

    def _partial_array_lines(self, raid, images_given):
        """For each array or volume group not read because members are not among the
        images given: which, and how to give them. The search beside one image is named
        when it did not run (turned off) or its finds were not taken."""
        search = self.member_search
        off = (search is None and images_given == 1) or (search is not None and not search.used)
        out = []
        for arr in raid.arrays:
            if arr.image is not None:
                continue
            if isinstance(arr, qnxprobe.LvmSpanned):
                missing = list(getattr(arr, 'absent', None) or ())
                what = f"its physical volume(s) {', '.join(missing)} are"
            else:
                missing = list(getattr(arr, 'not_given', None) or ())
                total = getattr(getattr(arr, 'sb', None), 'raid_disks', None)
                what = (f"role(s) {', '.join(map(str, missing))}"
                        + (f' of {total}' if total else '') + ' are')
            if not missing:
                continue
            out.append(f'{arr.label}: {what} not in the images given. Give the other member '
                       f'images with it (several paths to -i, or several files picked '
                       f'together)'
                       + (', or leave member finding on to look for them beside the image '
                          'given' if off else '') + '.')
        return out

    def _read_source(self, image, size, image_name, keys, prefix='', covers=(), spans=None,
                     groups=None):
        """Open the encrypted volumes ``keys`` open, list the volumes of ``image``, walk
        each one the reader reads, and offer its free space. Returns the image as
        unlocked. ``prefix`` starts each volume's name; a volume inside a region in
        ``covers`` [(start, end, where it is read)], or named in ``spans`` {label: volume
        read across the images}, is listed and not walked, because it is read there."""
        # A BitLocker volume the keys open reads as the filesystem inside it, and an
        # encrypted APFS volume they open is read decrypted; one they do not open is
        # listed with the reason and nothing in it is searched.
        image, _found = qnxprobe.unlock_bitlocker(
            image, size, keys.bitlocker_passwords(), keys.bitlocker_keys)
        image, _apfs_found = qnxprobe.unlock_apfs(image, size, keys.apfs_passwords())
        # A LUKS container a passphrase opens reads as what it holds, a region of
        # its own; one none opens is listed with the reason.
        image, _luks_found = qnxprobe.unlock_luks(image, size, keys.luks_passwords())
        volumes = qnxprobe.volumes(image, size)
        if prefix or covers or spans or groups:
            volumes = [_as_read_here(vol, prefix, covers, spans or {}, groups)
                       for vol in volumes]
        self.volumes += volumes
        if not volumes:
            logfunc('  no partition table and no filesystem the reader knows: '
                    'nothing to search')
        for vol in volumes:
            note = vol.get('note')
            line = (f"  {vol['name'] or vol['label']:<40} {vol['kind']:<16} "
                    f"{qnxprobe.human(vol['size'] or 0):>10}")
            if vol['label'] and vol['name']:
                line += f"   {vol['label']}"
            if vol.get('encryption') and vol['kind'] != 'bitlocker':  # a locked one's note says
                line += f"   [{vol['encryption']}]"
            if note:
                line += f'   ({note})'
                if 'damage' in note and vol.get('walker') is not None:
                    # the reader's note already counts what it had met by now
                    self._damage_said[id(vol['walker'])] = qnxprobe.damage_lines(
                        vol['walker'], limit=0)[0]
            logfunc(line)

        # A partition table describes a whole disk and the file may hold only
        # the front of it: a lone first segment of a split image reads this way,
        # its boot volumes whole and the volume holding the user data cut. Say
        # so before any of its files is staged.
        short = [v for v in volumes if v.get('missing_past_end')]
        if short:
            logfunc('WARNING: the image is shorter than the volumes it describes. '
                    'Rows from these volumes come from an incomplete read:')
            for vol in short:
                logfunc(f"  {vol['name'] or vol['label']}: reaches "
                        f"{vol['missing_past_end']:,} bytes past the end of the image")
            logfunc('  If this is a numbered segment of a split image, the rest of the '
                    'set is not beside it: the reader joins every segment it finds in '
                    'the same folder.')

        for vol in volumes:
            walker = vol.get('walker')
            if walker is None:
                continue
            started = timex.monotonic()
            deep_before = self._too_deep
            files, dirs, streams, route = self._walk(walker, vol['name'])
            logfunc(f"  walked {vol['name']}: {files:,} files, {dirs:,} directories "
                    f"in {timex.monotonic() - started:.1f}s ({route})")
            if self._too_deep > deep_before:
                logfunc(f'  WARNING: {self._too_deep - deep_before:,} directories sit '
                        f'more than {_MAX_DEPTH} levels deep in {vol["name"]} and were '
                        f'not walked; the files under them are not listed')
            if streams:
                logfunc(f'    and {streams:,} alternate data streams, matched only by a '
                        f'pattern that names one')
            self._walker_names[id(walker)] = vol['name']
            for line in self._new_damage(walker):
                logfunc(f'    {line}')
        for vol in volumes:
            # a filesystem that reports its free space, or an LVM2 physical volume,
            # whose extents no logical volume holds are its free space
            if (getattr(vol.get('walker'), 'free_extents', None) is None
                    and vol.get('free_extents') is None):
                continue
            member = (f"{vol['name']}/{FREE_SPACE_FOLDER}/"
                      f"{image_name}.{vol['name']}{FREE_SPACE_SUFFIX}")
            self.free_list.append(member)
            self._free[member] = (vol, image, size, image_name)
        return image

    def _listing_complete(self):
        self._say_padding('  WARNING: the listing read ')
        if self.free_list:
            logfunc(f'  {len(self.free_list):,} volumes can give their free space, to a '
                    f'pattern that asks for it (*{FREE_SPACE_SUFFIX})')
        if self.index_list:
            logfunc(f'  {len(self.index_list):,} directories can give their index, to a '
                    f'pattern that asks for it (*:$I30)')
        logfunc(f'File listing complete - {len(self.name_list):,} members'
                + (f' and {len(self.stream_list):,} streams' if self.stream_list else ''))

    def _open_logical(self, name, image):
        """List the entries of logical evidence as members, under their paths in it."""
        kind = 'an AD1' if image.format == _ewfprobe.FORMAT_AD1 else 'an L01'
        logfunc(f'Reading {name}, {kind} (logical evidence), in place with the vendored '
                f'ewfprobe {_ewfprobe.__version__}; only the files an artifact asks for '
                f'leave it.')
        if getattr(image, 'encryption', None):
            logfunc(f"  encrypted ({image.encryption.get('cipher', '')}, "
                    f"{image.encryption.get('container', '')})")
        started = timex.monotonic()
        files, dirs, streams, left_out = self._walk_logical(image)
        logfunc(f'  walked {name}: {files:,} files, {dirs:,} folders in '
                f'{timex.monotonic() - started:.1f}s')
        if streams:
            logfunc(f'    and {streams:,} alternate data streams, matched only by a '
                    f'pattern that names one')
        for why, count in sorted(left_out.items()):
            logfunc(f'  not searched: {count:,} {why}')
        if self._renamed:
            logfunc(f'  {self._renamed:,} entries share their path with a later entry. '
                    f'An artifact matching the path is handed both: the later one '
                    f'staged under the path, each earlier one beside it as '
                    f'<name>~entry-<N><ext>, N its position in the evidence, both with '
                    f'the path in the evidence as their source.')
        self._say_padding('  WARNING: the listing read ')
        logfunc(f'File listing complete - {len(self.name_list):,} members'
                + (f' and {len(self.stream_list):,} streams' if self.stream_list else ''))

    def _walk_logical(self, image):
        """Register the entries of logical evidence in the order it stores them (a
        folder's children before its next sibling), each under its path in the
        evidence. Returns (files, folders, streams, {what was left out: count}).

        An AD1 marks what each entry is. An NTFS alternate data stream (type D) is
        ``<file>:<stream>`` beside its file, as on a disk. Its deleted entries, and the
        file slack, index and attribute records FTK Imager keeps beside a file
        (_AD1_NOT_FILES), are not members, as a disk's deleted records are not; every
        other entry is, files of type 1 and 11 among them. An L01 marks no such kinds:
        every entry is a member, and one that is a folder and holds data too is both a
        folder and a file of the same name.
        """
        reader = _LogicalReader(image)
        ad1 = image.format == _ewfprobe.FORMAT_AD1
        member_of = {}
        position_of = {}
        files = dirs = streams = 0
        left_out = {}

        def leave(why):
            left_out[why] = left_out.get(why, 0) + 1

        for position, entry in enumerate(image.logical_entries):
            path = entry.path
            if not path:
                continue
            times = reader.stamps(entry)
            if ad1 and entry.is_deleted:
                leave('deleted entries')
                continue
            code = entry.type_code if ad1 else None
            if ad1 and code == 'D':
                parent = member_of.get(id(entry.parent))
                if parent is None:
                    leave('streams of entries not listed')
                    continue
                name = f'{parent}:{entry.name}'
                self.stream_list.append(name)
                self._entries[name] = _Entry(reader, entry, entry.size, times[1])
                streams += 1
                continue
            if entry.is_folder:
                self.name_list.append(path + '/')
                self._entries[path + '/'] = None
                member_of[id(entry)] = path
                dirs += 1
                if ad1 or not entry.size:
                    continue
            elif ad1 and code in _AD1_NOT_FILES:
                leave(_AD1_NOT_FILES[code])
                continue
            if path in position_of:
                # Two entries at one path. The later keeps the name, as it always
                # has; the earlier is staged beside it, so its bytes still reach an
                # artifact, and its source path stays the path in the evidence.
                base, ext = os.path.splitext(path)
                earlier = f'{base}~entry-{position_of[path]}{ext}'
                self._entries[earlier] = self._entries[path]
                self._member_source[earlier] = path
                self.name_list.append(earlier)
                self._renamed += 1
            else:
                self.name_list.append(path)
            position_of[path] = position
            self._entries[path] = _Entry(reader, entry, entry.size, times[1],
                                         folder=entry.is_folder)
            member_of[id(entry)] = path
            files += 1
        return files, dirs, streams, left_out

    def _new_damage(self, walker):
        """The run log's lines for what ``walker`` recorded as damage since they were
        last asked for (qnxprobe.damage_lines), or []: how many, and the first few."""
        said = self._damage_said.get(id(walker), 0)
        count, lines = qnxprobe.damage_lines(walker, limit=said + _SHOWN)
        if count <= said:
            return []
        self._damage_said[id(walker)] = count
        name = self._walker_names.get(id(walker), 'the volume')
        new = count - said
        out = [f'damage the reader recorded in {name}: {new:,} '
               f'{"entry" if new == 1 else "entries"}']
        out += [f'  {self._name_damage(walker, line)}' for line in lines[said:]]
        if new > _SHOWN:
            out.append(f'  and {new - _SHOWN:,} more')
        return out

    def _name_damage(self, walker, line):
        """``line`` with the member it is about added, when the reader names a file by
        its APFS object id or HFS+ catalog id and exactly one member listed from
        ``walker`` has that record; otherwise ``line`` as the reader wrote it. An APFS
        object id is counted within its volume, so one a container's volumes share
        names no member."""
        found = _DAMAGE_RECORD.match(line)
        if found is None:
            return line
        number = int(found.group(2))
        apfs = found.group(1) == 'object'
        named = [member for member, entry in self._entries.items()
                 if entry is not None and entry.walker is walker
                 and isinstance(entry.node, int)
                 and (entry.node & qnxprobe.APFS_OID_MASK if apfs else entry.node) == number]
        return f'{named[0]}: {line}' if len(named) == 1 else line

    def _new_padding(self):
        """For each acquisition read so far, the run log's lines (padding_lines) for
        its units whose stored data ran out (ewfprobe's ``padded_chunks``) and that
        were not said before: a list of line lists, one per acquisition, or []."""
        out = []
        for name, image in self._acquired:
            seen = self._padding_said.setdefault(id(image), set())
            units = [u for u in image.padded_chunks
                     if (u['unit'], u['index'], u.get('file')) not in seen]
            if units:
                seen.update((u['unit'], u['index'], u.get('file')) for u in units)
                out.append(padding_lines(name, units))
        return out

    def _say_padding(self, start, end=''):
        """Write _new_padding() to the run log, each acquisition's first line as a
        WARNING that starts with ``start`` and ends with ``end``."""
        for lines in self._new_padding():
            logfunc(f'{start}{lines[0]}{end}')
            for line in lines[1:]:
                logfunc(f'{" " * (len(start) - len(start.lstrip()))}{line}')

    def _zeros_read(self):
        """Zero bytes the acquisitions read so far have handed out where their data
        ran out (ewfprobe's ``padded_zeros_read``, 0.15.0 or later). Each is taken
        from the image the walker reads, which counts its parents' too, so a parent
        is not counted twice."""
        images = [image for _, image in self._acquired]
        parents = {id(getattr(image, 'parent', None)) for image in images}
        return sum(getattr(image, 'padded_zeros_read', 0) for image in images
                   if id(image) not in parents)

    def _say_met(self, member):
        """Say what reading ``member`` met that was not said before: the damage its
        volume's reader recorded, and the acquisition units it read whose stored data
        ran out, so zeros were read in their place and the copy can hold them."""
        entry = self._entries.get(member)
        walker = entry.walker if entry is not None else None
        damage = self._new_damage(walker) if walker is not None else []
        if damage:
            logfunc(f'While reading {member}, {damage[0]}')
            for line in damage[1:]:
                logfunc(f'  {line}')
        self._say_padding(f'WARNING: reading {member} met ',
                          ', so what was staged for it can hold those zeros')

    def _walk(self, walker, prefix):
        """Register every file and directory under a volume's root, and the
        alternate data streams of each when the walker has them.

        Returns (files, directories, streams, route), where route names how the
        entries were read, for the run log.

        A volume is walked one directory at a time: list its children, read each
        child's entry, descend. On NTFS that means reading every directory's index
        and reaching the MFT records in directory order, and on APFS it means
        searching the catalog tree once per lookup. The reader offers a faster
        way to have the same entries on both: one pass over $MFT for NTFS
        (walker.listing) and one pass over the catalog's leaves for APFS
        (walker.prime_records). On a 7.4 GB Windows acquisition the listing went
        from 6.9 s to 2.0 s, and on a 32 GB macOS one from 147.0 s to 8.0 s.

        Only where the entries come from changes. The traversal below is the one
        this has always used, depth first with each directory's children sorted
        by name, and the member list is the order search() hands artifacts their
        files in, so it stays exactly what it was. Everything else is walked as
        before.
        """
        by_directory = self._one_pass_listing(walker)
        if by_directory is not None:
            route = 'one pass over $MFT'
        else:
            route = 'directory by directory'
            prime = getattr(walker, 'prime_records', None)
            if prime is not None:
                try:
                    prime()
                    route = 'one pass over the catalog'
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logfunc(f'  could not read the catalog in one pass ({type(exc).__name__}: '
                            f'{exc}); searching it once per lookup instead')
        files = dirs = 0
        streams_of = getattr(walker, 'streams', None)
        streams = self._add_streams(streams_of, walker, walker.root, prefix + '/', 0, '')
        seen = set()
        stack = [(walker.root, prefix, 0, '')]
        while stack:
            node, path, depth, within = stack.pop()
            if node in seen:
                continue
            if depth > _MAX_DEPTH:
                self._too_deep += 1
                continue
            seen.add(node)
            try:
                if by_directory is not None:
                    listing = list(by_directory.get(within, ()))
                elif hasattr(walker, 'listdir_records'):
                    # FAT and exFAT keep wall-clock readings rather than instants;
                    # the reader hands them back as text beside each entry.
                    listing = [(name, child, (recorded or {}).get('modified', ''), None)
                               for name, child, recorded in walker.listdir_records(node)]
                else:
                    listing = [(name, child, '', None) for name, child in walker.listdir(node)]
                listing.sort(key=lambda item: item[0])
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logfunc(f'Could not list {path}/ in the image: {exc}')
                continue
            for child_name, child, reading, known in listing:
                try:
                    ent = known if known is not None else walker.entry(child)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logfunc(f'Could not read the entry for {path}/{child_name}: {exc}')
                    continue
                if not ent:
                    continue
                mode, size, mtime = ent
                member = f'{path}/{child_name}'
                # The format bits, not the directory bit alone: a socket (0o140000)
                # and a block device (0o060000) carry S_IFDIR's bit too.
                if mode & qnxprobe.S_IFMT == qnxprobe.S_IFDIR:
                    self.name_list.append(member + '/')
                    self._entries[member + '/'] = None
                    dirs += 1
                    stack.append((child, member, depth + 1,
                                  f'{within}/{child_name}' if within else child_name))
                elif (mode & 0o170000) == 0o100000:          # regular files only
                    self.name_list.append(member)
                    self._entries[member] = _Entry(walker, child, size or 0, mtime or 0, reading)
                    files += 1
                else:
                    continue
                streams += self._add_streams(streams_of, walker, child, member,
                                             mtime, reading)
        return files, dirs, streams, route

    def _add_streams(self, streams_of, walker, node, member, mtime, reading):
        """Register the alternate data streams of one file or directory as
        ``<member>:<stream>``, beside it but out of ``name_list``. Returns how
        many. A stream carries its file's dates, since NTFS keeps none per
        stream, and the size the reader will return for it."""
        if streams_of is None:
            return 0
        try:
            found = streams_of(node)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logfunc(f'Could not list the streams of {member}: {exc}')
            return 0
        for name, stream_node, size in found:
            name = f'{member}:{name}'
            self.stream_list.append(name)
            self._entries[name] = _Entry(walker, stream_node, size or 0, mtime or 0, reading)
        # A directory's $I30 index allocation, where the reader offers it (qnxprobe 1.63
        # or later): a member of its own kind, counted apart from the streams.
        index_of = getattr(walker, 'directory_index', None)
        if index_of is not None:
            try:
                for name, index_node, size in index_of(node):
                    name = f'{member}:{name}'
                    self.index_list.append(name)
                    self._entries[name] = _Entry(walker, index_node, size or 0, mtime or 0, reading)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logfunc(f'Could not list the directory index of {member}: {exc}')
        return len(found)

    @staticmethod
    def _one_pass_listing(walker):
        """Every entry of the volume, grouped by the directory holding it, or None.

        {directory path within the volume: [(name, node, reading, (mode, size,
        mtime))]}, built from a walker's one-pass listing, which NTFS offers.
        None when the walker has none, or when the pass fails part way: the
        caller then walks the volume directory by directory, which reports what
        it cannot read one entry at a time and carries on.

        A tree walk and this read the volume differently: the first asks each
        directory what it holds, this asks each record what it is called. They
        agree on every consistent volume measured. On two Windows acquisitions
        they differ, by 4 of the 313,892 members this lists on one and by 3 of
        181,521 on the other, where a directory's index holds an entry for a
        file at an older sequence number than the file's own record carries:
        the tree walk rightly refuses the entry and so loses a file whose
        record is live. The reader's NtfsWalker.listing says which and what is
        known about why. Two records naming the same file in the same directory
        is that same disagreement: the first in record order is kept, so a path
        is never listed twice.
        """
        listing = getattr(walker, 'listing', None)
        if listing is None:
            return None
        by_directory, taken, clashes = {}, set(), 0
        try:
            for path, node, mode, size, mtime, recorded in listing():
                parent, _slash, name = path.rpartition('/')
                if (parent, name) in taken:
                    clashes += 1
                    continue
                taken.add((parent, name))
                by_directory.setdefault(parent, []).append(
                    (name, node, (recorded or {}).get('modified', ''), (mode, size, mtime)))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logfunc(f'  the one-pass listing failed ({type(exc).__name__}: {exc}); '
                    f'walking the volume directory by directory instead')
            return None
        if clashes:
            logfunc(f'  {clashes:,} name(s) were claimed by more than one record in the '
                    f'same directory; the first in record order was kept')
        return by_directory

    # ---- searching and staging ----------------------------------------------

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        members = self.name_list
        if self.stream_list and names_a_stream(filepattern):
            members = self.name_list + self.stream_list
        if self.index_list and names_a_directory_index(filepattern):
            members = members + self.index_list
        if self.free_list and names_free_space(filepattern):
            members = members + self.free_list
        if names_deleted(filepattern):
            if self.deleted_list is None:
                self._list_deleted()
            members = members + self.deleted_list
        for member in members:
            # matched by its path in the evidence, which a renamed member keeps
            if pat(root + normcase(self._member_source.get(member, member))) is None:
                continue
            if member not in self.copied or force:
                zeros_before = self._zeros_read()
                try:
                    staged = self._stage(member)
                except OSError as ex:
                    logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                    continue
                finally:
                    self._say_met(member)
                if staged is None:
                    continue
                zeros = self._zeros_read() - zeros_before
                if zeros:
                    # counted on every read (ewfprobe 0.15.0), so a file that reads a
                    # damaged unit after another file did is named too
                    self.padded_files[staged] = zeros
                    logfunc(f'WARNING: {member} was read through acquisition data '
                            f'that ran out: {zeros:,} zero bytes were read in its '
                            f'place, so what was staged for it can hold zeros')
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
        the reader refused it (an encrypted NTFS file), it raised part way, the
        image ends before the file does, or the volume records fewer clusters
        for the file than its size needs. Each case is logged by name; a
        partial or empty copy is never left where a pattern could find it,
        because a truncated database parses as a smaller one, not as an error.
        """
        if member in self._free:
            return self._stage_free_space(member)
        if member in self._deleted:
            return self._stage_deleted(member)
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
        if entry.folder:
            # Logical evidence can hold data under a folder's own name; the folder
            # keeps the name so its children stage beneath it, and the data takes
            # the guard's alternative beside it.
            os.makedirs(intended, exist_ok=True)
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
        except _REFUSALS as exc:
            # the reader says why, in words: an encrypted NTFS file, or a macOS
            # compressed file it does not decode (LZBITMAP) or whose stream is damaged
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
            # A copy of the wrong length must not reach an artifact, because a
            # database cut short parses as a smaller one rather than as an error.
            self._discard(dest_path)
            # A FAT32 or exFAT volume records a file's size in its directory
            # entry and its clusters in the allocation table, and can hold the
            # two in disagreement. A read that stops where the chain does is
            # then what the volume describes, not something the reader lost.
            cut = qnxprobe.chain_shortfall(entry.walker, entry.node)
            if cut and got < entry.size:
                logfunc(f'Not staged, {member}: the volume records {entry.size:,} bytes '
                        f'for it and a cluster chain that ends after {cut[0]:,} of the '
                        f'{cut[1]:,} clusters that size needs ({got:,} bytes read)')
                return None
            # The image holds the whole file, the volume does not account for
            # the difference, and the reader still returned another length.
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
        self.file_infos[dest_path] = FileInfo(self._member_source.get(member, member),
                                              created, modified)
        return dest_path

    def _list_deleted(self):
        """List the deleted files each volume's reader can recover, once.

        A reader that offers both ``recover_deleted()`` and ``read_deleted()`` is
        asked (the flash filesystems EFS, JFFS2, UBIFS and YAFFS, and exFAT for its
        orphan entries). Each entry it
        calls recoverable becomes one member:

            <volume>/$Deleted/<folder>/<name>.deleted-<n>

        <folder> is the entry's folder when the reader could place it and
        ``$NoFolder`` when not; an entry with no name is ``$NoName``; <n> counts
        the volume's entries in the order the reader gave them, so two versions of
        one file stay apart. An entry the reader cannot read whole is counted and
        not listed.
        """
        self.deleted_list = []
        for vol in self.volumes:
            walker = vol.get('walker')
            if getattr(walker, 'recover_deleted', None) is None \
                    or getattr(walker, 'read_deleted', None) is None:
                continue
            listed = refused = 0
            try:
                for number, entry in enumerate(walker.recover_deleted()):
                    if not entry.recoverable:
                        refused += 1
                        continue
                    folder = entry.parent_path
                    folder = '$NoFolder' if folder is None else folder.strip('/')
                    name = entry.name or '$NoName'
                    parts = [vol['name'], DELETED_FOLDER, folder, f'{name}.deleted-{number:06d}']
                    member = '/'.join(part for part in parts if part)
                    self._deleted[member] = (walker, entry)
                    self.deleted_list.append(member)
                    listed += 1
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # One volume the reader cannot finish must not end the run.
                logfunc(f"  deleted files of {vol['name']}: the reader raised "
                        f'{type(exc).__name__}: {exc}')
            if listed or refused:
                logfunc(f"  {vol['name']}: {listed:,} files outside the live tree can be read, "
                        f'{refused:,} are named and cannot')

    def _stage_deleted(self, member):
        """Copy one recovered deleted file out of the image. Returns the staged
        path, or None when the reader could not give it."""
        walker, entry = self._deleted[member]
        dest_path = self._intended_path(member)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            content = walker.read_deleted(entry)
            with open(dest_path, 'wb') as fout:
                if isinstance(content, (bytes, bytearray)):
                    fout.write(content)
                else:
                    for chunk in content:
                        fout.write(chunk)
        except OSError:
            self._discard(dest_path)
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._discard(dest_path)
            logfunc(f'Not staged, {member}: the reader raised {type(exc).__name__}: {exc}')
            return None
        modified = entry.mtime or 0
        if modified:
            try:
                os.utime(dest_path, (modified, modified))
            except (OSError, OverflowError, ValueError):
                pass
        self.file_infos[dest_path] = FileInfo(member, 0, modified)
        return dest_path

    def _stage_free_space(self, member):
        """Write one volume's free space under the data folder. Returns the staged
        path, or None when the volume gave none.

        The reader's own writer does the work, so what an examiner gets here is
        what ``qnxprobe --unallocated`` writes: the free runs in order, a ``.tsv``
        beside them mapping each run to its offset in the image, a run past the
        end of a partial image cut there, and nothing written when the volume's
        allocation map could not be read or reports nothing free.
        """
        vol, image, size, image_name = self._free[member]
        intended = self._intended_path(member)
        out_dir = os.path.dirname(intended)
        os.makedirs(out_dir, exist_ok=True)
        if os.path.isfile(intended):
            # a forced second search: the writer never overwrites, and the copy is there
            return intended
        records = qnxprobe.write_unallocated(image, size, [vol], out_dir, image_name,
                                             say=logfunc)
        record = records[0] if records else {}
        if record.get('status') != 'written':
            logfunc(f"Not staged, {member}: {record.get('status', 'no free space reported')}")
            return None
        staged = os.path.join(out_dir, record['file'])
        self.file_infos[staged] = FileInfo(member, 0, 0)
        return staged

    @staticmethod
    def _discard(path):
        try:
            os.remove(path)
        except OSError:
            pass

    def cleanup(self):
        image, self._image = self._image, None
        owned, self._owned = self._owned, []
        for one in [image] + owned:
            if one is not None:
                try:
                    one.close()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
        raid, self.raid = self.raid, None
        if raid is not None:
            raid.close()
