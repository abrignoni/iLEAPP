__artifacts_v2__ = {
    "photosDbexif": {
        "name": "Photos.sqlite EXIF Analysis",
        "description": "Correlates Photos.sqlite asset records with on-disk file EXIF to surface "
                       "timestamp and coordinate mismatches between the library database, cached EXIF, "
                       "and the media file.",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "Photos",
        "notes": "Photos only (ZKIND=0 when available). Only assets with a matching on-disk image "
                 "file and readable EXIF are output. Search patterns cover DCIM and "
                 "PhotoCloudSharingData image extensions. DB Created and DB Modified are UTC "
                 "(datetime). File and Cache DateTime columns are local wall time without timezone "
                 "(strings). DB Modify Lag under 5 minutes is commonly normal ingest delay. DB "
                 "Latitude/Longitude of -180 means no location stored. Latitude/Longitude are file "
                 "EXIF GPS for KML output. File vs DB Delta compares local file EXIF to UTC DB "
                 "Created; sub-minute skew within 2 seconds is tolerated. Mismatch flags are "
                 "investigative leads, not conclusions.",
        "paths": (
            '*Media/PhotoData/Photos.sqlite*',
            '*Media/DCIM/*/*.HEIC',
            '*Media/DCIM/*/*.HEIF',
            '*Media/DCIM/*/*.JPG',
            '*Media/DCIM/*/*.JPEG',
            '*Media/DCIM/*/*.PNG',
            '*Media/PhotoData/PhotoCloudSharingData/*/*/*/*.HEIC',
            '*Media/PhotoData/PhotoCloudSharingData/*/*/*/*.HEIF',
            '*Media/PhotoData/PhotoCloudSharingData/*/*/*/*.JPG',
            '*Media/PhotoData/PhotoCloudSharingData/*/*/*/*.JPEG',
            '*Media/PhotoData/PhotoCloudSharingData/*/*/*/*.PNG',
        ),
        "output_types": "all",
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | co.visualsupply.cam | 350 rows",
            "dexter_ios18": "iOS 18.3.2 | 337 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios18_7": "iOS 18.7.8 | 27 rows",
            "iphone11_ios17": "iOS 17.3 | 289 rows",
            "iphone12_ios18": "iOS 18.7 | 4088 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 451 rows",
            "abe_ios16": "iOS 16.5 | 1683 rows",
            "felix23_ios16": "iOS 16.5 | 33 rows",
            "hickman_ios13": "iOS 13.3.1 | 112 rows",
            "hickman_ios14": "iOS 14.3 | 116 rows",
            "jess_ios15": "iOS 15.0.2 | 12 rows",
            "magnet_ios16": "iOS 16.1.1 | 74 rows",
        }
    }
}

import io
import os
import sqlite3
from datetime import datetime, timedelta

from PIL import Image
from pillow_heif import register_heif_opener

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               does_column_exist_in_db, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

register_heif_opener()

_EXIF_ERRORS = (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError)
_NO_LOCATION = -180.0
_DB_MODIFY_DRIFT_THRESHOLD = timedelta(minutes=5)
_TIMESTAMP_TOLERANCE = timedelta(seconds=2)
_MAX_UTC_OFFSET = timedelta(hours=14)
_IMAGE_EXTENSIONS = ('.HEIC', '.HEIF', '.JPG', '.JPEG', '.PNG')

_EXIF_TAG_NAMES = {
    271: 'Manufacturer',
    272: 'Model',
    305: 'Software',
    274: 'Orientation',
    306: 'DateTime',
    36867: 'DateTimeOriginal',
    36868: 'DateTimeDigitized',
    282: 'Resolution X',
    283: 'Resolution Y',
    316: 'Host device',
}


def _is_exif_image_path(path):
    return str(path).upper().endswith(_IMAGE_EXTENSIONS)


def _is_heic_path(path):
    return str(path).upper().endswith(('.HEIC', '.HEIF'))


def _resolved_path_matches(resolved_path, zdirectory, zfilename):
    """Require the resolved path to match the Photos.sqlite directory and filename."""
    suffix = f'{zdirectory}/{zfilename}'.replace('\\', '/')
    norm = str(resolved_path).replace('\\', '/')
    return norm == suffix or norm.endswith('/' + suffix)


