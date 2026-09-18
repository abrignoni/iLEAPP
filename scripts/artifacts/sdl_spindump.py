__artifacts_v2__ = {
    "spindump": {
        "name": "Sysdiagnose - Spin Dump Info",
        "description": "Header values from the spindump-nosymbols.txt in a sysdiagnose (time since boot and since wake, free disk space, preferred language, country code, keyboards), as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "Reads the header before the first Process line: Time Since Boot, Time Awake Since Boot "
            "and Time Since Wake (as stored, with a value in seconds decoded into days, hours, "
            "minutes and seconds), Free disk space, Preferred User Language, Country Code and "
            "Keyboards, each row carrying the dump's Date/Time converted to UTC. Which lines a file "
            "holds varies: the iOS 13.3.1 and 14.3 test sysdiagnoses had only the two awake and "
            "wake lines, the iOS 16 to 26 ones had all seven, and Time Since Wake read n/a (machine "
            "hasn't slept) on one. Preferred User Language and Country Code are pushed to Device "
            "Info; the time and disk readings are not, because they describe the moment the dump "
            "was taken, and a sysdiagnose packed inside a full file system image can be much older "
            "than the image (the two in the iOS 16.5 test image were taken in December 2022 and "
            "February 2023, and the image in July 2023)."
        ),
        "paths": (
            '*/spindump-nosymbols.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 7 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 7 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 7 rows",
            "felix23_ios16": "iOS 16.5 | 14 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "spindump_process": {
        "name": "Sysdiagnose - Spin Dump Processes",
        "description": "Process entries from the spindump-nosymbols.txt in a sysdiagnose (name, PID, state, identifier, path, parent, footprint, CPU time), as stored",
        "author": "@stark4n6 & Gemini",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "One row per 'Process: name [pid] (state)' line and the key: value lines under it until "
            "a Thread, Binary Images or --- line; State is the parenthetical as stored, empty when "
            "there was none (on test data it was empty on 2,260 rows and 'suspended' on 321). Dump "
            "Start Time and Dump End Time are the header's Date/Time and End time converted to UTC, "
            "and OS Version and Hardware Model come from the header. Identifier, Version, Path, "
            "UUID, Parent, Responsible, UID, Architecture, Footprint, Time Since Fork, CPU Time and "
            "Sudden Term are as stored and empty where a file lacks them. The seven test "
            "sysdiagnoses (iOS 13.3.1 to 26) held 247 to 541 process entries each."
        ),
        "paths": (
            '*/spindump-nosymbols.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 378 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 541 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 405 rows",
            "felix23_ios16": "iOS 16.5 | 722 rows",
            "hickman_ios13": "iOS 13.3.1 | 288 rows",
            "hickman_ios14": "iOS 14.3 | 247 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        },
    }
}

import re
import tarfile
import zlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)
_SECONDS_RE = re.compile(r'^(\d+)s\b')

# Header lines reported by the Spin Dump Info artifact: (key in the file, row label,
# Device Info category and label or None). Durations are decoded; the time-based
# readings are not pushed to Device Info because they describe the moment the dump
# was taken, which a packed sysdiagnose may place long before the extraction.
_INFO_FIELDS = (
    ('Time Since Boot', 'Time Since Boot', None),
    ('Time Awake Since Boot', 'Time Awake Since Boot', None),
    ('Time Since Wake', 'Time Since Wake', None),
    ('Free disk space', 'Free disk space', None),
    ('Preferred User Language', 'Preferred User Language',
     ('Settings & Preferences', 'Preferred Language')),
    ('Country Code', 'Country Code', ('Device Information', 'Country Code')),
    ('Keyboards', 'Keyboards', None),
)

_PROCESS_RE = re.compile(r'^Process:\s+(?P<name>.+?)\s+\[(?P<pid>\d+)\](?:\s*\((?P<state>.+?)\))?\s*$')
_KEY_VALUE_RE = re.compile(r'^(?P<key>[A-Za-z0-9\s]+?):\s+(?P<value>.*)$')
_PROCESS_COLUMNS = ('Identifier', 'Version', 'Path', 'UUID', 'Parent', 'Responsible', 'UID',
                    'Architecture', 'Footprint', 'Time Since Fork', 'CPU Time', 'Sudden Term')


