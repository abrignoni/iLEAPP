import datetime
import struct
import typing
import dataclasses
import pathlib
import os
import zlib
from .ccl_segb_common import bytes_to_hexview, decode_cocoa_time, EntryState

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

__version__ = "0.3"
__description__ = "A python module to read SEGB v1 files found on iOS, macOS etc."
__contact__ = "Alex Caithness"

MAGIC = b"SEGB"
HEADER_LENGTH = 56
RECORD_HEADER_LENGTH = 32
ALIGNMENT_BYTES_LENGTH = 8


@dataclasses.dataclass(frozen=True)
class Segb1Entry:
    timestamp1: datetime.datetime
    timestamp2: datetime.datetime
    data_start_offset: int
    metadata_crc: int
    actual_crc: int
    data: bytes
    state: EntryState
    _unknown_value: int = dataclasses.field(kw_only=True, compare=False)

    @property
    def crc_passed(self):
        return self.metadata_crc == self.actual_crc


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
        record_length, entry_state_raw, timestamp1_raw, timestamp2_raw, crc32_stored, unknown_raw = struct.unpack(
            "<iiddIi", record_header_raw[:32])
        timestamp1 = decode_cocoa_time(timestamp1_raw)
        timestamp2 = decode_cocoa_time(timestamp2_raw)

        record_offset = stream.tell()

        data = stream.read(record_length)
        calculated_crc32 = zlib.crc32(data)
        yield Segb1Entry(timestamp1, timestamp2, record_offset, crc32_stored, calculated_crc32, data,
                                 EntryState(entry_state_raw), _unknown_value=unknown_raw)


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


def run_command(file_path: pathlib.Path | os.PathLike | str):
    for record in read_segb1_file(file_path):
        print("=" * 72)
        print(f"Offset: {record.data_start_offset}")
        print(f"Timestamp1: {record.timestamp1}")
        print(f"Timestamp2: {record.timestamp2}")
        if record.state == 1:
            print(f"CRC Passed: {'True' if record.crc_passed else 'False'}")
        print()
        print(bytes_to_hexview(record.data))
        print()
    print("End of records")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print(f"USAGE: {pathlib.Path(sys.argv[0]).name} <SEGB1 file>")
        print()
        exit(1)

    run_command(sys.argv[1])
    print()
