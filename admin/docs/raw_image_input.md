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
FAT32, FAT16, FAT12, exFAT, ext2/3/4, F2FS, HFS+, APFS, QNX6, QNX4, ETFS, EFS, SquashFS, JFFS2,
UBI/UBIFS, YAFFS and QNX IFS volumes are searched directly, on disks of 512-byte
or 4096-byte sectors: a GPT whose header sits at byte 4096, as on a UFS LUN image
or a 4Kn drive, has its partitions counted in 4096-byte sectors. An image with no
partition table and nothing recognised at its start (a chip-off flash dump, or an
eMMC image from an embedded device) has its SquashFS, UBI, JFFS2 and, since qnxprobe
1.51, ext2/3/4 volumes found by their own headers. Since 1.52, JFFS2 data compressed
with OpenWrt's LZMA is read, and on a raw NAND dump a UBIFS node that fails its CRC by
one flipped bit is read with that bit restored, as the NAND controller would have
read it. Since 1.55, two JFFS2 partitions that sit side by side are read as two
filesystems, and a U-Boot environment or a Belkin WeMo NVRM configuration store whose
CRC-32 holds is listed as a volume holding one file, `uboot-env.bin` or `nvram.bin`.
Since 1.56, an NTFS file the Windows Overlay Filter compressed with XPRESS (Store app
files, Defender's platform files, anything `compact /exe` touched) is staged as its
content, where it used to be staged as zeros of the right length, and a cloud
provider's online-only placeholder (OneDrive Files On-Demand) is not staged at all:
its content is not in the image, and the run log names it.
Since 1.57, an NTFS-compressed file with a compression unit that stops early is staged
at its recorded length, the rest of that unit as zeros. Before, the reader returned
fewer bytes than the file records and the file was not staged.
Since 1.65, the linear logical volumes of an LVM2 physical volume, each one run of extents
on one physical volume in the image, are searched as volumes of their own, named
`lvm_lba<first sector>_<group>_<volume>`. The physical volume's line in the run log
names any logical volume that is not read (a RAID level other than 1, thin, a snapshot,
or one with a run on a physical volume missing from the image) and why. Since 1.66, a
logical volume split into separate runs of extents, or striped, is searched too,
read through a map of its runs; its name counts the first sector of its first run.
Since 1.67, a RAID1 or mirror logical volume is searched too, read from the first of
its copies whose extents are all in the image, and a LUKS1 or LUKS2 container a
passphrase opens is searched as what it holds (see Encrypted images).
Since 1.74, a file macOS compressed on APFS or HFS+ (decmpfs: zlib, LZVN, LZFSE or
stored, in the compression attribute or the resource fork) is staged as its content.
Before, the reader decoded methods 3 and 4 (zlib) and read method 5 as zlib, and
refused every other method, naming its number, so a file compressed with LZVN, LZFSE
or a stored method was listed and not staged. A file compressed with LZBITMAP, which
this reader does not decode, or with method 5, is now listed and not staged, and the
run log gives the reason, as it does for a compressed stream that is damaged. A compression attribute on a file not
flagged compressed is not the file's content: the file is read as stored, as macOS
reads it, and the run log lists it under the damage the reader recorded in its volume,
by member name when one listed member holds that record and otherwise by its object id
or catalog id.

## Several images: the members of a RAID set

Since qnxprobe 1.70, the images of a Linux software RAID set are read together, one
image per disk. `-i` takes several paths with `-t raw`, and the GUI's file dialog takes
several files. Each image can be any disk image or acquisition `-t raw` reads (raw,
split, E01 and the rest). Logical evidence (an L01 or AD1) holds files, not a disk:
given with other images it is refused before the run, on the command line and in the
GUI. The reader assembles the images as `qnxprobe.raid_assemble` does: Linux md arrays
(metadata 0.90, 1.0, 1.1 and 1.2; linear, RAID0, 1, 4, 5, 6 and 10) and LVM2 logical
volumes spread over several images (LVM RAID4, 5, 6 and 10 among them). Which arrays
are read, which are not and why, which members are left out (stale, faulty, a spare)
and which roles are missing is the reader's own report, written to the run log before
any volume is walked. A RAID5 missing one member, or a RAID6 missing two, is rebuilt
from parity only when the array was stopped clean; the reader's README, "RAID", says
what is read and what is refused. Since qnxprobe 1.72 the heading of that report counts
as assembled only the arrays that are read ("1 array(s) or spanned volume(s) found in
the images given, 0 of them assembled" for one RAID5 member given alone), and two images
that share a file name in different folders are named in it by the folders that tell
them apart (`share-left/member.img`, `share-right/member.img`); their volume names
still start with the file name, told apart by a number as below. The reader's own hint
to look for the other members with its `--find-members` option is not given, because
these tools do not have that option: they look beside one image themselves (below).

A member left out of its array (stale, faulty, a spare) is not read anywhere in that
run: the array is read from the other members, and the left-out member's own copy of
the data, which can differ from the array's, is not searched. To see that copy, run
the member image on its own.

One disk is read once. Two paths that name the same file (the same path twice, a hard
or symbolic link, a relative and an absolute path) or two files of one set (two
segments of a split raw set, an EWF set or an AD1 set) are one disk: the second is not
read, and the command line prints, the GUI shows and the run log and the report's
"Extraction location" record which path is read, in the vendored reader's words (since
qnxprobe 1.72): another name of the same file is "the same disk as" the first, "read
once", and a later file of a split raw or EWF set the first opens is "read as a segment
of the split set opened from" the first (or "the EWF set"), "not on its own".

A split raw set is joined by its file names alone: files named `<stem>.001`,
`<stem>.002` ... in one folder are read as one image. Since qnxprobe 1.72, when a later
segment begins as a disk does (an md superblock, or a partition table), the run log
carries the reader's warning that they may be separate disks named like one split image,
and that copies named otherwise (`<stem>-1.img`) are read as separate images. Measured:
four RAID5 member images named `m.001` to `m.004` give the warning; one NTFS image cut
in two gives none.

Each image is then read as it would be alone, except its volumes that lie inside a
member of an array read here: those are listed in the run log with where they are read
instead, and not walked, so a file is not listed twice. Each array read is read as a
disk of its own, its volumes named as any disk's are. When more than one image or array
is read, every volume name starts with the name of what holds it: the image's file name
made safe (`disk0_img_p1_lba2048`; two images whose names make the same safe name are
told apart by a number, `disk0_img_2_p1_lba2048`), or the array's own name, the one the
reader's extraction gives it (`md_<name>_<first eight hex digits of its uuid>_lba0` for
an md array, `lvm_<group>_<volume>_lba0` for an LVM2 volume read across images). The
same name replaces the image's file name in an array's free space members.

