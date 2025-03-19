__artifacts_v2__ = {
    "applicationSnapshots": {
        "name": "App Snapshots",
        "description": "Snapshots saved by iOS for individual apps appear here. Blank screenshots are excluded here. \
            Dates and times shown are from file modified timestamps",
        "author": "@ydkhatri",
        "creation_date": "2020-07-23",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": (
            '*/Library/Caches/Snapshots/*.ktx', 
            '*/Library/Caches/Snapshots/*.jpeg', 
            '*/SplashBoard/Snapshots/*.ktx', 
            '*/SplashBoard/Snapshots/*.jpeg'),
        "output_types": "standard",
        "artifact_icon": "package"
    },
}

import inspect
import hashlib
import shutil
from pathlib import Path

from PIL import Image
from scripts.ktx.ios_ktx2png import KTX_reader, liblzfse
from scripts.ilapfuncs import artifact_processor, check_in_media, lava_get_full_media_info, logfunc, convert_unix_ts_to_utc

def save_ktx_to_png_if_valid(ktx_path, save_to_path):
    '''Excludes all white or all black blank images'''

    with open(ktx_path, 'rb') as f:
        ktx = KTX_reader()
        try:
            if ktx.validate_header(f):
                data = ktx.get_uncompressed_texture_data(f)
                dec_img = Image.frombytes('RGBA', (ktx.pixelWidth, ktx.pixelHeight), data, 'astc', (4, 4, False))
                # either all black or all white https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
                # if sum(dec_img.convert("L").getextrema()) in (0, 2):
                #     logfunc('Skipping image as it is blank')
                #     return False
                    
                dec_img.save(save_to_path, "PNG", compress_type=3)
                #                                    ^
                # as per https://github.com/python-pillow/Pillow/issues/5986

                return True
        except (OSError, ValueError, liblzfse.error) as ex:
            logfunc(f'Had an exception - {str(ex)}')
    return False

def html_path(report_folder, file_path):
    data_path = Path(report_folder).parents[1].joinpath('data')
    original_path = file_path.replace(str(data_path), '')[1:]
    return hashlib.sha1(original_path.encode()).hexdigest()

@artifact_processor
def applicationSnapshots(files_found, report_folder, seeker, wrap_text, timezone_offset):
    artifact_info = inspect.stack()[0]
    source_path = 'File path in the report below'
    data_list = []

    for file_found in files_found:
        media_path = Path(file_found)
        parts = media_path.parts
        if parts[-2] != 'downscaled':
            app_name = parts[-2].split(' ')[0].replace("sceneID:", "")
        else:
            app_name = parts[-3].split(' ')[0].replace("sceneID:", "")
        dash_pos = app_name.find('-') 
        if dash_pos > 0:
            app_name = app_name[0:dash_pos]
        if file_found.lower().endswith('.ktx'):
            if media_path.stat().st_size < 2500: # too small, they are blank
                continue
            png_path = Path(report_folder).joinpath(html_path(report_folder, file_found)).with_suffix((".png"))
            if save_ktx_to_png_if_valid(media_path, png_path):
                media_item = check_in_media(seeker, file_found, artifact_info, app_name, already_extracted=True, converted_file_path=png_path)
            else:
                continue
        else:
            jpg_path = Path(report_folder).joinpath(html_path(report_folder, file_found)).with_suffix((".jpeg"))
            try:
                shutil.copy2(file_found, jpg_path)
            except shutil.Error as e:
                logfunc(f'Could not copy media into {jpg_path}: ' + str(e))
            media_item = check_in_media(seeker, file_found, artifact_info, app_name, already_extracted=True, converted_file_path=jpg_path)
        last_modified_date = convert_unix_ts_to_utc(lava_get_full_media_info(media_item)[-1])
        data_list.append([last_modified_date, app_name, file_found, media_item])
    
    data_headers = (('Date Modified', 'datetime'), 'App Name', 'Source Path', ('Snapshot', 'media'))

    return data_headers, data_list, source_path
