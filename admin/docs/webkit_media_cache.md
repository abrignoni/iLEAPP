# WebKit Media Cache — experimental version 0.1.1

`webkitMediaCache.py` adds one selectable artifact, **WebKit - Media Cache**.
It reconstructs stored resources from `MediaCache/CachedMedia-*` block mappings,
registers the derivatives with the existing media manager, and produces HTML,
TSV and LAVA rows. Repository-level timestamp events are written to `tl.db` in
the same pass. No FFmpeg, network access, additional runtime dependency or codec
transcoding is used by this module.

## Evidence and scope

The cache layout is an experimental inference from byte-preserved members of
the public **Magnet Virtual Summit 2023 iOS 16.1.1** filesystem extraction:

`https://storage.googleapis.com/mvs-2023/00008101-0010541A1130001E_files_full-001.zip`

It is not a published Apple format specification. Successful media recovery has
been exercised on that image in a current Chrome container and in the
SafariViewService store of a current Gmail container. The current container owner
comes from acquired mobile-container-manager metadata. This does not establish
which application originally created a file, which email initiated a request, or
whether a user clicked, viewed or played it. A stored resource can itself be a
preview or a segment; complete byte coverage of it does not make it an entire
original video.

Two byte-preserved, empty indexes from the **MVS 2021 iOS 14.4** image are a
negative-data check, not positive validation of the media block layout on iOS 14:

`https://digitalcorpora.s3.amazonaws.com/corpora/scenarios/magnet/2021%20CTF%20-%20iOS.zip`

The original archive members were acquired selectively and checked against their
archive CRCs and recorded SHA-256 values. The entire archives were not downloaded
or checked against publisher whole-archive hashes. Only public CTF or explicitly
synthetic data is included in the fixtures.

## Recognized cache structures

The observed outer atoms use big-endian 32-bit lengths, including their 8-byte
headers. Duplicate atoms, truncation and invalid bounds are rejected.

| Atom | Observed interpretation |
| --- | --- |
| `frei` | Initial atom; contents are not treated as media |
| `verz` | Outer version 2 |
| `stid` | Plist with identity version 1, `Size`, `URL` and other retained values |
| `stst` | Version 5, marker `crab`, block size, entry count and block entries |
| `stcs` | Storage containing the physical media ranges |

Each block entry is `logical_index:uint32`, `length:uint32`,
`physical_offset:uint64`, all big endian. Logical offset is the index multiplied
by the stored block size. Physical offsets are absolute offsets in the cache
file. The observed block sizes are 16,384 and 65,536 bytes. The resource bytes
are written in logical order, rather than their physical order in the cache.

Before export the parser requires unique logical blocks, valid lengths, ranges
inside `stcs`, no physical overlaps, and full contiguous coverage of the stored
resource size. It records gaps as half-open `[start, end)` ranges. It exports no
partial playable approximation and inserts no padding or fabricated headers.
Unsupported formats and incomplete entries remain in the report with their
status and any successfully decoded identity metadata.

The source is opened read-only and hashed before and after reconstruction. Each
exported block is checked again against the written output. Source SHA-256,
derivative SHA-256/MD5, offsets, lengths and per-block SHA-256 values are retained.
These are reconstruction checks; there is no producer-provided cryptographic
checksum to authenticate the cache table itself.

Processing streams file data rather than allocating the stated resource size.
Limits are 1,000,000 table entries, 4 MiB identity metadata and 16 MiB repository
plist. Other outer/identity/table versions and block sizes are left unsupported.

## Media output

The stored `ftyp`/`moov`/`mdat` structures are used to recognize ISO-BMFF content.
Extended MP4 atom lengths and end-of-file lengths are supported for the rebuilt
resource. Stored movie/track durations, handler types, sample-entry codec tags
and video dimensions are extracted where available. Duration Seconds is the
stored movie-header duration, not a measurement of user viewing. Encrypted media
is not decrypted. No media decoder runs in the parser; format recognition and
box bounds alone are not a promise of successful playback on every player.

Video is saved as `.mp4`, audio-only MP4 as `.m4a`; unknown reconstructed bytes
are retained as `.bin`. The URL extension is not used to choose the media type:
the public `success.mp3` URL actually contains an MP4/AAC audio resource.
The normal HTML and LAVA media columns reference the generated files. A separate
Recovered File path retains the derivative even when media registration is
unavailable. LAVA's media filesystem dates follow its existing source-file
handling; they are not presented as playback events by this module.

## Repository relationships and time

