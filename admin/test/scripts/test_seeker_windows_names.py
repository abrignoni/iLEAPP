"""Stage archive members whose names Windows treats specially, and check each one survives.

Before a seeker writes a member into the report's data folder it passes the name
through sanitize_file_path, which replaces the characters Windows forbids. Two kinds of
name get through unchanged and are still special on Windows: reserved device names
(CON, PRN, AUX, NUL, COM1 to COM9 and LPT1 to LPT9, with or without an extension), and
names ending in a dot or a space, which an ordinary Windows path drops. Registered
extractions carry both: AUX and aux.dat on 15 of 63 corpora, and names ending in a dot
or a space, such as the CleverTap SDK's app_CleverTap.Files. folder, on 16.

Here the tar and the zip seeker stage one member of each kind, plus an ordinary one,
into a data folder given as an ordinary path and, on Windows, two more ways: with the
extended-length prefix the entry points add for an output folder on a drive letter, and
through the drive's administrative share (\\\\localhost\\C$), which stands in for a
report on a network share, where the entry points add no prefix. Every member is
staged before any is read back, so a member written over another shows up as the wrong
bytes. Each must come back from its own search as its own file holding its own bytes.
The failure message says what happened to every member, so a Windows run shows which
names Windows turned into something else. Elsewhere these names are ordinary and the
test guards the same property. The same file runs in all five LEAPP cores.
"""
import io
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerTar, FileSeekerZip  # pylint: disable=wrong-import-position

# Every content differs, so a member that lands on another member's file reads wrong.
MEMBERS = {
    'ok/plain.txt': b'PLAIN',
    'dev/AUX': b'AUX WITHOUT AN EXTENSION',
    'dev/aux.dat': b'AUX WITH AN EXTENSION',
    'dev/CON': b'CON WITHOUT AN EXTENSION',
    'dev/nul.txt': b'NUL WITH AN EXTENSION',
    'dev/COM1.log': b'COM1 WITH AN EXTENSION',
    'dev/LPT1': b'LPT1 WITHOUT AN EXTENSION',
    'app_CleverTap.Files./cached.bin': b'INSIDE A FOLDER ENDING IN A DOT',
    'pair/name.': b'NAME ENDING IN A DOT',
    'pair/name': b'NAME WITHOUT THE DOT',
    'space/name ': b'NAME ENDING IN A SPACE',
}


def _extended(path):
    """The extended-length form the entry points use on Windows."""
    return '\\\\?\\' + os.path.abspath(path).replace('/', '\\')


def _share(path):
    """The same folder reached through its drive's administrative share."""
    full = os.path.abspath(path)
    return '\\\\localhost\\' + full[0] + '$' + full[2:]


class TestWindowsSpecialMemberNames(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_windows_names_')
        # A file named like aux.dat cannot be removed through an ordinary Windows path.
        self.addCleanup(shutil.rmtree, _extended(self.tmp) if os.name == 'nt' else self.tmp, True)
        self.tar_path = os.path.join(self.tmp, 'names.tar')
        with tarfile.open(self.tar_path, 'w') as archive:
            for name, content in MEMBERS.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mtime = 1000
                archive.addfile(info, io.BytesIO(content))
        self.zip_path = os.path.join(self.tmp, 'names.zip')
        with zipfile.ZipFile(self.zip_path, 'w') as archive:
            for name, content in MEMBERS.items():
                archive.writestr(name, content)

    def _data_folder(self, label, form):
        report = os.path.join(self.tmp, label)
        os.makedirs(report)
        data = os.path.join(report, 'data')
        if form == 'extended':
            return _extended(data)
        if form == 'share':
            if not os.path.isdir(_share(report)):
                self.skipTest(f'the administrative share {_share(report)[:15]}... is not reachable here')
            return _share(data)
        return data

    def _check(self, seeker_class, archive, data):
        """Stage every member, then read every one back; return what went wrong, by member."""
        log = []
        staged = {}
        with mock.patch.object(search_files, 'logfunc', side_effect=log.append):
            seeker = seeker_class(archive, data)
            try:
                for name in MEMBERS:
                    staged[name] = seeker.search('*/' + name)
            finally:
                seeker.cleanup()
        problems = {}
        for name, content in MEMBERS.items():
            found = staged[name]
            if len(found) != 1:
                problems[name] = f'search returned {len(found)} paths'
                continue
            try:
                with open(found[0], 'rb') as handle:
                    held = handle.read()
            except OSError as ex:
                problems[name] = f'staged as {os.path.basename(found[0])!r} but unreadable ({type(ex).__name__})'
                continue
            if held != content:
                other = next((n for n, c in MEMBERS.items() if c == held), None)
                problems[name] = (f'staged as {os.path.basename(found[0])!r} but holds '
                                  + (f'the bytes of {other!r}' if other else f'{len(held)} other bytes'))
        return problems, [m for m in log if 'Could not' in m]

    def _assert_all_survive(self, seeker_class, archive, form):
        data = self._data_folder(f'{seeker_class.__name__}_{form}', form)
        problems, log = self._check(seeker_class, archive, data)
        report = '\n'.join(f'  {name!r}: {what}' for name, what in problems.items())
        self.assertEqual(problems, {}, f'\n{seeker_class.__name__}, {form} data folder:\n{report}\n'
                         f'log: {log}')

    def test_tar_members_in_an_ordinary_folder(self):
        self._assert_all_survive(FileSeekerTar, self.tar_path, 'ordinary')

    def test_zip_members_in_an_ordinary_folder(self):
        self._assert_all_survive(FileSeekerZip, self.zip_path, 'ordinary')

    @unittest.skipUnless(os.name == 'nt', 'the extended-length prefix is a Windows path form')
    def test_tar_members_in_an_extended_length_folder(self):
        self._assert_all_survive(FileSeekerTar, self.tar_path, 'extended')

    @unittest.skipUnless(os.name == 'nt', 'the extended-length prefix is a Windows path form')
    def test_zip_members_in_an_extended_length_folder(self):
        self._assert_all_survive(FileSeekerZip, self.zip_path, 'extended')

    @unittest.skipUnless(os.name == 'nt', 'an administrative share is a Windows path form')
    def test_tar_members_in_a_folder_on_a_share(self):
        self._assert_all_survive(FileSeekerTar, self.tar_path, 'share')

    @unittest.skipUnless(os.name == 'nt', 'an administrative share is a Windows path form')
    def test_zip_members_in_a_folder_on_a_share(self):
        self._assert_all_survive(FileSeekerZip, self.zip_path, 'share')


if __name__ == '__main__':
    unittest.main()
