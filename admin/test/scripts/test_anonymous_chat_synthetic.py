"""Metadata-only smoke tests for the Anonymous Chat parser.

These tests deliberately use synthetic paths and mocked Media Manager calls.  They
exercise correlation and LAVA field wiring without opening, hashing, or uploading a
casework media payload.
"""

# These tests intentionally exercise private parser helpers and data builders.
# pylint: disable=protected-access

import hashlib
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from scripts.artifacts import anonymousChat as module


DATA_UUID = '11111111-1111-4111-8111-111111111111'
PHOTO_UUID = 'AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA'
BASE_TIME = datetime(2030, 1, 1, tzinfo=timezone.utc)
PHOTO_URL = 'https://example.invalid/synthetic/photo.png'
CACHE_KEY = hashlib.md5(
    PHOTO_URL.encode('utf-8'), usedforsecurity=False).hexdigest()


class SyntheticSeeker:
    """Return synthetic staged names; never opens a source file."""

    def search(self, pattern, return_on_first_hit=False):
        if pattern == '*/Media/PhotoData/Photos.sqlite*':
            return ['C:/synthetic/Photos.sqlite']
        if return_on_first_hit:
            return 'C:/synthetic/' + pattern.rstrip('/').rsplit('/', 1)[-1]
        return []


class SyntheticContext:
    def __init__(self):
        self.files = []
        self.seeker = SyntheticSeeker()

    def get_files_found(self):
        return self.files

    def get_seeker(self):
        return self.seeker

    def get_artifact_name(self):
        return 'Anonymous Chat - Synthetic Media'

    def get_relative_path(self, path):
        return path


def _reference(kind, **values):
    result = {
        'kind': kind,
        'reference': '',
        'source': 'synthetic database',
        'message_timestamp': '',
        'media_timestamp': '',
        'conversation_id': '',
        'message_id': '',
        'message_uuid': '',
        'direction': '',
        'sender': '',
        'recipient': '',
        'media_id': '',
        'filename': '',
        'mime': '',
        'size': '',
        'duration': '',
        'media_origin': '',
        'media_show': '',
    }
    result.update(values)
    return result


