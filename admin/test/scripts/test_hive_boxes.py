"""The Hive box inventory's read-outcome phrases and its owner attribution.

`_how_it_read` reports one of eight outcomes and the corpus image reaches two of
them, so the rest are built here from synthetic frames. Two matter most: a read
that stops without the reader recording a frame, which only the byte accounting
catches, and an undecodable frame sitting before a stop, where the two clauses can
otherwise contradict each other.

The attribution tests cover what is specific to this core. On iOS a box carries no
application name in its path, so the identifier comes from the container's metadata
plist. `hydrated_box.hive` is hydrated_bloc's own box name, so two applications
each holding a box of that name is the ordinary case, and a resolver keyed on
anything narrower than the container would merge them.

The shared resolver has a second branch that takes a directory name out of the path
for a file under Library/Caches or Library/WebKit. That name is one anyone can
create, so the module must report nothing for it rather than place it in a column
an examiner reads as recorded identity.
"""
import plistlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from scripts.artifacts.hiveBoxes import _container_identifier, _how_it_read
from scripts.hive_parser import looks_encrypted, read_frames
from scripts.webkit_helpers import WebKitOwnerResolver

META = '.com.apple.mobile_container_manager.metadata.plist'


def string_value(text):
    return b'\x04' + struct.pack('<I', len(text)) + text.encode()


def frame(key, value, bad_crc=False):
    """One Hive frame: length, key, value, CRC32 of everything before it.

    Key type 1 is KEY_UTF8: a uint8 length then the bytes. Type 0 is a uint32
    key, which silently eats four bytes of whatever follows.
    """
    body = b'\x01' + bytes([len(key)]) + key.encode() + value
    raw = struct.pack('<I', len(body) + 8) + body
    crc = zlib.crc32(raw) & 0xffffffff
    if bad_crc:
        crc ^= 0xffffffff
    return raw + struct.pack('<I', crc)


def read(blob):
    """What the module gets for a box holding these bytes."""
    frames = read_frames(blob)
    return _how_it_read(frames, looks_encrypted(frames), len(blob))


GOOD = frame('a', string_value('x'))


class HowItRead(unittest.TestCase):

    def test_empty_file(self):
        self.assertEqual(read(b''), 'the file is empty')

    def test_bytes_but_no_frame_at_offset_zero(self):
        said = read(struct.pack('<I', 2) + b'\x00\x00\x00\x00')
        self.assertEqual(said, 'no frame could be read at offset 0, in a file of 8 byte(s)')

    def test_clean_read(self):
        self.assertEqual(read(GOOD), 'the read reached the end of the file')

    def test_stopped_early_on_an_unusable_length(self):
        # A declared length below the 8-byte minimum: the reader records nothing
        # and stops, so only the byte accounting shows the read did not finish.
        blob = GOOD + struct.pack('<I', 2) + b'\x00\x00\x00\x00'
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where no further frame could be read, '
            'leaving 8 byte(s) unread')

    def test_a_short_tail_is_not_called_a_clean_end(self):
        self.assertIn('leaving 3 byte(s) unread', read(GOOD + b'\x00\x00\x00'))

    def test_truncated_frame(self):
        blob = GOOD + struct.pack('<I', 200) + b'\x00\x00\x00\x00'
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where a frame is cut short by the end of the file')

    def test_failed_crc(self):
        blob = GOOD + frame('b', string_value('y'), bad_crc=True)
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where a frame failed its own CRC')

    def test_frame_that_did_not_decode_cleanly(self):
        # Type id 20 is a reserved id the reader has no decoder for, so the frame
        # records a decode error while its own checksum still holds.
        blob = frame('a', bytes([20]) + b'\x00\x00\x00\x00')
        self.assertEqual(
            read(blob),
            '1 frame(s) did not decode cleanly and are left out of the entry and '
            'displaced counts')

    def test_an_undecoded_frame_before_a_stop_claims_nothing_about_the_rest(self):
        # Both clauses fire on this box. The undecoded clause must not say the
        # rest of the box was read while the clause beside it names a stop.
        blob = (frame('a', bytes([20]) + b'\x00\x00\x00\x00')
                + frame('b', string_value('y'), bad_crc=True))
        self.assertEqual(
            read(blob),
            'the read stopped at offset 16, where a frame failed its own CRC; '
            '1 frame(s) did not decode cleanly and are left out of the entry and '
            'displaced counts')

    def test_encrypted_box_claims_nothing_about_keys(self):
        # The table has no key column, so the phrase must not promise keys.
        blob = (frame('a', string_value('x'), bad_crc=True)
                + frame('b', string_value('y'), bad_crc=True))
        self.assertEqual(
            read(blob),
            'every frame failed its CRC while its keys read cleanly, which is how an '
            'encrypted box reads; values are not decoded')

    def test_a_stopped_read_is_reported_once(self):
        blob = GOOD + frame('b', string_value('y'), bad_crc=True) + b'\x00' * 32
        self.assertEqual(read(blob).count('the read stopped at offset'), 1)


