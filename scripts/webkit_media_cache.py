"""Read the CachedMedia atom/block layout observed in the MVS 2023 iOS image.

The outer format is experimentally inferred, not an Apple specification. Only
complete, non-overlapping stored ranges are exported; no missing bytes are made.
"""

import hashlib
import math
import plistlib
import struct
from errno import errorcode
from pathlib import Path
from xml.parsers.expat import ExpatError

_CHUNK = 1024 * 1024
_MAX_METADATA = 4 * 1024 * 1024
_MAX_BLOCKS = 1000000
PLIST_ERRORS = (OSError, ValueError, TypeError, OverflowError,
                plistlib.InvalidFileException, ExpatError, RecursionError)


class CacheFormatError(ValueError):
    """Unsupported or inconsistent stored cache structure."""


def error_text(error):
    """Describe I/O failures without publishing an examiner's local paths."""
    if isinstance(error, OSError):
        return f'{type(error).__name__} ({errorcode.get(error.errno, "I/O error")})'
    return str(error)


def file_hashes(path):
    """Hash a file without loading it into memory."""
    sha = hashlib.sha256()
    md5 = hashlib.md5()  # Recorded fingerprint, not authentication.
    nonzero = False
    with open(path, 'rb') as handle:
        for data in iter(lambda: handle.read(_CHUNK), b''):
            sha.update(data)
            md5.update(data)
            nonzero = nonzero or bool(data.strip(b'\x00'))
    return {'sha256': sha.hexdigest(), 'md5': md5.hexdigest(), 'nonzero': nonzero}


def _read(handle, size):
    data = handle.read(size)
    if len(data) != size:
        raise CacheFormatError('Truncated field')
    return data


def _boxes(handle, start, end, extended=False):
    offset = start
    count = 0
    while offset < end:
        if end - offset < 8 or count >= _MAX_BLOCKS:
            raise CacheFormatError('Truncated atom header or atom count limit')
        handle.seek(offset)
        size, kind = struct.unpack('>I4s', _read(handle, 8))
        header = 8
        if extended and size == 1:
            size = struct.unpack('>Q', _read(handle, 8))[0]
            header = 16
        elif extended and size == 0:
            size = end - offset
        if size < header or size > end - offset:
            raise CacheFormatError('Invalid atom bounds')
        yield kind, offset + header, offset + size
        offset += size
        count += 1


