"""Apple Messages preview cache: ATX and KTX textures, cached PNG and JPEG previews,
and the contact card and location shares recorded beside them."""

import io
import os
import plistlib
import struct
from pathlib import Path

from PIL import Image

from leapp_functions.parsers.apple_atx import decode_atx_file
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    logfunc,
)
from scripts.ktx.ios_ktx2png import KTX_reader

ATX_MAGIC = b'AAPL\r\n\x1a\n'
KTX1_MAGIC = b'\xabKTX 11\xbb\r\n\x1a\n'
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
JPEG_MAGIC = b'\xff\xd8\xff'
LENGTH_PREFIX_BYTES = 8

__artifacts_v2__ = {
    "apple_sms_preview_ktx_atx": {
        "name": "Apple SMS Preview Cache",
        "description": "Preview images Messages cached under com.apple.MobileSMS, covering the "
                       "attachment, sticker, location and search preview folders, plus the name "
                       "recorded when a contact card or location was shared",
        "author": "@charpy4n6, Claude",
        "creation_date": "2026-09-09",
        "last_update_date": "2026-09-10",
        "requirements": "astc_decomp_faster, liblzfse",
        "category": "SMS & iMessage",
        "notes": "Reads the .ktx, .jpeg and .png files Messages caches under "
                 "com.apple.MobileSMS/Previews/. The Preview Type column is the folder each "
                 "file sits in (Attachments, StickerCache, Location or Search), which is "
                 "recorded by the app rather than inferred. The Container column is decided by "
                 "the file's magic bytes, not its extension, because the extension and the "
                 "container disagree on some files: files named .ktx in this cache were AAPL "
                 "ATX containers, Khronos KTX1, or KTX1 behind an eight byte little endian "
                 "length, and files named .jpeg were sometimes ATX rather than JPEG. ATX is "
                 "decoded by the shared leapp_functions/parsers/apple_atx parser and its "
                 "best-effort ASTC 4x4 tile-order heuristic, the same code the Apple ATX Images "
                 "artifact uses; that ATX layout was derived from observed files and is not "
                 "vendor-documented. KTX1 is decoded by scripts/ktx/ios_ktx2png, the same reader "
                 "the App Snapshots artifact uses. PNG and JPEG files are reported as stored "
                 "without conversion. A file whose container is not recognised, or that a "
                 "decoder rejects, is still listed with whatever fields parsed plus a Status "
                 "note, but no image. Messages also writes a plist beside a preview when a "
                 "contact card or a location is shared, and the Shared Name column carries the "
                 "title the app composed for it, copied onto the other files in the same "
                 "folder. That names what was shared, not who sent it. A location share is "
                 "titled Current Location on every tested image, so it establishes that a "
                 "location was shared and not where. Plists in this cache that carry no "
                 "contact fields, which on the tested images were Live Photo complement "
                 "metadata and an asset flag, record no share and are not reported. "
                 "Beyond that name this artifact reports file timestamps, container and "
                 "texture metadata only; it does not link a preview to a specific message, "
                 "direction, or send or receive time. The cache also holds copies of some "
                 "attachments; the Messages artifact reports those from Library/SMS/Attachments "
                 "with their message context.",
        "paths": (
            '*/com.apple.MobileSMS/Previews/*.ktx',
            '*/com.apple.MobileSMS/Previews/*.jpeg',
            '*/com.apple.MobileSMS/Previews/*.png',
            '*/com.apple.MobileSMS/Previews/*.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 29 rows",
            "otto_ios17": "iOS 17.5.1 | 29 rows",
            "iphone11_ios17": "iOS 17.3 | 26 rows",
            "dexter_ios18": "iOS 18.3.2 | 18 rows",
            "hickman_ios15": "iOS 15.3.1 | 17 rows",
            "felix23_ios16": "iOS 16.5 | 14 rows",
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 7 rows",
            "ctf2020_ios12": "iOS 12.4 | 7 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios26": "iOS 26.5.2 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows"
        }
    }
}


def _path_name(path):
    return str(path).replace('\\', '/').rstrip('/').split('/')[-1]


def _previews_root(path):
    """Return the path truncated at Previews/<subdir>, so the artifact cites the
    cache directories rather than one per-attachment UUID folder."""
    normalized = str(path).replace('\\', '/')
    marker = '/Previews/'
    index = normalized.find(marker)
    if index == -1:
        return os.path.dirname(str(path))

    subdir = normalized[index + len(marker):].split('/')[0]
    return normalized[:index + len(marker)] + subdir


