"""Prove the output checker still detects the defects it exists to detect.

check_artifact_output.py reads a generated report and reports the column-level
defects that source review cannot see. It is itself a script, so it can rot: in
the session that introduced it, two of its own checks were wrong before they were
right, and nothing but a run against known input caught them. This locks in the
behaviour so a later edit that breaks a check fails here instead of shipping a
checker that quietly passes everything.

The check functions are pure: check_table takes columns, rows and the notes text,
and check_scaling takes two {artifact: count} maps. So this needs no report on
disk and no evidence data, and it runs in the ordinary unittest job on every
platform.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_artifact_output.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_artifact_output', _MODULE_PATH)
coa = importlib.util.module_from_spec(_spec)
sys.modules['check_artifact_output'] = coa
_spec.loader.exec_module(coa)


def _kinds(findings):
    """The set of finding kinds a check_table result holds."""
    return {kind for kind, _ in findings}


class EmptyColumn(unittest.TestCase):
    def test_flags_a_column_that_is_empty_on_every_row(self):
        rows = [{'A': 'x', 'B': ''}, {'A': 'y', 'B': ''}, {'A': 'z', 'B': ''}]
        findings = coa.check_table(['A', 'B'], rows, notes='')
        self.assertIn('empty-column', _kinds(findings))

    def test_a_note_naming_the_column_silences_it(self):
        rows = [{'A': 'x', 'B': ''}, {'A': 'y', 'B': ''}, {'A': 'z', 'B': ''}]
        findings = coa.check_table(['A', 'B'], rows, notes='Column B was empty on every row.')
        self.assertNotIn('empty-column', _kinds(findings))

    def test_the_note_match_ignores_an_as_stored_qualifier(self):
        rows = [{'A': 'x', 'B (as stored)': ''} for _ in range(3)]
        findings = coa.check_table(['A', 'B (as stored)'], rows, notes='B was empty here.')
        self.assertNotIn('empty-column', _kinds(findings))


class ConstantColumn(unittest.TestCase):
    def test_flags_one_value_across_every_row(self):
        rows = [{'A': str(i), 'B': 'same'} for i in range(4)]
        findings = coa.check_table(['A', 'B'], rows, notes='')
        self.assertIn('constant-column', _kinds(findings))

    def test_does_not_flag_below_the_row_threshold(self):
        rows = [{'A': '1', 'B': 'same'}, {'A': '2', 'B': 'same'}]
        findings = coa.check_table(['A', 'B'], rows, notes='')
        self.assertNotIn('constant-column', _kinds(findings))


class IdenticalColumns(unittest.TestCase):
    def test_flags_two_columns_equal_on_every_varying_row(self):
        rows = [{'A': '1', 'B': '1'}, {'A': '2', 'B': '2'}, {'A': '3', 'B': '3'}]
        findings = coa.check_table(['A', 'B'], rows, notes='')
        self.assertIn('identical-columns', _kinds(findings))

    def test_a_note_naming_both_columns_silences_it(self):
        rows = [{'A': '1', 'B': '1'}, {'A': '2', 'B': '2'}, {'A': '3', 'B': '3'}]
        findings = coa.check_table(['A', 'B'], rows, notes='A and B are equal by design here.')
        self.assertNotIn('identical-columns', _kinds(findings))

    def test_two_empty_columns_are_not_identical(self):
        # Both empty is the empty-column case, not a no-op derivation.
        rows = [{'A': '', 'B': ''} for _ in range(3)]
        findings = coa.check_table(['A', 'B'], rows, notes='')
        self.assertNotIn('identical-columns', _kinds(findings))


class SparseLead(unittest.TestCase):
    def test_flags_a_timestamp_lead_that_is_mostly_blank(self):
        rows = [{'When': '2024-01-01 00:00:00', 'X': 'a'}] + [{'When': '', 'X': 'a'}
                                                              for _ in range(4)]
        findings = coa.check_table(['When', 'X'], rows, notes='')
        self.assertIn('sparse-lead', _kinds(findings))

    def test_a_full_timestamp_lead_is_fine(self):
        rows = [{'When': '2024-01-0%d 00:00:00' % (i + 1), 'X': 'a'} for i in range(4)]
        findings = coa.check_table(['When', 'X'], rows, notes='')
        self.assertNotIn('sparse-lead', _kinds(findings))


class IgnoredColumns(unittest.TestCase):
    def test_source_file_is_never_reported_even_when_constant(self):
        rows = [{'A': str(i), 'Source File': 'app/db'} for i in range(4)]
        findings = coa.check_table(['A', 'Source File'], rows, notes='')
        self.assertEqual(_kinds(findings), set())


class Scaling(unittest.TestCase):
    def test_exact_double_is_clean(self):
        self.assertEqual(coa.check_scaling({'a': 10}, {'a': 20}), [])

    def test_same_count_is_a_dropped_tenant(self):
        findings = coa.check_scaling({'a': 10}, {'a': 10})
        self.assertEqual([kind for _, kind, _ in findings], ['scaling-1x'])

    def test_triple_is_uncollapsed_views(self):
        findings = coa.check_scaling({'a': 10}, {'a': 30})
        self.assertEqual([kind for _, kind, _ in findings], ['scaling-3x'])

    def test_more_than_double_is_a_leak(self):
        findings = coa.check_scaling({'a': 10}, {'a': 25})
        self.assertEqual([kind for _, kind, _ in findings], ['scaling-high'])

    def test_a_zero_row_artifact_is_not_judged(self):
        self.assertEqual(coa.check_scaling({'a': 0}, {'a': 0}), [])


if __name__ == '__main__':
    unittest.main()
