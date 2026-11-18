"""The Jami artifact's git object reader against git itself.

Builds a throwaway repository with git, packs it so that most objects are stored as offset
deltas, adds loose objects after the pack, and checks that the reader returns every object git
lists, with the same type and content. A corrupted loose object must be refused, not returned.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
import zlib

from scripts.artifacts import jami


def _git(repo, *args, data=None):
    return subprocess.run(['git', '-C', repo, *args], input=data, capture_output=True, check=True,
                          env={**os.environ, 'GIT_AUTHOR_NAME': 'a', 'GIT_AUTHOR_EMAIL': 'a@b',
                               'GIT_COMMITTER_NAME': 'a', 'GIT_COMMITTER_EMAIL': 'a@b',
                               'GIT_AUTHOR_DATE': '1700000000 +0000',
                               'GIT_COMMITTER_DATE': '1700000000 +0000'}).stdout


def _files(repo):
    found = {}
    for root, _, names in os.walk(os.path.join(repo, '.git')):
        for name in names:
            path = os.path.join(root, name)
            found[os.path.relpath(path, repo).replace(os.sep, '/')] = path
    return found


@unittest.skipUnless(shutil.which('git'), 'git is not installed')
class JamiGitReaderTest(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        _git(self.repo, 'init', '-q')
        text = ''.join(f'line {n}\n' for n in range(400))
        for n in range(12):
            with open(os.path.join(self.repo, 'file.txt'), 'w', encoding='utf-8') as handle:
                handle.write(text + f'change {n}\n')
            _git(self.repo, 'add', 'file.txt')
            _git(self.repo, 'commit', '-q', '-m', f'{{"type":"text/plain","body":"{n}"}}')
        _git(self.repo, 'repack', '-adfq', '--depth=20', '--window=20')
        _git(self.repo, 'commit', '-q', '--allow-empty', '-m', 'loose')

    def test_every_object_matches_git(self):
        objects = jami._GitObjects(_files(self.repo))  # pylint: disable=protected-access
        listed = _git(self.repo, 'cat-file', '--batch-all-objects',
                      '--batch-check=%(objectname) %(objecttype)').decode().split('\n')
        expected = dict(line.split() for line in listed if line)
        self.assertEqual(objects.names(), set(expected))
        for name, kind in expected.items():
            found = objects.get(name)
            self.assertIsNotNone(found, name)
            self.assertEqual(found[0].decode(), kind)
            self.assertEqual(found[1], _git(self.repo, 'cat-file', kind, name))
        self.assertEqual(objects.bad, 0)

    def test_offset_deltas_were_exercised(self):
        verify = _git(self.repo, 'verify-pack', '-v',
                      *[os.path.join(self.repo, '.git/objects/pack', name)
                        for name in os.listdir(os.path.join(self.repo, '.git/objects/pack'))
                        if name.endswith('.idx')]).decode()
        self.assertTrue(any(len(line.split()) >= 7 for line in verify.split('\n')
                            if line[:40].strip()), 'the pack holds no deltas')

    def test_a_corrupted_loose_object_is_refused(self):
        files = _files(self.repo)
        name = _git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        path = files[f'.git/objects/{name[:2]}/{name[2:]}']
        with open(path, 'rb') as handle:
            raw = zlib.decompress(handle.read())
        os.chmod(path, 0o644)
        with open(path, 'wb') as handle:
            handle.write(zlib.compress(raw.replace(b'loose', b'lOose')))
        objects = jami._GitObjects(files)  # pylint: disable=protected-access
        self.assertIsNone(objects.get(name))
        self.assertEqual(objects.bad, 1)


if __name__ == '__main__':
    unittest.main()
