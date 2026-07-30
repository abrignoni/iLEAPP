"""Cover the native Apple Unified Log import and the streaming LAVA writer behind it.

Two things here are easy to break and expensive to notice.

The first is memory. The logarchive artifact imports tens of millions of records, and
artifact_processor materializes every row twice: once as the returned data_list and again
as the converted rows lava_insert_sqlite_data builds before executemany(). At ~617 bytes
per row that is roughly 19 GB for a 31M row import and ~39 GB at peak, which is why the
artifact uses artifact_processor_streaming instead. Nothing in a normal test run would
catch a regression back to list building, so the streaming decorator is tested directly:
it must never pull more than one batch of rows into memory at a time.

The second is the table contract. Twelve dependent artifacts all query `FROM logarchive`
with LIKE predicates against the same eight columns. Whether the rows came from Apple's
json export or from tracev3 data read natively, the column order and meaning have to be
identical or those artifacts silently return nothing.
"""
import datetime
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts import unifiedlogs  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import artifact_processor_streaming  # pylint: disable=wrong-import-position


class TestIteratorTimestamp(unittest.TestCase):
    """unifiedlog_iterator emits nanosecond RFC 3339 timestamps that 3.10 cannot parse."""

    def test_nanosecond_precision_is_accepted(self):
        parsed = logarchive.parse_iterator_timestamp('2026-07-29T14:11:07.452774400Z')
        self.assertEqual(parsed,
                         datetime.datetime(2026, 7, 29, 14, 11, 7, 452774,
                                           tzinfo=datetime.timezone.utc))

    def test_result_is_utc(self):
        # The parser always emits UTC; tagging it as such is what stops lava_insert_sqlite_data
        # from reading the value in the examiner machine's local timezone.
        parsed = logarchive.parse_iterator_timestamp('2026-01-01T00:00:00.000000000Z')
        self.assertEqual(parsed.utcoffset(), datetime.timedelta(0))

    def test_microsecond_and_second_precision_still_parse(self):
        self.assertEqual(logarchive.parse_iterator_timestamp('2026-07-29T14:11:07.452774Z').second, 7)
        self.assertEqual(logarchive.parse_iterator_timestamp('2026-07-29T14:11:07Z').minute, 11)

    def test_unparsable_input_yields_empty_rather_than_raising(self):
        # A single malformed record must not abort an import of millions.
        self.assertEqual(logarchive.parse_iterator_timestamp('not a timestamp'), '')
        self.assertEqual(logarchive.parse_iterator_timestamp(''), '')


class TestArchiveRootDiscovery(unittest.TestCase):
    """The parser needs directory roots, but the seeker hands back individual file paths."""

    def test_finds_diagnostics_and_uuidtext_roots(self):
        found = [
            '/case/data/private/var/db/diagnostics/Persist/0000000000000001.tracev3',
            '/case/data/private/var/db/diagnostics/timesync/0000000000000002.timesync',
            '/case/data/private/var/db/uuidtext/dsc/ABCDEF',
            '/case/data/private/var/db/uuidtext/00/1122334455',
        ]
        archive, diagnostics, uuidtext = unifiedlogs.find_archive_roots(found)
        self.assertIsNone(archive)
        self.assertEqual(diagnostics, '/case/data/private/var/db/diagnostics')
        self.assertEqual(uuidtext, '/case/data/private/var/db/uuidtext')

    def test_ready_made_logarchive_is_used_directly(self):
        # An examiner who already built a .logarchive should not have it reassembled.
        found = ['/case/device.logarchive/Persist/0000000000000001.tracev3',
                 '/case/device.logarchive/dsc/ABCDEF']
        archive, diagnostics, uuidtext = unifiedlogs.find_archive_roots(found)
        self.assertEqual(archive, '/case/device.logarchive')
        self.assertIsNone(diagnostics)
        self.assertIsNone(uuidtext)


