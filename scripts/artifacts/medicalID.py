import biplist
import pathlib
import os
import nska_deserialize as nd

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_name(name_with_prefix):
    retval = name_with_prefix
    if name_with_prefix.startswith('HKMedicalIDData'):
        retval = name_with_prefix[15:]
    if retval.endswith('Key'):
        retval = retval[:-3]
    return retval

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
    
    if len(data_list) > 0:
        description = 'User entered Medical information about self'
        report = ArtifactHtmlReport('Medical ID')
        report.start_artifact_report(report_folder, 'Health Info', description)
        report.add_script()
        data_headers = ('Key', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Medical ID'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Medical ID'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data on Medical ID')

__artifacts__ = {
    "medicalID": (
        "Medical ID",
        ('*/mobile/Library/MedicalID/MedicalIDData.archive'),
        get_medicalID)
}