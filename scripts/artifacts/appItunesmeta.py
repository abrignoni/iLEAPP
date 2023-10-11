import biplist
import pathlib
import os
import nska_deserialize as nd
import plistlib
import sys

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows


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
                bundleid = plist.get('softwareVersionBundleId', '')
                itemname = plist.get('itemName', '')
                artistname = plist.get('artistName', '')
                versionnum = plist.get('bundleShortVersionString', '')
                downloadedby = plist.get('com.apple.iTunesStore.downloadInfo', {}) .get('accountInfo', {}).get('AppleID', '')
                genre = plist.get('genre', '')
                factoryinstall = plist.get('isFactoryInstall', '')
                appreleasedate = plist.get('releaseDate', '')
                sourceapp = plist.get('sourceApp', '')
                sideloaded = plist.get('sideLoadedDeviceBasedVPP', '')
                variantid = plist.get('variantID', '')
                
                p = pathlib.Path(file_found)
                parent = p.parent

                itunes_metadata_path = (os.path.join(parent, "BundleMetadata.plist"))
                if os.path.exists(itunes_metadata_path):
                    with open(itunes_metadata_path, 'rb') as f:
                        deserialized_plist = nd.deserialize_plist(f)
                        install_date = deserialized_plist.get('installDate', '')
                else:
                    install_date = ''
        
                data_list.append((install_date, purchasedate, bundleid, itemname, artistname, versionnum, downloadedby, genre, factoryinstall, appreleasedate, sourceapp, sideloaded, variantid, parent))   

    if len(data_list) > 0:
        fileloc = 'See source file location column'
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

__artifacts__ = {
    "appitunesmeta": (
        "Installed Apps",
        ('**/iTunesMetadata.plist', '**/BundleMetadata.plist'),
        get_appItunesmeta)
}

    