# common standard imports
import codecs
import csv
from datetime import *
import os
import pathlib
import re
import shutil
import sqlite3
import sys
from functools import lru_cache
from pathlib import Path

# common third party imports
import magic
import pytz
import simplekml
from bs4 import BeautifulSoup

# LEAPP version unique imports
import binascii
import math
import string
from PIL import Image


os.path.basename = lru_cache(maxsize=None)(os.path.basename)

thumbnail_root = '**/Media/PhotoData/Thumbnails/**/'
media_root = '**/Media/'
thumb_size = 256, 256

class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''

    def __init__(self, output_folder):
        now = datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder,
                                               'iLEAPP_Reports_' + currenttime)  # aleapp , aleappGUI, ileap_artifacts, report.py
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs',
                                                                'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs',
                                                                        'DeviceInfo.html')

        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def convert_time_obj_to_utc(ts):
    timestamp = ts.replace(tzinfo=timezone.utc)
    return timestamp

def convert_utc_human_to_timezone(utc_time, time_offset): 
    #fetch the timezone information
    timezone = pytz.timezone(time_offset)
    
    #convert utc to timezone
    timezone_time = utc_time.astimezone(timezone)
    
    #return the converted value
    return timezone_time

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return(finaltime)

def convert_ts_human_to_utc(ts): #This is for timestamp in human form
    if '.' in ts:
        ts = ts.split('.')[0]
        
    dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') #Make it a datetime object
    timestamp = dt.replace(tzinfo=timezone.utc) #Make it UTC
    return timestamp

def convert_ts_int_to_utc(ts): #This int timestamp to human format & utc
    timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
    return timestamp

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

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

