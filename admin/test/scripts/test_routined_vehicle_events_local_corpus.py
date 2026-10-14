#!/usr/bin/env python3
"""Opt-in structural checks of the routined vehicle event artifact against a local,
non-public extraction (see admin/docs/testing/local_corpus_tests.md). Only shapes and
timestamp sanity are asserted; no value from the image is recorded.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_routined_vehicle_events_local_corpus.py -v
"""

import unittest

from admin.test.scripts.test_local_corpus_artifacts import LOCAL_IMAGE, LocalCorpusTestCase, \
    _Context
from scripts.artifacts.routinedParkedCar import routinedParkedCar

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
class RoutinedParkedCarLocalTest(_RoutinedLocal):
    SUFFIX = 'Library/Caches/com.apple.routined/Local.sqlite'
    ARTIFACT = routinedParkedCar
    TIME_COLUMNS = (0, 1)

    def test_structure(self):
        _headers, rows = self.check(2, 3)
        for row in rows:
            self.assertIn(row[11], ('ZRTVEHICLEEVENTMO', 'ZRTVEHICLEEVENTHISTORYMO'))


if __name__ == '__main__':
    unittest.main()
