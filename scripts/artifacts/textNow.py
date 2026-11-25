__artifacts_v2__ = {
    "textnow_ios_messages": {
        "name": "TextNow - Messages",
        "description": "Messages held in the TextNow account store, with the picture "
                       "each picture message points at where the app cached it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per row of ZTMOINTERACTION that carries no call "
                 "identifier, in the Core Data store the app keeps for the "
                 "account. On the two older tested images (TextNow 20.10.0 and "
                 "21.3.0) the store is Documents/<20 digits><username> in the "
                 "app's own container; what the digits are is not established "
                 "here. On the iOS 26.5.2 image (TextNow 26.39.1) it sits at "
                 "the top of the app group container "
                 "group.com.textnow.TextNowSwiftAppGroup and is named for the "
                 "username alone, and no file matching the Documents pattern is "
                 "in the app's container on that image. The store is named for "
                 "the account it belongs to, so it cannot be matched on its "
                 "name: in Documents the glob accepts any file whose path below "
                 "Documents starts with ten digits, which includes every file "
                 "under a folder named that way, in the app group every file of "
                 "the group container is offered, and the module then reads "
                 "only the ones that are SQLite and carry the app's own "
                 "ZTMOACCOUNTINFO table. On two of the four tested images files "
                 "of other apps matched the Documents glob (6 files and 10 "
                 "files, 3 of them SQLite databases), were staged, and produced "
                 "no rows. The app's container and the group container are "
                 "recognised by the identifier their "
                 ".com.apple.mobile_container_manager.metadata.plist records, "
                 "com.tinginteractive.usms for the app and the group name above "
                 "for the group, and an app group store is tied to the app's "
                 "container, where its pictures are cached, only when exactly "
                 "one container records the app's identifier. At this revision, "
                 "in a test tree holding a second copy of the group container "
                 "and a third copy whose metadata names another group, the "
                 "artifact reported the 26 rows twice and nothing from the "
                 "third. On the two older images the data lives in the "
                 "write-ahead log: on the iOS 13.3.1 and 14.3 images, of the "
                 "eleven tables that hold rows, the eight that hold app data "
                 "return zero rows when the database is read without its log, "
                 "ZTMOINTERACTION, ZTMOCONVERSATION, ZTMOCONTACTVALUE, "
                 "ZTMOABCONTACT and ZTMOSERVERCONTACT among them, and only the "
                 "three Core Data bookkeeping tables survive in the database "
                 "itself. On the iOS 26.5.2 image the database already holds 20 "
                 "of the 26 ZTMOINTERACTION rows, and the log adds the other 6 "
                 "and changes 18 of those 20. The sidecar is therefore not "
                 "optional and the glob picks it up. Message Time is "
                 "ZLOCALTIMESTAMP and Remote Time is ZREMOTETIMESTAMP, both "
                 "Core Data times, seconds since 2001, reported in UTC. They "
                 "are not the same reading: on the iOS 14.3 image four rows "
                 "carry a remote time from October 2020 against a local time in "
                 "February 2021. Direction reads the app's stored ZDIRECTION, 2 "
                 "as outgoing and 1 as incoming, and that reading rests on the "
                 "tested stores, not on a source: there, rows read as outgoing "
                 "carry no author name and rows read as incoming carry one "
                 "except where Sender is blank, and the same two values appear "
                 "on the call rows where the app's separate call history names "
                 "one as dialled. Sender takes the stored author name, and on "
                 "an outgoing row it takes the value the store marks with "
                 "ZCONTACTISSELF, since no outgoing row on the tested images "
                 "carries an author name. On the two older images that is an "
                 "address holding the username. On the iOS 26.5.2 image it is a "
                 "four-digit string, which fills Sender on all 11 outgoing rows "
                 "there, and what it denotes is not established. It is blank on "
                 "5 rows, which are incoming rows the app left without an "
                 "author. Picture is filled from two caches, and each names its "
                 "file by something the store records, so the link is one the "
                 "app made, not a match on size or time. The first is the image "
                 "library's cache. A picture message stores the address the "
                 "picture was fetched from as its text, and the cache file is "
                 "looked up under the MD5 of that address with no extension. "
                 "That cache is Documents/com.hackemist.SDWebImageCache.default "
                 "on the two older images and "
                 "Library/Caches/com.hackemist.SDImageCache/default on the iOS "
                 "26.5.2 image, and both are read. Current SDWebImage "
                 "(SDDiskCacheFileNameForKey in SDWebImage/Core/SDDiskCache.m "
                 "at 8a1be70a, 2024) appends the address's path extension when "
                 "it has one, so when no file carries the bare MD5 name a file "
                 "in the same container named with that MD5, a dot and an "
                 "extension is used. No message resolved through that second "
                 "form on the tested images. Two of the 16 entries on the iOS "
                 "26.5.2 image carry an extension, and neither is named by a "
                 "message. This cache resolved on 4 of the 4 rows that carry "
                 "thumbnail dimensions on the two older images and on 6 of the "
                 "7 picture messages on the iOS 26.5.2 image. The second is the "
                 "app's own cache, Library/Caches/media, used when the first "
                 "has no file. A file there is named for the message's Core "
                 "Data object identifier, x-coredata://<store "
                 "UUID>/<entity>/p<row>, with everything but letters and digits "
                 "removed. That form was read off the tested images, not from a "
                 "TextNow source: on all three, every file in the folder (15, 2 "
                 "and 7) carries the UUID of the store beside it and the key of "
                 "an image message row, and every image message row has one. "
                 "The two caches hold different bytes for the same message, at "
                 "the same pixel dimensions on all 10 messages where both have "
                 "a file, so the order decides which copy is shown; the image "
                 "library's copy is tried first, which keeps the pictures "
                 "reported on the older images unchanged. The app's cache adds "
                 "two kinds of row. On the iOS 13.3.1 image it adds a picture "
                 "to 13 rows whose message text is a local path into the app's "
                 "Leanplum resource cache, not an address; the 13 texts name "
                 "the same resource file, under two container paths, and all 13 "
                 "resolve to one identical JPEG, which was not compared with "
                 "the Leanplum copy. On the iOS 26.5.2 image it adds the one "
                 "picture message for which the image library's cache holds no "
                 "file under the MD5 of its address. The bytes are checked "
                 "before anything is rendered and only a file starting with a "
                 "JPEG, PNG or GIF signature, or a RIFF header, is attached; "
                 "the files attached were JPEG on the older images and JPEG, "
                 "PNG and GIF on the iOS 26.5.2 image. The pairing is "
                 "corroborated where the row records thumbnail dimensions: the "
                 "message row records ZTHUMBNAILWIDTH and ZTHUMBNAILHEIGHT, and "
                 "on the 4 such rows of the older images and on 5 of the 7 of "
                 "the iOS 26.5.2 image those two numbers equal the pixel "
                 "dimensions of the file attached. On the other 2 the file is "
                 "smaller in the same proportion, 3:4. The image library's "
                 "cache was counted in full. On the two older images it holds "
                 "11 entries, all JPEG, of which 4 are named by a message. Of "
                 "the 7 that are not, 2 carry the same pixel dimensions as a "
                 "picture a message already names, so they match a named "
                 "picture in dimensions only; whether they are the same "
                 "photograph was not established. The remaining 5 are 320 "
                 "pixels square or smaller. On the iOS 26.5.2 image it holds 16 "
                 "entries, of which 6 are named by a message, and 2 of the 10 "
                 "others are byte-identical to named ones. What the entries no "
                 "message names are is not established here. That cache folder "
                 "is named for the image library, not for the app, so an entry "
                 "is only used for a store tied to the same container. "
                 "Conversation is the name or address the conversation is with, "
                 "and it is blank on 40 rows because the store left them with "
                 "no conversation link: 30 on the iOS 13.3.1 image, which carry "
                 "an author identifier made of digits and two # characters, not "
                 "a name, and, on eleven of them, a local file path to an image "
                 "in place of message text, and 10 on the iOS 26.5.2 image, all "
                 "incoming. Two further rows on the iOS 13.3.1 image carry such "
                 "a path and do have a conversation link, so thirteen rows in "
                 "all hold one. Deleted State is reported as stored and is 0 on "
                 "86 rows and 2 on 4; the four rows marked 2 still hold their "
                 "full text, and Deleted State held 0 on all 26 rows of the iOS "
                 "26.5.2 image. Read State, Send Status and Image Type are "
                 "reported as stored and are not translated. Image Type is "
                 "blank on 66 rows. Thumbnail Width and Height are filled only "
                 "on picture rows that carry an address, 4 on the older images "
                 "and 7 on the iOS 26.5.2 image. The store also holds "
                 "ZTMOSIPDATA, ZTMOBLOCKEDCONTACT, ZTMOCALLERIDENTRY, "
                 "ZTMOPURCHASETRANSACTION, ZTMOQOSTESTPROFILE and "
                 "ZTMOQOSTESTSERVER, all empty on the three tested images, "
                 "ZTMOPREMIUMSTATE, which holds one row on each of the three, "
                 "and Documents/ILDRates.sqlite, whose tables (ZTMOCOUNTRY, "
                 "ZTMODIALCODE, ZTMORATE on the iOS 26.5.2 image) hold call and "
                 "SMS rates by country and dial code. The iOS 26.5.2 store adds "
                 "ZTMOMUTEDCONTACT, ZTMOREACTION, ZTMOSCHEDULEDMESSAGE and "
                 "ZTMOSUBSCRIPTION, all empty, and three Core Data history "
                 "tables that hold rows. None of those is read here.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/Documents/com.hackemist.SDWebImageCache.default/*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 49 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 15 rows",
                                            "wilkerson_iphone16_ios26": "iOS 26.5.2 | TextNow 26.39.1 | 26 rows",
                                            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no TextNow container",
                                        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Time",
                "senderColumn": "Sender",
                "mediaColumn": "Picture",
            }
        },
    },
    "textnow_ios_calls": {
        "name": "TextNow - Calls",
        "description": "Calls held in the TextNow account store, with the matching row "
                       "from eventHistory.db, a separate call history database in the app's "
                       "container, beside each one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per row of ZTMOINTERACTION that carries a call "
                 "identifier, in the same account store the messages are read "
                 "from, in the app's Documents or in its app group container. "
                 "Call Start comes out of that identifier, which the app writes "
                 "as the other number and the call's own Core Data time joined "
                 "by a hyphen, and Recorded At is the row's ZLOCALTIMESTAMP. "
                 "They are not the same instant: on the calls of the tested "
                 "images the row time is later than the start. The columns "
                 "whose names begin with Call History come from "
                 "eventHistory.db, a separate database in the app's container; "
                 "which component writes it is not sourced here. The two are "
                 "joined on the time inside the call identifier, which is that "
                 "database's own Events.timestamp, so the link is recorded "
                 "rather than inferred, and it matched on 4 of 4 calls. Each "
                 "database holds exactly two calls on each of the two older "
                 "images and none was left unmatched. An eventHistory.db entry "
                 "is only used for a store tied to the same container. The iOS "
                 "26.5.2 image (TextNow 26.39.1) holds no call row and no "
                 "eventHistory.db under the app's Library/Application Support, "
                 "so calls from a store in the app group container are "
                 "unexercised. Duration and Call History Duration are two "
                 "separate recordings of the same call and they disagree "
                 "slightly, the app's own row being shorter by less than a "
                 "tenth of a second on all four, so both are reported rather "
                 "than one being chosen. Direction reads ZDIRECTION the same "
                 "way the messages do, and here the second database "
                 "corroborates it: the 2 rows read as outgoing are the ones it "
                 "records with a dial action and no sender, and the 2 read as "
                 "incoming are the ones whose sender is the other number. Call "
                 "History Dial Action is therefore blank on 2 rows by the same "
                 "token. Call History Result holds that database's own codes "
                 "and is reported as stored, without translation, because no "
                 "source for their meaning was found; on the tested images it "
                 "reads 16 on the two outgoing calls and 1 on the two incoming "
                 "ones. Status is the app's own value and reads 4 on all 4 "
                 "rows. Call ID and Call History Call ID are the two stores' "
                 "separate identifiers for the same call and they do not match "
                 "each other. A call recorded in eventHistory.db with no "
                 "matching row in the account store would not be reported here; "
                 "on the tested images there were none.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/Library/Application Support/eventHistory.db*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 2 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 2 rows",
                                            "wilkerson_iphone16_ios26": "iOS 26.5.2 | TextNow 26.39.1 | 0 rows, no call rows and no eventHistory.db in the app container",
                                            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no TextNow container",
                                        },
    },
    "textnow_ios_contacts": {
        "name": "TextNow - Contacts",
        "description": "Addresses and names the TextNow account store holds, for the "
                       "account itself, for the correspondents it has conversations "
                       "with and for the other addresses the store holds.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per row of ZTMOCONTACTVALUE, in the same account "
                 "store the messages are read from, in the app's Documents or "
                 "in its app group container. Contact Value is the address as "
                 "stored, which is a telephone number on some rows, an email "
                 "address or a service address on others, and a four-digit "
                 "string on one row of the iOS 26.5.2 image. Account Own "
                 "Address reads Yes on the 3 rows the store marks with "
                 "ZCONTACTISSELF, one per image. On the two older images those "
                 "rows hold an address made from the account's username. On the "
                 "iOS 26.5.2 image the row holds a four-digit string, and what "
                 "it denotes is not established. Address Book Name comes from "
                 "ZTMOABCONTACT through the join table Core Data keeps between "
                 "the two. That table and its two columns are named for the "
                 "numbers Core Data gave the entities, and those numbers move "
                 "between releases, so the table is found by shape rather than "
                 "by a name written into this module. Two address book rows "
                 "point at one address on the iOS 14.3 image, so two rows there "
                 "list that name twice over. The column is blank on 14 of 22 "
                 "rows. Address Book Name is blank on all 6 rows of the iOS "
                 "26.5.2 image, whose ZTMOABCONTACT is empty, and Label is "
                 "blank on all 6 rows of that image as well. Contact Name is "
                 "the name the app itself holds and is blank on 18 rows. "
                 "Service Contact Name and Service Contact Picture Key come "
                 "from ZTMOSERVERCONTACT, joined through the row's "
                 "ZSERVERCONTACT link. What a linked row represents is not "
                 "established here. In Network is reported as stored and is "
                 "blank on 13 rows. Conversation names the conversation the "
                 "address is attached to and is blank on 10 rows, which are "
                 "addresses the store holds without one. Rows are addresses the "
                 "app knows about, not a list of the device's contacts: the "
                 "device address book itself is not read here.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 8 rows",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 8 rows",
                                            "wilkerson_iphone16_ios26": "iOS 26.5.2 | TextNow 26.39.1 | 6 rows",
                                            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no TextNow container",
                                        },
    },
    "textnow_ios_account": {
        "name": "TextNow - Account",
        "description": "The TextNow account the store belongs to, with the number "
                       "assigned to it and its service settings.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Original contribution credited to Claude. One row per "
                 "ZTMOACCOUNTINFO row, in the same account store the messages "
                 "are read from, in the app's Documents or in its app group "
                 "container. It held a single row on each of the 3 tested "
                 "images that carry the store. The two older images carry the "
                 "same account and the iOS 26.5.2 image another. TextNow Number "
                 "is ZPHONENUMBER as stored; it differs between the two older "
                 "images, so it is not a fixed property of the account, and it "
                 "is NULL on the iOS 26.5.2 row, so TextNow Number is blank "
                 "there. Username, Email, User ID and User ID (Hex) are "
                 "reported as stored. Name joins ZFIRSTNAME and ZLASTNAME with "
                 "surrounding spaces removed. Record Updated, Server Record "
                 "Time, Wallet Updated and Ad Removal Expiry are Core Data "
                 "times, seconds since 2001, reported in UTC. Ad Removal Expiry "
                 "falls on midnight UTC on all 3 rows. SIP Username and SIP "
                 "Host are reported as stored and are NULL on the iOS 26.5.2 "
                 "row. SIP Client IP is ZSIPCLIENTIP as stored and is filled on "
                 "2 of the 3 rows. Where the value comes from is not "
                 "established here. The store can also hold the account's SIP "
                 "password. It is not printed here: SIP Password Stored says "
                 "only whether a value is present, which it was on the two "
                 "older rows and was not on the iOS 26.5.2 row. Account Status, "
                 "Credits, TextNow Credit, Currency, Unlimited and Show Ads are "
                 "reported as stored. Email Verified (as stored) retains "
                 "ZEMAILVERIFIED without interpreting its values. A stored NULL "
                 "and an absent column both return NULL through the existing "
                 "optional-column query; they are not distinguished here. "
                 "Account Status reads ENABLED and Unlimited reads 1 on all 3 "
                 "rows. ZEMAILVERIFIED reads 1, Credits 5 and TextNow Credit 10 "
                 "on the two older rows, and all three read 0 on the iOS 26.5.2 "
                 "row. Show Ads reads 1 on two rows and 0 on one. A release of "
                 "the app that does not carry a column is read as an empty "
                 "column of that name rather than costing the query every row: "
                 "the iOS 13.3.1 store has no SIP Client IP column and still "
                 "reports its account.",
        "paths": ('*/Containers/Data/Application/*/Documents/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user-check",
                         "sample_data": {
                                            "hickman_ios13": "iOS 13.3.1 | TextNow 20.10.0 | 1 row",
                                            "hickman_ios14": "iOS 14.3 | TextNow 21.3.0 | 1 row",
                                            "wilkerson_iphone16_ios26": "iOS 26.5.2 | TextNow 26.39.1 | 1 row",
                                            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows, no TextNow container",
                                        },
    },
}

