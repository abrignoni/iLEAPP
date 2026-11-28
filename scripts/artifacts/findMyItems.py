__artifacts_v2__ = {
    "findMyItemsInfo": {
        "name": "Find My Items Info",
        "description": "Item records from the Find My Items.data cache file, in its plain JSON or encrypted form",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-10-18",
        "last_update_date": "2026-11-20",
        "version": "0.3.2",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Items.data is read in its JSON form or, on dexter_ios18, felix_ios17, otto_ios17, falken_ios26, "
                 "hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, decrypted with the FMIPDataManager key from"
                 " the keychain carried by the extraction or supplied with --keychain (falken_ios26 was run with "
                 "--keychain), and only when the ChaCha20-Poly1305 tag verifies; the signature is not checked. The"
                 " text $null in a decrypted file is read as no value. Layout published in "
                 "PnutCN/findmy-cache-decryptor. For an encrypted file, no rows are reported without the key. That"
                 " is not evidence that no items were recorded. Keys not reported include isAppleItem, "
                 "rangeDistanceInMeters, isAppleAudioAccessory, isFirmwareUpdateMandatory, partInfo and the "
                 "top-level productIdentifier. The list is not exhaustive. ItemGroups.data, an empty list on the "
                 "dexter_ios18, felix_ios17 and wilkerson_iphone16_ios26 files, is not read.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "info-circle",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows (run with --keychain)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "findMyItemsLocations": {
        "name": "Find My Items Locations",
        "description": "The location and address records stored for each item in the Find My Items.data cache file. One "
                       "row per item.",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-10-18",
        "last_update_date": "2026-11-20",
        "version": "0.3.2",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Timestamp is the timeStamp value stored in the item's location record, converted from Unix time "
                 "to UTC. What it marks is not established. Items.data is read in its JSON form or, on "
                 "dexter_ios18, felix_ios17, otto_ios17, falken_ios26, hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26, decrypted with the FMIPDataManager key from the keychain carried by "
                 "the extraction or supplied with --keychain (falken_ios26 was run with --keychain), and only when"
                 " the ChaCha20-Poly1305 tag verifies; the signature is not checked. The text $null in a decrypted"
                 " file is read as no value. Layout published in PnutCN/findmy-cache-decryptor. For an encrypted "
                 "file, no rows are reported without the key. That is not evidence that no items were recorded. "
                 "Keys not reported include isAppleItem, rangeDistanceInMeters, isAppleAudioAccessory, "
                 "isFirmwareUpdateMandatory, partInfo and the top-level productIdentifier. The list is not "
                 "exhaustive. ItemGroups.data, an empty list on the dexter_ios18, felix_ios17 and "
                 "wilkerson_iphone16_ios26 files, is not read.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows (run with --keychain)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "findMyItemsSafeLocations": {
        "name": "Find My Items Safe Locations",
        "description": "Safe location records listed for each item in the Find My Items.data cache "
                       "file",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-10-18",
        "last_update_date": "2026-11-20",
        "version": "0.3.2",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Timestamp is the timeStamp value stored with the safe location, converted from Unix time to UTC;"
                 " what it marks is not established. Street Address is read from the streetAddress key or, when "
                 "that is absent or empty, from a key spelled streetAddres. Items.data is read in its JSON form "
                 "or, on dexter_ios18, felix_ios17, otto_ios17, falken_ios26, hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26, decrypted with the FMIPDataManager key from the keychain carried by "
                 "the extraction or supplied with --keychain (falken_ios26 was run with --keychain), and only when"
                 " the ChaCha20-Poly1305 tag verifies; the signature is not checked. The text $null in a decrypted"
                 " file is read as no value. Layout published in PnutCN/findmy-cache-decryptor. For an encrypted "
                 "file, no rows are reported without the key. That is not evidence that no items were recorded. "
                 "Keys not reported include isAppleItem, rangeDistanceInMeters, isAppleAudioAccessory, "
                 "isFirmwareUpdateMandatory, partInfo and the top-level productIdentifier. The list is not "
                 "exhaustive. ItemGroups.data, an empty list on the dexter_ios18, felix_ios17 and "
                 "wilkerson_iphone16_ios26 files, is not read.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all",
        "artifact_icon": "shield-check",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 1 row (run with --keychain)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "findMyItemsCrowdsourcedLocations": {
        "name": "Find My Items Crowdsourced Locations",
        "description": "The crowdSourcedLocation record stored for each item in the Find My "
                       "Items.data cache file",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-10-18",
        "last_update_date": "2026-11-20",
        "version": "0.3.2",
        "date": "2022-01-22",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Timestamp is the timeStamp value stored in the crowdSourcedLocation record, converted from Unix "
                 "time to UTC. What it marks is not established. The position is the one stored for the item under"
                 " the crowdSourcedLocation key; how it was obtained is not established here, and a row does not "
                 "show that the examined device was at that position. Items.data is read in its JSON form or, on "
                 "dexter_ios18, felix_ios17, otto_ios17, falken_ios26, hill_iphone15pro_ios26 and "
                 "wilkerson_iphone16_ios26, decrypted with the FMIPDataManager key from the keychain carried by "
                 "the extraction or supplied with --keychain (falken_ios26 was run with --keychain), and only when"
                 " the ChaCha20-Poly1305 tag verifies; the signature is not checked. The text $null in a decrypted"
                 " file is read as no value. Layout published in PnutCN/findmy-cache-decryptor. For an encrypted "
                 "file, no rows are reported without the key. That is not evidence that no items were recorded. "
                 "Keys not reported include isAppleItem, rangeDistanceInMeters, isAppleAudioAccessory, "
                 "isFirmwareUpdateMandatory, partInfo and the top-level productIdentifier. The list is not "
                 "exhaustive. ItemGroups.data, an empty list on the dexter_ios18, felix_ios17 and "
                 "wilkerson_iphone16_ios26 files, is not read.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all",
        "artifact_icon": "users",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 2 rows (run with --keychain)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        }
    }
}


