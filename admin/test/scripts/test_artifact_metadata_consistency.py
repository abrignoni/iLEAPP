"""Two artifact block fields that go wrong without any error.

- last_update_date earlier than creation_date. Threema's two artifacts carried 2022-01-03
  as the update of a module created on 2026-01-03.
- An html_columns entry that names no header. The HTML writer leaves unescaped only the
  columns whose header is listed, so after a header is renamed its formatting is escaped
  and shown as tags. BeReal listed 'Thumbnail URL' and 'RealMojis', neither of them a
  header of the artifact. The check covers artifacts whose data_headers are literal.
"""
import ast
import datetime
import pathlib
import unittest

ARTIFACTS = pathlib.Path(__file__).resolve().parents[3] / 'scripts' / 'artifacts'


def modules():
    for path in sorted(ARTIFACTS.glob('*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        block = None
        for node in tree.body:
            if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == '__artifacts_v2__'):
                try:
                    block = ast.literal_eval(node.value)
                except ValueError:
                    block = None
        if isinstance(block, dict):
            yield path.name, tree, block


def literal_headers(tree, function_name):
    """Every header any literal data_headers assignment in the function declares."""
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == function_name]
    headers = set()
    for function in functions:
        for node in ast.walk(function):
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == 'data_headers' for t in node.targets):
                try:
                    value = ast.literal_eval(node.value)
                except ValueError:
                    continue
                headers.update(h if isinstance(h, str) else h[0] for h in value)
    return headers


class ArtifactMetadataConsistencyTest(unittest.TestCase):

    def test_no_artifact_was_updated_before_it_was_created(self):
        backwards = []
        for name, _, block in modules():
            for artifact, info in block.items():
                try:
                    created = datetime.date.fromisoformat(info['creation_date'])
                    updated = datetime.date.fromisoformat(info['last_update_date'])
                except (KeyError, TypeError, ValueError):
                    continue
                if updated < created:
                    backwards.append((name, artifact, str(created), str(updated)))
        self.assertEqual(backwards, [])

    def test_every_html_column_names_a_header(self):
        checked = 0
        unknown = []
        for name, tree, block in modules():
            for artifact, info in block.items():
                columns = info.get('html_columns') if isinstance(info, dict) else None
                if not columns:
                    continue
                headers = literal_headers(tree, artifact)
                if not headers:
                    continue
                checked += 1
                unknown += [(name, artifact, column) for column in columns if column not in headers]
        self.assertGreater(checked, 50)
        self.assertEqual(unknown, [])


if __name__ == '__main__':
    unittest.main()