def read_cache(path):
    """Return metadata and validated block mappings, retaining failed entries."""
    path = Path(path)
    row = {'status': 'Not reconstructed', 'source_bytes': path.stat().st_size,
           'blocks': [], 'warnings': []}
    hashes = file_hashes(path)
    row['source_sha256'] = hashes['sha256']
    if not hashes['nonzero']:
        row['status'] = 'Empty or all-zero cache file'
        return row
    try:
        with path.open('rb') as handle:
            if _read(handle, 8)[4:] != b'frei':
                row['status'] = 'Unsupported cache layout (no initial frei atom)'
                return row
            boxes = {}
            for kind, start, end in _boxes(handle, 0, row['source_bytes']):
                if kind in boxes:
                    raise CacheFormatError('Duplicate cache atom')
                boxes[kind] = (start, end)
            if not all(kind in boxes for kind in (b'verz', b'stid', b'stst', b'stcs')):
                raise CacheFormatError('Required cache atom missing')
            start, end = boxes[b'stid']
            if end - start > _MAX_METADATA:
                raise CacheFormatError('Identity plist exceeds metadata limit')
            handle.seek(start)
            identity = plistlib.loads(_read(handle, end - start))
            if not isinstance(identity, dict):
                raise CacheFormatError('Identity is not a dictionary')
            row['identity'] = identity
            url = identity.get('URL')
            row['url'] = url if isinstance(url, str) else ''
            size = identity.get('Size')
            if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
                raise CacheFormatError('Invalid stored resource size')
            row['resource_bytes'] = size
            start, end = boxes[b'verz']
            handle.seek(start)
            if end - start != 4 or _read(handle, 4) != b'\x00\x00\x00\x02':
                raise CacheFormatError('Unsupported cache version (expected 2)')
            if type(identity.get('Version')) is not int or identity.get('Version') != 1:
                raise CacheFormatError('Unsupported identity version (expected 1)')
            start, end = boxes[b'stst']
            if end - start < 16:
                raise CacheFormatError('Truncated block table')
            handle.seek(start)
            version, marker, block_size, count = struct.unpack('>I4sII', _read(handle, 16))
            row.update(table_version=version, block_size=block_size, block_count=count)
            if version != 5 or marker != b'crab' or block_size not in (16384, 65536):
                raise CacheFormatError('Unsupported block table version, marker or block size')
            if count > _MAX_BLOCKS or end - start != 16 + count * 16:
                raise CacheFormatError('Block table length/count mismatch')
            payload_start, payload_end = boxes[b'stcs']
            indices = set()
            for _ in range(count):
                index, length, physical = struct.unpack('>IIQ', _read(handle, 16))
                logical = index * block_size
                if index in indices:
                    raise CacheFormatError('Duplicate logical block')
                if not 0 < length <= block_size or logical + length > size:
                    raise CacheFormatError('Invalid logical block bounds')
                if physical < payload_start or physical + length > payload_end:
                    raise CacheFormatError('Block outside stcs payload')
                indices.add(index)
                row['blocks'].append({'logical_index': index, 'logical_offset': logical,
                                      'source_offset': physical, 'length': length})
            physical_ranges = sorted((b['source_offset'], b['source_offset'] + b['length'])
                                     for b in row['blocks'])
            if any(a[1] > b[0] for a, b in zip(physical_ranges, physical_ranges[1:])):
                raise CacheFormatError('Overlapping physical blocks')
            covered = 0
            position = 0
            missing = []
            for block in sorted(row['blocks'], key=lambda value: value['logical_offset']):
                if position < block['logical_offset']:
                    missing.append([position, block['logical_offset']])
                position = block['logical_offset'] + block['length']
                covered += block['length']
            if position < size:
                missing.append([position, size])
            row.update(covered_bytes=covered, missing_ranges=missing)
            row['status'] = 'Incomplete resource; no export' if missing else 'Ready for reconstruction'
    except (CacheFormatError, struct.error) + PLIST_ERRORS as error:
        row['status'] = 'Invalid or unsupported cache: ' + error_text(error)
    return row


def reconstruct(path, destination, row):
    """Copy stored bytes in logical order, checking source stability and hashes."""
    if row['status'] != 'Ready for reconstruction':
        return False
    destination = Path(destination)
    created = False
    try:
        with open(path, 'rb') as source, destination.open('xb') as output:
            created = True
            for block in sorted(row['blocks'], key=lambda value: value['logical_offset']):
                source.seek(block['source_offset'])
                data = _read(source, block['length'])
                output.write(data)
                block['sha256'] = hashlib.sha256(data).hexdigest()
        if file_hashes(path)['sha256'] != row['source_sha256']:
            raise CacheFormatError('Source changed during reconstruction')
        if destination.stat().st_size != row['resource_bytes']:
            raise CacheFormatError('Output size mismatch')
        hashes = file_hashes(destination)
        # Verify the persisted output against each source block.
        with destination.open('rb') as output:
            for block in row['blocks']:
                output.seek(block['logical_offset'])
                if hashlib.sha256(_read(output, block['length'])).hexdigest() != block['sha256']:
                    raise CacheFormatError('Persisted block hash mismatch')
        row.update(output_sha256=hashes['sha256'], output_md5=hashes['md5'],
                   status='Reconstructed complete stored resource')
        return True
    except (OSError, CacheFormatError) as error:
        if created:
            destination.unlink(missing_ok=True)
        row['status'] = 'Reconstruction failed: ' + error_text(error)
        return False


