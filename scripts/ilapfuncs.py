# common standard imports
import codecs
import csv
import hashlib
import inspect
import json
import math
import nska_deserialize
import os
import plistlib
import re
import shutil
import sqlite3
import sys
import xml

from datetime import *
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote
import scripts.artifact_report as artifact_report
from scripts.context import Context

# common third party imports
import pytz
import simplekml
from scripts.filetype import guess_mime, guess_extension
from functools import wraps

# LEAPP version unique imports
import binascii
from PIL import Image

from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data, lava_get_media_item, \
    lava_insert_sqlite_media_item, lava_insert_sqlite_media_references, lava_get_media_references, \
    lava_get_full_media_info

os.path.basename = lru_cache(maxsize=None)(os.path.basename)

thumbnail_root = '**/Media/PhotoData/Thumbnails/**/'
media_root = '**/Media/'
thumb_size = 256, 256

identifiers = {}
icons = {}
lava_only_artifacts = {}

class iOS:
    _version = None

    @staticmethod
    def get_version():
        """Return the value of the class property."""
        return iOS._version

    @staticmethod
    def set_version(os_version):
        """Assign a value to the class property once."""
        if iOS._version is None:
            iOS._version = os_version


class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''

    def __init__(self, output_folder, custom_folder_name=None):
        now = datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        if custom_folder_name:
            folder_name = custom_folder_name
        else:
            folder_name = 'iLEAPP_Reports_' + currenttime
        self.report_folder_base = os.path.join(output_folder, folder_name)
        self.data_folder = os.path.join(self.report_folder_base, 'data')
        OutputParameters.screen_output_file_path = os.path.join(
            self.report_folder_base, '_HTML', '_Script_Logs', 'Screen_Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(
            self.report_folder_base, '_HTML', '_Script_Logs', 'DeviceInfo.html')
        OutputParameters.screen_output_file_path_lava_only = os.path.join(
            self.report_folder_base, '_HTML', '_Script_Logs', 'Lava_only_artifacts_log.html')

        os.makedirs(os.path.join(self.report_folder_base, '_HTML', '_Script_Logs'))
        os.makedirs(self.data_folder)
        
class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None  # static variable

    @staticmethod
    def SetProgressBar(n, total):
        if GuiWindow.window_handle:
            progress_bar = GuiWindow.window_handle.nametowidget('!progressbar')
            progress_bar.config(value=n)

class MediaItem():
    def __init__(self, id):
        self.id = id
        self.source_path = ""
        self.extraction_path = ""
        self.mimetype = ""
        self.metadata = ""
        self.created_at = 0
        self.updated_at = 0
    
    def set_values(self, media_info):
        self.id = media_info[0]
        self.source_path = media_info[1]
        self.extraction_path = media_info[2]
        self.mimetype = media_info[3]
        self.metadata = media_info[4]
        self.created_at = media_info[5]
        self.updated_at = media_info[6]

class MediaReferences():
    def __init__(self, id):
        self.id = id
        self.media_item_id = ""
        self.module_name = ""
        self.artifact_name = ""
        self.name = ""
        self.media_path = ""
    
    def set_values(self, media_ref_info):
        self.id = media_ref_info[0]
        self.media_item_id = media_ref_info[1]
        self.module_name = media_ref_info[2]
        self.artifact_name = media_ref_info[3]
        self.name = media_ref_info[4]
        self.media_path = media_ref_info[5]


def logfunc(message=""):
    def redirect_logs(string):
        log_text.insert('end', string)
        log_text.see('end')
        log_text.update()

    if GuiWindow.window_handle:
        log_text = GuiWindow.window_handle.nametowidget('logs_frame.log_text')
        sys.stdout.write = redirect_logs

    if OutputParameters.screen_output_file_path:
        with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
            a.write(message + '<br>' + OutputParameters.nl)
    print(message)


def strip_tuple_from_headers(data_headers):
    return [header[0] if isinstance(header, tuple) else header for header in data_headers]

def get_media_header_info(data_headers):
    media_header_info = {}
    for index, header in enumerate(data_headers):
        if isinstance(header, tuple) and header[1] == 'media':
            style = header[2] if len(header) == 3 else ''
            media_header_info[index] = style
    return media_header_info

