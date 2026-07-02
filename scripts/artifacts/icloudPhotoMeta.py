__artifacts_v2__ = {
    "icloudPhotoMeta": {
        "name": "iCloud Photos Metadata",
        "description": "Parses photo metadata returned by iCloud (cloudphotolibrary Metadata.txt), "
                       "including decoded filenames, timestamps, GPS and embedded EXIF/TIFF.",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iCloud",
        "notes": "The full decoded media-metadata bplist for each record is written to the "
                 "report folder's 'bplists' subfolder.",
        "paths": ('*/cloudphotolibrary/Metadata.txt',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "photo"
    }
}

import base64
import datetime
import json
import os
import plistlib

from scripts.ilapfuncs import artifact_processor, logfunc


def _convert_cloudkit_ts(value):
    """CloudKit ms/microsecond epoch -> aware UTC datetime; '' for empty/non-positive."""
    if not value:
        return ''
    text = str(value)
    factor = 1000000 if len(text) == 16 else 1000
    try:
        ts = int(text)
    except (ValueError, TypeError):
        return ''
    if ts <= 0:
        return ''
    return datetime.datetime.fromtimestamp(ts / factor, tz=datetime.timezone.utc)


@artifact_processor
def icloudPhotoMeta(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Row ID', 'Record Type', 'Decoded', 'Title', 'Original Filesize',
        'Latitude', 'Longitude', 'Altitude', 'GPS Datestamp', 'GPS Time', ('Added Date', 'datetime'),
        'Timezone Offset', 'Decoded TZ', 'Is Deleted?', 'Is Expunged?', ('Import Date', 'datetime'),
        ('Modification Date', 'datetime'), 'Res Original Filesize', 'ID', 'TIFF', 'EXIF')
    data_list = []
    sources = []

    bplist_folder = os.path.join(context.get_report_folder(), "bplists")
    os.makedirs(bplist_folder, exist_ok=True)

    for file_found in context.get_files_found():
        file_found = str(file_found)
        try:
            with open(file_found, "r", encoding="utf-8") as filecontent:
                lines = filecontent.readlines()
        except OSError as ex:
            logfunc(f'Failed to read iCloud photo metadata {file_found}: {ex}')
            continue

        rel = context.get_relative_path(file_found)
        for line in lines:
            try:
                jsonconv = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(jsonconv, dict):
                jsonconv = jsonconv.get('results', [])

            for i, record in enumerate(jsonconv):
                created_timestamp = ''
                latitude = longitude = altitude = datestamp = timestamp = ''
                decoded = decoded_tz = title = ''
                is_deleted = is_expunged = org_filesize = res_org_filesize = ''
                rec_mod_date = import_date = added_date = timezoneoffse = ''
                tiff = exif = ''
                rowid = str(i)
                rec_id = record.get('id', '')
                recordtype = record.get('recordType', '')

                if record.get('created'):
                    created_timestamp = _convert_cloudkit_ts(record['created'].get('timestamp', ''))

                fields = record.get('fields')
                if fields:
                    decoded = base64.b64decode(fields.get('filenameEnc', '')).decode(errors='replace')
                    decoded_tz = base64.b64decode(fields.get('timeZoneNameEnc', '')).decode(errors='replace')
                    is_deleted = fields.get('isDeleted', '')
                    is_expunged = fields.get('isExpunged', '')
                    org_filesize = fields.get('resOriginalFileSize', '')
                    res_org_filesize = fields.get('resOriginalFileSize', '')

                    if fields.get('originalCreationDate', ''):
                        created_timestamp = _convert_cloudkit_ts(fields.get('originalCreationDate', ''))
                    rec_mod_date = _convert_cloudkit_ts(fields.get('recordModificationDate', ''))
                    import_date = _convert_cloudkit_ts(fields.get('importDate', ''))
                    added_date = _convert_cloudkit_ts(fields.get('addedDate', ''))
                    timezoneoffse = fields.get('timeZoneOffse', '')
                    title = base64.b64decode(fields.get('title', '')).decode(errors='replace')

                    coded_bplist = fields.get('mediaMetaDataEnc')
                    if coded_bplist is not None:
                        decoded_bplist = base64.b64decode(coded_bplist)
                        with open(os.path.join(bplist_folder, rowid + ".bplist"), 'wb') as g:
                            g.write(decoded_bplist)
                        try:
                            pl = plistlib.loads(decoded_bplist)
                        except (plistlib.InvalidFileException, ValueError):
                            pl = {}
                        if pl.get('{TIFF}'):
                            tiff = str(pl.get('{TIFF}'))
                            exif = str(pl.get('{Exif}'))
                            gps = pl.get('{GPS}')
                            if gps is not None:
                                latitude = gps.get('Latitude')
                                longitude = gps.get('Longitude')
                                altitude = gps.get('Altitude')
                                datestamp = gps.get('DateStamp')
                                timestamp = gps.get('TimeStamp')

                data_list.append((created_timestamp, rowid, recordtype, decoded, title, org_filesize,
                                  latitude, longitude, altitude, datestamp, timestamp, added_date,
                                  timezoneoffse, decoded_tz, is_deleted, is_expunged, import_date,
                                  rec_mod_date, res_org_filesize, rec_id, tiff, exif))
        sources.append(rel)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