def _duration(handle, start, end):
    handle.seek(start)
    data = _read(handle, min(32, end - start))
    if not data:
        return None
    if data[0] == 0 and len(data) >= 20:
        scale, duration = struct.unpack_from('>II', data, 12)
        sentinel = 0xffffffff
    elif data[0] == 1 and len(data) >= 32:
        scale, duration = struct.unpack_from('>IQ', data, 20)
        sentinel = 0xffffffffffffffff
    else:
        return None
    return duration / scale if scale and duration != sentinel else None


def media_info(path):
    """Read stored ISO-BMFF metadata; this is a structural check, not a decoder."""
    result = {'kind': 'Unknown', 'extension': 'bin', 'mime': 'application/octet-stream',
              'tracks': [], 'validation': 'Not decoded at runtime'}
    try:
        with open(path, 'rb') as handle:
            top = list(_boxes(handle, 0, Path(path).stat().st_size, extended=True))
            kinds = {box[0] for box in top}
            if not {b'ftyp', b'moov'}.issubset(kinds) or not kinds.intersection((b'mdat', b'moof')):
                return result
            for kind, start, end in top:
                if kind != b'moov':
                    continue
                for child, cstart, cend in _boxes(handle, start, end, extended=True):
                    if child == b'mvhd':
                        result['duration_seconds'] = _duration(handle, cstart, cend)
                    elif child == b'trak':
                        result['tracks'].append(_track(handle, cstart, cend))
            handlers = {track.get('handler') for track in result['tracks']}
            if 'vide' in handlers:
                result.update(kind='Video', extension='mp4', mime='video/mp4')
            elif 'soun' in handlers:
                result.update(kind='Audio', extension='m4a', mime='audio/mp4')
            else:
                result.update(kind='ISO-BMFF', extension='mp4', mime='application/mp4')
            result['validation'] = 'ISO-BMFF box bounds checked; not decoded at runtime'
    except (OSError, CacheFormatError, struct.error) as error:
        result['validation'] = 'Unrecognized/invalid media structure: ' + error_text(error)
    return result


def _track(handle, start, end):
    track = {}
    for kind, first, last in _boxes(handle, start, end, extended=True):
        if kind == b'tkhd' and last - first >= 84:
            handle.seek(last - 8)
            width, height = struct.unpack('>II', _read(handle, 8))
            track.update(width=width / 65536, height=height / 65536)
        elif kind == b'mdia':
            for child, cstart, cend in _boxes(handle, first, last, extended=True):
                if child == b'hdlr' and cend - cstart >= 12:
                    handle.seek(cstart + 8)
                    track['handler'] = _read(handle, 4).decode('latin1')
                elif child == b'mdhd':
                    track['duration_seconds'] = _duration(handle, cstart, cend)
                elif child == b'minf':
                    track['codecs'] = _codecs(handle, cstart, cend)
    if track.get('handler') != 'vide':
        track.pop('width', None)
        track.pop('height', None)
    return track


def _codecs(handle, start, end):
    codecs = []
    for kind, first, last in _boxes(handle, start, end, extended=True):
        if kind != b'stbl':
            continue
        for child, cstart, cend in _boxes(handle, first, last, extended=True):
            if child != b'stsd' or cend - cstart < 8:
                continue
            handle.seek(cstart)
            version, count = struct.unpack('>II', _read(handle, 8))
            if version != 0 or count > 256:
                continue
            entries = list(_boxes(handle, cstart + 8, cend, extended=True))
            if len(entries) != count:
                raise CacheFormatError('Sample description count mismatch')
            codecs.extend(item[0].decode('latin1') for item in entries)
    return codecs


def valid_number(value):
    return not isinstance(value, bool) and isinstance(value, (float, int)) and math.isfinite(value)
