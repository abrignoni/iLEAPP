__artifacts_v2__ = {
    "widgets": {
        "name": "Widgets",
        "description": "Snapshots of widgets saved by iOS appear here. \
            Dates and times shown are from file modified timestamps",
        "author": "@maala-nfi",
        "date": "2026-06-18",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Most code copied from appSnapshots.py",
        "paths": ('*/Library/Caches/com.apple.chrono/snapshot-cache/*/*/*.snapshot',),
        "output_types": "standard",
        "artifact_icon": "package"
    },
}

from pathlib import Path

from PIL import Image
from scripts.ktx.ios_ktx2png import KTX_reader
from scripts.ilapfuncs import artifact_processor, check_in_media, lava_get_full_media_info, logfunc, convert_unix_ts_to_utc


def save_ktx_to_png_if_valid(ktx_path, save_to_path):
    '''Excludes all white or all black blank images'''

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


@artifact_processor
def widgets(context):
    data_list = []

    for file_found in context.get_files_found():
        media_path = Path(file_found)
        parts = media_path.parts
        if parts[-2] != 'downscaled':
            app_name = parts[-2].split(' ')[0].replace("sceneID:", "")
        else:
            app_name = parts[-3].split(' ')[0].replace("sceneID:", "")
        dash_pos = app_name.find('-')
        if dash_pos > 0:
            app_name = app_name[0:dash_pos]

        png_path = media_path.with_suffix((".png"))
        if save_ktx_to_png_if_valid(media_path, png_path):
            media_item = check_in_media(file_found, app_name, png_path)
            print(f"file_found = [{file_found}], media_item = [{media_item}]")
        else:
            continue

        if not media_item:
            continue

        last_modified_date = convert_unix_ts_to_utc(
            lava_get_full_media_info(media_item)[-2])
        data_list.append(
            [last_modified_date, app_name, file_found, media_item])

    data_headers = (('Date Modified', 'datetime'), 'App Name',
                    'Source Path', ('Snapshot', 'media'))

    return data_headers, data_list, 'see Source Path for more info'
