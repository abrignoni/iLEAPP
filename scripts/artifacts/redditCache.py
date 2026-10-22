__artifacts_v2__ = {'reddit_cached_posts': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Reddit',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'brand-reddit',
                         'name': 'Reddit - Cached Posts',
                         'description': 'Cached post text, author, community and stored post '
                                        'states.',
                         'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                         'notes': 'Content Created and Content Edited are post creation/edit '
                                  'dates, not view or cache-receipt times. Dates without a '
                                  'timezone remain blank; original values are in Object JSON. '
                                  'Account is the source account directory, not a verified person. '
                                  'Source File separates cache stores. Author/community references '
                                  'come from the same cache. Cached content may be prefetched and '
                                  'does not establish reading or authorship; own/saved/vote flags '
                                  'are reported as stored.'},
 'reddit_cached_comments': {'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Reddit',
                            'output_types': ['html', 'tsv', 'lava'],
                            'artifact_icon': 'brand-reddit',
                            'name': 'Reddit - Cached Comments',
                            'description': 'Cached comment text, author and linked post context.',
                            'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                            'notes': 'Content Created and Content Edited are comment creation/edit '
                                     'dates, not view times. Original values are in Object JSON. '
                                     'Post ID and community come from a stored permalink matching '
                                     'the comment ID; Cached Post Title requires a matching post '
                                     'in the same cache. Missing links remain blank; reply nesting '
                                     'is not established. Account and Source File identify the '
                                     'source context. Cached comments and own/saved/vote flags do '
                                     'not establish reading or device-owner authorship.'},
 'reddit_cached_communities': {'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Reddit',
                               'output_types': ['html', 'tsv', 'lava'],
                               'artifact_icon': 'brand-reddit',
                               'name': 'Reddit - Cached Communities',
                               'description': 'Cached community IDs, names, descriptions and '
                                              'subscription/notification states.',
                               'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                               'notes': 'Community ID identifies the stored subreddit; Account and '
                                        'Source File distinguish source accounts and caches. '
                                        'Subscription, favorite, mute and notification fields are '
                                        'reported as stored. A cached community does not establish '
                                        'a visit or who set a state. Object JSON preserves the '
                                        'source fields; blank values were not retained in the '
                                        'object.'},
 'reddit_cached_profiles': {'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Reddit',
                            'output_types': ['html', 'tsv', 'lava'],
                            'artifact_icon': 'brand-reddit',
                            'name': 'Reddit - Cached Profiles',
                            'description': 'Cached Reddit user IDs, names, account types and '
                                           'blocked states.',
                            'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                            'notes': 'Profile ID identifies the cached Redditor object. Account is '
                                     'the containing source account, not necessarily the profile '
                                     'being described. Source File separates caches; Object JSON '
                                     'preserves additional fields. Blocked and account-type values '
                                     'are reported as stored. Profile presence does not establish '
                                     'contact or a visit. Separate Profile objects and suggestions '
                                     'are not included.'},
 'reddit_post_history': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Reddit',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'brand-reddit',
                         'name': 'Reddit - Post History Store',
                         'description': 'Stored post IDs, list positions and glance flags.',
                         'paths': ('*/Documents/release02/accountData/*/PostHistory',),
                         'notes': 'List Position is zero-based storage order, not a timestamp or '
                                  'established viewing sequence. Membership distinguishes list '
                                  'entries from info-dictionary-only entries; duplicate entries '
                                  'are retained. kGlanceInfoKey is reported as stored and is not a '
                                  'read receipt. Account and Source File distinguish history '
                                  'stores; Info JSON retains the entry metadata.'},
 'reddit_community_history': {'author': '@CyberMike81, OpenAI Codex',
                              'creation_date': '2026-10-22',
                              'last_update_date': '2026-10-22',
                              'requirements': 'none',
                              'category': 'Reddit',
                              'output_types': ['html', 'tsv', 'lava'],
                              'artifact_icon': 'brand-reddit',
                              'name': 'Reddit - Community History Store',
                              'description': 'Stored community-history entries and list positions.',
                              'paths': ('*/Documents/release02/accountData/*/SubredditHistory',),
                              'notes': 'List Position is zero-based storage order, not a timestamp '
                                       'or established visit sequence. Entry holds the stored '
                                       'identifier; Entry JSON preserves the original value. '
                                       'Account and Source File distinguish history stores. An '
                                       'entry does not establish subscription, deliberate reading '
                                       'or a visit time.'},
 'reddit_comment_drafts': {'author': '@CyberMike81, OpenAI Codex',
                           'creation_date': '2026-10-22',
                           'last_update_date': '2026-10-22',
                           'requirements': 'none',
                           'category': 'Reddit',
                           'output_types': ['html', 'tsv', 'lava'],
                           'artifact_icon': 'brand-reddit',
                           'name': 'Reddit - Comment Drafts',
                           'description': 'Stored comment drafts, parent/post IDs and modification '
                                          'dates.',
                           'paths': ('*/Documents/release02/accountData/*/commentDrafts/CommentDraftEntity.sqlite*',),
                           'notes': 'Modified is the draft modification field in Core Data seconds '
                                    'since 2001-01-01 UTC; Modified Raw retains the stored value. '
                                    'Zero displays as 2001-01-01 UTC, but its application meaning '
                                    'is unknown. Content is draft text, not proof of sending. '
                                    'Parent Comment ID, Post ID and Post Title are stored context; '
                                    'Account and Source File identify the source store.'}}

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlsplit

from scripts.ilapfuncs import (
    artifact_processor, get_plist_file_content, logfunc, open_sqlite_db_readonly,
)


def _files(context, basename):
    return sorted({str(p) for p in context.get_files_found()
                   if os.path.isfile(p) and os.path.basename(p) == basename})


def _account(path):
    match = re.search(r'/accountData/([^/]+)/', str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _iso(value, location=''):
    if value is None or value == '':
        return ''
    try:
        if not isinstance(value, str):
            raise ValueError('not a timestamp string')
        # Python 3.10 needs a colon in offsets such as the observed +0000.
        normalized = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', value)
        # Python 3.10 accepts only 3/6 fractional digits. Normalize the
        # HH:MM:SS fraction to microseconds; preserve the original in Object JSON.
        normalized = re.sub(r'(\d{2}:\d{2}:\d{2})[.,](\d+)',
                            lambda m: m[1] + '.' + m[2][:6].ljust(6, '0'), normalized)
        if normalized.endswith('Z'):
            normalized = normalized[:-1] + '+00:00'
        stamp = datetime.fromisoformat(normalized)
        if stamp.tzinfo is None:
            raise ValueError('timezone missing')
        return stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        logfunc(f'Reddit cache: invalid or timezone-free content date; {location}')
        return ''


def _cache(path, display_path):
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'Reddit cache: could not open {display_path}')
        return {}
    result = {}
    try:
        for rowid, key, raw in db.execute('SELECT _id, key, record FROM records ORDER BY _id'):
            try:
                value = json.loads(raw)
            except (ValueError, TypeError, UnicodeError):
                logfunc(f'Reddit cache: skipped malformed JSON; file={display_path}; row={rowid}; key={key}')
                continue
            if isinstance(key, str) and isinstance(value, dict):
                result[key] = value
            else:
                logfunc(f'Reddit cache: unsupported record shape; file={display_path}; row={rowid}; key={key}')
    except sqlite3.Error:
        logfunc(f'Reddit cache: unsupported or unreadable records table; file={display_path}')
    finally:
        db.close()
    return result


def _resolve(value, records, seen=(), depth=0):
    # Bound cycles/hostile nesting and keep unresolved reference tokens for audit.
    if depth >= 12:
        return value
    if isinstance(value, dict):
        ref = value.get('$reference', value.get('__ref'))
        if isinstance(ref, str):
            if ref in seen or ref not in records:
                return value
            return _resolve(records[ref], records, seen + (ref,), depth + 1)
        return {k: _resolve(v, records, seen, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, records, seen, depth + 1) for v in value]
    return value


def _dict(value):
    return value if isinstance(value, dict) else {}


def _objects(context, kind):
    for path in _files(context, 'sqlNormalizedCache'):
        records = _cache(path, context.get_relative_path(path))
        for key, obj in records.items():
            # Child fragments share the prefix but are not additional posts/users.
            if not re.fullmatch(re.escape(kind) + r':[^.:]+', key):
                continue
            yield path, key, obj, records


