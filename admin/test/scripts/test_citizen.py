"""Citizen container isolation and URL cache rows, with synthetic SQLite and plist inputs."""
from contextlib import closing
import json
from pathlib import Path
import plistlib
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts import citizen


API = 'https://data.sp0n.io'
MAP = API + '/v3/homescreen/mapIncidents'


class CitizenTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.files = []
        self.context = SimpleNamespace(get_files_found=lambda: self.files,
                                       get_relative_path=lambda f: Path(f).relative_to(self.root).as_posix())

    def file(self, container, suffix):
        path = self.root / 'private/var/mobile/Containers/Data/Application' / container / 'Library' / suffix
        path.parent.mkdir(parents=True, exist_ok=True)
        self.files.append(str(path))
        return path

    def preferences(self, container):
        locations = json.dumps([{'storedAt': 10.125}])
        history = json.dumps([{'viewedAt': 10.125, 'id': 'common'}])
        self.file(container, 'Preferences/com.sp0n.vigilante.plist').write_bytes(plistlib.dumps({
            'com.citizen.location.coldLaunchLocations': locations.encode(),
            'com.citizen.recently_viewed_incidents': history,
        }))

    def cache(self, container, entries, with_receiver=True):
        path = self.file(container, 'Caches/com.sp0n.vigilante/Cache.db')
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY, time_stamp, request_key)')
            if with_receiver:
                db.execute('CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER PRIMARY KEY, isDataOnFS, receiver_data)')
            for i, (url, data, external) in enumerate(entries, 1):
                db.execute('INSERT INTO cfurl_cache_response VALUES (?, ?, ?)', (i, '2026-01-01 02:00:00.125+02:00', url))
                if with_receiver:
                    payload = json.dumps(data).encode()
                    if external:
                        self.file(container, 'Caches/com.sp0n.vigilante/fsCachedData/body').write_bytes(payload)
                        payload = b'body'
                    db.execute('INSERT INTO cfurl_cache_receiver_data VALUES (?, ?, ?)', (i, int(external), payload))
            db.commit()

    def rows(self, artifact):
        headers, rows, _ = artifact.__wrapped__(self.context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(names, r, strict=True)) for r in rows]

    def test_titles_and_preferences_are_scoped_to_their_container(self):
        for name in ('A', 'B', 'C'):
            self.preferences(name)
            if name != 'C':
                self.cache(name, [(MAP, {'incidents': [{'incidentId': 'common', 'title': name}]}, name == 'B'),
                                  ('https://example.org/v3/homescreen/mapIncidents',
                                   {'incidents': [{'incidentId': 'common', 'title': 'unrelated'}]}, False)])
        locations = self.rows(citizen.citizenColdLaunchLocations)
        self.assertEqual(len(locations), 3)
        self.assertEqual(len({row['Source File'] for row in locations}), 3)
        history = self.rows(citizen.citizenIncidentHistory)
        self.assertEqual({r['Source File'].split('/')[-4]: r['Title'] for r in history}, {'A': 'A', 'B': 'B', 'C': ''})
        self.assertEqual(len(self.rows(citizen.citizenMapIncidents)), 2)

    def test_conflicting_titles_and_unrelated_endpoints(self):
        self.preferences('A')
        def response(title):
            return {'incidents': [{'incidentId': 'common', 'title': title, 'subcategory': 'fixture'}]}
        self.cache('A', [(MAP, response('first'), False), (MAP+'?page=2', response('second'), False),
                         (MAP+'Archive', response('other'), False), (API+'/v1/user/requested', {'id': 'returned', 'username': 'sample',
                                                           'plus': {'active': True, 'other': 2}}, False),
                         (API+'/v1/user/missing', {'error': 'not found'}, False)])
        self.assertEqual(self.rows(citizen.citizenIncidentHistory)[0]['Title'], '')
        maps = self.rows(citizen.citizenMapIncidents)
        self.assertEqual([r['Cache Entry ID'] for r in maps], [1, 2])
        self.assertEqual(json.loads(maps[0]['Other Incident Fields']), {'subcategory': 'fixture'})
        profile, = self.rows(citizen.citizenAccount)
        self.assertEqual(profile['username'], 'sample')
        self.assertEqual(json.loads(profile['Other Profile Fields']), {'plus': {'other': 2}})
        self.assertEqual((profile['Requested User ID'], profile['id']), ('requested', 'returned'))

    def test_requests_without_receiver_table_and_repeated_parameters(self):
        self.cache('A', [('https://DATA.SP0N.IO:443/test?q=first&q=second', {}, False),
                         ('https://[bad', {}, False)], with_receiver=False)
        request, = self.rows(citizen.citizenCachedRequests)
        self.assertEqual(json.loads(request['Search Query']), ['first', 'second'])
        self.assertEqual(request['Cached At'].isoformat(), '2026-01-01T00:00:00.125000+00:00')


if __name__ == '__main__':
    unittest.main()
