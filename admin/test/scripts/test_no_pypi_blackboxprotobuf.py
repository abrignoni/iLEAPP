"""Guard against reintroducing the PyPI blackboxprotobuf package.

iLEAPP vendors blackboxprotobuf at scripts/blackboxprotobuf because the PyPI
release pins protobuf==3.10.0, which force-downgrades the protobuf runtime
below the security pin in requirements.txt (see that file's comments).

A top-level `import blackboxprotobuf` slips in easily: contributions branched
before the vendoring, or new artifacts copied from old examples. It fails soft
at load time (the artifact is skipped with a loader warning), so review can
miss it. This test fails CI instead. The correct import is:

    from scripts import blackboxprotobuf
"""
import pathlib
import re
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VENDORED_DIR = REPO_ROOT / 'scripts' / 'blackboxprotobuf'
STALE_IMPORT = re.compile(r'^\s*(import blackboxprotobuf|from blackboxprotobuf\b)')


class TestNoPypiBlackboxprotobuf(unittest.TestCase):
    def test_no_stale_blackboxprotobuf_imports(self):
        offenders = []
        for py_file in (REPO_ROOT / 'scripts').rglob('*.py'):
            if VENDORED_DIR in py_file.parents:
                continue
            for line_number, line in enumerate(
                    py_file.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
                if STALE_IMPORT.match(line):
                    offenders.append(f'{py_file.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}')
        self.assertEqual(
            offenders, [],
            'PyPI-style blackboxprotobuf import found; use "from scripts import '
            'blackboxprotobuf" instead (see requirements.txt):\n' + '\n'.join(offenders))


if __name__ == '__main__':
    unittest.main()
