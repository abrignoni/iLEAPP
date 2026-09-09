"""Apple Messages attachment previews stored as ATX textures with a .ktx extension."""

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
        "description": "Messages attachment preview thumbnails cached under com.apple.MobileSMS "
                       "that carry a .ktx extension but are AAPL ATX texture containers, "
                       "decoded to images when possible",
        "author": "@charpy4n6, Claude",
        "creation_date": "2026-09-09",
        "last_update_date": "2026-09-09",
        "requirements": "astc_decomp_faster, liblzfse",
        "category": "SMS & iMessage",
        "notes": "Scans files with a .ktx extension under the Messages app path com.apple.MobileSMS/Previews/Attachments/. Some of these are AAPL ATX texture containers (AAPL magic, then HEAD/astc/LZFS chunks) rather than Khronos KTX1; the shared leapp_functions/parsers/apple_atx parser identifies the container by its magic bytes and decodes ASTC 4x4 payloads with a best-effort tile-order heuristic, the same code the Apple ATX Images artifact uses. That ATX layout was derived from observed files and is not vendor-documented. A file that is KTX1, or not a texture, is still listed with whatever header and payload fields parsed plus a Status note, but no decoded image.  Cached preview images from the Messages app's attachment-preview cache. This artifact decodes the images and reports file timestamps and texture metadata only; it does not link a preview to a specific message, contact, direction, or send/receive time.",
        "paths": (
            '*/com.apple.MobileSMS/Previews/Attachments/*.ktx',
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | iPhone XS | tested by @charpy4n6; row count not recorded"
        }
    }
}


def _path_name(path):
    return str(path).replace('\\', '/').rstrip('/').split('/')[-1]


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

    for file_found in context.get_files_found():
        file_found = str(file_found)
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

    return data_headers, data_list, 'See Source Path column'
