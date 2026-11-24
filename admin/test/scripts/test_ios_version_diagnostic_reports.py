"""The iOS version fallback read from .ips diagnostic reports."""
# pylint: disable=protected-access
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import iosVersionDiagnosticReports as module
from scripts.ilapfuncs import iOS


class Context:
    files = []
    installed = None

    @classmethod
    def get_files_found(cls):
        return cls.files

    @staticmethod
    def get_relative_path(path):
        return Path(path).name

    @classmethod
    def set_installed_os_version(cls, value):
        cls.installed = value


def ips(folder, name, meta, body=''):
    path = Path(folder) / name
    path.write_text(json.dumps(meta) + '\n' + body, encoding='utf-8')
    return str(path)


def run(files, start=None):
    Context.files = files
    Context.installed = None
    with patch.object(iOS, '_version', start), patch.object(module, 'device_info'), \
            patch.object(module, 'logfunc') as log:
        headers, rows, source = module.ios_version_diagnostic_reports.__wrapped__(Context)
        version = iOS.get_version()
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], source, version, [c.args[0] for c in log.call_args_list]


class TestIosVersionDiagnosticReports(unittest.TestCase):
    def test_newest_report_decides_and_both_versions_are_listed(self):
        with tempfile.TemporaryDirectory() as folder:
            old = ips(folder, 'a.ips', {'bug_type': '313', 'timestamp': '2026-01-02 10:00:00.00 -0500',
                                        'os_version': 'iPhone OS 26.2 (23C55)'})
            new = ips(folder, 'b.ips', {'bug_type': '221', 'timestamp': '2026-03-02 10:00:00.00 -0500',
                                        'os_version': 'iPhone OS 26.2.1 (23C71)'})
            also_old = ips(folder, 'c.ips', {'bug_type': '313', 'timestamp': '2026-01-03 10:00:00.00 -0500',
                                             'os_version': 'iPhone OS 26.2 (23C55)'})
            bad = ips(folder, 'd.ips', {'bug_type': '313', 'os_version': 'garbled'})
            rows, source, version, log = run([old, new, also_old, bad])
        self.assertEqual(version, '26.2.1')
        self.assertEqual(Context.installed, '26.2.1')
        self.assertEqual([(r['iOS Version'], r['Build'], r['Report Count'], r['Used']) for r in rows],
                         [('26.2.1', '23C71', 1, 'Yes'), ('26.2', '23C55', 2, 'No')])
        self.assertEqual(source.split('\n'), [new, also_old])
        self.assertTrue(any('1 diagnostic report(s) gave no readable' in line for line in log))
        self.assertTrue(any('name 2 iOS version and build pairs' in line for line in log))
        self.assertTrue(any('b.ips' in line and 'os_version (metadata)' in line for line in log))

    def test_crash_report_body_version_is_used_for_bug_type_309(self):
        with tempfile.TemporaryDirectory() as folder:
            crash = ips(folder, 'App-2026.ips', {'bug_type': '309', 'timestamp': '2026-03-02 10:00:00.00 +0000',
                                                 'os_version': 'iPhone OS 26.2 (23C55)'},
                        json.dumps({'osVersion': {'train': 'iPhone OS 26.2', 'build': '23C55'}}))
            rows, _, version, _ = run([crash])
        self.assertEqual(version, '26.2')
        self.assertEqual(rows[0]['Field'], 'osVersion (body)')
        self.assertEqual(rows[0]['Build'], '23C55')

    def test_no_readable_report_leaves_the_version_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = ips(folder, 'x.ips', {'bug_type': '313'})
            rows, source, version, _ = run([bad])
        self.assertEqual((rows, source, version), ([], '', None))

    def test_an_empty_version_read_earlier_is_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            report = ips(folder, 'a.ips', {'bug_type': '313', 'timestamp': '2026-01-02 10:00:00.00 -0500',
                                           'os_version': 'iPhone OS 26.2.1 (23C71)'})
            _, _, version, _ = run([report], start='')
        self.assertEqual(version, '26.2.1')

    def test_an_earlier_version_is_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            report = ips(folder, 'a.ips', {'bug_type': '313', 'timestamp': '2026-01-02 10:00:00.00 -0500',
                                           'os_version': 'iPhone OS 26.2.1 (23C71)'})
            _, _, version, _ = run([report], start='18.3.2')
        self.assertEqual(version, '18.3.2')

    def test_without_timestamps_the_most_reports_decide_and_the_log_says_so(self):
        with tempfile.TemporaryDirectory() as folder:
            files = [ips(folder, f'{n}.ips', {'bug_type': '313', 'os_version': text})
                     for n, text in enumerate(['iPhone OS 26.2 (23C55)', 'iPhone OS 26.2 (23C55)',
                                               'iPhone OS 26.2.1 (23C71)'])]
            rows, _, version, log = run(files)
        self.assertEqual(version, '26.2')
        self.assertEqual([r['Used'] for r in rows], ['Yes', 'No'])
        self.assertTrue(any('the pair with the most reports decides' in line for line in log))
        self.assertFalse(any('The newest report decides' in line for line in log))
        self.assertTrue(any('no readable timestamp' in line for line in log))

    def test_parse(self):
        self.assertEqual(module._parse('iPhone OS 26.2.1 (23C71)'), ('26.2.1', '23C71'))
        self.assertEqual(module._parse('iPhone OS 18.3.2'), ('18.3.2', ''))
        self.assertIsNone(module._parse('iPhone OS'))


if __name__ == '__main__':
    unittest.main()
