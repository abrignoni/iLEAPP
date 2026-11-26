"""A Berla iVe export (.iVa) given as the source of the window.

An .iVa is a zip that holds another zip, so its first bytes say zip archive. Read as one,
the vehicle data inside the inner zip is never reached and the report comes out empty.
leapp_functions.app.input_type.detect therefore knows it by its name, as -t iva, and only
a LEAPP whose data/leapp_config.json lists "iva" accepts it. The others refuse it and say
which LEAPP reads it. The supported types are passed in, so the test means the same in
every core.
"""
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from leapp_functions import leapp  # pylint: disable=wrong-import-position
from leapp_functions.app import input_type  # pylint: disable=wrong-import-position

READS_IVA = frozenset(('fs', 'tar', 'gz', 'zip', 'raw', 'file', 'iva'))
NO_IVA = frozenset(('fs', 'tar', 'gz', 'zip', 'raw', 'file'))


class IvaExportTest(unittest.TestCase):
    """How the window names an .iVa, with and without "iva" among the supported types."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='input_type_iva_')
        self.addCleanup(shutil.rmtree, self.folder, True)

    def export(self, name='Vehicle.iVa', zipped=True):
        """An export as iVe writes it: a zip holding Vehicle.json and an inner zip."""
        path = os.path.join(self.folder, name)
        if not zipped:
            with open(path, 'wb') as handle:
                handle.write(b'\0' * 4096)
            return path
        with zipfile.ZipFile(path, 'w') as outer:
            outer.writestr('Vehicle.json', '{}')
            outer.writestr('Inner.zip', b'PK\x05\x06' + b'\0' * 18)
        return path

    def test_an_export_is_read_as_iva_where_it_is_supported(self):
        """An .iVa that is a zip is read as -t iva, with no note."""
        detected = input_type.detect([self.export()], supported=READS_IVA)
        self.assertEqual(detected, input_type.Detected('iva', 'Berla iVe export'))

    def test_the_extension_is_matched_in_any_case(self):
        """.IVA and .iVa are the same extension."""
        detected = input_type.detect([self.export('VEHICLE.IVA')], supported=READS_IVA)
        self.assertEqual(detected.kind, 'iva')

    def test_an_export_that_is_not_a_zip_is_read_with_a_note(self):
        """The name decides; the note says when the content does not agree."""
        detected = input_type.detect([self.export(zipped=False)], supported=READS_IVA)
        self.assertEqual(detected.kind, 'iva')
        self.assertEqual(detected.note, 'Its content does not look like a zip archive, which an export is.')

    def test_a_leapp_without_iva_refuses_it_rather_than_read_it_as_a_zip(self):
        """Elsewhere it is refused, with the name of the LEAPP that reads it."""
        detected = input_type.detect([self.export()], supported=NO_IVA)
        self.assertEqual(detected.kind, '')
        self.assertEqual(detected.problem, f'VLEAPP reads Berla iVe exports, {leapp.name} does not.')

    def test_read_as_a_single_file_it_is_not_opened(self):
        """Read as a single file, it is -t file like any other file."""
        detected = input_type.detect([self.export()], supported=READS_IVA, single_file=True)
        self.assertEqual(detected.kind, 'file')
        self.assertIn('It looks like a zip archive', detected.note)

    def test_another_zip_is_still_a_zip_archive(self):
        """Only the .iva extension is taken for an export."""
        path = os.path.join(self.folder, 'files.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('a.txt', 'a')
        self.assertEqual(input_type.detect([path], supported=READS_IVA).kind, 'zip')


if __name__ == '__main__':
    unittest.main()
