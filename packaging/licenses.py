"""Third-party code the packaged program carries, and its licence texts.

The program's own source is MIT. To show HEIC images it uses heicreader (MIT), whose helper
program is built from a pure-Go HEVC decoder (MIT) and the Go runtime (BSD-3-Clause).
LICENSES/ holds those texts and THIRD-PARTY-NOTICES.md, and ships inside every build.

Every build also carries LICENSES/bundled/, written while the spec runs: the licence files
of each Python package that has a file in the bundle, Python's own licence, PyInstaller's
(its bootloader starts the program), the licences of the repository's vendored code, and
INDEX.md, which lists them and names the packages under copyleft terms with their source.
A package whose wheel ships no licence file takes its text from LICENSES/packages/; a
bundled package with neither stops the build. A file from the build machine itself, such as
a system library a package compiled on that machine links, is traced to the system package
that installed it (dpkg on Debian and Ubuntu, a Homebrew keg on macOS) and that package's
licence file is shipped; a file traced to nothing stops the build. Windows builds leave out
the Universal C Runtime, which Windows 10 and later always load from the system.

    python packaging/licenses.py check     the installed heicreader matches LICENSES/

heicreader's version is pinned by the wheel URLs in requirements.txt. A build refuses to run
when the installed heicreader is another version, when its licence texts differ from the
copies in LICENSES/, or when a file named like a GPL library (GPL_CODECS below) would be
bundled: pillow-heif once brought x265 in that way. This file is the same in all five LEAPP cores.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LICENSES = ROOT / "LICENSES"
NOTICES = "THIRD-PARTY-NOTICES.md"
DEST = "LICENSES"
HELPER_DEST = "heicreader/bin"
# Name parts of GPL-licensed libraries that must never be bundled: video codecs (pillow-heif
# once brought x265 in) and GNU Readline, which Python's readline module links on Linux.
GPL_CODECS = ("x264", "x265", "xvid", "rubberband", "vidstab", "frei0r", "libreadline")
# Modules the spec leaves out. Python's readline module links GNU Readline (GPL-3.0) on Linux;
# the programs never import it, and the standard library imports it only inside try/except.
EXCLUDES = ["readline"]

# Licence texts for packages whose wheels ship none, by normalised package name.
FALLBACKS = LICENSES / "packages"
BUNDLED_DEST = f"{DEST}/bundled"
BUNDLED_INDEX = f"{BUNDLED_DEST}/INDEX.md"
GENERATED = ROOT / "build" / "licences" / "bundled"
REPOSITORIES = {"iLEAPP": "abrignoni/iLEAPP", "ALEAPP": "abrignoni/ALEAPP",
                "RLEAPP": "abrignoni/RLEAPP", "VLEAPP": "abrignoni/VLEAPP",
                "DLEAPP": "abrignoni/DLEAPP"}
_LICENCE_NAME = re.compile(r"^(LICEN[CS]E|COPYING|NOTICE|AUTHORS)", re.I)
# A licence the metadata states, and, in a licence file, the title of a GPL or LGPL text or an
# SPDX identifier. Matched with case in the files, so prose that only mentions the GPL is not.
_COPYLEFT = re.compile(r"\bL?GPL|General Public License|Mozilla Public License|\bMPL\b", re.I)
_COPYLEFT_TEXT = re.compile(r"GNU (LESSER |LIBRARY )?GENERAL PUBLIC LICENSE|\b(L?GPL|MPL)-[0-9]")
_COPYLEFT_HEADER = re.compile(r"GNU (LESSER |LIBRARY )?GENERAL PUBLIC LICENSE|"
                              r"SPDX-License-Identifier:.*\b(L?GPL|MPL)", re.I)
# The Universal C Runtime: ucrtbase.dll and its api-ms-win-*.dll forwarders. "On Windows 10 and
# Windows 11, the Universal CRT in the system directory is always used, even if an application
# includes an application-local copy" (learn.microsoft.com/cpp/windows/universal-crt-deployment),
# and Python's Windows guide says "If you require Windows 8.1 support, install Python 3.12"
# (docs.python.org/3.14/using/windows.html), so from 3.13 every Windows that runs it has one.
_UCRT = re.compile(r"^(api-ms-win-.+|ucrtbase)\.dll$", re.I)
# Where each Debian or Ubuntu package keeps its copyright file (Debian Policy 12.5).
DEBIAN_DOCS = Path("/usr/share/doc")
_CELLAR = re.compile(r"^(?P<keg>.*/Cellar/(?P<formula>[^/]+)/(?P<version>[^/]+))/")


def pinned_version() -> str | None:
    """The heicreader version the requirements.txt wheel URLs name, if they all agree."""
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    found = set(re.findall(r"/heicreader-([0-9][\w.]*)-py3-none-", text))
    return found.pop() if len(found) == 1 else None


def license_files() -> list[Path]:
    """Every file in LICENSES/, sorted, so the bundle and the zip carry the same set."""
    return sorted(p for p in LICENSES.iterdir() if p.is_file() and not p.name.startswith("."))


def bundle_datas() -> list[tuple[str, str]]:
    """LICENSES/ as PyInstaller data entries, placed in LICENSES/ inside the bundle."""
    return [(str(path), DEST) for path in license_files()]


def bundled_names() -> list[str]:
    """The licence paths a built program must hold, with / as the separator."""
    return [f"{DEST}/{path.name}" for path in license_files()] + [BUNDLED_INDEX]


def helper_binary() -> Path | None:
    """The heicreader helper of the installed package, or None."""
    try:
        import heicreader  # pylint: disable=import-outside-toplevel
    except ImportError:
        return None
    return heicreader.binary_path()


def heicreader_binaries() -> list[tuple[str, str]]:
    """The helper as a PyInstaller binaries entry, beside heicreader's own package.

    A binary rather than data, because PyInstaller keeps the execute permission of binaries
    only. heicreader looks for it in heicreader/bin next to its __init__, which in a frozen
    program is under sys._MEIPASS, so the same rule finds it there.
    """
    binary = helper_binary()
    return [(str(binary), HELPER_DEST)] if binary else []


def _installed_licences(dist) -> dict[str, bytes]:
    """The licence files in heicreader's dist-info, keyed by name, LICENSE as heicreader-LICENSE.txt."""
    found = {}
    for entry in dist.files or []:
        parts = Path(str(entry)).parts
        if "licenses" not in parts:
            continue
        name = parts[-1]
        found["heicreader-LICENSE.txt" if name == "LICENSE" else name] = \
            Path(dist.locate_file(entry)).read_bytes()
    return found


