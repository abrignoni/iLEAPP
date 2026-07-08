# Alternate artifacts

Artifacts in this folder are **not** part of a normal iLEAPP run. They are
developer/tooling oriented modules that are only loaded when the CLI is given
this folder explicitly:

```
python3 ileapp.py -t zip -i <extraction.zip> -o <output> \
    --custom_artifacts_path scripts/alternate_artifacts
```

The GUI and default CLI runs never load them, so regular users are unaffected.

## Modules

- **appInventory.py** — writes three tables into the LAVA SQLite output
  (`_lava_artifacts.db`) for parsing-coverage analysis (used by batch-leapp to
  determine which installed apps are not parsed by the tooling):
  - `extractioninfo`: extraction/device/run identifiers
  - `installedappinventory`: one row per app container (bundle ID, path, UUID)
  - `appfileinventory`: every file in the extraction mapped to its app
    container (lava_only; can be hundreds of thousands of rows)