class TestArchiveAssembly(unittest.TestCase):
    """diagnostics/ and uuidtext/ contents must merge into the single directory the parser wants."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, True)
        self.diagnostics = os.path.join(self.tmpdir, 'diagnostics')
        self.uuidtext = os.path.join(self.tmpdir, 'uuidtext')
        os.makedirs(os.path.join(self.diagnostics, 'Persist'))
        os.makedirs(os.path.join(self.diagnostics, 'timesync'))
        os.makedirs(os.path.join(self.uuidtext, 'dsc'))
        os.makedirs(os.path.join(self.uuidtext, '1A'))
        with open(os.path.join(self.diagnostics, 'Persist', '01.tracev3'), 'wb') as handle:
            handle.write(b'tracev3')
        with open(os.path.join(self.uuidtext, 'dsc', 'ABC'), 'wb') as handle:
            handle.write(b'dsc')

    def test_contents_of_both_directories_appear_at_the_root(self):
        workdir = unifiedlogs.assemble_archive(
            self.diagnostics, self.uuidtext, os.path.join(self.tmpdir, 'assembled'))
        entries = sorted(os.listdir(workdir))
        self.assertEqual(entries, ['1A', 'Persist', 'dsc', 'timesync'])
        # Contents have to be reachable through the assembled tree, not just the names.
        with open(os.path.join(workdir, 'Persist', '01.tracev3'), 'rb') as handle:
            self.assertEqual(handle.read(), b'tracev3')

    def test_assembly_is_repeatable(self):
        # Two runs against the same output folder must not fail on existing entries.
        target = os.path.join(self.tmpdir, 'assembled')
        unifiedlogs.assemble_archive(self.diagnostics, self.uuidtext, target)
        unifiedlogs.assemble_archive(self.diagnostics, self.uuidtext, target)
        self.assertEqual(len(os.listdir(target)), 4)


class TestBinaryDiscovery(unittest.TestCase):
    """A missing binary must degrade to 'not available', never to a crash."""

    def setUp(self):
        self.original = os.environ.get(unifiedlogs.BINARY_ENV_VAR)
        self.addCleanup(self._restore)

    def _restore(self):
        if self.original is None:
            os.environ.pop(unifiedlogs.BINARY_ENV_VAR, None)
        else:
            os.environ[unifiedlogs.BINARY_ENV_VAR] = self.original

    def test_env_var_pointing_at_nothing_returns_none(self):
        os.environ[unifiedlogs.BINARY_ENV_VAR] = '/nonexistent/unifiedlog_iterator'
        self.assertIsNone(unifiedlogs.find_iterator())

    def test_env_var_pointing_at_an_executable_wins(self):
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, True)
        fake = os.path.join(tmpdir, 'unifiedlog_iterator')
        with open(fake, 'w', encoding='utf-8') as handle:
            handle.write('#!/bin/sh\n')
        os.chmod(fake, 0o755)
        os.environ[unifiedlogs.BINARY_ENV_VAR] = fake
        self.assertEqual(unifiedlogs.find_iterator(), fake)


__artifacts_v2__ = {
    'streaming_probe': {
        'name': 'streaming probe',
        'description': 'test fixture',
        'category': 'Unified Logs',
        'paths': None,
        'output_types': 'lava_only',
        'artifact_icon': 'database',
    },
}


class TestStreamingWriter(unittest.TestCase):
    """artifact_processor_streaming must write everything without ever holding everything."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, True)
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self.addCleanup(Context.clear)

    def _run(self, row_count):
        """Run the decorator over a generator, tracking how far ahead it consumes."""
        headers = (('Timestamp', 'datetime'), 'Row Number', 'Event Message')
        state = {'produced': 0, 'max_outstanding': 0}
        written = {'count': 0}

        original_insert = lavafuncs.lava_insert_sqlite_data

        def counting_insert(table_name, data, object_columns, hdrs, column_map):
            written['count'] += len(data)
            # Rows produced but not yet handed to SQLite: the decorator's true footprint.
            outstanding = state['produced'] - written['count']
            state['max_outstanding'] = max(state['max_outstanding'], outstanding)
            return original_insert(table_name, data, object_columns, hdrs, column_map)

        lavafuncs.lava_insert_sqlite_data = counting_insert
        self.addCleanup(setattr, lavafuncs, 'lava_insert_sqlite_data', original_insert)

        # ilapfuncs imported the symbol directly, so patch it there too.
        from scripts import ilapfuncs
        original_ref = ilapfuncs.lava_insert_sqlite_data
        ilapfuncs.lava_insert_sqlite_data = counting_insert
        self.addCleanup(setattr, ilapfuncs, 'lava_insert_sqlite_data', original_ref)

        def rows():
            for index in range(row_count):
                state['produced'] += 1
                yield (datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc),
                       index, f'message {index}')

        @artifact_processor_streaming
        def streaming_probe(context):  # pylint: disable=unused-argument
            return headers, rows(), None

        streaming_probe.__globals__['__artifacts_v2__'] = __artifacts_v2__
        # The decorator copies the wrapped function's one-argument signature, so pylint
        # reads this five-argument call (the framework's calling convention) as wrong.
        streaming_probe([], self.tmpdir, None, False, 0)  # pylint: disable=too-many-function-args
        return written['count'], state['max_outstanding']

    def test_all_rows_reach_the_database(self):
        row_count = 3 * 50000 + 137  # deliberately not a batch multiple
        written, _ = self._run(row_count)
        self.assertEqual(written, row_count)

        lavafuncs.lava_db.commit()
        with sqlite3.connect(os.path.join(self.tmpdir, '_lava_artifacts.db')) as connection:
            stored = connection.execute('SELECT COUNT(*) FROM streaming_probe').fetchone()[0]
        self.assertEqual(stored, row_count)

    def test_memory_stays_bounded_by_the_batch_size(self):
        from scripts.ilapfuncs import STREAMING_BATCH_SIZE
        row_count = 3 * STREAMING_BATCH_SIZE + 137
        _, max_outstanding = self._run(row_count)
        # If this ever regresses to building a list, outstanding would reach row_count.
        self.assertLessEqual(max_outstanding, STREAMING_BATCH_SIZE)

    def test_record_count_is_corrected_after_streaming(self):
        row_count = 12345
        self._run(row_count)
        artifacts = lavafuncs.lava_data['artifacts']['Unified Logs']
        probe = next(a for a in artifacts if a['tablename'] == 'streaming_probe')
        # Registered as 0 before the rows were counted; must not stay that way.
        self.assertEqual(probe['record_count'], row_count)

    def test_empty_result_creates_no_table(self):
        written, _ = self._run(0)
        self.assertEqual(written, 0)
        lavafuncs.lava_db.commit()
        with sqlite3.connect(os.path.join(self.tmpdir, '_lava_artifacts.db')) as connection:
            tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
        self.assertNotIn('streaming_probe', tables)


