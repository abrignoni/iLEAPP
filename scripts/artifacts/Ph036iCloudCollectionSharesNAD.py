__artifacts_v2__ = {
'Ph036_1iCloudCollectionShareAlbumsPhDaPsql': {
'name': 'Ph036.1-iCloud Collection Share Albums-PhDaPsql',
'description': 'CollectionShare records in PhotoData/Photos.sqlite ZSHARE, one row per record, with its post,'
' participant and asset counts. The records seen in testing were shared albums.',
'author': '@AlexisBrignoni, Claude',
'creation_date': '2026-11-24',
'last_update_date': '2026-11-24',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Built on the Photos.sqlite research of Scott Koenig,'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/.'
' In the tested iOS 27.2.1 extraction the shared album was a ZSHARE row whose entity is CollectionShare.'
' That store held no ZGENERICALBUM row with ZKIND 1505, and Ph023 and Ph024, which read only those rows,'
' returned nothing for it. The CollectionShare entity number is read by name from the Z_PRIMARYKEY table'
' of the store, and the artifact runs whenever that entity exists, whatever iOS version was read, so it'
' also runs on an extraction with no iOS version file. Post Count counts the ZSHAREPOST rows that name the'
' record, and is empty when the store has no ZSHAREPOST table. Participant Count counts the'
' ZSHAREPARTICIPANT rows that name the record; the participants themselves are in Ph030. The ZSCOPETYPE,'
' ZCOLLECTIONSHAREKIND, ZPUBLICPERMISSION, ZCURRENTPARTICIPANTROLE and ZTRASHEDSTATE columns are reported'
' as stored; no meaning is assigned to their values. Start Date and End Date are ZSTARTDATE and ZENDDATE'
' converted from Cocoa time to UTC; what they mark for an album is not established.'
' Evidence: data-proven on a private iOS 27.2.1 full file system extraction (field mapped from a private'
' sample) holding an album its owner made with no one invited. Creation Date agreed with the time'
' recorded when the album was made, and Last Modified Date with the time of the last comment posted to it,'
' each within five seconds. Expiry Date and Trashed Date were empty on that album, which was not made'
' temporary and was not deleted. The CollectionShare entity also exists on the tested iOS 26 image, which'
' holds no such record, so the iOS 26 output has not been seen.',
'paths': ('*/PhotoData/Photos.sqlite*',),
'output_types': 'standard',
'artifact_icon': 'cloud',
'sample_data': {
'abe_ios16': 'iOS 16.5 | 0 rows',
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'falken_ios26': 'iOS 26.2.1 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
}
},
'Ph036_2iCloudCollectionSharePostsPhDaPsql': {
'name': 'Ph036.2-iCloud Collection Share Posts and Assets-PhDaPsql',
'description': 'Posts to CollectionShare records from PhotoData/Photos.sqlite ZSHAREPOST, one row per'
' post and asset, with the contributor and the asset media found in the extraction.',
'author': '@AlexisBrignoni, Claude',
'creation_date': '2026-11-24',
'last_update_date': '2026-11-24',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Built on the Photos.sqlite research of Scott Koenig,'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/.'
' A post is a ZSHAREPOST row whose ZSHARE names a CollectionShare record; its assets are the ZASSET rows'
' whose ZSHAREPOST names it, so a post with several assets gives several rows and a post with none gives'
' one row with the asset columns empty. The contributor is the ZSHAREPARTICIPANT row named by'
' ZSHAREPOST.ZCONTRIBUTOR. Contributor Is Current User, Asset Trashed State and Asset Saved Asset Type are'
' reported as stored. In the tested extraction each album asset was a separate ZASSET row from the library'
' copy of the same photo.'
' Media: the asset row records ZDIRECTORY and ZFILENAME. The files were found under'
' PhotoData/UBF/scopes/collectionshare/resources/derivatives/<ZDIRECTORY>/ and under'
' derivatives/masters/<ZDIRECTORY>/, named for the ZFILENAME stem followed by an underscore and a suffix.'
' That layout is observed in the data, not sourced. A file is matched only by that recorded directory and'
' stem, inside the same PhotoData folder as the database, and the first one whose first bytes read as'
' JPEG, HEIF or PNG is shown, derivatives before masters. Resource Files lists every matched file with the'
' format read from its first bytes and its size. In the tested extraction each album asset had a JPEG and'
' a QuickTime file in derivatives and a smaller JPEG in masters, and their sizes equal'
' ZINTERNALRESOURCE.ZDATALENGTH for that asset. No file named for the asset stem was found anywhere else'
' in that extraction, so the original photo (ZUNIFORMTYPEIDENTIFIER public.heic) and its original video'
' were not in it. ZINTERNALRESOURCE.ZLOCALAVAILABILITY is not used: it held the same value on the missing'
' originals and on the masters JPEG that was present.'
' Evidence: data-proven on a private iOS 27.2.1 full file system extraction (field mapped from a private'
' sample) with a post by the device account. Post Creation Date agreed with the time the album was made,'
' and each Asset Date Created with the time its photo was taken, each within five seconds. Post Creation'
' Date, Album Title, Post Cloud GUID, zSharePost-zPK,'
' zShare-zPK, Contributor Email, Contributor User ID, Contributor Is Current User, Asset Saved Asset Type'
' and Asset Trashed State each held one value on every row. Contributor Phone was empty. Post Caption and'
' Post Last Edited Date were empty and Post Comments Count and Post Reactions Count held zero, although the'
' photos had comments and reactions: those rows name the asset, not the post (see Ph036.3). Posts by'
' another participant, captions and post-level comments are unexercised. Needs the ZSHAREPOST table, which'
' the tested iOS 26 image does not have.',
'paths': ('*/PhotoData/Photos.sqlite*', '*/PhotoData/UBF/scopes/collectionshare/resources/derivatives/*'),
'output_types': 'standard',
'artifact_icon': 'image',
'sample_data': {
'abe_ios16': 'iOS 16.5 | 0 rows',
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'falken_ios26': 'iOS 26.2.1 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
}
},
'Ph036_3iCloudCollectionShareCommentsReactionsPhDaPsql': {
'name': 'Ph036.3-iCloud Collection Share Comments and Reactions-PhDaPsql',
'description': 'Comments, reactions and likes on CollectionShare assets and posts from'
' PhotoData/Photos.sqlite ZCLOUDSHAREDCOMMENT, one row per record, with the participant and the asset'
' media.',
'author': '@AlexisBrignoni, Claude',
'creation_date': '2026-11-24',
'last_update_date': '2026-11-24',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Built on the Photos.sqlite research of Scott Koenig,'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/.'
' A ZCLOUDSHAREDCOMMENT row is reported when the asset it names (ZREACTEDASSET, ZCOMMENTEDASSET or'
' ZLIKEDASSET, in that order) belongs to a CollectionShare record through ZASSET.ZCOLLECTIONSHARE, or when'
' the post it names (ZREACTEDPOST or ZCOMMENTEDPOST) belongs to one. Linked By names the first link column'
' that holds a value, in the order ZREACTEDASSET, ZCOMMENTEDASSET, ZLIKEDASSET, ZREACTEDPOST,'
' ZCOMMENTEDPOST. Kind is named for the first of these that holds a value: Reaction for ZREACTTEXT, Comment'
' for ZCOMMENTTEXT, Like for ZISLIKE equal to 1. It is None of the three when none does. The reaction rows'
' in the tested extraction had no comment text, a NULL ZCOMMENTTYPE and ZISLIKE 0, so Ph011 did not list'
' them. The participant is the ZSHAREPARTICIPANT row named by ZSHAREPARTICIPANT on the comment row. Is My'
' Comment and Participant Is Current User are reported as stored.'
' Evidence: data-proven on a private iOS 27.2.1 full file system extraction (field mapped from a private'
' sample) with reactions and comments on photos, all made by the device account. Kind, the reaction, the'
' comment text, the photo each one names and the Comment Date agreed with what was recorded when each was'
' made, Comment Date within five seconds. Is My Comment, Participant Is Current User, Album Title,'
' zShare-zPK, zSharePost-zPK, Participant Email and Contributor User ID each held one value on every row.'
' Participant Phone and Commenter Hashed Person ID were'
' empty. Linked By was ZREACTEDASSET or ZCOMMENTEDASSET on every row; ZCOMMENTEDPOST, ZREACTEDPOST and'
' ZCOMMENTTYPE (ZCOMMENTTYPE Raw Value) were empty, and so were Comment Client Date and Last Edited Date.'
' zSharePost-zPK comes from the asset when the row names no post. Comments and reactions by another'
' participant, likes and post-level comments are unexercised.',
'paths': ('*/PhotoData/Photos.sqlite*', '*/PhotoData/UBF/scopes/collectionshare/resources/derivatives/*'),
'output_types': 'standard',
'artifact_icon': 'message-square',
'sample_data': {
'abe_ios16': 'iOS 16.5 | 0 rows',
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'falken_ios26': 'iOS 26.2.1 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
}
},
}

