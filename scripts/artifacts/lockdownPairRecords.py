__artifacts_v2__ = {
    "lockdownPairRecords": {
        "name": "Lockdown Pair Records",
        "description": "Hosts the device holds a lockdown pair record or escrow record for, with the host "
                       "certificate's validity start and the record's WallTimeWhenCreated where it holds one",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Identifiers",
        "notes": ("One row per host ID found in root/Library/Lockdown/pair_records, pair_records.movedaside or "
                  "escrow_records, each a plist named by that host ID. Pair Record Folder names the folder that"
                  " held the pair record (blank when only an escrow record exists; 4 hosts on 4 tested images) "
                  "and Escrow Record says whether escrow_records holds a file for the same host ID. What moving"
                  " a record to pair_records.movedaside means is not established; all 4 records on hc_ios18_7 "
                  "were there. Host Certificate Valid From is the notBefore time of the pair record's "
                  "HostCertificate, read with the DER reader in scripts/vendor/c2pareader.py, which agreed with"
                  " the cryptography package on all 32 tested certificates. Wall Time When Created is "
                  "WallTimeWhenCreated read as Unix seconds: on the 13 tested records that hold it, it fell "
                  "within 4 seconds of the host certificate's notBefore, which is how the epoch was established"
                  " (no Apple source was found). Time When Created is TimeWhenCreated as stored, a 3 to 6 digit"
                  " integer beside BootSessionWhenCreated on the 22 of 32 tested pair records that hold it; it "
                  "is not a calendar date by magnitude and its meaning is not established. Host Name, Marketing"
                  " Name, Serial Number, Host ID and System BUID are as stored; Host Name was set on 12 of 36 "
                  "tested rows. Whose serial number and marketing name the SerialNumber and MarketingName keys "
                  "describe is not established. Not reported: the HostCertificate, DeviceCertificate and "
                  "RootCertificate themselves and the escrow record's BagBag bytes. The device's own name in "
                  "Lockdown/data_ark.plist is read by the Device Name artifact. Not tested on an iTunes backup."),
        "paths": ('*/root/Library/Lockdown/pair_records/*.plist',
                  '*/root/Library/Lockdown/pair_records.movedaside/*.plist',
                  '*/root/Library/Lockdown/escrow_records/*.plist'),
        "output_types": "standard",
        "artifact_icon": "device-desktop",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "belkactf6_tar": "iOS 16.3 | 3 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 2 rows",
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        }
    }
}

import base64
import binascii
import os
import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.vendor.c2pareader import _x509

RECORD_FOLDERS = ('pair_records', 'pair_records.movedaside', 'escrow_records')


def _certificate_not_before(value):
    """The notBefore of a PEM or DER certificate as a UTC datetime, or '' when it does not parse."""
    if not isinstance(value, (bytes, bytearray)) or not value:
        return ''
    data = bytes(value)
    try:
        if data.startswith(b'-----'):
            data = base64.b64decode(b''.join(line for line in data.splitlines()
                                             if not line.startswith(b'-----')))
        not_before = _x509(data)['not_before']
        return datetime.strptime(not_before, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except (binascii.Error, ValueError, IndexError, KeyError, TypeError) as error:
        logfunc(f'Lockdown Pair Records: host certificate not read: {error}')
        return ''


def _unix_seconds(value):
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return datetime.fromtimestamp(value, timezone.utc)
    return ''


@artifact_processor
def lockdownPairRecords(context):
    data_headers = (('Host Certificate Valid From', 'datetime'), ('Wall Time When Created', 'datetime'),
                    'Host Name', 'Marketing Name', 'Serial Number', 'Host ID', 'System BUID',
                    'Pair Record Folder', 'Escrow Record', 'Time When Created (as stored)',
                    'Boot Session When Created')
    # (Lockdown folder, HostID) -> what each record folder holds for that host, so two
    # extraction roots in one input never merge and each host is one row
    hosts = {}
    sources = []
    for file_found in sorted(str(f) for f in context.get_files_found()):
        folder = os.path.basename(os.path.dirname(file_found))
        if folder not in RECORD_FOLDERS or not os.path.isfile(file_found):
            continue
        try:
            with open(file_found, 'rb') as fp:
                record = plistlib.load(fp)
        except (OSError, plistlib.InvalidFileException, ValueError) as error:
            logfunc(f'Lockdown Pair Records: could not read {os.path.basename(file_found)}: {error}')
            continue
        if not isinstance(record, dict):
            continue
        host_id = record.get('HostID') or os.path.splitext(os.path.basename(file_found))[0]
        lockdown = os.path.dirname(os.path.dirname(file_found))
        entry = hosts.setdefault((lockdown, host_id), {})
        entry[folder] = record
        sources.append(file_found)

    data_list = []
    for (_, host_id), entry in sorted(hosts.items(), key=lambda kv: kv[0]):
        folder = next((f for f in ('pair_records', 'pair_records.movedaside') if f in entry), '')
        pair = entry[folder] if folder else {}  # an escrow record carries no host details
        data_list.append((
            _certificate_not_before(pair.get('HostCertificate')),
            _unix_seconds(pair.get('WallTimeWhenCreated')),
            pair.get('HostName', ''), pair.get('MarketingName', ''), pair.get('SerialNumber', ''),
            host_id, pair.get('SystemBUID', ''), folder,
            'Yes' if 'escrow_records' in entry else 'No',
            pair.get('TimeWhenCreated', ''), pair.get('BootSessionWhenCreated', '')))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
