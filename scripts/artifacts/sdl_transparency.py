__artifacts_v2__ = {
    "transparency_devices": {
        "name": "Sysdiagnose - Transparency Log",
        "description": "Devices listed under stateMachine/devices in the transparency.log of a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            (
            (
            "One row per stateMachine/devices entry whose value is a JSON object: name, model, "
            "osVersion, build, serial, deviceID and pushToken as stored. Model Name is the tool's "
            "device model table entry "
            "for the model identifier and OS Version (from build) its build table entry for the "
            "build, looked up with the model's family; both are empty where they do not resolve. On "
            "the 21 test entries the build lookup matched the stored osVersion on 17, gave macOS "
            "11.4.0 against a stored 11.4 on the VMware7,1 entry, and named a Windows 10 version "
            "for the three PC entries, whose osVersion read 10.00; Model Name resolved on the 17 "
            "entries that were not PC or VMware7,1. The name key was present only in the iOS 17.3 "
            "test log (6 of 6 entries) and absent from the two iOS 26 ones. The file was empty (0 "
            "bytes) in both packed sysdiagnoses of the iOS 16.5 test image, and the iOS 13.3.1 and "
            "14.3 test sysdiagnoses had none; the three test sysdiagnoses holding entries listed "
            "13, 2 and 6 devices. The separate logs/swtransparency.log, carried by the two iOS 26 "
            "test sysdiagnoses, is not read; its stateMachine held neither devices nor "
            "cloudRecords in either."
        )
        )
        ),
        "paths": (
            '*/[Tt]ransparency.log',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud-download",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 13 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 2 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 6 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "transparency_cloud": {
        "name": "Sysdiagnose - Transparency Log Cloud Records",
        "description": "Opt-in records listed under stateMachine/cloudRecords in the transparency.log of a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "One row per stateMachine/cloudRecords/optIn entry whose value is a JSON object: "
            "record name, state, osVersion and sn as stored, and timestampReadable as stored and, "
            "where it parses, converted to UTC. The only state "
            "value on test data was KTOptIn(rawValue: 0); the iOS 26.5.2 and 17.3 test sysdiagnoses "
            "held 3 and 2 entries and the iOS 26 one none. The separate logs/swtransparency.log, "
            "carried by the two iOS 26 test sysdiagnoses, is not read; its stateMachine held "
            "neither devices nor cloudRecords in either."
        ),
        "paths": (
            '*/[Tt]ransparency.log',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "timeline", "tsv", "lava"],
        "artifact_icon": "box",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 3 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import json
import re
import tarfile
import zlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)
# Anchored on a path segment: a sysdiagnose archive can carry an AppleDouble sidecar
# (._transparency.log) beside the log, and logs/swtransparency.log is a different file.
TRANSPARENCY_LOG_RE = re.compile(r'(?:^|/)[Tt]ransparency\.log$')


def _is_pax_header(path):
    """True for an entry some extractors write for a tar's pax header, not for a file."""
    return any(part.startswith('PaxHeader') for part in path.replace(' >> ', '/').split('/'))


def _as_text(value):
    return '' if value is None else str(value)


def _parse_to_utc(text):
    """Aware UTC datetime for a '2023-05-20 18:36:50.961 -0400' style value, else None."""
    if not text:
        return None
    text = text.strip()
    for fmt in ('%Y-%m-%d %H:%M:%S.%f %z', '%Y-%m-%d %H:%M:%S %z'):
        try:
            return datetime.strptime(text, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _logs(context):
    """Yield (parsed JSON, evidence path, staged path) for every transparency.log read."""
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), TRANSPARENCY_LOG_RE, text_mode=False):
        rel = context.get_relative_path(source_path)
        if _is_pax_header(rel):
            continue
        try:
            data = file_obj.read()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        if not data.strip():
            logfunc(f'{rel} is empty')
            continue
        try:
            log = json.loads(data.decode('utf-8', errors='replace'))
        except ValueError as ex:
            logfunc(f'{rel} is not JSON: {ex}')
            continue
        if isinstance(log, dict):
            yield log, rel, source_path


def _state_machine(log, key):
    state_machine = log.get('stateMachine')
    value = state_machine.get(key) if isinstance(state_machine, dict) else None
    return value if isinstance(value, dict) else {}


@artifact_processor
def transparency_devices(context):
    data_list = []
    sources = []
    for log, rel, source_path in _logs(context):
        sources.append(source_path)
        for device in _state_machine(log, 'devices').values():
            if not isinstance(device, dict):
                continue
            model = _as_text(device.get('model'))
            build = _as_text(device.get('build'))
            model_name = context.lookup_metadata('apple_device_id_to_model', model) if model else ''
            version_from_build = context.get_apple_os_version(build, model) if build else ''
            data_list.append((_as_text(device.get('name')), model, model_name,
                              _as_text(device.get('osVersion')), build, version_from_build,
                              _as_text(device.get('serial')), _as_text(device.get('deviceID')),
                              _as_text(device.get('pushToken')), rel))
    data_headers = ('Device Name', 'Model', 'Model Name', 'OS Version', 'OS Build',
                    'OS Version (from build)', 'Serial Number', 'Device ID', 'Push Token',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def transparency_cloud(context):
    data_list = []
    sources = []
    for log, rel, source_path in _logs(context):
        sources.append(source_path)
        opt_in = _state_machine(log, 'cloudRecords').get('optIn')
        if not isinstance(opt_in, dict):
            continue
        for name, values in opt_in.items():
            if not isinstance(values, dict):
                continue
            readable = _as_text(values.get('timestampReadable'))
            data_list.append((_parse_to_utc(readable), readable, name, _as_text(values.get('state')),
                              _as_text(values.get('osVersion')), _as_text(values.get('sn')), rel))
    data_headers = (('Timestamp', 'datetime'), 'Timestamp (as stored)', 'Record', 'State',
                    'OS Version', 'Serial Number', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
