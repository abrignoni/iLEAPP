__artifacts_v2__ = {
'Ph086assetsdcloudServiceEnableLogPlist': {
'name': 'Ph086-assetsd-cloud-Service-Enable-Log-Plist',
'description': 'Parses basic data from */PhotoData/private/com.apple.accountsd/cloudServiceEnableLog.plist'
' which is a plist that tracks when Cloud Photos Library (CPL) has been enabled.'
' Based on research and published blogs written by Scott Koenig'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'version': '5.0',
'date': '2025-01-05',
'requirements': 'Acquisition that contains assetsd cloudServiceEnableLog.plist',
'category': 'Photos.sqlite-Y-Settings-Plist-CPL-Service-Enabled',
'notes': '',
'paths': ('*/com.apple.assetsd/cloudServiceEnableLog.plist',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "settings",
'sample_data': {
'dexter_ios18': 'iOS 18.3.2 | 1 row',
'hc_ios18_7': 'iOS 18.7.8 | 1 row',
'iphone11_ios17': 'iOS 17.3 | 1 row',
'iphone12_ios18': 'iOS 18.7 | 1 row',
'iphone14plus_ios18': 'iOS 18.0 | 1 row',
'otto_ios17': 'iOS 17.5.1 | 3 rows',
'felix23_ios16': 'iOS 16.5 | 1 row',
'hickman_ios14': 'iOS 14.3 | 1 row',
'jess_ios15': 'iOS 15.0.2 | 1 row',
'magnet_ios16': 'iOS 16.1.1 | 1 row',
}
}
}

import plistlib
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def Ph086assetsdcloudServiceEnableLogPlist(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
    if len(pl) > 0:
        for key in pl:
            if 'timestamp' in key:
                timestamputc = key['timestamp']
            else:
                timestamputc = ''
            if 'type' in key:
                servicetype = key['type']
            else:
                servicetype = ''
            if 'enabled' in key:
                enabledstate = key['enabled']
            else:
                enabledstate = ''

            data_list.append((timestamputc, servicetype, enabledstate))

    data_headers = (
    'TimestampUTC',
    'Service-Type',
    'Enabled-State')
    return data_headers, data_list, source_path
