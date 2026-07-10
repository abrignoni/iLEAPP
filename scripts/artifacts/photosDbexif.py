__artifacts_v2__ = {
    "photosDbexif": {
        "name": "Photos.sqlite EXIF Analysis",
        "description": "Correlates Photos.sqlite asset records with the on-disk media EXIF to flag "
                       "mismatched timestamps and coordinates (possible tampering).",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Photos",
        "notes": "All times labeled 'False' require validation. Database timestamps are UTC; the EXIF "
                 "Creation/Changed timestamp is local time — use the Possible Exif Offset to compare.",
        "paths": ('*Media/PhotoData/Photos.sqlite*', '*Media/DCIM/*/**'),
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
        }
    }
}

import io
import os
import sqlite3
from datetime import datetime

import pytz
from PIL import Image
from pillow_heif import register_heif_opener

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media,
                               does_column_exist_in_db, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_EXIF_ERRORS = (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError)


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif().get_ifd(0x8825)


def get_geotagging(exif):
    if not exif:
        return None
    gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']
    geo_tagging_info = {}
    for k, v in exif.items():
        try:
            geo_tagging_info[gps_keys[k]] = str(v)
        except IndexError:
            pass
    return geo_tagging_info


def get_all_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif()


def get_asset_table_name(db_path):
    if does_table_exist_in_db(db_path, 'ZASSET'):
        return 'ZASSET'
    if does_table_exist_in_db(db_path, 'ZGENERICASSET'):
        return 'ZGENERICASSET'
    return None


def _build_query(asset_table, has_creator):
    creator = 'ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID' if has_creator else "'' as Placeholder_CreatorID"
    join = (f'INNER JOIN ZADDITIONALASSETATTRIBUTES ON {asset_table}.Z_PK = ZADDITIONALASSETATTRIBUTES.Z_PK'
            if has_creator else '')
    return f'''
    SELECT
        DATETIME({asset_table}.ZDATECREATED+978307200,'UNIXEPOCH'),
        DATETIME({asset_table}.ZMODIFICATIONDATE+978307200,'UNIXEPOCH'),
        {asset_table}.ZDIRECTORY,
        {asset_table}.ZFILENAME,
        {asset_table}.ZLATITUDE,
        {asset_table}.ZLONGITUDE,
        {creator}
    FROM {asset_table}
    {join}
    '''


def _exif_to_decimal(results, ref_key, val_key):
    """Convert an EXIF GPS DMS value to a signed decimal degree."""
    direction = results[ref_key]
    parts = results[val_key].replace('(', '').replace(')', '').split(', ')
    decimal = float(parts[0]) + float(parts[1]) / 60 + float(parts[2]) / (60 * 60)
    return decimal * (-1 if direction in ['W', 'S'] else 1)


def _infer_tz_offset(db_iso_utc, creationchanged):
    """Find the timezone whose local time matches the EXIF Creation/Changed time.

    Returns (creationchanged_normalized, same_time_flag, offset).
    """
    mytz = pytz.timezone('UTC')
    dbdate = mytz.normalize(mytz.localize(datetime.fromisoformat(db_iso_utc), is_dst=True))
    exifdate = creationchanged.replace(':', '-', 2)
    creationchanged = exifdate
    exifdate = exifdate[:-1]

    time_list = [(str(dbdate.astimezone(pytz.timezone(tz))), tz) for tz in pytz.all_timezones]
    responsive = ''
    suspecttime = 'False'
    for date in time_list:
        if exifdate in date[0]:
            responsive, suspecttime = date[0], 'True'
            break
        if exifdate[:-1] in date[0][:-7]:
            responsive, suspecttime = date[0], 'True'
            break
        if exifdate[:-2] in date[0][:-8]:
            responsive, suspecttime = date[0], 'True'
            break
        responsive, suspecttime = '', 'False'
    offset = responsive[-6:] if responsive else ''
    return creationchanged, suspecttime, offset