A RAID1 array whose data starts at the first byte of its first member (metadata 0.90 or
1.0, superblock at the end) is not read again, as the reader's own report says ("not
read again"): that member's own volume holds the same bytes and is walked, and the
other members' copies are listed with a note naming the member read and are not walked.

One image that holds an md member (a lone member of a RAID set, or a disk whose
partitions are members) is read the same way, with its arrays, as far as the members it
holds allow. This changes what such an image gives compared with earlier releases: a
lone RAID1 member whose superblock is at its start (metadata 1.1 or 1.2; the fixture
measured is 1.2) now reads its filesystem through the array,
a lone RAID5 member reads no array, and the volume names gain the prefixes above
whenever an array is read beside the image. A lone RAID1 member with metadata 0.90 or
1.0 is read as before, from its own volume, under the same names.

The reader also decides, on its own, that some single images are not walked. A region
it identifies as an md member is listed as a RAID member and not walked, except a RAID1
member whose filesystem starts at its first byte (the case above): a member of a linear,
RAID0, RAID4/5/6 or RAID10 array holds only part of the array's data, and walking it
alone reads a filesystem cut short. Since qnxprobe 1.71 the same rule holds for a DDF or
Intel IMSM (RST) member, whose array is never assembled here: the level its own metadata
records decides, and only a mirror in its normal state is walked, on its own, with a
note saying its array is not assembled; any other level, a mirror in any other state, or
metadata that cannot be read leaves the region (and everything on that disk, partitions
included) listed as a RAID member and not walked, its note naming the level or why the
metadata was not read. With other images, the run log's RAID section also names each
such disk as not read and says why. Measured: read alone, the first member of
qnxprobe's linear fixture (`md-linear-0`) and the second and third members of its DDF
fixture (`md-ddf-1`, `md-ddf-2`, a RAID5) gave files through qnxprobe 1.67 and give none
through 1.71, with the DDF members' notes naming RAID5; a test disk carrying only the
IMSM signature, with and without a partition table, is named as an IMSM member whose
metadata was not read and is not walked, alone and with another image. No fixture here
holds a DDF or IMSM mirror, so the mirror case is the reader's code, not exercised here.
An image in which the reader finds no RAID metadata is read exactly as before: the same
member names and the same run log, byte for byte apart from the vendored reader's
version.

