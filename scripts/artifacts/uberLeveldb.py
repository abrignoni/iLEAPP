import pathlib
import json
import datetime
import scripts.ccl_leveldb

from scripts.ilapfuncs import logfunc, artifact_processor


@artifact_processor
def get_uberloc(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    maindirectory = ''
    for in_db_dir in in_dirs:
        leveldb_records = scripts.ccl_leveldb.RawLevelDb(in_db_dir)

        for record in leveldb_records.iterate_records_raw():
            record_sequence = record.seq
            record_value = record.value
            origin = str(record.origin_file)

            p = str(pathlib.Path(origin).parent.name)
            f = str(pathlib.Path(origin).name)
            pf = f'{p}/{f}'

            value = record_value.decode()

            try:
                value = json.loads(value)
            except Exception:
                pass
            else:
                active_trips = (value['jsonConformingObject']['data'].get('active_trips', ''))

                ui_state = value['jsonConformingObject']['data'].get('ui_state', '')
                if ui_state == '':
                    metadata = ''
                    scene = ''
                    timestamp_ms_ui = ''
                else:
                    metadata = ui_state['metadata']
                    scene = ui_state['scene']
                    timestamp_ms_ui = ui_state['timestamp_ms']
                    timestamp_ms_ui = datetime.datetime.fromtimestamp(timestamp_ms_ui / 1000, datetime.UTC)

                app_type_value_map = (value['jsonConformingObject']['data'].get('app_type_value_map', ''))

                time_ms = value['jsonConformingObject']['meta']['time_ms']
                time_ms = datetime.datetime.fromtimestamp(time_ms / 1000, datetime.UTC)
                location = value['jsonConformingObject']['meta'].get('location', '')
                if location == '':
                    lat = lon = speed = city = gps_time = horz_acc = ''
                else:
                    lat = location['latitude']
                    lon = location['longitude']
                    speed = location['speed']
                    city = location['city']
                    gps_time = location['gps_time_ms']
                    gps_time = datetime.datetime.fromtimestamp(gps_time / 1000, datetime.UTC)
                    horz_acc = location['horizontal_accuracy']

                data_list.append((time_ms, record_sequence, city, speed, gps_time, lat, lon,
                                 horz_acc, timestamp_ms_ui, metadata, scene, app_type_value_map,
                                 active_trips, pf))

    if in_dirs:
        maindirectory = str(pathlib.Path(in_db_dir).parent)

    data_headers = ('Timestamp', 'Rec. Sequence', 'City', 'Speed', 'GPS Timestamp', 'Latitude',
                    'Longitude', 'Horizontal Acc.', 'UI Timestamp', 'Metadata', 'Scene',
                    'App Type Value Map', 'Active Trips', 'Origin')
    return data_headers, data_list, maindirectory

__artifacts_v2__ = {
    "get_uberloc": {
        "name": "Uber Locations",
        "description": "Uber locations inside LevelDB",
        "author": "Alexis 'Brigs' Brignoni",
        "version": "1",
        "date": "04/08/2024",
        "requirements": "",
        "category": "Uber",
        "notes": "Thanks to Alex Caithness for the ccc_leveldb libraries",
        "paths": (
            '*/Data/Application/*/Library/Application Support/com.ubercab.UberClient/storagev2/*',
        ),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
