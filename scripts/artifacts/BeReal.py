__artifacts_v2__ = {
    "bereal_preferences": {
        "name": "Preferences",
        "description": "Parses and extract BeReal Preferences",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.BeReal.plist',
                  '*/mobile/Containers/Data/Application/*/Library/Preferences/AlexisBarreyat.BeReal.plist'),
        "output_types": [ "none" ],
        "artifact_icon": "settings"
    },
    "bereal_accounts": {
        "name": "Accounts",
        "description": "Parses and extract BeReal Accounts",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-ProfileRepository/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/EntitiesStore.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL", "Timezone", "Device UID", "Device Model and OS", "App version", "RealMojis",
                          "Source file name", "Location" ],
        "artifact_icon": "user"
    },
    "bereal_contacts": {
        "name": "Contacts",
        "description": "Parses and extract BeReal Contacts",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsContactsManager-contact/*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "users"
    },
    "bereal_persons": {
        "name": "Persons",
        "description": "Parses and extract BeReal Persons",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_officialAccountProfiles/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL", "URLs", "Source file name", "Location" ],
        "artifact_icon": "users"
    },
    "bereal_friends": {
        "name": "Friends",
        "description": "Parses and extract BeReal Friends, Friend Requests Sent, Friend Requests Received, and Friends Following",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsFriendsListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsRequestSentListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsRequestReceivedListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-Production_FriendsStorage.following/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-Production_FriendsStorage.followers/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/EntitiesStore.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL", "Source file name", "Location" ],
        "artifact_icon": "user-plus"
    },
    "bereal_blocked_users": {
        "name": "Blocked Users",
        "description": "Parses and extract BeReal Blocked Users",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-BlockedUserManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Source file name", "Location" ],
        "artifact_icon": "slash"
    },
    "bereal_posts": {
        "name": "Posts",
        "description": "Parses and extract BeReal Memories, Person BeReal of the day and Production Feeds",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/EntitiesStore.sqlite*'),
        "output_types": [ "all" ],
        "html_columns": [ "Primary URL", "Secondary URL", "Thumbnail URL", "Song URL", "Visibility", "Tagged friends", "Source file name", "Location" ],
        "artifact_icon": "calendar"
    },
    "bereal_pinned_memories": {
        "name": "Pinned Memories",
        "description": "Parses and extract BeReal Pinned Memories",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-pinnedMemories-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-PersonRepository-pinnedMemories-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Primary URL", "Secondary URL", "Source file name", "Location" ],
        "artifact_icon": "bookmark"
    },
    "bereal_realmojis": {
        "name": "RealMojis",
        "description": "Parses and extract BeReal RealMojis from my memories and Person's memories",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/EntitiesStore.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "RealMoji URL", "Source file name", "Location" ],
        "chatParams": {
            "timeColumn": "Created",
            "threadDiscriminatorColumn": "BeReal ID",
            "threadLabelColumn": "Owner",
            "directionColumn": "Direction",
            "directionSentValue": "Outgoing",
            "senderColumn": "Author",
            "textColumn": "Emoji"
        },
        "artifact_icon": "thumbs-up"
    },
    "bereal_comments": {
        "name": "Comments",
        "description": "Parses and extract BeReal Comments from my memories, Person's posts, and Production post Feeds",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/AlexisBarreyat.BeReal/Cache.db*',
                  '*/mobile/Containers/Shared/AppGroup/*/EntitiesStore.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "RealMojis", "Source file name", "Location" ],
        "chatParams": {
            "timeColumn": "Created",
            "threadDiscriminatorColumn": "BeReal ID",
            "threadLabelColumn": "Owner",
            "directionColumn": "Direction",
            "directionSentValue": "Outgoing",
            "senderColumn": "Author",
            "textColumn": "Text"
        },
        "artifact_icon": "message-square"
    },
    "bereal_messages": {
        "name": "Messages",
        "description": "Parses and extract BeReal Messages",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/bereal-chat.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Media URL", "Source file name", "Location" ],
        "chatParams": {
            "timeColumn": "Sent",
            "threadDiscriminatorColumn": "Thread ID",
            "threadLabelColumn": "Owner",
            "directionColumn": "Direction",
            "directionSentValue": "Outgoing",
            "senderColumn": "Sender",
            "textColumn": "Message"
        },
        "artifact_icon": "message-square"
    },
    "bereal_chat_list": {
        "name": "Chat List",
        "description": "Parses and extract BeReal Chat List",
        "author": "@djangofaiola",
        "version": "0.2",
        "creation_date": "2024-12-20",
        "last_update_date": "2025-05-03",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/bereal-chat.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Administrators", "Participants", "Source file name", "Location" ],
        "artifact_icon": "message-circle"
    }
}

from pathlib import Path
import inspect
import json
import sqlite3
import re
import hashlib
from datetime import timedelta, datetime
from base64 import standard_b64decode
from urllib.parse import urlparse, urlunparse
from scripts.ilapfuncs import get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, get_plist_content, get_plist_file_content, lava_get_full_media_info, \
    convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc, convert_ts_int_to_utc, check_in_media, check_in_embedded_media, artifact_processor, logfunc

# <id, fullname|username>
bereal_user_map = {}
# bereal user id
bereal_user_id = None
# bereal app id
bereal_app_identifier = None
# bereal images
bereal_images = ()
# constants
LINE_BREAK = '\n'
COMMA_SEP = ', '
HTML_LINE_BREAK = '<br>'


def get_json_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logfunc(f"Error reading file {file_path}: {str(e)}")
        return None


def get_json_content(data):
    try:
        return json.loads(data)
    except Exception as e:
        logfunc(f"Unexpected error reading json data: {str(e)}")
        return {}


def get_sqlite_db_records_regexpr(file_path, query, attach_query=None, regexpr=None):
    file_path = str(file_path)
    db = open_sqlite_db_readonly(file_path)
    if not bool(db):
        return None

    try:
        # regexp() user function
        if bool(regexpr):
            db.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)
    
        cursor = db.cursor()
        if bool(attach_query):
            cursor.execute(attach_query)
        cursor.execute(query)
        records = cursor.fetchall()
        return records

    except sqlite3.OperationalError as e:
        logfunc(f"Error with {file_path}:")
        logfunc(f" - {str(e)}")

    except sqlite3.ProgrammingError as e:
        logfunc(f"Error with {file_path}:")
        logfunc(f" - {str(e)}")


# Cache.db query
BEREAL_CACHE_DB_QUERY = '''
    SELECT
        crd.entry_ID,
        cr.request_key,
        crd.isDataOnFS,
        crd.receiver_data
    FROM cfurl_cache_response AS "cr"
    LEFT JOIN cfurl_cache_receiver_data AS "crd" ON (cr.entry_ID = crd.entry_ID)
    WHERE cr.request_key REGEXP "{0}"
    '''


# iso 8601 format to utc
def convert_iso8601_to_utc(str_date):
    if bool(str_date) and isinstance(str_date, str) and (str_date != 'null'):
        if len(str_date) <= 10:
            str_date = str_date + 'T00:00:00.000Z'
        dt = datetime.fromisoformat(str_date).timestamp()
        return convert_ts_int_to_utc(dt)
    else:
        return str_date


# get key0
def get_key0(obj):
    return list(obj.keys())[0] if bool(obj) and isinstance(obj, dict) else None


# profile picture or thumbnail or media or primary or secondary
def get_media(obj):
    if bool(obj) and isinstance(obj, dict):
        # url
        pp_url = obj.get('url', '')
        # size 1.x
        if bool(pp_size := obj.get('size')) and len(pp_size) == 2:
            pp_size = f"{pp_size[0]}x{pp_size[1]}"
        # size 2.x, 4.x
        elif (w := obj.get('width')) and (h := obj.get('height')):
            pp_size = f"{w}x{h}"
        # none
        else:
            pp_size = None
        # media type
        media_type = obj.get('mediaType')
        # dict
        if isinstance(media_type, dict):
            pp_mt = get_key0(media_type)
        # string
        elif isinstance(media_type, str):
            pp_mt = media_type
        # none
        else:
            pp_mt = None
    else:
        pp_url = ''
        pp_size = None
        pp_mt = None

    # media type, url and size string
    return pp_mt, pp_url, pp_size


# placeholder from primary or secondary or thumbnail
def get_place_holder0_url(obj):
    result = None
    if bool(obj):
        place_holders = obj.get('placeholders', [])
        if bool(place_holders):
            result = place_holders[0].get('url')

    return result


# music url
def get_music_artist_and_track(obj):
    result = None

    if bool(obj) and isinstance(obj, dict) and bool(music := obj.get('music')):
        # artist
        artist = music.get('artist')
        # track
        track = music.get('track')
        # artist and track
        if bool(track):
            result = f"{artist} - {track}" if bool(artist) else track
        else:
            result = artist if bool(artist) else None

    return result


# music url
def get_music_url(obj, html_format=False):
    song_url = None
    
    if bool(obj) and isinstance(obj, dict) and bool(music := obj.get('music')):
        # openUrl?
        song_url = music.get('openUrl')
        if not bool(song_url):
            # provider (spotify, apple)
            provider = music.get('provider')
            # provider id/track id
            track_id = music.get('providerId')
            # album id
            album_id = None
            # audio type (track, ...)
            # audioType
            # spotify
            if provider == 'spotify' and bool(track_id):
                # old link: "https://open.spotify.com/track/{track_id}""
                # new link: "https://open.spotify.com/intl-it/track/{track_id}"
                song_url = f"https://open.spotify.com/track/{track_id}"
            # apple
            elif ((provider == 'apple') or (provider.lower == 'apple music')) and bool(track_id):
                # link: "https://music.apple.com/us/album/{album_id}?i={track_id}"
#                song_url = f"https://music.apple.com/us/album/{album_id}?i={track_id}"
                song_url = '?'

        # html?
        if html_format:
            song_url = generic_url(song_url, html_format=html_format)

    return song_url


# profile type (regular, brand, celebrity, ...)
def get_profile_type(obj):
    REGULAR = 'User'
    REAL_BRAND = 'RealBrand'
    REAL_PEOPLE = 'RealPeople'
    profile_type = None

    if isinstance(obj, str):
        profile_type = obj
    else:
        # type      
        _type = obj.get('type', '')
        # regular
        if (_type == 'USER'):
            profile_type = REGULAR
        # real brand
        elif (_type == 'REAL_BRAND'):
            profile_type = REAL_BRAND
        # real people/celebrity
        elif (_type == 'REAL_PERSON'):
            profile_type = REAL_PEOPLE
        # no type/unknown type
        else:
            profile_type = _type
            # profile type
            if bool(profile_type) == False:
                profile_type = get_key0(obj.get('profileType'))
            # official account profile type
            if bool(profile_type) == False:
                profile_type = get_key0(obj.get('officialAccountProfileType'))            
                
    # friendly name
    profile_type_lower = profile_type.lower() if bool(profile_type) else profile_type
    # regular
    if (bool(profile_type_lower) == False) or (profile_type_lower == 'regular'):
        profile_type = REGULAR
    # real brand
    elif profile_type_lower == 'brand':
        profile_type = REAL_BRAND
    # real people/celebrity
    elif profile_type_lower == 'celebrity':
        profile_type = REAL_PEOPLE

    return profile_type


# format post type
def format_post_type(is_late, is_main):
    # post type
    post_type = 'late' if is_late else 'onTime'
    if not is_main:
        post_type = f"{post_type} bonus"

    return post_type


# post type (onTime, late, ...)
def get_post_type(obj, is_late=False):
    post_type = obj.get('postType', '')

    if post_type.lower() == 'bonus':
        post_type = f"late {post_type}" if is_late else f"onTime {post_type}"

    return post_type


# post visibilities
def get_post_visibilities(obj, html_format=False):
    if isinstance(obj, dict):
        # friends, friends-of-friends, public
        visibilities = obj.get('visibilities')
        if not visibilities:
            visibilities = obj.get('visibility')
    elif isinstance(obj, list):
        visibilities = obj
    else:
        visibilities = None

    if visibilities:
        return HTML_LINE_BREAK.join(visibilities) if html_format else LINE_BREAK.join(visibilities)
    else:
        return 'N/D'


# late secs to time
def get_late_secs(obj):
    # late in seconds
    if isinstance(obj, dict):
        late_secs = obj.get('lateInSeconds')
    elif isinstance(obj, int):
        late_secs = obj
    else:
        late_secs = None
    return str(timedelta(seconds=late_secs)) if bool(late_secs) else late_secs


# generic url
def generic_url(value, html_format=False):
    # default
    result = None

    if bool(value) and (value != 'null'):
        u = urlparse(value)
        # 0=scheme, 2=path
        if not bool(u.scheme) and u.path.startswith('www'):
            u = u._replace(scheme='http')
        url = urlunparse(u)
        result =  f'<a href="{url}" target="_blank">{value}</a>' if html_format else url

    return result


# unordered list
def unordered_list(values, html_format=False):
    if not bool(values):
        return None

    return HTML_LINE_BREAK.join(values) if html_format else LINE_BREAK.join(values)


# links
def get_links(obj, html_format=False):
    if bool(obj) and isinstance(obj, list):
        links_urls = []
        # array
        for i in range(0, len(obj)):
           url = obj[i].get('url')
           if not bool(url):
               url = obj[i].get('link') # json
           url = generic_url(url, html_format=html_format)
           links_urls.append(url)
        return unordered_list(links_urls, html_format=html_format)
    else:
        return ''


# realmojis
def get_realmojis(obj, html_format=False):
    # real mojis
    all_mojis = []

    # realmojis
    if bool(real_mojis := obj.get('realmojis')):
        # array
        for i in range(0, len(real_mojis)):
            # real moji
            real_moji = real_mojis[i]
            # emoji->url
            url_moji = generic_url(real_moji.get('media', {}).get('url'), html_format=html_format)
            all_mojis.append(f"{real_moji.get('emoji')} {url_moji}")

        return unordered_list(all_mojis, html_format=html_format)

    # realMojis
    elif bool(real_mojis := obj.get('realMojis')):
        # array
        for i in range(0, len(real_mojis)):
            # real moji
            real_moji = real_mojis[i]
            # emoji->uri
            uri_moji = generic_url(real_moji.get('uri'), html_format=html_format)
            all_mojis.append(f"{real_moji.get('emoji')} {uri_moji}")

        return unordered_list(all_mojis, html_format=html_format)

    # none
    else:
        return ''


# string "id (user name|full name)"
def format_userid(id, name=None):
    if id:
        # "id (name)"
        if name:
            return f"{id} ({name})"
        # "id (m_name)"
        else:
            m_name = bereal_user_map.get(id)
            return f"{id} ({m_name})" if bool(m_name) else id
    else:
        return "Local User"


# get_user
def get_user(obj):
    if obj:
        # user
        user = obj.get('user')
        if user:
            return user.get('id'), user.get('username')
        # userName and uid?
        elif bool(obj.get('userName')) and bool(obj.get('uid')):
            return obj.get('uid'), obj.get('userName')
        # username and id?
        elif bool(obj.get('username')) and bool(obj.get('id')):
            return obj.get('id'), obj.get('username')
        # none
        return None, None
    # none
    else:
        return None, None


# get_tags
def get_tags(obj, html_format=False, as_ul=False):
    tag_list = []

    tags = obj.get('tags')
    if not bool(tags):
        tags = obj.get('tagsV2')

    # array
    if bool(tags) and isinstance(tags, list):
        for i in range(0, len(tags)):
            tag = tags[i]

            # has user?
            user = tag.get('user')
            if bool(user):
                id = user.get('id')
                fullname = user.get('fullname')
                # userid (fullname)
                if bool(fullname):
                    user = f"{id} ({fullname})"
                # userid (username)
                else:
                    username = user.get('username')
                    user = f"{id} ({username})"
            else:
                # V1?
                id = tag.get('userId')
                if bool(id):
                    # userid (fullname)
                    user = format_userid(id)
                # V2
                else:
                    id = tag.get('id')
                    fullname = tag.get('fullname')
                    # userid (fullname)
                    if bool(fullname):
                        user = f"{id} ({fullname})"
                    # userid (username)
                    else:
                        username = tag.get('username')
                        user = f"{id} ({username})"

            if bool(user):
                tag_list.append(user)

    return unordered_list(tag_list, html_format=html_format)


# get_devices -> [ uid, info, app_ver, timezone ]
def get_devices(obj, html_format=False):
    if bool(devices := obj.get('devices')):
        # devices
        dev_uid = []
        dev_info = []
        app_ver = []
        timezone = []
        # array
        for i in range(0, len(devices)):
            # device
            device = devices[i]
            # device uid
            dev_uid.append(device.get('deviceId'))
            # device info (model, ios ver)
            dev_info.append(device.get('device'))
            # app version
            app_ver.append(device.get('clientVersion'))
            # timezone
            timezone.append(device.get('timezone'))
        line_sep = HTML_LINE_BREAK if html_format else LINE_BREAK
        return [ line_sep.join(dev_uid), line_sep.join(dev_info), line_sep.join(app_ver), line_sep.join(timezone) ]
    else:
        return None, None, None, None


# media item file from url
def media_item_from_url(seeker, url, artifact_info, from_photos=False):
    file_path = None

    # https://cdn-us1.bereal.network/cdn-cgi/image/height=130/Photos/LRHP7nD4UhfzEJacyRtuZE37txxx/post/a2jRGMvcxwdfkNEI.webp
    if bool(url):
        i_photos = url.find('/Photos/')
        if i_photos > -1:
            # Photos/LRHP7nD4UhfzEJacyRtuZE37txxx/post/a2jRGMvcxwdfkNEI.webp
            if from_photos:
                url_path = url[i_photos + 1:]
            # cdn-cgi/image/height=130/Photos/LRHP7nD4UhfzEJacyRtuZE37txxx/post/a2jRGMvcxwdfkNEI.webp
            else:
                url_path = str(urlparse(url).path[1:])
        else:
            url_path = url

        # is thumbnail? yes -> <APP_UID>/Library/Caches/com.hackemist.SDImageCache/memories_thumbnails_cache/
        if '/image/height=' in url:
            img_dir = 'memories_thumbnails_cache'
        # default <APP_UID>/Library/Caches/com.hackemist.SDImageCache/default/
        else:
            img_dir = 'default'

        hash = hashlib.md5(url_path.encode('utf-8')).hexdigest()
        rel_path = Path(url_path).with_stem(hash)
        file_name = rel_path.name
        cache_pattern = str(Path(f"/{bereal_app_identifier}/Library/Caches/com.hackemist.SDImageCache/{img_dir}/{file_name}"))
        for image in bereal_images:
            if image.endswith(cache_pattern):
                file_path = check_in_media(seeker, image, artifact_info, already_extracted=bereal_images)
                break

    return file_path


# device path/local path
def get_device_file_path(file_path, seeker):
    device_path = file_path

    if bool(file_path):
        file_info = seeker.file_infos.get(file_path) if file_path else None
        # data folder: /path/to/report/data
        if file_info:
            source_path = file_info.source_path
        # extraction folder: /path/to/directory
        else:
            source_path = file_path
        if source_path.startswith('\\\\?\\'): source_path = source_path[4:]
        source_path = Path(source_path).as_posix()

        index_private = source_path.find('/private/')
        if index_private > 0:
            device_path = source_path[index_private:]
        else:
            device_path = source_path

    return device_path


def get_cache_db_fs_path(data, file_found, seeker):
    if bool(data):
        # */<GUID>/Library/Caches/AlexisBarreyat.BeReal/fsCachedData/<data>
        filter = Path('*').joinpath(*Path(file_found).parts[-5:-1], 'fsCachedData', data)
        json_file = seeker.search(filter, return_on_first_hit=True)
        return json_file
    else:
        return None


# preferences
@artifact_processor
def bereal_preferences(files_found, report_folder, seeker, wrap_text, timezone_offset):

    source_path = None
    global bereal_user_id
    global bereal_app_identifier
    global bereal_images
    artifact_info = inspect.stack()[0]

    # all files
    for file_found in files_found:
        file_found = str(file_found)
        # prefs
        plist_data = get_plist_file_content(file_found)
        if not bool(plist_data):
            continue

        try:
            # source path
            source_path = file_found

            # group
            if file_found.endswith('group.BeReal.plist'):
                # me <id, username>
                user_name = 'Local User'
                user_id = plist_data.get('bereal-user-id')
                if not bool(user_id):
                    user_id = plist_data.get('userId')
                if not bool(user_id):
                    user_id = plist_data.get('myUserID')
                if bool(user_id):
                    user_name = plist_data.get('myAccount', {}).get(user_id, {}).get('username')
                    if not bool(user_name): user_name = 'Local User'
                    bereal_user_map[user_id] = user_name
                    # bereal user id
                    bereal_user_id = user_id

                # current friends <id, fullname>
                current_friends = plist_data.get('currentFriends', {})
                for user_id, user_name in current_friends.items():
                    bereal_user_map[user_id] = user_name

            # preferences
            elif file_found.endswith('AlexisBarreyat.BeReal.plist'):
                bereal_app_identifier = Path(file_found).parents[2].name
                cache_pattern = str(Path('*', bereal_app_identifier, 'Library', 'Caches', 'com.hackemist.SDImageCache', '**', '*'))
                bereal_images = seeker.search(cache_pattern, return_on_first_hit=False)

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # return empty
    return (), [], source_path


# accounts
@artifact_processor
def bereal_accounts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Profile type',
        'Full name',
        'User name',
        'Profile picture URL',
        ('Profile picture', 'media', 'height: 96px; border-radius: 50%;'),
        'Gender',
        ('Birthday', 'date'),
        'Biography',
        'Country code',
        'Region',
        'Address',
        'Timezone',
        ('Phone number', 'phonenumber'),
        'Device UID',
        'Device Model and OS',
        'App version',
        'Private',
        'RealMojis',
        'User ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_accounts']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # disk-bereal-ProfileRepository
        if file_rel_path.startswith('disk-bereal-ProfileRepository'):
            try:
                device_file_paths = [ device_file_path ]

                # json data
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # account
                account = json_data.get('object')
                if not bool(account):
                    continue

                # created
                created = convert_cocoa_core_data_ts_to_utc(account.get('createdAt'))
                # profile type
                profile_type = get_profile_type(account)
                # full name
                fullname = account.get('fullname')
                # username
                username = account.get('username')
                # profile picture url
                pp_mt, pp_url, pp_size = get_media(account.get('profilePicture'))
                pp_url_html = generic_url(pp_url, html_format=True)
                # profile picture
                pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                # gender
                gender = get_key0(account.get('gender'))
                # birth date
                birth_date = convert_cocoa_core_data_ts_to_utc(account.get('birthDate'))
                # biography
                biography = account.get('biography')
                # country code
                country_code = account.get('countryCode')
                # region
                region = account.get('region')
                # 2.x, 4.x
                if bool(region) and isinstance(region, dict):
                    region = account.get('region', {}).get('value')
                # location/address
                address = account.get('location')
                # phone number
                phone_number = account.get('phoneNumber')
                # devices
                devices = get_devices(account)
                devices_html = get_devices(account, html_format=True)
                # is private?
                is_private = account.get('isPrivate')
                # realmojis
                realmojis = get_realmojis(account)
                realmojis_html = get_realmojis(account, html_format=True)
                # unique id/user id
                id = account.get('id')

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f"[object]"

                # html row
                data_list_html.append((created, profile_type, fullname, username, pp_url_html, pp_media_ref_id, gender, birth_date, biography,
                                       country_code, region, address, devices_html[3], phone_number, devices_html[0], devices_html[1], devices_html[2],
                                       is_private, realmojis_html, id, source_file_name_html, location))
                # lava row
                data_list.append((created, profile_type, fullname, username, pp_url, pp_media_ref_id, gender, birth_date, biography,
                                  country_code, region, address, devices[3], phone_number, devices[0], devices[1], devices[2],
                                  is_private, realmojis, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/person\/me$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    db_device_file_paths = [ device_file_path ]

                    # from file?
                    isDataOnFS = bool(record[2])
                    # from FS
                    if isDataOnFS:
                        fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                        json_data = get_json_file_content(fs_cached_data_path)
                        if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                    # from BLOB
                    else:
                        json_data = get_json_content(record[3])

                    device_file_paths = db_device_file_paths

                    # accounts
                    if not (bool(json_data) or isinstance(json_data, dict)):
                        continue

                    # account
                    account = json_data
                    if not bool(account):
                        continue

                    # created
                    created = convert_iso8601_to_utc(account.get('createdAt'))
                    # profile type
                    profile_type = get_profile_type(account)
                    # full name
                    fullname = account.get('fullname')
                    # username
                    username = account.get('username')
                    # profile picture url
                    pp_mt, pp_url, pp_size = get_media(account.get('profilePicture'))
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # gender
                    gender = account.get('gender')
                    # birth date
                    birth_date = convert_iso8601_to_utc(account.get('birthdate'))
                    # biography
                    biography = account.get('biography')
                    # country code
                    country_code = account.get('countryCode')
                    # region
                    region = account.get('region')
                    # location/address
                    address = account.get('location')
                    # phone number
                    phone_number = account.get('phoneNumber')
                    # devices
                    devices = get_devices(account)
                    devices_html = get_devices(account, html_format=True)
                    # is private?
                    is_private = account.get('isPrivate')
                    # realmojis
                    realmojis = get_realmojis(account)
                    realmojis_html = get_realmojis(account, html_format=True)
                    # unique id/user id
                    id = account.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((created, profile_type, fullname, username, pp_url_html, pp_media_ref_id, gender, birth_date, biography,
                                           country_code, region, address, devices_html[3], phone_number, devices_html[0], devices_html[1], devices_html[2],
                                           is_private, realmojis_html, id, source_file_name_html, location))
                    # lava row
                    data_list.append((created, profile_type, fullname, username, pp_url, pp_media_ref_id, gender, birth_date, biography,
                                      country_code, region, address, devices[3], phone_number, devices[0], devices[1], devices[2],
                                      is_private, realmojis, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Accounts: " + str(ex))
                pass

        # EntitiesStore.sqlite
        elif file_rel_path.endswith('EntitiesStore.sqlite'):
            try:
                query = '''
                SELECT
                    U.Z_PK,
                    U.ZPROFILETYPE,
                    U.ZFULLNAME,
                    U.ZUSERNAME,
                    U.ZPROFILEPICTUREURL,
                    U.ZBIO,
                    U.ZID
                FROM ZUSERMO AS "U"
                WHERE U.ZID = "{0}"
                '''.format(bereal_user_id)
                db_records = get_sqlite_db_records(file_found, query)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    device_file_paths = [ device_file_path ]

                    # profile type
                    profile_type = get_profile_type(record[1])
                    # full name
                    fullname = record[2]
                    # username
                    username = record[3]
                    # profile picture url
                    pp_url = record[4]
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # biography
                    biography = record[5]
                    # unique id/user id
                    id = record[6]

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"ZUSERMO (Z_PK: {record[0]})" ]
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((None, profile_type, fullname, username, pp_url_html, pp_media_ref_id, None, None, biography,
                                           None, None, None, None, None, None, None, None,
                                           None, None, id, source_file_name_html, location))
                    # lava row
                    data_list.append((None, profile_type, fullname, username, pp_url, pp_media_ref_id, None, None, biography,
                                      None, None, None, None, None, None, None, None,
                                      None, None, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - EntitiesStore.sqlite Accounts: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# contacts
@artifact_processor
def bereal_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        'Full name',
        'Family name',
        'Middle name',
        'Given name',
        'Nick name',
        ('Profile picture', 'media', 'height: 96px; border-radius: 50%;'),
        'Organization name',
        'Phone numbers',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_contacts']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        try:
            # json data
            json_data = get_json_file_content(file_found)
            if not bool(json_data):
                continue

            # contacts
            contacts = json_data.get('object')
            if not bool(contacts):
                continue

            # array
            for i in range(0, len(contacts)):
                device_file_paths = [ device_file_path ]
        
                contact = contacts[i]
                if not bool(contact):
                    continue

                # full name
                full_name = contact.get('completeName')
                # family name
                family_name = contact.get('familyName')
                # middle name
                middle_name = contact.get('middleName')
                # given name
                given_name = contact.get('givenName')
                # nick name
                nick_name = contact.get('nickName')
                # photo (base64)
                photo_b64 = contact.get('photo')
                if bool(photo_b64):
                    photo_raw = standard_b64decode(photo_b64)   # bytes
                    pp_media_ref_id = check_in_embedded_media(seeker, file_found, photo_raw, artifact_info)
                else:
                    pp_media_ref_id = None
                # organization name
                organization_name = contact.get('organizationName')
                # phone numbers
                phone_numbers = LINE_BREAK.join(contact.get('phoneNumbers'))
                phone_numbers_html = HTML_LINE_BREAK.join(contact.get('phoneNumbers'))

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f"[object][{i}]"

                # html row
                data_list_html.append((full_name, family_name, middle_name, given_name, nick_name, pp_media_ref_id, organization_name,
                                       phone_numbers_html, source_file_name_html, location))
                # lava row
                data_list.append((full_name, family_name, middle_name, given_name, nick_name, pp_media_ref_id, organization_name,
                                  phone_numbers, source_file_name, location))
        except Exception as ex:
            logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
            pass

    return data_headers, (data_list, data_list_html), ' '


# persons
@artifact_processor
def bereal_persons(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Profile type',
        'Full name',
        'User name',
        'Profile picture URL',
        ('Profile picture', 'media', 'height: 96px; border-radius: 50%;'),
        'Biography',
        'Address',
        'Relationship',
        ('Friended at', 'datetime'),
        'URLs',
        'Streak count',
        'Unique ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_persons']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # PersonRepository
        if file_rel_path.startswith('PersonRepository'):
            try:
                device_file_paths = [ device_file_path ]

                # json data
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # person
                person = json_data.get('object')
                if not bool(person):
                    continue

                # created (utc)
                created = convert_cocoa_core_data_ts_to_utc(person.get('createdAt'))
                # profile type
                profile_type = get_profile_type(person)
                # fullname
                fullname = person.get('fullname')
                # username
                username = person.get('username')
                # profile picture url
                pp_url = person.get('profilePictureURL')
                pp_url_html = generic_url(pp_url, html_format=True)
                # profile picture
                pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                # biography
                biography = person.get('biography')
                # location
                address = person.get('location')
                # relationship
                relationship = person.get('relationship')
                if bool(relationship):
                    relationship_type = ''
                    # status
                    relationship_status = relationship.get('status')
                    if relationship_status == 'accepted' or relationship_status == 'pending':
                        relationship_type = 'Friend'
                    # friended at
                    relationship_friended_at = convert_cocoa_core_data_ts_to_utc(relationship.get('friendedAt'))
                else:
                    relationship_type = ''  # Following?
                    relationship_friended_at = ''
                # links
                links = get_links(person.get('links'))
                links_html = get_links(person.get('links'), html_format=True)
                # streak count
                streak_count = person.get('streakCount')
                # unique id
                id = person.get('id')

                # source file name
                device_file_paths = dict.fromkeys(device_file_paths)
                source_file_name = unordered_list(device_file_paths)
                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                # location
                location = f"[object]"

                # html row
                data_list_html.append((created, profile_type, fullname, username, pp_url_html, pp_media_ref_id, biography, address,
                                       relationship_type, relationship_friended_at, links_html, streak_count, id, source_file_name_html, location))
                # lava row
                data_list.append((created, profile_type, fullname, username, pp_url, pp_media_ref_id, biography, address,
                                  relationship_type, relationship_friended_at, links, streak_count, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-Production_officialAccountProfiles
        elif file_rel_path.startswith('disk-bereal-Production_officialAccountProfiles'):
            try:
                # json data
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # persons
                persons = json_data.get('object')
                if not bool(persons):
                    continue
                for uid, person in persons.items():
                    device_file_paths = [ device_file_path ]

                    # uids
                    if not bool(person):
                        continue
                    
                    # created (utc)
                    created = None
                    # profile type
                    profile_type = get_profile_type(person)
                    # fullname
                    fullname = person.get('fullname')
                    # username
                    username = person.get('username')
                    # profile picture url
                    pp_url = person.get('profilePictureURL')
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # biography
                    biography = person.get('biography')
                    # location
                    address = person.get('location')
                    # relationship
                    relationship_type = ''  # Following?
                    relationship_friended_at = ''
                    # links
                    links = get_links(person.get('links'))
                    links_html = get_links(person.get('links'), html_format=True)
                    # streak count
                    streak_count = None
                    # unique id
                    id = person.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[object][{uid}]"

                    # html row
                    data_list_html.append((created, profile_type, fullname, username, pp_url_html, pp_media_ref_id, biography, address,
                                           relationship_type, relationship_friended_at, links_html, streak_count, id, source_file_name_html, location))
                    # lava row
                    data_list.append((created, profile_type, fullname, username, pp_url, pp_media_ref_id, biography, address,
                                      relationship_type, relationship_friended_at, links, streak_count, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/person\/profiles\/[\w-]+\?')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    db_device_file_paths = [ device_file_path ]

                    # from file?
                    isDataOnFS = bool(record[2])
                    # from FS
                    if isDataOnFS:
                        fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                        json_data = get_json_file_content(fs_cached_data_path)
                        if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                    # from BLOB
                    else:
                        json_data = get_json_content(record[3])

                    device_file_paths = db_device_file_paths

                    # person
                    if not (bool(json_data) or isinstance(json_data, dict)):
                        continue

                    # person
                    person = json_data
                    if not bool(person):
                        continue

                    # created (utc)
                    created = convert_iso8601_to_utc(person.get('createdAt'))
                    # profile type
                    profile_type = get_profile_type(person)
                    # fullname
                    fullname = person.get('fullname')
                    # username
                    username = person.get('username')
                    # profile picture url
                    pp_mt, pp_url, pp_size = get_media(person.get('profilePicture'))
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # biography
                    biography = person.get('biography')
                    # location
                    address = person.get('location')
                    # relationship
                    relationship = person.get('relationship')
                    if bool(relationship):
                        relationship_type = ''
                        # status
                        relationship_status = relationship.get('status')
                        if relationship_status == 'accepted' or relationship_status == 'pending':
                            relationship_type = 'Friend'
                        # friended at
                        relationship_friended_at = convert_iso8601_to_utc(relationship.get('friendedAt'))
                    else:
                        relationship_type = None    # Following?
                        relationship_friended_at = None
                    # links
                    links = get_links(person.get('links'))
                    links_html = get_links(person.get('links'), html_format=True)
                    # streak length
                    streak_count = person.get('streakLength')
                    # unique id
                    id = person.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((created, profile_type, fullname, username, pp_url_html, pp_media_ref_id, biography, address,
                                           relationship_type, relationship_friended_at, links_html, streak_count, id, source_file_name_html, location))
                    # lava row
                    data_list.append((created, profile_type, fullname, username, pp_url, pp_media_ref_id, biography, address,
                                      relationship_type, relationship_friended_at, links, streak_count, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Persons: " + str(ex))
                pass
            
    return data_headers, (data_list, data_list_html), ' '


# friends
@artifact_processor
def bereal_friends(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Status updated at', 'datetime'),
        'Status',
        'Profile type',
        'Full name',
        'Username',
        'Profile picture URL',
        ('Profile picture', 'media', 'height: 96px; border-radius: 50%;'),
        'Mutual friends',
        'Unique ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_friends']['name']

    # status
    def status_friendly_name(status):
        if bool(status):
            value = status.lower()
            if value == 'accepted': value = 'Friend'
            elif value == 'sent': value = 'Request Sent'
            elif value == 'pending': value = 'Request Received'
            elif value == 'canceled': value = 'Request Canceled'
            elif value == 'rejected': value = 'Request Rejected'
            return value
        else:
            return ''


    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)
            
        # following (dictionary)
        # disk-bereal-Production_FriendsStorage.following/<GUID>.following
        # disk-bereal-Production_FriendsStorage.followers/<GUID>.followers
        if file_rel_path.endswith('.following') or file_rel_path.endswith('.followers'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # relationship
                relationship = obj_ref.get('relationship', '')
                # users
                obj_ref = obj_ref.get('users')
                if not bool(obj_ref):
                    continue

                # array
                for i in range(0, len(obj_ref)):
                    device_file_paths = [ device_file_path ]

                    user = obj_ref[i]
                    if not bool(user):
                        continue

                    # status
                    status = 'Following' if relationship.lower() == 'following' else "Follower"
                    # profile type
                    profile_type = get_profile_type(user)
                    # fullname
                    fullname = user.get('fullname')
                    # username
                    username = user.get('username')
                    # profile picture url
                    pp_url = user.get('profilePictureURL')
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # unique id
                    id = user.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[object][users][{i}]"

                    # html row
                    data_list_html.append((None, status, profile_type, fullname, username, pp_url_html, pp_media_ref_id,
                                           None, id, source_file_name_html, location))
                    # lava row
                    data_list.append((None, status, profile_type, fullname, username, pp_url, pp_media_ref_id,
                                      None, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # friends (array)
        # disk-bereal-RelationshipsFriendsListManager/*
        # disk-bereal-RelationshipsRequestSentListManager/*
        # disk-bereal-RelationshipsRequestReceivedListManager/*
        elif file_rel_path.startswith('disk-bereal-RelationshipsFriendsListManager') or \
                file_rel_path.startswith('disk-bereal-RelationshipsRequestSentListManager') or \
                file_rel_path.startswith('disk-bereal-RelationshipsRequestReceivedListManager'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # array
                for i in range(0, len(obj_ref)):
                    device_file_paths = [ device_file_path ]

                    friend = obj_ref[i]
                    if not friend:
                        continue

                    # status updated at
                    status_updated_at = convert_cocoa_core_data_ts_to_utc(friend.get('statusUpdatedAt'))
                    # status
                    status = status_friendly_name(friend.get('status'))
                    # profile type
                    profile_type = get_profile_type(friend)
                    # fullname
                    fullname = friend.get('fullname')
                    # username
                    username = friend.get('username')
                    # profile picture url
                    pp_url = friend.get('profilePictureURL')
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # mutual friends
                    mutual_friends = friend.get('mutualFriends')
                    # unique id
                    id = friend.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[object][{i}]"

                    # html row
                    data_list_html.append((status_updated_at, status, profile_type, fullname, username, pp_url_html, pp_media_ref_id,
                                           mutual_friends, id, source_file_name_html, location))
                    # lava row
                    data_list.append((status_updated_at, status, profile_type, fullname, username, pp_url, pp_media_ref_id,
                                      mutual_friends, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # friends
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/relationships\/friends($|\/\?page)')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        obj_ref = json_data.get('data')
                        if not bool(obj_ref):
                            continue

                        # array
                        for i in range(0, len(obj_ref)):
                            device_file_paths = db_device_file_paths

                            friend = obj_ref[i]
                            if not friend:
                                continue

                            # status
                            status = status_friendly_name(friend.get('status'))
                            # profile type
                            profile_type = get_profile_type(friend)
                            # fullname
                            fullname = friend.get('fullname')
                            # username
                            username = friend.get('username')
                            # profile picture url
                            pp_mt, pp_url, pp_size = get_media(friend.get('profilePicture'))
                            pp_url_html = generic_url(pp_url, html_format=True)
                            # profile picture
                            pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                            pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                            if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                            # unique id
                            id = friend.get('id')

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                            location.append(f"[data][{i}]")
                            location = COMMA_SEP.join(location)

                            # html row
                            data_list_html.append((None, status, profile_type, fullname, username, pp_url_html, pp_media_ref_id,
                                                   None, id, source_file_name_html, location))
                            # lava row
                            data_list.append((None, status, profile_type, fullname, username, pp_url, pp_media_ref_id,
                                              None, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Friends: " + str(ex))
                pass

            try:
                # friend requests (received/sent)
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/relationships\/friend-requests\/(received|sent)\?page')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        obj_ref = json_data.get('data')
                        if not bool(obj_ref):
                            continue

                        # array
                        for i in range(0, len(obj_ref)):
                            device_file_paths = db_device_file_paths

                            friend = obj_ref[i]
                            if not friend:
                                continue

                            # status updated at
                            status_updated_at = convert_iso8601_to_utc(friend.get('updatedAt'))
                            # status
                            status = status_friendly_name(friend.get('status'))
                            # profile type
                            profile_type = get_profile_type(friend)
                            # fullname
                            fullname = friend.get('fullname')
                            # username
                            username = friend.get('username')
                            # profile picture url
                            pp_mt, pp_url, pp_size = get_media(friend.get('profilePicture'))
                            pp_url_html = generic_url(pp_url, html_format=True)
                            # profile picture
                            pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                            pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                            if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                            # mutual friends
                            mutual_friends = friend.get('mutualFriends')
                            # unique id
                            id = friend.get('id')

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                            location.append(f"[data][{i}]")
                            location = COMMA_SEP.join(location)

                            # html row
                            data_list_html.append((status_updated_at, status, profile_type, fullname, username, pp_url_html, pp_media_ref_id,
                                                   mutual_friends, id, source_file_name_html, location))
                            # lava row
                            data_list.append((status_updated_at, status, profile_type, fullname, username, pp_url, pp_media_ref_id,
                                              mutual_friends, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Friend requests: " + str(ex))
                pass

        # EntitiesStore.sqlite
        elif file_rel_path.endswith('EntitiesStore.sqlite'):
            try:
                query = '''
                SELECT
                    U.Z_PK,
                    U.ZPROFILETYPE,
                    U.ZFULLNAME,
                    U.ZUSERNAME,
                    U.ZPROFILEPICTUREURL,
                    U.ZBIO,
                    U.ZID
                FROM ZUSERMO AS "U"
                WHERE U.ZID != "{0}"
                '''.format(bereal_user_id)
                db_records = get_sqlite_db_records(file_found, query)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    device_file_paths = [ device_file_path ]

                    # profile type
                    profile_type = get_profile_type(record[1])
                    # full name
                    fullname = record[2]
                    # username
                    username = record[3]
                    # profile picture url
                    pp_url = record[4]
                    pp_url_html = generic_url(pp_url, html_format=True)
                    # profile picture
                    pp_media_ref_id = media_item_from_url(seeker, pp_url, artifact_info)
                    pp_media_item = lava_get_full_media_info(pp_media_ref_id)
                    if pp_media_item: device_file_paths.append(get_device_file_path(pp_media_item[5], seeker))
                    # biography
                    biography = record[5]
                    # unique id/user id
                    id = record[6]

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"ZUSERMO (Z_PK: {record[0]})" ]
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((None, None, profile_type, fullname, username, pp_url_html, pp_media_ref_id,
                                           None, id, source_file_name_html, location))
                    # lava row
                    data_list.append((None, None, profile_type, fullname, username, pp_url, pp_media_ref_id,
                                      None, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# blocked users
@artifact_processor
def bereal_blocked_users(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Blocked', 'datetime'),
        'Full name',
        'Username',
        'Unique ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['bereal_blocked_users']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # disk-bereal-BlockedUserManager
        if file_rel_path.endswith('disk-bereal-BlockedUserManager'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # users
                users = json_data.get('object')
                if not bool(users):
                    continue

                # array
                for i in range(0, len(users)):
                    device_file_paths = [ device_file_path ]

                    user = users[i]
                    if not bool(user):
                        continue

                    # blocked date
                    blocked_date = convert_cocoa_core_data_ts_to_utc(user.get('blockedDate'))
                    # fullname
                    fullname = user.get('fullname')
                    # username
                    username = user.get('username')
                    # unique id
                    id = user.get('id')

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[object][{i}]"

                    # html row
                    data_list_html.append((blocked_date, fullname, username, id, source_file_name_html, location))
                    # lava row
                    data_list.append((blocked_date, fullname, username, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # blocked users
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/moderation\/block-users\?page')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    db_device_file_paths = [ device_file_path ]

                    # from file?
                    isDataOnFS = bool(record[2])
                    # from FS
                    if isDataOnFS:
                        fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                        json_data = get_json_file_content(fs_cached_data_path)
                        if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                    # from BLOB
                    else:
                        json_data = get_json_content(record[3])

                    # object?
                    users = json_data.get('data')
                    if not bool(users):
                        continue

                    # array
                    for i in range(0, len(users)):
                        device_file_paths = db_device_file_paths

                        user = users[i]
                        if not user:
                            continue

                        # blocked date
                        blocked_date = convert_iso8601_to_utc(user.get('blockedAt'))
                        # fullname
                        fullname = user.get('user', {}).get('fullname')
                        # username
                        username = user.get('user', {}).get('username')
                        # unique id
                        id = user.get('user', {}).get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                        location.append(f"[data][{i}]")
                        location = COMMA_SEP.join(location)

                        # html row
                        data_list_html.append((blocked_date, fullname, username, id, source_file_name_html, location))
                        # lava row
                        data_list.append((blocked_date, fullname, username, id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Blocked Users: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# posts
@artifact_processor
def bereal_posts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Taken at', 'datetime'),
        'Post type',
        'Author',
        'Primary media type',
        'Primary URL',
        ('Primary image', 'media', 'height: 96px; border-radius: 5%;'),
        'Secondary media type',
        'Secondary URL',
        ('Secondary image', 'media', 'height: 96px; border-radius: 5%;'),
        'Thumbnail media type',
        'Thumbnail URL',
        ('Thumbnail image', 'media', 'height: 96px; border-radius: 5%;'),
        'Song title',
        'Song URL',
        'Caption',
        'Latitude',
        'Longitude',
        'Retake counter',
        'Late time',
        'Visibility',
        'Tagged friends',
        'Moment ID',
        'BeReal ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_posts']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # PersonRepository
        if file_rel_path.startswith('PersonRepository'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # posts
                posts = obj_ref.get('beRealOfTheDay', {}).get('series', {}).get('posts')
                if not bool(posts):
                    continue

                # array
                for i in range(0, len(posts)):
                    device_file_paths = [ device_file_path ]
    
                    post = posts[i]
                    if not bool(post):
                        continue

                    # bereal id
                    bereal_id = post.get('id')
                    # moment id
                    moment_id = post.get('momentID')
                    # is late?
                    is_late = post.get('isLate')
                    # late in seconds
                    late_secs = get_late_secs(post)
                    # post type
                    post_type = format_post_type(is_late, post.get('isMain'))
                    # caption
                    caption = post.get('caption')
                    # latitude
                    latitude = post.get('location', {}).get('latitude')
                    # longitude
                    longitude = post.get('location', {}).get('longitude')
                    # author
                    author_id, author_user_name = get_user(post)
                    author = format_userid(author_id, author_user_name)
                    # visibilities
                    visibilities = get_post_visibilities(post)
                    visibilities_html = get_post_visibilities(post, html_format=True)
                    # taken at
                    taken_at = convert_cocoa_core_data_ts_to_utc(post.get('takenAt'))
                    # retake counter
                    retake_counter = post.get('retakeCounter')
                    # primary
                    p_mt, p_url, p_size = get_media(post.get('primaryMedia'))
                    p_url_html = generic_url(p_url, html_format=True)
                    p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                    p_media_item = lava_get_full_media_info(p_media_ref_id)
                    if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                    # secondary
                    s_mt, s_url, s_size = get_media(post.get('secondaryMedia'))
                    s_url_html = generic_url(s_url, html_format=True)
                    s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                    s_media_item = lava_get_full_media_info(s_media_ref_id)
                    if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                    # music
                    song_title = None
                    song_url = None
                    song_url_html = None
                    # tags
                    tags = get_tags(post)
                    tags_html = get_tags(post, html_format=True)

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = f"[object][beRealOfTheDay][series][posts][{i}]"

                    # html row
                    data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                           None, None, None, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                           visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                    # lava row
                    data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                      None, None, None, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                      visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-MemoriesRepository-subject-key
        elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # author
                author = format_userid(bereal_user_id)

                # array
                for i in range(0, len(obj_ref)):
                    memory = obj_ref[i]
                    if not bool(memory):
                        continue

                    # is late
                    is_late = memory.get('isLate')
                    # detailed posts
                    detailed_posts = memory.get('allDetailedPosts')
                    if not bool(detailed_posts):
                        continue

                    for j in range(0, len(detailed_posts)):
                        device_file_paths = [ device_file_path ]

                        # detailed post
                        detailed_post = detailed_posts[j]
                        if not bool(detailed_post):
                            continue

                        # bereal id
                        bereal_id = detailed_post.get('id')
                        # moment id
                        moment_id = detailed_post.get('momentID')
                        # post type
                        post_type = get_post_type(detailed_post, is_late)
                        # late in seconds???
                        late_secs = get_late_secs(detailed_post)
                        # metadata
                        metadata = detailed_post.get('details', {}).get('full', {}).get('metadata')
                        if not bool(metadata):
                            continue
                        # caption
                        caption = metadata.get('caption')
                        # latitude
                        latitude = metadata.get('location', {}).get('latitude')
                        # longitude
                        longitude = metadata.get('location', {}).get('longitude')
                        # tags
                        tags = get_tags(metadata)
                        tags_html = get_tags(metadata, html_format=True)
                        # visibilities
                        visibilities = visibilities_html = None
                        # full data
                        data = detailed_post.get('details', {}).get('full', {}).get('data')
                        # preview data
                        if not bool(data):
                            data = detailed_post.get('details', {}).get('preview', {}).get('data')
                        if not bool(data):
                            continue
                        # taken at
                        taken_at = convert_cocoa_core_data_ts_to_utc(data.get('takenAt'))
                        # retake counter
                        retake_counter = data.get('retakeCounter')
                        # late in seconds???
                        late_secs = get_late_secs(data)
                        # is video?
                        is_video = get_key0(data.get('postType')) == 'video'
                        # primary
                        primary = data.get('primary', {})
                        p_mt, p_url, p_size = get_media(primary)
                        p_url_html = generic_url(p_url, html_format=True)
                        if is_video:
                            p_media_ref_id = media_item_from_url(seeker, get_place_holder0_url(primary), artifact_info, from_photos=True)
                        else:
                            p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                        p_media_item = lava_get_full_media_info(p_media_ref_id)
                        if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                        # secondary
                        secondary = data.get('secondary', {})
                        s_mt, s_url, s_size = get_media(secondary)
                        s_url_html = generic_url(s_url, html_format=True)
                        if is_video:
                            s_media_ref_id = media_item_from_url(seeker, get_place_holder0_url(secondary), artifact_info, from_photos=True)
                        else:
                            s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                        s_media_item = lava_get_full_media_info(s_media_ref_id)
                        if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                        # thumbnail
                        thumbnail = data.get('thumbnail', {})
                        t_mt, t_url, t_size = get_media(thumbnail)
                        t_url_html = generic_url(t_url, html_format=True)
                        t_media_ref_id = media_item_from_url(seeker, t_url, artifact_info, from_photos=is_video)
                        t_media_item = lava_get_full_media_info(t_media_ref_id)
                        if t_media_item: device_file_paths.append(get_device_file_path(t_media_item[5], seeker))

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = f"[object][{i}]"

                        # html row
                        data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                               t_mt, t_url_html, t_media_ref_id, None, None, caption, latitude, longitude, retake_counter, late_secs,
                                               visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                        # lava row
                        data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                          t_mt, t_url, t_media_ref_id, None, None, caption, latitude, longitude, retake_counter, late_secs,
                                          visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-Production_postFeedItems
        elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # array (string, array)
                for i in range(0, len(obj_ref)):
                    # array
                    if not (bool(obj_ref[i]) and isinstance(obj_ref[i], list)):
                        continue

                    # moment
                    for m in range(0, len(obj_ref[i])):
                        moment = obj_ref[i][m]
                        if not bool(moment):
                            continue

                        # author
                        author_id, author_user_name = get_user(moment)
                        author = format_userid(author_id, author_user_name)

                        # posts
                        posts = moment.get('posts')
                        if not bool(posts):
                            continue

                        for p in range(0, len(posts)):
                            device_file_paths = [ device_file_path ]

                            post = posts[p]
                            if not bool(post):
                                continue

                            # bereal id
                            bereal_id = post.get('id')
                            # moment id
                            moment_id = post.get('momentID')
                            # is late?
                            is_late = post.get('isLate')
                            # late in seconds
                            late_secs = get_late_secs(post)
                            # post type
                            post_type = format_post_type(is_late, post.get('isMain'))
                            # caption
                            caption = post.get('caption')
                            # latitude
                            latitude = post.get('location', {}).get('latitude')
                            # longitude
                            longitude = post.get('location', {}).get('longitude')
                            # tags
                            tags = get_tags(post)
                            tags_html = get_tags(post, html_format=True)
                            # visibilities
                            visibilities = get_post_visibilities(post)
                            visibilities_html = get_post_visibilities(post, html_format=True)
                            # taken at
                            taken_at = convert_cocoa_core_data_ts_to_utc(post.get('takenAt'))
                            # retake counter
                            retake_counter = post.get('retakeCounter')
                            # primary
                            primary = post.get('primaryMedia', {})
                            p_mt, p_url, p_size = get_media(primary)
                            p_url_html = generic_url(p_url, html_format=True)
                            if p_mt == 'video':
                                p_media_ref_id = media_item_from_url(seeker, post.get('primaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                            p_media_item = lava_get_full_media_info(p_media_ref_id)
                            if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                            # secondary
                            secondary = post.get('secondaryMedia', {})
                            s_mt, s_url, s_size = get_media(secondary)
                            s_url_html = generic_url(s_url, html_format=True)
                            if s_mt == 'video':
                                s_media_ref_id = media_item_from_url(seeker, post.get('secondaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                            s_media_item = lava_get_full_media_info(s_media_ref_id)
                            if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                            # music
                            song_title = None
                            song_url = None
                            song_url_html = None

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = f"[object][{i}][{m}][posts][{p}]"

                            # html row
                            data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                                   None, None, None, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                                   visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                            # lava row
                            data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                              None, None, None, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                              visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # person posts
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/person\/profiles\/[\w-]+\?')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # user posts
                        user_posts = json_data.get('beRealOfTheDay', {}).get('userPosts')
                        if not bool(user_posts):
                            continue

                        # author
                        author_id, author_user_name = get_user(user_posts)
                        author = format_userid(author_id, author_user_name)

                        # moment id
                        moment_id = user_posts.get('momentId')
                        if not bool(moment_id): moment_id = user_posts.get('moment', {}).get('id')

                        # posts
                        posts = user_posts.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            device_file_paths = db_device_file_paths

                            post = posts[i]
                            if not bool(post):
                                continue

                            # bereal id
                            bereal_id = post.get('id')
                            # is late?
                            is_late = post.get('isLate')
                            # late in seconds
                            late_secs = get_late_secs(post)
                            # post type
                            post_type = format_post_type(is_late, post.get('isMain'))
                            # caption
                            caption = post.get('caption')
                            # latitude
                            latitude = post.get('location', {}).get('latitude')
                            # longitude
                            longitude = post.get('location', {}).get('longitude')
                            # visibilities
                            visibilities = get_post_visibilities(post)
                            visibilities_html = get_post_visibilities(post, html_format=True)
                            # taken at
                            taken_at = convert_iso8601_to_utc(post.get('takenAt'))
                            # retake counter
                            retake_counter = post.get('retakeCounter')
                            # primary
                            primary = post.get('primary', {})
                            p_mt, p_url, p_size = get_media(primary)
                            p_url_html = generic_url(p_url, html_format=True)
                            if p_mt == 'video':
                                p_media_ref_id = media_item_from_url(seeker, post.get('primaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                            p_media_item = lava_get_full_media_info(p_media_ref_id)
                            if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                            # secondary
                            secondary = post.get('secondary', {})
                            s_mt, s_url, s_size = get_media(secondary)
                            s_url_html = generic_url(s_url, html_format=True)
                            if s_mt == 'video':
                                s_media_ref_id = media_item_from_url(seeker, post.get('secondaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                            s_media_item = lava_get_full_media_info(s_media_ref_id)
                            if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                            # music
                            song_title = None
                            song_url = None
                            song_url_html = None
                            # tags
                            tags = get_tags(post)
                            tags_html = get_tags(post, html_format=True)

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                            location.append(f"[beRealOfTheDay][userPosts][posts][{i}]")
                            location = COMMA_SEP.join(location)

                            # html row
                            data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                                   None, None, None, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                                   visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                            # lava row
                            data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                              None, None, None, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                              visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Person Posts: " + str(ex))
                pass

            try:
                # memories
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/memories-v(\d)+\/[\w-]+$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # posts
                        posts = json_data.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            device_file_paths = db_device_file_paths

                            post = posts[i]
                            if not bool(post):
                                continue

                            # moment id
                            moment_id = str(record[1]).split('/')[-1]
                            # bereal id
                            bereal_id = post.get('id')
                            # late in seconds
                            late_secs = get_late_secs(post)
                            # post type
                            post_type = format_post_type(post.get('isLate'), post.get('isMain'))
                            # caption
                            caption = post.get('caption')
                            # latitude
                            latitude = post.get('location', {}).get('latitude')
                            # longitude
                            longitude = post.get('location', {}).get('longitude')
                            # visibilities
                            visibilities = get_post_visibilities(post)
                            visibilities_html = get_post_visibilities(post, html_format=True)
                            # taken at
                            taken_at = convert_iso8601_to_utc(post.get('takenAt'))
                            # retake counter
                            retake_counter = post.get('retakeCounter')
                            # primary
                            primary = post.get('primary', {})
                            p_mt, p_url, p_size = get_media(primary)
                            p_url_html = generic_url(p_url, html_format=True)
                            if p_mt == 'video':
                                p_media_ref_id = media_item_from_url(seeker, post.get('primaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                            p_media_item = lava_get_full_media_info(p_media_ref_id)
                            if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                            # secondary
                            secondary = post.get('secondary', {})
                            s_mt, s_url, s_size = get_media(secondary)
                            s_url_html = generic_url(s_url, html_format=True)
                            if s_mt == 'video':
                                s_media_ref_id = media_item_from_url(seeker, post.get('secondaryPlaceholder', {}).get('url'), artifact_info, from_photos=True)
                            else:
                                s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                            s_media_item = lava_get_full_media_info(s_media_ref_id)
                            if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                            # thumbnail
                            thumbnail = post.get('thumbnail', {})
                            t_mt, t_url, t_size = get_media(thumbnail)
                            t_url_html = generic_url(t_url, html_format=True)
                            t_media_ref_id = media_item_from_url(seeker, t_url, artifact_info, from_photos = p_mt == 'video')
                            t_media_item = lava_get_full_media_info(t_media_ref_id)
                            if t_media_item: device_file_paths.append(get_device_file_path(t_media_item[5], seeker))
                            # music
                            song_title = get_music_artist_and_track(post)
                            song_url = get_music_url(post)
                            song_url_html = get_music_url(post, html_format=True)
                            # tags
                            tags = get_tags(post)
                            tags_html = get_tags(post, html_format=True)
                            # author
                            author = format_userid(bereal_user_id)

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                            location.append(f"[posts][{i}]")
                            location = COMMA_SEP.join(location)

                            # html row
                            data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                                   t_mt, t_url_html, t_media_ref_id, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                                   visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                            # lava row
                            data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                              t_mt, t_url, t_media_ref_id, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                              visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Memories Posts: " + str(ex))
                pass

            # feeds discovery
            try:
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/discovery$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # json
                        if not bool(json_data):
                            continue

                        # posts
                        posts = json_data.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            device_file_paths = db_device_file_paths
            
                            post = posts[i]
                            if not bool(post):
                                continue

                            # moment id
                            moment_id = None
                            # bereal id
                            bereal_id = post.get('id')
                            # late in seconds
                            late_secs = get_late_secs(post)
                            # post type
                            post_type = format_post_type(post.get('mediaType') == 'late', True)
                            # caption
                            caption = post.get('caption')
                            # latitude
                            latitude = post.get('location', {}).get('_latitude')
                            # longitude
                            longitude = post.get('location', {}).get('_longitude')
                            # visibilities
                            visibilities = get_post_visibilities(post)
                            visibilities_html = get_post_visibilities(post, html_format=True)
                            # taken at
                            taken_at = convert_ts_int_to_utc(post.get('takenAt', {}).get('_seconds'))
                            # retake counter
                            retake_counter = post.get('retakeCounter')
                            # primary
                            p_mt = 'photo'
                            p_url = post.get('photoURL')
                            p_url_html = generic_url(p_url, html_format=True)
                            p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                            p_media_item = lava_get_full_media_info(p_media_ref_id)
                            if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                            # secondary
                            s_mt = 'photo'
                            s_url = post.get('secondaryPhotoURL')
                            s_url_html = generic_url(s_url, html_format=True)
                            s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                            s_media_item = lava_get_full_media_info(s_media_ref_id)
                            if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                            # music
                            song_title = get_music_artist_and_track(post)
                            song_url = get_music_url(post)
                            song_url_html = get_music_url(post, html_format=True)
                            # tags
                            tags = get_tags(post)
                            tags_html = get_tags(post, html_format=True)
                            # author
                            author_id, author_user_name = get_user(post)
                            author = format_userid(author_id, author_user_name)

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                            location.append(f"[posts][{i}]")
                            location = COMMA_SEP.join(location)

                            # html row
                            data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                                   None, None, None, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                                   visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                            # lava row
                            data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                              None, None, None, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                              visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Feeds Discovery: " + str(ex))
                pass

        # EntitiesStore.sqlite
        elif file_rel_path.endswith('EntitiesStore.sqlite'):
            try:
                query = '''
                SELECT
                    P.Z_PK,
                    U.Z_PK,
                    PM.Z_PK,
                    SM.Z_PK,
                    PTM.Z_PK,
                    STM.Z_PK,
                    M.Z_PK,
                    L.Z_PK,
	                (P.ZTAKENAT + 978307200) AS "taken_at",
                    P.ZISLATE,
                    P.ZISMAIN,
                    U.ZID AS "author_id",
                    coalesce(U.ZFULLNAME, U.ZUSERNAME) AS "author_name",
                    PM.ZMEDIATYPE,
                    PM.ZURL,
                    SM.ZMEDIATYPE,
                    SM.ZURL,
                    PTM.ZMEDIATYPE,
                    PTM.ZURL,
                    STM.ZMEDIATYPE,
                    STM.ZURL,
                    (M.ZARTIST || " - " || M.ZTRACK) AS "song_title",
                    M.ZOPENURL,
                    P.ZCAPTION,
                    L.ZLATITUDE,
                    L.ZLONGITUDE,
                    P.ZRETAKECOUNTER,
                    P.ZLATEINSECONDS,
                    P.ZVISIBILITIES,
                    (P.ZRESHAREDFROM > 0) AS "reshared",
                    NULL AS "tags",
                    P.ZMOMENTID,
                    P.ZID AS "bereal_id"
                FROM ZPOSTMO AS "P"
                LEFT JOIN ZUSERMO AS "U" ON (P.ZUSER = U.Z_PK)
                LEFT JOIN ZPOSTMO_MEDIAMO AS "PM" ON (P.ZPRIMARYMEDIA = PM.Z_PK)
                LEFT JOIN ZPOSTMO_MEDIAMO AS "SM" ON (P.ZSECONDARYMEDIA = SM.Z_PK)
                LEFT JOIN ZPOSTMO_MEDIAMO AS "PTM" ON (P.ZPRIMARYTHUMBNAIL = PTM.Z_PK)
                LEFT JOIN ZPOSTMO_MEDIAMO AS "STM" ON (P.ZSECONDARYTHUMBNAIL = STM.Z_PK)
                LEFT JOIN ZPOSTMO_MUSICMO AS "M" ON (P.ZMUSIC = M.Z_PK)
                LEFT JOIN ZPOSTMO_LOCATIONMO AS "L" ON (P.ZLOCATION = L.Z_PK)
                '''
                db_records = get_sqlite_db_records(file_found, query)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    device_file_paths = [ device_file_path ]

                    # taken at
                    taken_at = convert_ts_int_to_utc(record[8])
                    # post type
                    post_type = format_post_type(record[9], record[10])
                    # author
                    author = format_userid(record[11], record[12])
                    # primary
                    p_mt = record[13]
                    p_url = generic_url(record[14])
                    p_url_html = generic_url(p_url, html_format=True)
                    p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                    p_media_item = lava_get_full_media_info(p_media_ref_id)
                    if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                    # secondary
                    s_mt = record[15]
                    s_url = generic_url(record[16])
                    s_url_html = generic_url(s_url, html_format=True)
                    s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                    s_media_item = lava_get_full_media_info(s_media_ref_id)
                    if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                    # primary thumbnail
                    t_mt = record[17]
                    t_url = generic_url(record[18])
                    t_url_html = generic_url(t_url, html_format=True)
                    t_media_ref_id = media_item_from_url(seeker, t_url, artifact_info, from_photos = p_mt == 'video')
                    t_media_item = lava_get_full_media_info(t_media_ref_id)
                    if t_media_item: device_file_paths.append(get_device_file_path(t_media_item[5], seeker))
                    # secondary thumbnail
# todo
                    # music
                    song_title = record[21]
                    song_url = generic_url(record[22])
                    song_url_html = get_music_url(song_url, html_format=True)
                    # caption
                    caption = record[23]
                    # latitude
                    latitude = record[24]
                    # longitude
                    longitude = record[25]
                    # retake counter
                    retake_counter = record[26]
                    # late in seconds
                    late_secs = get_late_secs(record[27])
                    # visibility
                    visibilities_plist = get_plist_content(record[28])
                    visibilities = get_post_visibilities(visibilities_plist)
                    visibilities_html = get_post_visibilities(visibilities_plist, html_format=True)
                    # reshared
                    reshared = record[29]
                    # tags
# todo
                    tags = record[30]
                    # moment id
                    moment_id = record[31]
                    # bereal id
                    bereal_id = record[32]
                    
                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"ZUSERMO (Z_PK: {record[0]})" ]
                    if record[1] is not None: location.append(f"ZPOSTMO_MEDIAMO (Z_PK: {record[1]})")
                    if record[2] is not None: location.append(f"ZPOSTMO_MEDIAMO (Z_PK: {record[2]})")
                    if record[3] is not None: location.append(f"ZPOSTMO_MEDIAMO (Z_PK: {record[3]})")
                    if record[4] is not None: location.append(f"ZPOSTMO_MEDIAMO (Z_PK: {record[4]})")
                    if record[5] is not None: location.append(f"ZPOSTMO_MUSICMO (Z_PK: {record[5]})")
                    if record[6] is not None: location.append(f"ZPOSTMO_LOCATIONMO (Z_PK: {record[6]})")
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                           t_mt, t_url_html, t_media_ref_id, song_title, song_url_html, caption, latitude, longitude, retake_counter, late_secs,
                                           visibilities_html, tags_html, moment_id, bereal_id, source_file_name_html, location))
                    # lava row
                    data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                      t_mt, t_url, t_media_ref_id, song_title, song_url, caption, latitude, longitude, retake_counter, late_secs,
                                      visibilities, tags, moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# pinned memories
@artifact_processor
def bereal_pinned_memories(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Pinned at', 'datetime'),
        'Post type',
        'Author',
        'Primary media type',
        'Primary URL',
        ('Primary image', 'media', 'height: 96px; border-radius: 5%;'),
        'Secondary media type',
        'Secondary URL',
        ('Secondary image', 'media', 'height: 96px; border-radius: 5%;'),
        'Moment ID',
        'BeReal ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_pinned_memories']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # disk-bereal-MemoriesRepository-pinnedMemories-key
        # disk-bereal-PersonRepository-pinnedMemories-key
        if file_rel_path.startswith('disk-bereal-MemoriesRepository-pinnedMemories-key') or file_rel_path.startswith('disk-bereal-PersonRepository-pinnedMemories-key'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # disk-bereal-MemoriesRepository-pinnedMemories-key
                if file_rel_path.startswith('disk-bereal-MemoriesRepository-pinnedMemories-key'):
                    # pinned
                    for i in range(0, len(obj_ref)):
                        device_file_paths = [ device_file_path ]

                        pin = obj_ref[i]
                        if not bool(pin):
                            continue

                        # taken at
                        taken_at = convert_cocoa_core_data_ts_to_utc(pin.get('takenAt'))
                        # post type
                        post_type = pin.get('analyticsPostType')
                        # author
                        author = format_userid(pin.get('analyticsAuthorID'))
                        # primary
                        p_mt, p_url, p_size = get_media(pin.get('primary'))
                        p_url_html = generic_url(p_url, html_format=True)
                        p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                        p_media_item = lava_get_full_media_info(p_media_ref_id)
                        if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                        # secondary
                        s_mt, s_url, s_size = get_media(pin.get('secondary'))
                        s_url_html = generic_url(s_url, html_format=True)
                        s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                        s_media_item = lava_get_full_media_info(s_media_ref_id)
                        if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                        # moment id
                        moment_id = pin.get('analyticsMomentID')
                        # bereal id
                        bereal_id = pin.get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = f"[object][{i}]"

                        # html row
                        data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                               moment_id, bereal_id, source_file_name_html, location))
                        # lava row
                        data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                          moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-PersonRepository-pinnedMemories-key
        elif file_rel_path.startswith('disk-bereal-PersonRepository-pinnedMemories-key'):
            try:
                # users
                for key, val in obj_ref.items():
                    # uids
                    if not bool(val) or not isinstance(val, list):
                        continue

                    # pinned
                    for i in range(0, len(val)):
                        device_file_paths = [ device_file_path ]

                        pin = val[i]
                        if not bool(pin):
                            continue

                        # taken at
                        taken_at = convert_cocoa_core_data_ts_to_utc(pin.get('takenAt'))
                        # post type
                        post_type = pin.get('analyticsPostType')
                        # author
                        author_id = pin.get('analyticsAuthorID')
                        author = format_userid(author_id)
                        # primary
                        p_mt, p_url, p_size = get_media(pin.get('primary'))
                        p_url_html = generic_url(p_url, html_format=True)
                        p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                        p_media_item = lava_get_full_media_info(p_media_ref_id)
                        if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                        # secondary
                        s_mt, s_url, s_size = get_media(pin.get('secondary'))
                        s_url_html = generic_url(s_url, html_format=True)
                        s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                        s_media_item = lava_get_full_media_info(s_media_ref_id)
                        if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                        # moment id
                        moment_id = pin.get('analyticsMomentID')
                        # bereal id
                        bereal_id = pin.get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = f"[object][{author_id}][{i}]"

                        # html row
                        data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                               moment_id, bereal_id, source_file_name_html, location))
                        # lava row
                        data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                          moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # pinned memories
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/memories-v(\d)+\/pinned-memories\/for-user\/')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    db_device_file_paths = [ device_file_path ]

                    # from file?
                    isDataOnFS = bool(record[2])
                    # from FS
                    if isDataOnFS:
                        fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                        json_data = get_json_file_content(fs_cached_data_path)
                        if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                    # from BLOB
                    else:
                        json_data = get_json_content(record[3])

                    # object?
                    obj_ref = json_data.get('pinnedMemories')
                    if not bool(obj_ref):
                        continue

                    # user id
                    user_id = str(record[1]).split('/')[-1]

                    # pinned
                    for i in range(0, len(obj_ref)):
                        device_file_paths = db_device_file_paths

                        pin = obj_ref[i]
                        if not pin:
                            continue

                        # taken at
                        taken_at = convert_iso8601_to_utc(pin.get('takenAt'))
                        # post type
                        post_type = format_post_type(pin.get('isLate'), pin.get('isMain'))
                        # author
                        author = format_userid(user_id)
                        # primary
                        p_mt, p_url, p_size = get_media(pin.get('primary'))
                        p_url_html = generic_url(p_url, html_format=True)
                        p_media_ref_id = media_item_from_url(seeker, p_url, artifact_info)
                        p_media_item = lava_get_full_media_info(p_media_ref_id)
                        if p_media_item: device_file_paths.append(get_device_file_path(p_media_item[5], seeker))
                        # secondary
                        s_mt, s_url, s_size = get_media(pin.get('secondary'))
                        s_url_html = generic_url(s_url, html_format=True)
                        s_media_ref_id = media_item_from_url(seeker, s_url, artifact_info)
                        s_media_item = lava_get_full_media_info(s_media_ref_id)
                        if s_media_item: device_file_paths.append(get_device_file_path(s_media_item[5], seeker))
                        # moment id
                        moment_id = pin.get('momentId')
                        # bereal id
                        bereal_id = pin.get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                        location.append(f"[pinnedMemories][{i}]")
                        location = COMMA_SEP.join(location)

                        # html row
                        data_list_html.append((taken_at, post_type, author, p_mt, p_url_html, p_media_ref_id, s_mt, s_url_html, s_media_ref_id,
                                               moment_id, bereal_id, source_file_name_html, location))
                        # lava row
                        data_list.append((taken_at, post_type, author, p_mt, p_url, p_media_ref_id, s_mt, s_url, s_media_ref_id,
                                          moment_id, bereal_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Pinned Memories: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# realmojis
@artifact_processor
def bereal_realmojis(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'BeReal ID',
        'Direction',
        'Owner',
        'Author',
        'Emoji',
        'RealMoji URL',
        ('RealMoji picture', 'media', 'height: 96px; border-radius: 50%;'),
        'Moment ID',
        'RealMoji ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info = inspect.stack()[0]
    artifact_info_name = __artifacts_v2__['bereal_realmojis']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # person (dictionary)
        # PersonRepository
        if file_rel_path.startswith('PersonRepository'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # series
                series = json_data.get('object', {}).get('beRealOfTheDay', {}).get('series')
                if not bool(series):
                    continue

                # owner
                owner_user_id, owner_user_name = get_user(series)
                owner = format_userid(owner_user_id, owner_user_name)

                # posts
                posts = series.get('posts')
                if not bool(posts):
                    continue

                # array
                for i in range(0, len(posts)):
                    post = posts[i]
                    if not bool(post):
                        continue

                    # bereal id
                    bereal_id = post.get('id')
                    # moment id
                    moment_id = post.get('momentID')

                    # realmojis
                    realmojis = post['realMojis']
                    if not bool(realmojis):
                        continue

                    for r in range(0, len(realmojis)):
                        device_file_paths = [ device_file_path ]

                        # realmoji
                        realmoji = realmojis[r]
                        if not bool(realmoji):
                            continue

                        # reation date
                        reaction_date = realmoji.get('date')
                        reaction_date = convert_cocoa_core_data_ts_to_utc(reaction_date)
                        # author: id, user name
                        author_id, author_user_name = get_user(realmoji)
                        # author
                        author = format_userid(author_id, author_user_name)
                        # direction
                        direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                        # emoji
                        emoji = realmoji.get('emoji')
                        uri_moji = generic_url(realmoji.get('uri'))
                        uri_moji_html = generic_url(realmoji.get('uri'), html_format=True)
                        # realmoji
                        r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                        r_media_item = lava_get_full_media_info(r_media_ref_id)
                        if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                        # realmoji id
                        realmoji_id = realmoji.get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = f"[object][beRealOfTheDay][series][posts][{i}][realMojis][{r}]"

                        # html row
                        data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                               moment_id, realmoji_id, source_file_name_html, location))
                        # lava row
                        data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                          moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # memories (array)
        # disk-bereal-MemoriesRepository-subject-key
        elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # memories
                memories = json_data.get('object')
                if not bool(memories):
                    continue

                # owner
                owner_user_id = bereal_user_id
                owner_user_name = bereal_user_map.get(owner_user_id)
                owner = format_userid(owner_user_id, owner_user_name)

                # array
                for i in range(0, len(memories)):
                    memory = memories[i]
                    if not bool(memory):
                        continue

                    # detailed posts
                    detailed_posts = memory.get('allDetailedPosts')
                    if not bool(detailed_posts):
                        continue
                    for j in range(0, len(detailed_posts)):
                        # detailed post
                        detailed_post = detailed_posts[j]
                        if not bool(detailed_post):
                            continue

                        # bereal id
                        bereal_id = detailed_post.get('id')
                        # moment id
                        moment_id = detailed_post.get('momentID')

                        # metadata
                        metadata = detailed_post.get('details', {}).get('full', {}).get('metadata')
                        if not bool(metadata):
                            continue

                        # realmojis
                        realmojis = metadata['realMojis']
                        if not bool(realmojis):
                            continue

                        for r in range(0, len(realmojis)):
                            device_file_paths = [ device_file_path ]

                            # realmoji
                            realmoji = realmojis[r]
                            if not bool(realmoji):
                                continue

                            # reaction date
                            reaction_date = realmoji.get('date')
                            reaction_date = convert_cocoa_core_data_ts_to_utc(reaction_date)
                            # author: id, user name
                            author_id, author_user_name = get_user(realmoji)
                            # author
                            author = format_userid(author_id, author_user_name)
                            # direction
                            direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                            # emoji
                            emoji = realmoji.get('emoji')
                            uri_moji = generic_url(realmoji.get('uri'))
                            uri_moji_html = generic_url(realmoji.get('uri'), html_format=True)
                            # realmoji
                            r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                            r_media_item = lava_get_full_media_info(r_media_ref_id)
                            if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                            # realmoji id
                            realmoji_id = realmoji.get('id')

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = f"[object][{i}][allDetailedPosts][{j}][details][full][metadata][realMojis][{r}]"

                            # html row
                            data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                                   moment_id, realmoji_id, source_file_name_html, location))                    
                            # lava row
                            data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                              moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-Production_postFeedItems
        elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # array (string, array)
                for i in range(0, len(obj_ref)):
                    # array
                    if not (bool(obj_ref[i]) and isinstance(obj_ref[i], list)):
                        continue

                    # moment
                    for m in range(0, len(obj_ref[i])):
                        moment = obj_ref[i][m]
                        if not bool(moment):
                            continue

                        posts = moment.get('posts')
                        if not bool(posts):
                            continue

                        for p in range(0, len(posts)):
                            post = posts[p]
                            if not bool(post):
                                continue

                            # bereal id
                            bereal_id = post.get('id')
                            # moment id
                            moment_id = post.get('momentID')
                            # owner
                            owner_user_id, owner_user_name = get_user(post)
                            owner = format_userid(owner_user_id, owner_user_name)

                            # realmojis
                            realmojis = post.get('realMojis')
                            if not bool(realmojis):
                                continue

                            for r in range(0, len(realmojis)):
                                device_file_paths = [ device_file_path ]

                                # realmoji
                                realmoji = realmojis[r]
                                if not bool(realmoji):
                                    continue

                                # reaction date
                                reaction_date = realmoji.get('date')
                                reaction_date = convert_cocoa_core_data_ts_to_utc(reaction_date)
                                # author: id, user name
                                author_id, author_user_name = get_user(realmoji)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # emoji
                                emoji = realmoji.get('emoji')
                                uri_moji = generic_url(realmoji.get('uri'))
                                uri_moji_html = generic_url(realmoji.get('uri'), html_format=True)   
                                # realmoji
                                r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                                r_media_item = lava_get_full_media_info(r_media_ref_id)
                                if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                                # realmoji id
                                realmoji_id = realmoji.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = f"[object][beRealOfTheDay][series][posts][{i}][realMojis][{r}]"

                                # html row
                                data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                                       moment_id, realmoji_id, source_file_name_html, location))
                                # lava row
                                data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                                  moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # person posts
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/person\/profiles\/[\w-]+\?')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # user posts
                        user_posts = json_data.get('beRealOfTheDay', {}).get('userPosts')
                        if not bool(user_posts):
                            continue

                        # owner
                        owner_id, owner_user_name = get_user(user_posts)
                        owner = format_userid(owner_id, owner_user_name)

                        # moment id
                        moment_id = user_posts.get('momentId')
                        if not bool(moment_id): moment_id = user_posts.get('moment', {}).get('id')

                        # posts
                        posts = user_posts.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            post = posts[i]
                            if not bool(post):
                                continue

                            # bereal id (thread)
                            bereal_id = post.get('id')

                            # realmojis
                            realmojis = post.get('realMojis')
                            if not bool(realmojis):
                                continue

                            for r in range(0, len(realmojis)):
                                device_file_paths = db_device_file_paths

                                # realmoji
                                realmoji = realmojis[r]
                                if not bool(realmoji):
                                    continue

                                # reaction date
                                reaction_date = convert_iso8601_to_utc(realmoji.get('postedAt'))
                                # author: id, user name
                                author_id, author_user_name = get_user(realmoji)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # emoji
                                emoji = realmoji.get('emoji')
                                uri_moji = generic_url(realmoji.get('media', {}).get('url'))
                                uri_moji_html = generic_url(realmoji.get('media', {}).get('url'), html_format=True)
                                # realmoji
                                r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                                r_media_item = lava_get_full_media_info(r_media_ref_id)
                                if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                                # realmoji id
                                realmoji_id = realmoji.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                                location.append(f"[beRealOfTheDay][userPosts][posts][{i}][realMojis][{r}]")
                                location = COMMA_SEP.join(location)

                                # html row
                                data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                                       moment_id, realmoji_id, source_file_name_html, location))
                                # lava row
                                data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                                  moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Persons: " + str(ex))
                pass

            try:
                # memories
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/memories-v(\d)+\/[\w-]+$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # posts
                        posts = json_data.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            post = posts[i]
                            if not bool(post):
                                continue

                            # owner
                            owner = format_userid(bereal_user_id)
                            # moment id
                            moment_id = str(record[1]).split('/')[-1]
                            # bereal id
                            bereal_id = post.get('id')

                            # realmojis
                            realmojis = post.get('realmojis')
                            if not bool(realmojis):
                                continue

                            for r in range(0, len(realmojis)):
                                device_file_paths = db_device_file_paths

                                # realmoji
                                realmoji = realmojis[r]
                                if not bool(realmoji):
                                    continue

                                # reaction date
                                reaction_date = convert_iso8601_to_utc(realmoji.get('postedAt'))
                                # author: id, user name
                                author_id, author_user_name = get_user(realmoji)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # emoji
                                emoji = realmoji.get('emoji')
                                uri_moji = generic_url(realmoji.get('media', {}).get('url'))
                                uri_moji_html = generic_url(realmoji.get('media', {}).get('url'), html_format=True)
                                # realmoji
                                r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                                r_media_item = lava_get_full_media_info(r_media_ref_id)
                                if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                                # realmoji id
                                realmoji_id = realmoji.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                                location.append(f"[posts][{i}][realmojis][{r}]")
                                location = COMMA_SEP.join(location)

                                # html row
                                data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                                       moment_id, realmoji_id, source_file_name_html, location))
                                # lava row
                                data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                                  moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Memories: " + str(ex))
                pass

            try:
                # feeds discovery
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/discovery$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # json
                        if not bool(json_data):
                            continue

                        # posts
                        posts = json_data.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            post = posts[i]
                            if not bool(post):
                                continue

                            # owner
                            owner_id, owner_user_name = get_user(post)
                            owner = format_userid(owner_id, owner_user_name)
                            # moment id
                            moment_id = None
                            # bereal id
                            bereal_id = post.get('id')

                            # realmojis
                            realmojis = post.get('realMojis')
                            if not bool(realmojis):
                                continue

                            for r in range(0, len(realmojis)):
                                device_file_paths = db_device_file_paths

                                # realmoji
                                realmoji = realmojis[r]
                                if not bool(realmoji):
                                    continue

                                # reaction date
                                reaction_date = convert_ts_int_to_utc(realmoji.get('date', {}).get('_seconds'))
                                # author: id, user name
                                author_id, author_user_name = get_user(realmoji)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # emoji
                                emoji = realmoji.get('emoji')
                                uri_moji = generic_url(realmoji.get('uri'))
                                uri_moji_html = generic_url(realmoji.get('uri'), html_format=True)
                                # realmoji
                                r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                                r_media_item = lava_get_full_media_info(r_media_ref_id)
                                if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                                # realmoji id
                                realmoji_id = realmoji.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                                location.append(f"[posts][{i}][realMojis][{r}]")
                                location = COMMA_SEP.join(location)

                                # html row
                                data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                                       moment_id, realmoji_id, source_file_name_html, location))
                                # lava row
                                data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                                  moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Feeds Discovery: " + str(ex))
                pass

        # EntitiesStore.sqlite
        elif file_rel_path.endswith('EntitiesStore.sqlite'):
            try:
                query = '''
                SELECT
                    R.Z_PK,
                    P.Z_PK,
                    U.Z_PK,
                    (R.ZDATE + 978307200),
                    P.ZID AS "bereal_id",
                    IIF(U.ZID = R.ZUSERID, "Outgoing", "Incoming"),
                    U.ZID AS "owner_id",
                    U.ZUSERNAME AS "owner_name",
                    R.ZUSERID AS "author_id",
                    R.ZUSERNAME AS "author_name",
                    R.ZEMOJI,
                    R.ZURL,
                    P.ZMOMENTID AS "moment_id",
                    R.ZID AS "realmoji_id"
                FROM ZPOSTMO_REALMOJIMO AS "R"
                LEFT JOIN ZPOSTMO AS "P" ON (R.ZPOST = P.Z_PK)
                LEFT JOIN ZUSERMO AS "U" ON (P.ZUSER = U.Z_PK)
                '''
                db_records = get_sqlite_db_records(file_found, query)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    device_file_paths = [ device_file_path ]

                    # reaction date
                    reaction_date = convert_ts_int_to_utc(record[3])
                    # bereal id
                    bereal_id = record[4]
                    # direction
                    direction = record[5]
                    # owner
                    owner = format_userid(record[6], record[7])
                    # author
                    author = format_userid(record[8], record[9])
                    # emoji
                    emoji = record[10]
                    uri_moji = generic_url(record[11])
                    uri_moji_html = generic_url(record[11], html_format=True)
                    # realmoji
                    r_media_ref_id = media_item_from_url(seeker, uri_moji, artifact_info)
                    r_media_item = lava_get_full_media_info(r_media_ref_id)
                    if r_media_item: device_file_paths.append(get_device_file_path(r_media_item[5], seeker))
                    # moment id
                    moment_id = record[12]
                    # realmoji id
                    realmoji_id = record[13]

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"ZPOSTMO_REALMOJIMO (Z_PK: {record[0]})" ]
                    if record[1] is not None: location.append(f"ZPOSTMO (Z_PK: {record[1]})")
                    if record[2] is not None: location.append(f"ZUSERMO (Z_PK: {record[2]})")
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, r_media_ref_id,
                                           moment_id, realmoji_id, source_file_name_html, location))
                    # lava row
                    data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, r_media_ref_id,
                                      moment_id, realmoji_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# comments
@artifact_processor
def bereal_comments(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'BeReal ID',
        'Direction',
        'Owner',
        'Author',
        'Text',
        'Moment ID',
        'Comment ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    artifact_info_name = __artifacts_v2__['bereal_comments']['name']

    # all files
    for file_found in files_found:
        file_rel_path = Path(Path(file_found).parent.name, Path(file_found).name).as_posix()
        device_file_path = get_device_file_path(file_found, seeker)

        # person (dictionary)
        # PersonRepository
        if file_rel_path.startswith('PersonRepository'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # series
                series = json_data.get('object', {}).get('beRealOfTheDay', {}).get('series')
                if not bool(series):
                    continue

                # owner: user id, user name
                owner_user_id, owner_user_name = get_user(series)
                # owner
                owner = format_userid(owner_user_id, owner_user_name)

                # posts
                posts = series.get('posts')
                if not bool(posts):
                    continue

                # array
                for i in range(0, len(posts)):
                    post = posts[i]
                    if not bool(post):
                        continue

                    # bereal id
                    bereal_id = post.get('id')
                    # moment id
                    moment_id = post.get('momentID')
                    # comments
                    comments = post['comment']
                    if not bool(comments):
                        continue
                                
                    for c in range(0, len(comments)):
                        device_file_paths = [ device_file_path ]

                        # comment
                        comment = comments[c]
                        if not bool(comment):
                            continue

                        # creation date
                        creation_date = comment.get('creationDate')
                        creation_date = convert_cocoa_core_data_ts_to_utc(creation_date)
                        # author: id, user name
                        author_id, author_user_name = get_user(comment)
                        # author
                        author = format_userid(author_id, author_user_name)
                        # direction
                        direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                        # text
                        text = comment.get('text')
                        # comment id
                        comment_id = comment.get('id')

                        # source file name
                        device_file_paths = dict.fromkeys(device_file_paths)
                        source_file_name = unordered_list(device_file_paths)
                        source_file_name_html = unordered_list(device_file_paths, html_format=True)
                        # location
                        location = f"[object][beRealOfTheDay][series][posts][{i}][comment][{c}]"

                        # html row
                        data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                        # lava row
                        data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # memories (array)
        # disk-bereal-MemoriesRepository-subject-key
        elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # memories
                memories = json_data.get('object')
                if not bool(memories):
                    continue

                # owner user id
                owner_user_id = bereal_user_id
                # owner user name
                owner_user_name = bereal_user_map.get(owner_user_id)
                # owner
                owner = format_userid(owner_user_id, owner_user_name)

                # array
                for i in range(0, len(memories)):
                    memory = memories[i]
                    if not bool(memory):
                        continue
                
                    # detailed posts
                    detailed_posts = memory.get('allDetailedPosts')
                    if not bool(detailed_posts):
                        continue

                    for j in range(0, len(detailed_posts)):
                        # detailed post
                        detailed_post = detailed_posts[j]
                        if not bool(detailed_post):
                            continue

                        # bereal id (thread)
                        bereal_id = detailed_post.get('id')
                        # moment id
                        moment_id = detailed_post.get('momentID')
                        # metadata
                        metadata = detailed_post.get('details', {}).get('full', {}).get('metadata')
                        if not bool(metadata):
                            continue

                        # comments
                        comments = metadata['comments']
                        if not bool(comments):
                            continue

                        for c in range(0, len(comments)):
                            device_file_paths = [ device_file_path ]

                            # comment
                            comment = comments[c]
                            if not bool(comment):
                                continue

                            # creation date
                            creation_date = comment.get('creationDate')
                            creation_date = convert_cocoa_core_data_ts_to_utc(creation_date)
                            # author: id, user name
                            author_id, author_user_name = get_user(comment)
                            # author
                            author = format_userid(author_id, author_user_name)
                            # direction
                            direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                            # text
                            text = comment.get('text')
                            # uid
                            comment_id = comment.get('id')

                            # source file name
                            device_file_paths = dict.fromkeys(device_file_paths)
                            source_file_name = unordered_list(device_file_paths)
                            source_file_name_html = unordered_list(device_file_paths, html_format=True)
                            # location
                            location = f"[object][{i}][allDetailedPosts][{j}][details][full][metadata][comments][{c}]"

                            # html row
                            data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                            # lava row
                            data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # disk-bereal-Production_postFeedItems
        elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
            try:
                # json
                json_data = get_json_file_content(file_found)
                if not bool(json_data):
                    continue

                # object?
                obj_ref = json_data.get('object')
                if not bool(obj_ref):
                    continue

                # array (string, array)
                for i in range(0, len(obj_ref)):
                    # array
                    if not (bool(obj_ref[i]) and isinstance(obj_ref[i], list)):
                        continue

                    # moment
                    for m in range(0, len(obj_ref[i])):
                        moment = obj_ref[i][m]
                        if not bool(moment):
                            continue

                        posts = moment.get('posts')
                        if not bool(posts):
                            continue

                        for p in range(0, len(posts)):
                            post = posts[p]
                            if not bool(post):
                                continue

                            # owner: user id, user name
                            owner_user_id, owner_user_name = get_user(post)
                            # owner
                            owner = format_userid(owner_user_id, owner_user_name)
                            # bereal id (thread)
                            bereal_id = post.get('id')
                            # moment id
                            moment_id = post.get('momentID')
                            # comments
                            comments = post.get('comment')
                            if not bool(comments):
                                continue
                            for c in range(0, len(comments)):
                                device_file_paths = [ device_file_path ]

                                # comment
                                comment = comments[c]
                                if not bool(comment):
                                    continue
                                # creation date
                                creation_date = comment.get('creationDate')
                                creation_date = convert_cocoa_core_data_ts_to_utc(creation_date)
                                # author: id, user name
                                author_id, author_user_name = get_user(comment)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # text
                                text = comment.get('text')
                                # uid
                                comment_id = comment.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = f"[object][{i}][{m}][posts][{p}][comment][{c}]"

                                # html row
                                data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                                # lava row
                                data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

        # Cache.db
        elif file_rel_path.endswith('Cache.db'):
            try:
                # person posts
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/person\/profiles\/[\w-]+\?')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # user posts
                        user_posts = json_data.get('beRealOfTheDay', {}).get('userPosts')
                        if not bool(user_posts):
                            continue

                        # owner
                        owner_user_id, owner_user_name = get_user(user_posts)
                        owner = format_userid(owner_user_id, owner_user_name)

                        # moment id
                        moment_id = user_posts.get('momentId')
                        if not bool(moment_id): moment_id = user_posts.get('moment', {}).get('id')

                        # posts
                        posts = user_posts.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            post = posts[i]
                            if not bool(post):
                                continue

                            # bereal id (thread)
                            bereal_id = post.get('id')

                            # comments
                            comments = post.get('comments')
                            if not bool(comments):
                                continue

                            for c in range(0, len(comments)):
                                device_file_paths = db_device_file_paths

                                # comment
                                comment = comments[c]
                                if not bool(comment):
                                    continue

                                # creation date
                                creation_date = convert_iso8601_to_utc(comment.get('postedAt'))
                                # author: id, user name
                                author_id, author_user_name = get_user(comment)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # text
                                text = comment.get('content')
                                # uid
                                comment_id = comment.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                                location.append(f"[beRealOfTheDay][userPosts][posts][{i}][comments][{c}]")
                                location = COMMA_SEP.join(location)

                                # html row
                                data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                                # lava row
                                data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Persons: " + str(ex))
                pass

            try:
                # memories
                query = BEREAL_CACHE_DB_QUERY.format(r'https:\/\/mobile[-\w]*\.bereal\.com\/api\/feeds\/memories-v(\d)+\/[\w-]+$')
                db_records = get_sqlite_db_records_regexpr(file_found, query, regexpr=True)
                if len(db_records) > 0:
                    for record in db_records:
                        db_device_file_paths = [ device_file_path ]

                        # from file?
                        isDataOnFS = bool(record[2])
                        # from FS
                        if isDataOnFS:
                            fs_cached_data_path = get_cache_db_fs_path(record[3], file_found, seeker)
                            json_data = get_json_file_content(fs_cached_data_path)
                            if bool(fs_cached_data_path): db_device_file_paths.append(get_device_file_path(fs_cached_data_path, seeker))
                        # from BLOB
                        else:
                            json_data = get_json_content(record[3])

                        # object?
                        if not bool(json_data):
                            continue

                        # posts
                        posts = json_data.get('posts')
                        if not bool(posts):
                            continue

                        # array
                        for i in range(0, len(posts)):
                            post = posts[i]
                            if not bool(post):
                                continue

                            # moment id
                            moment_id = str(record[1]).split('/')[-1]
                            # bereal id
                            bereal_id = post.get('id')
                            # owner
                            owner_user_id = bereal_user_id
                            owner = format_userid(owner_user_id)

                            # comments
                            comments = post.get('comments')
                            if not bool(comments):
                                continue

                            for c in range(0, len(comments)):
                                device_file_paths = db_device_file_paths

                                # comment
                                comment = comments[c]
                                if not bool(comment):
                                    continue

                                # creation date
                                creation_date = convert_iso8601_to_utc(comment.get('postedAt'))
                                # author: id, user name
                                author_id, author_user_name = get_user(comment)
                                # author
                                author = format_userid(author_id, author_user_name)
                                # direction
                                direction = 'Outgoing' if author_id == owner_user_id else 'Incoming'
                                # text
                                text = comment.get('content')
                                # uid
                                comment_id = comment.get('id')

                                # source file name
                                device_file_paths = dict.fromkeys(device_file_paths)
                                source_file_name = unordered_list(device_file_paths)
                                source_file_name_html = unordered_list(device_file_paths, html_format=True)
                                # location
                                location = [ f"cfurl_cache_receiver_data (entry_ID: {record[0]})" ]
                                location.append(f"[posts][{i}][comments][{c}]")
                                location = COMMA_SEP.join(location)

                                # html row
                                data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                                # lava row
                                data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))

            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - Cached.db Memories: " + str(ex))
                pass

        # EntitiesStore.sqlite
        elif file_rel_path.endswith('EntitiesStore.sqlite'):
            try:
                query = '''
                SELECT
                    C.Z_PK,
                    P.Z_PK,
                    U.Z_PK,
                    (C.ZCREATIONDATE + 978307200),
                    P.ZID AS "bereal_id",
                    IIF(U.ZID = C.ZUSERID, "Outgoing", "Incoming"),
                    U.ZID AS "owner_id",
                    U.ZUSERNAME AS "owner_name",
                    C.ZUSERID AS "author_id",
                    C.ZUSERNAME AS "author_name",
                    C.ZTEXT,
                    P.ZMOMENTID AS "moment_id",
                    C.ZID AS "comment_id"
                FROM ZPOSTMO_COMMENTMO AS "C"
                LEFT JOIN ZPOSTMO AS "P" ON (C.ZPOST = P.Z_PK)
                LEFT JOIN ZUSERMO AS "U" ON (P.ZUSER = U.Z_PK)
                '''
                db_records = get_sqlite_db_records(file_found, query)
                if len(db_records) == 0:
                    continue

                for record in db_records:
                    device_file_paths = [ device_file_path ]

                    # creation date
                    creation_date = convert_ts_int_to_utc(record[3])
                    # bereal id
                    bereal_id = record[4]
                    # direction
                    direction = record[5]
                    # owner
                    owner = format_userid(record[6], record[7])
                    # author
                    author = format_userid(record[8], record[9])
                    # text
                    text = record[10]
                    # moment id
                    moment_id = record[11]
                    # comment id
                    comment_id = record[12]

                    # source file name
                    device_file_paths = dict.fromkeys(device_file_paths)
                    source_file_name = unordered_list(device_file_paths)
                    source_file_name_html = unordered_list(device_file_paths, html_format=True)
                    # location
                    location = [ f"ZPOSTMO_COMMENTMO (Z_PK: {record[0]})" ]
                    if record[1] is not None: location.append(f"ZPOSTMO (Z_PK: {record[1]})")
                    if record[2] is not None: location.append(f"ZUSERMO (Z_PK: {record[2]})")
                    location = COMMA_SEP.join(location)

                    # html row
                    data_list_html.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name_html, location))
                    # lava row
                    data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, source_file_name, location))
            except Exception as ex:
                logfunc(f"Exception while parsing {artifact_info_name} - {file_found}: " + str(ex))
                pass

    return data_headers, (data_list, data_list_html), ' '


# messages
@artifact_processor
def bereal_messages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Sent', 'datetime'),
        'Owner',
        'Direction',
        'Sender',
        'Recipient',
        'Message',
        'Message type',
        'Source',
        'Media URL',
        ('Media image', 'media', 'height: 96px; border-radius: 5%;'),
        'Thread ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    artifact_info = inspect.stack()[0]
    device_file_paths = []
    file_found = get_file_path(files_found, "bereal-chat.sqlite")
    device_file_path = get_device_file_path(file_found, seeker)

    query = '''
    SELECT
        M.Z_PK,
        C.Z_PK,
        ME.Z_PK,
        (M.ZCREATEDAT + 978307200) AS "sent",
        C.ZOWNER,
        IIF(M.ZSENDER = C.ZOWNER, "Outgoing", "Incoming") AS "direction",
        M.ZSENDER AS "sender",
        M.ZBODY,
	    CASE M.ZBODYTYPE
	    	WHEN 1 THEN "Text"
            WHEN 3 THEN "RealMoji"
    		WHEN 9 THEN "Photo"
            WHEN 10 THEN "Deleted"
		    ELSE "N/D " || M.ZBODYTYPE
	    END AS "body_type",
        ME.ZSOURCE,
        ME.ZURL,
        M.ZCONVERSATIONID
    FROM ZMESSAGEMO AS "M"
    LEFT JOIN ZCONVERSATIONMO AS "C" ON (M.ZCONVERSATION = C.Z_PK)
    LEFT JOIN ZMEDIAMO AS "ME" ON (M.Z_PK = ME.ZMESSAGE)
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        device_file_paths = [ device_file_path ]

        # created
        created = convert_unix_ts_to_utc(record[3])
        # owner
        owner = record[4]
        # sender
        sender = record[6]
        # recipient
        if record[5] == 'Outgoing':
            recipient = bereal_user_id
        else:
            recipient = owner        
        # "id (fullame|userid)"
        owner = format_userid(owner)
        sender = format_userid(sender)
        recipient = format_userid(recipient)
        # body
        body = record[7].decode('utf-8') if bool(record[7]) else record[7]
        # media source
        if record[9] == 'remote':
            # media url
            media_url = generic_url(record[10])
            media_url_html = generic_url(record[10], html_format=True)
            # media
            media_ref_id = media_item_from_url(seeker, media_url, artifact_info)
            media_item = lava_get_full_media_info(media_ref_id)
            if media_item: device_file_paths.append(get_device_file_path(media_item[5], seeker))
        elif record[9] == 'local':
            # local path /Documents/<url>
            media_url = record[10]
            media_url_html = record[10]
            # media
            file_image = f"*/{bereal_app_identifier}/Documents/{record[10]}"
            media_ref_id = check_in_media(seeker, file_image, artifact_info)
            media_item = lava_get_full_media_info(media_ref_id)
            if media_item: device_file_paths.append(get_device_file_path(media_item[5], seeker))
        else:
            media_url = record[10]
            media_url_html = record[10]
            media_ref_id = None
            media_item = None

        # source file name
        device_file_paths = dict.fromkeys(device_file_paths)
        source_file_name = unordered_list(device_file_paths)
        source_file_name_html = unordered_list(device_file_paths, html_format=True)
        # location
        location = [ f"ZMESSAGEMO (Z_PK: {record[0]})" ]
        if record[1] is not None: location.append(f"ZCONVERSATIONMO (Z_PK: {record[1]})")
        if record[2] is not None: location.append(f"ZMEDIAMO (Z_PK: {record[2]})")
        location = COMMA_SEP.join(location)

        # html row
        data_list_html.append((created, owner, record[5], sender, recipient, body, record[8],
                               record[9], media_url_html, media_ref_id, record[11], source_file_name_html, location))
        # lava row
        data_list.append((created, owner, record[5], sender, recipient, body, record[8],
                          record[9], media_url, media_ref_id, record[11], source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '


# chat list
@artifact_processor
def bereal_chat_list(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = (
        ('Created', 'datetime'),
        'Owner',
        'Type',
        'Administrators',
        'Participants',
        'Last message',
        'Total messages',
        ('Last updated', 'datetime'),
        'Unread messages count',
        'ID',
        'Source file name',
        'Location'
    )
    data_list = []
    data_list_html = []
    device_file_paths = []
    file_found = get_file_path(files_found, "bereal-chat.sqlite")
    device_file_path = get_device_file_path(file_found, seeker)

    query = '''
    SELECT
        C.Z_PK,
        S.Z_PK,
        M.Z_PK,
        (C.ZCREATEDAT + 978307200) AS "created",
        C.ZOWNER,
        CASE C.ZTYPE WHEN 1 THEN "private" ELSE "group" END AS "chat_type",
        C.ZADMINS,
        C.ZPARTICIPANTS,
        M.ZBODY,
        C.ZCURRENTSEQNUM AS "total_messages",
        C.ZLASTUPDATETIME,
        S.ZUNREADMESSAGECOUNT,
        C.ZID AS "id"
    FROM ZCONVERSATIONMO AS "C"
    LEFT JOIN ZCONVERSATIONSTATUSMO AS "S" ON (C.ZSTATUS = S.Z_PK)
    LEFT JOIN ZMESSAGEMO AS "M" ON (C.ZLASTMESSAGE = M.Z_PK)
    '''

    db_records = get_sqlite_db_records(file_found, query)
    for record in db_records:
        device_file_paths = [ device_file_path ]

        # created
        created = convert_unix_ts_to_utc(record[3])
        # owner
        owner = format_userid(record[4])
        # last updated
        last_updated = convert_unix_ts_to_utc(record[10])
        # admins (plist)
        admins = get_plist_content(record[6])
        admins_list = []
        for a in admins:
            admins_list.append(format_userid(a))
        if bool(admins_list):
            admins = LINE_BREAK.join(admins_list)
        admins_html = admins.replace(LINE_BREAK, HTML_LINE_BREAK)
        # participants (plist)
        participants = get_plist_content(record[7])
        participants_list = []
        for p in participants:
            participants_list.append(format_userid(p))
        if bool(participants_list):
            participants = LINE_BREAK.join(participants_list)
        participants_html = participants.replace(LINE_BREAK, HTML_LINE_BREAK)
        # body
        body = record[8].decode('utf-8') if bool(record[8]) else record[8]

        # source file name
        device_file_paths = dict.fromkeys(device_file_paths)
        source_file_name = unordered_list(device_file_paths)
        source_file_name_html = unordered_list(device_file_paths, html_format=True)
        # location
        location = [ f"ZCONVERSATIONMO (Z_PK: {record[0]})" ]
        if record[1] is not None: location.append(f"ZCONVERSATIONSTATUSMO (Z_PK: {record[1]})")
        if record[2] is not None: location.append(f"ZMESSAGEMO (Z_PK: {record[2]})")
        location = COMMA_SEP.join(location)

        # html row
        data_list_html.append((created, owner, record[5], admins_html, participants_html, body, record[9], last_updated,
                               record[11], record[12], source_file_name_html, location))
        # lava row
        data_list.append((created, owner, record[5], admins, participants, body, record[9], last_updated,
                          record[11], record[12], source_file_name, location))

    return data_headers, (data_list, data_list_html), ' '
