__artifacts_v2__ = {
    "findMy_items": {
        "name": "Find My - Items",
        "description": "Extract Items information From Find My",
        "author": "@AlexisBrignoni",
        "version": "0.3.1",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Find My",
        "notes": "",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "none",
        "function": "findMy_items"
    }
}

import datetime
import json
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, timeline, kmlgen, lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import convert_unix_ts_to_timezone

    
def findMy_items(files_found, report_folder, seeker, wrap_text, timezone_offset):
    info_data_list = []
    safeloc_data_list = []
    location_data_list = []
    crowdloc_data_list = []

    category = "Find My"
    module_name = "findMy_items"
    
    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, mode='r', encoding="UTF-8") as f:
            deserialized = json.load(f)
            
        for x in deserialized:
            
            name = (x['name'])
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            
            gid = (x['groupIdentifier'])
            
            owner = (x.get('owner'))
            batstat = (x['batteryStatus'])
            
            serial = (x['serialNumber'])
            lostmode = (x['lostModeMetadata'])
            
            cap = (x['capabilities'])
            id = (x['identifier'])
            
            asubAdministrativeArea =  (x['address'].get('subAdministrativeArea'))
            aslabel =  (x['address'].get('label'))
            astreetAddress =  (x['address'].get('streetAddress'))
            acountryCode =  (x['address'].get('countryCode'))
            astateCode =  (x['address'].get('stateCode'))
            administrativeArea =  (x['address'].get('administrativeArea'))
            astreetName =  (x['address'].get('streetName'))
            aformattedAddressLines =  (x['address'].get('formattedAddressLines'))
            if isinstance(aformattedAddressLines, list):
                aformattedAddressLines = (', '.join(aformattedAddressLines))
            amapItemFullAddress =  (x['address'].get('mapItemFullAddress'))
            afullThroroughfare =  (x['address'].get('fullThroroughfare'))
            areaOfInterest =  (x['address'].get('areaOfInterest'))
            if isinstance(areaOfInterest, list):
                areaOfInterest = (', '.join(areaOfInterest))
            alocality =  (x['address'].get('locality'))
            acountry =  (x['address'].get('country'))
            
            lpostype = (x['location'].get('positionType'))
            lverticalAccuracy = (x['location'].get('verticalAccuracy'))
            llong = (x['location'].get('longitude'))
            lfloor = (x['location'].get('floorLevel'))
            lisin = (x['location'].get('isInaccurate'))
            lisold = (x['location'].get('isOld'))
            lhorz = (x['location'].get('horizontalAccuracy'))
            llat = (x['location'].get('latitude'))
            ltimestamp = (x['location'].get('timeStamp'))
            ltimestamp = convert_unix_ts_to_timezone(ltimestamp, timezone_offset)
            lalt = (x['location'].get('altitude'))
            lloc = (x['location'].get('locationFinished'))
            
            sysver = (x['systemVersion'])
            crowdloc = (x['crowdSourcedLocation'])
            crowdpostype = (x['crowdSourcedLocation'].get('positionType'))
            crowdvert = (x['crowdSourcedLocation'].get('verticalAccuracy'))
            crowdlong = (x['crowdSourcedLocation'].get('longitude'))
            crowdfloor = (x['crowdSourcedLocation'].get('floorLevel'))
            crowdisacc = (x['crowdSourcedLocation'].get('isInaccurate'))
            crowdisold = (x['crowdSourcedLocation'].get('isOld'))
            crowdhorzcc = (x['crowdSourcedLocation'].get('horizontalAccuracy'))
            crowdlat = (x['crowdSourcedLocation'].get('latitude'))
            crowdtimestamp= (x['crowdSourcedLocation'].get('timeStamp'))
            crowdtimestamp = convert_unix_ts_to_timezone(crowdtimestamp, timezone_offset)
            crowdalt = (x['crowdSourcedLocation'].get('altitude'))
            crowdlocfin = (x['crowdSourcedLocation'].get('locationFinished'))
            
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            
            for safeloc in x.get('safeLocations'):
                sname = (safeloc.get('name'))
                stype = (safeloc.get('type'))
                sid = (safeloc.get('identifier'))
                sva = (safeloc['location'].get('verticalAccuracy'))
                sha = (safeloc['location'].get('horizontalAccuracy'))
                slong = (safeloc['location'].get('longitude'))
                slat = (safeloc['location'].get('latitude'))
                sfloor = (safeloc['location'].get('floorLevel'))
                sisina = (safeloc['location'].get('isInaccurate'))
                sisold = (safeloc['location'].get('isOld'))
                stimestamp = (safeloc['location'].get('timeStamp'))
                stimestamp = convert_unix_ts_to_timezone(stimestamp, timezone_offset)
                salt = (safeloc['location'].get('altitude'))
                ssub = (safeloc['address'].get('subAdministrativeArea'))
                slabel = (safeloc['address'].get('label'))
                sstreet = (safeloc['address'].get('streetAddres'))
                scountry = (safeloc['address'].get('countryCode'))
                sstate = (safeloc['address'].get('stateCode'))
                sadmin = (safeloc['address'].get('administrativeArea'))
                pstreetn = (safeloc['address'].get('streetName'))
                sformated = (safeloc['address'].get('formattedAddressLines'))
                if isinstance(sformated, list):
                    sformated = (', '.join(sformated))
                smapfull = (safeloc['address'].get('mapItemFullAddress'))
                sthro = (safeloc['address'].get('fullThroroughfare'))
                saoi = (safeloc['address'].get('areaOfInterest'))
                if isinstance(saoi, list):
                    saoi = (', '.join(saoi))
                sloc = (safeloc['address'].get('locality'))
                scount = (safeloc['address'].get('country'))
                
                safeloc_data_list.append(
                    (stimestamp, name, serial, id, rname, remoji, ris, sname, stype, sid, sva, sha, 
                     slong, slat, sfloor, sisina, sisold, salt, ssub, slabel, sstreet, scountry, 
                     sstate, sadmin, pstreetn, sformated, smapfull, sthro, saoi, sloc, scount))
                
            info_data_list.append(
                (name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, 
                 batstat, lostmode, cap, sysver,))
            
            location_data_list.append(
                (ltimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, 
                 owner, batstat, lostmode, cap, sysver, asubAdministrativeArea, aslabel, astreetAddress, 
                 acountryCode, astateCode, administrativeArea, astreetName, aformattedAddressLines, 
                 amapItemFullAddress, afullThroroughfare, areaOfInterest, alocality, lpostype, lverticalAccuracy, 
                 llong, lisin, lisold, lhorz, llat, lalt, lloc, acountry))
            
            crowdloc_data_list.append((crowdtimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, 
                                       ap, gid, owner, batstat, lostmode, cap, sysver, crowdpostype, crowdvert, crowdlong, 
                                       crowdlat, crowdalt, crowdfloor, crowdisacc, crowdisold, crowdhorzcc, crowdlocfin ))

    if safeloc_data_list:
        safeloc_artifact_name = 'FindMy Items Safe Locations'
        safeloc_headers = (
            'Timestamp', 'Item Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Location Name', 'Type', 
            'Identifier', 'Vertical Accuracy', 'Horizontal Accuracy', 'Longitude', 'Latitude', 'Floor Level', 'Is Inaccurate', 
            'Is Old', 'Altitude', 'Sub-Administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 
            'Street Name', 'Formatted Address Line', 'Map Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Country')
        lava_safeloc_headers = (
            ('Timestamp', 'datetime'), 'Item Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Location Name', 'Type', 
            'Identifier', 'Vertical Accuracy', 'Horizontal Accuracy', 'Longitude', 'Latitude', 'Floor Level', 'Is Inaccurate', 
            'Is Old', 'Altitude', 'Sub-Administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 
            'Street Name', 'Formatted Address Line', 'Map Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Country')
        
        report = ArtifactHtmlReport(safeloc_artifact_name)
        report.start_artifact_report(report_folder, safeloc_artifact_name)
        report.add_script()
        report.write_artifact_data_table(safeloc_headers, safeloc_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = safeloc_artifact_name
        tsv(report_folder, safeloc_headers, safeloc_data_list, tsvname)
        
        tlactivity = safeloc_artifact_name
        timeline(report_folder, tlactivity, safeloc_data_list, safeloc_headers)
        
        kmlactivity = safeloc_artifact_name
        kmlgen(report_folder, kmlactivity, safeloc_data_list, safeloc_headers)

        safeloc_table, safeloc_columns, safeloc_column_map = lava_process_artifact(
            category, module_name, safeloc_artifact_name, lava_safeloc_headers, len(safeloc_data_list))
        lava_insert_sqlite_data(safeloc_table, safeloc_data_list, safeloc_columns, lava_safeloc_headers, safeloc_column_map)

    if location_data_list:
        location_artifact_name = 'FindMy Items Locations'
        location_headers = (
            'Timestamp', 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 
            'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version', 
            'Sub-administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 'Street Name', 
            'Formatted Address Line', 'Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Type', 'Vertical Accuracy', 
            'Longitude', 'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Latitude', 'Altitude', 'Location Finished', 'Country')
        lava_location_headers = (
            ('Timestamp', 'datetime'), 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 
            'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version', 
            'Sub-administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 'Street Name', 
            'Formatted Address Line', 'Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Type', 'Vertical Accuracy', 
            'Longitude', 'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Latitude', 'Altitude', 'Location Finished', 'Country')
        
        report = ArtifactHtmlReport(location_artifact_name)
        report.start_artifact_report(report_folder, location_artifact_name)
        report.add_script()
        report.write_artifact_data_table(location_headers, location_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = location_artifact_name
        tsv(report_folder, location_headers, location_data_list, tsvname)
        
        tlactivity = location_artifact_name
        timeline(report_folder, tlactivity, location_data_list, location_headers)
        
        kmlactivity = location_artifact_name
        kmlgen(report_folder, kmlactivity, location_data_list, location_headers)
        
        location_table, location_columns, location_column_map = lava_process_artifact(
            category, module_name, location_artifact_name, lava_location_headers, len(location_data_list))
        lava_insert_sqlite_data(location_table, location_data_list, location_columns, lava_location_headers, location_column_map)

    if info_data_list:
        info_artifact_name = 'FindMy Items Info'
        info_headers = (
            'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 
            'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version' )
        
        report = ArtifactHtmlReport(info_artifact_name)
        report.start_artifact_report(report_folder, info_artifact_name)
        report.add_script()
        report.write_artifact_data_table(info_headers, info_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = info_artifact_name
        tsv(report_folder, info_headers, info_data_list, tsvname)
        
        info_table, info_columns, info_column_map = lava_process_artifact(
            category, module_name, info_artifact_name, info_headers, len(info_data_list))
        lava_insert_sqlite_data(info_table, info_data_list, info_columns, info_headers, info_column_map)

    if crowdloc_data_list:
        crowdloc_artifact_name = 'FindMy Items Crowdsourced Locations'
        crowdloc_headers = (
            'Timestamp', 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 
            'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 
            'System Version', 'Position Type', 'Vertical Accuracy', 'Longitude', 'Latitude', 'Altitude', 'Floor Level', 
            'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Location Finished')

        lava_crowdloc_headers = (
            ('Timestamp', 'datetime'), 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 
            'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 
            'System Version', 'Position Type', 'Vertical Accuracy', 'Longitude', 'Latitude', 'Altitude', 'Floor Level', 
            'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Location Finished')

        report = ArtifactHtmlReport(crowdloc_artifact_name)
        report.start_artifact_report(report_folder, crowdloc_artifact_name)
        report.add_script()
        report.write_artifact_data_table(crowdloc_headers, crowdloc_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = crowdloc_artifact_name
        tsv(report_folder, crowdloc_headers, crowdloc_data_list, tsvname)
        
        tlactivity = crowdloc_artifact_name
        timeline(report_folder, tlactivity, crowdloc_data_list, crowdloc_headers)
        
        kmlactivity = crowdloc_artifact_name
        kmlgen(report_folder, kmlactivity, crowdloc_data_list, crowdloc_headers)

        crowdloc_table, crowdloc_columns, crowdloc_column_map = lava_process_artifact(
            category, module_name, crowdloc_artifact_name, lava_crowdloc_headers, len(crowdloc_data_list))
        lava_insert_sqlite_data(crowdloc_table, crowdloc_data_list, crowdloc_columns, lava_crowdloc_headers, crowdloc_column_map)
