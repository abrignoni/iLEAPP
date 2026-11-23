"""
The questions asked to open an encrypted source, from a thread of their own.
"""

import queue
import threading
from collections import namedtuple
from types import SimpleNamespace

from scripts.raw_image import unlock_raw_input
from scripts.search_files import decrypt_itunes_backup

Question = namedtuple("Question", "kind title text extra", defaults=("", "", None))

BACKUP_TITLE = "Backup password"
BACKUP_PROMPT = "The password set when the backup was encrypted:"


class Unlock:
    """
    One sequence on its worker thread. It is also the asker the sequence is given: it has
    the five methods of raw_image.DialogAsker, called on the worker thread.
    """

    def __init__(self, sequence):
        """ sequence(asker) runs on the thread; what it returns is kept in result. """
        self.questions = queue.Queue()
        self.answers = queue.Queue()
        self.cancelled = threading.Event()
        self.result = None
        # What the window shows, kept here so that it outlives its widgets: the question waiting
        # for an answer, the last message, whether the sequence has ended, and whether a
        # question about a volume was cancelled, which leaves that volume locked
        self.shown = SimpleNamespace(waiting=None, message=None, done=False, locked=False)
        self.thread = threading.Thread(target=self.work, args=(sequence,), daemon=True)
        self.thread.start()

    def work(self, sequence):
        """ The worker thread: the sequence, then "done" whatever happened. """
        try:
            self.result = sequence(self)
        finally:
            self.questions.put(Question("done"))

    # Called by the window, on the Tk thread

    def next_question(self):
        """ The next question asked, None while there is none. Never waits. """
        try:
            return self.questions.get_nowait()
        except queue.Empty:
            return None

    def poll(self):
        """ Take in the questions asked since the last call. """
        shown = self.shown
        question = self.next_question()
        while question is not None:
            if question.kind in ("info", "error"):
                shown.message = question
            elif question.kind == "done":
                shown.waiting = None
                shown.done = True
            else:
                shown.waiting = question
            question = self.next_question()

    def answer(self, value):
        """ Answer the question on show: the sequence goes on. """
        shown = self.shown
        if value is None and shown.waiting is not None and shown.waiting.kind in ("secret", "file"):
            shown.locked = True
        shown.waiting = None
        shown.message = None
        self.answers.put(value)

    def cancel(self):
        """ Stop the sequence: the question it waits on, and any after it, get None. """
        self.cancelled.set()
        self.answers.put(None)

    # Called by the sequence, on the worker thread

    def ask(self, question):
        """ Hand a question to the window and wait for its answer. """
        if self.cancelled.is_set():
            return None
        self.questions.put(question)
        answer = self.answers.get()
        return None if self.cancelled.is_set() else answer

    def ask_secret(self, title, prompt):
        """ A password, "" when left empty, None when cancelled. """
        return self.ask(Question("secret", title, prompt))

    def ask_file(self, title, filetypes):
        """ The path of a file, "" or None when cancelled. """
        return self.ask(Question("file", title, extra=filetypes))

    def confirm_members(self, search):
        """ "use", "only" or None: see raw_image.confirm_found_members. """
        return self.ask(Question("members", "RAID members found", extra=search))

    def show_info(self, title, message):
        """ Something to tell the examiner: the sequence goes on without waiting. """
        self.questions.put(Question("info", title, message))

    def show_error(self, title, message):
        """ Why something did not open: the sequence goes on without waiting. """
        self.questions.put(Question("error", title, message))


def raw_image_sequence(paths, _detected):
    """ The sequence that opens a raw disk image: it can be encrypted, hold encrypted volumes
    or have RAID members beside it. Whether it asks anything is known only once it has run. """
    return lambda asker: unlock_raw_input(paths, asker)


def backup_sequence(paths, detected):
    """ The sequence that asks for the password of a backup.
    The detection has read that on its own thread: the window does not read the backup again. """
    if not detected.encrypted:
        return None
    return lambda asker: unlock_backup(paths[0], asker)


def unlock_backup(path, asker):
    """
    Ask through asker for the password of the backup at path until one decrypts it.
    Returns:
        The keys as decrypt_itunes_backup returns them, or None when the examiner cancels.
    """
    prompt = BACKUP_PROMPT
    while True:
        password = asker.ask_secret(BACKUP_TITLE, prompt)
        if password is None:
            return None
        keys, message = decrypt_itunes_backup(path, password)
        if keys:
            return keys
        prompt = f"{message}. {BACKUP_PROMPT}"


UNLOCKERS = {"raw": raw_image_sequence, "itunes": backup_sequence}