An LVM2 physical volume read with the other images of its volume group keeps the
reader's own note on its line in the run log, which names the group's volumes that
image alone cannot read, followed by where each is read across the images given (`r5 as
lvm_qpraid2_r5`). Since qnxprobe 1.71, two volume groups that share a name (a default
such as `vg0`) are matched by their ids and read on their own; their labels and names
carry the start of the id (`lvm_vg0_<id6>_root`), and each physical volume's line names
only its own group's volumes (measured with the fixture set and a copy of it given a
second group id).

Given one image that holds an md member or an LVM2 physical volume of a set that is
not complete in it (a role or a physical volume no file given holds), the command line
looks in that image's folder for the other members with `qnxprobe.raid_siblings`,
which goes by what each file records about itself (an md superblock's array uuid, an
LVM2 volume group's id and its list of physical volumes), never by its name. An image
that holds every member of its arrays and volume groups (a one-disk LVM2 image, or a
disk whose own partitions form an array) is not searched beside, and nothing is said.
The search prints what the image holds, every file it adds and every other entry of the
folder with what became of it and why (another array, no RAID metadata, a folder, a
symbolic link, and the rest), the roles or physical volumes no file holds, and its
result, then the set is read. Several images given are read as given, with no search.
`--no-find-members` turns the search off, and only the image given is read (with its
arrays, as far as one member allows). An array or volume group not read because members
are not among the images given gets a line in the run log naming the roles or physical
volumes missing and saying the other member images can be given with it (several paths
to `-i`, or several files picked together); when the search was turned off, or what it
found was not taken, the line adds that leaving member finding on looks for them beside
the image given. The GUI makes the same search when one image is
picked, and when it adds files it shows them, and those it did not use with why, before
the run, with "Use them" (the default), "Only the file I picked" and "Cancel". Nothing
is asked when the image needs no search or the search adds nothing.

Whenever a search ran, the run log repeats what it printed, ending with its result and
the examiner's choice ("Result: ... the examiner chose to read only ..."). When the
search read nothing more (none found, or the examiner chose the file picked alone), the
report's "Extraction location" and LAVA's `param_input` add the same sentence after the
path.

The report's "Extraction location", the run log's first lines, LAVA's `param_input`
and the recent-inputs history name every image read; the ones the search added are
marked "found automatically". The history keeps its list of paths as before (the
images given) and records each set read together, with the ones found marked, under
`input_sets`. A set is offered in the GUI's history only while the images given in it
are still among the recent input paths. A LEAPP release from before sets that clears
its history removes the recent input paths and leaves `input_sets` in the file; the
sets are then no longer offered, and this release's own clear removes them.

A password or key is asked for each image that needs one, and the BitLocker, APFS and
LUKS volumes of each image and of each array read are asked about in turn. As for one
image, every password that opened one of the images is also tried on those volumes.

Measured: the member images of five fixture sets mdadm and lvm2 wrote (a RAID1 with
metadata 1.2 and one with 0.90, a RAID5 with 1.2 and one with 0.90, and three LVM2
volumes, RAID5, RAID6 and RAID10, across five images; copied from qnxprobe's
`tests/fixtures/raid` into `admin/test/data/raw_images/raid/`) read to the SHA-256 of
every file of the tree each array was built from, and so does the RAID5 with one
member left out. Not covered by any fixture here: E01 or other acquisition containers
as members, an LVM2 volume group on an md array, encrypted volumes inside an
array, and an array whose members are partitions of one image.

## Where the pieces are

- `scripts/vendor/qnxprobe.py` and `scripts/vendor/ewfprobe.py` are the reader,
  copied verbatim from their repositories and guarded by
  `admin/scripts/check_vendored.py` (see `scripts/vendor/README.md`). Fix them
  upstream and re-vendor; an edit here is reverted by the next sync.
- `scripts/raw_image.py` holds everything of ours: `FileSeekerRaw`, the constants
  the GUI uses to recognise an image by extension and to fill its file dialog
  (`RAW_IMAGE_SUFFIXES`, `RAW_IMAGE_FILE_PATTERNS`), `split_image_sibling`, and
  `ImageKeys` with the functions that ask for them (`cli_image_keys`,
  `ask_image_keys`), and the several-image input: `cli_raw_input` and `ask_raw_input`
  (what to read and what opens it, with the member search), `find_members`,
  `confirm_found_members`, `input_text` (the input as the report names it) and the
  GUI's `selection_text`, `selected_paths` and `PathsTooltip`.
  **This file is byte-identical in all five cores.** Change it in one, land the
  same bytes in the other four in the same round, and let the parity scanner in
  leapps-org/leapps-parity confirm they match.
- The entry point adds one `-t` choice, one dispatch branch and a `finally` that
  calls `seeker.cleanup()` on every exit. Its `-i` takes several paths with `-t raw`,
  and `--no-find-members` turns the member search off. The GUI maps the conventional image
  extensions onto `raw` and lists them in the file dialog. A folder the reader opens
  as one disk image, an Apple sparse bundle or an AFD folder, is mapped onto `raw` too
  when it is chosen with the folder button (`names_an_image_folder`), so it is not
  walked as a folder of extracted files. On a Mac the file dialog lists a
  `.sparsebundle` as one item; on Windows and Linux it is a folder.
- `leapp_functions/app/history.py` records a set of images read together
  (`record_input_set`, `get_input_sets`); it is byte-identical in the five cores too.
- `admin/test/scripts/test_raw_image_seeker.py` checks staged bytes against
  independent hash lists over the fixtures in `admin/test/data/raw_images/`,
  including an E01 set, an AFF file, an AFD folder, a `.dmg`, a `.dmg` split into
  `.dmgpart` files, a `.sparseimage`, a sparse bundle, an encrypted `.dmg` and an
  encrypted sparse bundle (opened with their password) and a split set built at test
  time; an AD1 against FTK Imager's own listing of it (live files, a stream, a
  deleted entry left out), an AD1 sealed to a test certificate, a BitLocker
  volume opened with its password, recovery password or startup key, and an APFS
  volume macOS encrypted in place, opened with its password; a volume Windows 11
  wrote, against Windows's own hashes of its overlay-compressed, NTFS compressed and
  sparse files, with cloud placeholders that must not be staged; and a damaged
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
secrets and startup key files of any BitLocker volume in it, the passwords of any
encrypted APFS volume in it, and the passphrases of any LUKS container in it. The GUI asks for each in a dialog when the run starts
(`ask_image_keys`): the password, or the key file, until one opens the image, then, for
each BitLocker volume inside that nothing given opens, its password or recovery
password, or, left empty, its startup key (`.BEK`) file, and for each encrypted APFS
volume nothing given opens, its password or personal recovery key, the prompt showing
the passphrase hint the volume stores, and for each LUKS container nothing given opens,
its passphrase; cancelling a volume's prompt leaves that volume locked. The command line (`cli_image_keys`) takes a password from
`--image_password_file` (the file's first line) or `--image_password_env` (an
environment variable), tried on the image, on each BitLocker volume as a password and
as a recovery password, on each encrypted APFS volume as a password and as a
personal recovery key, and on each LUKS container as a passphrase, a private key from `--image_private_key`, and startup keys from
`--bitlocker_key` (repeatable); at a terminal it asks for what is missing, and
otherwise it names each BitLocker, APFS or LUKS volume left locked on stderr and runs
without it. As qnxprobe 1.72 does, which option takes what opens a volume is said only
when nothing was given for that kind of volume; when something was given and the volume
stays locked, the line carries the reader's own reason alone (none of the passwords
given opens it, the pycryptodome package is missing, or a LUKS container sits inside a
logical volume read through a map, where it is not opened, so the passphrase given was
not tried on it). Either way the keys are checked before the
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
an error. What the reader records as damage while it walks a volume (a record that
fails its check, a compression attribute on a file not flagged compressed) is listed
under the volume's walked line, the first few entries and a count, and damage met
while a file is staged is said with that file. Since ewfprobe 0.14.0, a chunk of an
E01, SMART or Ex01 acquisition, a VMDK grain or a QCOW cluster whose stored data runs
out before the bytes it covers, or whose compressed stream stops before its end, is
read with zeros in its place, as before, and the run log now says so: once for what
the listing read, and with the file whose staging first read it, since that file can
hold those zeros. Only the units read are known; the reader reads the rest only when
asked to verify the whole image.

