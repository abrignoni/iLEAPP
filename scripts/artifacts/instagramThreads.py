""" instagramThreads """
__artifacts_v2__ = {
    "instagram_threads": {
        "name": "Instagram Threads",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "senderColumn": "Username",
                "directionColumn": "Viewer ID equals Sender PK",
                "directionSentValue": 1,
                "timeColumn": "Timestamp"
            }
        },
        "description": "Existing messages sent and received in the Instagram App.",
        "author": "@AlexisBrignoni",
        "creation_date": "2021-03-09",
        "last_update_date": "2026-06-05",
        "requirements": "",
        "category": "Instagram",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "brand-instagram",
        "sample_data": {
            "josh_ios_15": "75 rows; includes messages, VOIP call activity, and conversation view fields",
            "mvs_2026": "0 rows; verifies multi-DB handling with no matching thread records",
            "ctf2020_ios12": "iOS 12.4 | com.burbn.instagram | 1 row",
            "dexter_ios18": "iOS 18.3.2 | Instagram 400.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Instagram 282.0 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | Instagram 425.0.0 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | Instagram 341.0.1 | 42 rows",
            "iphone12_ios18": "iOS 18.7 | Instagram 408.0.0 | 20 rows",
            "iphone14plus_ios18": "iOS 18.0 | Instagram 409.1.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Instagram 344.0.9 | 11 rows",
        },
    },
    "instagram_calls": {
        "name": "Instagram Threads Calls",
        "description": "Existing calls sent and received in the Instagram App.",
        "author": "@AlexisBrignoni",
        "creation_date": "2021-03-09",
        "last_update_date": "2026-06-05",
        "requirements": "",
        "category": "Instagram",
        "notes": "",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "josh_ios_15": "25 rows; VOIP call activity extracted from Threads messages",
            "mvs_2026": "0 rows; verifies multi-DB handling with no matching call records",
            "ctf2020_ios12": "iOS 12.4 | com.burbn.instagram | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Instagram 400.0.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Instagram 282.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Instagram 425.0.0 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Instagram 341.0.1 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | Instagram 408.0.0 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | Instagram 409.1.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Instagram 344.0.9 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import (
    artifact_processor,
    convert_plist_date_to_utc,
    get_plist_content,
    get_sqlite_db_records,
)

from datetime import datetime as _dt

def _safe_plist_date(value):
    """Convert plist <date> objects to UTC; pass strings/None through unchanged."""
    return convert_plist_date_to_utc(value) if isinstance(value, _dt) else value



def _database_files(context):
    return [
        str(file_found)
        for file_found in context.get_files_found()
        if not str(file_found).endswith(("wal", "shm"))
    ]


def _source_path(context, files_found):
    if not files_found:
        return ''
    return '\n'.join(context.get_relative_path(file_found) for file_found in files_found)


def _add_user(userdict, user):
    if not isinstance(user, dict):
        return

    user_data = user.get("NSDictionary<NSString *, id>*userDict", {})
    user_pk = user_data.get("pk") or user.get("pk")
    if not user_pk:
        return

    user_full = (
        user_data.get("full_name")
        or user.get("fullName")
        or user.get("userName")
    )
    userdict[user_pk] = user_full


def _build_userdict(db_records):
    userdict = {}
    for row in db_records:
        plist = get_plist_content(row[0])
        if not isinstance(plist, dict):
            continue

        for user in plist.get("NSArray<IGUser *>*users", []):
            _add_user(userdict, user)

        inviter = plist.get("IGUser*inviter_DEPRECATED") or plist.get("IGUser*inviter")
        _add_user(userdict, inviter)

    return userdict


def _nested_get(value, *keys):
    for key in keys:
        try:
            value = value[key]
        except (IndexError, KeyError, TypeError):
            return None
    return value


