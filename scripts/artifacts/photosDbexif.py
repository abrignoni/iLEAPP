import os
from datetime import datetime
import pytz
import json
import magic
import shutil
import base64
from PIL import Image
from pillow_heif import register_heif_opener

from pathlib import Path	

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly

def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif().get_ifd(0x8825)

def get_geotagging(exif):
    geo_tagging_info = {}
    if not exif:
        #raise ValueError("No EXIF metadata found")
        return None
    else:
        gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                    'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                    'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                    'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                    'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                    'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']
        
        for k, v in exif.items():
            try:
                geo_tagging_info[gps_keys[k]] = str(v)
            except IndexError:
                pass
        return geo_tagging_info
    
def get_all_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif()

def get_photosDbexif(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if is_platform_windows():
            separator = '\\'
        else:
            separator = '/'
            
        #split_path = file_found.split(separator) #might not need
        #account = (split_path[-3]) #might not need
        
        filename = os.path.basename(file_found)
        
        if filename.endswith('.sqlite'):
            #print(file_found)
            data_list =[]
            #sqlite portion
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            DATETIME(ZDATECREATED+978307200,'UNIXEPOCH') AS DATECREATED,
            DATETIME(ZMODIFICATIONDATE+978307200,'UNIXEPOCH') AS MODIFICATIONDATE,
            ZDIRECTORY,
            ZFILENAME,
            ZLATITUDE,
            ZLONGITUDE
            FROM ZASSET
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            
            if usageentries > 0:
                for row in all_rows:
                    
                    thumb = suspecttime = suspectcoordinates = zdatecreated = zmodificationdate = zdirectory = zfilename = zlatitude = zlongitude = creationchanged = latitude = longitude = exifdata = offset = ''
                    
                    zdatecreated = row[0]
                    zmodificationdate = row[1]
                    zdirectory = row[2]
                    zfilename = row[3]
                    zlatitude = row[4]
                    zlongitude = row[5]
                    
                
                    for search in files_found:
                        searchbase = os.path.basename(search)
                        pathingval = row[2].split('/')
                        
                        if (pathingval[0] in search) and (pathingval[1] in search) and (zfilename in search):
                            
                            if search.endswith('HEIC'):
                                register_heif_opener()
                                
                                image = Image.open(search)
                                convertedfilepath = os.path.join(report_folder, f'{searchbase}.jpg')
                                image.save(convertedfilepath)
                                convertedlist = []
                                convertedlist.append(convertedfilepath)
                                thumb = media_to_html(f'{searchbase}.jpg', convertedlist, report_folder)
                                convertedlist = []
                            
                            if (search.endswith('JPG')) or (search.endswith('PNG')) or (search.endswith('JPEG')):
                                thumb = media_to_html(zfilename,files_found,report_folder)
                            
                            if (search.endswith('JPG')) or (search.endswith('PNG')) or (search.endswith('JPEG')) or (search.endswith('HEIC')):
                                
                                try:
                                    image_info = get_exif(search)
                                    results = get_geotagging(image_info)
                                    
                                    if results is None:
                                        latitude = ''
                                        longitude = ''
                                    else:
                                        directionlat = results['GPSLatitudeRef']
                                        latitude = results['GPSLatitude']
                                        latitude = (latitude.replace('(','').replace(')','').split(', '))
                                        latitude = (float(latitude[0]) + float(latitude[1])/60 + float(latitude[2])/(60*60)) * (-1 if directionlat in ['W', 'S'] else 1)
                                        
                                        
                                        directionlon = results['GPSLongitudeRef']
                                        longitude = results['GPSLongitude']
                                        longitude = (longitude.replace('(','').replace(')','').split(', '))
                                        longitude = (float(longitude[0]) + float(longitude[1])/60 + float(longitude[2])/(60*60)) * (-1 if directionlon in ['W', 'S'] else 1)
                                        
                                        #datamap = []
                                        #datamap.append((originalcreationdate,latitude,longitude))
                                        #kmlactivity = f'{search}'
                                        #data_headers = ('Timestamp','Latitude','Longitude')
                                        #print(report_folder)
                                        #kmlgen(report_folder, kmlactivity, datamap, data_headers)
                                        
                                    exifall = get_all_exif(search)
                                    exifdata = ''
                                    
                                    creationchanged = ''
                                    for x, y in exifall.items():
                                        if x == 271:
                                            exifdata = exifdata + f'Manufacturer: {y}<br>'
                                        elif x == 272:
                                            exifdata = exifdata + f'Model: {y}<br>'
                                        elif x == 305:
                                            exifdata = exifdata + f'Software: {y}<br>'
                                        elif x == 274:
                                            exifdata = exifdata + f'Orientation: {y}<br>'
                                        elif x == 306:
                                            exifdata = exifdata + f'Creation/Changed: {y}<br>'
                                            creationchanged = y
                                        elif x == 282:
                                            exifdata = exifdata + f'Resolution X: {y}<br>'
                                        elif x == 283:
                                            exifdata = exifdata + f'Resolution Y: {y}<br>'
                                        elif x == 316:
                                            exifdata = exifdata + f'Host device: {y}<br>'
                                        else:
                                            exifdata = exifdata + f'{x}: {y}<br>'
                                            
                                    if (isinstance(zlatitude, float)) and (isinstance(latitude, float)):
                                        suspectcoordinatesA = isclose(zlatitude,latitude )
                                        if (isinstance(zlongitude, float)) and (isinstance(longitude, float)):
                                            suspectcoordinatesb = isclose(zlongitude,longitude )
                                            if suspectcoordinatesA and suspectcoordinatesb:
                                                suspectcoordinates = 'True'
                                            else:
                                                suspectcoordinates = 'False'
                                                
                                    if creationchanged != '':
                                        mytz = pytz.timezone('UTC')             ## Set your timezone
                                        
                                        dbdate = datetime.fromisoformat(row[0])
                                        dbdate = mytz.normalize(mytz.localize(dbdate, is_dst=True))
                                        
                                        exifdate = creationchanged
                                        exifdate = exifdate.replace(':','-',2)
                                        creationchanged = exifdate
                                        exifdate = exifdate[:-1]
                                        
                                        
                                        time_list =[]
                                        for timeZone in pytz.all_timezones:
                                            dbtimezonedate = dbdate.astimezone(pytz.timezone(timeZone))
                                            time_list.append((str(dbtimezonedate),(timeZone)))
                                            
                                        for date in time_list:
                                            if exifdate in date[0]:
                                                responsive = date[0]
                                                suspecttime = 'True'
                                                break
                                            elif exifdate[:-1] in date[0][:-7]:
                                                responsive = date[0]
                                                suspecttime = 'True'
                                                break
                                            elif exifdate[:-2] in date[0][:-8]:
                                                responsive = date[0]
                                                suspecttime = 'True'
                                                break
                                            
                                            else:
                                                responsive = ''
                                                suspecttime = 'False'
                                                offset = ''
                                                
                                        offset = responsive[-6:]
                                except:
                                    results = None
                                    logfunc(f'Error getting exif on: {search}')
                                
                                data_list.append((thumb,suspecttime,offset, suspectcoordinates,zdatecreated,zmodificationdate,zdirectory,zfilename,zlatitude,zlongitude,creationchanged,latitude,longitude,exifdata))
                        
                            else:
                                """ videos. Nees to figure this out
                                #print(filenamedec)
                                thumb = media_to_html(file_found, files_found, report_folder)
                                latitude = ''
                                longitude = ''
                                exifdata = ''
                                
                                data_list.append((originalcreationdatedec, thumb, filenamedec, latitude, longitude, exifdata, filenameEnc, isdeleted, isexpunged))
                                """
                                pass
                    
                
            if data_list:
                description = 'All times labeled as False require validation. Compare database times and geolocation points to their EXIF counterparts. Timestamp value is in UTC. Exif Creation/Change timestamp is on local time. Use Possible Exif Offset column value to compare the times.'
                report = ArtifactHtmlReport(f'Photos.sqlite Analysis')
                report.start_artifact_report(report_folder, f'Photos.sqlite Analysis', description)
                report.add_script()
                data_headers = ('Media','Same Timestamps?','Possible Exif Offset','Same Coordinates?','Timestamp','Timestamp Modification','Directory','Filename','Latitude DB','Longitude DB','Exif Creation/Changed','Latitude','Longitude','Exif')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media','Exif'])
                report.end_artifact_report()
                
                tsvname = f'Photos.sqlite Analysis'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Photos.sqlite Analysis'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                #kmlactivity = f'iCloud Returns - Photo Library - {account}'
                #kmlgen(report_folder, kmlactivity, data_list, data_headers)
                
            else:
                logfunc(f'No Photos.sqlite Analysis data available')
                
__artifacts__ = {
        "photosDbexif": (
            "Photos",
            ('*Media/PhotoData/Photos.sqlite*','*Media/DCIM/*/**'),
            get_photosDbexif)
}