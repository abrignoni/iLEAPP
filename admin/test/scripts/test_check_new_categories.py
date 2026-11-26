"""The new-category check finds categories outside the agreed list and reports nothing else."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import check_new_categories as check  # noqa: E402

ALLOWED = {"Messaging", "Browsers"}

KNOWN = '__artifacts_v2__ = {"a": {"name": "A", "category": "Messaging"}}\n'
NEW = '__artifacts_v2__ = {"a": {"name": "A", "category": "Smart Fridges"}}\n'
HELPER = ('def _meta(name):\n'
          '    return {"name": name, "category": "Weather Stations"}\n'
          '__artifacts_v2__ = {"a": _meta("A")}\n')
NOT_LITERAL = 'CAT = "Messaging"\n__artifacts_v2__ = {"a": {"name": "A", "category": CAT}}\n'
SUBSCRIPT = ('def _copy(source):\n'
             '    metadata = dict(source)\n'
             '    metadata["category"] = "Lawn Mowers"\n'
             '    return metadata\n')
DATA_ROW = 'def _row(f):\n    return {"line": 1, "category": f.get("category") or ""}\n'


class CategoriesInSource(unittest.TestCase):
    def test_a_listed_category_is_not_reported(self):
        self.assertEqual(check.review({"known": KNOWN}, ALLOWED), {})

    def test_a_category_outside_the_list_is_reported(self):
        self.assertEqual(check.review({"new": NEW}, ALLOWED), {"new": (["Smart Fridges"], [])})

    def test_a_category_set_inside_a_helper_is_reported(self):
        self.assertEqual(check.review({"helper": HELPER}, ALLOWED),
                         {"helper": (["Weather Stations"], [])})

    def test_a_category_that_is_not_a_literal_is_reported_as_unreadable(self):
        self.assertEqual(check.review({"expr": NOT_LITERAL}, ALLOWED), {"expr": ([], [2])})

    def test_a_category_assigned_by_subscript_is_reported(self):
        self.assertEqual(check.review({"copy": SUBSCRIPT}, ALLOWED),
                         {"copy": (["Lawn Mowers"], [])})

    def test_a_category_assigned_from_a_name_is_reported_as_unreadable(self):
        source = 'CAT = "Lawn Mowers"\ndef _copy(m):\n    m["category"] = CAT\n'
        self.assertEqual(check.review({"copy": source}, ALLOWED), {"copy": ([], [3])})

    def test_a_data_row_with_a_category_field_is_not_an_artifact(self):
        self.assertEqual(check.review({"row": DATA_ROW}, ALLOWED), {})

    def test_a_file_that_does_not_parse_is_reported(self):
        self.assertEqual(check.review({"broken": "def (:\n"}, ALLOWED), {"broken": ([], [0])})


class Comment(unittest.TestCase):
    def test_the_comment_mentions_the_maintainer_and_names_the_category(self):
        body = check.render_comment(check.review({"new": NEW}, ALLOWED))
        self.assertIn(check.MARKER, body)
        self.assertIn("@" + check.MAINTAINER, body)
        self.assertIn("`Smart Fridges`", body)

    def test_a_category_the_pr_adds_to_the_list_is_still_reported(self):
        report = check.review({"new": NEW}, ALLOWED)
        body = check.render_comment(report, frozenset({"Smart Fridges"}))
        self.assertIn("@" + check.MAINTAINER, body)
        self.assertIn("`Smart Fridges` (added to the list in this PR)", body)
        self.assertNotIn("please use it", body)

    def test_only_the_bots_own_comment_is_edited(self):
        quoted = {"id": 1, "body": "quoting " + check.MARKER, "user": {"login": "someone"}}
        own = {"id": 2, "body": check.MARKER + " alert", "user": {"login": check.BOT}}
        self.assertIsNone(check.own_comment([quoted]))
        self.assertEqual(check.own_comment([quoted, own])["id"], 2)

    def test_a_clean_result_mentions_no_one(self):
        body = check.render_comment({})
        self.assertIn(check.MARKER, body)
        self.assertNotIn("@", body)


class OlderFormAndListShape(unittest.TestCase):
    def test_the_older_tuple_form_is_read(self):
        source = '__artifacts__ = {"r": ("Smart Fridges", ("*/f",), None)}\n'
        self.assertEqual(check.review({"old": source}, ALLOWED), {"old": (["Smart Fridges"], [])})

    def test_an_older_entry_that_is_not_a_tuple_is_unreadable(self):
        source = 'X = ("Messaging",)\n__artifacts__ = {"r": X}\n'
        self.assertEqual(check.review({"old": source}, ALLOWED), {"old": ([], [2])})

    def test_a_list_of_the_wrong_shape_reads_as_empty(self):
        for text in ('[]', '{"categories": null}', '{"categories": "Messaging"}', 'not json', None):
            self.assertEqual(check.categories_from_list(text), set(), text)
        self.assertEqual(check.categories_from_list('{"categories": ["A", 3]}'), {"A"})


class Rendering(unittest.TestCase):
    def test_pr_supplied_names_render_as_inert_code(self):
        report = {"evil`\n@someone": (["x`y\n@team [link](http://e)"], [])}
        body = check.render_comment(report)
        self.assertNotIn("\n@someone", body)
        self.assertNotIn("\n@team", body)
        self.assertIn("`evil' @someone`", body)
        self.assertEqual(body.count("@"), 3)  # the maintainer, plus two inside code spans


class Network(unittest.TestCase):
    def setUp(self):
        self.saved = check.api_request

    def tearDown(self):
        check.api_request = self.saved

    def test_a_missing_page_stops_the_run(self):
        check.api_request = lambda _token, _url, **_kw: None
        with self.assertRaises(RuntimeError):
            list(check.paginate("t", "https://api/x"))

    def test_an_empty_page_ends_the_list(self):
        check.api_request = lambda _token, _url, **_kw: []
        self.assertEqual(list(check.paginate("t", "https://api/x")), [])

    def test_a_module_that_cannot_be_fetched_is_reported_missing(self):
        files = [{"filename": "scripts/artifacts/a.py", "status": "modified", "contents_url": "u"}]

        def fake(_token, url, **_kw):
            return files if "/files" in url else None
        check.api_request = fake
        sources, proposed, missing = check.pr_sources("t", "o/r", 1)
        self.assertEqual((sources, proposed, missing), ({}, None, ["scripts/artifacts/a.py"]))

    def test_a_category_list_that_cannot_be_fetched_is_reported_missing(self):
        files = [{"filename": "admin/data/artifact_categories.json", "status": "modified",
                  "contents_url": "u"}]

        def fake(_token, url, **_kw):
            return files if "/files" in url else None
        check.api_request = fake
        sources, proposed, missing = check.pr_sources("t", "o/r", 1)
        self.assertEqual((sources, proposed, missing),
                         ({}, None, ["admin/data/artifact_categories.json"]))

    def test_a_label_created_by_another_run_is_used(self):
        calls = []

        def fake(_token, url, method="GET", **_kw):
            calls.append((method, url))
            if url.endswith("/issues/1/comments?per_page=100&page=1"):
                return []
            if url.endswith("/issues/1"):
                return {"labels": []}
            if url.endswith("/labels/new-category"):
                return None if sum(1 for c in calls if c[1].endswith("/labels/new-category")) == 1 else {}
            if url == "https://api.github.com/repos/o/r/labels" and method == "POST":
                raise RuntimeError("HTTP 422: already_exists")
            return {}
        check.api_request = fake
        check.apply_state("t", "o/r", 1, {"m": (["Smart Fridges"], [])})
        self.assertIn(("POST", "https://api.github.com/repos/o/r/issues/1/labels"), calls)


class IncompleteScan(unittest.TestCase):
    def test_a_partial_scan_never_changes_the_alert(self):
        saved = (check.pr_sources, check.apply_state, check.allowed_categories)
        calls = []
        check.pr_sources = lambda *_a: ({"b": NEW}, None, ["scripts/artifacts/a.py"])
        check.apply_state = lambda *a, **_kw: calls.append(a)
        check.allowed_categories = lambda: ALLOWED
        env = {"GITHUB_TOKEN": "t", "PR_NUMBER": "1", "GITHUB_REPOSITORY": "o/r"}
        old = {k: check.os.environ.get(k) for k in env}
        check.os.environ.update(env)
        try:
            self.assertEqual(check.main([]), 0)
        finally:
            check.pr_sources, check.apply_state, check.allowed_categories = saved
            for k, v in old.items():
                if v is None:
                    check.os.environ.pop(k, None)
                else:
                    check.os.environ[k] = v
        self.assertEqual(calls, [])


class AllowedList(unittest.TestCase):
    def test_the_list_reads_and_has_no_duplicates(self):
        data = json.loads(check.ALLOWED_PATH.read_text(encoding="utf-8"))["categories"]
        self.assertEqual(len(data), len(set(data)))
        self.assertTrue(data)

    def test_a_working_tree_is_read_from_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts" / "artifacts").mkdir(parents=True)
            (root / "scripts" / "artifacts" / "new.py").write_text(NEW, encoding="utf-8")
            self.assertEqual(check.review(check.tree_sources(root), ALLOWED),
                             {"new": (["Smart Fridges"], [])})
            (root / "scripts" / "artifacts" / "new.py").write_text(KNOWN, encoding="utf-8")
            self.assertEqual(check.review(check.tree_sources(root), ALLOWED), {})


if __name__ == "__main__":
    unittest.main()
