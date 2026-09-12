__artifacts_v2__ = {
    "tutanota_ios_accounts": {
        "name": "Tutanota - Accounts",
        "description": "Accounts the app held credentials for, from its credentials database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per row of the credentials table in credentials.sqlite, which the app "
                 "keeps in its shared app group container. The file is a plain SQLite database "
                 "and is read directly. Sourced from the app's own code at tutao/tutanota commit "
                 "3b8e8472bba09342d49851f0e14bb22b398879a8: "
                 "app-ios/TutanotaSharedFramework/Credentials/CredentialsDatabase.swift names the "
                 "file credentials.sqlite and creates these tables, and it opens the file with "
                 "the SqliteDb class, whose own comment in app-ios/Sqlcipher/SqliteDb.swift "
                 "states that it does not set the key for SQLCipher. That code describes the "
                 "current app; the reading here is what the tested images hold, and the database "
                 "on the tested image carries no meta table, which that code creates. Login is "
                 "the address the account signs in with and User ID is the account identifier the "
                 "app uses. Credential Type and Credential Encryption Mode are reported as "
                 "stored; the tested image holds internal and DEVICE_LOCK, and the database also "
                 "carries the three modes the app allows, BIOMETRICS, DEVICE_LOCK and "
                 "SYSTEM_PASSWORD. The row stores an access token, an offline database key and an "
                 "encrypted password, and a separate table stores a credential encryption key. "
                 "All four are encrypted, so this artifact reports only whether each is present "
                 "and prints none of them. The offline database is opened by "
                 "openDb(userId:dbkey:) in "
                 "app-ios/TutanotaSharedFramework/Offline/SqlCipherDb.swift with a per-account "
                 "key, and the key that protects the credential fields is held through the iOS "
                 "keychain by app-ios/TutanotaSharedFramework/Keychain/KeychainEncryption.swift. "
                 "Neither key is in the filesystem, so the mail the offline database holds is not "
                 "readable from an extraction alone. Offline Database is the file in the same "
                 "container whose name carries this row's user id, matched on that id rather than "
                 "by position, and Offline Database Size is that file's size in bytes. Only the "
                 "iOS 17.3 image held a credentials database. The iOS 15.3.1, 14.3 and 13.3.1 "
                 "images, running Tutanota 3.112.6, 3.80.5 and 3.69.2, hold no such file, so they "
                 "report nothing here while still reporting a push registration. A file is read "
                 "only when it sits inside a container whose own "
                 ".com.apple.mobile_container_manager.metadata.plist names de.tutao.tutanota or "
                 "group.de.tutao.tutanota, so a credentials.sqlite belonging to another app is "
                 "not read. On the two tested images that do not carry the app every artifact in "
                 "this module reported nothing.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/credentials.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/offline_*.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Documents/offline_*.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Tuta Mail 232.240621.0 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | Tutanota 3.112.6 | 0 rows",
            "hickman_ios14": "iOS 14.3 | Tutanota 3.80.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Tutanota 3.69.2 | 0 rows",
            "abe_ios16": "iOS 16.5 | Tutanota not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Tutanota not installed | 0 rows",
        },
    },
    "tutanota_ios_push_registration": {
        "name": "Tutanota - Push Registration",
        "description": "The push registration the app kept in its preferences, with the server "
                       "it registered against.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per preferences file that carries the app's sseInfo value, from "
                 "Library/Preferences/de.tutao.tutanota.plist in the app's data container and "
                 "Library/Preferences/group.de.tutao.tutanota.plist in its shared app group "
                 "container. The iOS 17.3 image holds the value in both files with the same push "
                 "identifier in each, which is why it reports 2 rows for one device; the other "
                 "three images hold it in one file and report one row each. Push Identifier is "
                 "the identifier the app registered for server sent events and Server Origin is "
                 "the server it registered against. That origin was https://mail.tutanota.com on "
                 "the iOS 13.3.1, 14.3 and 15.3.1 images and https://app.tuta.com on the iOS 17.3 "
                 "image, whose app bundle is named Tuta Mail and carries version 232.240621.0 "
                 "against 3.69.2, 3.80.5 and 3.112.6 on the others. User IDs is the list the same "
                 "value carries: it named one account on the iOS 13.3.1, 14.3 and 15.3.1 images "
                 "and was empty on the iOS 17.3 image, whose account identifier is in the "
                 "credentials database instead. Last Missed Notification Check is a plist date "
                 "and is present on the iOS 14.3 and 15.3.1 images only. Last Processed "
                 "Notification ID is reported as stored. Repeating Alarm Notifications is the "
                 "number of entries in the app's stored repeating alarm list, which is a JSON "
                 "array kept as bytes; it held none on every image that carries the key and the "
                 "key is absent on the iOS 13.3.1 image, so no calendar alarm is reported from "
                 "any tested image. A row records a registration the app made. It does not "
                 "establish that any notification was delivered or read. On the two tested images "
                 "that do not carry the app every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Preferences/de.tutao.tutanota.plist',
                  '*/mobile/Containers/Shared/AppGroup/*/Library/Preferences/group.de.tutao.tutanota.plist'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "bell",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Tuta Mail 232.240621.0 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | Tutanota 3.112.6 | 1 row",
            "hickman_ios14": "iOS 14.3 | Tutanota 3.80.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | Tutanota 3.69.2 | 1 row",
            "abe_ios16": "iOS 16.5 | Tutanota not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Tutanota not installed | 0 rows",
        },
    },
    "tutanota_ios_offline_stores": {
        "name": "Tutanota - Offline Stores",
        "description": "Offline mail databases the app kept, one per account, with whether each "
                       "could be read.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per offline database the app kept, matched by the name shape "
                 "offline_<user id>.sqlite. The app writes one per account and names it for that "
                 "account, so User ID In File Name is read from the file name. On the iOS 17.3 "
                 "image that id equalled the user id of the one row in the credentials database, "
                 "and on the iOS 15.3.1 image it equalled the user id the push registration "
                 "carries. Reads As Plain SQLite is measured here by opening the file: it was No "
                 "on both stores, and First Sixteen Bytes is the head of each file, neither of "
                 "which is the SQLite magic. The offline database is opened by "
                 "openDb(userId:dbkey:) in "
                 "app-ios/TutanotaSharedFramework/Offline/SqlCipherDb.swift with a per-account "
                 "key, and the key that protects the credential fields is held through the iOS "
                 "keychain by app-ios/TutanotaSharedFramework/Keychain/KeychainEncryption.swift. "
                 "Neither key is in the filesystem, so the mail the offline database holds is not "
                 "readable from an extraction alone. So a row records that an offline mail "
                 "database exists for that account and how large it is, and nothing about the "
                 "mail in it. The iOS 14.3 and 13.3.1 images, running Tutanota 3.80.5 and 3.69.2, "
                 "hold no offline database. The app moved the file between releases: it was in "
                 "the app's own Documents folder on the iOS 15.3.1 image and in the shared app "
                 "group container on the iOS 17.3 image, and both locations are read. A file is "
                 "read only when it sits inside a container whose own "
                 ".com.apple.mobile_container_manager.metadata.plist names de.tutao.tutanota or "
                 "group.de.tutao.tutanota. On the two tested images that do not carry the app "
                 "every artifact in this module reported nothing.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/offline_*.sqlite*',
                  '*/mobile/Containers/Data/Application/*/Documents/offline_*.sqlite*',
                  '*/mobile/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "database",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | Tuta Mail 232.240621.0 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | Tutanota 3.112.6 | 1 row",
            "hickman_ios14": "iOS 14.3 | Tutanota 3.80.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Tutanota 3.69.2 | 0 rows",
            "abe_ios16": "iOS 16.5 | Tutanota not installed | 0 rows",
            "jess_ios15": "iOS 15.0.2 | Tutanota not installed | 0 rows",
        },
    },
}

