__artifacts_v2__ = {
    "medicalID": {
        "name": "Medical ID",
        "description": "User entered Medical ID information about self (MedicalIDData.archive)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-06-22",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ('*/mobile/Library/MedicalID/MedicalIDData.archive',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 16 rows",
            "otto_ios17": "iOS 17.5.1 | 36 rows",
        }
    }
}

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor


def get_name(name_with_prefix):
    retval = name_with_prefix
    if name_with_prefix.startswith('HKMedicalIDData'):
        retval = name_with_prefix[15:]
    if retval.endswith('Key'):
        retval = retval[:-3]
    return retval


@artifact_processor
def medicalID(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('Key', 'Value')
    data_list = []

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('MedicalIDData.archive'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as f:
        deserialized_plist = nd.deserialize_plist(f)
        for key, value in deserialized_plist.items():
            key_name = get_name(key)
            if isinstance(value, dict):
                unit = value.get('UnitKey', {}).get('HKUnitStringKey', '')
                val = str(value.get('ValueKey', ''))
                if unit:
                    val += ' ' + unit
                data_list.append((key_name, val))
            elif isinstance(value, list):
                # not seen!
                data_list.append((key_name, str(value)))
            else:
                data_list.append((key_name, value))

    return data_headers, data_list, source_path
