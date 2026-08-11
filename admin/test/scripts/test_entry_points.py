"""The command line and GUI entry points must load on every supported Python.

The artifact import test covers scripts/, but the entry points themselves sat
outside any version-matrixed check, so a change to either could break on the
oldest supported Python and only surface when a user ran it.

The two are checked differently on purpose. ileapp.py guards its startup with
'if __name__', so it can be imported outright, which catches import-time errors
as well as syntax. ileappGUI.py builds its window at module level, so importing
it would need a display that CI does not have; compiling it still catches the
syntax-level breakage this is chiefly guarding against, such as an f-string
that only parses on Python 3.12 (PEP 701).
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CLI_ENTRY_POINT = REPO_ROOT / 'ileapp.py'
GUI_ENTRY_POINT = REPO_ROOT / 'ileappGUI.py'


class TestEntryPoints(unittest.TestCase):

    def test_cli_entry_point_imports(self):
        """ileapp.py must import, and expose main()."""
        self.assertTrue(CLI_ENTRY_POINT.is_file(), f'{CLI_ENTRY_POINT} is missing')
        spec = importlib.util.spec_from_file_location('ileapp_entry_point_check',
                                                      CLI_ENTRY_POINT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, 'main'), 'ileapp.py no longer exposes main()')

    def test_gui_entry_point_compiles(self):
        """ileappGUI.py must at least compile; it cannot be imported without a display."""
        self.assertTrue(GUI_ENTRY_POINT.is_file(), f'{GUI_ENTRY_POINT} is missing')
        source = GUI_ENTRY_POINT.read_text(encoding='utf-8', errors='replace')
        try:
            compile(source, str(GUI_ENTRY_POINT), 'exec')
        except SyntaxError as error:
            self.fail(f'ileappGUI.py does not compile on this Python: '
                      f'line {error.lineno}: {error.msg}')


if __name__ == '__main__':
    unittest.main()
