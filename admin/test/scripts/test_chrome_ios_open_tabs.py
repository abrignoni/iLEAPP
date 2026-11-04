"""Pin how chromeIosOpenTabs.py reads Chromium iOS session storage.

Author: @AlexisBrignoni, Claude.

Every store here is synthetic. The SessionStorage files are protocol buffers encoded by hand
with the field numbers of Chromium's WebStateListStorage and WebStateStorage messages, and the
session.plist is an NSKeyedArchiver archive built by hand with Chromium's key names. The
expected values are written out, never read back from the code under test.
"""
import datetime
import pathlib
import plistlib
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import chromeIosOpenTabs  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
EPOCH_1601 = datetime.datetime(1601, 1, 1, tzinfo=UTC)
# An iTunes backup names the container by bundle identifier, so no metadata plist is needed.
CHROME = 'private/var/mobile/Containers/Data/Application/com.google.chrome.ios/Library/Application Support/Google/Chrome/Default'
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 16


def varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    return bytes(out + bytes([value]))


def field(number, value):
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    if isinstance(value, str):
        value = value.encode()
    return varint(number << 3 | 2) + varint(len(value)) + value


def us(when):
    """A datetime as microseconds since 1601, the unit TimeFromProto reads."""
    return int((when - EPOCH_1601).total_seconds() * 1_000_000)


def timestamp(when):
    return field(1, us(when))


def metadata(created, last_active):
    return field(1, timestamp(created)) + field(2, timestamp(last_active))


def tab_list(items, active):
    body = b''.join(field(1, field(1, ident) + field(3, metadata(c, l))) for ident, c, l in items)
    return body + field(2, active)


def web_state(entries, current):
    nav = field(1, current) if current else b''
    for url, title, when, virtual in entries:
        item = field(1, url) + (field(2, virtual) if virtual else b'') + field(3, title) + field(4, timestamp(when))
        nav += field(2, item)
    return field(4, nav)


def keyed_archive(root):
    """A minimal NSKeyedArchiver archive of nested dicts and lists, as Chromium's coders write them."""
    objects = ['$null']

    def add(value):
        if isinstance(value, dict):
            index = len(objects)
            objects.append(None)
            entry = {key: add(item) for key, item in value.items()}
            entry['$class'] = add_class('CRWSessionStorage', ['CRWSessionStorage', 'NSObject'])
            objects[index] = entry
            return plistlib.UID(index)
        if isinstance(value, list):
            index = len(objects)
            objects.append(None)
            objects[index] = {'NS.objects': [add(item) for item in value],
                              '$class': add_class('NSArray', ['NSArray', 'NSObject'])}
            return plistlib.UID(index)
        if isinstance(value, (str, bytes)):
            objects.append(value)
            return plistlib.UID(len(objects) - 1)
        return value

    classes = {}

    def add_class(name, hierarchy):
        if name not in classes:
            objects.append({'$classname': name, '$classes': hierarchy})
            classes[name] = plistlib.UID(len(objects) - 1)
        return classes[name]

    top = add(root)
    return plistlib.dumps({'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': top},
                           '$objects': objects}, fmt=plistlib.PlistFormat.FMT_BINARY)