Only the `diskcacherepository.plist` in the **same acquired cache directory** is
considered for a cache file. Entries in `checkedinlist` and `checkedoutlist` are
retained as stored. An observed UUID-plus-`=` checkout prefix is removed only for
the separately displayed repository URL; the original key remains in Metadata.
These list names are stored states, not user-action classifications.

Resource URL comes from the resource identity plist. Repository URLs are a
separate column. Exact stored-path matches, same-directory filename plus exact
identity-URL matches, filename-only candidates and conflicting URLs are labelled
separately. No URL normalization, token stripping or cross-container lookup is
used to make a match. The public SafariViewService index names older container
GUIDs: this is recorded rather than silently replacing those GUIDs. A missing
referenced file stays as an index-source row; a matching filename elsewhere is
not substituted. Empty and malformed repositories also remain visible when they
have no media rows of their own.

`lastmodtime` is interpreted as seconds since **2001-01-01 UTC**. That epoch fits
the observed indexes; no closed-source producer implementation has been checked
to establish every circumstance in which the field is written. Its raw numeric
value and the interpretation remain available. `lastmodpid` is retained as
stored, without resolving it to a particular process lifetime.

There is **one event per repository with a usable lastmodtime**, named
`WebKit MediaCache - Repository Last Modified`. It describes the index, not an
individual resource request or playback. Missing, invalid, sentinel and
non-finite dates do not produce events. Media rows repeat their repository time
for context but do not each create a timeline event. UTC microseconds survive
in `tl.db`; LAVA's existing typed datetime columns have integer-second precision,
with the original fractional value additionally retained in Metadata.

## Public-run results

The full selected iOS-16 input contains **16 acquired files**: 10 cache files,
three repository indexes and three container-owner metadata files.

| Output | Result |
| --- | --- |
| Report rows | 11: 10 cache entries and one empty repository |
| Reconstructed media | 6: five videos and one audio-only resource |
| Long video | About 429.5 seconds, 640×360, `avc1` + `mp4a` |
| Other videos | Four clips, about 5–6 seconds each |
| Audio | About 0.49 seconds, `mp4a` |
| Unreconstructed caches | Three all-zero files and one unsupported layout |
| Timeline | Three repository-level events |

All six derivative SHA-256 values match the earlier independent PoC outputs.
All six files written by this module were subsequently fully decoded with
FFmpeg, with zero errors. This is development validation; FFmpeg is not a runtime
dependency. Controlled duplication into two evidence roots is an isolation and
scaling test, not a second independently acquired image.

## Fixtures and tests

Three recorded cases are provided under `admin/test/cases/` with their baselines
under `admin/test/results/webkitMediaCache/`. Every fixture ZIP is under 10 MB.

| Case | Contents and expected result |
| --- | --- |
| `casepublic_ios16` | Original small media and metadata; long cache omitted deliberately: 11 rows, five media check-ins, three index events |
| `casesynthetic` | Reversed H.264/AAC blocks, two containers, a gap, zero/unsupported files and a missing reference: six rows, two media check-ins, two events |
| `caseios14_empty` | Two original empty indexes: two rows, no media, two index events |

The 35,829-byte `admin/test/fixtures/webkitMediaCache/tone_test.mp4` is synthetic,
generated solely for these tests. It contains two seconds of a color test pattern
and an 880-Hz tone, generated with FFmpeg's `testsrc2`/`sine` sources, libx264
and AAC. Runtime unit tests use the committed file and need no FFmpeg.

Version 0.1.1 additionally tests I/O failure reporting: unreadable cache files do
not stop another container's recovery, unreadable indexes do not block media
recovery, and errors retain their exception/errno type without publishing the
examiner's local file paths. The successful reconstruction path and the six
public derivative hashes are unchanged from the manually tested version 0.1.0.

On 2026-10-15 the contributor confirmed successful processing of the full
10.7-GB MVS 2023 source ZIP with version 0.1.0. This is a separate manual test;
no exported report from that run was supplied for independent count verification.

From an existing iLEAPP source environment, use the **same Python interpreter**
for dependencies and every command:

```text
python -m unittest admin.test.scripts.test_webkit_media_cache -v
python admin/test/scripts/run_test_cases.py --module webkitMediaCache
python ileapp.py -t zip -i EXTRACTION.zip -o EXISTING_OUTPUT_FOLDER -m admin/docs/webkit_media_cache.ilprofile
python admin/scripts/check_artifact_output.py GENERATED_REPORT_FOLDER --strict
```

Use `admin/docs/webkit_media_cache_validation.json` for the actual final checks,
counts and runtime. No Windows/macOS native build, full Python-version matrix,
controlled cache-creation/deletion study or independent maintainer test is
claimed. Additional positive images and layout versions remain validation gaps.
