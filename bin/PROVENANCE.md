# bin/

Holds the third-party `unifiedlog_iterator` executable used to read Apple Unified Log
`.tracev3` data directly, so Unified Logs can be imported without a Mac and without
Apple's `log show`. See `scripts/unifiedlogs.py` for how iLEAPP calls it.

The executable is **not committed**. It is fetched per build:

```
python admin/scripts/fetch_unifiedlog_iterator.py
```

That verifies a pinned SHA-256 before writing anything, and also writes
`LICENSE-unifiedlog_iterator` next to the binary. Builds without it still succeed; they
just ship without native Unified Log support, and the artifact reports that at runtime.

## What is pinned

| Platform | Archive sha256 |
|---|---|
| macOS arm64 | `bf5c4a3418b133fbd403ca7893a2280acb8c2c3605b4ad6f87f9fc75b35a20b7` |
| macOS x86_64 | `32e23956c3ac6364f56e96243357cf02959f79a6e24a5afddba1047914bf7f1a` |
| Linux arm64 (gnu) | `ab40daf464376a2e52c4b51fd82b003b7f360a4e2726501ba853889fa3a959f4` |
| Linux x86_64 (musl) | `c1fea0f142850ac05e0faf66f3d69aca848793bc121e972238fb1927daf31004` |
| Linux x86_64 (gnu) | `7192a187f93c6fb8eafdad9885522e73dc2ae7a9a5000f5957edd4fcd0ca1c82` |
| Windows x86_64 | `4776ac9c677ad3bdec6a0cee3e92e27308f7493a0ac4e4fedde65555eb36373d` |

