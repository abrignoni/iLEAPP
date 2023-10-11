# Parts of this script have been modified from code 
# found in Yogesh Khatri's mac_apt project Notes plugin (https://github.com/ydkhatri/mac_apt) 
# and used under terms of the MIT License.

from os.path import dirname, join
from PIL import Image
import imghdr
import zlib
import binascii

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db


def get_notes(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            if does_column_exist_in_db(db, 'ZICCLOUDSYNCINGOBJECT','ZACCOUNT4') == True:
                        
                cursor.execute('''
                    SELECT 
                    DATETIME(TabA.ZCREATIONDATE3+978307200,'UNIXEPOCH'), 
                    TabA.ZTITLE1,
                    TabA.ZSNIPPET,
                    TabB.ZTITLE2,
                    TabC.ZNAME,
                    DATETIME(TabA.ZMODIFICATIONDATE1+978307200,'UNIXEPOCH'),
                    case TabA.ZISPASSWORDPROTECTED
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    TabA.ZPASSWORDHINT,
                    case TabA.ZMARKEDFORDELETION
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    case TabA.ZISPINNED
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    TabE.ZFILENAME,
                    TabE.ZIDENTIFIER,
                    TabD.ZFILESIZE,
                    TabD.ZTYPEUTI,
                    DATETIME(TabD.ZCREATIONDATE+978307200,'UNIXEPOCH') as "Attachment Created",
                    DATETIME(TabD.ZMODIFICATIONDATE+978307200,'UNIXEPOCH') as "Attachment Modified",
                    TabF.ZDATA
                    FROM ZICCLOUDSYNCINGOBJECT TabA
                    INNER JOIN ZICCLOUDSYNCINGOBJECT TabB on TabA.ZFOLDER = TabB.Z_PK
                    INNER JOIN ZICCLOUDSYNCINGOBJECT TabC on TabA.ZACCOUNT4 = TabC.Z_PK
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabD on TabA.Z_PK = TabD.ZNOTE
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabE on TabD.Z_PK = TabE.ZATTACHMENT1
                    LEFT JOIN ZICNOTEDATA TabF on TabF.ZNOTE = TabA.Z_PK
                    ''')
                
            else:
                cursor.execute('''
                    SELECT 
                    DATETIME(TabA.ZCREATIONDATE1+978307200,'UNIXEPOCH'), 
                    TabA.ZTITLE1,
                    TabA.ZSNIPPET,
                    TabB.ZTITLE2,
                    TabC.ZNAME,
                    DATETIME(TabA.ZMODIFICATIONDATE1+978307200,'UNIXEPOCH'),
                    case TabA.ZISPASSWORDPROTECTED
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    TabA.ZPASSWORDHINT,
                    case TabA.ZMARKEDFORDELETION
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    case TabA.ZISPINNED
                    when 0 then "No"
                    when 1 then "Yes"
                    end,
                    TabE.ZFILENAME,
                    TabE.ZIDENTIFIER,
                    TabD.ZFILESIZE,
                    TabD.ZTYPEUTI,
                    DATETIME(TabD.ZCREATIONDATE+978307200,'UNIXEPOCH') as "Attachment Created",
                    DATETIME(TabD.ZMODIFICATIONDATE+978307200,'UNIXEPOCH') as "Attachment Modified",
                    TabF.ZDATA
                    FROM ZICCLOUDSYNCINGOBJECT TabA
                    INNER JOIN ZICCLOUDSYNCINGOBJECT TabB on TabA.ZFOLDER = TabB.Z_PK
                    INNER JOIN ZICCLOUDSYNCINGOBJECT TabC on TabA.ZACCOUNT2 = TabC.Z_PK
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabD on TabA.Z_PK = TabD.ZNOTE
                    LEFT JOIN ZICCLOUDSYNCINGOBJECT TabE on TabD.Z_PK = TabE.ZATTACHMENT1
                    LEFT JOIN ZICNOTEDATA TabF on TabF.ZNOTE = TabA.Z_PK
                    ''')
            
            all_rows = cursor.fetchall()
            analyzed_file = file_found

    if len(all_rows) > 0:
        for row in all_rows:
            
            if row[6] == 'No' and row[16] is not None:
                data = GetUncompressedData(row[16])
                text_content = ProcessNoteBodyBlob(data)
            else:
                text_content = ''
            
            if row[10] is not None and row[11] is not None:
                attachment_file = join(dirname(analyzed_file), 'Accounts/LocalAccount/Media', row[11], row[10])
                attachment_storage_path = dirname(attachment_file)
                if imghdr.what(attachment_file) == 'jpeg' or imghdr.what(attachment_file) == 'jpg' or imghdr.what(attachment_file) == 'png':
                    thumbnail_path = join(report_folder, 'thumbnail_'+row[10])
                    save_original_attachment_as_thumbnail(attachment_file, thumbnail_path)
                    thumbnail = '<img src="{}">'.format(thumbnail_path)
                else:
                    thumbnail = 'File is not an image or the filetype is not supported yet.'
            else:
                thumbnail = ''
                attachment_storage_path = ''

            if row[12] is not None:
                filesize = '.'.join(str(row[12])[i:i+3] for i in range(0, len(str(row[12])), 3))
            else:
                filesize = ''

            data_list.append((row[0], row[1], row[2], text_content, row[3], row[4], row[5], row[6], row[7], row[8], row[9], thumbnail, row[10], attachment_storage_path, filesize, row[13], row[14], row[15]))

        report = ArtifactHtmlReport('Notes')
        report.start_artifact_report(report_folder, 'Notes')
        report.add_script()
        data_headers = ('Creation Date', 'Note Title', 'Snippet', 'Note Contents', 'Folder', 'Storage Place', 'Last Modified',
                        'Password Protected', 'Password Hint', 'Marked for Deletion', 'Pinned', 'Attachment Thumbnail',
                        'Attachment Original Filename', 'Attachment Storage Folder', 'Attachment Size in KB',
                        'Attachment Type', 'Attachment Creation Date', 'Attachment Last Modified')
        report.write_artifact_data_table(data_headers, data_list, analyzed_file, html_no_escape=['Attachment Thumbnail'])
        report.end_artifact_report()

        tsvname = 'Notes'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Notes'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Notes available')

    db.close()