import json
import os
import plistlib
import re
import sqlite3

from scripts.ilapfuncs import (artifact_processor, get_plist_file_content, get_sqlite_db_records,
                               logfunc)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_APP_ID = 'de.tutao.tutanota'
_GROUP_ID = 'group.de.tutao.tutanota'
_CREDENTIALS = 'credentials.sqlite'
_SQLITE_MAGIC = b'SQLite format 3\x00'
# The app names each offline database for the account's own user id.
_OFFLINE_NAME = re.compile(r'^offline_(.+)\.sqlite$')


def _containers(files_found):
    '''{container directory: identifier} from each container's own metadata plist.'''
    containers = {}
    for found in files_found:
        path = str(found)
        if os.path.basename(path) != _METADATA_NAME or os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Tutanota: could not read a container metadata plist: {error}')
            continue
        identifier = plist.get('MCMMetadataIdentifier')
        if identifier in (_APP_ID, _GROUP_ID):
            containers[os.path.dirname(path).replace('\\', '/')] = identifier
    return containers


def _in_tutanota_container(path, containers):
    '''True when the file sits inside a container the metadata plist names as the app's.'''
    path = str(path).replace('\\', '/')
    return any(path.startswith(container + '/') for container in containers)


def _files(files_found, containers, wanted):
    '''Matched files named <wanted>, kept only inside the app's own containers.'''
    keep = []
    for found in files_found:
        path = str(found).replace('\\', '/')
        if os.path.isdir(path) or not wanted(os.path.basename(path)):
            continue
        if _in_tutanota_container(path, containers) and path not in keep:
            keep.append(path)
    return keep


