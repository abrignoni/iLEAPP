"""twitterX and skg_archive read a keyed archive without leaving its file open.

Both passed a file path to nska_deserialize.deserialize_plist, which opens the file and never
closes it: one leaked handle per archive, reported as a ResourceWarning under python -X dev,
and on Windows a file that stays locked for the rest of the run. Each now reads the bytes in
a with block and decodes them.
"""
import gc
import os
import plistlib
import shutil
import tempfile
import unittest
import warnings

from scripts.artifacts import skg_archive, twitterX
from scripts.context import Context


def keyed_archive(root_object, *objects):
    return {'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': plistlib.UID(1)},
            '$objects': ['$null', root_object, *objects]}


class ArtifactsCloseArchivesTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def write(self, name, archive):
        path = os.path.join(self.tmpdir, name)
        with open(path, 'wb') as f:
            plistlib.dump(archive, f, fmt=plistlib.PlistFormat.FMT_BINARY)
        return path

    def leaks(self, call):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', ResourceWarning)
            result = call()
            gc.collect()
        # gc.collect() also reports files and databases other tests in a full discovery left
        # open, so only the warnings about files in this test's own folder count.
        return result, [str(w.message) for w in caught
                        if issubclass(w.category, ResourceWarning) and self.tmpdir in str(w.message)]

    def test_the_twitterx_dm_cache_is_decoded_and_closed(self):
        path = self.write('TDfir-1', keyed_archive(
            {'NS.keys': [plistlib.UID(2)], 'NS.objects': [plistlib.UID(3)], '$class': plistlib.UID(4)},
            'inbox', 'value', {'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']}))

        cache, leaks = self.leaks(lambda: twitterX._load_dm_cache(path))  # pylint: disable=protected-access

        self.assertEqual(cache, {'inbox': 'value'})
        self.assertEqual(leaks, [])

    def test_an_skg_archive_is_read_and_closed(self):
        path = self.write('skg.archive', keyed_archive(
            {'NS.objects': [], '$class': plistlib.UID(2)},
            {'$classname': 'NSArray', '$classes': ['NSArray', 'NSObject']}))
        Context.clear()
        Context.set_data_folder(self.tmpdir)
        Context.set_files_found([path])

        (_, rows, _), leaks = self.leaks(lambda: skg_archive.skg_archive.__wrapped__(Context))

        self.assertEqual(rows, [])
        self.assertEqual(leaks, [])


if __name__ == '__main__':
    unittest.main()
