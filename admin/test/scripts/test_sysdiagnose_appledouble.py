"""Cover get_sysdiagnose_files() skipping macOS AppleDouble sidecars.

A sysdiagnose archive carries an AppleDouble member (._<name>) beside each file that has
extended attributes. The sidecar holds the other file's metadata, so it is never the file a
caller asks for, whether the caller passes an exact name or a regex, and whether the file
sits inside an archive or on disk. The regexes below are the unanchored member patterns of
mobileActivationLogs, powerlog and sysShutdown, each of which also matches a sidecar name.
"""
import contextlib
import io
import os
import pathlib
import re
import sys
import tarfile
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.ilapfuncs import get_sysdiagnose_files  # pylint: disable=wrong-import-position

SD = 'sysdiagnose_2026.01.02_03-04-05-0500_iPhone-OS_iPhone_23A000'
# The start of an AppleDouble file: magic 0x00051607, version 0x00020000, filler.
APPLEDOUBLE = b'\x00\x05\x16\x07\x00\x02\x00\x00Mac OS X        \x00\x00'

ACTIVATION = f'{SD}/logs/MobileActivation/mobileactivationd.log.0'
SHUTDOWN = f'{SD}/system_logs.logarchive/Extra/shutdown.0.log'
POWERLOG = f'{SD}/logs/powerlogs/powerlog_2026-01-02_03-05_ABCD1234.PLSQL'
STATUS = f'{SD}/otctl_status.txt'


def _sidecar(inner):
    head, _sep, tail = inner.rpartition('/')
    return f'{head}/._{tail}'


def _make_archive(directory, members, name=f'{SD}.tar.gz'):
    """Write a gzipped tar laid out like a sysdiagnose; members maps inner path -> bytes."""
    path = os.path.join(directory, name)
    with tarfile.open(path, 'w:gz') as tar:
        for inner, data in members.items():
            info = tarfile.TarInfo(inner)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


class AppleDoubleSidecarsAreNotYielded(unittest.TestCase):
    """Each real file sits beside its sidecar, sidecar written first, as in a real archive."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        members = {}
        for inner, data in ((ACTIVATION, b'activation log\n'), (SHUTDOWN, b'shutdown log\n'),
                            (POWERLOG, b'SQLite format 3\x00'), (STATUS, b'status\n')):
            members[_sidecar(inner)] = APPLEDOUBLE
            members[inner] = data
        self.archive = _make_archive(self.dir, members)

    def _members(self, target):
        return [source.split(' >> ', 1)[1] for _stream, source
                in get_sysdiagnose_files([self.archive], target, text_mode=False)]

    def test_unanchored_regexes_yield_the_file_not_its_sidecar(self):
        for pattern, expected in ((r'mobileactivationd\.log(\.\d+)?$', ACTIVATION),
                                  (r'shutdown[^/]*\.log$', SHUTDOWN),
                                  (r'/logs/powerlogs/[^/]+\.(?:PLSQL|EPSQL|BGSQL)$', POWERLOG)):
            with self.subTest(pattern=pattern):
                self.assertEqual(self._members(re.compile(pattern)), [expected])

    def test_an_exact_name_still_yields_the_file(self):
        self.assertEqual(self._members('otctl_status.txt'), [STATUS])

    def test_the_file_content_is_the_file_not_the_sidecar(self):
        pattern = re.compile(r'mobileactivationd\.log(\.\d+)?$')
        contents = [stream.read() for stream, _source
                    in get_sysdiagnose_files([self.archive], pattern)]
        self.assertEqual(contents, ['activation log\n'])

    def test_a_sidecar_on_disk_is_not_opened(self):
        real = os.path.join(self.dir, 'mobileactivationd.log.0')
        sidecar = os.path.join(self.dir, '._mobileactivationd.log.0')
        for path, data in ((real, b'activation log\n'), (sidecar, APPLEDOUBLE)):
            with open(path, 'wb') as handle:
                handle.write(data)
        found = [source for _stream, source in get_sysdiagnose_files(
            [sidecar, real], re.compile(r'mobileactivationd\.log(\.\d+)?$'), text_mode=False)]
        self.assertEqual(found, [real])

    def test_a_sidecar_named_like_an_archive_is_not_opened_as_one(self):
        sidecar = os.path.join(self.dir, f'._{SD}.tar.gz')
        with open(sidecar, 'wb') as handle:
            handle.write(APPLEDOUBLE)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            found = list(get_sysdiagnose_files([sidecar], 'otctl_status.txt', text_mode=False))
        self.assertEqual(found, [])
        self.assertEqual(printed.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
