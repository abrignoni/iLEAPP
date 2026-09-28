"""Build iLEAPP for the machine this runs on, in two phases so a signed build is possible.

    python packaging/build.py exe                 phase 1: PyInstaller -> dist/iLEAPP/ (one folder);
                                                  on macOS also dist/iLEAPP.app
    python packaging/build.py exe --onefile       phase 1: dist/ileapp[.exe], a single executable
                                                  (no installer from this)
    python packaging/build.py smoke [--onefile]   run what phase 1 built, headlessly: --version, a run
                                                  over an empty extraction and over a raw image, the
                                                  bundled parser, and the window's --selfcheck
    python packaging/build.py installer           phase 2: Windows -> dist/iLEAPP-Setup-<version>.exe (Inno Setup);
                                                  macOS -> dist/iLEAPP-<version>.dmg around dist/iLEAPP.app (dmgbuild);
                                                  Linux -> dist/iLEAPP-<version>.AppImage (appimagetool)
    python packaging/build.py installer --sign-tool NAME
                                                  phase 2, with Inno Setup signing the installer and the
                                                  uninstaller using the Sign Tool configured under NAME
    python packaging/build.py all                 both phases in one go, for unsigned local builds
    python packaging/build.py verify PATH ...     assert a code signature is present and valid
                                                  (Authenticode on Windows, codesign on macOS);
                                                  --subject TEXT also requires the signer to match

One executable, ileapp, is both programs. packaging/entrypoint.py opens the window when
it is started without arguments, as a double-click starts it, and is the command line
when it is given some, so tools that run `ileapp -t fs -i ... -o ...` see no change. The
choice never depends on the file's name, so the executable may be renamed.

Signing belongs between the two phases. Sign dist/iLEAPP/ileapp.exe, or codesign
dist/iLEAPP.app, after phase 1 and before phase 2, or the installer carries an unsigned
executable inside a signed wrapper. `all` refuses --sign-tool for exactly that reason.

The version is read from scripts/version_info.py as text, so nothing is imported, and
handed to the spec and to Inno Setup, so neither the executable nor the installer can
report a different version from the app. Windows and macOS take only numbers in their
version fields, so a suffix such as -dev is left out there and kept everywhere else.
ONEFILE reaches the spec through the ILEAPP_ONEFILE environment variable; the spec is
never edited by a build. PyInstaller is pinned in packaging/requirements-build.txt,
which phase 1 installs with requirements.txt.

What goes into the bundle is decided here rather than in packaging/ileapp.spec, which
loads this file and only wires the answers into PyInstaller, so it can be tested without
running a build: the Unified Log parser with its licence and notices, the data trees, and
every artifact module as a hidden import.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGING = ROOT / "packaging"
SPEC = PACKAGING / "ileapp.spec"
ENTRYPOINT = PACKAGING / "entrypoint.py"
BUILD_REQUIREMENTS = PACKAGING / "requirements-build.txt"
ISS = PACKAGING / "installer.iss"
ICO = PACKAGING / "ileapp.ico"
ICNS = ROOT / "assets" / "icon.icns"
ICON_PNG = ROOT / "assets" / "icon.png"
DMG_SETTINGS = PACKAGING / "dmg_settings.py"
DMG_BACKGROUND = PACKAGING / "dmg_background.png"
BIN = ROOT / "bin"
DIST = ROOT / "dist"
BUILD = ROOT / "build"
APP = "iLEAPP"
EXE = "ileapp"
# PyInstaller's default, named so the smoke test and the spec agree on where the
# one-folder build keeps everything but the executable.
CONTENTS = "_internal"
BUNDLE_ID = "org.leapps.iLEAPP"
PUBLISHER = "Alexis Brignoni"
COPYRIGHT = "Result of a collaborative effort in the DFIR community."
UNIFIEDLOG = "unifiedlog_iterator"
UNIFIEDLOG_LICENSE = "LICENSE-unifiedlog_iterator"
UNIFIEDLOG_NOTICES = "THIRD-PARTY-NOTICES-unifiedlog_iterator.txt"
RAW_FIXTURE = ROOT / "admin" / "test" / "data" / "raw_images" / "ntfs-fixture.img.gz"
ISCC_DEFAULT = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# Folders shipped as files beside the executable. The plugin loader reads the artifacts
# from scripts/artifacts as source, the report copies scripts/_elements, and the window
# loads its images from assets/. leapp_functions/ is imported by the artifacts.
DATA_TREES = ("scripts", "leapp_functions", "assets")
# Never shipped: bytecode caches from the build machine, and Finder metadata.
DATA_EXCLUDED_DIRS = {"__pycache__"}
DATA_EXCLUDED_SUFFIXES = (".pyc", ".pyo")
DATA_EXCLUDED_NAMES = {".DS_Store"}

# Imports that the analysis of the artifacts below does not reach, each learned from a
# frozen build that failed without it. google.protobuf and PIL are collected whole in the
# spec, because that needs PyInstaller.
FIXED_HIDDEN_IMPORTS = (
    "astc_decomp_faster",
    "bencoding",
    "Crypto.Cipher.AES",
    "ijson",
    "liblzfse",
    "mdplist",
    "mmh3",
    "nska_deserialize",
    "pandas",
    "pgpy",
    "pillow_heif",
    "typedstream",
    "xml.etree.ElementTree",
)

# appimagetool and the AppImage runtime it prepends, pinned to releases and checked
# against these digests before anything runs. Both were downloaded and hashed
# independently, and match the digests GitHub publishes for the release assets. Without
# --runtime-file, appimagetool fetches the runtime's latest continuous build itself.
APPIMAGETOOL_URL = "https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-{arch}.AppImage"
APPIMAGE_RUNTIME_URL = "https://github.com/AppImage/type2-runtime/releases/download/20251108/runtime-{arch}"
APPIMAGE_DIGESTS = {
    "x86_64": {
        "appimagetool": "ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0",
        "runtime": "2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d",
    },
    "aarch64": {
        "appimagetool": "f0837e7448a0c1e4e650a93bb3e85802546e60654ef287576f46c71c126a9158",
        "runtime": "00cbdfcf917cc6c0ff6d3347d59e0ca1f7f45a6df1a428a0d6d8a78664d87444",
    },
}


def read_version() -> str:
    """The version string from scripts/version_info.py, read as text so nothing is imported."""
    text = (ROOT / "scripts" / "version_info.py").read_text(encoding="utf-8")
    m = re.search(r"""^leapp_version\s*=\s*['"]([^'"]+)['"]""", text, re.M)
    if not m:
        sys.exit("build: could not find leapp_version in scripts/version_info.py")
    return m.group(1)


def numeric_version(version: str) -> str:
    """The leading numbers of a version, '2026.4.2' from '2026.4.2-dev', for the fields
    Windows and macOS accept only numbers in. At most four, as Windows allows."""
    m = re.match(r"\d+(?:\.\d+){0,3}", version)
    if not m:
        sys.exit(f"build: version {version!r} does not start with a number")
    return m.group(0)


def windows_version_fields(version: str) -> dict:
    """What the spec writes into the Windows executable's version resource."""
    numbers = tuple(int(part) for part in numeric_version(version).split("."))
    numbers = (numbers + (0, 0, 0, 0))[:4]
    return {
        "numbers": numbers,
        "strings": {
            "CompanyName": PUBLISHER,
            "FileDescription": APP,
            "FileVersion": version,
            "InternalName": APP,
            "LegalCopyright": COPYRIGHT,
            "OriginalFilename": exe_name(EXE, windows=True),
            "ProductName": APP,
            "ProductVersion": version,
        },
    }


