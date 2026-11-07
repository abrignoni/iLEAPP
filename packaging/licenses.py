"""Third-party code the packaged program carries for HEIC images, and its licence texts.

The program's own source is MIT. To show HEIC images it uses heicreader (MIT), whose helper
program is built from a pure-Go HEVC decoder (MIT) and the Go runtime (BSD-3-Clause).
LICENSES/ holds those texts and THIRD-PARTY-NOTICES.md, and ships inside every build.

    python packaging/licenses.py check     the installed heicreader matches LICENSES/

heicreader's version is pinned by the wheel URLs in requirements.txt. A build refuses to run
when the installed heicreader is another version, when its licence texts differ from the
copies in LICENSES/, or when a GPL video codec (x264, x265 and the like) would be bundled:
pillow-heif once brought x265 in that way. This file is the same in all five LEAPP cores.
"""

from __future__ import annotations

import re
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LICENSES = ROOT / "LICENSES"
NOTICES = "THIRD-PARTY-NOTICES.md"
DEST = "LICENSES"
HELPER_DEST = "heicreader/bin"
# Name parts of GPL-licensed codec libraries that must never be bundled.
GPL_CODECS = ("x264", "x265", "xvid", "rubberband", "vidstab", "frei0r")


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
    return [f"{DEST}/{path.name}" for path in license_files()]


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
        sys.exit("licences: these GPL codec libraries would ship, and the program is MIT: "
                 + ", ".join(hits))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["check"]:
        check()
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
