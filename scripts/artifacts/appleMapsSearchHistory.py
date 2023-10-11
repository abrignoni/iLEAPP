import plistlib
import blackboxprotobuf
import base64
import pprint

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def longbase64proto(longstuff, longtypes):
    longstuff = longstuff.split('placeRequest=')[1]
    longstuff, t = blackboxprotobuf.decode_message(base64.b64decode(longstuff), longtypes)
    return longstuff

def shortbase64proto(shortstuff, shorttypes):
    shortstuff = shortstuff.split('=')[1]
    shortstuff, t = blackboxprotobuf.decode_message(base64.b64decode(shortstuff), shorttypes)
    return shortstuff

def get_appleMapsSearchHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    shorttypes = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}, '7': {'type': 'int', 'name': ''}, '8': {'type': 'message', 'message_typedef': {'4': {'type': 'message', 'message_typedef': {'3': {'type': 'int', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}
    
    longtypes = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}, '7': {'type': 'int', 'name': ''}, '8': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'3': {'type': 'bytes', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'5': {'type': 'double', 'name': ''}, '6': {'type': 'double', 'name': ''}, '7': {'type': 'double', 'name': ''}, '8': {'type': 'double', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '5': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}}, 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '12': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}, '15': {'type': 'int', 'name': ''}, '16': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '10000': {'type': 'bytes', 'name': ''}, '10001': {'type': 'int', 'name': ''}, '10011': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '6': {'type': 'bytes', 'name': ''}}, 'name': ''}, '10019': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}




    for file_found in files_found:
        file_found = str(file_found)
        
        with open(file_found, "rb") as plist_file:
            plist_content = plistlib.load(plist_file)
            #print(plist_content)
            
            for a, b in plist_content.items():
                pass
                
            for c, d in b.items():
                if isinstance(d, str):
                    pass
                if isinstance(d, dict): #records
                    for e, f in d.items():
                        guid = e
                        shortadd = pname = app = location = geo1 = geo2 = geo3 = geo4 = geo5 = geo6 = usersearch1 = usersearch2 = shortlat = shortlon = usersearchnotinproto = items = currentlocation = ''
                        for g, h in f.items():
                            
                            if g == 'modificationDate':
                                modificationdate = h
                            if g == 'contents':
                                
                                protostuff, types = blackboxprotobuf.decode_message(h)
                                #pp.pprint(protostuff)
                                items = (protostuff)
                                if protostuff.get('7'):
                                    try:
                                        for look in (protostuff.get('7')['1']['1'][0]['2']['1']['4']):
                                            if look.get('8'):
                                                data = (look['8'].get('1'))
                                                if data is not None:
                                                    pname = (data['10']['3'].decode())
                                    except:
                                        #yelp like stuff
                                        pp = pprint.PrettyPrinter(indent = 0)
                                        items = pp.pformat(protostuff.get('7')['1']['1'][1])
                                        
                                                
                                if protostuff.get('6'):
                                    try:
                                        location = protostuff['6']['1'].decode()
                                        location = location + ', ' + protostuff['6']['2'].decode() #GPs after it?
                                    except:
                                        pass
                                try:    
                                    if protostuff.get('8'):
                                        if (protostuff['8']['2']['1'].get('201')):
                                            usersearchnotinproto = (protostuff['8']['2']['1']['201']['2']['2']['1'].decode())
                                except:
                                    pass
                                    try:
                                        for mira in (protostuff['8']['2']['1']['4']):
                                            #print(mira)
                                            if mira.get('11'):
                                                if mira['11']['2'].startswith(b'pl'):
                                                    try:
                                                        longstuff = longbase64proto(mira['11']['2'].decode(), longtypes)
                                                        app = longstuff['1']['1'].decode()
                                                        location = longstuff['8']['1']['3'].decode()
                                                        geo1 = longstuff['8']['1']['4']['1']['5']
                                                        geo2 = longstuff['8']['1']['4']['1']['6']
                                                        geo3 = longstuff['8']['1']['4']['1']['7']
                                                        geo4 = longstuff['8']['1']['4']['1']['8']
                                                        usersearch1 = longstuff['8']['1']['7']['12']['1'].decode()
                                                        usersearch2 = longstuff['8']['1']['7']['10000'].decode()
                                                        geo5 = longstuff['8']['1']['7']['5']['1']['1']
                                                        geo6 = longstuff['8']['1']['7']['5']['1']['2']
                                                    except:
                                                        pass
                                                        
                                                    try: 
                                                        
                                                        shortstuff = shortbase64proto(mira['11']['2'].decode(), shorttypes)
                                                        
                                                        shortlat = (shortstuff['8']['4']['4']['1']['1'])
                                                        shortlon = (shortstuff['8']['4']['4']['1']['2'])
                                                        
                                                        
                                                    except:
                                                        pass
                                                    
                                                    if mira.get('8'):
                                                        pname = (mira.get('8')['1']['10']['3'].decode())
                                    except:
                                        currentlocation = (protostuff['8']['2']['8']['3'].decode())
                                        
                                try: 
                                    if protostuff.get('7'):
                                        shortstuff = shortbase64proto(protostuff.get('7')['1']['1'][0]['2']['1']['4'][8]['11']['2'].decode(), shorttypes)
                                        app = shortstuff['1']['1'].decode()
                                        location = (shortstuff['8']['1']['3'].decode())
                                        shortlat = (shortstuff['8']['4']['4']['1']['1'])
                                        shortlon = (shortstuff['8']['4']['4']['1']['2'])
                                        
                                        if (protostuff.get('7')['1']['1'][1]['1'].get('2')):
                                            
                                            #pp.pprint(protostuff.get('7')['1']['1'][1]['1'].get('2')['4']) #address
                                            pname = (protostuff.get('7')['1']['1'][1]['1'].get('2')['5'].decode()) #place name
                                            shortadd = ''
                                            for parts in (protostuff.get('7')['1']['1'][1]['1'].get('2')['6']):
                                                shortadd = shortadd  + parts.decode() + ', '
                                            shortadd = (shortadd[:-2])
                                except:
                                    pass
                                    
                                    
                                    """
                                    counter = 0
                                    for masa in protostuff.get('7')['1']['1'][1]['2']['1']['4']:
                                        print(counter)
                                        print(masa)
                                        counter = counter + 1
                                    """
                                    try:
                                        for mira in (protostuff.get('7')['1']['1'][1]['2']['1']['4']):
                                            #print(mira)
                                            if mira.get('11'):
                                                if mira['11']['2'].startswith(b'pl'):
                                                    try:
                                                        longstuff = longbase64proto(mira['11']['2'].decode(), longtypes)
                                                        app = longstuff['1']['1'].decode()
                                                        location = longstuff['8']['1']['3'].decode()
                                                        geo1 = longstuff['8']['1']['4']['1']['5']
                                                        geo2 = longstuff['8']['1']['4']['1']['6']
                                                        geo3 = longstuff['8']['1']['4']['1']['7']
                                                        geo4 = longstuff['8']['1']['4']['1']['8']
                                                        usersearch1 = longstuff['8']['1']['7']['12']['1'].decode()
                                                        usersearch2 = longstuff['8']['1']['7']['10000'].decode()
                                                        geo5 = longstuff['8']['1']['7']['5']['1']['1']
                                                        geo6 = longstuff['8']['1']['7']['5']['1']['2']
                                                    except:
                                                        pass
                                    except:
                                        pp = pprint.PrettyPrinter(indent = 0)
                                        items = pp.pformat(protostuff['7']['1']['1'][0]['2']['1']['4'])
                                        
                                data_list.append((modificationdate,app,location,shortadd,pname,shortlat,shortlon,usersearchnotinproto,usersearch1, usersearch2,geo1,geo2,geo3,geo4,geo5,geo6,guid,currentlocation,items ))
                                modificationdate = app = locatio = shortadd = pname = shortlat = shortlon = usersearch1 = usersearch2 = geo1 = geo2 = geo3 = geo4 = geo5 = geo6 = guid = items = currentlocation = '' 
        
        

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Apple Maps Search History')
        report.start_artifact_report(report_folder, 'Apple Maps Search History')
        report.add_script()
        data_headers = ('Timestamp','App','Location','Short Address','Place Name','Latitude','Longitude','Search Not in Protobuf','Search Term','Search Term','Lat1','Lon1','Lat2','Lon2','Lat2','Lon3','Record GUID','Current Location','Items' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Apple Maps Search History'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Apple Maps Search History'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No data available for Apple Maps Search History')

__artifacts__ = {
    "applemapssearchhistory": (
        "Locations",
        ('*/mobile/Containers/Data/Application/*/Library/Maps/GeoHistory.mapsdata','*/GeoHistory.mapsdata'),
        get_appleMapsSearchHistory)
}