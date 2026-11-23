"""
Leave at once when the window has closed.
After a large run, millions of objects are still alive, and Python frees them one by one on the
way out, which takes many seconds with no window on show. The system takes the memory back in one
go when the process ends, so that work can be skipped. It is not skipped when the window closes
during a run: the LAVA database is still open, and leaving the usual way removes its journal.
Hooks run from the last one registered to the first one. The program must import this module
before any other of its own, and before logging, so that its hook runs after the others, which
still have work to do: closing the log, deleting the copy made of a tar.
"""

import atexit
import os
import sys
import threading

WINDOW_CLOSED = threading.Event()


def window_closed():
    """ The window has closed: the program can leave at once. """
    WINDOW_CLOSED.set()


def leave():
    """ Leave without freeing the objects. Until the window has closed, leaving goes the usual way,
    which keeps the exit code and the traceback of a program stopped by an error. """
    if WINDOW_CLOSED.is_set():
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)


atexit.register(leave)
