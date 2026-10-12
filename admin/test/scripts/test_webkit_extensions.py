"""Regression tests for WebKit statistics, cache decoding and owner attribution."""
# pylint: disable=protected-access

import hashlib
import io
import json
import plistlib
import sqlite3
import struct
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.artifacts import webkitAdditionalCache as webkit
from scripts.artifacts import webkit as original_webkit
from scripts.artifacts import webkitResourceLoadStatistics as statistics
from scripts.context import Context
from scripts.search_files import FileSeekerZip
from scripts.webkit_helpers import WebKitOwnerResolver, unix_timestamp


def _plist(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps(value))
    return path


def _context(root, files, info):
    Context.clear()
    Context.set_data_folder(str(root))
    Context.set_files_found(list(map(str, files)))
    Context.set_artifact_info(info)
    return Context


def _run(root, files, module, name):
    result = getattr(module, name).__wrapped__(_context(root, files, module.__artifacts_v2__[name]))
    headers = [column[0] if isinstance(column, tuple) else column for column in result.headers]
    rows = list(result) if result else []
    assert all(len(row) == len(headers) for row in rows)
    return [dict(zip(headers, row)) for row in rows]


def _database(root, guid='DATA', store='Library/WebKit/WebsiteData'):
    path = root / 'private/var/mobile/Containers/Data/Application' / guid / store
    path = path / 'ResourceLoadStatistics/observations.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _schema(db):
    db.executescript('''
        CREATE TABLE ObservedDomains (
            domainID INTEGER PRIMARY KEY, registrableDomain TEXT,
            lastSeen REAL, hadUserInteraction INTEGER, mostRecentUserInteractionTime REAL,
            futureField TEXT);
        CREATE TABLE OperatingDates (year INTEGER, month INTEGER, monthDay INTEGER);
        CREATE TABLE SubresourceUnderTopFrameDomains (
            subresourceDomainID INTEGER, lastUpdated REAL, topFrameDomainID INTEGER,
            FOREIGN KEY(subresourceDomainID) REFERENCES ObservedDomains(domainID),
            FOREIGN KEY(topFrameDomainID) REFERENCES ObservedDomains(domainID));
    ''')


def _string(value, wide=False):
    if value is None:
        return struct.pack('<I', 0xffffffff)
    data = value.encode('utf-16-le' if wide else 'latin-1')
    units = len(data) // 2 if wide else len(data)
    return struct.pack('<I', units) + bytes([0 if wide else 1]) + data


def _cache_bytes(salt, uri='https://example.org/image.png', byte_range=None, headers=None,
                 version=16):
    headers = headers or {'Content-Type': 'image/png'}
    body = b'body'
    response = b'\0' + _string(uri) + _string('image/png') + struct.pack('<q', len(body))
    response += _string(None) + _string('') + _string('HTTP/1.1')
    response += struct.pack('<Q', len(headers))
    response += b''.join(_string(key) + _string(value) for key, value in headers.items())
    response += struct.pack('<H', 206) + b'\0' * 40
    record = struct.pack('<I', version)
    record += _string('example.org') + _string('Resource') + _string(uri) + _string(byte_range)
    record += b'K' * 20 + b'P' * 20 + struct.pack('<d', 1700000000.125)
    record += hashlib.sha1(salt + response).digest() + struct.pack('<Q', len(response))
    record += hashlib.sha1(salt + body).digest() + struct.pack('<Q', len(body))
    return record + b'\x01' + b'C' * 20 + response + body


def _cache_file(root, guid, salt, service=False):
    container = root / 'private/var/mobile/Containers/Data/Application' / guid
    store = (container / 'SystemData/com.apple.SafariViewService/Library/WebKit/WebsiteData'
             if service else container / 'Library/WebKit/WebsiteData')
    version = store / 'NetworkCache/Version 16'
    record = version / 'Records/PARTITION/Resource/RECORD'
    record.parent.mkdir(parents=True, exist_ok=True)
    (version / 'salt').write_bytes(salt)
    record.write_bytes(_cache_bytes(salt, byte_range='bytes=100-199'))
    return record, version / 'salt'


class WebKitExtensionTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.tmp_path = Path(folder.name)

    def test_invalid_and_sentinel_times_are_not_dates(self):
        for value in (None, 0, -1, float('nan'), float('inf'), 1e100, '1700000000', True):
            with self.subTest(value=value):
                assert unix_timestamp(value) is None

    def test_unix_fractional_seconds_are_preserved(self):
        assert unix_timestamp(1700000000.125) == datetime(2023, 11, 14, 22, 13, 20, 125000, timezone.utc)

    def test_zip_search_finds_direct_safari_view_statistics_and_wal(self):
        source = _database(self.tmp_path / 'source', store=(
            'SystemData/com.apple.SafariViewService/Library/WebKit/WebsiteData'))
        with sqlite3.connect(source) as db:
            _schema(db)
            db.execute('INSERT INTO ObservedDomains VALUES (1, ?, ?, 0, -1, ?)',
                       ('example.org', 1700000000.125, 'preserved'))
        source.with_name('observations.db-wal').write_bytes(b'')
        archive = self.tmp_path / 'input.zip'
        with ZipFile(archive, 'w') as output:
            for path in (source, source.with_name('observations.db-wal')):
                output.write(path, path.relative_to(self.tmp_path / 'source').as_posix())
        seeker = FileSeekerZip(str(archive), str(self.tmp_path / 'staged'))
        try:
            files = [path for pattern in statistics.__artifacts_v2__['webkit_observed_domains']['paths']
                     for path in seeker.search(pattern)]
            assert any(path.endswith('observations.db-wal') for path in files)
            row, = _run(self.tmp_path / 'staged', files, statistics, 'webkit_observed_domains')
            assert row['Domain'] == 'example.org'
            assert row['Web Data Store'] == 'SafariViewService'
        finally:
            seeker.cleanup()

    def test_old_schema_and_additional_values_are_retained(self):
        path = _database(self.tmp_path)
        with sqlite3.connect(path) as db:
            _schema(db)
            db.execute('INSERT INTO ObservedDomains VALUES (1, ?, ?, 0, -1, ?)',
                       ('example.org', 1700000000.125, 'preserved'))
        row, = _run(self.tmp_path, [path, path], statistics, 'webkit_observed_domains')
        assert row['Domain'] == 'example.org'
        assert row['Had User Interaction'] == 0
        assert row['Most Recent User Interaction'] is None
        assert row['Most Recent Web Push Interaction'] is None
        assert json.loads(row['Stored Values'])['futureField'] == 'preserved'
        assert json.loads(row['Stored Values'])['mostRecentUserInteractionTime'] == -1
        assert not row['Source File'].startswith(str(self.tmp_path))

    def test_operating_dates_use_zero_based_months_and_keep_invalid_rows(self):
        path = _database(self.tmp_path)
        with sqlite3.connect(path) as db:
            _schema(db)
            db.executemany('INSERT INTO OperatingDates VALUES (?, ?, ?)',
                           [(2024, 0, 1), (2024, 11, 31), (2024, 1, 29), (2023, 1, 29), (2024, -1, 1)])
        rows = _run(self.tmp_path, [path], statistics, 'webkit_operating_dates')
        assert [row['Operating Date'] for row in rows] == [
            '2024-01-01', '2024-12-31', '2024-02-29', None, None]
        assert rows[-1]['Date Status'] == 'Invalid stored date'
        assert json.loads(rows[-1]['Stored Values'])['month'] == -1

    def test_relationships_resolve_declared_foreign_keys_without_inventing_domains(self):
        path = _database(self.tmp_path)
        with sqlite3.connect(path) as db:
            _schema(db)
            db.executemany('INSERT INTO ObservedDomains VALUES (?, ?, 0, 0, -1, NULL)',
                           [(1, 'cdn.example.org'), (2, 'example.org')])
            db.executemany('INSERT INTO SubresourceUnderTopFrameDomains VALUES (?, ?, ?)',
                           [(1, 1700000000.25, 2), (99, 1700000000.5, 2)])
        rows = _run(self.tmp_path, [path], statistics, 'webkit_domain_relationships')
        assert json.loads(rows[0]['Resolved Domain Fields']) == {
            'subresourceDomainID': 'cdn.example.org', 'topFrameDomainID': 'example.org'}
        assert json.loads(rows[1]['Resolved Domain Fields'])['subresourceDomainID'] is None
        assert json.loads(rows[1]['Stored Values'])['subresourceDomainID'] == 99

    def test_rows_present_only_in_wal_are_read_without_changing_database_or_wal(self):
        path = _database(self.tmp_path)
        writer = sqlite3.connect(path)
        try:
            writer.execute('PRAGMA journal_mode=WAL')
            writer.execute('PRAGMA wal_autocheckpoint=0')
            _schema(writer)
            writer.commit()
            writer.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            writer.execute('INSERT INTO ObservedDomains VALUES (1, ?, ?, 1, ?, NULL)',
                           ('wal.example.org', 1700000000.125, 1700000000.25))
            writer.commit()
            wal = Path(str(path) + '-wal')
            before = [hashlib.sha256(p.read_bytes()).digest() for p in (path, wal)]
            with sqlite3.connect(path.as_uri() + '?immutable=1', uri=True) as db:
                assert db.execute('SELECT COUNT(*) FROM ObservedDomains').fetchone()[0] == 0
            rows = _run(self.tmp_path, [path, wal], statistics, 'webkit_observed_domains')
            assert rows[0]['Domain'] == 'wal.example.org'
            assert [hashlib.sha256(p.read_bytes()).digest() for p in (path, wal)] == before
        finally:
            writer.close()

    def test_owner_mapping_uses_container_metadata_and_acquired_display_names(self):
        container = self.tmp_path / 'private/var/mobile/Containers/Data/Application/APP'
        metadata = _plist(container / '.com.apple.mobile_container_manager.metadata.plist',
                          {'MCMMetadataIdentifier': 'org.example.reader'})
        info = _plist(self.tmp_path / 'private/var/containers/Bundle/Application/BUNDLE/Reader.app/Info.plist',
                      {'CFBundleIdentifier': 'org.example.reader', 'CFBundleDisplayName': 'Reader'})
        context = _context(self.tmp_path, [metadata, info], {'name': 'test'})
        resolver = WebKitOwnerResolver(context, [metadata, info])
        owner = resolver.resolve(container / 'SystemData/com.apple.SafariViewService/Library/WebKit/WebsiteData/file')
        assert owner[:5] == ('Reader', 'org.example.reader', 'APP', 'Data/Application', 'SafariViewService')
        assert str(self.tmp_path) not in owner[5]
        assert resolver.resolve(self.tmp_path / 'private/var/mobile/Containers/Data/Application/OTHER/file')[1] == ''
        assert resolver.resolve(self.tmp_path / 'private/var/mobile/Containers/Shared/AppGroup/APP/file')[1] == ''

    def test_group_identifier_is_not_reported_as_a_host_app(self):
        container = self.tmp_path / 'private/var/mobile/Containers/Shared/AppGroup/GROUP'
        metadata = _plist(container / '.com.apple.mobile_container_manager.metadata.plist',
                          {'MCMMetadataIdentifier': 'group.org.example.reader'})
        resolver = WebKitOwnerResolver(_context(self.tmp_path, [metadata], {'name': 'test'}), [metadata])
        assert resolver.resolve(container / 'Library/WebKit/WebsiteData/file')[:4] == (
            '', 'group.org.example.reader', 'GROUP', 'Shared/AppGroup')

    def test_webkit_string_encodings_are_preserved(self):
        for value, wide in (('café', False), ('漢字😀', True)):
            with self.subTest(value=value):
                assert webkit.read_vf(io.BytesIO(_string(value, wide)))[0] == value

    def test_cache_range_does_not_shift_timestamp_or_response_fields(self):
        path, salt = _cache_file(self.tmp_path, 'APP', b'12345678')
        values, offset = webkit._parse_record(path, salt.read_bytes())
        assert values['Byte Range'] == 'bytes=100-199'
        assert values['Timestamp'] == unix_timestamp(1700000000.125)
        assert values['Response Code'] == 206
        assert values['Header Hash Status'] == 'Verified'
        assert path.read_bytes()[offset:] == b'body'

    def test_cache_salts_are_scoped_to_store_and_do_not_leak_between_runs(self):
        normal, salt1 = _cache_file(self.tmp_path, 'APP', b'12345678')
        service, salt2 = _cache_file(self.tmp_path, 'APP', b'87654321', service=True)
        patcher = mock.patch.object(webkit, '_thumbnail', lambda *args: None)
        patcher.start()
        self.addCleanup(patcher.stop)
        rows = _run(self.tmp_path, [normal, salt1, service, salt2], webkit, 'webkit_additional_cache_records')
        assert len(rows) == 2
        assert {row['Salt'] for row in rows} == {'3132333435363738', '3837363534333231'}
        assert all(row['Header Hash Status'] == 'Verified' for row in rows)
        assert {row['Web Data Store'] for row in rows} == {'', 'SafariViewService'}
        row, = _run(self.tmp_path, [service], webkit, 'webkit_additional_cache_records')
        assert row['Salt'] == ''
        assert row['Header Hash Status'] == 'Salt not acquired'

    def test_more_than_one_hundred_response_headers_are_read(self):
        path = self.tmp_path / 'record'
        headers = {f'X-Header-{index}': str(index) for index in range(150)}
        path.write_bytes(_cache_bytes(b'12345678', headers=headers))
        values, _ = webkit._parse_record(path, b'12345678')
        assert len(json.loads(values['HTTP Headers'])) == 150
        assert values['Response Code'] == 206

    def test_corruption_and_unknown_versions_have_explicit_status(self):
        path = self.tmp_path / 'record'
        path.write_bytes(struct.pack('<I', 18))
        values, offset = webkit._parse_record(path, b'')
        assert values['Parse Status'] == 'Unsupported cache version 18'
        assert offset is None
        path.write_bytes(struct.pack('<I', 16) + struct.pack('<I', 0x7fffffff))
        values, _ = webkit._parse_record(path, b'')
        assert values['Parse Status'].startswith('Partial:')

    def test_version_17_records_are_decoded_with_the_version_16_layout(self):
        path = self.tmp_path / 'record'
        path.write_bytes(_cache_bytes(b'12345678', version=17))
        values, offset = webkit._parse_record(path, b'12345678')
        assert values['Header'] == 17
        assert values['URI'] == 'https://example.org/image.png'
        assert values['Header Hash Status'] == 'Verified'
        assert values['Parse Status'].startswith('Decoded fields')
        assert path.read_bytes()[offset:] == b'body'

    def test_response_hash_mismatch_is_reported(self):
        path, _ = _cache_file(self.tmp_path, 'APP', b'12345678')
        values, _ = webkit._parse_record(path, b'87654321')
        assert values['Header Hash Status'] == 'Mismatch'

    def test_additional_cache_does_not_repeat_original_cache_rows(self):
        service, service_salt = _cache_file(self.tmp_path, 'APP', b'12345678', service=True)
        original = (self.tmp_path / 'private/var/mobile/Containers/Data/Application/APP'
                    / 'Library/Caches/WebKit/NetworkCache/Version 16/Records/PARTITION/Resource/ORIGINAL')
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_bytes(service.read_bytes())
        original_salt = original.parents[3] / 'salt'
        original_salt.write_bytes(service_salt.read_bytes())
        patcher = mock.patch.object(webkit, '_thumbnail', lambda *args: None)
        patcher.start()
        self.addCleanup(patcher.stop)
        row, = _run(self.tmp_path, [original, original_salt, service, service_salt],
                    webkit, 'webkit_additional_cache_records')
        assert row['Web Data Store'] == 'SafariViewService'
        assert row['Full File Path'].endswith('Resource/RECORD')
        assert not _run(self.tmp_path, [original, original_salt], webkit,
                        'webkit_additional_cache_records')

    def test_original_artifact_registration_and_research_fields_are_preserved(self):
        assert set(original_webkit.__artifacts_v2__) == {'webkit_cache_records'}
        assert set(webkit.__artifacts_v2__) == {'webkit_additional_cache_records'}
        assert original_webkit.__artifacts_v2__['webkit_cache_records']['sample_data']
        assert original_webkit.__artifacts_v2__['webkit_cache_records']['author'] == '@JamesHabben'
        assert {'Marker', 'Marker Content Type', 'Marker2', 'Trailing Size', 'Trailing Hash',
                *[f'U{index}' for index in range(1, 9)]}.issubset(original_webkit.RESEARCH_HEADERS)


if __name__ == '__main__':
    unittest.main()
