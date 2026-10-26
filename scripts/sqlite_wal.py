"""States of a SQLite database held in its write-ahead log.

A database in WAL mode keeps each committed transaction as frames appended to
<db>-wal until a checkpoint copies them into the database file. Until the log is
reset, the frames of earlier transactions stay in it, so the log holds every
committed state of the database since the last reset, not only the latest one.
A row deleted, or changed, in one of those later transactions can still be read
from the state before it.

Committed states of the current log generation are read by SQLite itself. A scratch
copy of the database and its log is made, the log copy is cut at the end of a
committed transaction, and the copy is opened read-only, so SQLite applies its own
salt, checksum and commit rules to the frames that remain. That is the set of frames
SQLite itself reads at acquisition, cut at each commit.

Two further kinds of state are read only when a caller asks for them (include=):

- KIND_EARLIER: the previous log generation. When the log is reset, the next
  generation overwrites it from the first frame, so a generation longer than the
  one after it leaves its later frames behind. The database file then holds that
  generation's final state, as long as the current generation has not been
  checkpointed. An earlier state is rebuilt by writing the left-over frames' page
  images onto a scratch copy of the database file at the offsets their page numbers
  name, and SQLite reads the result. It is read only when every gate holds: the
  database file matches the generation's last commit on every page the left-over
  frames touch; every page written after the state has an image at or before it; every
  page the state's size covers comes from the file or a frame; and SQLite's
  quick_check passes. The first left-over frame's checksum cannot be verified, since
  the frame it chains from was overwritten.
- KIND_UNCOMMITTED: frames after the last commit of the current generation, a
  transaction that had not committed when the files were copied. It is rebuilt the
  same way on top of the current state and read only if quick_check passes.

Not read, and counted (see WalStates.summary): frames of generations older than the
previous one, frames after a checksum break, freelist pages, freeblocks and
unallocated space in the database file, and rollback journals.

Committed states of the current generation are only exact when the database file
still holds, for every page the log touches later, the content it had then. Once a
checkpoint has copied part of the log into the database file, the states before
that point are only readable where every page the checkpoint wrote was also written
earlier in the log. States that fail a test are skipped and counted, never rebuilt
from a mix of times.

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

KIND_COMMITTED = 'committed'
KIND_UNCOMMITTED = 'uncommitted'
KIND_EARLIER = 'earlier generation'


def _wal_checksum(data, big_endian, state=(0, 0)):
    """SQLite's WAL checksum over data (a multiple of 8 bytes), continuing from state."""
    first, second = state
    words = struct.unpack(('>' if big_endian else '<') + str(len(data) // 4) + 'I', data)
    for index in range(0, len(words), 2):
        first = (first + words[index] + second) & 0xFFFFFFFF
        second = (second + words[index + 1] + first) & 0xFFFFFFFF
    return first, second


def _valid_page_size(size):
    size = 65536 if size == 1 else size
    return size if 512 <= size <= 65536 and not size & (size - 1) else 0


def _db_page_size(db_path):
    """Page size from the database header, or 0."""
    try:
        with open(db_path, 'rb') as handle:
            header = handle.read(18)
    except OSError:
        return 0
    if len(header) < 18 or header[:16] != b'SQLite format 3\x00':
        return 0
    return _valid_page_size(struct.unpack('>H', header[16:18])[0])


class EarlierRun:
    """The contiguous frames the previous log generation left after the current one.

    frames holds (frame number, page number, commit size, image offset) for each
    checksum-verified frame up to and including the run's last commit frame.
    """

    def __init__(self):
        self.salts = None
        self.frames = []
        self.commits = []
        self.after_break_pages = set()
        self.after_break_frames = 0
        self.uncommitted_frames = 0


class WalLog:
    """The frame layout of one write-ahead log, as SQLite would validate it.

    commits holds (transaction number, frame number) for each commit frame in the
    checksum-valid prefix of the current generation, transaction numbers from 1.
    """

    def __init__(self, wal_path, fallback_page_size=0):
        self.path = wal_path
        self.page_size = 0
        self.header_valid = False
        self.reason = ''
        self.total_frames = 0
        self.valid_frames = 0
        self.uncommitted_frames = 0
        self.other_frames = 0
        self.older_frames = 0
        self.trailing_bytes = 0
        self.commits = []
        self.frame_pages = []
        self.frame_hashes = []
        self.earlier = None
        self.big_endian = True
        self.data = b''
        self._read(fallback_page_size)

    def image(self, offset):
        return self.data[offset:offset + self.page_size]

    def frame_header(self, index):
        offset = WAL_HEADER_SIZE + index * (FRAME_HEADER_SIZE + self.page_size)
        page_number, commit_size, salt1, salt2, check1, check2 = struct.unpack(
            '>6I', self.data[offset:offset + FRAME_HEADER_SIZE])
        return offset, page_number, commit_size, (salt1, salt2), (check1, check2)

    def _chain(self, index, state):
        offset = WAL_HEADER_SIZE + index * (FRAME_HEADER_SIZE + self.page_size)
        image_offset = offset + FRAME_HEADER_SIZE
        return _wal_checksum(self.data[offset:offset + 8] +
                             self.data[image_offset:image_offset + self.page_size],
                             self.big_endian, state)

    def _read(self, fallback_page_size):
        with open(self.path, 'rb') as handle:
            self.data = data = handle.read()
        if len(data) < WAL_HEADER_SIZE:
            self.reason = f'log is {len(data)} bytes, shorter than its header'
            return
        magic, _version, page_size, _sequence, salt1, salt2, sum1, sum2 = struct.unpack(
            '>8I', data[:WAL_HEADER_SIZE])
        header_salts = None
        if magic not in WAL_MAGIC:
            self.reason = f'log header magic is 0x{magic:08x}, not a WAL header'
        elif not _valid_page_size(page_size):
            self.reason = f'log header page size {page_size} is not valid'
        else:
            self.big_endian = bool(magic & 1)
            if _wal_checksum(data[:24], self.big_endian) != (sum1, sum2):
                self.reason = 'log header checksum does not match'
            else:
                self.header_valid = True
                header_salts = (salt1, salt2)
                page_size = _valid_page_size(page_size)
        self.page_size = page_size if self.header_valid else _valid_page_size(fallback_page_size)
        if not self.page_size:
            return
        frame_size = FRAME_HEADER_SIZE + self.page_size
        self.total_frames, self.trailing_bytes = divmod(len(data) - WAL_HEADER_SIZE, frame_size)
        if self.header_valid:
            self._read_current(header_salts, (sum1, sum2))
        self._read_earlier(header_salts)
        run = self.earlier
        used = self.valid_frames + (len(run.frames) + run.uncommitted_frames +
                                    run.after_break_frames if run else 0)
        self.other_frames = self.total_frames - self.valid_frames
        self.older_frames = self.total_frames - used

    def _read_current(self, salts, state):
        last_commit = 0
        for index in range(self.total_frames):
            offset, page_number, commit_size, frame_salts, checks = self.frame_header(index)
            if frame_salts != salts or page_number == 0:
                break
            state = self._chain(index, state)
            if state != checks:
                break
            self.valid_frames = index + 1
            self.frame_pages.append(page_number)
            self.frame_hashes.append(hashlib.sha1(self.image(offset + FRAME_HEADER_SIZE)).digest())
            if commit_size:
                last_commit = index + 1
                self.commits.append((len(self.commits) + 1, index + 1))
        self.uncommitted_frames = self.valid_frames - last_commit
        del self.frame_pages[last_commit:]
        del self.frame_hashes[last_commit:]

    def _read_earlier(self, header_salts):
        """Find the previous generation's left-over run, after the current generation.

        With a valid header the run starts right after the current generation's valid
        frames and carries salt-1 one less than the header's (SQLite increments salt-1
        at each reset). With an unusable header there is no current generation and the
        run is the generation that starts at frame 1.
        """
        start = self.valid_frames
        if start >= self.total_frames:
            return
        _offset, page_number, _size, salts, _checks = self.frame_header(start)
        if page_number == 0:
            return
        if header_salts is not None and salts[0] != (header_salts[0] - 1) & 0xFFFFFFFF:
            return
        run = EarlierRun()
        run.salts = salts
        members = []
        for index in range(start, self.total_frames):
            frame = self.frame_header(index)
            if frame[3] != salts or frame[1] == 0:
                break
            members.append((index, frame))
        if header_salts is None and len(members) > 1:
            # No header to name the byte order: take the one under which the chain holds.
            for big_endian in (True, False):
                self.big_endian = big_endian
                if self._chain(members[1][0], members[0][1][4]) == members[1][1][4]:
                    break
        verified = members[:1]
        for (index, frame), (_previous, previous) in zip(members[1:], members):
            if self._chain(index, previous[4]) != frame[4]:
                break
            verified.append((index, frame))
        for _index, frame in members[len(verified):]:
            run.after_break_pages.add(frame[1])
        run.after_break_frames = len(members) - len(verified)
        last_commit = 0
        for position, (index, frame) in enumerate(verified):
            offset, page_number, commit_size = frame[0], frame[1], frame[2]
            run.frames.append((index + 1, page_number, commit_size, offset + FRAME_HEADER_SIZE))
            if commit_size:
                last_commit = position + 1
                run.commits.append((len(run.commits) + 1, index + 1))
        run.uncommitted_frames = len(run.frames) - last_commit
        del run.frames[last_commit:]
        if run.frames or run.after_break_frames or run.uncommitted_frames:
            self.earlier = run


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
    """Open each readable state of a WAL-mode database read-only.

    Use as a context manager; the scratch copies are removed on exit. The evidence
    files are only read.

        with WalStates(db_path) as wal:
            for state in wal.states():
                rows = state.connection.execute(query).fetchall()

    The first state yielded is the current one. Then come the uncommitted state when
    asked for, the earlier committed states newest first, and the previous generation's
    states newest first when asked for. state.kind is one of KIND_COMMITTED,
    KIND_UNCOMMITTED and KIND_EARLIER. For a committed state, state.number is the count
    of committed transactions it includes (0 for the database file before any log
    frame); for an earlier-generation state, it counts the commits among that
    generation's left-over frames. state.frame is the log frame that ends the state.
    """

    class State:
        def __init__(self, number, frame, connection, kind=KIND_COMMITTED):
            self.number = number
            self.frame = frame
            self.connection = connection
            self.kind = kind

    def __init__(self, db_path, max_states=DEFAULT_MAX_STATES, include=(KIND_COMMITTED,)):
        self.db_path = str(db_path)
        self.wal_path = self.db_path + '-wal'
        self.max_states = max_states
        self.include = tuple(include)
        self.log = None
        self.checkpointed_frame = 0
        self.skipped_mixed = 0
        self.skipped_limit = 0
        self.readable = []
        self.earlier_readable = []
        self.earlier_reason = ''
        self.earlier_skipped = 0
        self.earlier_failed_check = 0
        self.uncommitted_failed_check = False
        self._work = None
        self._connection = None
        if not os.path.isfile(self.wal_path) or not os.path.getsize(self.wal_path):
            return
        self.log = WalLog(self.wal_path, _db_page_size(self.db_path))
        if self.log.commits:
            self.checkpointed_frame = _checkpointed_through(self.db_path, self.log)
            self.readable = self._readable_states()
        if KIND_EARLIER in self.include and self.log.earlier and self.log.earlier.commits:
            self.earlier_readable = self._earlier_states()
            if self.earlier_readable and not self.readable:
                # No current generation: the database file alone is the current state.
                self.readable = [(0, 0)]

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

    def _db_hashes(self, pages):
        page_size = self.log.page_size
        hashes = {}
        with open(self.db_path, 'rb') as handle:
            for page in pages:
                handle.seek((page - 1) * page_size)
                image = handle.read(page_size)
                hashes[page] = hashlib.sha1(image).digest() if len(image) == page_size else None
        return hashes

    def _earlier_states(self):
        """(number, frame, {page: image offset}, size in pages) for each earlier state
        that passes the gates, newest first."""
        log, run = self.log, self.log.earlier
        if self.checkpointed_frame:
            self.earlier_reason = 'the database file already holds part of the current log'
            self.earlier_skipped = len(run.commits)
            return []
        if self.log.frame_pages:
            # The current generation must not have reached the database file at all.
            current_pages = set(self.log.frame_pages)
            current_hashes = self._db_hashes(current_pages)
            latest = {}
            for page, digest in zip(self.log.frame_pages, self.log.frame_hashes):
                latest[page] = digest
            if any(latest[page] == current_hashes[page] for page in current_pages):
                self.earlier_reason = ('the database file may already hold part of the '
                                       'current log')
                self.earlier_skipped = len(run.commits)
                return []
        final = {}
        for _frame, page, _size, offset in run.frames:
            final[page] = offset
        db_hashes = self._db_hashes(final)
        for page, offset in final.items():
            if hashlib.sha1(log.image(offset)).digest() != db_hashes[page]:
                self.earlier_reason = ('the database file does not hold the previous '
                                       'generation\'s last commit')
                self.earlier_skipped = len(run.commits)
                return []
        file_pages = os.path.getsize(self.db_path) // log.page_size
        last_write = {}
        for position, (_frame, page, _size, _offset) in enumerate(run.frames):
            last_write[page] = position
        states = []
        images = {}
        commit_positions = {frame: number for number, frame in run.commits}
        for position, (frame, page, size, offset) in enumerate(run.frames):
            images[page] = offset
            number = commit_positions.get(frame)
            if number is None or number == len(run.commits):
                continue
            # Only pages inside this state's size matter: a page allocated later was not
            # part of it, and truncating to the size removes it.
            later = {p for p, last in last_write.items() if last > position and p <= size}
            later |= {p for p in run.after_break_pages if p <= size}
            if any(p not in images for p in later):
                self.earlier_skipped += 1
                continue
            if any(p > file_pages and p not in images for p in range(1, size + 1)):
                self.earlier_skipped += 1
                continue
            states.append((number, frame, dict(images), size))
        states.reverse()
        if len(states) > self.max_states:
            self.earlier_skipped += len(states) - self.max_states
            states = states[:self.max_states]
        return states

    def summary(self):
        """One line describing what was read and what was not, for the log."""
        name = os.path.basename(self.db_path)
        if self.log is None:
            return f'{name}: no write-ahead log beside the database'
        log = self.log
        earlier = KIND_EARLIER in self.include
        if not log.header_valid and not (earlier and log.earlier):
            return f'{name}: write-ahead log not read ({log.reason})'
        if log.header_valid:
            parts = [f'{name}: {log.total_frames} log frames, {len(log.commits)} committed '
                     f'transactions, {len(self.readable)} states read']
        else:
            parts = [f'{name}: {log.total_frames} log frames under an unusable header '
                     f'({log.reason}), database file read as the current state']
        if self.checkpointed_frame:
            parts.append(f'database file already holds the log through frame '
                         f'{self.checkpointed_frame}')
        if self.skipped_mixed:
            parts.append(f'{self.skipped_mixed} states before that checkpoint not readable')
        if self.skipped_limit:
            parts.append(f'{self.skipped_limit} oldest states over the limit of '
                         f'{self.max_states} not read')
        if log.uncommitted_frames:
            read = (KIND_UNCOMMITTED in self.include and not self.uncommitted_failed_check)
            parts.append(f'{log.uncommitted_frames} frames after the last commit '
                         f'{"read as an uncommitted state" if read else "not read"}')
        run = log.earlier
        if run and earlier:
            parts.append(f'{len(run.frames)} frames left by the previous generation, '
                         f'{len(self.earlier_readable) - self.earlier_failed_check} of its '
                         f'{len(run.commits)} commits read'
                         + (f' ({self.earlier_reason})' if self.earlier_reason else ''))
            if run.after_break_frames:
                parts.append(f'{run.after_break_frames} of its frames after a checksum break '
                             f'not read')
            if self.earlier_failed_check:
                parts.append(f'{self.earlier_failed_check} rebuilt states failed quick_check')
        elif log.other_frames:
            parts.append(f'{log.other_frames} frames from an earlier log generation or '
                         f'failing their checksum not read')
        if earlier and run and log.older_frames:
            parts.append(f'{log.older_frames} frames from older generations or failing their '
                         f'checksum not read')
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

    def _open_rebuilt(self, path, images, size):
        """Write page images onto a copy of the database file and open it, or None
        when SQLite's quick_check does not pass."""
        page_size = self.log.page_size
        shutil.copyfile(self.db_path, path)
        with open(path, 'r+b') as handle:
            for page, offset in images.items():
                handle.seek((page - 1) * page_size)
                handle.write(self.log.image(offset))
            handle.truncate(size * page_size)
        connection = sqlite3.connect(Path(path).as_uri() + '?mode=ro&immutable=1', uri=True)
        try:
            ok = connection.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
        except sqlite3.Error:
            ok = False
        if not ok:
            connection.close()
            return None
        return connection

    def _uncommitted(self, path):
        log = self.log
        images = {}
        commit_size = 0
        frame_size = FRAME_HEADER_SIZE + log.page_size
        for index in range(log.valid_frames):
            _offset, page, size, _salts, _checks = log.frame_header(index)
            images[page] = WAL_HEADER_SIZE + index * frame_size + FRAME_HEADER_SIZE
            if size:
                commit_size = size
        file_pages = os.path.getsize(self.db_path) // log.page_size
        size = max([commit_size or file_pages] + list(images))
        return self._open_rebuilt(path, images, size)

    def states(self):
        """Yield a State for each readable state, current first, as the class says.

        Each connection is closed before the next state is opened.
        """
        if not self.readable:
            return
        self._work = tempfile.mkdtemp(prefix='leapp-wal-')
        db_copy = os.path.join(self._work, 'state.db')
        wal_copy = db_copy + '-wal'
        shm_copy = db_copy + '-shm'
        rebuilt = os.path.join(self._work, 'rebuilt.db')
        shutil.copyfile(self.db_path, db_copy)
        if self.log.header_valid:
            shutil.copyfile(self.wal_path, wal_copy)
        frame_size = FRAME_HEADER_SIZE + self.log.page_size
        uri = Path(db_copy).as_uri()
        for position, (number, frame) in enumerate(reversed(self.readable)):
            if os.path.exists(shm_copy):
                os.unlink(shm_copy)
            if number:
                os.truncate(wal_copy, WAL_HEADER_SIZE + frame * frame_size)
                self._connection = sqlite3.connect(uri + '?mode=ro', uri=True)
            else:
                if os.path.exists(wal_copy):
                    os.unlink(wal_copy)
                self._connection = sqlite3.connect(uri + '?mode=ro&immutable=1', uri=True)
            yield WalStates.State(number, frame, self._connection)
            self._connection.close()
            self._connection = None
            if position == 0 and KIND_UNCOMMITTED in self.include and self.log.uncommitted_frames:
                self._connection = self._uncommitted(rebuilt)
                if self._connection is None:
                    self.uncommitted_failed_check = True
                else:
                    yield WalStates.State(len(self.log.commits), self.log.valid_frames,
                                          self._connection, KIND_UNCOMMITTED)
                    self._connection.close()
                    self._connection = None
        for number, frame, images, size in self.earlier_readable:
            self._connection = self._open_rebuilt(rebuilt, images, size)
            if self._connection is None:
                self.earlier_failed_check += 1
                continue
            yield WalStates.State(number, frame, self._connection, KIND_EARLIER)
            self._connection.close()
            self._connection = None


class EarlierRow:
    """A row read from another state that the current state does not hold.

    first_state and last_state are the oldest and newest committed states of the
    current generation the row was read in (None when it was read in none of them);
    earlier_generation is the (oldest, newest) commit of the previous generation's
    left-over frames it was read in, or None; uncommitted says whether the uncommitted
    state held it.
    """

    def __init__(self, values, status, first_state, last_state, first_frame, last_frame,
                 earlier_generation=None, uncommitted=False):
        self.values = values
        self.status = status
        self.first_state = first_state
        self.last_state = last_state
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.earlier_generation = earlier_generation
        self.uncommitted = uncommitted


NOT_IN_CURRENT = 'Not in current state'
EARLIER_VERSION = 'Earlier version of a current row'
UNCOMMITTED_CHANGE = 'Only in uncommitted frames'


def rows_not_in_current(db_path, query, params=(), key_columns=None,
                        max_states=DEFAULT_MAX_STATES, include=(KIND_COMMITTED,)):
    """Rows the query returns in another state but not in the current one.

    Returns (columns, rows, wal) where rows is a list of EarlierRow, oldest first, and
    wal is the WalStates object for its summary(). include chooses the kinds of state
    read besides the current one (see WalStates). Rows compare by every value the
    query returns. With key_columns (indexes into the result), a row whose key the
    current state still holds is labelled EARLIER_VERSION, otherwise NOT_IN_CURRENT; a
    row read only in the uncommitted state is labelled UNCOMMITTED_CHANGE. A state in
    which the query fails (its table not created yet, or a column added later)
    contributes no rows.
    """
    columns = []
    current = None
    current_keys = set()
    found = {}
    with WalStates(db_path, max_states=max_states, include=include) as wal:
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
                seen = found.setdefault(row, {'committed': None, 'earlier': None,
                                              'uncommitted': False})
                if state.kind == KIND_UNCOMMITTED:
                    seen['uncommitted'] = True
                    continue
                slot = 'committed' if state.kind == KIND_COMMITTED else 'earlier'
                if seen[slot] is None:
                    seen[slot] = [state.number, state.number, state.frame, state.frame]
                else:
                    seen[slot][0], seen[slot][2] = state.number, state.frame
    result = []
    for row, seen in found.items():
        committed, earlier = seen['committed'], seen['earlier']
        if committed is None and earlier is None:
            status = UNCOMMITTED_CHANGE
        elif key_columns and tuple(row[i] for i in key_columns) in current_keys:
            status = EARLIER_VERSION
        else:
            status = NOT_IN_CURRENT
        first, last, first_frame, last_frame = committed or (None, None, None, None)
        result.append(EarlierRow(row, status, first, last, first_frame, last_frame,
                                 (earlier[0], earlier[1]) if earlier else None,
                                 seen['uncommitted']))

    def order(item):
        if item.earlier_generation and item.first_state is None:
            return (0, item.earlier_generation[0], item.earlier_generation[1])
        if item.first_state is not None:
            return (1, item.first_state, item.last_state)
        return (2, 0, 0)
    result.sort(key=order)
    return columns, result, wal
