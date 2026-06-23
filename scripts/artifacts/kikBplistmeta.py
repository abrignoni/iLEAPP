__artifacts_v2__ = {
    "kikBplistmeta": {
        "name": "Kik Attachments Bplist Metadata",
        "description": "Metadata from the Kik attachments directory bplist files, with the embedded thumbnail",
        "author": "@AlexisBrignoni",
        "version": "1.0",
        "date": "2026-06-22",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/cores/private/*/attachments/*',),
        "output_types": "standard",
        "artifact_icon": "paperclip"
    }
}

import os

import biplist

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media


@artifact_processor
def kikBplistmeta(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('Content ID', 'Filename', 'File Size', 'Allow Forward', 'Layout', 'App Name',
                    'App ID', 'SHA1 Original', 'SHA1 Scaled', 'Blockhash Scaled',
                    ('Internal Thumbnail', 'media'))
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as f:
                plist = biplist.readPlist(f)
        except Exception:  # pylint: disable=broad-exception-caught
            continue  # not a (readable) binary plist
        if not isinstance(plist, dict):
            continue
        source_path = source_path or file_found

        content_id = appid = filename = filesize = allowforward = layout = appname = ''
        sha1org = sha1scaled = blockhash = ''
        image_data = None

        for key, val in plist.items():
            if key == 'id':
                content_id = val
            elif key == 'app-id':
                appid = val
            elif key == 'hashes':
                for x in val:
                    if x.get('name') == 'sha1-original':
                        sha1org = x.get('value', '')
                    elif x.get('name') == 'sha1-scaled':
                        sha1scaled = x.get('value', '')
                    elif x.get('name') == 'blockhash-scaled':
                        blockhash = x.get('value', '')
            elif key == 'string':
                for x in val:
                    name = x.get('name')
                    if name == 'app-name':
                        appname = x.get('value', '')
                    elif name == 'layout':
                        layout = x.get('value', '')
                    elif name == 'allow-forward':
                        allowforward = x.get('value', '')
                    elif name == 'file-size':
                        filesize = x.get('value', '')
                    elif name == 'file-name':
                        filename = x.get('value', '')
            elif key == 'image':
                try:
                    image_data = val[0]['value']
                except (KeyError, IndexError, TypeError):
                    image_data = None

        thumb = ''
        if image_data:
            force_type = force_extension = None
            if image_data[:3] == b'\xff\xd8\xff':
                force_type, force_extension = 'image/jpeg', 'jpg'
            elif image_data[:8] == b'\x89PNG\r\n\x1a\n':
                force_type, force_extension = 'image/png', 'png'
            thumb = check_in_embedded_media(file_found, image_data, name=str(content_id),
                                            force_type=force_type, force_extension=force_extension) or ''

        data_list.append((content_id, filename, filesize, allowforward, layout, appname, appid,
                          sha1org, sha1scaled, blockhash, thumb))

    return data_headers, data_list, source_path
