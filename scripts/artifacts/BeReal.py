__artifacts_v2__ = {
    "bereal_preferences": {
        "name": "BeReal Preferences",
        "description": "Parses and extract BeReal Preferences",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-09",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.BeReal.plist'),
        "output_types": [ "none" ],
        "artifact_icon": "settings"
    },
    "bereal_accounts": {
        "name": "BeReal Accounts",
        "description": "Parses and extract BeReal Accounts",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-ProfileRepository/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL", "Timezone", "Device UID", "Device Model and OS", "App version", "RealMojis" ],
        "artifact_icon": "user"
    },
    "bereal_contacts": {
        "name": "BeReal Contacts",
        "description": "Parses and extract BeReal Contacts",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsContactsManager-contact/*'),
        "output_types": [ "lava", "html", "tsv" ],
        "html_columns": [ "Profile picture"],
        "artifact_icon": "users",
        "media_style": ("height: 80px; border-radius: 50%;", "height: 80px;")
    },
    "bereal_persons": {
        "name": "BeReal Persons",
        "description": "Parses and extract BeReal Persons",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL", "Urls" ],
        "artifact_icon": "users"
    },
    "bereal_friends": {
        "name": "BeReal Friends",
        "description": "Parses and extract BeReal Friends, Friend Requests Sent, Friend Requests Received, and Friends Following",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsFriendsListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsRequestSentListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-RelationshipsRequestReceivedListManager/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-Production_FriendsStorage.following/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-Production_FriendsStorage.followers/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL" ],
        "artifact_icon": "user-plus"
    },
    "bereal_blocked_users": {
        "name": "BeReal Blocked Users",
        "description": "Parses and extract BeReal Blocked Users",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-BlockedUserManager/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Profile picture URL" ],
        "artifact_icon": "slash"
    },
    "bereal_posts": {
        "name": "BeReal Posts",
        "description": "Parses and extract BeReal Memories, Person BeReal of the day and Production Feeds",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Primary URL", "Secondary URL", "Thumbnail URL", "Tagged friends", "Source file name", "Location" ],
        "artifact_icon": "calendar"
    },
    "bereal_pinned_memories": {
        "name": "BeReal Pinned Memories",
        "description": "Parses and extract BeReal Pinned Memories",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-pinnedMemories-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-PersonRepository-pinnedMemories-key/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Primary URL", "Secondary URL", "Thumbnail URL", "Source file name", "Location" ],
        "artifact_icon": "bookmark"
    },
    "bereal_realmojis": {
        "name": "BeReal RealMojis",
        "description": "Parses and extract BeReal RealMojis from my memories and Person's memories",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "RealMoji" ],
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
        "name": "BeReal Comments",
        "description": "Parses and extract BeReal Comments from my memories, Person's posts, and Production post Feeds",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/disk-bereal-MemoriesRepository-subject-key/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/PersonRepository/*',
                  '*/mobile/Containers/Shared/AppGroup/*/disk-bereal-Production_postFeedItems/*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "RealMojis" ],
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
        "name": "BeReal Messages",
        "description": "Parses and extract BeReal Messages",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/bereal-chat.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Media URL" ],
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
        "name": "BeReal Chat List",
        "description": "Parses and extract BeReal Chat List",
        "author": "@djangofaiola",
        "version": "0.1",
        "creation_date": "2024-12-20",
        "last_update_date": "2024-03-08",
        "requirements": "none",
        "category": "BeReal",
        "notes": "https://djangofaiola.blogspot.com",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/bereal-chat.sqlite*'),
        "output_types": [ "lava", "html", "tsv", "timeline" ],
        "html_columns": [ "Administrators", "Participants" ],
        "artifact_icon": "message-circle"
    }
}

from pathlib import Path
import inspect
import json
from datetime import timedelta
from base64 import standard_b64decode
from urllib.parse import urlparse, urlunparse
from scripts.ilapfuncs import get_file_path, get_sqlite_db_records, get_plist_content, get_plist_file_content, convert_unix_ts_to_utc, \
    convert_cocoa_core_data_ts_to_utc, check_in_embedded_media, artifact_processor, logfunc, is_platform_windows

# <id, fullname|username>
map_id_name = {}
# bereal user id
bereal_user_id = None


def format_userid(id, name=None):
    if id:
        # "id (name)"
        if name:
            return f"{id} ({name})"
        # "id (m_name)"
        else:
            m_name = map_id_name.get(id)
            return f"{id} ({m_name})" if bool(m_name) else id
    else:
        return "Local User"


def get_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logfunc(f"Error reading file {file_path}: {str(e)}")
        return None


# get key0
def get_key0(obj):
    return list(obj.keys())[0] if bool(obj) and isinstance(obj, dict) else None


# profile picture or thumbnail or media or primary or secondary
def get_media(obj : dict):
    if bool(obj) and isinstance(obj, dict):
        # url
        pp_url = obj.get('url')
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
        pp_url = None
        pp_size = None
        pp_mt = None

    # media type, url and size string
    return pp_mt, pp_url, pp_size


# profile type (regular, brand, celebrity, ...)
def get_profile_type(obj):
    profile_type = None

    # profile type 1.x
    is_real_people = obj.get('isRealPeople')
    if is_real_people is not None:
        profile_type = 'regular' if (is_real_people == False) else 'real_people'
    # profile type 2.x, 4.x
    else:
        profile_type = get_key0(obj.get('profileType'))

    return profile_type


# post type (onTime, late, ...)
def get_post_type(obj, is_late=False):
    post_type = obj.get('postType', '')
    if post_type.lower() == 'bonus':
        post_type = f"late {post_type}" if is_late else f"onTime {post_type}"

    return post_type


# post visibilities
def get_post_visibilities(obj):
    visibilities = obj.get('visibilities')
    if visibilities is not None:
        return ', '.join(obj)
    else:
        return None


# generic url
def generic_url(value, html_format=False):
    if value != None and len(value) > 0:
        u = urlparse(value)
        # 0=scheme, 2=path
        if not bool(u[0]) and u[2].startswith('www'):
            u = u._replace(scheme='http')
        url = urlunparse(u)
        return value if not html_format else f'<a href="{url}" target="_blank">{value}</>'
    else:
        return None


# links
def get_links(obj, html_format=False):
    if obj:
        links_urls = []
        # array
        for i in range(0, len(obj)):
           url = generic_url(obj[i].get('url'), html_format)
           links_urls.append(url)
        if html_format:
            return '<br />'.join(links_urls)
        else:
            return '\n'.join(links_urls)
    else:
        return None


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
            url_moji = generic_url(real_moji.get('media', {}).get('url'), html_format)
            all_mojis.append(f"{real_moji.get('emoji')} {url_moji}")
        if html_format:
            return '<br />'.join(all_mojis)
        else:
            return '\n'.join(all_mojis)
    # realMojis
    elif bool(real_mojis := obj.get('realMojis')):
        # array
        for i in range(0, len(real_mojis)):
            # real moji
            real_moji = real_mojis[i]
            # moji identifier
            #id = real_moji.get('id')
            # uid 
            #uid = real_moji.get('uid')
            # user name
            #user_name = real_moji.get('userName')
            # date
            #reaction_date = convert_cocoa_core_data_ts_to_utc(real_moji.get('date'))
            # emoji->uri
            uri_moji = generic_url(real_moji.get('uri'), html_format)
            all_mojis.append(f"{real_moji.get('emoji')} {uri_moji}")

        return '<br />'.join(all_mojis) if html_format else '\n'.join(all_mojis)
    # none
    else:
        return None


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
def get_tags(obj, html_format=False): 
    tag_list = []

    tags = obj.get('tags')
    if not bool(tags):
        tags = obj.get('tagsV2')

    # array
    if bool(tags) and isinstance(tags, list):
        for i in range(0, len(tags)):
            tag = tags[i]

            # V1?
            if bool(tag.get('tagName')):
                # userid (fullname)
                user = format_userid(tag.get('userId'))
            # V2
            else:
                id = tag.get('id')
                fullname = tag.get('fullname')
                # userid (fullname)
                if bool(fullname):
                    user = f"{id} ({fullname})"
                # userid (fullname|username)
                else:
                    username = tag.get('username')
                    user = f"{id} ({username})"

            if bool(user):
                tag_list.append(user)
                

    return '<br />'.join(tag_list) if html_format else '\n'.join(tag_list)


# preferences
@artifact_processor
def bereal_preferences(files_found, report_folder, seeker, wrap_text, timezone_offset):

    source_path = None
    global bereal_user_id

    # all files
    for file_found in files_found:
        # prefs
        plist_data = get_plist_file_content(file_found)
        if not bool(plist_data):
            continue

        try:
            # source path
            source_path = file_found

            # group
            if str(file_found).endswith('group.BeReal.plist'):
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
                    map_id_name[user_id] = user_name
                    # bereal user id
                    bereal_user_id = user_id
                    # local profile picture (file:///private/var/mobile/Containers/Shared/AppGroup/<APP_GUID>/notification/file.jpg)
                    bereal_profile_picture = plist_data.get('myAccount', {}).get(user_id, {}).get('profilePictureURL')

                # current friends <id, fullname>
                current_friends = plist_data.get('currentFriends', {})
                for user_id, user_name in current_friends.items():
                    map_id_name[user_id] = user_name
            
            # app
            else:
                continue

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # return empty
    return (), [], source_path


# accounts
@artifact_processor
def bereal_accounts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Profile type', 'Full name', 'User name', 'Profile picture URL', 'Gender', 'Birthday', 'Biography', 
                     'Country code', 'Region', 'Address', 'Timezone', 'Phone number', 'Device UID', 'Device Model and OS', 'App version', 
                     'Private', 'RealMojis', 'User ID', 'Source file name' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        # accounts
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

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
            pp_url_html = generic_url(pp_url, html_format = True)
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
            dev_uid = []
            dev_info = []
            app_ver = []
            timezone = []
            dev_uid_html = []
            dev_info_html = []
            app_ver_html = []
            timezone_html = []
            devices = account.get('devices')
            if bool(devices):
                # array
                for i in range(0, len(devices)):
                    # device
                    device = devices[i]
                    # device uid
                    dev_uid.append(device.get('deviceId'))
                    dev_uid_html = dev_uid
                    # device info (model, ios ver)
                    dev_info.append(device.get('device'))
                    dev_info_html = dev_info
                    # app version
                    app_ver.append(device.get('clientVersion'))
                    app_ver_html = app_ver
                    # timezone
                    timezone.append(device.get('timezone'))
                    timezone_html = timezone
            dev_uid = '\n'.join(dev_uid)
            dev_info = '\n'.join(dev_info)
            app_ver = '\n'.join(app_ver)
            timezone = '\n'.join(timezone)
            dev_uid_html = '<br />'.join(dev_uid_html)
            dev_info_html = '<br />'.join(dev_info_html)
            app_ver_html = '<br />'.join(app_ver_html)
            timezone_html = '<br />'.join(timezone_html)
            # is private?
            is_private = account.get('isPrivate')
            # realmojis
            realmojis = get_realmojis(account, html_format = False)
            realmojis_html = get_realmojis(account, html_format = True)
            # unique id/user id
            id = account.get('id')

            # html row
            data_list_html.append((created, profile_type, fullname, username, pp_url_html, gender, birth_date, biography, 
                                   country_code, region, address, timezone_html, phone_number, dev_uid_html, dev_info_html, app_ver_html, 
                                   is_private, realmojis_html, id, file_rel_path))

            # lava row
            data_list.append((created, profile_type, fullname, username, pp_url, gender, birth_date, biography, 
                              country_code, region, address, timezone, phone_number, dev_uid, dev_info, app_ver, 
                              is_private, realmojis, id, file_rel_path))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[6] = (data_headers[6], 'date')
    data_headers[12] = (data_headers[12], 'phonenumber')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# contacts
@artifact_processor
def bereal_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Full name', 'Family name', 'Middle name', 'Given name', 'Nick name', 'Profile picture', 'Organization name',
                     'Phone numbers', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()
    artifact_info = inspect.stack()[0]

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # contacts
            contacts = json_data.get('object')
            if not bool(contacts):
                continue

            # array
            for i in range(0, len(contacts)):
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
                    photo_item = check_in_embedded_media(seeker, file_found, photo_raw, artifact_info)
                    photo = photo_item.id
                else:
                    photo = ''
                # organization name
                organization_name = contact.get('organizationName')
                # phone numbers
                phone_numbers = '\n'.join(contact.get('phoneNumbers'))
                phone_numbers_html = '<br />'.join(contact.get('phoneNumbers'))

                # location
                location = f"[object][{i}]"

                # html row
                data_list_html.append((full_name, family_name, middle_name, given_name, nick_name, photo, organization_name,
                                       phone_numbers_html, file_rel_path, location))

                # lava row
                data_list.append((full_name, family_name, middle_name, given_name, nick_name, photo, organization_name,
                                  phone_numbers, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[5] = (data_headers[5], 'media')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# persons
@artifact_processor
def bereal_persons(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Profile type', 'Full name', 'User name', 'Profile picture URL', 'Biography', 'Address',
                     'Relationship', 'Friended at', 'Urls', 'Streak count', 'Unique ID', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)
            
            # person
            person = json_data.get('object')
            if not bool(person):
                continue

            # created (utc)
            created = person.get('createdAt')
            created = convert_cocoa_core_data_ts_to_utc(created)
            # profile type
            profile_type = get_profile_type(person)
            # fullname
            fullname = person.get('fullname')
            # username
            username = person.get('username')
            # profile picture url
            pp_url = person.get('profilePictureURL')
            pp_url_html = generic_url(pp_url, html_format = True)
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
            links = get_links(person.get('links'), html_format = False)
            links_html = get_links(person.get('links'), html_format = True)
            # streak count
            streak_count = person.get('streakCount')
            # unique id
            id = person.get('id')

            # location
            location = f"[object]"

            # html row
            data_list_html.append((created, profile_type, fullname, username, pp_url_html, biography, address,
                                   relationship_type, relationship_friended_at, links_html, streak_count, id, file_rel_path, location))

            # lava row
            data_list.append((created, profile_type, fullname, username, pp_url, biography, address,
                              relationship_type, relationship_friended_at, links, streak_count, id, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass
            
    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[8] = (data_headers[8], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# friends
@artifact_processor
def bereal_friends(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Status updated at', 'Status', 'Profile type', 'Full name', 'Username', 'Profile picture URL', 'Mutual friends', 'Unique ID', 
                     'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)
            
            # object?
            obj_ref = json_data.get('object')
            if not bool(obj_ref):
                continue

            # following (dictionary)
            # disk-bereal-Production_FriendsStorage.following/<GUID>.following
            # disk-bereal-Production_FriendsStorage.followers/<GUID>.followers
            if file_rel_path.endswith('.following') or file_rel_path.endswith('.followers'):
                # relationship
                relationship = obj_ref.get('relationship', '')
                # users
                obj_ref = obj_ref.get('users')
                if not bool(obj_ref):
                    continue

                # array
                for i in range(0, len(obj_ref)):
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
                    pp_url_html = generic_url(pp_url, html_format = True)
                    # unique id
                    id = user.get('id')

                    # location
                    location = f"[object][users][{i}]"

                    # html row
                    data_list_html.append((None, status, profile_type, fullname, username, pp_url_html, None, id,
                                           file_rel_path, location))
                    # lava row
                    data_list.append((None, status, profile_type, fullname, username, pp_url, None, id,
                                      file_rel_path, location))

            # friends (array)
            # disk-bereal-RelationshipsFriendsListManager/*
            # disk-bereal-RelationshipsRequestSentListManager/*
            # disk-bereal-RelationshipsRequestReceivedListManager/*
            elif file_rel_path.startswith('disk-bereal-RelationshipsFriendsListManager') or \
                 file_rel_path.startswith('disk-bereal-RelationshipsRequestSentListManager') or \
                 file_rel_path.startswith('disk-bereal-RelationshipsRequestReceivedListManager'):
                # array
                for i in range(0, len(obj_ref)):
                    friend = obj_ref[i]
                    if not friend:
                        continue

                    # status updated at
                    status_updated_at = convert_cocoa_core_data_ts_to_utc(friend.get('statusUpdatedAt'))
                    # status
                    status = friend.get('status', '').lower()
                    if status == 'accepted': status = 'Friend'
                    elif status == 'sent': status = 'Request Sent'
                    elif status == 'pending': status = 'Request Received'
                    elif status == 'canceled': status = 'Request Canceled'
                    elif status == 'rejected': status = 'Request Rejected'
                    # profile type
                    profile_type = get_profile_type(friend)
                    # fullname
                    fullname = friend.get('fullname')
                    # username
                    username = friend.get('username')
                    # profile picture url
                    pp_url = friend.get('profilePictureURL')
                    pp_url_html = generic_url(pp_url, html_format = True)
                    # mutual friends
                    mutual_friends = friend.get('mutualFriends')
                    # unique id
                    id = friend.get('id')

                    # location
                    location = f"[object][{i}]"

                    # html row
                    data_list_html.append((status_updated_at, status, profile_type, fullname, username, pp_url_html, mutual_friends, id,
                                           file_rel_path, location))
                    # lava row
                    data_list.append((status_updated_at, status, profile_type, fullname, username, pp_url, mutual_friends, id,
                                      file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# blocked users
@artifact_processor
def bereal_blocked_users(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Blocked', 'Full name', 'Username', 'Profile picture URL', 'Unique ID', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # friends
            friends = json_data.get('object')
            if not bool(friends):
                continue

            # array
            for i in range(0, len(friends)):
                friend = friends[i]
                if not bool(friend):
                    continue

                # blocked date
                blocked_date = convert_cocoa_core_data_ts_to_utc(friend.get('blockedDate'))
                # fullname
                fullname = friend.get('fullname')
                # username
                username = friend.get('username')
                # profile picture url
                pp_url = friend.get('profilePictureURL')
                pp_url_html = generic_url(pp_url, html_format = True)
                # unique id
                id = friend.get('id')

                # location
                location = f"[object][{i}]"

                # html row
                data_list_html.append((blocked_date, fullname, username, pp_url_html, id, file_rel_path, location))

                # lava row
                data_list.append((blocked_date, fullname, username, pp_url, id, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# posts
@artifact_processor
def bereal_posts(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Taken at', 'Moment day', 'Post type', 'Author', 'Primary media type', 'Primary URL', 'Secondary media type', 'Secondary URL',
                     'Thumbnail media type', 'Thumbnail URL', 'Caption', 'Latitude', 'Longitude', 'Retake counter', 'Late time', 'Tagged friends',
                     'Moment ID', 'BeReal ID', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # object?
            obj_ref = json_data.get('object')
            if not bool(obj_ref):
                continue

            # PersonRepository
            if file_rel_path.startswith('PersonRepository'):
                # posts
                posts = json_data.get('object', {}).get('beRealOfTheDay', {}).get('series', {}).get('posts')
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
                    # moment at
                    moment_at = None
                    # is late?
                    is_late = post.get('isLate')
                    # late in seconds
                    late_secs = post.get('lateInSeconds')
                    if bool(late_secs): late_secs = str(timedelta(seconds=late_secs))
                    # is main?
                    is_main = post.get('isMain')                  
                    # post type
                    post_type = 'late' if is_late else 'onTime'
                    if not is_main: post_type = f"{post_type} bonus"
                    # caption
                    caption = post.get('caption')
                    # latitude
                    latitude = post.get('location', {}).get('latitude')
                    # longitude
                    longitude = post.get('location', {}).get('longitude')
                    # author
                    author_id, author_user_name = get_user(post)
                    author = format_userid(author_id, author_user_name)
                    # post visibilities
                    post_visibilities = get_post_visibilities(post)
                    # taken at
                    taken_at = convert_cocoa_core_data_ts_to_utc(post.get('takenAt'))
                    # retake counter
                    retake_counter = post.get('retakeCounter')
                    # primary
                    p_mt, p_url, p_size = get_media(post.get('primaryMedia'))
                    p_url_html = generic_url(p_url, html_format = True)
                    # secondary
                    s_mt, s_url, s_size = get_media(post.get('secondaryMedia'))
                    s_url_html = generic_url(s_url, html_format = True)
                    # tags
                    tags = get_tags(post, html_format = False)
                    tags_html = get_tags(post, html_format = True)

                    # location
                    location = f"[object][beRealOfTheDay][series][posts][{i}]"

                    # html row
                    data_list_html.append((taken_at, moment_at, post_type, author, p_mt, p_url_html, s_mt, s_url_html,
                                           None, None, caption, latitude, longitude, retake_counter, late_secs, tags_html,
                                           moment_id, bereal_id, file_rel_path, location))
                    # lava row
                    data_list.append((taken_at, moment_at, post_type, author, p_mt, p_url, s_mt, s_url,
                                      None, None, caption, latitude, longitude, retake_counter, late_secs, tags,
                                      moment_id, bereal_id, file_rel_path, location))
            
            # disk-bereal-MemoriesRepository-subject-key
            elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
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
                        # detailed post
                        detailed_post = detailed_posts[j]
                        if not bool(detailed_post):
                            continue

                        # bereal id
                        bereal_id = detailed_post.get('id')
                        # moment id
                        moment_id = detailed_post.get('momentID')
                        # moment at
                        moment_at = convert_cocoa_core_data_ts_to_utc(detailed_post.get('momentAt'))
                        # post type
                        post_type = get_post_type(detailed_post, is_late)
#                        # late in seconds???
                        late_secs = detailed_post.get('lateInSeconds')
                        if bool(late_secs): late_secs = str(timedelta(seconds=late_secs))
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
                        tags = get_tags(metadata, html_format = False)
                        tags_html = get_tags(metadata, html_format = True)
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
#                        # late in seconds???
                        if not bool(late_secs):
                            late_secs = data.get('lateInSeconds')
                            if bool(late_secs): str(timedelta(seconds=late_secs))
                        # primary
                        p_mt, p_url, p_size = get_media(data.get('primary'))
                        p_url_html = generic_url(p_url, html_format = True)
                        # secondary
                        s_mt, s_url, s_size = get_media(data.get('secondary'))
                        s_url_html = generic_url(s_url, html_format = True)
                        # thumbnail
                        t_mt, t_url, t_size = get_media(data.get('thumbnail'))
                        t_url_html = generic_url(t_url, html_format = True)

                        # location
                        location = f"[object][{i}]"

                        # html row
                        data_list_html.append((taken_at, moment_at, post_type, author, p_mt, p_url_html, s_mt, s_url_html,
                                               t_mt, t_url_html, caption, latitude, longitude, retake_counter, late_secs, tags_html,
                                               moment_id, bereal_id, file_rel_path, location))
                        # lava row
                        data_list.append((taken_at, moment_at, post_type, author, p_mt, p_url, s_mt, s_url,
                                          t_mt, t_url, caption, latitude, longitude, retake_counter, late_secs, tags,
                                          moment_id, bereal_id, file_rel_path, location))
   
            # disk-bereal-Production_postFeedItems
            elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
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
                            post = posts[p]
                            if not bool(post):
                                continue

                            # bereal id
                            bereal_id = post.get('id')
                            # moment id
                            moment_id = post.get('momentID')
                            # moment at
                            moment_at = None
                            # is late?
                            is_late = post.get('isLate')
                            # late in seconds
                            late_secs = post.get('lateInSeconds')
                            if bool(late_secs): late_secs = str(timedelta(seconds=late_secs))
                            # is main?
                            is_main = post.get('isMain')                  
                            # post type
                            post_type = 'late' if is_late else 'onTime'
                            if not is_main: post_type = f"{post_type} bonus"
                            # caption
                            caption = post.get('caption')
                            # latitude
                            latitude = post.get('location', {}).get('latitude')
                            # longitude
                            longitude = post.get('location', {}).get('longitude')
                            # tags
                            tags = get_tags(post, html_format = False)
                            tags_html = get_tags(post, html_format = True)
                            # post visibilities
                            post_visibilities = get_post_visibilities(post)
                            # taken at
                            taken_at = convert_cocoa_core_data_ts_to_utc(post.get('takenAt'))
                            # retake counter
                            retake_counter = post.get('retakeCounter')
                            # primary
                            p_mt, p_url, p_size = get_media(post.get('primaryMedia'))
                            p_url_html = generic_url(p_url, html_format = True)
                            # secondary
                            s_mt, s_url, s_size = get_media(post.get('secondaryMedia'))
                            s_url_html = generic_url(s_url, html_format = True)

                            # location
                            location = f"[object][{i}][{m}][posts][{p}]"

                            # html row
                            data_list_html.append((taken_at, moment_at, post_type, author, p_mt, p_url_html, s_mt, s_url_html,
                                                   t_mt, t_url_html, caption, latitude, longitude, retake_counter, late_secs, tags_html,
                                                   moment_id, bereal_id, file_rel_path, location))
                            # lava row
                            data_list.append((taken_at, moment_at, post_type, author, p_mt, p_url, s_mt, s_url,
                                              t_mt, t_url, caption, latitude, longitude, retake_counter, late_secs, tags,
                                              moment_id, bereal_id, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[1] = (data_headers[1], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# pinned memories
@artifact_processor
def bereal_pinned_memories(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Pinned at', 'Moment day', 'Post type', 'Author ID', 'Primary media type', 'Primary URL', 'Secondary media type', 'Secondary URL',
                     'Moment ID', 'Pin ID', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    def append_data(obj, index, from_person):
        if not bool(obj):
            return

        # taken at
        taken_at = convert_cocoa_core_data_ts_to_utc(obj.get('takenAt'))
        # moment day
        moment_day = convert_cocoa_core_data_ts_to_utc(obj.get('momentDay'))
        # post type
        post_type = obj.get('analyticsPostType')
        # author id
        author_id = obj.get('analyticsAuthorID')
        # primary
        p_mt, p_url, p_size = get_media(obj.get('primary'))
        p_url_html = generic_url(p_url, html_format = True)
        # secondary
        s_mt, s_url, s_size = get_media(obj.get('secondary'))
        s_url_html = generic_url(s_url, html_format = True)
        # moment id
        moment_id = obj.get('analyticsMomentID')
        # unique id
        pin_id = obj.get('id')


        # location
        location = f"[object][{author_id}][{index}]" if from_person else f"[object][{index}]"

        # html row
        data_list_html.append((taken_at, moment_day, post_type, author_id, p_mt, p_url_html, s_mt, s_url_html,
                               moment_id, pin_id, file_rel_path, location))
        # lava row
        data_list.append((taken_at, moment_day, post_type, author_id, p_mt, p_url, s_mt, s_url,
                          moment_id, pin_id, file_rel_path, location))
        
        return


    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # object?
            obj_ref = json_data.get('object')
            if not bool(obj_ref):
                continue

            # memories repository
            # disk-bereal-MemoriesRepository-pinnedMemories-key
            if file_rel_path.startswith('disk-bereal-MemoriesRepository-pinnedMemories-key'):
                # pinned
                for i in range(0, len(obj_ref)):
                    append_data(obj_ref[i], i, from_person = False)

            # person memories
            # disk-bereal-PersonRepository-pinnedMemories-key
            elif file_rel_path.startswith('disk-bereal-PersonRepository-pinnedMemories-key'):
                # users
                for key, val in obj_ref.items():
                    # uids
                    if not bool(val) or not isinstance(val, list):
                        continue
                        
                    # pinned
                    for i in range(0, len(val)):
                        append_data(val[i], i, from_person = True)

            # none
            else:
                continue
   
        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[1] = (data_headers[1], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# realmojis
@artifact_processor
def bereal_realmojis(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'BeReal ID', 'Direction', 'Owner', 'Author', 'Emoji', 'RealMoji', 'Moment ID', 'RealMoji ID', 'Source file name', 'Location' ]
    data_list = []
    data_list_html = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # object?
            obj_ref = json_data.get('object')
            if not bool(obj_ref):
                continue

            # person (dictionary)
            # PersonRepository
            if file_rel_path.startswith('PersonRepository'):
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

                    # realmojis
                    realmojis = post['realMojis']
                    if not bool(realmojis):
                        continue

                    for r in range(0, len(realmojis)):
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
                        uri_moji = generic_url(realmoji.get('uri'), False)
                        uri_moji_html = generic_url(realmoji.get('uri'), True)                 
                        # realmoji id
                        realmoji_id = realmoji.get('id')

                        # location
                        location = f"[object][beRealOfTheDay][series][posts][{i}][realMojis][{r}]"

                        # html row
                        data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, moment_id, realmoji_id, file_rel_path, location))

                        # lava row
                        data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, moment_id, realmoji_id, file_rel_path, location))
                
            # memories (array)
            # disk-bereal-MemoriesRepository-subject-key
            elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
                # memories
                memories = json_data.get('object')
                if not bool(memories):
                    continue

                # owner user id
                owner_user_id = bereal_user_id
                # owner user name
                owner_user_name = map_id_name.get(owner_user_id)
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
                            uri_moji = generic_url(realmoji.get('uri'), False)
                            uri_moji_html = generic_url(realmoji.get('uri'), True)                 
                            # realmoji id
                            realmoji_id = realmoji.get('id')

                            # location
                            location = f"[object][{i}][allDetailedPosts][{j}][details][full][metadata][realMojis][{r}]"

                            # html row
                            data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, moment_id, realmoji_id, file_rel_path, location))
                    
                            # lava row
                            data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, moment_id, realmoji_id, file_rel_path, location))

            # disk-bereal-Production_postFeedItems
            elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
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

                            # realmojis
                            realmojis = post.get('realMojis')
                            if not bool(realmojis):
                                continue

                            for r in range(0, len(realmojis)):
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
                                uri_moji = generic_url(realmoji.get('uri'), False)
                                uri_moji_html = generic_url(realmoji.get('uri'), True)                 
                                # realmoji id
                                realmoji_id = realmoji.get('id')

                                # location
                                location = f"[object][beRealOfTheDay][series][posts][{i}][realMojis][{r}]"

                                # html row
                                data_list_html.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji_html, moment_id, realmoji_id, file_rel_path, location))
                        
                                # lava row
                                data_list.append((reaction_date, bereal_id, direction, owner, author, emoji, uri_moji, moment_id, realmoji_id, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass
            
    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, (data_list, data_list_html), source_path


# comments
@artifact_processor
def bereal_comments(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'BeReal ID', 'Direction', 'Owner', 'Author', 'Text', 'Moment ID', 'Comment ID', 'Source file name', 'Location' ]
    data_list = []
    source_paths = set()

    # all files
    for file_found in files_found:
        json_data = get_json_data(file_found)
        if not bool(json_data):
            continue

        try:
            if is_platform_windows() and file_found.startswith('\\\\?\\'):
                file_location = str(Path(file_found[4:]).parents[1])
                file_rel_path = str(Path(file_found[4:]).relative_to(file_location))
            else:
                file_location = str(Path(file_found).parents[1])
                file_rel_path = str(Path(file_found).relative_to(file_location))
            source_paths.add(file_location)

            # object?
            obj_ref = json_data.get('object')
            if not bool(obj_ref):
                continue

            # person (dictionary)
            # PersonRepository
            if file_rel_path.startswith('PersonRepository'):               
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

                        # location
                        location = f"[object][beRealOfTheDay][series][posts][{i}][comment][{c}]"

                        # lava row
                        data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, file_rel_path, location))

            # memories (array)
            # disk-bereal-MemoriesRepository-subject-key
            elif file_rel_path.startswith('disk-bereal-MemoriesRepository-subject-key'):
                # memories
                memories = json_data.get('object')
                if not bool(memories):
                    continue

                # owner user id
                owner_user_id = bereal_user_id
                # owner user name
                owner_user_name = map_id_name.get(owner_user_id)
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

                            # location
                            location = f"[object][{i}][allDetailedPosts][{j}][details][full][metadata][comments][{c}]"

                            # lava row
                            data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, file_rel_path, location))

            # disk-bereal-Production_postFeedItems
            elif file_rel_path.startswith('disk-bereal-Production_postFeedItems'):
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

                                # location
                                location = f"[object][{i}][{m}][posts][{p}][comment][{c}]"

                                # lava row
                                data_list.append((creation_date, bereal_id, direction, owner, author, text, moment_id, comment_id, file_rel_path, location))

        except Exception as e:
            logfunc(f"Error: {str(e)}")
            pass
            
    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    # paths
    source_path = ', '.join(source_paths)

    return data_headers, data_list, source_path


# messages
@artifact_processor
def bereal_messages(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Sent', 'Owner', 'Direction', 'Sender', 'Recipient', 'Message', 'Message type',
                    'Source', 'Media URL', 'Thread ID', 'Location' ]
    data_list = []
    data_list_html = []
    source_path = get_file_path(files_found, "bereal-chat.sqlite")

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

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
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

        # media url
        media_url_html = generic_url(record[10], html_format = True)
        media_url = generic_url(record[10], html_format = False)

        # location
        location = [ f'ZMESSAGEMO (Z_PK: {record[0]})' ]
        if record[1] is not None: location.append(f'ZCONVERSATIONMO (Z_PK: {record[1]})')
        if record[2] is not None: location.append(f'ZMEDIAMO (Z_PK: {record[2]})')
        location = ', '.join(location)

        # html row
        data_list_html.append((created, owner, record[5], sender, recipient, body, record[8], 
                               record[9], media_url_html, record[11], location))

        # lava row
        data_list.append((created, owner, record[5], sender, recipient, body, record[8], 
                          record[9], media_url, record[11], location))

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')

    return data_headers, (data_list, data_list_html), source_path


# chat list
@artifact_processor
def bereal_chat_list(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_headers = [ 'Created', 'Owner', 'Type', 'Administrators', 'Participants', 'Last message', 'Total messages', 'Last updated',
                     'Unread messages count', 'ID', 'Location' ]
    data_list = []
    data_list_html = []
    source_path = get_file_path(files_found, "bereal-chat.sqlite")

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

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
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
            admins = '\n'.join(admins_list)
        admins_html = admins.replace('\n', '<br />')

        # participants (plist)
        participants = get_plist_content(record[7])
        participants_list = []
        for p in participants:
            participants_list.append(format_userid(p))
        if bool(participants_list):
            participants = '\n'.join(participants_list)
        participants_html = participants.replace('\n', '<br />')

        # body
        body = record[8].decode('utf-8') if bool(record[8]) else record[8]

        # location
        location = [ f'ZCONVERSATIONMO (Z_PK: {record[0]})' ]
        if record[1] is not None: location.append(f'ZCONVERSATIONSTATUSMO (Z_PK: {record[1]})')
        if record[2] is not None: location.append(f'ZMESSAGEMO (Z_PK: {record[2]})')
        location = ', '.join(location)

        # html row
        data_list_html.append((created, owner, record[5], admins_html, participants_html, body, record[9], last_updated,
                               record[11], record[12], location))

        # lava row
        data_list.append((created, owner, record[5], admins, participants, body, record[9], last_updated,
                          record[11], record[12], location))

    # lava types
    data_headers[0] = (data_headers[0], 'datetime')
    data_headers[10] = (data_headers[10], 'datetime')

    return data_headers, (data_list, data_list_html), source_path
