"""Build an offline, linked Reddit workspace from existing iLEAPP exports.

The workspace combines the original Reddit artifacts and the optional cache/history
artifacts. Joins preserve source observations; they do not infer reading or authorship.
"""
import argparse
import base64
import html
import os
import shutil
import tempfile
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


KINDS = {
    'reddit_cached_posts': 'post', 'reddit_cached_comments': 'comment',
    'reddit_chats': 'chat', 'reddit_chat_messages': 'chat',
    'reddit_cached_communities': 'community', 'reddit_subreddit_subscriptions': 'community',
    'reddit_cached_profiles': 'profile', 'reddit_users': 'profile',
    'reddit_chat_users': 'matrix_user', 'reddit_chat_contacts': 'contact',
    'reddit_post_history': 'post_history', 'reddit_community_history': 'community_history',
    'reddit_comment_drafts': 'draft',
}


def _quote(value):
    return '"' + value.replace('"', '""') + '"'


def _value(row, *labels):
    for label in labels:
        value = row.get(label)
        if value is not None and value != '':
            return value
    return ''


def _role(raw, view, key):
    column = view.get(key)
    return raw[column] if column in raw.keys() and raw[column] is not None else ''


def _scope(source, account):
    """A source account directory, never an account name alone or a guessed account."""
    if '\n' in source:
        return ''
    match = re.match(r'^(.*?/accountData/([^/]+))/', source.replace('\\', '/'))
    if match and (not account or str(account) == match[2]):
        return match[1]
    return ''


def _container(source):
    if '\n' in source:
        return ''
    match = re.match(r'^(.*?/Containers/(?:Data/Application|Shared/AppGroup)/[^/]+)/',
                     source.replace('\\', '/'))
    return match[1] if match else ''


