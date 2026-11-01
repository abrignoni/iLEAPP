"""get_plist_file_content reads a keyed archive without leaving a file open.

For an NSKeyedArchiver plist it called nska_deserialize.deserialize_plist(file_path), which
opened the file a second time and never closed it: a leaked handle per archive, and on
Windows the temporary copy of a stream could not be deleted while it was held. It now
decodes the bytes of the handle it already holds.
"""
import gc
import os
import plistlib
import shutil
import tempfile
import unittest
import warnings

from scripts.ilapfuncs import get_plist_file_content

ARCHIVE = {'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': plistlib.UID(1)},
           '$objects': ['$null',
                        {'NS.keys': [plistlib.UID(2)], 'NS.objects': [plistlib.UID(3)],
                         '$class': plistlib.UID(4)},
                        'name', 'value',
                        {'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']}]}


class PlistFileKeyedArchiveHandleTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, 'archive.plist')
        with open(self.path, 'wb') as f:
            plistlib.dump(ARCHIVE, f, fmt=plistlib.PlistFormat.FMT_BINARY)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def read(self, source):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', ResourceWarning)
            content = get_plist_file_content(source)
            gc.collect()
        leaks = [w for w in caught if issubclass(w.category, ResourceWarning)]
        return content, leaks

    def test_a_path_is_decoded_and_closed(self):
        content, leaks = self.read(self.path)

        self.assertEqual(content, {'name': 'value'})
        self.assertEqual(leaks, [])

    def test_a_stream_is_decoded_and_its_temporary_copy_removed(self):
        before = set(os.listdir(tempfile.gettempdir()))
        with open(self.path, 'rb') as stream:
            content, leaks = self.read(stream)

        self.assertEqual(content, {'name': 'value'})
        self.assertEqual(leaks, [])
        added = {n for n in set(os.listdir(tempfile.gettempdir())) - before if n.endswith('.plist')}
        self.assertEqual(added, set())


if __name__ == '__main__':
    unittest.main()
