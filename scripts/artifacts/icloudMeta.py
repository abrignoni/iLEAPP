__artifacts_v2__ = {
    "icloudmeta": {
        "name": "iCloud - File Metadata",
        "description": "iCloud Drive file metadata parsed from Metadata.txt (iCloud Returns)",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "iCloud Returns",
        "notes": "btime/ctime/mtime are epoch milliseconds, stored as UTC.",
        "paths": ('*/iclouddrive/Metadata.txt',),
        "output_types": "standard",
        "artifact_icon": "cloud"
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc


def _ms_to_utc(value):
    """Epoch-milliseconds (UTC) to an aware UTC datetime; blank for missing/zero values."""
    if isinstance(value, (int, float)) and value > 0:
        return convert_unix_ts_to_utc(value)
    return ''


@artifact_processor
def icloudmeta(context):
    data_headers = (('Btime', 'datetime'), ('Ctime', 'datetime'), ('Mtime', 'datetime'), 'Name',
                    'Last Editor Name', 'Doc ID', 'Parent ID', 'Type', 'Deleted?', 'Size', 'Zone',
                    'Executable?', 'Hidden?')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        had_data = False
        with open(file_found, 'r', encoding='utf-8') as filecontent:
            for line in filecontent:
                try:
                    records = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for rec in records:
                    flags = rec.get('file_flags', {})
                    last_editor = ''
                    if rec.get('last_editor_name'):
                        try:
                            last_editor = json.loads(rec['last_editor_name']).get('name', '')
                        except (json.JSONDecodeError, TypeError, AttributeError):
                            last_editor = ''
                    data_list.append((
                        _ms_to_utc(rec.get('btime')), _ms_to_utc(rec.get('ctime')),
                        _ms_to_utc(rec.get('mtime')), rec.get('name', ''), last_editor,
                        rec.get('document_id', ''), rec.get('parent_id', ''), rec.get('type', ''),
                        rec.get('deleted', ''), rec.get('size', ''), rec.get('zone', ''),
                        flags.get('is_executable', ''), flags.get('is_hidden', '')))
                    had_data = True
        if had_data:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
