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
        "notes": "iOS caches preview thumbnails for Messages attachments under "
                 "com.apple.MobileSMS/Previews/Attachments. Some of these files use a .ktx "
                 "extension but the container is Apple's ATX format (AAPL magic followed by "
                 "HEAD/astc/LZFS chunks), not Khronos KTX1. The ATX layout was derived from "
                 "observed files and is not vendor-documented. Decoding reuses the shared "
                 "leapp_functions/parsers/apple_atx parser and its best-effort ASTC 4x4 "
                 "tile-order heuristic, the same as the Apple ATX Images artifact. A file "
                 "that is genuinely KTX1, or not a texture at all, is still listed with "
                 "whatever metadata parsed plus a Status note, but no image. The presence of "
                 "a preview here indicates an attachment was received or sent in Messages and "
                 "rendered on the device; it does not prove the original attachment is still "
                 "present. Tile-order heuristic caveat: if an image looks scrambled, capture "
                 "the source file for the parser maintainers. Run against the HC iPhone XS "
                 "(iOS 18.7.8) extraction; per-corpus row counts have not been recorded in "
                 "sample_data yet.",
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
