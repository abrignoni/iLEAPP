"""Prove the claim checker reads notes, reads them with the right vocabulary, and
that the vocabulary is the same one every core enforces.

Extending the check to `notes` is only worth having if three things hold at once, and
each fails silently on its own:

* notes are actually matched, or the field is nominally covered and never read;
* the completeness words do not apply to notes, or the check fires on every artifact
  that states what it was tested against, which is the wording this project asks for;
* a denial is not treated as a claim, or the same wording is taxed and the allowlist
  grows every time somebody writes a limitation down correctly.

The vocabulary is pinned to a literal here. The five cores each carry their own copy of
the checker, and they had already drifted: four spelled the habit stem open, so
"habitat" matched, and only one had it closed. A checker that quietly enforces a
different standard per repo is worse than a strict one, and nothing else compares them.
This file is identical in all five, so a change made in one repo alone fails that
repo's own CI.

The expected values are spelled out rather than derived from the patterns under test.
A fixture built from the constant it verifies moves with the bug.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_claim_language.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_claim_language', _MODULE_PATH)
ccl = importlib.util.module_from_spec(_spec)
sys.modules['check_claim_language'] = ccl
_spec.loader.exec_module(ccl)

# The vocabulary every core is expected to enforce, written out rather than imported.
EXPECTED_CLAIM = (
    r'\ball\b|\bevery\b|\bcomplete|\bfull list\b|\bentire\b|'
    r'\bthe user (?:searched|typed|viewed|visited|opened|selected|deleted|'
    r'read|sent|created|hid|chose)\b|\buser[- ](?:created|entered|typed|'
    r'searched|selected|initiated)\b|\bsearched by\b|\btyped by\b|'
    r'\bviewed by\b|\bread by\b|\bmanually\b|\bproves?\b|\bdefinitively\b|'
    r'\balways\b|\breliable|\bvisited\b|\bhabits?\b'
)
EXPECTED_NOTES = (
    r'\bthe user (?:searched|typed|viewed|visited|opened|selected|deleted|'
    r'read|sent|created|hid|chose)\b|\buser[- ](?:created|entered|typed|'
    r'searched|selected|initiated)\b|\bsearched by\b|\btyped by\b|'
    r'\bviewed by\b|\bmanually\b|\bproves?\b|\bdefinitively\b|\balways\b|'
    r'\breliable|\bvisited\b|\bhabits?\b'
)
EXPECTED_NEGATION = (
    r'\b(not|no|never|nor|neither|without|cannot|rather than|instead of|'
    r"isn't|doesn't|don't|does not|do not)\b"
)
EXPECTED_FIELDS = ('description', 'name', 'notes')


def fires(field, text):
    """True when the vocabulary for `field` reports a match in `text`, negation applied."""
    pattern = ccl.CHECKED_FIELDS[field]
    hits = list(pattern.finditer(text))
    if field == 'notes':
        hits = [hit for hit in hits if not ccl.negated(text, hit.start())]
    return bool(hits)


class VocabularyParity(unittest.TestCase):
    """The five cores must enforce one standard. Drift in any of them fails here."""

    def test_claim_vocabulary_is_the_shared_one(self):
        self.assertEqual(ccl.CLAIM_PATTERN.pattern, EXPECTED_CLAIM)

    def test_notes_vocabulary_is_the_shared_one(self):
        self.assertEqual(ccl.NOTES_PATTERN.pattern, EXPECTED_NOTES)

    def test_negation_vocabulary_is_the_shared_one(self):
        self.assertEqual(ccl.NEGATION_PATTERN.pattern, EXPECTED_NEGATION)
        self.assertEqual(ccl.NEGATION_WINDOW, 60)

    def test_the_same_three_fields_are_checked(self):
        self.assertEqual(tuple(sorted(ccl.CHECKED_FIELDS)), EXPECTED_FIELDS)

    def test_the_habit_stem_is_closed(self):
        # The open stem also matches "habitat". Four cores carried that until 2026-08-29.
        self.assertFalse(ccl.CLAIM_PATTERN.search('habitat'))
        self.assertFalse(ccl.NOTES_PATTERN.search('habitat'))
        self.assertTrue(ccl.CLAIM_PATTERN.search('habits'))


class FieldCoverage(unittest.TestCase):
    def test_notes_is_checked(self):
        self.assertIn('notes', ccl.CHECKED_FIELDS)

    def test_name_and_description_keep_the_full_vocabulary(self):
        self.assertIs(ccl.CHECKED_FIELDS['name'], ccl.CLAIM_PATTERN)
        self.assertIs(ccl.CHECKED_FIELDS['description'], ccl.CLAIM_PATTERN)

    def test_notes_uses_its_own_vocabulary(self):
        self.assertIs(ccl.CHECKED_FIELDS['notes'], ccl.NOTES_PATTERN)


class NotesVocabulary(unittest.TestCase):
    # Attribution and certainty mean the same thing in a note as in a description.
    CLAIMS = (
        'the term the user typed into the search box',
        'a page the user visited',
        'a term the user entered',
        'this proves the account holder sent it',
        'the column is always populated',
        'a reliable record of the conversation',
    )
    # Notes state what was tested. These must stay silent or the check punishes the
    # coverage discipline it exists alongside.
    COVERAGE = (
        'empty on all 18 copies tested',
        'NULL for every account tested',
        'the complete table list is given above',
        'present on the entire corpus',
        'columns are read by position over a select star',
        'the sidecar is not read by this artifact',
    )

    def test_claims_fire(self):
        for text in self.CLAIMS:
            with self.subTest(text=text):
                self.assertTrue(fires('notes', text))

    def test_coverage_wording_stays_silent(self):
        for text in self.COVERAGE:
            with self.subTest(text=text):
                self.assertFalse(fires('notes', text))

    def test_notes_drops_exactly_the_two_documented_classes(self):
        """The two vocabularies differ only where the module says they do."""
        removed = ('all', 'every', 'complete', 'entire', 'full list', 'read by')
        for word in removed:
            with self.subTest(word=word, vocabulary='description'):
                self.assertTrue(ccl.CLAIM_PATTERN.search(word))
            with self.subTest(word=word, vocabulary='notes'):
                self.assertFalse(ccl.NOTES_PATTERN.search(word))
        kept = ('the user typed', 'typed by', 'manually', 'proves', 'always',
                'reliable', 'visited', 'habits', 'user-created')
        for word in kept:
            with self.subTest(word=word):
                self.assertTrue(ccl.CLAIM_PATTERN.search(word))
                self.assertTrue(ccl.NOTES_PATTERN.search(word))

    def test_description_still_flags_completeness(self):
        # The narrowing applies to notes only. Regression guard on the original behaviour.
        self.assertTrue(fires('description', 'every message in the conversation'))
        self.assertTrue(fires('description', 'all sites the user visited'))


class Negation(unittest.TestCase):
    def test_denial_in_the_same_clause_is_not_a_claim(self):
        for text in (
            'this store holds suggestions the app downloaded, not terms the user searched for',
            'their presence does not establish that the user viewed them',
            'they evidence the app running rather than anything the user chose',
            'the app stores no user created images',
        ):
            with self.subTest(text=text):
                self.assertFalse(fires('notes', text))

    def test_a_negation_in_the_previous_sentence_does_not_carry(self):
        # "not" governs its own clause. A full stop ends it, so the claim after it stands.
        text = 'The table is not a cache. It records the term the user typed.'
        self.assertTrue(fires('notes', text))

    def test_a_distant_negation_does_not_carry(self):
        # Sixty characters is the window; padding past it must leave the claim visible.
        text = 'not' + ' x' * 45 + ' the term the user typed'
        self.assertTrue(fires('notes', text))


class AllowlistIsTermScoped(unittest.TestCase):
    """An exception silences the word it was granted for, not the whole field.

    Keyed on (file, artifact_key, field) an entry pre-approves every future claim
    anyone adds to that text. The term is part of the key so that it does not.
    """

    def test_every_entry_is_a_four_tuple_of_strings(self):
        for entry in ccl.ALLOWLIST:
            with self.subTest(entry=entry):
                self.assertEqual(len(entry), 4)
                self.assertTrue(all(isinstance(part, str) for part in entry))

    def test_every_entry_names_a_term_the_vocabulary_can_produce(self):
        # A term no pattern can emit is dead on arrival: it silences nothing and the
        # stale check cannot tell it apart from an entry whose text was reworded.
        for filename, artifact_key, field, term in ccl.ALLOWLIST:
            with self.subTest(entry=(filename, artifact_key, field, term)):
                self.assertEqual(term, term.lower())
                match = ccl.CHECKED_FIELDS[field].search(term)
                self.assertIsNotNone(match, f'{term!r} is not in the {field} vocabulary')
                self.assertEqual(match.group(0).lower(), term)

    def test_an_entry_covers_its_own_term_only(self):
        # A key no repo can hold, so this behaves the same in all five.
        probe = ('no_such_module.py', 'no_such_artifact', 'notes')
        self.assertEqual(
            ccl.unallowlisted(*probe, ['always', 'the user typed']),
            ['always', 'the user typed'])

    def test_unallowlisted_returns_only_what_is_uncovered(self):
        for filename, artifact_key, field, term in sorted(ccl.ALLOWLIST):
            covered = ccl.unallowlisted(filename, artifact_key, field, [term])
            self.assertEqual(covered, [], f'{term!r} should be covered by its own entry')
            # A different term on the same field must still be reported.
            other = 'proves' if term != 'proves' else 'always'
            self.assertEqual(
                ccl.unallowlisted(filename, artifact_key, field, [term, other]), [other])
            break   # one entry is enough; repos with an empty allowlist skip the loop


if __name__ == '__main__':
    unittest.main()
