__artifacts_v2__ = {
    "realmUndecodedStores": {
        "name": "Realm - Undecoded Stores",
        "description": "Realm databases that hold content but from which the bundled parser "
                       "decoded no classes, so the store is present in the extraction and has "
                       "not been read.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Realm",
        "notes": "This artifact reports nothing about the contents of any database. It exists so "
                 "that a store the bundled parser cannot read is visible as unread rather than "
                 "indistinguishable from an empty one. The parser's row decoders need the Cluster "
                 "table layout that Realm introduced in file format 10. On the tested extractions "
                 "every store it returned classes for reported file format 24, and every file it "
                 "returned no tables for reported file format 9, which predates that layout; the "
                 "parser reads the class names of a format 9 store but returns no tables for it "
                 "rather than raising, so an unsupported format and an empty store look the same "
                 "in this output. Reported upstream as kalink0/crush-forensics issue 55, where "
                 "the class name reading was fixed and row support remains open. A row is emitted "
                 "only when the file holds more than 1024 non-zero bytes, which excludes "
                 "uninitialised stores: on the tested data a populated undecoded store held "
                 "1,662,831 and 9,119 non-zero bytes while an uninitialised one held 204. "
                 "Non-Zero Bytes is a count of bytes, not an interpretation of them. A row here "
                 "means the file should be examined with other tooling; it is not evidence that "
                 "the app held any particular data, and an absence of rows means every Realm "
                 "store found was decoded, not that none exists. Header Read separates two "
                 "different conditions. False means the file does not begin with the Realm "
                 "mnemonic, so no header could be read and File Format Version (as stored) is "
                 "empty; Realm supports whole-file encryption, which presents this way, and the "
                 "artifact does not assert which cause applies. True with a file format the "
                 "parser does not decode is the unsupported-format case described above.",
        "paths": ('*.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "database",
        "sample_data": {
            "falken_ios26": "iOS 26.2.1 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
}

import os

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.realm_parser import parse_realm_file

# An uninitialised Realm still carries a header and a little structure. The tested
# populated-but-undecoded stores held 1,662,831 and 9,119 non-zero bytes; an
# uninitialised one held 204. Anything at or below this is not worth reporting.
_MIN_NON_ZERO = 1024


def _non_zero_bytes(path):
    """Count of bytes that are not 0x00, read in chunks so a large store is safe."""
    total = 0
    try:
        with open(path, 'rb') as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk) - chunk.count(b'\x00')
    except OSError as error:
        logfunc(f'Realm: could not read {os.path.basename(path)}: {error}')
        return None
    return total


@artifact_processor
def realmUndecodedStores(context):
    data_headers = (
        'File Name',
        'Header Read',
        'File Format Version (as stored)',
        'Size (Bytes)',
        'Non-Zero Bytes',
        'Classes Decoded',
        'Source File',
    )
    data_list = []
    source_files = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('.realm'):
            continue
        try:
            parsed = parse_realm_file(file_found)
        except Exception as error:  # pylint: disable=broad-exception-caught
            # A store the parser cannot open at all belongs in this table too.
            logfunc(f'Realm: {os.path.basename(file_found)} did not parse: {error}')
            parsed = None

        if parsed is None:
            header_read, file_format, decoded = False, '', 0
        else:
            header = parsed.get('header') or {}
            header_read = bool(header)
            file_format = header.get('File format (top ref 0)', '')
            names = set(parsed.get('active') or {}) | set(parsed.get('inactive') or {})
            decoded = len([name for name in names if name != 'metadata'])

        if decoded:
            continue

        non_zero = _non_zero_bytes(file_found)
        if non_zero is None or non_zero <= _MIN_NON_ZERO:
            continue

        try:
            size = os.path.getsize(file_found)
        except OSError:
            size = ''
        data_list.append((
            os.path.basename(file_found),
            header_read,
            file_format,
            size,
            non_zero,
            decoded,
            context.get_relative_path(file_found),
        ))
        source_files.append(file_found)

    return data_headers, data_list, '\n'.join(source_files)
