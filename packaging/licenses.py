"""Third-party licences the packaged program carries, kept in LICENSES/.

The program's own source is MIT. The packaged builds also carry code from other projects,
and the one with conditions on redistribution is pillow-heif, whose binary wheels bundle
libheif and libde265 (LGPL-3.0) and x265 (GPL-2.0-or-later). LICENSES/ holds their texts
and THIRD-PARTY-NOTICES.md, and LICENSES/sources.json names the source archive of each
bundled library with its SHA-256, so each release can carry that source beside the program.

    python packaging/licenses.py check            the installed pillow-heif matches LICENSES/
    python packaging/licenses.py fetch-sources DIR
                                                  download every archive in sources.json into
                                                  DIR, refusing any whose SHA-256 differs

The texts are pinned to one pillow-heif version. A newer wheel can bundle other library
versions, so a build with any other version installed is refused until LICENSES/ is updated.
This file is the same in all five LEAPP cores.
"""

from __future__ import annotations

import hashlib
import json
import ssl
import sys
import urllib.request
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LICENSES = ROOT / "LICENSES"
SOURCES = LICENSES / "sources.json"
NOTICES = "THIRD-PARTY-NOTICES.md"
# The wheel's own list of what it bundles, committed as shipped by the pinned version.
BUNDLED_LIST = "pillow-heif-LICENSES_bundled.txt"
DEST = "LICENSES"


def sources() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def license_files() -> list[Path]:
    """Every file in LICENSES/, sorted, so the bundle and the zip carry the same set."""
    return sorted(p for p in LICENSES.iterdir() if p.is_file() and not p.name.startswith("."))


def bundle_datas() -> list[tuple[str, str]]:
    """LICENSES/ as PyInstaller data entries, placed in LICENSES/ inside the bundle."""
    return [(str(path), DEST) for path in license_files()]


def bundled_names() -> list[str]:
    """The paths a built program must hold, with / as the separator."""
    return [f"{DEST}/{path.name}" for path in license_files()]


def problems() -> list[str]:
    """Why the installed pillow-heif does not match LICENSES/, or [] when it does."""
    found = []
    for name in (NOTICES, BUNDLED_LIST, "sources.json"):
        if not (LICENSES / name).is_file():
            found.append(f"{LICENSES / name} is missing")
    if found:
        return found
    pinned = sources()["pillow-heif"]
    try:
        dist = metadata.distribution("pillow-heif")
    except metadata.PackageNotFoundError:
        return ["pillow-heif is not installed; run pip install -r requirements.txt"]
    if dist.version != pinned:
        return [f"pillow-heif {dist.version} is installed, but LICENSES/ covers {pinned}. "
                f"Install {pinned}, or update LICENSES/ for the new version first."]
    shipped = next((f for f in dist.files or [] if f.name == "LICENSES_bundled.txt"), None)
    if shipped is None:
        return ["the installed pillow-heif has no LICENSES_bundled.txt to compare"]
    committed = (LICENSES / BUNDLED_LIST).read_text(encoding="utf-8")
    if Path(dist.locate_file(shipped)).read_text(encoding="utf-8") != committed:
        return [f"the installed pillow-heif {pinned} lists other bundled libraries than "
                f"LICENSES/{BUNDLED_LIST}; update LICENSES/ to match it"]
    return []


def check() -> None:
    """Refuse a build whose pillow-heif is not the one LICENSES/ describes."""
    found = problems()
    if found:
        sys.exit("licences: " + "\n licences: ".join(found))
    print(f"==> licences: pillow-heif {sources()['pillow-heif']} matches LICENSES/", flush=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_sources(folder: Path) -> list[Path]:
    """Download each source archive in sources.json into folder, verified by SHA-256."""
    folder.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context()
    fetched = []
    for entry in sources()["sources"]:
        dest = folder / entry["asset"]
        request = urllib.request.Request(entry["url"], headers={"User-Agent": "leapp-release"})
        with urllib.request.urlopen(request, context=context, timeout=300) as response, \
                open(dest, "wb") as out:
            while block := response.read(1 << 20):
                out.write(block)
        actual = _sha256(dest)
        if actual != entry["sha256"]:
            dest.unlink()
            sys.exit(f"licences: {entry['url']} has SHA-256 {actual}, "
                     f"sources.json expects {entry['sha256']}")
        print(f"==> {dest.name}: {dest.stat().st_size:,} bytes, SHA-256 verified", flush=True)
        fetched.append(dest)
    return fetched


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["check"]:
        check()
        return 0
    if len(args) == 2 and args[0] == "fetch-sources":
        fetch_sources(Path(args[1]))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
