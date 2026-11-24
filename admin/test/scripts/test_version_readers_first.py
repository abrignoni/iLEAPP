"""Artifacts that read the iOS version run before the ones that choose a query by it."""
import unittest
from pathlib import Path
from types import SimpleNamespace

import ileapp
from scripts import plugin_loader

ARTIFACTS = Path(__file__).resolve().parents[3] / 'scripts' / 'artifacts'

# Version setters that crunch_artifacts places itself.
PLACED_BY_CRUNCH = {'lastBuild', 'iTunesBackupInfo', 'iosVersionDiagnosticReports'}


def specs(*plugin_names):
    return [SimpleNamespace(name=name) for name in plugin_names]


def names(plugins):
    return [plugin.name for plugin in plugins]


class TestVersionReadersFirst(unittest.TestCase):
    def test_readers_move_to_the_front_in_their_own_order(self):
        ordered = ileapp.version_readers_first(specs(
            'a', 'Ph087UFEDdevcievaluesplist', 'b', 'system_version_plist', 'c'))
        self.assertEqual(names(ordered), [
            'system_version_plist', 'Ph087UFEDdevcievaluesplist', 'a', 'b', 'c'])

    def test_nothing_is_added_or_dropped(self):
        self.assertEqual(names(ileapp.version_readers_first(specs('b', 'a'))), ['b', 'a'])
        self.assertEqual(names(ileapp.version_readers_first(specs(
            'b', 'system_version_plist', 'a'))), ['system_version_plist', 'b', 'a'])
        self.assertEqual(ileapp.version_readers_first([]), [])

    def test_crash_report_fallback_goes_after_the_readers(self):
        fallback = SimpleNamespace(name=ileapp.CRASH_REPORT_VERSION)
        placed = ileapp.add_crash_report_version(specs(
            'last_build', 'system_version_plist', 'Ph087UFEDdevcievaluesplist', 'a', 'b'), fallback)
        self.assertEqual(names(placed), ['last_build', 'system_version_plist', 'Ph087UFEDdevcievaluesplist',
                                         ileapp.CRASH_REPORT_VERSION, 'a', 'b'])
        self.assertEqual(names(ileapp.add_crash_report_version(specs('a'), fallback)),
                         [ileapp.CRASH_REPORT_VERSION, 'a'])
        self.assertEqual(names(ileapp.add_crash_report_version(specs('last_build', 'a'), fallback)),
                         ['last_build', ileapp.CRASH_REPORT_VERSION, 'a'])

    def test_stopped_count_leaves_out_the_added_steps(self):
        self.assertEqual(ileapp.chosen_count(specs(ileapp.CRASH_REPORT_VERSION, 'a')), 1)
        self.assertEqual(ileapp.chosen_count(specs('last_build', 'system_version_plist',
                                                   ileapp.CRASH_REPORT_VERSION, 'a')), 2)

    def test_every_version_setter_is_placed(self):
        loader = plugin_loader.PluginLoader()
        reader_modules = {loader[name].module_name for name in ileapp.VERSION_READERS}
        setters = {path.stem for path in ARTIFACTS.glob('*.py')
                   if 'iOS.set_version(' in path.read_text(encoding='utf-8')}
        self.assertEqual(setters, reader_modules | PLACED_BY_CRUNCH)

    def test_a_full_run_list_starts_with_the_readers(self):
        loader = plugin_loader.PluginLoader()
        ordered = ileapp.version_readers_first(
            sorted(loader.plugins, key=lambda plugin: plugin.category))
        self.assertEqual(tuple(names(ordered)[:len(ileapp.VERSION_READERS)]),
                         ileapp.VERSION_READERS)
        self.assertEqual(len(ordered), len(list(loader.plugins)))


if __name__ == '__main__':
    unittest.main()
