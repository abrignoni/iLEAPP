# ZIP search literal prefilter: evaluation

This candidate speeds up `FileSeekerZip.search` by rejecting filenames that lack a necessary literal substring before calling the existing wildcard matcher. The production diff adds 19 lines and changes two lines in `scripts/search_files.py`. The regression tests and this evaluation are separate from that small production change.

## Behavior and scope

For normalized patterns without brackets, each literal segment between `*` and `?` must occur in every matching string. The helper selects the longest such segment once per uncached search. Each filename is normalized and prefixed with the same `root/` string used by the existing matcher. A missing required segment rejects the filename; the original matcher still confirms every accepted candidate.

Any `[` or `]`, including malformed bracket syntax, disables the prefilter. Empty literals also retain the existing matcher path. Extraction order, duplicate-member selection, corrupt-member handling, cache/force behavior and first-hit behavior are covered by regression tests. Other seeker classes and `peek` are unchanged. The existing normalization cache remains; the candidate adds no retained filename index or second filename collection.

## Repeated timing results

Measurements used macOS arm64 and Python 3.14.6, with `PYTHONHASHSEED=0`, bytecode writing disabled, ZIP input and `--hash`. Baseline runs substituted the original search method from the preserved source; candidate runs used the edited method. The remaining code, inputs, profile and instrumentation were the same.

The focused profile selected 12 artifacts, plus mandatory framework processing. Each row below summarizes three measured runs per version in fresh processes and output directories. Runs were warm, with alternating baseline/candidate order. The iOS 16 and iOS 18 images also had separate unmeasured warm-ups for both versions. These are shared-machine measurements with VMs running, not cold-start or isolated-hardware claims.

| Image registry key | Baseline wall median (range), seconds | Candidate wall median (range), seconds | Speedup | Elapsed reduction |
| --- | ---: | ---: | ---: | ---: |
| `iphone11_ios17` | 20.122 (19.935–20.306) | 9.558 (9.548–9.806) | 2.11x | 52.5% |
| `magnet_ios16` | 10.622 (10.621–10.627) | 4.728 (4.717–4.815) | 2.25x | 55.5% |
| `iphone12_ios18` | 8.957 (8.919–8.972) | 3.647 (3.631–3.698) | 2.46x | 59.3% |

| Image | Search-time median, baseline → candidate, seconds | Peak RSS median, baseline → candidate, MiB |
| --- | ---: | ---: |
| iOS 17 | 15.226 → 4.790 | 1159.0 → 1155.6 |
| iOS 16 | 7.279 → 1.394 | 777.5 → 773.2 |
| iOS 18 | 6.288 → 1.037 | 648.5 → 648.3 |

Memory use did not increase materially; small RSS differences are not claimed as savings. Baseline method compilation adds a measured median 0.00972 seconds after imports (10 trials), included in wall timings. These figures describe these workloads, not a guaranteed speedup for every profile or platform.

An actual-method enumeration experiment over eight selected patterns, with already-staged mappings and no extraction, measured 7.610 versus 1.504 seconds when summing per-pattern medians: 5.06x. This is a search-only result, separate from end-to-end timings.

Broad patterns can pay overhead when the substring excludes few names. On 830,298 members, `*a*` measured 0.418 versus 0.430 seconds (three warm trials per version), about 2.9% slower in that small experiment. All ordered matches agreed. Other broad/bracket patterns were near the baseline. No universal per-pattern speedup is claimed.

## Corpus output checks

The focused outputs matched in ordered searches, evidence data, exports, media and staged-file bytes under the comparison rules below. All six iOS 17 outputs and all eight outputs for each additional image were retained and compared, including the two additional-image warm-ups.

| Focused image | Reported rows | Artifact outputs | Files in data/ | Media files | Exports | Database tables |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| iOS 17 | 1,202 | 21 | 30 | 8 | 14 | 26 |
| iOS 16 | 313 | 11 | 19 | 0 | 10 | 16 |
| iOS 18 | 311 | 6 | 16 | 2 | 8 | 11 |

A separate full all-artifact iOS 17 baseline/candidate pair both exited successfully and produced:

- 22,832,461 evidence rows across 675 artifact outputs and 680 database tables.
- 76,212 files in `data/` (including generated derivatives), 7,456 media files and 660 exports.
- Identical ordered source fingerprints, cache flags, match counts and staged counts for all 2,598 search calls, including 1,168 distinct uncached patterns.
- Matching typed, ordered evidence rows, schemas, recorded evidence dates, file relationships, artifact HTML tables, exports, media and staged-file bytes. Both databases passed integrity checks with zero foreign-key violations.
- Zero traceback, “had errors” or “failed after” markers in either console log.

That single full pair recorded 1,695.597 seconds (28.3 minutes) for baseline and 877.667 seconds (14.6 minutes) for candidate. Native Windows validation overlapped part of the baseline. These are reference timings from a correctness pair, not repeated isolated full-workflow benchmarks.

### Comparison rules and filesystem timestamps

Output-folder locations and parser execution start/end times are normalized. Process-local Python file IDs are replaced by fingerprints of the complete file record excluding that ID, preserving duplicate multiplicity and every relationship. Only the two framework file-ID tables are sorted; artifact-row order is retained. Report index/script logs are excluded from artifact HTML-table comparison. Export SQLite sidecars are not separate exports; logical database contents, including WAL, are read normally.