import os

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_cocoa_core_data_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc, null_absent_columns)

_DERIVATIVES = ('UBF', 'scopes', 'collectionshare', 'resources', 'derivatives')


def _databases(files_found):
    '''Photos.sqlite files only, not their sidecars or media, each once.'''
    seen = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'Photos.sqlite' and file_found not in seen:
            seen.append(file_found)
    return seen


def _collection_share_entity(db_path):
    '''The Z_ENT of CollectionShare read by name from the store, or None.'''
    if not does_table_exist_in_db(db_path, 'Z_PRIMARYKEY'):
        return None
    for record in get_sqlite_db_records(db_path, "SELECT Z_ENT FROM Z_PRIMARYKEY WHERE Z_NAME = 'CollectionShare'"):
        return record[0]
    return None


def _text(value):
    return '' if value is None else str(value)


def _ts(value):
    return convert_cocoa_core_data_ts_to_utc(value) if value is not None else ''


def _media_index(files_found, db_path):
    '''{(subfolder, directory, file name): path} for derivative files in this database's PhotoData folder.'''
    root = os.path.join(os.path.dirname(db_path), *_DERIVATIVES)
    index = {}
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        parent, name = os.path.split(file_found)
        parent, directory = os.path.split(parent)
        subfolder = ''
        if parent != root:
            parent, subfolder = os.path.split(parent)
            if parent != root or subfolder != 'masters':
                continue
        index[(subfolder, directory, name)] = file_found
    return index


