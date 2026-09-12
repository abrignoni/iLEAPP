# Raw image input

For maintainers, and shared by iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP.

`-t raw` takes a disk image (`.img`, `.dd`, `.bin`, or any numbered `.001`
segment of a split set) or an EnCase/EWF acquisition (`.E01` and its segments)
and reads it in place: no mounting, no administrator rights, and no copy of the
image or of its files anywhere but the files an artifact asks for. Its NTFS,
FAT32, exFAT, ext2/3/4, HFS+, APFS, QNX6, QNX4, ETFS, EFS and QNX IFS volumes
are searched directly.

## Where the pieces are

- `scripts/vendor/qnxprobe.py` and `scripts/vendor/ewfprobe.py` are the reader,
  copied verbatim from their repositories and guarded by
  `admin/scripts/check_vendored.py` (see `scripts/vendor/README.md`). Fix them
  upstream and re-vendor; an edit here is reverted by the next sync.
- `scripts/raw_image.py` holds everything of ours: `FileSeekerRaw`, the constants
  the GUI uses to recognise an image by extension, and `split_image_sibling`.
  **This file is byte-identical in all five cores.** Change it in one, land the
  same bytes in the other four in the same round, and let the parity scanner in
  leapps-org/leapps-parity confirm they match.
- The entry point adds one `-t` choice, one dispatch branch and a `finally` that
  calls `seeker.cleanup()` on every exit. The GUI maps the conventional image
  extensions onto `raw` and lists them in the file dialog.
- `admin/test/scripts/test_raw_image_seeker.py` checks staged bytes against
  independent hash lists over the fixtures in `admin/test/data/raw_images/`,
  including an E01 set and a split set built at test time.

## How it reads

`FileSeekerRaw` opens the image through the reader's `open_image()` (which joins
a split set and reads an EWF set), asks `volumes()` for every volume the reader's
own report would name, walks each readable volume once for its directory tree,
and offers the run a member list in the shape the zip seeker offers: one name per
file and one per directory (with a trailing slash), each prefixed by the volume's
extraction name, `p<partition>_lba<start>[_<label>]` or `lba0` for a bare volume.
`search()` matches a pattern against that list with the same `fnmatch` rules as
the zip seeker and reads only the matches out of the image, so the cost of a run
is the walk plus the files the artifacts wanted.

Measured on a 238.5 GiB Windows acquisition (PC-MUS-001, 253,032 files): the
walk took 9 seconds, a pattern resolves in under half a second, and DLEAPP's
patterns select 694 MiB of the 103.3 GiB of live files. Staging every file to a
temporary folder first, the design this replaced, would have written those 103 GiB
before the first artifact ran.

The run log names every volume with its filesystem and size, says which it
cannot read and why, and warns when the image is shorter than the volumes its
partition table describes, which is what a lone first segment of a split set
looks like. A file that runs past the end of the image is named in the log and
not staged, because a truncated database parses as a smaller one rather than as
an error.

## Times

NTFS, ext, HFS+ and APFS store instants, and those reach the staged copy's
mtime and the `FileInfo` the run records. FAT32 and exFAT store a wall-clock
reading with no zone; the reader hands those back as text. The staged copy's
mtime is set from that reading in the machine's local zone, exactly as the zip
seeker sets it from a member's DOS stamp, and the `FileInfo` records no instant
for it, so no report field carries a zone the evidence never had.

## What it does not do

- It reads live files. Deleted records the reader can recover on NTFS, FAT32
  and exFAT are not staged.
- It does not re-root a bare partition image. A raw image of an Android
  `userdata` partition has `data/`, `media/` and `system/` at its root rather
  than under `data/`, and an iOS Data volume has `mobile/` and `containers/`
  rather than `private/var/`. Patterns that begin with `*/` match either way;
  the few that spell out `private/var/` or `data/media/` do not match on a
  bare partition image. Two measured consequences: on a bare Android `userdata`
  image the storage-view dedupe recognises only the `data/data`, `data/user/N`
  and `data_mirror` spellings, so a partition read at its own root is not
  collapsed and per-app row counts multiply; on a bare iOS Data volume the
  `iosfilesystemevents` family and `diagnosticlogdevents` find nothing. A
  full-disk or full-`/data` image carries the expected root and neither happens.
- F2FS, the filesystem most current Android userdata partitions use, is not
  one the reader walks; such a volume is listed as not recognised.
- An encrypted volume (Android file-based encryption, iOS data protection,
  FileVault, BitLocker) reads, but its names or contents are ciphertext.

## Comparing a raw run against a zip run

The same extraction read as a zip and as a raw image of the same file tree does
not produce byte-identical reports, and the differences are in the input format
and in a few artifacts, not in what the seeker staged. A raw run over a full-disk
or full-`/data` image stages every file an artifact asked for, so the run log's
`Not staged` count is zero. The reports still differ in three ways worth knowing,
none of them a file the seeker got wrong:

- Timestamps. A zip member carries an MS-DOS stamp: two-second granularity, no
  sub-second, no zone. A filesystem carries the real instant. So a column that
  surfaces a staged file's own time reads a second or two apart between the two
  routes, and the raw route is the more faithful of the two.
- First-match order. A few artifacts read one file out of several equivalent
  copies and take the first the seeker returns. The zip, tar and raw seekers each
  list a directory in their own order, so which copy wins can differ. On Android
  `emulatedSmeta` reads one user's `external.db`, `installedappsGass` labels its
  source by the view it read, and `walstrings` numbers its rows by arrival. This
  is a property of those artifacts and shows between the zip and tar routes too.
- Companion files beside the zip. Some artifacts read a file a tool exported next
  to the acquisition rather than inside it. iOS keychain artifacts read a
  `<udid>_keychain.plist` sitting beside the zip on disk, found only when the
  input is that zip. A raw image is the filesystem itself and carries no such
  companion, so those artifacts report nothing from it.

## Frozen builds

The reader is imported as a module, so a PyInstaller build carries it like any
other module; nothing is spawned. `test_builds.yml` runs the frozen CLI with
`-t raw` on the NTFS fixture and requires the run log to show the walk. An
earlier design that ran the reader as a subprocess through `sys.executable`
could not work frozen, because in a bundle that is the tool itself.

## The corpus validator

`admin/scripts/validate_sample_data.py --run` runs a registry entry through
`-t raw` when the entry carries `"input_type": "raw"`. A raw image is never
guessed from its extension, because a registry can hold `.bin` files that are
readable disk images and `.bin` files that are chip-level dumps no walker opens.
