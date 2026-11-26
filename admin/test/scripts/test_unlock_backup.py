"""
The password of an encrypted backup, opened by the window before the run, reaches the run with
its keys, so that the log of the run records it as the command line's does.
"""

import unittest
from types import SimpleNamespace
from unittest import mock

from leapp_functions.app import unlock
from leapp_functions.app.gui import run

KEYS = ("classes", "Manifest.db key")


def asker_answering(*answers):
    """ An asker that answers the password questions from a list, and records the prompts shown.
    """
    answers = iter(answers)
    prompts = []

    def ask_secret(title, prompt):
        prompts.append((title, prompt))
        return next(answers)

    return SimpleNamespace(ask_secret=ask_secret, prompts=prompts)


def decrypt(_path, password):
    """ decrypt_itunes_backup, for a backup whose password is "right". """
    return (KEYS, "Decryption successful") if password == "right" else (None, "Incorrect password")


class TestUnlockBackup(unittest.TestCase):
    """ unlock.unlock_backup keeps the password that opened the backup. """

    def test_the_password_comes_back_with_the_keys(self):
        """ A wrong password asks again; the right one gives the keys and itself. """
        asker = asker_answering("wrong", "right")
        with mock.patch.object(unlock, "decrypt_itunes_backup", side_effect=decrypt):
            opened = unlock.unlock_backup("backup", asker)
        self.assertEqual(opened, unlock.Backup(KEYS, "right"))
        self.assertEqual(len(asker.prompts), 2)
        self.assertTrue(asker.prompts[1][1].startswith("Incorrect password. "))

    def test_cancelling_gives_nothing(self):
        """ No password, no keys. """
        with mock.patch.object(unlock, "decrypt_itunes_backup", side_effect=decrypt):
            self.assertIsNone(unlock.unlock_backup("backup", asker_answering(None)))


def state_with(kind, opened):
    """ The little of AppState that build_request reads. """
    value = SimpleNamespace(get=lambda: "")
    unlocked = None if opened is None else SimpleNamespace(result=opened)
    return SimpleNamespace(
        run=SimpleNamespace(unlock=unlocked, detected=SimpleNamespace(kind=kind),
                            single_file=value, hash_files=value, output=value,
                            folder_name=value, secrets={}),
        artifacts=SimpleNamespace(loader=None), source_paths=lambda: ["backup"], case_values=dict)


class TestBuildRequest(unittest.TestCase):
    """ gui.run.build_request hands the keys and the password of a backup to the run. """

    def setUp(self):
        for name in ("run_order", "profile_for_report"):
            patcher = mock.patch.object(run.artifact_list, name, return_value=None)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_an_encrypted_backup(self):
        """ The keys and the password, apart. """
        request = run.build_request(state_with("itunes", unlock.Backup(KEYS, "right")))
        self.assertEqual(request.backup_keys, KEYS)
        self.assertEqual(request.backup_password, "right")

    def test_a_backup_that_is_not_encrypted(self):
        """ Nothing was asked: no keys, no password. """
        request = run.build_request(state_with("itunes", None))
        self.assertIsNone(request.backup_keys)
        self.assertIsNone(request.backup_password)


if __name__ == "__main__":
    unittest.main()