def problems() -> list[str]:
    """Why the installed heicreader does not match LICENSES/, or [] when it does."""
    if not (LICENSES / NOTICES).is_file():
        return [f"{LICENSES / NOTICES} is missing"]
    pinned = pinned_version()
    if pinned is None:
        return ["requirements.txt must name one heicreader version in its wheel URLs"]
    try:
        dist = metadata.distribution("heicreader")
    except metadata.PackageNotFoundError:
        return ["heicreader is not installed; run pip install -r requirements.txt"]
    if dist.version != pinned:
        return [f"heicreader {dist.version} is installed, but requirements.txt pins {pinned}"]
    if helper_binary() is None:
        return ["the installed heicreader has no helper for this platform"]
    found = []
    for name, data in sorted(_installed_licences(dist).items()):
        if name == NOTICES:
            name = "heicreader-THIRD-PARTY-NOTICES.md"
        committed = LICENSES / name
        if not committed.is_file():
            found.append(f"LICENSES/{name} is missing; copy it from the installed heicreader")
        elif committed.read_bytes().replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n"):
            found.append(f"LICENSES/{name} differs from the installed heicreader {pinned}")
    return found


def check() -> None:
    """Refuse a build whose heicreader is not the one LICENSES/ describes."""
    found = problems()
    if found:
        sys.exit("licences: " + "\n licences: ".join(found))
    print(f"==> licences: heicreader {pinned_version()} matches LICENSES/", flush=True)


