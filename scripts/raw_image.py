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
volume macOS encrypted in software with its password or personal recovery key. The
GUI asks for each; the command line takes a password from ``--image_password_file``
or ``--image_password_env`` (tried on the image and on any BitLocker or encrypted
APFS volume in it), a private key from ``--image_private_key`` and startup keys from
``--bitlocker_key``, or asks at a terminal. What is given is checked against the
image before the run and never stored; a BitLocker or APFS volume left locked is
reported and its files are not searched.

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

This file is shared by iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP and is kept
byte-identical across them. It names nothing specific to a platform; the
platform is in the artifacts.
"""

import getpass
import os
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
RAW_IMAGE_FILESYSTEMS = ('QNX6, QNX4, ETFS, EFS, ext2/3/4, F2FS, FAT32, exFAT, NTFS, '
                         'HFS+, APFS, SquashFS, JFFS2, UBI, UBIFS, YAFFS, QNX IFS, '
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
    APFS. Nothing here is written anywhere; it lasts as long as the run.
    """

    __slots__ = ('password', 'private_key', 'bitlocker_secrets', 'bitlocker_keys',
                 'apfs_secrets')

    def __init__(self, password=None, private_key=None, bitlocker_secrets=(),
                 bitlocker_keys=(), apfs_secrets=()):
        self.password = password
        self.private_key = private_key
        self.bitlocker_secrets = list(bitlocker_secrets)
        self.bitlocker_keys = list(bitlocker_keys)
        self.apfs_secrets = list(apfs_secrets)

    def bitlocker_passwords(self):
        """Every secret to try on a BitLocker volume, the image's password first."""
        return ([self.password] if self.password else []) + self.bitlocker_secrets

    def apfs_passwords(self):
        """Every secret to try on an encrypted APFS volume, the image's password first."""
        return ([self.password] if self.password else []) + self.apfs_secrets


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
        image = _ewfprobe.open_ewf(path, password=keys.password, private_key=keys.private_key)
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


def _unlock_bitlocker(path, keys, ask):
    """Try ``keys`` on each BitLocker volume in the image at ``path`` and offer every
    volume they leave locked to ``ask(bitlocker, wrong)`` until it opens: ``ask``
    returns ('secret', text) for a password or recovery password, ('key', path) for a
    startup key file, or None to leave it locked. What opens a volume is added to
    ``keys``. Returns the volumes still locked that something could have opened, as
    (label, locked note) pairs. Logical evidence holds no volumes."""
    logical = open_logical(path, keys)
    if logical is not None:
        logical.close()
        return []
    left = []
    with qnxprobe.open_image(path, password=keys.password,
                             private_key=keys.private_key) as image:
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
            if _askable(bitlocker):
                left.append((bitlocker.label, bitlocker.locked_note()))
    return left


def _unlock_apfs(path, keys, ask):
    """Try ``keys`` on each encrypted APFS volume in the image at ``path`` whose blocks
    are ciphertext there, and offer every volume they leave locked to ``ask(lock,
    wrong)`` until it opens: ``ask`` returns a password or personal recovery key, or
    None to leave it locked. What opens a volume is added to ``keys``. Returns the
    volumes still locked that a password could have opened, as (name, locked note)
    pairs, the name saying which volume of which region. Logical evidence holds no
    volumes."""
    logical = open_logical(path, keys)
    if logical is not None:
        logical.close()
        return []
    left = []
    with qnxprobe.open_image(path, password=keys.password,
                             private_key=keys.private_key) as image:
        _fh, found = qnxprobe.unlock_apfs(image, qnxprobe.image_size(image),
                                          keys.apfs_passwords())
        for lock in found:
            wrong = False
            while lock.vek is None and not lock.why:
                answer = ask(lock, wrong)
                if not answer:
                    break
                if lock.unlock([answer]):
                    keys.apfs_secrets.append(answer)
                wrong = lock.vek is None
            if lock.vek is None and not lock.why:
                left.append((f'{lock.name} in {lock.label}', lock.locked_note()))
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


