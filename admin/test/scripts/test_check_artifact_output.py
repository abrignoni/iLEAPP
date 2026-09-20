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



class SilencedOnTheFindingNotTheColumn(unittest.TestCase):
    """The notes silence a finding only by addressing that finding.

    Before this, any mention of the column anywhere in the notes silenced every
    finding about it, and the match was a bare substring. A real case: a module
    whose notes explained that ps_thread.txt carries %CPU in its 4th column had
    its own uniform %CPU column silenced by that sentence, and its uniform TIME
    column silenced by the words "timezone" and "timestamp".
    """

    CONSTANT = [{'A': str(i), '%CPU': '0.0', 'TIME': '0:00.00'} for i in range(5)]
    COLUMNS = ['A', '%CPU', 'TIME']

    def test_a_mention_for_another_reason_does_not_silence(self):
        notes = ('ps_thread.txt is not read: its 4th column is %CPU, where the 4th of '
                 'ps.txt holds the process identifier.')
        findings = coa.check_table(self.COLUMNS, self.CONSTANT, notes=notes)
        reported = [m for k, m in findings if k == 'constant-column']
        self.assertTrue(any("'%CPU'" in m for m in reported))

    def test_a_longer_word_containing_the_name_does_not_silence(self):
        notes = "STARTED carries no date or timezone and is not a usable timestamp."
        findings = coa.check_table(self.COLUMNS, self.CONSTANT, notes=notes)
        reported = [m for k, m in findings if k == 'constant-column']
        self.assertTrue(any("'TIME'" in m for m in reported))

    def test_saying_the_column_is_uniform_does_silence(self):
        notes = "%CPU and TIME each held a single value on all 5 rows."
        findings = coa.check_table(self.COLUMNS, self.CONSTANT, notes=notes)
        self.assertNotIn('constant-column', _kinds(findings))

    def test_a_plural_still_names_the_column(self):
        rows = [{'A': 'x', 'Timestamp': ''} for _ in range(3)]
        findings = coa.check_table(['A', 'Timestamp'], rows,
                                   notes='The timestamps were blank on every row.')
        self.assertNotIn('empty-column', _kinds(findings))

    def test_a_colon_list_is_one_statement(self):
        rows = [{'A': 'x', 'B': ''} for _ in range(3)]
        findings = coa.check_table(['A', 'B'], rows, notes='These are blank: A, B and C.')
        self.assertNotIn('empty-column', _kinds(findings))

    def test_documenting_emptiness_does_not_silence_uniformity(self):
        """Each kind has its own vocabulary, so the wrong one leaves the finding."""
        rows = [{'A': 'x', 'B': 'same'} for _ in range(4)]
        findings = coa.check_table(['A', 'B'], rows, notes='B is blank on rows with no record.')
        self.assertIn('constant-column', _kinds(findings))

    def test_identical_columns_need_both_named_in_one_sentence(self):
        rows = [{'A': str(i), 'B': str(i)} for i in range(4)]
        loose = coa.check_table(['A', 'B'], rows,
                                notes='A is the path. Separately, B is the name.')
        self.assertIn('identical-columns', _kinds(loose))
        stated = coa.check_table(['A', 'B'], rows,
                                 notes='A and B are identical because the store repeats it.')
        self.assertNotIn('identical-columns', _kinds(stated))

    def test_a_bare_mention_is_reported_with_a_hint(self):
        notes = 'The %CPU column is read from the 7th field.'
        findings = coa.check_table(self.COLUMNS, self.CONSTANT, notes=notes)
        hinted = [m for k, m in findings if "'%CPU'" in m]
        self.assertTrue(hinted and 'not as this finding' in hinted[0])


if __name__ == '__main__':
    unittest.main()