def exe_name(stem: str, windows: bool | None = None) -> str:
    windows = sys.platform == "win32" if windows is None else windows
    return f"{stem}.exe" if windows else stem


def macos_app() -> Path:
    return DIST / f"{APP}.app"


def output(onefile: bool) -> Path:
    """The executable phase 1 leaves for the platform's release to ship.

    On macOS the one-folder build is also at dist/iLEAPP/, but what ships is the bundle
    around it, whose layout differs, so the bundle's executable is the one to check.
    """
    if onefile:
        return DIST / exe_name(EXE)
    if sys.platform == "darwin":
        return macos_app() / "Contents" / "MacOS" / EXE
    return DIST / APP / exe_name(EXE)


def bundled_bin_dir() -> Path:
    """Where a one-folder build keeps the Unified Log parser: sys._MEIPASS/bin at run time."""
    if sys.platform == "darwin":
        return macos_app() / "Contents" / "Frameworks" / "bin"
    return DIST / APP / CONTENTS / "bin"


def run(cmd: list[str], **kwargs) -> None:
    print("==>", " ".join(str(part) for part in cmd), flush=True)
    result = subprocess.run(cmd, check=False, **kwargs)
    if result.returncode != 0:
        sys.exit(f"build: '{cmd[0]}' exited {result.returncode}")


