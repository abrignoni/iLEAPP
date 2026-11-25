"""Google Tasks reads tasks.db only from containers whose metadata plist names a Google app.

The store sits at three relative paths across Keep, Gmail, Google Chat and Calendar
containers. These tests pin the path globs against each shape and a decoy, the container
scoping (Google identifier read, other identifier and missing plist skipped), the App and
Account Folder columns, and the field 9 time and zone decode.
"""
import fnmatch
import pathlib
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import blackboxprotobuf  # pylint: disable=wrong-import-position
from scripts.artifacts.googleTasks import __artifacts_v2__, googleTasks  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

META = '.com.apple.mobile_container_manager.metadata.plist'
VAR = '/private/var/mobile/Containers'
SHAPES = {
    'app': 'Data/Application/{c}/Library/Application Support/Tasks/{a}/tasks.db',
    'group': 'Shared/AppGroup/{c}/tasks/{a}_tdl/tasks.db',
    'calendar': 'Shared/AppGroup/{c}/Library/Application Support/Tasks/tasks/{a}/tasks.db',
}
TASK = {
    '2': {'3': b'Task title'},
    '3': {'1': 1700000001, '2': 0},
    '9': {'1': {'4': b'Europe/Lisbon', '6': {'1': 1700003600}}},
    '11': {'1': 1700000000, '2': 0},
}
TASK_LIST = {'2': {'1': b'List A'}}


class TestGoogleTasks(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_report_folder(self.tmpdir)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _store(self, shape, container, bundle_id, tasks=1):
        db_path = pathlib.Path(self.tmpdir + VAR) / SHAPES[shape].format(c=container, a='1234')
        db_path.parent.mkdir(parents=True)
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE Tasks (TaskId TEXT, TaskListId TEXT, DueDate TEXT, Completed INTEGER, '
                   'EffectiveTask BLOB, ShardId TEXT)')
        db.execute('CREATE TABLE TaskLists (ShardId TEXT, TaskListIdWithoutShard TEXT, '
                   'EffectiveTaskList BLOB)')
        task_blob = blackboxprotobuf.encode_message(TASK, _typedef(TASK))
        list_blob = blackboxprotobuf.encode_message(TASK_LIST, _typedef(TASK_LIST))
        for number in range(tasks):
            db.execute('INSERT INTO Tasks VALUES (?, "L1", "2023-11-14", 0, ?, "u:")',
                       (f'u:T{number}', task_blob))
        db.execute('INSERT INTO TaskLists VALUES ("u:", "L1", ?)', (list_blob,))
        db.commit()
        db.close()
        files = [str(db_path)]
        if bundle_id is not None:
            root = pathlib.Path(self.tmpdir + VAR) / SHAPES[shape].split('/{c}/')[0] / container
            plist_path = root / META
            with open(plist_path, 'wb') as handle:
                plistlib.dump({'MCMMetadataIdentifier': bundle_id}, handle)
            files.append(str(plist_path))
        return files

    def _run(self, files):
        Context.set_files_found(files)
        headers, rows, source = googleTasks.__wrapped__(Context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return names, rows, source

    def test_paths_match_every_shape_and_not_the_decoy(self):
        globs = __artifacts_v2__['googleTasks']['paths']
        for shape in SHAPES.values():
            path = VAR + '/' + shape.format(c='C', a='1234')
            self.assertTrue(any(fnmatch.fnmatch(path, g) for g in globs), path)
        decoy = '/private/var/mobile/Library/Trial/Database/trial.tasks.db'
        self.assertFalse(any(fnmatch.fnmatch(decoy, g) for g in globs))

    def test_google_containers_read_others_skipped(self):
        files = (self._store('app', 'KEEP', 'com.google.Keep', tasks=2)
                 + self._store('group', 'GMAIL', 'group.com.google.Gmail')
                 + self._store('calendar', 'CAL', 'group.com.google.calendar')
                 + self._store('group', 'DECOY', 'group.com.example.app', tasks=5)
                 + self._store('group', 'NOPLIST', None, tasks=7))
        names, rows, source = self._run(files)
        apps = sorted(row[names.index('App')] for row in rows)
        self.assertEqual(apps, ['com.google.Keep', 'com.google.Keep', 'group.com.google.Gmail',
                                'group.com.google.calendar'])
        self.assertEqual(len(source.split('\n')), 3)
        self.assertNotIn('DECOY', source)
        self.assertNotIn('NOPLIST', source)

    def test_no_identifier_reads_nothing(self):
        _names, rows, source = self._run(self._store('group', 'NOPLIST', None))
        self.assertEqual(rows, [])
        self.assertEqual(source, '')

    def test_columns(self):
        names, rows, _source = self._run(self._store('group', 'GMAIL', 'group.com.google.Gmail'))
        row = dict(zip(names, rows[0]))
        self.assertEqual(str(row['Time (field 9.1.6.1)']), '2023-11-14 23:13:20+00:00')
        self.assertEqual(row['Zone (field 9.1.4)'], 'Europe/Lisbon')
        self.assertEqual(row['Text (field 2.3)'], 'Task title')
        self.assertEqual(row['Task List Text (field 2.1)'], 'List A')
        self.assertEqual(row['Account Folder'], '1234_tdl')
        self.assertEqual(row['Completed'], 'No')
        self.assertEqual(row['Due Date (as stored)'], '2023-11-14')


def _typedef(message):
    typedef = {}
    for key, value in message.items():
        if isinstance(value, dict):
            typedef[key] = {'type': 'message', 'name': '', 'message_typedef': _typedef(value)}
        elif isinstance(value, bytes):
            typedef[key] = {'type': 'bytes', 'name': ''}
        else:
            typedef[key] = {'type': 'int', 'name': ''}
    return typedef


if __name__ == '__main__':
    unittest.main()
