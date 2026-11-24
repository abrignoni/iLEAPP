"""Ph036 reads CollectionShare albums, posts, comments and reactions from a synthetic store."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import Ph036iCloudCollectionSharesNAD as module

COCOA = 817000000.0  # seconds after 2001-01-01, a time in 2026


class Context:
    def __init__(self, files):
        self.files = [str(f) for f in files]

    def get_files_found(self):
        return self.files

    @staticmethod
    def get_relative_path(path):
        return path


def build(directory, ios27=True):
    path = Path(directory) / 'PhotoData' / 'Photos.sqlite'
    path.parent.mkdir(parents=True)
    db = sqlite3.connect(path)
    db.executescript('''
    CREATE TABLE Z_PRIMARYKEY (Z_ENT INTEGER, Z_NAME VARCHAR, Z_SUPER INTEGER, Z_MAX INTEGER);
    CREATE TABLE ZSHARE (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, ZCREATIONDATE TIMESTAMP,
        ZLASTMODIFIEDDATE TIMESTAMP, ZSTARTDATE TIMESTAMP, ZENDDATE TIMESTAMP, ZEXPIRYDATE TIMESTAMP,
        ZTRASHEDDATE TIMESTAMP, ZTITLE VARCHAR, ZASSETCOUNT INTEGER, ZPHOTOSCOUNT INTEGER,
        ZVIDEOSCOUNT INTEGER, ZSHAREURL VARCHAR, ZPUBLICSHAREURL VARCHAR, ZSCOPEIDENTIFIER VARCHAR,
        ZUUID VARCHAR, ZSCOPETYPE INTEGER, ZCOLLECTIONSHAREKIND INTEGER, ZPUBLICPERMISSION INTEGER,
        ZCURRENTPARTICIPANTROLE INTEGER, ZTRASHEDSTATE INTEGER);
    CREATE TABLE ZSHAREPARTICIPANT (Z_PK INTEGER PRIMARY KEY, ZSHARE INTEGER, ZEMAILADDRESS VARCHAR,
        ZPHONENUMBER VARCHAR, ZISCURRENTUSER INTEGER);
    ''')
    asset_extra = ', ZSHAREPOST INTEGER' if ios27 else ''
    db.execute(f'''CREATE TABLE ZASSET (Z_PK INTEGER PRIMARY KEY, ZDATECREATED TIMESTAMP, ZADDEDDATE TIMESTAMP,
        ZDIRECTORY VARCHAR, ZFILENAME VARCHAR, ZUUID VARCHAR, ZSAVEDASSETTYPE INTEGER, ZTRASHEDSTATE INTEGER,
        ZCOLLECTIONSHARE INTEGER{asset_extra})''')
    comment_extra = (', ZREACTTEXT VARCHAR, ZREACTEDASSET INTEGER, ZCOMMENTEDPOST INTEGER, ZREACTEDPOST INTEGER,'
                     ' ZCONTRIBUTORUSERIDENTIFIER VARCHAR, ZLASTEDITEDDATE TIMESTAMP' if ios27 else '')
    db.execute(f'''CREATE TABLE ZCLOUDSHAREDCOMMENT (Z_PK INTEGER PRIMARY KEY, ZCOMMENTDATE TIMESTAMP,
        ZCOMMENTCLIENTDATE TIMESTAMP, ZCOMMENTTEXT VARCHAR, ZCOMMENTTYPE VARCHAR, ZISLIKE INTEGER,
        ZISMYCOMMENT INTEGER, ZCOMMENTEDASSET INTEGER, ZLIKEDASSET INTEGER, ZSHAREPARTICIPANT INTEGER,
        ZCOMMENTERHASHEDPERSONID VARCHAR, ZCLOUDGUID VARCHAR{comment_extra})''')
    # 72 is CollectionShare here on purpose: the module must read the number, not assume one.
    db.executemany('INSERT INTO Z_PRIMARYKEY (Z_ENT, Z_NAME) VALUES (?, ?)',
                   [(71, 'Share'), (72, 'CollectionShare'), (73, 'LibraryScope')])
    db.execute("INSERT INTO ZSHARE (Z_PK, Z_ENT, ZCREATIONDATE, ZTITLE, ZSCOPETYPE) VALUES (1, 72, ?, 'album', 7)",
               (COCOA,))
    db.execute("INSERT INTO ZSHARE (Z_PK, Z_ENT, ZCREATIONDATE, ZTITLE) VALUES (2, 73, ?, 'library')", (COCOA,))
    db.execute("INSERT INTO ZSHAREPARTICIPANT VALUES (1, 1, 'owner@example.invalid', NULL, 1)")
    if ios27:
        db.execute('''CREATE TABLE ZSHAREPOST (Z_PK INTEGER PRIMARY KEY, ZSHARE INTEGER, ZCONTRIBUTOR INTEGER,
            ZCREATIONDATE TIMESTAMP, ZLASTEDITEDDATE TIMESTAMP, ZCAPTION VARCHAR, ZCOMMENTSCOUNT INTEGER,
            ZREACTIONSCOUNT INTEGER, ZCONTRIBUTORUSERIDENTIFIER VARCHAR, ZCLOUDGUID VARCHAR)''')
        db.execute('INSERT INTO ZSHAREPOST (Z_PK, ZSHARE, ZCONTRIBUTOR, ZCREATIONDATE) VALUES (1, 1, 1, ?)', (COCOA,))
        db.execute("INSERT INTO ZASSET (Z_PK, ZDATECREATED, ZDIRECTORY, ZFILENAME, ZCOLLECTIONSHARE, ZSHAREPOST)"
                   " VALUES (10, ?, 'E', 'STEM.HEIC', 1, 1)", (COCOA,))
        db.execute("INSERT INTO ZASSET (Z_PK, ZDATECREATED, ZDIRECTORY, ZFILENAME, ZCOLLECTIONSHARE, ZSHAREPOST)"
                   " VALUES (11, ?, 'F', 'OTHER.HEIC', 1, 1)", (COCOA,))
        # an asset in an old-style album, no CollectionShare: its like must not be reported
        db.execute("INSERT INTO ZASSET (Z_PK, ZDATECREATED, ZDIRECTORY, ZFILENAME) VALUES (12, ?, 'G', 'OLD.HEIC')",
                   (COCOA,))
        db.executemany('INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK, ZCOMMENTDATE, ZREACTTEXT, ZREACTEDASSET, ZISLIKE,'
                       ' ZCOMMENTTEXT, ZCOMMENTEDASSET, ZLIKEDASSET, ZSHAREPARTICIPANT) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       [(1, COCOA, 'r', 10, 0, None, None, None, 1),
                        (2, COCOA + 1, None, None, 0, 'text', 11, None, 1),
                        (3, COCOA + 2, None, None, 1, None, None, 12, None)])
    else:
        db.execute("INSERT INTO ZASSET (Z_PK, ZDATECREATED, ZDIRECTORY, ZFILENAME, ZCOLLECTIONSHARE)"
                   " VALUES (10, ?, 'E', 'STEM.HEIC', 1)", (COCOA,))
        db.execute('INSERT INTO ZCLOUDSHAREDCOMMENT (Z_PK, ZCOMMENTDATE, ZCOMMENTTEXT, ZCOMMENTEDASSET,'
                   " ZSHAREPARTICIPANT) VALUES (1, ?, 'text', 10, 1)", (COCOA,))
    db.commit()
    db.close()
    derivatives = path.parent / 'UBF' / 'scopes' / 'collectionshare' / 'resources' / 'derivatives'
    (derivatives / 'E').mkdir(parents=True)
    (derivatives / 'masters' / 'E').mkdir(parents=True)
    (derivatives / 'E' / 'STEM_1_102_o.jpeg').write_bytes(b'\xff\xd8\xff\xe0' + b'\0' * 20)
    (derivatives / 'E' / 'STEM_2_101_o.mov').write_bytes(b'\0\0\0\x14ftypqt  ' + b'\0' * 8)
    (derivatives / 'masters' / 'E' / 'STEM_4_5005_c.jpeg').write_bytes(b'\xff\xd8\xff\xe0' + b'\0' * 4)
    # same stem in another directory must not match asset 10
    (derivatives / 'F').mkdir()
    (derivatives / 'F' / 'STEM_1_102_o.jpeg').write_bytes(b'\xff\xd8\xff\xe0')
    return path, [path] + sorted(p for p in derivatives.rglob('*') if p.is_file())


def run(key, files):
    with patch.object(module, 'check_in_media', side_effect=lambda p, n: 'media:' + Path(p).parent.name + '/' + n):
        headers, rows, source = getattr(module, key).__wrapped__(Context(files))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], source


class TestPhotosCollectionShares(unittest.TestCase):
    def test_ios27_albums_posts_reactions(self):
        with tempfile.TemporaryDirectory() as directory:
            path, files = build(directory)
            albums, source = run('Ph036_1iCloudCollectionShareAlbumsPhDaPsql', files)
            self.assertEqual(source, str(path))
            self.assertEqual([(a['Title'], a['Post Count'], a['Participant Count'], a['ZSCOPETYPE Raw Value'])
                              for a in albums], [('album', 1, 1, 7)])
            self.assertEqual(albums[0]['Creation Date'].year, 2026)

            posts, _ = run('Ph036_2iCloudCollectionSharePostsPhDaPsql', files)
            self.assertEqual([(p['zAsset-zPK'], p['Media']) for p in posts],
                             [(10, 'media:E/STEM_1_102_o.jpeg'), (11, '')])
            self.assertEqual(posts[0]['Resource Files'],
                             'STEM_1_102_o.jpeg (JPEG, 24 bytes); STEM_2_101_o.mov (QuickTime, 20 bytes); '
                             'masters/STEM_4_5005_c.jpeg (JPEG, 8 bytes)')
            self.assertEqual(posts[0]['Contributor Is Current User'], 1)

            comments, _ = run('Ph036_3iCloudCollectionShareCommentsReactionsPhDaPsql', files)
            self.assertEqual([(c['Kind'], c['Linked By'], c['zAsset-zPK'], c['zSharePost-zPK']) for c in comments],
                             [('Reaction', 'ZREACTEDASSET', 10, 1), ('Comment', 'ZCOMMENTEDASSET', 11, 1)])
            self.assertEqual(comments[0]['Reaction'], 'r')
            self.assertEqual(comments[0]['Media'], 'media:E/STEM_1_102_o.jpeg')

    def test_ios26_shape_without_posts_or_reaction_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            _, files = build(directory, ios27=False)
            albums, _ = run('Ph036_1iCloudCollectionShareAlbumsPhDaPsql', files)
            self.assertEqual([(a['Title'], a['Post Count']) for a in albums], [('album', None)])
            posts, source = run('Ph036_2iCloudCollectionSharePostsPhDaPsql', files)
            self.assertEqual((posts, source), ([], files[0].__str__()))
            comments, _ = run('Ph036_3iCloudCollectionShareCommentsReactionsPhDaPsql', files)
            self.assertEqual([(c['Kind'], c['Linked By'], c['zSharePost-zPK']) for c in comments],
                             [('Comment', 'ZCOMMENTEDASSET', None)])

    def test_store_without_collection_share_entity(self):
        with tempfile.TemporaryDirectory() as directory:
            path, files = build(directory)
            db = sqlite3.connect(path)
            db.execute("DELETE FROM Z_PRIMARYKEY WHERE Z_NAME = 'CollectionShare'")
            db.commit()
            db.close()
            for key in ('Ph036_1iCloudCollectionShareAlbumsPhDaPsql', 'Ph036_2iCloudCollectionSharePostsPhDaPsql',
                        'Ph036_3iCloudCollectionShareCommentsReactionsPhDaPsql'):
                self.assertEqual(run(key, files), ([], str(path)))


if __name__ == '__main__':
    unittest.main()
