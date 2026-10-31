"""No two artifact categories differ only by letter case or surrounding spaces.

A category is a key in the LAVA manifest and the name of a report section, compared as an
exact string. 'Wifi Connections' beside 'WiFi Connections', and 'Cloudkit' beside
'CloudKit', made two categories of what was meant as one. This test reads every module's
artifact block and fails when two spellings fold to the same name.
"""
import ast
import collections
import pathlib
import unittest

ARTIFACTS = pathlib.Path(__file__).resolve().parents[3] / 'scripts' / 'artifacts'


def declared_categories():
    for path in sorted(ARTIFACTS.glob('*.py')):
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == '__artifacts_v2__'):
                try:
                    block = ast.literal_eval(node.value)
                except ValueError:
                    continue
                for info in block.values():
                    if isinstance(info, dict) and isinstance(info.get('category'), str):
                        yield info['category']


class CategorySpellingTest(unittest.TestCase):

    def test_no_two_categories_differ_only_by_case_or_spaces(self):
        spellings = collections.defaultdict(set)
        for category in declared_categories():
            spellings[category.strip().casefold()].add(category)

        self.assertGreater(len(spellings), 100)
        self.assertEqual(sorted(sorted(s) for s in spellings.values() if len(s) > 1), [])


if __name__ == '__main__':
    unittest.main()