def assert_artifact(path: Path, what: str) -> None:
    """A build that exits 0 can still leave no usable output. Check the file, not the code."""
    if not path.is_file():
        sys.exit(f"build: {what} not produced at {path}")
    print(f"==> {what}: {path} ({path.stat().st_size:,} bytes)", flush=True)


# -- what goes into the bundle, read by packaging/ileapp.spec ----------------------------

def _unifiedlog_binary() -> Path | None:
    binary = BIN / exe_name(UNIFIEDLOG)
    return binary if binary.is_file() else None


def bundle_binaries() -> list[tuple[str, str]]:
    """The Unified Log parser as a PyInstaller `binaries` entry, or [] when not fetched.

    It is a binary rather than data because PyInstaller keeps the execute permission of
    binaries only; as data it arrives without it on macOS and Linux, and
    scripts/unifiedlogs.py then skips it as not executable. Its destination, bin/, is
    where scripts/unifiedlogs.py looks under sys._MEIPASS.
    """
    binary = _unifiedlog_binary()
    if binary is None:
        print(f"==> {BIN / exe_name(UNIFIEDLOG)} not found; building without native Unified "
              "Log support. admin/scripts/fetch_unifiedlog_iterator.py fetches it.", flush=True)
        return []
    return [(str(binary), "bin")]


def _tree(source: Path, dest: str) -> list[tuple[str, str]]:
    """Every file under source as (file, folder in the bundle), without caches or Finder files."""
    entries = []
    for folder, dirs, files in os.walk(source):
        dirs[:] = sorted(d for d in dirs if d not in DATA_EXCLUDED_DIRS)
        rel = Path(folder).relative_to(source)
        for name in sorted(files):
            if name in DATA_EXCLUDED_NAMES or name.endswith(DATA_EXCLUDED_SUFFIXES):
                continue
            entries.append((str(Path(folder) / name), (Path(dest) / rel).as_posix()))
    return entries


def bundle_datas() -> list[tuple[str, str]]:
    """The data trees, and the parser's licence and notices when the parser ships.

    Apache-2.0 section 4(a) requires that recipients of a redistribution get a copy of the
    licence, and the parser statically links Rust crates under their own licences, whose
    texts the notices file carries. So the parser never ships without both.
    """
    entries = []
    for tree in DATA_TREES:
        entries += _tree(ROOT / tree, tree)
    if _unifiedlog_binary() is not None:
        for name, remedy in (
                (UNIFIEDLOG_LICENSE, "Re-run admin/scripts/fetch_unifiedlog_iterator.py."),
                (UNIFIEDLOG_NOTICES, "It is committed in bin/; restore it from git.")):
            path = BIN / name
            if not path.is_file():
                sys.exit(f"build: {path} is missing. The {UNIFIEDLOG} binary may not be "
                         f"redistributed without it. {remedy}")
            entries.append((str(path), "bin"))
    return entries


def artifact_modules() -> list[str]:
    """Every artifact module, named as PyInstaller can analyse it.

    The plugin loader reads the artifacts from source files at run time, so PyInstaller
    never sees what they import, and before this every such import had to be listed by
    hand; three startup crashes came from that list (google.protobuf, PIL,
    leapp_functions). Naming each artifact as a hidden import makes PyInstaller follow its
    imports instead. A file whose name is not a valid module name (kleinanzeigen.de.py)
    cannot be named this way; it still ships as source and loads, but what it imports has
    to be bundled because something else imports it too.
    """
    stems = sorted(p.stem for p in (ROOT / "scripts" / "artifacts").glob("*.py"))
    return [f"scripts.artifacts.{stem}" for stem in stems
            if stem.isidentifier() and stem != "__init__"]


