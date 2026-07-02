__artifacts_v2__ = {
    "mobileContainerManager": {
        "name": "Mobile Container Manager",
        "description": "Group container removals logged by containermanagerd (last reference removed)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Mobile Container Manager",
        "notes": "",
        "paths": ('**/containermanagerd.log.*',),
        "output_types": "standard",
        "artifact_icon": "trash-2"
    }
}

from datetime import datetime

from scripts.ilapfuncs import artifact_processor

_MARKER = ('[MCMGroupManager _removeGroupContainersIfNeededforUser:groupContainerClass:identifiers:'
           'referenceCounts:]: Last reference to group container')


@artifact_processor
def mobileContainerManager(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = (('Datetime', 'datetime'), 'Removed', 'Line')
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = source_path or file_found
        try:
            with open(file_found, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
        except OSError:
            continue

        for linecount, line in enumerate(lines, 1):
            if _MARKER not in line:
                continue
            txts = line.split()
            try:
                # log prefix: <dow> <Mon> <day> <HH:MM:SS> <year> ... <group at index 15>
                month_number = datetime.strptime(txts[1], '%b').month
                dtime_obj = datetime.strptime(f'{txts[4]}-{month_number}-{txts[2]} {txts[3]}',
                                              '%Y-%m-%d %H:%M:%S')
                group = txts[15]
            except (ValueError, IndexError):
                continue
            data_list.append((dtime_obj, group, linecount))

    return data_headers, data_list, source_path
