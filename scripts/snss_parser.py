"""Reader for Chromium SNSS session files, specifically the tab restore files Chrome and the
other Chromium browsers write as Sessions/Tabs_<timestamp>.

On-disk shape, derived from the files themselves and confirmed against Chromium's own code:

    "SNSS"            4 bytes of magic
    version           int32, 1 or 3
    then records of   uint16 size, then `size` bytes whose first byte is the command id and
                      whose remainder is that command's payload

The command ids are Chromium's, from components/sessions/core/tab_restore_service_impl.cc:
kCommandUpdateTabNavigation = 1, kCommandRestoredEntry = 2, kCommandWindowDeprecated = 3,
kCommandSelectedNavigationInTab = 4, kCommandPinnedState = 5, kCommandSetExtensionAppID = 6,
kCommandSetWindowAppName = 7, kCommandSetTabUserAgentOverride = 8, kCommandWindow = 9,
kCommandSetTabGroupData = 10, kCommandSetTabUserAgentOverride2 = 11,
kCommandSetWindowUserTitle = 12, kCommandCreateGroup = 13, kCommandAddTabExtraData = 14,
kCommandCreateSplit = 15, kCommandSetTabSplitData = 16. Ids outside that list are returned as
stored and are not interpreted here.

These ids belong to the tab restore file. Chromium's session files use a different set for the
same magic, so this reader is for Tabs_ files only.

Two command payloads are decoded:

* Command 1 carries a base::Pickle: an int tab id followed by a SerializedNavigationEntry, whose
  field order is set by WriteToPickle in components/sessions/core/serialized_navigation_entry.cc:
  index, virtual url, title, encoded page state, transition type, type mask, referrer url, an
  obsolete referrer policy int, original request url, is overriding user agent, timestamp,
  an empty placeholder string16, http status code, referrer policy, an extended info map, and
  three task ids with a child count. Everything after the type mask is optional in Chromium's
  reader, so a payload that ends early yields the fields that were present.
* Command 4 is not a pickle. It is the fixed SelectedNavigationInTabPayload2 struct: an int32 tab
  id, an int32 selected navigation index, and an int64 timestamp.

Timestamps are Chromium's base::Time internal value, microseconds since 1601-01-01 UTC. They are
returned as stored; converting them is the caller's job.

A base::Pickle holds a uint32 payload size and then its fields, each advanced to a four byte
boundary; a string is an int32 length then that many bytes, and a string16 is an int32 length in
UTF-16 code units then twice that many bytes.
"""
import struct

MAGIC = b'SNSS'
SUPPORTED_VERSIONS = (1, 3)

COMMAND_UPDATE_TAB_NAVIGATION = 1
COMMAND_SELECTED_NAVIGATION_IN_TAB = 4


class SNSSError(Exception):
    """Raised for a file that is not a readable SNSS session file."""


class _Pickle:
    """Reads a base::Pickle laid out as Chromium writes it."""

    def __init__(self, buffer):
        if len(buffer) < 4:
            raise SNSSError('pickle shorter than its header')
        self._buffer = buffer
        self._size = struct.unpack_from('<I', buffer, 0)[0]
        self._offset = 4
        self._end = 4 + self._size
        if self._end > len(buffer):
            raise SNSSError('pickle records more payload than the command carries')

    def _advance(self, count):
        self._offset += (count + 3) & ~3

    def _need(self, count):
        if self._offset + count > self._end:
            raise SNSSError('pickle field runs past the end of the payload')

    def read_int(self):
        self._need(4)
        value = struct.unpack_from('<i', self._buffer, self._offset)[0]
        self._advance(4)
        return value

    def read_int64(self):
        self._need(8)
        value = struct.unpack_from('<q', self._buffer, self._offset)[0]
        self._advance(8)
        return value

    def read_string(self):
        length = self.read_int()
        if length < 0:
            raise SNSSError('negative string length')
        self._need(length)
        value = self._buffer[self._offset:self._offset + length].decode('utf-8', 'replace')
        self._advance(length)
        return value

    def read_string16(self):
        length = self.read_int()
        if length < 0:
            raise SNSSError('negative string16 length')
        self._need(2 * length)
        value = self._buffer[self._offset:self._offset + 2 * length].decode('utf-16-le', 'replace')
        self._advance(2 * length)
        return value

    @property
    def remaining(self):
        """Payload bytes not yet read. Zero after a complete decode."""
        return self._end - self._offset


