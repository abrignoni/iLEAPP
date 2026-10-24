"""The times an L01 or an AD1 records for each entry, in the staged-file record.

The expected values are read without ewfprobe: an L01's from the ltree text of the
fixture, by the reading below of the EWF specification (libyal/libewf,
"Expert Witness Compression Format (EWF).asciidoc": the section descriptor, the
ltree header and the EnCase 7 entry columns), and an AD1's from FTK Imager's own
listing of the image (lean-multi-ntfs-c9.ad1.csv), whose times are UTC.
"""

import contextlib
import datetime
import io
import os
import pathlib
import shutil
import struct
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position
import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.raw_image import FileSeekerRaw  # pylint: disable=wrong-import-position
from scripts.search_files import staged_files_tsv_line  # pylint: disable=wrong-import-position

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'
L01 = FIXTURES / 'l01-times.L01'
AD1 = FIXTURES / 'lean-multi-ntfs-c9.ad1'


def ltree_rows(path):
    """{entry name: {column: value as stored}} from the first ltree section of an
    EWF-L01 segment: each section starts with a 76-byte descriptor (type, next
    offset, size), and the ltree's data is a 48-byte header (its text size at byte
    16) and UTF-16LE text whose "entry" category names its columns on its third line
    and gives each entry as a count line and a values line."""
    data = path.read_bytes()
    assert data[:8] == b'LVF\x09\x0d\x0a\xff\x00'
    offset = 13
    while True:
        kind, following, size = struct.unpack_from('<16sQQ', data, offset)
        if kind.rstrip(b'\0') == b'ltree':
            body = data[offset + 76:offset + size]
            text = body[48:48 + struct.unpack_from('<Q', body, 16)[0]].decode('utf-16-le')
            break
        assert following > offset
        offset = following
    lines = text.split('\n')
    start = lines.index('entry')
    columns = lines[start + 2].split('\t')
    rows = {}
    for line in lines[start + 3:]:
        values = line.split('\t')
        if len(values) == len(columns):
            row = dict(zip(columns, values))
            rows[row['n']] = row
    return rows


def stored(row, column):
    return int(row[column]) if row[column] else None


def listed_time(text):
    """A time in FTK Imager's listing, read as UTC."""
    if not text:
        return None
    return datetime.datetime.strptime(text, '%Y-%b-%d %H:%M:%S.%f').replace(
        tzinfo=datetime.timezone.utc).timestamp()


class LogicalEvidenceTimesTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_logical_times_')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for module in (raw_image, search_files):
            patcher = mock.patch.object(module, 'logfunc', lambda *_a, **_k: None)
            patcher.start()
            self.addCleanup(patcher.stop)

    def staged(self, image, pattern):
        """{name: FileInfo} for every file of ``image`` matching ``pattern``."""
        with contextlib.redirect_stdout(io.StringIO()):
            seeker = FileSeekerRaw(str(image), tempfile.mkdtemp(dir=self.tmp))
            self.addCleanup(seeker.cleanup)
            paths = seeker.search(pattern)
        return {os.path.basename(path): seeker.file_infos[path] for path in paths}

    def test_an_l01_records_its_four_times(self):
        rows = ltree_rows(L01)
        infos = self.staged(L01, '*/*.*')
        self.assertEqual(sorted(infos), ['none.bin', 'notes.txt', 'zero.bin'])
        for name, info in infos.items():
            row = rows[name]
            expected = tuple(stored(row, column) for column in ('wr', 'ac', 'mo', 'cr'))
            self.assertEqual(info.times[:4], expected, name)
            self.assertEqual(info.times[4], 'file system' if any(
                value is not None for value in expected) else 'none', name)
            self.assertEqual(info.times[5:], (None, None, None, None), name)

    def test_the_l01_fixture_holds_what_the_test_relies_on(self):
        rows = ltree_rows(L01)
        notes = rows['notes.txt']
        # every column read above, the deletion and acquisition times set too
        self.assertTrue(all(notes[column] for column in ('cr', 'ac', 'wr', 'mo', 'dl', 'aq')))
        self.assertEqual(rows['zero.bin']['ac'], '0')
        self.assertFalse(any(rows['none.bin'][c] for c in ('cr', 'ac', 'wr', 'mo', 'dl')))

    def test_an_l01_time_stored_as_zero_is_kept(self):
        info = self.staged(L01, '*/zero.bin')['zero.bin']
        self.assertEqual(info.times.accessed, 0)
        self.assertEqual(staged_files_tsv_line(info, 'file', None).split('\t')[4],
                         '1970-01-01T00:00:00Z')

    def test_an_ad1_records_the_three_times_ftk_imager_lists(self):
        text = (AD1.parent / (AD1.name + '.csv')).read_text(encoding='utf-16')
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        header = lines[0].split('\t')
        listed = [dict(zip(header, line.split('\t'))) for line in lines[1:]]
        files = [row for row in listed if row.get('Stored MD5 Hash') and row['Is Deleted'] == 'no'
                 and not row['Full Path'].endswith(f'readme.txt\\{row["Filename"]}')]
        self.assertEqual(len(files), 7)
        compared = 0
        for row in files:
            infos = self.staged(AD1, f'*/{row["Filename"]}')
            self.assertEqual(len(infos), 1, row['Filename'])
            info = infos[row['Filename']]
            want = [listed_time(row[column]) for column in ('Modified', 'Accessed', 'Created')]
            got = [info.times.modified, info.times.accessed, info.times.created]
            for column, wanted, value in zip(('Modified', 'Accessed', 'Created'), want, got):
                if wanted is None:
                    self.assertIsNone(value, (row['Filename'], column))
                else:
                    self.assertAlmostEqual(value, wanted, delta=1e-6,
                                           msg=(row['Filename'], column))
            self.assertIsNone(info.times.changed, row['Filename'])
            self.assertEqual(info.times.source, 'file system', row['Filename'])
            compared += 1
        self.assertEqual(compared, 7)


if __name__ == '__main__':
    unittest.main()
