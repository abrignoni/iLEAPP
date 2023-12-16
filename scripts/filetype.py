"""
This is a Python port from filetype Go package.
Small and dependency free Python package to infer file type and MIME type checking the magic numbers signature of a file or buffer.
Version: 1.2.0
Copyright (c) 2016 Tomás Aparicio

-----
The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

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

# -*- coding: utf-8 -*-
import pathlib

from scripts.filetypes import ARCHIVE as archive_matchers
from scripts.filetypes import AUDIO as audio_matchers
from scripts.filetypes import APPLICATION as application_matchers
from scripts.filetypes import DOCUMENT as document_matchers
from scripts.filetypes import FONT as font_matchers
from scripts.filetypes import IMAGE as image_matchers
from scripts.filetypes import VIDEO as video_matchers
from scripts.filetypes import TYPES, Type


# utils.py

_NUM_SIGNATURE_BYTES = 8192


def get_signature_bytes(path):
    """
    Reads file from disk and returns the first 8192 bytes
    of data representing the magic number header signature.

    Args:
        path: path string to file.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    with open(path, 'rb') as fp:
        return bytearray(fp.read(_NUM_SIGNATURE_BYTES))


def signature(array):
    """
    Returns the first 8192 bytes of the given bytearray
    as part of the file header signature.

    Args:
        array: bytearray to extract the header signature.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    length = len(array)
    index = _NUM_SIGNATURE_BYTES if length > _NUM_SIGNATURE_BYTES else length

    return array[:index]


def get_bytes(obj):
    """
    Infers the input type and reads the first 8192 bytes,
    returning a sliced bytearray.

    Args:
        obj: path to readable, file-like object(with read() method), bytes,
        bytearray or memoryview

    Returns:
        First 8192 bytes of the file content as bytearray type.

    Raises:
        TypeError: if obj is not a supported type.
    """
    if isinstance(obj, bytearray):
        return signature(obj)

    if isinstance(obj, str):
        return get_signature_bytes(obj)

    if isinstance(obj, bytes):
        return signature(obj)

    if isinstance(obj, memoryview):
        return bytearray(signature(obj).tolist())

    if isinstance(obj, pathlib.PurePath):
        return get_signature_bytes(obj)

    if hasattr(obj, 'read'):
        if hasattr(obj, 'tell') and hasattr(obj, 'seek'):
            start_pos = obj.tell()
            obj.seek(0)
            magic_bytes = obj.read(_NUM_SIGNATURE_BYTES)
            obj.seek(start_pos)
            return get_bytes(magic_bytes)
        return get_bytes(obj.read(_NUM_SIGNATURE_BYTES))

    raise TypeError('Unsupported type as file input: %s' % type(obj))


# match.py

def match(obj, matchers=TYPES):
    """
    Matches the given input against the available
    file type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if type matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    buf = get_bytes(obj)

    for matcher in matchers:
        if matcher.match(buf):
            return matcher

    return None


def image_match(obj):
    """
    Matches the given input against the available
    image type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, image_matchers)


def font_match(obj):
    """
    Matches the given input against the available
    font type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, font_matchers)


def video_match(obj):
    """
    Matches the given input against the available
    video type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, video_matchers)


def audio_match(obj):
    """
    Matches the given input against the available
    autio type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, audio_matchers)


def archive_match(obj):
    """
    Matches the given input against the available
    archive type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, archive_matchers)


def application_match(obj):
    """
    Matches the given input against the available
    application type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, application_matchers)


def document_match(obj):
    """
    Matches the given input against the available
    document type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, document_matchers)


# Expose supported matchers types
types = TYPES


def guess(obj):
    """
    Infers the type of the given input.

    Function is overloaded to accept multiple types in input
    and perform the needed type inference based on it.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched type instance. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj) if obj else None


def guess_mime(obj):
    """
    Infers the file type of the given input
    and returns its MIME type.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched MIME type as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.mime if kind else kind


def guess_extension(obj):
    """
    Infers the file type of the given input
    and returns its RFC file extension.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched file extension as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.extension if kind else kind


def get_type(mime=None, ext=None):
    """
    Returns the file type instance searching by
    MIME type or file extension.

    Args:
        ext: file extension string. E.g: jpg, png, mp4, mp3
        mime: MIME string. E.g: image/jpeg, video/mpeg

    Returns:
        The matched file type instance. Otherwise None.
    """
    for kind in types:
        if kind.extension == ext or kind.mime == mime:
            return kind
    return None

