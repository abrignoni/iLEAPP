#!/usr/bin/env python3
"""Build a SYNTHETIC extraction holding the files the Craigslist artifacts read.

Everything here is fabricated: queries are fixed phrases, places are an invented town on the reserved
.invalid domain, coordinates are round numbers, posting ids are made up, and times are fixed offsets
from one base date. Nothing comes from a real device. The layout follows what the artifacts read:

* Library/Application Support/org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/: a
  manifest.json holding persist:chat and startupLog inline and null for persist:search and persist:root,
  and the two files named with the MD5 of those keys, the form React Native uses for a large value.
* Library/Caches/org.craigslist.CraigslistMobile/Cache.db: the cfurl_cache_* tables with suggestion,
  search, category-count and posting-detail requests, one detail response kept on disk (isDataOnFS).
* Library/Preferences/org.craigslist.CraigslistMobile.plist with a fabricated deviceUID.

    python synthetic_craigslist.py out.zip

``build(zip_path)`` writes the zip and returns {name: expected} counts the tests compare against.
"""
import hashlib
import json
import os
import plistlib
import sqlite3
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

BUNDLE = 'org.craigslist.CraigslistMobile'
CONTAINER = 'private/var/mobile/Containers/Data/Application/00000000-0000-4000-8000-000000000001'
BASE = int(datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc).timestamp())  # Unix seconds

LOCATION = {'areaId': 1, 'subareaId': 0, 'city': 'Exampleville', 'country': 'US', 'postal': '00000',
            'region': 'EX', 'url': 'https://exampleville.example.invalid', 'lat': 10.5, 'lon': 20.5,
            'radius': 25.0}
POSTING_IDS = ('9000000001', '9000000002', '9000000003')


def md5_name(key):
    return hashlib.md5(key.encode('utf-8')).hexdigest()


def search_state():
    recent = [
        {'catabbr': 'sss', 'categoryLabels': ['for sale'], 'params': {'query': 'synthetic desk'},
         'humanReadableParams': [{'key': 'query', 'name': 'search', 'value': 'synthetic desk'},
                                 {'key': 'search_distance', 'name': 'distance', 'value': '25'}],
         'location': LOCATION, 'timestamp': (BASE + 60) * 1000},
        {'catabbr': 'bbb', 'categoryLabels': ['services', 'household'], 'params': {'query': 'example painter'},
         'humanReadableParams': [{'key': 'query', 'name': 'search', 'value': 'example painter'}],
         'location': LOCATION, 'timestamp': (BASE + 120) * 1000},
        # an entry with no location and no filters
        {'catabbr': 'ccc', 'params': {'query': 'sample bicycle'}, 'timestamp': (BASE + 180) * 1000},
    ]
    return {'viewMode': 'list', 'recentSearches': recent,
            'visitedPostings': {POSTING_IDS[0]: (BASE + 300) * 1000, POSTING_IDS[1]: (BASE + 360) * 1000,
                                POSTING_IDS[2]: (BASE + 420) * 1000, '9000000099': (BASE + 480) * 1000},
            'postingsNotFound': {}, 'postingViewTelemetrySent': {POSTING_IDS[0]: 1},
            'showingMap': False, '_persist': {'version': 2, 'rehydrated': True}}


