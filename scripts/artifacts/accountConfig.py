__artifacts_v2__ = {
    'accountConfig': {
        'name': 'Account Configuration',
        'description': 'Extracts account configuration information',
        'author': '@AlexisBrignoni',
        'creation_date': '2020-04-30',
        "last_update_date": "2025-10-03",
        'requirements': 'none',
        'category': 'Accounts',
        'notes': '',
        'paths': ('*/preferences/SystemConfiguration/com.apple.accounts.exists.plist',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'user',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 26 rows',
            'felix_ios17': 'iOS 17.6.1 | 32 rows',
            'fsfull002_ios17': 'iOS 17.1 | 28 rows',
            'iphone11_ios17': 'iOS 17.3 | 30 rows',
            'otto_ios17': 'iOS 17.5.1 | 30 rows',
            'abe_ios16': 'iOS 16.5 | 30 rows',
            'felix23_ios16': 'iOS 16.5 | 32 rows',
            'hickman_ios13': 'iOS 13.3.1 | 28 rows',
            'hickman_ios14': 'iOS 14.3 | 30 rows',
            'jess_ios15': 'iOS 15.0.2 | 28 rows',
            'magnet_ios16': 'iOS 16.1.1 | 30 rows',
        }
    }
}


from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def accountConfig(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'com.apple.accounts.exists.plist')
    data_list = []

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        data_list.append((key, val))

    data_headers = ('Account ID', 'Data Value')
    return data_headers, data_list, source_path
