"""Committed states of a SQLite database held in its write-ahead log.

A database in WAL mode keeps each committed transaction as frames appended to
<db>-wal until a checkpoint copies them into the database file. Until the log is
reset, the frames of earlier transactions stay in it, so the log holds every
committed state of the database since the last reset, not only the latest one.
A row deleted, or changed, in one of those later transactions can still be read
from the state before it.

Each state is read by SQLite itself. A scratch copy of the database and its log is
made, the log copy is cut at the end of a committed transaction, and the copy is
opened read-only, so SQLite applies its own salt, checksum and commit rules to the
frames that remain. Nothing here decodes a page or a record.

What is replayed: the frames of the current log generation (salts equal to the log
header's) up to the last commit frame inside the checksum-valid prefix. That is the
set of frames SQLite itself reads at acquisition.

What is not, and is counted instead (see WalStates.summary):
- frames after the last commit frame of the valid prefix (a transaction that never
  committed, or was cut short by the acquisition);
- frames after the valid prefix (left behind by an earlier log generation, or
  damaged), which describe states the database file no longer starts from;
- a log whose header is zeroed or fails its checksum, which SQLite does not read;
- freelist pages, freeblocks and unallocated space in the database file;
- rollback journals.

A state is only exact when the database file still holds, for every page the log
touches later, the content it had then. Once a checkpoint has copied part of the
log into the database file, the states before that point are only readable where
every page the checkpoint wrote was also written earlier in the log. States that
fail that test are skipped and counted, never rebuilt from a mix of times.

Format: https://www.sqlite.org/fileformat2.html#the_write_ahead_log
"""

import hashlib
import os
import shutil
import sqlite3
import struct
import tempfile
from pathlib import Path

WAL_MAGIC = (0x377F0682, 0x377F0683)
WAL_HEADER_SIZE = 32
FRAME_HEADER_SIZE = 24
DEFAULT_MAX_STATES = 2000


