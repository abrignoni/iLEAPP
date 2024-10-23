__artifacts_v2__ = {
    "conDev": {
        "name": "Connected Devices",
        "description": "Extracts information about connected devices from iTunes preferences",
        "author": "",
        "version": "1.0",
        "date": "2024-10-23",
        "requirements": "none",
        "category": "Connected Devices",
        "notes": "",
        "paths": ('*/iTunes_Control/iTunes/iTunesPrefs',),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import logfunc, artifact_processor
import os

MAGIC_BYTES = b"\x01\x01\x80\x00\x00"
MAGIC_OFFSET = 92
NAME_OFFSET = 157

@artifact_processor
def conDev(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ('User Name', 'Computer Name', 'File Offset', 'Source File')
    source_path = ''

    for file_found in files_found:
        source_path = file_found
        with open(file_found, "rb") as f:
            data = f.read()

        logfunc(f"Data being interpreted for FRPD is of type: {type(data)}")
        
        magic_index = data.find(MAGIC_BYTES)
        if magic_index == -1:
            logfunc("Magic bytes not found in iTunes Prefs FRPD")
            continue

        logfunc("Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now")
        
        names = []
        current_name = bytearray()
        name_start_offset = magic_index + MAGIC_OFFSET
        for i, byte in enumerate(data[name_start_offset:]):
            if byte == 0:
                if current_name:
                    names.append((current_name.decode(), name_start_offset + i - len(current_name)))
                    current_name = bytearray()
                    name_start_offset = name_start_offset + i + 1
            else:
                current_name.append(byte)

        # Process names in pairs
        for i in range(0, len(names), 2):
            if i + 1 < len(names):
                user_name, user_offset = names[i]
                computer_name, _ = names[i+1]
                data_list.append((
                    user_name,
                    computer_name,
                    str(user_offset),
                    os.path.basename(file_found)
                ))
            else:
                user_name, user_offset = names[i]
                data_list.append((
                    user_name,
                    '',
                    str(user_offset),
                    os.path.basename(file_found)
                ))

    return data_headers, data_list, source_path
