"""Cover the two sysdiagnose archive names that get_sysdiagnose_files() reads.

An archive is read whether its name holds sysdiagnose_ (sysdiagnose_<date>_<platform>_<model>_<build>.tar.gz)
or ends in _sysdiagnose.tar.gz (<device identifier>_sysdiagnose.tar.gz, seen on a corpus archive). Before
the second form was accepted, such an archive was never opened: no artifact glob matched it and the helper
did not treat it as an archive. Every artifact that declares one form must declare the other, or an
archive saved under the second name reaches none of them. The identifier below is invented.
"""
import ast
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

from scripts.ilapfuncs import get_sysdiagnose_files, is_sysdiagnose_archive  # pylint: disable=wrong-import-position

SD = 'sysdiagnose_2026.01.02_03-04-05-0500_iPhone-OS_iPhone_23A000'
SAVED = '00008110-0000000000000000_sysdiagnose.tar.gz'
INNER = f'{SD}/WiFi/com.apple.wifi.plist'
OLD_GLOB = '*/sysdiagnose_*.tar.gz'
NEW_GLOB = '*/*_sysdiagnose.tar.gz'


def _make_archive(directory, name):
    path = os.path.join(directory, name)
    with tarfile.open(path, 'w:gz') as tar:
        data = b'archive member\n'
        info = tarfile.TarInfo(INNER)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return path


class ArchiveNames(unittest.TestCase):

    def test_names_read_as_an_archive(self):
        for name in (f'{SD}.tar.gz', SAVED, '00008110-0000000000000000_sysdiagnose.tar',
                     f'/evidence/folder/{SAVED}'):
            with self.subTest(name=name):
                self.assertTrue(is_sysdiagnose_archive(name))

    def test_names_not_read_as_an_archive(self):
        for name in (f'IN_PROGRESS_{SD}.tar.gz', 'IN_PROGRESS_00008110_sysdiagnose.tar.gz',
                     'sysdiagnose_process_tree.png', 'notes_sysdiagnose.txt', 'backup.tar.gz',
                     'sysdiagnose.tar.gz.part'):
            with self.subTest(name=name):
                self.assertFalse(is_sysdiagnose_archive(name))

    def test_a_member_of_an_archive_saved_under_an_identifier_is_yielded(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in (f'{SD}.tar.gz', SAVED):
                with self.subTest(name=name):
                    path = _make_archive(tmp, name)
                    found = [(stream.read(), source) for stream, source in
                             get_sysdiagnose_files([path], re.compile(r'com\.apple\.wifi\.plist$'),
                                                   text_mode=False)]
                    self.assertEqual(found, [(b'archive member\n', f'{path} >> {INNER}')])


class EveryArtifactDeclaresBothNames(unittest.TestCase):

    def test_both_globs_together(self):
        missing = []
        for path in sorted((REPO_ROOT / 'scripts' / 'artifacts').glob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in tree.body:
                if not (isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == '__artifacts_v2__'):
                    continue
                for key, block in ast.literal_eval(node.value).items():
                    paths = block.get('paths') or ()
                    if isinstance(paths, str):
                        paths = (paths,)
                    if (OLD_GLOB in paths) != (NEW_GLOB in paths):
                        missing.append(f'{path.name}:{key}')
        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()