def _wal_checksum(data, big_endian, state=(0, 0)):
    """SQLite's WAL checksum over data (a multiple of 8 bytes), continuing from state."""
    first, second = state
    words = struct.unpack(('>' if big_endian else '<') + str(len(data) // 4) + 'I', data)
    for index in range(0, len(words), 2):
        first = (first + words[index] + second) & 0xFFFFFFFF
        second = (second + words[index + 1] + first) & 0xFFFFFFFF
    return first, second


class WalLog:
    """The frame layout of one write-ahead log, as SQLite would validate it.

    commits holds (transaction number, frame number) for each commit frame in the
    checksum-valid prefix of the current generation, transaction numbers from 1.
    """

    def __init__(self, wal_path):
        self.path = wal_path
        self.page_size = 0
        self.header_valid = False
        self.reason = ''
        self.total_frames = 0
        self.valid_frames = 0
        self.uncommitted_frames = 0
        self.other_frames = 0
        self.trailing_bytes = 0
        self.commits = []
        self.frame_pages = []
        self.frame_hashes = []
        self._read()

    def _read(self):
        with open(self.path, 'rb') as handle:
            data = handle.read()
        if len(data) < WAL_HEADER_SIZE:
            self.reason = f'log is {len(data)} bytes, shorter than its header'
            return
        magic, _version, page_size, _sequence, salt1, salt2, sum1, sum2 = struct.unpack(
            '>8I', data[:WAL_HEADER_SIZE])
        if magic not in WAL_MAGIC:
            self.reason = f'log header magic is 0x{magic:08x}, not a WAL header'
            return
        page_size = 65536 if page_size == 1 else page_size
        if page_size < 512 or page_size > 65536 or page_size & (page_size - 1):
            self.reason = f'log header page size {page_size} is not valid'
            return
        big_endian = magic & 1
        state = _wal_checksum(data[:24], big_endian)
        if state != (sum1, sum2):
            self.reason = 'log header checksum does not match'
            return
        self.header_valid = True
        self.page_size = page_size
        frame_size = FRAME_HEADER_SIZE + page_size
        self.total_frames, self.trailing_bytes = divmod(len(data) - WAL_HEADER_SIZE, frame_size)
        last_commit = 0
        for index in range(self.total_frames):
            offset = WAL_HEADER_SIZE + index * frame_size
            page_number, commit_size, frame_salt1, frame_salt2, check1, check2 = struct.unpack(
                '>6I', data[offset:offset + FRAME_HEADER_SIZE])
            if (frame_salt1, frame_salt2) != (salt1, salt2) or page_number == 0:
                break
            image = data[offset + FRAME_HEADER_SIZE:offset + frame_size]
            state = _wal_checksum(data[offset:offset + 8] + image, big_endian, state)
            if state != (check1, check2):
                break
            self.valid_frames = index + 1
            self.frame_pages.append(page_number)
            self.frame_hashes.append(hashlib.sha1(image).digest())
            if commit_size:
                last_commit = index + 1
                self.commits.append((len(self.commits) + 1, index + 1))
        self.uncommitted_frames = self.valid_frames - last_commit
        self.other_frames = self.total_frames - self.valid_frames
        del self.frame_pages[last_commit:]
        del self.frame_hashes[last_commit:]


def _checkpointed_through(db_path, log):
    """The last frame a checkpoint is known to have copied into the database file, or 0.

    For each commit, the database file is consistent with it when every page the log
    has touched so far holds the image that commit left. The latest such commit is
    taken as the checkpoint point. A page that coincidentally matches can only move
    the point later, which skips states rather than admitting a mixed one.
    """
    if not log.frame_pages:
        return 0
    page_size = log.page_size
    db_hashes = {}
    with open(db_path, 'rb') as handle:
        for page in set(log.frame_pages):
            handle.seek((page - 1) * page_size)
            image = handle.read(page_size)
            db_hashes[page] = hashlib.sha1(image).digest() if len(image) == page_size else None
    latest = {}
    mismatched = set()
    commit_frames = {frame for _number, frame in log.commits}
    through = 0
    for index, page in enumerate(log.frame_pages):
        latest[page] = log.frame_hashes[index]
        if latest[page] == db_hashes[page]:
            mismatched.discard(page)
        else:
            mismatched.add(page)
        if index + 1 in commit_frames and not mismatched:
            through = index + 1
    return through


class WalStates:
    """Open each committed state of a WAL-mode database read-only, newest first.

    Use as a context manager; the scratch copies are removed on exit. The evidence
    files are only read.

        with WalStates(db_path) as wal:
            for state in wal.states():
                rows = state.connection.execute(query).fetchall()

    state.number is the count of committed transactions it includes (0 for the
    database file before any log frame) and state.frame the log frame that commits it.
    """

    class State:
        def __init__(self, number, frame, connection):
            self.number = number
            self.frame = frame
            self.connection = connection

    def __init__(self, db_path, max_states=DEFAULT_MAX_STATES):
        self.db_path = str(db_path)
        self.wal_path = self.db_path + '-wal'
        self.max_states = max_states
        self.log = None
        self.checkpointed_frame = 0
        self.skipped_mixed = 0
        self.skipped_limit = 0
        self.readable = []
        self._work = None
        self._connection = None
        if not os.path.isfile(self.wal_path) or not os.path.getsize(self.wal_path):
            return
        self.log = WalLog(self.wal_path)
        if not self.log.commits:
            return
        self.checkpointed_frame = _checkpointed_through(self.db_path, self.log)
        self.readable = self._readable_states()

    def _readable_states(self):
        log = self.log
        first_touch = {}
        for index, page in enumerate(log.frame_pages):
            first_touch.setdefault(page, index + 1)
        through = self.checkpointed_frame
        late_pages = sorted(frame for frame in first_touch.values() if frame <= through)
        candidates = [(0, 0)] + list(log.commits)
        readable = []
        for number, frame in candidates:
            # A state before the checkpoint point is exact only when no page the
            # checkpoint wrote was first written after this state.
            if frame < through and late_pages and late_pages[-1] > frame:
                self.skipped_mixed += 1
                continue
            readable.append((number, frame))
        if len(readable) > self.max_states:
            self.skipped_limit = len(readable) - self.max_states
            readable = readable[-self.max_states:]
        return readable

    def summary(self):
        """One line describing what was replayed and what was not, for the log."""
        name = os.path.basename(self.db_path)
        if self.log is None:
            return f'{name}: no write-ahead log beside the database'
        log = self.log
        if not log.header_valid:
            return f'{name}: write-ahead log not read ({log.reason})'
        parts = [f'{name}: {log.total_frames} log frames, {len(log.commits)} committed '
                 f'transactions, {len(self.readable)} states read']
        if self.checkpointed_frame:
            parts.append(f'database file already holds the log through frame '
                         f'{self.checkpointed_frame}')
        if self.skipped_mixed:
            parts.append(f'{self.skipped_mixed} states before that checkpoint not readable')
        if self.skipped_limit:
            parts.append(f'{self.skipped_limit} oldest states over the limit of '
                         f'{self.max_states} not read')
        if log.uncommitted_frames:
            parts.append(f'{log.uncommitted_frames} frames after the last commit not read')
        if log.other_frames:
            parts.append(f'{log.other_frames} frames from an earlier log generation or '
                         f'failing their checksum not read')
        if log.trailing_bytes:
            parts.append(f'{log.trailing_bytes} bytes after the last whole frame')
        return '; '.join(parts)

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        if self._work:
            shutil.rmtree(self._work, ignore_errors=True)
            self._work = None

    def states(self):
        """Yield a State for each readable committed state, newest first.

        Each connection is closed before the next state is opened.
        """
        if not self.readable:
            return
        self._work = tempfile.mkdtemp(prefix='leapp-wal-')
        db_copy = os.path.join(self._work, 'state.db')
        wal_copy = db_copy + '-wal'
        shm_copy = db_copy + '-shm'
        shutil.copyfile(self.db_path, db_copy)
        shutil.copyfile(self.wal_path, wal_copy)
        frame_size = FRAME_HEADER_SIZE + self.log.page_size
        uri = Path(db_copy).as_uri()
        for number, frame in reversed(self.readable):
            if os.path.exists(shm_copy):
                os.unlink(shm_copy)
            if number:
                os.truncate(wal_copy, WAL_HEADER_SIZE + frame * frame_size)
                self._connection = sqlite3.connect(uri + '?mode=ro', uri=True)
            else:
                os.unlink(wal_copy)
                self._connection = sqlite3.connect(uri + '?mode=ro&immutable=1', uri=True)
            yield WalStates.State(number, frame, self._connection)
            self._connection.close()
            self._connection = None


class EarlierRow:
    """A row read from an earlier committed state that the current state does not hold."""

    def __init__(self, values, status, first_state, last_state, first_frame, last_frame):
        self.values = values
        self.status = status
        self.first_state = first_state
        self.last_state = last_state
        self.first_frame = first_frame
        self.last_frame = last_frame


NOT_IN_CURRENT = 'Not in current state'
EARLIER_VERSION = 'Earlier version of a current row'


def rows_not_in_current(db_path, query, params=(), key_columns=None,
                        max_states=DEFAULT_MAX_STATES):
    """Rows the query returns in an earlier committed state but not in the current one.

    Returns (columns, rows, wal) where rows is a list of EarlierRow, oldest first, and
    wal is the WalStates object for its summary(). Rows compare by every value the
    query returns. With key_columns (indexes into the result), a row whose key the
    current state still holds is labelled EARLIER_VERSION, otherwise NOT_IN_CURRENT.
    A state in which the query fails (its table not created yet, or a column added
    later) contributes no rows.
    """
    columns = []
    current = None
    current_keys = set()
    found = {}
    with WalStates(db_path, max_states=max_states) as wal:
        for state in wal.states():
            try:
                cursor = state.connection.execute(query, params)
                rows = cursor.fetchall()
            except sqlite3.Error:
                if current is None:
                    break
                continue
            if current is None:
                columns = [item[0] for item in cursor.description]
                current = set(rows)
                if key_columns:
                    current_keys = {tuple(row[i] for i in key_columns) for row in current}
                continue
            for row in rows:
                if row in current:
                    continue
                seen = found.get(row)
                if seen is None:
                    found[row] = [state.number, state.number, state.frame, state.frame]
                else:
                    seen[0], seen[2] = state.number, state.frame
    result = []
    for row, (first, last, first_frame, last_frame) in found.items():
        status = NOT_IN_CURRENT
        if key_columns and tuple(row[i] for i in key_columns) in current_keys:
            status = EARLIER_VERSION
        result.append(EarlierRow(row, status, first, last, first_frame, last_frame))
    result.sort(key=lambda item: (item.first_state, item.last_state))
    return columns, result, wal
