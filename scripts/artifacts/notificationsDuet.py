from io import StringIO
from io import BytesIO
import os
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def getoffsets(hexvalue, readdata):
    index_pos = 0
    offsetlist = []
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            index_pos = readdata.index(hexvalue, index_pos)
            # Add the index position in list
            offsetlist.append(index_pos)
            index_pos = index_pos + 1
        except ValueError as e:
            break
        
    return offsetlist

def get_notificationsDuet(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = os.path.basename(file_found)
        
        with open(file_found, 'rb') as file:
            data = file.read()
            
            messagestarts= getoffsets(b'\x00\x01\x00\x00\x00', data)
            
            #print(messagestarts)
            #print(len(messagestarts))
            
        internaloff = {'guid': b'\x12\x24', 'phone': b'\x00\xa2\x01', 'phone2': b'\x00R\x0c','guid2': b'\x6A\x24','user': b'\x1A','message': b'\x2A', 'message2': b'\x2A\x16','bundle': b'\x62\x13', 'bundle2': b'\x42\x18', 'bundle3': b'\x62\x15', 'bundle4': b'\x62\x16'}
        
        bundlefinals = ''
        messagefinals = ''
        phonefinals = ''
        guidfinals = ''
        userfinals = ''
        guid = ''
        guid2 = ''
        for y, x in enumerate(messagestarts):
            b = data
            ab = BytesIO(b)
            ab.seek(x)
            
            if y == 2517:
                stoppingpoint = 256
            else:
                stopingpoint = messagestarts[y+1]
                stopingpoint = stopingpoint - x
                
            data_cuto = ab.read(stopingpoint)
            
            #print(data_cuto)
            #print()
            
            
            for llave, valor in internaloff.items():
                
                #attributes GUID
                data_cut = data_cuto
                
                offset = (data_cut.find(valor))
                
                data_cut = BytesIO(data_cut)
                #print(offset)
                if offset < 0:
                    pass
                    #print(f'No {llave} Value')
                else:
                    val = (data_cut.seek(offset))
                    nbytes = ord(data_cut.read(1))
                    nbytes = ord(data_cut.read(1))
                    
                    if llave == 'phone' or llave == 'phone2':
                        data_message = data_cut.read(14) #phones only
                    else:
                        data_message = data_cut.read(nbytes) #for not phones
                    data_message = data_message.decode('latin-1').replace('\n','') 
                    #print(f'{llave} Value = {data_message}')
                    
                    if llave.startswith('bun'):
                        bundlefinals = bundlefinals + ',' + data_message
                    if llave.startswith('message'):
                        messagefinals = messagefinals + '^' + data_message 
                    if llave.startswith('phone'):
                        phonefinals = phonefinals + '^' + data_message  
                    if llave == 'guid':
                        guid =  data_message
                    if llave == 'guid2':
                        guid2 =  data_message  
                    if llave.startswith('user'):
                        userfinals = userfinals + '^' + data_message 
                        
            data_list.append((filename, userfinals[1:],messagefinals[1:], bundlefinals[1:], phonefinals[1:], guid, guid2, data_cuto))
            bundlefinals = ''
            messagefinals = ''
            phonefinals = ''
            guidfinals = ''
            userfinals = ''
            
    

    if len(data_list) > 0:
    
        description = ''
        report = ArtifactHtmlReport('Notifications Duet')
        report.start_artifact_report(report_folder, 'Notifications Duet', description)
        report.add_script()
        data_headers = ('Filename','Usernames','Messages','Bundles','Phones','GUID 1','GUID 2', 'Raw Notification')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Notifications Duet'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No data available for Notifications Duet')
    


    