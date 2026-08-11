"""Download the pinned unifiedlog_iterator release into bin/ for packaging.

The binary reads Apple Unified Log .tracev3 data directly, which is what lets iLEAPP
import Unified Logs without a Mac and without Apple's `log show`. It is not committed to
this repository: it is a third-party compiled artifact, it exists per platform, and an
examiner should be able to see exactly which build went into a release.

Run before building a release, on the machine doing the build:

    python admin/scripts/fetch_unifiedlog_iterator.py
    python admin/scripts/fetch_unifiedlog_iterator.py --platform linux-x86_64

There is one bin/unifiedlog_iterator, holding the build for the platform being packaged,
so fetching several in a row would just overwrite it. Each release build fetches its own.

Every download is checked against the digest pinned below and the run refuses to write
anything that does not match. Update PINNED_VERSION and the digests together, and record
what changed; a release should be reproducible from the version in bin/PROVENANCE.md.
"""
import argparse
import hashlib
import io
import os
import pathlib
import platform
import ssl
import sys
import tarfile
import urllib.request
import zipfile

PINNED_VERSION = 'v0.6.0'
REPO = 'mandiant/macos-UnifiedLogs'
BASE_URL = f'https://github.com/{REPO}/releases/download/{PINNED_VERSION}'

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / 'bin'

# sha256 of each release archive. Every digest below was verified by downloading the
# archive and hashing it independently, not just read from the published .sha256 files.
# All values are stored lowercase; comparisons are case-insensitive (see
# _normalize_digest) because upstream's per-platform build runners disagree on case -
# the Windows .sha256 is uppercase (PowerShell Get-FileHash style), the rest lowercase.
ASSETS = {
    'macos-arm64': ('unifiedlog_iterator-v0.6.0-aarch64-apple-darwin.tar.gz',
                    'd3e0e620b51358dc3f4a7d376551a435153e9a4a7942cb52ddb7144a72bbdb63'),
    'macos-x86_64': ('unifiedlog_iterator-v0.6.0-x86_64-apple-darwin.tar.gz',
                     '28f4a5641543559ef90472537950fafb344a13eb64c432d7929748b45007afe8'),
    # No musl build is published for aarch64; gnu is the only option there.
    'linux-arm64': ('unifiedlog_iterator-v0.6.0-aarch64-unknown-linux-gnu.tar.gz',
                    '1e519eef11e5763d44311600077318d9bdd2c8b1c806191b7c9b345e1c995c5f'),
    # Linux x86_64 deliberately takes the musl build (verified static-pie linked, no
    # dynamic libc). The gnu build links whatever glibc the release runner carries, and a
    # binary built against a newer glibc refuses to start on older distros - the exact
    # machines an AppImage exists to support, and forensic workstations skew old. The gnu
    # build stays reachable below for anyone who wants it.
    'linux-x86_64': ('unifiedlog_iterator-v0.6.0-x86_64-unknown-linux-musl.tar.gz',
                     '43fb304af5b3cc19ce15490f6e0ff4255e7707b69c51fc67e279677ea9784adb'),
    'linux-x86_64-gnu': ('unifiedlog_iterator-v0.6.0-x86_64-unknown-linux-gnu.tar.gz',
                         'f5a17b056092be347e5d7f5051a6c3698e635bd7eeb22e595efbf13897e03419'),
    'windows-x86_64': ('unifiedlog_iterator-v0.6.0-x86_64-pc-windows-msvc.zip',
                       '749731fc09d0d107958d777188c99682db8f2d7810835d6afe46172e1d0d9d36'),
}


def _normalize_digest(value):
    """Lowercase a hex digest and unfold upstream's doubled-digest quirk.

    Two independent formatting differences in upstream's published .sha256 files have
    produced false "mismatch" refusals for users: the Windows file is UPPERCASE
    (PowerShell Get-FileHash), and some files print the digest twice on one line. The
    hex value is what matters; its presentation is not evidence of tampering.
    """
    value = value.strip().split()[0].lower() if value.strip() else ''
    if len(value) == 128 and value[:64] == value[64:]:
        value = value[:64]
    return value


