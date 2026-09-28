# Raw image fixtures for the seeker tests

Small filesystem images the raw image seeker (`scripts/raw_image.py`) is tested
against, each with a list of the files it holds and their SHA-256, written by a
reader other than the one under test.

| image | filesystem | files | hash list written by |
| --- | --- | --- | --- |
| `ntfs-fixture.img.gz` | NTFS, 16 MiB, 475 files with fixups, attribute lists, LZNT1 compression and sparse runs | 475 | `sha256sum` over an `ntfs-3g` mount of the image on Linux, at build time (qnxprobe `tools/make_ntfs_fixture.sh`) |
| `fat32-deleted.img.gz` | FAT32, 64 MiB, two live files (`a.bin`, `c.bin`) and deleted ones | 2 | `shasum -a 256` over the image mounted read-only by macOS's own FAT driver, 2026-09-12 |
| `exfat-deleted.img.gz` | exFAT, 64 MiB, two live files and deleted ones | 2 | `shasum -a 256` over the image mounted read-only by macOS's own exFAT driver, 2026-09-12 |
| `apfs-fixture.img.gz` | APFS, 32 MiB, a container holding one volume of 411 files, one of them decmpfs-compressed, and a symbolic link | 411 | `shasum -a 256` over the files as macOS's own APFS driver wrote them, and the build fails unless The Sleuth Kit's reading of the finished image agrees (qnxprobe `tools/make_apfs_fixture.sh`) |
| `ntfs-streams.img.gz` | NTFS, 8 MiB, 28 alternate data streams, among them two `Zone.Identifier` streams and a `$J` whose front is a 1 MiB hole and whose run list continues in a second MFT record, beside a stream sized and never written, which is not listed | 28 streams | The Sleuth Kit's `icat` from each stream's first stored cluster, as counted by `istat`, at build time, and the build fails unless `ntfs-3g` reads back every stream as written (qnxprobe `tools/make_ntfs_streams_fixture.sh`) |
| `lean-multi-ntfs-c9.ad1` | AD1 (logical evidence), 36 KB, two sources: an NTFS volume (`U:`) and a folder (`C:\AD1Lean\second`), with an alternate data stream and a file FTK Imager lists as deleted | 7 live files and 1 stream | FTK Imager 4.7.3.61's own listing of the image, `lean-multi-ntfs-c9.ad1.csv` (UTF-16, stored MD5 per file), written when it made the image |
| `ftk-ad-cert-ad1.ad1` | AD1 of three files, AD-encrypted and sealed to a test certificate; opens with `ad-cert-test-key-2048.pem` | 3 | `shasum -a 256` over the three source files before FTK Imager 4.7.3.61 imaged them, 2026-09-27 (`ftk-ad-cert-ad1.sha256`) |
| `bitlocker-xts128.img.gz` | BitLocker (AES-128-XTS) around qnxprobe's SquashFS fixture, 272 KiB; opens with its password, its recovery password or `bitlocker-xts128.BEK` | 612 | the test carries the file count and two SHA-256 from qnxprobe's `squashfs.src.sha256`, hashed from the source files the SquashFS image was built from |
| `apfs-converted.sparseimage.gz` | Apple sparse image holding an APFS volume macOS encrypted in place after files were written, with a passphrase hint, 345 KiB; opens with its password | 3 | `shasum -a 256` over the files while macOS had the volume mounted, after the last was written (qnxprobe `tools/make_apfs_converted_fixture.sh`, `apfs-converted.sha256`) |

The two AD1s and the test key are copies of fixtures committed in
[abrignoni/ewfprobe](https://github.com/abrignoni/ewfprobe) under `tests/fixtures/` at
commit `34c34b8496f0f3d57450d77b7f27a3247f4b08aa`, the BitLocker image and its
startup key of fixtures in qnxprobe at `2149e20cdf4951ebc900b0e560514175eda285d7`
(built by its `tools/make_bitlocker_fixtures.py`), and the encrypted APFS image of the
fixture in qnxprobe at `a45821b9b24017c280eae63757065e1819c9772d`. Every key, password
and hint in them is a test value made for the fixture.

The images are copies of the fixtures committed in
[abrignoni/qnxprobe](https://github.com/abrignoni/qnxprobe) under `tests/fixtures/`,
taken at commit `34cc4607799f58ab9157fc4be1d89098f687699d` (`ntfs-streams` at
`75164a971a80b54acaf23306228e2f047ce50a1d`); that repository's
`tools/` scripts say how each was built. They are stored gzipped and the tests
decompress them into a temporary folder. The FAT and exFAT images were written on
a Mac and also hold `._` AppleDouble companions, which the macOS driver hides and
the reader lists; the hash lists cover the files a person put there.

The `.live.sha256` lists are "<sha256>  <path>" lines, paths relative to the
volume root, the same shape `sha256sum` writes. `ntfs-streams.sha256` has the same
shape with a stream's path written `<file>:<stream>` (`:<stream>` on the root), after
a few `#` lines saying which two streams it leaves out because they store nothing.
