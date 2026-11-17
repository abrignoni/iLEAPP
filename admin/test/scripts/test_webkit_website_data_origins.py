"""WebKit Website Data Origins on synthetic WebsiteData trees (values invented for the test)."""
import pathlib
import plistlib
import struct
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import webkitWebsiteDataOrigins as parser  # noqa: E402  # pylint: disable=wrong-import-position

APP = 'private/var/mobile/Containers/Data/Application/AAAA'


def _string(text, wide=False):
    if text is None:
        return struct.pack('<I', 0xFFFFFFFF)
    raw = text.encode('utf-16-le' if wide else 'latin-1')
    return struct.pack('<IB', len(text), 0 if wide else 1) + raw


def _origin(protocol, host, port=None, wide=False):
    tail = b'\x00' if port is None else b'\x01' + struct.pack('<H', port)
    return _string(protocol) + _string(host, wide) + tail


class DecodeTest(unittest.TestCase):
    def test_origin_file_decodes_exactly(self):
        blob = _origin('https', 'top.example') + _origin('https', 'frame.example', 8443, wide=True)
        self.assertEqual(parser.decode_origin_file(blob),
                         (('https', 'top.example', None), ('https', 'frame.example', 8443)))
        self.assertIsNone(parser.decode_origin_file(blob + b'\x00'))
        self.assertIsNone(parser.decode_origin_file(blob[:-3]))

    def test_database_identifier(self):
        self.assertEqual(parser.parse_database_identifier('https_a_b.example_0'), ('https', 'a_b.example', None))
        self.assertEqual(parser.parse_database_identifier('http_host%3Aname_8080'), ('http', 'host:name', 8080))
        self.assertIsNone(parser.parse_database_identifier('nounderscore'))
        self.assertIsNone(parser.parse_database_identifier('https_host_x1'))


class ArtifactTest(unittest.TestCase):
    def test_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            app = root / APP
            files = []

            def write(relative, data):
                path = app / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                files.append(str(path))

            write('.com.apple.mobile_container_manager.metadata.plist',
                  plistlib.dumps({'MCMMetadataIdentifier': 'com.example.app'}))
            new = 'Library/WebKit/WebsiteData/Default/h1/h2/'
            write(new + 'origin', _origin('https', 'top.example') + _origin('https', 'frame.example'))
            write(new + 'CacheStorage/origin', _origin('https', 'top.example') + _origin('https', 'frame.example'))
            write(new + 'LocalStorage/localstorage.sqlite3', b'')
            write(new + 'IndexedDB/x/IndexedDB.sqlite3', b'')
            write('Library/WebKit/WebsiteData/Default/h3/h4/origin', b'\x01\x02')
            write('SystemData/com.apple.SafariViewService/Library/WebKit/WebsiteData/Default/h5/h6/origin',
                  _origin('https', 'svs.example') + _origin('https', 'svs.example'))
            write('Library/WebKit/WebsiteData/LocalStorage/https_old.example_0.localstorage', b'')
            write('Library/WebKit/WebsiteData/IndexedDB/v1/https_idb.example_0/db1/IndexedDB.sqlite3', b'')
            write('Library/WebKit/WebsiteData/IndexedDB/v1/https_idb.example_0/db2/IndexedDB.sqlite3', b'')
            store = 'Library/WebKit/WebsiteDataStore/U1/Origins/h7/h8/'
            write(store + 'origin', _origin('https', 'store.example') + _origin('https', 'store.example'))
            write(store + 'LocalStorage/localstorage.sqlite3', b'')
            write('Library/WebKit/WebsiteData/https_loose.example_0.localstorage', b'')
            write('Library/WebKit/WebsiteData/https_looseidb.example_0/db/IndexedDB.sqlite3', b'')
            write('Library/WebKit/WebsiteData/not-an-identifier.localstorage', b'')
            context = SimpleNamespace(get_files_found=lambda: files, get_seeker=lambda: None)
            headers, rows, source = parser.webkit_website_data_origins.__wrapped__(context)
        self.assertEqual(len(headers), len(rows[0]))
        by_origin = {row[4]: row for row in rows}
        self.assertEqual(len(rows), 7)
        self.assertEqual(by_origin['https://store.example'][2], 'App data store')
        self.assertEqual(by_origin['https://store.example'][5], 'LocalStorage')
        self.assertEqual(by_origin['https://loose.example'][5:], ('LocalStorage', 'file name'))
        self.assertEqual(by_origin['https://looseidb.example'][5:], ('IndexedDB', 'folder name'))
        main = by_origin['https://frame.example']
        self.assertEqual(main[1:4], ('com.example.app', 'App', 'https://top.example'))
        self.assertEqual(main[5:], ('CacheStorage, IndexedDB, LocalStorage', 'origin file'))
        self.assertEqual(by_origin['https://svs.example'][2], 'SafariViewService')
        self.assertEqual(by_origin['https://old.example'][3:], ('', 'https://old.example', 'LocalStorage', 'file name'))
        self.assertEqual(by_origin['https://idb.example'][5:], ('IndexedDB', 'folder name'))
        self.assertEqual(len(source.splitlines()), 7)


if __name__ == '__main__':
    unittest.main()