def _permalink_context(value, object_id):
    """Return post/community from a matching stored Reddit comment permalink only."""
    if not isinstance(value, str) or not isinstance(object_id, str):
        return '', ''
    try:
        link = urlsplit(value)
    except ValueError:
        return '', ''
    if link.netloc:
        host = (link.hostname or '').lower()
        if link.scheme not in ('', 'http', 'https') or not (
                host == 'reddit.com' or host.endswith('.reddit.com')):
            return '', ''
    elif link.scheme or not value.startswith('/'):
        return '', ''
    match = re.fullmatch(r'/(r|user)/([^/]+)/comments/([a-z0-9]+)/[^/]*/([a-z0-9]+)/?',
                         link.path, re.IGNORECASE)
    if match is None or object_id != 't1_' + match.group(4):
        return '', ''
    return 't3_' + match.group(3), match.group(2) if match.group(1) == 'r' else ''


def _content(context, kind):
    rows = []
    source = ''
    for path, key, obj, records in _objects(context, kind):
        source = source or path
        content = _dict(_resolve(obj.get('content'), records))
        author = _dict(_resolve(obj.get('authorInfo'), records))
        community = _dict(_resolve(obj.get('subreddit'), records))
        # Preserve direct reference keys and resolved selected objects without expanding forests.
        resolved = {'content': content, 'authorInfo': author, 'subreddit': community}
        post_id, link_community = _permalink_context(obj.get('permalink'), obj.get('id'))
        parent = _dict(records.get('SubredditPost:' + post_id)) if post_id else {}
        rows.append((_iso(obj.get('createdAt'), f'file={context.get_relative_path(path)}; key={key}; field=createdAt'),
                     _iso(obj.get('editedAt'), f'file={context.get_relative_path(path)}; key={key}; field=editedAt'),
                     _account(path), obj.get('id', ''), obj.get('title', ''),
                     content.get('markdown', content.get('preview', '')),
                     author.get('id', ''), author.get('displayName', author.get('name', '')),
                     community.get('id', ''), community.get('name', ''),
                     obj.get('permalink', ''), obj.get('url', ''),
                     obj.get('isOwnPost' if kind == 'SubredditPost' else 'isOwnComment'),
                     obj.get('isSaved'), obj.get('voteState'), obj.get('isRemoved'),
                     key, _json(obj), _json(resolved), context.get_relative_path(path),
                     post_id, link_community, parent.get('title', ''),
                     'SubredditPost:' + post_id if parent else ''))
    return rows, source


