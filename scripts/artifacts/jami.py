__artifacts_v2__ = {
    "jami_conversations": {
        "name": "Jami - Conversation History",
        "description": "Commits of the Jami conversation repositories: messages, files, "
                       "member changes and calls, with the transferred file on the row.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Jami",
        "notes": "Jami keeps each conversation as a git repository at "
                 "Documents/<account>/conversations/<conversation id>/ in the app group container "
                 "group.com.savoirfairelinux.ring, which is recognised by the identifier its "
                 "container metadata records. Every commit is one row, read from the repository's "
                 "loose objects and pack files by a reader written from git's published formats, "
                 "which checks each object against its name (the SHA-1 of its type, size and "
                 "content) and leaves out any that fail; on the tested images all 89 objects "
                 "passed and the same 46 commits came out as git itself lists, with the same "
                 "author device, time, parents and message. Commit messages are JSON whose keys "
                 "and types are those jami-daemon defines in src/jamidht/commit_message.h "
                 "(25fadf1a, 2026); the iOS app version (Jami 4.20 on both tested images) is not "
                 "mapped to a daemon commit. Type is the type key as stored. Message is the body "
                 "of text/plain commits: an edit carries Edit Of, and the source says an edit with "
                 "an empty body is a deletion; a reaction carries React To. Other Fields holds any "
                 "key this artifact does not show in its own column, and held nothing on the "
                 "tested images. Timestamp is the commit time, which the daemon reads as the "
                 "message time (git_commit_time, src/jamidht/conversationrepository.cpp line "
                 "2969); the author time equals it on all 46 commits. Author Device is the "
                 "commit's author email, which the daemon uses as the device ID. Author Account is "
                 "the userId of the issuer of that device's certificate in the repository's "
                 "devices/ folder, which is how the daemon resolves a device to an account "
                 "(uriFromDevice, conversationrepository.cpp line 517); the certificate chain and "
                 "the commit signatures are not verified here. On all 7 device certificates of the "
                 "tested images that issuer is a member or admin of the same conversation. Account "
                 "is the issuer of the account's own ring_device.crt, and Direction compares it "
                 "with Author Account. Author Name (as stored) is the commit's author name: it "
                 "equals Author Device on the 34 outgoing commits and is 4 characters on the 12 "
                 "incoming ones, and what it holds is not established. Attachment is the file the "
                 "daemon keeps at conversation_data/<conversation>/<commit id>_<tid> plus the "
                 "display name's extension (getFileId, src/data_transfer.cpp line 94), so the link "
                 "is recorded, not inferred; all 11 file transfers on the tested images resolved, "
                 "and File Hash Matches compares the file's SHA3-512 with the stored sha3sum, "
                 "which matched on all 11. The same folders hold 11 more files under plain names; "
                 "each is byte-identical, by SHA3-512, to a file a transfer commit records, and "
                 "they are not reported separately. Reachable From A Branch says whether the "
                 "commit can be reached from a branch head or HEAD, and held Yes on every row of "
                 "both tested images; Account held one value on every row of each image. Reply To "
                 "and Call Duration (ms), Call Peer and Call End Reason are empty on every row of "
                 "both tested images, which hold no replies and no call history commits; Edit Of "
                 "is empty on hill_iphone15pro_ios26 and React To on wilkerson_iphone16_ios26. "
                 "Conversation Mode names the stored mode by the daemon's ConversationMode values. "
                 "Not read here: the account's legacy <account>.db, whose conversations and "
                 "interactions tables are empty on both images; the msgpack files contacts, "
                 "convInfo and convRequests and the Library/Caches message stores; profiles/*.vcf "
                 "and each conversation's profile.vcf; config.yml, dring.yml and the account "
                 "archive archive.gz; and the certificate and key files.",
        "paths": ('*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/Documents/*/ring_device.crt',
                  '*/Containers/Shared/AppGroup/*/Documents/*/conversations/*',
                  '*/Containers/Shared/AppGroup/*/Documents/*/conversation_data/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | Jami 4.20 | 21 rows, 3 conversations, 1 file",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | Jami 4.20 | 25 rows, 2 conversations, 10 files",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no Jami container",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Author Account",
                "mediaColumn": "Attachment",
            }
        },
    },
}

