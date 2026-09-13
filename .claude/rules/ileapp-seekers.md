---
paths:
  - "scripts/artifacts/**/*.py"
  - "scripts/search_files.py"
---

# iLEAPP seeker specifics

iLEAPP has an input type the other cores do not: an **iOS backup**. Its seeker behaves
differently from the directory, zip and tar seekers in one way that changes what a pattern
matches.

`FileSeekerItunes` matches against the **full reconstructed path with no synthetic `root/`
prefix**, and it does **not** apply `os.path.normcase`, so backup matching is always
case-sensitive on every platform, including Windows. The other seekers prepend `root/` and
normcase both sides.

A pattern written against a filesystem extraction can therefore behave differently against
a backup of the same device. Test both input types when the artifact is meant to support
both.

## Biome lives under two differently-cased roots

- `/private/var/db/biome/` (lowercase). The `_DKEvent.*` streams.
- `/private/var/mobile/Library/Biome/` (capital). Older streams, and occasionally
  `_DKEvent.*` SEGB files too.

Which root a stream uses varies **per stream, not per iOS version**, so verify against the
corpora rather than assuming. Use a single `[Bb]iome` bracket class, never a two-pattern
tuple. See `leapp-artifact-paths.md` for why the tuple double-counts on Windows.

## Validate globs against the recorded path listings

`admin/data/filepath-lists/*.csv.zip` holds real file listings from published research
images across several iOS generations. Run a candidate pattern against them with
`fnmatch.fnmatchcase` and confirm the hit count per generation before committing.

## Duplicate artifact names are rejected at load

iLEAPP refuses to load when two artifacts declare the same `name`. Nothing catches this
except a full run, so run the tool once before opening the PR.
