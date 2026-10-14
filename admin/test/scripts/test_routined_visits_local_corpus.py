#!/usr/bin/env python3
"""Opt-in structural checks of the routined visit artifacts against a local,
non-public extraction (see admin/docs/testing/local_corpus_tests.md). Only shapes and
timestamp sanity are asserted; no value from the image is recorded.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_routined_visits_local_corpus.py -v
"""

import unittest

from admin.test.scripts.test_local_corpus_artifacts import LOCAL_IMAGE, LocalCorpusTestCase, \
    _Context
from scripts.artifacts.routinedVisits import routinedCacheVisits, routinedCloudVisits

COORD = r'^-?\d{1,3}\.\d+$'


class _RoutinedLocal(LocalCorpusTestCase):
    SUFFIX = ''
    ARTIFACT = None
    TIME_COLUMNS = ()

    def setUp(self):
        super().setUp()
        self.path = self.fetch(self.SUFFIX)
        if not self.path:
            self.skipTest(f'{self.SUFFIX} not present in the local image')

    def check(self, lat_index, lon_index):
        headers, rows, source = type(self).ARTIFACT.__wrapped__(_Context(self.path))
        self.assertEqual(source, str(self.path))
        self.assert_row_shape(headers, rows)
        for row in rows:
            for i in self.TIME_COLUMNS:
                self.assert_plausible_timestamp(row[i])
            self.assert_matches(row[lat_index], COORD, 'latitude')
            self.assert_matches(row[lon_index], COORD, 'longitude')
        return headers, rows


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class RoutinedCacheVisitsLocalTest(_RoutinedLocal):
    SUFFIX = 'Library/Caches/com.apple.routined/Cache.sqlite'
    ARTIFACT = routinedCacheVisits
    TIME_COLUMNS = (0, 1, 2, 3)

    def test_structure(self):
        _headers, rows = self.check(4, 5)
        for row in rows:
            self.assertIsNotNone(row[0], 'every visit row has an entry time')


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class RoutinedCloudVisitsLocalTest(_RoutinedLocal):
    SUFFIX = 'Library/Caches/com.apple.routined/Cloud-V2.sqlite'
    ARTIFACT = routinedCloudVisits
    TIME_COLUMNS = (0, 1, 2, 3)

    def test_structure(self):
        self.check(4, 5)


if __name__ == '__main__':
    unittest.main()
