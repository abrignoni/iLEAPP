__artifacts_v2__ = {
    "iTunesBackupInfo": {
        "name": "iTunes Backup Information",
        "description": "Extract information from the Info.plist file of an iTunes backup",
        "author": "@AlexisBrignoni - @johannplw",
        "version": "0.1",
        "date": "2023-10-11",
        "requirements": "none",
        "category": "Device Info",
        "notes": "",
        "paths": ('*Info.plist',),
        "function": "get_iTunesBackupInfo"
    }
}

import datetime
import plistlib
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_iTunesMetadata(applications):
    app_list=[]
    
    for bundle_id, app_data in applications.items():
        apple_id = ''
        purchase_date = ''
        if 'iTunesMetadata' in app_data.keys():
            itunes_metadata = plistlib.loads(app_data['iTunesMetadata'])
            item_name = itunes_metadata.get('itemName', '')
            artist_name = itunes_metadata.get('artistName', '')
            version = itunes_metadata.get('bundleShortVersionString', '')
            genre = itunes_metadata.get('genre', '')
            store_cohort = itunes_metadata.get('storeCohort', '')
            if 'date=' in store_cohort:
                date_start = store_cohort.find('date=') + 5
                unix_install_timestamp = store_cohort[date_start:date_start + 10]
                install_date = datetime.datetime.fromtimestamp(int(unix_install_timestamp)).strftime('%Y-%m-%d')
            download_info = itunes_metadata.get('com.apple.iTunesStore.downloadInfo', '')
            if download_info:
                account_info = download_info.get('accountInfo', '')
                if account_info:
                    apple_id = account_info.get('AppleID')
                purchase_date = download_info.get('purchaseDate', '')
                if purchase_date:
                    purchase_date = purchase_date[:-1].replace('T', ' ')
            release_date = itunes_metadata.get('releaseDate', '')
            source_app = itunes_metadata.get('sourceApp', '')
            auto_download = itunes_metadata.get('is-auto-download', '')
            purchased_redownload = itunes_metadata.get('is-purchased-redownload', '')
            factory_install = itunes_metadata.get('isFactoryInstall', '')
            side_loaded = itunes_metadata.get('sideLoadedDeviceBasedVPP', '')
            game_center_enabled = itunes_metadata.get('gameCenterEnabled', '')
            game_center_ever_enabled = itunes_metadata.get('gameCenterEverEnabled', '')
            messages_extension = itunes_metadata.get('hasMessagesExtension', '')
            app_list.append((bundle_id, item_name, artist_name, version, genre, 
                            install_date, apple_id, purchase_date, release_date, 
                            source_app, auto_download, purchased_redownload, 
                            factory_install, side_loaded, game_center_enabled, 
                            game_center_ever_enabled, messages_extension))
        elif 'info_plist_bundle_id' in app_data.keys():
            app_info = (bundle_id, )
            app_info += ('',) * 16
            app_list.append(app_info)
    
    return app_list


def get_iTunesBackupInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    apps_iTunesMetadata = []
    installed_apps = None
    apps = None

    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, datetime.datetime):
                data_list.append((key, val))
                if key == ('Product Version'):
                    scripts.artifacts.artGlobals.versionf = val
                    logfunc(f"iOS version: {val}")

            elif key == "Applications":
                apps = val

            elif key == "Installed Applications":
                installed_apps = set(val)

    if installed_apps and apps:
        apps_bundle_ids = set(apps)
        if len(installed_apps) > len(apps_bundle_ids):
            installed_apps = installed_apps.symmetric_difference(apps_bundle_ids)
            for installed_app in installed_apps:
                apps[installed_app] = {'info_plist_bundle_id': installed_app}
        apps_iTunesMetadata = get_iTunesMetadata(apps)
    elif installed_apps:
        data_list.append(("Installed Applications", ', '.join(installed_apps)))


    keys = [data[0] for data in data_list]
    device_info = ('Product Name', 'Product Type', 'Device Name', 'Product Version', 'Build Version', 
                   'Serial Number', 'MEID', 'IMEI', 'IMEI 2', 'ICCID', 'Phone Number', 
                   'Unique Identifier', 'Last Backup Date')
    for info in device_info:
        if info in keys:
            index = keys.index(info)
            info_key = data_list[index][0]
            value_key = data_list[index][1]
            logdevinfo(f"{info_key}: {value_key}")

    report = ArtifactHtmlReport('iTunes Backup')
    report.start_artifact_report(report_folder, 'iTunes Backup Information')
    report.add_script()
    data_headers = ('Key','Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'iTunes Backup'
    tsv(report_folder, data_headers, data_list, tsvname)

    if apps_iTunesMetadata:
        report = ArtifactHtmlReport('iTunes Backup - Installed Applications')
        report.start_artifact_report(report_folder, 'iTunes Backup Installed Applications')
        report.add_script()
        data_headers = ('Bundle ID', 'Item Name', 'Artist Name', 'Version', 
                        'Genre', 'Install Date', 'Downloaded by', 'Purchase Date', 
                        'Release Date', 'Source App', 'Auto Download', 
                        'Purchased Redownload', 'Factory Install', 'Side Loaded', 
                        'Game Center Enabled', 'Game Center Ever Enabled', 
                        'Messages Extension')
        report.write_artifact_data_table(data_headers, apps_iTunesMetadata, file_found)
        report.end_artifact_report()

