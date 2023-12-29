import datetime
import struct
import typing
import dataclasses
import pathlib
import os

"""
Copyright 2023, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.2"
__description__ = "A python module to read SEGB v1 files found on iOS, macOS etc."
__contact__ = "Alex Caithness"

MAGIC = b"SEGB"
HEADER_LENGTH = 56
RECORD_HEADER_LENGTH = 32
ALIGNMENT_BYTES_LENGTH = 8
COCOA_EPOCH = datetime.datetime(2001, 1, 1, 0, 0, 0)


@dataclasses.dataclass(frozen=True)
class Segb1Entry:
    timestamp1: datetime.datetime
    timestamp2: datetime.datetime
    data_start_offset: int
    data: bytes


def decode_cocoa_time(seconds) -> datetime.datetime:
    """
    Decodes a Cocoa/Mac Absolute timestamp

    :param seconds: the timestamp value in seconds
    :return: the decoded timestamp as a datetime.datetime
    """
    return COCOA_EPOCH + datetime.timedelta(seconds=seconds)


def bytes_to_hexview(b: bytes, width=16, show_offset=True, show_ascii=True,
                     line_sep="\n", start_offset=0, max_bytes=-1) -> str:
    """
    Generates a hexview style string for the bytes object b

    :param b: The data (as a bytes object) to be presented as a hexview
    :param width: the width of each line of the hexview in bytes (16 by default)
    :param show_offset: whether to show the offset on the left of the hexview (True by default)
    :param show_ascii: whether to show the ASCII representation of the data on the right of the hexview (True by
    default)
    :param line_sep: string to separate each line of the hexview ('\n' by default)
    :param start_offset: offset to start reading the data from (0 by default)
    :param max_bytes: the maximum number of bytes to render as a hexview or -1 for all of the data (-1 by default)
    :return: a hexview style string for the bytes object b
    """
    line_fmt = ""
    if show_offset:
        line_fmt += "{offset:08x}: "
    line_fmt += "{hex}"
    if show_ascii:
        line_fmt += " {ascii}"

    b = b[start_offset:]
    if max_bytes > -1:
        b = b[:max_bytes]

    offset = 0
    lines = []
    while offset < len(b):
        chunk = b[offset:offset + width]
        ascii = "".join(chr(x) if x >= 0x20 and x < 0x7f else "." for x in chunk)
        hex = " ".join(format(x, "02x") for x in chunk).ljust(width * 3)
        line = line_fmt.format(offset=offset, hex=hex, ascii=ascii)
        lines.append(line)
        offset += width

    return line_sep.join(lines)


def stream_matches_segbv1_signature(stream: typing.BinaryIO) -> bool:
    """
    Returns True if the stream contains data matching the SEGB v1 file signature. Resets the stream to the same position
    before returning.

    :param stream: The stream potentially containing SEGB v1 data
    :return: True if the stream contains data matching the SEGB v1 file signature.
    """
    reset_offset = stream.tell()
    file_header = stream.read(HEADER_LENGTH)
    stream.seek(reset_offset, os.SEEK_SET)

    if len(file_header) != HEADER_LENGTH or file_header[-4:] != MAGIC:
        return False

    # TODO: consider whether we should check the end of data offset is less than the stream's size?
    return True


def file_matches_segbv1_signature(path: pathlib.Path | os.PathLike | str) -> bool:
    """
    Returns True if the file at the given path contains data matching the SEGB v1 file signature. Resets the stream to
    the same position before returning.

    :param path: The path of the file potentially containing SEGB v1 data
    :return: True if the stream contains data matching the SEGB v1 file signature.
    """
    path = pathlib.Path(path)
    with path.open("rb") as f:
        return stream_matches_segbv1_signature(f)


def read_segb1_stream(stream: typing.BinaryIO) -> typing.Iterable[Segb1Entry]:
    """
    Reads SEGB v1 data from a stream and yields an iterable of Segb1Entry objects
    :param stream: a binary stream containing the SEGB data. The data is assumed to begin at the start of the stream
    :return: an iterable of Segb1Entry objects
    """
    file_header = stream.read(HEADER_LENGTH)
    if len(file_header) != HEADER_LENGTH or file_header[-4:] != MAGIC:
        raise ValueError(f"Unexpected file magic. Expected: {MAGIC.hex()}; got: {file_header[-4:].hex()}")

    end_of_data_offset, = struct.unpack("<I", file_header[0:4])

    while stream.tell() < end_of_data_offset:
        record_header_raw = stream.read(RECORD_HEADER_LENGTH)
        record_length, timestamp1_raw, timestamp2_raw = struct.unpack("<i4xdd", record_header_raw[:24])
        timestamp1 = decode_cocoa_time(timestamp1_raw)
        timestamp2 = decode_cocoa_time(timestamp2_raw)

        record_offset = stream.tell()

        data = stream.read(record_length)
        yield Segb1Entry(timestamp1, timestamp2, record_offset, data)

        # align to 8 bytes
        if (remainder := stream.tell() % ALIGNMENT_BYTES_LENGTH) != 0:
            stream.seek(ALIGNMENT_BYTES_LENGTH - remainder, os.SEEK_CUR)


def read_segb1_file(path: pathlib.Path | os.PathLike | str) -> typing.Iterable[Segb1Entry]:
    """
    Reads SEGB v1 data from a file and yields an iterable of Segb1Entry objects
    :param path: the path of the file to be opened
    :return: an iterable of Segb1Entry objects
    """
    path = pathlib.Path(path)
    with path.open("rb") as f:
        yield from read_segb1_stream(f)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print(f"USAGE: {pathlib.Path(sys.argv[0]).name} <SEG2 file>")
        print()
        exit(1)

    for record in read_segb1_file(sys.argv[1]):
        print("=" * 72)
        print(f"Offset: {record.data_start_offset}")
        print(f"Timestamp1: {record.timestamp1}")
        print(f"Timestamp2: {record.timestamp2}")
        print()
        print(bytes_to_hexview(record.data))
        print()
    print("End of records")
    print()
