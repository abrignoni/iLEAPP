"""Tests for the pure logic in run_test_cases.py.

The artifact-execution path is exercised by the runner itself in CI; these
cover baseline selection, normalization, and the comparison verdicts against
synthetic inputs only.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

import run_test_cases as rtc  # noqa: E402  pylint: disable=wrong-import-position


class NormalizeRowsTests(unittest.TestCase):
    def test_temp_extract_path_is_tokenized(self):
        rows = [["admin/test/temp/extract_foo_bar_1750464339/x/y.plist", 1]]
        other = [["admin/test/temp/extract_foo_bar_1999999999/x/y.plist", 1]]
        self.assertEqual(rtc.normalize_rows(rows), rtc.normalize_rows(other))

    def test_row_order_does_not_matter(self):
        self.assertEqual(rtc.normalize_rows([[1, "a"], [2, "b"]]),
                         rtc.normalize_rows([[2, "b"], [1, "a"]]))

    def test_content_change_is_detected(self):
        self.assertNotEqual(rtc.normalize_rows([[1, "a"]]),
                            rtc.normalize_rows([[1, "b"]]))

    def test_tuple_and_list_rows_normalize_alike(self):
        self.assertEqual(rtc.normalize_rows([(1, "a")]), rtc.normalize_rows([[1, "a"]]))


class CompareTests(unittest.TestCase):
    BASE = {"headers": ["A", "B"], "data": [[1, "x"], [2, "y"]]}

    def test_match_returns_no_problems(self):
        self.assertEqual(rtc.compare(["A", "B"], [[2, "y"], [1, "x"]], self.BASE), [])

    def test_header_change_reported(self):
        problems = rtc.compare(["A", "C"], [[1, "x"], [2, "y"]], self.BASE)
        self.assertTrue(any("headers differ" in p for p in problems))

    def test_row_change_reported_with_counts(self):
        problems = rtc.compare(["A", "B"], [[1, "x"], [2, "z"]], self.BASE)
        joined = "\n".join(problems)
        self.assertIn("rows differ", joined)
        self.assertIn("1 new", joined)
        self.assertIn("1 missing", joined)


class LatestBaselineTests(unittest.TestCase):
    def test_picks_newest_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod_dir = Path(tmp) / "results" / "m"
            mod_dir.mkdir(parents=True)
            for stamp in ("20240101000000", "20250101000000", "20230101000000"):
                (mod_dir / f"m.a.case1.{stamp}.json").write_text("{}", encoding="utf-8")
            (mod_dir / "m.a.case2.20990101000000.json").write_text("{}", encoding="utf-8")
            old_results = rtc.RESULTS_DIR
            rtc.RESULTS_DIR = Path(tmp) / "results"
            try:
                chosen = rtc.latest_baseline("m", "a", "case1")
            finally:
                rtc.RESULTS_DIR = old_results
            self.assertEqual(chosen.name, "m.a.case1.20250101000000.json")

    def test_none_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_results = rtc.RESULTS_DIR
            rtc.RESULTS_DIR = Path(tmp)
            try:
                self.assertIsNone(rtc.latest_baseline("m", "a", "c"))
            finally:
                rtc.RESULTS_DIR = old_results


class BaselineJsonRoundTripTests(unittest.TestCase):
    def test_fresh_python_values_match_their_json_serialized_form(self):
        from datetime import datetime, timezone
        ts = int(datetime(2024, 5, 1, tzinfo=timezone.utc).timestamp())
        fresh = [[ts, b"bytes-value"]]
        recorded = json.loads(json.dumps({"data": fresh}, default=str))["data"]
        self.assertEqual(rtc.normalize_rows(fresh), rtc.normalize_rows(recorded))


if __name__ == "__main__":
    unittest.main()
