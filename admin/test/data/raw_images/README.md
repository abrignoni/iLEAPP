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
