# iLEAPP Versioning and Release Guide

This document outlines the versioning scheme used for iLEAPP and the steps required to update version numbers across the codebase for a new release.

## Versioning Scheme

iLEAPP follows a semantic-style versioning system (`Major.Minor.Patch`):

- **Major (X.0.0)**: Reserved for significant architectural changes or potentially breaking changes to the core framework.
- **Minor (0.X.0)**: The standard release for core updates or new/updated modules. Non-critical or non-breaking bug fixes are typically rolled into the next minor release.
- **Patch (0.0.X)**: Specific releases targeting critical bugs that need to be pushed out immediately between minor releases.

### Versioning Rules
- **Non-Decimal Sequence**: Version components are not decimals. After version `2.9.0`, the next minor version is `2.10.0`, then `2.11.0`, etc.
- **Development Tags**: Immediately after a build release, the version number is bumped to the next planned release (Minor or Major) with a `-dev.0` suffix (e.g., `2.6.0-dev.0`). This indicates pre-release source code and assists in troubleshooting by distinguishing between official builds and source-run instances.

---

## Files to Update

The version lives in one place, and changing it there is the whole change.

### `scripts/version_info.py`
The only source of the version string. The CLI and GUI report it, and it is written into
every report.
- Update the `leapp_version` variable.
- **Example**: `leapp_version = '2.6.0-dev.0'`

`packaging/build.py` reads it from there when it builds, so the Windows executable's
version information, the macOS bundle's `Info.plist`, the installer and the disk image
all follow it. Windows and macOS accept only numbers in those fields, so the build puts
`2.6.0` there for `2.6.0-dev.0`; the full string stays everywhere else.

## Releasing

Pushing a tag `v` + `leapp_version` (for example `v2.6.0`) runs
`.github/workflows/release.yml`, which builds every platform and creates a **draft**
release. It refuses a tag that does not match `leapp_version`, so set the release version
first, tag that commit, then bump to the next `-dev.0`. It also refuses to publish while
the repository lacks the `MACOS_*` secrets that sign and notarise the macOS disk images;
`.claude/rules/ileapp-build-and-release.md` lists them.

## Summary Checklist
- [ ] Update `scripts/version_info.py`

## Reference Examples
- [PR #1494: Update version number](https://github.com/abrignoni/iLEAPP/pull/1494/changes)
