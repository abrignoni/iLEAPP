import json
import datetime
import base64
import plistlib
import os
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, is_platform_windows 

def get_icloudPhotoMeta(files_found, report_folder, seeker):
    counter = 0
    os.makedirs(os.path.join(report_folder, "bplists"))
    for file_found in files_found:
        file_found = str(file_found)
        counter = counter + 1
        data_list = []
        with open(file_found, "r") as filecontent:
            for line in filecontent:
                jsonconv = json.loads(line)
                #print(jsonconv)
                
                if (isinstance(jsonconv, dict)):
                    jsonconv = jsonconv['results']
                length = len(jsonconv)
                
                for i in range(length):
                    #Initialize variables for when items are not located in a loop.
                    id = ''
                    created_timestamp = ''
                    created_user = ''
                    created_device = ''
                    modified_timestamp = ''
                    modified_user = ''
                    modified_device = ''
                    decoded = ''
                    is_deleted = ''
                    is_expunged = ''
                    org_filesize = ''
                    rec_mod_date = ''
                    import_date = ''
                    f_org_creation_date = ''
                    res_org_filesize = ''
                    added_date = ''
                    timezoneoffse = ''
                    latitude = ''
                    longitude = ''
                    altitude = ''
                    datestamp = ''
                    timestamp = ''
                    vid_name = ''
                    decoded_tz = ''
                    title = ''
                    recordtype = ''
                    tiff = ''
                    exif = ''
                    
                    id = (jsonconv[i].get('id', ''))
                    rowid = str(i)
                    recordtype = (jsonconv[i].get('recordType', ''))
                    
                    if (jsonconv[i].get('created', '')):
                        created_timestamp = str(jsonconv[i]['created'].get('timestamp', ''))
                        created_timestamp = int(created_timestamp.rstrip("0")) 
                        if isinstance(created_timestamp, int):
                            created_timestamp = datetime.datetime.fromtimestamp(created_timestamp/1000)
                            created_timestamp = str(created_timestamp)
                        #created_user = (jsonconv[i]['created'].get('user', ''))
                        #created_device = (jsonconv[i]['created'].get('device', ''))
                        
                    if(jsonconv[i].get('modified', '')):
                        modified_timestamp = str(jsonconv[i]['created'].get('timestamp', ''))
                        modified_timestamp = int(modified_timestamp.rstrip("0")) 
                        if isinstance(modified_timestamp, int):
                            modified_timestamp = datetime.datetime.fromtimestamp(modified_timestamp/1000)
                            modified_timestamp = str(modified_timestamp)
                        #modified_user = (jsonconv[i]['modified'].get('user', ''))
                        #modified_device = (jsonconv[i]['modified'].get('device', ''))
                        
                    if (jsonconv[i].get('fields')):
                        coded_string = (jsonconv[i]['fields'].get('filenameEnc', '')) #base64
                        decoded = base64.b64decode(coded_string)
                        decoded = decoded.decode()
                        coded_string_tz = (jsonconv[i]['fields'].get('timeZoneNameEnc', ''))#base64
                        decoded_tz = base64.b64decode(coded_string_tz)
                        decoded_tz = decoded_tz.decode()
                        is_deleted = (jsonconv[i]['fields'].get('isDeleted', ''))
                        is_expunged = (jsonconv[i]['fields'].get('isExpunged', ''))
                        org_filesize = (jsonconv[i]['fields'].get('resOriginalFileSize', ''))
                        rec_mod_date = (jsonconv[i]['fields'].get('recordModificationDate', ''))
                        if isinstance(rec_mod_date, int):
                            if rec_mod_date > 0:
                                rec_mod_date = datetime.datetime.fromtimestamp(rec_mod_date/1000)
                                rec_mod_date = str(rec_mod_date)
                        import_date = (jsonconv[i]['fields'].get('importDate', ''))
                        if isinstance(import_date, int):
                            import_date = datetime.datetime.fromtimestamp(import_date/1000)
                            import_date = str(import_date)
                        f_org_creation_date = (jsonconv[i]['fields'].get('originalCreationDate', ''))
                        if isinstance(f_org_creation_date, int):
                            f_org_creation_date = datetime.datetime.fromtimestamp(f_org_creation_date/1000)
                            f_org_creation_date = str(f_org_creation_date)
                        res_org_filesize = (jsonconv[i]['fields'].get('resOriginalFileSize', ''))
                        added_date = (jsonconv[i]['fields'].get('addedDate', ''))
                        if isinstance(added_date, int):
                            added_date = datetime.datetime.fromtimestamp(added_date/1000)
                            added_date = str(added_date)
                        timezoneoffse = (jsonconv[i]['fields'].get('timeZoneOffse', ''))
                        title = (jsonconv[i]['fields'].get('title', ''))
                        decodedt = base64.b64decode(title)
                        title = decodedt.decode()
                        
                        coded_bplist = (jsonconv[i]['fields'].get('mediaMetaDataEnc')) #convert from base64 to bplist and process
                        if coded_bplist is not None:
                            decoded_bplist = base64.b64decode(coded_bplist)
                            # If needed send the full bplist to report folder by editing the outputpath below
                            with open(os.path.join(report_folder, "bplists", rowid + ".bplist"), 'wb') as g: 
                                g.write(decoded_bplist)
                            pl = plistlib.loads(decoded_bplist)
                            if (pl.get('{TIFF}')):
                                #print('YESS TIFF # '+str(i))
                                tiff = (pl.get('{TIFF}'))
                                exif = (pl.get('{Exif}'))
                                
                                if (pl.get('{GPS}')) is not None:
                                    #print(pl['{GPS}'])
                                    latitude = (pl['{GPS}'].get('Latitude'))
                                    longitude = (pl['{GPS}'].get('Longitude'))
                                    altitude = (pl['{GPS}'].get('Altitude'))
                                    datestamp = (pl['{GPS}'].get('DateStamp'))
                                    timestamp = (pl['{GPS}'].get('TimeStamp'))
                                    #print(latitude)
                            else:
                                if (pl.get('moop')): #If needed send binary content to report flder
                                    pass
                                    #with open(f'{outputpath}/{i}.moop', 'wb') as g:
                                    #    g.write(pl.get('moop'))
                                        
                    data_list.append((created_timestamp, rowid, recordtype, decoded, title, org_filesize, latitude,longitude,altitude,datestamp,timestamp,added_date, timezoneoffse, decoded_tz ,is_deleted,is_expunged, import_date, rec_mod_date,res_org_filesize, id, tiff, exif))
            
        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('iCloud - Photos Metadata'+' '+str(counter))
            report.start_artifact_report(report_folder, 'iCloud - Photos Metadata'+' '+str(counter))
            report.add_script()
            data_headers = ('Timestamp', 'Row ID','Record Type','Decoded', 'Title', 'Filesize', 'Latitude', 'Longitude', 'Altitude', 'GPS Datestamp','GPS Time', 'Added Date', 'Timezone Offset','Decoded TZ', 'Is Deleted?','Is Expunged?','Import Date', 'Modification Date', 'Filesize', 'ID', 'TIFF', 'EXIF')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'iCloud - Photos Metadata'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            kmlactivity = 'iCloud - Photos Metadata'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
        else:
            logfunc('No data available')
                