@artifact_processor
def photosDbexif(context):
    data_headers = (
        ('Media', 'media'), 'Same Timestamps?', 'Possible Exif Offset', 'Same Coordinates?',
        ('Timestamp', 'datetime'), ('Timestamp Modification', 'datetime'), 'Directory', 'Filename',
        'Latitude DB', 'Longitude DB', 'Exif Creation/Changed', 'Latitude', 'Longitude', 'Exif',
        'Bundle Creator')
    data_list = []
    sources = []
    files_found = [str(f) for f in context.get_files_found()]

    for file_found in files_found:
        if not os.path.basename(file_found).endswith('.sqlite'):
            continue

        asset_table = get_asset_table_name(file_found)
        if not asset_table:
            logfunc("INFO: No asset table (ZASSET or ZGENERICASSET) found. Skipping Photos.sqlite Analysis.")
            continue

        has_creator = does_column_exist_in_db(file_found, 'ZADDITIONALASSETATTRIBUTES', 'ZCREATORBUNDLEID')
        try:
            rows = get_sqlite_db_records(file_found, _build_query(asset_table, has_creator))
        except sqlite3.Error as ex:
            logfunc(f'Error processing Photos.sqlite Analysis: {ex}')
            continue

        for row in rows:
            zdatecreated, zmodificationdate, zdirectory, zfilename, zlatitude, zlongitude, zbundlecreator = row
            if not zdirectory:
                continue
            pathingval = zdirectory.split('/')

            for search in files_found:
                searchbase = os.path.basename(search)
                if not (len(pathingval) > 1 and pathingval[0] in search
                        and pathingval[1] in search and zfilename and zfilename in search):
                    continue

                thumb = suspecttime = suspectcoordinates = creationchanged = ''
                latitude = longitude = exifdata = offset = ''

                if search.endswith('HEIC'):
                    register_heif_opener()
                    try:
                        with io.BytesIO() as buf:
                            Image.open(search).save(buf, format='JPEG')
                            thumb = check_in_embedded_media(search, buf.getvalue(), f'{searchbase}.jpg',
                                                            force_type='image/jpeg', force_extension='jpg')
                    except _EXIF_ERRORS as ex:
                        logfunc(f'Error converting HEIC thumbnail on {search}: {ex}')
                elif search.endswith(('JPG', 'PNG', 'JPEG')):
                    thumb = check_in_media(search)

                if search.endswith(('JPG', 'PNG', 'JPEG', 'HEIC')):
                    try:
                        results = get_geotagging(get_exif(search))
                        if results is not None:
                            latitude = _exif_to_decimal(results, 'GPSLatitudeRef', 'GPSLatitude')
                            longitude = _exif_to_decimal(results, 'GPSLongitudeRef', 'GPSLongitude')

                        exifall = get_all_exif(search)
                        tags = {271: 'Manufacturer', 272: 'Model', 305: 'Software', 274: 'Orientation',
                                306: 'Creation/Changed', 282: 'Resolution X', 283: 'Resolution Y',
                                316: 'Host device'}
                        for x, y in exifall.items():
                            exifdata += f'{tags.get(x, x)}: {y}\n'
                            if x == 306:
                                creationchanged = y

                        if isinstance(zlatitude, float) and isinstance(latitude, float) \
                                and isinstance(zlongitude, float) and isinstance(longitude, float):
                            suspectcoordinates = ('True' if isclose(zlatitude, latitude)
                                                  and isclose(zlongitude, longitude) else 'False')

                        if creationchanged != '':
                            creationchanged, suspecttime, offset = _infer_tz_offset(zdatecreated, creationchanged)
                    except _EXIF_ERRORS as ex:
                        logfunc(f'Error getting exif on: {search}: {ex}')

                    data_list.append((thumb, suspecttime, offset, suspectcoordinates, zdatecreated,
                                      zmodificationdate, zdirectory, zfilename, zlatitude, zlongitude,
                                      creationchanged, latitude, longitude, exifdata, zbundlecreator))

        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