@artifact_processor
def reddit_cached_posts(context):
    data_headers = ('Account', 'Title', 'Text', 'Author Name', 'Community',
                    ('Content Created', 'datetime'), ('Content Edited', 'datetime'),
                    'Object ID', 'Author ID', 'Community ID', 'Permalink', 'URL',
                    'Is Own (as stored)', 'Is Saved (as stored)', 'Vote State (as stored)',
                    'Is Removed (as stored)', 'Cache Key', 'Object JSON',
                    'Resolved Content JSON', 'Source File')
    rows, source = _content(context, 'SubredditPost')
    indexes = (2, 4, 5, 7, 9, 0, 1, 3, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
    return data_headers, [tuple(row[i] for i in indexes) for row in rows], source


@artifact_processor
def reddit_cached_comments(context):
    data_headers = (('Content Created', 'datetime'), ('Content Edited', 'datetime'),
                    'Account', 'Cached Post Title', 'Post ID (from permalink)',
                    'Community (from permalink)', 'Author Name', 'Text', 'Object ID',
                    'Author ID', 'Permalink', 'Is Own (as stored)', 'Is Saved (as stored)',
                    'Vote State (as stored)', 'Is Removed (as stored)', 'Cache Key',
                    'Post Cache Key', 'Object JSON', 'Resolved Content JSON', 'Source File')
    rows, source = _content(context, 'Comment')
    indexes = (0, 1, 2, 22, 20, 21, 7, 5, 3, 6, 10, 12, 13, 14, 15, 16, 23, 17, 18, 19)
    return data_headers, [tuple(row[i] for i in indexes) for row in rows], source


def _entities(context, kind, fields):
    rows = []
    source = ''
    for path, key, obj, _ in _objects(context, kind):
        source = source or path
        rows.append((_account(path), key, *(obj.get(k) for k, _ in fields),
                     _json(obj), context.get_relative_path(path)))
    return ('Account', 'Cache Key', *(label for _, label in fields), 'Object JSON',
            'Source File'), rows, source


@artifact_processor
def reddit_cached_communities(context):
    return _entities(context, 'Subreddit', (
        ('id', 'Community ID'), ('name', 'Community'), ('title', 'Title'),
        ('publicDescriptionText', 'Public Description'), ('path', 'Path'),
        ('isSubscribed', 'Is Subscribed (as stored)'), ('isFavorite', 'Is Favorite (as stored)'),
        ('isMuted', 'Is Muted (as stored)'), ('notificationLevel', 'Notification Level (as stored)'),
    ))


@artifact_processor
def reddit_cached_profiles(context):
    return _entities(context, 'Redditor', (
        ('id', 'Profile ID'), ('name', 'Name'), ('displayName', 'Display Name'),
        ('isBlocked', 'Is Blocked (as stored)'), ('accountType', 'Account Type (as stored)'),
    ))


@artifact_processor
def reddit_post_history(context):
    rows = []
    source = ''
    for path in _files(context, 'PostHistory'):
        source = source or path
        data = get_plist_file_content(path)
        if not isinstance(data, dict):
            logfunc(f'Reddit history: expected PostHistory dictionary; file={context.get_relative_path(path)}')
            continue
        order = data.get('kPostIDDictionaryKey', [])
        raw_info = data.get('kInfoDictionaryKey', {})
        if not isinstance(raw_info, dict):
            logfunc(f'Reddit history: invalid kInfoDictionaryKey; file={context.get_relative_path(path)}')
        info = _dict(raw_info)
        if not isinstance(order, list):
            logfunc(f'Reddit history: invalid kPostIDDictionaryKey; file={context.get_relative_path(path)}')
            order = []
        listed = set()
        for position, post in enumerate(order):
            if not isinstance(post, str):
                logfunc(f'Reddit history: non-string post ID; file={context.get_relative_path(path)}; position={position}')
                continue
            listed.add(post)
            entry = info.get(post)
            rows.append((_account(path), post, position, 'List', _dict(entry).get('kGlanceInfoKey'),
                         _json(entry), context.get_relative_path(path)))
        for post, entry in info.items():
            if post not in listed:
                rows.append((_account(path), post, None, 'Info dictionary only',
                             _dict(entry).get('kGlanceInfoKey'), _json(entry),
                             context.get_relative_path(path)))
    return ('Account', 'Post ID', 'List Position (zero-based)', 'Membership',
            'kGlanceInfoKey (as stored)', 'Info JSON', 'Source File'), rows, source


@artifact_processor
def reddit_community_history(context):
    rows = []
    source = ''
    for path in _files(context, 'SubredditHistory'):
        source = source or path
        data = get_plist_file_content(path)
        if not isinstance(data, list):
            logfunc(f'Reddit history: expected SubredditHistory list; file={context.get_relative_path(path)}')
            continue
        if isinstance(data, list):
            for position, entry in enumerate(data):
                rows.append((_account(path), position, entry if isinstance(entry, str) else '',
                             _json(entry), context.get_relative_path(path)))
    return ('Account', 'List Position (zero-based)', 'Entry', 'Entry JSON', 'Source File'), rows, source


@artifact_processor
def reddit_comment_drafts(context):
    rows = []
    source = ''
    for path in _files(context, 'CommentDraftEntity.sqlite'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'Reddit drafts: could not open {context.get_relative_path(path)}')
            continue
        source = source or path
        try:
            for row in db.execute('SELECT Z_PK,ZMODIFIEDDATE,ZCONTENT,ZID,ZPARENTCOMMENTPK,'
                                  'ZPOSTPK,ZPOSTTITLE FROM ZCOMMENTDRAFTENTITY'):
                stamp = ''
                if isinstance(row[1], (int, float)):
                    try:
                        stamp = datetime.fromtimestamp(row[1] + 978307200, timezone.utc)
                    except (ValueError, OverflowError, OSError):
                        pass
                rows.append((stamp, _account(path), row[0], *row[2:], row[1], context.get_relative_path(path)))
        except sqlite3.Error:
            logfunc(f'Reddit drafts: unsupported or unreadable ZCOMMENTDRAFTENTITY; file={context.get_relative_path(path)}')
        finally:
            db.close()
    return (('Modified', 'datetime'), 'Account', 'Row ID', 'Content', 'Draft ID', 'Parent Comment ID',
            'Post ID', 'Post Title', 'Modified Raw (Core Data seconds)', 'Source File'), rows, source