class _Context:
    """Just enough of the artifact context for the resolver."""

    def __init__(self, root):
        self.root = str(root)

    def get_relative_path(self, path):
        return str(path)[len(self.root):].lstrip('/')


class OwnerAttribution(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.containers = self.root / 'private/var/mobile/Containers/Data/Application'
        self.addCleanup(self.tmp.cleanup)

    def container(self, uuid, bundle_id):
        root = self.containers / uuid
        root.mkdir(parents=True, exist_ok=True)
        if bundle_id:
            (root / META).write_bytes(plistlib.dumps({'MCMMetadataIdentifier': bundle_id}))
        box = root / 'Library/Application Support/hydrated_box.hive'
        box.parent.mkdir(parents=True, exist_ok=True)
        box.write_bytes(GOOD)
        return box

    def owners(self, *boxes):
        """What the module would put in the column, not what the resolver returns."""
        files = tuple(str(p) for p in self.root.rglob('*') if p.is_file())
        resolver = WebKitOwnerResolver(_Context(self.root), files)
        return [_container_identifier(resolver, str(b)) for b in boxes]

    def test_two_same_named_boxes_keep_their_own_owners(self):
        a = self.container('AAAA-A', 'com.example.alpha')
        b = self.container('BBBB-B', 'com.example.beta')
        self.assertEqual(self.owners(a, b), ['com.example.alpha', 'com.example.beta'])

    def test_a_container_without_metadata_borrows_no_owner(self):
        self.container('AAAA-A', 'com.example.alpha')
        orphan = self.container('CCCC-C', None)
        self.assertEqual(self.owners(orphan), [''])

    def test_a_box_outside_any_container_has_no_owner(self):
        self.container('AAAA-A', 'com.example.alpha')
        stray = self.root / 'private/var/root/stray.hive'
        stray.parent.mkdir(parents=True, exist_ok=True)
        stray.write_bytes(GOOD)
        self.assertEqual(self.owners(stray), [''])

    def test_a_directory_name_in_the_path_is_not_reported_as_an_identifier(self):
        # The resolver answers 'com.anything' for these two shapes, from the
        # directory name alone. Reporting it would publish a name the filesystem
        # supplied as though a container had recorded it.
        shapes = []
        for parent in ('Library/Caches/com.apple.something',
                       'Library/WebKit/com.evil.spoof'):
            box = self.root / 'private/var/mobile' / parent / 'box.hive'
            box.parent.mkdir(parents=True, exist_ok=True)
            box.write_bytes(GOOD)
            shapes.append(box)
        self.assertEqual(self.owners(*shapes), ['', ''])

    def test_a_shared_container_reports_the_group_identifier_it_records(self):
        # Not a bundle identifier, which is why the column is not named for an app.
        root = self.root / 'private/var/mobile/Containers/Shared/AppGroup/GGGG-G'
        root.mkdir(parents=True, exist_ok=True)
        (root / META).write_bytes(
            plistlib.dumps({'MCMMetadataIdentifier': 'group.com.example.alpha'}))
        box = root / 'box.hive'
        box.write_bytes(GOOD)
        self.assertEqual(self.owners(box), ['group.com.example.alpha'])

    def test_a_container_plist_without_the_identifier_reports_nothing(self):
        root = self.containers / 'DDDD-D'
        root.mkdir(parents=True, exist_ok=True)
        (root / META).write_bytes(plistlib.dumps({'MCMMetadataUUID': 'DDDD-D'}))
        box = root / 'box.hive'
        box.write_bytes(GOOD)
        self.assertEqual(self.owners(box), [''])


if __name__ == '__main__':
    unittest.main()