def sanitize_file_path(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed. Does not replace \ or /
    '''
    return re.sub(r'[*?:"<>|\'\r\n]', replacement_char, filename)

def sanitize_file_name(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed.
    '''
    return re.sub(r'[\\/*?:"<>|\'\r\n]', replacement_char, filename)

def get_next_unused_name(path):
    '''Checks if path exists, if it does, finds an unused name by appending -xx
       where xx=00-99. Return value is new path.
       If it is a file like abc.txt, then abc-01.txt will be the next
    '''
    folder, basename = os.path.split(path)
    ext = None
    if basename.find('.') > 0:
        basename, ext = os.path.splitext(basename)
    num = 1
    new_name = basename
    if ext != None:
        new_name += f"{ext}"
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = basename + "-{:02}".format(num)
        if ext != None:
            new_name += f"{ext}"
        num += 1
    return os.path.join(folder, new_name)

def open_sqlite_db_readonly(path):
    '''Opens an sqlite db in read-only mode, so original db (and -wal/journal are intact)'''
    if is_platform_windows():
        if path.startswith('\\\\?\\UNC\\'): # UNC long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\?\\'):    # normal long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\'):       # UNC path
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                               # normal path
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def does_column_exist_in_db(db, table_name, col_name):
    '''Checks if a specific col exists'''
    col_name = col_name.lower()
    try:
        db.row_factory = sqlite3.Row # For fetching columns by name
        query = f"pragma table_info('{table_name}');"
        cursor = db.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        for row in all_rows:
            if row['name'].lower() == col_name:
                return True
    except sqlite3.Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
        pass
    return False

def does_table_exist(db, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        cursor = db.execute(query)
        for row in cursor:
            return True
    except sqlite3Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
    return False

def does_view_exist(db, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='view' AND name='{table_name}'"
        cursor = db.execute(query)
        for row in cursor:
            return True
    except sqlite3Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
    return False

class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None  # static variable
    progress_bar_total = 0
    progress_bar_handle = None

    @staticmethod
    def SetProgressBar(n):
        if GuiWindow.progress_bar_handle:
            GuiWindow.progress_bar_handle.UpdateBar(n)

def logfunc(message=""):
    with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
        print(message)
        a.write(message + '<br>' + OutputParameters.nl)

    if GuiWindow.window_handle:
        GuiWindow.window_handle.refresh()

def logdevinfo(message=""):
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        b.write(message + '<br>' + OutputParameters.nl)

def tsv(report_folder, data_headers, data_list, tsvname):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')

    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)
    
    
    with codecs.open(os.path.join(tsv_report_folder, tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter='\t')
        tsv_writer.writerow(data_headers)
        for i in data_list:
            tsv_writer.writerow(i)
            
def timeline(report_folder, tlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tl_report_folder = os.path.join(report_folder_base, '_Timeline')

    if os.path.isdir(tl_report_folder):
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(tl_report_folder)
        # create database
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb, isolation_level = 'exclusive')
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE data(key TEXT, activity TEXT, datalist TEXT)
            """
        )
        db.commit()
    
    a = 0
    length = (len(data_list))
    while a < length: 
        modifiedList = list(map(lambda x, y: x.upper() + ': ' +  str(y), data_headers, data_list[a]))
        cursor.executemany("INSERT INTO data VALUES(?,?,?)", [(str(data_list[a][0]), tlactivity.upper(), str(modifiedList))])
        a += 1
    db.commit()
    db.close()

def kmlgen(report_folder, kmlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    kml_report_folder = os.path.join(report_folder_base, '_KML Exports')
    if os.path.isdir(kml_report_folder):
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(kml_report_folder)
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(key TEXT, latitude TEXT, longitude TEXT, activity TEXT)
        """
            )
        db.commit()
    
    kml = simplekml.Kml(open=1)
    
    a = 0
    length = (len(data_list))
    while a < length:
        modifiedDict = dict(zip(data_headers, data_list[a]))
        times = modifiedDict.get('Timestamp','N/A')
        lon = modifiedDict['Longitude']
        lat = modifiedDict['Latitude']
        if lat:
            pnt = kml.newpoint()
            pnt.name = times
            pnt.description = f"Timestamp: {times} - {kmlactivity}"
            pnt.coords = [(lon, lat)]
            cursor.execute("INSERT INTO data VALUES(?,?,?,?)", (times, lat, lon, kmlactivity))
        a += 1
    db.commit()
    db.close()
    kml.save(os.path.join(kml_report_folder, f'{kmlactivity}.kml'))
    
''' Returns string of printable characters. Replacing non-printable characters
with '.', or CHR(46)
``'''
def strings_raw(data):
    return "".join([chr(byte) if byte >= 0x20 and byte < 0x7F else chr(46) for byte in data])

''' Returns string of printable characters. Works similar to the Linux
`string` function.
'''
def strings(data):
    cleansed = "".join([chr(byte) if byte >= 0x20 and byte < 0x7F else chr(0) for byte in data])
    return filter(lambda string: len(string) >= 4, cleansed.split(chr(0)))

''' Retuns HTML table of the hexdump of the passed in data.
'''
def generate_hexdump(data, char_per_row = 5):
    data_hex = binascii.hexlify(data).decode('utf-8')
    str_raw = strings_raw(data)
    str_hex = ''
    str_ascii = ''

    ''' Generates offset column
    '''
    offset_rows = math.ceil(len(data_hex)/(char_per_row * 2))
    offsets = [i for i in  range(0, len(data_hex), char_per_row)][:offset_rows]
    str_offset = '<br>'.join([ str(hex(s)[2:]).zfill(4).upper() for s in offsets ])

    ''' Generates hex data column
    '''
    c = 0
    for i in range(0, len(data_hex), 2):
        str_hex += data_hex[i:i + 2] + '&nbsp;'

        if c == char_per_row - 1:
            str_hex += '<br>'
            c = 0
        else:
            c += 1

    ''' Generates ascii column of data
    '''
    for i in range(0, len(str_raw), char_per_row):
        str_ascii += str_raw[i:i + char_per_row] + '<br>'

    return f'''
    <table id="GeoLocationHexTable" aria-describedby="GeoLocationHexTable" cellspacing="0">
    <thead>
        <tr>
        <th style="border-right: 1px solid #000;border-bottom: 1px solid #000;">Offset</th>
        <th style="width: 100px; border-right: 1px solid #000;border-bottom: 1px solid #000;">Hex</th>
        <th style="border-bottom: 1px solid #000;">Ascii</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td style="white-space:nowrap; border-right: 1px solid #000;">{str_offset}</td>
    <td style="border-right: 1px solid #000; white-space:nowrap;">{str_hex}</td>
    <td style="white-space:nowrap;">{str_ascii}</td>
    </tr></tbody></table>
    '''

'''
searching for thumbnails, copy it to report folder and return tag  to insert in html
'''
def generate_thumbnail(imDirectory, imFilename, seeker, report_folder):
    thumb = thumbnail_root+imDirectory+'/'+imFilename+'/'
    thumblist = seeker.search(thumb+'**.JPG', return_on_first_hit=True)
    thumbname = imDirectory.replace('/','_')+'_'+imFilename+'.JPG'
    pathToThumb = os.path.join(os.path.basename(os.path.abspath(report_folder)), thumbname)
    htmlThumbTag = '<img src="{0}"></img>'.format(pathToThumb)
    if thumblist:
        shutil.copyfile(thumblist[0],os.path.join(report_folder, thumbname))
    else:
        #recreate thumbnail from image
        #TODO: handle videos and HEIC
        files = seeker.search(media_root+imDirectory+'/'+imFilename, return_on_first_hit=True)
        if files:
            try:
                im = Image.open(files[0])
                im.thumbnail(thumb_size)
                im.save(os.path.join(report_folder, thumbname))
            except:
                pass #unsupported format
    return htmlThumbTag

def media_to_html(media_path, files_found, report_folder):

    def media_path_filter(name):
        return media_path in name

    def relative_paths(source, splitter):
        splitted_a = source.split(splitter)
        for x in splitted_a:
            if 'LEAPP_Reports_' in x:
                report_folder = x

        splitted_b = source.split(report_folder)
        return '.' + splitted_b[1]

    platform = is_platform_windows()
    if platform:
        media_path = media_path.replace('/', '\\')
        splitter = '\\'
    else:
        splitter = '/'

    thumb = media_path
    for match in filter(media_path_filter, files_found):
        filename = os.path.basename(match)
        if filename.startswith('~') or filename.startswith('._') or filename != media_path:
            continue

        dirs = os.path.dirname(report_folder)
        dirs = os.path.dirname(dirs)
        env_path = os.path.join(dirs, 'temp')
        if env_path in match:
            source = match
            source = relative_paths(source, splitter)
        else:
            path = os.path.dirname(match)
            dirname = os.path.basename(path)
            filename = Path(match)
            filename = filename.name
            locationfiles = Path(report_folder).joinpath(dirname)
            Path(f'{locationfiles}').mkdir(parents=True, exist_ok=True)
            shutil.copy2(match, locationfiles)
            source = Path(locationfiles, filename)
            source = relative_paths(str(source), splitter)

        mimetype = magic.from_file(match, mime=True)

        if 'video' in mimetype:
            thumb = f'<video width="320" height="240" controls="controls"><source src="{source}" type="video/mp4" preload="none">Your browser does not support the video tag.</video>'
        elif 'image' in mimetype:
            thumb = f'<a href="{source}" target="_blank"><img src="{source}"width="300"></img></a>'
        elif 'audio' in mimetype:
            thumb = f'<audio controls><source src="{source}" type="audio/ogg"><source src="{source}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
        else:
            thumb = f'<a href="{source}" target="_blank"> Link to {filename} file</>'
    return thumb


def get_resolution_for_model_id(model_id: str):
    data = [
        {'Model ID': 'iPhone16,2', 'Model Name': 'iPhone 15 Pro Max', 'Width': 1290, 'Height': 2796},
        {'Model ID': 'iPhone16,1', 'Model Name': 'iPhone 15 Pro', 'Width': 1179, 'Height': 2556},
        {'Model ID': 'iPhone15,5', 'Model Name': 'iPhone 15 Plus', 'Width': 1290, 'Height': 2796},
        {'Model ID': 'iPhone15,4', 'Model Name': 'iPhone 15', 'Width': 1179, 'Height': 2556},
        {'Model ID': 'iPhone14,8', 'Model Name': 'iPhone 14 Plus', 'Width': 1284, 'Height': 2778},
        {'Model ID': 'iPhone15,3', 'Model Name': 'iPhone 14 Pro Max', 'Width': 1290, 'Height': 2796},
        {'Model ID': 'iPhone15,2', 'Model Name': 'iPhone 14 Pro', 'Width': 1179, 'Height': 2556},
        {'Model ID': 'iPhone14,7', 'Model Name': 'iPhone 14', 'Width': 1170, 'Height': 2532},
        {'Model ID': 'iPhone14,6', 'Model Name': 'iPhone SE 3rd gen', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone14,5', 'Model Name': 'iPhone 13', 'Width': 1170, 'Height': 2532},
        {'Model ID': 'iPhone14,4', 'Model Name': 'iPhone 13 mini', 'Width': 1080, 'Height': 2340},
        {'Model ID': 'iPhone14,3', 'Model Name': 'iPhone 13 Pro Max', 'Width': 1284, 'Height': 2778},
        {'Model ID': 'iPhone14,2', 'Model Name': 'iPhone 13 Pro', 'Width': 1170, 'Height': 2532},
        {'Model ID': 'iPhone13,2', 'Model Name': 'iPhone 12', 'Width': 1170, 'Height': 2532},
        {'Model ID': 'iPhone13,1', 'Model Name': 'iPhone 12 mini', 'Width': 1080, 'Height': 2340},
        {'Model ID': 'iPhone13,4', 'Model Name': 'iPhone 12 Pro Max', 'Width': 1284, 'Height': 2778},
        {'Model ID': 'iPhone13,3', 'Model Name': 'iPhone 12 Pro', 'Width': 1170, 'Height': 2532},
        {'Model ID': 'iPhone12,8', 'Model Name': 'iPhone SE 2nd gen', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone12,5', 'Model Name': 'iPhone 11 Pro Max', 'Width': 1242, 'Height': 2688},
        {'Model ID': 'iPhone12,3', 'Model Name': 'iPhone 11 Pro', 'Width': 1125, 'Height': 2436},
        {'Model ID': 'iPhone12,1', 'Model Name': 'iPhone 11', 'Width': 828, 'Height': 1792},
        {'Model ID': 'iPhone11,8', 'Model Name': 'iPhone XR', 'Width': 828, 'Height': 1792},
        {'Model ID': 'iPhone11,6', 'Model Name': 'iPhone XS Max', 'Width': 1242, 'Height': 2688},
        {'Model ID': 'iPhone11,2', 'Model Name': 'iPhone XS', 'Width': 1125, 'Height': 2436},
        {'Model ID': 'iPhone10,6', 'Model Name': 'iPhone X', 'Width': 1125, 'Height': 2436},
        {'Model ID': 'iPhone10,3', 'Model Name': 'iPhone X', 'Width': 1125, 'Height': 2436},
        {'Model ID': 'iPhone10,5', 'Model Name': 'iPhone 8 Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone10,2', 'Model Name': 'iPhone 8 Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone10,4', 'Model Name': 'iPhone 8', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone10,1', 'Model Name': 'iPhone 8', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone9,4', 'Model Name': 'iPhone 7 Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone9,2', 'Model Name': 'iPhone 7 Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone9,3', 'Model Name': 'iPhone 7', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone9,1', 'Model Name': 'iPhone 7', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone8,4', 'Model Name': 'iPhone SE 1st gen', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone8,2', 'Model Name': 'iPhone 6s Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone8,1', 'Model Name': 'iPhone 6s', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone7,1', 'Model Name': 'iPhone 6 Plus', 'Width': 1080, 'Height': 1920},
        {'Model ID': 'iPhone7,2', 'Model Name': 'iPhone 6', 'Width': 750, 'Height': 1334},
        {'Model ID': 'iPhone5,3', 'Model Name': 'iPhone 5C', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone5,4', 'Model Name': 'iPhone 5C', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone6,1', 'Model Name': 'iPhone 5S', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone6,2', 'Model Name': 'iPhone 5S', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone5,1', 'Model Name': 'iPhone 5', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone5,2', 'Model Name': 'iPhone 5', 'Width': 640, 'Height': 1136},
        {'Model ID': 'iPhone4,1', 'Model Name': 'iPhone 4S', 'Width': 640, 'Height': 960},
        {'Model ID': 'iPhone3,1', 'Model Name': 'iPhone 4', 'Width': 640, 'Height': 960},
        {'Model ID': 'iPhone3,2', 'Model Name': 'iPhone 4', 'Width': 640, 'Height': 960},
        {'Model ID': 'iPhone3,3', 'Model Name': 'iPhone 4', 'Width': 640, 'Height': 960},
        {'Model ID': 'iPhone2,1', 'Model Name': 'iPhone 3GS', 'Width': 320, 'Height': 480},
        {'Model ID': 'iPhone1,2', 'Model Name': 'iPhone 3G', 'Width': 320, 'Height': 480},
        {'Model ID': 'iPhone1,1', 'Model Name': 'iPhone 1st gen', 'Width': 320, 'Height': 480},
        {'Model ID': 'iPad14,5', 'Model Name': 'iPad Pro (6th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad14,6', 'Model Name': 'iPad Pro (6th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad14,3', 'Model Name': 'iPad Pro (4th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad14.4', 'Model Name': 'iPad Pro (4th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad13,18', 'Model Name': 'iPad 10th gen', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad13,19', 'Model Name': 'iPad 10th gen', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad13,17', 'Model Name': 'iPad Air (5th gen)', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad13,16', 'Model Name': 'iPad Air (5th gen)', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad12,1', 'Model Name': 'iPad 9th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad12,2', 'Model Name': 'iPad 9th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad13,8', 'Model Name': 'iPad Pro (5th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad13,9', 'Model Name': 'iPad Pro (5th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad13,10', 'Model Name': 'iPad Pro (5th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad13,11', 'Model Name': 'iPad Pro (5th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad13,4', 'Model Name': 'iPad Pro (5th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad13,5', 'Model Name': 'iPad Pro (5th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad13,6', 'Model Name': 'iPad Pro (5th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad13,7', 'Model Name': 'iPad Pro (5th gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad13,1', 'Model Name': 'iPad Air (4th gen)', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad13,2', 'Model Name': 'iPad Air (4th gen)', 'Width': 1640, 'Height': 2360},
        {'Model ID': 'iPad11,6', 'Model Name': 'iPad 8th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad11,7', 'Model Name': 'iPad 8th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad8,11', 'Model Name': 'iPad Pro (4th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,12', 'Model Name': 'iPad Pro (4th gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,9', 'Model Name': 'iPad Pro (2nd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad8,10', 'Model Name': 'iPad Pro (2nd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad7,11', 'Model Name': 'iPad 7th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad7,12', 'Model Name': 'iPad 7th gen', 'Width': 1620, 'Height': 2160},
        {'Model ID': 'iPad14,1', 'Model Name': 'iPad Mini (6th gen)', 'Width': 1488, 'Height': 2266},
        {'Model ID': 'iPad14,2', 'Model Name': 'iPad Mini (6th gen)', 'Width': 1488, 'Height': 2266},
        {'Model ID': 'iPad11,1', 'Model Name': 'iPad Mini (5th gen)', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad11,2', 'Model Name': 'iPad Mini (5th gen)', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad11,3', 'Model Name': 'iPad Air (3rd gen)', 'Width': 1668, 'Height': 2224},
        {'Model ID': 'iPad11,4', 'Model Name': 'iPad Air (3rd gen)', 'Width': 1668, 'Height': 2224},
        {'Model ID': 'iPad8,5', 'Model Name': 'iPad Pro (3rd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,6', 'Model Name': 'iPad Pro (3rd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,7', 'Model Name': 'iPad Pro (3rd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,8', 'Model Name': 'iPad Pro (3rd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad8,1', 'Model Name': 'iPad Pro (3rd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad8,2', 'Model Name': 'iPad Pro (3rd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad8,3', 'Model Name': 'iPad Pro (3rd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad8,4', 'Model Name': 'iPad Pro (3rd gen 11")', 'Width': 1668, 'Height': 2388},
        {'Model ID': 'iPad7,5', 'Model Name': 'iPad 6th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad7,6', 'Model Name': 'iPad 6th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad7,1', 'Model Name': 'iPad Pro (2nd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad7,2', 'Model Name': 'iPad Pro (2nd gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad7,3', 'Model Name': 'iPad Pro (2nd gen 10.5")', 'Width': 1668, 'Height': 2224},
        {'Model ID': 'iPad7,4', 'Model Name': 'iPad Pro (2nd gen 10.5")', 'Width': 1668, 'Height': 2224},
        {'Model ID': 'iPad6,11', 'Model Name': 'iPad 5th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad6,12', 'Model Name': 'iPad 5th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad6,3', 'Model Name': 'iPad Pro (1st gen 9.7”)', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad6,4', 'Model Name': 'iPad Pro (1st gen 9.7”)', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad6,7', 'Model Name': 'iPad Pro (1st gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad6,8', 'Model Name': 'iPad Pro (1st gen 12.9")', 'Width': 2048, 'Height': 2732},
        {'Model ID': 'iPad5,1', 'Model Name': 'iPad mini 4', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad5,2', 'Model Name': 'iPad mini 4', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad5,3', 'Model Name': 'iPad Air 2', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad5,4', 'Model Name': 'iPad Air 2', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,7', 'Model Name': 'iPad mini 3', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,8', 'Model Name': 'iPad mini 3', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,9', 'Model Name': 'iPad mini 3', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,4', 'Model Name': 'iPad mini 2', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,5', 'Model Name': 'iPad mini 2', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,6', 'Model Name': 'iPad mini 2', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,1', 'Model Name': 'iPad Air', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,2', 'Model Name': 'iPad Air', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad4,3', 'Model Name': 'iPad Air', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad3,4', 'Model Name': 'iPad 4th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad3,5', 'Model Name': 'iPad 4th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad3,6', 'Model Name': 'iPad 4th gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad2,5', 'Model Name': 'iPad mini', 'Width': 768, 'Height': 1024},
        {'Model ID': 'iPad2,6', 'Model Name': 'iPad mini', 'Width': 768, 'Height': 1024},
        {'Model ID': 'iPad2,7', 'Model Name': 'iPad mini', 'Width': 768, 'Height': 1024},
        {'Model ID': 'iPad3,1', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad3,2', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad3,3', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad2,1', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad2,2', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad2,3', 'Model Name': 'iPad 3rd gen', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad1,1', 'Model Name': 'iPad 1st gen', 'Width': 768, 'Height': 1024}]

    for entry in data:
        if entry.get('Model ID').lower() == model_id.lower():
            return entry
    logfunc(
        f"Warning! - Resolution not found for '{model_id}', contact developers to add resolution into the get_resolution_for_model_id function")
    return None


def convert_bytes_to_unit(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return size

