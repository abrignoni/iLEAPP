# DJI TXT fixture provenance

The following accepted ALEAPP provenance is retained as historical source
documentation. Its descriptions of Android archive paths and original member
times apply to the ALEAPP source fixtures. The iLEAPP fixture archives instead
use synthetic iOS paths and new packaging times; all TXT member bytes match.
See the iLEAPP adaptation section below.

## Accepted ALEAPP source provenance

Case 1 is synthetic binary test data authored for this module. It contains version
6 and version 12 records with known coordinates, units, timestamps and gimbal
angles. It does not claim to be a mobile extraction or the DF020 corpus.

Case 2 contains the original public example from
[pydjirecord](https://github.com/rembish/pydjirecord/blob/cabbce1bb8c24bb00bd861af80aac7601c03e5f6/examples/DJIFlightRecord_2024-09-01_%5B14-55-49%5D.txt),
commit `cabbce1bb8c24bb00bd861af80aac7601c03e5f6`, unchanged. It is a version 14
encrypted log. Android-style archive paths were chosen for the test and do not
establish the acquisition device's OS or original filesystem paths.
The original TXT bytes are packaged twice because ALEAPP uses one fixture per
artifact. No API key or keychain is included.

Case 3 comes from VTO/NIST DF020's
`2018_June/mobile_android_logical/Android_Logical.zip`. The publisher archive MD5 was
verified as `6bc5cdc147e813f8744c04814a89e18a`. The two `dji.go.v4` logs are version 11
from June 19, 2018. The `dji.pilot` log is version 9 from October 10, 2017;
it is retained as an older log, not claimed as a June salted flight.

The Summary case 3 zip holds the three original logs, unchanged, with their original
archive paths and member times. SHA256:

- `DJIFlightRecord_2018-06-19_[14-50-34].txt`: `0a9f1816d52a98f840f6e67c08a14473ae5a0a2e75e9484d5de66368c4fd4c4a`
- `DJIFlightRecord_2018-06-19_[18-48-38].txt`: `ab5bbc58a921d81c323a76c3a9d955fde58d503536facf43306e7e6bbb208c8d`
- `DJIFlightRecord_2017-10-10_[10-02-22].txt`: `f134bef34e6877ae5a030297f56ae6e12fe946b468c5143ef9976c08170295f8`

The Records case 3 zip holds shortened copies of two of them, so the recorded baseline
stays small (the full Records baseline was about 42 MB). Each copy keeps the original
100-byte prefix, the first N complete records, and the original Details block, with the
prefix's Details offset rewritten to the new position. Nothing inside a kept record is
changed. Archive paths and member times are the originals.

- `DJIFlightRecord_2018-06-19_[18-48-38].txt`: first 60 records, plus the 4 bytes that
  sat between the last complete record and the Details block in the original, so the
  stopped-parse warning is still exercised. SHA256 of the copy:
  `d48094f0a54c5e5b9a0338f408f367391896bb92fc12e3b9792d06657ee2794c`.
- `DJIFlightRecord_2017-10-10_[10-02-22].txt`: first 170 records. SHA256 of the copy:
  `e5e9d6c0b5b10631696eeba60e4ab95aa09446db3f4a429a91e1d886f53e67b5`.

Together the two copies contain every record type the Records artifact decodes into
fields, App Tip and App Warning messages, and types it counts without reporting. App
Serious Warning (type 24) does not occur in DF020. The dataset's MIT notice is preserved in
`djiFlightRecordTxt_DF020_DATASET_LICENSE.txt` beside this file.

The case 2 public example is distributed with this license:

MIT License

Copyright (c) 2025 pydjirecord contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## iLEAPP adaptation (2026-10-23)

All six fixture archives retain their accepted ALEAPP member bytes; only member paths were repackaged to private/var/mobile/Containers/Data/Application/SYNTHETIC-DJI/Documents/FlightRecords/. These are invented packaging paths, not evidence of an iOS acquisition. Android source metadata remains Android. Baselines are the accepted v0.3 outputs with only source-path substitution; any comparison failure must be investigated. No iOS or app version is asserted.

New iLEAPP snapshots were recorded only after all six path-adapted accepted baselines passed. Headers and decoded row multisets were identical; row ordering alone differed. The original evidence content and legacy Android platform fields were retained.

## Real iOS case4 — DF020 August 2017

Corpus key: df020_mavic_pro_ios (VTO-published MD5 b6f1280375b0c8512dcbcf440bd7a362, SHA1 3d507bd020bd35873bb1c06d5476a37a20edc656).

Source archive: df020_flight_ios_backup.zip (698544846 bytes), supplied locally by Neal from VTO/NIST DF020. Unencrypted iTunes backup. Info.plist reports iOS 10.3.2 and product iPad5,1. Backup application metadata identifies DJI GO 4, bundle com.dji.go, build 2952. The original TXT Details reports IOS (1), app 4.1.5 and log v8. These observations are separate metadata sources, not invented device versions.

Manifest.db maps fileID cf2db800671979863d7f97d14983f99f1b323159 to AppDomain-com.dji.go / Documents/FlightRecords/DJIFlightRecord_2017-08-29_[12-21-48].txt. Original TXT size 1292669 bytes; SHA256 50e7fcdef6db9490af4b058330ed0c03d2f3eccc80168fed4b263b431aef5c5a. Summary case4 preserves all TXT bytes. Records case4 keeps bytes 0:6380 (first 160 displayed records, including intervening unknown types), appends original Details bytes 1292198:end, and changes only the prefix Details offset to 6380. Compact SHA256 0dff176c1cae3913b9649d73fd9cdc577e4a5704215365bcfad1640c2574d015. The reconstructed iLEAPP path is used in ZIP fixtures. The fixture ZIPs are file-oriented discovery tests; a separate actual -t itunes run against unchanged backup control files and the hashed original TXT validates AppDomain discovery. The source ZIP and TXT are unchanged.

Full TXT output: 16441 rows = 16433 defined records + 8 embedded JPEG entries; 4515 OSD positions, no App/RC GPS fields in this sample. Undefined-type counts: type17=2537, type18=1, type20=1, type27=1, type30=178 (2718 total). No warnings after bounded handling of observed prefix 39 30 00 00 immediately preceding JPEG SOI at offset 612416. Eight contiguous JPEGs end exactly at Details offset 1292198. No image is extracted or correlated.

Reference comparison: dji-log-parser v0.5.7 commit e2e0775670a8391b4f7ecc40fca4cb01ea4a90fa, dji-log-parser/src/record/mod.rs lines319-337 and src/utils.rs lines26-95, recognizes raw JPEGs and can skip invalid bytes to a following JPEG. This implementation does not adopt broad resynchronization: it only skips the exact four-byte prefix observed in this sample when SOI follows. Other framing variants remain unvalidated.
