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
        'artifact_icon': 'user'
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
