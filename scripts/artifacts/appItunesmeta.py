__artifacts_v2__ = {
    "get_appItunesmeta": {
        "name": "Apps - Itunes Metadata",
        "description": "iTunes & Bundle ID Metadata contents for apps",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-04",
        "last_update_date": "2024-10-17",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/iTunesMetadata.plist', '*/BundleMetadata.plist',),
        "output_types": "standard"
    }
}

import biplist
import pathlib
import os
import nska_deserialize as nd
import plistlib
import sys
from datetime import *

#from scripts.artifact_report import ArtifactHtmlReport
#from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows
from scripts.ilapfuncs import artifact_processor, convert_time_obj_to_utc, convert_plist_date_to_utc
from scripts.context import Context

@artifact_processor
def get_appItunesmeta(context:Context):
    data_list = []       
    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('iTunesMetadata.plist'):
            with open(file_found, "rb") as fp:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(fp)
                else:
                    plist = biplist.readPlist(fp)
                
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
                    with open(itunes_metadata_path, 'rb') as f:
                        deserialized_plist = nd.deserialize_plist(f)
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
    return data_headers, data_list, ''
        


    