__artifacts_v2__ = {
    "bluetooth_status": {
        "name": "Sysdiagnose - Bluetooth Status",
        "description": "Bluetooth adapter state lines from the bluetooth_status.txt in a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "The file opens with a title line and then key : value lines, reported as stored; on "
            "all seven test sysdiagnoses (iOS 13.3.1 to 26) the keys were Power, MAC Address, "
            "Discoverable, Connectable, Scanning and Devices. The meaning of each flag is not "
            "decoded here. A sysdiagnose holds the file under WiFi/ and again under "
            "logs/Bluetooth/CoreCapture/; the two copies were byte-identical on the six test "
            "sysdiagnoses holding both (the iOS 13.3.1 one had only the WiFi/ copy), so a copy "
            "identical to one already read is skipped and the rows cite the copy read first. Rows "
            "came only from sysdiagnoses on test data: the three standalone ones, the two packed "
            "inside the iOS 16.5 test image and the one packed inside each of the iOS 13.3.1 and "
            "14.3 images; the unpacked IN_PROGRESS sysdiagnose folder in the iOS 16.1.1 test image "
            "matched no bluetooth_status.txt."
        ),
        "paths": (
            '*/WiFi/bluetooth_status.txt',
            '*/logs/Bluetooth/CoreCapture/bluetooth_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 6 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 6 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 6 rows",
            "felix23_ios16": "iOS 16.5 | 12 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "bluetooth_devices": {
        "name": "Sysdiagnose - Bluetooth Devices",
        "description": "Bluetooth device entries from the bluetooth_status.txt in a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "One row per block after the adapter lines; blocks are separated by blank lines and "
            "start with the device name. Address (letter case as stored), Paired, CloudPaired, "
            "Connected, Type and LE are reported as stored, and any other key in a block goes to "
            "Other Properties: Apple, RSSI, Manufacturer, Role, Conn Mode, Conn Interval and AFH "
            "Map appeared on test data. On all seven test sysdiagnoses (iOS 13.3.1 to 26) the count "
            "at the start of the adapter's Devices line equalled the number of blocks. Copies of "
            "the file inside a sysdiagnose are handled as described for Sysdiagnose - Bluetooth "
            "Status."
        ),
        "paths": (
            '*/WiFi/bluetooth_status.txt',
            '*/logs/Bluetooth/CoreCapture/bluetooth_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 9 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1 row",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 5 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import hashlib
import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)
_DEVICE_COLUMNS = ('Address', 'Paired', 'CloudPaired', 'Connected', 'Type', 'LE')


def _status_files(context):
    """Yield (lines, evidence path, staged path) once per distinct file content.

    A sysdiagnose holds bluetooth_status.txt under WiFi/ and again under
    logs/Bluetooth/CoreCapture/. The two were byte-identical on every test sysdiagnose
    carrying both, so a copy whose content was already read is skipped and the rows
    cite the copy read first.
    """
    seen = set()
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'bluetooth_status.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        try:
            data = file_obj.read()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        digest = hashlib.sha256(data).digest()
        if digest in seen:
            continue
        seen.add(digest)
        yield data.decode('utf-8', errors='replace').splitlines(), rel, source_path


def _split_sections(lines):
    """(adapter key/value pairs, device blocks).

    The file opens with a title line, then 'key : value' lines up to a blank line,
    then one block per device separated by blank lines, each starting with the
    device name.
    """
    status = []
    index = 1
    while index < len(lines):
        text = lines[index].strip()
        if not text:
            if status:
                break
        elif ':' in text:
            key, value = text.split(':', 1)
            status.append((key.strip(), value.strip()))
        index += 1
    blocks = []
    block = []
    for line in lines[index:] + ['']:
        text = line.strip()
        if text:
            block.append(text)
        elif block:
            blocks.append(block)
            block = []
    return status, blocks


@artifact_processor
def bluetooth_status(context):
    data_list = []
    sources = []
    for lines, rel, source_path in _status_files(context):
        status, _blocks = _split_sections(lines)
        for key, value in status:
            data_list.append((key, value, rel))
        sources.append(source_path)
    data_headers = ('Category', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def bluetooth_devices(context):
    data_list = []
    sources = []
    for lines, rel, source_path in _status_files(context):
        _status, blocks = _split_sections(lines)
        for block in blocks:
            props = {}
            for line in block[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    props[key.strip()] = value.strip()
            other = '; '.join(f'{key}: {value}' for key, value in props.items()
                              if key not in _DEVICE_COLUMNS)
            data_list.append((block[0], *(props.get(column, '') for column in _DEVICE_COLUMNS),
                              other, rel))
        sources.append(source_path)
    data_headers = ('Device Name', 'Address', 'Paired', 'Cloud Paired', 'Connected', 'Type',
                    'LE', 'Other Properties (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
