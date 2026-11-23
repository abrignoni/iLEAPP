"""
Looking at the disk without holding up the window.
A drive or a network share that stops answering can block a call as simple as os.stat
for minutes, and nothing can interrupt it. So each question runs on a thread of its own, and the
window waits for the answer a moment, once..
"""

import os
import stat
import threading
import time

FILE, FOLDER, OTHER, MISSING, SILENT = "file", "folder", "other", "missing", "silent"
PENDING = "pending"

WAIT = 0.05  # seconds the window waits for an answer
FRESH = 0.5  # seconds an answer is good for
PATIENCE = 3  # seconds a question can take before the last answer no longer holds
FORGET = 60  # seconds before an answer nobody asks for again is dropped

PROBES = {}


class Probe:
    """ One question being answered on its own thread. """

    def __init__(self, work, previous):
        self.previous = previous
        self.answer = SILENT
        self.started = time.monotonic()
        self.finished = threading.Event()
        self.waited = False
        self.delivered = False
        threading.Thread(target=self.run, args=(work,), daemon=True).start()

    def run(self, work):
        """ On the thread: get the answer. """
        try:
            self.answer = work()
        finally:
            self.finished.set()

    def age(self):
        """ The seconds since the question was asked. """
        return time.monotonic() - self.started

    def is_stale(self, fresh):
        """ Whether the question must be asked again: answered, told, and too long ago. """
        return self.finished.is_set() and self.delivered and self.age() > fresh

    def result(self, wait):
        """ The answer. While there is none, the last one for a while, and then SILENT. """
        if not self.waited:
            self.waited = True
            self.finished.wait(wait)
        if self.finished.is_set():
            self.delivered = True
            return self.answer
        return self.previous if self.age() < PATIENCE else SILENT


def ask(key, work, wait=WAIT, fresh=FRESH):
    """
    The answer to a question.
    Args:
        key: what identifies the question.
        work (function): gets the answer, on another thread: it must not touch a Tk object.
        wait (float): the seconds the window can wait, the first time only.
        fresh (float): the seconds an answer already told can be given again.
    """
    probe = PROBES.get(key)
    if probe is None or probe.is_stale(fresh):
        probe = PROBES[key] = Probe(work, probe.answer if probe else PENDING)
        for old_key, old in list(PROBES.items()):
            if old.finished.is_set() and old.age() > FORGET:
                del PROBES[old_key]
    return probe.result(wait)


def status_of(path):
    """ What a path is, from the disk. A stat call changes nothing on the evidence. """
    try:
        mode = os.stat(path).st_mode
    except (OSError, ValueError):
        return MISSING
    if stat.S_ISDIR(mode):
        return FOLDER
    return FILE if stat.S_ISREG(mode) else OTHER


def path_status(path):
    """ FILE, FOLDER, OTHER, MISSING, PENDING or SILENT, from status_of() on its own thread. """
    return ask(("status", path), lambda: status_of(path))