## Free space

A volume's free space is a member too, but one only a pattern that asks for it can
reach. For every volume whose filesystem reports what is free (the reader's
`free_extents()`: qnx6, F2FS, FAT32, FAT16, FAT12, exFAT, NTFS, HFS+ and APFS), and, since
qnxprobe 1.67, for every LVM2 physical volume, whose extents no logical volume holds are
its free space, the member list gains one name, kept apart from the files in
`free_list`:

    <volume>/$Unallocated/<image name>.<volume>.unallocated.bin

Only a pattern whose last segment ends in `.unallocated.bin` is matched against it
(`names_free_space()`), the way only a pattern that names a stream is matched against
alternate data streams. A broad pattern such as `*` or `*.bin` never stages free
space, and nothing is read for it until a pattern matches, so a run that selects no
such artifact costs nothing more than before.

Staging it calls the reader's own `write_unallocated()`, so the copy is what
`qnxprobe --unallocated` writes: the free runs one after another, and a `.tsv`
beside the copy that maps each run to its offset in the image. Two neighbours in
that file were not neighbours on the disk, so an artifact that reads records out of
it should read the map and never read a record across two runs. A volume whose
allocation map could not be read, or that reports nothing free, gives no file, and
the run log says which.

The reason to have it: a rolled or deleted file's blocks are released, not erased.
This was measured in VLEAPP, where the change was made (VLEAPP #328), and has not
been measured in this tool. On a 29.1 GiB Ford SYNC 4 image (key `ford_syncg4`),
whose platform log rolls, the image holds 718,195 log lines and the live log files
about 107,000 of them; the rest sit in blocks the qnx6 bitmap marks free. A VLEAPP
run that selected its five platform log artifacts staged 14.2 GiB of free space
from the storage volume in 5,422 runs (and 27.5 MiB from two small volumes),
finished in 3 minutes 8 seconds, and gave 2,379 position rows where the live files
alone give 120. The same artifacts pointed at the whole image file gave 2,381: the
two more are lines that cross from an allocated block into a free one, which only a
read of the whole image sees.

What it costs is the write: the free space of every volume a pattern matches goes
into the data folder, 14.2 GiB in that VLEAPP run.

## Directory indexes

Since qnxprobe 1.63. An NTFS directory whose file name index has grown into an
`$INDEX_ALLOCATION` attribute gives one more member, kept apart from the files and from
the alternate data streams in `index_list`:

    <volume>/<directory>:$I30

A record that also holds a `$DATA` stream named `$I30` gives no such member: that name
then reads as the stream.

Only a pattern whose last segment ends in `:$I30` is matched against it
(`names_a_directory_index()`), and such a pattern is handed the indexes besides what
it was handed before. A pattern that does not end that way, `*:*` included, is handed
exactly what it was, and the run log counts the indexes on a line of their own, so the
count of alternate data streams does not move.

What is staged is the attribute as the volume stores it: one index block after another,
most starting `INDX` and some all zero, with the update sequence array of each block not
applied. The space past a block's last entry can still hold entries the list no longer
includes, and copies of entries it still does, which is what DLEAPP's two NTFS $I30
Index Slack artifacts read. The index root, which sits in the directory's `$MFT` record or in
a record that extends it, is not staged; those artifacts read it from the `$MFT`.

On four Windows acquisitions every file and stream member, and its size, was the same
with qnxprobe 1.62 and 1.63, and 5,313 to 13,158 directories gave an index.

## Deleted files a flash filesystem still holds

A flash filesystem writes a change to a new place and leaves the old data until its
block is erased, so a deleted file can still be read. The reader recovers those on
EFS, JFFS2, UBIFS and YAFFS (`recover_deleted()` and `read_deleted()`), and the
seeker offers each one it calls recoverable as a member of a `$Deleted` folder in
its volume:

    <volume>/$Deleted/<folder>/<name>.deleted-<n>

`<folder>` is the file's folder when the reader could place it and `$NoFolder` when
it could not. A recovered run of extents that no directory entry names is
`$NoName`. `<n>` is the entry's position in the reader's list for that volume, so
several versions of one file stay apart.

exFAT is asked too, since qnxprobe 1.61, and what it gives is a different thing
under the same folder name: orphan entries. Those are file entries still marked in
use, with a valid checksum, in directory clusters the volume marks allocated and the
directory tree no longer reaches. Nothing in such an entry says the file was deleted,
so read `$Deleted` there as "outside the live tree". An entry is listed only when
every cluster it names is allocated and unreached. Measured with VLEAPP on a Ford
SYNC Gen2 partition image (key `xtrmp_item016`, partition 2), whose `Windows`
directory lists nothing: 2,858 orphan entries, 2,455 listed, 974 of them with no
folder the reader could name. Nothing on the volume says which directory those 974
belonged to.

Only a pattern with `$Deleted` as one of its segments is matched against them
(`names_deleted()`). `*` and `*/gps.dat*` never reach a deleted file, and the reader
is not asked to look for any until such a pattern is searched. An artifact that
wants them names the folder, for example `*/$Deleted/*/gps.dat.deleted-*`, and
should say in its output that the row came from a deleted file: the member path
does.

An entry the reader names but cannot read whole is counted in the run log and not
listed. Its last modified time, where the filesystem kept one, is put on the staged
copy.

This was measured in VLEAPP, where the change was made (VLEAPP #332), and has not
been measured in this tool. On two GM OnStar flash images, both EFS (keys
`xtrmp_item081` and `xtrmp_item027`), the reader gave 3,040 and 901 entries, of
which 2,983 and 893 were listed and 57 and 8 could not be read whole. Most had no
folder the reader could place (2,875 and 672). Listing took under a second on each.
JFFS2, UBIFS and YAFFS go through the same code and were not run there: the tests
use a stand-in reader.

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
mtime and the `FileInfo` the run records. FAT32, FAT16, FAT12 and exFAT store a wall-clock
reading with no zone; the reader hands those back as text. The staged copy's
mtime is set from that reading in the machine's local zone, exactly as the zip
seeker sets it from a member's DOS stamp, and the `FileInfo` records no instant
for it, so no report field carries a zone the evidence never had.

## What it does not do

- It reads live files, a volume's free space for a pattern that asks for it (see
  Free space above) and the deleted files of a flash filesystem for a pattern that
  names `$Deleted`. Deleted records the reader can recover on NTFS, FAT and exFAT
  are not staged, nor are the entries an AD1 lists as deleted.
- It reads software RAID only as Linux md and LVM2 write it. Hardware RAID imaged as
  one logical disk is one image already. DDF and Intel IMSM (RST) arrays are not
  assembled; only a member of a mirror in its normal state is walked, on its own (see
  above). The GPT partitions of Windows LDM, Windows
  Storage Spaces and Apple RAID are not assembled either; when the run assembles RAID
  members (several images, or one holding an md member) the reader's RAID section
  names them as not read (from the reader's code, `raid_assemble`; no fixture here
  exercises it). The member search looks in the image's own folder only, not
  its subfolders, and does not follow the identities of the files it adds.
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
- It does not stage what the image does not hold. A cloud provider's online-only
  placeholder on NTFS records a size and stores nothing, and the run log says
  `Not staged` with the size recorded and the bytes stored. A file overlay-compressed
  with LZX (`compact /exe:lzx`) is not decoded and is not staged either; the three
  XPRESS forms are. Before qnxprobe 1.56 both kinds were staged as zeros.
- It does not stage a FAT or exFAT file whose cluster chain ends before its
  recorded size. The directory entry records the size and the allocation table
  records the clusters, and a volume can hold the two in disagreement. The run log
  says `Not staged` with the size recorded, the clusters the chain holds and the
  clusters that size needs. Before qnxprobe 1.59 the log said only that the reader
  returned fewer bytes than the size. The file is not staged in either case.
- It does not offer file slack, the bytes a file's cluster chain holds past the file's
  recorded size. An artifact sees each file at its size, so text that survives only in
  slack is not reached. This was measured in VLEAPP (VLEAPP #360) and has not been
  measured in this tool: on eight Ford SYNC Gen1 partition images, six artifacts that
  also read the partition image as bytes gave 2,336 rows from the acquisition folders
  and 2,293 from raw input, and all 43 rows raw input did not give sat only in the
  slack of a listed file.
- A sparse file is staged at its recorded size with its holes written as zeros, so
  the copy can occupy more than the file did in the image: an emulator disk recording
  6.4 GB and storing 108 MB stages as 6.4 GB. `qnxprobe.allocation(walker, node)` gives
  what the image stores for a file, for a caller that needs to know before writing.
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
