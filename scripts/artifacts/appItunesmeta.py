__artifacts_v2__ = {
    "get_appItunesmeta": {
        "name": "Apps - Itunes Metadata",
        "description": "iTunes & Bundle ID Metadata contents for apps",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2020-10-04",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/iTunesMetadata.plist', '**/BundleMetadata.plist',),
        "function": "get_appItunesmeta",
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
import pytz

#from scripts.artifact_report import ArtifactHtmlReport
#from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows
from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_timezone_offset, convert_time_obj_to_utc

def convert_plist_date_to_timezone_offset_b(plist_date, timezone_offset):
    if plist_date:
        plist_date = datetime.strptime(plist_date, '%Y-%m-%dT%H:%M:%SZ')
        iso_date = plist_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return convert_ts_human_to_timezone_offset(iso_date, timezone_offset)
    else:
        return plist_date


@artifact_processor
def get_appItunesmeta(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []       
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('iTunesMetadata.plist'):
            with open(file_found, "rb") as fp:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(fp)
                else:
                    plist = biplist.readPlist(fp)
                
                purchasedate = plist.get('com.apple.iTunesStore.downloadInfo', {}).get('purchaseDate', '')
                #print(purchasedate, timezone_offset)
                purchasedate = convert_plist_date_to_timezone_offset_b(purchasedate, timezone_offset)
                
                bundleid = plist.get('softwareVersionBundleId', '')
                itemname = plist.get('itemName', '')
                artistname = plist.get('artistName', '')
                versionnum = plist.get('bundleShortVersionString', '')
                downloadedby = plist.get('com.apple.iTunesStore.downloadInfo', {}) .get('accountInfo', {}).get('AppleID', '')
                genre = plist.get('genre', '')
                factoryinstall = plist.get('isFactoryInstall', '')
                appreleasedate = plist.get('releaseDate', '')
                appreleasedate = convert_plist_date_to_timezone_offset_b(appreleasedate, timezone_offset)
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

    if len(data_list) > 0:
        fileloc = 'See source file location column'
        """
        description = 'iTunes & Bundle ID Metadata contents for apps'
        report = ArtifactHtmlReport('Apps - Itunes & Bundle Metadata')
        report.start_artifact_report(report_folder, 'Apps - Itunes Metadata', description)
        report.add_script()
        data_headers = ('Installed Date', 'App Purchase Date','Bundle ID', 'Item Name', 'Artist Name', 'Version Number', 'Downloaded by', 'Genre', 'Factory Install', 'App Release Date', 'Source App', 'Sideloaded?', 'Variant ID', 'Source File Location')     
        report.write_artifact_data_table(data_headers, data_list, fileloc)
        report.end_artifact_report()
        
        tsvname = 'Apps - Itunes Bundle Metadata'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Apps - Itunes Bundle Metadata'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data on Apps - Itunes Bundle Metadata')
        """
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
        return data_headers, data_list, fileloc
        


    