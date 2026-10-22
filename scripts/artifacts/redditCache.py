__artifacts_v2__ = {'reddit_cached_posts': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Reddit',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'brand-reddit',
                         'name': 'Reddit - Cached Posts',
                         'description': 'Post objects and resolved content, author and community '
                                        'references in the normalized cache.',
                         'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                         'notes': 'Account is the containing accountData directory, not a verified '
                                  'person. Cached content can be prefetched; presence does not '
                                  'establish reading, authorship or intent. References resolve '
                                  'only within each database. Missing values remain blank; stored '
                                  'false and zero are retained. Content Created and Content Edited '
                                  'are content dates, not cache receipt or view times. Only dates '
                                  'with an explicit timezone are converted; invalid dates are '
                                  'logged with source, key and field. See '
                                  'admin/docs/reddit_cache_history.md for excluded stores and '
                                  'validation boundaries. Content Created was sparse in private '
                                  'validation. Content Edited and Is Removed (as stored) were '
                                  'empty; retained for populated stores. Is Own (as stored) and Is '
                                  'Saved (as stored) were identical in this sample but are '
                                  'independent stored flags. Source File distinguishes multiple '
                                  'stores for an account.'},
 'reddit_cached_comments': {'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Reddit',
                            'output_types': ['html', 'tsv', 'lava'],
                            'artifact_icon': 'brand-reddit',
                            'name': 'Reddit - Cached Comments',
                            'description': 'Comment objects, linked post context, and resolved '
                                           'text and author references in the normalized cache.',
                            'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                            'notes': 'Account is the containing accountData directory, not a '
                                     'verified person. Cached content can be prefetched; presence '
                                     'does not establish reading, authorship or intent. References '
                                     'resolve only within each database. Missing values remain '
                                     'blank; stored false and zero are retained. Content Created '
                                     'and Content Edited are content dates, not cache receipt or '
                                     'view times. Only dates with an explicit timezone are '
                                     'converted; invalid dates are logged with source, key and '
                                     'field. See admin/docs/reddit_cache_history.md for excluded '
                                     'stores and validation boundaries. Post ID (from permalink) '
                                     'and Community (from permalink) require a stored Reddit '
                                     'permalink matching the comment ID. Cached Post Title and '
                                     'Post Cache Key require a matching post in the same database; '
                                     'only 28 of 1029 private comments had a cached title. Missing '
                                     'or mismatched links remain unlinked; reply hierarchy is not '
                                     'inferred. Account, Is Own (as stored), Is Saved (as stored), '
                                     'and Vote State (as stored) were uniform in private '
                                     'validation; retained for source separation and independent '
                                     'stored states.'},
 'reddit_cached_communities': {'author': '@CyberMike81, OpenAI Codex',
                               'creation_date': '2026-10-22',
                               'last_update_date': '2026-10-22',
                               'requirements': 'none',
                               'category': 'Reddit',
                               'output_types': ['html', 'tsv', 'lava'],
                               'artifact_icon': 'brand-reddit',
                               'name': 'Reddit - Cached Communities',
                               'description': 'Community descriptions and stored '
                                              'subscription/notification state in the normalized '
                                              'cache.',
                               'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                               'notes': 'Account is the containing accountData directory, not a '
                                        'verified person. Cached content can be prefetched; '
                                        'presence does not establish reading, authorship or '
                                        'intent. References resolve only within each database. '
                                        'Missing values remain blank; stored false and zero are '
                                        'retained. See admin/docs/reddit_cache_history.md for '
                                        'excluded stores and validation boundaries. Subscription '
                                        'and notification fields are reported as stored without '
                                        'inferring their writer. Account was uniform in private '
                                        'validation; retained to separate source accounts across '
                                        'inputs.'},
 'reddit_cached_profiles': {'author': '@CyberMike81, OpenAI Codex',
                            'creation_date': '2026-10-22',
                            'last_update_date': '2026-10-22',
                            'requirements': 'none',
                            'category': 'Reddit',
                            'output_types': ['html', 'tsv', 'lava'],
                            'artifact_icon': 'brand-reddit',
                            'name': 'Reddit - Cached Profiles',
                            'description': 'Redditor objects retained in the normalized cache, '
                                           'separated by source account.',
                            'paths': ('*/Documents/release02/accountData/*/sqlNormalizedCache*',),
                            'notes': 'Account is the containing accountData directory, not a '
                                     'verified person. Cached content can be prefetched; presence '
                                     'does not establish reading, authorship or intent. References '
                                     'resolve only within each database. Missing values remain '
                                     'blank; stored false and zero are retained. See '
                                     'admin/docs/reddit_cache_history.md for excluded stores and '
                                     'validation boundaries. Only Redditor roots are reported; '
                                     'Profile roots and suggestions are outside this artifact.'},
 'reddit_post_history': {'author': '@CyberMike81, OpenAI Codex',
                         'creation_date': '2026-10-22',
                         'last_update_date': '2026-10-22',
                         'requirements': 'none',
                         'category': 'Reddit',
                         'output_types': ['html', 'tsv', 'lava'],
                         'artifact_icon': 'brand-reddit',
                         'name': 'Reddit - Post History Store',
                         'description': 'Post identifiers, stored list positions and glance flags '
                                        'in PostHistory.',
                         'paths': ('*/Documents/release02/accountData/*/PostHistory',),
                         'notes': 'Account is the containing accountData directory, not a verified '
                                  'person. List Position (zero-based) is storage order, not a '
                                  'timestamp or established chronology. Duplicate list entries and '
                                  'info-only entries are retained. kGlanceInfoKey (as stored) is '
                                  'not interpreted as a view. Missing values remain blank; stored '
                                  'false and zero are retained. Source File distinguishes multiple '
                                  'history stores for an Account. See '
                                  'admin/docs/reddit_cache_history.md for excluded stores and '
                                  'validation boundaries. '},
 'reddit_community_history': {'author': '@CyberMike81, OpenAI Codex',
                              'creation_date': '2026-10-22',
                              'last_update_date': '2026-10-22',
                              'requirements': 'none',
                              'category': 'Reddit',
                              'output_types': ['html', 'tsv', 'lava'],
                              'artifact_icon': 'brand-reddit',
                              'name': 'Reddit - Community History Store',
                              'description': 'Entries and stored positions in SubredditHistory.',
                              'paths': ('*/Documents/release02/accountData/*/SubredditHistory',),
                              'notes': 'Account is the containing accountData directory, not a '
                                       'verified person. List Position (zero-based) is storage '
                                       'order, not established chronology. Entries do not '
                                       'establish subscription, a visit time or deliberate '
                                       'reading. Raw Entry JSON is retained. Source File '
                                       'distinguishes multiple stores for an Account. See '
                                       'admin/docs/reddit_cache_history.md for excluded stores and '
                                       'validation boundaries. '},
 'reddit_comment_drafts': {'author': '@CyberMike81, OpenAI Codex',
                           'creation_date': '2026-10-22',
                           'last_update_date': '2026-10-22',
                           'requirements': 'none',
                           'category': 'Reddit',
                           'output_types': ['html', 'tsv', 'lava'],
                           'artifact_icon': 'brand-reddit',
                           'name': 'Reddit - Comment Drafts',
                           'description': 'Comment draft rows, parent identifiers and stored '
                                          'modification dates.',
                           'paths': ('*/Documents/release02/accountData/*/commentDrafts/CommentDraftEntity.sqlite*',),
                           'notes': 'Account is the containing accountData directory, not a '
                                    'verified person. Only '
                                    'Documents/release02/accountData/*/commentDrafts/CommentDraftEntity.sqlite '
                                    'stores are selected. Modified uses Core Data seconds; '
                                    'Modified Raw (Core Data seconds) preserves the original '
                                    'value. A stored zero converts to 2001-01-01 UTC; its '
                                    'application meaning is unverified. Draft text is not proof of '
                                    'sending. Populated draft rows are synthetic-tested only; the '
                                    'private validation store was empty. See '
                                    'admin/docs/reddit_cache_history.md for excluded stores and '
                                    'validation boundaries. '}}

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
        if normalized.endswith('Z'):
            normalized = normalized[:-1] + '+00:00'
        stamp = datetime.fromisoformat(normalized)
        if stamp.tzinfo is None:
            raise ValueError('timezone missing')
        return stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        logfunc(f'Reddit cache: invalid or timezone-free content date; {location}')
        return ''