Strict filesystem-mtime equality did not hold for the full pair. There were 209 SQLite SHM files and 501 parser-generated PNGs with differing filesystem mtimes. Their bytes and recorded source/evidence dates matched. The PNGs comprise 482 App Snapshots derivatives, seven Widget derivatives and 12 SMS-preview derivatives. Two unchanged-baseline-only runs of those three artifacts reproduced varying mtimes with identical bytes for every one of the same 501 PNGs; their 525 evidence rows and other report outputs agreed. SHM mtime variation also occurred between unchanged baseline runs in the focused evaluation. Strict mismatch flags were retained; no blanket PNG or evidence-time exclusion was added.

The bounded-memory database comparator was checked against 11 constructed fixtures covering types, ordering, rowid behavior and file-ID relationships, and against the earlier real 26-table focused output. Streaming output-path normalization was checked at 15 chunk boundaries. Original reports, commands, image-hash records, per-run timings, logs and comparison results are retained locally; no corpus payload is included in this change.

## Regression and platform coverage

Nine new tests cover the filter's necessary-substring property, 24,008 generated pattern/name comparisons under POSIX and Windows normalization, real ZIP staging/order/bytes, directories and sidecars, bracket fallback, first-hit caching, force re-extraction, no matches, matcher-call reduction and corrupt-member continuation. Separate enumeration checks covered all 1,168 recorded patterns on 8,196 sampled/edge names, plus 39 selected patterns on all 830,298 archive entries. The full workflow then checked every search actually issued by that run.

| macOS Python | Full suite run | Failures | Errors | Skipped |
| --- | ---: | ---: | ---: | ---: |
| 3.11.18 | 2,313 | 0 | 0 | 56 |
| 3.12.1 | 2,256 | 0 | 0 | 59 |
| 3.13.18 | 2,313 | 0 | 0 | 56 |
| 3.14.6 | 2,313 | 0 | 0 | 59 |
| 3.15.2 | 2,313 | 0 | 0 | 56 |

A fresh PR-branch run based on `77202309` again passed all 2,313 tests on Python 3.14.6, with zero failures/errors and 59 skips (75.28 seconds).

Actual discovery/optional-dependency counts differ between environments. Python 3.12's final isolated environment used heicreader 0.1.0, msgpack 1.2.3 and protobuf 5.29.6 after earlier dependency setup failures. New tests had zero pylint findings; the production change introduced no error/warning findings under the project's existing CI policy.

On native Windows 11 ARM64, all 35 targeted filter, repeated-member and Windows-name tests passed on Python 3.11.9 and 3.12.10, with zero failures/errors/skips. Four fresh full-suite processes compared the same 2,304 existing tests in baseline and candidate. The nine candidate-only tests were excluded from both common cohorts and had already passed separately.

| Native Windows Python | Baseline failures / errors / skips | Candidate failures / errors / skips | Candidate-only failing IDs |
| --- | ---: | ---: | ---: |
| 3.11.9 | 150 / 257 / 52 | 149 / 257 / 52 | 0 |
| 3.12.10 | 149 / 253 / 52 | 149 / 253 / 52 | 0 |

Every candidate failing ID also occurred in its corresponding full original baseline. The Windows suite is not green: it has platform/test-environment failures. Counts and error classifications are not perfectly identical on 3.11 because of existing Mixpanel temporary-SQLite cleanup behavior. The same zero-row assertion followed by WinError 32 was already reproduced in unchanged-baseline controls. Six successful Photos subtest labels also contain randomized temporary folders; a supplementary comparison canonicalized only those fixture-folder labels, keeping filenames and versions. Raw strict differences were retained. Windows Python 3.13–3.15 and native Windows corpus/performance runs were not tested. No unrelated Windows fix is included.

## Reproduction and provenance

Timing/evidence runs used baseline revision `6f3cc7152499b303936c64f92dfe7dd9d9877f77`. The PR's newer main baseline changes two corpus registry paths; it does not change this search module or the regression tests.

- Original `search_files.py` SHA256: `2b83dfb04fc258a1d7d629264ddf9c70d2f544666a206bd3c5ee6af4d174047e`.
- Candidate SHA256: `1435d3e5d125304c92328567aecc51753ec455f0386418be97fe258fb8f95b07`.

The focused profile is:

```json
{
  "leapp": "ileapp",
  "format_version": 1,
  "plugins": [
    "twitterTweets", "twitterCachedUsers", "twitterNotifications",
    "safariHistory", "safariHistoryTags", "addressBook",
    "calendarEvents", "calendarBirthdays", "calendarList",
    "chromeWebHistory", "chromeWebVisits", "chromeWebSearch"
  ]
}
```

Run the same profile/input/options on baseline and candidate in separate output directories. Warm both versions and alternate order; preserve all repetitions rather than selecting the fastest. Use the same installed dependencies. For example:

```sh
python3 -B ileapp.py -t zip -i /path/to/image.zip -o /path/to/new-output \
  -m /path/to/focused.ilprofile --hash --custom_output_folder report
python3 -B -m unittest discover -s admin/test/scripts -p 'test_seeker_zip_literal_filter.py'
python3 -B -m unittest discover -s admin/test/scripts -p 'test_*.py'
```

Performance measurements support this small filter-only implementation for review. Benefits are workload-dependent; other seeker classes and other LEAPP repositories are outside these results.
