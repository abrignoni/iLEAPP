"""Block reconstruction, failure isolation and real report integration tests."""
# pylint: disable=protected-access

import copy
import errno
import hashlib
import json
import os
import plistlib
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
from zipfile import ZipFile, ZIP_DEFLATED

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from scripts import webkit_media_cache as core
from scripts.artifacts import webkitMediaCache as artifact

MEDIA = REPO / 'admin/test/fixtures/webkitMediaCache/tone_test.mp4'
URL = 'https://example.org/test.mp4?a=1&b=2'
BASE = 'private/var/mobile/Containers/Data/Application'


def atom(kind, data):
    return struct.pack('>I4s', len(data) + 8, kind) + data


def cache_bytes(resource, url=URL, block_size=16384, omit=(), transform=None):
    """Encode independent test resources with reversed physical block order."""
    parts = [resource[start:start + block_size] for start in range(0, len(resource), block_size)]
    records = [(index, len(data), 8192 + (len(parts) - 1 - index) * block_size)
               for index, data in enumerate(parts) if index not in omit]
    if transform:
        records = transform(records)
    table = struct.pack('>I4sII', 5, b'crab', block_size, len(records))
    table += b''.join(struct.pack('>IIQ', *record) for record in records)
    identity = plistlib.dumps({'Size': len(resource), 'URL': url, 'Version': 1, 'no-cache': True})
    metadata = atom(b'verz', struct.pack('>I', 2)) + atom(b'stst', table) + atom(b'stid', identity)
    free = atom(b'frei', b'\x00' * (8192 - len(metadata) - 16))
    payload = b''.join(data.ljust(block_size, b'\x00') for data in reversed(parts))
    return free + metadata + atom(b'stcs', payload)


def stage(root, guid='APP-A', resource=None, url=URL, service=False):
    container = root / BASE / guid
    store = ('SystemData/com.apple.SafariViewService/Library/WebKit/WebsiteData/MediaCache'
             if service else 'tmp/WebKit/MediaCache')
    folder = container / store
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'CachedMedia-SAME'
    path.write_bytes(cache_bytes(MEDIA.read_bytes() if resource is None else resource, url))
    repo = folder / 'diskcacherepository.plist'
    repo.write_bytes(plistlib.dumps({'checkedinlist': {url: '/' + path.relative_to(root).as_posix()},
                                    'checkedoutlist': {}, 'lastmodtime': 700000000.125, 'lastmodpid': 35}))
    owner = container / '.com.apple.mobile_container_manager.metadata.plist'
    owner.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'org.example.' + guid}))
    return path, repo, owner


class FakeContext:
    def __init__(self, root, files):
        self.root = root
        self.files = files
        self.output = root.parent / (root.name + '-report')
        self.report = self.output / '_HTML/Browser'
        self.report.mkdir(parents=True, exist_ok=True)

    def get_files_found(self):
        return list(map(str, self.files))

    def get_report_folder(self):
        return str(self.report)

    def get_relative_path(self, path):
        for base in (self.root, self.output):
            try:
                return Path(path).relative_to(base).as_posix()
            except ValueError:
                pass
        return str(path)


def run_artifact(context):
    with mock.patch.object(artifact, 'check_in_media', return_value='media-reference'), \
         mock.patch.object(artifact, 'timeline') as timeline, \
         mock.patch.object(artifact, 'logfunc'):
        headers, rows, _ = artifact.webkit_media_cache.__wrapped__(context)
    names = [header[0] if isinstance(header, tuple) else header for header in headers]
    if any(len(row) != len(names) for row in rows):
        raise AssertionError('Header/row mismatch')
    return [dict(zip(names, row)) for row in rows], timeline


class MediaCacheCoreTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'CachedMedia-test'
        self.output = self.root / 'reconstructed'
        self.media = MEDIA.read_bytes()

    def read(self, content):
        self.source.write_bytes(content)
        return core.read_cache(self.source)

    def test_reversed_blocks_reconstruct_byte_for_byte_with_provenance(self):
        row = self.read(cache_bytes(self.media))
        before = self.source.read_bytes()
        mtime = self.source.stat().st_mtime_ns
        self.assertTrue(core.reconstruct(self.source, self.output, row))
        self.assertEqual(self.output.read_bytes(), self.media)
        self.assertEqual(row['output_sha256'], hashlib.sha256(self.media).hexdigest())
        self.assertEqual(row['output_md5'], hashlib.md5(self.media).hexdigest())
        for block in row['blocks']:
            data = before[block['source_offset']:block['source_offset'] + block['length']]
            self.assertEqual(hashlib.sha256(data).hexdigest(), block['sha256'])
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(self.source.stat().st_mtime_ns, mtime)

    def test_64k_blocks_are_supported(self):
        data = self.media * 4
        row = self.read(cache_bytes(data, block_size=65536))
        self.assertTrue(core.reconstruct(self.source, self.output, row))
        self.assertEqual(self.output.read_bytes(), data)

    def test_missing_middle_block_is_recorded_without_export(self):
        row = self.read(cache_bytes(self.media, omit=(1,)))
        self.assertEqual(row['missing_ranges'], [[16384, 32768]])
        self.assertFalse(core.reconstruct(self.source, self.output, row))
        self.assertFalse(self.output.exists())

    def test_short_nonfinal_block_leaves_a_gap(self):
        def shorten(records):
            records[0] = (0, 100, records[0][2])
            return records
        row = self.read(cache_bytes(self.media, transform=shorten))
        self.assertEqual(row['missing_ranges'], [[100, 16384]])

    def test_missing_tail_is_recorded(self):
        row = self.read(cache_bytes(self.media, omit=(2,)))
        self.assertEqual(row['missing_ranges'], [[32768, len(self.media)]])

    def test_no_block_table_entries_is_incomplete(self):
        row = self.read(cache_bytes(self.media, omit=(0, 1, 2)))
        self.assertEqual(row['covered_bytes'], 0)
        self.assertEqual(row['missing_ranges'], [[0, len(self.media)]])

    def test_bad_block_ranges_are_rejected(self):
        cases = {
            'duplicate logical': lambda rows: rows + [rows[0]],
            'outside payload': lambda rows: [(0, rows[0][1], 0)] + rows[1:],
            'overlap physical': lambda rows: [rows[0], (1, rows[1][1], rows[0][2])] + rows[2:],
            'beyond resource': lambda rows: [(100, 100, rows[0][2])] + rows[1:],
            'zero length': lambda rows: [(0, 0, rows[0][2])] + rows[1:],
            'excess length': lambda rows: [(0, 16385, rows[0][2])] + rows[1:],
        }
        for label, transform in cases.items():
            with self.subTest(label=label):
                row = self.read(cache_bytes(self.media, transform=transform))
                self.assertTrue(row['status'].startswith('Invalid or unsupported'))
                self.assertFalse(core.reconstruct(self.source, self.output, row))

    def test_versions_marker_and_blocksize_are_not_guessed(self):
        original = cache_bytes(self.media)
        mutations = [
            (original.index(b'verz') + 4, struct.pack('>I', 3)),
            (original.index(b'stst') + 4, struct.pack('>I', 6)),
            (original.index(b'crab'), b'xxxx'),
            (original.index(b'crab') + 4, struct.pack('>I', 4096)),
            (original.index(b'crab') + 8, struct.pack('>I', 0xffffffff)),
        ]
        for offset, value in mutations:
            with self.subTest(offset=offset):
                data = original[:offset] + value + original[offset + len(value):]
                self.assertTrue(self.read(data)['status'].startswith('Invalid or unsupported'))

    def test_duplicate_atoms_and_truncation_are_rejected(self):
        original = cache_bytes(self.media)
        for data in (original + atom(b'verz', b'\0\0\0\2'), original[:-1], original + b'x'):
            with self.subTest(length=len(data)):
                self.assertTrue(self.read(data)['status'].startswith('Invalid or unsupported'))

    def test_identity_version_size_and_type_are_validated(self):
        original = cache_bytes(self.media)
        mutations = [
            original.replace(b'<integer>1</integer>', b'<integer>2</integer>'),
            original.replace(b'<key>Size</key>', b'<key>OOPS</key>'),
            original.replace(b'<key>URL</key>', b'<key>XXX</key>'),
        ]
        self.assertIn('identity version', self.read(mutations[0])['status'])
        self.assertIn('resource size', self.read(mutations[1])['status'])
        self.assertEqual(self.read(mutations[2])['url'], '')

    def test_zero_and_unsupported_layouts_are_retained(self):
        self.assertEqual(self.read(b'\0' * 8192)['status'], 'Empty or all-zero cache file')
        self.assertEqual(self.read(b'')['status'], 'Empty or all-zero cache file')
        self.assertIn('Unsupported cache layout', self.read(b'not cache data')['status'])
        self.assertIn('Truncated', self.read(b'abc')['status'])

    def test_existing_destination_and_source_are_not_deleted(self):
        row = self.read(cache_bytes(self.media))
        before = self.source.read_bytes()
        self.assertFalse(core.reconstruct(self.source, self.source, row))
        self.assertEqual(self.source.read_bytes(), before)
        self.output.write_bytes(b'keep')
        row = core.read_cache(self.source)
        self.assertFalse(core.reconstruct(self.source, self.output, row))
        self.assertEqual(self.output.read_bytes(), b'keep')

    def test_source_change_discards_derivative(self):
        row = self.read(cache_bytes(self.media))
        with mock.patch.object(core, 'file_hashes', return_value={'sha256': 'changed'}):
            self.assertFalse(core.reconstruct(self.source, self.output, row))
        self.assertFalse(self.output.exists())
        self.assertIn('Source changed', row['status'])

    def test_stored_media_metadata_matches_generated_test_clip(self):
        info = core.media_info(MEDIA)
        self.assertEqual(info['kind'], 'Video')
        self.assertAlmostEqual(info['duration_seconds'], 2.0, places=3)
        self.assertEqual(len(info['tracks']), 2)
        video = info['tracks'][0]
        audio = info['tracks'][1]
        self.assertEqual((video['width'], video['height']), (128, 96))
        self.assertEqual(video['codecs'], ['avc1'])
        self.assertEqual(audio['codecs'], ['mp4a'])

    def test_unknown_resource_is_retained_as_binary(self):
        self.output.write_bytes(b'unknown resource')
        self.assertEqual(core.media_info(self.output)['extension'], 'bin')

    def test_output_io_error_does_not_publish_local_paths(self):
        row = self.read(cache_bytes(self.media))
        self.assertFalse(core.reconstruct(self.source, self.root / 'absent/output', row))
        self.assertIn('ENOENT', row['status'])
        self.assertNotIn(str(self.root), row['status'])
        self.assertTrue(self.source.exists())

    def test_media_info_io_error_does_not_publish_local_paths(self):
        info = core.media_info(self.root / 'missing/private-file')
        self.assertIn('ENOENT', info['validation'])
        self.assertNotIn(str(self.root), info['validation'])


class MediaCacheArtifactTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'input'
        self.root.mkdir()

    def test_one_selection_keeps_media_urls_owner_and_one_repository_event(self):
        paths = stage(self.root, service=True)
        context = FakeContext(self.root, paths + paths)
        rows, timeline = run_artifact(context)
        row, = rows
        self.assertEqual(row['Resource URL'], URL)
        self.assertEqual(row['Identifier'], 'org.example.APP-A')
        self.assertEqual(row['Web Data Store'], 'SafariViewService')
        self.assertIn('Exact stored path', row['Repository Association'])
        self.assertEqual(row['Recovered Media'], 'media-reference')
        args = timeline.call_args.args
        self.assertEqual(len(args[2]), 1)
        self.assertIn('Repository', args[1])
        proof = json.loads((context.output / row['Provenance File']).read_text())
        self.assertEqual(len(proof['blocks']), 3)
        self.assertEqual(proof['repository_raw_lastmodtime'], 700000000.125)
        self.assertNotIn(str(self.root), json.dumps(row, default=str))

    def test_same_filename_across_containers_never_cross_joins(self):
        first = stage(self.root, 'APP-A')
        second = stage(self.root, 'APP-B', url='https://example.org/other.mp4')
        rows, timeline = run_artifact(FakeContext(self.root, first + second))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(timeline.call_args.args[2]), 2)
        self.assertEqual({row['Identifier']: row['Resource URL'] for row in rows},
                         {'org.example.APP-A': URL, 'org.example.APP-B': 'https://example.org/other.mp4'})

    def test_absent_metadata_does_not_guess_owner(self):
        paths = stage(self.root)
        rows, _ = run_artifact(FakeContext(self.root, paths[:2]))
        self.assertEqual(rows[0]['Identifier'], '')
        self.assertEqual(rows[0]['Container GUID'], 'APP-A')

    def test_missing_index_does_not_block_recovery_or_invent_timeline(self):
        path, _, owner = stage(self.root)
        rows, timeline = run_artifact(FakeContext(self.root, (path, owner)))
        self.assertEqual(rows[0]['Recovered Media'], 'media-reference')
        self.assertEqual(rows[0]['Repository Source'], '')
        timeline.assert_not_called()

    def test_corrupt_index_does_not_block_recovery_or_invent_timeline(self):
        paths = stage(self.root)
        paths[1].write_bytes(b'not a plist')
        rows, timeline = run_artifact(FakeContext(self.root, paths))
        self.assertEqual(rows[0]['Recovered Media'], 'media-reference')
        self.assertIn('Invalid repository', json.loads(rows[0]['Metadata'])['repository_status'])
        timeline.assert_not_called()

    def test_unreadable_cache_retains_relative_source_and_does_not_stop_other_container(self):
        first = stage(self.root, 'APP-A')
        second = stage(self.root, 'APP-B')

        def read(path):
            if path == first[0]:
                raise PermissionError(errno.EACCES, 'Permission denied', str(path))
            return core.read_cache(path)

        with mock.patch.object(artifact, 'read_cache', side_effect=read):
            rows, _ = run_artifact(FakeContext(self.root, first + second))
        self.assertEqual(len(rows), 2)
        self.assertIn('EACCES', rows[0]['Recovery Status'])
        self.assertEqual(rows[0]['Recovered Media'], '')
        self.assertEqual(rows[1]['Recovered Media'], 'media-reference')
        self.assertNotIn(str(self.root), json.dumps(rows, default=str))

    def test_unreadable_repository_retains_media_without_publishing_local_paths(self):
        paths = stage(self.root)
        error = PermissionError(errno.EACCES, 'Permission denied', str(paths[1]))
        with mock.patch.object(artifact, 'file_hashes', side_effect=error):
            rows, timeline = run_artifact(FakeContext(self.root, paths))
        self.assertEqual(rows[0]['Recovered Media'], 'media-reference')
        self.assertIn('EACCES', rows[0]['Metadata'])
        self.assertNotIn(str(self.root), json.dumps(rows, default=str))
        timeline.assert_not_called()

    def test_missing_files_are_retained_as_references_not_found_in_other_container(self):
        first = stage(self.root, 'APP-A')
        second = stage(self.root, 'APP-B')
        first[0].unlink()
        rows, _ = run_artifact(FakeContext(self.root, first[1:] + second))
        missing = [row for row in rows if 'not acquired' in row['Recovery Status']]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]['Identifier'], 'org.example.APP-A')
        self.assertEqual(missing[0]['Recovered Media'], '')

    def test_stale_container_guid_requires_url_corroboration(self):
        paths = stage(self.root)
        repo = plistlib.loads(paths[1].read_bytes())
        repo['checkedinlist'][URL] = repo['checkedinlist'][URL].replace('APP-A', 'OLD-APP')
        paths[1].write_bytes(plistlib.dumps(repo))
        rows, _ = run_artifact(FakeContext(self.root, paths))
        self.assertIn('filename and identity URL', rows[0]['Repository Association'])
        self.assertIn('stored path differs', rows[0]['Repository Association'])

    def test_conflicting_query_tokens_remain_distinct(self):
        paths = stage(self.root)
        repo = plistlib.loads(paths[1].read_bytes())
        stored = repo['checkedinlist'].pop(URL)
        other = URL + '&token=other'
        repo['checkedinlist'][other] = stored
        paths[1].write_bytes(plistlib.dumps(repo))
        rows, _ = run_artifact(FakeContext(self.root, paths))
        self.assertEqual(rows[0]['Resource URL'], URL)
        self.assertEqual(rows[0]['Repository URLs'], other)
        self.assertIn('conflicts', rows[0]['Repository Association'])

    def test_checkedout_prefix_is_removed_but_original_key_preserved(self):
        paths = stage(self.root)
        repo = plistlib.loads(paths[1].read_bytes())
        stored = repo['checkedinlist'].pop(URL)
        key = '12345678-1234-1234-1234-123456789abc=' + URL
        repo['checkedoutlist'][key] = stored
        paths[1].write_bytes(plistlib.dumps(repo))
        rows, _ = run_artifact(FakeContext(self.root, paths))
        self.assertEqual(rows[0]['Repository URLs'], URL)
        self.assertEqual(json.loads(rows[0]['Metadata'])['repository_references'][0]['key'], key)

    def test_index_timestamp_is_repository_level_with_fractional_precision(self):
        expected = datetime(2023, 3, 8, 20, 26, 40, 125000, timezone.utc)
        self.assertEqual(artifact.repository_time(700000000.125), expected)
        for value in (None, True, 0, -1, float('nan'), float('inf'), 1e100, '700000000'):
            with self.subTest(value=value):
                self.assertIsNone(artifact.repository_time(value))

    def test_all_zero_entries_keep_repository_urls_with_no_resource_claim(self):
        paths = stage(self.root)
        paths[0].write_bytes(b'\0' * 8192)
        rows, _ = run_artifact(FakeContext(self.root, paths))
        self.assertEqual(rows[0]['Resource URL'], '')
        self.assertEqual(rows[0]['Repository URLs'], URL)
        self.assertEqual(rows[0]['Recovered Media'], '')

    def test_empty_index_is_visible(self):
        path, repo, owner = stage(self.root)
        path.unlink()
        value = plistlib.loads(repo.read_bytes())
        value['checkedinlist'] = {}
        repo.write_bytes(plistlib.dumps(value))
        rows, timeline = run_artifact(FakeContext(self.root, (repo, owner)))
        self.assertIn('no cache references', rows[0]['Recovery Status'])
        self.assertEqual(len(timeline.call_args.args[2]), 1)

    def test_repeated_run_preserves_outputs(self):
        paths = stage(self.root)
        context = FakeContext(self.root, paths)
        rows1, _ = run_artifact(context)
        rows2, _ = run_artifact(context)
        self.assertEqual(rows1, rows2)

    def test_no_global_context_mutation_in_undecorated_parser(self):
        from scripts.context import Context
        before = {name: value for name, value in vars(Context).items()
                  if name.startswith('_') and not name.startswith('__') and not callable(value)}
        snapshots = {name: copy.deepcopy(value) for name, value in before.items()
                     if type(value) in (dict, list, set, tuple)}
        run_artifact(FakeContext(self.root, stage(self.root)))
        for name, value in before.items():
            self.assertIs(getattr(Context, name), value, name)
        for name, value in snapshots.items():
            self.assertTrue(getattr(Context, name) == value, name)

    def test_two_evidence_roots_with_identical_guids_keep_separate_owners(self):
        first = stage(self.root / 'image-a', 'SAME')
        second = stage(self.root / 'image-b', 'SAME')
        second[2].write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'org.example.other'}))
        rows, _ = run_artifact(FakeContext(self.root, first + second))
        self.assertEqual({row['Identifier'] for row in rows}, {'org.example.SAME', 'org.example.other'})


