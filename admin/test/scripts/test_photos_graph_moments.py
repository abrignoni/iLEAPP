#!/usr/bin/env python3
"""Synthetic tests for the Photos Graph Moment Locations artifact (photosgraph.kgdb)."""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifacts.photosGraphMoments import photosGraphMoments

START, END = 1776255287.0, 1776255806.0       # Unix seconds, as utcs / utce are stored
COCOA = 978307200


class _Context:
    def __init__(self, paths):
        self.paths = [str(p) for p in paths]

    def get_files_found(self):
        return self.paths

    def get_relative_path(self, path):
        return Path(path).name


def _write(path, statements):
    db = sqlite3.connect(path)
    try:
        with db:
            for statement, values in statements:
                db.execute(statement, values)
    finally:
        db.close()                                     # Windows cannot delete an open file
    return path


class PhotosGraphMomentsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def _graph(self):
        # attribute ids: 1 lat, 2 lng, 3 utcs, 4 utce, 5 noa, 6 relevance, 7 name, 8 lclid, 9 cnt
        attrs = ['lat', 'lng', 'utcs', 'utce', 'noa', 'relevance', 'name', 'lclid', 'cnt']
        statements = [
            ('CREATE TABLE Attribute (identifier INTEGER PRIMARY KEY, name TEXT)', ()),
            ('CREATE TABLE Node (identifier INTEGER PRIMARY KEY, labels BLOB, edgesIn BLOB, edgesOut BLOB)', ()),
            ('CREATE TABLE Edge (identifier INTEGER PRIMARY KEY, labels BLOB, sourceNodeId INTEGER, '
             'targetNodeId INTEGER)', ()),
            ('CREATE TABLE NodeValue (elementId INTEGER, attributeId INTEGER, intValue INTEGER, '
             'realValue REAL, stringValue TEXT, dataType INTEGER)', ()),
            ('CREATE TABLE EdgeValue (elementId INTEGER, attributeId INTEGER, intValue INTEGER, '
             'realValue REAL, stringValue TEXT, dataType INTEGER)', ()),
        ]
        statements += [('INSERT INTO Attribute VALUES (?, ?)', (i + 1, n)) for i, n in enumerate(attrs)]
        statements += [
            ('INSERT INTO Node VALUES (10, NULL, NULL, NULL)', ()),     # moment
            ('INSERT INTO Node VALUES (20, NULL, NULL, NULL)', ()),     # address
            ('INSERT INTO Node VALUES (30, NULL, NULL, NULL)', ()),     # a scene, no location
            ('INSERT INTO NodeValue VALUES (10, 8, NULL, NULL, ?, 3)', ('MOMENT-UUID-1',)),
            ('INSERT INTO NodeValue VALUES (10, 9, 2, NULL, NULL, 1)', ()),
            ('INSERT INTO NodeValue VALUES (20, 7, NULL, NULL, ?, 3)', ('1 Example Rd, Albany',)),
            ('INSERT INTO NodeValue VALUES (20, 1, NULL, 42.6847, NULL, 2)', ()),
            ('INSERT INTO NodeValue VALUES (20, 2, NULL, -73.8186, NULL, 2)', ()),
            ('INSERT INTO Edge VALUES (100, NULL, 10, 20)', ()),
            ('INSERT INTO Edge VALUES (101, NULL, 10, 30)', ()),        # no lat: not reported
            ('INSERT INTO EdgeValue VALUES (100, 1, NULL, 42.6840, NULL, 2)', ()),
            ('INSERT INTO EdgeValue VALUES (100, 2, NULL, -73.8185, NULL, 2)', ()),
            ('INSERT INTO EdgeValue VALUES (100, 3, NULL, ?, NULL, 2)', (START,)),
            ('INSERT INTO EdgeValue VALUES (100, 4, NULL, ?, NULL, 2)', (END,)),
            ('INSERT INTO EdgeValue VALUES (100, 5, 2, NULL, NULL, 1)', ()),
            ('INSERT INTO EdgeValue VALUES (100, 6, NULL, 1.0, NULL, 2)', ()),
            ('INSERT INTO EdgeValue VALUES (101, 6, NULL, 0.5, NULL, 2)', ()),
        ]
        return _write(self.root / 'photosgraph.kgdb', statements)

    def _photos(self):
        folder = self.root / 'Media' / 'PhotoData'
        folder.mkdir(parents=True)
        return _write(folder / 'Photos.sqlite', [
            ('CREATE TABLE ZMOMENT (Z_PK INTEGER PRIMARY KEY, ZUUID TEXT)', ()),
            ('CREATE TABLE ZASSET (Z_PK INTEGER PRIMARY KEY, ZMOMENT INTEGER, ZDATECREATED REAL, '
             'ZDIRECTORY TEXT, ZFILENAME TEXT)', ()),
            ('INSERT INTO ZMOMENT VALUES (1, ?)', ('MOMENT-UUID-1',)),
            ('INSERT INTO ZMOMENT VALUES (2, ?)', ('OTHER',)),
            ('INSERT INTO ZASSET VALUES (2, 1, ?, ?, ?)', (END - COCOA, 'DCIM/100APPLE', 'IMG_0002.HEIC')),
            ('INSERT INTO ZASSET VALUES (1, 1, ?, ?, ?)', (START - COCOA, 'DCIM/100APPLE', 'IMG_0001.MOV')),
            ('INSERT INTO ZASSET VALUES (3, 2, ?, ?, ?)', (START - COCOA, 'DCIM/100APPLE', 'IMG_0009.JPG')),
        ])

    def test_moment_with_address_and_photos(self):
        graph, photos = self._graph(), self._photos()
        headers, rows, source = photosGraphMoments.__wrapped__(_Context([graph, photos]))
        self.assertEqual(len(rows), 1)                 # only the edge carrying lat / lng
        row = rows[0]
        self.assertEqual(len(row), len(headers))
        self.assertEqual(row[0], datetime.fromtimestamp(START, tz=timezone.utc))
        self.assertEqual(row[1], datetime.fromtimestamp(END, tz=timezone.utc))
        self.assertEqual(row[2:6], (42.6840, -73.8185, 2, '1 Example Rd, Albany'))
        self.assertEqual(row[6:9], (42.6847, -73.8186, 'MOMENT-UUID-1'))
        # photos of that moment only, in capture order
        self.assertEqual(row[10], 'DCIM/100APPLE/IMG_0001.MOV, DCIM/100APPLE/IMG_0002.HEIC')
        self.assertIsNone(row[11])                     # no DCIM files in the extraction to attach
        self.assertEqual(source.split('\n'), [str(graph), str(photos)])

    def test_without_photos_database(self):
        graph = self._graph()
        _headers, rows, source = photosGraphMoments.__wrapped__(_Context([graph]))
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0][10])
        self.assertEqual(source, str(graph))

    def test_not_a_graph(self):
        path = _write(self.root / 'photosgraph.kgdb', [('CREATE TABLE Other (x)', ())])
        _headers, rows, _source = photosGraphMoments.__wrapped__(_Context([path]))
        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
