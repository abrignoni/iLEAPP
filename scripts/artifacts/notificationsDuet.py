from io import StringIO
from io import BytesIO
import os
import struct
from datetime import datetime
from time import mktime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

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
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return(finaltime)

def get_notificationsDuet(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
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
    
        convertedtime1 = guid = title = subtitle = bundledata = bodyread = bundleidread = optionaltextread = bundleid2read = optionalgmarkeread = appleidread = convertedtime2 =  ''
        
        with open(file_found, 'rb') as file:
            data = file.read()
        
        data_list = []    
        headerloc = data.index(b'SEGB')
        #print(headerloc)
        
        b = data
        ab = BytesIO(b)
        ab.seek(headerloc)
        ab.read(4) #Main header
        #print('---- Start of Notifications ----')
        
        while True:
            #print('----')
            sizeofnotificatoninhex = (ab.read(4))
            try:
                sizeofnotificaton = (struct.unpack_from("<i",sizeofnotificatoninhex)[0])
            except:
                break
            if sizeofnotificaton == 0:
                break
            notificatonmessage = (ab.read(sizeofnotificaton + 28))
            
            #print(sizeofnotificatoninhex)
            #print(sizeofnotificaton)
            #print(notificatonmessage)
            
            notification = notificatonmessage
            mensaje = BytesIO(notification)
            
            mensaje.read(4) #Notification Header
            
            date1 = mensaje.read(8) #Date in hex
            #print(f'Date1: {date1}')
            date1 = (struct.unpack_from("<d",date1)[0])
            convertedtime1 = timestampsconv(date1)
            #print(convertedtime1)
            
            mensaje.read(27)
            """ #Revisit to get date out.
            date2 = mensaje.read(8) #Date in hex
            #print(f'Date2: {date2}')
            for x in date2:
                #print(hex(x))
            date2 = (struct.unpack_from("<d",date2)[0])
            convertedtime2 = timestampsconv(date2)
            #print(convertedtime2)
            """
            test = mensaje.read(1)
            if test == b'\x12':
                mensaje.read(1) #byte length guid
            else:
                mensaje.read(2) #1st byte indicator 2nd byte length to sweep. Both standard.
                
            guid = mensaje.read(36)
            guid = (guid.decode('latin-1'))
            #print(guid)
            
            checktitle = mensaje.read(1) #Title marker
            if checktitle == b'\x1a':
                #print('there is x1a')
                titlelength = mensaje.read(1)
                #print(titlelength)
                if titlelength >= b'\x80':
                    mensaje.read(1)
                lengthtoread = (int(titlelength.hex(), 16))
                #print(lengthtoread)
                title = mensaje.read(lengthtoread)
                
                title = (title.decode('latin-1'))
                
                title = (utf8_in_extended_ascii(title)[1])
                #print(f'Title: {title}')
                checksubtitle = mensaje.read(1)
            else:
                checksubtitle = checktitle
            if  checksubtitle == b'\x22':
                #print('there is x22')
                checksubtitlelength = mensaje.read(1)
                #print(checksubtitlelength)
                if checksubtitlelength >= b'\x80':
                    mensaje.read(1)
                subtitlelengthtoread = (int(checksubtitlelength.hex(), 16))
                #print(subtitlelengthtoread )
                subtitle = mensaje.read(subtitlelengthtoread )
                subtitle = (subtitle.decode('latin-1'))
                subtitle= (utf8_in_extended_ascii(subtitle)[1])
                #print(f'Subtitle: {subtitle}')
                bodylenght = mensaje.read(1)
            else:
                body = checktitle
                #print(f'Checktitle: {body}')
                
            bodylenght = mensaje.read(1)
            #print(f'Body lenght: {bodylenght}')
            #print(f'File tell:{mensaje.tell()}')
            
            if b'\x80' <= bodylenght <= b'\x8F' :
                factor = mensaje.read(1)
                factor = (int(factor.hex(), 16))
                
                #print(f'Factor: {factor}')
                if factor == 1:
                    bodytoread = (int(bodylenght.hex(), 16))
                    bodytoread = bodytoread * factor
                else:
                    byted = (bodylenght.hex())
                    
                    values = []
                    for byte in byted:
                        byte = int(byte, 16)
                        high, low = byte >> 4, byte & 0x0F
                        #print(hex(high), hex(low))
                        values.append(low)
                        
                    #print(values[0], values[1]) 
                    #calculation
                    firstorder = values[0] * 16
                    secondorder = values[1] * 1
                    
                    basenumber = firstorder * factor
                    sweep = basenumber + secondorder
                    
                    bodytoread = sweep
                    
                    
            elif bodylenght > b'\x8F':
                #print(f'Mayor body lenght: {bodylenght}')
                offsetbody = mensaje.tell()
                #print(f'Offset mensaje: {offsetbody}')
                
                abcd = notificatonmessage.index(b'\x30\x00\x42')
                #print(f"Notificationmensaje index offset: {abcd}")
                #print(f'Notification seek offset: {notification.tell()}')
                bodytoread = abcd - offsetbody
                
            else:
                bodytoread = (int(bodylenght.hex(), 16))
                
            #print(f'Body to read afuera: {bodytoread}')
            
            if bodylenght == b'\x00':
                bundlelen = mensaje.read(1)
                bundlelen = mensaje.read(1)
                #print(bundlelen)
                bundlelen = (int(bundlelen.hex(), 16))
                bundledata = mensaje.read(bundlelen)
                bundledata  = (bundledata.decode('latin-1'))
                bundledata = (utf8_in_extended_ascii(bundledata)[1])
                #print(f'Bundle ID: {bundledata}')
                optionaltextcheck = mensaje.read(3)
                #print(f'Optional cuando mensaje es 00: {optionaltextcheck}')
            else:
                
                bodyread= mensaje.read(bodytoread)
                bodyread = (bodyread.decode('latin-1'))
                bodyread = (utf8_in_extended_ascii(bodyread)[1])
                #print(f'Body to read len: {len(bodyread)}')
                #print(f'Body: {bodyread}\n')
                
                bundleheader = mensaje.read(3)
                #print(f'Bundle header: {bundleheader}')
                
                bundleidtoread = mensaje.read(1)
                bundleidtoread = (int(bundleidtoread.hex(), 16))
                bundleidread = mensaje.read(bundleidtoread)
                bundleidread  = (bundleidread.decode('latin-1'))
                bundleidread = (utf8_in_extended_ascii(bundleidread)[1])
                #print(f'Bundle ID: {bundleidread}')
                
                optionaltextcheck = mensaje.read(3)
                #print(f'OPtional text header A: {optionaltextcheck}')
            bundle2lenght = ''
            if optionaltextcheck == b'\x4A\x00\x52':
                #print('In x52')
                optionaltextlength = mensaje.read(1)
                optionaltextlength = (int(optionaltextlength.hex(), 16))
                optionaltextread = mensaje.read(optionaltextlength)
                optionaltextread = (optionaltextread.decode('latin-1'))
                boptionaltextread = (utf8_in_extended_ascii(optionaltextread)[1])
                #print(f'Optional Text: {optionaltextread}')
                bundle2header = mensaje.read(1) #Always x62
                bundle2lenght = mensaje.read(1) #lenght
                
            if optionaltextcheck == b'\x4A\x00\x62':
                #print('in X62')
                bundle2lenght = mensaje.read(1)
                
            if bundle2lenght != '':
                bundle2lenght = (int(bundle2lenght.hex(), 16))
                bundleid2read = mensaje.read(bundle2lenght)
                bundleid2read  = (bundleid2read.decode('latin-1'))
                bundleid2read = (utf8_in_extended_ascii(bundleid2read)[1])
                #print(f'Bundle ID 2: {bundleid2read}\n')
                
            optionalgmarker = mensaje.read(1) #unknown bytes
            if optionalgmarker == b'\x6A':
                optionalgmarkerlen = mensaje.read(1)
                optionalgmarkerlen = (int(optionalgmarkerlen.hex(), 16))
                optionalgmarkeread = mensaje.read(optionalgmarkerlen)
                optionalgmarkeread  = (optionalgmarkeread.decode('latin-1'))
                optionalgmarkeread= (utf8_in_extended_ascii(optionalgmarkeread)[1])
                #print(f'Optional GUID: {optionalgmarkeread}')
                mensaje.read(20)
            else:
                mensaje.read(19)
                
            checkappleid = mensaje.read(2)
            if checkappleid == b'\xA2\x01':
                appleidread = ''
                while True:
                    appleidlen = mensaje.read(1)
                    appleidlen = (int(appleidlen.hex(), 16))
                    appleidread = mensaje.read(appleidlen)
                    appleidread  = (appleidread .decode('latin-1'))
                    appleidread = (utf8_in_extended_ascii(appleidread)[1])
                    #print(f'Apple ID: {appleidread}')
                    appleidread = appleidread + ' ' + appleidread
                    innercheck = mensaje.read(2)
                    if innercheck == b'\xA2\x01':
                        pass
                    else:
                        mensaje.read(1)
                        break
            else:
                mensaje.read(3)
                
            lastdate = mensaje.read(8)
            #print(lastdate)
            date2 = (struct.unpack_from("<d",lastdate)[0])
            convertedtime2 = timestampsconv(date2)
            #print(f'Date2: {convertedtime2}')
            data_list.append((convertedtime1,guid,title,subtitle,bundledata,bodyread,bundleidread,optionaltextread,bundleid2read,optionalgmarkeread,appleidread,convertedtime2, filename))
            
            convertedtime1 = guid = title = subtitle = bundledata = bodyread = bundleidread = optionaltextread = bundleid2read = optionalgmarkeread = appleidread = convertedtime2 =  ''
            
            modresult = (sizeofnotificaton % 8)
            resultante =  8 - modresult
            
            if modresult == 0:
                pass
            else:
                ab.read(resultante)
                #print("--------")
                
            
    

        if len(data_list) > 0:
        
            description = ''
            report = ArtifactHtmlReport(f'Notifications Duet')
            report.start_artifact_report(report_folder, f'Notifications Duet - {filename}', description)
            report.add_script()
            data_headers = ('Timestamp','GUID','Title','Subtitle','Bundle Data','Body','Bundle ID', 'Optional Text', 'Bundle ID', 'Optional GUID', 'Apple ID', 'Timestamp', 'Filename')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Notifications Duet - {filename}'
            tsv(report_folder, data_headers, data_list, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set
        else:
            logfunc(f'No data available for Notifications Duet')
    

__artifacts__ = {
    "notificationsDuet": (
        "Notifications",
        ('*/DuetExpertCenter/streams/userNotificationEvents/local/*', '*/userNotificationEvents/local/*'),
        get_notificationsDuet)
}