def root_state():
    favorite = {'categoryAbbr': 'sss', 'categoryId': '9', 'dedupeKey': 'x', 'images': [],
                'location': {'areaId': 1, 'description': 'Example Heights', 'hostname': 'exampleville',
                             'lat': 10.5, 'lon': 20.5, 'subareaAbbr': 'ex'},
                'postedDate': BASE - 3600, 'postingId': int(POSTING_IDS[0]),
                'postingUuid': '00000000-0000-4000-8000-0000000000aa', 'remuneration': '$10',
                'seo': 'synthetic-desk', 'title': 'Synthetic desk'}
    return {
        'config': {'appVersion': '1.29.1-synthetic', 'configTs': BASE + 5, 'translations': {'Apr': 'Apr'}},
        'permissions': {'camera': 'undetermined', 'location': 'blocked', 'notification': 'granted'},
        'tokens': {'accessToken': 'SYNTHETIC-NOT-A-TOKEN', 'browserCookie': 'SYNTHETIC-NOT-A-COOKIE',
                   'pushToken': None},
        'user': {'login': 'owner@example.invalid', 'isLoggedIn': True, 'emailAppToUse': 'standard',
                 'colorSchemeOverride': 'system', 'location': LOCATION, 'pushTokenSent': 'unsynched',
                 'savedSearches': {
                     'favorites': [favorite],
                     'hidden': [{'postingId': 9000000050, 'title': 'Synthetic hidden posting'}],
                     'searches': [{'name': 'synthetic saved search', 'query': 'example lamp'}],
                     'favoriteLookup': {POSTING_IDS[0]: 'unsynched'}, 'hiddenLookup': {}},
                 'ratingStatus': {'daysInARow': 2, 'lastDayIUsedTheApp': (BASE + 600) * 1000,
                                  'gotStartupPrompt': (BASE + 660) * 1000, 'gotDeletePrompt': 0,
                                  'didRating': 0}},
        '_persist': {'version': 2, 'rehydrated': True}}


def manifest(startup):
    return {'persist:search': None, 'persist:root': None,
            'persist:chat': json.dumps({'chats': {}, 'messages': {}}),
            'startupLog': startup}


def startup_log():
    stamps = ['2026-03-01T12:10:00.000Z', '2026-03-01T12:10:00.100Z', '2026-03-01T12:10:01.200Z',
              '2026-03-01T12:10:02.300Z', '2026-03-01T12:10:03.400Z']
    lines = [f'{stamps[0]}\tInit Log File\t', f'{stamps[1]}\tsetAppMode\tinit', f'{stamps[2]}\tsetAppMode\tonboarding',
             f'{stamps[3]}\tsetAppMode\ttab', f'{stamps[4]}\tSTARTUP COMPLETE\tAppReadyListener']
    return '\n,'.join(lines) + '\n'


def detail_item(posting_id, title, price, kind):
    item = {'attributes': [], 'body': f'Synthetic body for {title}.', 'category': 'furniture',
            'categoryAbbr': 'fua', 'categoryId': 9, 'hasContactInfo': True, 'images': ['3:a', '3:b'],
            'location': {'area': 'Exampleville', 'areaAbbr': 'ex', 'areaId': 1, 'description': 'Example Heights',
                         'lat': 10.5, 'lon': 20.5, 'neighborhood': 'Example Heights', 'type': kind},
            'notices': [], 'postedDate': BASE - 7200, 'postingId': int(posting_id), 'recordCreated': BASE - 9000,
            'section': 'for sale', 'title': title, 'updatedDate': BASE - 3600,
            'url': f'https://exampleville.example.invalid/fua/d/{posting_id}.html'}
    if price:
        item['priceString'] = price
    return item


