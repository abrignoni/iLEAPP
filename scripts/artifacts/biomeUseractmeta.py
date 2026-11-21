__artifacts_v2__ = {
    "get_biomeUseractmeta": {
        "name": "Biome - User Activity Metadata",
        "description": "Parses user activity metadata entries from biomes",
        "author": "@JohnHyla, @mattiaepi (Mattia Epifani)",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Timestamp, Activity Type (User Activity Data), Title, Bplist Data and "
                 "Payload Data are read from the property list stored in the userActivityData "
                 "field. Container Data is read from a second property list nested in it. Activity Type and Bundle ID are the activityType and "
                 "associatedBundleID fields of the BMUniversalRecentsMetadata class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Activity Type was reported before as Description; the property-list value "
                 "reported before as Activity type is now Activity Type (User Activity Data). "
                 "On the tested images Activity Type and Activity Type (User Activity Data) were "
                 "identical on each of the 1,125 written rows; both are kept because they "
                 "come from different places in the record. Associated URL is field 6 (associatedURLString) of the BMUniversalRecentsMetadata class in BiomeLibrary.framework, macOS 27.2.1 (26B131); no iOS copy was read. It was not reported before as its own column. On the 21 iOS images tested it was set on 187 of 551 written UniversalRecents.UserActivity.Metadata rows (15 of the 16 images with written records) and 145 of 574 written UserActivityMetadata rows (5 of 5 images). On these 332 rows the same string also appeared inside Bplist Data.",
        "paths": (
            '*/Biome/streams/restricted/UserActivityMetadata/local*',
            '*/streams/*/UniversalRecents.UserActivity.Metadata/local/*',
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 364 rows",
            "felix23_ios16": "iOS 16.5 | 166 rows",
            "jess_ios15": "iOS 15.0.2 | 72 rows",
            "magnet_ios16": "iOS 16.1.1 | 131 rows",
            "hc_ios18_7": "iOS 18.7.8 | 101 rows",
            "iphone11_ios17": "iOS 17.3 | 450 rows",
        }
    }
}


import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_time_obj_to_utc, get_plist_content, logfunc

from datetime import datetime as _dt

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

def _safe_time_obj(value):
    """Set UTC tzinfo on datetime objects; pass strings/None through unchanged."""
    return convert_time_obj_to_utc(value) if isinstance(value, _dt) else value



@artifact_processor
def get_biomeUseractmeta(context):

    #typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'double', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}
    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    # field 6 is pinned so a URL string is never decoded as a nested message
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, {'6': {'type': 'bytes', 'name': ''}})
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome User Activity Metadata: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                bplistdata = (protostuff['2'])
                desc1 = (protostuff['4'].decode())
                desc2 = (protostuff['5'].decode())
                associated_url = protostuff.get('6')
                associated_url = associated_url.decode('utf-8', errors='replace') \
                    if isinstance(associated_url, bytes) else ''
                
                
                #deserialized_plist = nd.deserialize_plist_from_string(bplistdata)
                deserialized_plist = get_plist_content(bplistdata)
                if not deserialized_plist or not isinstance(deserialized_plist, dict):
                    continue                
                
                title = (deserialized_plist.get('title',''))
                when = (deserialized_plist['when'])
                when = _safe_time_obj(when)
                actype = (deserialized_plist['activityType'])
                #exdate = (deserialized_plist.get('expirationDate',''))
                
                if (deserialized_plist.get('payload', '')) != '':
                    payload = (deserialized_plist.get('payload'))
                else:
                    payload = ''
                    
                internalbplist = (deserialized_plist.get('contentAttributeSetData',''))
                
                if internalbplist != '':
                    if type(internalbplist) != str:
                        try:
                            internalbplist = (deserialized_plist['contentAttributeSetData']['NS.data'])
                        except (KeyError, TypeError) as ex:
                            print(ex)
                            print('Processing as bplist["container"] directly.')
                        #deserialized_plist2 = nd.deserialize_plist_from_string(internalbplist)
                        deserialized_plist2 = get_plist_content(internalbplist)
                        if not deserialized_plist2 or not isinstance(deserialized_plist2, dict):
                            continue
                        container = (deserialized_plist2['container'])
                    else:
                        container = internalbplist
                else:
                    container =''
                
                agg = ''
                for a, b in deserialized_plist.items():
                    if a == 'payload':
                        pass
                    else:
                        if b == ' ':
                            b = 'NULL'
                        agg = agg + f'{a} = {b}<br>'
                
                data_list.append((ts, when, record.state.name, actype, desc1, desc2, title, associated_url, agg.strip(), payload,
                                  container, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State',
                    'Activity Type (User Activity Data)', 'Activity Type', 'Bundle ID', 'Title', 'Associated URL', 'Bplist Data', 'Payload Data','Container Data', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
