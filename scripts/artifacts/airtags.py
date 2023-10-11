import os
import datetime
import json
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, logdevinfo, kmlgen

    
def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

def get_airtags(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list_info = []
    data_list_safeloc = []
    data_list_location = []
    data_list_crowdloc = []
    
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
            amapItemFullAddress =  (x['address'].get('mapItemFullAddress'))
            afullThroroughfare =  (x['address'].get('fullThroroughfare'))
            areaOfInterest =  (x['address'].get('areaOfInterest'))
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
            ltimestamp = timestampcalc(ltimestamp)
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
            crowdtimestamp = timestampcalc(crowdtimestamp)
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
                stimestamp = timestampcalc(stimestamp)
                salt = (safeloc['location'].get('altitude'))
                ssub = (safeloc['address'].get('subAdministrativeArea'))
                slabel = (safeloc['address'].get('label'))
                sstreet = (safeloc['address'].get('streetAddres'))
                scountry = (safeloc['address'].get('countryCode'))
                sstate = (safeloc['address'].get('stateCode'))
                sadmin = (safeloc['address'].get('administrativeArea'))
                pstreetn = (safeloc['address'].get('streetName'))
                sformated = (safeloc['address'].get('formattedAddressLines'))
                smapfull = (safeloc['address'].get('mapItemFullAddress'))
                sthro = (safeloc['address'].get('fullThroroughfare'))
                saoi = (safeloc['address'].get('areaOfInterest'))
                sloc = (safeloc['address'].get('locality'))
                scount = (safeloc['address'].get('country'))
                
                data_list_safeloc.append((stimestamp, name, serial, id, rname, remoji, ris, sname, stype, sid, sva, sha, slong, slat, sfloor, sisina, sisold, salt, ssub, slabel, sstreet, scountry, sstate, sadmin, pstreetn, sformated, smapfull, sthro, saoi, sloc, scount))	
                
            data_list_info.append((name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, batstat, lostmode, cap, sysver,))
            
            data_list_location.append((ltimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, batstat, lostmode, cap, sysver, asubAdministrativeArea, aslabel, astreetAddress, acountryCode, astateCode, administrativeArea, astreetName, aformattedAddressLines, amapItemFullAddress, afullThroroughfare, areaOfInterest, alocality, lpostype, lverticalAccuracy, llong, lisin, lisold, lhorz, llat, lalt, lloc, acountry))
            
            data_list_crowdloc.append((crowdtimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, batstat, lostmode, cap, sysver, crowdpostype, crowdvert, crowdlong, crowdlat, crowdalt, crowdfloor, crowdisacc, crowdisold, crowdhorzcc, crowdlocfin ))

    if data_list_safeloc:
        report = ArtifactHtmlReport('Safe Locations')
        report.start_artifact_report(report_folder, 'Safe Locations')
        report.add_script()
        data_list_safeloc_headers = ('Timestamp', 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Name', 'Type', 'Identifier', 'Vertical Accuracy', 'Horizontal Accuracy', 'Longitude', 'Latitude', 'Floor Level', 'Is Inaccurate', 'Is Old', 'Altitude', 'Sub-Administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 'Street Name', 'Formatted Address Line', 'Map Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Country' )
        report.write_artifact_data_table(data_list_safeloc_headers, data_list_safeloc, file_found)
        report.end_artifact_report()
        
        tsvname = f'Airtags Safe Locations'
        tsv(report_folder, data_list_safeloc_headers, data_list_safeloc, tsvname)
        
        tlactivity = f'Airtags Safe Locations'
        timeline(report_folder, tlactivity, data_list_safeloc, data_list_safeloc_headers)
        
        kmlactivity = 'Airtags Safe Locations'
        kmlgen(report_folder, kmlactivity, data_list_safeloc, data_list_safeloc_headers)
    else:
        logfunc('No Airtags Safe Locations data available')
            
    if data_list_location:
        report = ArtifactHtmlReport('Locations')
        report.start_artifact_report(report_folder, 'Locations')
        report.add_script()
        data_list_location_headers = ('Timestamp','Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version', 'Sub-administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 'Street Name', 'Formatted Address Line', 'Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Type', 'Vertical Accuracy', 'Longitude', 'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Latitude', 'Altitude', 'Location Finished', 'Country'  )
        report.write_artifact_data_table(data_list_location_headers, data_list_location, file_found)
        report.end_artifact_report()
        
        tsvname = f'Airtags Locations'
        tsv(report_folder, data_list_location_headers, data_list_location, tsvname)
        
        tlactivity = f'Airtags Locations'
        timeline(report_folder, tlactivity, data_list_location, data_list_location_headers)
        
        kmlactivity = 'Airtags Locations'
        kmlgen(report_folder, kmlactivity, data_list_location, data_list_location_headers)
    else:
        logfunc('No Airtags Locations data available')
        
    if data_list_info:
        report = ArtifactHtmlReport('Airtags Info')
        report.start_artifact_report(report_folder, 'Airtags Info')
        report.add_script()
        data_list_info_headers = ('Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version' )
        report.write_artifact_data_table(data_list_info_headers, data_list_info, file_found)
        report.end_artifact_report()
        
        tsvname = f'Airtags Info'
        tsv(report_folder, data_list_info_headers, data_list_info, tsvname)
        
        tlactivity = f'Airtags Info'
        timeline(report_folder, tlactivity, data_list_info, data_list_info_headers)
        
    else:
        logfunc('No Airtags Info data available')
        
    
    if data_list_crowdloc:
        report = ArtifactHtmlReport('Crowdsourced Locations')
        report.start_artifact_report(report_folder, 'Crowdsourced Locations')
        report.add_script()
        data_headers_crowdloc = ('Timestamp', 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version', 'Position Type', 'Vertical Accuracy', 'Longitude', 'Latitude', 'Altitude', 'Floor Level', 'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Location Finished')
        report.write_artifact_data_table(data_headers_crowdloc, data_list_crowdloc, file_found)
        report.end_artifact_report()
        
        tsvname = f'Airtgas Crowdsourced Locations'
        tsv(report_folder, data_headers_crowdloc, data_list_crowdloc, tsvname)
        
        tlactivity = f'Airtags Crowdsourced Locations'
        timeline(report_folder, tlactivity, data_list_crowdloc, data_headers_crowdloc)
        
        kmlactivity = 'Airtags Crowdsourced Locations'
        kmlgen(report_folder, kmlactivity, data_list_crowdloc, data_headers_crowdloc)
        
    else:
        logfunc('No Airtags Crowdsourced Locations data available')

__artifacts__ = {
    "airtags": (
        "Airtags",
        ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        get_airtags)
}