def _offline_stores(files_found, containers):
    '''(path, user id from the file name) for each offline database.'''
    stores = []
    for path in _files(files_found, containers, lambda name: bool(_OFFLINE_NAME.match(name))):
        stores.append((path, _OFFLINE_NAME.match(os.path.basename(path)).group(1)))
    return stores


def _readable(path):
    '''Whether the file opens as a plain SQLite database, and its first table names.'''
    try:
        with open(path, 'rb') as handle:
            if handle.read(16) != _SQLITE_MAGIC:
                return False
    except OSError as error:
        logfunc(f'Tutanota: could not read {os.path.basename(path)}: {error}')
        return False
    try:
        get_sqlite_db_records(path, "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
    except sqlite3.Error as error:
        logfunc(f'Tutanota: {os.path.basename(path)} did not open: {error}')
        return False
    return True


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return ''


def _alarm_count(value):
    '''How many entries the stored repeating alarm list holds, or '' when it is absent.'''
    if value in (None, ''):
        return ''
    if isinstance(value, list):
        return len(value)
    if isinstance(value, bytes):
        value = value.decode('utf8', 'replace')
    if isinstance(value, str):
        try:
            return len(json.loads(value))
        except (ValueError, TypeError):
            return ''
    return ''


def _present(value):
    '''Yes or No for a stored value, without printing the value itself.'''
    return 'Yes' if value not in (None, '', b'') else 'No'


@artifact_processor
def tutanota_ios_accounts(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    stores = {user: (path, _size(path))
              for path, user in _offline_stores(files_found, containers)}
    data_list = []
    sources = []

    for path in _files(files_found, containers, lambda name: name == _CREDENTIALS):
        if not _readable(path):
            logfunc(f'Tutanota: {os.path.basename(path)} is not a plain SQLite database')
            continue
        try:
            mode = list(get_sqlite_db_records(
                path, 'SELECT credentialEncryptionMode FROM credentialEncryptionMode'))
            key = list(get_sqlite_db_records(
                path, 'SELECT credentialEncryptionKey FROM credentialEncryptionKey'))
            rows = list(get_sqlite_db_records(
                path, 'SELECT login, userId, type, accessToken, databaseKey, encryptedPassword '
                      'FROM credentials'))
        except sqlite3.Error as error:
            logfunc(f'Tutanota: could not read the credentials database: {error}')
            continue
        if path not in sources:
            sources.append(path)
        stored_mode = mode[0][0] if mode else ''
        for login, user, kind, token, database_key, password in rows:
            store, size = stores.get(str(user), ('', ''))
            if store and store not in sources:
                sources.append(store)
            data_list.append((
                login,
                user,
                kind,
                stored_mode,
                _present(key[0][0] if key else None),
                _present(token),
                _present(database_key),
                _present(password),
                os.path.basename(store) if store else '',
                size,
            ))

    data_headers = (
        'Login',
        'User ID',
        'Credential Type (as stored)',
        'Credential Encryption Mode (as stored)',
        'Credential Encryption Key Stored',
        'Access Token Stored',
        'Offline Database Key Stored',
        'Encrypted Password Stored',
        'Offline Database',
        'Offline Database Size (Bytes)',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tutanota_ios_push_registration(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for found in files_found:
        path = str(found)
        name = os.path.basename(path)
        if os.path.isdir(path) or name not in (f'{_APP_ID}.plist', f'{_GROUP_ID}.plist'):
            continue
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            continue
        registration = plist.get('sseInfo')
        if not isinstance(registration, dict):
            continue
        if path not in sources:
            sources.append(path)
        alarms = _alarm_count(plist.get('repeatingAlarmNotification'))
        data_list.append((
            plist.get('lastMissedNotificationCheckTime', ''),
            ', '.join(str(user) for user in registration.get('userIds') or []),
            registration.get('pushIdentifier', ''),
            registration.get('sseOrigin', ''),
            plist.get('lastProcessedNotificationId', ''),
            alarms,
            name,
        ))

    data_headers = (
        ('Last Missed Notification Check', 'datetime'),
        'User IDs',
        'Push Identifier',
        'Server Origin',
        'Last Processed Notification ID',
        'Repeating Alarm Notifications',
        'Preferences File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tutanota_ios_offline_stores(context):
    files_found = context.get_files_found()
    containers = _containers(files_found)
    data_list = []
    sources = []

    for path, user in _offline_stores(files_found, containers):
        if path not in sources:
            sources.append(path)
        with open(path, 'rb') as handle:
            head = handle.read(16)
        data_list.append((
            os.path.basename(path),
            user,
            _size(path),
            'Yes' if _readable(path) else 'No',
            head.hex(),
        ))

    data_headers = (
        'File Name',
        'User ID In File Name',
        'File Size (Bytes)',
        'Reads As Plain SQLite',
        'First Sixteen Bytes',
    )
    return data_headers, data_list, '\n'.join(sources)