class ChromeIosOpenTabsTest(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.files = []

    def tearDown(self):
        shutil.rmtree(self.root)

    def _write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.files.append(str(path))

    def _relative(self, path):
        return str(pathlib.Path(path).relative_to(self.root)).replace('\\', '/')

    def _run(self, function):
        context = SimpleNamespace(get_files_found=lambda: list(self.files), get_relative_path=self._relative)
        with mock.patch.object(chromeIosOpenTabs, 'logfunc'), \
                mock.patch.object(chromeIosOpenTabs, 'check_in_media',
                                  side_effect=lambda path, name='': f'media:{name}'):
            return getattr(chromeIosOpenTabs, function).__wrapped__(context)

    def _session_storage(self):
        t1 = datetime.datetime(2025, 3, 1, 10, 0, tzinfo=UTC)
        t2 = datetime.datetime(2025, 3, 2, 11, 30, tzinfo=UTC)
        normal = f'{CHROME}/SessionStorage/{{SyntheticIdentifier}}'
        self._write(f'{normal}/session_metadata.pb', tab_list([(0x5c445af7, t1, t2), (0x10, t1, t1)], active=0))
        self._write(f'{normal}/5c445af7/data.pb', web_state([
            ('https://example.com/a', 'A', t1, None), ('https://example.com/b', 'B', t2, 'https://example.com/v')],
            current=1))
        self._write(f'{normal}/5c445af7/state.pb', b'\x00not a message')
        self._write(f'{normal}/00000010/data.pb', web_state([('https://example.com/c', 'C', t1, None)], 0))
        self._write(f'{normal}/0000abcd/data.pb', b'')  # a folder the tab list does not name
        self._write(f'{CHROME}/Snapshots/{{SyntheticIdentifier}}/{0x5c445af7:08d}@2x.jpg', JPEG)
        self._write(f'{CHROME}/Snapshots/{{SyntheticIdentifier}}/{0x5c445af7:08d}Grey@2x.jpg', JPEG)
        self._write(f'{CHROME}/Snapshots/{{SyntheticIdentifier}}/{0x10:08d}@2x.jpg', b'PNGNOTJPEG')
        incognito = f'{CHROME}/OTR/SessionStorage/{{SyntheticIdentifier}}'
        self._write(f'{incognito}/session_metadata.pb', tab_list([(0x20, t2, t2)], active=0))
        self._write(f'{incognito}/00000020/data.pb', web_state([('https://example.org/x', 'X', t2, None)], 0))
        inactive = f'{CHROME}/SessionStorage/{{SyntheticIdentifier}}-Inactive'
        self._write(f'{inactive}/session_metadata.pb', tab_list([(0x30, t1, t1)], active=0))
        self._write(f'{inactive}/00000030/data.pb', web_state([('https://example.net/y', 'Y', t1, None)], 0))
        return t1, t2

    def test_session_storage_tabs(self):
        t1, t2 = self._session_storage()
        headers, rows, sources = self._run('chrome_ios_open_tabs')
        self.assertEqual(len(rows[0]), len(headers))
        by_id = {row[4]: row for row in rows}
        self.assertEqual(sorted(by_id), ['00000010', '00000020', '00000030', '0000abcd', '5c445af7'])
        first = by_id['5c445af7']
        self.assertEqual(first[:9], (t2, t1, 'com.google.chrome.ios', 'Normal', '5c445af7', 'Yes', 'Yes', 2,
                                     'https://example.com/v'))
        self.assertEqual(first[9], 'B')
        self.assertEqual(first[10], f'media:{0x5c445af7:08d}@2x.jpg')
        self.assertEqual(by_id['00000010'][10], '')  # the bytes are not a JPEG
        self.assertEqual(by_id['00000010'][6], 'No')
        self.assertEqual(by_id['00000020'][3], 'Incognito')
        self.assertEqual(by_id['00000030'][3], 'Inactive')
        self.assertEqual(by_id['0000abcd'][:8], ('', '', 'com.google.chrome.ios', 'Normal', '0000abcd', 'No', '', 0))
        self.assertNotIn('state.pb', sources)

    def test_session_storage_entries(self):
        t1, t2 = self._session_storage()
        headers, rows, _ = self._run('chrome_ios_open_tab_entries')
        self.assertEqual(len(rows[0]), len(headers))
        tab = [row for row in rows if row[3] == '5c445af7']
        self.assertEqual([row[:9] for row in tab], [
            (t1, 'com.google.chrome.ios', 'Normal', '5c445af7', 0, 'No', 'https://example.com/a', '', 'A'),
            (t2, 'com.google.chrome.ios', 'Normal', '5c445af7', 1, 'Yes', 'https://example.com/b',
             'https://example.com/v', 'B'),
        ])
        self.assertEqual(len(rows), 5)

    def test_session_plist_tabs_and_unclaimed_snapshot(self):
        t1 = datetime.datetime(2023, 5, 4, 8, 0, tzinfo=UTC)
        archive = keyed_archive({'sessionWindows': [{'selectedIndex': 0, 'sessions': [{
            'stableIdentifier': 'ABC', 'creationTime': us(t1), 'lastActiveTime': us(t1),
            'lastCommittedItemIndex': 0,
            'entries': [{'urlString': b'https://example.com/p', 'title': 'P', 'timestamp': us(t1)}],
        }]}]})
        self._write(f'{CHROME}/OTR/Sessions/{{SyntheticIdentifier}}/session.plist', archive)
        self._write(f'{CHROME}/OTR/Sessions/{{SyntheticIdentifier}}/Snapshots/ABC@2x.jpg', JPEG)
        self._write(f'{CHROME}/OTR/Sessions/{{SyntheticIdentifier}}/Snapshots/DEF@2x.jpg', JPEG)
        self._write(f'{CHROME}/OTR/Sessions/{{SyntheticIdentifier}}/Snapshots/DEFGrey@2x.jpg', JPEG)
        _, rows, _ = self._run('chrome_ios_open_tabs')
        self.assertEqual(len(rows), 2)
        tab, unclaimed = rows
        self.assertEqual(tab[:11], (t1, t1, 'com.google.chrome.ios', 'Incognito', 'ABC', '', 'Yes', 1,
                                    'https://example.com/p', 'P', 'media:ABC@2x.jpg'))
        self.assertEqual(unclaimed[:11], ('', '', 'com.google.chrome.ios', 'Incognito', 'DEF', 'No', '', 0, '', '',
                                          'media:DEF@2x.jpg'))
        _, entries, _ = self._run('chrome_ios_open_tab_entries')
        self.assertEqual([row[:9] for row in entries], [
            (t1, 'com.google.chrome.ios', 'Incognito', 'ABC', 0, 'Yes', 'https://example.com/p', '', 'P')])

    def test_a_snapshot_folder_of_no_read_session_is_not_reported(self):
        self._write('private/var/mobile/Containers/Data/Application/com.example.other/Library/Application Support/'
                    'Vendor/App/Snapshots/x/00000001@2x.jpg', JPEG)
        _, rows, _ = self._run('chrome_ios_open_tabs')
        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