def _object(row):
    try:
        obj = json.loads(_value(row, 'Object JSON') or '{}')
    except (ValueError, TypeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def load_records(report):
    """Read all supported exports without changing the database, manifest or rows."""
    report = Path(report).resolve()
    manifest = json.loads((report / '_lava_data.lava').read_text(encoding='utf-8'))
    records = []
    uri = (report / '_lava_artifacts.db').as_uri() + '?mode=ro'
    db = sqlite3.connect(uri, uri=True)
    db.row_factory = sqlite3.Row
    try:
        for artifact in manifest.get('artifacts', {}).get('Reddit', []):
            table = artifact.get('tablename')
            if table not in KINDS:
                continue
            columns = artifact['column_map']
            for raw in db.execute('SELECT rowid AS __reader_rowid, * FROM ' + _quote(table)):
                row = {label: raw[sql] for sql, label in columns.items()}
                source = str(_value(row, 'Source File') or artifact.get('source_path', ''))
                account = _value(row, 'Account', 'Account ID')
                kind = KINDS[table]
                record = {'table': table, 'rowid': raw['__reader_rowid'], 'kind': kind,
                          'ref': f'{table}:{raw["__reader_rowid"]}', 'account': account,
                          'source': source, 'scope': _scope(source, account),
                          'container': _container(source), 'fields': row, 'links': [],
                          'text': '', 'title': '', 'id': '', 'created': '', 'author': '',
                          'community': '', 'communityId': '', 'profileId': ''}
                if kind == 'chat':
                    view = artifact.get('data_views', {}).get('conversation', {})
                    channel = _role(raw, view, 'conversationDiscriminatorColumn')
                    record.update(text=_role(raw, view, 'textColumn'),
                                  author=_role(raw, view, 'senderColumn'),
                                  created=_role(raw, view, 'timeColumn'),
                                  direction=_role(raw, view, 'directionColumn'),
                                  sentValue=view.get('directionSentValue'),
                                  title=_role(raw, view, 'conversationLabelColumn'), channel=channel,
                                  senderId=_value(row, 'Sender ID'),
                                  id=_value(row, 'Event ID', 'Message ID (as stored)'),
                                  event=_value(row, 'Event Type'), attachment=_value(row, 'Attachment'))
                    record['group'] = json.dumps([table, account, source,
                                                  channel or ['unassigned', record['rowid']]])
                elif kind in ('post', 'comment'):
                    comment = kind == 'comment'
                    post_id = _value(row, 'Post ID (from permalink)') if comment else _value(row, 'Object ID')
                    record.update(text=_value(row, 'Text'),
                                  author=_value(row, 'Author Name', 'Author ID'),
                                  profileId=_value(row, 'Author ID'),
                                  created=_value(row, 'Content Created'), edited=_value(row, 'Content Edited'),
                                  title=_value(row, 'Cached Post Title') if comment else _value(row, 'Title'),
                                  community=_value(row, 'Subreddit (from permalink)', 'Community (from permalink)') if comment else _value(row, 'Subreddit', 'Community'),
                                  communityId=_value(row, 'Subreddit ID', 'Community ID'),
                                  postId=post_id, id=_value(row, 'Object ID'),
                                  permalink=_value(row, 'Permalink'), own=_value(row, 'Is Own (as stored)'))
                    record['group'] = json.dumps(['discussion', account, source,
                                                  post_id or ['unassigned', table, record['rowid']]])
                elif kind == 'community':
                    record.update(id=_value(row, 'Subreddit ID', 'Community ID'), communityId=_value(row, 'Subreddit ID', 'Community ID'),
                                  community=_value(row, 'Subreddit', 'Community'), title=_value(row, 'Title'),
                                  text=_value(row, 'Public Description'), created=_value(row, 'Community Created'))
                elif kind in ('profile', 'contact', 'matrix_user'):
                    record.update(id=_value(row, 'Profile ID', 'Reddit ID', 'User ID', 'Matrix User ID'),
                                  author=_value(row, 'Display Name', 'Name', 'Username'),
                                  title=_value(row, 'Display Name', 'Name', 'Username'),
                                  text=_value(row, 'Real Name'),
                                  created=_value(row, 'Profile Created', 'Created', 'Updated Date'))
                    record['profileId'] = record['id']
                elif kind == 'post_history':
                    record.update(id=_value(row, 'Post ID'), postId=_value(row, 'Post ID'))
                elif kind == 'community_history':
                    record.update(id=_value(row, 'Entry'), communityId=_value(row, 'Entry'))
                elif kind == 'draft':
                    record.update(id=_value(row, 'Draft ID'), postId=_value(row, 'Post ID'),
                                  title=_value(row, 'Post Title'), text=_value(row, 'Content'),
                                  created=_value(row, 'Modified'))
                date_labels = {'reddit_cached_posts': 'Content Created', 'reddit_cached_comments': 'Content Created',
                    'reddit_chats': 'Server Timestamp', 'reddit_chat_messages': 'Timestamp',
                    'reddit_subreddit_subscriptions': 'Community Created', 'reddit_users': 'Profile Created',
                    'reddit_chat_users': 'Updated Date', 'reddit_chat_contacts': 'Created', 'reddit_comment_drafts': 'Modified'}
                record['dateLabel'] = date_labels.get(table, '')
                record['dateFields'] = [columns[item['name']] for item in artifact.get('object_columns', [])
                                        if item.get('type') == 'datetime' and item.get('name') in columns]
                if 'group' not in record:
                    namespace = record['scope'] if kind == 'community' else record['container']
                    if kind in ('community', 'profile', 'contact', 'matrix_user') and namespace and record['id']:
                        identity_kind = 'matrix_user' if kind == 'matrix_user' else 'community' if kind == 'community' else 'profile'
                        record['group'] = json.dumps([identity_kind, namespace, record['id']])
                    else:
                        record['group'] = json.dumps([kind, record['ref']])
                records.append(record)
    finally:
        db.close()
    link_records(records)
    return records


def link_records(records):
    """Attach explicit, reversible relationships; never substitute source field values."""
    discussions = defaultdict(dict)
    communities = defaultdict(list)
    cached_communities = defaultdict(list)
    community_names = defaultdict(list)
    profiles = defaultdict(list)
    cached_profiles = defaultdict(list)
    matrix_users = defaultdict(list)
    for record in records:
        kind = record['kind']
        if kind in ('post', 'comment') and record['scope'] and record.get('postId'):
            key = (record['scope'], record['postId'])
            previous = discussions[key].get(record['group'])
            if previous is None or kind == 'post':
                discussions[key][record['group']] = record
        if kind == 'community' and record['id']:
            if record['scope']:
                communities[(record['scope'], record['id'])].append(record)
            if record['table'] == 'reddit_cached_communities':
                cached_communities[(record['source'], record['id'])].append(record)
                if record['community']:
                    community_names[(record['source'], str(record['community']).casefold())].append(record)
        if kind in ('profile', 'contact') and record['id']:
            if record['container']:
                profiles[(record['container'], record['id'])].append(record)
            if record['table'] == 'reddit_cached_profiles':
                cached_profiles[(record['source'], record['id'])].append(record)
        if kind == 'matrix_user' and record['id'] and record['container']:
            matrix_users[(record['container'], record['id'])].append(record)

    def connect(left, right, basis):
        if left['ref'] == right['ref']:
            return
        forward = {'ref': right['ref'], 'basis': basis}
        reverse = {'ref': left['ref'], 'basis': basis}
        if forward not in left['links']:
            left['links'].append(forward)
        if reverse not in right['links']:
            right['links'].append(reverse)

    for record in records:
        kind = record['kind']
        if kind in ('post_history', 'draft') and record['scope'] and record.get('postId'):
            matches = discussions.get((record['scope'], record['postId']), {})
            record['matchCount'] = len(matches)
            for match in matches.values():
                connect(record, match, 'Exact post ID; same account directory. Multiple cache stores remain separate.')
        if kind == 'community_history' and record['scope'] and record['id']:
            matches = communities.get((record['scope'], record['id']), [])
            record['matchCount'] = len({match['group'] for match in matches})
            for match in matches:
                connect(record, match, 'Exact subreddit ID; same account directory.')
        if kind in ('post', 'comment'):
            obj = _object(record['fields'])
            # Older exports may retain only the explicit cache reference in Object JSON.
            ref = obj.get('subreddit')
            explicit = ref.get('$reference', ref.get('__ref', '')) if isinstance(ref, dict) else ''
            community_id = record['communityId']
            if not community_id and isinstance(explicit, str) and explicit.startswith('Subreddit:'):
                community_id = explicit[len('Subreddit:'):]
            for match in cached_communities.get((record['source'], community_id), []) if community_id else []:
                connect(record, match, 'Exact subreddit ID/reference; same normalized cache.')
            if record['scope'] and community_id:
                for match in communities.get((record['scope'], community_id), []):
                    connect(record, match, 'Exact subreddit ID; same account directory. Subscription/cache observations stay separate.')
            if kind == 'comment' and record['community']:
                matches = community_names.get((record['source'], str(record['community']).casefold()), [])
                if len({match['id'] for match in matches}) == 1:
                    for match in matches:
                        connect(record, match, 'Stored, validated permalink subreddit name; unique subreddit in the same cache.')
            for match in cached_profiles.get((record['source'], record['profileId']), []) if record['profileId'] else []:
                connect(record, match, 'Exact author ID; same normalized cache.')
            if record['container'] and record['profileId']:
                for match in profiles.get((record['container'], record['profileId']), []):
                    connect(record, match, 'Exact Reddit user ID; same application container. Account-specific states remain separate.')
        if kind == 'chat' and record['container'] and record.get('senderId'):
            candidates = matrix_users if record['table'] == 'reddit_chats' else profiles
            for match in candidates.get((record['container'], record['senderId']), []):
                connect(record, match, 'Exact stored sender ID; same application container. No username guessing.')


TABLE_STYLE = '''<style id="reddit-reader-wrap">
/* Report-local formatting only; original text, TSV and LAVA stay unchanged. */
.table-responsive td,.table-responsive th{white-space:pre-wrap!important;overflow-wrap:anywhere!important;word-break:normal!important;min-width:8rem;max-width:26rem}
.table-responsive td pre{white-space:pre-wrap!important;overflow-wrap:anywhere!important;max-width:26rem}
</style>'''


def wrap_tables(report):
    """Opt-in formatting of Reddit HTML pages, without touching exported field values."""
    count = 0
    report = Path(report)
    # Current iLEAPP flattens category pages into _HTML; earlier reports may nest them.
    pages = set((report / '_HTML').glob('Reddit_*.html'))
    pages.update((report / '_HTML' / 'Reddit').glob('*.html'))
    for page in sorted(pages):
        content = page.read_text(encoding='utf-8')
        if 'id="reddit-reader-wrap"' not in content and '</head>' in content:
            page.write_text(content.replace('</head>', TABLE_STYLE + '\n</head>', 1), encoding='utf-8')
            count += 1
    return count



def report_branding():
    """Embed iLEAPP's own local assets; no external stylesheet/font requests."""
    assets = Path(__file__).resolve().parents[2] / 'scripts' / '_elements'
    fonts = []
    files = {400: 'KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2',
             500: 'KFOlCnqEu92Fr1MmEU9fBBc4AMP6lQ.woff2'}
    for weight, filename in files.items():
        path = assets / 'fonts' / 'roboto' / 'v32' / filename
        if path.is_file() and path.stat().st_size < 1024 * 1024:
            encoded = base64.b64encode(path.read_bytes()).decode('ascii')
            fonts.append(f"@font-face{{font-family:Roboto;font-style:normal;font-weight:{weight};"
                         f"font-display:swap;src:url(data:font/woff2;base64,{encoded}) format('woff2')}}")
    logo = assets / 'iLEAPP_banner.png'
    brand = ''
    if logo.is_file() and logo.stat().st_size < 1024 * 1024:
        encoded = base64.b64encode(logo.read_bytes()).decode('ascii')
        brand = f'<img class="report-brand" alt="iLEAPP" src="data:image/png;base64,{encoded}">'
    return '\n'.join(fonts), brand


def _preserve_report(report, manifest_path, database_path):
    """Publish a complete backup directory only after both files are saved."""
    backup = report / '_Reader_Originals'
    if backup.exists():
        expected = (backup / '_lava_data.lava', backup / '_lava_artifacts.db')
        if not all(path.is_file() for path in expected):
            raise ValueError('Incomplete original report backup; use a fresh report copy')
        return
    with tempfile.TemporaryDirectory(prefix='_reader_backup_', dir=report) as temporary:
        staged = Path(temporary) / '_Reader_Originals'
        staged.mkdir()
        with sqlite3.connect(database_path.as_uri() + '?mode=ro', uri=True) as original:
            with sqlite3.connect(staged / '_lava_artifacts.db') as saved:
                original.backup(saved)
        shutil.copy2(manifest_path, staged / '_lava_data.lava')
        staged.rename(backup)


def add_navigation(report):
    """Add generated report shortcuts using LAVA's existing document/media contract.

    Only an explicitly selected output report is updated. Original extraction rows
    are untouched; original report database/manifest copies are retained first.
    """
    report = Path(report).resolve()
    manifest_path = report / '_lava_data.lava'
    database_path = report / '_lava_artifacts.db'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for category in manifest.get('artifacts', {}).values():
        for artifact in category:
            if artifact.get('tablename') == 'reddit_reader_navigation' and artifact.get('module') != 'RedditReader':
                raise ValueError('Navigation artifact name is already in use')
    for module in manifest.get('meta', {}).get('modules', []):
        if module.get('module_name') == 'RedditReader' and module.get('module_filename') != 'build_reddit_reader.py':
            raise ValueError('Navigation module name is already in use')
    _preserve_report(report, manifest_path, database_path)
    item_id = 'reddit-reader-generated-document-v1'
    reference_id = 'reddit-reader-generated-reference-v1'
    with sqlite3.connect(database_path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS _lava_media_items (id TEXT PRIMARY KEY, '
                   'source_path TEXT, extraction_path TEXT, type TEXT, metadata TEXT, '
                   'created_at INTEGER, updated_at INTEGER, is_embedded INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS _lava_media_references (id TEXT PRIMARY KEY, '
                   'media_item_id TEXT, module_name TEXT, artifact_name TEXT, name TEXT)')
        existing = db.execute('SELECT metadata FROM _lava_media_items WHERE id=?', (item_id,)).fetchone()
        if existing and json.loads(existing[0]).get('generator') != 'RedditReader':
            raise ValueError('Generated navigation identifier is already in use')
        existing_reference = db.execute('SELECT media_item_id,module_name FROM _lava_media_references WHERE id=?',
                                        (reference_id,)).fetchone()
        if existing_reference and existing_reference != (item_id, 'RedditReader'):
            raise ValueError('Generated navigation reference is already in use')
        db.execute('INSERT OR REPLACE INTO _lava_media_items VALUES (?,?,?,?,?,?,?,?)',
                   (item_id, 'Generated report navigation; no device source', 'Reddit_Reader.html',
                    'text/html', json.dumps({'generator': 'RedditReader', 'generated_report': True}),
                    None, None, 0))
        db.execute('INSERT OR REPLACE INTO _lava_media_references VALUES (?,?,?,?,?)',
                   (reference_id, item_id, 'RedditReader', 'Reddit Reader (generated report link)',
                    'Open Reddit Reader'))
        exists = db.execute("SELECT name FROM sqlite_master WHERE name='reddit_reader_navigation'").fetchone()
        if exists:
            columns = [column[1] for column in db.execute('PRAGMA table_info(reddit_reader_navigation)')]
            if columns != ['reader_link', 'description']:
                raise ValueError('Navigation table name is already in use')
            if db.execute('SELECT count(*) FROM reddit_reader_navigation WHERE reader_link != ?',
                          (reference_id,)).fetchone()[0]:
                raise ValueError('Navigation table contains unrecognized rows')
        db.execute('CREATE TABLE IF NOT EXISTS reddit_reader_navigation (reader_link TEXT PRIMARY KEY, description TEXT)')
        db.execute('INSERT OR REPLACE INTO reddit_reader_navigation VALUES (?,?)',
                   (reference_id, 'Generated navigation only. Click Open Reddit Reader to open the local linked report.'))
    artifact = {'artifact_key': 'reddit_reader_navigation', 'name': 'Reddit Reader (generated report link)',
                'tablename': 'reddit_reader_navigation', 'module': 'RedditReader',
                'column_map': {'reader_link': 'Open Reddit Reader', 'description': 'Description'},
                'object_columns': [{'name': 'reader_link', 'type': 'media'}],
                'record_count': 1, 'artifact_icon': 'brand-reddit'}
    categories = manifest.setdefault('artifacts', {})
    navigation = [entry for entry in categories.get('Report Navigation', [])
                  if entry.get('tablename') != 'reddit_reader_navigation']
    manifest['artifacts'] = {'Report Navigation': [artifact, *navigation],
                             **{key: value for key, value in categories.items() if key != 'Report Navigation'}}
    modules = manifest.setdefault('meta', {}).setdefault('modules', [])
    modules[:] = [module for module in modules if module.get('module_name') != 'RedditReader']
    modules.append({'module_name': 'RedditReader', 'module_filename': 'build_reddit_reader.py',
                    'artifacts': [{**artifact, 'category': 'Report Navigation',
                                   'description': 'Generated report shortcut; not an extracted artifact.',
                                   'notes': 'Linked Reddit content, history and chats. This entry is navigation, not evidence.'}]})
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding='utf-8')
    folder = report / '_HTML'
    folder.mkdir(exist_ok=True)
    (folder / 'Reddit_Reader.html').write_text('<!doctype html><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=../Reddit_Reader.html">'
        '<a href="../Reddit_Reader.html">Open Reddit Reader</a>', encoding='utf-8')
    pages = set(folder.glob('*.html')) | set((folder / 'Reddit').glob('*.html'))
    count = 0
    for page in sorted(pages):
        content = page.read_text(encoding='utf-8')
        if 'id="reddit-reader-link"' in content or '</nav>' not in content:
            continue
        target = html.escape(os.path.relpath(folder / 'Reddit_Reader.html', page.parent).replace(os.sep, '/'), quote=True)
        link = f'<a class="nav-link text-white" id="reddit-reader-link" href="{target}">Reddit Reader</a>'
        page.write_text(content.replace('</nav>', link + '</nav>', 1), encoding='utf-8')
        count += 1
    return count


def build(report, output=None, format_tables=False, navigation=False):
    """Write the workspace; table formatting is an explicit, optional report-only edit."""
    report = Path(report)
    destination = Path(output) if output else report / 'Reddit_Reader.html'
    if navigation and destination.resolve() != (report / 'Reddit_Reader.html').resolve():
        raise ValueError('Navigation requires the standard report-local Reddit_Reader.html destination')
    records = load_records(report)
    payload = json.dumps(records, ensure_ascii=True).replace('<', r'\u003c')
    page = Path(__file__).with_name('reddit_reader.html').read_text(encoding='utf-8')
    controls = Path(__file__).with_name('reddit_reader_controls.js').read_text(encoding='utf-8')
    fonts, brand = report_branding()
    page = page.replace('__CONTROLS__', controls).replace('__REPORT_FONTS__', fonts).replace('__REPORT_BRAND__', brand)
    destination.write_text(page.replace('__RECORDS__', payload), encoding='utf-8')
    if format_tables:
        wrap_tables(report)
    if navigation:
        add_navigation(report)
    return len(records)


def main():
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument('report', type=Path, help='iLEAPP report containing _lava_data.lava')
    command.add_argument('--wrap-tables', action='store_true', help='Also wrap long cells in the report\'s Reddit HTML tables')
    command.add_argument('--add-navigation', action='store_true', help='Add iLEAPP links and a generated LAVA navigation entry, preserving the original report first')
    args = command.parse_args()
    count = build(args.report, format_tables=args.wrap_tables, navigation=args.add_navigation)
    print(f'Wrote Reddit_Reader.html containing {count} exported records')


if __name__ == '__main__':
    main()
