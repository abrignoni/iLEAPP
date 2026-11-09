# Vendored third-party readers

Code copied in from another repository so the tool can read disk images and
acquisitions without asking the examiner to install anything. Every file is
unmodified except ccl/ccl_leveldb.py, whose section says what differs.

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

## c2pareader.py

| | |
| --- | --- |
| upstream | https://github.com/abrignoni/c2pareader (called c2paprobe up to v0.1.1) |
| licence | MIT, kept beside it as LICENSE-c2pareader |

Reads the Content Credentials (C2PA) manifest store and the XMP a picture or video
holds, walking its container from the bytes. `scripts/artifacts/c2paProvenance.py`
imports it. ALEAPP vendors the same file. Standard library only.

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
    cp ../c2pareader/c2pareader/__init__.py scripts/vendor/c2pareader.py
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

## ccl/ (CCL Forensics LevelDB reader)

| | |
| --- | --- |
| upstream | https://github.com/cclgroupltd/ccl_chromium_reader and https://github.com/cclgroupltd/ccl_simplesnappy |
| licence | MIT, kept beside them as LICENSE-ccl_chromium_reader and LICENSE-ccl_simplesnappy |

Reads LevelDB stores. The KeepSafe, Spotify, Uber and Chromium sync data artifacts import it
from `scripts.vendor.ccl`. Both files are the same as DLEAPP's and ALEAPP's `scripts/vendor/ccl`
copies.

- `ccl_simplesnappy.py`: ccl_simplesnappy 2161c40 (2024-07-29), verbatim, recorded in vendored.json.
  That commit carried no LICENSE file; the MIT text kept here is the repository's later one, and
  the file's own header holds the same licence.
- `ccl_leveldb.py`: ccl_chromium_reader ad37443 (2026-10-28) with local changes, so it is not in
  vendored.json. `import ccl_simplesnappy` is `from . import ccl_simplesnappy`, and the file
  handle bounding from iLEAPP 41af38df is merged in: a reader closes each .log and .ldb file
  after checking it and reopens it for each pass, and what a pass skips as damage is copied back
  to the file's reader. That change is offered upstream as
  https://github.com/cclgroupltd/ccl_chromium_reader/pull/56; once upstream has it, re-vendor
  and record the file in vendored.json.
  A further local change, from DLEAPP 0e4953a (2026-11-08): a data block of a table (.ldb)
  file that cannot be read whole or whose snappy stream does not decompress is skipped, logged
  (noting when its checksum does not match) and listed in the reader's `damage`, and reading goes
  on with the next block and file. Upstream ad37443 raises there, so a caller gets nothing more
  from that folder. Measured 2026-11-09 over the zip, tar and folder sources in the corpus
  registries (disk images and other containers were not read): of 9,305 table files (six-digit .ldb and .sst
  names) under 62 corpus keys, the reader before and after this change returns the same records
  from 9,287, and both refuse the other 18
  when the table is opened (footer magic), a check this change does not touch. A skipped block
  can have held a newer version of a key, so a caller that keeps the newest record per key can
  then see an older one. admin/test/scripts/test_leveldb_table_damage.py pins the decompression
  cases and the read of the next file.

Before 2026-11-03 iLEAPP kept an older copy of this reader (closest to upstream 210b5c6, 2021) in
`scripts/`. The newer upstream code skips and reports a damaged or zero-filled .log block where
the older one stopped reading (ccl_chromium_reader a321210 and 6e5dbe5).
