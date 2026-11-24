"""Read local Biome stream records and retain each record's evidence location."""
from pathlib import PurePosixPath
import os
import struct

from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ilapfuncs import logfunc, webkit_timestampsconv


def local_records(context, stream):
    suffix = ('Biome', 'streams', 'restricted', stream, 'local')
    for found in dict.fromkeys(map(str, context.get_files_found())):
        source = PurePosixPath(context.get_relative_path(found).replace('\\', '/'))
        if (source.parent.parts[-5:] != suffix or source.name.startswith('.')
                or 'tombstone' in source.name or not os.path.isfile(found)):
            continue
        try:
            for record in read_segb_file(found):
                yield source, record
        except (OSError, ValueError, OverflowError, struct.error) as error:
            logfunc(f'{stream}: could not finish reading {source}: {error}')


def cocoa_date(value, label, filename, offset):
    """Cocoa seconds as UTC, or None when the stored value cannot be a date.

    The conversion error is logged with the record's file and offset, so the caller keeps the record's row
    with an empty date. A sentinel converts to '' exactly as webkit_timestampsconv returns it.
    """
    try:
        return webkit_timestampsconv(value)
    except (ValueError, TypeError) as ex:
        logfunc(f'{label}: date at offset {offset} in {filename} could not be converted '
                f'({type(ex).__name__}: {ex}); left empty')
        return None