def hidden_imports() -> list[str]:
    return list(FIXED_HIDDEN_IMPORTS) + artifact_modules()


# -- phase 1 -----------------------------------------------------------------------------

def clean() -> None:
    """Remove build/ and what phase 1 put in dist/, and nothing else that dist/ holds."""
    for target in (BUILD, DIST / APP, macos_app(), output(onefile=True)):
        if target.is_symlink() or target.is_file():
            print(f"==> removing {target}", flush=True)
            target.unlink()
        elif target.is_dir():
            print(f"==> removing {target}", flush=True)
            shutil.rmtree(target)


def refuse_collision(onefile: bool) -> None:
    """Stop a build from silently destroying the other layout's output.

    The one-folder build is dist/iLEAPP/ and the one-file build dist/ileapp, and on a
    case-insensitive file system, the default on macOS, those are the same path.
    PyInstaller's --noconfirm removes whatever is there without a word; GLEAPP measured a
    --onefile build replacing a 1,257-file folder build that way, exit 0. In the signing
    workflow that folder can be the signed build waiting for phase 2. --clean is the
    explicit way to discard it.
    """
    single = DIST / exe_name(EXE)
    folder = DIST / APP
    if onefile and single.is_dir():
        sys.exit(f"build: {single} is an existing one-folder build and a --onefile build at "
                 "that name would delete it; pass --clean to discard it, or move it first")
    if not onefile and folder.is_file():
        sys.exit(f"build: {folder} is an existing one-file build sitting where the folder "
                 "build must go; pass --clean to discard it, or move it first")


def build_exe(onefile: bool, clean_first: bool) -> Path:
    if clean_first:
        clean()
    refuse_collision(onefile)
    run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check",
         "-r", str(ROOT / "requirements.txt"), "-r", str(BUILD_REQUIREMENTS)])
    env = dict(os.environ, ILEAPP_ONEFILE="1" if onefile else "0")
    run([sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm",
         "--distpath", str(DIST), "--workpath", str(BUILD)], env=env)
    if sys.platform == "darwin" and not onefile:
        assert_artifact(DIST / APP / EXE, "one-folder executable")
    out = output(onefile)
    assert_artifact(out, "executable")
    return out


# -- phase 2 -----------------------------------------------------------------------------

def find_iscc() -> str:
    found = shutil.which("iscc") or shutil.which("ISCC")
    if found:
        return found
    if Path(ISCC_DEFAULT).is_file():
        return ISCC_DEFAULT
    sys.exit("build: Inno Setup (ISCC.exe) not found on PATH or at the default install "
             "location; get it from https://jrsoftware.org/isdl.php")


def build_installer(sign_tool: str | None) -> Path:
    if sign_tool and sys.platform != "win32":
        sys.exit("build: --sign-tool is an Inno Setup concept, for Windows only; on macOS "
                 "sign the bundle with codesign after 'exe', then run 'installer' for the "
                 "disk image")
    if sys.platform == "win32":
        return _build_inno(sign_tool)
    if sys.platform == "darwin":
        return _build_dmg()
    if sys.platform.startswith("linux"):
        return _build_appimage()
    sys.exit(f"build: no installer is wired up for {sys.platform}")


def _build_inno(sign_tool: str | None) -> Path:
    folder = DIST / APP
    exe = folder / exe_name(EXE, windows=True)
    if not exe.is_file():
        sys.exit(f"build: {exe} not found; run 'exe' first, the one-folder build rather "
                 f"than --onefile, because the installer packages {folder}")
    version = read_version()
    cmd = [find_iscc(), f"/DAppVer={version}", f"/DAppVerNumeric={numeric_version(version)}"]
    # An ARM64 build installs only on ARM64 Windows; x64compatible would also let an x64
    # machine install it, where it cannot run.
    if platform.machine().lower() in ("arm64", "aarch64"):
        cmd.append("/DAppArm64")
    if sign_tool:
        cmd.append(f"/DSignToolName={sign_tool}")
    cmd.append(str(ISS))
    run(cmd)
    out = DIST / f"{APP}-Setup-{version}.exe"
    assert_artifact(out, "installer")
    return out


