__artifacts_v2__ = {
    "findMyItemsInfo": {
        "name": "Find My Items Info",
        "description": "Extract items information from Find My",
        "author": "@AlexisBrignoni",
        "version": "0.3.1",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Find My",
        "notes": "",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": ["html", "tsv", "lava"],
    },
    "findMyItemsLocations": {
        "name": "FindMy Items Locations",
        "description": "Extract items locations from Find My",
        "author": "@AlexisBrignoni",
        "version": "0.3.1",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Find My",
        "notes": "",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all"
    },
    "findMyItemsSafeLocations": {
        "name": "FindMy Items Safe Locations",
        "description": "Extract items safe locations from Find My",
        "author": "@AlexisBrignoni",
        "version": "0.3.1",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Find My",
        "notes": "",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all"
    },
    "findMyItemsCrowdsourcedLocations": {
        "name": "FindMy Items Crowdsourced Locations",
        "description": "Extract items crowdsourced locations from Find My",
        "author": "@AlexisBrignoni",
        "version": "0.3.1",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Find My",
        "notes": "",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all"
    }
}


import json
from scripts.ilapfuncs import artifact_processor
from scripts.ilapfuncs import convert_unix_ts_to_timezone

@artifact_processor
def findMyItemsInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, mode='r', encoding="UTF-8") as f:
        deserialized = json.load(f)
        for x in deserialized:
            name = (x['name'])
            serial = (x['serialNumber'])
            id = (x['identifier'])
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x['groupIdentifier'])
            owner = (x.get('owner'))
            batstat = (x['batteryStatus'])
            lostmode = (x['lostModeMetadata'])
            cap = (x['capabilities'])
            sysver = (x['systemVersion'])

            data_list.append(
                (name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, 
                    batstat, lostmode, cap, sysver,))

    data_headers = (
        'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 
        'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version')
    return data_headers, data_list, source_path

@artifact_processor
def findMyItemsLocations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, mode='r', encoding="UTF-8") as f:
        deserialized = json.load(f)
        for x in deserialized:
            ltimestamp = (x['location'].get('timeStamp'))
            ltimestamp = convert_unix_ts_to_timezone(ltimestamp, timezone_offset)
            name = (x['name'])
            serial = (x['serialNumber'])
            id = (x['identifier'])
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x['groupIdentifier'])
            owner = (x.get('owner'))
            batstat = (x['batteryStatus'])
            lostmode = (x['lostModeMetadata'])
            cap = (x['capabilities'])
            sysver = (x['systemVersion'])
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
            lpostype = (x['location'].get('positionType'))
            lverticalAccuracy = (x['location'].get('verticalAccuracy'))
            llong = (x['location'].get('longitude'))
            lisin = (x['location'].get('isInaccurate'))
            lisold = (x['location'].get('isOld'))
            lhorz = (x['location'].get('horizontalAccuracy'))
            llat = (x['location'].get('latitude'))
            lalt = (x['location'].get('altitude'))
            lloc = (x['location'].get('locationFinished'))
            acountry =  (x['address'].get('country'))

            data_list.append(
                (ltimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, 
                    owner, batstat, lostmode, cap, sysver, asubAdministrativeArea, aslabel, astreetAddress, 
                    acountryCode, astateCode, administrativeArea, astreetName, aformattedAddressLines, 
                    amapItemFullAddress, afullThroroughfare, areaOfInterest, alocality, lpostype, lverticalAccuracy, 
                    llong, lisin, lisold, lhorz, llat, lalt, lloc, acountry))

    data_headers = (
        ('Timestamp', 'datetime'), 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 
        'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version', 
        'Sub-administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 'Street Name', 
        'Formatted Address Line', 'Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Type', 'Vertical Accuracy', 
        'Longitude', 'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Latitude', 'Altitude', 'Location Finished', 'Country')
    return data_headers, data_list, source_path

@artifact_processor
def findMyItemsSafeLocations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, mode='r', encoding="UTF-8") as f:
        deserialized = json.load(f)
        for x in deserialized:
            name = (x['name'])
            serial = (x['serialNumber'])
            id = (x['identifier'])
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            for safeloc in x.get('safeLocations'):
                stimestamp = (safeloc['location'].get('timeStamp'))
                stimestamp = convert_unix_ts_to_timezone(stimestamp, timezone_offset)
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

                data_list.append(
                    (stimestamp, name, serial, id, rname, remoji, ris, sname, stype, sid, sva, sha, 
                        slong, slat, sfloor, sisina, sisold, salt, ssub, slabel, sstreet, scountry, 
                        sstate, sadmin, pstreetn, sformated, smapfull, sthro, saoi, sloc, scount))

    data_headers = (
        ('Timestamp', 'datetime'), 'Item Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Location Name', 'Type', 
        'Identifier', 'Vertical Accuracy', 'Horizontal Accuracy', 'Longitude', 'Latitude', 'Floor Level', 'Is Inaccurate', 
        'Is Old', 'Altitude', 'Sub-Administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 
        'Street Name', 'Formatted Address Line', 'Map Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Country')
    return data_headers, data_list, source_path

@artifact_processor
def findMyItemsCrowdsourcedLocations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, mode='r', encoding="UTF-8") as f:
        deserialized = json.load(f)
        for x in deserialized:
            crowdtimestamp= (x['crowdSourcedLocation'].get('timeStamp'))
            crowdtimestamp = convert_unix_ts_to_timezone(crowdtimestamp, timezone_offset)
            name = (x['name'])
            serial = (x['serialNumber'])
            id = (x['identifier'])
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x['groupIdentifier'])
            owner = (x.get('owner'))
            batstat = (x['batteryStatus'])
            lostmode = (x['lostModeMetadata'])
            cap = (x['capabilities'])
            sysver = (x['systemVersion'])
            crowdpostype = (x['crowdSourcedLocation'].get('positionType'))
            crowdvert = (x['crowdSourcedLocation'].get('verticalAccuracy'))
            crowdlong = (x['crowdSourcedLocation'].get('longitude'))
            crowdlat = (x['crowdSourcedLocation'].get('latitude'))
            crowdalt = (x['crowdSourcedLocation'].get('altitude'))
            crowdfloor = (x['crowdSourcedLocation'].get('floorLevel'))
            crowdisacc = (x['crowdSourcedLocation'].get('isInaccurate'))
            crowdisold = (x['crowdSourcedLocation'].get('isOld'))
            crowdhorzcc = (x['crowdSourcedLocation'].get('horizontalAccuracy'))
            crowdlocfin = (x['crowdSourcedLocation'].get('locationFinished'))

            data_list.append(
                (crowdtimestamp, name, serial, id, rname, remoji, ris, ptype, maname, pid, vid, 
                ap, gid, owner, batstat, lostmode, cap, sysver, crowdpostype, crowdvert, crowdlong, 
                crowdlat, crowdalt, crowdfloor, crowdisacc, crowdisold, crowdhorzcc, crowdlocfin ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 
        'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 
        'System Version', 'Position Type', 'Vertical Accuracy', 'Longitude', 'Latitude', 'Altitude', 'Floor Level', 
        'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Location Finished')
    return data_headers, data_list, source_path