
---

## Which file to download

| Platform | File |
|---|---|
| Windows 10 or 11, 64-bit Intel or AMD | `-windows-x64-setup.exe` (installer), or `-windows-x64-portable.zip` to run without installing |
| Windows 11 on ARM | `-windows-arm64-setup.exe`, or `-windows-arm64-portable.zip` |
| macOS, Apple silicon | `-macos-arm64.dmg` |
| macOS, Intel | `-macos-x64.dmg` |
| Linux, 64-bit Intel or AMD | `-linux-x64.AppImage` |
| Linux on ARM | `-linux-arm64.AppImage` |

Every download holds one program, `ileapp`. Started without arguments, from the Start
menu, the Applications folder or a double-click, it opens the window. Given arguments in a
terminal, it is the command line. On macOS the command line is inside the app:

```bash
/Applications/iLEAPP.app/Contents/MacOS/ileapp --help
```

**For tools that run iLEAPP themselves.** The options, output and exit codes of `ileapp`
are those of earlier releases, but the downloads changed shape: there is no `ileappGUI`
any more, since `ileapp` without arguments opens the window. On Windows and macOS,
`ileapp` needs the folder it came in, so run it from there rather than copying the
executable elsewhere on its own; on Linux the AppImage is the whole program.

## First launch

The macOS disk images are signed with a Developer ID and notarised by Apple, so they open
without a warning.

The Windows binaries are not signed yet, so SmartScreen says "Windows protected your PC"
the first time. Choose More info, then Run anyway.

On Linux, make the AppImage executable once (`chmod +x iLEAPP-*.AppImage`). It needs FUSE
to start; where FUSE is not available, run it with `--appimage-extract-and-run`.

If you would rather not clear a warning, run from source instead; the README has the steps.

## Verify what you downloaded

`SHA256SUMS.txt` covers every file in this release. On macOS or Linux, from the folder you
downloaded into:

```bash
grep <the file you downloaded> SHA256SUMS.txt | shasum -a 256 -c -
```

Use `sha256sum` in place of `shasum -a 256` on Linux. On Windows, in PowerShell:

```powershell
(Get-FileHash -Algorithm SHA256 .\<the file you downloaded>).Hash
```

and compare it with the line in `SHA256SUMS.txt`, which is lower case.

## Linux

The build is made on Ubuntu 22.04, so it needs glibc 2.35 or newer and will not start on
an older distribution.
