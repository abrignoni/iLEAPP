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
def get_medicalID(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, 'rb') as f:
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

    data_headers = ('Key', 'Value')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_medicalID": {
        "name": "Medical ID",
        "description": "User entered Medical information about self",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Medical ID",
        "notes": "",
        "paths": ('*/mobile/Library/MedicalID/MedicalIDData.archive',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
