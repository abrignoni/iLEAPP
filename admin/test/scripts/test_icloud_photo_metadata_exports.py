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
            self.assertEqual(len(headers), 22)
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
            self.assertEqual({row[21] for row in rows if row[21]}, set(expected))
            self.assertEqual(sum(not row[21] for row in rows), 4)
            self.assertEqual({str(path.relative_to(output)): path.read_bytes()
                              for path in output.rglob('*.bplist')}, expected)
            # Existing caught plist errors still retain the original decoded bytes.
            self.assertEqual((output / rows[3][21]).read_bytes(), b'not a plist')
            self.assertEqual((output / rows[4][21]).read_bytes(), b'')
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
            self.assertEqual(rows[0][21],
                             'bplists/input-000002-line-000001-record-000000.bplist')

    def test_gps_is_read_without_tiff_and_signed_from_reference(self):
        cases = [
            ({'{GPS}': {'Latitude': 10.5, 'LatitudeRef': 'S', 'Longitude': 20.25,
                        'LongitudeRef': 'W'}}, (-10.5, -20.25, '', '')),
            ({'{GPS}': {'Latitude': 10.5, 'LatitudeRef': 'N', 'Longitude': 20.25,
                        'LongitudeRef': 'E'}, '{TIFF}': {'Make': 'm'}},
             (10.5, 20.25, "{'Make': 'm'}", '')),
            ({'{GPS}': {'Latitude': -10.5, 'LatitudeRef': 'S', 'Longitude': 20.25}},
             (-10.5, 20.25, '', '')),
            ({'{Exif}': {'ISO': 1}}, ('', '', '', "{'ISO': 1}")),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = [{'fields': {'resOriginalFileSize': 7, 'mediaMetaDataEnc': base64.b64encode(
                plistlib.dumps(value, fmt=plistlib.PlistFormat.FMT_BINARY)).decode()}}
                for value, _ in cases]
            records.append({'fields': {'mediaMetaDataEnc': base64.b64encode(
                plistlib.dumps(['list root'], fmt=plistlib.PlistFormat.FMT_BINARY)).decode()}})
            source = root / 'Metadata.txt'
            source.write_text(json.dumps(records) + '\n', encoding='utf-8')
            context = SimpleNamespace(
                get_files_found=lambda: [source],
                get_report_folder=lambda: str(root / 'report'),
                get_relative_path=lambda path: Path(path).name)
            headers, rows, _ = inspect.unwrap(icloudPhotoMeta)(context)
            names = [header[0] if isinstance(header, tuple) else header for header in headers]
            self.assertNotIn('Original Filesize', names)
            index = {name: names.index(name) for name in
                     ('Latitude', 'Longitude', 'TIFF', 'EXIF', 'Res Original Filesize')}
            for row, (_, expected) in zip(rows, cases):
                self.assertEqual((row[index['Latitude']], row[index['Longitude']],
                                  row[index['TIFF']], row[index['EXIF']]), expected)
                self.assertEqual(row[index['Res Original Filesize']], 7)
            self.assertEqual((rows[-1][index['Latitude']], rows[-1][index['TIFF']]), ('', ''))


if __name__ == '__main__':
    unittest.main()
