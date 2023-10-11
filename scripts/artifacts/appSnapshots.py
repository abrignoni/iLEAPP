import datetime
import os
import shutil

from html import escape
from PIL import Image
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows
from scripts.ktx.ios_ktx2png import KTX_reader, liblzfse
from urllib.parse import quote

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

def get_applicationSnapshots(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    slash = '\\' if is_platform_windows() else '/'
    data_headers = ('Date Modified', 'App Name', 'Source Path', 'Snapshot')
    data_list = [] # Format=  [ [ 'App Name', 'ktx_path', mod_date, 'png_path' ], .. ]

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if file_found.lower().endswith('.ktx'):
            if os.path.getsize(file_found) < 2500: # too small, they are blank
                continue
            parts = file_found.split(slash)
            if parts[-2] != 'downscaled':
                app_name = parts[-2].split(' ')[0]
            else:
                app_name = parts[-3].split(' ')[0]

            png_path = os.path.join(report_folder, app_name + '_' + parts[-1][:-4] + '.png')
            if save_ktx_to_png_if_valid(file_found, png_path):
                last_modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_found))
                data_list.append([last_modified_date, app_name, file_found, png_path])

        elif file_found.lower().endswith('.jpeg'):
            parts = file_found.split(slash)
            if parts[-2] != 'downscaled':
                app_name = parts[-2].split(' ')[0]
            else:
                app_name = parts[-3].split(' ')[0]
            if app_name.startswith('sceneID'):
                app_name = app_name[8:]
            #if app_name.endswith('-default'):
            #    app_name = app_name[:-8]
            dash_pos = app_name.find('-') 
            if dash_pos > 0:
                app_name = app_name[0:dash_pos]

            jpg_path = os.path.join(report_folder, app_name + '_' + parts[-1])
            if shutil.copy2(file_found, jpg_path):
                last_modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_found))
                data_list.append([last_modified_date, app_name, file_found, jpg_path])
    
    if len(data_list):
        description = "Snapshots saved by iOS for individual apps appear here. Blank screenshots are excluded here. Dates and times shown are from file modified timestamps"
        report = ArtifactHtmlReport('App Snapshots (screenshots)')
        report.start_artifact_report(report_folder, 'App Snapshots', description)
        report.add_script()
        report_folder_name = os.path.basename(report_folder.rstrip(slash))
        data_list_for_report = []
        for mod_date, app_name, ktx_path, png_path in data_list:
            dir_path, base_name = os.path.split(png_path)
            img_html = '<a href="{1}/{0}"><img src="{1}/{0}" class="img-fluid" style="max-height:300px; max-width:400px"></a>'.format(quote(base_name), quote(report_folder_name))
            data_list_for_report.append(( mod_date, escape(app_name), escape(ktx_path), img_html) )
        report.write_artifact_data_table(data_headers, data_list_for_report, '', html_escape=False, write_location=False)
        report.end_artifact_report()

        tsvname = 'App Snapshots'
        tsv_headers = ('Date Modified', 'App Name', 'Source Path')
        tsv(report_folder, tsv_headers, data_list, tsvname)
        
        tlactivity = 'App Snapshots'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No snapshots available')

__artifacts__ = {
    "applicationsnapshots": (
        "Installed Apps",
        ('**/Library/Caches/Snapshots/*', '**/SplashBoard/Snapshots/*'),
        get_applicationSnapshots)
}