def cli_image_keys(path, password_file=None, password_env=None, private_key=None,
                   bitlocker_keys=()):
    """What opens the image at ``path`` and the encrypted volumes in it, for the
    command line, as ImageKeys.

    A password comes from the first line of ``password_file``, else the environment
    variable ``password_env``; it opens an encrypted image, and it is tried on each
    BitLocker volume in the image as a password and as a recovery password, and on
    each encrypted APFS volume as a password and as a personal recovery key.
    ``private_key`` opens an image sealed to a certificate and ``bitlocker_keys`` are
    startup key (.BEK) files. At a terminal, what is missing is asked for (three tries
    each); a BitLocker or APFS volume nothing opens is reported on stderr and left
    locked.

    Raises ValueError, saying why, when the image itself cannot be opened with what was
    given.
    """
    name = os.path.basename(os.path.normpath(path))
    keys = ImageKeys(private_key=private_key, bitlocker_keys=bitlocker_keys)
    at_terminal = sys.stdin is not None and sys.stdin.isatty()
    try:
        given = _secret_given(password_file, password_env)
        if needs_private_key(path):
            if private_key is None:
                raise ValueError(f'{name} is sealed to a certificate and opens only with '
                                 f"that certificate's private key; give it with "
                                 f'--image_private_key')
            if not _opens(path, given, private_key):
                raise ValueError(f'the private key does not open {name}')
            keys.password = given
        elif needs_password(path):
            keys.private_key = None
            if private_key is not None and _opens(path, None, private_key):
                keys.private_key = private_key          # sealed to a certificate as well
            elif given is not None:
                if not _opens(path, given):
                    raise ValueError(f'the password does not open {name}')
                keys.password = given
            elif at_terminal:
                for _ in range(3):
                    password = getpass.getpass(f'Password for {name}: ')
                    if _opens(path, password):
                        keys.password = password
                        break
                    print('That password does not open the image.', file=sys.stderr)
                else:
                    raise ValueError(f'the password does not open {name}')
            else:
                raise ValueError(f'{name} is {_encrypted_kind(path)} and opens only '
                                 f'with its password; give it with --image_password_file '
                                 f'or --image_password_env, or run at a terminal to be '
                                 f'asked for it')
        else:
            keys.password = given           # it can still open a BitLocker volume
        tries = {}

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

        for label, note in _unlock_bitlocker(path, keys, ask):
            print(f'{label} of {name} stays locked and its files are not searched ({note}). '
                  f'Give its password or recovery password with --image_password_file or '
                  f'--image_password_env, or its startup key with --bitlocker_key.',
                  file=sys.stderr)
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

        for label, note in _unlock_apfs(path, keys, ask_apfs):
            print(f'{label} of {name} stays locked and its files are not searched ({note}). '
                  f'Give its password or personal recovery key with --image_password_file '
                  f'or --image_password_env.', file=sys.stderr)
    except _open_errors() as exc:
        raise ValueError(f'{name} could not be opened: {exc}') from None
    return keys


def ask_image_keys(parent, path):
    """What opens the image at ``path`` and the encrypted volumes in it, asked for in
    dialogs over ``parent``, as ImageKeys: its password, or the private key file of the
    certificate it is sealed to, until one opens it, then for each BitLocker volume
    inside, its password or recovery password, or left empty, its startup key (.BEK)
    file, and for each encrypted APFS volume, its password or personal recovery key.
    Cancelling a volume's prompt leaves it locked. None when the examiner cancels the
    image's own prompt, or when the image will not open for another reason, which is
    shown."""
    from tkinter import filedialog, messagebox, simpledialog  # pylint: disable=import-outside-toplevel
    name = os.path.basename(os.path.normpath(path))
    keys = ImageKeys()
    try:
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
                        keys.private_key = key
                        break
                    why = f'That key does not open {name}.'
                except _ewfprobe.EwfError as exc:        # not a key it can read
                    why = str(exc)
                messagebox.showerror('Encrypted disk image', why, parent=parent)
        elif needs_password(path):
            prompt = f'{name} is {_encrypted_kind(path)}. Its password:'
            while True:
                password = simpledialog.askstring('Encrypted disk image', prompt, show='*',
                                                  parent=parent)
                if password is None:
                    return None
                if _opens(path, password=password):
                    keys.password = password
                    break
                prompt = f'That password does not open {name}. Its password:'

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

        _unlock_bitlocker(path, keys, ask)

        def ask_apfs(lock, wrong):
            return simpledialog.askstring('Encrypted APFS volume',
                                          _apfs_prompt(lock, name, wrong) + ':',
                                          show='*', parent=parent)

        _unlock_apfs(path, keys, ask_apfs)
    except _open_errors() as exc:
        messagebox.showerror('Error', f'{name} could not be opened:\n{exc}', parent=parent)
        return None
    return keys


def names_a_stream(filepattern):
    """True when a pattern's last segment holds a ``:``, which is how a pattern
    asks for an NTFS alternate data stream (``*:Zone.Identifier``,
    ``*/$Extend/$UsnJrnl:$J``). Only such a pattern is matched against streams."""
    return ':' in filepattern.replace('\\', '/').rpartition('/')[2]


