__artifacts_v2__ = {
    "fdrInfo": {
        "name": "Sysdiagnose - FDR Diagnostic Report",
        "description": "Device properties the FDRDiagnosticReport.plist in a sysdiagnose lists as verified or failed, with their live and sealed values as stored",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "FDR is described by The Apple Wiki as a protocol whereby factory calibration data is "
            "'reset' or 'restored' to the device (Reference: The Apple Wiki, 'Factory Data "
            "Restore', https://theapplewiki.com/wiki/Factory_Data_Restore); what each list in the "
            "report means beyond its name is not established here. One row per entry of "
            "VerifiedProperties (LiveProperty) and of FailureProperties (LiveProperty, "
            "SealedProperty and FailureReason), plus one for the SealDate string, all as stored; "
            "the VerifiedData and FailureData lists are not reported. Keys seen under "
            "VerifiedProperties on the five test sysdiagnoses holding the file (iOS 16 to 26): "
            "SrNm, BMac, WMac, imei, ime2, meid, seid, tsid, mlb#, arc#, drp#, nuid, bat#, SDOM, "
            "BORD and eeid; the iOS 17.3 one listed eeid under FailureProperties with FailureReason "
            "PropertyMismatched. Five keys are also pushed to Device Info when listed under "
            "VerifiedProperties: SrNm as Serial Number (it equalled the SerialNumber in "
            "remotectl_dumpstate.txt on all five), BMac as Bluetooth MAC Address (it equalled the "
            "MAC Address in bluetooth_status.txt on the four whose adapter reported one), WMac as "
            "Wi-Fi MAC Address (it equalled the en0 interface's IOMACAddress in "
            "NetworkInterfaces.plist on the one full file system test image holding both), and imei "
            "and meid as IMEI and MEID, named by their keys and 15 and 14 digits long on test data. "
            "The iOS 13.3.1 and 14.3 test sysdiagnoses had no FDRDiagnosticReport.plist."
        ),
        "paths": (
            '*/logs/FDR/FDRDiagnosticReport.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "id",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 14 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 15 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 15 rows",
            "felix23_ios16": "iOS 16.5 | 22 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
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

# Keys pushed to the report's Device Info page when the report lists them as verified.
# SrNm equalled the serial in remotectl_dumpstate.txt on every test sysdiagnose, and
# WMac equalled the Wi-Fi interface's MAC in the one full extraction holding both.
_DEVICE_INFO = {
    'SrNm': ('Device Information', 'Serial Number'),
    'imei': ('Cellular', 'IMEI'),
    'meid': ('Cellular', 'MEID'),
    'WMac': ('Network', 'Wi-Fi MAC Address'),
    'BMac': ('Network', 'Bluetooth MAC Address'),
}


def _as_text(value):
    return '' if value is None else str(value)


@artifact_processor
def fdrInfo(context):
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'FDRDiagnosticReport.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        try:
            plist = plistlib.loads(file_obj.read())
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        if not isinstance(plist, dict):
            continue
        sources.append(source_path)
        for list_name in ('VerifiedProperties', 'FailureProperties'):
            for item in plist.get(list_name) or []:
                if not isinstance(item, dict):
                    continue
                for key, value in item.items():
                    fields = value if isinstance(value, dict) else {}
                    live = _as_text(fields.get('LiveProperty'))
                    data_list.append((key, list_name, live, _as_text(fields.get('SealedProperty')),
                                      _as_text(fields.get('FailureReason')), rel))
                    if list_name == 'VerifiedProperties' and key in _DEVICE_INFO and live:
                        category, label = _DEVICE_INFO[key]
                        device_info(category, label, live, rel)
        if 'SealDate' in plist:
            data_list.append(('SealDate', '', _as_text(plist.get('SealDate')), '', '', rel))
    data_headers = ('Property', 'List', 'Live Value', 'Sealed Value', 'Failure Reason',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)
