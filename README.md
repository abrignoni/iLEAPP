![iLEAPP](scripts/_elements/iLEAPP_banner.png)

# iOS Logs, Events, And Plists Parser

iLEAPP parses iOS and iPadOS forensic extractions and produces HTML, TSV, timeline, KML, and LAVA output. It supports iOS/iPadOS 11 through current versions.

Browse the full searchable artifact list at [leapps.org/artifacts](https://leapps.org/artifacts) (filter by LEAPP tool).

## Quick Start (Recommended)

Download a pre-built release — no Python installation required.

- [LEAPPs Releases](https://leapps.org/releases) — browse all LEAPP family tools
- [iLEAPP GitHub Releases](https://github.com/abrignoni/iLEAPP/releases) — direct downloads

| Platform | Download |
| -------- | -------- |
| Windows (Intel/AMD) | `iLEAPP-*-windows-x64-setup.exe` (installer) or `iLEAPP-*-windows-x64-portable.zip` |
| Windows (ARM) | `iLEAPP-*-windows-arm64-setup.exe` or `iLEAPP-*-windows-arm64-portable.zip` |
| macOS (Apple Silicon) | `iLEAPP-*-macos-arm64.dmg` |
| macOS (Intel) | `iLEAPP-*-macos-x64.dmg` |
| Linux (Intel/AMD) | `iLEAPP-*-linux-x64.AppImage` |
| Linux (ARM) | `iLEAPP-*-linux-arm64.AppImage` |

Each download holds one program, `ileapp`. `SHA256SUMS.txt` in each release lets you check a download.

**GUI** — open iLEAPP the usual way: from the Start menu after installing on Windows, by
double-clicking `ileapp.exe` from the portable zip, iLEAPP in Applications on macOS, or
the AppImage on Linux. Started without arguments, it opens the window; select your input
type, source path, output folder, and modules to process.

**CLI** — give `ileapp` arguments in a terminal and it runs as a command line instead. The
output folder must already exist. On Windows, use the portable `ileapp.exe`, or the
installed `ileapp.exe`, which stays in its folder with the files beside it.

```
ileapp.exe -t zip -i C:\path\to\extraction.zip -o C:\path\to\output\
```

On Linux, run the AppImage with the same arguments. On macOS it is inside the app; to
type just `ileapp` in a terminal, link it onto your PATH once:

```
sudo ln -s /Applications/iLEAPP.app/Contents/MacOS/ileapp /usr/local/bin/ileapp
```

## Input Types

| Type | Description |
| ---- | ----------- |
| `fs` | Folder of extracted files with normal paths and names |
| `zip` | ZIP archive containing files with normal names |
| `tar` | TAR archive, plain or xz-compressed (`.tar.xz`) |
| `gz` | GZIP-compressed archive |
| `itunes` | iTunes/Finder backup folder with hashed paths and names |
| `file` | Single file input |

Encrypted iTunes/Finder backups (`-t itunes`) are supported. The GUI will prompt for a password before processing when encryption is detected. On the CLI, pass the password with `--itunes_password` (see [Optional parsing options](#optional-parsing-options) below).

## CLI Arguments

These options apply only to the **CLI** (`ileapp` / `ileapp.exe` given arguments, or `python ileapp.py`). The GUI (`ileapp` started without arguments, or `python ileappGUI.py`) exposes the same settings through its interface instead of command-line flags.

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
| `--html_row_limit` | | Rows above which an artifact's table is left off its HTML page, which then points at the LAVA database and the TSV export instead. Default 50000; `0` writes every table. The GUI uses the default |
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

## Test data and sample_data for your PR

A PR that adds or changes an artifact is easiest to review and merge when it arrives with
two things: a small test fixture cut from a real extraction, and `sample_data` values that
record what the module produced. Scripts generate both. Here is the whole flow.

One rule before anything else: whatever you commit here becomes public. Only use data you
are allowed to share, like a test device you populated yourself, a public research image,
or a file you sanitized by hand. Never casework.

**1. Cut a fixture from your extraction**

```
python admin/test/scripts/make_test_data.py <module> --case 1 --input <extraction.zip>
```

This pulls the files your module's `paths` patterns match out of the extraction and writes
the case file `admin/test/cases/testdata.<module>.json` plus one small zip per artifact
under `admin/test/cases/data/<module>/`.

Size rules: under 10 MB per zip, commit it with the PR. Between 10 and 25 MB, commit the
case file and attach the zip to a PR comment. Bigger than that, say so in the PR and a
maintainer will arrange a handoff.

**2. Record the expected output**

```
TZ=UTC python admin/test/scripts/test_module.py <module> -a all -c all
```

This runs the module against the fixture and writes a snapshot of the output under
`admin/test/results/<module>/`. Commit the snapshot too. It becomes the baseline that
guards the module after merge. Keep the `TZ=UTC` part: the committed snapshots are UTC
and CI runs UTC.

**3. Run the same comparison CI will run**

```
python admin/test/scripts/run_test_cases.py --module <module>
```

**4. Generate the sample_data values**

```
python admin/scripts/validate_sample_data.py --emit <extraction.zip> --key <image_name>
```

This runs iLEAPP end to end on your extraction and prints ready-to-paste `sample_data`
blocks for the modules changed on your branch. Paste them into your module's
`__artifacts_v2__` and add the app name and version you saw on the image. If a count is
zero, check the source file really is empty before recording it.

**5. Commit it all and open the PR**

Commit the module, the case file, the fixture zips, and the recorded snapshot together.
More detail lives in
[admin/docs/testing/create_module_test_cases.md](admin/docs/testing/create_module_test_cases.md).

If your extraction cannot be shared, open the PR anyway and say so. A fixture can often be
cut from a public research image instead, or the real file can be sanitized by hand. The
review does not stop while we work that out.

## Running from Source

Releases are the easiest way to run iLEAPP. Use source if you are developing modules or need unreleased changes from `main`.

### Requirements

- Python 3.10 to 3.14
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
python ileapp.py -t raw -i /path/to/acquisition.E01 -o /path/to/output/
```

`raw` reads a disk image (`.img`, `.dd`, `.bin`, or any numbered `.001` segment of
a split set), or an acquisition and the segments or files beside it (EnCase/EWF
`.E01`, SMART `.s01`, EWF2 `.Ex01`, AFF `.aff`, AFM `.afm`, any `.aff` in an AFD folder,
AFF4 `.aff4`, an Apple `.dmg`, with any `.dmgpart` files beside it, `.sparseimage` or
`.sparsebundle` folder, or a virtual machine disk, `.vhd`, `.vhdx`, `.vmdk` or `.qcow2`), in
place: no mounting and no administrator rights. Its NTFS, FAT32, exFAT, ext2/3/4,
F2FS, HFS+, APFS, QNX6, QNX4, ETFS, EFS, SquashFS, JFFS2, UBI/UBIFS, YAFFS and QNX IFS
volumes are searched directly (and a U-Boot environment or Belkin NVRM store is read as one
file), and
only the files an artifact asks for are read out of the image. Logical evidence, an
EnCase `.L01` or an FTK Imager `.ad1`, is read as the files it holds. The GUI picks
`raw` on its own for those extensions, and for a sparse bundle or AFD folder chosen with
its folder button. See `admin/docs/raw_image_input.md`.

An encrypted image opens with its password (`--image_password_file` or
`--image_password_env`), or, when it is sealed to a certificate, with that certificate's
RSA private key (`--image_private_key`). A BitLocker volume in an image opens with its
password or recovery password, given the same way, or its startup key
(`--bitlocker_key`, repeatable), and an APFS volume macOS encrypted in software with its
password or personal recovery key, given the same way. At a terminal whatever is missing
is asked for, and the GUI asks in dialogs; a BitLocker or APFS volume nothing opens is
reported and not searched.

`tar` also reads an xz-compressed tar (`.tar.xz`), and the GUI picks `tar` for that
extension. A compressed tar, `.tar.gz` included, is decompressed once into the report folder
before any file is read, so the run needs free space there for the uncompressed tar. The
copy is deleted when the run ends, and the run log says how long the step took.

**GUI:**

```
python ileappGUI.py
```

See [CLI Arguments](#cli-arguments) above, or run `python ileapp.py --help`.

### Building the binaries

`packaging/build.py` builds `ileapp` with PyInstaller for the machine it runs on, from the
same virtual environment. Run `python admin/scripts/fetch_unifiedlog_iterator.py` first to
bundle the Unified Log parser.

```
python packaging/build.py exe          # dist/iLEAPP/, and dist/iLEAPP.app on macOS
python packaging/build.py smoke        # run what it built, without opening a window
python packaging/build.py installer    # Windows: Inno Setup installer; macOS: .dmg; Linux: AppImage
```

`exe --onefile` makes `dist/ileapp` (`dist\ileapp.exe` on Windows) as a single file
instead. The Windows installer needs [Inno Setup](https://jrsoftware.org/isdl.php); on
Linux, `smoke` needs a display, which `xvfb-run` provides. `python packaging/build.py --help`
has the rest.

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by
[SignPath Foundation](https://signpath.org/).

The Windows builds are not signed yet. iLEAPP is applying to SignPath Foundation's free code
signing program for open source projects, and this policy applies to every Windows release
signed under it.

The Windows executables and installers attached to
[GitHub Releases](https://github.com/abrignoni/iLEAPP/releases) are built from this
repository by GitHub Actions, on GitHub-hosted runners
([`release.yml`](.github/workflows/release.yml)). Under this policy, SignPath signs only
what that workflow built. The macOS disk images are signed separately, with an Apple
Developer ID, and notarised by Apple.

### Team roles

- Committers and reviewers: [@abrignoni](https://github.com/abrignoni),
  [@JamesHabben](https://github.com/JamesHabben),
  [@Johann-PLW](https://github.com/Johann-PLW), [@stark4n6](https://github.com/stark4n6)
- Approvers: [@abrignoni](https://github.com/abrignoni),
  [@Johann-PLW](https://github.com/Johann-PLW)

Changes proposed by people who are not committers are reviewed by a committer before they
are merged. Every release signing request is approved by an approver.

### Privacy policy

iLEAPP processes extractions locally, on the machine it runs on. This program will not
transfer any information to other networked systems unless specifically requested by the
user or the person installing or operating it.

The same policy covers the other LEAPPs:
[leapps.org/releases#code-signing-policy](https://leapps.org/releases#code-signing-policy).

## Acknowledgements

This traiging tool is the result of a collaborative effort of many people in the DFIR community.

iLEAPP logo courtesy of Kevin Pagano. The earlier iLEAPP logo was by Derek Eiri.
