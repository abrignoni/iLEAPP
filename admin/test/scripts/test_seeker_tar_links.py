"""Pin how the tar seeker stages a hard or symbolic link member.

A hard link member stores no data of its own and a symbolic link only its target's
name. The seeker read each as itself and staged an empty file at the link's name,
which an artifact matching that name was then handed. Now a link is read as the
member it points to, as the folder seeker reads a link that stays inside the input:
a link to a file stages that file's bytes, a link to a folder stages a folder, and a
link whose target the archive does not hold is logged and not staged.

The archives are built here with tarfile, plain and gzip compressed. Every expected
value is written out as a literal.
"""
import io
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerTar  # pylint: disable=wrong-import-position


class TestTarLinks(unittest.TestCase):
    """One archive holding each kind of link, one seeker; then the same archive gzipped."""

    # (name, type, content or link target) in archive order
    ENTRIES = (
        ('data/dir', tarfile.DIRTYPE, None),
        ('data/dir/real.db', tarfile.REGTYPE, b'SQLite format 3\x00REALDATA'),
        ('data/hard.db', tarfile.LNKTYPE, 'data/dir/real.db'),
        ('data/hdir', tarfile.LNKTYPE, 'data/dir'),
        ('data/sym.db', tarfile.SYMTYPE, 'dir/real.db'),
        ('data/symdir', tarfile.SYMTYPE, 'dir'),
        ('data/dangling.db', tarfile.SYMTYPE, '/system/elsewhere.db'),
        ('data/hgone.db', tarfile.LNKTYPE, 'data/missing.db'),
    )

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_tar_links_')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.paths = []
        for name, mode in (('links.tar', 'w'), ('links.tar.gz', 'w:gz')):
            path = os.path.join(self.tmp, name)
            with tarfile.open(path, mode) as archive:
                for member, kind, value in self.ENTRIES:
                    info = tarfile.TarInfo(member)
                    info.type = kind
                    info.mtime = 1_600_000_000
                    if kind == tarfile.REGTYPE:
                        info.size = len(value)
                        archive.addfile(info, io.BytesIO(value))
                    else:
                        if value is not None:
                            info.linkname = value
                        archive.addfile(info)
            self.paths.append(path)

    def _seeker(self, path):
        out = tempfile.mkdtemp(dir=self.tmp)
        log = []
        with mock.patch.object(search_files, 'logfunc', log.append):
            seeker = FileSeekerTar(path, out)
        self.addCleanup(seeker.cleanup)
        return seeker, log

    def test_each_kind_of_link(self):
        for path in self.paths:
            with self.subTest(archive=os.path.basename(path)):
                seeker, log = self._seeker(path)
                with mock.patch.object(search_files, 'logfunc', log.append):
                    staged = {os.path.relpath(p, seeker.data_folder).replace(os.sep, '/'): p
                              for p in seeker.search('*/data/*')}
                real = b'SQLite format 3\x00REALDATA'
                for name in ('data/dir/real.db', 'data/hard.db', 'data/sym.db'):
                    with open(staged[name], 'rb') as handle:
                        self.assertEqual(handle.read(), real, name)
                    self.assertEqual(seeker.file_infos[staged[name]].source_path, name)
                # a link to a folder is a folder, not an empty file
                for name in ('data/hdir', 'data/symdir'):
                    self.assertTrue(os.path.isdir(staged[name]), name)
                    self.assertNotIn(staged[name], seeker.file_infos)
                # a target the archive does not hold is said, and nothing is staged
                self.assertNotIn('data/dangling.db', staged)
                self.assertNotIn('data/hgone.db', staged)
                said = [line for line in log if line.startswith("INFO: Link '")]
                self.assertEqual(said, [
                    "INFO: Link 'data/dangling.db' points to '/system/elsewhere.db', which "
                    "is not in the archive. Its target was not staged.",
                    "INFO: Link 'data/hgone.db' points to 'data/missing.db', which is not "
                    "in the archive. Its target was not staged."])


if __name__ == '__main__':
    unittest.main()
