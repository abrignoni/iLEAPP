"""Pin how the directory seeker treats symbolic links in a folder input.

A folder made by extracting a tar or copying a live system keeps the links the
device had, and many of them are absolute (etc/localtime pointing into
/usr/share/zoneinfo, var/lib/dbus/machine-id pointing to /etc/machine-id). The
directory seeker followed every link when it staged a match, so an absolute link
resolved on the examiner's machine and the examiner's own file was staged into the
case under the evidence path, with that file's times. A relative link that climbs
out of the input folder did the same.

The seeker now stages a link's target only when the target, with every link on the
way resolved, is inside the input folder. Any other link is still returned, so an
artifact can report the link (Linux System Information reads its target text), but
nothing is staged at its path and file_infos holds the link's own times.

These tests build a tree with a link that stays inside, a link that climbs out and
comes back in, an absolute link to a file outside, a relative link that climbs out,
a link inside that points to the absolute one and an absolute link to a folder
outside. They check what is staged, what is returned, what file_infos records and
what is logged, for each form the input path can take. The files outside stand in
for ones on the examiner's machine, and their folder's name begins with the input
folder's name, so a check by string prefix would take them for the inside.
"""
import contextlib
import io
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileSeekerDir  # pylint: disable=wrong-import-position

EVIDENCE = b'NAME="evidence os-release"\n'
HOSTNAME = b'evidence-host\n'
EXAMINER = b'a file on the examiner machine, never evidence\n'
EXAMINER_MTIME = 1000
PATTERN = '*/etc/*'
STAGED = ['etc/back_in', 'etc/hostname', 'etc/os-release']
OUTSIDE = {
    'etc/localtime': 'examiner_file',
    'etc/climb': 'examiner_file',
    'etc/chain': 'localtime',
    'etc/dir_outside': 'examiner_dir',
}


