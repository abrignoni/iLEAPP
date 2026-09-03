"""MMKV key-value store reader.

MMKV is Tencent's mmap-backed key-value store, used by a number of Android and
iOS apps in place of SharedPreferences or NSUserDefaults
(github.com/Tencent/MMKV, BSD-3-Clause). Its on-disk layout is small enough to
read directly:

    [0:4]   actual size of the data region, uint32 little-endian
    [4:4+actual_size]
            the data region. It opens with one varint, the total size of the
            items that follow (Tencent's MMKV_IO.cpp reserves a fixed 4-byte
            slot for it on the append path, ItemSizeHolderSize, and writes a
            plain varint on the full-rewrite path in MiniPBCoder.cpp, so on
            disk it is 1 to 4 bytes long). After it, entries laid end to end,
            each one
                varint  key length
                bytes   key, UTF-8
                varint  value container length
                bytes   value container
    the remainder of the file is zero padding out to the mmap page size

The value container is untyped on disk. MMKV records the type in the calling
code, not in the file, so this module returns the raw container and leaves the
reading to the caller. `decode_value` applies the one distinction that can be
made from the bytes alone: a container that is exactly a varint length followed
by that many bytes is how MMKV writes a string, and anything else is read as a
varint scalar, which is how it writes the integer and boolean types.

Two properties matter when reading one of these files as evidence.

**The store is append-only between rewrites.** Setting a key appends a new
entry rather than editing the existing one, so a key that has been changed
appears more than once and the earlier entries are superseded values still
present in the file. `read_entries` returns every entry in file order so those
remain visible; `read_dict` collapses to the last occurrence, which is the value
the app reads.

**A zero-length container marks a removal**, not an empty string. `read_dict`
drops those keys, matching what the app sees. They stay visible in
`read_entries`.

Nothing here decrypts. MMKV supports an AES-encrypted mode; the AES vector for it
is kept in the sibling ``<name>.crc`` meta file at bytes 12 to 28. When that file
is present and the vector is non-zero, `read_entries` raises MMKVError rather than
returning the garbage keys an encrypted region decodes to.
"""

import struct


class MMKVError(Exception):
    """Raised when a file cannot be read as an MMKV store."""


_HEADER_LENGTH = 4
# Ten sevens covers a 64-bit value, which is the widest scalar MMKV writes.
# A varint longer than that means the walk has lost alignment.
_MAX_VARINT_BYTES = 10


def _read_varint(data, offset):
    """Return (value, new_offset) for the varint at offset."""
    result = 0
    shift = 0
    for _ in range(_MAX_VARINT_BYTES):
        if offset >= len(data):
            raise MMKVError('varint runs past end of data')
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7
    raise MMKVError('varint longer than 5 bytes')


def read_entries(path):
    """Return every (key, raw_value_container) entry in file order.

    Every entry is returned, including repeats of the same key. Later entries
    for a key supersede earlier ones; see read_dict for the collapsed view.
    Raises MMKVError for a file that is not a readable MMKV store, including one
    whose .crc meta file records an AES vector (an encrypted store).
    """
    with open(path, 'rb') as handle:
        data = handle.read()
    if len(data) < _HEADER_LENGTH:
        raise MMKVError('file shorter than an MMKV header')
    actual_size = struct.unpack_from('<I', data, 0)[0]
    if actual_size == 0:
        return []
    end = _HEADER_LENGTH + actual_size
    if end > len(data):
        raise MMKVError('recorded data size runs past the end of the file')
    if _aes_vector(path):
        raise MMKVError('store is AES-encrypted (non-zero vector in the .crc meta file)')

    entries = []
    # The data region opens with the items-size varint; the first key follows it.
    _items_size, offset = _read_varint(data, _HEADER_LENGTH)
    while offset < end:
        try:
            key_length, offset = _read_varint(data, offset)
            if key_length == 0 or offset + key_length > end:
                break
            key = data[offset:offset + key_length].decode('utf-8')
            offset += key_length
            value_length, offset = _read_varint(data, offset)
            if offset + value_length > end:
                break
            entries.append((key, data[offset:offset + value_length]))
            offset += value_length
        except (MMKVError, UnicodeDecodeError):
            break
    return entries


def _aes_vector(path):
    """The 16-byte AES vector from the sibling .crc meta file, or b'' when absent or zero.

    MMKVMetaInfo lays out: crc u32, version u32, sequence u32, aesVector[16], ...
    """
    meta = path + '.crc'
    try:
        with open(meta, 'rb') as handle:
            head = handle.read(28)
    except OSError:
        return b''
    vector = head[12:28]
    return vector if len(vector) == 16 and any(vector) else b''


def decode_value(container):
    """Decode a value container to a str or an int.

    A container that is exactly a varint length followed by that many bytes is
    how MMKV writes a string; anything else is read as a varint scalar, which
    covers its integer and boolean types. Returns None for a removal marker,
    and the raw bytes when neither reading applies.
    """
    if not container:
        return None
    try:
        length, offset = _read_varint(container, 0)
    except MMKVError:
        return container
    if offset + length == len(container):
        try:
            return container[offset:offset + length].decode('utf-8')
        except UnicodeDecodeError:
            return container[offset:offset + length]
    try:
        value, offset = _read_varint(container, 0)
    except MMKVError:
        return container
    if offset == len(container):
        return value
    return container


def read_dict(path):
    """Return {key: decoded value} using the last occurrence of each key.

    Removed keys are omitted. Use read_entries when the superseded values
    matter.
    """
    result = {}
    for key, container in read_entries(path):
        value = decode_value(container)
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result
