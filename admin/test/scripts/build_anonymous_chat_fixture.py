"""Build a shareable Anonymous Chat iLEAPP test fixture.

The fixture contains synthetic SQLite/plist/JSON metadata only.  It contains no
casework and no media payloads.  Media-manager behavior is covered separately by
the metadata-only smoke test, where the manager is mocked.
"""

from __future__ import annotations

import argparse
import json
import plistlib
import sqlite3
import zipfile
from pathlib import Path


DATA_UUID = '11111111-1111-4111-8111-111111111111'
BUNDLE_UUID = '22222222-2222-4222-8222-222222222222'
PHOTO_UUID = 'AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA'
BASE_TIME = 1770000000

DATA_ROOT = Path(
    'private/var/mobile/Containers/Data/Application'
) / DATA_UUID
BUNDLE_ROOT = Path(
    'private/var/containers/Bundle/Application'
) / BUNDLE_UUID


def write_plist(path: Path, values: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as handle:
        plistlib.dump(values, handle, sort_keys=True)


def build_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
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
                    'https://example.invalid/synthetic/photo.png',
                    'image/png', 'image', 1234, None, 'cache', '1', None,
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
                    'message-3', 'conversation-1', 'UUID-PHOTO',
                    'Synthetic Photos-linked metadata message',
                    None, 'image/png', 'image', 5678, None, 'photos', '1', None,
                    None, None, None, json.dumps({
                        'media_id': f'ph://{PHOTO_UUID}/L0/001',
                    }, separators=(',', ':')), None,
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
            (f'ph://{PHOTO_UUID}/L0/001', 'SYNTH001.PNG', None, BASE_TIME + 2),
        )


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

    photos_path = output_root / 'private/var/mobile/Media/PhotoData/Photos.sqlite'
    photos_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(photos_path) as db:
        db.execute(
            'CREATE TABLE ZASSET (ZUUID TEXT, ZDIRECTORY TEXT, ZFILENAME TEXT)'
        )
        db.execute(
            'INSERT INTO ZASSET VALUES (?, ?, ?)',
            (PHOTO_UUID, 'DCIM/100APPLE', 'SYNTH001.PNG'),
        )

    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(output_root.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(output_root).as_posix())
    return archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-root',
        type=Path,
        default=Path(__file__).parent / 'testdata' / 'anonymousChat_synthetic_extraction',
    )
    args = parser.parse_args()
    archive = build_fixture(args.output_root)
    print(f'Created synthetic extraction archive: {archive}')
    print(f'Fixture root: {args.output_root}')


if __name__ == '__main__':
    main()
