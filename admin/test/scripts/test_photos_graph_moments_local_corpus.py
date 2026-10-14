#!/usr/bin/env python3
"""Opt-in structural checks of the Photos Graph Moment Locations artifact against a local,
non-public extraction (see admin/docs/testing/local_corpus_tests.md). Only shapes and
timestamp sanity are asserted; no value from the image is recorded.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_photos_graph_moments_local_corpus.py -v
"""

import unittest

from admin.test.scripts.test_local_corpus_artifacts import LOCAL_IMAGE, LocalCorpusTestCase
from scripts.artifacts.photosGraphMoments import photosGraphMoments

COORD = r'^-?\d{1,3}\.\d+$'


class _Context:
    def __init__(self, paths):
        self.paths = [str(p) for p in paths]

    def get_files_found(self):
        return self.paths

    def get_relative_path(self, path):
        return str(path)


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class PhotosGraphMomentsLocalTest(LocalCorpusTestCase):
    def setUp(self):
        super().setUp()
        self.graph = self.fetch('Caches/GraphService/PhotosGraph/photosgraph.kgdb')
        if not self.graph:
            self.skipTest('photosgraph.kgdb not present in the local image')
        self.photos = self.fetch('mobile/Media/PhotoData/Photos.sqlite')

    def test_structure(self):
        paths = [self.graph] + ([self.photos] if self.photos else [])
        headers, rows, _source = photosGraphMoments.__wrapped__(_Context(paths))
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_plausible_timestamp(row[1])
            self.assert_matches(row[2], COORD, 'latitude')
            self.assert_matches(row[3], COORD, 'longitude')
            if self.photos:
                self.assertTrue(row[10], 'each moment lists its photos when Photos.sqlite is present')


if __name__ == '__main__':
    unittest.main()