@artifact_processor
def instagram_threads(context):
    """ see artifact description """
    files_found = _database_files(context)
    source_path = _source_path(context, files_found)
    query = """
        SELECT
        METADATA
        FROM THREADS
    """

    query_2 = """
        SELECT
        MESSAGES.MESSAGE_ID,
        MESSAGES.THREAD_ID,
        MESSAGES.ARCHIVE,
        THREADS.VIEWER_ID
        FROM MESSAGES, THREADS
        WHERE MESSAGES.THREAD_ID = THREADS.THREAD_ID
    """

    data_list = []
    for file_found in files_found:
        db_records = get_sqlite_db_records(file_found, query)
        userdict = _build_userdict(db_records)
        db_records_2 = get_sqlite_db_records(file_found, query_2)

        for row in db_records_2:
            plist = get_plist_content(row[2])
            if not isinstance(plist, dict):
                continue

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
            metadata = plist["IGDirectPublishedMessageMetadata*metadata"]
            content = plist["IGDirectPublishedMessageContent*content"]
            sender_pk = metadata["NSString*senderPk"]
            # Calculating directionColumn for LAVA Coversations View
            if int(sender_pk) == int(row[3]):
                was_sent = 1
            else:
                was_sent = 0

            thread_id = metadata["NSString*threadId"]
            server_timestamp = metadata["NSDate*serverTimestamp"]
            server_timestamp = _safe_plist_date(server_timestamp)
            message = content.get("NSString*string")

            # VOIP calls
            thread_activity = content.get("IGDirectThreadActivityAnnouncement*threadActivity")
            if thread_activity is not None:
                video_chat_title = thread_activity.get("NSString*voipTitle")
                video_chat_call_id = thread_activity.get("NSString*videoCallId")

            # Reactions
            reactions = plist["NSArray<IGDirectMessageReaction *>*reactions"]
            if reactions:
                dm_reaction = reactions[0].get("emojiUnicode")
                reaction_server_timestamp = reactions[0].get("serverTimestamp")
                reaction_server_timestamp = _safe_plist_date(reaction_server_timestamp)
                reaction_user_id = reactions[0].get("userId")

            # Shared media
            media = content.get("IGDirectPublishedMessageMedia*media")
            if media:
                shared_media_id = _nested_get(
                    media,
                    "IGDirectPublishedMessagePermanentMedia*permanentMedia",
                    "IGPhoto*photo",
                    "kIGPhotoMediaID",
                )
                shared_media_url = _nested_get(
                    media,
                    "IGDirectPublishedMessagePermanentMedia*permanentMedia",
                    "IGPhoto*photo",
                    "imageVersions",
                    0,
                    "url",
                    "NS.relative",
                )
                shared_media_url_expiration_date = _nested_get(
                    media,
                    "IGDirectPublishedMessagePermanentMedia*permanentMedia",
                    "IGPhoto*photo",
                    "imageVersions",
                    0,
                    "expiration_date",
                )
                shared_media_url_expiration_date = _safe_plist_date(
                    shared_media_url_expiration_date
                )

            user = userdict.get(sender_pk, "")

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
        ("Timestamp", "datetime"),
        "Sender ID",
        "Username",
        "Message",
        "Thread ID",
        "Video Chat Title",
        "Video Chat ID",
        "DM Reaction",
        ("DM Reaction Server Timestamp", "datetime"),
        "Reaction User ID",
        "Shared Media ID",
        "Shared Media URL",
        ("Shared Media URL Expiration Date", "datetime"),
        "Viewer ID equals Sender PK",
    )

    return data_headers, data_list, source_path


@artifact_processor
def instagram_calls(context):
    """ see artifact description """
    files_found = _database_files(context)
    source_path = _source_path(context, files_found)
    query = """
        SELECT
        METADATA
        FROM THREADS
    """

    query_2 = """
        SELECT
        MESSAGES.MESSAGE_ID,
        MESSAGES.THREAD_ID,
        MESSAGES.ARCHIVE,
        THREADS.VIEWER_ID
        FROM MESSAGES, THREADS
        WHERE MESSAGES.THREAD_ID = THREADS.THREAD_ID
    """

    data_list = []
    for file_found in files_found:
        db_records = get_sqlite_db_records(file_found, query)
        userdict = _build_userdict(db_records)
        db_records_2 = get_sqlite_db_records(file_found, query_2)

        for row in db_records_2:
            plist = get_plist_content(row[2])
            if not isinstance(plist, dict):
                continue

            sender_pk = ""
            server_timestamp = ""
            video_chat_title = ""
            video_chat_call_id = ""

            # Messages
            metadata = plist["IGDirectPublishedMessageMetadata*metadata"]
            content = plist["IGDirectPublishedMessageContent*content"]
            sender_pk = metadata["NSString*senderPk"]
            server_timestamp = metadata["NSDate*serverTimestamp"]
            server_timestamp = _safe_plist_date(server_timestamp)

            # VOIP calls
            thread_activity = content.get("IGDirectThreadActivityAnnouncement*threadActivity")
            if thread_activity is not None:
                video_chat_title = thread_activity.get("NSString*voipTitle")
                video_chat_call_id = thread_activity.get("NSString*videoCallId")

            user = userdict.get(sender_pk, "")

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

    return data_headers, data_list, source_path
