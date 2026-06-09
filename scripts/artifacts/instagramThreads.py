__artifacts_v2__ = {
    "get_instagramThreads": {
        "name": "Instagram Threads",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "senderColumn": "Username",
                "directionColumn": "Viewer ID equals Sender PK",
                "directionSentValue": 1,
                "timeColumn": "Timestamp (UTC)"
            }
        },
        "description": "Existing messages sent and received in the Instagram App.",
        "author": "@AlexisBrignoni",
        "version": "0.7",
        "creation_date": "2021-03-09",
        "last_update_date": "2026-06-05",
        "requirements": "",
        "category": "Instagram",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*"
        ),
        "output_types": "standard",
        "artifact_icon": "instagram",
    },
    "get_instagram_calls": {
        "name": "Instagram Threads Calls",
        "description": "Existing calls sent and received in the Instagram App.",
        "author": "@AlexisBrignoni",
        "version": "0.7",
        "creation_date": "2021-03-09",
        "last_update_date": "2026-06-05",
        "requirements": "",
        "category": "Instagram",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*"
        ),
        "output_types": "standard",
        "artifact_icon": "phone",
    },
}

from scripts.ilapfuncs import (artifact_processor, convert_plist_date_to_utc, get_plist_content,
                               get_sqlite_db_records, logfunc)


