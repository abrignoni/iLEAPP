__artifacts_v2__ = {
    'twitterDirectMessages': {
        'name': 'Twitter X - Direct Messages',
        'description': 'Direct message conversations cached by the Twitter X application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Twitter X',
        'notes': 'The direct message cache is an NSKeyedArchiver archive of the app inbox; it holds the trusted, untrusted and low quality timelines.',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.atebits.tweetie.direct-message.cache/*',),
        'output_types': 'all',
        'artifact_icon': 'message',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 72 rows across 4 conversations',
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
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Twitter X',
        'notes': '',
        'paths': ('*/mobile/Containers/Data/Application/*/Library/Caches/com.atebits.tweetie.direct-message.cache/*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 5 rows',
        },
    },
    'twitterTweets': {
        'name': 'Twitter X - Cached Posts',
        'description': 'Posts (tweets) cached in the Twitter X model cache database',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Twitter X',
        'notes': 'Cached objects are gzip compressed JSON stored in the Items table.',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'brand-twitter',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 523 rows',
        },
    },
    'twitterCachedUsers': {
        'name': 'Twitter X - Cached Users',
        'description': 'User profiles cached in the Twitter X model cache database',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Twitter X',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 340 rows',
        },
    },
    'twitterNotifications': {
        'name': 'Twitter X - Notifications',
        'description': 'In-app notifications cached by the Twitter X application',
        'author': '@AlexisBrignoni',
        'creation_date': '2026-07-25',
        'last_update_date': '2026-07-25',
        'requirements': 'none',
        'category': 'Twitter X',
        'notes': '',
        'paths': ('*/mobile/Containers/Shared/AppGroup/*/TFSModelCache.*/*/database/modelCache.sqlite3*',),
        'output_types': 'standard',
        'artifact_icon': 'bell',
        'sample_data': {
            'josh_ios17_ffs': 'iOS 17.3 | 119 rows',
        },
    },
}

import gzip
import json
import os

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, logfunc, \
    get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc, \
    convert_unix_ts_to_utc

# The three inbox timelines the app keeps. Conversations that were never
# accepted land in the untrusted or low quality lists rather than the main one.
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
        return nd.deserialize_plist(source_path)
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
        ('Timestamp', 'datetime'), 'Conversation', 'Conversation ID', 'Timeline',
        'Sender', 'Sender User ID', 'Message', 'Attachment Media URL',
        'Attachment Display URL', 'Marked As Spam', 'Marked As Abuse',
        'In Reply To Message ID', 'Message ID', 'Account ID', 'From Me')

    # The cache directory holds one archive per signed-in account, so every
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
                        conversation_label,
                        conversation_id,
                        timeline_label,
                        _user_label(sender),
                        sender_id,
                        entry.get('displayText') or entry.get('originalText'),
                        media_url,
                        display_url,
                        'Yes' if entry.get('marked_as_spam') else '',
                        'Yes' if entry.get('marked_as_abuse') else '',
                        reply_to_id,
                        (entry.get('identifier') or {}).get('canonicalID', ''),
                        account_id,
                        1 if local_user_id and sender_id == local_user_id else 0,
                    ))

    return data_headers, data_list, ', '.join(source_paths)


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
                convert_cocoa_core_data_ts_to_utc(updated) if isinstance(updated, (int, float)) else '',
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

    return data_headers, data_list, ', '.join(source_paths)


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
        logfunc(f'Twitter X {model_type}: {evicted} cache key(s) had no stored '
                f'object (evicted from cache) and are not reported.')
    if undecodable:
        logfunc(f'Twitter X {model_type}: {undecodable} cached object(s) could '
                f'not be decoded.')


def _projected(value):
    """Unwrap the {'projectedValue': x, 'defaultValue': y} shape used by users."""
    if isinstance(value, dict) and ('projectedValue' in value or 'defaultValue' in value):
        projected = value.get('projectedValue')
        return projected if projected is not None else value.get('defaultValue')
    return value


@artifact_processor
def twitterTweets(context):
    source_path = get_file_path(context.get_files_found(), 'modelCache.sqlite3')
    data_list = []
    data_headers = (
        ('Posted', 'datetime'), ('Cache Updated', 'datetime'), 'Text',
        'Author User ID', 'Language', 'Replies', 'Retweets', 'Quotes',
        'Bookmarks', 'Views', 'Possibly Sensitive', 'Quoted Post URL',
        'Conversation ID', 'Post ID')
    if not source_path:
        return data_headers, data_list, ''

    for uid, model in _iter_cached_models(source_path, MODEL_TYPE_STATUS):
        view_count = model.get('viewCountInfo')
        quoted = model.get('quotedStatusPermalinkEntity')
        posted = model.get('date')
        updated = model.get('updatedTimestamp')

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(posted) if isinstance(posted, (int, float)) else '',
            convert_cocoa_core_data_ts_to_utc(updated) if isinstance(updated, (int, float)) else '',
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
        ))

    return data_headers, data_list, source_path


@artifact_processor
def twitterCachedUsers(context):
    source_path = get_file_path(context.get_files_found(), 'modelCache.sqlite3')
    data_list = []
    data_headers = (
        ('Cache Updated', 'datetime'), 'Username', 'User ID', 'Bio',
        'Followers', 'Following', 'Favourites', 'Blue Verified', 'Protected',
        'Profile Image URL')
    if not source_path:
        return data_headers, data_list, ''

    for uid, model in _iter_cached_models(source_path, MODEL_TYPE_USER):
        updated = model.get('updatedTimestamp')
        profile_image = model.get('profileImageMediaEntity')

        data_list.append((
            convert_cocoa_core_data_ts_to_utc(updated) if isinstance(updated, (int, float)) else '',
            model.get('username'),
            uid,
            _projected(model.get('bio')),
            _projected(model.get('followersCount')),
            _projected(model.get('followingCount')),
            _projected(model.get('favoritesCount')),
            'Yes' if model.get('isBlueVerified') else '',
            'Yes' if model.get('protectedUser') else '',
            profile_image.get('mediaURL') if isinstance(profile_image, dict) else '',
        ))

    return data_headers, data_list, source_path


@artifact_processor
def twitterNotifications(context):
    source_path = get_file_path(context.get_files_found(), 'modelCache.sqlite3')
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'), 'Text', 'Icon', 'From Users',
        'Notification ID')
    if not source_path:
        return data_headers, data_list, ''

    for uid, model in _iter_cached_models(source_path, MODEL_TYPE_NOTIFICATION):
        rich_text = model.get('richText')
        icon = model.get('icon')
        milliseconds = model.get('timestampMilliseconds')
        from_users = model.get('fromUsers')
        if isinstance(from_users, list):
            from_users = ', '.join(
                str(u.get('username') or u.get('userID') or '')
                for u in from_users if isinstance(u, dict))
        else:
            from_users = ''

        data_list.append((
            convert_unix_ts_to_utc(milliseconds / 1000) if isinstance(milliseconds, (int, float)) else '',
            rich_text.get('text') if isinstance(rich_text, dict) else '',
            icon.get('iconID') if isinstance(icon, dict) else '',
            from_users,
            model.get('notificationID') or uid,
        ))

    return data_headers, data_list, source_path
