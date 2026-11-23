"""Prove the staged-file-time check still detects what it exists to detect.

check_staged_file_times.py reads the source under scripts/ and fails on a read of a file's stat
times. A checker that stops matching passes everything, so each spelling it must catch is pinned
here, along with the code that must stay silent and how an ALLOWED entry can go stale.
"""
import importlib.util
import os
import pathlib
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('check_staged_file_times',
                                              REPO_ROOT / 'admin' / 'scripts' / 'check_staged_file_times.py')
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class EverySpelling(unittest.TestCase):
    def test_each_form_of_a_stat_time_read_is_caught(self):
        for source in ('import os\nvalue = os.path.getmtime(p)\n',
                       'import os\nvalue = os.path.getctime(p)\n',
                       'import os\nvalue = os.path.getatime(p)\n',
                       'from os.path import getmtime\n',
                       'value = getmtime(p)\n',
                       'read = os.path.getmtime\n',
                       'value = Path(p).stat().st_mtime\n',
                       'value = os.stat(p).st_mtime_ns\n',
                       'value = result.st_ctime\n',
                       'value = result.st_atime_ns\n',
                       'value = result.st_birthtime\n',
                       'value = os.stat(p)[8]\n',
                       'value = os.lstat(p)[7]\n',
                       'value = result[stat.ST_MTIME]\n',
                       "value = getattr(result, 'st_mtime')\n",
                       'value = os.fstat(fd)[8]\n',
                       'value = os.stat(p)[-2]\n',
                       'value = os.stat(p)[7:]\n',
                       'value = os.stat(p)[:9]\n',
                       'value = os.stat(p)[::-1]\n',
                       'value = os.stat(p)[:7:-1]\n',
                       'result: os.stat_result = os.stat(p)\nvalue = result[8]\n',
                       'read: object = os.stat\nvalue = read(p)[8]\n',
                       'value = os.stat(p)[-4:]\n',
                       'value = os.stat(p)[start:]\n',
                       'result = os.stat(p)\nvalue = result[8]\n',
                       'result = os.lstat(p)\nvalue = result[index]\n',
                       'from os import stat as read\nvalue = read(p)[8]\n',
                       'read = os.stat\nvalue = read(p)[8]\n',
                       'a, b, c, d, e, f, g, h, i, j = os.stat(p)\n',
                       'first, *rest = os.stat(p)\n',
                       'value = tuple(os.stat(p))\n',
                       'def f(p):\n    if (saved := os.stat(p)):\n        return saved[8]\n',
                       'def f(p):\n    saved = os.stat(p)\n    def g():\n        return saved[8]\n    return g\n'):
            with self.subTest(source=source):
                self.assertTrue(check.reads_in(source), source)

    def test_recorded_times_and_other_stat_fields_stay_silent(self):
        for source in ('value = info.modification_date\n',
                       'value = info.times.modified\n',
                       'value = info.times.modified_no_zone\n',
                       'value = os.stat(p).st_size\n',
                       'value = os.stat(p)[6]\n',
                       "notes = 'not read from os.path.getmtime or st_mtime'\n",
                       "value = getattr(result, 'st_size')\n",
                       'result = os.stat(p)\nvalue = result[6]\n',
                       'value = os.stat(p)[:7]\n',
                       'items = other(p)\nvalue = items[8]\n',
                       'mode, ino = other(p)\n',
                       'value = os.stat(p)[:-3]\n',
                       'value = os.stat(p)[6::-1]\n',
                       'def f(p):\n    saved = os.stat(p)\n    def g(saved):\n        return saved[8]\n'
                       '    return saved.st_size, g\n',
                       'def f(p):\n    saved = os.stat(p)\n    def g():\n        saved = rows()\n        return saved[8]\n'
                       '    return saved.st_size, g\n',
                       'def f(p):\n    read = os.stat\n    return read(p).st_size\n\ndef g(read):\n    return read(p)[8]\n',
                       'saved = os.stat(p)\nfield = lambda saved: saved[8]\n',
                       'def a(p):\n    result = os.stat(p)\n    return result.st_size\n\n'
                       'def b(x):\n    result = x\n    return result[8]\n'):
            with self.subTest(source=source):
                self.assertEqual(check.reads_in(source), [], source)

    def test_the_enclosing_function_is_named(self):
        found = check.reads_in('def outer():\n    def inner():\n        return os.path.getmtime(p)\n')
        self.assertEqual([(what, where) for _line, what, where in found], [('getmtime', 'outer.inner')])


class Scan(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = folder.name
        self.write('scripts/version_info.py', "leapp_name = 'VLEAPP'\n")

    def write(self, relative, source):
        path = os.path.join(self.root, *relative.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(source)

    def test_a_read_outside_allowed_fails(self):
        self.write('scripts/artifacts/a.py', 'def key(p):\n    return os.path.getmtime(p)\n')
        count, problems = check.scan(self.root, allowed={})
        self.assertEqual(count, 2)
        self.assertEqual(len(problems), 1)
        self.assertIn('scripts/artifacts/a.py:2', problems[0])

    def test_an_allowed_read_passes(self):
        self.write('scripts/artifacts/a.py', 'def key(p):\n    return os.path.getmtime(p)\n')
        allowed = {'scripts/artifacts/a.py': {'key': (1, 'cache key')}}
        self.assertEqual(check.scan(self.root, allowed=allowed)[1], [])

    def test_a_new_read_in_an_allowed_function_fails(self):
        self.write('scripts/artifacts/a.py',
                   'def key(p):\n    first = os.path.getmtime(p)\n    return first, os.stat(p).st_mtime\n')
        allowed = {'scripts/artifacts/a.py': {'key': (1, 'cache key')}}
        self.assertTrue(check.scan(self.root, allowed=allowed)[1])

    def test_an_entry_that_no_longer_matches_fails(self):
        self.write('scripts/artifacts/a.py', 'def key(p):\n    return p\n')
        allowed = {'scripts/artifacts/a.py': {'key': (1, 'cache key')}}
        problems = check.scan(self.root, allowed=allowed)[1]
        self.assertEqual(len(problems), 1)
        self.assertIn('ALLOWED', problems[0])

    def test_the_seekers_and_vendored_code_are_not_read(self):
        for relative in ('scripts/search_files.py', 'scripts/raw_image.py', 'scripts/vendor/reader.py'):
            self.write(relative, 'value = os.path.getmtime(p)\n')
        self.assertEqual(check.scan(self.root, allowed={})[1], [])

    def test_a_file_that_cannot_be_parsed_is_reported(self):
        self.write('scripts/artifacts/broken.py', 'def (:\n')
        problems = check.scan(self.root, allowed={})[1]
        self.assertEqual(len(problems), 1)
        self.assertIn('could not be parsed', problems[0])

    def test_an_unknown_core_stops_the_check(self):
        self.write('scripts/version_info.py', "leapp_name = 'other'\n")
        with self.assertRaises(SystemExit):
            check.scan(self.root)


class ThisRepository(unittest.TestCase):
    def test_no_staged_file_time_reaches_a_report(self):
        self.assertEqual(check.scan(str(REPO_ROOT))[1], [])


if __name__ == '__main__':
    unittest.main()
