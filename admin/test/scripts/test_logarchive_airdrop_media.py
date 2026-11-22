"""Pin which unified log entries the AirDrop and media playback artifacts select.

Both artifacts select from the table logarchive_artifacts builds, so every row goes through the
collection query first. The messages are synthetic and follow Apple's format strings. The
expected rows are written out, never read back from the code.
"""
import pathlib
import sqlite3
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import log_filter  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive as module  # pylint: disable=wrong-import-position

SHARINGD = '/usr/libexec/sharingd'
MEDIAREMOTED = '/usr/libexec/mediaremoted'
APP = '/Applications/Example.app/Example'
SHARING = 'com.apple.sharing'
SHARE_SHEET = 'com.apple.ShareSheet'
MEDIA = 'com.apple.amp.mediaremote'
IS_PLAYING = '[MRDNowPlayingPlayerClient] isPlaying changed to 1 for player'

AIRDROP_ROWS = (
    ('a1', SHARINGD, SHARING, 'AirDrop', 'Scanning mode Everyone'),
    ('a2', SHARINGD, SHARING, 'AirDropNW', 'Started scanning for AirDrop'),
    ('a3', '/System/Library/CoreServices/Finder', SHARING, 'AirDrop', 'Discoverable mode changed to Everyone'),
    ('a4', SHARINGD, SHARING, 'Daemon', 'Everyone mode expired - setting to Contacts Only'),
    ('a5', '/System/Library/AirDropUI', SHARING, 'AirDrop', 'Accept transfer for transfer identifier: ABC.'),
    ('a6', SHARINGD, SHARE_SHEET, 'ShareSheet', 'current connection bundle ID: com.example.app'),
    ('a7', APP, SHARE_SHEET, 'ShareSheet', 'UIAVC: view did appear'),
    ('a8', APP, SHARE_SHEET, 'ShareSheet', 'Activating com.apple.sharing.sharesheet'),
    ('a9', SHARINGD, '', '', 'title: SharingDaemon State\nbody'),
    ('a10', SHARINGD, None, None, 'SharingDaemon State'),
)
MEDIA_ROWS = (
    ('m1', MEDIAREMOTED, MEDIA, 'x', IS_PLAYING),
    ('m2', APP, MEDIA, 'x', '[AVDiscoverySession] Current airplay active state = 1'),
    ('m3', APP, MEDIA, 'x', 'PlaybackQueueInvalidation: NowPlayingItem for p changed from\n a\n -> b\n'),
)
LOOKALIKES = (
    ('x1', '/usr/sbin/CommCenter', '', '', 'startSending to: "x", validated 1 airdrop items. properties: y'),
    ('x2', SHARINGD, SHARE_SHEET, 'ShareSheet', 'Activating com.apple.sharing.sharesheet'),
    ('x3', APP, SHARING, 'AirDrop', 'Scanning mode Everyone'),
    ('x4', SHARINGD, SHARING, 'Daemon', 'Scanning mode Everyone'),
    ('x5', SHARINGD, '', '', 'prefix SharingDaemon State'),
    ('x6', SHARINGD, SHARING, 'AirDrop', 'Scanning modes'),
    ('x7', SHARINGD, SHARING, 'Daemon', 'Everyone mode expired'),
    ('y1', APP, MEDIA, 'x', IS_PLAYING),
    ('y2', MEDIAREMOTED, 'com.example.other', 'x', IS_PLAYING),
    ('y3', MEDIAREMOTED, MEDIA, 'x', 'power callback received'),
)


class AirDropMediaSelectionTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('''CREATE TABLE logarchive (row_number TEXT, process_image_path TEXT,
            subsystem TEXT, category TEXT, event_message TEXT)''')
        self.db.executemany('INSERT INTO logarchive VALUES (?,?,?,?,?)', AIRDROP_ROWS + MEDIA_ROWS + LOOKALIKES)
        source = pathlib.Path(module.__file__).read_text(encoding='utf-8')
        collection = source.split('def logarchive_artifacts', 1)[1].split("query = '''", 1)[1].split("'''", 1)[0]
        accelerated, _status = log_filter.accelerate_query(self.db, collection)
        rows = self.db.execute(accelerated).fetchall()
        self.db.execute('CREATE TABLE logarchive_artifacts AS SELECT * FROM logarchive WHERE 0')
        self.db.executemany('INSERT INTO logarchive_artifacts VALUES (?,?,?,?,?)', rows)

    def _selected(self, where):
        return {row[0] for row in self.db.execute(f'SELECT row_number FROM logarchive_artifacts WHERE {where}')}

    def test_airdrop_selects_its_writers_and_rejects_lookalikes(self):
        self.assertEqual(self._selected(module._AIRDROP_WHERE),  # pylint: disable=protected-access
                         {row[0] for row in AIRDROP_ROWS})

    def test_media_selects_its_writers_and_rejects_lookalikes(self):
        self.assertEqual(self._selected(module._MEDIA_WHERE),  # pylint: disable=protected-access
                         {row[0] for row in MEDIA_ROWS})


if __name__ == '__main__':
    unittest.main()
