import sqlite3
import textwrap
import blackboxprotobuf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_recursively(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []
    
    for key, value in search_dict.items():
        
        if key == field:
            fields_found.append(value)
            
        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)
                
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)
                        
    return fields_found

def get_mapsSync(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('MapsSync_0.0.1'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(ZHISTORYITEM.ZCREATETIME+978307200,'UNIXEPOCH','localtime') AS 'Time Created',
        datetime(ZHISTORYITEM.ZMODIFICATIONTIME+978307200,'UNIXEPOCH','localtime') AS 'Time Modified',
        ZHISTORYITEM.z_pk AS 'Item Number',
        CASE
        when ZHISTORYITEM.z_ent = 14 then 'coordinates of search'
        when ZHISTORYITEM.z_ent = 16 then 'location search'
        when ZHISTORYITEM.z_ent = 12 then 'navigation journey'
        end AS 'Type',
        ZHISTORYITEM.ZQUERY AS 'Location Search',
        ZHISTORYITEM.ZLOCATIONDISPLAY AS 'Location City',
        ZHISTORYITEM.ZLATITUDE AS 'Latitude',
        ZHISTORYITEM.ZLONGITUDE AS 'Longitude',
        ZHISTORYITEM.ZROUTEREQUESTSTORAGE AS 'Journey BLOB',
        ZMIXINMAPITEM.ZMAPITEMSTORAGE as 'Map Item Storage BLOB'
        from ZHISTORYITEM
        left join ZMIXINMAPITEM on ZMIXINMAPITEM.Z_PK=ZHISTORYITEM.ZMAPITEM
        ''')
        
        # Above query courtesy of CheekyForensicsMonkey
        # https://cheeky4n6monkey.blogspot.com/2020/11/ios14-maps-history-blob-script.html
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                #print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                directa = ''
                directb = ''
                mapitem = ''
                agg1 = ''
                if row[8] is None:
                    pass
                #pp = pprint.PrettyPrinter(indent = 1)
                #pp.pprint(message)
                else:
                    message, types = blackboxprotobuf.decode_message(row[8])
                    
                    for x in message['1']:
                        for y in x['2']['1']['4']:
                            z = y.get('8')
                            if z == None:
                                pass
                            else:
                                if isinstance(z, dict):
                                    w = z.get('31')
                                    if w == None:
                                        pass
                                    else:
                                        three = get_recursively(w, '3')
                                        if three[1] == b'create':
                                            #print(f'Three: {three[1]}')
                                            if message['1'][1]['1'].get('2') is not None:
                                                for address in (message['1'][1]['1']['2']['6']):
                                                    directa = directa + ' ' + (address.decode('latin-1'))
                                                    #print(row[0],directa, 'directa')
                                                if agg1 == '':
                                                    agg1 = directa
                                                    directa = ''
                                                else:
                                                    agg1 = agg1 + ' <---> ' + directa
                                                    
                                            else:
                                                for address in (w['1']['101']['2']['11']):
                                                    directa = directa + ' ' + (address.decode('latin-1'))
                                                    #print(row[0], directb, 'directb')
                                                if agg1 == '':
                                                    agg1 = directa
                                                    directa = ''
                                                else:
                                                    agg1 = agg1 + ' <---> ' + directa
                                                    
                                                    
                                                    
                if row[9] is None:
                    pass
                else: 
                    message, types = blackboxprotobuf.decode_message(row[9])
                    #pp = pprint.PrettyPrinter(indent = 1)
                    #pp.pprint(message['1']['4'])#[7]['8']['31']['1']['101']['2']['11'])
                    get101 = (get_recursively(message, '101'))
                    
                    for address in (get101[0]['2']['11']):
                        mapitem = mapitem + ' ' + (address.decode('latin-1'))
                        
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], agg1, mapitem))
                agg1 = ''
            

        if usageentries > 0:
            description = 'Disclaimer: Entries should be corroborated. Locations and searches from other linked devices might show up here. Travel should be confirmed. Medium confidence.'
            report = ArtifactHtmlReport('MapsSync')
            report.start_artifact_report(report_folder, 'MapsSync', description)
            report.add_script()
            data_headers = ('Timestamp','Modified Time','Item Number','Type','Location Search','Location City','Latitude','Longitude','Journey BLOB Item', 'Map Item Storage BLOB item')
            
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'MapsSync'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'MapsSync'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'MapsSync'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
        else:
            logfunc('No MapsSync data available')