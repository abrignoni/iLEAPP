"""peek(): a file's first bytes read without staging it, on every kind of input.

On the raw image fixtures peek() must name the same files search() stages, give the
same first bytes and the same FileInfo, and leave the data folder empty, so a later
search() still stages the file whole. The folder, zip and tar seekers are checked on
small inputs built here; the single-file seeker refuses with PeekUnsupported.
"""
import gzip
import io
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import raw_image, search_files  # pylint: disable=wrong-import-position
from scripts.raw_image import FileSeekerRaw  # pylint: disable=wrong-import-position
from scripts.search_files import (FileSeekerDir, FileSeekerFile, FileSeekerTar,  # pylint: disable=wrong-import-position
                                  FileSeekerZip, PeekUnsupported)

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'


def _files_in(folder):
    return sorted(os.path.join(root, name) for root, _dirs, names in os.walk(folder) for name in names)


class RawPeekTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='peek_raw_')
        cls.images = {}
        for stem in ('ntfs-fixture', 'fat32-deleted', 'exfat-deleted', 'apfs-fixture'):
            target = os.path.join(cls.work, f'{stem}.img')
            with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, open(target, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            cls.images[stem] = target

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.lines = []
        for module in (raw_image, search_files):
            patcher = mock.patch.object(module, 'logfunc', self.lines.append)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _seeker(self):
        data = tempfile.mkdtemp(prefix='peek_data_')
        self.addCleanup(shutil.rmtree, data, True)
        return data

    def test_peek_matches_search_and_stages_nothing(self):
        for stem, image in self.images.items():
            with self.subTest(image=stem):
                data = self._seeker()
                seeker = FileSeekerRaw(image, data)
                self.addCleanup(seeker.cleanup)
                peeked = seeker.peek('*', size=100)
                self.assertTrue(peeked)
                self.assertEqual(_files_in(data), [], 'peek wrote into the data folder')
                self.assertEqual(seeker.copied, {})
                self.assertEqual(seeker.file_infos, {})
                staged = {info.source_path: path for path, info in
                          ((path, seeker.file_infos.get(path)) for path in seeker.search('*'))
                          if info is not None and info.kind not in ('folder',)}
                by_path = {item.path: item for item in peeked}
                files = {path: staged_path for path, staged_path in staged.items() if os.path.isfile(staged_path)}
                self.assertEqual(sorted(by_path), sorted(files), 'peek and search name different files')
                for path, staged_path in files.items():
                    item = by_path[path]
                    with open(staged_path, 'rb') as handle:
                        whole = handle.read()
                    self.assertEqual(item.head, whole[:100], path)
                    self.assertEqual(item.size, len(whole), path)
                    recorded = seeker.file_infos[staged_path]
                    self.assertEqual((item.info.source_path, item.info.creation_date, item.info.modification_date,
                                      item.info.kind, item.info.times),
                                     (recorded.source_path, recorded.creation_date, recorded.modification_date,
                                      recorded.kind, recorded.times), path)
                self.assertTrue(any(line.startswith('Read the first ') for line in self.lines))

    def test_a_large_file_on_a_whole_file_reader_is_not_read(self):
        data = self._seeker()
        seeker = FileSeekerRaw(self.images['fat32-deleted'], data)
        self.addCleanup(seeker.cleanup)
        with mock.patch.object(FileSeekerRaw, 'WHOLE_FILE_PEEK_LIMIT', 0):
            peeked = [item for item in seeker.peek('*') if item.size]
        self.assertTrue(peeked)
        for item in peeked:
            self.assertIsNone(item.head)
            self.assertIn('reads whole files', item.note)

    def test_an_empty_file_gives_empty_bytes(self):
        data = self._seeker()
        seeker = FileSeekerRaw(self.images['ntfs-fixture'], data)
        self.addCleanup(seeker.cleanup)
        for item in seeker.peek('*'):
            if item.size == 0:
                self.assertEqual((item.head, item.note), (b'', ''))


class ArchivePeekTest(unittest.TestCase):
    def setUp(self):
        self.lines = []
        patcher = mock.patch.object(search_files, 'logfunc', self.lines.append)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.work = tempfile.mkdtemp(prefix='peek_inputs_')
        self.addCleanup(shutil.rmtree, self.work, True)
        self.data = os.path.join(self.work, 'data')
        os.makedirs(self.data)
        self.payload = {'root/disks/a.vhdx': b'vhdxfile' + b'A' * 200, 'root/other/b.txt': b'text'}

    def _check(self, seeker):
        peeked = seeker.peek('*.vhdx', size=12)
        self.assertEqual([(item.path.split('/')[-1], item.size, item.head, item.note) for item in peeked],
                         [('a.vhdx', 208, b'vhdxfileAAAA', '')])
        self.assertEqual(_files_in(self.data), [])
        self.assertTrue(seeker.search('*.vhdx'))
        self.assertEqual(len(_files_in(self.data)), 1)

    def test_folder(self):
        source = os.path.join(self.work, 'in')
        for name, raw in self.payload.items():
            path = os.path.join(source, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as handle:
                handle.write(raw)
        self._check(FileSeekerDir(source, self.data))

    def test_zip(self):
        path = os.path.join(self.work, 'in.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            for name, raw in self.payload.items():
                archive.writestr(name, raw)
        seeker = FileSeekerZip(path, self.data)
        self.addCleanup(seeker.cleanup)
        self._check(seeker)

    def test_tar(self):
        path = os.path.join(self.work, 'in.tar')
        with tarfile.open(path, 'w') as archive:
            for name, raw in self.payload.items():
                member = tarfile.TarInfo(name)
                member.size = len(raw)
                archive.addfile(member, io.BytesIO(raw))
        seeker = FileSeekerTar(path, self.data)
        self.addCleanup(seeker.cleanup)
        self._check(seeker)

    def test_single_file_refuses(self):
        path = os.path.join(self.work, 'a.vhdx')
        with open(path, 'wb') as handle:
            handle.write(b'vhdxfile')
        with self.assertRaises(PeekUnsupported):
            FileSeekerFile(path, self.data).peek('*.vhdx')


if __name__ == '__main__':
    unittest.main()