import hashlib
import os
import plistlib
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, is_sqlite_sidecar, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_CONTAINER = re.compile(r'(.*?/Containers/Data/Application/[0-9A-Fa-f-]{36})/', re.I)
_METADATA = '.com.apple.mobile_container_manager.metadata.plist'
_METADATA_GLOBS = ('*/Containers/Data/Application/*/' + _METADATA,
                   '*/Containers/Shared/AppGroup/*/' + _METADATA)
# The identifiers the container metadata recorded for TextNow 26.39.1 on iOS 26.5.2.
_APP_ID = 'com.tinginteractive.usms'
_GROUP_ID = 'group.com.textnow.TextNowSwiftAppGroup'
_IMAGE_CACHES = ('/com.hackemist.SDWebImageCache.default/', '/com.hackemist.SDImageCache/default/')
_MEDIA_CACHE = '/Library/Caches/media/'
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a', b'RIFF')
_CALL_ID = re.compile(r'^(.*)-(\d+(?:\.\d+)?)$')


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    if value is None:
        return ''
    return str(value)


def _name(first, last):
    '''A first and last name as one, with the padding the store keeps around them dropped.'''
    return ' '.join(part for part in (_text(first).strip(), _text(last).strip()) if part)

def _number(value):
    '''A stored number as text, without a trailing .0 on a whole value.'''
    if value in (None, ''):
        return ''
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return str(int(number)) if number == int(number) else f'{number:.6f}'


