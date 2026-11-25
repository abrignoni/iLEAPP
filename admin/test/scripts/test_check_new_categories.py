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
        self.assertIn('"Smart Fridges"', body)

    def test_a_category_the_pr_adds_to_the_list_is_still_reported(self):
        report = check.review({"new": NEW}, ALLOWED)
        body = check.render_comment(report, frozenset({"Smart Fridges"}))
        self.assertIn("@" + check.MAINTAINER, body)
        self.assertIn('"Smart Fridges" (added to the list in this PR)', body)
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