def _format(path):
    try:
        with open(path, 'rb') as handle:
            head = handle.read(12)
    except OSError:
        return ''
    if head[:3] == b'\xff\xd8\xff':
        return 'JPEG'
    if head[4:8] == b'ftyp':
        brand = head[8:12]
        if brand in (b'heic', b'heix', b'mif1', b'heim', b'heis'):
            return 'HEIF'
        if brand == b'qt  ':
            return 'QuickTime'
        return 'ISO media ' + brand.decode('latin-1').strip()
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG'
    return 'unrecognised'


def _resolve_media(index, directory, filename):
    '''(media reference, resource files text) for one asset, matched by recorded directory and stem.'''
    if not directory or not filename:
        return '', ''
    stem = os.path.splitext(filename)[0]
    matched = []
    for subfolder in ('', 'masters'):
        for (sub, dir_name, name), path in sorted(index.items()):
            if sub == subfolder and dir_name == directory and name.startswith(stem + '_'):
                matched.append((subfolder, name, path))
    media = ''
    described = []
    for subfolder, name, path in matched:
        kind = _format(path)
        try:
            size = os.path.getsize(path)
        except OSError:
            size = ''
        described.append(f"{os.path.join(subfolder, name) if subfolder else name} ({kind}, {size} bytes)")
        if not media and kind in ('JPEG', 'HEIF', 'PNG'):
            media = check_in_media(path, name) or ''
    return media, '; '.join(described)