from scripts.findmy_cache import read_find_my_cache
from scripts.ilapfuncs import artifact_processor
from scripts.ilapfuncs import convert_unix_ts_to_utc


def _read_items_json(source_path):
    """Return the item records of Items.data, in its JSON or encrypted form.

    A file that cannot be read is logged by read_find_my_cache and gives no records. Sections an
    item holds as null become empty so that one item without a location keeps its other rows.
    """
    items = read_find_my_cache(source_path)
    if not isinstance(items, list):
        return []
    records = [item for item in items if isinstance(item, dict)]
    for item in records:
        for section in ('role', 'productType', 'location', 'crowdSourcedLocation', 'address'):
            item[section] = item.get(section) or {}
        item['productType']['productInformation'] = item['productType'].get('productInformation') or {}
        item['safeLocations'] = [loc for loc in item.get('safeLocations') or [] if isinstance(loc, dict)]
        for safe_location in item['safeLocations']:
            for section in ('location', 'address'):
                safe_location[section] = safe_location.get(section) or {}
    return records


@artifact_processor
def findMyItemsInfo(context):
    data_list = []
    source_path = str(context.get_files_found()[0])

    deserialized = _read_items_json(source_path)
    if deserialized:
        for x in deserialized:
            name = (x.get('name'))
            serial = (x.get('serialNumber'))
            item_id = (x.get('identifier'))
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x.get('groupIdentifier'))
            owner = (x.get('owner'))
            batstat = (x.get('batteryStatus'))
            lostmode = (x.get('lostModeMetadata'))
            cap = (x.get('capabilities'))
            sysver = (x.get('systemVersion'))

            data_list.append(
                (name, serial, item_id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, owner, 
                    batstat, lostmode, cap, sysver,))

    data_headers = (
        'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 'Product ID', 'Vendor ID', 
        'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 'System Version')
    return data_headers, data_list, source_path

@artifact_processor
def findMyItemsLocations(context):
    data_list = []
    source_path = str(context.get_files_found()[0])
    
    deserialized = _read_items_json(source_path)
    if deserialized:
        for x in deserialized:
            ltimestamp = (x['location'].get('timeStamp'))
            ltimestamp = convert_unix_ts_to_utc(ltimestamp)
            name = (x.get('name'))
            serial = (x.get('serialNumber'))
            item_id = (x.get('identifier'))
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x.get('groupIdentifier'))
            owner = (x.get('owner'))
            batstat = (x.get('batteryStatus'))
            lostmode = (x.get('lostModeMetadata'))
            cap = (x.get('capabilities'))
            sysver = (x.get('systemVersion'))
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
                (ltimestamp, name, serial, item_id, rname, remoji, ris, ptype, maname, pid, vid, ap, gid, 
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
def findMyItemsSafeLocations(context):
    data_list = []
    source_path = str(context.get_files_found()[0])
    
    deserialized = _read_items_json(source_path)
    if deserialized:
        for x in deserialized:
            name = (x.get('name'))
            serial = (x.get('serialNumber'))
            item_id = (x.get('identifier'))
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            for safeloc in x.get('safeLocations'):
                stimestamp = (safeloc['location'].get('timeStamp'))
                stimestamp = convert_unix_ts_to_utc(stimestamp)
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
                sstreet = safeloc['address'].get('streetAddress') or safeloc['address'].get('streetAddres')
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
                    (stimestamp, name, serial, item_id, rname, remoji, ris, sname, stype, sid, sva, sha, 
                        slong, slat, sfloor, sisina, sisold, salt, ssub, slabel, sstreet, scountry, 
                        sstate, sadmin, pstreetn, sformated, smapfull, sthro, saoi, sloc, scount))

    data_headers = (
        ('Timestamp', 'datetime'), 'Item Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Location Name', 'Type', 
        'Identifier', 'Vertical Accuracy', 'Horizontal Accuracy', 'Longitude', 'Latitude', 'Floor Level', 'Is Inaccurate', 
        'Is Old', 'Altitude', 'Sub-Administrative Area', 'Label', 'Street Address', 'Country Code', 'State Code', 'Administrative Area', 
        'Street Name', 'Formatted Address Line', 'Map Item Full Address', 'Throroughfare', 'Area of Interest', 'Locality', 'Country')
    return data_headers, data_list, source_path