def _preview_type(path):
    """The Previews subfolder the file sits in, as the app recorded it."""
    normalized = str(path).replace('\\', '/')
    marker = '/Previews/'
    index = normalized.find(marker)
    if index == -1:
        return ''

    parts = normalized[index + len(marker):].split('/')
    return parts[0] if len(parts) > 1 else ''


def _file_timestamps(context, file_found):
    file_info = context.get_seeker().file_infos.get(file_found)
    if not file_info:
        return '', ''

    return (
        convert_unix_ts_to_utc(file_info.creation_date),
        convert_unix_ts_to_utc(file_info.modification_date)
    )


def _sniff_container(head):
    """Identify the container from its magic bytes rather than its extension."""
    if head.startswith(ATX_MAGIC):
        return 'ATX'
    if head.startswith(KTX1_MAGIC):
        return 'KTX1'
    if head[LENGTH_PREFIX_BYTES:LENGTH_PREFIX_BYTES + len(KTX1_MAGIC)] == KTX1_MAGIC:
        return 'KTX1 (length prefixed)'
    if head.startswith(PNG_MAGIC):
        return 'PNG'
    if head.startswith(JPEG_MAGIC):
        return 'JPEG'
    return 'Unrecognised'


def _ktx_blob(file_found, container):
    """Return just the KTX bytes. The length prefixed variant carries the KTX length
    in the first eight bytes and unrelated trailing data after it, and the reader
    would otherwise read that whole tail as texture payload."""
    with open(file_found, 'rb') as texture_file:
        raw = texture_file.read()

    if container != 'KTX1 (length prefixed)':
        return raw

    declared = struct.unpack_from('<Q', raw, 0)[0]
    end = LENGTH_PREFIX_BYTES + declared
    if declared <= 0 or end > len(raw):
        return raw[LENGTH_PREFIX_BYTES:]
    return raw[LENGTH_PREFIX_BYTES:end]


def _decode_ktx(file_found, container):
    """Decode a Khronos KTX1 texture. Returns (image, width, height, mipmaps, note)."""
    reader = KTX_reader()
    handle = io.BytesIO(_ktx_blob(file_found, container))
    if not reader.validate_header(handle):
        return None, '', '', '', reader.error_message or 'KTX header not valid'

    data = reader.get_uncompressed_texture_data(handle)
    image = Image.frombytes('RGBA', (reader.pixelWidth, reader.pixelHeight),
                            data, 'astc', (4, 4, False))
    return image, reader.pixelWidth, reader.pixelHeight, reader.numberOfMipmapLevels, ''


def _shared_name(file_found):
    """The display title Messages composed for a shared contact card or location.
    Returns '' for the plists in this cache that carry no contact fields."""
    try:
        with open(file_found, 'rb') as plist_file:
            parsed = plistlib.load(plist_file)
    except (OSError, ValueError, plistlib.InvalidFileException) as ex:
        logfunc(f'Failed to read SMS preview plist {file_found}: {ex}')
        return ''

    if not isinstance(parsed, dict):
        return ''
    return str(parsed.get('contactFormatterTitle') or '')


def _native_dimensions(file_found):
    try:
        with Image.open(file_found) as image:
            return image.width, image.height
    except (OSError, ValueError):
        return '', ''