@artifact_processor
def get_instagramThreads(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith("wal") and not x.endswith("shm")]
    query = """
        SELECT
        METADATA
        FROM THREADS
    """

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    userdict = {}
    for row in db_records:
        plist = get_plist_content(row[0])

        for _i in plist["NSArray<IGUser *>*users"]:
            for x, _y in enumerate(plist["NSArray<IGUser *>*users"]):
                if plist["NSArray<IGUser *>*users"][x].get("NSDictionary<NSString *, id>*userDict", {}).get("pk"):
                    user_pk = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["pk"]
                elif plist["NSArray<IGUser *>*users"][x].get("pk"):
                    user_pk = plist["NSArray<IGUser *>*users"][x]["pk"]
                else:
                    user_pk = None

                if plist["NSArray<IGUser *>*users"][x].get("NSDictionary<NSString *, id>*userDict", {}).get("full_name"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["full_name"]
                elif plist["NSArray<IGUser *>*users"][x].get("fullName"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["fullName"]
                elif plist["NSArray<IGUser *>*users"][x].get("userName"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["userName"]
                else:
                    user_full = None
                userdict[user_pk] = user_full

        if plist.get("IGUser*inviter_DEPRECATED", {}).get("NSDictionary<NSString *, id>*userDict", {}).get("pk"):
            inviter_pk = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["pk"]
        elif plist["IGUser*inviter"].get("pk"):
            inviter_pk = plist["IGUser*inviter"]["pk"]
        else:
            inviter_pk = None

        if plist.get("IGUser*inviter_DEPRECATED", {}).get("NSDictionary<NSString *, id>*userDict", {}).get("full_name"):
            inviter_full = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["full_name"]
        elif plist["IGUser*inviter"].get("fullName"):
            inviter_full = plist["IGUser*inviter"]["fullName"]
        else:
            inviter_full = None
        userdict[inviter_pk] = inviter_full

    query_2 = """
        SELECT
        MESSAGES.MESSAGE_ID,
        MESSAGES.THREAD_ID,
        MESSAGES.ARCHIVE,
        THREADS.VIEWER_ID
        FROM MESSAGES, THREADS
        WHERE MESSAGES.THREAD_ID = THREADS.THREAD_ID
    """

    db_records_2 = get_sqlite_db_records(str(files_found[0]), query_2)
    for row in db_records_2:
        plist = get_plist_content(row[2])

        sender_pk = ""
        server_timestamp = ""
        thread_id = ""
        message = ""
        video_chat_title = ""
        video_chat_call_id = ""
        dm_reaction = ""
        reaction_server_timestamp = ""
        reaction_user_id = ""
        shared_media_id = ""
        shared_media_url = ""
        shared_media_url_expiration_date = ""
        was_sent = None

        # Messages
        sender_pk = plist["IGDirectPublishedMessageMetadata*metadata"]["NSString*senderPk"]
        # Calculating directionColumn for LAVA Coversations View
        if int(sender_pk) == int(row[3]):
            was_sent = 1
        else:
            was_sent = 0

        thread_id = plist["IGDirectPublishedMessageMetadata*metadata"]["NSString*threadId"]
        server_timestamp = plist["IGDirectPublishedMessageMetadata*metadata"]["NSDate*serverTimestamp"]
        server_timestamp = convert_plist_date_to_utc(server_timestamp)
        message = plist["IGDirectPublishedMessageContent*content"].get("NSString*string")

        # VOIP calls
        if plist["IGDirectPublishedMessageContent*content"].get("IGDirectThreadActivityAnnouncement*threadActivity") is not None:
            video_chat_title = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*voipTitle")
            video_chat_call_id = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*videoCallId")

        # Reactions
        reactions = plist["NSArray<IGDirectMessageReaction *>*reactions"]
        if reactions:
            dm_reaction = reactions[0].get("emojiUnicode")
            reaction_server_timestamp = reactions[0].get("serverTimestamp")
            reaction_server_timestamp = convert_plist_date_to_utc(reaction_server_timestamp)
            reaction_user_id = reactions[0].get("userId")

        # Shared media
        if plist["IGDirectPublishedMessageContent*content"].get("IGDirectPublishedMessageMedia*media"):
            try:
                shared_media_id = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["kIGPhotoMediaID"]
            except (KeyError, ValueError, TypeError, OSError, OverflowError) as e:
                logfunc(f"Error: {str(e)}")
                shared_media_id = None

            try:
                shared_media_url = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["imageVersions"][0]["url"]["NS.relative"]
            except (KeyError, ValueError, TypeError, OSError, OverflowError) as e:
                logfunc(f"Error: {str(e)}")
                shared_media_url = None

            try:
                shared_media_url_expiration_date = plist["IGDirectPublishedMessageContent*content"]["IGDirectPublishedMessageMedia*media"]["IGDirectPublishedMessagePermanentMedia*permanentMedia"]["IGPhoto*photo"]["imageVersions"][0]["expiration_date"]
                shared_media_url_expiration_date = convert_plist_date_to_utc(shared_media_url_expiration_date)
            except (KeyError, ValueError, TypeError, OSError, OverflowError) as e:
                logfunc(f"Error: {str(e)}")
                shared_media_url_expiration_date = None

        if sender_pk in userdict:
            user = userdict[sender_pk]
        else:
            user = ""

        data_list.append(
            (
                server_timestamp,
                sender_pk,
                user,
                message,
                thread_id,
                video_chat_title,
                video_chat_call_id,
                dm_reaction,
                reaction_server_timestamp,
                reaction_user_id,
                shared_media_id,
                shared_media_url,
                shared_media_url_expiration_date,
                was_sent,
            )
        )

    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        "Sender ID",
        "Username",
        "Message",
        "Thread ID",
        "Video Chat Title",
        "Video Chat ID",
        "DM Reaction",
        "DM Reaction Server Timestamp",
        "Reaction User ID",
        "Shared Media ID",
        "Shared Media URL",
        ("Shared Media URL Expiration Date", "datetime"),
        "Viewer ID equals Sender PK",
    )

    return data_headers, data_list, files_found[0]


@artifact_processor
def get_instagram_calls(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith("wal") and not x.endswith("shm")]
    query = """
        SELECT
        METADATA
        FROM THREADS
    """

    db_records = get_sqlite_db_records(str(files_found[0]), query)
    data_list = []
    userdict = {}
    for row in db_records:
        plist = get_plist_content(row[0])

        for _i in plist["NSArray<IGUser *>*users"]:
            for x, _y in enumerate(plist["NSArray<IGUser *>*users"]):
                if plist["NSArray<IGUser *>*users"][x].get("NSDictionary<NSString *, id>*userDict", {}).get("pk"):
                    user_pk = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["pk"]
                elif plist["NSArray<IGUser *>*users"][x].get("pk"):
                    user_pk = plist["NSArray<IGUser *>*users"][x]["pk"]
                else:
                    user_pk = None

                if plist["NSArray<IGUser *>*users"][x].get("NSDictionary<NSString *, id>*userDict", {}).get("full_name"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["NSDictionary<NSString *, id>*userDict"]["full_name"]
                elif plist["NSArray<IGUser *>*users"][x].get("fullName"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["fullName"]
                elif plist["NSArray<IGUser *>*users"][x].get("userName"):
                    user_full = plist["NSArray<IGUser *>*users"][x]["userName"]
                else:
                    user_full = None
                userdict[user_pk] = user_full

        if plist.get("IGUser*inviter_DEPRECATED", {}).get("NSDictionary<NSString *, id>*userDict", {}).get("pk"):
            inviter_pk = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["pk"]
        elif plist["IGUser*inviter"].get("pk"):
            inviter_pk = plist["IGUser*inviter"]["pk"]
        else:
            inviter_pk = None

        if plist.get("IGUser*inviter_DEPRECATED", {}).get("NSDictionary<NSString *, id>*userDict", {}).get("full_name"):
            inviter_full = plist["IGUser*inviter_DEPRECATED"]["NSDictionary<NSString *, id>*userDict"]["full_name"]
        elif plist["IGUser*inviter"].get("fullName"):
            inviter_full = plist["IGUser*inviter"]["fullName"]
        else:
            inviter_full = None
        userdict[inviter_pk] = inviter_full

    query_2 = """
    SELECT
    MESSAGES.MESSAGE_ID,
    MESSAGES.THREAD_ID,
    MESSAGES.ARCHIVE,
    THREADS.VIEWER_ID
    FROM MESSAGES, THREADS
    WHERE MESSAGES.THREAD_ID = THREADS.THREAD_ID
"""

    db_records_2 = get_sqlite_db_records(str(files_found[0]), query_2)
    for row in db_records_2:
        plist = get_plist_content(row[2])
        sender_pk = ""
        server_timestamp = ""
        video_chat_title = ""
        video_chat_call_id = ""

        # Messages
        sender_pk = plist["IGDirectPublishedMessageMetadata*metadata"]["NSString*senderPk"]
        server_timestamp = plist["IGDirectPublishedMessageMetadata*metadata"]["NSDate*serverTimestamp"]
        server_timestamp = convert_plist_date_to_utc(server_timestamp)

        # VOIP calls
        if plist["IGDirectPublishedMessageContent*content"].get("IGDirectThreadActivityAnnouncement*threadActivity") is not None:
            video_chat_title = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*voipTitle")
            video_chat_call_id = plist["IGDirectPublishedMessageContent*content"]["IGDirectThreadActivityAnnouncement*threadActivity"].get("NSString*videoCallId")

        if sender_pk in userdict:
            user = userdict[sender_pk]
        else:
            user = ""

        if video_chat_title:
            data_list.append(
                (
                    server_timestamp,
                    sender_pk,
                    user,
                    video_chat_title,
                    video_chat_call_id,
                )
            )

    data_headers = (
        ("Timestamp", "datetime"),
        "Sender ID",
        "Username",
        "Video Chat Title",
        "Video Chat ID",
    )

    return data_headers, data_list, files_found[0]
