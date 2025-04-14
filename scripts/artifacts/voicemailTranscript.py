__artifacts_v2__ = {
    'voicemail_transcript': {
        'name': 'Voicemail Transcript',
        'description': 'Parses Voicemail Transcript Files',
        'author': '@JohnHyla',
        'creation_date': '2025-04-05',
        'last_update_date': '2025-04-14',
        'requirements': 'none',
        'category': 'Call History',
        'notes': '',
        'paths': (
            '*/mobile/Library/Voicemail/*.transcript',
            '*/mobile/Library/Application Support/com.apple.FaceTime/Assets/*.transcript'
        ),
        'output_types': 'standard',
        "artifact_icon": "file-text"
    }
}


from scripts.ilapfuncs import artifact_processor, get_plist_file_content, convert_ts_int_to_utc


@artifact_processor
def voicemail_transcript(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        deserialized_plist = get_plist_file_content(file_found)

        data_list.append([
            convert_ts_int_to_utc(seeker.file_infos[file_found].creation_date),
            convert_ts_int_to_utc(seeker.file_infos[file_found].modification_date),
            seeker.file_infos[file_found].source_path,
            deserialized_plist.get('transcriptionString', ''),
            deserialized_plist.get('confidence', '')])

    data_headers = (
        ('File Created', 'datetime'), ('File Modified', 'datetime'), 
        'Filename', 'Transcript', 'Confidence')

    return data_headers, data_list, 'See Filename Column'
