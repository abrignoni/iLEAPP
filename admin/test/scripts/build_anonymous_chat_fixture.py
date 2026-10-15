"""Build a synthetic Anonymous Chat & Fun extraction for iLEAPP tests.

Every value is invented. The images are 1x1 PNGs written here. The layout follows
the paths the module reads; the field values do not come from a real device.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sqlite3
import struct
import zipfile
import zlib
from contextlib import closing
from pathlib import Path


DATA_UUID = '11111111-1111-4111-8111-111111111111'
BUNDLE_UUID = '22222222-2222-4222-8222-222222222222'
BASE_TIME = 1770000000
CACHED_URL = 'https://example.invalid/synthetic/photo.png'
UNCACHED_URL = 'https://example.invalid/synthetic/missing.jpg'
UNREFERENCED_URL = 'https://example.invalid/synthetic/never-stored.png'
SDIMAGECACHE = 'Library/Caches/com.hackemist.SDImageCache/default'

DATA_ROOT = Path(
    'private/var/mobile/Containers/Data/Application'
) / DATA_UUID
BUNDLE_ROOT = Path(
    'private/var/containers/Bundle/Application'
) / BUNDLE_UUID


def png(tag: int) -> bytes:
    """A valid 1x1 RGB PNG whose single pixel is (tag, 0, 0)."""
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data)))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(bytes([0, tag, 0, 0]))) + chunk(b'IEND', b''))


def cache_name(url: str) -> str:
    """SDWebImage's default disk-cache file name: MD5 of the URL plus its extension."""
    return hashlib.md5(url.encode('utf-8')).hexdigest() + '.' + url.rsplit('.', 1)[1]


def write_plist(path: Path, values: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as handle:
        plistlib.dump(values, handle, sort_keys=True)


def build_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.executescript(
            '''
            CREATE TABLE conversations (
                conversation_id TEXT,
                from_username TEXT,
                to_username TEXT,
                anonymous_status INTEGER,
                anonymous_color TEXT,
                anonymous_reveal INTEGER,
                anonymous_alert INTEGER,
                anonymous_alias TEXT,
                trusted_media INTEGER,
                pin_status INTEGER,
                unread_count INTEGER,
                last_message_time INTEGER,
                seen_message_id TEXT,
                seen_message_time INTEGER,
                conversation_time INTEGER
            );
            CREATE TABLE messages (
                message_id TEXT,
                conversation_id TEXT,
                msg_id TEXT,
                message TEXT,
                media_url TEXT,
                media_mime_type TEXT,
                media_ac_type TEXT,
                media_size INTEGER,
                media_duration REAL,
                media_origin TEXT,
                media_show TEXT,
                media_spotify TEXT,
                anonymous_reveal TEXT,
                message_reaction TEXT,
                message_reply TEXT,
                message_info TEXT,
                message_verified_profile_link TEXT,
                message_time INTEGER,
                sender INTEGER,
                sender_name TEXT,
                send_time INTEGER
            );
            CREATE TABLE blocked (
                block_id TEXT,
                from_username TEXT,
                to_username TEXT
            );
            CREATE TABLE media (
                media_id TEXT,
                media_name TEXT,
                media_data TEXT,
                media_time INTEGER
            );
            '''
        )
        db.executemany(
            'INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [(
                'conversation-1',
                'local.synthetic',
                'remote.synthetic',
                1,
                'blue',
                0,
                0,
                None,
                0,
                0,
                0,
                BASE_TIME + 2,
                'message-3',
                BASE_TIME + 2,
                BASE_TIME,
            )],
        )
        db.executemany(
            'INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [
                (
                    'message-1', 'conversation-1', 'UUID-OUT',
                    'Synthetic outgoing message',
                    CACHED_URL,
                    'image/png', 'image', len(png(1)), None, 'cache', '1', None,
                    None, None, None, None, None,
                    BASE_TIME, 0, 'local.synthetic', BASE_TIME,
                ),
                (
                    'message-2', 'conversation-1', 'UUID-IN',
                    'Synthetic incoming message',
                    None, None, None, None, None, None, None, None,
                    None, None, None, None, None,
                    BASE_TIME + 1, 1, 'remote.synthetic', BASE_TIME + 1,
                ),
                (
                    'message-3', 'conversation-1', 'UUID-MEDIA',
                    'Synthetic media message with no cached file',
                    UNCACHED_URL, 'image/jpeg', 'image', 5678, None, 'cache', '1', None,
                    None, None, None, None, None,
                    BASE_TIME + 2, 1, 'remote.synthetic', BASE_TIME + 2,
                ),
            ],
        )
        db.execute(
            'INSERT INTO blocked VALUES (?, ?, ?)',
            ('block-1', 'local.synthetic', 'blocked.synthetic'),
        )
        db.execute(
            'INSERT INTO media VALUES (?, ?, ?, ?)',
            ('media-1', 'SYNTH001.PNG', None, BASE_TIME + 2),
        )
        db.commit()