class TestDirectorySeekerLinks(unittest.TestCase):
    """A link's target is staged only when it resolves inside the input folder."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_links_')
        self.root = os.path.join(self.tmp, 'extraction')
        outside = os.path.join(self.tmp, 'extraction_examiner')
        os.makedirs(os.path.join(outside, 'examiner_dir'))
        examiner_file = os.path.join(outside, 'examiner_file')
        with open(examiner_file, 'wb') as fout:
            fout.write(EXAMINER)
        os.utime(examiner_file, (EXAMINER_MTIME, EXAMINER_MTIME))
        with open(os.path.join(outside, 'examiner_dir', 'inner'), 'wb') as fout:
            fout.write(EXAMINER)
        etc = os.path.join(self.root, 'etc')
        lib = os.path.join(self.root, 'usr', 'lib')
        os.makedirs(etc)
        os.makedirs(lib)
        with open(os.path.join(lib, 'os-release'), 'wb') as fout:
            fout.write(EVIDENCE)
        with open(os.path.join(etc, 'hostname'), 'wb') as fout:
            fout.write(HOSTNAME)
        links = (
            ('os-release', os.path.join('..', 'usr', 'lib', 'os-release'), False),
            ('back_in', os.path.join('..', '..', 'extraction', 'usr', 'lib', 'os-release'), False),
            ('localtime', examiner_file, False),
            ('climb', os.path.join('..', '..', 'extraction_examiner', 'examiner_file'), False),
            ('chain', 'localtime', False),
            ('dir_outside', os.path.join(outside, 'examiner_dir'), True),
        )
        try:
            for name, target, is_dir in links:
                os.symlink(target, os.path.join(etc, name), target_is_directory=is_dir)
        except (OSError, NotImplementedError) as ex:
            shutil.rmtree(self.tmp, ignore_errors=True)
            self.skipTest(f'this account cannot create symbolic links: {ex}')
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _check_directory_input(self, label, directory):
        data_folder = os.path.join(self.tmp, 'data_' + label)
        os.makedirs(data_folder)
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            seeker = FileSeekerDir(directory, data_folder)
            found = seeker.search(PATTERN)
            single = seeker.search('*/etc/localtime')
        by_rel = {os.path.relpath(p, data_folder).replace(os.sep, '/'): p for p in found}
        self.assertEqual(sorted(by_rel), sorted(STAGED + list(OUTSIDE)), label)
        self.assertEqual(single, [by_rel['etc/localtime']], label)
        for rel in STAGED:
            staged = by_rel[rel]
            self.assertEqual(seeker.file_infos[staged].source_path, rel, label)
            with open(staged, 'rb') as fin:
                self.assertEqual(fin.read(), HOSTNAME if rel == 'etc/hostname' else EVIDENCE,
                                 (label, rel))
        for rel in OUTSIDE:
            path = by_rel[rel]
            self.assertFalse(os.path.lexists(path), (label, rel))
            info = seeker.file_infos[path]
            self.assertEqual(info.source_path, rel, (label, rel))
            link_mtime = os.lstat(os.path.join(self.root, *rel.split('/'))).st_mtime
            self.assertEqual(info.modification_date, link_mtime, (label, rel))
            self.assertNotEqual(info.modification_date, EXAMINER_MTIME, (label, rel))
        on_disk = []
        for folder, _dirs, files in os.walk(data_folder):
            for name in files:
                with open(os.path.join(folder, name), 'rb') as fin:
                    self.assertNotEqual(fin.read(), EXAMINER, (label, folder, name))
                on_disk.append(os.path.relpath(os.path.join(folder, name), data_folder)
                               .replace(os.sep, '/'))
        self.assertEqual(sorted(on_disk), STAGED, label)
        lines = [line for line in log.getvalue().splitlines() if line.startswith('INFO: Link ')]
        self.assertEqual(len(lines), len(OUTSIDE), (label, lines))
        for rel, target_name in OUTSIDE.items():
            named = [line for line in lines if line.startswith(f"INFO: Link '{rel}' points to '")]
            self.assertEqual(len(named), 1, (label, rel, lines))
            self.assertIn(target_name, named[0], (label, rel))
            self.assertNotIn(EXAMINER.decode(), named[0], (label, rel))

    def test_absolute_directory_input(self):
        self._check_directory_input('absolute', self.root)

    def test_directory_input_with_a_trailing_separator(self):
        self._check_directory_input('trailing', self.root + os.sep)

    def test_relative_directory_input(self):
        os.chdir(self.tmp)
        self._check_directory_input('relative', 'extraction')

    def test_dot_as_the_directory_input(self):
        os.chdir(self.root)
        self._check_directory_input('dot', '.')

    @unittest.skipUnless(os.name == 'nt', 'the extended-length prefix is a Windows path form')
    def test_extended_length_prefix_on_windows(self):
        prefixed = '\\\\?\\' + self.root.replace('/', '\\')
        self._check_directory_input('prefixed', prefixed)
        self._check_directory_input('prefixed_trailing', prefixed + '\\')

    def test_a_file_that_folds_onto_an_outside_link_gets_its_own_path(self):
        # On a data folder that folds case, nothing may be staged at the path returned
        # for an outside link, so a file named like it but for case is written elsewhere.
        try:
            with open(os.path.join(self.root, 'etc', 'LOCALTIME'), 'xb') as fout:
                fout.write(EVIDENCE)
        except FileExistsError:
            self.skipTest('the input folder folds case, so it cannot hold both names')
        data_folder = os.path.join(self.tmp, 'data_folds')
        with mock.patch('scripts.search_files._probe_volume_case_insensitive',
                        return_value=True), contextlib.redirect_stdout(io.StringIO()):
            seeker = FileSeekerDir(self.root, data_folder)
            found = seeker.search('*/etc/[lL][oO][cC][aA][lL][tT][iI][mM][eE]')
        by_source = {seeker.file_infos[p].source_path: p for p in found}
        self.assertEqual(sorted(by_source), ['etc/LOCALTIME', 'etc/localtime'])
        link_path, file_path = by_source['etc/localtime'], by_source['etc/LOCALTIME']
        self.assertNotEqual(os.path.normcase(link_path).casefold(),
                            os.path.normcase(file_path).casefold())
        self.assertFalse(os.path.lexists(link_path))
        with open(file_path, 'rb') as fin:
            self.assertEqual(fin.read(), EVIDENCE)


if __name__ == '__main__':
    unittest.main()
