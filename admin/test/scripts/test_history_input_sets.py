"""The recent-inputs history for images read together (leapp_functions/app/history.py).

A run over several images, the members of a RAID set, records each image given as a
recent input path, as a run over one does, and the whole set, with the images found
beside the one given marked, under "input_sets". The input paths stay a list of
paths, which LAVA reads too.
"""
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import leapp_functions.app.history as history  # pylint: disable=wrong-import-position


class InputSetHistoryTest(unittest.TestCase):

    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp(prefix='leapp_history_'))
        self.addCleanup(shutil.rmtree, self.folder, True)
        patcher = mock.patch.object(history, 'get_shared_directory', lambda: self.folder)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _p(self, name):
        # a path as history stores it on this platform
        return os.path.normpath(os.path.join(str(self.folder), name))

    def _stored(self):
        return json.loads((self.folder / 'history.json').read_text(encoding='utf-8'))

    def test_nothing_is_recorded_while_history_is_off(self):
        history.record_input_set([self._p('a.img'), self._p('b.img')], [self._p('b.img')])
        self.assertFalse((self.folder / 'history.json').exists())

    def test_a_set_records_its_given_paths_and_marks_the_found_ones(self):
        history.set_history_enabled(True)
        history.record_input_path(self._p('older.img'))
        history.record_input_set([self._p('a.img'), self._p('b.img'), self._p('c.img')], [self._p('b.img'), self._p('c.img')])
        self.assertEqual(history.get_input_paths(), [self._p('a.img'), self._p('older.img')])
        self.assertEqual(history.get_input_sets(), [
            {'paths': [self._p('a.img'), self._p('b.img'), self._p('c.img')],
             'found_automatically': [self._p('b.img'), self._p('c.img')]}])
        self.assertTrue(all(isinstance(p, str) for p in self._stored()['input_paths']))

    def test_several_given_paths_are_each_recorded_the_first_on_top(self):
        history.set_history_enabled(True)
        history.record_input_set([self._p('a.img'), self._p('b.img')])
        self.assertEqual(history.get_input_paths(), [self._p('a.img'), self._p('b.img')])

    def test_the_same_images_given_again_replace_the_set(self):
        history.set_history_enabled(True)
        history.record_input_set([self._p('a.img'), self._p('b.img')])
        history.record_input_set([self._p('a.img'), self._p('b.img'), self._p('c.img')], [self._p('c.img')])
        self.assertEqual(len(history.get_input_sets()), 1)
        self.assertEqual(history.get_input_sets()[0]['found_automatically'], [self._p('c.img')])

    def test_one_path_is_recorded_as_before(self):
        history.set_history_enabled(True)
        history.record_input_set([self._p('a.img')])
        self.assertEqual(history.get_input_paths(), [self._p('a.img')])
        self.assertNotIn('input_sets', self._stored())

    def test_a_set_whose_paths_an_older_release_cleared_is_not_offered(self):
        history.set_history_enabled(True)
        history.record_input_set([self._p('a.img'), self._p('b.img')], [self._p('b.img')])
        stored = self._stored()
        stored.pop('input_paths')        # what an older release's clear leaves behind
        (self.folder / 'history.json').write_text(json.dumps(stored), encoding='utf-8')
        self.assertEqual(history.get_input_sets(), [])

    def test_clearing_this_tool_s_history_clears_the_sets(self):
        history.set_history_enabled(True)
        history.record_input_set([self._p('a.img'), self._p('b.img')], [self._p('b.img')])
        history.clear_single_leapp_history('dleapp')
        self.assertEqual(history.get_input_sets(), [])


if __name__ == '__main__':
    unittest.main()
