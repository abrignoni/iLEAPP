"""Exercise queue, fixture context, delivery routing and safe retries with synthetic PRs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import review_ileapp_pr as pilot


class PilotTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.enterContext(patch.object(pilot, "STATE", Path(tmp.name)))
        self.db = pilot.database()
        self.addCleanup(self.db.close)
        self.head = "a" * 40
        self.pr = {"number": 1, "user": {"id": 42, "login": "contributor"},
                   "state": "open", "draft": False, "head": {"sha": self.head},
                   "base": {"sha": "b" * 40, "repo": {"full_name": "abrignoni/iLEAPP"}},
                   "changed_files": 1}
        self.reviews = []
        self.posts = []
        self.files = [{"status": "added", "filename": "scripts/artifacts/demo.py"}]
        self.enterContext(patch.object(pilot, "api", side_effect=self.api))
        self.comments = [{"path": self.files[0]["filename"], "line": 1, "body": "A test finding."}]

    def api(self, path, *, pages=False, body=None, raw=False):
        if pages:
            self.assertIn("per_page=100", path)
        if raw:
            self.assertIn("/contents/", path)
        if body is not None:
            self.posts.append(body)
            self.reviews.append(dict(body, user={"id": 27}))
            return {}
        if path == "user":
            return {"id": 27}
        if "/files?" in path:
            return self.files
        if "/reviews?" in path:
            return self.reviews
        if "/pulls?" in path:
            return [self.pr]
        if path.endswith("/pulls/1"):
            return self.pr
        if "image_manifest.json" in path:
            return json.dumps({"images": [{"sample_data_key": "public-image"}]})
        if "/contents/scripts/artifacts/demo.py" in path:
            return "__artifacts_v2__ = {'demo': {'sample_data': {'public-image': '1 row'}}}"
        raise AssertionError(path)

    def test_contributor_end_to_end(self):
        self.assertEqual(pilot.queue(self.db)[0]["delivery"], "contributor")
        self.assertEqual(pilot.context(1)["manifest_matches"], {"demo": ["public-image"]})
        pilot.finish(self.db, 1, self.head, "private notes", self.comments)
        self.assertEqual(self.posts[0]["comments"][0]["side"], "RIGHT")
        self.assertNotIn("private notes", json.dumps(self.posts))
        self.assertEqual(pilot.queue(self.db), [])
        self.db.execute("DELETE FROM reviews")
        self.db.commit()
        pilot.finish(self.db, 1, self.head, "retry after interruption", self.comments)
        self.assertEqual(len(self.posts), 1)
        self.pr["head"]["sha"] = "c" * 40
        self.assertEqual(len(pilot.queue(self.db)), 1)

    def test_owner_end_to_end(self):
        self.pr["user"]["id"] = pilot.OWNER
        self.assertEqual(pilot.context(1)["delivery"], "private")
        with self.assertRaises(ValueError):
            pilot.finish(self.db, 1, self.head, "private notes", self.comments)
        pilot.finish(self.db, 1, self.head, "private notes", [])
        report = pilot.STATE / "reports" / f"PR-1-{self.head}.md"
        self.assertEqual(report.read_text(), "private notes")
        self.assertEqual(report.stat().st_mode & 0o077, 0)
        self.assertEqual(self.posts, [])
        self.assertEqual(self.db.execute("SELECT result FROM reviews").fetchone(), ("private notes",))

    def test_stale_draft_and_closed(self):
        self.pr["draft"] = True
        self.assertEqual(pilot.queue(self.db), [])
        for state, draft, sha in [("open", True, self.head), ("closed", False, self.head),
                                  ("open", False, "c" * 40)]:
            self.pr.update(state=state, draft=draft)
            self.pr["head"]["sha"] = sha
            with self.assertRaises(ValueError):
                pilot.finish(self.db, 1, self.head, "private notes", self.comments)
        self.assertFalse(self.posts)

    def test_touched_case_is_not_a_verified_run(self):
        self.files.append({"status": "modified", "filename": "admin/test/cases/testdata.demo.json"})
        self.pr["changed_files"] = 2
        self.assertEqual(pilot.context(1)["test_files_touched"], ["demo"])
        self.assertFalse(pilot.context(1)["manifest_matches"])


if __name__ == "__main__":
    unittest.main()
