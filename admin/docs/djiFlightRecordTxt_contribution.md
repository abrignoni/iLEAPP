# DJI TXT iLEAPP contribution and validation

Updated October 23, 2026. Branch: artifact/dji-flight-record-txt.
Upstream base: a1c48df4fc3ecab96916e28407332a37fe0717de.
All iLEAPP work is under DIRK/ILEAPP, a sibling of DIRK/ALEAPP. Standalone and existing ALEAPP files are untouched.
No commit, push, PR or GitHub message has been made.

## What changed

Adds original DJI GO / GO 4 / Fly DJIFlightRecord*.txt decoding to iLEAPP with
record and summary artifacts, UTC timestamps first, separate position sources,
relative per-row paths and actual files read as the third return value.
HTML, TSV, timeline, KML and LAVA use the existing framework. No external decoder,
CSV import, network call, API key, viewer, replay or photo correlation is added.

The accepted ALEAPP v0.3 decoder (PR1513, October16) is the starting point.
Original source SHA256: c991d072a8fabd0da83d000a2b997155063c1468bf212b873fac66772551303f.
It was initially AST-identical after metadata adaptation. Real iOS testing then
identified one framing difference now handled locally: the exact bytes
39 30 00 00 immediately before JPEG SOI. The parser skips those four bytes only
when SOI follows; it does not scan past arbitrary corruption. Existing raw JPEG
handling then consumes eight contiguous images, ending at the Details boundary.
Images stay in the source; image rows have no invented record-type number.

This shared decoder issue also exists in the untouched ALEAPP copy. A future
ALEAPP fix should port the bounded framing change and regression tests; no fix
has been silently propagated to that separate contribution.

