# Raw image input

For maintainers, and shared by iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP.

`-t raw` takes a disk image (`.img`, `.dd`, `.bin`, or any numbered `.001`
segment of a split set) or an acquisition (EnCase/EWF `.E01`, SMART `.s01`, EWF2
`.Ex01`, AFF `.aff`, an AFM `.afm` with its raw files, or an AFD folder of AFF files,
each with its segments or files, an AFF4 `.aff4`, an Apple `.dmg`, with any
`.dmgpart` files `hdiutil segment` split it into, `.sparseimage`, or `.sparsebundle`
folder, or a virtual machine's disk, `.vhd`, `.vhdx`, `.vmdk` or `.qcow2`, a
difference disk read through the disks under it) and reads it in place: no mounting,
no administrator rights, and no copy of the image or of its files anywhere but the
files an artifact asks for. Logical evidence, an EnCase `.L01` or an FTK Imager
`.ad1`, is read as the files it holds (see below). Its NTFS,
FAT32, exFAT, ext2/3/4, F2FS, HFS+, APFS, QNX6, QNX4, ETFS, EFS, SquashFS, JFFS2,
UBI/UBIFS, YAFFS and QNX IFS volumes are searched directly, on disks of 512-byte
or 4096-byte sectors: a GPT whose header sits at byte 4096, as on a UFS LUN image
or a 4Kn drive, has its partitions counted in 4096-byte sectors. An image with no
partition table and nothing recognised at its start (a chip-off flash dump, or an
eMMC image from an embedded device) has its SquashFS, UBI, JFFS2 and, since qnxprobe
1.51, ext2/3/4 volumes found by their own headers. Since 1.52, JFFS2 data compressed
with OpenWrt's LZMA is read, and on a raw NAND dump a UBIFS node that fails its CRC by
one flipped bit is read with that bit restored, as the NAND controller would have
read it.

## Where the pieces are

- `scripts/vendor/qnxprobe.py` and `scripts/vendor/ewfprobe.py` are the reader,
  copied verbatim from their repositories and guarded by
  `admin/scripts/check_vendored.py` (see `scripts/vendor/README.md`). Fix them
  upstream and re-vendor; an edit here is reverted by the next sync.
- `scripts/raw_image.py` holds everything of ours: `FileSeekerRaw`, the constants
  the GUI uses to recognise an image by extension and to fill its file dialog
  (`RAW_IMAGE_SUFFIXES`, `RAW_IMAGE_FILE_PATTERNS`), `split_image_sibling`, and
  `ImageKeys` with the functions that ask for them (`cli_image_keys`,
  `ask_image_keys`).
  **This file is byte-identical in all five cores.** Change it in one, land the
  same bytes in the other four in the same round, and let the parity scanner in
  leapps-org/leapps-parity confirm they match.
- The entry point adds one `-t` choice, one dispatch branch and a `finally` that
  calls `seeker.cleanup()` on every exit. The GUI maps the conventional image
  extensions onto `raw` and lists them in the file dialog. A folder the reader opens
  as one disk image, an Apple sparse bundle or an AFD folder, is mapped onto `raw` too
  when it is chosen with the folder button (`names_an_image_folder`), so it is not
  walked as a folder of extracted files. On a Mac the file dialog lists a
  `.sparsebundle` as one item; on Windows and Linux it is a folder.
- `admin/test/scripts/test_raw_image_seeker.py` checks staged bytes against
  independent hash lists over the fixtures in `admin/test/data/raw_images/`,
  including an E01 set, an AFF file, an AFD folder, a `.dmg`, a `.dmg` split into
  `.dmgpart` files, a `.sparseimage`, a sparse bundle, an encrypted `.dmg` and an
  encrypted sparse bundle (opened with their password) and a split set built at test
  time; an AD1 against FTK Imager's own listing of it (live files, a stream, a
  deleted entry left out), an AD1 sealed to a test certificate, a BitLocker
  volume opened with its password, recovery password or startup key, and an APFS
  volume macOS encrypted in place, opened with its password; and a damaged
  L01, an encrypted image opened without its password or with a wrong one, a damaged
  encrypted header and a `.dmgpart` opened on its own that must be refused.

## Encrypted images