def current_platform():
    machine = platform.machine().lower()
    arch = 'arm64' if machine in ('arm64', 'aarch64') else 'x86_64'
    if sys.platform == 'darwin':
        return f'macos-{arch}'
    if sys.platform.startswith('linux'):
        return f'linux-{arch}'
    if sys.platform.startswith('win'):
        return 'windows-x86_64'
    raise SystemExit(f'no published build for {sys.platform}')


def _ssl_context():
    """Build a verifying SSL context that also works on a bare python.org install.

    Those ship without a CA store until 'Install Certificates.command' is run, so an
    otherwise fine build machine fails with CERTIFICATE_VERIFY_FAILED. certifi's bundle is
    used when it happens to be installed. Verification is never disabled: this downloads an
    executable that goes into a forensic tool.
    """
    try:
        import certifi  # pylint: disable=import-outside-toplevel
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _download(url):
    print(f'  fetching {url}')
    with urllib.request.urlopen(  # nosec B310 - fixed https GitHub URL
            url, context=_ssl_context()) as response:
        return response.read()


def _expected_digest(asset, pinned):
    """Use the pinned digest, or fall back to the published .sha256 for platforms we
    have not pinned yet (a new PINNED_VERSION), reporting the value so it can be
    added above."""
    if pinned:
        return _normalize_digest(pinned)
    published = _normalize_digest(_download(f'{BASE_URL}/{asset}.sha256').decode())
    print(f'  no pinned digest for {asset}; published value is {published}')
    return published


def _extract(archive_bytes, asset, destination_name):
    """Pull the executable and the LICENSE out of the release archive."""
    binary = license_text = None
    if asset.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            for name in archive.namelist():
                base = os.path.basename(name)
                if base in ('unifiedlog_iterator', 'unifiedlog_iterator.exe'):
                    binary = archive.read(name)
                elif base == 'LICENSE':
                    license_text = archive.read(name)
    else:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as archive:
            for member in archive.getmembers():
                base = os.path.basename(member.name)
                if base in ('unifiedlog_iterator', 'unifiedlog_iterator.exe'):
                    binary = archive.extractfile(member).read()
                elif base == 'LICENSE':
                    license_text = archive.extractfile(member).read()

    if binary is None:
        raise SystemExit(f'{asset} does not contain unifiedlog_iterator')
    if license_text is None:
        raise SystemExit(f'{asset} does not contain its LICENSE; Apache-2.0 redistribution '
                         f'requires it')

    BIN_DIR.mkdir(exist_ok=True)
    target = BIN_DIR / destination_name
    target.write_bytes(binary)
    target.chmod(0o755)
    (BIN_DIR / 'LICENSE-unifiedlog_iterator').write_bytes(license_text)
    print(f'  wrote {target} ({len(binary):,} bytes) and its LICENSE')


def fetch(key):
    asset, pinned = ASSETS[key]
    print(f'{key}:')
    expected = _expected_digest(asset, pinned)
    archive_bytes = _download(f'{BASE_URL}/{asset}')
    actual = hashlib.sha256(archive_bytes).hexdigest()
    if _normalize_digest(actual) != expected:
        raise SystemExit(f'  DIGEST MISMATCH for {asset}\n'
                         f'    expected {expected}\n    got      {actual}\n'
                         f'  Nothing was written.')
    print(f'  sha256 verified: {actual}')
    name = 'unifiedlog_iterator.exe' if key.startswith('windows') else 'unifiedlog_iterator'
    _extract(archive_bytes, asset, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=sorted(ASSETS), default=None,
                        help='build to fetch; defaults to the platform this is run on')
    args = parser.parse_args()

    fetch(args.platform or current_platform())
    print(f'\nDone. {PINNED_VERSION} from https://github.com/{REPO}')


if __name__ == '__main__':
    main()
