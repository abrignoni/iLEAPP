"""Pin the source path a media item records in the LAVA database.

`_lava_media_items.source_path` says where in the evidence a media item came from. It
used to be the FileInfo source path only when the source resolved through the current
artifact's files_found by file name, and otherwise the string the artifact passed, as
given. Two kinds of source never resolved that way, and both carry the examiner's own
folders:

- A file read out of a staged archive. iLEAPP's get_sysdiagnose_files yields such a file
  as '<staged archive> >> <member>', and its sysdiagnoseProcessTree checks the rendered
  image in with that string. Measured on a real iOS 14 extraction in folder, zip and tar form, the
  media item recorded the report's data folder whole.
- A staged file the artifact did not search for itself, for example one another search
  staged. ALEAPP's Signal - Messages decrypts attachment files it finds with its own
  seeker search, while its files_found holds only signal.db.

Worse, the lookup by file name resolved '<archive> >> <folder>/ps.txt' to any other
ps.txt the artifact found, so with the same capture unpacked beside the archive, the
archive's image was recorded as coming from the unpacked copy.

These tests check media in the way an artifact does and read the recorded path back
from the LAVA database. The file is the same in all five LEAPP cores: where a core has
get_sysdiagnose_files, the archive member's source comes from it, and elsewhere it is
built in the shape that function yields.
"""
import hashlib
import io
import os
import pathlib
import shutil
import sqlite3
import sys
import tarfile
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs, lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.search_files import FileInfo  # pylint: disable=wrong-import-position

SD = 'sysdiagnose_2026.01.02_03-04-05-0500_iPhone-OS_iPhone_23A000'
ARCHIVE = f'private/var/mobile/Library/Logs/CrashReporter/DiagnosticLogs/sysdiagnose/{SD}.tar.gz'
MEMBER = f'{SD}/ps.txt'
PS_TXT = (b'USER UID PRSNA PID PPID F %CPU %MEM PRI NI VSZ RSS WCHAN TT STAT STARTED TIME COMMAND\n'
          b'root 0 - 1 0 4004 0.0 0.0 31 0 0 0 - ?? Ss 1:25PM 0:00.00 /sbin/launchd\n')
PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 64


class CheckInMediaSourcePathTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.report = pathlib.Path(self.tmpdir)
        self.data_folder = self.report / 'data'
        media_folder = self.report / 'media'
        html_media_folder = self.report / '_HTML' / 'media'
        for folder in (self.data_folder, media_folder, html_media_folder):
            folder.mkdir(parents=True, exist_ok=True)
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        Context.clear()
        # The folders a run sets: evidence is staged into the data folder, inside the report.
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(media_folder), html_media_folder=str(html_media_folder),
            data_folder=str(self.data_folder), output_folder_base=str(self.report)))
        Context.set_module_name('test_module')
        Context.set_artifact_name('Test Artifact')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _stage(self, rel_path, content):
        staged = self.data_folder / rel_path
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(content)
        return str(staged)

    def _stage_archive(self):
        staged = self.data_folder / ARCHIVE
        staged.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(staged, 'w:gz') as tar:
            info = tarfile.TarInfo(MEMBER)
            info.size = len(PS_TXT)
            tar.addfile(info, io.BytesIO(PS_TXT))
        return str(staged)

    @staticmethod
    def _seek(files_found, file_infos):
        """Set files_found and a seeker holding a FileInfo per staged path, as a run does."""
        Context.set_files_found(files_found)
        Context.set_seeker(types.SimpleNamespace(file_infos={
            staged: FileInfo(rel_path, 0, 0) for staged, rel_path in file_infos.items()}))

    @staticmethod
    def _recorded(data):
        row = lavafuncs.lava_db.execute(
            'SELECT source_path FROM _lava_media_items WHERE id = ?',
            (hashlib.sha1(data).hexdigest(),)).fetchone()
        return row[0] if row else None

    def _check_in_archive_member(self, staged_archive, files_found):
        """Check a rendered image in for the member, the way sysdiagnoseProcessTree does."""
        producer = getattr(ilapfuncs, 'get_sysdiagnose_files', None)
        if producer is None:
            sources = [f'{staged_archive} >> {MEMBER}']
        else:
            sources = [source for _, source in producer(files_found, 'ps.txt') if ' >> ' in source]
        self.assertEqual(sources, [f'{staged_archive} >> {MEMBER}'])
        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(
            sources[0], PNG, 'sysdiagnose_process_tree.png',
            force_type='image/png', force_extension='png'))

    def assert_not_on_examiners_machine(self, recorded):
        self.assertNotIn(self.tmpdir, recorded)
        self.assertFalse(os.path.isabs(recorded), f'still absolute: {recorded!r}')

    def test_a_file_read_out_of_a_staged_archive_is_recorded_by_its_evidence_path(self):
        staged_archive = self._stage_archive()
        self._seek([staged_archive], {staged_archive: ARCHIVE})

        self._check_in_archive_member(staged_archive, [staged_archive])

        recorded = self._recorded(PNG)
        self.assertEqual(recorded, f'{ARCHIVE} >> {MEMBER}')
        self.assert_not_on_examiners_machine(recorded)

    def test_the_archive_part_is_the_path_its_file_info_records(self):
        # Some extractions spell every member with a leading slash, and the FileInfo keeps
        # that spelling; the image should read like every other file from the same input.
        staged_archive = self._stage_archive()
        self._seek([staged_archive], {staged_archive: f'/{ARCHIVE}'})

        self._check_in_archive_member(staged_archive, [staged_archive])

        recorded = self._recorded(PNG)
        self.assertEqual(recorded, f'/{ARCHIVE} >> {MEMBER}')
        self.assertNotIn(self.tmpdir, recorded)

    def test_a_member_of_an_archive_nothing_staged_is_recorded_without_the_data_folder(self):
        database = 'private/var/mobile/Library/Example/example.sqlite'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        self._seek([staged_database], {staged_database: database})
        source = f'{self.data_folder / ARCHIVE} >> {MEMBER}'

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(source, PNG, 'image.png'))

        recorded = self._recorded(PNG)
        self.assertEqual(recorded, f'{ARCHIVE} >> {MEMBER}')
        self.assert_not_on_examiners_machine(recorded)

    def test_the_member_is_not_attributed_to_another_file_of_the_same_name(self):
        staged_archive = self._stage_archive()
        unpacked = f'unpacked/{MEMBER}'
        staged_unpacked = self._stage(unpacked, PS_TXT)
        self._seek([staged_archive, staged_unpacked],
                   {staged_archive: ARCHIVE, staged_unpacked: unpacked})

        self._check_in_archive_member(staged_archive, [staged_archive, staged_unpacked])

        self.assertEqual(self._recorded(PNG), f'{ARCHIVE} >> {MEMBER}')

    def test_a_staged_file_the_artifact_did_not_search_for_is_recorded_by_its_file_info(self):
        database = 'data/data/org.thoughtcrime.securesms/databases/signal.db'
        part = 'data/data/org.thoughtcrime.securesms/app_parts/part1234.mms'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        # A case variant of the name was staged first, so the seeker wrote this copy as
        # name~case-<tag>.ext; its FileInfo still names the evidence file.
        staged_part = self._stage(
            'data/data/org.thoughtcrime.securesms/app_parts/part1234~case-1a2b3c4d.mms',
            b'encrypted attachment')
        # The part was staged by a search of its own; files_found lists only the database.
        self._seek([staged_database], {staged_database: database, staged_part: part})

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(staged_part, PNG, 'attachment.png'))

        self.assertEqual(self._recorded(PNG), part)

    def test_a_staged_path_without_a_file_info_is_recorded_without_the_data_folder(self):
        database = 'private/var/mobile/Library/Example/example.sqlite'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        unstaged = str(self.data_folder / 'private/var/mobile/Library/Example/not_staged.bin')
        self._seek([staged_database], {staged_database: database})

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(unstaged, PNG, 'image.png'))

        recorded = self._recorded(PNG)
        self.assertEqual(recorded, 'private/var/mobile/Library/Example/not_staged.bin')
        self.assert_not_on_examiners_machine(recorded)

    def test_a_file_the_artifact_found_is_recorded_as_before(self):
        database = 'private/var/mobile/Library/Example/example.sqlite'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        self._seek([staged_database], {staged_database: database})

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(staged_database, PNG, 'image.png'))

        self.assertEqual(self._recorded(PNG), database)

    def test_a_path_object_for_a_found_file_is_recorded_as_before(self):
        database = 'private/var/mobile/Library/Example/example.sqlite'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        self._seek([staged_database], {staged_database: database})

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media(
            pathlib.Path(staged_database), PNG, 'image.png'))

        self.assertEqual(self._recorded(PNG), database)

    def test_a_relative_name_nothing_matches_is_recorded_as_given(self):
        database = 'private/var/mobile/Library/Example/example.sqlite'
        staged_database = self._stage(database, b'SQLite format 3\x00')
        self._seek([staged_database], {staged_database: database})

        self.assertIsNotNone(ilapfuncs.check_in_embedded_media('ThreemaData.sqlite', PNG, 'image.png'))

        self.assertEqual(self._recorded(PNG), 'ThreemaData.sqlite')


if __name__ == '__main__':
    unittest.main()
