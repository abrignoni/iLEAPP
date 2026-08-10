# pylint: disable=broad-exception-caught
"""Smoke test: every artifact module must import on the running Python.

Run across the supported Python versions in CI, this is the only check that a
change still parses and imports on the oldest one. Syntax accepted by a newer
interpreter is not always accepted by an older one -- a multi-line expression
inside an f-string, for example, needs 3.12 (PEP 701) -- and lint alone does
not catch it because lint runs on a single, newer version.

It validates *importability*, not parsing correctness (which needs sample
data). Modules are loaded by file path -- mirroring scripts/plugin_loader.py
-- so files with dots in their name load correctly.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / 'scripts' / 'artifacts'

# Floors, not exact counts, so ordinary additions and removals do not fail the
# build while a collapse in what loads still does.
MINIMUM_ARTIFACT_MODULES = 300
MINIMUM_PLUGINS = 600


class TestArtifactImports(unittest.TestCase):

    def test_all_artifact_modules_import(self):
        """Import every scripts/artifacts/*.py and fail on any import error."""
        failures = []
        count = 0
        for py_file in sorted(ARTIFACTS_DIR.glob('*.py')):
            if py_file.name.startswith('__'):
                continue
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                count += 1
            except Exception as exc:
                failures.append(f'{py_file.name}: {type(exc).__name__}: {exc}')

        self.assertEqual(failures, [],
                         f'{len(failures)} artifact import failure(s):\n' + '\n'.join(failures))
        self.assertGreater(count, MINIMUM_ARTIFACT_MODULES,
                           f'Only {count} artifact modules imported - did the search path change?')

    def test_plugin_loader_loads(self):
        """The real PluginLoader must load a healthy number of plugins."""
        from scripts.plugin_loader import PluginLoader
        loader = PluginLoader()
        self.assertGreater(len(loader), MINIMUM_PLUGINS,
                           f'PluginLoader loaded only {len(loader)} plugins')


if __name__ == '__main__':
    unittest.main()
