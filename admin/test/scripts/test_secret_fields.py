"""
leapp_functions.app.secret_fields: the kinds, names and checks of the secrets of the configuration.
The fields are written here, so the test does not depend on what one LEAPP's configuration holds.
"""

import unittest
import uuid

from leapp_functions.app import secret_fields

KEYCHAIN = {"name": "keychain", "label": "Optional.", "if_absent": "No keychain file."}
RECOVERY_KEY = {"name": "recovery_key", "kind": "text", "display": "Signal recovery key",
                "label": "Optional.", "if_absent": "No key.", "check": "uuid:UUID"}


class TestSecretFields(unittest.TestCase):
    """ What the window reads from a field of "secrets". """

    def test_a_field_is_a_file_unless_it_says_otherwise(self):
        """ The keychain of iLEAPP has no kind: a file. """
        self.assertEqual(secret_fields.kind(KEYCHAIN), "file")
        self.assertEqual(secret_fields.kind(RECOVERY_KEY), "text")

    def test_the_name_shown_is_display_or_name(self):
        """ The name keeps its capitals inside a sentence, and starts with one on a line. """
        self.assertEqual(secret_fields.name(KEYCHAIN), "keychain")
        self.assertEqual(secret_fields.title(KEYCHAIN), "Keychain")
        self.assertEqual(secret_fields.name(RECOVERY_KEY), "Signal recovery key")
        self.assertEqual(secret_fields.title(RECOVERY_KEY), "Signal recovery key")

    def test_file_types_default_to_all_files(self):
        """ The file dialog offers every file unless the field lists kinds. """
        self.assertEqual(secret_fields.file_types(KEYCHAIN), [("All files", "*")])
        listed = dict(KEYCHAIN, filetypes=[["Keychain files", "*.plist"]])
        self.assertEqual(secret_fields.file_types(listed), [("Keychain files", "*.plist")])

    def test_a_text_is_checked_by_the_function_named(self):
        """ The message of the check, after the name; nothing for an empty text. """
        self.assertEqual(secret_fields.text_problem(RECOVERY_KEY, ""), "")
        self.assertEqual(secret_fields.text_problem(RECOVERY_KEY, str(uuid.uuid4())), "")
        problem = secret_fields.text_problem(RECOVERY_KEY, "not-a-key")
        self.assertTrue(problem.startswith("Signal recovery key: "))
        self.assertNotIn("not-a-key", problem)

    def test_a_text_without_check_is_always_usable(self):
        """ No "check": any text will do. """
        self.assertEqual(secret_fields.text_problem(dict(RECOVERY_KEY, check=""), "anything"), "")
        unchecked = {key: value for key, value in RECOVERY_KEY.items() if key != "check"}
        self.assertEqual(secret_fields.text_problem(unchecked, "anything"), "")


if __name__ == "__main__":
    unittest.main()
