"""Apple Messages attachment previews stored as ATX textures with a .ktx extension."""

import os
from pathlib import Path

from leapp_functions.parsers.apple_atx import decode_atx_file
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    logfunc,
)

__artifacts_v2__ = {
    "apple_sms_preview_ktx_atx": {
        "name": "Apple SMS Preview Attachments (ATX in KTX)",
        "description": "Messages attachment preview thumbnails with a .ktx extension cached "
                       "under com.apple.MobileSMS, most of them AAPL ATX texture containers "
                       "rather than Khronos KTX1, decoded to images where supported",
        "author": "@charpy4n6, Claude",
        "creation_date": "2026-09-09",
        "last_update_date": "2026-09-09",
        "requirements": "astc_decomp_faster, liblzfse",
        "category": "SMS & iMessage",
        "notes": "Scans files with a .ktx extension under the Messages app path com.apple.MobileSMS/Previews/Attachments/. Some of these are AAPL ATX texture containers (AAPL magic, then HEAD/astc/LZFS chunks) rather than Khronos KTX1; the shared leapp_functions/parsers/apple_atx parser identifies the container by its magic bytes and decodes ASTC 4x4 payloads with a best-effort tile-order heuristic, the same code the Apple ATX Images artifact uses. That ATX layout was derived from observed files and is not vendor-documented. A file that is KTX1, or not a texture, is still listed with whatever header and payload fields parsed plus a Status note, but no decoded image. Cached preview images from the Messages app's attachment-preview cache. This artifact decodes the images and reports file timestamps and texture metadata only; it does not link a preview to a specific message, contact, direction, or send/receive time.",
        "paths": (
            '*/com.apple.MobileSMS/Previews/Attachments/*.ktx',
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 22 rows",
            "abe_ios16": "iOS 16.5 | 20 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hc_ios18_7": "iOS 18.7.8 | 9 rows",
            "hickman_ios15": "iOS 15.3.1 | 8 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 7 rows",
            "ctf2020_ios12": "iOS 12.4 | 7 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
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


def _file_timestamps(context, file_found):
    file_info = context.get_seeker().file_infos.get(file_found)
    if not file_info:
        return '', ''

    return (
        convert_unix_ts_to_utc(file_info.creation_date),
        convert_unix_ts_to_utc(file_info.modification_date)
    )


@artifact_processor
def apple_sms_preview_ktx_atx(context):
    """ See artifact description """
    data_headers = (
        ('File Created', 'datetime'),
        ('File Modified', 'datetime'),
        ('Image', 'media'),
        'Filename',
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

    for file_found in context.get_files_found():
        file_found = str(file_found)
        source_roots.add(_previews_root(file_found))
        source_path = context.get_relative_path(file_found)
        filename = _path_name(file_found)
        created_at, modified_at = _file_timestamps(context, file_found)
        media_ref = None

        try:
            result = decode_atx_file(file_found)
        except OSError as ex:
            logfunc(f'Failed to read SMS preview ATX/KTX {file_found}: {ex}')
            data_list.append((created_at, modified_at,
                None, filename, '', '', '', '', '', '', '', '', '', '',
                '', f'Failed to read file: {ex}', source_path
            ))
            continue

        header = result.header
        payload = result.payload
        chunks = ', '.join(chunk.tag for chunk in result.chunks)
        warnings = '; '.join(result.warnings)
        status = 'Parsed ATX metadata'

        if result.image:
            png_path = Path(file_found).with_suffix('.png')
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
