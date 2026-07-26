"""Guard the CloudKit artifacts against NoteStore.sqlite files that carry no schema.

iOS keeps zero-byte NoteStore.sqlite placeholders under
group.com.apple.notes/Backups/<date>/, and the artifact's '*NoteStore.sqlite*' path
glob matches them. sqlite3 opens a zero-byte file happily as an empty database, so the
first SELECT raised `no such table: ZICCLOUDSYNCINGOBJECT` and aborted both artifacts
before the real NoteStore.sqlite in the same extraction was ever read - the examiner got
no CloudKit shares at all, only a parsing error in the log. Deleting the backup files by
hand was the only workaround.

scripts/artifacts/notes.py already guards its own queries with does_table_exist_in_db();
these tests hold cloudkitSharing.py to the same contract.
"""
import pathlib
import sqlite3
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.cloudkitSharing import (  # pylint: disable=wrong-import-position
    cloudkit_participants, cloudkit_sharing)
from scripts.context import Context  # pylint: disable=wrong-import-position


class TestCloudkitSharingMissingTable(unittest.TestCase):
    """A NoteStore.sqlite without ZICCLOUDSYNCINGOBJECT must be skipped, not fatal."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.empty_db = pathlib.Path(self.tmpdir) / 'Backups' / '2026-07-18' / 'NoteStore.sqlite'
        self.empty_db.parent.mkdir(parents=True)
        self.empty_db.touch()  # the zero-byte placeholder iOS leaves behind

        self.populated_db = pathlib.Path(self.tmpdir) / 'NoteStore.sqlite'
        db = sqlite3.connect(self.populated_db)
        db.execute('CREATE TABLE ZICCLOUDSYNCINGOBJECT '
                   '(Z_PK INTEGER, ZIDENTIFIER TEXT, ZSERVERRECORDDATA BLOB, '
                   'ZSERVERSHAREDATA BLOB)')
        db.commit()
        db.close()

        Context.clear()
        Context.set_report_folder(self.tmpdir)
        Context.set_files_found([str(self.empty_db), str(self.populated_db)])

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_zero_byte_notestore_really_has_no_table(self):
        """Documents the trap: the placeholder opens fine, then the SELECT fails."""
        db = sqlite3.connect(f'file:{self.empty_db}?mode=ro', uri=True)
        with self.assertRaises(sqlite3.OperationalError):
            db.execute('SELECT Z_PK FROM ZICCLOUDSYNCINGOBJECT')
        db.close()

    def test_sharing_skips_notestore_without_the_table(self):
        _headers, data_list, _source = cloudkit_sharing.__wrapped__(Context)
        self.assertEqual(data_list, [])

    def test_participants_skips_notestore_without_the_table(self):
        _headers, data_list, _source = cloudkit_participants.__wrapped__(Context)
        self.assertEqual(data_list, [])


if __name__ == '__main__':
    unittest.main()
