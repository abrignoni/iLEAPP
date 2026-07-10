__artifacts_v2__ = {
    "get_applePodcastsShows": {
        "name": "Apple Podcasts Shows",
        "description": "Extract Apple podcasts shows.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "",
        "paths": ('*/MTLibrary.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "microphone",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 243LU875E5.groups.com.apple.podcasts | 7 rows",
            "felix_ios17": "iOS 17.6.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 243LU875E5.groups.com.apple.podcasts | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 243LU875E5.groups.com.apple.podcasts | 2 rows",
        }
    },
    "get_applePodcastsEpisodes": {
        "name": "Apple Podcasts Episodes",
        "description": "Extract Apple podcasts episodes.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "",
        "paths": ('*/MTLibrary.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 243LU875E5.groups.com.apple.podcasts | 4099 rows",
            "felix_ios17": "iOS 17.6.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 243LU875E5.groups.com.apple.podcasts | 1774 rows",
            "iphone12_ios18": "iOS 18.7 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 243LU875E5.groups.com.apple.podcasts | 164 rows",
        }
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc, artifact_processor

@artifact_processor
def get_applePodcastsShows(context):
    
    data_list = []
    data_headers = [
                ('Date Added', 'datetime'),
                ('Date Last Played', 'datetime'),
                ('Date Last Updated', 'datetime'),
                ('Date Downloaded', 'datetime'),
                'Author','Title',
                'Feed URL',
                'Description',
                'Web Page URL',
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
            
            timestampadded = convert_cocoa_core_data_ts_to_utc(row[0])
            timestampdateplayed = convert_cocoa_core_data_ts_to_utc(row[1])
            timestampdupdate = convert_cocoa_core_data_ts_to_utc(row[2])
            timestampdowndate = convert_cocoa_core_data_ts_to_utc(row[3])
            
            data_list.append((timestampadded,timestampdateplayed,timestampdupdate,timestampdowndate,row[4],row[5],row[6],row[7],row[8], context.get_relative_path(file_found)))
    
    return data_headers, data_list, 'see Source File for more info'
        
@artifact_processor
def get_applePodcastsEpisodes(context):
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
            timestampmeta = convert_cocoa_core_data_ts_to_utc(row[1])
            timestamplastplay = convert_cocoa_core_data_ts_to_utc(row[2])
            timestamplastmod = convert_cocoa_core_data_ts_to_utc(row[3])
            timestampdowndate = convert_cocoa_core_data_ts_to_utc(row[4])

            data_list.append((timestampimport,timestampmeta,timestamplastplay,timestamplastmod,timestampdowndate,row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13], context.get_relative_path(file_found)))
    
    return data_headers, data_list, 'see Source File for more info'