def _textnow_containers(files_found):
    '''([app container roots], [app group folder names]) the container metadata names as TextNow's.

    The metadata plist at the top of each container records the identifier of the app or
    group that owns it, so the containers are found by what the device recorded, not by
    what they hold.
    '''
    apps, groups = [], []
    for found in files_found:
        path = str(found).replace('\\', '/')
        if os.path.basename(path) != _METADATA:
            continue
        try:
            with open(path, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (OSError, plistlib.InvalidFileException, ValueError) as error:
            logfunc(f'TextNow: could not read {path}: {error}')
            continue
        identifier = metadata.get('MCMMetadataIdentifier') if isinstance(metadata, dict) else None
        folder = os.path.dirname(path)
        if identifier == _APP_ID:
            apps.append(folder)
        elif identifier == _GROUP_ID:
            groups.append(os.path.basename(folder))
    return apps, groups


def _files(context):
    '''Every file the artifact reads: its own matches, plus what the TextNow containers hold.

    From TextNow 26 the account store sits at the top of the app group container rather than
    in the app's Documents folder, and the app caches its pictures under Library/Caches. Those
    containers are named by a random identifier, so they are searched for once the metadata
    has said which ones they are.
    '''
    files_found = [str(found) for found in context.get_files_found()]
    apps, groups = _textnow_containers(files_found)
    if not apps and not groups:
        return files_found, apps
    seeker = context.get_seeker()
    extra = []
    for group in groups:
        extra.extend(seeker.search(f'*/Containers/Shared/AppGroup/{group}/*'))
    for app in apps:
        guid = os.path.basename(app)
        extra.extend(seeker.search(f'*/Containers/Data/Application/{guid}/Library/Caches/media/*'))
        extra.extend(seeker.search(
            f'*/Containers/Data/Application/{guid}/Library/Caches/com.hackemist.SDImageCache/default/*'))
        extra.extend(seeker.search(
            f'*/Containers/Data/Application/{guid}/Library/Application Support/eventHistory.db*'))
    seen = set(files_found)
    files_found.extend(str(path) for path in extra if str(path) not in seen)
    return files_found, apps


def _home(path, apps):
    '''The app container a store belongs to.

    A store in the app's own container belongs to that container. A store in the app group
    belongs to the TextNow app container, which is only decided when the metadata names
    exactly one; with none or several, nothing is joined to it from an app container.
    '''
    container = _container(path)
    if container:
        return container
    if len(apps) == 1:
        return _container(apps[0] + '/')
    if apps:
        logfunc(f'TextNow: {len(apps)} app containers carry {_APP_ID}; '
                f'the app group store at {path} is not joined to any of them')
    return ''


def _stores(files_found, apps=()):
    '''[(container, path)] for every TextNow account store among the matches.

    The store is named for the account it belongs to, so it cannot be matched by name alone.
    A match is only used when it is a database carrying the app's own entity tables, which
    means a file from another app that happens to sit at the same shape of path is refused.
    '''
    stores = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    continue
        except OSError as error:
            logfunc(f'TextNow: could not read {path}: {error}')
            continue
        if not does_table_exist_in_db(path, 'ZTMOACCOUNTINFO'):
            continue
        stores.append((_home(path, apps), path))
    return stores


def _call_histories(files_found):
    '''{container: path} for the call history database the app's calling library keeps.

    That database is the calling library's rather than the app's, so an entry is only used
    for a store found in the same container.
    '''
    histories = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or os.path.basename(path) != 'eventHistory.db':
            continue
        histories[_container(path)] = path
    return histories


def _cached_images(files_found):
    '''{(container, cache file name): path} for the app's own image cache.

    The cache folder is named for the image library rather than for the app, so every entry
    is kept with the container it was found in.
    '''
    entries = {}
    for found in files_found:
        path = str(found)
        normal = path.replace('\\', '/')
        if os.path.isdir(path):
            continue
        if _MEDIA_CACHE in normal:
            # Named for the message's Core Data object identifier, which carries the store's
            # own UUID, so the name alone ties the file to one row of one store.
            entries[('', os.path.basename(path))] = path
            continue
        if not any(cache in normal for cache in _IMAGE_CACHES):
            continue
        name = os.path.basename(path)
        entries[(_container(path), name)] = path
        # SDWebImage can append '.<extension>' to the MD5 name; keep the part before
        # the first dot as a second key, never replacing an exact name.
        stem = name.split('.', 1)[0]
        if stem != name and len(stem) == 32:
            entries.setdefault((_container(path), stem + '.'), path)
    return entries


def _columns(path, table):
    '''The set of column names a table has, or an empty set when it cannot be read.'''
    try:
        return {str(row[1]) for row in get_sqlite_db_records(path, f'PRAGMA table_info({table})')}
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not read the columns of {table}: {error}')
        return set()


def _rows(path, table, columns, where=''):
    '''Rows of a table, or nothing when the store does not have it.

    Releases of the app differ in which columns the store carries, so a column the store
    does not have is selected as an empty one under its own name rather than costing the
    query every row it would have returned.
    '''
    if not does_table_exist_in_db(path, table):
        return []
    wanted = [name.strip() for name in columns.split(',')]
    present = _columns(path, table)
    if not present:
        return []
    selected = ', '.join(name if name in present else f'NULL AS {name}' for name in wanted)
    try:
        return list(get_sqlite_db_records(path, f'SELECT {selected} FROM {table} {where}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not read {table}: {error}')
        return []


def _address_book_join(store):
    '''{contact value row id: [address book row ids]} from the join table between them.

    The join table and its two columns are named for the numbers Core Data gave the two
    entities, and those numbers move between releases, so the table is looked up by shape
    rather than by a name typed here.
    '''
    query = ("SELECT name FROM sqlite_master WHERE type='table' "
             "AND name LIKE 'Z!_%CONTACTVALUES' ESCAPE '!'")
    try:
        tables = [str(row[0]) for row in get_sqlite_db_records(store, query)]
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'TextNow: could not list the join tables: {error}')
        return {}
    links = {}
    for table in tables:
        columns = sorted(_columns(store, table))
        contact = next((name for name in columns if 'ADDRESSBOOK' in name.upper()), '')
        value = next((name for name in columns if name != contact), '')
        if not contact or not value:
            continue
        for row in _rows(store, table, f'{contact}, {value}'):
            links.setdefault(row[1], []).append(row[0])
    return links


def _object_ids(store):
    '''(store UUID without hyphens, {entity number: entity name}) from the Core Data metadata.'''
    uuid = ''
    for row in _rows(store, 'Z_METADATA', 'Z_UUID'):
        uuid = re.sub(r'[^0-9A-Za-z]', '', _text(row[0]))
    entities = {row[0]: _text(row[1]) for row in _rows(store, 'Z_PRIMARYKEY', 'Z_ENT, Z_NAME')}
    return uuid, entities


def _object_name(object_ids, entity, row_id):
    '''The name the app's media cache gives a message's file, or ''.

    That name is the message's Core Data object identifier, x-coredata://<store UUID>/<entity>/p<row>,
    with everything but letters and digits removed.
    '''
    uuid, entities = object_ids
    name = entities.get(entity, '')
    if not uuid or not name or row_id is None:
        return ''
    return f'xcoredata{uuid}{name}p{row_id}'


def _picture(images, container, url, object_name=''):
    '''The cached copy of a picture a message points at, as a media reference, or ''.

    Two caches are read, and both name a file by something the store records, so the link
    is one the app made rather than a match on size or time. The image library's cache names
    the file for the MD5 of the address the picture was fetched from and is tried first. The
    app's own media cache names it for the message's Core Data object identifier and is used
    when the first has no file. The two hold different bytes for the same message, so the
    order decides which copy is shown. The bytes are sniffed before they are rendered and
    anything that is not an image is left alone.
    '''
    path = ''
    if url:
        digest = hashlib.md5(url.encode('utf8')).hexdigest()
        path = images.get((container, digest)) or images.get((container, digest + '.'))
    if not path and object_name:
        path = images.get(('', object_name))
    if not path:
        return ''
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError as error:
        logfunc(f'TextNow: could not read {path}: {error}')
        return ''
    if not head.startswith(_IMAGE_SIGNATURES):
        logfunc(f'TextNow: cached file for a message is not an image: {path}')
        return ''
    return check_in_media(path, os.path.basename(path))


def _self_address(store):
    '''The address the store marks as the account's own, or ''.'''
    for row in _rows(store, 'ZTMOCONTACTVALUE', 'ZCONTACTVALUE', 'WHERE ZCONTACTISSELF = 1'):
        if row[0]:
            return str(row[0])
    return ''


def _conversation_labels(store):
    '''{conversation row id: the name or address the conversation is with}.'''
    values = {row[0]: (_text(row[2]) or _text(row[1]))
              for row in _rows(store, 'ZTMOCONTACTVALUE', 'Z_PK, ZCONTACTVALUE, ZCONTACTNAME')}
    return {row[0]: values.get(row[1], '')
            for row in _rows(store, 'ZTMOCONVERSATION', 'Z_PK, ZCONTACTVALUE')}


def _direction(value):
    '''The app's stored direction as a word, or the value as stored.'''
    return {1: 'Incoming', 2: 'Outgoing'}.get(value, _text(value))


@artifact_processor
def textnow_ios_messages(context):
    '''Messages and their pictures from the TextNow account store.'''
    files_found, apps = _files(context)
    images = _cached_images(files_found)
    data_list, sources = [], []

    for container, store in _stores(files_found, apps):
        sources.append(store)
        labels = _conversation_labels(store)
        own = _self_address(store)
        object_ids = _object_ids(store)
        for row in _rows(store, 'ZTMOINTERACTION',
                         'ZLOCALTIMESTAMP, ZREMOTETIMESTAMP, ZDIRECTION, ZAUTHORNAME, '
                         'ZCONVERSATION, ZCONTENT, ZREAD, ZDELETEDSTATE, ZSTATUS1, '
                         'ZIMAGETYPE, ZTHUMBNAILWIDTH, ZTHUMBNAILHEIGHT, ZMESSAGEID, '
                         'ZORDERINGID, ZCALLID, Z_PK, Z_ENT',
                         'WHERE ZCALLID IS NULL'):
            (local, remote, direction, author, conversation, content, read, deleted, status,
             image_type, width, height, message_id, ordering, _, row_id, entity) = row
            message = _text(content)
            sender = _text(author)
            if not sender and direction == 2:
                sender = own
            data_list.append((
                _core_data_to_utc(local),
                _core_data_to_utc(remote),
                _direction(direction),
                sender,
                message,
                _picture(images, container, message if message.startswith('http') else '',
                         _object_name(object_ids, entity, row_id)),
                labels.get(conversation, ''),
                _text(read),
                _text(deleted),
                _text(status),
                _text(image_type),
                _number(width),
                _number(height),
                _text(message_id),
                _text(ordering),
                _text(row_id),
            ))

    data_headers = (
        ('Message Time', 'datetime'), ('Remote Time', 'datetime'), 'Direction', 'Sender',
        'Message', ('Picture', 'media'), 'Conversation', 'Read State (as stored)',
        'Deleted State (as stored)', 'Send Status (as stored)', 'Image Type (as stored)',
        'Thumbnail Width', 'Thumbnail Height', 'Message ID', 'Ordering ID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_calls(context):
    '''Calls from the TextNow account store, with the calling library's own record beside them.'''
    files_found, apps = _files(context)
    histories = _call_histories(files_found)
    data_list, sources = [], []

    for container, store in _stores(files_found, apps):
        sources.append(store)
        labels = _conversation_labels(store)
        history_path = histories.get(container, '')
        history = {}
        if history_path:
            sources.append(history_path)
            attributes = {}
            for event_id, key, value in _rows(history_path, 'EventAttributes',
                                              'eventId, key, value'):
                attributes.setdefault(event_id, {})[key] = value
            parties = {row[0]: row[1] for row in _rows(history_path, 'RemoteUsers',
                                                       'eventId, transportUri')}
            for event_id, stamp, direction, sender in _rows(
                    history_path, 'Events', 'eventId, timestamp, direction, sender'):
                history[f'{float(stamp):.6f}'] = {
                    'direction': direction, 'sender': sender,
                    'party': parties.get(event_id, ''), **attributes.get(event_id, {})}

        for row in _rows(store, 'ZTMOINTERACTION',
                         'ZLOCALTIMESTAMP, ZDIRECTION, ZLENGTH, ZCALLID, ZCONVERSATION, '
                         'ZSTATUS, Z_PK',
                         'WHERE ZCALLID IS NOT NULL'):
            local, direction, length, call_id, conversation, status, row_id = row
            match = _CALL_ID.match(_text(call_id))
            number, start = (match.group(1), match.group(2)) if match else ('', '')
            record = history.get(f'{float(start):.6f}', {}) if start else {}
            data_list.append((
                _core_data_to_utc(start) if start else '',
                _core_data_to_utc(local),
                _direction(direction),
                number,
                labels.get(conversation, ''),
                _number(length),
                _number(record.get('callDuration')),
                _text(record.get('callResult')),
                _text(record.get('dialAction')),
                _text(record.get('party')),
                _text(call_id),
                _text(record.get('callId')),
                _text(status),
                _text(row_id),
            ))

    data_headers = (
        ('Call Start', 'datetime'), ('Recorded At', 'datetime'), 'Direction',
        ('Number', 'phonenumber'), 'Conversation', 'Duration (Seconds)',
        'Call History Duration (Seconds)', 'Call History Result (as stored)',
        'Call History Dial Action', ('Call History Party', 'phonenumber'), 'Call ID',
        'Call History Call ID', 'Status (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_contacts(context):
    '''Contacts and addresses held in the TextNow account store.'''
    files_found, apps = _files(context)
    data_list, sources = [], []

    for _, store in _stores(files_found, apps):
        sources.append(store)
        labels = _conversation_labels(store)
        servers = {row[0]: (_text(row[1]), _text(row[2]))
                   for row in _rows(store, 'ZTMOSERVERCONTACT', 'Z_PK, ZNAME, ZPICTUREIMAGEKEY')}
        book = {row[0]: (_name(row[1], row[2]), _text(row[3]))
                for row in _rows(store, 'ZTMOABCONTACT',
                                 'Z_PK, ZFIRSTNAME, ZLASTNAME, ZCONTACTID')}
        linked = {value: [book.get(contact, ('', ''))[0] for contact in contacts]
                  for value, contacts in _address_book_join(store).items()}

        for row in _rows(store, 'ZTMOCONTACTVALUE',
                         'Z_PK, ZCONTACTVALUE, ZCONTACTNAME, ZCONTACTLABEL, ZCONTACTISSELF, '
                         'ZINNETWORK, ZSERVERCONTACT, ZCONVERSATION'):
            (row_id, value, name, label, is_self, in_network, server, conversation) = row
            server_name, server_picture = servers.get(server, ('', ''))
            data_list.append((
                _text(value),
                _text(name),
                ', '.join(n for n in linked.get(row_id, []) if n),
                _text(label),
                'Yes' if is_self == 1 else 'No',
                _text(in_network),
                server_name,
                server_picture,
                labels.get(conversation, ''),
                _text(row_id),
            ))

    data_headers = (
        'Contact Value', 'Contact Name', 'Address Book Name', 'Label', 'Account Own Address',
        'In Network (as stored)', 'Service Contact Name', 'Service Contact Picture Key',
        'Conversation', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def textnow_ios_account(context):
    '''The account the TextNow store belongs to.'''
    files_found, apps = _files(context)
    data_list, sources = [], []

    for _, store in _stores(files_found, apps):
        sources.append(store)
        for row in _rows(store, 'ZTMOACCOUNTINFO',
                         'ZUSERNAME, ZPHONENUMBER, ZEMAIL, ZFIRSTNAME, ZLASTNAME, '
                         'ZACCOUNTSTATUS, ZEMAILVERIFIED, ZUSERID, ZUSERIDHEX, ZSIPUSERNAME, '
                         'ZSIPHOST, ZSIPCLIENTIP, ZCREDITS, ZTEXTNOWCREDIT, ZCURRENCY, '
                         'ZISUNLIMITED, ZSHOWADS, ZLOCALTIMESTAMP, ZREMOTETIMESTAMP, '
                         'ZLASTWALLETUPDATETIMESTAMP, ZADREMOVALEXPIRYDATE, ZSIPPASSWORD'):
            (username, number, email, first, last, status, verified, user_id, user_id_hex,
             sip_user, sip_host, sip_ip, credit_count, textnow_credit, currency, unlimited,
             show_ads, local, remote, wallet, ad_expiry, sip_password) = row
            data_list.append((
                _core_data_to_utc(local),
                _core_data_to_utc(remote),
                _core_data_to_utc(wallet),
                _core_data_to_utc(ad_expiry),
                _text(username),
                _text(number),
                _text(email),
                _name(first, last),
                _text(status),
                verified,
                _text(user_id),
                _text(user_id_hex),
                _text(sip_user),
                _text(sip_host),
                _text(sip_ip),
                'Yes' if sip_password else 'No',
                _text(credit_count),
                _text(textnow_credit),
                _text(currency),
                _text(unlimited),
                _text(show_ads),
            ))

    data_headers = (
        ('Record Updated', 'datetime'), ('Server Record Time', 'datetime'),
        ('Wallet Updated', 'datetime'), ('Ad Removal Expiry', 'datetime'), 'Username',
        ('TextNow Number', 'phonenumber'), 'Email', 'Name', 'Account Status',
        'Email Verified (as stored)', 'User ID', 'User ID (Hex)', 'SIP Username', 'SIP Host',
        'SIP Client IP', 'SIP Password Stored', 'Credits', 'TextNow Credit', 'Currency',
        'Unlimited (as stored)', 'Show Ads (as stored)')
    return data_headers, data_list, '\n'.join(sources)
