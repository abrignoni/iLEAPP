"""callHistoryTransactions on a record that lacks some fields (constructed input only)."""
import plistlib
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import callHistoryTransactions


def keyed_archive(value):
    """A minimal NSKeyedArchiver plist of a dictionary whose values are strings, numbers,
    bytes or lists of such dictionaries."""
    objects = ['$null']

    def add(obj):
        if isinstance(obj, dict):
            index = len(objects)
            objects.append(None)
            keys = [add(k) for k in obj]
            values = [add(v) for v in obj.values()]
            objects[index] = {'NS.keys': keys, 'NS.objects': values, '$class': add_class('NSDictionary')}
            return plistlib.UID(index)
        if isinstance(obj, list):
            index = len(objects)
            objects.append(None)
            objects[index] = {'NS.objects': [add(v) for v in obj], '$class': add_class('NSArray')}
            return plistlib.UID(index)
        objects.append(obj)
        return plistlib.UID(len(objects) - 1)

    classes = {}

    def add_class(name):
        if name not in classes:
            objects.append({'$classname': name, '$classes': [name, 'NSObject']})
            classes[name] = plistlib.UID(len(objects) - 1)
        return classes[name]

    root = add(value)
    return plistlib.dumps({'$archiver': 'NSKeyedArchiver', '$version': 100000,
                           '$top': {'root': root}, '$objects': objects}, fmt=plistlib.FMT_BINARY)


def transaction(record):
    body = keyed_archive({'record': keyed_archive(record)})
    return struct.pack('<I', len(body)) + body


class TestCallHistoryTransactions(unittest.TestCase):
    def test_a_record_without_disconnected_cause_gives_a_row_with_that_column_blank(self):
        full = {'handleType': 2, 'callStatus': 1, 'duration': 5.0, 'callerId': 'a',
                'timeToEstablish': 1.0, 'disconnectedCause': 3, 'uniqueId': 'u1',
                'remoteParticipantHandles': [{'value': '+15550100'}]}
        short = {k: v for k, v in full.items() if k != 'disconnectedCause'}
        short['uniqueId'] = 'u2'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / 'filesystem2/mobile/Library/CallHistoryTransactions/transactions.log'
            log.parent.mkdir(parents=True)
            log.write_bytes(transaction(full) + transaction(short))
            context = SimpleNamespace(get_files_found=lambda: [str(log)],
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
            _, rows, _ = callHistoryTransactions.callHistoryTransactions.__wrapped__(context)
        self.assertEqual([(r[4], r[7], r[8]) for r in rows], [('+15550100', 3, 'u1'), ('+15550100', '', 'u2')])


if __name__ == '__main__':
    unittest.main()
