"""PotatoChat finds its versioned tables, and a store missing one reports no rows.

The table names carry a version suffix, so each artifact looked them up with next() on a
sqlite_master query. A store without the table raised StopIteration and stopped the
artifact. The conversations lookup also ended in "OR 'conversations_v__'", a bare string
SQLite reads as false, so only the legacy spelling convesations_v__ could ever match.
"""
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock

from scripts.artifacts import potatoChat
from scripts.context import Context


class PotatoChatTableLookupTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        documents = os.path.join(self.tmpdir, 'private/var/mobile/Containers/Shared/AppGroup/A/Documents')
        os.makedirs(documents)
        self.path = os.path.join(documents, 'tgdata.db')
        Context.clear()
        Context.set_data_folder(self.tmpdir)
        patcher = mock.patch.object(potatoChat, 'logfunc', create=True)
        self.log = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def store(self, *tables):
        db = sqlite3.connect(self.path)
        for table in tables:
            db.execute(f'CREATE TABLE {table} (x)')
        db.commit()
        db.close()

    def test_both_spellings_of_the_conversations_table_are_found(self):
        self.store('conversations_v29')
        self.assertEqual(potatoChat._table_name(self.path, 'convesations_v__', 'conversations_v__'),  # pylint: disable=protected-access
                         'conversations_v29')
        os.remove(self.path)
        self.store('convesations_v29')
        self.assertEqual(potatoChat._table_name(self.path, 'convesations_v__', 'conversations_v__'),  # pylint: disable=protected-access
                         'convesations_v29')

    def test_a_store_without_its_tables_reports_no_rows(self):
        self.store('unrelated')
        Context.set_files_found([self.path])
        for artifact in (potatoChat.potatochat_chats, potatoChat.potatochat_users,
                         potatoChat.potatochat_group_chats):
            headers, rows, _ = artifact.__wrapped__(Context)
            self.assertEqual(rows, [], artifact.__name__)
            self.assertTrue(headers, artifact.__name__)
        self.assertTrue(any('no messages table' in c.args[0] for c in self.log.call_args_list))


if __name__ == '__main__':
    unittest.main()
