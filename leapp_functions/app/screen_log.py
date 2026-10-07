"""Recoverable HTML run logging. Author: @AlexisBrignoni, Codex."""
from collections import deque
from contextlib import contextmanager
import errno
import os
import threading


class ScreenLogWriter:
    """Keep one run handle, with bounded replay when descriptors are unavailable."""

    MAX_PENDING_BYTES = 1024 * 1024
    MAX_PENDING_MESSAGES = 1024

    def __init__(self):
        self._path = ''
        self._handle = None
        self._pending = deque()
        self._pending_bytes = 0
        self._dropped = 0
        self._unavailable = False
        self._sessions = 0
        self._lock = threading.RLock()

    @staticmethod
    def _is_exhaustion(exc):
        return exc.errno in (errno.EMFILE, errno.ENFILE)

    @staticmethod
    def _encode(text):
        # Match open(..., encoding='utf8') newline translation on Windows. An
        # unbuffered binary handle lets a short write retain only its unwritten
        # suffix, instead of replaying bytes a text buffer may already have sent.
        return text.replace('\n', os.linesep).encode('utf8')

    def _open(self):
        if self._handle is None and self._path:
            self._handle = open(self._path, 'ab', buffering=0)  # pylint: disable=consider-using-with

    def _close_handle(self):
        if self._handle is not None:
            handle, self._handle = self._handle, None
            handle.close()

    def _select_path(self, path):
        path = os.fspath(path) if path else ''
        if path != self._path:
            self.close()
            self._path = path

    def _send(self, data):
        while data:
            try:
                written = self._handle.write(data)
            except OSError as exc:
                if not self._is_exhaustion(exc):
                    raise
                return data, exc
            if not written:
                raise OSError(errno.EIO, 'HTML log write made no progress')
            data = data[written:]
        return b'', None

    def _drain(self):
        self._open()
        while self._pending or self._dropped:
            if not self._pending:
                notice = (f'HTML log buffer full: {self._dropped} message(s) omitted; '
                          'console/GUI logging continued.<br>\n')
                self._pending.append(self._encode(notice))
                self._pending_bytes = len(self._pending[0])
                self._dropped = 0
            original = self._pending[0]
            remaining, error = self._send(original)
            self._pending_bytes -= len(original) - len(remaining)
            if remaining:
                self._pending[0] = remaining
            else:
                self._pending.popleft()
            if error:
                raise error

    def _remember(self, data):
        if not data:
            return
        # Once full, omit subsequent messages until the earlier ones and their
        # omission notice can be written. This preserves chronological order.
        if (self._dropped or len(self._pending) >= self.MAX_PENDING_MESSAGES
                or self._pending_bytes + len(data) > self.MAX_PENDING_BYTES):
            self._dropped += 1
        else:
            self._pending.append(data)
            self._pending_bytes += len(data)

    def write(self, path, text):
        """Append now, or retain the unwritten bytes for the next recovery attempt."""
        with self._lock:
            self._select_path(path)
            if not self._path:
                return
            data = self._encode(text)
            try:
                self._drain()
                data, error = self._send(data)
                if error:
                    raise error
            except OSError as exc:
                if not self._is_exhaustion(exc):
                    raise
                self._remember(data)
                if not self._unavailable:
                    print(f'HTML log unavailable ({exc}); buffering messages; '
                          'console/GUI logging continues.')
                self._unavailable = True
            else:
                self._unavailable = False
            finally:
                # Legacy calls outside a processing session retain the old
                # open/close lifecycle, but can still replay pending messages.
                if not self._sessions:
                    self._close_handle()

    def close(self):
        """Retry pending output, then release the handle on every exit path."""
        with self._lock:
            try:
                if self._pending or self._dropped:
                    try:
                        self._drain()
                    except OSError as exc:
                        if not self._is_exhaustion(exc):
                            raise
                        print(f'HTML log unavailable at close ({exc}); '
                              f'{len(self._pending)} buffered message(s) remain unwritten '
                              f'and {self._dropped} message(s) were omitted. '
                              'See console/GUI output for these messages.')
            finally:
                self._close_handle()
                self._pending.clear()
                self._pending_bytes = 0
                self._dropped = 0
                self._unavailable = False
                self._path = ''

    @contextmanager
    def session(self, path):
        """Own the persistent handle for a processing run, including early exits."""
        with self._lock:
            self._select_path(path)
            self._sessions += 1
        try:
            with self._lock:
                try:
                    self._open()
                except OSError as exc:
                    if not self._is_exhaustion(exc):
                        raise
                    # logfunc establishes GUI routing before emitting the notice.
            yield
        finally:
            with self._lock:
                self._sessions -= 1
                if not self._sessions:
                    self.close()
