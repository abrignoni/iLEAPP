![iLEAPP](scripts/_elements/iLEAPP_banner.png)

# iOS Logs, Events, And Plists Parser

iLEAPP parses iOS and iPadOS forensic extractions and produces HTML, TSV, timeline, KML, and LAVA output. It supports iOS/iPadOS 11 through current versions.

Browse the full searchable artifact list at [leapps.org/artifacts](https://leapps.org/artifacts) (filter by LEAPP tool).

## Quick Start (Recommended)

Download a pre-built release — no Python installation required.

- [LEAPPs Releases](https://leapps.org/releases) — browse all LEAPP family tools
- [iLEAPP GitHub Releases](https://github.com/abrignoni/iLEAPP/releases) — direct downloads

| Platform | GUI | CLI |
| -------- | --- | --- |
| Windows | `ileappGUI-*-Windows_x64.zip` | `ileapp-*-Windows_x64.zip` |
| macOS (Apple Silicon) | `ileappGUI-*-macOS_Apple_Silicon.dmg` | `ileapp-*-macOS_Apple_Silicon.zip` |
| macOS (Intel) | `ileappGUI-*-macOS_Mac_Intel.dmg` | `ileapp-*-macOS_Mac_Intel.zip` |
| Linux | `ileappGUI-*-Linux_x86_64.AppImage` | `ileapp-*-Linux_x86_64.AppImage` |

**GUI** — extract the download, run `ileappGUI`, then select your input type, source path, output folder, and modules to process.

**CLI** — extract the download and run from a terminal. The output folder must already exist.

```
ileapp.exe -t zip -i C:\path\to\extraction.zip -o C:\path\to\output\
```

On macOS and Linux, use the `ileapp` binary from the extracted archive instead of `ileapp.exe`.

## Input Types

| Type | Description |
| ---- | ----------- |
| `fs` | Folder of extracted files with normal paths and names |
| `zip` | ZIP archive containing files with normal names |
| `tar` | TAR archive |
| `gz` | GZIP-compressed archive |
| `itunes` | iTunes/Finder backup folder with hashed paths and names |
| `file` | Single file input |

Encrypted iTunes/Finder backups (`-t itunes`) are supported. The GUI will prompt for a password before processing when encryption is detected. On the CLI, pass the password with `--itunes_password` (see [Optional parsing options](#optional-parsing-options) below).

## CLI Arguments

These options apply only to the **CLI** build (`ileapp` / `ileapp.exe` / `python ileapp.py`). The GUI (`ileappGUI`) exposes the same settings through its interface instead of command-line flags.

Run `ileapp --help` (or `python ileapp.py --help` from source) for the built-in reference.

### Parsing a case

These three arguments are required for a normal parse run:

| Argument | Long form | Description |
| -------- | --------- | ----------- |
| `-t` | | Input type: `fs`, `tar`, `zip`, `gz`, `itunes`, or `file` |
| `-i` | `--input_path` | Path to the input file or folder |
| `-o` | `--output_path` | Path to the output folder (**must already exist**) |

**Example:**

```
ileapp -t zip -i /path/to/extraction.zip -o /path/to/output/
```

### Optional parsing options

| Argument | Long form | Description |
| -------- | --------- | ----------- |
| `-w` | `--wrap_text` | Pass this flag to **disable** text wrapping in output files |
| `-m` | `--load_profile` | Path to an iLEAPP profile file (`.ilprofile`) to limit which modules run |
| `-d` | `--load_case_data` | Path to a LEAPP case data file (`.lcasedata`) |
| `--custom_output_folder` | | Custom name for the report output subfolder |
| `--custom_artifacts_path` | | Extra folder to load artifact modules from (e.g. `scripts/alternate_artifacts`) |
| `--itunes_password` | | | Password for an encrypted iTunes/Finder backup (`-t 12345`) |

### Standalone utility modes

These modes do not parse a case. Use them **alone** — without `-t`, `-i`, or `-o`:

| Argument | Long form | Description |
| -------- | --------- | ----------- |
| `-p` | `--artifact_paths` | Write all artifact search paths to `path_list.txt` in the current directory |
| `-c` | `--create_profile_casedata` | Interactive wizard to create a `.ilprofile` or `.lcasedata` file in the given folder |

**Examples:**

```
ileapp -p
ileapp -c /path/to/output/folder/
```

## Contributing

Artifact modules live in `scripts/artifacts/` and are loaded dynamically at runtime.

**New modules:** start with the step-by-step guide at [How to Write an iLEAPP Module](https://leapps.org/blog-post?post=2026-06-14-how-to-write-an-ileapp-module).

**Additional references:**

- [Artifact Info Block Structure](admin/docs/artifact_info_block.md)
- [Updating Modules for Automatic Output Generation](admin/docs/module_updates.md)
- [Updating Complex Modules to Include LAVA Output](admin/docs/module_updates_advanced.md)
- [Testing Modules](admin/docs/testing/readme.md)

## Running from Source

Releases are the easiest way to run iLEAPP. Use source if you are developing modules or need unreleased changes from `main`.

### Requirements

- Python 3.10, 3.11, or 3.12
- Git

### Setup

```
git clone https://github.com/abrignoni/iLEAPP.git
cd iLEAPP
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

On **Linux**, install `tkinter` for the GUI:

```
sudo apt-get install python3-tk
```

Windows setup help from Hexordia:

- [ILEAPP Walkthrough (PDF)](https://www.hexordia.com/s/ILEAPP-Walkthrough.pdf)
- [ILEAPP Walkthrough (video)](https://www.youtube.com/watch?v=7qvVFfBM2NU)

### Usage

The output folder must exist before running. Source builds report a `-dev` version (e.g. `2.6.0-dev.0`) to distinguish them from official release builds.

**CLI:**

```
python ileapp.py -t zip -i /path/to/extraction.zip -o /path/to/output/
```

**GUI:**

```
python ileappGUI.py
```

See [CLI Arguments](#cli-arguments) above, or run `python ileapp.py --help`.

## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.

iLEAPP logo courtesy of Derek Eiri.
