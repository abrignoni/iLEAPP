"""Actual newline JSON streams and bounded shape diagnostics for restore.log."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import restoreLog as module
from scripts.context import Context
from scripts.ilapfuncs import convert_unix_ts_to_utc


class FileContext:
    get_apple_os_version = staticmethod(Context.get_apple_os_version)
    lookup_metadata = staticmethod(Context.lookup_metadata)
    get_relative_path = staticmethod(Context.get_relative_path)

    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


def event(**changes):
    result = {'eventTime': 1700000000, 'originalOSVersion': '21D50',
              'currentOSVersion': '21F90', 'deviceClass': 'iPhone',
              'deviceModel': 'N104AP', 'event': 'opaque & <event>',
              'batteryLevel': 0, 'batteryIsCharging': False}
    result.update(changes)
    return result


def write_stream(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('unmarked line\n' + ''.join(
        'prefix data = ' + json.dumps(record) + '\n' for record in records), encoding='utf-8')
    path.chmod(0o444)


class RestoreLogEventsTest(unittest.TestCase):
    def setUp(self):
        data_folder = patch.object(Context, '_data_folder', None)
        data_folder.start()
        self.addCleanup(data_folder.stop)

    def test_order_repeats_later_eligibility_and_native_key_presence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Context.set_data_folder(str(root))
            first = event()
            later = event(eventTime=1700000001, batteryLevel=None, batteryIsCharging=1)
            raw_values = [None, '', 0, False]
            falsy_events = [event(originalOSVersion=value, eventTime=1700000010 + i)
                           for i, value in enumerate(raw_values)]
            path = root / 'mobile/MobileSoftwareUpdate/restore.log'
            write_stream(path, [{'events': [first, later, first]},
                                {'events': [{}, later]}, {},
                                *({'events': [value]} for value in falsy_events)])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with patch.object(module, 'logfunc') as log:
                headers, rows, source = module.restore_log.__wrapped__(FileContext([path]))
            self.assertEqual(len(rows), 8)
            self.assertEqual([row[0] for row in rows], [convert_unix_ts_to_utc(v) for v in
                             [1700000000, 1700000001, 1700000000, 1700000001,
                              1700000010, 1700000011, 1700000012, 1700000013]])
            self.assertEqual(rows[0], rows[2])
            self.assertEqual(rows[1], rows[3])
            self.assertEqual(rows[0], (convert_unix_ts_to_utc(1700000000), '21D50',
                                      Context.get_apple_os_version('21D50', 'iPhone'), '21F90',
                                      Context.get_apple_os_version('21F90', 'iPhone'),
                                      'opaque & <event>', 'iPhone', 'N104AP',
                                      Context.lookup_metadata('apple_board_id_to_model', 'N104AP'),
                                      0, False))
            self.assertEqual([row[1] for row in rows[4:]], raw_values)
            self.assertEqual([type(row[1]) for row in rows[4:]], [type(v) for v in raw_values])
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertEqual(len(headers), 11)
            self.assertEqual(source, path)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            log.assert_not_called()

    def test_shapes_skip_only_unsupported_values_and_cap_private_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Context.set_data_folder(str(root))
            path = root.joinpath(*(['long' * 35] * 4), 'control\npath', 'restore.log')
            records = [None, [], 1, True, 'PRIVATE_ROOT', {'events': None},
                       {'events': {}}, {'events': 'PRIVATE_EVENTS'}, {'events': 0},
                       {'events': False}, {'events': [None, [], 0, False, 'PRIVATE_MEMBER', {},
                                                       event(), event()]},
                       *({'events': None} for _ in range(8)), {'events': []}, {},
                       {'events': [event(eventTime=1700000001)]}]
            write_stream(path, records)
            with patch.object(module, 'logfunc') as log:
                _, rows, _ = module.restore_log.__wrapped__(FileContext([path]))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0], rows[1])
            messages = [call.args[0] for call in log.call_args_list]
            self.assertEqual(len(messages), 11)
            self.assertIn('line=2 skipped parsed_root_not_object type=null', messages[0])
            self.assertIn('parsed_root_not_object=5, events_not_array=13, '
                          'event_not_object=5, suppressed_examples=13', messages[-1])
            for message in messages:
                self.assertNotIn('PRIVATE', message)
                self.assertNotIn(folder, message)
                self.assertNotIn('\n', message)
                self.assertIn('[truncated; length=', message)
                self.assertLessEqual(len(message.split('restoreLog: ', 1)[1].split(' line=', 1)[0]
                                         .split(' shape skips:', 1)[0]), 512)
            # Under the cap, event ordinal/type identify a skipped member without its value.
            write_stream(root / 'short/restore.log', [{'events': [None, event()]}])
            with patch.object(module, 'logfunc') as log:
                _, rows, _ = module.restore_log.__wrapped__(FileContext([root / 'short/restore.log']))
            self.assertEqual(len(rows), 1)
            self.assertIn('short/restore.log line=2 event=1 skipped event_not_object type=null',
                          log.call_args_list[0].args[0])

    def test_missing_empty_arrays_and_first_source_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Context.set_data_folder(str(root))
            first, second = root / 'a/restore.log', root / 'b/restore.log'
            write_stream(first, [{}, {'events': []}])
            write_stream(second, [{'events': [event()]}])
            with patch.object(module, 'logfunc') as log:
                _, rows, source = module.restore_log.__wrapped__(FileContext([first, second]))
            self.assertEqual(rows, [])
            self.assertEqual(source, first)
            log.assert_not_called()


if __name__ == '__main__':
    unittest.main()
