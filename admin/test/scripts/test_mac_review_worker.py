"""Check pickup across updates, offline periods and retries without a model or GitHub."""
import os
import sqlite3
import subprocess
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
                   "user": {"login": "contributor", "id": 42}}
        self.enterContext(patch.object(worker.pilot, "get_pr", return_value=self.pr))
        self.expected = self.enterContext(patch.object(worker, "expected_workflows", return_value=set()))
        self.alert = self.enterContext(patch.object(worker, "notify"))
        self.checks = self.enterContext(patch.object(worker, "checks", return_value=[("flag", "SUCCESS", "Flag PR for Mac review", "")]))
        self.enterContext(patch.object(worker, "review_packet",
                                       return_value={"context": {"delivery": "contributor"}}))
        self.model = self.enterContext(patch.object(worker, "analyze", return_value={
            "summary": "private review", "public_comments": []}))

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

    def test_labeled_owner_pr_is_skipped_even_with_a_cached_result(self):
        self.pr["user"] = {"login": "renamed-maintainer", "id": worker.pilot.OWNER}
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        worker.run()
        with worker.contextlib.closing(worker.pilot.database()) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM pickup").fetchone(), (0,))
            self.pr["head"]["sha"] = "b"*40
            with db:
                db.execute("INSERT INTO pickup VALUES(?,?,?)", (11, "b"*40, "stale result"))
        with patch.object(worker.pilot, "finish") as finish:
            worker.run()
            finish.assert_not_called()
        self.model.assert_not_called()
        self.checks.assert_not_called()
        self.alert.assert_not_called()
        self.assertFalse((self.root / "reports").exists())

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
        with patch.object(worker.subprocess, "Popen", side_effect=FileNotFoundError) as send:
            worker.run()
            send.assert_called_once()
            args = send.call_args.args[0]
            self.assertEqual(args[:5], ["codex", "queue", "--thread", thread, "--message"])
            self.assertIn(str(self.root / "reports" / ("PR-11-" + "b"*40 + ".md")), args[5])
            self.assertNotIn("private review", args[5])
        self.issues.return_value = []
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, thread)
        with patch.object(worker.subprocess, "Popen") as send:
            send.return_value.wait.return_value = 0
            worker.run()
            worker.run()
            send.assert_called_once()
        self.model.assert_called_once()

    def test_worker_restart_after_codex_accepts(self):
        thread = "11111111-1111-4111-8111-111111111111"
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, thread)
            db.execute("INSERT INTO reviews VALUES(11,?,?)", ("a"*40, "report"))
            db.commit()
        # Use real child processes and SQLite. The sender exits abruptly at the
        # point between the CLI's acknowledgement and the local SQL commit.
        fake = self.root / "codex"
        fake.write_text("#!/bin/sh\necho called >> calls\n"
                        'echo "Queued message 22222222-2222-4222-8222-222222222222 for thread $3."\n')
        fake.chmod(0o700)
        script = """
import os, sys
from pathlib import Path
import mac_review_worker as w
w.pilot.STATE = Path.cwd()
if sys.argv[1] == "crash":
    send = w.queue_report
    def interrupted(*args):
        assert send(*args)
        os._exit(77)
    w.queue_report = interrupted
with w.pilot.database() as db, (w.pilot.STATE / "pickup.lock").open("a") as lock:
    w.fcntl.flock(lock, w.fcntl.LOCK_EX)
    w.deliver_inbox(db)
"""
        env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                   PYTHONPATH=str(Path(worker.__file__).parent))
        for mode, expected in (("crash", 77), ("restart", 0), ("idle", 0)):
            result = subprocess.run([sys.executable, "-B", "-c", script, mode],
                                    env=env, cwd=self.root, check=False, timeout=10)
            self.assertEqual(result.returncode, expected)
        self.assertEqual((self.root / "calls").read_text().splitlines(), ["called"])
        with worker.contextlib.closing(worker.pilot.database()) as db:
            self.assertEqual(db.execute("SELECT pr,head FROM inbox_recorded").fetchall(),
                             [(11, "a"*40)])

    def test_uncertain_and_unstartable_sends_do_not_block_later_reviews(self):
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, "11111111-1111-4111-8111-111111111111")
            with db:
                db.executemany("INSERT INTO reviews VALUES(?,?,?)",
                               [(pr, "a"*40, "report") for pr in (11, 12, 13, 14)])
            # Two ambiguous results, a failure before launch, then a successful send.
            with patch.object(worker, "queue_report", side_effect=[False, False, None, True]) as send:
                worker.run()
                self.assertEqual([call.args[1] for call in send.call_args_list], [11, 12, 13, 14])
            with patch.object(worker, "queue_report", return_value=None) as send:
                worker.run()
                self.assertEqual([call.args[1] for call in send.call_args_list], [13])
            self.assertEqual(self.alert.call_count, 2)
            self.assertEqual(db.execute("SELECT pr FROM inbox_recorded").fetchall(), [(14,)])
            worker.resolve_inbox(db, 11, "a"*40, "received")
            worker.resolve_inbox(db, 12, "a"*40, "retry")
            with patch.object(worker, "queue_report", return_value=True) as send:
                worker.run()
                worker.run()
                self.assertEqual([call.args[1] for call in send.call_args_list], [12, 13])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM inbox_recorded").fetchone(), (4,))
        self.model.assert_not_called()

    def test_manual_retry_cannot_race_a_surviving_sender_or_a_late_receipt(self):
        thread = "11111111-1111-4111-8111-111111111111"
        head = "a"*40
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, thread)
            with db:
                db.execute("INSERT INTO reviews VALUES(11,?,?)", (head, "report"))
            with patch.object(worker, "queue_report", return_value=False):
                worker.run()
            receipt = self.root / f"inbox-11-{head}.receipt"
            with receipt.open("wb") as child_output:
                worker.fcntl.flock(child_output, worker.fcntl.LOCK_EX)
                with self.assertRaisesRegex(ValueError, "still running"):
                    worker.resolve_inbox(db, 11, head, "retry")
                child_output.write(f"Queued message {thread} for thread {thread}.\n".encode())
            with self.assertRaisesRegex(ValueError, "acknowledged"):
                worker.resolve_inbox(db, 11, head, "retry")
            def deny_commit(action, operation, *_):
                if action == sqlite3.SQLITE_TRANSACTION and operation == "COMMIT":
                    return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            db.set_authorizer(deny_commit)
            try:
                with self.assertRaises(sqlite3.DatabaseError):
                    worker.resolve_inbox(db, 11, head, "received")
            finally:
                db.set_authorizer(None)
            self.assertTrue(receipt.is_file())
            with patch.object(worker, "queue_report") as send:
                worker.run()
                send.assert_not_called()
            self.assertEqual(db.execute("SELECT pr FROM inbox_recorded").fetchall(), [(11,)])

    def test_interrupted_warning_resumes_without_resending(self):
        with worker.contextlib.closing(worker.pilot.database()) as db:
            worker.configure_inbox(db, "11111111-1111-4111-8111-111111111111")
            with db:
                db.execute("INSERT INTO reviews VALUES(11,?,?)", ("a"*40, "report"))
        self.alert.side_effect = SystemExit
        with patch.object(worker, "queue_report", return_value=False) as send:
            with self.assertRaises(SystemExit):
                worker.run()
            self.alert.side_effect = None
            worker.run()
            worker.run()
            send.assert_called_once()
        self.assertEqual(self.alert.call_count, 2)

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
