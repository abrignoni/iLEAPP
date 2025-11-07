__artifacts_v2__ = {
    "get_biomeIntents": {
        "name": "Biome - Intents",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-10-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/AppIntent/local/*'),
        "html_columns": ["Data"],
        "output_types": "standard",
    }
}

import os
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import convert_time_obj_to_utc, get_plist_content, logfunc, artifact_processor

@artifact_processor
def get_biomeIntents(context):
    data_headers = (('Timestamp', 'datetime'), ('End Date', 'datetime'), 'Duration Interval', 'Donated by Siri',
                         'App ID', 'Classname', 'Action', 'Direction', 'Group ID', 'Data', 'Filename',
                         'Protobuf data Offset')
    files_found = context.get_files_found()
    files_found = sorted(files_found)

    data_list_html = []
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            if record.state == EntryState.Written:
                protostuff, _ = blackboxprotobuf.decode_message(record.data)
                offset = record.data_start_offset

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

                #deserialized_plist = nd.deserialize_plist_from_string(protostuff['8'])
                deserialized_plist = get_plist_content(protostuff['8'])
                if not deserialized_plist or not isinstance(deserialized_plist, dict):
                    logfunc('Problemitas')
                    continue

                startdate = (deserialized_plist['dateInterval']['NS.startDate'])
                startdate = convert_time_obj_to_utc(startdate)

                enddate = (deserialized_plist['dateInterval']['NS.endDate'])
                enddate = convert_time_obj_to_utc(enddate)

                durationinterval = (deserialized_plist['dateInterval']['NS.duration'])
                donatedbysiri = 'True' if deserialized_plist['_donatedBySiri'] else 'False'
                groupid = (deserialized_plist['groupIdentifier'])
                #ident = (deserialized_plist['identifier'])
                direction = (deserialized_plist['direction'])
                if direction == 0:
                    direction = 'Unspecified'
                elif direction == 1:
                    direction = 'Outgoing'
                elif direction == 2:
                    direction = 'Incoming'

                protostuffinner = (deserialized_plist['intent']['backingStore']['bytes'])
                protostuffinner, _ = blackboxprotobuf.decode_message(protostuffinner)


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

                data_list_html.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction, groupid, datoshtml, filename, offset))
                data_list.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction, groupid, datos, filename, offset))
    
    return data_headers, (data_list, data_list_html), 'see Filename for more info'