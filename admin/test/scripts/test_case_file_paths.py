"""Structural check: committed case files carry no machine-local paths.

The image manifest split (iLEAPP #2028) keeps machine-independent identity in
committed files and machine-specific locations in the git-ignored
admin/image_manifest.local.json. A case entry's make_data.input_data_path is
display text for the case pickers, which take its basename; recording an
absolute path there publishes one machine's corpus layout into the repo. This
guards the make_test_data.py writer and the committed case files together.
"""
import glob
import json
import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CASES_GLOB = os.path.join(REPO_ROOT, 'admin', 'test', 'cases', 'testdata.*.json')


class CaseFilePathTests(unittest.TestCase):
    def test_input_data_path_is_a_bare_file_name(self):
        offenders = []
        for path in sorted(glob.glob(CASES_GLOB)):
            with open(path, encoding='utf-8') as f:
                cases = json.load(f)
            for case_key, case in cases.items():
                value = case.get('make_data', {}).get('input_data_path', '')
                if '/' in value or '\\' in value:
                    offenders.append(f"{os.path.basename(path)} [{case_key}]: {value}")
        self.assertEqual(offenders, [],
                         "case files must record only the image file name in "
                         "make_data.input_data_path:\n" + "\n".join(offenders))


if __name__ == '__main__':
    unittest.main()
