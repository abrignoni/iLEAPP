__artifacts_v2__ = {
    "get_uberloc": {
        "name": "Uber - Locations (LevelDB)",
        "description": "Uber locations extracted from LevelDB storage.",
        "author": "Alexis Brignoni",
        "creation_date": "2024-04-08",
        "last_update_date": "2025-11-21",
        "requirements": "",
        "category": "Uber",
        "notes": "Thanks to Alex Caithness for the ccc_leveldb libraries",
        "paths": (
            '*/Data/Application/*/Library/Application Support/com.ubercab.UberClient/storagev2/*',
        ),
        'output_types': "standard",
        'artifact_icon': "map-pin"
    }
}

import pathlib
import json
import scripts.ccl_leveldb
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    logfunc
)


@artifact_processor
def get_uberloc(context):
    files_found = context.get_files_found()
    data_list = []

    in_dirs = set(pathlib.Path(x).parent for x in files_found)

    source_path = ', '.join([str(p) for p in in_dirs])

    for in_db_dir in in_dirs:
        try:
            leveldb_records = scripts.ccl_leveldb.RawLevelDb(in_db_dir)
        except Exception as e:
            logfunc(f"Error opening LevelDB at {in_db_dir}: {e}")
            continue

        for record in leveldb_records.iterate_records_raw():
            record_sequence = record.seq
            # record_key = record.user_key
            record_value = record.value
            origin = str(record.origin_file)

            p = str(pathlib.Path(origin).parent.name)
            f = str(pathlib.Path(origin).name)
            pf = f'{p}/{f}'

            try:
                value_str = record_value.decode()
                value = json.loads(value_str)
            except Exception:
                continue

            try:
                json_obj = value.get('jsonConformingObject', {})
                data_obj = json_obj.get('data', {})
                meta_obj = json_obj.get('meta', {})

                active_trips = data_obj.get('active_trips', '')
                ui_state = data_obj.get('ui_state', '')
                app_type_value_map = data_obj.get('app_type_value_map', '')

                metadata = ''
                scene = ''
                timestamp_ms_ui = ''

                if ui_state:
                    metadata = ui_state.get('metadata', '')
                    scene = ui_state.get('scene', '')
                    ts_val = ui_state.get('timestamp_ms')
                    if ts_val:
                        timestamp_ms_ui = convert_unix_ts_to_utc(ts_val / 1000)

                time_ms_val = meta_obj.get('time_ms')
                time_ms = ''
                if time_ms_val:
                    time_ms = convert_unix_ts_to_utc(time_ms_val / 1000)

                location = meta_obj.get('location', '')
                lat = ''
                lon = ''
                speed = ''
                city = ''
                gps_time = ''
                horz_acc = ''

                if location:
                    lat = location.get('latitude', '')
                    lon = location.get('longitude', '')
                    speed = location.get('speed', '')
                    city = location.get('city', '')
                    gps_val = location.get('gps_time_ms')
                    if gps_val:
                        gps_time = convert_unix_ts_to_utc(gps_val / 1000)
                    horz_acc = location.get('horizontal_accuracy', '')

                data_list.append((
                    time_ms,
                    record_sequence,
                    city,
                    speed,
                    gps_time,
                    lat,
                    lon,
                    horz_acc,
                    timestamp_ms_ui,
                    metadata,
                    scene,
                    app_type_value_map,
                    active_trips,
                    pf
                ))

            except Exception as e:
                pass

    data_headers = (
        ('Timestamp', 'datetime'),
        'Rec. Sequence',
        'City',
        'Speed',
        ('GPS Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Horizontal Acc.',
        ('UI Timestamp', 'datetime'),
        'Metadata',
        'Scene',
        'App Type Value Map',
        'Active Trips',
        'Origin'
    )

    return data_headers, data_list, source_path
