"""Cloud Configuration Details on a synthetic plist (values invented for the test)."""
import hashlib
import json
import pathlib
import plistlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import cloudConfigurationDetails as parser  # noqa: E402

BASE = 'private/var/containers/Shared/SystemGroup/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles'
CERT = b'\x30\x82\x01\x00' + b'\x01' * 20


class CloudConfigurationDetailsTest(unittest.TestCase):
    def test_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory) / BASE
            base.mkdir(parents=True)
            main = base / 'CloudConfigurationDetails.plist'
            main.write_bytes(plistlib.dumps({'IsSupervised': False, 'ConfigurationSource': 0,
                                             'SupervisorHostCertificates': [CERT, CERT + b'\x02'],
                                             'Nested': {'b': 1, 'a': b'xy'}}))
            aside = base / 'CloudConfigurationSetAsideDetails.plist'
            aside.write_bytes(plistlib.dumps({'ConfigurationWasApplied': False}))
            broken = base / 'other' / 'CloudConfigurationDetails.plist'
            broken.parent.mkdir()
            broken.write_bytes(b'not a plist')
            paths = [str(main), str(aside), str(broken)]
            headers, rows, source = parser.cloud_configuration_details.__wrapped__(
                SimpleNamespace(get_files_found=lambda: paths))
        self.assertEqual(headers, ('File', 'Key', 'Value'))
        values = {(r[0], r[1]): r[2] for r in rows}
        self.assertEqual(values[('CloudConfigurationDetails.plist', 'IsSupervised')], 'False')
        self.assertEqual(values[('CloudConfigurationDetails.plist', 'ConfigurationSource')], '0')
        self.assertEqual(values[('CloudConfigurationDetails.plist', 'SupervisorHostCertificates [0]')],
                         f'bytes starting 30 82, {len(CERT)} bytes, SHA-256 {hashlib.sha256(CERT).hexdigest()}')
        self.assertIn(('CloudConfigurationDetails.plist', 'SupervisorHostCertificates [1]'), values)
        nested = json.loads(values[('CloudConfigurationDetails.plist', 'Nested')])
        self.assertEqual(nested['b'], 1)
        self.assertTrue(nested['a'].startswith('bytes, 2 bytes, SHA-256 '))
        self.assertEqual(values[('CloudConfigurationSetAsideDetails.plist', 'ConfigurationWasApplied')], 'False')
        self.assertEqual(len(rows), 6)
        self.assertEqual(len(source.splitlines()), 3)


if __name__ == '__main__':
    unittest.main()
