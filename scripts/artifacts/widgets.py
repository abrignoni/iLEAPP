__artifacts_v2__ = {
    "widgets": {
        "name": "Widgets",
        "description": "Snapshot images from the com.apple.chrono snapshot-cache folder. Dates "
                       "and times shown are from file modified timestamps",
        "author": "@maala-nfi, @AlexisBrignoni",
        "creation_date": "2026-06-18",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Each .snapshot file under com.apple.chrono/snapshot-cache that decodes as a KTX "
                 "image is converted to PNG and shown; files that do not decode are not listed. "
                 "In the 12 tested extractions every snapshot sat two folders below snapshot-cache. "
                 "Both folder names are reported as found in the extraction. Widget Extension Bundle "
                 "ID is the first folder, and the label rests on this match: in those 12 extractions "
                 "(iOS 15 to 18), 81 of its 86 distinct values (counted per extraction) matched the "
                 "CFBundleIdentifier of a WidgetKit extension (NSExtensionPointIdentifier "
                 "com.apple.widgetkit-extension) in the same extraction, and each of those began "
                 "with the bundle identifier of the app that holds the extension; for the other 5, "
                 "no .appex Info.plist in the extraction carried that CFBundleIdentifier. Snapshot "
                 "Folder is the second folder. On some rows it equals the bundle identifier of an "
                 "app or extension in the same extraction, on others a dotted identifier not found "
                 "there, and on others a single word. Its meaning is not established. Date Modified "
                 "is the modified time recorded for the snapshot file when it was checked in as "
                 "media.",
        "paths": ('*/Library/Caches/com.apple.chrono/snapshot-cache/*/*/*.snapshot',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 24 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 11 rows",
            "iphone11_ios17": "iOS 17.3 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 10 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 12 rows",
            "abe_ios16": "iOS 16.5 | 16 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 10 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
        }
    },
}

from pathlib import Path, PurePosixPath

from PIL import Image
from scripts.ktx.ios_ktx2png import KTX_reader
from scripts.ilapfuncs import artifact_processor, check_in_media, lava_get_full_media_info, logfunc, convert_unix_ts_to_utc


def save_ktx_to_png_if_valid(ktx_path, save_to_path):
    '''Convert a valid iOS KTX image to PNG.'''

    with open(ktx_path, 'rb') as f:
        ktx = KTX_reader()
        try:
            if ktx.validate_header(f):
                data = ktx.get_uncompressed_texture_data(f)
                dec_img = Image.frombytes(
                    'RGBA', (ktx.pixelWidth, ktx.pixelHeight), data, 'astc', (4, 4, False))

                dec_img.save(save_to_path, "PNG", compress_type=3)

                return True
        except (OSError, ValueError) as ex:
            logfunc(f'Had an exception - {str(ex)}')
    return False


def _cache_folders(source_path):
    """Return the two folder names below snapshot-cache, as stored.

    source_path is the evidence-relative path, so a folder of the examiner's that
    happens to be named snapshot-cache cannot be read as the cache."""

    parts = PurePosixPath(str(source_path).replace('\\', '/')).parts
    positions = [idx for idx, part in enumerate(parts) if part == 'snapshot-cache']
    if not positions:
        return '', ''
    below = parts[positions[-1] + 1:-1]
    extension_id = below[0] if below else ''
    snapshot_folder = below[1] if len(below) > 1 else ''
    return extension_id, snapshot_folder


@artifact_processor
def widgets(context):
    data_list = []
    source_dirs = set()

    for file_found in context.get_files_found():
        media_path = Path(file_found)
        source_path = context.get_relative_path(file_found)
        extension_id, snapshot_folder = _cache_folders(source_path)

        png_path = media_path.with_suffix((".png"))
        if save_ktx_to_png_if_valid(media_path, png_path):
            media_item = check_in_media(
                file_found, extension_id, png_path, force_type='image/png', force_extension='png')
        else:
            continue

        if not media_item:
            continue

        source_dirs.add(str(media_path.parent))
        last_modified_date = convert_unix_ts_to_utc(
            lava_get_full_media_info(media_item)[-2])
        data_list.append(
            [last_modified_date, extension_id, snapshot_folder, source_path, media_item])

    data_headers = (('Date Modified', 'datetime'), 'Widget Extension Bundle ID', 'Snapshot Folder',
                    'Source Path', ('Snapshot', 'media'))

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
