"""Pin what --hash records for a staged file, from each kind of input.

A file's digest is a statement about the evidence only when the staged copy holds
what the evidence holds under that name. So a regular file must hash the same
whether it came from a folder, a tar or a zip, and a link, which every seeker now
stages as its target's bytes, is recorded by kind with no digest: its digest would
be its target's, said under the link's name. With hashing off nothing is hashed and
the kind is still recorded. The inputs are built here; every expected value is a
literal or a digest of the bytes written.
"""
import hashlib
import os
import pathlib
import shutil
import stat
import sys
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import ileapp  # pylint: disable=wrong-import-position
import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.search_files import (  # pylint: disable=wrong-import-position
    FileInfo, FileSeekerDir, FileSeekerTar, FileSeekerZip)

CONTENT = b'SQLite format 3\x00' + bytes(range(256)) * 20


class TestHashStagedFiles(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_hash_staged_')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        src = os.path.join(self.tmp, 'src')
        os.makedirs(os.path.join(src, 'data', 'app', 'databases'))
        with open(os.path.join(src, 'data', 'app', 'databases', 'real.db'), 'wb') as handle:
            handle.write(CONTENT)
        os.symlink('real.db', os.path.join(src, 'data', 'app', 'databases', 'link.db'))
        self.src = src
        self.tar = os.path.join(self.tmp, 'in.tar')
        with tarfile.open(self.tar, 'w') as archive:
            archive.add(os.path.join(src, 'data'), arcname='data')
        self.zip = os.path.join(self.tmp, 'in.zip')
        with zipfile.ZipFile(self.zip, 'w') as archive:
            archive.write(os.path.join(src, 'data', 'app', 'databases', 'real.db'),
                          'data/app/databases/real.db')
            info = zipfile.ZipInfo('data/app/databases/link.db')
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, 'real.db')
        self.want = hashlib.sha256(CONTENT).hexdigest()

    def _records(self, make, hash_files=True):
        out = tempfile.mkdtemp(dir=self.tmp)
        with mock.patch.object(search_files, 'logfunc', lambda *_a, **_k: None):
            seeker = make(out)
            found = seeker.search('*/databases/*')
        self.addCleanup(getattr(seeker, 'cleanup', lambda: None))
        records = {}
        for path in found:
            info = seeker.file_infos.get(path)
            if info is None:
                continue
            records[info.source_path.rsplit('/', 1)[-1]] = ileapp.staged_file_record(
                seeker, path, info, hash_files)
        return records

    def test_a_file_hashes_the_same_from_every_input_and_a_link_has_no_digest(self):
        for label, make in (('folder', lambda out: FileSeekerDir(self.src, out)),
                            ('tar', lambda out: FileSeekerTar(self.tar, out)),
                            ('zip', lambda out: FileSeekerZip(self.zip, out))):
            with self.subTest(input=label):
                records = self._records(make)
                self.assertEqual(records['real.db'], (self.want, 'file'))
                self.assertEqual(records['link.db'], (None, 'link'))

    def test_with_hashing_off_the_kind_is_still_recorded(self):
        records = self._records(lambda out: FileSeekerTar(self.tar, out), hash_files=False)
        self.assertEqual(records, {'real.db': (None, 'file'), 'link.db': (None, 'link')})

    def test_a_staged_file_is_hashed_once(self):
        staged = os.path.join(self.tmp, 'once.bin')
        with open(staged, 'wb') as handle:
            handle.write(b'first')
        info = FileInfo('evidence/once.bin', 0, 0)
        seeker = mock.Mock(spec=[])
        first = ileapp.staged_file_record(seeker, staged, info, True)
        with open(staged, 'wb') as handle:
            handle.write(b'changed later, by an artifact opening it')
        self.assertEqual(ileapp.staged_file_record(seeker, staged, info, True), first)
        self.assertEqual(first, (hashlib.sha256(b'first').hexdigest(), 'file'))

    def test_a_file_read_with_zeros_says_so_in_its_kind(self):
        staged = os.path.join(self.tmp, 'padded.bin')
        with open(staged, 'wb') as handle:
            handle.write(bytes(10))
        seeker = mock.Mock(spec=['padded_files'])
        seeker.padded_files = {staged: 10}
        digest, kind = ileapp.staged_file_record(seeker, staged, FileInfo('x', 0, 0), True)
        self.assertEqual(digest, hashlib.sha256(bytes(10)).hexdigest())
        self.assertEqual(kind, "file; read with zeros where the acquisition's data ran out")

    def test_a_decrypted_backup_file_is_hashed_and_labelled(self):
        # an encrypted iTunes backup's file is staged as its plaintext: the digest is
        # of the plaintext, and the kind keeps it from reading as the backup's bytes
        staged = os.path.join(self.tmp, 'plain.db')
        with open(staged, 'wb') as handle:
            handle.write(CONTENT)
        info = FileInfo('HomeDomain/Library/plain.db', 0, 0, kind='decrypted file')
        self.assertEqual(ileapp.staged_file_record(mock.Mock(spec=[]), staged, info, True),
                         (self.want, 'decrypted file'))

    def test_kinds_that_are_not_hashed(self):
        staged = os.path.join(self.tmp, 'folder')
        os.makedirs(staged)
        for kind in ('folder', 'link', 'link outside the input'):
            info = FileInfo('x', 0, 0, kind=kind)
            self.assertEqual(ileapp.staged_file_record(mock.Mock(spec=[]), staged, info, True),
                             (None, kind))


if __name__ == '__main__':
    unittest.main()
