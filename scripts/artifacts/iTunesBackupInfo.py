""" See artifact description below """

__artifacts_v2__ = {
    "itunes_backup_info": {
        "name": "iTunes Backup Information",
        "description": "Extract information from the Info.plist file of an iTunes backup",
        "author": "@AlexisBrignoni - @johannplw",
        "creation_date": "2023-10-11",
        "last_update_date": "2025-10-14",
        "requirements": "none",
        "category": "iTunes Backup",
        "notes": "",
        "paths": ("info.plist",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "refresh-cw"
    },
    "itunes_backup_installed_applications": {
        "name": "iTunes Backup - Installed Applications",
        "description": "Extract information about installed applications from the "
                       "Info.plist file of an iTunes backup",
        "author": "@johannplw",
        "creation_date": "2023-10-11",
        "last_update_date": "2025-10-14",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ("info.plist",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package"
    }
}


import datetime
import plistlib
from scripts.ilapfuncs import artifact_processor, get_plist_file_content, \
    check_in_embedded_media, device_info, logfunc, iOS


@artifact_processor
def itunes_backup_info(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Info.plist')
    data_list = []
    installed_apps = None
    apps = None

    pl = get_plist_file_content(data_source)
    for key, val in pl.items():
        if isinstance(val, str) or isinstance(val, int) or isinstance(val, datetime.datetime):
            data_list.append((key, val))
            if key == ('Product Version'):
                iOS.set_version(val)
                context.set_installed_os_version(val)
                logfunc(f"iOS version: {val}")
        elif key == "Applications":
            apps = val
        elif key == "Installed Applications":
            installed_apps = set(val)

    if not installed_apps and apps:
        data_list.append(("Installed Applications", ', '.join(installed_apps)))

    # Device details
    keys = [data[0] for data in data_list]
    dev_info = ('Product Name', 'Product Type', 'Device Name', 'Product Version',
                'Build Version', 'Serial Number', 'MEID', 'IMEI', 'IMEI 2', 'ICCID',
                'Phone Number', 'Unique Identifier', 'Last Backup Date')
    for info in dev_info:
        if info in keys:
            index = keys.index(info)
            info_key = data_list[index][0]
            value_key = data_list[index][1]
            device_info("iTunes Backup Information", info_key, value_key, data_source)

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, data_source


@artifact_processor
def itunes_backup_installed_applications(context):
    """ See artifact description """
    data_source = context.get_source_file_path('Info.plist')
    data_list = []
    installed_apps = None
    apps = None

    pl = get_plist_file_content(data_source)
    for key, val in pl.items():
        if key == "Applications":
            apps = val
        if key == "Installed Applications":
            installed_apps = set(val)

    if installed_apps and apps:
        apps_bundle_ids = set(apps)
        if len(installed_apps) > len(apps_bundle_ids):
            installed_apps = installed_apps.symmetric_difference(apps_bundle_ids)
            for installed_app in installed_apps:
                apps[installed_app] = {'info_plist_bundle_id': installed_app}
        for bundle_id, app_data in apps.items():
            install_date = ''
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
                icon = app_data.get('PlaceholderIcon', '')
                if icon:
                    icon_item = check_in_embedded_media(data_source, icon, item_name)
                else:
                    icon_item = ''

                data_list.append((bundle_id, icon_item, item_name, artist_name,
                                  version, genre, install_date, apple_id, purchase_date,
                                  release_date, source_app, auto_download, purchased_redownload,
                                  factory_install, side_loaded, game_center_enabled,
                                  game_center_ever_enabled, messages_extension))
            elif 'info_plist_bundle_id' in app_data.keys():
                app_info = (bundle_id, )
                app_info += ('',) * 17
                data_list.append(app_info)

    data_headers = ('Bundle ID', ('App Icon', 'media', 'width: 60px;'), 'Item Name',
                    'Artist Name', 'Version', 'Genre', ('Install Date', 'date'),
                    'Downloaded by', ('Purchase Date', 'datetime'),
                    ('Release Date', 'datetime'), 'Source App', 'Auto Download',
                    'Purchased Redownload', 'Factory Install', 'Side Loaded',
                    'Game Center Enabled', 'Game Center Ever Enabled',
                    'Messages Extension')

    return data_headers, data_list, data_source