Project: [mandiant/macos-UnifiedLogs](https://github.com/mandiant/macos-UnifiedLogs),
version v0.7.0 (released 2026-09-14), Apache-2.0 (`LICENSE-unifiedlog_iterator`).

Every digest above was verified by downloading the archive and hashing it independently,
not by trusting the published `.sha256` files alone. Digest comparison in the fetch
script is case-insensitive: upstream's Windows `.sha256` is published in UPPERCASE
(PowerShell `Get-FileHash` style) while the others are lowercase, and some files print
the digest twice on one line. Presentation quirks of the publication, not corruption.
When bumping PINNED_VERSION, verify and pin all six the same way.

## Linux: musl, not gnu

`linux-x86_64` fetches the **musl** build, verified `static-pie linked` - it carries no
dynamic libc dependency at all. The gnu build links the glibc of whatever machine built
it, and a binary built against a newer glibc refuses to start on older distros with
`version 'GLIBC_x.yy' not found`. iLEAPP ships Linux as an AppImage, whose whole premise
is one file that runs anywhere; forensic workstations also skew old and locked down.
`--platform linux-x86_64-gnu` remains available. No musl build is published for aarch64.

## Why the version is pinned

An examiner needs to be able to say which parser produced a set of records. Pin the
version, record it here, and change both together. When a release is built, the version
above is the one that shipped.

## What changed from v0.6.0 to v0.7.0, measured

Upstream's v0.7.0 notes: lzbitmap decompression, initial support for GoldenGate and iOS
27, more detail on Simpledump and Statedump entries, and a fix for plaintext plists in
Statedump entries. The command line, the JSONL field names and the fields
`scripts/unifiedlogs.py` and `logarchive.py` read (`timestamp`, `process`, `pid`,
`subsystem`, `category`, `message`, `evidence`) are unchanged.

Both versions were run over the same assembled input for 13 iOS corpora (iOS 12 to 26,
10 of them the ones cited in the `logarchive` artifact's `sample_data`) and a live macOS
26.6.2 log store, 236,802,895 records in total. Every unit produced the same record
count under both versions, and every `sample_data` count was reproduced to the digit. On
12 of the 13 iOS units and the macOS store every record paired one to one across
versions; the exception is the timesync case described below. What differs is content,
all of it in the direction of more or corrected information:

- Simpledump and Statedump rows carry a Process Image Path that v0.6.0 left blank (every
  such row, on every unit).
- A `%.f` or `%{public}1.f` specifier (precision given with no digits) was left in the
  message verbatim by v0.6.0, and the arguments after it were rendered against the wrong
  specifiers: in one locationd message the accuracy 59 was printed under the next field
  as the raw bits of the double, 4633500329122463744, and the `src` field (`als` under
  v0.7.0) carried the raw bits of the vertical accuracy, 86.72. v0.7.0 renders the
  specifier and the fields line up. Counted as rows whose rendered message still carries
  such a specifier: 280,107 rows across the 13 iOS units under v0.6.0, 0 under v0.7.0.
  v0.6.0 also wrote a `Failed to parse float log message value` warning to stderr in
  numbers close to those row counts (dexter_ios18: 14,122 warnings against 14,136 such
  rows); v0.7.0 writes none.
- DNS `getaddrinfo` option flags are decoded (`0x20 {use-cache-only}` where v0.6.0 wrote
  `Unknown DNS getaddrinfo options`), a private-string argument that v0.6.0 sliced from
  the wrong offset (its text began with the tail of the preceding string) is read
  correctly, and one location decoder key is spelled `locationServicesEnabledStatus`.

**Timestamps can differ when one boot's timesync records span two files.** v0.6.0 read
the timesync directory in whatever order the filesystem returned it; v0.7.0 sorts the
files by path (upstream's comment: "macOS does not guarantee order of files returned by
the filesystem"). Both versions append the sync records of a boot uuid already seen to
the records read earlier, and the timestamp walk stops at the first record whose kernel
time exceeds the entry's, so the records have to arrive in ascending order for that walk
to select the right one. On felix23_ios16 boot 5C73B4A335FC4145A14735B2E784E369 has
records in both 0000000000000002.timesync and 0000000000000003.timesync, and this Mac's
APFS directory listed 03 before 02. Result: 3,121,195 of its 19,419,414 records carry a
different timestamp under v0.7.0: 804,643 rows in 6 tracev3 files move by 659.9 to 660.7
s, and 2,306,530 rows in 12 files by 15 to 39 ms. To decide which is right, 400 records
on the affected files whose message text carries a wall-clock string were compared with
the record timestamp, whole-hour zone offsets removed: the string sat within 45 s of the
timestamp on 91 of them under v0.7.0 and on 12 under v0.6.0, and an accessory
launch-history record carrying a launch date was 2 s from its own timestamp under v0.7.0
and 662 s under v0.6.0. Two other units (ai16_ios26_sysdiag, hc_ios18_7) also have a
boot spread over two timesync files and agreed under both versions here; a v0.6.0 result
on those may depend on the examiner's directory order, which this run did not vary. The
other 10 iOS units and the macOS store have no boot spanning two files.

Statedump messages built from a protobuf are serialized from a hash map, so their key
order varies from run to run of the same binary (100 of the 2,932 such rows on
rodeo_ios17_sysdiag differed between two runs of v0.6.0). That is not a version
difference.

No corpus in hand runs iOS 27, so the lzbitmap and GoldenGate paths are unexercised
here; they are code-present only.

Speed: on hc_ios26_sysdiag (6,457,901 records), three alternating runs of each binary
with output discarded and no other parser running, on an Apple M-series Mac, took 45.5,
46.0 and 48.5 s for v0.6.0 and 41.7, 41.7 and 41.8 s for v0.7.0. The full sweep, where
runs shared the machine, put v0.7.0 between 0 and 12 percent faster on every unit and
never slower.

## License obligations

Apache-2.0 permits redistribution inside this MIT-licensed project. For any build that
includes the binary:

- `LICENSE-unifiedlog_iterator` ships alongside it.
- `THIRD-PARTY-NOTICES-unifiedlog_iterator.txt` ships alongside it. The binary statically
  links Rust crates published under their own licenses; every one of the 57 on the list
  offers MIT or Apache-2.0, alone or as one of the choices its declared license gives.
  Upstream's release archive carries only its own LICENSE, so the notices are generated
  here by `admin/scripts/make_unifiedlog_notices.py` and committed. Its `--verify` option
  checks a fetched binary against the committed file without network access, and the test
  builds run it after fetching.
- The PyInstaller specs refuse to build when the binary is present and either file is not.
- Attribution stays in `ATTRIBUTIONS.md`.