def _build_dmg() -> Path:
    """A compressed disk image around the .app phase 1 produced, laid out by dmgbuild: the
    app and an Applications link either side of the arrow on packaging/dmg_background.png,
    so installing is one drag."""
    app = macos_app()
    if not app.is_dir():
        sys.exit(f"build: {app} not found; run 'exe' first, the one-folder build, which "
                 "produces the bundle on macOS")
    try:
        # macOS only, in packaging/requirements-build.txt, which phase 1 installs.
        import dmgbuild  # pylint: disable=import-outside-toplevel,import-error
    except ImportError:
        sys.exit("build: dmgbuild is missing; pip install -r packaging/requirements-build.txt "
                 "installs it on macOS")
    version = read_version()
    out = DIST / f"{APP}-{version}.dmg"
    if out.exists():
        out.unlink()
    print(f"==> dmgbuild -s {DMG_SETTINGS.relative_to(ROOT)} {APP} {out}", flush=True)
    dmgbuild.build_dmg(str(out), APP, settings_file=str(DMG_SETTINGS),
                       defines={"app": str(app), "icon": str(ICNS),
                                "background": str(DMG_BACKGROUND)})
    run(["hdiutil", "verify", str(out)])
    assert_artifact(out, "disk image")
    return out


def appimage_arch(machine: str | None = None) -> str:
    """The architecture name AppImage tooling uses for this machine."""
    machine = (machine or platform.machine()).lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("aarch64", "arm64"):
        return "aarch64"
    sys.exit(f"build: no pinned AppImage tooling for {machine}")


def appimage_desktop_entry() -> str:
    """The .desktop file an AppImage must carry. Started from it there are no arguments,
    so it opens the window; Terminal=false because nothing is printed to one."""
    return "\n".join((
        "[Desktop Entry]",
        "Type=Application",
        f"Name={APP}",
        "Comment=iOS Logs, Events, And Plists Parser",
        f"Exec={EXE}",
        f"Icon={EXE}",
        "Terminal=false",
        "Categories=Utility;",
        "",
    ))


def make_appdir(folder: Path, appdir: Path) -> Path:
    """Lay the one-folder build out as an AppDir.

    The folder goes to usr/bin/ whole, and AppRun is a link to the executable in it.
    PyInstaller's bootloader finds its _internal/ folder from /proc/self/exe, which is the
    link's target, so the link needs no wrapper script.
    """
    if appdir.exists():
        shutil.rmtree(appdir)
    shutil.copytree(folder, appdir / "usr" / "bin", symlinks=True)
    (appdir / "AppRun").symlink_to(Path("usr") / "bin" / EXE)
    (appdir / f"{EXE}.desktop").write_text(appimage_desktop_entry(), encoding="utf-8")
    shutil.copyfile(ICON_PNG, appdir / f"{EXE}.png")
    (appdir / ".DirIcon").symlink_to(f"{EXE}.png")
    return appdir


def _ssl_context() -> ssl.SSLContext:
    """A verifying context that also works on a python.org install without its CA store,
    as admin/scripts/fetch_unifiedlog_iterator.py does. Verification is never disabled."""
    try:
        import certifi  # pylint: disable=import-outside-toplevel
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def fetch_verified(url: str, dest: Path, sha256: str) -> Path:
    """Download url to dest unless a copy with the pinned digest is already there.

    The digest is checked either way, so a cached file that changed is never run.
    """
    if not (dest.is_file() and hashlib.sha256(dest.read_bytes()).hexdigest() == sha256):
        print(f"==> fetching {url}", flush=True)
        with urllib.request.urlopen(url, context=_ssl_context()) as response:  # nosec B310 - pinned https URL
            data = response.read()
        actual = hashlib.sha256(data).hexdigest()
        if actual != sha256:
            sys.exit(f"build: {url} has sha256 {actual}, expected {sha256}; refusing to use it")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    dest.chmod(0o755)
    return dest