An Apple disk image encrypted with a password (`hdiutil -encryption`: a `.dmg`, a
split one, a `.sparseimage` or a sparse bundle) or an encrypted AFF opens with that
password, which the vendored ewfprobe needs the `pycryptodome` package to use; the
cores already require it. `needs_password(path)` says whether an image needs one. One
sealed only to a certificate (`hdiutil -certificate`, `affcrypto`, or FTK Imager's AD
encryption given a certificate) opens instead with that certificate's RSA private key,
unencrypted, as PEM or DER; `needs_private_key(path)` says so.

What opens an image travels as `ImageKeys`: its password, a private key's path, the
secrets and startup key files of any BitLocker volume in it, and the passwords of any
encrypted APFS volume in it. The GUI asks for each in a dialog when the run starts
(`ask_image_keys`): the password, or the key file, until one opens the image, then, for
each BitLocker volume inside that nothing given opens, its password or recovery
password, or, left empty, its startup key (`.BEK`) file, and for each encrypted APFS
volume nothing given opens, its password or personal recovery key, the prompt showing
the passphrase hint the volume stores; cancelling a volume's prompt leaves that volume
locked. The command line (`cli_image_keys`) takes a password from
`--image_password_file` (the file's first line) or `--image_password_env` (an
environment variable), tried on the image, on each BitLocker volume as a password and
as a recovery password, and on each encrypted APFS volume as a password and as a
personal recovery key, a private key from `--image_private_key`, and startup keys from
`--bitlocker_key` (repeatable); at a terminal it asks for what is missing, and
otherwise it names each BitLocker or APFS volume left locked on stderr and runs
without it. Either way the keys are checked before the
run, handed to `crunch_artifacts(..., image_password=...)` and on to
`FileSeekerRaw(..., password=...)`, which passes them to the reader and does not keep
them; nothing writes them to the report, the log or the history. A secret is never
taken as an argument's value, which would put it in the process list and the shell
history. An image that will not open for another reason (a damaged header, no cipher
package) is reported by name rather than asked about again.

A BitLocker volume the keys open reads as the filesystem inside it, and the run log
names the method and what opened it (`[BitLocker AES-256-CBC, unlocked with its
recovery password]`); one they do not open is listed with the reason and what would
open it, and nothing in it is searched. A volume that keeps a clear key (protection
suspended) opens with nothing given. A Vista-era volume, the diffuser and a TPM-only
volume are named as not read. Measured on five volumes Windows 11 encrypted
(NTFS, FAT32 and exFAT, in fixed VHDs): every file Windows hashed before encrypting
staged with that hash, opened with a startup key, a recovery password, a password and
a clear key.

An APFS volume macOS encrypted in software (an external drive, or a Mac without a T2
chip or Apple silicon) that the keys open is read decrypted, and the run log says so on
its line (`CONVVOL is encrypted and was opened with a password, so its files are read
decrypted`); one they do not open is listed as locked, with what would open it and the
passphrase hint the volume stores, as stored, and nothing in it is searched. A volume
with per-file keys, one caught part way through being encrypted, decrypted or given a
new key, and the internal storage of a Mac with a T2 chip or Apple silicon (whose key
Apple ties to the hardware) are named as not read. Measured on the fixture qnxprobe
builds with `tools/make_apfs_converted_fixture.sh`, a volume macOS encrypted in place
after files were written: every file macOS hashed staged with that hash.

An E01, SMART or raw (dd) set FTK Imager encrypted with AD encryption opens the same
way, with the same prompts and options. Every file of such a set is encrypted and only
the first carries the header, so an E01 or SMART set is opened from its first file and
a raw set from any of its numbered files (`.001`, `.002`, ...); the reader decrypts and
joins them itself, and the run log names the set as the reader reports it rather than
as a split image. `needs_password(path)` answers for both kinds.

## How it reads

`FileSeekerRaw` opens the image through the reader's `open_image()` (which joins
a split set, and reads an EWF, EWF2, AFF, AFM, AFD or AFF4 acquisition, an Apple disk
image (a `.dmg` and its `.dmgpart` files, a `.sparseimage`, or a sparse bundle
folder) or a virtual machine's disk), opens any BitLocker volume the keys open
(`unlock_bitlocker()`) and any encrypted APFS volume they open (`unlock_apfs()`),
asks `volumes()` for every volume the reader's
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

## Logical evidence

