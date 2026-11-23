"""
Leaving at once when the window has closed, without losing what the exit hooks do.
"""

import ast
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

PROGRAM = """
import atexit, sys
from leapp_functions.app.gui import quick_exit

class Noisy:
    def __del__(self):
        sys.stdout.write("freed\\n")

kept = Noisy()
atexit.register(sys.stdout.write, "hook\\n")
sys.stdout.write("end\\n")  # not flushed: stdout is a pipe here
{ending}
"""


def run(ending):
    """ Run PROGRAM with this ending in a process of its own, and return what it did. """
    return subprocess.run([sys.executable, "-c", PROGRAM.format(ending=ending)], cwd=REPO_ROOT,
                          capture_output=True, text=True, check=False)


def is_standard(node):
    """ Whether an import statement imports from the standard library. """
    name = node.names[0].name if isinstance(node, ast.Import) else node.module
    return name.partition(".")[0] in sys.stdlib_module_names


class QuickExitTests(unittest.TestCase):
    """ What leaving at once keeps, and what it skips. """

    def test_after_the_window_closed_hooks_run_and_nothing_is_freed(self):
        """ The hooks have run, the output is written, and __del__ has not run. """
        done = run("quick_exit.window_closed()")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, "end\nhook\n")

    def test_before_the_window_closed_the_exit_code_is_kept(self):
        """ A program stopped before its window has closed leaves the usual way. """
        done = run("sys.exit(3)")
        self.assertEqual(done.returncode, 3)
        self.assertIn("hook", done.stdout)

    def test_it_comes_before_the_other_imports_of_ours_in_the_window_program(self):
        """ Imported later, its hook would run before the others and skip them. """
        tree = ast.parse((REPO_ROOT / "ileappGUI.py").read_text(encoding="utf-8"))
        imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        first = next(node for node in imports if not is_standard(node))
        self.assertEqual(first.module, "leapp_functions.app.gui")
        self.assertEqual([alias.name for alias in first.names], ["quick_exit"])


if __name__ == "__main__":
    unittest.main()
