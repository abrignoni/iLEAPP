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
        "output_types": "standard",
        "artifact_icon": "apps",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 53 rows",
            "dexter_ios18": "iOS 18.3.2 | 49 rows",
            "felix_ios17": "iOS 17.6.1 | 32 rows",
            "fsfull002_ios17": "iOS 17.1 | 47 rows",
            "hc_ios18_7": "iOS 18.7.8 | 30 rows",
            "iphone11_ios17": "iOS 17.3 | 57 rows",
            "iphone12_ios18": "iOS 18.7 | 45 rows",
            "iphone14plus_ios18": "iOS 18.0 | 17 rows",
            "otto_ios17": "iOS 17.5.1 | 45 rows",
        }
    }
}

import pathlib
import os
from datetime import datetime
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
            # purchaseDate may be a plist <date> object or an ISO string; only convert objects
            if isinstance(purchasedate, datetime):
                purchasedate = convert_plist_date_to_utc(purchasedate)
            
            bundleid = plist.get('softwareVersionBundleId', '')
            itemname = plist.get('itemName', '')
            artistname = plist.get('artistName', '')
            versionnum = plist.get('bundleShortVersionString', '')
            downloadedby = plist.get('com.apple.iTunesStore.downloadInfo', {}) .get('accountInfo', {}).get('AppleID', '')
            genre = plist.get('genre', '')
            factoryinstall = plist.get('isFactoryInstall', '')
            appreleasedate = plist.get('releaseDate', '')
            if isinstance(appreleasedate, datetime):
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
                    if isinstance(install_date, datetime):
                        install_date = convert_time_obj_to_utc(install_date)
            else:
                install_date = ''
    
            data_list.append((install_date, purchasedate, bundleid, itemname, artistname, versionnum, downloadedby, genre, factoryinstall, appreleasedate, sourceapp, sideloaded, variantid, context.get_relative_path(parent)))   

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
        


    