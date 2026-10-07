"""Actual JSON and TAR streams for serial-only native membership."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import sdl_account_devices as module
from scripts.context import Context


class FileContext:
    lookup_metadata = staticmethod(Context.lookup_metadata)
    get_apple_os_version = staticmethod(Context.get_apple_os_version)
    get_relative_path = staticmethod(Context.get_relative_path)

    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


def peer(serial, model='iPhone12,1', build='iOS 17.3 (21D50)'):
    return {'permanentInfo': {'model_id': model},
            'stableInfo': {'os_version': build, 'serial_number': serial}}


def payload(serials, push='push-value'):
    return {'lastOctagonPush': push, 'contextDump': {'peers': [peer(v) for v in serials]}}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')
    path.chmod(0o444)


def full_selection(records, serial_only):
    """Select complete stream independently, using real unchanged metadata helpers."""
    rows = []
    admitted = []
    for data, source in records:
        for item in data['contextDump']['peers']:
            try:
                model = item['permanentInfo']['model_id']
                product = Context.lookup_metadata('apple_device_id_to_model', model)
                build = item['stableInfo']['os_version']
                version = Context.get_apple_os_version(build.split('(')[1].split(')')[0], model)
                serial = item['stableInfo']['serial_number']
            except (KeyError, IndexError):
                continue
            row = (data.get('lastOctagonPush', ''), model, product, build, version, serial, source)
            excluded = serial in admitted if serial_only else any(serial in prior for prior in rows)
            if not excluded:
                rows.append(row)
                admitted.append(serial)
    return rows


class SdlSerialComparisonTest(unittest.TestCase):
    def setUp(self):
        folder = patch.object(Context, '_data_folder', None)
        folder.start()
        self.addCleanup(folder.stop)

    def test_cross_field_collisions_global_repeats_and_full_selector(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Context.set_data_folder(str(root))
            product = Context.lookup_metadata('apple_device_id_to_model', 'iPhone12,1')
            version = Context.get_apple_os_version('21D50', 'iPhone12,1')
            first_rel = 'case-A/otctl_status.txt'
            cross_fields = ['push-value', 'iPhone12,1', product, 'iOS 17.3 (21D50)',
                            version, first_rel]
            a = payload(['A', *cross_fields, 'A', 'XA', 'AX', 'iPhone12,1'])
            # A newly admitted peer's nonserial fields must not exclude later serials either.
            a['contextDump']['peers'] += [peer('new-serial', model='new-model'), peer('new-model')]
            b = payload(['A', 'unique', 'second-push'], push='second-push')
            a['contextDump']['peers'] += [{'permanentInfo': {}}, peer('bad-build', build='no brackets')]
            paths = [root / first_rel, root / 'case-B/otctl_status.txt']
            for path, data in zip(paths, [a, b]):
                write_json(path, data)
            records = [(json.loads(path.read_text()), str(path.relative_to(root))) for path in paths]
            headers, rows, source = module.sdl_account_devices.__wrapped__(FileContext(paths))
            self.assertEqual(rows, full_selection(records, True))
            self.assertEqual(len(rows), 13)
            self.assertEqual(len(full_selection(records, False)), 5)
            self.assertEqual([row[5] for row in rows].count('A'), 1)
            self.assertIn('XA', [row[5] for row in rows])
            self.assertIn('AX', [row[5] for row in rows])
            self.assertTrue(all(value in [row[5] for row in rows] for value in cross_fields))
            self.assertEqual(headers, ('lastOctagonPush', 'Model', 'Product', 'OS Build',
                                       'OS Version', 'Serial Number', 'Source Path'))
            self.assertEqual(source, '\n'.join(sorted(map(str, paths))))

    def test_native_equality_null_empty_and_unhashable_serials(self):
        values = [None, '', 0, 0.0, False, True, 1, 2, 0.5, '0', [], [], [1], [1], {}, {},
                  {'a': 1}, {'a': 1}, {'a': 2}]
        for serials in [values, list(reversed(values))]:
            with self.subTest(reverse=serials[0] is not None), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                Context.set_data_folder(str(root))
                path = root / 'otctl_status.txt'
                write_json(path, payload(serials, push=0))
                data = json.loads(path.read_text())
                before = hashlib.sha256(path.read_bytes()).hexdigest()
                _, rows, _ = module.sdl_account_devices.__wrapped__(FileContext([path]))
                expected = full_selection([(data, 'otctl_status.txt')], True)
                self.assertEqual(rows, expected)
                self.assertEqual([type(row[5]) for row in rows], [type(row[5]) for row in expected])
                self.assertEqual(len(rows), 12)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
                self.assertTrue(any(row[5] is None for row in rows))
                self.assertTrue(any(isinstance(row[5], list) for row in rows))
                self.assertTrue(any(isinstance(row[5], dict) for row in rows))

    def test_actual_tar_standalone_source_union_and_appledouble(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Context.set_data_folder(str(root))
            direct = root / 'direct/otctl_status.txt'
            a = payload(['A', 'push-value', 'XA'])
            b = payload(['A', 'B', 'iPhone12,1'])
            write_json(direct, a)
            package = root / 'sysdiagnose_fixture.tar.gz'
            with tarfile.open(package, 'w:gz') as archive:
                for name, data in [('case/otctl_status.txt', json.dumps(b).encode()),
                                   ('case/._otctl_status.txt', b'not JSON')]:
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
            package.chmod(0o444)
            initial = [hashlib.sha256(path.read_bytes()).hexdigest() for path in [direct, package]]
            _, rows, sources = module.sdl_account_devices.__wrapped__(FileContext([direct, package]))
            expected = full_selection([(a, 'direct/otctl_status.txt'),
                                       (b, 'sysdiagnose_fixture.tar.gz >> case/otctl_status.txt')], True)
            self.assertEqual(rows, expected)
            self.assertEqual(len(rows), 5)
            self.assertEqual(sources, '\n'.join(sorted([str(direct),
                                                       str(package) + ' >> case/otctl_status.txt'])))
            self.assertEqual(initial, [hashlib.sha256(path.read_bytes()).hexdigest()
                                       for path in [direct, package]])


if __name__ == '__main__':
    unittest.main()
