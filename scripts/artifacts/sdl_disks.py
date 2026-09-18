__artifacts_v2__ = {
    "sdl_disks": {
        "name": "Sysdiagnose - Disks",
        "description": "Filesystem lines from the disks.txt in a sysdiagnose, as stored",
        "author": "@Hexordia",
        "creation_date": "2024-01-30",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "The file is a table headed Filesystem, Size, Used, Avail, Capacity, iused, ifree, "
            "%iused and Mounted on; each line that splits into exactly nine whitespace-separated "
            "fields is a row, values as stored, so a mount point containing a space would be "
            "skipped (none on test data). The seven test sysdiagnoses (iOS 13.3.1 to 26) held 6 to "
            "12 rows each, and the unpacked IN_PROGRESS sysdiagnose folder in the iOS 16.1.1 test "
            "image 11."
        ),
        "paths": (
            '*/disks.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "server",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 10 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 9 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 12 rows",
            "felix23_ios16": "iOS 16.5 | 20 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 10 rows",
            "magnet_ios16": "iOS 16.1.1 | 11 rows",
        }
    }
}

import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error)


def _is_pax_header(path):
    """True for an entry some extractors write for a tar's pax header, not for a file."""
    return any(part.startswith('PaxHeader') for part in path.replace(' >> ', '/').split('/'))


@artifact_processor
def sdl_disks(context):
    data_list = []
    sources = []
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'disks.txt', text_mode=False):
        rel = context.get_relative_path(source_path)
        if _is_pax_header(rel):
            continue
        try:
            lines = file_obj.read().decode('utf-8', errors='replace').splitlines()
        except _READ_ERRORS as ex:
            logfunc(f'Failed to read {rel}: {ex}')
            continue
        sources.append(source_path)
        for line in lines:
            fields = line.split()
            # A table headed 'Filesystem Size Used Avail Capacity iused ifree %iused
            # Mounted on'; every data line on test data split into these nine fields.
            if len(fields) != 9 or fields[0] == 'Filesystem':
                continue
            data_list.append(tuple(fields) + (rel,))
    # 'iused' and '%iused' would sanitize to the same LAVA column name, so the inode
    # columns are spelled out.
    data_headers = ('Filesystem', 'Size', 'Used', 'Available', 'Capacity', 'Inodes Used',
                    'Inodes Free', 'Percent Inodes Used', 'Mounted On', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
