import os
import struct
import blackboxprotobuf
import nska_deserialize as nd
from io import StringIO
from io import BytesIO

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, convert_time_obj_to_utc 

def utf8_in_extended_ascii(input_string, *, raise_on_unexpected=False):
    """Returns a tuple of bool (whether mis-encoded utf-8 is present) and str (the converted string)"""
    output = []  # individual characters, join at the end
    is_in_multibyte = False  # True if we're currently inside a utf-8 multibyte character
    multibytes_expected = 0
    multibyte_buffer = []
    mis_encoded_utf8_present = False
    
    def handle_bad_data(index, character):
        if not raise_on_unexpected: # not raising, so we dump the buffer into output and append this character
            output.extend(multibyte_buffer)
            multibyte_buffer.clear()
            output.append(character)
            nonlocal is_in_multibyte
            is_in_multibyte = False
            nonlocal multibytes_expected
            multibytes_expected = 0
        else:
            raise ValueError(f"Expected multibyte continuation at index: {index}")
            
    for idx, c in enumerate(input_string):
        code_point = ord(c)
        if code_point <= 0x7f or code_point > 0xf4:  # ASCII Range data or higher than you get for mis-encoded utf-8:
            if not is_in_multibyte:
                output.append(c)  # not in a multibyte, valid ascii-range data, so we append
            else:
                handle_bad_data(idx, c)
        else:  # potentially utf-8
            if (code_point & 0xc0) == 0x80:  # continuation byte
                if is_in_multibyte:
                    multibyte_buffer.append(c)
                else:
                    handle_bad_data(idx, c)
            else:  # start-byte
                if not is_in_multibyte:
                    assert multibytes_expected == 0
                    assert len(multibyte_buffer) == 0
                    while (code_point & 0x80) != 0:
                        multibytes_expected += 1
                        code_point <<= 1
                    multibyte_buffer.append(c)
                    is_in_multibyte = True
                else:
                    handle_bad_data(idx, c)
                    
        if is_in_multibyte and len(multibyte_buffer) == multibytes_expected:  # output utf-8 character if complete
            utf_8_character = bytes(ord(x) for x in multibyte_buffer).decode("utf-8")
            output.append(utf_8_character)
            multibyte_buffer.clear()
            is_in_multibyte = False
            multibytes_expected = 0
            mis_encoded_utf8_present = True
        
    if multibyte_buffer:  # if we have left-over data
        handle_bad_data(len(input_string), "")
    
    return mis_encoded_utf8_present, "".join(output)

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return(finaltime)

