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

When changing the version number, it must be updated in the following four locations to ensure consistency across CLI, GUI, and compiled executables.

### 1. `scripts/version_info.py`
The primary source of truth for the version string within the application.
- Update the `leapp_version` variable.
- **Example**: `leapp_version = '2.6.0-dev.0'`

### 2. `scripts/pyinstaller/ileapp-file_version_info.txt`
Metadata for the Windows CLI executable.
- Update `filevers` and `prodvers` tuples. These must be four comma-separated integers.
  - **Example**: `filevers=(2, 6, 0, 0), prodvers=(2, 6, 0, 0),`
- Update `StringStruct('FileVersion', '...')` and `StringStruct('ProductVersion', '...')`.
  - **Example**: `StringStruct('FileVersion', '2.6.0-dev.0'),`

### 3. `scripts/pyinstaller/ileappGUI-file_version_info.txt`
Metadata for the Windows GUI executable.
- Follow the same steps as the CLI text file above.

### 4. `scripts/pyinstaller/ileappGUI_macOS.spec`
Configuration for the macOS application bundle.
- Update the `version` parameter in the `BUNDLE` section at the end of the file.
- **Example**: `version='2.6.0-dev.0'`

## Summary Checklist
- [ ] Update `scripts/version_info.py`
- [ ] Update `scripts/pyinstaller/ileapp-file_version_info.txt`
- [ ] Update `scripts/pyinstaller/ileappGUI-file_version_info.txt`
- [ ] Update `scripts/pyinstaller/ileappGUI_macOS.spec`

## Reference Examples
- [PR #1494: Update version number](https://github.com/abrignoni/iLEAPP/pull/1494/changes)
