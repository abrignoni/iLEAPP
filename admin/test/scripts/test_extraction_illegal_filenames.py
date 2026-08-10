"""Guard extraction against archive members whose names Windows cannot write.

Real iOS extractions carry files with ASCII control characters in their names:
/private/var/mobile/Library/chronod/icons/ holds entries like
'╞¼\\x01\\x0e::com.apple.siri.heic'. ZipFile.extract() only replaces a fixed
set of printable characters (:<>|"?*) and only on Windows, so the control
bytes reach the OS untouched and open() fails with [Errno 22] Invalid
argument. In a case run this produced 81 'Could not write file to filesystem'
lines and the matched files were silently absent from the extraction; worse,
the failing member appended the *previous* member's path to the seeker's
result list because `extracted_path` still held its stale value.

These tests pin the fix: sanitize_file_path()/sanitize_file_name() treat
control characters as illegal, and FileSeekerZip writes such members manually
to a sanitized path inside the data folder on every platform.
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

from leapp_functions.app.platform import (  # pylint: disable=wrong-import-position
    sanitize_file_name, sanitize_file_path, validate_filename)
from scripts.search_files import FileSeekerZip  # pylint: disable=wrong-import-position

# The real member name observed in an iOS 26 full file system extraction.
ICON_MEMBER = ('/private/var/mobile/Library/chronod/icons/'
               '╖¬\x01\x0e::com.apple.siri.heic')
ICON_CONTENT = b'not really a heic'


def _has_control_chars(text):
    return any(ord(c) < 0x20 or ord(c) == 0x7f for c in text)


class TestSanitizeControlChars(unittest.TestCase):
    """The sanitize helpers must replace what Windows rejects with EINVAL."""

    def test_file_path_replaces_control_chars_but_keeps_separators(self):
        cleaned = sanitize_file_path('icons/\x01\x0e::a.heic')
        self.assertEqual(cleaned, 'icons/__::a.heic'.replace(':', '_'))
        self.assertIn('/', cleaned)
        self.assertFalse(_has_control_chars(cleaned))

    def test_file_name_replaces_control_chars(self):
        self.assertEqual(sanitize_file_name('a\x00b\x1fc\x7fd'), 'a_b_c_d')

    def test_printable_illegal_chars_still_replaced(self):
        self.assertEqual(sanitize_file_name('a:b*c?d'), 'a_b_c_d')

    def test_unicode_stays_untouched(self):
        self.assertEqual(sanitize_file_name('╖¬ café'),
                         '╖¬ café')

    def test_validate_filename_rejects_control_chars_without_crashing(self):
        is_valid, message = validate_filename('output\x01folder')
        self.assertFalse(is_valid)
        self.assertTrue(message)


class TestFileSeekerZipIllegalNames(unittest.TestCase):
    """A zip member with control characters in its name must still extract."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data_folder = os.path.join(self.tmpdir, 'data')
        os.makedirs(self.data_folder)
        self.zip_path = os.path.join(self.tmpdir, 'fs-full.zip')
        with zipfile.ZipFile(self.zip_path, 'w') as z:
            z.writestr(ICON_MEMBER, ICON_CONTENT)
            z.writestr('/private/var/mobile/Library/chronod/icons/plain.heic',
                       b'plain content')
        self.seeker = FileSeekerZip(self.zip_path, self.data_folder)

    def tearDown(self):
        self.seeker.cleanup()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_both_members_are_extracted(self):
        paths = self.seeker.search('*/chronod/icons/*')
        self.assertEqual(len(paths), 2)
        for path in paths:
            self.assertTrue(os.path.isfile(path), path)

    def test_extracted_path_carries_no_illegal_characters(self):
        paths = self.seeker.search('*/chronod/icons/*')
        sanitized = [p for p in paths if p.endswith('com.apple.siri.heic')]
        self.assertEqual(len(sanitized), 1)
        relative = os.path.relpath(sanitized[0], self.data_folder)
        self.assertFalse(_has_control_chars(relative))
        self.assertNotIn(':', relative)

    def test_extracted_content_is_intact(self):
        paths = self.seeker.search('*/chronod/icons/*')
        sanitized = [p for p in paths if p.endswith('com.apple.siri.heic')][0]
        with open(sanitized, 'rb') as f:
            self.assertEqual(f.read(), ICON_CONTENT)

    def test_extraction_stays_inside_the_data_folder(self):
        """Member names lead with '/'; a naive join would escape data_folder."""
        for path in self.seeker.search('*/chronod/icons/*'):
            self.assertTrue(
                os.path.realpath(path).startswith(
                    os.path.realpath(self.data_folder) + os.sep), path)

    def test_file_info_is_recorded_for_sanitized_members(self):
        paths = self.seeker.search('*/chronod/icons/*')
        sanitized = [p for p in paths if p.endswith('com.apple.siri.heic')][0]
        self.assertIn(sanitized, self.seeker.file_infos)
        self.assertEqual(self.seeker.file_infos[sanitized].source_path, ICON_MEMBER)

    def test_dot_dot_segments_cannot_escape_the_data_folder(self):
        traversal_zip = os.path.join(self.tmpdir, 'traversal.zip')
        with zipfile.ZipFile(traversal_zip, 'w') as z:
            z.writestr('icons/../../../evil\x01.txt', b'x')
        seeker = FileSeekerZip(traversal_zip, self.data_folder)
        try:
            paths = seeker.search('**')
            self.assertTrue(paths)
            for path in paths:
                self.assertTrue(
                    os.path.realpath(path).startswith(
                        os.path.realpath(self.data_folder) + os.sep), path)
        finally:
            seeker.cleanup()


if __name__ == '__main__':
    unittest.main()
