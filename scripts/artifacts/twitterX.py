__artifacts_v2__ = {
    'twitterDirectMessages': {
        'name': 'Twitter X - Direct Messages',
        'description': 'Direct message conversations cached by the Twitter X application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-11-17',
        'requirements': 'none',
        'category': 'Social Media',
        'notes': 'The direct message cache is an NSKeyedArchiver archive of the app inbox; it '
                 'holds the trusted, untrusted and low quality timelines, and the Timeline column '
                 'names which of those three archive keys a conversation came from. From Me is '
                 'computed by this module: 1 when the entry\'s sender user id equals the user id '
                 'in the archive\'s inbox context, and 0 in every other case, including an entry '
                 'with no sender id. On the iOS 26.5.2 image (X 12.32.1) the archive holds no '
                 'conversations, and the app group also holds a SQLite store at '
                 'com.atebits.tweetie.databases/v1/<id>/<id>-dmv2.db, which is not read here. Its '
                 'dm_conversation, dm_entry and dm_user tables held no rows in any of the 6 states read '
                 'from it and its write-ahead log there.',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.atebits.tweetie.direct-message.cache/*',),
        'output_types': 'standard',
        'artifact_icon': 'message',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 72 rows across 4 conversations',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | X 12.32.1 | 0 rows, the archive holds no conversations',
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 0 rows, store absent',
        },
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Conversation ID',
                'conversationLabelColumn': 'Conversation',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender',
            }
        }
    },
    'twitterDMUsers': {
        'name': 'Twitter X - Direct Message Users',
        'description': 'Twitter X accounts cached alongside the direct message inbox',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-11-17',
        'requirements': 'none',
        'category': 'Social Media',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.atebits.tweetie.direct-message.cache/*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 5 rows',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | X 12.32.1 | 0 rows, the archive holds no users',
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 0 rows, store absent',
        },
    },
    'twitterTweets': {
        'name': 'Twitter X - Cached Posts',
        'description': 'Posts (tweets) cached in the Twitter X model cache database',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-11-17',
        'requirements': 'none',
        'category': 'Social Media',
        'notes': ('Cached objects are gzip compressed JSON stored in the Items table. A key with '
                  'no stored object, or one that does not decode, gives no row and is counted in '
                  'the run log, which names the cache. '
                  'Every modelCache.sqlite3 is read. On the sample images each one sits in its own '
                  'folder under TFSModelCache.1/. On both images that hold the store one folder '
                  'is named <username>-<number>, where the username is the signed-in account\'s; '
                  'what the number means is not established. On the iOS 26.5.2 image (X 12.32.1) '
                  'two more are named - app - and - guest -, and they held no keys there. Only '
                  'the first match used to be read, and on that image it was an empty one, so '
                  'the artifact reported no rows. Account Cache names the folder a row came '
                  'from. The two sample images that hold the store (iphone11_ios17, '
                  'wilkerson_iphone16_ios26) each have one account cache with keys, so Account '
                  'Cache held one value on every row there. A device with two signed-in '
                  'accounts was not available.'),
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'brand-twitter',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 520 rows',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | X 12.32.1 | 17795 rows',
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 0 rows, store absent',
        },
    },
    'twitterCachedUsers': {
        'name': 'Twitter X - Cached Users',
        'description': 'User profiles cached in the Twitter X model cache database',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-11-18',
        'requirements': 'none',
        'category': 'Social Media',
        'notes': ('Every modelCache.sqlite3 is read. On the sample images each one sits in its own '
                  'folder under TFSModelCache.1/. On both images that hold the store one folder '
                  'is named <username>-<number>, where the username is the signed-in account\'s; '
                  'what the number means is not established. On the iOS 26.5.2 image (X 12.32.1) '
                  'two more are named - app - and - guest -, and they held no keys there. Only '
                  'the first match used to be read, and on that image it was an empty one, so '
                  'the artifact reported no rows. Account Cache names the folder a row came '
                  'from. The two sample images that hold the store (iphone11_ios17, '
                  'wilkerson_iphone16_ios26) each have one account cache with keys, so Account '
                  'Cache held one value on every row there. A device with two signed-in '
                  'accounts was not available.'
                  ' Cache Updated is blank where updatedTimestamp holds -63114076800, the value '
                  'of NSDate.distantPast: 23 of 5,318 rows on the iOS 26.5.2 image and none on '
                  'iphone11_ios17. Foundation shows that value as 0001-01-01 00:00:00 UTC; in '
                  'Python\'s calendar it is 0000-12-30, two days before the earliest date Python '
                  'can hold. What the app means by it is not established. 63113904000 '
                  '(NSDate.distantFuture) is blank too, and so would be a real date of exactly '
                  '4001-01-01 00:00:00 UTC, which is stored as the same number.'),
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 306 rows',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | X 12.32.1 | 5318 rows',
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 0 rows, store absent',
        },
    },
    'twitterNotifications': {
        'name': 'Twitter X - Notifications',
        'description': 'In-app notifications cached by the Twitter X application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-11-17',
        'requirements': 'none',
        'category': 'Social Media',
        'notes': ('From Users holds the user IDs a notification names, as stored in its fromUsers list; usernames are not looked up. On the josh_ios17_ffs test case 116 of 119 notifications name one user and 3 name none. '
                  'Every modelCache.sqlite3 is read. On the sample images each one sits in its own '
                  'folder under TFSModelCache.1/. On both images that hold the store one folder '
                  'is named <username>-<number>, where the username is the signed-in account\'s; '
                  'what the number means is not established. On the iOS 26.5.2 image (X 12.32.1) '
                  'two more are named - app - and - guest -, and they held no keys there. Only '
                  'the first match used to be read, and on that image it was an empty one, so '
                  'the artifact reported no rows. Account Cache names the folder a row came '
                  'from. The two sample images that hold the store (iphone11_ios17, '
                  'wilkerson_iphone16_ios26) each have one account cache with keys, so Account '
                  'Cache held one value on every row there. A device with two signed-in '
                  'accounts was not available.'),
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'bell',
        'sample_data': {
            'iphone11_ios17': 'iOS 17.3 | 119 rows',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | X 12.32.1 | 1064 rows',
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 0 rows, store absent',
        },
    },
}

import gzip
import json
import os
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, logfunc, \
    get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc, \
    convert_unix_ts_to_utc

# The three inbox timelines the app keeps. Per X's message-request behavior as
# observed in testing, conversations that were never accepted land in the
# untrusted or low quality lists rather than the main one.
INBOX_TIMELINES = (
    ('trusted_conversations_timeline', 'Trusted'),
    ('untrusted_conversations_timeline', 'Untrusted'),
    ('low_quality_conversations_timeline', 'Low Quality'),
)

# Item key format in modelCache.sqlite3 is "<uid>|<modelType>|Twitter".
MODEL_TYPE_STATUS = 'TwitterStatus'
MODEL_TYPE_USER = 'TwitterMasterUser'
MODEL_TYPE_NOTIFICATION = 'URTNotification'


def _dm_cache_paths(context):
    """Every direct message archive collected, one per signed-in account.

    The cache directory also picks up sidecar files (WAL/journal style leftovers
    and hidden entries), so only real NSKeyedArchiver plists are returned.
    """
    paths = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(file_found).startswith('.'):
            continue
        try:
            with open(file_found, 'rb') as handle:
                if handle.read(8) != b'bplist00':
                    continue
        except OSError:
            continue
        paths.append(file_found)
    return paths


def _load_dm_cache(source_path):
    """Deserialize the direct message NSKeyedArchiver cache."""
    try:
        # deserialize_plist(path) opens the file and never closes it.
        with open(source_path, 'rb') as cache_file:
            return nd.deserialize_plist_from_string(cache_file.read())
    except (nd.DeserializeError, ValueError, TypeError, OSError) as ex:
        logfunc(f'Could not deserialize Twitter X direct message cache: {ex}')
        return None


def _user_label(user):
    """Format a cached DM user as 'Full Name (@username)'."""
    if not isinstance(user, dict):
        return ''
    username = user.get('username') or ''
    full_name = user.get('fullName') or ''
    if full_name and username:
        return f'{full_name} (@{username})'
    return f'@{username}' if username else full_name


def _conversation_participants(conversation):
    """Return the participatingUser dicts of a conversation.

    The archive stores the participant set as an NSMutableSet, which the
    deserializer renders as a dict of NS.object.<n> keys.
    """
    participants = conversation.get('participants')
    if isinstance(participants, dict):
        values = participants.values()
    elif isinstance(participants, list):
        values = participants
    else:
        return []
    return [v.get('participatingUser') for v in values
            if isinstance(v, dict) and isinstance(v.get('participatingUser'), dict)]


def _attachment_urls(entry):
    """Return the media URL and display URL attached to a DM entry."""
    attachment = entry.get('attachment')
    if not isinstance(attachment, dict):
        return '', ''
    media = attachment.get('entityMedia')
    if not isinstance(media, dict):
        return '', ''
    return media.get('mediaURL') or '', media.get('displayURL') or ''


@artifact_processor
def twitterDirectMessages(context):
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'),
        'From Me',
        'Sender',
        'Conversation',
        'Message',
        'Conversation ID',
        'Timeline',
        'Sender User ID',
        'Attachment Media URL',
        'Attachment Display URL',
        'Marked As Spam',
        'Marked As Abuse',
        'In Reply To Message ID',
        'Message ID',
        'Account ID',
    )

    # One archive per signed-in account was observed in test data, so every
    # matched file is parsed rather than only the first.
    source_paths = _dm_cache_paths(context)
    if not source_paths:
        return data_headers, data_list, ''

    for source_path in source_paths:
        cache = _load_dm_cache(source_path)
        if not cache:
            continue

        inbox = cache.get('inbox') or {}
        local_user_id = (inbox.get('context') or {}).get('userID')
        account_id = (inbox.get('context') or {}).get('accountID')

        for timeline_key, timeline_label in INBOX_TIMELINES:
            timeline = inbox.get(timeline_key) or {}
            for conversation in timeline.get('conversations') or []:
                if not isinstance(conversation, dict):
                    continue

                identifier = conversation.get('identifier') or {}
                conversation_id = identifier.get('canonicalID') or identifier.get('localID') or ''

                # Prefer a group's own name; otherwise name the thread after the
                # participants who are not the account holder.
                others = [_user_label(u) for u in _conversation_participants(conversation)
                          if u.get('userID') != local_user_id]
                conversation_label = conversation.get('conversationName') \
                    or ', '.join(label for label in others if label) or str(conversation_id)

                for entry in conversation.get('entries') or []:
                    if not isinstance(entry, dict):
                        continue
                    sender = entry.get('sender') if isinstance(entry.get('sender'), dict) else {}
                    sender_id = sender.get('userID')
                    media_url, display_url = _attachment_urls(entry)
                    reply_to = entry.get('inReplyToMessageEntry')
                    reply_to_id = ''
                    if isinstance(reply_to, dict):
                        reply_to_id = (reply_to.get('identifier') or {}).get('canonicalID', '')

                    data_list.append((
                        entry.get('time'),
                        1 if local_user_id and sender_id == local_user_id else 0,
                        _user_label(sender),
                        conversation_label,
                        entry.get('displayText') or entry.get('originalText'),
                        conversation_id,
                        timeline_label,
                        sender_id,
                        media_url,
                        display_url,
                        'Yes' if entry.get('marked_as_spam') else '',
                        'Yes' if entry.get('marked_as_abuse') else '',
                        reply_to_id,
                        (entry.get('identifier') or {}).get('canonicalID', ''),
                        account_id,
                    ))

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def twitterDMUsers(context):
    data_list = []
    data_headers = (
        ('Updated', 'datetime'), 'Full Name', 'Username', 'User ID',
        'Account Holder', 'Bio', 'Verified', 'Blue Verified', 'Protected',
        'Blocking', 'Profile Image URL')

    source_paths = _dm_cache_paths(context)
    if not source_paths:
        return data_headers, data_list, ''

    for source_path in source_paths:
        cache = _load_dm_cache(source_path)
        if not cache:
            continue

        local_user_id = ((cache.get('inbox') or {}).get('context') or {}).get('userID')

        for user_id, user in (cache.get('cachedUserByUserID') or {}).items():
            if not isinstance(user, dict):
                continue
            updated = user.get('kUpdatedTimestampCodingKey')
            profile_image = user.get('profileImageMediaEntity')
            data_list.append((
                _dm_user_updated(updated),
                user.get('fullName'),
                user.get('username'),
                user_id,
                'Yes' if local_user_id and str(local_user_id) == str(user_id) else '',
                user.get('bio'),
                'Yes' if user.get('verified') else '',
                'Yes' if user.get('isBlueVerified') else '',
                'Yes' if user.get('protected') else '',
                'Yes' if user.get('blocking') else '',
                profile_image.get('url') if isinstance(profile_image, dict) else '',
            ))

    return data_headers, data_list, '\n'.join(source_paths)


def _dm_user_updated(value):
    """kUpdatedTimestampCodingKey as a UTC datetime, or '' when absent.

    nska_deserialize decodes this NSDate as a naive datetime holding UTC wall time, so it is
    marked UTC. A number is still read as Cocoa seconds. Only the number was accepted
    before, so every decoded value was dropped and Updated was empty on every row.
    """
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return convert_cocoa_core_data_ts_to_utc(value)
    return ''


def _notification_user(entry):
    """The user a URTNotification fromUsers entry names, or ''.

    The cached entries are shaped {'type': {'user': {'userID': <int>}}}. Reading username
    or userID at the top level found nothing, so From Users was empty on every row; the
    top-level keys are still tried first in case another app version stores them there.
    """
    if not isinstance(entry, dict):
        return ''
    found = entry.get('username') or entry.get('userID')
    if not found:
        kind = entry.get('type')
        user = kind.get('user') if isinstance(kind, dict) else None
        found = user.get('userID') if isinstance(user, dict) else None
    return str(found) if found else ''


def _model_caches(context):
    """Every modelCache.sqlite3 collected, one per cache folder, in path order.

    On the sample images each model cache sits in its own folder under TFSModelCache.1/: one
    named <username>-<number> for the signed-in account and, on one image, two more named
    "- app -" and "- guest -". Only the first match used to be read, and in zip order that
    can be an empty one, so every cache is read.
    """
    return sorted(str(found) for found in context.get_files_found()
                  if os.path.basename(str(found)) == 'modelCache.sqlite3'
                  and not os.path.isdir(str(found)))


def _cache_folder(source_path):
    """The name of the folder a model cache belongs to, which names its account."""
    return os.path.basename(os.path.dirname(os.path.dirname(source_path)))


def _iter_cached_models(source_path, model_type):
    """Yield (itemKey uid, decoded model dict) for one model type.

    Rows in Items hold gzip compressed JSON; the wrapper carries the payload
    under 'cacheableModel'. An ItemKeys row with no matching Items row is a key
    whose cached object has been evicted, so there is nothing left to report for
    it; those are counted and logged rather than dropped quietly.
    """
    query = '''
    SELECT k.itemKey, i.archivedObjectData
    FROM ItemKeys k
    LEFT JOIN Items i ON i.id = k.itemId
    WHERE k.itemKey LIKE :pattern
    '''.replace(':pattern', f"'%|{model_type}|%'")

    evicted = 0
    undecodable = 0
    for record in get_sqlite_db_records(source_path, query):
        if record['archivedObjectData'] is None:
            evicted += 1
            continue
        try:
            payload = json.loads(gzip.decompress(record['archivedObjectData']))
        except (OSError, ValueError, TypeError):
            undecodable += 1
            continue
        model = payload.get('cacheableModel')
        if isinstance(model, dict):
            yield record['itemKey'].split('|')[0], model
        else:
            undecodable += 1

    if evicted:
        logfunc(f'Twitter X {model_type} in {_cache_folder(source_path)}: {evicted} cache '
                f'key(s) had no stored object (possibly evicted) and are not reported.')
    if undecodable:
        logfunc(f'Twitter X {model_type} in {_cache_folder(source_path)}: {undecodable} '
                f'cached object(s) could not be decoded.')


def _every_cached_model(source_paths, model_type):
    """Yield (source path, itemKey uid, decoded model dict) across every model cache."""
    for source_path in source_paths:
        for uid, model in _iter_cached_models(source_path, model_type):
            yield source_path, uid, model


def _cocoa(value):
    """A cached model's Cocoa seconds as UTC, or '' for a missing or non-numeric value.

    Some cached users store -63114076800 (NSDate.distantPast) as their updatedTimestamp;
    the shared converter returns '' for it and for 63113904000 (NSDate.distantFuture)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _projected(value):
    """Unwrap the {'projectedValue': x, 'defaultValue': y} shape used by users."""
    if isinstance(value, dict) and ('projectedValue' in value or 'defaultValue' in value):
        projected = value.get('projectedValue')
        return projected if projected is not None else value.get('defaultValue')
    return value


@artifact_processor
def twitterTweets(context):
    source_paths = _model_caches(context)
    data_headers = (
        ('Posted', 'datetime'), ('Cache Updated', 'datetime'), 'Text',
        'Author User ID', 'Language', 'Replies', 'Retweets', 'Quotes',
        'Bookmarks', 'Views', 'Possibly Sensitive', 'Quoted Post URL',
        'Conversation ID', 'Post ID', 'Account Cache')
    if not source_paths:
        return data_headers, [], ''

    results = context.create_artifact_result(
        headers=data_headers,
        source_path='\n'.join(source_paths),
    )

    for source_path, uid, model in _every_cached_model(source_paths, MODEL_TYPE_STATUS):
        view_count = model.get('viewCountInfo')
        quoted = model.get('quotedStatusPermalinkEntity')
        posted = model.get('date')
        updated = model.get('updatedTimestamp')

        results.add_row((
            _cocoa(posted),
            _cocoa(updated),
            model.get('originalText'),
            model.get('fromUserID'),
            model.get('language'),
            model.get('replyCount'),
            model.get('retweetCount'),
            model.get('quoteCount'),
            model.get('bookmarkCount'),
            view_count.get('count') if isinstance(view_count, dict) else '',
            'Yes' if model.get('isPossiblySensitive') else '',
            quoted.get('expandedURL') if isinstance(quoted, dict) else '',
            model.get('conversationID'),
            uid,
            _cache_folder(source_path),
        ))

    return results


@artifact_processor
def twitterCachedUsers(context):
    source_paths = _model_caches(context)
    data_list = []
    data_headers = (
        ('Cache Updated', 'datetime'), 'Username', 'User ID', 'Bio',
        'Followers', 'Following', 'Favourites', 'Blue Verified', 'Protected',
        'Profile Image URL', 'Account Cache')
    if not source_paths:
        return data_headers, data_list, ''

    for source_path, uid, model in _every_cached_model(source_paths, MODEL_TYPE_USER):
        updated = model.get('updatedTimestamp')
        profile_image = model.get('profileImageMediaEntity')

        data_list.append((
            _cocoa(updated),
            model.get('username'),
            uid,
            _projected(model.get('bio')),
            _projected(model.get('numberOfFollowers')),
            _projected(model.get('numberOfFollowing')),
            _projected(model.get('favoritesCount')),
            'Yes' if model.get('isBlueVerified') else '',
            'Yes' if model.get('protectedUser') else '',
            profile_image.get('mediaURL') if isinstance(profile_image, dict) else '',
            _cache_folder(source_path),
        ))

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def twitterNotifications(context):
    source_paths = _model_caches(context)
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Text', 'Icon', 'From Users',
        'Notification ID', 'Account Cache')
    if not source_paths:
        return data_headers, data_list, ''

    for source_path, uid, model in _every_cached_model(source_paths, MODEL_TYPE_NOTIFICATION):
        rich_text = model.get('richText')
        icon = model.get('icon')
        milliseconds = model.get('timestampMilliseconds')
        from_users = model.get('fromUsers')
        if isinstance(from_users, list):
            from_users = ', '.join(
                user for user in (_notification_user(u) for u in from_users) if user)
        else:
            from_users = ''

        data_list.append((
            convert_unix_ts_to_utc(milliseconds / 1000) if isinstance(milliseconds, (int, float)) else '',
            rich_text.get('text') if isinstance(rich_text, dict) else '',
            icon.get('iconID') if isinstance(icon, dict) else '',
            from_users,
            model.get('notificationID') or uid,
            _cache_folder(source_path),
        ))

    return data_headers, data_list, '\n'.join(source_paths)
