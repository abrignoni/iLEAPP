"""The default-deselected module list has to name real modules, and cover the expensive ones.

`scripts/modules_to_exclude.py` is matched against `plugin.module_name`, which is the
artifact script's filename stem. An entry that names an artifact instead of its module, or
that survives a module being renamed or deleted, silently does nothing: the checkbox goes
back to selected and nobody notices until a run takes far longer than expected. Nothing
else in the suite reads this file.

The logarchive entry matters most. It is the largest job in iLEAPP by a wide margin, it
now triggers on every full file system extraction because the artifact declares
diagnostics/ and uuidtext/ paths, and its cost is paid during file extraction before any
parsing starts. It has to stay opt-in.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.modules_to_exclude import modules_to_exclude  # pylint: disable=wrong-import-position
from scripts.plugin_loader import PluginLoader  # pylint: disable=wrong-import-position

ARTIFACTS_DIR = REPO_ROOT / 'scripts' / 'artifacts'


class TestExcludedModulesAreReal(unittest.TestCase):
    """Every entry must correspond to a module that exists and is actually loaded."""

    @classmethod
    def setUpClass(cls):
        cls.loaded_module_names = {plugin.module_name for plugin in PluginLoader().plugins}

    def test_no_duplicate_entries(self):
        self.assertEqual(sorted(modules_to_exclude), sorted(set(modules_to_exclude)),
                         'modules_to_exclude contains duplicates')

    def test_each_entry_names_an_existing_artifact_script(self):
        for name in modules_to_exclude:
            with self.subTest(module=name):
                self.assertTrue((ARTIFACTS_DIR / f'{name}.py').is_file(),
                                f'{name} is listed but scripts/artifacts/{name}.py does not exist')

    def test_each_entry_matches_a_loaded_module_name(self):
        # module_name is what the GUI compares against; an entry that never matches is dead.
        for name in modules_to_exclude:
            with self.subTest(module=name):
                self.assertIn(name, self.loaded_module_names,
                              f'{name} never appears as a plugin module_name')


class TestLogarchiveIsOptIn(unittest.TestCase):
    """Unified Logs must not run unless the examiner asks for them."""

    def test_logarchive_is_deselected_by_default(self):
        self.assertIn('logarchive', modules_to_exclude)

    def test_the_entry_covers_every_logarchive_artifact(self):
        # One module supplies the raw import plus twelve dependent artifacts. They all
        # share module_name 'logarchive', so the single entry has to cover the whole set;
        # if any of them ever moved to its own file, this would catch it.
        plugins = [p for p in PluginLoader().plugins if p.name.startswith('logarchive')]
        self.assertGreater(len(plugins), 1, 'expected the logarchive artifact family')
        for plugin in plugins:
            with self.subTest(artifact=plugin.name):
                self.assertEqual(plugin.module_name, 'logarchive')


if __name__ == '__main__':
    unittest.main()
