"""
leapp_functions.app.gui: sentences the window builds from counts, without opening a window.
The secrets and the run are written here, so the test does not depend on one LEAPP's configuration.
"""

from types import SimpleNamespace
import unittest

from leapp_functions.app.gui.results import result_rows
from leapp_functions.app.gui.source import summary_text
from leapp_functions.app.gui.status_bar import StatusBar, artifacts_subtitle

SECRETS = [{"name": "signal", "kind": "text", "display": "Signal key"},
           {"name": "threema", "kind": "text", "display": "Threema password or key"},
           {"name": "keychain"}]


def variables(*values):
    """ What summary_text reads from the variables of the fields: their get(). """
    return [SimpleNamespace(get=lambda value=value: value) for value in values]


def worker(with_files, without_files=0, total=None):
    """ A finished run, as result_rows and show_progress read it. """
    summary = SimpleNamespace(with_files=with_files, without_files=without_files, errors=[],
                              run_time="00:00:01")
    total = with_files + without_files if total is None else total
    return SimpleNamespace(shown=SimpleNamespace(done=total, total=total, summary=summary,
                                                 outcome="done", folder="", log_file="",
                                                 stopping=False))


class TestSummaryText(unittest.TestCase):
    """ The one line of the secrets card when a LEAPP has several secrets. """

    def test_none_given(self):
        """ Empty and blank values are not given. """
        self.assertEqual(summary_text(SECRETS, variables("", "  ", "")), "Optional. None of the 3 given.")

    def test_some_given_in_their_order(self):
        """ The names are those shown, in the order of the configuration. """
        self.assertEqual(summary_text(SECRETS, variables("key", "", "/tmp/keychain.plist")),
                         "Optional. 2 of 3 given: Signal key, keychain.")

    def test_one_given(self):
        """ "1 of 3 given", the example of the card. """
        self.assertEqual(summary_text(SECRETS, variables("", "secret", "")),
                         "Optional. 1 of 3 given: Threema password or key.")


class TestArtifactCounts(unittest.TestCase):
    """ "1 artifact", never "1 artifacts". """

    def test_results_files_found(self):
        """ The Files found line of the Results screen. """
        rows = dict(result_rows(worker(1, 215)))
        self.assertEqual(rows["Files found"], "1 artifact · 215 without files")
        rows = dict(result_rows(worker(2, 1)))
        self.assertEqual(rows["Files found"], "2 artifacts · 1 without files")

    def test_progress(self):
        """ The progress of the status bar, called with a stand-in for the bar. """
        shown = []
        for total, expected in ((1, "Progress: 1 of 1 artifact done"),
                                (1208, "Progress: 1,208 of 1,208 artifacts done")):
            stand_in = SimpleNamespace(
                app=SimpleNamespace(app_state=SimpleNamespace(run=SimpleNamespace(worker=worker(0, total=total)))),
                texts=SimpleNamespace(show_progress=lambda title, done, count: shown.append(title)))
            StatusBar.show_progress(stand_in)
            self.assertEqual(shown[-1], expected)

    def test_artifacts_left_out_by_default(self):
        """ The subtitle of the Artifacts screen: "1 slow or large one is", "2 ... ones are". """
        def artifacts(defaults):
            listed = [SimpleNamespace(name=str(index), default=default)
                      for index, default in enumerate(defaults)]
            return SimpleNamespace(listed=listed, selected={item.name for item in listed if item.default})
        self.assertEqual(artifacts_subtitle(artifacts([True, True])), "2 of 2 artifacts selected")
        self.assertEqual(artifacts_subtitle(artifacts([True, False])),
                         "1 of 2 artifacts selected · 1 slow or large one is unselected by default")
        self.assertEqual(artifacts_subtitle(artifacts([True, False, False])),
                         "1 of 3 artifacts selected · 2 slow or large ones are unselected by default")


if __name__ == "__main__":
    unittest.main()