import hashlib
import json
import os
import plistlib
import re
import ssl
import struct
import zlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

_GROUP_ID = 'group.com.savoirfairelinux.ring'
_METADATA = '.com.apple.mobile_container_manager.metadata.plist'
# <group container>/Documents/<account>/conversations/<conversation>/<rest>
_CONVERSATION = re.compile(
    r'^(?P<group>.*/Containers/Shared/AppGroup/[^/]+)/Documents/(?P<account>[^/]+)/'
    r'conversations/(?P<conversation>[0-9a-f]{40})/(?P<rest>.+)$')
_DATA = re.compile(
    r'^(?P<group>.*/Containers/Shared/AppGroup/[^/]+)/Documents/(?P<account>[^/]+)/'
    r'conversation_data/(?P<conversation>[0-9a-f]{40})/(?P<name>[^/]+)$')
_DEVICE_CERT = re.compile(
    r'^(?P<group>.*/Containers/Shared/AppGroup/[^/]+)/Documents/(?P<account>[^/]+)/ring_device\.crt$')
_LOOSE = re.compile(r'^\.git/objects/([0-9a-f]{2})/([0-9a-f]{38})$')
_PACK_INDEX = re.compile(r'^\.git/objects/pack/(pack-[0-9a-f]{40})\.idx$')

# Git object types as packed (Documentation/gitformat-pack.txt).
_PACK_TYPES = {1: b'commit', 2: b'tree', 3: b'blob', 4: b'tag'}
_OFS_DELTA = 6
_REF_DELTA = 7

# jami-daemon src/jamidht/commit_message.h (25fadf1a, 2026): ConversationMode values, which
# the source says are persisted in initial commits.
_MODES = {0: 'One to one', 1: 'Admin invites only', 2: 'Invites only', 3: 'Public',
          4: 'Document', 5: 'Feed'}
_SHOWN_KEYS = ('type', 'body', 'reply-to', 'react-to', 'edit', 'action', 'uri', 'displayName',
               'totalSize', 'sha3sum', 'tid', 'duration', 'to', 'reason', 'mode', 'invited')
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a')


