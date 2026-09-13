# Anonymous Chat & Fun synthetic case

`testdata.anonymousChat.json` case 1 and its six artifact archives are generated
from a metadata-only iOS-shaped fixture for the iOS app Anonymous Chat & Fun
(bundle ID `com.anonimchat.app`). The fixture contains
synthetic SQLite, plist, and JSON records for container discovery, messages,
direction, conversation fields, media-table metadata, and a Photos `ZASSET`
reference. It contains no casework and no media payloads.

The snapshot baseline is recorded in UTC. Run the regression gate with:

```powershell
python admin/test/scripts/run_test_cases.py --module anonymousChat --strict
```

`admin/test/scripts/test_anonymous_chat_synthetic.py` separately mocks seeker
staging and Media Manager check-ins. It verifies the cache and Photos correlation
paths plus the LAVA conversation mapping without opening media bytes.

## Reproduction and release checks

The complete fixture builder is included at
`admin/test/scripts/build_anonymous_chat_fixture.py`. It creates eight fresh
SQLite/plist/JSON files from literal invented values. It takes no casework input,
stores no media payload, and refuses to replace an existing fixture or archive.
Use a new parent directory when rebuilding:

```powershell
python admin/test/scripts/build_anonymous_chat_fixture.py --output-root scratch/anonymous-chat-new/extraction
python -m unittest discover -s admin/test/scripts -p 'test_anonymous_chat*.py'
python admin/test/scripts/run_test_cases.py --module anonymousChat --strict
```

The focused tests cover duplicate filenames, contradictory sizes/types,
cross-container and cross-database collisions, direction/recipient metadata,
malformed URLs/timestamps, partial SQLite schemas, WAL visibility, read-only
database connections, Photos UUID/path ambiguity, source attribution, safe
staging patterns, and ZIP, TAR, iTunes, and extracted-folder report generation,
including two app containers that reuse the same conversation/message IDs.
Media Manager and signature calls in media-link tests are mocked; the CLI tests
generate metadata-only inputs and confirm that zero media items are registered.
Hostile synthetic message markup is checked as escaped HTML text, without
opening a browser or fetching its URL.

The provenance test regenerates the fixture and compares JSON/plist bytes plus
SQLite schema and row data in all six case archives. It ignores SQLite version
bytes that vary by platform. It skips only this archive comparison in the
upstream runtime-contract sparse checkout, which intentionally omits case
archives; the fresh-build and CLI tests still run there.

The 2026-09-13 changes retain all original fixture rows. Application Info now
attributes all consulted container plists; Messages and Conversations add a
source-scoped Conversation Key; incoming media recipient metadata identifies
the local account instead of repeating the remote sender; iTunes bundle-domain
and raw-image discovery are covered; and inferred filename/timestamp links are
no longer created.

## Interpretation and acceptance limits

LAVA uses Conversation Key for grouping and Other Party for its sidebar label.
The original Conversation ID remains separately available. Filesystem media rows
represent associations: the same file can appear once per referencing message,
with its own timestamp/participants. Count distinct Filesystem Path values when
counting files.

Message media is linked only through an application-recorded local path, an
SDImageCache key derived from stored URL text, or an explicit media/join key.
Size, timestamps, MIME compatibility, and filename similarity alone never link a
message. Contradictory or ambiguous paths, cache keys, and filenames are left
unlinked. Timestamp-only matching across the wider Photos library is not
performed. Photos originals are labelled because their contents and size can
differ from the transmitted media. Remote attachment URLs are never fetched by
the parser.

Supported discovery targets are full-filesystem ZIP/TAR and extracted-directory
layouts, hashed iTunes backups, and raw disk images/E01 acquisitions containing
the app's container paths. Standalone databases without an identifiable app
container are not targeted. No container UUID is hard-coded. Python 3.10 /
iLEAPP 2026.3.3 was used for local release checks; the other supported Python
versions require upstream CI.

These tests establish code and metadata/report behavior, not a forensic validation
certificate. Real-media rendering and case-specific association correctness need
an examiner's final check in a newly generated LAVA report. No examiner case data
or case media is included in these samples or expected outputs.
