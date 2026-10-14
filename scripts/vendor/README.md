# Vendored third-party readers

Code copied in from another repository, unmodified, so the tool can read disk
images and acquisitions without asking the examiner to install anything.

## qnxprobe.py

| | |
| --- | --- |
| upstream | https://github.com/abrignoni/qnxprobe |
| licence | MIT, kept beside it as LICENSE-qnxprobe |

Reads QNX6, QNX4, ext2/3/4, FAT32, exFAT, NTFS, HFS+, APFS, the QNX flash
filesystems ETFS and EFS, and QNX IFS boot images out of a raw image, without
mounting and with no administrator rights. `scripts/raw_image.py` imports it and
reads an image through its `volumes()` call. Python 3 standard library only, so
vendoring it adds no dependency to requirements.txt.

## ewfprobe.py

| | |
| --- | --- |
| upstream | https://github.com/abrignoni/ewfprobe |
| licence | MIT, kept beside it as LICENSE-ewfprobe |

Reads an EnCase/EWF acquisition (`.E01` and its numbered segments) as an ordinary
seekable image. qnxprobe reaches it by name, and `scripts/raw_image.py` imports
this copy first so that the name resolves to it in a frozen build as well as from
source. Standard library only, so this adds no dependency either.

The vendored version, upstream commit and sha256 of each file are recorded in
`vendored.json` in this directory, which `admin/scripts/check_vendored.py`
enforces in CI: it checks the hashes and fetches each upstream file at its
recorded commit. They are deliberately not repeated here, because prose is
checked by nobody and the manifest is checked on every push.

**These files are copied verbatim. Do not edit them here.** Fix upstream, then
re-vendor, or the next sync silently reverts the change.

### Re-vendoring

    cp ../qnxprobe/qnxprobe.py scripts/vendor/qnxprobe.py
    cp ../qnxprobe/ewfprobe.py scripts/vendor/ewfprobe.py
    python3 admin/scripts/check_vendored.py --update

`--update` rewrites the hashes only. The upstream commit and date in
`vendored.json` are what say which version this is, so set those by hand from
`git -C ../qnxprobe log -1 --format='%H %cI' main` (ewfprobe's come from
qnxprobe's own `vendored.json`, since the copy here is the one qnxprobe carries).
Then run the check without `--update`, which fetches the upstream file at the
commit you recorded and fails if the copy is not that file.

### Checking for drift

`admin/scripts/check_vendored.py` compares each copy against the sha256 recorded
in `vendored.json` and against the upstream file at the recorded commit, and
fails when either differs. It runs in CI, so a local edit or a stale copy after an
upstream release is caught rather than noticed later. Pass `--upstream <path>`
(or `--upstream qnxprobe=<path>`) to compare against a checkout instead of
fetching, and `--offline` to check the hashes alone.
