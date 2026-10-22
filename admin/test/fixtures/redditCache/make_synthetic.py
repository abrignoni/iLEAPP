"""Build only fabricated data for the committed regression snapshots."""
import fnmatch
import json
import plistlib
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from admin.test.scripts.test_reddit_cache_history import cache
from scripts.artifacts import redditCache as parser


def main():
    repo = Path(__file__).resolve().parents[4]
    module = 'redditCache'
    destination = repo / 'admin/test/cases/data' / module
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for account in ['alpha', 'beta']:
            p = cache(root, account, {
                'SubredditPost:t3_demo': {'id': 't3_demo', 'title': 'Synthetic post',
                    'createdAt': ('2024-01-02T03:04:05.125000+0000' if account == 'alpha' else '2024-01-02T03:04:05.12+0000'), 'isOwnPost': False,
                    'content': {'$reference': 'body'}, 'subreddit': {'$reference': 'Subreddit:t5_demo'}},
                'body': {'markdown': 'Fabricated body ' + account},
                'Comment:t1_demo': {'id': 't1_demo', 'content': {'$reference': 'body'},
                    'createdAt': ('2024-01-02T03:04:05.1+0000' if account == 'alpha' else '2024-01-02T03:04:05.12345+0000'),
                    'editedAt': ('2024-01-02T03:04:06.1234+0000' if account == 'alpha' else '2024-01-02T03:04:06.125+0000'),
                    'authorInfo': {'$reference': 'Redditor:t2_demo'}, 'isSaved': False,
                    'permalink': '/r/SyntheticCommunity/comments/demo/synthetic/demo/'},
                'Redditor:t2_demo': {'id': 't2_demo', 'displayName': 'Synthetic ' + account},
                'Subreddit:t5_demo': {'id': 't5_demo', 'name': 'SyntheticCommunity', 'isSubscribed': False},
            })
            (p.parent / 'PostHistory').write_bytes(plistlib.dumps({
                'kPostIDDictionaryKey': ['t3_demo'], 'kInfoDictionaryKey': {
                    't3_demo': {'kGlanceInfoKey': False}, 't3_extra': {'kGlanceInfoKey': True}}}))
            (p.parent / 'SubredditHistory').write_bytes(plistlib.dumps(['t5_demo']))
        draft = root/'Documents/release02/accountData/alpha/commentDrafts/CommentDraftEntity.sqlite'
        draft.parent.mkdir(parents=True)
        with sqlite3.connect(draft) as db:
            db.execute('CREATE TABLE ZCOMMENTDRAFTENTITY (Z_PK,ZMODIFIEDDATE,ZCONTENT,ZID,ZPARENTCOMMENTPK,ZPOSTPK,ZPOSTTITLE)')
            db.execute('INSERT INTO ZCOMMENTDRAFTENTITY VALUES (1,0,\'Synthetic draft\',\'draft-a\',NULL,\'t3_demo\',\'Synthetic post\')')
        for name, meta in parser.__artifacts_v2__.items():
            paths = [p for p in root.rglob('*') if p.is_file() and any(
                fnmatch.fnmatchcase('root/' + p.relative_to(root).as_posix(), pat) for pat in meta['paths'])]
            with zipfile.ZipFile(destination / f'testdata.{module}.{name}.synthetic.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for p in sorted(paths):
                    entry = zipfile.ZipInfo(p.relative_to(root).as_posix(), (2024, 1, 1, 0, 0, 0))
                    z.writestr(entry, p.read_bytes())
            artifacts[name] = {'search_patterns': list(meta['paths']), 'file_count': len(paths)}
    case = {'synthetic': {'description': 'Fabricated cache, multi-account, history and draft records.',
                         'maker': '@CyberMike81', 'os_name': 'iOS', 'os_version': 'synthetic',
                         'image_info': {'os_name': 'iOS', 'os_version': 'synthetic'},
                         'artifacts': artifacts}}
    (repo / f'admin/test/cases/testdata.{module}.json').write_text(json.dumps(case, indent=2) + '\n')


if __name__ == '__main__':
    main()