FREE_SPACE_FOLDER = '$Unallocated'
FREE_SPACE_SUFFIX = '.unallocated.bin'


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

    ``password`` is what opens the image and the encrypted volumes in it: ImageKeys,
    or a bare password, as earlier callers passed.
    """

    def __init__(self, image_path, data_folder, password=None):
        FileSeekerBase.__init__(self)
        self.image_path = image_path
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self.name_list = []
        self.stream_list = []
        self.free_list = []
        self.volumes = []
        self._free = {}
        self._size = 0
        self._entries = {}
        self._image = None
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
        name = os.path.basename(self.image_path)
        logical = open_logical(self.image_path, keys)
        if logical is not None:
            self._image = logical
            self._open_logical(name, logical)
            return
        logfunc(f'Reading {name} in place with the vendored qnxprobe '
                f'{qnxprobe.QNXPROBE_VERSION}; only the files an artifact asks for '
                f'leave the image.')
        # an acquisition's reader joins its own files; a raw set FTK Imager encrypted
        # is numbered like a split image and its files are ciphertext until then
        acquisition = qnxprobe.acquisition_format(self.image_path)
        sibling = None if acquisition else split_image_sibling(self.image_path)
        if sibling:
            logfunc(f'{name} is one segment of a split image: '
                    f'{os.path.basename(sibling)} sits beside it. The reader joins '
                    f'every segment of the set in order.')
        # A set with a hole in its numbering raises SplitImageError here, by
        # name, and the run stops with that message rather than reading half a
        # disk as though it were whole.
        segments = [] if acquisition else qnxprobe.split_segments(self.image_path)
        self._image = qnxprobe.open_image(self.image_path, segments, password=keys.password,
                                          private_key=keys.private_key)
        size = qnxprobe.image_size(self._image)
        self._size = size
        if segments:
            logfunc(f'  {len(segments):,} segments joined in order, '
                    f'{os.path.basename(segments[0])} .. '
                    f'{os.path.basename(segments[-1])}')
        elif getattr(self._image, 'paths', None):
            # the container and its segment or file count, as the reader reports it
            logfunc(f'  {qnxprobe.describe_acquisition(self._image)}')
        logfunc(f'  {size:,} bytes ({qnxprobe.human(size)})')

        # A BitLocker volume the keys open reads as the filesystem inside it, and an
        # encrypted APFS volume they open is read decrypted; one they do not open is
        # listed with the reason and nothing in it is searched.
        self._image, _found = qnxprobe.unlock_bitlocker(
            self._image, size, keys.bitlocker_passwords(), keys.bitlocker_keys)
        self._image, _apfs_found = qnxprobe.unlock_apfs(self._image, size,
                                                         keys.apfs_passwords())
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
            if vol.get('encryption') and vol['kind'] != 'bitlocker':  # a locked one's note says
                line += f"   [{vol['encryption']}]"
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
            files, dirs, streams, route = self._walk(walker, vol['name'])
            logfunc(f"  walked {vol['name']}: {files:,} files, {dirs:,} directories "
                    f"in {timex.monotonic() - started:.1f}s ({route})")
            if streams:
                logfunc(f'    and {streams:,} alternate data streams, matched only by a '
                        f'pattern that names one')
        image_name = os.path.basename(self.image_path)
        for vol in self.volumes:
            if getattr(vol.get('walker'), 'free_extents', None) is None:
                continue
            member = (f"{vol['name']}/{FREE_SPACE_FOLDER}/"
                      f"{image_name}.{vol['name']}{FREE_SPACE_SUFFIX}")
            self.free_list.append(member)
            self._free[member] = vol
        if self.free_list:
            logfunc(f'  {len(self.free_list):,} volumes can give their free space, to a '
                    f'pattern that asks for it (*{FREE_SPACE_SUFFIX})')
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
        files = dirs = streams = 0
        left_out = {}

        def leave(why):
            left_out[why] = left_out.get(why, 0) + 1

        for entry in image.logical_entries:
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
            self.name_list.append(path)
            self._entries[path] = _Entry(reader, entry, entry.size, times[1],
                                         folder=entry.is_folder)
            member_of[id(entry)] = path
            files += 1
        return files, dirs, streams, left_out

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
            if depth > _MAX_DEPTH or node in seen:
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
        if self.free_list and names_free_space(filepattern):
            members = members + self.free_list
        for member in members:
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
        the reader refused it (an encrypted NTFS file), it raised part way, the
        image ends before the file does, or the volume records fewer clusters
        for the file than its size needs. Each case is logged by name; a
        partial or empty copy is never left where a pattern could find it,
        because a truncated database parses as a smaller one, not as an error.
        """
        if member in self._free:
            return self._stage_free_space(member)
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
        self.file_infos[dest_path] = FileInfo(member, created, modified)
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
        vol = self._free[member]
        intended = self._intended_path(member)
        out_dir = os.path.dirname(intended)
        os.makedirs(out_dir, exist_ok=True)
        if os.path.isfile(intended):
            # a forced second search: the writer never overwrites, and the copy is there
            return intended
        records = qnxprobe.write_unallocated(
            self._image, self._size, [vol], out_dir, os.path.basename(self.image_path),
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
        if image is not None:
            try:
                image.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
