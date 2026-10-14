__artifacts_v2__ = {
    "get_applePodcastsShows": {
        "name": "Apple Podcasts Shows",
        "description": "Extract Apple podcasts shows.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2026-09-16",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "Columns the store lacks are reported empty and named in the run log. ZMTPODCAST carried "
                 "all nine selected columns on the 13 registered images found to carry MTLibrary.sqlite "
                 "(iOS 13.3.1 through 26.5.2), so no such column has been observed for this artifact.",
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
            "abe_ios16": "iOS 16.5 | 243LU875E5.groups.com.apple.podcasts | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 243LU875E5.groups.com.apple.podcasts | 6 rows",
            "hickman_ios14": "iOS 14.3 | 243LU875E5.groups.com.apple.podcasts | 6 rows",
            "hc_ios26": "iOS 26.5.2 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
        }
    },
    "get_applePodcastsEpisodes": {
        "name": "Apple Podcasts Episodes",
        "description": "Extract Apple podcasts episodes.",
        "author": "@stark4n6",
        "creation_date": "2021-07-21",
        "last_update_date": "2026-09-16",
        "requirements": "none",
        "category": "Apple Podcasts",
        "notes": "Columns the store lacks are reported empty and named in the run log. ZMTEPISODE carried "
                 "all fourteen selected columns on the 13 registered images found to carry "
                 "MTLibrary.sqlite (iOS 13.3.1 through 26.5.2). iLEAPP issue #2192 reports an iOS 27.0 "
                 "store whose ZMTEPISODE column list lacks ZDOWNLOADDATE, ZASSETURL, ZITUNESSUBTITLE and "
                 "ZDURATION and includes a ZCURRENTMEDIAENCLOSURE column that none of those 13 images has; "
                 "on such a store Download Date, Subtitle, Asset URL and Duration are empty. No iOS 27 "
                 "image is registered: that layout was exercised on a copy of the iOS 17.3 store with "
                 "those four columns removed, which reported its 1,774 rows with the four columns empty "
                 "and every other column, apart from the source path, identical to the run on the "
                 "unmodified store. Where the four values are kept on iOS 27 has not been examined.",
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
            "abe_ios16": "iOS 16.5 | 243LU875E5.groups.com.apple.podcasts | 150 rows",
            "hickman_ios13": "iOS 13.3.1 | 243LU875E5.groups.com.apple.podcasts | 1024 rows",
            "hickman_ios14": "iOS 14.3 | 243LU875E5.groups.com.apple.podcasts | 1200 rows",
            "hc_ios26": "iOS 26.5.2 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 243LU875E5.groups.com.apple.podcasts | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    null_absent_columns, convert_cocoa_core_data_ts_to_utc

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
    source_files = set()

    query = '''
        SELECT
        ZADDEDDATE,
        ZLASTDATEPLAYED,
        ZUPDATEDDATE,
        ZDOWNLOADEDDATE,
        ZAUTHOR,
        ZTITLE,
        ZFEEDURL,
        ZITEMDESCRIPTION,
        ZWEBPAGEURL
        FROM ZMTPODCAST
        '''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files

        source_files.add(file_found)

        for row in get_sqlite_db_records(file_found, null_absent_columns(file_found, query)):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row['ZADDEDDATE']),
                convert_cocoa_core_data_ts_to_utc(row['ZLASTDATEPLAYED']),
                convert_cocoa_core_data_ts_to_utc(row['ZUPDATEDDATE']),
                convert_cocoa_core_data_ts_to_utc(row['ZDOWNLOADEDDATE']),
                row['ZAUTHOR'],
                row['ZTITLE'],
                row['ZFEEDURL'],
                row['ZITEMDESCRIPTION'],
                row['ZWEBPAGEURL'],
                context.get_relative_path(file_found)))

    return data_headers, data_list, '\n'.join(sorted(source_files))

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
    source_files = set()

    query = '''
        SELECT
        ZIMPORTDATE,
        CASE ZMETADATATIMESTAMP
            WHEN 0 THEN ''
            ELSE ZMETADATATIMESTAMP
        END AS ZMETADATATIMESTAMP,
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
        ORDER BY ZMETADATATIMESTAMP, ZMTEPISODE.rowid
        '''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue # Skip all other files

        source_files.add(file_found)

        for row in get_sqlite_db_records(file_found, null_absent_columns(file_found, query)):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row['ZIMPORTDATE']),
                convert_cocoa_core_data_ts_to_utc(row['ZMETADATATIMESTAMP']),
                convert_cocoa_core_data_ts_to_utc(row['ZLASTDATEPLAYED']),
                convert_cocoa_core_data_ts_to_utc(row['ZPLAYSTATELASTMODIFIEDDATE']),
                convert_cocoa_core_data_ts_to_utc(row['ZDOWNLOADDATE']),
                row['ZPLAYCOUNT'],
                row['ZAUTHOR'],
                row['ZTITLE'],
                row['ZITUNESSUBTITLE'],
                row['ZASSETURL'],
                row['ZWEBPAGEURL'],
                row['ZDURATION'],
                row['ZBYTESIZE'],
                row['ZPLAYSTATE'],
                context.get_relative_path(file_found)))

    return data_headers, data_list, '\n'.join(sorted(source_files))