def get_biomeIntents(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    files_found = sorted(files_found)
    
    for file_found in files_found:
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                pass
        else:
            continue
        
        data_list = []
        data_list_tsv = []
        
        with open(file_found, 'rb') as file:
            data = file.read()
            
            b = data
            ab = BytesIO(b)
            
            #header area
            first8bytes = ab.read(8)
            
            sometimestamp = ab.read(8)
            #sometimestamp = (struct.unpack_from("<d",sometimestamp)[0])
            
            unknownint = ab.read(4)
            #unknownint = (struct.unpack_from("<i",unknownint)[0])
            
            filenameh = ab.read(15)
            #print(filenameh.decode()) #needs . between 9 & 10 char. Cocoa
            
            whoknows = ab.read(17)
            
            segbheader = ab.read(4)
            
            
            while True:
                datalenght = ab.read(4)
                breakfull = 0
                try:
                    datalenght = (struct.unpack_from("<I",datalenght)[0])
                except:
                    breakfull = 1
                
                if breakfull == 1:
                    break
                
                if datalenght == 0:
                    break
                
                dataflag = ab.read(4)
                dataflag = (struct.unpack_from("<I",dataflag)[0])
                
                uknowntime1 = ab.read(8)
                uknowntime1 = (struct.unpack_from("<d",uknowntime1)[0])
                
                uknowntime2 = ab.read(8)
                uknowntime2 = (struct.unpack_from("<d",uknowntime2)[0])
                
                ab.read(4) #unknown
                
                dataflag2 = ab.read(4)
                dataflag2 = (struct.unpack_from("<I",dataflag2)[0])
                
                offset = ab.tell()
                protostuff = ab.read(datalenght)
                
                if dataflag == 3:
                    protostuff = 'Deleted'
                else:
                    with open(os.path.join(report_folder, str(filename) + '-' + str(offset)), 'wb') as wr:
                        wr.write(protostuff)
                        
                    protostuff, types = blackboxprotobuf.decode_message(protostuff)
                    
                if protostuff == 'Deleted':
                    pass
                else:
                    
                    #print(protostuff['1'], 'proto1') apple absolute time. Needs to be turned to double and then datetime. No need for it so far.
                    
                    typeofintent = protostuff.get('2','')
                    try:
                        typeofintent = typeofintent.decode()
                    except:
                        break
                    appid = typeofintent
                    
                    #print(protostuff['3']) #always says intents
                    
                    classname = (protostuff.get('4',''))
                    try:
                        classname = classname.decode()
                    except:
                        pass
                    
                    if protostuff.get('5') is not None:
                        action = protostuff.get('5')
                    else:
                        action = protostuff.get('5')
                    #print(protostuff['6']) #unknown
                    #print(protostuff['7']) #unknown
                    
                    deserialized_plist = nd.deserialize_plist_from_string(protostuff['8'])
                    
                    with open(os.path.join(report_folder, str(filename) + '-' + str(offset) + '.bplist'), 'wb') as wr:
                        wr.write(protostuff['8']) #keep here
                        
                    with open(os.path.join(report_folder, str(filename) + '-' + str(offset) + '.des_bplist'), 'w') as wr:
                        wr.write(str(deserialized_plist))
                    
                    #print(deserialized_plist)
                    startdate = (deserialized_plist['dateInterval']['NS.startDate'])
                    startdate = convert_time_obj_to_utc(startdate)
                    startdate = convert_utc_human_to_timezone(startdate, timezone_offset)
                    
                    enddate = (deserialized_plist['dateInterval']['NS.endDate'])
                    enddate = convert_time_obj_to_utc(enddate)
                    enddate = convert_utc_human_to_timezone(enddate, timezone_offset)
                    
                    durationinterval = (deserialized_plist['dateInterval']['NS.duration'])
                    #print(deserialized_plist['intent'])
                    donatedbysiri = (deserialized_plist['_donatedBySiri'])
                    groupid = (deserialized_plist['groupIdentifier'])
                    ident = (deserialized_plist['identifier'])
                    direction = (deserialized_plist['direction'])
                    if direction == 0:
                        direction = 'Unspecified'
                    elif direction == 1:
                        direction == 'Outgoing'
                    elif direction == 2:
                        direction = 'Incoming'
                        
                    protostuffinner = (deserialized_plist['intent']['backingStore']['bytes'])
                    protostuffinner, types = blackboxprotobuf.decode_message(protostuffinner)
                    
                    
                    #Instagram
                    if typeofintent == 'com.burbn.instagram':
                        datoshtml = deserialized_plist['intent']['backingStore']['bytes'].decode('latin-1')
                        datos = datoshtml
                    
                    #snapchat
                    elif typeofintent == 'com.toyopagroup.picaboo':
                        datoshtml = deserialized_plist['intent']['backingStore']['bytes'].decode('latin-1')
                        datos = datoshtml
                        
                    #notes
                    elif typeofintent == 'com.apple.assistant_service':
                        datoshtml = deserialized_plist['intent']['backingStore']['bytes'].decode('latin-1')
                        datos = datoshtml
                        
                    #notes
                    elif typeofintent == 'com.apple.mobilenotes':
                        a = (protostuffinner['1']['16'].decode()) #create
                        b = (protostuffinner['2']['1']) #message
                        c = (protostuffinner['2']['2']) #message
                        
                        datos = f'Action: {a}, Data Field 1: {b}, Data Field 2: {c}'
                        datoshtml = (datos.replace(',', '<br>'))
                        
                    #telegraph
                    elif typeofintent == 'ph.telegra.Telegraph':
                        datoshtml = deserialized_plist['intent']['backingStore']['bytes'].decode('latin-1')
                        datos = datoshtml
                        
                    #calls
                    elif typeofintent == 'com.apple.InCallService':
                        #print(protostuffinner)
                        try:
                            a = (protostuffinner['5']['1']['4'].decode()) #content number
                        except:
                            pass
                            #print(protostuffinner)
                        
                        datos = f'Number: {a}'
                        datoshtml = (datos.replace(',', '<br>'))
                    
                    #whatsapp
                    elif typeofintent == 'net.whatsapp.WhatsApp':
                        datoshtml = str(protostuffinner)
                        datos = datoshtml
                        
                    elif typeofintent == 'org.whispersystems.signal':
                        datoshtml = str(protostuffinner)
                        datos = datoshtml
                    
                    #sms
                    elif typeofintent == 'com.apple.MobileSMS':
                        if protostuffinner.get('5', '') != '':
                            if type(protostuffinner['5']['1']['2']) is not dict:
                                a = protostuffinner['5']['1']['2'].decode()
                            else:
                                a = protostuffinner['5']['1']['2']
                            
                            #a = (protostuffinner['5']['1']['2']) #content
                            
                            b = (protostuffinner.get('8', ''))#threadid
                            
                            c = (protostuffinner.get('15', ''))#senderid if not binary show dict
                            try:
                                d = (protostuffinner['2']['1']['4'])
                            except:
                                d = ''
                                
                            datos = f'Thread ID: {b}, Sender ID: {c}, Content:, {a}'
                            datoshtml = (datos.replace(',', '<br>'))
                        else:
                            print('Mobile SMS' + str(protostuffinner))
                    #maps
                    elif typeofintent == 'com.apple.Maps':
                        #print(protostuffinner)
                        if (protostuffinner['4'][0]['2']['2']['2']) == b'com.apple.Maps':
                            a = (protostuffinner['3'].decode()) #action
                            b = (protostuffinner['1']['16'].decode()) #value
                            
                            c = (protostuffinner['4'][0]['1'].decode())#source
                            d = (protostuffinner['4'][0]['2']['2']['2'].decode()) #value of above
                            
                            e = (protostuffinner['4'][1]['1'].decode()) #nav_identifier
                            f = (protostuffinner['4'][1]['2']['2']['2'].decode()) #value of above
                            
                            g = (protostuffinner['4'][2]['1'].decode()) #navigation_type
                            h = (protostuffinner['4'][2]['2']['2']['2'].decode()) #value of above
                            
                            datos = f'{a}: {b}, {c}: {d}, {e}: {f}, {g}: {h}'
                            datoshtml = (datos.replace(',', '<br>'))
                            
                        else:
                            datos = ''
                            a = (protostuffinner['3'].decode()) #action
                            b = (protostuffinner['1']['16'].decode()) #value
                            
                            datos = datos + f'{a}: {b},'
                            
                            for loopy in protostuffinner['4']:
                                a = loopy['1'].decode()
                                try:
                                    b = loopy['2']['2']['2']
                                except:
                                    b = loopy['2']
                                datos = datos + f'{a}: {b},'
                                
                            datoshtml = (datos.replace(',', '<br>'))
                        
                            #logfunc('Maps' + str(protostuffinner))
                        
                    else:
                        datos = ''
                        datoshtml = 'Unsupported intent.'
                        
                    data_list.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction,groupid, datoshtml, filename, offset))
                    data_list_tsv.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction, groupid, datos, filename, offset))
                    
                modresult = (datalenght % 8)
                resultante =  8 - modresult
                
                if modresult == 0:
                    pass
                else:
                    ab.read(resultante)
        
        if len(data_list) > 0:
        
            description = 'App Intents. Protobuf data for unsupported apps is located in the Intents directory within the report folder. Use the offset name for identification and further processing.'
            report = ArtifactHtmlReport(f'Intents')
            report.start_artifact_report(report_folder, f'Biome Intents - {filename}', description)
            report.add_script()
            data_headers = ('Timestamp','End Date','Duration Interval','Donated by Siri','App ID','Classname','Action', 'Direction', 'Group ID', 'Data', 'Filename', 'Protobuf data Offset')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = f'Biome Intents - {filename}'
            tsv(report_folder, data_headers, data_list_tsv, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
            
            tlactivity = f'Biome Intents - {filename}'
            timeline(report_folder, tlactivity, data_list_tsv, data_headers)
        else:
            logfunc(f'No data available for Biome Intents')
    

__artifacts__ = {
    "Intents": (
        "Biome Intents",
        ('*/mobile/Library/Biome/streams/public/AppIntent/local/*','*/AppIntent/local/*'),
        get_biomeIntents)
}