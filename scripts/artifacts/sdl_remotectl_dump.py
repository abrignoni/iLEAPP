__artifacts_v2__ = {
    "remotectl_dump": {
        "name": "Sysdiagnose - Dump State",
        "description": "Device values from the remotectl_dumpstate.txt in a sysdiagnose (UUID, product type, build, serial, model, region, hardware model, architecture, device and chip identifiers), as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "Reads the first 'UUID:', 'Product Type:' and 'OS Build:' lines and the first "
            "'SerialNumber =>', 'ModelNumber =>', 'RegionCode =>', 'HWModel =>', 'CPUArchitecture "
            "=>', 'UniqueDeviceID =>' and 'UniqueChipID =>' lines, as stored. Product Type is "
            "looked up in the tool's device model table and Region Code in its region table, each "
            "added as its own row where it resolves; both resolved on every test file with content. "
            "UUID, Product Type, Serial Number and Hardware Model are pushed to Device Info as "
            "stored, and the resolved region as Product Region. All ten lines were present on the "
            "five test sysdiagnoses holding a non-empty file (iOS 16 to 26) and in the unpacked "
            "IN_PROGRESS sysdiagnose folder of the iOS 16.1.1 test image; the iOS 14.3 test "
            "sysdiagnose's copy was empty and the iOS 13.3.1 one had no such file."
        ),
        "paths": (
            '*/remotectl_dumpstate.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 12 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 12 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 12 rows",
            "felix23_ios16": "iOS 16.5 | 24 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 12 rows",
        }
    }
}

import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)

# (text the line starts with, row label, Device Info category and label or None)
_FIELDS = (
    ('UUID: ', 'UUID', ('Device Information', 'UUID')),
    ('Product Type: ', 'Product Type', ('Device Information', 'Product Type')),
    ('OS Build: ', 'OS Build', None),
    ('SerialNumber => ', 'Serial Number', ('Device Information', 'Serial Number')),
    ('ModelNumber => ', 'Model Number', None),
    ('RegionCode => ', 'Region Code', None),
    ('HWModel => ', 'Hardware Model', ('Device Information', 'Hardware Model')),
    ('CPUArchitecture => ', 'CPU Architecture', None),
    ('UniqueDeviceID => ', 'Unique Device ID', None),
    ('UniqueChipID => ', 'Unique Chip ID', None),
)


def _is_pax_header(path):
    """True for an entry some extractors write for a tar's pax header, not for a file."""
    return any(part.startswith('PaxHeader') for part in path.replace(' >> ', '/').split('/'))


@artifact_processor
def remotectl_dump(context):
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'remotectl_dumpstate.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        if _is_pax_header(rel):
            continue
        try:
            lines = file_obj.read().decode('utf-8', errors='replace').splitlines()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        sources.append(source_path)
        values = {}
        for line in lines:
            text = line.strip()
            for prefix, label, _info in _FIELDS:
                if label not in values and text.startswith(prefix):
                    values[label] = text[len(prefix):].strip()
        for _prefix, label, info in _FIELDS:
            if label not in values:
                continue
            value = values[label]
            data_list.append((label, value, rel))
            if info:
                device_info(info[0], info[1], value, rel)
            if label == 'Product Type':
                model_name = context.lookup_metadata('apple_device_id_to_model', value)
                if model_name:
                    data_list.append(('Product Type (model name)', model_name, rel))
            if label == 'Region Code':
                region = context.lookup_metadata('apple_device_region_code_to_region', value)
                if region:
                    data_list.append(('Region (from code)', region, rel))
                    device_info('Device Information', 'Product Region', region, rel)
    data_headers = ('Property', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
