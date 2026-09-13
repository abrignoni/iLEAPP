# iLEAPP

iOS, iPadOS and watchOS logs, events and protobuf parser. The largest of the five LEAPP
extractors and the one where shared infrastructure usually lands first.

## Read these before changing an artifact

`admin/docs/` is the authority and is more current than anything summarised here:

| doc | covers |
| --- | --- |
| `admin/docs/artifact_info_block.md` | the `__artifacts_v2__` block, every field, and the `paths` glob semantics |
| `admin/docs/module_updates.md` | writing and updating a module |
| `admin/docs/module_updates_advanced.md` | multi-artifact modules, chaining, advanced cases |
| `admin/docs/features/file_search_architecture.md` | how the seekers find and extract files |
| `admin/docs/testing/create_module_test_cases.md` | test cases for a module |
| `admin/docs/testing/local_corpus_tests.md` | running against local corpora, and the hygiene rules for doing so |

If something here ever contradicts `admin/docs/`, the doc wins and this file is stale.

## Repo-specific things worth knowing

- **Input types.** Filesystem directory, zip, tar/tar.gz, and iOS backup. The backup seeker
  matches differently from the others. See `.claude/rules/ileapp-seekers.md`.
- **Duplicate artifact `name` values are rejected at load time.** Only a full run catches
  this, so run `ileapp.py` once before opening a PR.
- **blackboxprotobuf is vendored** at `scripts/blackboxprotobuf/`. Import it as
  `from scripts import blackboxprotobuf`. Do not add the PyPI package; a test enforces this.
- **Frozen builds need their imports declared.** PyInstaller cannot see the vendored
  protobuf or PIL submodules, so the specs collect them explicitly. If you add a dependency
  that is imported dynamically, expect a working dev run and a crashing frozen build, and
  check `.github/workflows/test_builds.yml` covers it.

## Local corpora

Artifacts record verified row counts in `sample_data`. The images behind those keys are not
in this repo and most are not public. Print counts and value shapes from them, never actual
values, and delete anything you extract when you are done. `admin/docs/testing/local_corpus_tests.md`
has the full policy.

## Rules

`.claude/rules/` holds the detail. Files prefixed `leapp-` are shared across all five
extractors and `lava-` across all six repos. **Edit those at their canonical source, not
here**, or the next sync overwrites you. `ileapp-` files are local to this repo.