def check_output_types(type, output_types):
    if type in output_types or type == output_types or 'all' in output_types or 'all' == output_types:
        return True
    elif type != 'kml' and ('standard' in output_types or 'standard' == output_types):
        return True
    elif type == 'lava' and ('lava_only' in output_types or 'lava_only' == output_types):
        return True
    else:
        return False

def get_media_references_id(media_id, artifact_name, name):
    return hashlib.sha1(f"{media_id}-{artifact_name}-{name}".encode()).hexdigest()

def set_media_references(media_ref_id, media_id, module_name, artifact_name, name, media_path):
    media_references = MediaReferences(media_ref_id)
    media_references.set_values((
        media_ref_id, media_id, module_name, artifact_name, name, media_path
    ))
    lava_insert_sqlite_media_references(media_references)

def check_in_media(file_path, name="", converted_file_path=False):
    report_folder = Context.get_report_folder()
    seeker = Context.get_seeker()
    module_name = Context.get_module_name()
    artifact_name = Context.get_artifact_name()

    extraction_path = Context.get_source_file_path(file_path)

    if not extraction_path:
        logfunc(f'No matching file found for "{file_path}"')
        return None

    file_info = seeker.file_infos.get(extraction_path)
    if file_info:
        extraction_path = converted_file_path if converted_file_path else Path(extraction_path)
        if extraction_path.is_file():
            media_id = hashlib.sha1(f"{file_info.source_path}".encode()).hexdigest()
            media_ref_id = get_media_references_id(media_id, artifact_name, name)
            lava_media_ref = lava_get_media_references(media_ref_id)
            if lava_media_ref:
                return media_ref_id
            media_path = Path(report_folder).joinpath(media_ref_id).with_suffix(extraction_path.suffix)
            try:
                media_path.hardlink_to(extraction_path)
            except OSError:
                shutil.copy2(extraction_path, media_path)
            lava_media_item = lava_get_media_item(media_id)
            if not lava_media_item:
                media_item = MediaItem(media_id)
                media_item.source_path = file_info.source_path
                media_item.extraction_path = f"./{Path(report_folder).stem}/{media_ref_id}{extraction_path.suffix}"
                media_item.mimetype = guess_mime(extraction_path)
                media_item.metadata = "not implemented yet"
                media_item.created_at = file_info.creation_date
                media_item.updated_at = file_info.modification_date
                lava_insert_sqlite_media_item(media_item)
            set_media_references(media_ref_id, media_id, module_name, artifact_name, name, media_path)
            return media_ref_id
        else:
            logfunc(f"{extraction_path} is not a file")
            return None            
    else:
        logfunc(f'No matching file found for "{file_path}"')
        return None

def check_in_embedded_media(source_file, data, name=""):
    report_folder = Context.get_report_folder()
    seeker = Context.get_seeker()
    module_name = Context.get_module_name()
    artifact_name = Context.get_artifact_name()

    file_info = seeker.file_infos.get(source_file)
    source_path = file_info.source_path if file_info else source_file
    if data:
        media_id = hashlib.sha1(data).hexdigest()
        media_ref_id = get_media_references_id(media_id, artifact_name, name)
        lava_media_ref = lava_get_media_references(media_ref_id)
        if lava_media_ref:
            return media_ref_id
        media_path = Path(report_folder).joinpath(media_ref_id).with_suffix(f".{guess_extension(data)}")
        lava_media_item = lava_get_media_item(media_id)
        if not lava_media_item:
            media_item = MediaItem(media_id)
            media_item.source_path = source_path
            media_item.extraction_path = media_path
            media_item.mimetype = guess_mime(data)
            media_item.metadata = "not implemented yet"
            media_item.created_at = 0
            media_item.updated_at = 0
            try:
                with open(media_item.extraction_path, "wb") as file:
                    file.write(data)
            except Exception as ex:
                logfunc(f'Could not copy embedded media into {media_item.extraction_path} ' + str(ex))
            lava_insert_sqlite_media_item(media_item)
        set_media_references(media_ref_id, media_id, module_name, artifact_name, name, media_path)
        return media_ref_id
    else:
        return None

