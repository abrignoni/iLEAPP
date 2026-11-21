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
        self.alert = self.enterContext(patch.object(worker, "notify"))
        self.checks = self.enterContext(patch.object(worker, "checks", return_value=[]))
        self.enterContext(patch.object(worker, "review_packet",
                                       return_value={"context": {"delivery": "private"}}))
        self.model = self.enterContext(patch.object(worker, "analyze", return_value={
            "summary": "private review", "public_comments": [{"body": "private"}]}))

    def test_offline_pickup_update_and_idle(self):
        worker.run()
        self.model.assert_not_called()
        self.issues.return_value = [{"number": 11, "pull_request": {}}]
        self.checks.return_value = [("checks", "IN_PROGRESS")]
        worker.run()
        self.model.assert_not_called()
        self.checks.return_value = [("checks", "SUCCESS")]
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


if __name__ == "__main__":
    unittest.main()