class _GitObjects:
    '''Reads the objects of one git repository from its loose files and pack files.

    Written from git's published formats (gitformat-loose, gitformat-pack). Every object
    returned is checked against its name: the SHA-1 of "<type> <size>\\0" and the content.
    '''

    def __init__(self, files):
        self.loose = {}
        self.packs = []
        self.bad = 0
        for rest, path in files.items():
            match = _LOOSE.match(rest)
            if match:
                self.loose[match.group(1) + match.group(2)] = path
                continue
            match = _PACK_INDEX.match(rest)
            if match:
                pack = files.get(f'.git/objects/pack/{match.group(1)}.pack')
                if pack:
                    self._read_index(path, pack)
                else:
                    logfunc(f'Jami: pack index without its pack: {path}')
        self.cache = {}

    def _read_index(self, index_path, pack_path):
        with open(index_path, 'rb') as handle:
            data = handle.read()
        if data[:8] != b'\xfftOc\x00\x00\x00\x02':
            logfunc(f'Jami: not a version 2 pack index: {index_path}')
            return
        count = struct.unpack_from('>I', data, 8 + 255 * 4)[0]
        names_at = 8 + 256 * 4
        offsets_at = names_at + 20 * count + 4 * count
        large_at = offsets_at + 4 * count
        offsets = {}
        for index in range(count):
            name = data[names_at + 20 * index:names_at + 20 * index + 20].hex()
            offset = struct.unpack_from('>I', data, offsets_at + 4 * index)[0]
            if offset & 0x80000000:
                offset = struct.unpack_from('>Q', data, large_at + 8 * (offset & 0x7fffffff))[0]
            offsets[name] = offset
        with open(pack_path, 'rb') as handle:
            pack = handle.read()
        if pack[:4] != b'PACK':
            logfunc(f'Jami: not a pack file: {pack_path}')
            return
        self.packs.append((pack, offsets, {offset: name for name, offset in offsets.items()}))

    def names(self):
        found = set(self.loose)
        for _, offsets, _ in self.packs:
            found.update(offsets)
        return found

    def get(self, name):
        '''(type, content) of an object whose name checks out, or None.'''
        if name in self.cache:
            return self.cache[name]
        found = None
        if name in self.loose:
            found = self._loose(name)
        else:
            for pack, offsets, _ in self.packs:
                if name in offsets:
                    found = self._packed(pack, offsets[name], 0)
                    break
        if found is not None:
            kind, content = found
            check = hashlib.sha1(kind + b' ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if check != name:
                logfunc(f'Jami: object {name} does not match its content and is not used')
                self.bad += 1
                found = None
        self.cache[name] = found
        return found

    def _loose(self, name):
        try:
            with open(self.loose[name], 'rb') as handle:
                raw = zlib.decompress(handle.read())
        except (OSError, zlib.error) as error:
            logfunc(f'Jami: could not read loose object {name}: {error}')
            return None
        header, _, content = raw.partition(b'\0')
        kind, _, size = header.partition(b' ')
        if not size.isdigit() or int(size) != len(content):
            logfunc(f'Jami: loose object {name} has a wrong size')
            return None
        return kind, content

    def _packed(self, pack, offset, depth):
        if depth > 50:
            logfunc('Jami: delta chain too long, object not read')
            return None
        try:
            position = offset
            byte = pack[position]
            kind = (byte >> 4) & 7
            size = byte & 15
            shift = 4
            while byte & 0x80:
                position += 1
                byte = pack[position]
                size |= (byte & 0x7f) << shift
                shift += 7
            position += 1
            base = None
            if kind == _OFS_DELTA:
                byte = pack[position]
                position += 1
                distance = byte & 0x7f
                while byte & 0x80:
                    byte = pack[position]
                    position += 1
                    distance = ((distance + 1) << 7) | (byte & 0x7f)
                base = self._packed(pack, offset - distance, depth + 1)
            elif kind == _REF_DELTA:
                base = self.get(pack[position:position + 20].hex())
                position += 20
            elif kind not in _PACK_TYPES:
                logfunc(f'Jami: unknown packed object type {kind}')
                return None
            content = zlib.decompressobj().decompress(memoryview(pack)[position:])
        except (IndexError, zlib.error) as error:
            logfunc(f'Jami: could not read a packed object: {error}')
            return None
        if len(content) != size:
            logfunc('Jami: packed object has a wrong size')
            return None
        if kind in _PACK_TYPES:
            return _PACK_TYPES[kind], content
        if base is None:
            logfunc('Jami: delta base not found, object not read')
            return None
        result = _apply_delta(base[1], content)
        return (base[0], result) if result is not None else None


def _delta_size(data, position):
    size = shift = 0
    while True:
        byte = data[position]
        position += 1
        size |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return size, position


def _apply_delta(base, delta):
    '''A git delta applied to its base, or None when the delta does not fit the base.'''
    try:
        source_size, position = _delta_size(delta, 0)
        target_size, position = _delta_size(delta, position)
        if source_size != len(base):
            return None
        out = bytearray()
        while position < len(delta):
            op = delta[position]
            position += 1
            if op & 0x80:
                offset = size = 0
                for bit in range(4):
                    if op & (1 << bit):
                        offset |= delta[position] << (8 * bit)
                        position += 1
                for bit in range(3):
                    if op & (0x10 << bit):
                        size |= delta[position] << (8 * bit)
                        position += 1
                out += base[offset:offset + (size or 0x10000)]
            elif op:
                out += delta[position:position + op]
                position += op
            else:
                return None
    except IndexError:
        return None
    return bytes(out) if len(out) == target_size else None


def _commit(content):
    '''{headers, message} from a commit object's content.'''
    head, _, message = content.partition(b'\n\n')
    headers = {}
    last = None
    for line in head.split(b'\n'):
        if line.startswith(b' ') and last:
            continue
        key, _, value = line.partition(b' ')
        last = key.decode('ascii', 'replace')
        headers.setdefault(last, []).append(value.decode('utf-8', 'replace'))
    return headers, message.decode('utf-8', 'replace')


def _signature(value):
    '''(name, email, seconds) from an author or committer line.'''
    match = re.match(r'^(.*) <([^>]*)> (-?\d+) [+-]\d{4}$', value or '')
    if not match:
        return '', '', None
    return match.group(1), match.group(2), int(match.group(3))


def _refs(files):
    '''Commit names the repository's branch heads, packed refs and HEAD point at.'''
    heads = set()
    for rest, path in files.items():
        if rest.startswith('.git/refs/heads/') or rest == '.git/HEAD':
            try:
                with open(path, 'r', encoding='ascii', errors='replace') as handle:
                    value = handle.read().strip()
            except OSError:
                continue
            if re.fullmatch(r'[0-9a-f]{40}', value):
                heads.add(value)
        elif rest == '.git/packed-refs':
            try:
                with open(path, 'r', encoding='ascii', errors='replace') as handle:
                    for line in handle:
                        match = re.match(r'^([0-9a-f]{40}) refs/heads/', line)
                        if match:
                            heads.add(match.group(1))
            except OSError:
                continue
    return heads


def _certificate_issuer(path):
    '''The userId of a certificate's issuer, read with the OpenSSL that Python links, or ''.'''
    decode = getattr(getattr(ssl, '_ssl', None), '_test_decode_cert', None)
    if decode is None:
        logfunc('Jami: this Python cannot decode certificates; Author Account is not filled')
        return ''
    try:
        decoded = decode(path)  # pylint: disable=assignment-from-no-return
    except (ssl.SSLError, OSError, ValueError) as error:
        logfunc(f'Jami: could not decode {path}: {error}')
        return ''
    for entry in decoded.get('issuer', ()):
        for key, value in entry:
            if key == 'userId':
                return value
    return ''


def _jami_groups(files_found):
    groups = set()
    for path in files_found:
        if os.path.basename(path) != _METADATA:
            continue
        try:
            with open(path, 'rb') as handle:
                metadata = plistlib.load(handle)
        except (OSError, plistlib.InvalidFileException, ValueError) as error:
            logfunc(f'Jami: could not read {path}: {error}')
            continue
        if isinstance(metadata, dict) and metadata.get('MCMMetadataIdentifier') == _GROUP_ID:
            groups.add(os.path.dirname(path))
    return groups


def _as_text(value):
    if value is None:
        return ''
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _mode(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return _as_text(value)
    return f'{_MODES[number]} ({number})' if number in _MODES else f'Unknown ({number})'


def _attachment(data_files, key, commit_name, body):
    '''(media reference, hash check) for a file transfer's file, or ('', '').

    The daemon keeps a received or sent file at conversation_data/<conversation>/<file id>,
    where the file id is <commit id>_<tid>, plus the display name's extension when it has a
    safe one (getFileId, src/data_transfer.cpp, jami-daemon 25fadf1a).
    '''
    tid = body.get('tid')
    if body.get('type') != 'application/data-transfer+json' or not isinstance(tid, str) or not tid:
        return '', ''
    path = data_files.get(key + (f'{commit_name}_{tid}',))
    if not path:
        return '', ''
    try:
        with open(path, 'rb') as handle:
            content = handle.read()
    except OSError as error:
        logfunc(f'Jami: could not read {path}: {error}')
        return '', ''
    stored = body.get('sha3sum')
    check = ''
    if isinstance(stored, str) and stored:
        check = 'Yes' if hashlib.sha3_512(content).hexdigest() == stored.lower() else 'No'
    return check_in_media(path, os.path.basename(path)), check


@artifact_processor
def jami_conversations(context):
    '''One row per commit object of every Jami conversation repository.'''
    files_found = sorted(dict.fromkeys(str(found).replace('\\', '/') for found in context.get_files_found()))
    groups = _jami_groups(files_found)
    repositories, data_files, own = {}, {}, {}
    for path in files_found:
        if os.path.isdir(path):
            continue
        match = _CONVERSATION.match(path)
        if match and match.group('group') in groups:
            key = (match.group('group'), match.group('account'), match.group('conversation'))
            repositories.setdefault(key, {})[match.group('rest')] = path
            continue
        match = _DATA.match(path)
        if match and match.group('group') in groups:
            key = (match.group('group'), match.group('account'), match.group('conversation'))
            data_files[key + (match.group('name').split('.', 1)[0],)] = path
            continue
        match = _DEVICE_CERT.match(path)
        if match and match.group('group') in groups:
            own[(match.group('group'), match.group('account'))] = _certificate_issuer(path)

    data_list, sources = [], []
    for key in sorted(repositories):
        group, account, conversation = key
        files = repositories[key]
        objects = _GitObjects(files)
        heads = _refs(files)
        devices = {}
        for rest, path in files.items():
            if rest.startswith('devices/') and rest.endswith('.crt'):
                devices[rest[len('devices/'):-len('.crt')]] = _certificate_issuer(path)
        commits = {}
        for name in sorted(objects.names()):
            found = objects.get(name)
            if found and found[0] == b'commit':
                commits[name] = _commit(found[1])
        reachable, stack = set(), [name for name in heads if name in commits]
        while stack:
            name = stack.pop()
            if name in reachable:
                continue
            reachable.add(name)
            stack.extend(parent for parent in commits[name][0].get('parent', []) if parent in commits)
        if commits:
            sources.append(files.get('.git/HEAD') or next(iter(files.values())))
        own_uri = own.get((group, account), '')
        for name, (headers, message) in commits.items():
            author_name, device, _ = _signature((headers.get('author') or [''])[0])
            _, _, seconds = _signature((headers.get('committer') or [''])[0])
            try:
                body = json.loads(message)
            except ValueError:
                body = None
            if not isinstance(body, dict):
                body = {'type': '', 'body': message}
            author = devices.get(device, '')
            direction = ''
            if author and own_uri:
                direction = 'Outgoing' if author == own_uri else 'Incoming'
            media, hash_check = _attachment(data_files, key, name, body)
            other = {k: v for k, v in body.items() if k not in _SHOWN_KEYS}
            data_list.append((
                datetime.fromtimestamp(seconds, timezone.utc) if seconds is not None else '',
                direction,
                author,
                _as_text(body.get('body')) if body.get('type') in ('text/plain', '') else '',
                media,
                conversation,
                device,
                _as_text(body.get('type')),
                _as_text(body.get('displayName')),
                _as_text(body.get('totalSize')),
                hash_check,
                _as_text(body.get('reply-to')),
                _as_text(body.get('react-to')),
                _as_text(body.get('edit')),
                _as_text(body.get('action')),
                _as_text(body.get('uri')),
                _as_text(body.get('duration')),
                _as_text(body.get('to')),
                _as_text(body.get('reason')),
                _mode(body['mode']) if 'mode' in body else '',
                _as_text(body.get('invited')),
                json.dumps(other, ensure_ascii=False) if other else '',
                'Yes' if name in reachable else 'No',
                name,
                ' '.join(headers.get('parent', [])),
                author_name,
                own_uri,
            ))
        if objects.bad:
            logfunc(f'Jami: {objects.bad} object(s) in conversation {conversation} failed their check')

    data_list.sort(key=lambda row: (row[5], row[0] or datetime.min.replace(tzinfo=timezone.utc)))
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Author Account', 'Message', ('Attachment', 'media'),
        'Conversation ID', 'Author Device', 'Type', 'File Name', 'File Size (bytes)',
        'File Hash Matches', 'Reply To', 'React To', 'Edit Of', 'Member Action', 'Member URI',
        'Call Duration (ms)', 'Call Peer', 'Call End Reason', 'Conversation Mode', 'Invited',
        'Other Fields', 'Reachable From A Branch', 'Commit ID', 'Parent Commits',
        'Author Name (as stored)', 'Account')
    return data_headers, data_list, '\n'.join(sources)
