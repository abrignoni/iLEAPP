__artifacts_v2__ = {
    "geodMapTiles": {
        "name": "GeoD Maptiles",
        "description": "Parses Map Tile Records from Apple geod Cache",
        "author": "@ydkhatri",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Geolocation",
        "notes": "",
        "paths": ('**/MapTiles.sqlitedb*'),
        "output_types": ['lava', 'tsv', 'timeline']
    }
}

import base64
import gzip
import struct
import sqlite3
import zlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, does_table_exist_in_db, artifact_processor


def ReadVLOC(data):
    names = []
    total_len = len(data)
    pos = 8
    while pos < total_len:
        if data[pos] < 0x80:
            skip_len = 2
        else:
            skip_len = 3
        end_pos = data[pos+skip_len:].find(b'\0')
        if end_pos >= 0:
            name = data[pos + skip_len : pos + skip_len + end_pos].decode('utf8', 'ignore')
            if name:
                names.append(name)
            pos += skip_len + end_pos + 1
        else:
            break
    return names


def ParseTCOL(data):
    '''returns tuple (VMP4 places, VLOC places)'''
    tcol_places = []
    data_size = len(data)
    if data_size >=8:
        tcol_data_offset = struct.unpack('<I', data[4:8])[0]
        tcol_compressed_data = data[tcol_data_offset:]
        if tcol_compressed_data:
            try:
                tcol_places = gzip.decompress(tcol_compressed_data)
                #print("VLOC ->", tcol_places)
            except (OSError, EOFError, zlib.error) as ex:
                logfunc('Gzip decompression error from ParseTCOL() - ' + str(ex))
                tcol_places = ''
        vmp4_places = ParseVMP4(data[8:tcol_data_offset])
        return vmp4_places, ReadVLOC(tcol_places)


def ParseVMP4(data):
    num_items = struct.unpack('<H', data[6:8])[0]
    pos = 8
    for x in range(num_items):
        item_type, offset, size = struct.unpack("<HII", data[pos:pos + 10])
        if item_type == 10:
            item_data = data[offset:offset + size]
            if item_data[0] == 1:
                compressed_data = item_data[5:]
                try:
                    places_data = zlib.decompress(compressed_data)
                except zlib.error as ex:
                    logfunc('Zlib decompression error from ParseVMP4() - ' + str(ex))
                    places_data = ''
            else:
                places_data = item_data[1:]
            #print("VMP4 ->", places_data.rstrip(b'\0').split(b'\0'))
            return [x.decode('UTF8', 'ignore') for x in places_data.rstrip(b'\0').split(b'\0')]
        pos += 10
    return []


def get_hex(num):
    if num:
        return hex(num).upper()
    return ''


@artifact_processor
def geodMapTiles(files_found, report_folder, seeker, wrap_text, timezone_offset):

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlitedb'):
            break
        
    #os.chmod(file_found, 0o0777)
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    usesDataTable = True
    
    if does_table_exist_in_db(file_found, 'tiles') and does_table_exist_in_db(file_found, 'data'):
        logfunc('Parsing Geolocation from data table with tiles table.')
        query = '''
            SELECT datetime(access_times.timestamp, 'unixepoch') as timestamp, key_a, key_b, key_c, key_d, tileset, data, size, etag
            FROM data
            INNER JOIN tiles on data.ROWID = tiles.data_pk
            INNER JOIN access_times on data.rowid = access_times.data_pk
            '''
    elif does_table_exist_in_db(file_found, 'data'):
        logfunc('Parsing Geolocation from data table.')        
        query = '''
            SELECT datetime(access_times.timestamp, 'unixepoch') as timestamp, key_a, key_b, key_c, key_d, tileset, data, size, etag
            FROM data
            INNER JOIN access_times on data.rowid = access_times.data_pk
            '''
    else:
        logfunc('Parsing Geolocation from image table.')
        usesDataTable = False
        query = '''
            SELECT datetime(retrieved, 'unixepoch') as timestamp, a, b, c, d, tileset, data, size, etag
            FROM image
            '''
    try:
        cursor.execute(query)
    except Exception as e:
        print(e)
        logfunc('Table is missing columns. No data available.')
        return

    all_rows = cursor.fetchall()
    data_list = []
    if len(all_rows) > 0:
        for row in all_rows:
            tcol_places = ''
            vmp4_places = ''
            data_parsed = ''
            data = row['data']
            if data: # NULL sometimes
                if len(data) >= 11 and data[:11] == b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00':
                    img_base64 = base64.b64encode(data).decode('utf-8')
                    img_html = f'<img src="data:image/jpeg;base64, {img_base64}" alt="Map Tile" />'
                    data_parsed = img_html
                elif len(data) >= 4 and data[:4] == b'TCOL':
                    vmp4_places, tcol_places = ParseTCOL(data)
                    vmp4_places = ", ".join(vmp4_places)
                    tcol_places = ", ".join(tcol_places)
                elif len(data) >=4 and data[:4] == b'VMP4':
                    vmp4_places = ParseVMP4(data)
                    vmp4_places = ", ".join(vmp4_places)
            #else:
                #header_bytes = data[:28]
                #hexdump = generate_hexdump(header_bytes, 5) if header_bytes else ''
                #data_parsed = hexdump

            if usesDataTable:
                data_list.append((row['timestamp'], tcol_places, vmp4_places, data_parsed, get_hex(row['tileset']), 
                                    get_hex(row['key_a']), get_hex(row['key_b']), get_hex(row['key_c']), get_hex(row['key_d'])) )
                                    # row['size']) , row['etag']))
            else:                                    
                data_list.append((row['timestamp'], tcol_places, vmp4_places, data_parsed, get_hex(row['tileset']), 
                                    get_hex(row['a']), get_hex(row['b']), get_hex(row['c']), get_hex(row['d'])) )
                                    # row['size']) , row['etag']))

        description = ''
        report = ArtifactHtmlReport('Geolocation')
        report.start_artifact_report(report_folder, 'Map Tile Cache', description)
        report.add_script()
        data_headers = ["Timestamp", "Places_from_VLOC", "Labels_in_tile", "Image", "Tileset", "Key A", "Key B", "Key C", "Key D"]#, "Size", "ETAG")
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape = False)
        report.end_artifact_report()

    db.close()

    data_headers[0] = (data_headers[0], 'datetime')

    # remove the image from lava output until Media Manager is ready
    data_list = [(row[0], row[1], row[2], 'See HTML Report', row[4], row[5], row[6], row[7], row[8])
                 if row[3] else row for row in data_list]
    return data_headers, data_list, file_found