def read_commands(path):
    """Yield (command id, payload) for every command in the file, in file order."""
    with open(path, 'rb') as handle:
        data = handle.read()
    if len(data) < 8 or data[:4] != MAGIC:
        raise SNSSError('file does not start with the SNSS magic')
    version = struct.unpack_from('<i', data, 4)[0]
    if version not in SUPPORTED_VERSIONS:
        raise SNSSError(f'unsupported SNSS version {version}')
    offset = 8
    while offset + 2 <= len(data):
        size = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        if size == 0 or offset + size > len(data):
            return
        yield data[offset], data[offset + 1:offset + size]
        offset += size


def decode_navigation_entry(payload):
    """One command 1 payload as a dict. `unread` is 0 when the pickle was consumed exactly."""
    pickle = _Pickle(payload)
    entry = {
        'tab_id': pickle.read_int(),
        'index': pickle.read_int(),
        'url': pickle.read_string(),
        'title': pickle.read_string16(),
        'page_state_length': 0,
        'transition_type': None,
        'has_post_data': None,
        'referrer_url': '',
        'original_request_url': '',
        'is_overriding_user_agent': None,
        'timestamp': None,
        'http_status_code': None,
        'referrer_policy': None,
        'extended_info': {},
        'unread': None,
    }
    entry['page_state_length'] = len(pickle.read_string())
    entry['transition_type'] = pickle.read_int()
    try:
        type_mask = pickle.read_int()
        entry['has_post_data'] = bool(type_mask & 1)
        entry['referrer_url'] = pickle.read_string()
        pickle.read_int()                       # obsolete referrer policy, written for compatibility
        entry['original_request_url'] = pickle.read_string()
        entry['is_overriding_user_agent'] = bool(pickle.read_int())
        entry['timestamp'] = pickle.read_int64()
        pickle.read_string16()                  # placeholder where search terms used to be
        entry['http_status_code'] = pickle.read_int()
        entry['referrer_policy'] = pickle.read_int()
        count = pickle.read_int()
        for _ in range(count):
            key = pickle.read_string()
            entry['extended_info'][key] = pickle.read_string()
        pickle.read_int64()                     # task id
        pickle.read_int64()                     # parent task id
        pickle.read_int64()                     # root task id
        pickle.read_int()                       # child task id count
    except (SNSSError, struct.error):
        # Chromium treats every field after the type mask as optional and stops rather than
        # failing, so a short payload keeps whatever was read.
        pass
    entry['unread'] = pickle.remaining
    return entry


def decode_selected_navigation(payload):
    """One command 4 payload: the tab, its selected navigation index, and the stored timestamp."""
    if len(payload) < 16:
        raise SNSSError('selected navigation payload shorter than its struct')
    tab_id, index, timestamp = struct.unpack_from('<iiq', payload, 0)
    return {'tab_id': tab_id, 'index': index, 'timestamp': timestamp}


def read_navigation_entries(path):
    """Every decodable command 1 entry in the file."""
    entries = []
    for command_id, payload in read_commands(path):
        if command_id != COMMAND_UPDATE_TAB_NAVIGATION:
            continue
        try:
            entries.append(decode_navigation_entry(payload))
        except (SNSSError, struct.error, UnicodeDecodeError):
            continue
    return entries


def read_selected_navigations(path):
    """Every decodable command 4 record in the file."""
    records = []
    for command_id, payload in read_commands(path):
        if command_id != COMMAND_SELECTED_NAVIGATION_IN_TAB:
            continue
        try:
            records.append(decode_selected_navigation(payload))
        except (SNSSError, struct.error):
            continue
    return records