def cache_db(path):
    db = sqlite3.connect(path)
    db.executescript('''
        CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, version INTEGER,
            hash_value INTEGER, storage_policy INTEGER, request_key TEXT UNIQUE,
            time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP, partition TEXT);
        CREATE TABLE cfurl_cache_blob_data(entry_ID INTEGER PRIMARY KEY, response_object BLOB,
            request_object BLOB, proto_props BLOB, user_info BLOB);
        CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER PRIMARY KEY, isDataOnFS INTEGER,
            receiver_data BLOB);
    ''')
    base = 'https://sapi.example.invalid'
    rows = [
        (f'{base}/v8/suggest/search?cc=us&lang=en&query=synthetic%20de&catabbr=sss', '2026-03-01 12:01:00', None),
        (f'{base}/v8/suggest/search?cc=us&lang=en&query=synthetic%20desk', '2026-03-01 12:01:05', None),
        (f'{base}/v8/categories/count?areaId=1&cc=us&lang=en&lat=10.5&lon=20.5&query=synthetic%20desk'
         '&search_distance=25', '2026-03-01 12:01:10', None),
        (f'{base}/v8/postings/sss/search?area_id=1&batchSize=20&cc=us&lang=en&lat=10.5&lon=20.5'
         '&query=synthetic%20desk&search_distance=25&startIndex=0', '2026-03-01 12:01:15', 1),
        ('https://rapi.example.invalid/v8/postings/exampleville/-/fua/%s?cc=us&lang=en' % POSTING_IDS[0],
         '2026-03-01 12:05:00', json.dumps({'data': {'items': [detail_item(POSTING_IDS[0], 'Synthetic desk',
                                                                              '$10', 'pin')]}})),
        ('https://rapi.example.invalid/v8/postings/exampleville/-/fua/%s?cc=us&lang=en' % POSTING_IDS[1],
         '2026-03-01 12:06:00', json.dumps({'data': {'items': [detail_item(POSTING_IDS[1], 'Synthetic chair',
                                                                              None, 'area')]}})),
        # body kept in an fsCachedData file, nothing to parse in the database
        ('https://rapi.example.invalid/v8/postings/exampleville/-/fua/%s?cc=us&lang=en' % POSTING_IDS[2],
         '2026-03-01 12:07:00', 'ONDISK'),
        # not search related and not a posting detail: both artifacts must ignore it
        ('https://rapi.example.invalid/v8/config?configId=synthetic', '2026-03-01 12:00:30', None),
    ]
    for index, (url, stamp, body) in enumerate(rows, start=1):
        db.execute('INSERT INTO cfurl_cache_response VALUES (?,?,?,?,?,?,?)', (index, 0, index, 0, url, stamp, None))
        db.execute('INSERT INTO cfurl_cache_blob_data VALUES (?,?,?,?,?)', (index, b'x', b'x', None, None))
        if body == 'ONDISK':
            db.execute('INSERT INTO cfurl_cache_receiver_data VALUES (?,?,?)', (index, 1, b'\x00' * 8))
        elif body == 1:
            db.execute('INSERT INTO cfurl_cache_receiver_data VALUES (?,?,?)',
                       (index, 0, json.dumps({'data': {'items': ['x']}}).encode()))
        else:
            db.execute('INSERT INTO cfurl_cache_receiver_data VALUES (?,?,?)',
                       (index, 0, body.encode() if body else b'{}'))
    db.commit()
    db.close()


def build(zip_path):
    folder = tempfile.mkdtemp()
    cache = os.path.join(folder, 'Cache.db')
    cache_db(cache)
    asyncdir = f'{CONTAINER}/Library/Application Support/{BUNDLE}/RCTAsyncLocalStorage_V1'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f'{asyncdir}/manifest.json', json.dumps(manifest(startup_log())))
        zf.writestr(f'{asyncdir}/{md5_name("persist:search")}', json.dumps(search_state()))
        zf.writestr(f'{asyncdir}/{md5_name("persist:root")}', json.dumps(root_state()))
        zf.write(cache, f'{CONTAINER}/Library/Caches/{BUNDLE}/Cache.db')
        zf.writestr(f'{CONTAINER}/Library/Preferences/{BUNDLE}.plist',
                    plistlib.dumps({'deviceUID': 'SYNTHETIC-DEVICE-UID-0001',
                                    'RCTI18nUtil_makeRTLFlipLeftAndRightStyles': False}))
    os.remove(cache)
    os.rmdir(folder)
    return {'recent_searches': 3, 'visited_postings': 4, 'visited_with_cached_title': 2, 'saved_items': 3,
            'startup_log': 5, 'cached_searches': 4, 'cached_postings': 2, 'cached_postings_on_disk': 1}


if __name__ == '__main__':
    build(sys.argv[1])
