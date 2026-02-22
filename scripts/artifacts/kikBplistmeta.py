#!/usr/bin/env python3
from pathlib import Path
import os
import biplist

from scripts.ilapfuncs import artifact_processor, media_to_html


@artifact_processor
def get_kikBplistmeta(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            pass
        else:
            sha1org = sha1scaled = blockhash = appname = layout = allowforward = filesize = filename = thumb = appid = content_id = ''
            with open(file_found, 'rb') as f:
                plist = biplist.readPlist(f)
                for key, val in plist.items():
                    if key == 'id':
                        content_id = val
                    elif key == 'hashes':
                        for x in val:
                            if x['name'] == 'sha1-original':
                                sha1org = x.get('value', '')
                            if x['name'] == 'sha1-scaled':
                                sha1scaled = x.get('value', '')
                            if x['name'] == 'blockhash-scaled':
                                blockhash = x.get('value', '')
                    elif key == 'string':
                        for x in val:
                            if x['name'] == 'app-name':
                                appname = x.get('value', '')
                            if x['name'] == 'layout':
                                layout = x.get('value', '')
                            if x['name'] == 'allow-forward':
                                allowforward = x.get('value', '')
                            if x['name'] == 'file-size':
                                filesize = x.get('value', '')
                            if x['name'] == 'file-name':
                                filename = x.get('value', '')
                    elif key == 'image':
                        thumbfilename = content_id

                        complete = Path(report_folder).joinpath('Kik')
                        if not complete.exists():
                            Path(f'{complete}').mkdir(parents=True, exist_ok=True)

                        imgfile = open(f'{complete}{thumbfilename}', "wb")
                        imgfile.write(val[0]['value'])
                        imgfile.close()

                        imagetofind = []
                        imagetofind.append(f'{complete}{thumbfilename}')
                        thumb = media_to_html(content_id, imagetofind, report_folder)

                    elif key == 'app-id':
                        appid = val

                data_list.append((content_id, filename, filesize, allowforward, layout, appname, appid, sha1org, sha1scaled, blockhash, thumb))

    data_headers = ('Content ID', 'Filename', 'File Size', 'Allow Forward', 'Layout', 'App Name',
                    'App ID', 'SHA1 Original', 'SHA1 Scaled', 'Blockhash Scaled', 'Internal Thumbnail')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_kikBplistmeta": {
        "name": "Kik Media Metadata",
        "description": "Metadata from Kik media directory bplist files.",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/cores/private/*/attachments/*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "html_columns": ["Internal Thumbnail"]
    }
}