def _cache(path):
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'Reddit cache: could not open {path}')
        return {}
    result = {}
    try:
        for rowid, key, raw in db.execute('SELECT _id, key, record FROM records ORDER BY _id'):
            try:
                value = json.loads(raw)
            except (ValueError, TypeError, UnicodeError):
                logfunc(f'Reddit cache: skipped malformed JSON; file={path}; row={rowid}; key={key}')
                continue
            if isinstance(key, str) and isinstance(value, dict):
                result[key] = value
            else:
                logfunc(f'Reddit cache: unsupported record shape; file={path}; row={rowid}; key={key}')
    except sqlite3.Error:
        logfunc(f'Reddit cache: unsupported or unreadable records table; file={path}')
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
        records = _cache(path)
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
        rows.append((_iso(obj.get('createdAt'), f'file={path}; key={key}; field=createdAt'),
                     _iso(obj.get('editedAt'), f'file={path}; key={key}; field=editedAt'),
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
            logfunc(f'Reddit history: expected PostHistory dictionary; file={path}')
            continue
        order = data.get('kPostIDDictionaryKey', [])
        raw_info = data.get('kInfoDictionaryKey', {})
        if not isinstance(raw_info, dict):
            logfunc(f'Reddit history: invalid kInfoDictionaryKey; file={path}')
        info = _dict(raw_info)
        if not isinstance(order, list):
            logfunc(f'Reddit history: invalid kPostIDDictionaryKey; file={path}')
            order = []
        listed = set()
        for position, post in enumerate(order):
            if not isinstance(post, str):
                logfunc(f'Reddit history: non-string post ID; file={path}; position={position}')
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
            logfunc(f'Reddit history: expected SubredditHistory list; file={path}')
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
            logfunc(f'Reddit drafts: could not open {path}')
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
            logfunc(f'Reddit drafts: unsupported or unreadable ZCOMMENTDRAFTENTITY; file={path}')
        finally:
            db.close()
    return (('Modified', 'datetime'), 'Account', 'Row ID', 'Content', 'Draft ID', 'Parent Comment ID',
            'Post ID', 'Post Title', 'Modified Raw (Core Data seconds)', 'Source File'), rows, source
