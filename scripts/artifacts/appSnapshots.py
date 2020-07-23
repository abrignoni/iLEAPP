import os

from PIL import Image
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows
from scripts.ktx.ios_ktx2png import KTX_reader, liblzfse

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
                    
                dec_img.save(save_to_path, "PNG")
                return True
        except (OSError, ValueError, liblzfse.error) as ex:
            logfunc(f'Had an exception - {str(ex)}')
    return False

def get_applicationSnapshots(files_found, report_folder, seeker):
    
    slash = '\\' if is_platform_windows() else '/'
    data_headers = ('App Name', 'Source Path', 'Snapshot')
    data_list = [] # Format=  [ [ 'App Name', 'ktx_path', 'png_path' ], .. ]

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
                data_list.append([app_name, file_found, png_path])
    
    if len(data_list):
        description = "Snapshots saved by iOS for individual apps appear here. Blank screenshots are excluded here."
        report = ArtifactHtmlReport('App Snapshots (screenshots)')
        report.start_artifact_report(report_folder, 'App Screenshots', description)
        report.add_script()
        report_folder_name = os.path.basename(report_folder.rstrip(slash))
        data_list_for_report = []
        for app_name, ktx_path, png_path in data_list:
            dir_path, base_name = os.path.split(png_path)
            img_html = '<a href="{1}/{0}"><img src="{1}/{0}" class="img-fluid" style="max-height:300px; max-width:300px"></a>'.format(base_name, report_folder_name)
            data_list_for_report.append( (app_name, ktx_path, img_html) )
        report.write_artifact_data_table(data_headers, data_list_for_report, '', html_escape=False, write_location=False)
        report.end_artifact_report()

        tsvname = 'App Snapshots'
        tsv_headers = ('App Name', 'Source Path')
        tsv(report_folder, tsv_headers, data_list, tsvname)
    else:
        logfunc('No snapshots available')
    return