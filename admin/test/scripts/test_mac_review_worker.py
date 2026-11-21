"""Check pickup across updates, offline periods and retries without a model or GitHub."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
if sys.platform == "win32":
    worker = None
else:
    import mac_review_worker as worker


@unittest.skipIf(sys.platform == "win32", "launchd worker uses POSIX file locking")
class PickupTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.enterContext(patch.object(worker.pilot, "STATE", self.root))
        self.issues = self.enterContext(patch.object(worker.pilot, "api", return_value=[]))
        self.pr = {"state": "open", "draft": False, "number": 11, "head": {"sha": "a"*40},
                   "user": {"login": "abrignoni", "id": worker.pilot.OWNER}}
        self.enterContext(patch.object(worker.pilot, "get_pr", return_value=self.pr))
        self.expected = self.enterContext(patch.object(worker, "expected_workflows", return_value=set()))
        self.alert = self.enterContext(patch.object(worker, "notify"))
        self.checks = self.enterContext(patch.object(worker, "checks", return_value=[("flag", "SUCCESS", "Flag PR for Mac review", "")]))
        self.enterContext(patch.object(worker, "review_packet",
                                       return_value={"context": {"delivery": "private"}}))
        self.model = self.enterContext(patch.object(worker, "analyze", return_value={
            "summary": "private review", "public_comments": [{"body": "private"}]}))

    def test_offline_pickup_update_and_idle(self):
        worker.run()
        self.model.assert_not_called()
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.checks.return_value = []
        worker.run()
        self.model.assert_not_called()
        self.checks.return_value = [("checks", "IN_PROGRESS", "Tests", "")]
        worker.run()
        self.model.assert_not_called()
        self.checks.return_value = [("checks", "SUCCESS", "Tests", "")]
        worker.run()
        worker.run()
        self.model.assert_called_once()
        self.issues.assert_called_with(
            worker.pilot.REPO + "/issues?state=open&labels=mac-review&per_page=100", pages=True)
        report, = (self.root / "reports").glob("*.md")
        self.assertEqual(report.read_text(), "private review")
        self.pr["head"]["sha"] = "b"*40
        worker.run()
        self.assertEqual(self.model.call_count, 2)
        self.assertEqual(len(list((self.root / "reports").glob("*.md"))), 2)

    def test_flag_alone_cannot_finish_a_python_change(self):
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.expected.return_value = {"Python Lint Check"}
        worker.run()
        self.model.assert_not_called()

    def test_private_inbox_delivers_only_new_revisions_and_retries(self):
        thread = "11111111-1111-4111-8111-111111111111"
        with worker.contextlib.closing(worker.pilot.database()) as db:
            db.execute("INSERT INTO reviews VALUES(11,?,?)", ("a"*40, "old report"))
            db.commit()
            worker.configure_inbox(db, thread)
        self.pr["head"]["sha"] = "b"*40
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        with patch.object(worker.subprocess, "run", side_effect=OSError) as send:
            worker.run()
            send.assert_called_once()
            args = send.call_args.args[0]
            self.assertEqual(args[:5], ["codex", "queue", "--thread", thread, "--message"])
            self.assertIn(str(self.root / "reports" / ("PR-11-" + "b"*40 + ".md")), args[5])
            self.assertNotIn("private review", args[5])
        self.issues.return_value = []
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, thread)
        with patch.object(worker.subprocess, "run") as send:
            worker.run()
            worker.run()
            send.assert_called_once()
        self.model.assert_called_once()

    def test_workflow_filters_and_missing_late_checks(self):
        self.assertTrue(worker.path_match("scripts/artifacts/demo.py", ["**.py"]))
        self.assertFalse(worker.path_match("scripts/artifacts/demo.py", ["scripts/*.py"]))
        self.assertTrue(worker.path_match(".github/workflows/review.yml", [".github/workflows/review.yml"]))
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.expected.return_value = {"Tests", "PR review pilot tests"}
        self.checks.return_value = [("flag", "SUCCESS", "Flag PR for Mac review", ""),
                                    ("tests", "SUCCESS", "Tests", "")]
        worker.run()
        self.model.assert_not_called()

    def test_skip_directives_and_visible_run_identity(self):
        with patch.object(worker.pilot, "api", return_value={"message": "docs [skip ci]"}):
            self.assertTrue(worker.ci_skipped("a"*40))
        with patch.object(worker.pilot, "api", return_value={"message": "skip ci tests"}):
            self.assertFalse(worker.ci_skipped("a"*40))
        with self.assertRaises(ValueError):
            worker.path_match("file1", ["file[0-9]"])
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.expected.return_value = {"Tests"}
        self.checks.return_value = [("suite", "SUCCESS", "Tests", "")]
        worker.run()
        self.model.assert_not_called()

    def test_closed_and_draft_never_start_model(self):
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.pr["draft"] = True
        worker.run()
        self.pr.update(draft=False, state="closed")
        worker.run()
        self.model.assert_not_called()

    def test_delivery_retry_uses_saved_result(self):
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        with patch.object(worker.pilot, "finish", side_effect=OSError("offline")):
            worker.run()
        with patch.object(worker.time, "time", return_value=10**12):
            worker.run()
        self.model.assert_called_once()
        self.assertEqual(len(list((self.root / "reports").glob("*.md"))), 1)


@unittest.skipIf(sys.platform == "win32", "macOS worker uses system Ruby for YAML")
class WorkflowFilterTest(unittest.TestCase):
    def test_workflow_only_change_waits_for_its_own_suite(self):
        folder = Path(__file__).resolve().parents[3] / ".github/workflows"
        pr = {"number": 11, "head": {"sha": "a"*40}, "base": {"ref": "main"}}

        def contents(url, **_kwargs):
            if "/git/commits/" in url:
                return {"message": "update workflow"}
            if "/pulls/11/files?" in url:
                return [{"filename": ".github/workflows/review_pilot_tests.yml"}]
            if "/contents/.github/workflows?" in url:
                return [{"name": f.name} for f in folder.glob("*.yml")]
            return (folder / url.split("?")[0].rsplit("/", 1)[1]).read_text()

        with patch.object(worker.pilot, "api", side_effect=contents), patch.object(worker.pilot, "checked_pr"):
            self.assertEqual(worker.expected_workflows(pr), {"PR review pilot tests"})


if __name__ == "__main__":
    unittest.main()
