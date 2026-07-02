""" geodMapTiles """
__artifacts_v2__ = {
    "geodMapTiles": {
        "name": "GeoD Maptiles",
        "description": "Parses Map Tile Records from Apple geod Cache",
        "author": "@ydkhatri",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-06-17",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('**/MapTiles.sqlitedb*'),
        "output_types": "standard",
        "artifact_icon": "map"
    }
}

import gzip
import struct
import sqlite3
import zlib
from io import BytesIO

from PIL import Image
from pillow_heif import register_heif_opener
from scripts.filetype import guess_mime
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    does_table_exist_in_db,
    logfunc,
    open_sqlite_db_readonly
)


def read_vloc(data):
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


def parse_tcol(data):
    '''returns tuple (VMP4 places, VLOC places)'''
    tcol_places = []
    data_size = len(data)
    if data_size < 8:
        return [], []

    tcol_data_offset = struct.unpack('<I', data[4:8])[0]
    tcol_compressed_data = data[tcol_data_offset:]
    if tcol_compressed_data:
        try:
            tcol_places = gzip.decompress(tcol_compressed_data)
            #print("VLOC ->", tcol_places)
        except (OSError, EOFError, zlib.error) as ex:
            logfunc('Gzip decompression error from ParseTCOL() - ' + str(ex))
            tcol_places = ''
    vmp4_places = parse_vmp4(data[8:tcol_data_offset])
    return vmp4_places, read_vloc(tcol_places)


def parse_vmp4(data):
    if len(data) < 8:
        return []

    num_items = struct.unpack('<H', data[6:8])[0]
    pos = 8
    for x in range(num_items):
        if pos + 10 > len(data):
            break
        item_type, offset, size = struct.unpack("<HII", data[pos:pos + 10])
        if item_type == 10:
            item_data = data[offset:offset + size]
            if not item_data:
                return []
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


def check_in_tile_image(source_file, data, name):
    mime_type = guess_mime(data)
    if not (mime_type and mime_type.startswith('image/')):
        return None

    if mime_type == 'image/heic':
        try:
            register_heif_opener()
            with Image.open(BytesIO(data)) as image:
                converted = BytesIO()
                image.convert('RGB').save(converted, format='JPEG')
                data = converted.getvalue()
                mime_type = 'image/jpeg'
                force_extension = 'jpg'
        except (OSError, ValueError) as ex:
            logfunc(f'Failed to convert HEIC map tile image, using original. Error was: {ex}')
            force_extension = None
    else:
        force_extension = None

    return check_in_embedded_media(
        source_file, data, name, force_type=mime_type, force_extension=force_extension)


@artifact_processor
def geodMapTiles(context):
    """ see artifact description """
    file_found = ''
    data_headers = (
        ("Timestamp", "datetime"), "Places_from_VLOC", "Labels_in_tile",
        ("Image", "media", "max-height:240px; max-width:320px;"), "Tileset",
        "Key A", "Key B", "Key C", "Key D"
    )#, "Size", "ETAG")

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            break
    else:
        logfunc('No MapTiles.sqlitedb file found.')
        return (), [], ''
        
    #os.chmod(file_found, 0o0777)
    db = open_sqlite_db_readonly(file_found)
    if not db:
        return (), [], file_found

    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    if does_table_exist_in_db(file_found, 'tiles') and does_table_exist_in_db(file_found, 'data'):
        logfunc('Parsing Geolocation from data table with tiles table.')
        query = '''
            SELECT
                datetime(access_times.timestamp, 'unixepoch') as timestamp,
                key_a, key_b, key_c, key_d, tileset, data, size, etag
            FROM data
            INNER JOIN tiles on data.ROWID = tiles.data_pk
            INNER JOIN access_times on data.rowid = access_times.data_pk
            '''
    elif does_table_exist_in_db(file_found, 'data'):
        logfunc('Parsing Geolocation from data table.')
        query = '''
            SELECT
                datetime(access_times.timestamp, 'unixepoch') as timestamp,
                key_a, key_b, key_c, key_d, tileset, data, size, etag
            FROM data
            INNER JOIN access_times on data.rowid = access_times.data_pk
            '''
    elif does_table_exist_in_db(file_found, 'image'):
        logfunc('Parsing Geolocation from image table.')
        query = '''
            SELECT
                datetime(retrieved, 'unixepoch') as timestamp,
                a as key_a,
                b as key_b,
                c as key_c,
                d as key_d,
                tileset,
                data,
                size,
                etag
            FROM image
            '''
    else:
        logfunc('No supported Map Tiles tables found. No data available.')
        db.close()
        return (), [], file_found

    try:
        cursor.execute(query)
    except sqlite3.Error as ex:
        logfunc(f'Table is missing columns. No data available. Error was: {ex}')
        db.close()
        return (), [], file_found

    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    if len(all_rows) > 0:
        for row in all_rows:
            tcol_places = ''
            vmp4_places = ''
            data_parsed = ''
            data = row['data']
            if data: # NULL sometimes
                name = f"Map Tile {get_hex(row['tileset'])} {get_hex(row['key_a'])}-{get_hex(row['key_b'])}"
                data_parsed = check_in_tile_image(file_found, data, name)
                if not data_parsed and len(data) >= 4 and data[:4] == b'TCOL':
                    vmp4_places, tcol_places = parse_tcol(data)
                    vmp4_places = ", ".join(vmp4_places)
                    tcol_places = ", ".join(tcol_places)
                elif not data_parsed and len(data) >= 4 and data[:4] == b'VMP4':
                    vmp4_places = parse_vmp4(data)
                    vmp4_places = ", ".join(vmp4_places)

            row_data = (
                row['timestamp'], tcol_places, vmp4_places, data_parsed,
                get_hex(row['tileset']), get_hex(row['key_a']), get_hex(row['key_b']),
                get_hex(row['key_c']), get_hex(row['key_d'])
            )
            data_list.append(row_data)

    return data_headers, data_list, file_found