@artifact_processor
def findMyItemsCrowdsourcedLocations(context):
    data_list = []
    source_path = str(context.get_files_found()[0])
    
    deserialized = _read_items_json(source_path)
    if deserialized:
        for x in deserialized:
            crowdtimestamp= (x['crowdSourcedLocation'].get('timeStamp'))
            crowdtimestamp = convert_unix_ts_to_utc(crowdtimestamp)
            name = (x.get('name'))
            serial = (x.get('serialNumber'))
            item_id = (x.get('identifier'))
            rname = (x['role'].get('name'))
            remoji = (x['role'].get('emoji'))
            ris = (x['role'].get('identifier'))
            ptype = (x['productType'].get('type'))
            maname = (x['productType']['productInformation'].get('manufacturerName'))
            pid = (x['productType']['productInformation'].get('productIdentifier'))
            vid = (x['productType']['productInformation'].get('vendorIdentifier'))
            ap = (x['productType']['productInformation'].get('antennaPower'))
            gid = (x.get('groupIdentifier'))
            owner = (x.get('owner'))
            batstat = (x.get('batteryStatus'))
            lostmode = (x.get('lostModeMetadata'))
            cap = (x.get('capabilities'))
            sysver = (x.get('systemVersion'))
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
                (crowdtimestamp, name, serial, item_id, rname, remoji, ris, ptype, maname, pid, vid, 
                ap, gid, owner, batstat, lostmode, cap, sysver, crowdpostype, crowdvert, crowdlong, 
                crowdlat, crowdalt, crowdfloor, crowdisacc, crowdisold, crowdhorzcc, crowdlocfin ))

    data_headers = (
        ('Timestamp', 'datetime'), 'Name', 'Serial', 'ID', 'Role Name', 'Emoji', 'Role ID', 'Product Type', 'Manufacturer', 
        'Product ID', 'Vendor ID', 'Antenna Power', 'Group ID', 'Owner', 'Battery Status', 'Lost Mode', 'Capabilities', 
        'System Version', 'Position Type', 'Vertical Accuracy', 'Longitude', 'Latitude', 'Altitude', 'Floor Level', 
        'Is Inaccurate', 'Is Old', 'Horizontal Accuracy', 'Location Finished')
    return data_headers, data_list, source_path