"""Apple ATX image textures."""

from pathlib import Path

from leapp_functions.parsers.apple_atx import decode_atx_file
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    logfunc,
)

__artifacts_v2__ = {
    "apple_atx_images": {
        "name": "Apple ATX Images",
        "description": "Apple ATX texture archives decoded to images when possible",
        "author": "@JamesHabben",
        "creation_date": "2026-06-25",
        "last_update_date": "2026-06-25",
        "requirements": "astc_decomp_faster, liblzfse",
        "category": "Images",
        "notes": "ATX files are AAPL texture containers wrapping ASTC image data. These files "
                 "can appear in wallpapers, PosterBoard snapshots, avatars, and other Apple "
                 "UI image caches.",
        "paths": (
            '**/*.atx',
        ),
        "output_types": "standard",
        "artifact_icon": "image"
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
def apple_atx_images(context):
    """ See artifact description """
    data_headers = (
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
        ('File Created', 'datetime'),
        ('File Modified', 'datetime'),
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
            logfunc(f'Failed to read ATX image {file_found}: {ex}')
            data_list.append((
                None, filename, '', '', '', '', '', '', '', '', '', '',
                '', f'Failed to read ATX file: {ex}', created_at, modified_at, source_path
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
                logfunc(f'Failed to save decoded ATX image {file_found}: {ex}')
                status = 'Parsed ATX metadata, but PNG save failed'
                warnings = f'{warnings}; {ex}' if warnings else str(ex)
        elif warnings:
            status = 'Parsed ATX metadata with warnings'

        data_list.append((
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
            created_at,
            modified_at,
            source_path,
        ))

    return data_headers, data_list, 'See Source Path column'