def html_media_tag(media_path, mimetype, style, title=''):
    def relative_paths(source):
        splitter = '\\' if is_platform_windows() else '/'
        first_split = source.split(splitter)
        for x in first_split:
            if 'data' in x:
                index = first_split.index(x)
                last_split = source.split(first_split[index - 1])
                return '..' + last_split[1].replace('\\', '/')
            elif '_HTML' in x:
                index = first_split.index(x)
                last_split = source.split(first_split[index])
                return '.' + last_split[1].replace('\\', '/')
        return source

    filename = Path(media_path).name
    media_path = quote(relative_paths(media_path))

    if mimetype == None:
        mimetype = ''
    if 'video' in mimetype:
        thumb = f'<video width="320" height="240" controls="controls"><source src="{media_path}" type="video/mp4" preload="none">Your browser does not support the video tag.</video>'
    elif 'image' in mimetype:
        image_style = style if style else "max-height:300px; max-width:400px;"
        thumb = f'<a href="{media_path}" target="_blank"><img title="{title}"  src="{media_path}" style="{image_style}"></img></a>'
    elif 'audio' in mimetype:
        thumb = f'<audio controls><source src="{media_path}" type="audio/ogg"><source src="{media_path}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
    else:
        thumb = f'<a href="{media_path}" target="_blank"> Link to {filename} file</>'
    return thumb

def get_data_list_with_media(media_header_info, data_list):
    ''' 
    For columns with media item, generate:
      - A data list with HTML code for HTML output
      - A data list with extraaction path of media items for TSV, KML and Timeline exports  
    '''
    html_data_list = []
    txt_data_list = []
    for data in data_list:
        html_data = list(data)
        txt_data = list(data)
        for idx, style in media_header_info.items():
            if html_data[idx]:
                media_ref_id = html_data[idx]
                if isinstance(media_ref_id, list):
                    html_code = ''
                    path_list = []
                    for item in media_ref_id:
                        media_item = lava_get_full_media_info(item)
                        html_code += html_media_tag(
                            media_item['media_path'], media_item['type'], style, media_item['name'])
                        path_list.append(media_item[6])
                    txt_code = ' | '.join(path_list)
                else:
                    media_item = lava_get_full_media_info(media_ref_id)
                    html_code = html_media_tag(media_item['media_path'], media_item['type'], style, media_item['name'])
                    txt_code = media_item[6]
                html_data[idx] = html_code
                txt_data[idx] = txt_code
            else:
                html_data[idx] = ''
                txt_data[idx] = ''
        html_data_list.append(tuple(html_data))
        txt_data_list.append(tuple(txt_data))
    return html_data_list, txt_data_list

def artifact_processor(func):
    @wraps(func)
    def wrapper(files_found, report_folder, seeker, wrap_text, timezone_offset):
        module_name = func.__module__.split('.')[-1]
        func_name = func.__name__
        module_file_path = inspect.getfile(func)

        all_artifacts_info = func.__globals__.get('__artifacts_v2__', {})
        artifact_info = all_artifacts_info.get(func_name, {})

        artifact_name = artifact_info.get('name', func_name)
        category = artifact_info.get('category', '')
        description = artifact_info.get('description', '')
        icon = artifact_info.get('artifact_icon', '')
        html_columns = artifact_info.get('html_columns', [])

        output_types = artifact_info.get('output_types', ['html', 'tsv', 'timeline', 'lava', 'kml'])
        is_lava_only = 'lava_only' in output_types

        Context.set_report_folder(report_folder)
        Context.set_seeker(seeker)
        Context.set_files_found(files_found)
        Context.set_artifact_info(artifact_info)
        Context.set_module_name(module_name)
        Context.set_module_file_path(module_file_path)
        Context.set_artifact_name(artifact_name)
        
        try:
            sig = inspect.signature(func)
            if len(sig.parameters) == 1:
                data_headers, data_list, source_path = func(Context)
            else:
                data_headers, data_list, source_path = func(files_found, report_folder, seeker, wrap_text, timezone_offset)
        finally:
            Context.clear()
        
        if not source_path:
            logfunc(f"No file found")

        elif len(data_list):
            if isinstance(data_list, tuple):
                data_list, html_data_list = data_list
            else:
                html_data_list = data_list
            logfunc(f"Found {len(data_list):,} {'records' if len(data_list)>1 else 'record'} for {artifact_name}")
            icons.setdefault(category, {artifact_name: icon}).update({artifact_name: icon})

            # Strip tuples from headers for HTML, TSV, and timeline
            stripped_headers = strip_tuple_from_headers(data_headers)

            # Check if headers contains a 'media' type
            media_header_info = get_media_header_info(data_headers)
            if media_header_info:
                html_columns.extend([data_headers[idx][0] for idx in media_header_info])
                html_data_list, txt_data_list = get_data_list_with_media(media_header_info, data_list)

            if check_output_types('html', output_types):
                report = artifact_report.ArtifactHtmlReport(artifact_name)
                report.start_artifact_report(report_folder, artifact_name, description)
                report.add_script()
                report.write_artifact_data_table(stripped_headers, html_data_list, source_path, html_no_escape=html_columns)
                report.end_artifact_report()

            if check_output_types('tsv', output_types):
                tsv(report_folder, stripped_headers, txt_data_list if media_header_info else data_list, artifact_name)

            if check_output_types('timeline', output_types):
                timeline(report_folder, artifact_name, txt_data_list if media_header_info else data_list, stripped_headers)

            if check_output_types('lava', output_types):
                table_name, object_columns, column_map = lava_process_artifact(category,
                                                                               module_name,
                                                                               artifact_name,
                                                                               data_headers,
                                                                               len(data_list),
                                                                               data_views=artifact_info.get("data_views"),
                                                                               artifact_icon=icon)
                if is_lava_only:
                    lava_only_info(category, artifact_name, table_name, len(data_list))
                lava_insert_sqlite_data(table_name, data_list, object_columns, data_headers, column_map)

            if check_output_types('kml', output_types):
                kmlgen(report_folder, artifact_name, txt_data_list if media_header_info else data_list, stripped_headers)

        else:
            if output_types != 'none':
                logfunc(f"No data found for {artifact_name}")
                if is_lava_only:
                    lava_only_info(category, artifact_name, artifact_name, 0)

        return data_headers, data_list, source_path
    return wrapper


