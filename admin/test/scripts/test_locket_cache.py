"""Locket cache regression cases. cache.zip contains synthetic LevelDB log records only
and synthetic app/group marker and friends files. It exercises two independent stores,
a put followed by a deletion, a no-document observation, and two candidate user profiles.
"""
import datetime
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts import locket  # pylint: disable=wrong-import-position


class LocketCacheTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        with zipfile.ZipFile(ROOT / 'admin/test/fixtures/locket/cache.zip') as fixture:
            fixture.extractall(self.root)
        self.context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in self.root.rglob('*') if p.is_file()],
            get_relative_path=lambda path: Path(path).relative_to(self.root).as_posix())

    def rows(self, artifact):
        headers, rows, _ = artifact.__wrapped__(self.context)
        columns = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(columns, row, strict=True)) for row in rows]

    def test_scoped_owner_and_missing_sender(self):
        self.assertEqual([r['UID'] for r in self.rows(locket.locketAccount)], ['owner'])
        self.assertEqual(self.rows(locket.locketFriends)[0]['In Friends Collection'], 'Yes')
        directions = {r['Moment ID']: r['Direction'] for r in self.rows(locket.locketMoments)}
        self.assertEqual(directions, {'own': 'Sent', 'unknown': 'Unknown'})

    def test_lone_profile_and_conflicting_owner_paths_are_inconclusive(self):
        # pylint: disable=protected-access
        files = locket._locket_files(self.context)
        docs = locket._firestore_documents(files)
        contact = next(doc for doc in docs if doc.parts == ('users', 'contact'))
        self.assertEqual(locket._account_uid([contact]), '')
        conflicting = locket._Document(('history', 'contact', 'entries', 'x'), True, {}, None, contact.source)
        with patch.object(locket, '_firestore_documents', return_value=[*docs, conflicting]):
            self.assertEqual(self.rows(locket.locketAccount), [])
            self.assertEqual(self.rows(locket.locketFriends)[0]['In Friends Collection'], 'Unknown')
            self.assertEqual({r['Direction'] for r in self.rows(locket.locketMoments)}, {'Unknown'})

    def test_absence_has_observation_time_only(self):
        row, = self.rows(locket.locketFriendRequests)
        self.assertIsNone(row['Created'])
        self.assertEqual(row['State'], 'Observed Absent')
        self.assertEqual(row['Observed Absent'], datetime.datetime.fromtimestamp(1700000000, datetime.timezone.utc))
        self.assertEqual(row['Event Time'], row['Observed Absent'])

    def test_deleted_message_and_independent_stores(self):
        rows = self.rows(locket.locketMessages)
        self.assertEqual([r['Message ID'] for r in rows], ['shared', 'shared'])
        self.assertEqual({r['Body'] for r in rows}, {'first store', 'second store'})
        self.assertEqual(len({r['Source File'] for r in rows}), 2)
        for row in rows:
            self.assertTrue(row['Source File'].endswith('/000002.log'))
            self.assertFalse(Path(row['Source File']).is_absolute())

    def test_logs_remain_readable_without_current(self):
        before = self.rows(locket.locketMessages)
        for marker in self.root.rglob('CURRENT'):
            marker.unlink()
        with patch.object(locket, 'logfunc') as log:
            self.assertEqual(self.rows(locket.locketMessages), before)
        self.assertTrue(any('CURRENT missing' in str(call) for call in log.call_args_list))


if __name__ == '__main__':
    unittest.main()
