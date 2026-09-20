__artifacts_v2__ = {
    "pref_devinfo": {
        "name": "Sysdiagnose - Device Info",
        "description": "Device name, host name and model from the Networking/preferences.plist in a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "ComputerName and HostName are read from System/System, and Model and __VERSION__ from "
            "the top level, all as stored. Model equalled the HWModel line of "
            "remotectl_dumpstate.txt on the five test sysdiagnoses whose dump state had content and "
            "is pushed to Device Info as Hardware Model, with ComputerName as Device Name and "
            "HostName as Host Name. __VERSION__ was 20191120 on the iOS 14.3 to 26 test "
            "sysdiagnoses and absent from the iOS 13.3.1 one. A copy inside a packed sysdiagnose "
            "holds the values as they stood when the sysdiagnose was taken."
        ),
        "paths": (
            '*/Networking/preferences.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 1 row",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1 row",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 1 row",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "pref_netserv": {
        "name": "Sysdiagnose - Network Services",
        "description": "Network service interfaces from the Networking/preferences.plist in a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "One row per NetworkServices entry carrying an Interface dictionary: the service GUID "
            "and the interface's UserDefinedName, Type, Hardware and DeviceName, as stored, sorted "
            "by source file, device name and GUID. The seven test sysdiagnoses (iOS 13.3.1 to 26) "
            "held 7 to 13 entries each; the Type and Hardware pairs seen were Ethernet/AirPort, "
            "Ethernet/Ethernet, com.apple.CommCenter/com.apple.CommCenter and VPN with no Hardware."
        ),
        "paths": (
            '*/Networking/preferences.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 13 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 13 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 10 rows",
            "felix23_ios16": "iOS 16.5 | 15 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import plistlib
import tarfile
import zlib
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error,
                plistlib.InvalidFileException, ExpatError, ValueError)


def _as_text(value):
    return '' if value is None else str(value)


def _preferences(context):
    """Yield (plist, evidence path, staged path) for every Networking/preferences.plist.

    The archive match is by file name, so a preferences.plist elsewhere in a packed
    sysdiagnose is skipped by the directory test.
    """
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'preferences.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        if 'Networking' not in rel.replace(' >> ', '/').split('/'):
            continue
        try:
            plist = plistlib.loads(file_obj.read())
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        if isinstance(plist, dict):
            yield plist, rel, source_path


@artifact_processor
def pref_devinfo(context):
    data_list = []
    sources = []
    for plist, rel, source_path in _preferences(context):
        sources.append(source_path)
        system = plist.get('System')
        system = system.get('System') if isinstance(system, dict) else None
        if not isinstance(system, dict):
            system = {}
        computer_name = _as_text(system.get('ComputerName'))
        host_name = _as_text(system.get('HostName'))
        model = _as_text(plist.get('Model'))
        version = _as_text(plist.get('__VERSION__'))
        if computer_name:
            device_info('Device Information', 'Device Name', computer_name, rel)
        if host_name:
            device_info('Device Information', 'Host Name', host_name, rel)
        if model:
            device_info('Device Information', 'Hardware Model', model, rel)
        data_list.append((computer_name, host_name, model, version, rel))
    data_headers = ('Device Name', 'Host Name', 'Model', 'Preferences Version (__VERSION__)',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def pref_netserv(context):
    data_list = []
    sources = []
    for plist, rel, source_path in _preferences(context):
        sources.append(source_path)
        services = plist.get('NetworkServices')
        if not isinstance(services, dict):
            continue
        for service_id, service in services.items():
            interface = service.get('Interface') if isinstance(service, dict) else None
            if not isinstance(interface, dict):
                continue
            data_list.append((service_id, _as_text(interface.get('UserDefinedName')),
                              _as_text(interface.get('Type')), _as_text(interface.get('Hardware')),
                              _as_text(interface.get('DeviceName')), rel))
    data_list.sort(key=lambda row: (row[5], row[4], row[0]))
    data_headers = ('Network Service GUID', 'Interface Name', 'Interface Type',
                    'Interface Hardware', 'Interface Device Name', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
