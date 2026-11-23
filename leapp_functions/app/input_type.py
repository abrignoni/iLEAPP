"""
What the source is, named as the -t option of the command line names it.
"""

import os
import plistlib
from collections import namedtuple
from xml.parsers.expat import ExpatError

from leapp_functions import leapp
from scripts.filetype import guess_mime
from scripts.raw_image import (RAW_IMAGE_SUFFIXES, logical_among, logical_refusal,
                               names_an_image_folder, names_raw_images)
from scripts.vendor import qnxprobe

Detected = namedtuple("Detected", "kind label note problem encrypted", defaults=("", "", False))

NO_ANSWER = Detected("", "No answer", problem="Its drive does not answer: it may be disconnected.")
LOOKING = Detected("", "Looking at the source", note="Waiting for its drive to answer.")

LABELS = {"fs": "Folder of extracted files", "tar": "tar archive", "gz": "tar.gz archive",
          "zip": "zip archive", "raw": "Raw disk image"}
SUPPORTED = frozenset(leapp.input_types)

# The archives known by their first bytes, and the input type that reads each of them
CONTENT_KINDS = {"application/zip": "zip", "application/x-tar": "tar",
                 "application/gzip": "gz", "application/x-xz": "tar"}

# The names qnxprobe gives to the formats it recognises, as an examiner knows them
FORMAT_NAMES = {"EWF": "E01", "EWF2": "Ex01", "UDIF": "DMG", "DMG_ENCRYPTED": "encrypted DMG",
                "SPARSEIMAGE": "sparse image", "SPARSEBUNDLE": "sparse bundle",
                "AD_ENCRYPTED": "encrypted AD1"}


def detect(paths, supported=SUPPORTED, single_file=False):
    """
    Detect the file type. Nothing is opened beyond the first bytes of a file.
    Args:
        paths (list): the paths of the source field, several for the images of a RAID set.
        supported (frozenset): the -t values this LEAPP reads.
        single_file (bool): one file is to be read as it is (-t file), if this LEAPP can.
    Returns:
        Detected, or None when there is no path.
    """
    paths = [path for path in paths if path]
    if not paths:
        return None
    if len(paths) > 1:
        return detect_images(paths)
    path = paths[0]
    if not os.path.exists(path):
        return Detected("", "Not found", problem="This file or folder does not exist.")
    if names_an_image_folder(path):
        return detect_image(path)
    if os.path.isdir(path):
        return detect_folder(path, supported)
    return detect_single_file(path) if single_file and "file" in supported else detect_file(path)


def detect_images(paths):
    """ Several files: they are read together only as the disk images of a RAID set. """
    for path in paths:
        if not os.path.isfile(path) and not names_an_image_folder(path):
            return Detected("", "Not found", problem=f"{path} does not exist.")
    if not names_raw_images(paths):
        return Detected("", "Several files", problem="Several files are read together only as "
                        "disk images, the member images of a RAID set.")
    logical = logical_among(paths)
    if logical is not None:
        return Detected("", "Several files", problem=logical_refusal(logical))
    return Detected("raw", f"{len(paths)} disk images", note="Read together, as a RAID set.")


def detect_image(path):
    """ A disk image, with the name of its format when the first bytes give it. """
    try:
        found = qnxprobe.acquisition_format(path)
    except OSError as error:
        return unreadable(error)
    if found is None:
        return Detected("raw", LABELS["raw"])
    if found in ("L01", "Lx01", "AD1"):
        return Detected("raw", f"Logical evidence ({found})")
    return Detected("raw", f"Disk image ({FORMAT_NAMES.get(found, found)})")


def detect_folder(path, supported):
    """ An iPhone or iPad backup, or else a folder of extracted files. """
    kind = backup_type(path)
    if kind:
        return detect_backup(path, kind, supported)
    try:
        empty = not os.listdir(path)
    except OSError as error:
        return unreadable(error)
    if empty:
        return Detected("", "Empty folder", problem="This folder holds nothing to parse.")
    return Detected("fs", LABELS["fs"])


def detect_backup(path, kind, supported):
    """ An iTunes or Finder backup, "db" or the older "mbdb" kind: only iLEAPP reads them. """
    label = "iTunes backup" if kind == "db" else "Legacy iTunes backup"
    if "itunes" not in supported:
        return Detected("", label, problem=f"iLEAPP reads iPhone and iPad backups, {leapp.name} does not.")
    if not is_encrypted(path, kind):
        return Detected("itunes", label)
    if kind == "mbdb":
        return Detected("", f"{label}, encrypted", problem="iTunes Legacy Encrypted Backup not supported",
                        encrypted=True)
    return Detected("itunes", f"{label}, encrypted", encrypted=True)


def backup_type(path):
    """ "db" for a backup of iOS 10 or later, "mbdb" for an older one, "" for any other folder. """
    for name, kind in (("Manifest.db", "db"), ("Manifest.mbdb", "mbdb")):
        if os.path.exists(os.path.join(path, name)):
            return kind
    return ""


def is_encrypted(path, kind):
    """ Whether the backup is encrypted, as Manifest.plist says. """
    try:
        with open(os.path.join(path, "Manifest.plist"), "rb") as manifest:
            encrypted = bool(plistlib.load(manifest).get("IsEncrypted"))
    except (OSError, ValueError, ExpatError):  # missing, or not a plist
        return False
    if encrypted and kind == "db":
        return guess_mime(os.path.join(path, "Manifest.db")) != "application/x-sqlite3"
    return encrypted


def kind_by_name(path):
    """ The input type that the extension of a file stands for, or None. """
    name = os.path.basename(path).lower()
    if name.endswith((".tar", ".tar.xz")):
        return "tar"
    if name.endswith((".gz", ".tgz")):
        return "gz"
    if name.endswith(".zip"):
        return "zip"
    suffix = name.rpartition(".")[2]
    # A numbered segment of a split image: .001, .002...
    if suffix in RAW_IMAGE_SUFFIXES or (suffix.isascii() and suffix.isdigit()):
        return "raw"
    return None


def detect_file(path):
    """ A file, by its extension and by its first bytes. """
    try:
        if qnxprobe.acquisition_format(path) is not None:
            return detect_image(path)
        by_content = CONTENT_KINDS.get(guess_mime(path))
    except OSError as error:
        return unreadable(error)
    by_name = kind_by_name(path)
    kind = by_content or by_name
    if kind is None:
        return Detected("", "Unknown file", problem="It is neither an archive nor a disk image.")

    note = ""
    if by_content is None:
        if kind != "raw":
            note = f"Its content does not look like a {LABELS[kind]}."
    elif by_name not in (None, by_content):
        note = (f"Its name says {LABELS[by_name]}, its content {LABELS[by_content]}: "
                "it is read as its content.")
    return Detected(kind, LABELS[kind], note)


def detect_single_file(path):
    """ A file read as it is, even an archive or a disk image: it is not opened. """
    note = "Only the artifacts that look for a file of this name read it."
    looks = detect_file(path)
    if looks.kind:
        label = looks.label[0].lower() + looks.label[1:]
        note = f"It looks like a {label}, but it is read as it is, not opened. {note}"
    return Detected("file", "Single file", note)


def unreadable(error):
    """ The source exists but cannot be opened. """
    return Detected("", "Unreadable", problem=f"It cannot be read: {error.strerror}.")
