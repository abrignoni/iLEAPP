"""
A new run takes a new process.
"""

import os
import subprocess
import sys


def own_command():
    """ The command that starts this program. A build has no script to name. """
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, os.path.abspath(sys.argv[0])]


def start():
    """ Start the program again, with nothing from this process.
    Raises:
        OSError: the program could not be started. Nothing has changed.
    """
    environment = {**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"}
    return subprocess.Popen(own_command(), env=environment)
