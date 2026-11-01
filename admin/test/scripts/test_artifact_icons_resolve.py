"""Every artifact that writes an HTML page names an icon the report can show.

report.generate_report takes an artifact's icon from the bundled Tabler CSS, or maps it
through feather_to_tabler_icon_names.json, and otherwise shows alert-triangle. A name it
cannot resolve gives no error; the artifact appears in the sidebar under a warning icon.
lgThinqDevices ('device-washing-machine') and myqDevices ('garage') did that until they
were given bundled names. An artifact with no artifact_icon at all gets the same warning
icon; get_biomeNotificationUsage had none. This test reads every module's block and fails
on either.
"""
import ast
import json
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.report import get_tabler_icon_names  # pylint: disable=wrong-import-position

ARTIFACTS = REPO_ROOT / 'scripts' / 'artifacts'
FEATHER_MAP = REPO_ROOT / 'scripts' / 'data' / 'feather_to_tabler_icon_names.json'


def declared_blocks():
    for path in sorted(ARTIFACTS.glob('*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in tree.body:
            if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == '__artifacts_v2__'):
                try:
                    block = ast.literal_eval(node.value)
                except ValueError:
                    continue
                for name, info in block.items():
                    if isinstance(info, dict):
                        yield path.name, name, info


def declared_icons():
    for module, name, info in declared_blocks():
        if info.get('artifact_icon'):
            yield module, name, info['artifact_icon']


def writes_html(output_types):
    values = [output_types] if isinstance(output_types, str) else list(output_types or [])
    return any(v in ('html', 'standard', 'all') for v in values)


class ArtifactIconsResolveTest(unittest.TestCase):

    def test_every_artifact_icon_resolves(self):
        known = get_tabler_icon_names() | set(json.loads(FEATHER_MAP.read_text(encoding='utf-8')))
        icons = list(declared_icons())

        self.assertGreater(len(icons), 1000)
        self.assertEqual([icon for icon in icons if icon[2] not in known], [])

    def test_every_artifact_with_an_html_page_declares_an_icon(self):
        missing = [(module, name) for module, name, info in declared_blocks()
                   if writes_html(info.get('output_types')) and not info.get('artifact_icon')]

        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()
