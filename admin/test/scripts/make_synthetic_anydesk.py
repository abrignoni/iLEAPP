#!/usr/bin/env python3
"""Build the SYNTHETIC AnyDesk iOS fixtures used by testdata.anydesk.json (no data from any device).

Every file is made up: the IDs are 9-digit numbers starting 9000, the certificate and key lines say
SYNTHETIC-NOT-A-REAL-*, and the trace log carries invented process numbers. The layout follows the
folders the anydesk artifacts read, under private/var/mobile/Containers/Data/Application/<UUID>/.

Three fixtures, each written once per artifact named in the case file (the three zips of a fixture
hold the same members and contents):

  synthetic_anydesk_ios7         one container with every file the artifacts read, plus a decoy
                                 container whose files sit in a '.other' folder and must add nothing
  synthetic_anydesk_two_tenants  two AnyDesk containers (a reinstall) plus the decoy
  synthetic_anydesk_minimal      one container holding only anydesk.trace

    python make_synthetic_anydesk.py OUT_DIR

writes testdata.anydesk.<artifact>.<fixture>.zip into OUT_DIR (the repo keeps them in
admin/test/cases/data/anydesk/). Running it rebuilds the 9 fixture zips with the same members and contents;
member timestamps and permissions are fixed.
"""

import plistlib
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ARTIFACTS = ('anydeskConnectionHistory', 'anydeskSettings', 'anydeskTraceStartups')
FIXTURES = ('synthetic_anydesk_ios7', 'synthetic_anydesk_minimal', 'synthetic_anydesk_two_tenants')

APP = 'private/var/mobile/Containers/Data/Application/'
SUPPORT = 'Library/Application Support/'
ZIP_TIME = (2024, 1, 7, 12, 0, 0)

UUID_1 = '11111111-AAAA-4AAA-8AAA-111111111111'
UUID_2 = '22222222-BBBB-4BBB-8BBB-222222222222'
UUID_DECOY = '33333333-CCCC-4CCC-8CCC-333333333333'

TRACE_COLS = '         ad    svc   9999 1234567   99            '
MAIN_COLS = '         ad   main    123  45678                                  '
RULE = ' * * * * * * * * * * * * * * * * * *\n'


def _banner(day, version_line):
    return (f'   info {day} 10:00:00.100{MAIN_COLS}main - * AnyDesk iOS Startup *\n'
            f'   info {day} 10:00:00.101{MAIN_COLS}main - * Version {version_line}\n'
            f'   info {day} 10:00:00.102{MAIN_COLS}main - * Build 89abcdef0123456789abcdef0123456789abcdef\n'
            f'   info {day} 10:00:00.103{MAIN_COLS}main - * Prefix ad\n')


def _relay(stamp, text):
    return f'   info {stamp}{TRACE_COLS}anynet.connection_mgr - {text}\n'


def _tail(day):
    return (f'warning {day} 10:02:00.000{TRACE_COLS}anynet.relay_connector - Connection failed (synthetic).\n'
            f'  error {day} 10:02:01.000{TRACE_COLS}anynet.dns_resolver - Could not send packet.\n')


def _trace_main():
    established = 'Main relay connection established.'
    failed = 'Main relay connection failed (result_quit).'
    return (f'   info 2023-12-31 23:59:00.000{TRACE_COLS}fiber.scheduler - Scheduler started.\n'
            + RULE
            + _banner('2024-01-05', '7.0.2 (ios_release_7.0.2 0123456789abcdef0123456789abcdef01234567)')
            + _relay('2024-01-05 10:00:05.000', established)
            + _relay('2024-01-05 10:00:06.000', established)
            + _relay('2024-01-05 10:01:05.000', failed)
            + _tail('2024-01-05')
            + RULE
            + _banner('2024-01-06', '7.1.2 (release/ios_7.1.x 0123456789abcdef0123456789abcdef01234567)')
            + ''.join(_relay(f'2024-01-06 10:01:0{n}.000', failed) for n in (5, 6, 7))
            + _tail('2024-01-06'))


