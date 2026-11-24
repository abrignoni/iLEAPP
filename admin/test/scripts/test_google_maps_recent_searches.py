"""googleMapsRecentSearches reads kRecentSearches from Google Maps containers only (SYNTHETIC archives)."""
import datetime
import os
import plistlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import googleMapsRecentSearches as module

UID = plistlib.UID
MS = 1_790_000_000_000


def archive(items):
    """An NSKeyedArchiver plist whose kRecentSearches array holds the given (query, ms, lat, lon) items."""
    objects = ['$null', None]
    classes = {}

    def cls(name):
        if name not in classes:
            objects.append({'$classname': name, '$classes': [name, 'NSObject']})
            classes[name] = UID(len(objects) - 1)
        return classes[name]

    refs = []
    for query, ms, lat, lon in items:
        placemark = None
        if lat is not None:
            objects.append('One Line Address')
            address = UID(len(objects) - 1)
            objects.append({'$class': cls('AZMutablePlacemark'), '_coordinateLat': lat, '_coordinateLong': lon,
                            'singleLineAddress': address})
            placemark = UID(len(objects) - 1)
        objects.append(query)
        text = UID(len(objects) - 1)
        objects.append(ms)
        stamp = UID(len(objects) - 1)
        objects.append({'$class': cls('AZClientSideSuggestionItem'), 'query': text, 'title': text,
                        'timestamp': stamp, 'placemark': placemark or UID(0), 'secondaryInfo': UID(0)})
        refs.append(UID(len(objects) - 1))
    objects.append({'$class': cls('NSMutableArray'), 'NS.objects': refs})
    root = UID(len(objects) - 1)
    objects[1] = True
    return plistlib.dumps({'$archiver': 'NSKeyedArchiver', '$version': 100000, '$objects': objects,
                           '$top': {'kRecentSearches': root, 'kEnabledKey': UID(1)}}, fmt=plistlib.PlistFormat.FMT_BINARY)


class RecentSearchesTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def container(self, uuid, bundle, data):
        base = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application', uuid)
        os.makedirs(os.path.join(base, 'Library/Application Support'))
        meta = os.path.join(base, '.com.apple.mobile_container_manager.metadata.plist')
        with open(meta, 'wb') as handle:
            plistlib.dump({'MCMMetadataIdentifier': bundle}, handle)
        store = os.path.join(base, 'Library/Application Support/LocalSuggestions')
        with open(store, 'wb') as handle:
            handle.write(data)
        return [meta, store]

    def run_module(self, paths):
        context = SimpleNamespace(get_files_found=lambda: paths, get_relative_path=os.path.basename)
        with mock.patch.object(module, 'logfunc'):
            return module.googleMapsRecentSearches.__wrapped__(context)

    def test_items_in_stored_order_with_time_and_place(self):
        paths = self.container('A', 'com.google.Maps', archive([('newer', MS, 1.5, -2.5), ('older', MS - 1000, None, None)]))
        headers, rows, source = self.run_module(paths)
        self.assertEqual(len(headers), len(rows[0]))
        expected = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=MS)
        self.assertEqual(rows[0][:2], (expected, 'newer'))
        self.assertEqual(rows[0][3:], ('One Line Address', 1.5, -2.5, 1))
        self.assertEqual(rows[1][1:], ('older', '', '', '', '', 2))
        self.assertEqual(source, paths[1])

    def test_another_apps_container_is_not_read(self):
        paths = self.container('B', 'com.example.other', archive([('x', MS, 1.0, 1.0)]))
        self.assertEqual(self.run_module(paths)[1], [])

    def test_a_damaged_file_does_not_lose_the_other_container(self):
        good = self.container('A', 'com.google.Maps', archive([('kept', MS, None, None)]))
        bad = self.container('C', 'com.google.Maps', b'not a plist')
        _, rows, source = self.run_module(bad + good)
        self.assertEqual([row[1] for row in rows], ['kept'])
        self.assertEqual(source, good[1])


if __name__ == '__main__':
    unittest.main()