def is_platform_linux():
    '''Returns True if running on Linux'''
    return sys.platform == 'linux'

def is_platform_macos():
    '''Returns True if running on macOS'''
    return sys.platform == 'darwin'

def is_platform_windows():
    '''Returns True if running on Windows'''
    return sys.platform == 'win32'

def sanitize_file_path(filename, replacement_char='_'):
    r'''
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


def get_file_path(files_found, filename, skip=False):
    """Returns the path of the searched filename if exists or returns None"""
    try:
        for file_found in files_found:
            if skip and skip in file_found:
                continue
            if Path(file_found).match(filename):
                return file_found
    except Exception as e:
        logfunc(f"Error: {str(e)}")
    return None        

def get_txt_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.readlines()
            return file_content
    except FileNotFoundError:
        logfunc(f"Error: File not found at {file_path}")
    except PermissionError:
        logfunc(f"Error: Permission denied when trying to read {file_path}")
    except Exception as e:
        logfunc(f"Unexpected error reading file {file_path}: {str(e)}")
    return []

def get_plist_content(data):
    try:
        plist_content = plistlib.loads(data)
        if plist_content.get('$archiver', '') == 'NSKeyedArchiver':
            return nska_deserialize.deserialize_plist_from_string(data)
        else:
            return plist_content
    except plistlib.InvalidFileException:
        logfunc(f"Error: Invalid plist data")
    except xml.parsers.expat.ExpatError:
        logfunc(f"Error: Malformed XML")
    except TypeError as e:
        logfunc(f"Error: Type error when parsing plist data: {str(e)}")
    except ValueError as e:
        logfunc(f"Error: Value error when parsing plist data: {str(e)}")
    except OverflowError as e:
        logfunc(f"Error: Overflow error when parsing plist data: {str(e)}")
    except nska_deserialize.DeserializeError:
        logfunc(f"Error: Invalid NSKeyedArchive plist data")
    except Exception as e:
        logfunc(f"Unexpected error reading plist data: {str(e)}")
    return {}

def get_plist_file_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            plist_content = plistlib.load(file)
            if plist_content.get('$archiver', '') == 'NSKeyedArchiver':
                return nska_deserialize.deserialize_plist(file_path)
            else:
                return plist_content
    except FileNotFoundError:
        logfunc(f"Error: Plist file not found at {file_path}")
    except PermissionError:
        logfunc(f"Error: Permission denied when trying to read {file_path}")
    except plistlib.InvalidFileException:
        logfunc(f"Error: Invalid plist file format in {file_path}")
    except xml.parsers.expat.ExpatError:
        logfunc(f"Error: Malformed XML in plist file {file_path}")
    except TypeError as e:
        logfunc(f"Error: Type error when parsing plist {file_path}: {str(e)}")
    except ValueError as e:
        logfunc(f"Error: Value error when parsing plist {file_path}: {str(e)}")
    except OverflowError as e:
        logfunc(f"Error: Overflow error when parsing plist {file_path}: {str(e)}")
    except nska_deserialize.DeserializeError:
        logfunc(f"Error: {file_path} is not a valid NSKeyedArchive plist file")
    except Exception as e:
        logfunc(f"Unexpected error reading plist file {file_path}: {str(e)}")
    return {}

def get_sqlite_db_path(path):
    if is_platform_windows():
        if str(path).startswith('\\\\?\\UNC\\'): # UNC long path
            return "%5C%5C%3F%5C" + path[4:]
        elif str(path).startswith('\\\\?\\'):    # normal long path
            return "%5C%5C%3F%5C" + path[4:]
        elif str(path).startswith('\\\\'):       # UNC path
            return "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                               # normal path
            return "%5C%5C%3F%5C" + path
    else:
        return path

def open_sqlite_db_readonly(path):
    '''Opens a sqlite db in read-only mode, so original db (and -wal/journal are intact)'''
    try:
        if path:
            path = get_sqlite_db_path(path)
            with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
                return db
    except sqlite3.OperationalError as e:
        logfunc(f"Error with {path}:")
        logfunc(f" - {str(e)}")
    return None

def attach_sqlite_db_readonly(path, db_name):
    '''Return the query to attach a sqlite db in read-only mode.
    path: str --> Path of the SQLite DB to attach
    db_name: str --> Name of the SQLite DB in the query'''
    path = get_sqlite_db_path(path)
    return  f'''ATTACH DATABASE "file:{path}?mode=ro" AS {db_name}'''

def get_sqlite_db_records(path, query, attach_query=None):
    db = open_sqlite_db_readonly(path)
    if db:
        db.row_factory = sqlite3.Row  # For fetching columns by name
        try:
            cursor = db.cursor()
            if attach_query:
                cursor.execute(attach_query)
            cursor.execute(query)
            records = cursor.fetchall()
            return records
        except sqlite3.OperationalError as e:
            logfunc(f"Error with {path}:")
            logfunc(f" - {str(e)}")
        except sqlite3.ProgrammingError as e:
            logfunc(f"Error with {path}:")
            logfunc(f" - {str(e)}")
    return []

def get_sqlite_multiple_db_records(path_list, query, data_headers):
    multiple_source_files = len(path_list) > 1
    source_path = ""
    data_list = []
    if multiple_source_files:
        data_headers = list(data_headers)
        data_headers.append('Source Path')
        data_headers = tuple(data_headers)
        source_path = 'file path in the report below'
    elif path_list:
        source_path = path_list[0]
    for file in path_list:
        db_records = get_sqlite_db_records(file, query)
        for record in db_records:
            if multiple_source_files:
                modifiable_record = list(record)
                modifiable_record.append(file)
                record = tuple(modifiable_record)
            data_list.append(record)
    return data_headers, data_list, source_path

def does_column_exist_in_db(path, table_name, col_name):
    '''Checks if a specific col exists'''
    db = open_sqlite_db_readonly(path)
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

def does_table_exist_in_db(path, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    db = open_sqlite_db_readonly(path)
    if db:    
        try:
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            cursor = db.execute(query)
            for row in cursor:
                return True
        except sqlite3.Error as ex:
            logfunc(f"Query error, query={query} Error={str(ex)}")
    return False

def does_view_exist_in_db(path, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    db = open_sqlite_db_readonly(path)
    if db:
        try:
            query = f"SELECT name FROM sqlite_master WHERE type='view' AND name='{table_name}'"
            cursor = db.execute(query)
            for row in cursor:
                return True
        except sqlite3.Error as ex:
            logfunc(f"Query error, query={query} Error={str(ex)}")
    return False


def tsv(report_folder, data_headers, data_list, tsvname, source_file=None):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base = os.path.dirname(os.path.dirname(report_folder))
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')

    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)
    
    with codecs.open(os.path.join(tsv_report_folder, tsvname + '.tsv'), 'a', 'utf-8-sig') as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter='\t')
        tsv_writer.writerow(data_headers)
        
        for i in data_list:
            tsv_writer.writerow(i)
            
def timeline(report_folder, tlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base = os.path.dirname(os.path.dirname(report_folder))
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
    
    for entry in data_list:
        entry = [str(field) for field in entry]
        
        data_dict = dict(zip(data_headers, entry))

        data_str = json.dumps(data_dict)
        cursor.executemany(
            "INSERT INTO data VALUES(?,?,?)", [(str(entry[0]), tlactivity, data_str)])

    db.commit()
    db.close()

def kmlgen(report_folder, kmlactivity, data_list, data_headers):
    if 'Longitude' not in data_headers or 'Latitude' not in data_headers:
        return

    data = []
    kml = simplekml.Kml(open=1)    
    a = 0
    length = len(data_list)
    while a < length:
        modifiedDict = dict(zip(data_headers, data_list[a]))
        lon = modifiedDict['Longitude']
        lat = modifiedDict['Latitude']
        times_header = "Timestamp"
        if lat and lon:
            pnt = kml.newpoint()
            times = modifiedDict.get('Timestamp','N/A')
            if times == 'N/A':
                for key, value in modifiedDict.items():
                    if isinstance(value, datetime):
                        times_header = key
                        times = value
                        break
            pnt.name = times
            pnt.description = f"{times_header}: {times} - {kmlactivity}"
            pnt.coords = [(lon, lat)]
            data.append((times, lat, lon, kmlactivity))
        a += 1

    if len(data) > 0:
        report_folder = report_folder.rstrip('/')
        report_folder = report_folder.rstrip('\\')
        report_folder_base = os.path.dirname(os.path.dirname(report_folder))
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
            CREATE TABLE data(timestamp TEXT, latitude TEXT, longitude TEXT, activity TEXT)
            """
                )
            db.commit()
        
        cursor.executemany("INSERT INTO data VALUES(?, ?, ?, ?)", data)
        db.commit()
        db.close()
        kml.save(os.path.join(kml_report_folder, f'{kmlactivity}.kml'))

def media_to_html(media_path, files_found, report_folder):

    def media_path_filter(name):
        return media_path in name

    def relative_paths(source, splitter):
        splitted_a = source.split(splitter)
        for x in splitted_a:
            if '_HTML' in x:
                splitted_b = source.split(x)
                return '.' + splitted_b[1]
            elif 'data' in x:
                index = splitted_a.index(x)
                splitted_b = source.split(splitted_a[index - 1])
                return '..' + splitted_b[1]


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
        env_path = os.path.join(dirs, 'data')
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

        mimetype = guess_mime(match)
        if mimetype == None:
            mimetype = ''

        if 'video' in mimetype:
            thumb = f'<video width="320" height="240" controls="controls"><source src="{source}" type="video/mp4" preload="none">Your browser does not support the video tag.</video>'
        elif 'image' in mimetype:
            thumb = f'<a href="{source}" target="_blank"><img src="{source}"width="300"></img></a>'
        elif 'audio' in mimetype:
            thumb = f'<audio controls><source src="{source}" type="audio/ogg"><source src="{source}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
        else:
            thumb = f'<a href="{source}" target="_blank"> Link to {filename} file</>'
    return thumb


"""
Copyright 2021, CCL Forensics
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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

def logdevinfo(message=""):
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        b.write(message + '<br>' + OutputParameters.nl)

def write_device_info():
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        for category, values in identifiers.items():
            b.write('<b>--- <u>' + category + ' </u>---</b><br>' + OutputParameters.nl)
            b.write('<ul>' + OutputParameters.nl)
            for label, data in values.items():
                if isinstance(data, list):
                    # Handle multiple values
                    b.write('<li><b>' + label + ':</b><ul>' + OutputParameters.nl)
                    for item in data:
                        b.write(f'<li>{item["value"]} <span title="{item["source_file"]}" style="cursor:help"><i>(Source: {item["artifact"]})</i></span></li>' + OutputParameters.nl)
                    b.write('</ul></li>' + OutputParameters.nl)
                else:
                    # Handle single value
                    b.write(f'<li><b>{label}:</b> {data["value"]} <span title="{data["source_file"]}" style="cursor:help"><i>(Source: {data["artifact"]})</i></span></li>' + OutputParameters.nl)
            b.write('</ul>' + OutputParameters.nl)

def device_info(category, label, value, source_file=""):
    """
    Stores device information in the identifiers dictionary
    Args:
        category (str): The category of the information (e.g., "Device Info", "User Info")
        label (str): The label/description to use as the key
        value (str): The actual value to store
    """
    # Get the calling module's name more robustly
    try:
        frame = inspect.stack()[1]
        func_name = frame.function
    except:
        func_name = 'unknown'
    
    values = identifiers.get(category, {})
    
    # Create value object with both the value and source module
    value_obj = {
        'value': value,
        'source_file': source_file,
        'artifact': func_name
    }
    
    if label in values:
        # If the label exists, check if it's already a list
        if isinstance(values[label], list):
            values[label].append(value_obj)
        else:
            # Convert existing single value to list with both values
            values[label] = [values[label], value_obj]
    else:
        # New label, store single value
        values[label] = value_obj
        
    identifiers[category] = values

def write_lava_only_log():
    """Crates the lava_only_artifacts log file"""
    with open(OutputParameters.screen_output_file_path_lava_only, 'w', encoding='utf8') as lava_log:
        lava_log.write(
            """
                <p class="note alert-info mb-4">
                The artifacts listed below are likely to return too much data to be viewed \
                in a Web browser, so they have been stored in the <i>'_lava_artifacts.db'</i> \
                SQLite database.<br>
                They are not available from the side bar of the HTML report, but they can \
                currently be viewed with any SQLite database viewer until we release <b>LAVA</b> \
                (LEAPP Artifact Viewer App).<br></p>
            """
        )
        for category, artifacts in lava_only_artifacts.items():
            lava_log.write('<b>--- ' + category.upper() + ' ---</b><br>' + OutputParameters.nl)
            lava_log.write('<ul>' + OutputParameters.nl)
            for artifact in artifacts:
                lava_log.write('<li><b>' + artifact['artifact_name'] + '</b>' + OutputParameters.nl)
                if artifact['table_name']:
                    if artifact['records']:
                        lava_log.write(f'<ul><li>- Table name: <i>{artifact["table_name"]}</i></li>' + OutputParameters.nl)
                        lava_log.write(f'<li>- Number of records: <i>{artifact["records"]}</i></li>' + OutputParameters.nl)
                    else:
                        lava_log.write('<ul><li>- No data found</li>' + OutputParameters.nl)
                else:
                    lava_log.write('<ul><li>- No file found</li>' + OutputParameters.nl)
                lava_log.write('</ul></li>' + OutputParameters.nl)
            lava_log.write('</ul>' + OutputParameters.nl)

def lava_only_info(category, artifact_name, table_name, records):
    """
    Stores artifact information in the lava_only_artifacts dictionary
    Args:
        category (str): The category of the artifact collected from artifact_info block
        artifact_name (str): The name of the artifact collected from artifact_info block
        table_name (str): The name of the table in the _lava_artifacts.db SQLite database
        records (int): The number of records returned by the artifact
    """

    artifacts = lava_only_artifacts.get(category, [])

    artifacts.append({
        'artifact_name': artifact_name,
        'table_name': table_name,
        'records': records
    })

    lava_only_artifacts[category] = artifacts

### New timestamp conversion functions
def convert_unix_ts_in_seconds(ts):
    digits = int(math.log10(ts if ts > 0 else -ts))+1
    if digits > 10:
        extra_digits = digits - 10
        ts = ts // 10**extra_digits
    return int(ts)

def convert_unix_ts_to_utc(ts):
    if ts:
        try:
            ts = float(ts)
        except ValueError:
            return ts
        ts = convert_unix_ts_in_seconds(ts)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    else:
        return ts

def convert_unix_ts_to_str(ts):
    if ts:
        ts = convert_unix_ts_in_seconds(ts)
        return datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ts

def convert_human_ts_to_utc(ts):  #This is for timestamp in human form
    if ts:
        if '.' in ts:
            ts = ts.split('.')[0]
        dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')  #Make it a datetime object
        return dt.replace(tzinfo=timezone.utc)  #Make it UTC
    else:
        return ts

def convert_cocoa_core_data_ts_to_utc(cocoa_core_data_ts):
    if cocoa_core_data_ts:
        unix_timestamp = cocoa_core_data_ts + 978307200
        return convert_unix_ts_to_utc(unix_timestamp)
    else:
        return cocoa_core_data_ts

def convert_log_ts_to_utc(str_dt):
    if str_dt:
        try:
            return datetime.strptime(str_dt, '%b %d %Y %H:%M:%S').replace(tzinfo=timezone.utc)
        except:
            return str_dt
    else:
        return str_dt

### Legacy timestamp conversion functions
def convert_local_to_utc(local_timestamp_str):
    # Parse the timestamp string with timezone offset, ex. 2023-10-27 18:18:29-0400
    local_timestamp = datetime.strptime(local_timestamp_str, "%Y-%m-%d %H:%M:%S%z")
    
    # Convert to UTC timestamp
    utc_timestamp = local_timestamp.astimezone(timezone.utc)
    
    # Return the UTC timestamp
    return utc_timestamp

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

def convert_ts_int_to_timezone(time, time_offset):
    #convert ts_int_to_utc_human
    utc_time = convert_ts_int_to_utc(time)

    #fetch the timezone information
    timezone = pytz.timezone(time_offset)
    
    #convert utc to timezone
    timezone_time = utc_time.astimezone(timezone)
    
    #return the converted value
    return timezone_time

def webkit_timestampsconv(webkittime):
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

def convert_unix_ts_to_timezone(ts, timezone_offset):
    if ts:
        digits = int(math.log10(ts))+1
        if digits > 10:
            extra_digits = digits - 10
            ts = ts // 10**extra_digits
        return convert_ts_int_to_timezone(ts, timezone_offset)
    else:
        return ts

def convert_ts_human_to_timezone_offset(ts, timezone_offset):
    return convert_utc_human_to_timezone(convert_ts_human_to_utc(ts), timezone_offset) if ts else ts

def convert_plist_date_to_timezone_offset(plist_date, timezone_offset):
    if plist_date:
        str_date = '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
            plist_date.year, plist_date.month, plist_date.day, 
            plist_date.hour, plist_date.minute, plist_date.second
            )
        iso_date = datetime.fromisoformat(str_date).strftime("%Y-%m-%d %H:%M:%S")
        return convert_ts_human_to_timezone_offset(iso_date, timezone_offset)
    else:
        return plist_date

def convert_plist_date_to_utc(plist_date):
    if plist_date:
        str_date = '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
            plist_date.year, plist_date.month, plist_date.day, 
            plist_date.hour, plist_date.minute, plist_date.second
            )
        return datetime.fromisoformat(str_date)
    else:
        return plist_date

def get_birthdate(date):
    cocoa_epoch = datetime(2001, 1, 1, tzinfo=timezone.utc) # Create our own epoch to avoid gmtime() errors in fromtimestamp().
    utc_date = cocoa_epoch + timedelta(seconds=date)
    return utc_date.strftime('%d %B %Y') if utc_date.year != 1604 else utc_date.strftime('%d %B')

def get_birthdate_from_unix_ts(date):
    utc_date = convert_unix_ts_to_utc(date)
    return utc_date.strftime('%d %B %Y') if utc_date.year != 1604 else utc_date.strftime('%d %B')

def convert_bytes_to_unit(size):
    if size:
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:3.1f} {unit}"
            size /= 1024.0
        return size
    else:
        return size
  
''' Returns string of printable characters. Replacing non-printable characters
with '.', or CHR(46)
'''
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
        shutil.copyfile(thumblist,os.path.join(report_folder, thumbname))
    else:
        #recreate thumbnail from image
        #TODO: handle videos and HEIC
        files = seeker.search(media_root+imDirectory+'/'+imFilename, return_on_first_hit=True)
        if files:
            try:
                im = Image.open(files)
                im.thumbnail(thumb_size)
                im.save(os.path.join(report_folder, thumbname))
            except:
                pass #unsupported format
    return htmlThumbTag


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
        {'Model ID': 'iPad6,3', 'Model Name': 'iPad Pro (1st gen 9.7")', 'Width': 1536, 'Height': 2048},
        {'Model ID': 'iPad6,4', 'Model Name': 'iPad Pro (1st gen 9.7")', 'Width': 1536, 'Height': 2048},
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