def gpl_codecs(names) -> list[str]:
    """The names, among file names or paths, of GPL video codec libraries."""
    hits = []
    for name in names:
        base = Path(str(name).replace("\\", "/")).name.lower()
        if any(codec in base for codec in GPL_CODECS):
            hits.append(str(name))
    return sorted(hits)


def refuse_gpl_codecs(names) -> None:
    hits = gpl_codecs(names)
    if hits:
        sys.exit("licences: these GPL libraries would ship, and the program is MIT: "
                 + ", ".join(hits))


def without_ucrt(binaries, platform_: str = sys.platform, version=sys.version_info) -> list:
    """The spec's binaries without the Universal C Runtime, on Windows from Python 3.13."""
    if platform_ != "win32" or tuple(version[:2]) < (3, 13):
        return list(binaries)
    return [entry for entry in binaries
            if not _UCRT.match(Path(str(entry[0]).replace("\\", "/")).name)]


# -- files from the build machine -----------------------------------------------------------

def _dpkg_query(args: list[str]) -> str | None:
    """dpkg-query's output, or None where there is no dpkg."""
    try:
        run = subprocess.run(["dpkg-query", *args], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, check=False)
    except OSError:
        return None
    return run.stdout


def _path_spellings(src: str) -> list[str]:
    """The paths dpkg may know a file by: as found, resolved, and across the /usr merge.

    On a merged /usr, /lib is a link to /usr/lib, and dpkg's database records a library under
    whichever of the two its package installed it, so a resolved path is not enough.
    """
    found = []
    for path in (src, os.path.realpath(src)):
        merged = re.match(r"^/usr(/(?:lib|lib32|lib64|bin|sbin)/.*)$", path)
        split = re.match(r"^/(?:lib|lib32|lib64|bin|sbin)/", path)
        for spelling in (path, merged.group(1) if merged else "/usr" + path if split else path):
            if spelling not in found:
                found.append(spelling)
    return found


def _dpkg_owners(sources: list[str]) -> dict[str, str]:
    """{source path: the dpkg package that installed it}, for the paths dpkg knows."""
    spellings = {src: _path_spellings(src) for src in sources}
    query = sorted({s for found in spellings.values() for s in found})
    output = _dpkg_query(["-S", *query]) if query else None
    if not output:
        return {}
    owner = {}
    for line in output.splitlines():
        # "package[:arch][, package...]: /path"; diversion lines are not ownership.
        if line.startswith("diversion ") or ": " not in line:
            continue
        packages, path = line.split(": ", 1)
        owner.setdefault(path, packages.split(",")[0].strip().split(":")[0])
    return {src: next(owner[s] for s in found if s in owner)
            for src, found in spellings.items() if any(s in owner for s in found)}


def _debian_source_link(name: str, version: str) -> str:
    try:
        system = platform.freedesktop_os_release().get("ID", "")
    except OSError:
        system = ""
    if system == "ubuntu":
        return f"https://launchpad.net/ubuntu/+source/{name}/{version}"
    if system == "debian":
        return f"https://snapshot.debian.org/package/{name}/{version}/"
    return f"source package {name} {version}"


def _dpkg_package(name: str) -> dict:
    fields = (_dpkg_query(["-W", "-f", "${Version}\\t${source:Package}\\t${source:Version}\\n",
                           name]) or "").splitlines()
    version, source, source_version = (fields[0].split("\t") + ["", "", ""])[:3] if fields \
        else ("", "", "")
    copyright_file = DEBIAN_DOCS / name / "copyright"
    return {
        "name": name, "version": version,
        "licence": "see its copyright file",
        "source": _debian_source_link(source or name, source_version or version),
        "files": [("copyright", copyright_file)] if copyright_file.is_file() else [],
    }


