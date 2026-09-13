"""Tests for the pure logic in admin/scripts/check_pr_test_data.py.

The GitHub API layer is not exercised here; these cover file classification,
sample_data extraction from source text, the decision matrix, and the comment
rendering, all against synthetic inputs.
"""
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')))

import check_pr_test_data as bot  # noqa: E402  pylint: disable=wrong-import-position


def _files(*pairs):
    return [{'filename': name, 'status': status} for name, status in pairs]


class ArtifactModulesTests(unittest.TestCase):
    def test_added_and_modified_artifacts_counted(self):
        files = _files(('scripts/artifacts/foo.py', 'added'),
                       ('scripts/artifacts/bar.py', 'modified'),
                       ('scripts/ilapfuncs.py', 'modified'),
                       ('README.md', 'modified'))
        self.assertEqual(bot.artifact_modules(files), {'foo': 'added', 'bar': 'modified'})

    def test_removed_artifacts_ignored(self):
        files = _files(('scripts/artifacts/gone.py', 'removed'))
        self.assertEqual(bot.artifact_modules(files), {})

    def test_non_python_and_nested_paths_ignored(self):
        files = _files(('scripts/artifacts/notes.md', 'added'),
                       ('scripts/artifacts/sub/x.py', 'added'))
        self.assertEqual(bot.artifact_modules(files), {})


class CoveredModulesTests(unittest.TestCase):
    def test_case_json_covers(self):
        files = _files(('admin/test/cases/testdata.foo.json', 'added'))
        self.assertEqual(bot.covered_modules(files, {'foo': 'added'}), {'foo'})

    def test_data_dir_covers(self):
        files = _files(('admin/test/cases/data/foo/testdata.foo.a.img.zip', 'added'))
        self.assertEqual(bot.covered_modules(files, {'foo': 'added'}), {'foo'})

    def test_other_modules_data_does_not_cover(self):
        files = _files(('admin/test/cases/data/bar/testdata.bar.a.img.zip', 'added'))
        self.assertEqual(bot.covered_modules(files, {'foo': 'added'}), set())

    def test_removed_data_does_not_cover(self):
        files = _files(('admin/test/cases/testdata.foo.json', 'removed'))
        self.assertEqual(bot.covered_modules(files, {'foo': 'modified'}), set())


class SampleDataKeysTests(unittest.TestCase):
    def test_keys_collected_across_artifacts(self):
        source = (
            '__artifacts_v2__ = {\n'
            '    "a": {"name": "A", "sample_data": {"hickman_ios15": "5 rows"}},\n'
            '    "b": {"name": "B", "sample_data": {"dexter_ios18": "1 row",\n'
            '                                        "hickman_ios15": "2 rows"}},\n'
            '}\n')
        self.assertEqual(bot.sample_data_keys_from_source(source),
                         {'hickman_ios15', 'dexter_ios18'})

    def test_no_sample_data_yields_empty(self):
        source = '__artifacts_v2__ = {"a": {"name": "A"}}\n'
        self.assertEqual(bot.sample_data_keys_from_source(source), set())

    def test_non_literal_metadata_yields_empty(self):
        source = 'V = "x"\n__artifacts_v2__ = {"a": {"name": V}}\n'
        self.assertEqual(bot.sample_data_keys_from_source(source), set())

    def test_syntax_error_yields_empty(self):
        self.assertEqual(bot.sample_data_keys_from_source('def broken(:\n'), set())


class ClassifyTests(unittest.TestCase):
    PUBLIC = {'hickman_ios15', 'dexter_ios18'}

    def test_covered_module_needs_nothing(self):
        fixture, ask = bot.classify({'foo': 'added'}, {'foo'}, {}, self.PUBLIC)
        self.assertEqual((fixture, ask), ({}, []))

    def test_public_key_routes_to_fixture(self):
        fixture, ask = bot.classify({'foo': 'added'}, set(),
                                    {'foo': {'hickman_ios15', 'private_img'}}, self.PUBLIC)
        self.assertEqual(fixture, {'foo': ['hickman_ios15']})
        self.assertEqual(ask, [])

    def test_no_public_key_routes_to_ask(self):
        fixture, ask = bot.classify({'foo': 'added'}, set(),
                                    {'foo': {'private_img'}}, self.PUBLIC)
        self.assertEqual((fixture, ask), ({}, ['foo']))

    def test_mixed_pr(self):
        fixture, ask = bot.classify(
            {'a': 'added', 'b': 'added', 'c': 'added'}, {'c'},
            {'a': {'dexter_ios18'}, 'b': set()}, self.PUBLIC)
        self.assertEqual(fixture, {'a': ['dexter_ios18']})
        self.assertEqual(ask, ['b'])


class RenderCommentTests(unittest.TestCase):
    REPO = 'abrignoni/iLEAPP'

    def test_ask_comment_has_marker_module_and_ladder(self):
        body = bot.render_comment(self.REPO, {}, ['foo'])
        self.assertIn(bot.MARKER, body)
        self.assertIn('`foo.py`', body)
        self.assertIn('Under 10 MB', body)
        self.assertIn('not a gate', body)
        self.assertIn('admin/test/cases/data/<module>/', body)

    def test_fixture_only_comment_asks_nothing(self):
        body = bot.render_comment(self.REPO, {'foo': ['hickman_ios15']}, [])
        self.assertIn('`hickman_ios15`', body)
        self.assertIn('Nothing is needed from you', body)
        self.assertNotIn('Size rules', body)

    def test_resolved_comment(self):
        body = bot.render_comment(self.REPO, {}, [])
        self.assertIn(bot.MARKER, body)
        self.assertIn('Thank you', body)

    def test_no_em_dashes_anywhere(self):
        for body in (bot.render_comment(self.REPO, {}, ['foo']),
                     bot.render_comment(self.REPO, {'a': ['k']}, []),
                     bot.render_comment(self.REPO, {}, [])):
            self.assertNotIn('—', body)


class ShouldSkipTests(unittest.TestCase):
    def test_write_and_admin_authors_skip(self):
        self.assertTrue(bot.should_skip('dev', 'write', set())[0])
        self.assertTrue(bot.should_skip('dev', 'admin', set())[0])

    def test_bot_authors_skip(self):
        self.assertTrue(bot.should_skip('dependabot[bot]', 'none', set())[0])

    def test_external_authors_do_not_skip(self):
        self.assertFalse(bot.should_skip('someone', 'read', set())[0])
        self.assertFalse(bot.should_skip('someone', 'none', set())[0])

    def test_bot_test_label_overrides_every_skip(self):
        self.assertFalse(bot.should_skip('dev', 'admin', {bot.TEST_LABEL})[0])
        self.assertFalse(bot.should_skip('dependabot[bot]', 'none', {bot.TEST_LABEL})[0])


class DesiredLabelsTests(unittest.TestCase):
    def test_matrix(self):
        self.assertEqual(bot.desired_labels({}, []), set())
        self.assertEqual(bot.desired_labels({'a': ['k']}, []), {bot.LABEL_FIXTURE})
        self.assertEqual(bot.desired_labels({}, ['b']), {bot.LABEL_ASK})
        self.assertEqual(bot.desired_labels({'a': ['k']}, ['b']),
                         {bot.LABEL_FIXTURE, bot.LABEL_ASK})


if __name__ == '__main__':
    unittest.main()
