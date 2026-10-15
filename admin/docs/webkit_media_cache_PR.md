Suggested title: Recover WebKit MediaCache video and audio resources

## What this changes

Adds **WebKit - Media Cache** to reconstruct stored video/audio resources from
`CachedMedia-*` block tables, with media previews, URLs, qualified container/index
relationships and block-level provenance. One selection produces HTML/TSV/LAVA
output and repository-level `tl.db` events, without runtime FFmpeg or new dependencies.

## For a new or changed artifact

- [x] Ran the tool against a real extraction and confirmed the row counts, not just that it imports.
- [x] Ran `python admin/scripts/check_artifact_output.py <report folder>` and fixed or documented every finding.
- [x] Checked a second original app data directory: Chrome and Gmail/SafariViewService containers. Controlled evidence-root duplication also scaled exactly 2×.
- [x] `notes`, `description` and `sample_data` say only what the data shows, and the numbers were re-derived from the finished run.

## Anything reviewers should know

The public **MVS 2023 iOS 16.1.1** subset produced **11 rows, six recovered resources
(five videos, one audio) and three index events**. All six outputs fully decoded
without errors; controlled duplication produced **22/12/6**. The contributor also
confirmed a successful full-archive run. Three small public/synthetic fixtures,
baselines and 35 module tests are included.

The layout is experimentally inferred. Only fully covered stored resources are
exported; gaps and unsupported layouts remain visible. Index `lastmodtime` uses
an explicitly labelled Cocoa-epoch interpretation. Cache presence and index
times do not establish individual playback. A second positive image remains a
validation gap.

The full unittest suite passed (1,220 tests, 47 skips). Global fixture comparison retains
one GroupMe mismatch reproduced on unchanged upstream code, plus its existing
known Twitter-X failure; the exclusion registry is unchanged. Detailed scope,
counts and checks: `admin/docs/webkit_media_cache.md` and
`admin/docs/webkit_media_cache_validation.json`.