def _homebrew_package(keg: Path, formula: str, version: str) -> dict:
    """A Homebrew keg's licence files, and the licence and source its SBOM states."""
    files = sorted((p.name, p) for p in keg.iterdir() if p.is_file() and _LICENCE_NAME.match(p.name))
    licence, source = "not stated by Homebrew", f"https://formulae.brew.sh/formula/{formula}"
    try:
        sbom = json.loads((keg / "sbom.spdx.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        sbom = {}
    for package in sbom.get("packages", []):
        if package.get("name") != formula:
            continue
        concluded = package.get("licenseConcluded") or ""
        if concluded and concluded != "NOASSERTION" and licence.startswith("not stated"):
            licence = f"{concluded} (Homebrew's SBOM)"
        location = package.get("downloadLocation") or ""
        if location.startswith("https://") and "ghcr.io" not in location:
            source = location
    return {"name": formula, "version": version, "licence": licence, "source": source,
            "files": files}


def system_packages(entries: list[tuple[str, str]]):
    """Trace files from the build machine to the system packages that installed them.

    entries are (name in the bundle, source path). Returns ({package: record}, {package: the
    names it supplies}, [names traced to no package]). A record holds the package's name,
    version, licence, source and licence files.
    """
    packages, supplies, untraced = {}, {}, []
    if sys.platform.startswith("linux"):
        owners = _dpkg_owners(sorted({src for _, src in entries}))
        for name, src in entries:
            package = owners.get(src)
            if package is None:
                untraced.append(name)
                continue
            if package not in packages:
                packages[package] = _dpkg_package(package)
            supplies.setdefault(package, []).append(name)
    elif sys.platform == "darwin":
        for name, src in entries:
            match = _CELLAR.match(os.path.realpath(src).replace("\\", "/"))
            if match is None:
                untraced.append(name)
                continue
            formula = match["formula"]
            if formula not in packages:
                packages[formula] = _homebrew_package(Path(match["keg"]), formula, match["version"])
            supplies.setdefault(formula, []).append(name)
    else:
        untraced = [name for name, _ in entries]
    return packages, supplies, untraced


# -- the licences of what a build holds -----------------------------------------------------

def _key(path) -> str:
    return os.path.normcase(os.path.realpath(str(path)))


def _normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _owners(distributions) -> dict:
    """Every file an installed distribution's RECORD names, mapped to that distribution."""
    owned = {}
    for dist in distributions:
        for entry in dist.files or []:
            if "__pycache__" not in Path(str(entry)).parts:
                owned[_key(dist.locate_file(entry))] = dist
    return owned


def _licence_files(dist) -> list[tuple[str, Path]]:
    """(path inside the dist-info, file) for each licence file a distribution ships."""
    found = []
    for entry in dist.files or []:
        parts = Path(str(entry)).parts
        if len(parts) < 2 or not parts[0].endswith(".dist-info"):
            continue
        inside = parts[1:]
        if inside[0] == "licenses" and len(inside) > 1:
            name = "/".join(inside[1:])
        elif len(inside) == 1 and _LICENCE_NAME.match(inside[0]):
            name = inside[0]
        else:
            continue
        path = Path(dist.locate_file(entry))
        if path.is_file():
            found.append((name, path))
    return sorted(found)


def _licence_label(dist) -> str:
    """The licence a distribution's metadata states, as it states it."""
    meta = dist.metadata
    expression = (meta.get("License-Expression") or "").strip()
    if expression:
        return expression
    text = (meta.get("License") or "").strip()
    if text and "\n" not in text and len(text) <= 80:
        return text
    classifiers = [c.split("::")[-1].strip() for c in meta.get_all("Classifier") or []
                   if c.startswith("License ::")]
    return "; ".join(classifiers) or "not stated in its metadata"


def _python_licence() -> Path:
    # Beside the standard library on macOS and Linux, at the installation's root on Windows.
    for candidate in (Path(os.__file__).resolve().parent / "LICENSE.txt",
                      Path(sys.base_prefix) / "LICENSE.txt"):
        if candidate.is_file():
            return candidate
    sys.exit("licences: the LICENSE.txt of the Python running this build was not found")


def _copy(src: Path, out: Path, rel: str, written: list[str]) -> None:
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    written.append(rel)


def _source(dist) -> str:
    """Where the installed distribution came from: its direct URL, or its PyPI release page."""
    try:
        direct = json.loads(dist.read_text("direct_url.json") or "{}")
    except (OSError, ValueError):
        direct = {}
    url = direct.get("url", "")
    commit = direct.get("vcs_info", {}).get("commit_id")
    if url.startswith("https://"):
        return f"{url} (commit {commit})" if commit else url
    return f"https://pypi.org/project/{dist.metadata['Name']}/{dist.version}/#files"


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def collect_bundled(tocs, app: str, version: str, out: Path = GENERATED,
                    distributions=None, system=None) -> list[tuple[str, str, str]]:
    """Write LICENSES/bundled/ for the files a build holds; return it as PyInstaller data.

    tocs are the spec's a.pure, a.scripts, a.binaries and a.datas. Each entry's source file is
    looked up in the RECORD of every installed distribution, so a package is listed when, and
    only when, one of its files is in the bundle. A file under the repository is the
    program's own; one under the Python installation, outside site-packages, is Python's;
    any other came from the build machine and is traced by system (system_packages unless
    given) to the system package that installed it. A file traced to none stops the build.
    """
    dists = list(metadata.distributions()) if distributions is None else list(distributions)
    owned = _owners(dists)
    root = _key(ROOT) + os.sep
    bases = {_key(sys.base_prefix) + os.sep, _key(sys.prefix) + os.sep}
    bundled, repo_sources, other = {}, set(), {}
    for toc in tocs:
        for entry in toc:
            src = entry[1]
            if not src or not os.path.isabs(str(src)):
                continue
            key = _key(src)
            dist = owned.get(key)
            if dist is not None:
                bundled[_normalise(dist.metadata["Name"])] = dist
            elif key.startswith(root):
                repo_sources.add(Path(src))
            elif (any(key.startswith(base) for base in bases)
                  and "site-packages" not in Path(key).parts):
                continue
            else:
                other[str(entry[0]).replace("\\", "/")] = str(src)
    bundled.pop("pyinstaller", None)   # listed on its own below
    machine, supplies, untraced = (system or system_packages)(sorted(other.items()))
    if untraced:
        shown = ", ".join(sorted(untraced)[:20]) + (" ..." if len(untraced) > 20 else "")
        sys.exit(f"licences: {len(untraced)} bundled files came from the build machine and were "
                 "traced to no system package, so their licences cannot be shipped: " + shown)
    unlicensed = sorted(f"{p['name']} {p['version']}" for p in machine.values() if not p["files"])
    if unlicensed:
        sys.exit("licences: these system packages supply bundled files but have no licence "
                 "file on the build machine: " + ", ".join(unlicensed))

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    written: list[str] = []
    rows, copyleft, missing = [], [], []
    for name in sorted(bundled):
        dist = bundled[name]
        title, version_ = dist.metadata["Name"], dist.version
        folder = f"packages/{title}-{version_}"
        files = _licence_files(dist)
        names = []
        for rel, path in files:
            _copy(path, out, f"{folder}/{rel}", names)
        if not files:
            fallback = FALLBACKS / f"{name}.txt"
            if not fallback.is_file():
                missing.append(f"{title} {version_}")
                continue
            _copy(fallback, out, f"{folder}/LICENSE-from-LICENSES-packages.txt", names)
            files = [(fallback.name, fallback)]
        written += names
        label = _licence_label(dist)
        texts = " ".join(path.read_text(encoding="utf-8", errors="replace") for _, path in files)
        rows.append((title, version_, label, names))
        if _COPYLEFT.search(label) or _COPYLEFT_TEXT.search(texts):
            copyleft.append((title, version_, label, _source(dist)))
    if missing:
        sys.exit("licences: these bundled packages ship no licence file, and LICENSES/packages/ "
                 "has no text for them: " + ", ".join(missing))

    _copy(_python_licence(), out, "python/LICENSE.txt", written)
    try:
        pyinstaller = metadata.distribution("pyinstaller")
    except metadata.PackageNotFoundError:
        sys.exit("licences: PyInstaller is not installed, so its licence cannot be bundled")
    pyinstaller_files = _licence_files(pyinstaller)
    if not pyinstaller_files:
        sys.exit("licences: the installed PyInstaller ships no licence file")
    for rel, path in pyinstaller_files:
        _copy(path, out, f"pyinstaller/{rel}", written)

    machine_rows = []
    for key in sorted(machine):
        package = machine[key]
        folder = f"system/{package['name']}-{package['version']}".replace(":", "_")
        names = []
        for rel, path in package["files"]:
            _copy(Path(path), out, f"{folder}/{rel}", names)
        written += names
        machine_rows.append((package, names, sorted(supplies[key])))

    _copy(ROOT / "LICENSE", out, "repository/LICENSE", written)
    for path in sorted((ROOT / "scripts").rglob("*")):
        if path.is_file() and _LICENCE_NAME.match(path.name):
            _copy(path, out, f"repository/{path.relative_to(ROOT).as_posix()}", written)
    repo_copyleft = sorted(
        path.relative_to(ROOT).as_posix() for path in repo_sources
        if path.suffix == ".py"
        and _COPYLEFT_HEADER.search(path.read_text(encoding="utf-8", errors="replace")[:8192]))

    repo = REPOSITORIES.get(app, f"abrignoni/{app}")
    lines = [
        f"# Licences of the code inside {app} {version}",
        "",
        f"Written by packaging/licenses.py when this program was built, on {platform.system()} "
        f"{platform.machine()}, from the files PyInstaller put in it. The folders beside this file "
        "hold the licence texts.",
        "",
        f"{app}'s own code is MIT (repository/LICENSE). Its source, with how to build it, is at "
        f"https://github.com/{repo}; a release is built from the tag v{version}. The licences "
        "of the code it vendors are under repository/scripts/.",
        "",
        "## Python packages",
        "",
        "Each package's licence as its metadata states it, and its licence files.",
        "",
        "| Package | Version | Licence | Licence files |",
        "| --- | --- | --- | --- |",
    ]
    lines += [f"| {_cell(t)} | {_cell(v)} | {_cell(lab)} | {_cell(', '.join(n))} |"
              for t, v, lab, n in rows]
    if copyleft:
        lines += [
            "",
            "## Packages with copyleft terms",
            "",
            "These packages are under, or carry licence files that mention, the GNU GPL or LGPL "
            "or the Mozilla Public License. Their licence files say which parts those terms "
            "cover. The source of each, at the version bundled, is at the link given. "
            "The LGPL lets you use a modified version of such a library: build "
            f"{app} from its source (above) with the modified package installed.",
            "",
        ]
        lines += [f"- {t} {v} ({lab}): {src}" for t, v, lab, src in copyleft]
    if repo_copyleft:
        lines += ["", "## Repository files with copyleft terms", "",
                  "These bundled files of the repository carry a GNU GPL, LGPL or MPL licence "
                  "in their header; the source above holds them with it.", ""]
        lines += [f"- {name}" for name in repo_copyleft]
    lines += [
        "",
        "## Python",
        "",
        f"The program runs on the Python {platform.python_version()} that built it. "
        "python/LICENSE.txt is that Python's licence file.",
        "",
        "## PyInstaller",
        "",
        "PyInstaller packed the program, and its bootloader starts it. PyInstaller is "
        "GPL-2.0-or-later with a bootloader exception, which permits embedding the bootloader "
        "in a program and distributing it without restriction from that licence "
        "(pyinstaller/).",
    ]
    if machine_rows:
        lines += [
            "",
            "## Libraries from the build machine",
            "",
            "These files came from packages installed on the build machine, not from a Python "
            "package. Each package's licence files are under system/. A Debian or Ubuntu "
            "copyright file covers the package's whole source, so it can name licences for "
            "parts not shipped here. The Source column names where the source of each, at "
            "the version bundled, can be had.",
            "",
            "| Package | Version | Licence | Files in this program | Licence files | Source |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for package, names, files in machine_rows:
            shown = ", ".join(files) if len(files) <= 3 else f"{len(files)} files"
            lines.append(f"| {_cell(package['name'])} | {_cell(package['version'])} | "
                         f"{_cell(package['licence'])} | {_cell(shown)} | "
                         f"{_cell(', '.join(names))} | {_cell(package['source'])} |")
    (out / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append("INDEX.md")
    return [(f"{BUNDLED_DEST}/{rel}", str(out / rel), "DATA") for rel in sorted(written)]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["check"]:
        check()
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
