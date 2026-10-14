"""A damaged member of a zip is skipped; it does not abort the run.

A bad CRC-32 used to raise out of the seeker's
search() and end processing for every remaining artifact (ALEAPP issue 1522).
"""
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.append(os.path.dirname(__file__))

from scripts.search_files import FileSeekerZip  # noqa: E402  pylint: disable=wrong-import-position


class CorruptMemberTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_zip_bad_crc_member_is_skipped(self):
        path = os.path.join(self.tmp.name, 'a.zip')
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr('Dump/a.mp4', b'x' * 1000)
            zf.writestr('Dump/b.mp4', b'y' * 1000)
        with open(path, 'rb') as fh:
            raw = bytearray(fh.read())
        raw[raw.index(b'x' * 10) + 5] ^= 0xFF
        with open(path, 'wb') as fh:
            fh.write(raw)
        seeker = FileSeekerZip(path, os.path.join(self.tmp.name, 'out'))
        found = seeker.search('*.mp4')
        self.assertEqual([os.path.basename(p) for p in found], ['b.mp4'])
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, 'out', 'Dump', 'a.mp4')))
        self.assertEqual(seeker.search('*.mp4', force=True), found)


if __name__ == '__main__':
    unittest.main()