@artifact_processor
def Ph036_1iCloudCollectionShareAlbumsPhDaPsql(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    for db_path in _databases(files_found):
        sources.append(db_path)
        entity = _collection_share_entity(db_path)
        if entity is None:
            logfunc(f'{context.get_relative_path(db_path)} has no CollectionShare entity; no CollectionShare albums read')
            continue
        has_posts = does_table_exist_in_db(db_path, 'ZSHAREPOST')
        post_count = ('(SELECT COUNT(*) FROM ZSHAREPOST zSharePost WHERE zSharePost.ZSHARE = zShare.Z_PK)'
                      if has_posts else 'NULL')
        query = f'''
        SELECT
        zShare.ZCREATIONDATE, zShare.ZLASTMODIFIEDDATE, zShare.ZSTARTDATE, zShare.ZENDDATE,
        zShare.ZEXPIRYDATE, zShare.ZTRASHEDDATE,
        zShare.ZTITLE, zShare.ZASSETCOUNT, zShare.ZPHOTOSCOUNT, zShare.ZVIDEOSCOUNT,
        {post_count} AS POSTCOUNT,
        (SELECT COUNT(*) FROM ZSHAREPARTICIPANT zSharePartic WHERE zSharePartic.ZSHARE = zShare.Z_PK) AS PARTICCOUNT,
        zShare.ZSHAREURL, zShare.ZPUBLICSHAREURL, zShare.ZSCOPEIDENTIFIER, zShare.ZUUID,
        zShare.ZSCOPETYPE, zShare.ZCOLLECTIONSHAREKIND, zShare.ZPUBLICPERMISSION,
        zShare.ZCURRENTPARTICIPANTROLE, zShare.ZTRASHEDSTATE, zShare.Z_PK
        FROM ZSHARE zShare
        WHERE zShare.Z_ENT = {int(entity)}
        ORDER BY zShare.ZCREATIONDATE
        '''
        for row in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), _ts(row[3]), _ts(row[4]), _ts(row[5]),
                              _text(row[6]), row[7], row[8], row[9], row[10], row[11], _text(row[12]),
                              _text(row[13]), _text(row[14]), _text(row[15]), row[16], row[17], row[18],
                              row[19], row[20], row[21]))

    data_headers = (('Creation Date', 'datetime'), ('Last Modified Date', 'datetime'),
                    ('Start Date', 'datetime'), ('End Date', 'datetime'), ('Expiry Date', 'datetime'),
                    ('Trashed Date', 'datetime'), 'Title', 'Asset Count', 'Photos Count', 'Videos Count',
                    'Post Count', 'Participant Count', 'Share URL', 'Public Share URL', 'Scope ID', 'UUID',
                    'ZSCOPETYPE Raw Value', 'ZCOLLECTIONSHAREKIND Raw Value', 'ZPUBLICPERMISSION Raw Value',
                    'ZCURRENTPARTICIPANTROLE Raw Value', 'ZTRASHEDSTATE Raw Value', 'zShare-zPK')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def Ph036_2iCloudCollectionSharePostsPhDaPsql(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    for db_path in _databases(files_found):
        sources.append(db_path)
        entity = _collection_share_entity(db_path)
        if entity is None:
            logfunc(f'{context.get_relative_path(db_path)} has no CollectionShare entity; no CollectionShare posts read')
            continue
        if not does_table_exist_in_db(db_path, 'ZSHAREPOST'):
            logfunc(f'{context.get_relative_path(db_path)} has no ZSHAREPOST table; no CollectionShare posts read')
            continue
        index = _media_index(files_found, db_path)
        query = f'''
        SELECT
        zSharePost.ZCREATIONDATE, zSharePost.ZLASTEDITEDDATE, zAsset.ZDATECREATED, zAsset.ZADDEDDATE,
        zShare.ZTITLE, zAsset.ZDIRECTORY, zAsset.ZFILENAME, zAsset.ZUUID, zSharePost.ZCAPTION,
        zSharePost.ZCOMMENTSCOUNT, zSharePost.ZREACTIONSCOUNT,
        zSharePartic.ZEMAILADDRESS, zSharePartic.ZPHONENUMBER, zSharePartic.ZISCURRENTUSER,
        zSharePost.ZCONTRIBUTORUSERIDENTIFIER, zSharePost.ZCLOUDGUID, zAsset.ZSAVEDASSETTYPE,
        zAsset.ZTRASHEDSTATE, zSharePost.Z_PK, zAsset.Z_PK, zShare.Z_PK
        FROM ZSHAREPOST zSharePost
            JOIN ZSHARE zShare ON zShare.Z_PK = zSharePost.ZSHARE AND zShare.Z_ENT = {int(entity)}
            LEFT JOIN ZASSET zAsset ON zAsset.ZSHAREPOST = zSharePost.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.Z_PK = zSharePost.ZCONTRIBUTOR
        ORDER BY zSharePost.ZCREATIONDATE, zAsset.ZDATECREATED
        '''
        for row in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            media, resources = _resolve_media(index, _text(row[5]), _text(row[6]))
            data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), _ts(row[3]), _text(row[4]), media,
                              _text(row[6]), _text(row[5]), resources, _text(row[7]), _text(row[8]), row[9],
                              row[10], _text(row[11]), _text(row[12]), row[13], _text(row[14]),
                              _text(row[15]), row[16], row[17], row[18], row[19], row[20]))

    data_headers = (('Post Creation Date', 'datetime'), ('Post Last Edited Date', 'datetime'),
                    ('Asset Date Created', 'datetime'), ('Asset Added Date', 'datetime'), 'Album Title',
                    ('Media', 'media'), 'Asset Filename', 'Asset Directory', 'Resource Files', 'Asset UUID',
                    'Post Caption', 'Post Comments Count', 'Post Reactions Count', 'Contributor Email',
                    'Contributor Phone', 'Contributor Is Current User', 'Contributor User ID',
                    'Post Cloud GUID', 'Asset Saved Asset Type', 'Asset Trashed State', 'zSharePost-zPK',
                    'zAsset-zPK', 'zShare-zPK')
    return data_headers, data_list, '\n'.join(sources)