@artifact_processor
def apple_sms_preview_ktx_atx(context):
    """ See artifact description """
    data_headers = (
        ('File Created', 'datetime'),
        ('File Modified', 'datetime'),
        ('Image', 'media'),
        'Filename',
        'Preview Type',
        'Container',
        'Shared Name',
        'Width',
        'Height',
        'Depth',
        'Array Layers',
        'Mipmaps',
        'Pixel Format',
        'Texture UUID',
        'Payload',
        'Payload Bytes',
        'Declared Payload Bytes',
        'Chunks',
        'Status',
        'Source Path',
    )
    data_list = []
    source_roots = set()
    blank = ('',) * 11

    files_found = [str(found) for found in context.get_files_found()
                   if not os.path.isdir(str(found))]

    # A share plist names the contact or location for everything in its own folder,
    # so read those first and let the preview beside them carry the name too.
    shared_names = {}
    for file_found in files_found:
        if file_found.lower().endswith('.plist'):
            name = _shared_name(file_found)
            if name:
                shared_names[os.path.dirname(file_found)] = name

    for file_found in files_found:
        source_roots.add(_previews_root(file_found))
        source_path = context.get_relative_path(file_found)
        filename = _path_name(file_found)
        preview_type = _preview_type(file_found)
        shared = shared_names.get(os.path.dirname(file_found), '')
        created_at, modified_at = _file_timestamps(context, file_found)

        if file_found.lower().endswith('.plist'):
            if not shared:
                # The rest are Live Photo complement metadata and a single asset
                # flag; they record no share, so there is nothing to report.
                continue
            data_list.append((created_at, modified_at, None, filename, preview_type,
                              'plist', shared, *blank,
                              'Contact card or location share', source_path))
            continue

        try:
            with open(file_found, 'rb') as probe:
                head = probe.read(32)
        except OSError as ex:
            logfunc(f'Failed to read SMS preview {file_found}: {ex}')
            data_list.append((created_at, modified_at, None, filename, preview_type,
                              '', shared, *blank, f'Failed to read file: {ex}', source_path))
            continue

        container = _sniff_container(head)

        if container in ('PNG', 'JPEG'):
            width, height = _native_dimensions(file_found)
            media_ref = check_in_media(file_found, filename,
                                       force_type=f'image/{container.lower()}',
                                       force_extension=container.lower())
            data_list.append((created_at, modified_at, media_ref, filename, preview_type,
                              container, shared, width, height, '', '', '', '', '', '', '',
                              '', '', 'Cached image reported as stored', source_path))
            continue

        if container.startswith('KTX1'):
            media_ref = None
            width = height = mipmaps = pixel_format = ''
            try:
                image, width, height, mipmaps, note = _decode_ktx(file_found, container)
                if image:
                    # scripts/ktx/ios_ktx2png only returns data for glInternalFormat 0x93B0,
                    # GL_COMPRESSED_RGBA_ASTC_4x4_KHR, and raises for anything else
                    pixel_format = 'ASTC 4x4'
                    png_path = Path(file_found).with_name(f'{Path(file_found).stem}-decoded.png')
                    image.save(png_path, 'PNG')
                    media_ref = check_in_media(file_found, filename, png_path,
                                               force_type='image/png', force_extension='png')
                    status = 'Decoded KTX to PNG'
                else:
                    status = f'Parsed KTX header: {note}' if note else 'KTX not decoded'
            except (OSError, ValueError, struct.error) as ex:
                logfunc(f'Failed to decode SMS preview KTX {file_found}: {ex}')
                status = f'KTX decode failed: {ex}'
            data_list.append((created_at, modified_at, media_ref, filename, preview_type,
                              container, shared, width, height, '', '', mipmaps, pixel_format,
                              '', '', '', '', '', status, source_path))
            continue

        media_ref = None
        try:
            result = decode_atx_file(file_found)
        except OSError as ex:
            logfunc(f'Failed to read SMS preview ATX {file_found}: {ex}')
            data_list.append((created_at, modified_at, None, filename, preview_type,
                              container, shared, *blank, f'Failed to read file: {ex}',
                              source_path))
            continue

        header = result.header
        payload = result.payload
        chunks = ', '.join(chunk.tag for chunk in result.chunks)
        warnings = '; '.join(result.warnings)
        status = 'Parsed ATX metadata'

        if result.image:
            png_path = Path(file_found).with_name(f'{Path(file_found).stem}-decoded.png')
            try:
                result.image.to_pil().save(png_path, 'PNG')
                media_ref = check_in_media(file_found, filename, png_path,
                                           force_type='image/png', force_extension='png')
                status = 'Decoded ATX to PNG'
            except (OSError, ValueError) as ex:
                logfunc(f'Failed to save decoded SMS preview ATX image {file_found}: {ex}')
                status = 'Parsed ATX metadata, but PNG save failed'
                warnings = f'{warnings}; {ex}' if warnings else str(ex)
        elif warnings:
            status = 'Parsed ATX metadata with warnings'

        data_list.append((
            created_at,
            modified_at,
            media_ref,
            filename,
            preview_type,
            container,
            shared,
            header.width if header else '',
            header.height if header else '',
            header.depth if header else '',
            header.array_layers if header else '',
            header.mipmap_count if header else '',
            header.pixel_format if header else '',
            header.texture_uuid if header else '',
            payload.kind if payload else '',
            len(payload.data) if payload else '',
            payload.declared_size if payload else '',
            chunks,
            f'{status}: {warnings}' if warnings else status,
            source_path,
        ))

    return data_headers, data_list, '\n'.join(sorted(source_roots))