class TestFlashlightPredicates(unittest.TestCase):
    """The flashlight artifact has to match both spellings AVFoundation emits.

    On iOS 17.1 the logging macro renders '<<<< AVFlashlight >>>> -[AVFlashlight
    turnPowerOff]:' with spaces inside the brackets. The original predicate has no spaces,
    so an image with 190 genuine flashlight records reported nothing at all, which reads
    as "the flashlight was never used" rather than "the pattern did not match". Both
    spellings are now matched and both must stay.

    logarchive_flashlight selects from the table logarchive_artifacts builds, so a
    predicate missing from the broad query cannot be recovered by the narrow one. That
    coupling is the easy thing to get wrong, hence checking both.
    """

    SPACED = "'%<<<< AVFlashlight >>>>%'"
    UNSPACED = "'%<<<<AVFlashlight>>>>-%'"

    def _query_for(self, function_name):
        source = pathlib.Path(logarchive.__file__).read_text(encoding='utf-8')
        return source.split(f'def {function_name}', 1)[1].split("'''")[1]

    def test_broad_query_matches_both_spellings(self):
        query = self._query_for('logarchive_artifacts')
        self.assertIn(self.UNSPACED, query)
        self.assertIn(self.SPACED, query)

    def test_flashlight_artifact_matches_both_spellings(self):
        query = self._query_for('logarchive_flashlight')
        self.assertIn(self.UNSPACED, query)
        self.assertIn(self.SPACED, query)

    def test_spaced_predicate_matches_real_message_text(self):
        # Verbatim from an iOS 17.1 extraction.
        message = ('<<<< AVFlashlight >>>> -[AVFlashlight setFlashlightLevel:withError:]: '
                   'called (2800F8780) level 0')
        with sqlite3.connect(':memory:') as connection:
            connection.execute('CREATE TABLE t (event_message TEXT)')
            connection.execute('INSERT INTO t VALUES (?)', (message,))
            matched = connection.execute(
                f'SELECT COUNT(*) FROM t WHERE event_message LIKE {self.SPACED}').fetchone()[0]
        self.assertEqual(matched, 1)


class TestColumnContract(unittest.TestCase):
    """Both sources must produce the eight columns the dependent artifacts query."""

    def test_headers_match_the_dependent_artifact_queries(self):
        self.assertEqual(
            logarchive.DATA_HEADERS,
            (('Timestamp', 'datetime'), 'Row Number', 'Process Image Path', 'Process ID',
             'Subsystem', 'Category', 'Event Message', 'Trace ID'))

    def test_native_rows_line_up_with_the_headers(self):
        record = {
            'timestamp': '2026-07-29T14:11:07.452774400Z',
            'process': '/usr/libexec/locationd',
            'pid': 96,
            'subsystem': 'com.apple.locationd',
            'category': 'client',
            'message': 'Airplane Mode is now On',
        }
        original = unifiedlogs.stream_records
        unifiedlogs.stream_records = lambda binary, archive_dir: iter([record])
        self.addCleanup(setattr, unifiedlogs, 'stream_records', original)

        row = next(iter(logarchive.rows_from_tracev3('binary', 'archive')))
        self.assertEqual(len(row), len(logarchive.DATA_HEADERS))
        self.assertEqual(row[2], '/usr/libexec/locationd')  # Process Image Path
        self.assertEqual(row[3], 96)                        # Process ID
        self.assertEqual(row[6], 'Airplane Mode is now On')  # Event Message
        self.assertEqual(row[7], '')                        # Trace ID, not emitted by the parser
        self.assertEqual(row[1], 1)                         # Row Number starts at 1


if __name__ == '__main__':
    unittest.main()