class AnonymousChatSyntheticTests(unittest.TestCase):
    def test_direction_and_other_party_use_remote_participant(self):
        outgoing = {
            'sender_flag': 0,
            'sender_name': 'local.synthetic',
            'from_username': 'local.synthetic',
            'to_username': 'remote.synthetic',
        }
        incoming = {
            'sender_flag': 1,
            'sender_name': 'remote.synthetic',
            'from_username': 'local.synthetic',
            'to_username': 'remote.synthetic',
        }

        accounts = {'local.synthetic'}
        self.assertEqual(module._direction(outgoing, accounts), 'Outgoing')
        self.assertEqual(module._direction(incoming, accounts), 'Incoming')
        self.assertEqual(module._other_party(outgoing, accounts), 'remote.synthetic')
        self.assertEqual(module._other_party(incoming, accounts), 'remote.synthetic')

    def test_mocked_media_correlation_checks_in_cache_and_photos_files(self):
        cache_reference = _reference(
            'Message Attachment Reference',
            reference=PHOTO_URL,
            message_timestamp=BASE_TIME,
            conversation_id='conversation-cache',
            message_id='cache-message',
            message_uuid='CACHE-UUID',
            direction='Outgoing',
            sender='local.synthetic',
            recipient='remote.synthetic',
            filename='photo.png',
            mime='image/png',
            size=1234,
        )
        photo_reference = _reference(
            'Message Attachment Reference',
            message_timestamp=BASE_TIME,
            conversation_id='conversation-photo',
            message_id='photo-message',
            message_uuid='PHOTO-UUID',
            direction='Incoming',
            sender='remote.synthetic',
            recipient='local.synthetic',
            mime='image/png',
            size=5678,
            join_tokens=['ph://' + PHOTO_UUID + '/L0/001'],
        )
        media_table_reference = _reference(
            'Media Table Metadata',
            reference='SYNTH001.PNG',
            media_timestamp=BASE_TIME,
            media_id='ph://' + PHOTO_UUID + '/L0/001',
            filename='SYNTH001.PNG',
        )
        references = [cache_reference, photo_reference, media_table_reference]
        cache_path = (
            'private/var/mobile/Containers/Data/Application/' + DATA_UUID +
            '/Library/Caches/com.hackemist.sdimagecache/default/' + CACHE_KEY
        )
        photo_path = 'private/var/mobile/Media/DCIM/100APPLE/SYNTH001.PNG'
        entries = [
            {
                'path': cache_path,
                'size': 1234,
                'created': '',
                'modified': '',
                'modified_at': BASE_TIME,
                'accessed': '',
                'kind': 'synthetic',
            },
            {
                'path': photo_path,
                'size': 5678,
                'created': '',
                'modified': '',
                'modified_at': BASE_TIME,
                'accessed': '',
                'kind': 'synthetic',
            },
        ]
        context = SyntheticContext()
        checkins = Mock(side_effect=lambda path, **_kwargs:
                        'media-ref-cache' if CACHE_KEY in str(path)
                        else 'media-ref-photo')

        with patch.object(module, '_target_containers',
                          return_value=(set(), {DATA_UUID}, set(), {})), \
                patch.object(module, '_attachment_references',
                              return_value=references), \
                patch.object(module, '_iter_source_entries',
                             return_value=entries), \
                patch.object(module, '_query_rows', return_value=[{
                    'uuid': PHOTO_UUID,
                    'directory': 'DCIM/100APPLE',
                    'filename': 'SYNTH001.PNG',
                }]), \
                patch.object(module, '_signature_from_entry',
                             return_value=('PNG', 'Image', 'Synthetic signature')), \
                patch.object(module, 'check_in_media', checkins):
            rows = module._media_rows([], context)

        filesystem_rows = [row for row in rows
                           if row['kind'] == 'Filesystem Media']
        # The Photos original has separate media-table and message associations.
        self.assertEqual(len(filesystem_rows), 3)
        self.assertEqual(checkins.call_count, 2)
        self.assertEqual(
            {row['media_ref'] for row in filesystem_rows},
            {'media-ref-cache', 'media-ref-photo'},
        )

        cache_row = next(row for row in filesystem_rows
                         if row['filename'] == CACHE_KEY)
        self.assertEqual(cache_row['message_id'], 'cache-message')
        self.assertIn('SDImageCache URL-derived filename',
                      cache_row['correlation'])

        photo_row = next(row for row in filesystem_rows
                         if row['message_id'] == 'photo-message')
        self.assertEqual(photo_row['message_id'], 'photo-message')
        self.assertEqual(photo_row['media_id'], 'ph://' + PHOTO_UUID + '/L0/001')
        self.assertIn('Photos original', photo_row['correlation'])
        self.assertIn('explicit message_info media join', photo_row['correlation'])

    def test_lava_conversation_mapping_is_complete(self):
        mapping = module.__artifacts_v2__['anonymousChat_messages']['data_views']['conversation']
        self.assertEqual(mapping['conversationDiscriminatorColumn'], 'Conversation Key')
        self.assertEqual(mapping['conversationLabelColumn'], 'Other Party')
        self.assertEqual(mapping['directionColumn'], 'Direction')
        self.assertEqual(mapping['directionSentValue'], 'Outgoing')
        self.assertEqual(mapping['senderColumn'], 'Sender Name')
        self.assertEqual(mapping['textColumn'], 'Message Text')
        self.assertEqual(mapping['mediaColumn'], 'Media')
        self.assertEqual(mapping['timeColumn'], 'Message Timestamp')

        # Call the undecorated processor with no database paths so this checks
        # the module's declared/output header list without reading any file.
        with patch.object(module, '_target_db_paths', return_value=[]), \
                patch.object(module, '_message_media_references', return_value={}):
            headers, rows, _source = module.anonymousChat_messages.__wrapped__(
                SyntheticContext())
        self.assertEqual(rows, [])
        self.assertIn('Conversation ID', headers)
        self.assertIn('Conversation Key', headers)
        self.assertIn('Other Party', headers)
        self.assertIn(('Media', 'media'), headers)


if __name__ == '__main__':
    unittest.main()
