import csv
import datetime
import os
import pathlib
import re
import sys
import codecs
import sqlite3
import string
import binascii
import math
import simplekml
import shutil

from bs4 import BeautifulSoup
from PIL import Image

thumbnail_root = '**/Media/PhotoData/Thumbnails/**/'
media_root = '**/Media/'
thumb_size = 256, 256

class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''

    def __init__(self, output_folder):
        now = datetime.datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder, 'iLEAPP_Reports_' + currenttime) # aleapp , aleappGUI, ileap_artifacts, report.py
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs', 'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs', 'DeviceInfo.html')

        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

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
    return sqlite3.connect (f"file:{path}?mode=ro", uri=True)

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

class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None # static variable 
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
        #create database
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
        times = modifiedDict['Timestamp']
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
