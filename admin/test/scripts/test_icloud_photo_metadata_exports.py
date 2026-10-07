"""Embedded metadata exports retain input, line and record occurrences."""
import base64
import json
import inspect
import plistlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.icloudPhotoMeta import icloudPhotoMeta


class TestICloudMetadataExports(unittest.TestCase):
    """Use real JSON, base64 and plist bytes, including caught invalid plists."""

    def test_occurrences_and_payload_presence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            xml = plistlib.dumps({'marker': 'XML 雪'}, fmt=plistlib.PlistFormat.FMT_XML)
            binary = plistlib.dumps({'marker': 'binary'}, fmt=plistlib.PlistFormat.FMT_BINARY)
            payloads = [xml, binary, xml, b'not a plist', b'']
            records = [{'id': '../same', 'fields': {
                'mediaMetaDataEnc': base64.b64encode(value).decode()}}
                for value in payloads]
            records += [{'fields': {'mediaMetaDataEnc': None}}, {'fields': {'title': ''}}]
            first = root / 'first.txt'
            second = root / 'second.txt'
            first.write_text(json.dumps(records) + '\n\ninvalid JSON\n' +
                             json.dumps({'results': records[:2]}) + '\n', encoding='utf-8')
            second.write_text(json.dumps(records[:1]) + '\n', encoding='utf-8')
            output = root / 'report'
            context = SimpleNamespace(
                get_files_found=lambda: [first, second, first],
                get_report_folder=lambda: str(output),
                get_relative_path=lambda path: Path(path).name)
            headers, rows, source = inspect.unwrap(icloudPhotoMeta)(context)
            self.assertEqual(len(headers), 23)
            self.assertEqual(source, 'first.txt, second.txt')
            self.assertEqual(len(rows), 19)
            self.assertEqual([row[1] for row in rows],
                             ['0', '1', '2', '3', '4', '5', '6', '0', '1', '0',
                              '0', '1', '2', '3', '4', '5', '6', '0', '1'])
            expected = {}
            for occurrence, groups in [(1, [(1, payloads), (4, payloads[:2])]),
                                       (2, [(1, payloads[:1])]),
                                       (3, [(1, payloads), (4, payloads[:2])])]:
                for line, values in groups:
                    for ordinal, value in enumerate(values):
                        name = (f'bplists/input-{occurrence:06d}-line-{line:06d}-'
                                f'record-{ordinal:06d}.bplist')
                        expected[name] = value
            self.assertEqual(len(expected), 15)
            self.assertEqual({row[22] for row in rows if row[22]}, set(expected))
            self.assertEqual(sum(not row[22] for row in rows), 4)
            self.assertEqual({str(path.relative_to(output)): path.read_bytes()
                              for path in output.rglob('*.bplist')}, expected)
            # Existing caught plist errors still retain the original decoded bytes.
            self.assertEqual((output / rows[3][22]).read_bytes(), b'not a plist')
            self.assertEqual((output / rows[4][22]).read_bytes(), b'')
            _, repeated, _ = inspect.unwrap(icloudPhotoMeta)(context)
            self.assertEqual(rows, repeated)
            self.assertEqual({str(path.relative_to(output)): path.read_bytes()
                              for path in output.rglob('*.bplist')}, expected)

    def test_unreadable_input_still_occupies_input_ordinal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good = root / 'good.txt'
            good.write_text('[{"fields":{"mediaMetaDataEnc":""}}]\n', encoding='utf-8')
            context = SimpleNamespace(
                get_files_found=lambda: [root / 'missing.txt', good],
                get_report_folder=lambda: str(root / 'report'),
                get_relative_path=lambda path: Path(path).name)
            _, rows, source = inspect.unwrap(icloudPhotoMeta)(context)
            self.assertEqual(source, 'good.txt')
            self.assertEqual(rows[0][22],
                             'bplists/input-000002-line-000001-record-000000.bplist')


if __name__ == '__main__':
    unittest.main()