def GetUncompressedData(compressed):
    if compressed == None:
        return None
    data = None
    try:
        data = zlib.decompress(compressed, 15 + 32)
    except zlib.error:
        print('Zlib Decompression failed!')
    return data

def ProcessNoteBodyBlob(blob):
    data = b''
    if blob == None: return data
    try:
        pos = 0
        if blob[0:3] != b'\x08\x00\x12': # header
            print('Unexpected bytes in header pos 0 - ' + binascii.hexlify(blob[0:3]) + '  Expected 080012')
            return ''
        pos += 3
        length, skip = ReadLengthField(blob[pos:])
        pos += skip

        if blob[pos:pos+3] != b'\x08\x00\x10': # header 2
            print('Unexpected bytes in header pos {0}:{0}+3'.format(pos))
            return '' 
        pos += 3
        length, skip = ReadLengthField(blob[pos:])
        pos += skip

        # Now text data begins
        if blob[pos] != 0x1A:
            print('Unexpected byte in text header pos {} - byte is 0x{:X}'.format(pos, blob[pos]))
            return ''
        pos += 1
        length, skip = ReadLengthField(blob[pos:])
        pos += skip
        # Read text tag next
        if blob[pos] != 0x12:
            print('Unexpected byte in pos {} - byte is 0x{:X}'.format(pos, blob[pos]))
            return ''
        pos += 1
        length, skip = ReadLengthField(blob[pos:])
        pos += skip
        data = blob[pos : pos + length].decode('utf-8', 'backslashreplace')
        # Skipping the formatting Tags
    except (IndexError, ValueError):
        print('Error processing note data blob')
    return data

def ReadLengthField(blob):
    '''Returns a tuple (length, skip) where skip is number of bytes read'''
    length = 0
    skip = 0
    try:
        data_length = int(blob[0])
        length = data_length & 0x7F
        while data_length > 0x7F:
            skip += 1
            data_length = int(blob[skip])
            length = ((data_length & 0x7F) << (skip * 7)) + length
    except (IndexError, ValueError):
        log.exception('Error trying to read length field in note data blob')
    skip += 1
    return length, skip


def save_original_attachment_as_thumbnail(file, store_path):
    image = Image.open(file)
    thumbnail_max_size = (350, 350)
    image.thumbnail(thumbnail_max_size)
    image.save(store_path)

__artifacts__ = {
    "notes": (
        "Notes",
        ('*/NoteStore.sqlite*'),
        get_notes)
}