def _build_appimage() -> Path:
    """An AppImage around the one-folder build, made by the pinned appimagetool.

    Both appimagetool and the AppImage it makes run here with APPIMAGE_EXTRACT_AND_RUN,
    so no FUSE is needed on the build machine. The finished AppImage is then run once:
    it has to report the app's version, the same check phase 1's smoke test starts with.
    """
    folder = DIST / APP
    if not (folder / EXE).is_file():
        sys.exit(f"build: {folder / EXE} not found; run 'exe' first, the one-folder build "
                 f"rather than --onefile, because the AppImage packages {folder}")
    arch = appimage_arch()
    digests = APPIMAGE_DIGESTS[arch]
    tools = BUILD / "appimage-tools"
    tool = fetch_verified(APPIMAGETOOL_URL.format(arch=arch),
                          tools / f"appimagetool-{arch}.AppImage", digests["appimagetool"])
    runtime = fetch_verified(APPIMAGE_RUNTIME_URL.format(arch=arch),
                             tools / f"runtime-{arch}", digests["runtime"])
    appdir = make_appdir(folder, BUILD / f"{APP}.AppDir")
    version = read_version()
    out = DIST / f"{APP}-{version}.AppImage"
    if out.exists():
        out.unlink()
    env = dict(os.environ, ARCH=arch, APPIMAGE_EXTRACT_AND_RUN="1")
    run([str(tool), "--no-appstream", "--runtime-file", str(runtime), str(appdir), str(out)],
        env=env)
    assert_artifact(out, "AppImage")
    out.chmod(0o755)
    want = f"{APP} {version}"
    result = _run_built([str(out), "--version"], env=env)
    if result.returncode != 0 or result.stdout.strip() != want:
        sys.exit(f"build: the AppImage does not start: expected '{want}', got exit "
                 f"{result.returncode}\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}")
    print(f"==> the AppImage reports '{want}'", flush=True)
    return out


# -- verify ------------------------------------------------------------------------------

def _signature(path: Path) -> tuple[bool, str, bool, str]:
    """(valid, signer subject, timestamped, detail) from the platform's own verifier."""
    if sys.platform == "win32":
        literal = str(path).replace("'", "''")
        script = (f"$s = Get-AuthenticodeSignature -LiteralPath '{literal}'; "
                  "Write-Output $s.Status; "
                  "Write-Output ([string]$s.SignerCertificate.Subject); "
                  "Write-Output ([bool]$s.TimeStamperCertificate)")
        result = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                                capture_output=True, text=True, check=False)
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        if result.returncode != 0 or len(lines) < 3:
            return False, "", False, f"could not read the signature: {result.stderr.strip()[:200]}"
        status, signer, stamped = lines[0], lines[1], lines[2].lower() == "true"
        return status == "Valid", signer, stamped, f"status={status} signer={signer!r}"
    if sys.platform == "darwin":
        result = subprocess.run(["codesign", "--verify", "--strict", "--verbose=2", str(path)],
                                capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return False, "", False, f"codesign: {result.stderr.strip()[:200]}"
        detail = subprocess.run(["codesign", "-dv", "--verbose=2", str(path)],
                                capture_output=True, text=True, check=False).stderr
        authorities = [ln.split("=", 1)[1] for ln in detail.splitlines() if ln.startswith("Authority=")]
        # An ad-hoc signature names no authority. PyInstaller signs every macOS build that
        # way, so it verifies, and it is reported as what it is.
        signer = authorities[0] if authorities else "(ad hoc)"
        stamped = any(ln.startswith("Timestamp=") for ln in detail.splitlines())
        return True, signer, stamped, ""
    return False, "", False, f"no signature verifier for platform {sys.platform}"


def verify(paths: list[str], subject: str | None) -> int:
    failures = 0
    for raw in paths:
        path = Path(raw)
        # A macOS bundle is a folder, and codesign verifies it as one.
        is_bundle = sys.platform == "darwin" and path.suffix == ".app" and path.is_dir()
        if not (path.is_file() or is_bundle):
            print(f"FAIL  {path}: no such file")
            failures += 1
            continue
        valid, signer, stamped, detail = _signature(path)
        if not valid:
            print(f"FAIL  {path}  {detail}")
            failures += 1
            continue
        if subject and subject not in signer:
            print(f"FAIL  {path}  signer={signer!r} does not contain {subject!r}")
            failures += 1
            continue
        # An ad-hoc signature has no certificate to expire, and never carries a timestamp.
        note = "" if stamped or signer == "(ad hoc)" else \
            "  (no timestamp: this signature stops verifying when the certificate expires)"
        print(f"OK    {path}  signer={signer}{note}")
    return 1 if failures else 0


# -- smoke -------------------------------------------------------------------------------

def _run_built(cmd: list[str], timeout: int = 900, env: dict | None = None) -> subprocess.CompletedProcess:
    print("==>", " ".join(cmd), flush=True)
    # The executable prints whatever the evidence holds; a Windows console's code page must
    # not decide whether a run survives that.
    env = dict(os.environ if env is None else env, PYTHONIOENCODING="utf-8")
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=timeout, check=False)


