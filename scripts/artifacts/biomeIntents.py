__artifacts_v2__ = {
    "get_biomeIntents": {
        "name": "Biome Intents",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Intents",
        "notes": "",
        "paths": ('*/AppIntent/local/*'),
        "output_types": "none",
        "function": "get_biomeIntents"
    }
}


import os
import blackboxprotobuf
import nska_deserialize as nd
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, timeline, convert_utc_human_to_timezone, convert_time_obj_to_utc
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data


def get_biomeIntents(files_found, report_folder, seeker, wrap_text, timezone_offset):

    category = "Biome Intents"
    module_name = "get_biomeIntents"
    data_headers = ('Timestamp', 'End Date', 'Duration Interval', 'Donated by Siri', 'App ID', 'Classname', 'Action',
                    'Direction', 'Group ID', 'Data', 'Filename', 'Protobuf data Offset')
    lava_data_headers = (('Timestamp', 'datetime'), ('End Date', 'datetime'), 'Duration Interval', 'Donated by Siri',
                         'App ID', 'Classname', 'Action', 'Direction', 'Group ID', 'Data', 'Filename',
                         'Protobuf data Offset')
    files_found = sorted(files_found)

    data_list = []
    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue

        file_data_list_tsv = []
        file_data_list = []
        for record in read_segb_file(file_found):
            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data)
                offset = record.data_start_offset

                #Write raw protobuf to file
                with open(os.path.join(report_folder, str(filename) + '-' + str(offset)), 'wb') as wr:
                    wr.write(record.data)

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

                #Write bplist to file
                with open(os.path.join(report_folder, str(filename) + '-' + str(offset) + '.bplist'), 'wb') as wr:
                    wr.write(protostuff['8']) #keep here

                #Write deserialized bplist to file
                with open(os.path.join(report_folder, str(filename) + '-' + str(offset) + '.des_bplist'), 'w') as wr:
                    wr.write(str(deserialized_plist))


                startdate = (deserialized_plist['dateInterval']['NS.startDate'])
                startdate = convert_time_obj_to_utc(startdate)
                startdate = convert_utc_human_to_timezone(startdate, timezone_offset)

                enddate = (deserialized_plist['dateInterval']['NS.endDate'])
                enddate = convert_time_obj_to_utc(enddate)
                enddate = convert_utc_human_to_timezone(enddate, timezone_offset)

                durationinterval = (deserialized_plist['dateInterval']['NS.duration'])
                donatedbysiri = 'True' if deserialized_plist['_donatedBySiri'] else 'False'
                groupid = (deserialized_plist['groupIdentifier'])
                ident = (deserialized_plist['identifier'])
                direction = (deserialized_plist['direction'])
                if direction == 0:
                    direction = 'Unspecified'
                elif direction == 1:
                    direction = 'Outgoing'
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

                file_data_list.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction,groupid, datoshtml, filename, offset))
                file_data_list_tsv.append((startdate, enddate, durationinterval, donatedbysiri, appid, classname, action, direction, groupid, datos, filename, offset))

        data_list.extend(file_data_list)

        # File based reports for legacy HTML
        if len(file_data_list) > 0:
            description = ('App Intents. Protobuf data for unsupported apps is located in the Intents directory within '
                           'the report folder. Use the offset name for identification and further processing.')
            report = ArtifactHtmlReport(f'Intents')
            report.start_artifact_report(report_folder, f'Biome Intents - {filename}', description)
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()

            tsvname = f'Biome Intents - {filename}'
            tsv(report_folder, data_headers, file_data_list_tsv, tsvname) # TODO: _csv.Error: need to escape, but no escapechar set

            tlactivity = f'Biome Intents - {filename}'
            timeline(report_folder, tlactivity, file_data_list_tsv, data_headers)

    # Single table for LAVA output
    table_name, object_columns, column_map = lava_process_artifact(category, module_name,
                                                                   'Biome Intents',
                                                                   lava_data_headers,
                                                                   len(data_list))

    lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)