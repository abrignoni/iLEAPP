"""Read allocated table cells in main-file and checksum-valid committed WAL page versions.

Format: https://www.sqlite.org/fileformat2.html (btree, record, overflow and WAL sections).
No freeblock, freelist, old-salt, uncommitted-tail or raw-string carving is attempted.
Current Core Data entity IDs reject sibling entities. Historical btree/schema ownership is
not guaranteed where traversal needs main-file pages backfilled after the WAL transaction.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import struct

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly

_MAX_PAYLOAD = 32 * 1024 * 1024


def _u16(data, offset):
    return int.from_bytes(data[offset:offset + 2], 'big')


def _u32(data, offset):
    if offset < 0 or offset + 4 > len(data):
        raise ValueError('short integer')
    return int.from_bytes(data[offset:offset + 4], 'big')


def _varint(data, offset):
    value = 0
    for index in range(9):
        if offset >= len(data):
            raise ValueError('short varint')
        byte = data[offset]
        offset += 1
        value = (value << (8 if index == 8 else 7)) | (byte if index == 8 else byte & 127)
        if index == 8 or byte < 128:
            return value, offset
    raise ValueError('invalid varint')


def _checksum(data, order, seed=(0, 0)):
    if len(data) % 8:
        raise ValueError('unaligned checksum input')
    first, second = seed
    for left, right in struct.iter_unpack(order + 'II', data):
        first = (first + left + second) & 0xffffffff
        second = (second + right + first) & 0xffffffff
    return first, second


def wal_transactions(path, size, label, logger=None):
    """Yield only complete transactions in the valid WAL prefix; last image per page wins."""
    logger = logger or logfunc
    try:
        with Path(path).open('rb') as stream:
            header = stream.read(32)
            if not header:
                return
            if len(header) != 32:
                raise ValueError('truncated WAL header')
            magic, version, page_size, _, salt1, salt2, check1, check2 = struct.unpack('>8I', header)
            if magic not in (0x377f0682, 0x377f0683) or version != 3007000 or page_size != size:
                raise ValueError('unsupported WAL header or page size')
            order = '<' if magic == 0x377f0682 else '>'
            seed = _checksum(header[:24], order)
            if seed != (check1, check2):
                raise ValueError('WAL header checksum mismatch')
            pending = {}
            number = 0
            while True:
                raw = stream.read(24 + size)
                if not raw:
                    break
                number += 1
                if len(raw) != 24 + size:
                    logger(f'Life360 recovery {label!r}: truncated frame {number}; valid earlier commits retained')
                    break
                page, commit_size, a, b, x, y = struct.unpack('>6I', raw[:24])
                if page == 0 or page > 0xfffffffe or (a, b) != (salt1, salt2):
                    logger(f'Life360 recovery {label!r}: invalid page/salt at frame {number}; remaining frames excluded')
                    break
                calculated = _checksum(raw[:8] + raw[24:], order, seed)
                if calculated != (x, y):
                    logger(f'Life360 recovery {label!r}: checksum mismatch at frame {number}; remaining frames excluded')
                    break
                seed = calculated
                pending[page] = (raw[24:], number)
                if commit_size:
                    yield number, commit_size, pending
                    pending = {}
            if pending:
                logger(f'Life360 recovery {label!r}: uncommitted/incomplete transaction tail excluded')
    except (OSError, ValueError, struct.error) as error:
        logger(f'Life360 recovery {label!r}: WAL read/validation failed ({type(error).__name__}); '
                'valid earlier commits retained')


def _decode(payload, encoding):
    header_size, offset = _varint(payload, 0)
    if header_size > len(payload) or header_size < offset:
        raise ValueError('invalid record header')
    types = []
    while offset < header_size:
        kind, offset = _varint(payload, offset)
        types.append(kind)
    if offset != header_size:
        raise ValueError('record header overrun')
    offset = header_size
    result = []
    for kind in types:
        if kind in (10, 11):
            raise ValueError('reserved serial type')
        count = (0, 1, 2, 3, 4, 6, 8, 8, 0, 0)[kind] if kind < 10 else (kind - 12) // 2
        if offset + count > len(payload):
            raise ValueError('short record payload')
        data = payload[offset:offset + count]
        offset += count
        if kind == 0:
            value = None
        elif 1 <= kind <= 6:
            value = int.from_bytes(data, 'big', signed=True)
        elif kind == 7:
            value = struct.unpack('>d', data)[0]
        elif kind in (8, 9):
            value = kind - 8
        elif kind % 2:
            value = data.decode(encoding)
        else:
            value = data
        result.append(value)
    if offset != len(payload):
        raise ValueError('record payload length mismatch')
    return result


def _cell(page, position, page_number, usable, provider, encoding):
    size, cursor = _varint(page[:usable], position)
    rowid, cursor = _varint(page[:usable], cursor)
    if rowid >= 1 << 63:
        rowid -= 1 << 64
    if size > _MAX_PAYLOAD:
        raise ValueError('payload exceeds recovery limit')
    local = size
    if size > usable - 35:
        minimum = (usable - 12) * 32 // 255 - 23
        remainder = minimum + (size - minimum) % (usable - 4)
        local = remainder if remainder <= usable - 35 else minimum
    if cursor + local + (4 if size > local else 0) > usable:
        raise ValueError('cell payload overrun')
    parts = [page[cursor:cursor + local]]
    length = local
    references = []
    if size > local:
        following = _u32(page, cursor + local)
        visited = {page_number}
        while length < size:
            if following == 0 or following in visited:
                raise ValueError('invalid overflow chain')
            visited.add(following)
            other, frame = provider(following)
            if other is None or len(other) < usable:
                raise ValueError('overflow page unavailable in this source state')
            references.append({'page': following, 'frame': frame})
            following = _u32(other, 0)
            chunk = other[4:4 + min(usable - 4, size - length)]
            parts.append(chunk)
            length += len(chunk)
        if following:
            raise ValueError('overflow chain longer than payload')
    return rowid, _decode(b''.join(parts), encoding), position, references


def _cells(page, page_number, usable, provider, encoding, failures):
    head = 100 if page_number == 1 else 0
    if len(page) < usable or page[head] != 13:
        return
    count = _u16(page, head + 3)
    end = head + 8 + 2 * count
    if end > usable:
        raise ValueError('cell pointer array overrun')
    seen_offsets = set()
    for index in range(count):
        position = _u16(page, head + 8 + 2 * index)
        try:
            if position < end or position >= usable or position in seen_offsets:
                raise ValueError('invalid cell offset')
            seen_offsets.add(position)
            yield _cell(page, position, page_number, usable, provider, encoding)
        except (ValueError, UnicodeError, IndexError, struct.error):
            failures(index)


def _leaves(root, provider, usable):
    pending = [root]
    visited = set()
    result = set()
    while pending:
        number = pending.pop()
        if number in visited or len(visited) > 100000:
            raise ValueError('cyclic or excessive btree')
        visited.add(number)
        page, _ = provider(number)
        head = 100 if number == 1 else 0
        if page is None or len(page) < usable:
            raise ValueError('btree page unavailable')
        if page[head] == 13:
            result.add(number)
        elif page[head] == 5:
            count = _u16(page, head + 3)
            end = head + 12 + 2 * count
            if end > usable:
                raise ValueError('interior pointer array overrun')
            pending.append(_u32(page, head + 8))
            for index in range(count):
                position = _u16(page, head + 12 + index * 2)
                if position < end or position + 4 > usable:
                    raise ValueError('invalid interior cell')
                pending.append(_u32(page, position))
        else:
            raise ValueError('unsupported table btree page')
    return result


def fingerprint(values):
    """Retain byte/text distinctions; use an opaque fingerprint rather than printing source values."""
    serial = [('blob', v.hex()) if isinstance(v, bytes) else (type(v).__name__, v) for v in values]
    return hashlib.sha256(json.dumps(serial, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def recover_rows(path, table, label, logger=None):
    """Yield non-live records with source page/frame provenance, never inferred deletion status."""
    logger = logger or logfunc
    if table not in ('ZENTRY', 'ZDRIVEMODEL'):
        raise ValueError('unsupported recovery table')
    connection = open_sqlite_db_readonly(path)
    if connection is None:
        logger(f'Life360 recovery {label!r}: live comparison unavailable; recovery suppressed')
        return
    try:
        columns = connection.execute(f'PRAGMA table_info({table})').fetchall()
        root_row = connection.execute('SELECT rootpage FROM sqlite_master WHERE type=? AND name=?',
                                      ('table', table)).fetchone()
        if not columns or not root_row or [c[1] for c in columns[:3]] != ['Z_PK', 'Z_ENT', 'Z_OPT']:
            logger(f'Life360 recovery {label!r}: unsupported or missing {table} schema')
            return
        entities = connection.execute('SELECT Z_ENT FROM Z_PRIMARYKEY WHERE upper(Z_NAME)=?',
                                      (table[1:],)).fetchall()
        if len(entities) != 1 or not isinstance(entities[0][0], int):
            logger(f'Life360 recovery {label!r}: entity identity unavailable for {table}; recovery suppressed')
            return
        entity = entities[0][0]
        names = [c[1] for c in columns]
        live_encoding = connection.execute('PRAGMA encoding').fetchone()[0]
        real = [i for i, c in enumerate(columns) if 'FLOA' in c[2].upper() or 'REAL' in c[2].upper() or 'DOUB' in c[2].upper()]
        live = {fingerprint(tuple(row)[3:]) for row in connection.execute(f'SELECT * FROM {table}')}
    except (sqlite3.Error, ValueError, TypeError):
        logger(f'Life360 recovery {label!r}: schema/entity identity/live comparison failed; recovery suppressed')
        return
    finally:
        connection.close()
    try:
        main = Path(path).read_bytes()
        if main[:16] != b'SQLite format 3\x00' or len(main) < 100:
            raise ValueError('invalid database header')
        size = _u16(main, 16)
        size = 65536 if size == 1 else size
        if size < 512 or size > 65536 or size & (size - 1):
            raise ValueError('invalid database page size')
        usable = size - main[20]
        encoding_number = _u32(main, 56)
        encoding = {1: 'utf-8', 2: 'utf-16le', 3: 'utf-16be'}.get(encoding_number)
        # A newly created main file may have no schema yet; its schema/header lives in WAL page 1.
        if encoding_number == 0:
            encoding = {'UTF-8': 'utf-8', 'UTF-16le': 'utf-16le', 'UTF-16be': 'utf-16be'}.get(live_encoding)
        if encoding is None or usable < 480 or len(main) % size:
            raise ValueError('unsupported database encoding/size')
    except (OSError, ValueError, IndexError):
        logger(f'Life360 recovery {label!r}: main-file header read failed; file skipped')
        return

    def main_page(number):
        begin = (number - 1) * size
        return (main[begin:begin + size], 0) if 0 < number <= len(main) // size else (None, 0)

    def records(number, page, provider, state, frame, commit):
        try:
            def failure(index):
                logger(f'Life360 recovery {label!r}: page {number}, frame {frame}, cell {index} '
                        'was incomplete/unsupported; other cells continue')
            for rowid, values, offset, overflow in _cells(page, number, usable, provider, encoding, failure):
                if len(values) != len(names) or values[0] is not None:
                    logger(f'Life360 recovery {label!r}: schema-shaped cell check failed on page {number}; cell skipped')
                    continue
                if values[1] != entity:
                    logger(f'Life360 recovery {label!r}: entity identity mismatch on page {number}, '
                           f'frame {frame}, cell offset {offset}; cell skipped')
                    continue
                values[0] = rowid
                for index in real:
                    if isinstance(values[index], int):
                        values[index] = float(values[index])
                key = fingerprint(values[3:])
                if key in live:
                    continue
                yield {'values': dict(zip(names, values)), 'fingerprint': key,
                       'source': {'state': state, 'page': number, 'cellOffset': offset,
                                  'frame': frame, 'commitFrame': commit, 'rowID': rowid,
                                  'rowRevision': values[2], 'overflow': overflow,
                                  'fileOffset': (32 + (frame - 1) * (size + 24) + 24 + offset)
                                  if frame else (number - 1) * size + offset}}
        except (ValueError, UnicodeError, IndexError, struct.error):
            logger(f'Life360 recovery {label!r}: page {number}, frame {frame} had an incomplete/unsupported cell; '
                    'earlier cells retained')

    try:
        for number in sorted(_leaves(root_row[0], main_page, usable)):
            yield from records(number, main_page(number)[0], main_page, 'Main-file view without WAL', 0, 0)
    except ValueError:
        logger(f'Life360 recovery {label!r}: main-file btree incomplete; valid WAL pages still considered')
    wal = Path(str(path) + '-wal')
    if not wal.exists():
        return
    latest = {}
    for commit, database_size, pages in wal_transactions(wal, size, label, logger):
        latest.update(pages)
        latest = {number: image for number, image in latest.items() if number <= database_size}

        def snapshot_page(number):
            return latest.get(number, main_page(number))

        def overflow_page(number):
            # Never splice a historical WAL record with overflow bytes from the main file.
            return latest.get(number, (None, 0))

        try:
            leaves = _leaves(root_row[0], snapshot_page, usable)
        except ValueError:
            logger(f'Life360 recovery {label!r}: btree could not be assigned at commit frame {commit}; transaction skipped')
            continue
        for number, (page, frame) in sorted(pages.items()):
            if number in leaves and number <= database_size:
                yield from records(number, page, overflow_page, 'Committed WAL page version', frame, commit)
