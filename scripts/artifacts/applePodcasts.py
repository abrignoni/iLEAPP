__artifacts_v2__ = {
    "get_applePodcastsShows": {
        "name": "Apple Podcasts Shows",
        "description": "Extract Apple podcasts shows.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2025-09-25",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "",
        "paths": ('*/MTLibrary.sqlite*'),
        "output_types": "standard"
    },
    "get_applePodcastsEpisodes": {
        "name": "Apple Podcasts Episodes",
        "description": "Extract Apple podcasts episodes.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2025-09-25",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "",
        "paths": ('*/MTLibrary.sqlite*'),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc, artifact_processor
from scripts.context import Context

@artifact_processor
def get_applePodcastsShows(context:Context):
    
    data_list = []
    data_headers = [
                ('Date Added', 'datetime'),
                ('Date Last Played', 'datetime'),
                ('Date Last Updated', 'datetime'),
                ('Date Downloaded', 'datetime'),
                'Author','Title',
                'Feed URL',
                'Description',
                'Web Page URL'
                'Source File']
    
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        ZADDEDDATE,
        ZLASTDATEPLAYED,
        ZUPDATEDDATE,
        ZDOWNLOADEDDATE,
        ZAUTHOR,
        ZTITLE,
        ZFEEDURL,
        ZITEMDESCRIPTION,
        ZWEBPAGEURL
        from ZMTPODCAST
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            
            if (row[0] == '') or (row[0]== None):
                timestampadded = ''
            else:
                timestampadded = convert_cocoa_core_data_ts_to_utc(row[0])
            
            if (row[1] == '') or (row[1]== None):
                timestampdateplayed = ''
            else:
                timestampdateplayed = convert_cocoa_core_data_ts_to_utc(row[1])
            
            if (row[2] == '') or (row[2]== None):
                timestampdupdate = ''
            else:
                timestampdupdate = convert_cocoa_core_data_ts_to_utc(row[2])
            
            if (row[3] == '') or (row[3]== None):
                timestampdowndate = ''
            else:
                timestampdowndate = convert_cocoa_core_data_ts_to_utc(row[3])
            
            data_list.append((timestampadded,timestampdateplayed,timestampdupdate,timestampdowndate,row[4],row[5],row[6],row[7],row[8], file_found))
    
    return data_list, data_headers, ''
        
@artifact_processor
def get_applePodcastsEpisodes(context:Context):
    data_list = []
    data_headers = [
                ('Import Date', 'datetime'),
                ('Metadata Timestamp', 'datetime'),
                ('Date Last Played', 'datetime'),
                ('Play State Last Modified', 'datetime'),
                ('Download Date', 'datetime'),
                'Play Count',
                'Author',
                'Title',
                'Subtitle',
                'Asset URL',
                'Web Page URL',
                'Duration',
                'Size',
                'Play State',
                'Source File'] 
    
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
        SELECT
        ZIMPORTDATE,
        CASE ZMETADATATIMESTAMP
            WHEN 0 THEN ''
            ELSE ZMETADATATIMESTAMP
        END,
        ZLASTDATEPLAYED,
        ZPLAYSTATELASTMODIFIEDDATE,
        ZDOWNLOADDATE,
        ZPLAYCOUNT,
        ZAUTHOR,
        ZTITLE,
        ZITUNESSUBTITLE,
        ZASSETURL,
        ZWEBPAGEURL,
        ZDURATION,
        ZBYTESIZE,
        ZPLAYSTATE
        FROM ZMTEPISODE
        ORDER by ZMETADATATIMESTAMP
        ''')

        all_rows = cursor.fetchall()
        
        for row in all_rows:
            
            timestampimport = convert_cocoa_core_data_ts_to_utc(row[0])
            
            if (row[1] == '') or (row[1]== None):
                timestampmeta = ''
            else:
                timestampdameta = convert_cocoa_core_data_ts_to_utc(row[1])
            
            if (row[2] == '') or (row[2]== None):
                timestamplastplay = ''
            else:
                timestamplastplay = convert_cocoa_core_data_ts_to_utc(row[2])
            
            if (row[3] == '') or (row[3]== None):
                timestamplastmod = ''
            else:
                timestamplastmod = convert_cocoa_core_data_ts_to_utc(row[3])
            
            if (row[4] == '') or (row[4]== None):
                timestampdowndate = ''
            else:
                timestampdowndate = convert_cocoa_core_data_ts_to_utc(row[4])

        data_list.append((timestampimport,timestampmeta,timestamplastplay,timestamplastmod,timestampdowndate,row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13], file_found))
    
    return data_list, data_headers, ''