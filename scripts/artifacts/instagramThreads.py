__artifacts_v2__ = {
    "get_instagramThreads": {
        "name": "Instagram Threads",
        "description": "Existing messages sent and received in the Instagram App.",
        "author": "Alexis Brignoni",
        "version": "0.7",
        "creation_date": "2021-03-09",
        "last_update_date": "2026-04-23",
        "requirements": "",
        "category": "Instagram",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*"
        ),
        "output_types": ["html", "tsv", "timeline"],
        "artifact_icon": "instagram",
    }
}

import biplist
import io
import plistlib
import sys

import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_instagramThreads(
    files_found, report_folder, seeker, wrap_text, timezone_offset
):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith(".db"):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute("""
    select
    metadata
    from threads
    """)

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    fila = 0
    userdict = {}
    data_list = []
    video_calls = []

    if usageentries > 0:
        for row in all_rows:
            plist = ""
            plist_file_object = io.BytesIO(row[0])
            if row[0].find(b"NSKeyedArchiver") == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)
                except (
                    nd.DeserializeError,
                    nd.biplist.NotBinaryPlistException,
                    nd.biplist.InvalidPlistException,
                    nd.plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError,
                    ValueError,
                    TypeError,
                    OSError,
                    OverflowError,
                ) as ex:
                    logfunc(f"Failed to read plist for {row[0]}, error was:" + str(ex))

            for i in plist["NSArray<IGUser *>*users"]:
                for x, y in enumerate(plist["NSArray<IGUser *>*users"]):
                    userPk = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["pk"]
                    userFull = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["full_name"]
                    userdict[userPk] = userFull

            # DEPRECATED?
            inviterPk = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["pk"]
            inviterFull = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["full_name"]
            userdict[inviterPk] = inviterFull

    cursor.execute("""
    select
    messages.message_id,
    messages.thread_id,
    messages.archive,
    threads.metadata,
    threads.thread_messages_range,
    threads.visual_message_info
    from messages, threads
    where messages.thread_id = threads.thread_id
    """)

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    if usageentries > 0:
        for row in all_rows:
            plist = ""
            senderpk = ""
            serverTimestamp = ""
            message = ""
            videoChatTitle = ""
            videoChatCallID = ""
            dmreaction = ""
            reactionServerTimestamp = ""
            reactionUserID = ""
            sharedMediaID = ""
            sharedMediaURL = ""
            shared_media_url_expiration_date = ""

            plist_file_object = io.BytesIO(row[2])
            if row[2].find(b"NSKeyedArchiver") == -1:
                if sys.version_info >= (3, 9):
                    plist = plistlib.load(plist_file_object)
                else:
                    plist = biplist.readPlist(plist_file_object)
            else:
                try:
                    plist = nd.deserialize_plist(plist_file_object)
                except (
                    nd.DeserializeError,
                    nd.biplist.NotBinaryPlistException,
                    nd.biplist.InvalidPlistException,
                    nd.plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError,
                    ValueError,
                    TypeError,
                    OSError,
                    OverflowError,
                ) as ex:
                    logfunc(f"Failed to read plist for {row[2]}, error was:" + str(ex))

            # Messages
            senderpk = plist["IGDirectPublishedMessageMetadata*metadata"]["NSString*senderPk"]
            serverTimestamp = plist["IGDirectPublishedMessageMetadata*metadata"]["NSDate*serverTimestamp"]
            message = plist["IGDirectPublishedMessageContent*content"].get("NSString*string")

            # VOIP calls
            if (plist["IGDirectPublishedMessageContent*content"].get("IGDirectThreadActivityAnnouncement*threadActivity") is not None):
                videoChatTitle = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*voipTitle")
                videoChatCallID = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*videoCallId")

            # Reactions
            reactions = plist["NSArray<IGDirectMessageReaction *>*reactions"]
            if reactions:
                dmreaction = reactions[0].get("emojiUnicode")
                reactionServerTimestamp = reactions[0].get("serverTimestamp")
                reactionUserID = reactions[0].get("userId")

            # Shared media
            if plist["IGDirectPublishedMessageContent*content"].get("IGDirectPublishedMessageMedia*media"):
                try:
                    sharedMediaID = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["kIGPhotoMediaID"]
                except (KeyError, ValueError, TypeError, OSError, OverflowError) as ex:
                    print("Had exception: " + str(ex))
                    sharedMediaID = None

                try:
                    sharedMediaURL = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["imageVersions"][0]["url"]["NS.relative"]
                except (KeyError, ValueError, TypeError, OSError, OverflowError) as ex:
                    print("Had exception: " + str(ex))
                    sharedMediaURL = None

                try:
                    shared_media_url_expiration_date = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["imageVersions"][0]["expiration_date"]
                except (KeyError, ValueError, TypeError, OSError, OverflowError) as ex:
                    print("Had exception: " + str(ex))
                    shared_media_url_expiration_date = None

            if senderpk in userdict:
                user = userdict[senderpk]
            else:
                user = ""

            data_list.append(
                (
                    serverTimestamp,
                    senderpk,
                    user,
                    message,
                    videoChatTitle,
                    videoChatCallID,
                    dmreaction,
                    reactionServerTimestamp,
                    reactionUserID,
                    sharedMediaID,
                    sharedMediaURL,
                    shared_media_url_expiration_date,
                )
            )
            if videoChatTitle:
                video_calls.append(
                    (serverTimestamp, senderpk, user, videoChatTitle, videoChatCallID)
                )

        data_headers = (
            "Timestamp (UTC)",
            "Sender ID",
            "Username",
            "Message",
            "Video Chat Title",
            "Video Chat ID",
            "DM Reaction",
            "DM Reaction Server Timestamp",
            "Reaction User ID",
            "Shared Media ID",
            "Shared Media URL",
            "Shared Media URL Expiration Date"
        )
        return data_headers, data_list, file_found

    if len(video_calls) > 0:
        data_headersv = (
            "Timestamp",
            "Sender ID",
            "Username",
            "Video Chat Title",
            "Video Chat ID",
        )
        return data_headersv, video_calls, file_found

    db.close()