An EnCase `.L01` or an FTK Imager `.ad1` holds copies of files rather than a disk, so
it is read through ewfprobe's entry list instead of a filesystem walk
(`open_logical`). Each entry is a member under its path in the evidence, in the order
the evidence stores them (a folder's children before its next sibling); an AD1 of
several sources names each source at the top (`U:\:AD1LEAN [NTFS]/[root]/...`). A
file is staged from the entry's content, its mtime set from the entry's modified time
and its `FileInfo` given the created time. An AD-encrypted AD1 opens with its password
or the private key of its certificate, like any other encrypted image.

An AD1 marks what each entry is, and four kinds hold no file's content: file slack
(type 6), NTFS directory index records (`$I30`, type F), NTFS attribute records
(`$DSC`, `$TXF_DATA`, type 10) and index entries that hold no data (type 61). Those,
and the entries FTK Imager lists as deleted, are not members, as a disk's deleted
records are not; the run log counts each. Every other entry is a member, so an entry of
a kind not measured is searched rather than lost. An NTFS alternate data stream (type
D) is a member `<file>:<stream>`, as on a disk. Measured on a 316,682-entry AD1 of a
Windows profile (Hexordia's public 2025 CTF image): 237,538 files, 16,953 folders and
373 streams listed in 27 seconds, every other entry counted by kind, and every file and
stream a DLEAPP run staged (152) matching the MD5 FTK Imager stored for it.

An L01 marks no such kinds, so every entry is a member. An L01 entry can be a folder
and hold data too (EnCase's parsed items): the folder keeps its name so its children
stage beneath it, and its data is staged beside it under the name the seekers give a
clash.

## Times

NTFS, ext, HFS+ and APFS store instants, and those reach the staged copy's
mtime and the `FileInfo` the run records. FAT32 and exFAT store a wall-clock
reading with no zone; the reader hands those back as text. The staged copy's
mtime is set from that reading in the machine's local zone, exactly as the zip
seeker sets it from a member's DOS stamp, and the `FileInfo` records no instant
for it, so no report field carries a zone the evidence never had.

## What it does not do

- It reads live files. Deleted records the reader can recover on NTFS, FAT32
  and exFAT are not staged, nor are the entries an AD1 lists as deleted.
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
- On F2FS, a file the filesystem compressed is listed with its size and not
  decompressed, and one under per-file encryption (the norm on a current
  Android `userdata`) is listed and its content refused rather than staged as
  ciphertext.
- zstd-compressed SquashFS and UBIFS need Python 3.14 or later
  (`compression.zstd`), which the builds made by `test_builds.yml` use. Run from
  source on an older Python, a zstd SquashFS is listed as a volume with no files,
  and the run log gives the reason on that volume's line; a zstd-compressed UBIFS
  file is listed and not staged, and the log names the reason.
- An encrypted volume (Android file-based encryption, iOS data protection,
  FileVault) reads, but its names or contents are ciphertext. An encrypted APFS
  volume says on its line whether it was read in the clear, opened with a password
  (see above) or is locked. A BitLocker volume is read when its keys are given (see
  above), and otherwise named as locked.

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
  `walstrings` numbers its rows by arrival. This is a property of those artifacts
  and shows between the zip and tar routes too.
- Companion files beside the zip. Some artifacts read a file a tool exported next
  to the acquisition rather than inside it. iOS keychain artifacts read a
  `<udid>_keychain.plist` sitting beside the zip on disk, found only when the
  input is that zip. A raw image is the filesystem itself and carries no such
  companion, so those artifacts report nothing from it.

## Frozen builds

The reader is imported as a module, so a PyInstaller build carries it like any
other module; nothing is spawned. `python packaging/build.py smoke`, which
`test_builds.yml` and `release.yml` run on every platform, runs the built executable
with `-t raw` on the NTFS fixture and requires the run log to show the walk. An
earlier design that ran the reader as a subprocess through `sys.executable`
could not work frozen, because in a bundle that is the tool itself.

## The corpus validator

`admin/scripts/validate_sample_data.py --run` runs a registry entry through
`-t raw` when the entry carries `"input_type": "raw"`. A raw image is never
guessed from its extension, because a registry can hold `.bin` files that are
readable disk images and `.bin` files that are chip-level dumps no walker opens.