def _columns(db_path, table):
    return {record[0] for record in get_sqlite_db_records(db_path, f"SELECT name FROM pragma_table_info('{table}')")}


def _comment_query(db_path, entity):
    '''The comment query built from the columns this store has.

    Columns iOS 26 lacks (ZREACTTEXT, ZREACTEDASSET, the post links) sit inside COALESCE and CASE
    expressions, so each is written as NULL here when absent rather than left to a later rewrite.
    '''
    comment = _columns(db_path, 'ZCLOUDSHAREDCOMMENT')
    asset = _columns(db_path, 'ZASSET')
    has_posts = does_table_exist_in_db(db_path, 'ZSHAREPOST')

    def c(name):
        return f'zComment.{name}' if name in comment else 'NULL'

    def links(names):
        present = [f'zComment.{name}' for name in names if name in comment]
        if not present:
            return 'NULL'
        return present[0] if len(present) == 1 else f"COALESCE({', '.join(present)})"

    asset_key = links(('ZREACTEDASSET', 'ZCOMMENTEDASSET', 'ZLIKEDASSET'))
    post_key = links(('ZREACTEDPOST', 'ZCOMMENTEDPOST')) if has_posts else 'NULL'
    asset_share = 'zAsset.ZCOLLECTIONSHARE' if 'ZCOLLECTIONSHARE' in asset else 'NULL'
    asset_post = 'zAsset.ZSHAREPOST' if 'ZSHAREPOST' in asset else 'NULL'
    if post_key != 'NULL':
        post_join = f'LEFT JOIN ZSHAREPOST zSharePost ON zSharePost.Z_PK = {post_key}'
        share_key = f'COALESCE({asset_share}, zSharePost.ZSHARE)'
        post_pk = f'COALESCE({post_key}, {asset_post})'
    else:
        post_join = ''
        share_key = asset_share
        post_pk = asset_post
    linked_by = ''.join(f"\n        WHEN zComment.{name} IS NOT NULL THEN '{name}'"
                        for name in ('ZREACTEDASSET', 'ZCOMMENTEDASSET', 'ZLIKEDASSET', 'ZREACTEDPOST',
                                     'ZCOMMENTEDPOST') if name in comment)
    return f'''
    SELECT
    {c('ZCOMMENTDATE')}, {c('ZCOMMENTCLIENTDATE')}, {c('ZLASTEDITEDDATE')},
    CASE
        WHEN {c('ZREACTTEXT')} IS NOT NULL AND {c('ZREACTTEXT')} <> '' THEN 'Reaction'
        WHEN {c('ZCOMMENTTEXT')} IS NOT NULL AND {c('ZCOMMENTTEXT')} <> '' THEN 'Comment'
        WHEN {c('ZISLIKE')} = 1 THEN 'Like'
        ELSE 'None of the three'
    END,
    {c('ZREACTTEXT')}, {c('ZCOMMENTTEXT')}, zShare.ZTITLE, zAsset.ZDIRECTORY, zAsset.ZFILENAME,
    {c('ZISMYCOMMENT')}, zSharePartic.ZEMAILADDRESS, zSharePartic.ZPHONENUMBER, zSharePartic.ZISCURRENTUSER,
    {c('ZCONTRIBUTORUSERIDENTIFIER')}, {c('ZCOMMENTERHASHEDPERSONID')}, {c('ZCOMMENTTYPE')},
    CASE{linked_by}
        WHEN 1 = 0 THEN NULL
    END,
    {c('ZCLOUDGUID')}, {post_pk}, zAsset.Z_PK, zShare.Z_PK, zComment.Z_PK
    FROM ZCLOUDSHAREDCOMMENT zComment
        LEFT JOIN ZASSET zAsset ON zAsset.Z_PK = {asset_key}
        {post_join}
        JOIN ZSHARE zShare ON zShare.Z_PK = {share_key} AND zShare.Z_ENT = {int(entity)}
        LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.Z_PK = {c('ZSHAREPARTICIPANT')}
    ORDER BY {c('ZCOMMENTDATE')}
    '''


