__artifacts_v2__ = {
    "icloudPhotoMeta": {
        "name": "iCloud Photos Metadata",
        "description": "Parses photo metadata returned by iCloud (cloudphotolibrary Metadata.txt), "
                       "including decoded filenames, timestamps, and the GPS, EXIF and TIFF values "
                       "of the embedded metadata as stored (latitude and longitude are reported "
                       "without their N/S and E/W reference).",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "iCloud",
        "notes": 'Each successfully base64-decoded mediaMetaDataEnc value is exported as its original decoded '
                 "bytes under the report's bplists subfolder. The export filename identifies this "
                 "invocation's input occurrence, physical text-line number and record ordinal; it is "
                 'independent of the unchanged Row ID, which restarts on each line. Exported Bplist gives '
                 'that report-relative path only after a successful write, and is blank when mediaMetaDataEnc '
                 'is absent or None. Equal bytes and repeated input paths are retained as separate '
                 'occurrences; the filename is not a persistent record identifier. An export does not '
                 "establish a valid plist or independently verify its contents. Timestamp is the record's "
                 'originalCreationDate where present and its created timestamp otherwise. The GPS, EXIF and '
                 'TIFF columns are filled only when the decoded metadata carries a {TIFF} entry. Original '
                 'contribution credited to @abrignoni. This update only prevents per-occurrence export '
                 'collisions and records the export path; coordinate/reference, TIFF gating, duplicate '
                 'filesize projection, date ordering/interpretation, source association and unsupported '
                 'input-shape policies remain unchanged and unresolved.',
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
        ('Modification Date', 'datetime'), 'Res Original Filesize', 'ID', 'TIFF', 'EXIF', 'Exported Bplist')
    data_list = []
    sources = []

    bplist_folder = os.path.join(context.get_report_folder(), "bplists")
    os.makedirs(bplist_folder, exist_ok=True)

    for input_occurrence, file_found in enumerate(context.get_files_found(), start=1):
        file_found = str(file_found)
        try:
            with open(file_found, "r", encoding="utf-8") as filecontent:
                lines = filecontent.readlines()
        except OSError as ex:
            logfunc(f'Failed to read iCloud photo metadata {file_found}: {ex}')
            continue

        rel = context.get_relative_path(file_found)
        for physical_line_number, line in enumerate(lines, start=1):
            try:
                jsonconv = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(jsonconv, dict):
                jsonconv = jsonconv.get('results', [])

            for i, record in enumerate(jsonconv):
                exported_bplist = ""
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
                        export_name = (f"input-{input_occurrence:06d}-line-{physical_line_number:06d}-"
                                       f"record-{i:06d}.bplist")
                        with open(os.path.join(bplist_folder, export_name), 'wb') as g:
                            g.write(decoded_bplist)
                        exported_bplist = "bplists/" + export_name
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
                                  rec_mod_date, res_org_filesize, rec_id, tiff, exif, exported_bplist))
        sources.append(rel)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
