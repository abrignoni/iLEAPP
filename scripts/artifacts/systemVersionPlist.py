""" See artifact description below """

__artifacts_v2__ = {
    "system_version_plist": {
        "name": "System Version plist",
        "description": "Values from SystemVersion.plist, including the iOS version and build, read "
                       "from the extraction and from sysdiagnose archives in it. Previously named "
                       "Ph99SystemVersionPlist.py",
        "author": "Scott Koenig",
        "creation_date": "2025-06-02",
        "last_update_date": "2026-09-14",
        "requirements": "Acquisition that contains SystemVersion.plist",
        "category": "IOS Build",
        "notes": "Reads System/Library/CoreServices/SystemVersion.plist from the extraction and, inside "
                 "each sysdiagnose_*.tar.gz archive, logs/SystemVersion/SystemVersion.plist; other "
                 "SystemVersion.plist members of an archive, such as logs/Splat/OS/SystemVersion.plist, "
                 "are not read. A copy whose ProductVersion is empty is not reported, and a file matched "
                 "more than once is read once. When the extraction holds several copies, only those "
                 "nearest the extraction root are reported: on the images in sample_data the copies left "
                 "out sat under private/var/MobileAsset (each with an empty ProductVersion), usr/SDK "
                 "(ProductVersion 11.1 on an iOS 12.4 image) and private/preboot/Cryptexes. Rows read "
                 "from an archive name that archive in Source File and hold the values stored in it, "
                 "which can differ from the extraction's copy: on felix23_ios16 two archives hold 16.0.3 "
                 "and the extraction's copy holds 16.5. The Device Information entries come from the "
                 "extraction's copy; only when the extraction has no reported copy do they come from the "
                 "archive copies, each archive adding the values its own copy holds. That branch was "
                 "exercised on a constructed tree holding two felix23_ios16 sysdiagnose archives and a "
                 "MobileAsset copy, not on a registered image. Added parsing of SystemVersion.plist in a "
                 "sysdiagnose archive by C_Peter",
        "paths": (
            "*/System/Library/CoreServices/SystemVersion.plist",
            "*/sysdiagnose_*.tar.gz"),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "git-commit",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "felix23_ios16": "iOS 16.5 | 18 rows",
            "hickman_ios13": "iOS 13.3.1 | 12 rows",
            "hickman_ios14": "iOS 14.3 | 12 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
        }
    }
}

import os

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, \
    device_info, iOS, get_sysdiagnose_files

_ARCHIVE_MEMBER = 'logs/SystemVersion/SystemVersion.plist'

_DEVICE_INFO_LABELS = {
    'ProductBuildVersion': 'Product Build Version',
    'ProductVersion': 'iOS Version',
    'ProductName': 'Product Name',
    'BuildID': 'Build ID',
    'SystemImageID': 'System Image ID',
}


def _depth(path):
    """Number of components in a path, whichever separator it uses."""
    return len(path.replace('\\', '/').strip('/').split('/'))


@artifact_processor
def system_version_plist(context):
    """ See artifact description """
    extraction_copies = []
    archive_copies = []
    seen = set()

    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), "SystemVersion.plist", text_mode=False):
        if source_path in seen:
            continue
        seen.add(source_path)

        # A file on disk is a copy in the extraction; anything else is an archive member,
        # which the helper names "<archive> >> <member>".
        in_extraction = os.path.isfile(source_path)
        if not in_extraction:
            member = source_path.rsplit(' >> ', 1)[-1]
            if member != _ARCHIVE_MEMBER and not member.endswith('/' + _ARCHIVE_MEMBER):
                continue

        pl = get_plist_file_content(file_obj)
        if not pl or not pl.get('ProductVersion'):
            continue
        if in_extraction:
            extraction_copies.append((context.get_relative_path(source_path), source_path, pl))
        else:
            archive_copies.append((context.get_relative_path(source_path), source_path, pl))

    reported = []
    if extraction_copies:
        nearest = min(_depth(rel) for rel, _, _ in extraction_copies)
        reported = [(rel, source, pl, True) for rel, source, pl in sorted(extraction_copies, key=lambda c: c[0])
                    if _depth(rel) == nearest]
    archives_describe_device = not reported
    reported += [(rel, source, pl, archives_describe_device)
                 for rel, source, pl in sorted(archive_copies, key=lambda c: c[0])]

    data_list = []
    for rel, _, pl, describes_device in reported:
        for key, val in pl.items():
            data_list.append((key, val, rel))
            if not describes_device or key not in _DEVICE_INFO_LABELS:
                continue
            if key == 'ProductVersion':
                iOS.set_version(val)
                context.set_installed_os_version(val)
            device_info("Device Information", _DEVICE_INFO_LABELS[key], val, rel)

    data_headers = ('Property', 'Property Value', 'Source File')
    return data_headers, data_list, '\n'.join(source for _, source, _, _ in reported)
