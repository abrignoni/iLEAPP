__artifacts_v2__ = {
    "get_biomeCameraAutoFocusROI": {
        "name": "Biome - Camera Auto Focus ROI",
        "description": "Parses camera autofocus region of interest records from the "
                       "CameraCapture.AutoFocusROI biome stream: the camera port, the focus "
                       "region type and box, the lux level, the subject distance and the client "
                       "application type. What action writes a record is not established "
                       "here.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names and enum names are those of the BMCameraCaptureAutoFocusROI class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the "
                 "class was read. Camera Port is field 1 (portType). Focus Region Type is field 2 "
                 "(0 Unknown, 1 Default, 2 Window, 3 Face, 4 Body). Top Left Row, Top Left Column, "
                 "Width and Height are fields 3 to 6 and Lux Level is field 7; the field names carry "
                 "no unit and none is established here. Subject Distance is field 8, stored as a 32-bit float "
                 "(fixed32 on every tested written record) and shown rounded to three decimals; "
                 "the field name carries no unit and none is established here. Client App Type is field 9 "
                 "(clientApplicationIDType), for example 3 CameraApp, 4 MessagesApp, 6 WhatsApp "
                 "or 15 Zoom; it names a kind of app, not a bundle id. Before, fields 2 to 7 and 9 "
                 "were reported raw as Field N and field 8 as Field 8 (float)."),
        "paths": ('*/streams/*/CameraCapture.AutoFocusROI/local/*',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "dexter_ios18": "313 rows",
            "hc_ios18_7": "12 rows",
            "iphone12_ios18": "146 rows",
        },
    }
}


import os
import struct
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
    '9': {'type': 'int', 'name': ''},
}

# Enum names read from BiomeLibrary.framework BMCameraCaptureAutoFocusROI on macOS 27.2.1 (26B131).
FOCUS_REGION_TYPES = {0: 'Unknown', 1: 'Default', 2: 'Window', 3: 'Face', 4: 'Body'}
CLIENT_APP_TYPES = {0: 'Unknown', 1: 'External', 2: 'InternalUnknown', 3: 'CameraApp', 4:
                    'MessagesApp', 5: 'FaceTimeApp', 6: 'WhatsApp', 7: 'FacebookMessengerApp',
                    8: 'Skype', 9: 'WeChat', 10: 'MeasureApp', 11: 'Instagram', 12: 'SnapChat',
                    13: 'TikTok', 14: 'WebEx', 15: 'Zoom', 16: 'GoogleHangouts', 17:
                    'BlueJeans', 18: 'GoToMeeting', 19: 'JoinMe', 20: 'Houseparty', 21:
                    'CiscoJabber', 22: 'MicrosoftTeams', 23: 'InCallService', 24: 'MeetInOne',
                    25: 'GoogleMeet', 26: 'Slack', 27: 'QuickTimePlayerX', 28: 'PhotoBooth',
                    29: 'TencentMeeting', 30: 'Discord', 31: 'OBS', 32: 'DingTalk', 33:
                    'SidecarExtensionCapture', 34: 'ContinuityCaptureD', 35: 'DeskView', 36:
                    'BraveBrowser', 37: 'ChromeBrowser', 38: 'EdgeBrowser', 39:
                    'FirefoxBrowser', 40: 'Telegram', 41: 'Line', 42: 'Ecamm', 43: 'Camo', 44:
                    'ReplayD', 45: 'NetworkEndpointUI', 46: 'Music'}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _float32(value):
    if not isinstance(value, int):
        return ''
    try:
        return round(struct.unpack('<f', struct.pack('<I', value & 0xFFFFFFFF))[0], 3)
    except struct.error:
        return ''


@artifact_processor
def get_biomeCameraAutoFocusROI(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
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
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Camera Auto Focus ROI: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                region = protostuff.get('2')
                app = protostuff.get('9')
                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  CLIENT_APP_TYPES.get(app, '') if isinstance(app, int) else '',
                                  '' if app is None else app,
                                  FOCUS_REGION_TYPES.get(region, '') if isinstance(region, int) else '',
                                  '' if region is None else region,
                                  protostuff.get('3', ''), protostuff.get('4', ''),
                                  protostuff.get('5', ''), protostuff.get('6', ''),
                                  protostuff.get('7', ''), _float32(protostuff.get('8')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name) + (None,) * 11 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Camera Port',
                    'Client App Type', 'Client App Type (raw)', 'Focus Region Type',
                    'Focus Region Type (raw)', 'Top Left Row', 'Top Left Column', 'Width',
                    'Height', 'Lux Level', 'Subject Distance', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
