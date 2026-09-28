"""The built iLEAPP's entry point: one executable, the window or the command line.

Started without arguments, the way a double-click starts it, it opens the window.
Started with arguments it is the command line, exactly as ileapp.py is from source, so
tools that run `ileapp -t fs -i ... -o ...` see no difference. Where no window can open,
as over SSH on Linux, it prints the command line's help instead of failing.

packaging/ileapp.spec builds this file, not ileapp.py or ileappGUI.py, which stay the way
to run iLEAPP from source. The choice depends on the arguments, never on the file's name,
so the executable may be renamed.
"""

import multiprocessing
import os
import sys

if not getattr(sys, 'frozen', False):
    # From source, so the tests can run this file; a build carries both programs.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def user_arguments(argv):
    """The arguments a user gave, without the -psn_ serial number that older versions of
    macOS pass to an app started from the Finder."""
    return [arg for arg in argv if not arg.startswith('-psn_')]


def can_open_a_window(platform=sys.platform, environ=None):
    """False only where a window certainly cannot open: Linux, BSD and the like with no
    display. Windows and macOS always have one for a logged-in user."""
    environ = os.environ if environ is None else environ
    if platform in ('win32', 'darwin'):
        return True
    return bool(environ.get('DISPLAY') or environ.get('WAYLAND_DISPLAY'))


def wants_window(args, platform=sys.platform, environ=None):
    """True when these arguments ask for the window rather than the command line.

    --selfcheck goes to the window's code, which tests itself and exits before drawing
    anything; it is how a build is smoke tested headlessly.
    """
    if args == ['--selfcheck']:
        return True
    return not args and can_open_a_window(platform, environ)


def main():
    sys.argv[1:] = user_arguments(sys.argv[1:])
    if wants_window(sys.argv[1:]):
        # ileappGUI builds and runs its window when it is imported.
        import ileappGUI  # noqa: F401  pylint: disable=import-outside-toplevel,unused-import
        return 0
    from ileapp import main as cli_main  # pylint: disable=import-outside-toplevel
    cli_main()
    return 0


if __name__ == '__main__':
    # Nothing in iLEAPP starts a process through multiprocessing today. If something
    # does, a frozen child re-runs this executable, and without this it would open a
    # second window or parse the parent's arguments again.
    multiprocessing.freeze_support()
    sys.exit(main())