class MediaCacheReportIntegrationTests(unittest.TestCase):
    def test_cli_zip_writes_lava_media_and_repository_timeline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = stage(root / 'input', 'APP-A')
            second = stage(root / 'input', 'APP-B', service=True)
            archive = root / 'input.zip'
            with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
                for path in first + second:
                    output.write(path, path.relative_to(root / 'input').as_posix())
            profile = root / 'profile.ilprofile'
            profile.write_text(json.dumps({'leapp': 'ileapp', 'format_version': 1,
                                           'plugins': ['webkit_media_cache']}))
            result = subprocess.run([sys.executable, str(REPO / 'ileapp.py'), '-t', 'zip',
                                     '-i', str(archive), '-o', str(root), '-m', str(profile),
                                     '--custom_output_folder', 'report'], cwd=REPO,
                                    capture_output=True, text=True, timeout=120, check=False,
                                    env={**os.environ, 'TZ': 'UTC'})
            self.assertEqual(result.returncode, 0, result.stdout[-3500:] + result.stderr[-1500:])
            report = root / 'report'
            with sqlite3.connect(report / '_lava_artifacts.db') as db:
                rows = db.execute('SELECT recovery_status, output_sha256, resource_url '
                                  'FROM webkit_media_cache').fetchall()
                self.assertEqual(len(rows), 2)
                self.assertTrue(all(row[0].startswith('Reconstructed') for row in rows))
                media = db.execute('SELECT extraction_path, source_path FROM _lava_media_items').fetchall()
                self.assertEqual(len(media), 2)
                for relative, source in media:
                    self.assertEqual((report / relative).read_bytes(), MEDIA.read_bytes())
                    self.assertIn('/MediaCache/CachedMedia-SAME', source)
                    self.assertNotIn(str(root), source)
            with sqlite3.connect(report / '_Timeline/tl.db') as db:
                events = db.execute('SELECT key, activity, datalist FROM data').fetchall()
                self.assertEqual(len(events), 2)
                self.assertTrue(all('Repository Last Modified' in row[1] for row in events))
                self.assertTrue(all('.125000' in row[0] for row in events))
            manifest = json.loads((report / '_lava_data.lava').read_text())
            tables = [item for items in manifest['artifacts'].values() for item in items
                      if item.get('tablename') == 'webkit_media_cache']
            self.assertEqual(tables[0]['record_count'], 2)
            self.assertTrue(list((report / '_TSV Exports').glob('*Media Cache*.tsv')))
            page = next(path for path in (report / '_HTML').rglob('*.html')
                        if path.stem.replace('_', ' ') == 'WebKit - Media Cache').read_text()
            self.assertIn('<video', page)
            self.assertIn('a=1&amp;b=2', page)


if __name__ == '__main__':
    unittest.main()
