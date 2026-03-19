__artifacts_v2__ = {
    "get_appItunesmeta": {
        "name": "Apps - Itunes Metadata",
        "description": "iTunes & Bundle ID Metadata contents for apps",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-04",
        "last_update_date": "2025-12-16",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/iTunesMetadata.plist', '*/BundleMetadata.plist',),
        "output_types": "standard"
    }
}

import pathlib
import os
from scripts.ilapfuncs import artifact_processor, convert_time_obj_to_utc, convert_plist_date_to_utc, get_plist_file_content

@artifact_processor
def get_appItunesmeta(context):
    data_list = []       
    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('iTunesMetadata.plist'):
            # with open(file_found, "rb") as fp:
            #     if sys.version_info >= (3, 9):
            #         plist = plistlib.load(fp)
            #     else:
            #         plist = biplist.readPlist(fp)
            
            plist = get_plist_file_content(file_found)
            
            # Check if plist is a valid parseable object
            if not plist or not isinstance(plist, dict):
                continue
                
            purchasedate = plist.get('com.apple.iTunesStore.downloadInfo', {}).get('purchaseDate', '')
            #print(purchasedate, timezone_offset)
            purchasedate = convert_plist_date_to_utc(purchasedate)
            
            bundleid = plist.get('softwareVersionBundleId', '')
            itemname = plist.get('itemName', '')
            artistname = plist.get('artistName', '')
            versionnum = plist.get('bundleShortVersionString', '')
            downloadedby = plist.get('com.apple.iTunesStore.downloadInfo', {}) .get('accountInfo', {}).get('AppleID', '')
            genre = plist.get('genre', '')
            factoryinstall = plist.get('isFactoryInstall', '')
            appreleasedate = plist.get('releaseDate', '')
            appreleasedate = convert_plist_date_to_utc(appreleasedate)
            sourceapp = plist.get('sourceApp', '')
            sideloaded = plist.get('sideLoadedDeviceBasedVPP', '')
            variantid = plist.get('variantID', '')
            
            p = pathlib.Path(file_found)
            parent = p.parent
            parent = str(parent)

            itunes_metadata_path = (os.path.join(parent, "BundleMetadata.plist"))
            if os.path.exists(itunes_metadata_path):
                #with open(itunes_metadata_path, 'rb') as f:
                deserialized_plist = get_plist_file_content(itunes_metadata_path)
                # Check if deserialized_plist is a valid parseable object
                if not deserialized_plist or not isinstance(deserialized_plist, dict):
                    install_date = ''
                else:
                    install_date = deserialized_plist.get('installDate', '')
                    #print(install_date, type(install_date))
                    install_date = convert_time_obj_to_utc(install_date)
            else:
                install_date = ''
    
            data_list.append((install_date, purchasedate, bundleid, itemname, artistname, versionnum, downloadedby, genre, factoryinstall, appreleasedate, sourceapp, sideloaded, variantid, parent))   

    data_headers = (
        ('Installed Date','datetime'), 
        ('App Purchase Date','datetime'),
        'Bundle ID', 
        'Item Name', 
        'Artist Name', 
        'Version Number', 
        'Downloaded by', 
        'Genre', 
        'Factory Install', 
        'App Release Date', 
        'Source App', 
        'Sideloaded?', 
        'Variant ID', 
        'Source File Location')
    return data_headers, data_list, 'see Source File Location'
        


    