def _trace_second():
    return (RULE
            + _banner('2024-03-01', '7.1.2 (release/ios_7.1.x 0123456789abcdef0123456789abcdef01234567)')
            + _relay('2024-03-01 10:00:05.000', 'Main relay connection established.')
            + _tail('2024-03-01'))


def _history(rows):
    return ''.join(f'{d:<8}    {when}    {mode:<6}  {name:<22}    {a}    {b}\r\n'
                   for d, when, mode, name, a, b in rows)


def _system_conf(client_id):
    return (f'ad.anynet.alias=\r\nad.anynet.fpr={"0" * 40}\r\nad.anynet.id={client_id}\r\n'
            'ad.anynet.network_id=0001\r\nad.license.name=free\r\nad.security.frontend_clipboard=1\r\n'
            'ad.telemetry.active_consents=\r\n')


SERVICE_CONF = ('ad.anynet.cert=SYNTHETIC-NOT-A-REAL-CERTIFICATE\nad.anynet.pkey=SYNTHETIC-NOT-A-REAL-KEY\n'
                'ad.license.state_store=SYNTHETIC\nad.telemetry.last_cid=900000100\n')
USER_CONF = 'ad.general.online_status.remote_client=1\nad.privacy.name.show=1\nad.ui.lang=en\n'


def _plist(connected):
    return plistlib.dumps({'com.apple.feedback.managed': {},
                           'user.preference.already.connected.users': connected,
                           'user.preference.install.date': datetime(2023, 12, 1, 8, 30),
                           'user.preference.speed.dial.mode': 1},
                          fmt=plistlib.PlistFormat.FMT_BINARY)


def _container(uuid, history, client_id, trace, connected):
    base = f'{APP}{uuid}/'
    return {
        f'{base}{SUPPORT}.anydesk/connection_trace.txt': history,
        f'{base}{SUPPORT}.anydesk/service.conf': SERVICE_CONF,
        f'{base}{SUPPORT}.anydesk/system.conf': _system_conf(client_id),
        f'{base}{SUPPORT}.anydesk/user.conf': USER_CONF,
        f'{base}{SUPPORT}anydesk.trace': trace,
        f'{base}Library/Preferences/com.anydesk.AnyDesk.plist': _plist(connected),
    }


def _container_1():
    history = _history([
        ('Incoming', '2024-01-05, 10:15', 'User', '', 900000001, 900000001),
        ('Incoming', '2024-01-05, 11:40', 'Passwd', 'synthetic-name', 900000002, 900000002),
        ('Outgoing', '2024-01-06, 09:02', 'User', '', 900000003, 900000003),
    ]) + 'this line is not a connection record\r\n'     # kept whole in Raw Line
    return _container(UUID_1, history, 900000100, _trace_main(), [900000001, 900000002])


def _container_2():
    history = _history([('Incoming', '2024-03-01, 08:00', 'User', '', 900000009, 900000009)])
    return _container(UUID_2, history, 900000200, _trace_second(), [])


def _decoy():
    base = f'{APP}{UUID_DECOY}/{SUPPORT}.other/'
    return {f'{base}connection_trace.txt.bak': 'not an AnyDesk file\n',
            f'{base}system.conf': 'ad.anynet.id=999999999\n'}


def build_files(fixture):
    """{path in the zip: str or bytes} for one fixture name."""
    if fixture == 'synthetic_anydesk_ios7':
        return {**_container_1(), **_decoy()}
    if fixture == 'synthetic_anydesk_two_tenants':
        return {**_container_1(), **_container_2(), **_decoy()}
    if fixture == 'synthetic_anydesk_minimal':
        return {f'{APP}{UUID_1}/{SUPPORT}anydesk.trace': _trace_main()}
    raise ValueError(fixture)


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            data = files[name]
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, data.encode() if isinstance(data, str) else data)


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for fixture in FIXTURES:
        files = build_files(fixture)
        for artifact in ARTIFACTS:
            write_zip(out / f'testdata.anydesk.{artifact}.{fixture}.zip', files)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