def build_fixture(output_root: Path) -> Path:
    output_root = output_root.resolve()
    archive = output_root.parent / 'anonymousChat_synthetic_extraction.zip'
    # Never delete a caller-supplied directory or overwrite an existing archive.
    if output_root.exists() and (not output_root.is_dir() or any(output_root.iterdir())):
        raise FileExistsError(f'Choose a new or empty fixture directory: {output_root}')
    if archive.exists():
        raise FileExistsError(f'Refusing to replace an existing archive: {archive}')
    output_root.mkdir(parents=True, exist_ok=True)

    write_plist(
        output_root / DATA_ROOT / '.com.apple.mobile_container_manager.metadata.plist',
        {'MCMMetadataIdentifier': 'com.anonimchat.app'},
    )
    write_plist(
        output_root / DATA_ROOT / 'Library/Preferences/com.anonimchat.app.plist',
        {'synthetic_fixture': True, 'fixture_version': 1},
    )
    manifest_path = (
        output_root / DATA_ROOT / 'Library/Application Support/'
        'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json'
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes((
        json.dumps({'signedInUsername': 'local.synthetic',
                    'synthetic_fixture': True, 'record_count': 3}, indent=2) + '\n'
    ).encode('utf-8'))
    build_database(output_root / DATA_ROOT / 'Library/LocalDatabase/anonimchat.db')

    write_plist(
        output_root / BUNDLE_ROOT / '.com.apple.mobile_container_manager.metadata.plist',
        {'MCMMetadataIdentifier': 'com.anonimchat.app'},
    )
    write_plist(
        output_root / BUNDLE_ROOT / 'AnonimChat.app/Info.plist',
        {
            'CFBundleIdentifier': 'com.anonimchat.app',
            'CFBundleDisplayName': 'Anonymous Chat Synthetic',
            'CFBundleShortVersionString': '0.0.1',
            'CFBundleVersion': '1',
        },
    )
    write_plist(
        output_root / BUNDLE_ROOT / 'iTunesMetadata.plist',
        {
            'softwareVersionBundleId': 'com.anonimchat.app',
            'itemName': 'Anonymous Chat Synthetic',
            'bundleShortVersionString': '0.0.1',
            'bundleVersion': '1',
            'artistName': 'Synthetic Fixture',
            'purchaseDate': '2026-01-01T00:00:00Z',
        },
    )

    media = {
        # Linked: named for message-1's stored URL.
        DATA_ROOT / SDIMAGECACHE / cache_name(CACHED_URL): png(1),
        # In the cache, but no message stores its URL.
        DATA_ROOT / SDIMAGECACHE / cache_name(UNREFERENCED_URL): png(2),
        # Same size as the linked file, outside the cache: must never be linked.
        DATA_ROOT / 'Documents/decoy.png': png(3),
        # Ships inside the app bundle: must never be reported.
        BUNDLE_ROOT / 'AnonimChat.app/icon.png': png(4),
    }
    for relative, payload in media.items():
        (output_root / relative).parent.mkdir(parents=True, exist_ok=True)
        (output_root / relative).write_bytes(payload)

    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(output_root.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(output_root).as_posix())
    return archive


def build_appdomain_archive(output_archive: Path) -> Path:
    """Create a path-only AppDomain fixture; Application Info does not read database bytes."""
    output_archive = output_archive.resolve()
    output_archive.parent.mkdir(parents=True, exist_ok=True)
    if output_archive.exists():
        raise FileExistsError(f'Refusing to replace an existing archive: {output_archive}')

    appdomain_root = DATA_ROOT.parent / 'com.anonimchat.app'
    member = appdomain_root / 'Library/LocalDatabase/anonimchat.db'
    with zipfile.ZipFile(output_archive, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member.as_posix(), b'')
    return output_archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-root',
        type=Path,
        default=Path(__file__).parent / 'testdata' / 'anonymousChat_synthetic_extraction',
    )
    parser.add_argument(
        '--appdomain-archive',
        type=Path,
        help='write a synthetic ZIP with files under the reconstructed AppDomain path',
    )
    args = parser.parse_args()
    if args.appdomain_archive:
        archive = build_appdomain_archive(args.appdomain_archive)
    else:
        archive = build_fixture(args.output_root)
    print(f'Created synthetic extraction archive: {archive}')
    if not args.appdomain_archive:
        print(f'Fixture root: {args.output_root}')


if __name__ == '__main__':
    main()