@artifact_processor
def Ph036_3iCloudCollectionShareCommentsReactionsPhDaPsql(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    for db_path in _databases(files_found):
        sources.append(db_path)
        entity = _collection_share_entity(db_path)
        if entity is None:
            logfunc(f'{context.get_relative_path(db_path)} has no CollectionShare entity; no CollectionShare comments read')
            continue
        index = _media_index(files_found, db_path)
        for row in get_sqlite_db_records(db_path, null_absent_columns(db_path, _comment_query(db_path, entity))):
            media, _ = _resolve_media(index, _text(row[7]), _text(row[8]))
            data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), row[3], _text(row[4]), _text(row[5]),
                              _text(row[6]), media, _text(row[8]), row[9], _text(row[10]), _text(row[11]),
                              row[12], _text(row[13]), _text(row[14]), row[15], row[16], _text(row[17]),
                              row[18], row[19], row[20], row[21]))

    data_headers = (('Comment Date', 'datetime'), ('Comment Client Date', 'datetime'),
                    ('Last Edited Date', 'datetime'), 'Kind', 'Reaction', 'Comment Text', 'Album Title',
                    ('Media', 'media'), 'Asset Filename', 'Is My Comment', 'Participant Email',
                    'Participant Phone', 'Participant Is Current User', 'Contributor User ID',
                    'Commenter Hashed Person ID', 'ZCOMMENTTYPE Raw Value', 'Linked By', 'Cloud GUID',
                    'zSharePost-zPK', 'zAsset-zPK', 'zShare-zPK', 'zCloudSharedComment-zPK')
    return data_headers, data_list, '\n'.join(sources)