MIT/format attribution to Luc Vauvillier, existing AI assistance credit and accepted
Neal/Alexis/Claude metadata remain. Accepted maintainer commit d34efa9c8f29b24c496fab0f1b0e65b661819d6d
contains `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; retain it when
preparing attribution. For a future authorized commit add actual-agent credit
`Co-Authored-By: OpenAI Codex GPT-6 <codex@openai.com>`. Do not invent human emails.

## Real iOS validation

Neal supplied VTO/NIST DF020 August2017 df020_flight_ios_backup.zip (698544846 bytes).
The source archive was read, never modified. Only original control files and the
responsive hashed TXT were staged in ignored admin/test/output/df020_ios_backup.
No whole-backup extraction was necessary.

- Unencrypted iTunes backup; Info.plist reports iOS10.3.2, hardware iPad5,1.
- Backup application metadata: DJI GO4, bundle com.dji.go, build2952.
- Original TXT Details separately reports app4.1.5, IOS(1), TXT version8.
- Manifest.db maps fileID cf2db800671979863d7f97d14983f99f1b323159 to
  AppDomain-com.dji.go / Documents/FlightRecords/DJIFlightRecord_2017-08-29_[12-21-48].txt.
- Original TXT SHA256: 50e7fcdef6db9490af4b058330ed0c03d2f3eccc80168fed4b263b431aef5c5a;
  1292669 bytes. Staged source hash remained unchanged after report generation.
- Actual iLEAPP `-t itunes` discovery succeeds with the existing pattern
  `*/Documents/FlightRecords/DJIFlightRecord*.txt`; no pattern change was needed.
- Full original log: 16441 displayed rows (16433 defined records + 8 JPEG entries),
  1 summary, 4515 aircraft OSD positions. No App/RC GPS rows in this sample.
  2718 undefined-type records counted in Summary (17:2537,18:1,20:1,27:1,30:178).
- Parsing reaches the record-area end with no warnings. Initial run stopped at
  offset612412 with 679786 bytes unread; these bytes were image framing and eight
  images, not additional telemetry. SOI starts at612416; final EOI ends exactly at
  Details offset1292198. The fix adds eight image entries without changing telemetry.
- Manifest and database both contain16441 record rows and1 summary row. KML has4515
  coordinate entries; timeline database has16442 rows. HTML and both TSV exports exist.
  Source metadata and row paths are extraction-relative.

Windows notes: pass an absolute backup input path. A relative input path triggered
an existing framework extended-path/SQLite URI error before artifact execution.
Manifest.db is marked WAL mode, but no WAL exists in the source ZIP. iLEAPP opens
that original database read-only with immutable=1; no source database bytes were
changed. An initial exploratory in-memory SQLite read normalized only the memory
copy's mode bytes; it was not used as evidence input or written to any fixture.

## Fixtures and tests

38 focused tests pass:32 accepted parser tests,3 iOS discovery/backup/evidence tests,
and3 added tests for prefixed JPEG clusters, unconfirmed prefixes and truncated JPEGs.
Eight official fixture comparisons pass:

| Case | Records | Summary | Evidence |
| --- | ---: | ---: | --- |
|1|5|2|Synthetic v6/v12, synthetic iOS paths|
|2|0|1|Public pydjirecord v14, synthetic iOS paths|
|3|160|3|DF020 Android; compact records and full original summaries|
|4|160|1|Real DF020 iOS v8; compact records and full original summary|

Case4 Summary retains the entire unchanged iOS TXT, including all eight images.
Case4 Records retains prefix+first160 displayed records (including intervening
undefined records), appends original Details, and updates only the Details offset.
Full public source provenance, original/compact hashes and construction offsets are
in admin/test/cases/djiFlightRecordTxt_PROVENANCE.md. Fixture ZIP paths are reconstructed
from the real AppDomain, rather than invented UUIDs. Actual backup reader behavior
was tested separately with the original Manifest.db and hashed source file.
The compact Records fixture omits the image cluster; full Summary processing and
focused synthetic tests exercise the framing regression.

The original six Android/synthetic fixture payloads remain byte-identical to the
accepted revision. Their decoded row multisets and headers are unchanged. New iLEAPP
snapshots were recorded only after path-adapted accepted baselines passed; row order
was the only difference. Case4 is a new baseline, not a replacement of Android results.

Required artifact checks pass. Sample-data structure:0 errors,115 pre-existing warnings.
CI-configured pylint passes on all three Python files. Isolated Python3.12 environment
is .venv inside iLEAPP; existing ALEAPP environment was not changed.

```powershell
$env:TZ='UTC'
.\.venv\Scripts\python.exe -m unittest admin.test.scripts.test_dji_txt_parser admin.test.scripts.test_dji_txt_ios
.\.venv\Scripts\python.exe admin/test/scripts/run_test_cases.py --module djiFlightRecordTxt
.\.venv\Scripts\python.exe -m pylint scripts/artifacts/djiFlightRecordTxt.py admin/test/scripts/test_dji_txt_parser.py admin/test/scripts/test_dji_txt_ios.py --disable=C,R --persistent=no
```

Profile plugins must name djiFlightRecordTxtRecords and djiFlightRecordTxtSummary,
not just the module filename. Complete loader run found no artifact-name collision.
Latest real-iOS report: admin/test/output/iLEAPP_Output_2026-10-23_Friday_151328.

## Sources and remaining gaps

Read current admin/docs and the module guide:
https://leapps.org/blog-post?post=2026-06-14-how-to-write-an-ileapp-module
Both required helpers, artifact_processor and logfunc, exist in iLEAPP; Context
supports get_files_found/get_relative_path and iTunes AppDomain reconstruction.

DJI confirms FlightRecords for iOS GO4 and Fly file sharing:
https://repair.dji.com/help/content?customId=en-us03400006894&documentType=artical&lang=en&paperDocType=paper&re=US&spaceId=34
The real backup now independently establishes Documents/FlightRecords for this GO4
sample. Research leads for GO and other releases are not substituted for device tests.
The four bundled public iOS filepath-list archives contain zero DJI candidate rows.

Pinned MIT reference examined during framing investigation:
https://github.com/lvauvillier/dji-log-parser/blob/e2e0775670a8391b4f7ecc40fca4cb01ea4a90fa/dji-log-parser/src/record/mod.rs#L319
https://github.com/lvauvillier/dji-log-parser/blob/e2e0775670a8391b4f7ecc40fca4cb01ea4a90fa/dji-log-parser/src/utils.rs#L26
The reference recognizes raw JPEGs and can skip invalid bytes to the next marker;
this module deliberately retains its stricter corruption behavior except for the
precise four-byte prefix observed in the real iOS evidence.

Real iOS coverage is GO4 4.1.5 / iOS10.3.2 / TXT v8 only. iOS GO and Fly, newer app/OS
versions, other image-prefix variants, encrypted iTunes acquisition and v13/14 iOS
files remain unvalidated. Public v14 metadata and synthetic v13 coverage remain.
Legacy v1–12 work offline; v13–14 readable metadata only with explicit encrypted
telemetry status; other versions explicitly unsupported. Missing values stay None,
Custom UTC timestamp inheritance is labelled, telemetry is never carried forward.
LAVA desktop visual inspection and the full cross-platform/Python CI matrix remain
outstanding. No iOS extraction is needed to establish this specific legacy sample;
additional samples would broaden coverage.

Suggested title: Add offline DJI TXT flight records for iOS.
Suggested PR description: Adds DJI TXT record and flight-summary artifacts, adapting
the accepted ALEAPP decoder to iOS discovery and bounded observed JPEG framing.
Validated on the real DF020 DJI GO4 iOS10.3.2 backup:16433 defined records,8 embedded
JPEG entries,1 summary and4515 aircraft positions, with no parse warnings. Includes
38 focused tests and8 fixture comparisons with public provenance. LAVA visual review
and other iOS app/version coverage remain outstanding. Publishing is not authorized.

## Folder relocation

Moved the complete checkout, .venv, fixtures and generated reports from DIRK/ALEAPP/iLEAPP to DIRK/ILEAPP at Neal's request. Existing ALEAPP files remain under DIRK/ALEAPP. The moved environment passes all 38 focused tests and eight fixture comparisons. Use .venv/Scripts/python.exe -m pip for package management because executable launchers may retain the former environment path. Historical generated reports retain their original run-path strings.

## User-reported LAVA visual review

Neal reported that the real iOS report looked good in LAVA after receiving the inspection checklist. This is user-reported visual acceptance; the agent did not perform the visual inspection. LAVA version was not supplied. The earlier outstanding-LAVA notes above are historical and this report closes that local visual review item. Cross-platform CI and broader iOS app/version coverage remain outstanding.