def _onefile_members(exe: Path) -> set[str]:
    """The files packed into a one-file executable, with / as the separator."""
    from PyInstaller.archive.readers import CArchiveReader  # pylint: disable=import-outside-toplevel,import-error
    return {name.replace("\\", "/") for name in CArchiveReader(str(exe)).toc}


def _source_artifact_count() -> int:
    """How many artifacts the plugin loader finds from source, in this interpreter."""
    code = "from scripts.plugin_loader import PluginLoader; print(len(PluginLoader()))"
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True,
                            text=True, check=False)
    if result.returncode != 0:
        sys.exit(f"build: could not load the artifacts from source:\n{result.stderr[-2000:]}")
    return int(result.stdout.strip().splitlines()[-1])


def smoke(onefile: bool) -> int:
    """Run the built executable the ways a user does, without opening a window.

    Each check is here because a frozen iLEAPP has failed it: builds that crashed on
    startup over an import nobody declared, one that could not read a raw image, one that
    shipped without the Unified Log parser. An exit code of 0 from the build proves none
    of that; only running what it built does.
    """
    exe = output(onefile)
    if not exe.is_file():
        sys.exit(f"build: {exe} not found; run 'exe{' --onefile' if onefile else ''}' first")
    failures = []

    def check(ok: bool, what: str, result: subprocess.CompletedProcess | None = None) -> None:
        print(f"{'OK  ' if ok else 'FAIL'}  {what}", flush=True)
        if not ok:
            failures.append(what)
            if result is not None:
                print(f"exit {result.returncode}\n--- stdout\n{result.stdout[-3000:]}\n"
                      f"--- stderr\n{result.stderr[-3000:]}", flush=True)

    want = f"{APP} {read_version()}"
    result = _run_built([str(exe), "--version"])
    check(result.returncode == 0 and result.stdout.strip() == want,
          f"--version prints '{want}'", result)

    with tempfile.TemporaryDirectory(prefix="ileapp-smoke-") as tmp:
        tmp_path = Path(tmp)
        # An empty extraction still loads every artifact, runs the ones whose paths match
        # nothing, and writes a report: the whole program, end to end, in seconds.
        evidence, report = tmp_path / "in", tmp_path / "out"
        evidence.mkdir()
        report.mkdir()
        (evidence / "placeholder.txt").write_text("placeholder", encoding="utf-8")
        result = _run_built([str(exe), "-t", "fs", "-i", str(evidence), "-o", str(report)])
        check(result.returncode == 0 and any(report.rglob("index.html")),
              "a run over an empty extraction writes a report", result)

        # A raw image is read by the vendored reader imported as a module, the path a
        # frozen build is most likely to break, and the run log has to show the walk.
        image, raw_report = tmp_path / "ntfs-fixture.img", tmp_path / "raw_out"
        raw_report.mkdir()
        with gzip.open(RAW_FIXTURE, "rb") as src, open(image, "wb") as dst:
            shutil.copyfileobj(src, dst)
        result = _run_built([str(exe), "-t", "raw", "-i", str(image), "-o", str(raw_report)])
        logs = list(raw_report.rglob("Screen_Output.html"))
        walked = any("walked lba0: 4" in log.read_text(encoding="utf-8", errors="replace")
                     for log in logs)
        check(result.returncode == 0 and walked, "a raw image is walked", result)

    if _unifiedlog_binary() is not None and onefile:
        # A single executable unpacks at run time, so what it carries is read from the
        # archive inside it, with PyInstaller's reader, which phase 1 installed.
        members = _onefile_members(exe)
        wanted = [f"bin/{name}" for name in
                  (exe_name(UNIFIEDLOG), UNIFIEDLOG_LICENSE, UNIFIEDLOG_NOTICES)]
        missing = [name for name in wanted if name not in members]
        detail = f" (missing: {', '.join(missing)})" if missing else ""
        check(not missing, "the Unified Log parser, its licence and its notices are inside "
                           f"the executable{detail}")
    elif _unifiedlog_binary() is not None:
        # Where scripts/unifiedlogs.py looks for it at run time, and still executable.
        folder = bundled_bin_dir()
        bundled = folder / exe_name(UNIFIEDLOG)
        runs = bundled.is_file() and os.access(bundled, os.X_OK)
        result = _run_built([str(bundled), "--help"]) if runs else None
        check(runs and result.returncode == 0,
              f"the Unified Log parser is bundled and runs ({bundled})", result)
        check((folder / UNIFIEDLOG_LICENSE).is_file() and (folder / UNIFIEDLOG_NOTICES).is_file(),
              "the parser's licence and third-party notices are beside it")

    # The window is built with Tk, so on Linux it needs a display, which CI gets from
    # xvfb-run. Skipping it without one would pass a build nobody has tested.
    headless = sys.platform not in ("win32", "darwin")
    if headless and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        check(False, "the window's self-check needs a display; run this under xvfb-run")
    else:
        expected = _source_artifact_count()
        result = _run_built([str(exe), "--selfcheck"])
        found = re.search(r"selfcheck passed: (\d+) artifacts", result.stdout)
        loaded = int(found.group(1)) if found else None
        check(result.returncode == 0 and loaded == expected,
              f"the window starts Tk, loads its images and all {expected} artifacts "
              f"(the build loaded {loaded})", result)

    if headless:
        # Started without arguments where no window can open, as over SSH, it must say how
        # to use the command line rather than fail trying to open one.
        env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY")}
        result = _run_built([str(exe)], timeout=300, env=env)
        check(result.returncode == 0 and "usage:" in result.stdout + result.stderr,
              "without arguments or a display, it prints the command line's help", result)

    print(f"==> smoke: {len(failures)} of the checks failed" if failures
          else "==> smoke: every check passed", flush=True)
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build.py", epilog=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("exe", help="phase 1: build ileapp with PyInstaller")
    p.add_argument("--onefile", action="store_true", help="a single executable instead of one folder")
    p.add_argument("--clean", action="store_true",
                   help="remove build/ and the previous phase 1 output in dist/ first")
    p = sub.add_parser("smoke", help="run the phase 1 executable headlessly and check what it does")
    p.add_argument("--onefile", action="store_true", help="check the --onefile build")
    p = sub.add_parser("installer", help="phase 2: Inno Setup installer (Windows), .dmg (macOS) "
                                         "or AppImage (Linux)")
    p.add_argument("--sign-tool", metavar="NAME",
                   help="Inno Setup Sign Tool name; signs the installer and the uninstaller")
    p = sub.add_parser("all", help="both phases, unsigned")
    p.add_argument("--onefile", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--sign-tool", metavar="NAME", help=argparse.SUPPRESS)
    p.add_argument("--clean", action="store_true",
                   help="remove build/ and the previous phase 1 output in dist/ first")
    p = sub.add_parser("verify", help="check code signatures on built files")
    p.add_argument("paths", nargs="+")
    p.add_argument("--subject", metavar="TEXT", help="require the signer subject to contain TEXT")
    args = parser.parse_args(argv)

    if args.cmd == "all" and args.onefile:
        parser.error(f"the installer packages the one-folder layout, dist/{APP}/; "
                     "it cannot be built from a --onefile build")
    if args.cmd == "all" and args.sign_tool:
        parser.error(f"'all' builds unsigned; to sign, run 'exe', sign dist/{APP}/"
                     f"{exe_name(EXE)}, then 'installer --sign-tool NAME'")

    if args.cmd == "exe":
        build_exe(args.onefile, args.clean)
    elif args.cmd == "smoke":
        return smoke(args.onefile)
    elif args.cmd == "installer":
        build_installer(args.sign_tool)
    elif args.cmd == "all":
        build_exe(False, args.clean)
        build_installer(None)
    elif args.cmd == "verify":
        return verify(args.paths, args.subject)
    return 0


if __name__ == "__main__":
    sys.exit(main())