def _resolve_media_path(context, zdirectory, zfilename):
    """Resolve on-disk media via Context's pre-built filename lookup map."""
    if not zdirectory or not zfilename:
        return None
    partials = [
        f'Media/{zdirectory}/{zfilename}',
        f'private/var/mobile/Media/{zdirectory}/{zfilename}',
    ]
    if '/' not in zdirectory:
        partials.extend([
            f'Media/DCIM/{zdirectory}/{zfilename}',
            f'private/var/mobile/Media/DCIM/{zdirectory}/{zfilename}',
        ])
    for partial in partials:
        path = context.get_source_file_path(partial)
        if path and _resolved_path_matches(path, zdirectory, zfilename):
            return path
    return None


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def _normalize_db_coord(value):
    """Photos.sqlite uses -180 as a no-location sentinel."""
    if value is None or value == '':
        return None
    try:
        coord = float(value)
    except (TypeError, ValueError):
        return None
    if abs(coord - _NO_LOCATION) < 1e-6:
        return None
    return coord


def _format_db_coord(value):
    coord = _normalize_db_coord(value)
    return '' if coord is None else coord


def _parse_exif_datetime(value):
    if not value:
        return None
    text = str(value).strip()
    for fmt in ('%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _parse_db_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _format_timedelta(delta):
    if delta is None:
        return ''
    total = int(delta.total_seconds())
    sign = '+' if total >= 0 else '-'
    total = abs(total)
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    if days:
        return f'{sign}{days} days, {hours}:{minutes:02d}:{seconds:02d}'
    return f'{sign}{hours}:{minutes:02d}:{seconds:02d}'


def _format_utc_offset(delta):
    if delta is None:
        return ''
    total = int(delta.total_seconds())
    sign = '+' if total >= 0 else '-'
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    if seconds:
        return f'{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
    return f'{sign}{hours:02d}:{minutes:02d}'


def _snap_offset_to_minute(delta):
    """Snap offsets within _TIMESTAMP_TOLERANCE of a whole minute."""
    if delta is None:
        return None
    total = int(round(delta.total_seconds()))
    sign = 1 if total >= 0 else -1
    abs_total = abs(total)
    remainder = abs_total % 60
    tol = int(_TIMESTAMP_TOLERANCE.total_seconds())
    if remainder <= tol:
        abs_total -= remainder
    elif remainder >= 60 - tol:
        abs_total += (60 - remainder)
    return timedelta(seconds=sign * abs_total)


def _is_plausible_utc_offset(delta):
    snapped = _snap_offset_to_minute(delta)
    if snapped is None:
        return False
    seconds = abs(int(snapped.total_seconds()))
    if seconds > _MAX_UTC_OFFSET.total_seconds():
        return False
    if seconds > 86400:
        return False
    # Whole-hour offsets and common fractional zones (e.g. :30 India, :45 Nepal).
    return (seconds % 60) == 0 and ((seconds // 60) % 15) == 0


def _db_modify_metrics(created_str, modified_str):
    created = _parse_db_datetime(created_str)
    modified = _parse_db_datetime(modified_str)
    if not created or not modified:
        return '', ''
    lag = modified - created
    drift = 'Yes' if lag > _DB_MODIFY_DRIFT_THRESHOLD else 'No'
    return _format_timedelta(lag), drift


def _file_vs_cache_metrics(file_dt_str, cache_dt_str):
    file_dt = _parse_exif_datetime(file_dt_str)
    cache_dt = _parse_exif_datetime(cache_dt_str)
    if not file_dt or not cache_dt:
        return '', ''
    delta = file_dt - cache_dt
    mismatch = 'Yes' if abs(delta) > _TIMESTAMP_TOLERANCE else 'No'
    return _format_timedelta(delta), mismatch


def _file_vs_db_metrics(file_dt_str, db_created_str):
    file_dt = _parse_exif_datetime(file_dt_str)
    db_dt = _parse_db_datetime(db_created_str)
    if not file_dt or not db_dt:
        return '', ''
    offset = file_dt - db_dt
    mismatch = 'No' if _is_plausible_utc_offset(offset) else 'Yes'
    return _format_utc_offset(offset), mismatch


def _coordinate_mismatch(db_lat, db_lon, file_lat, file_lon):
    norm_db_lat = _normalize_db_coord(db_lat)
    norm_db_lon = _normalize_db_coord(db_lon)
    has_db = norm_db_lat is not None and norm_db_lon is not None
    has_file = file_lat != '' and file_lon != ''
    if not has_db and not has_file:
        return 'No'
    if has_db != has_file:
        return 'Yes'
    return 'No' if isclose(norm_db_lat, file_lat) and isclose(norm_db_lon, file_lon) else 'Yes'


def _exif_to_decimal(results, ref_key, val_key):
    direction = results[ref_key]
    parts = results[val_key].replace('(', '').replace(')', '').split(', ')
    decimal = float(parts[0]) + float(parts[1]) / 60 + float(parts[2]) / (60 * 60)
    return decimal * (-1 if direction in ['W', 'S'] else 1)


def _gps_from_ifd(gps_ifd):
    if not gps_ifd:
        return '', ''
    geo = {}
    gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']
    for key, val in gps_ifd.items():
        try:
            geo[gps_keys[key]] = str(val)
        except IndexError:
            pass
    if 'GPSLatitudeRef' not in geo or 'GPSLatitude' not in geo:
        return '', ''
    try:
        return (_exif_to_decimal(geo, 'GPSLatitudeRef', 'GPSLatitude'),
                _exif_to_decimal(geo, 'GPSLongitudeRef', 'GPSLongitude'))
    except _EXIF_ERRORS:
        return '', ''


def _read_file_exif(path):
    """Read EXIF once: timestamps, GPS, and a formatted tag dump."""
    with Image.open(path) as image:
        exif = image.getexif()
    if not exif:
        return '', '', '', '', ''

    file_datetime = ''
    file_datetime_original = ''
    tag_lines = []
    for tag_id, value in exif.items():
        tag_lines.append(f'{_EXIF_TAG_NAMES.get(tag_id, tag_id)}: {value}')
        if tag_id == 306:
            file_datetime = str(value)
        elif tag_id == 36867:
            file_datetime_original = str(value)

    file_lat, file_lon = _gps_from_ifd(exif.get_ifd(0x8825))
    return file_datetime, file_datetime_original, file_lat, file_lon, '\n'.join(tag_lines)


def get_asset_table_name(db_path):
    if does_table_exist_in_db(db_path, 'ZASSET'):
        return 'ZASSET'
    if does_table_exist_in_db(db_path, 'ZGENERICASSET'):
        return 'ZGENERICASSET'
    return None


def _build_query(asset_table, has_additional, has_exif_cache, has_creator, has_zkind):
    exif_cache = ('ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING'
                  if has_exif_cache else "''")
    creator = ('ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID'
               if has_creator else "''")
    join = (f'LEFT JOIN ZADDITIONALASSETATTRIBUTES ON '
            f'{asset_table}.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK'
            if has_additional else '')
    photo_filter = f'WHERE {asset_table}.ZKIND = 0' if has_zkind else ''
    return f'''
    SELECT
        DATETIME({asset_table}.ZDATECREATED+978307200,'UNIXEPOCH'),
        DATETIME({asset_table}.ZMODIFICATIONDATE+978307200,'UNIXEPOCH'),
        {asset_table}.ZDIRECTORY,
        {asset_table}.ZFILENAME,
        {asset_table}.ZLATITUDE,
        {asset_table}.ZLONGITUDE,
        {exif_cache},
        {creator}
    FROM {asset_table}
    {join}
    {photo_filter}
    '''


def _primary_file_datetime(file_datetime, file_datetime_original):
    return file_datetime_original or file_datetime


@artifact_processor
def photosDbexif(context):
    data_headers = (
        ('Media', 'media'),
        'Directory',
        'Filename',
        'Bundle Creator',
        ('DB Created', 'datetime'),
        ('DB Modified', 'datetime'),
        'DB Modify Lag',
        'DB Modify Drift',
        'File DateTime (local)',
        'File DateTimeOriginal (local)',
        'Cache DateTime (local)',
        'File vs DB Delta',
        'File vs Cache Delta',
        'File vs Cache Mismatch',
        'File vs DB Mismatch',
        'DB Latitude',
        'DB Longitude',
        'Latitude',
        'Longitude',
        'Coordinate Mismatch',
        'File EXIF Tags',
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.basename(file_found).endswith('.sqlite'):
            continue

        asset_table = get_asset_table_name(file_found)
        if not asset_table:
            logfunc("INFO: No asset table (ZASSET or ZGENERICASSET) found. Skipping Photos.sqlite Analysis.")
            continue

        has_additional = does_table_exist_in_db(file_found, 'ZADDITIONALASSETATTRIBUTES')
        has_exif_cache = (has_additional
                          and does_column_exist_in_db(file_found, 'ZADDITIONALASSETATTRIBUTES',
                                                      'ZEXIFTIMESTAMPSTRING'))
        has_creator = (has_additional
                       and does_column_exist_in_db(file_found, 'ZADDITIONALASSETATTRIBUTES',
                                                   'ZCREATORBUNDLEID'))
        has_zkind = does_column_exist_in_db(file_found, asset_table, 'ZKIND')

        try:
            rows = get_sqlite_db_records(file_found, _build_query(
                asset_table, has_additional, has_exif_cache, has_creator, has_zkind))
        except sqlite3.Error as ex:
            logfunc(f'Error processing Photos.sqlite Analysis: {ex}')
            continue

        skipped_non_image = 0
        skipped_no_file = 0
        skipped_no_exif = 0
        for row in rows:
            (zdatecreated, zmodificationdate, zdirectory, zfilename, zlatitude, zlongitude,
             cache_datetime, zbundlecreator) = row

            if zfilename and not _is_exif_image_path(zfilename):
                skipped_non_image += 1
                continue

            media_path = _resolve_media_path(context, zdirectory, zfilename)
            if not media_path:
                skipped_no_file += 1
                continue

            if not _is_exif_image_path(media_path):
                skipped_non_image += 1
                continue

            file_datetime = file_datetime_original = file_lat = file_lon = exif_tags = ''
            try:
                file_datetime, file_datetime_original, file_lat, file_lon, exif_tags = _read_file_exif(media_path)
            except _EXIF_ERRORS as ex:
                logfunc(f'Error getting exif on: {media_path}: {ex}')

            if not exif_tags:
                skipped_no_exif += 1
                continue

            thumb = ''
            searchbase = os.path.basename(media_path)
            if _is_heic_path(media_path):
                try:
                    with io.BytesIO() as buf:
                        Image.open(media_path).save(buf, format='JPEG')
                        thumb = check_in_embedded_media(
                            media_path, buf.getvalue(), f'{searchbase}.jpg',
                            force_type='image/jpeg', force_extension='jpg')
                except _EXIF_ERRORS as ex:
                    logfunc(f'Error converting HEIC thumbnail on {media_path}: {ex}')
            else:
                thumb = check_in_media(media_path)

            db_modify_lag, db_modify_drift = _db_modify_metrics(zdatecreated, zmodificationdate)
            primary_file_dt = _primary_file_datetime(file_datetime, file_datetime_original)
            cache_dt = cache_datetime or ''
            file_vs_db_delta, file_vs_db_mismatch = _file_vs_db_metrics(primary_file_dt, zdatecreated)
            file_vs_cache_delta, file_vs_cache_mismatch = _file_vs_cache_metrics(primary_file_dt, cache_dt)
            coord_mismatch = _coordinate_mismatch(zlatitude, zlongitude, file_lat, file_lon)

            data_list.append((
                thumb,
                zdirectory,
                zfilename,
                zbundlecreator or '',
                zdatecreated,
                zmodificationdate,
                db_modify_lag,
                db_modify_drift,
                file_datetime,
                file_datetime_original,
                cache_dt,
                file_vs_db_delta,
                file_vs_cache_delta,
                file_vs_cache_mismatch,
                file_vs_db_mismatch,
                _format_db_coord(zlatitude),
                _format_db_coord(zlongitude),
                file_lat,
                file_lon,
                coord_mismatch,
                exif_tags,
            ))

        if skipped_non_image:
            logfunc(f'Photos.sqlite EXIF: skipped {skipped_non_image} non-image assets')
        if skipped_no_file:
            logfunc(f'Photos.sqlite EXIF: skipped {skipped_no_file} assets with no matching on-disk file')
        if skipped_no_exif:
            logfunc(f'Photos.sqlite EXIF: skipped {skipped_no_exif} assets with no readable file EXIF')

        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