def _is_pax_header(path):
    """True for an entry some extractors write for a tar's pax header, not for a file."""
    return any(part.startswith('PaxHeader') for part in path.replace(' >> ', '/').split('/'))


def display_time(seconds):
    days = int(seconds / (24 * 3600))
    seconds -= days * (24 * 3600)
    hours = int(seconds / 3600)
    seconds -= hours * 3600
    minutes = int(seconds / 60)
    seconds -= minutes * 60
    return f"{days}d {hours}h {minutes}m {seconds}s"


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


def _dumps(context):
    """Yield (header lines, all lines, evidence path, staged path) per spindump read.

    The header is everything before the first 'Process:' line.
    """
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'spindump-nosymbols.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        if _is_pax_header(rel):
            continue
        try:
            lines = file_obj.read().decode('utf-8', errors='replace').splitlines()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        header = []
        for line in lines:
            if line.startswith('Process:'):
                break
            header.append(line)
        yield header, lines, rel, source_path


def _header_value(header, key):
    for line in header:
        if line.startswith(key + ':'):
            return line.split(':', 1)[1].strip()
    return ''


@artifact_processor
def spindump(context):
    data_list = []
    sources = []
    for header, _lines, rel, source_path in _dumps(context):
        sources.append(source_path)
        dump_time = _parse_to_utc(_header_value(header, 'Date/Time'))
        for key, label, info in _INFO_FIELDS:
            value = _header_value(header, key)
            if not value:
                continue
            seconds = _SECONDS_RE.match(value)
            decoded = display_time(int(seconds.group(1))) if seconds else ''
            data_list.append((dump_time, label, value, decoded, rel))
            if info:
                device_info(info[0], info[1], value, rel)
    data_headers = (('Dump Time', 'datetime'), 'Property', 'Value', 'Decoded', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def spindump_process(context):
    data_list = []
    sources = []
    for header, lines, rel, source_path in _dumps(context):
        sources.append(source_path)
        dump_start = _parse_to_utc(_header_value(header, 'Date/Time'))
        dump_end = _parse_to_utc(_header_value(header, 'End time'))
        os_version = _header_value(header, 'OS Version')
        hardware_model = _header_value(header, 'Hardware model')
        current = None
        for line in lines[len(header):]:
            text = line.strip()
            process = _PROCESS_RE.match(text)
            if process:
                if current is not None:
                    data_list.append(_process_row(current, dump_start, dump_end, os_version,
                                                  hardware_model, rel))
                current = {'name': process.group('name'), 'pid': process.group('pid'),
                           'state': process.group('state') or ''}
                continue
            if current is None:
                continue
            if text.startswith(('Thread ', 'Binary Images:', '---')):
                data_list.append(_process_row(current, dump_start, dump_end, os_version,
                                              hardware_model, rel))
                current = None
                continue
            key_value = _KEY_VALUE_RE.match(text)
            if key_value:
                current[key_value.group('key').strip()] = key_value.group('value').strip()
        if current is not None:
            data_list.append(_process_row(current, dump_start, dump_end, os_version,
                                          hardware_model, rel))
    data_headers = (
        ('Dump Start Time', 'datetime'),
        ('Dump End Time', 'datetime'),
        'Process Name',
        'PID',
        'State (as stored)',
        'Identifier',
        'Version',
        'Path',
        'UUID',
        'Parent',
        'Responsible',
        'UID',
        'Architecture',
        'Footprint',
        'Time Since Fork',
        'CPU Time',
        'Sudden Term',
        'OS Version',
        'Hardware Model',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


def _process_row(process, dump_start, dump_end, os_version, hardware_model, rel):
    return (dump_start, dump_end, process['name'], process['pid'], process['state'],
            *(process.get(column, '') for column in _PROCESS_COLUMNS),
            os_version, hardware_model, rel)
