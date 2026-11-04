__artifacts_v2__ = {
    "hive_boxes": {
        "name": "Hive - Boxes and Superseded Frames",
        "description": "One row per box file matching *.hive, with the identifier recorded for the "
                       "container that holds it, the frames the read returned, the entries a live "
                       "read returns, and the frames holding an overwritten or a deleted value.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "Hive",
        "notes": "Hive is a key-value store used by Flutter applications through the hive and "
                 "hive_ce packages. A box is an append-only log of frames: a write appends a new "
                 "frame for the key rather than replacing the old one, and a delete appends a "
                 "tombstone. What the application reads back is the last frame written for each key "
                 "that has not since been deleted, so the frames a file still holds can carry "
                 "values the application has already replaced or removed. This artifact reports "
                 "where the boxes are and how far the file's contents and the live view have "
                 "diverged. It does not report keys or values. 'Frames Holding an Overwritten "
                 "Value' counts value frames whose key's next readable frame in the file is another "
                 "write. 'Frames Holding a Deleted Value' counts value frames whose key's next "
                 "readable frame in the file is a tombstone. A frame whose checksum failed, or "
                 "whose key or value did not decode, is counted in neither. 'How the Box Read' "
                 "names the offset where the read stopped, and reports a clean end only when the "
                 "frames account for the whole file. Hive rewrites a box once more than 60 frames "
                 "have been superseded or deleted and that count exceeds 15 percent of the live "
                 "entry count (isar/hive v2.2.3, box/default_compaction_strategy.dart with "
                 "box/keystore.dart). An overwrite counts towards that total, not just a delete, "
                 "and an application can supply its own strategy or call compact() directly. The "
                 "rewrite leaves no marker, so a row showing no overwritten and no deleted frames "
                 "does not establish that nothing was ever overwritten or deleted in that box. Hive "
                 "also truncates a damaged tail itself on the next open when crash recovery is "
                 "enabled (isar/hive v2.2.3, backend/vm/storage_backend_vm.dart), so a row naming a "
                 "failed checksum or a cut-short frame is consistent with the application not "
                 "having reopened that box since the damage, or with recovery being off. The copy "
                 "in the extraction can also have been taken while a write was in flight. "
                 "Separately, the reader refuses a frame declaring more than 1 MiB, which Hive "
                 "itself does not, so a box holding a larger frame reads as a stop at that offset. "
                 "The Container Identifier column is the MCMMetadataIdentifier value recorded in "
                 "the .com.apple.mobile_container_manager.metadata.plist of the container the box "
                 "sits in, reported as stored: a bundle identifier for an application or app "
                 "extension container, an app group identifier for a shared container. This "
                 "artifact matches those plists for that purpose. The column is empty when the box "
                 "sits outside a container, or when that container's plist was not acquired, did "
                 "not parse, or carries no MCMMetadataIdentifier string. It is never inferred from "
                 "a neighbouring container and never taken from the path. A box whose every frame "
                 "fails its checksum while every key parses, with the frames ending on the file "
                 "end, is reported as reading like an encrypted box, and its values are not "
                 "decoded, because the encryption key is not in the file. For such a row the entry "
                 "and displaced counts are reported as 0, not as measured. A box whose every frame "
                 "is damaged can read the same way, when each key still parses and the frame "
                 "lengths still chain to the end of the file. Measured on dexter_ios18: 4 boxes, "
                 "all of them in one application container, so the Container Identifier column held "
                 "a single bundle identifier on all 4 rows. One is an empty file. Two boxes hold an "
                 "overwritten value, with 40 frames against 6 live entries and 21 against 6. Frames "
                 "Holding a Deleted Value was 0 on all 4 rows: no box on that image had a key whose "
                 "next readable frame was a tombstone. That run produced only two of the 'How the "
                 "Box Read' outcomes, the read reaching the end of the file and the file being "
                 "empty; the truncated, failed-CRC, undecoded-frame, encrypted, stopped-early and "
                 "no-frame-at-offset-0 branches are unexercised on it. The reader's handling of a "
                 "truncated frame, a failed checksum, an undecodable value, an encrypted box and an "
                 "unusable frame length is covered by its own tests (tests/test_hive_parser.py in "
                 "abrignoni/hive-parser at the vendored commit). The phrases this module builds, "
                 "and what the Container Identifier column does with each container shape, are "
                 "covered by admin/test/scripts/test_hive_boxes.py. The reader is "
                 "scripts/hive_parser.py, vendored from abrignoni/hive-parser.",
        "paths": (
            '*.hive',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "dexter_ios18": "iOS 18 | 4 rows | 1 empty file, 2 boxes with overwritten frames, 0 boxes with deleted frames",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.webkit_helpers import WebKitOwnerResolver, evidence_path
from scripts.hive_parser import (HiveError, displaced_counts, live_entries,
                                 looks_encrypted, read_frames)

# What a file named .hive that is not a Hive box, or is damaged, can raise.
READ_ERRORS = (HiveError, OSError, ValueError, IndexError, MemoryError)

# The container kinds whose identifier the resolver reads from that container's own
# metadata plist. Its other branch takes a directory name out of the path for a file
# under Library/Caches or Library/WebKit, which would put a name anyone can create
# into a column an examiner reads as recorded identity, so this list is what the
# column accepts and anything else reports nothing.
_PLIST_BACKED_KINDS = ('Data/Application', 'Data/PluginKitPlugin',
                       'Shared/AppGroup', 'Bundle/Application')


def _container_identifier(resolver, file_found):
    """The identifier the box's own container records, or '' when none does."""
    identifier, kind = (resolver.resolve(file_found)[i] for i in (1, 3))
    return identifier if kind in _PLIST_BACKED_KINDS else ''


def _how_it_read(frames, encrypted, size):
    """Why the frame count and the entry count differ, or that nothing stopped the read.

    The counts on their own do not say whether a smaller number means the box is
    small or means the read stopped early, and those are different findings. The
    reader's walk gives up without recording a frame when a declared length is
    unusable, so a clean end is reported only once the frames account for the
    whole file.
    """
    if not frames:
        if size == 0:
            return 'the file is empty'
        return f'no frame could be read at offset 0, in a file of {size} byte(s)'
    if encrypted:
        return ('every frame failed its CRC while its keys read cleanly, which is how an '
                'encrypted box reads; values are not decoded')
    said = []
    unverified = [f for f in frames if not f['crc_ok']]
    if unverified:
        first = unverified[0]
        if first['truncated']:
            said.append(f'the read stopped at offset {first["offset"]}, where a frame is '
                        f'cut short by the end of the file')
        else:
            said.append(f'the read stopped at offset {first["offset"]}, where a frame '
                        f'failed its own CRC')
    else:
        end = frames[-1]['offset'] + frames[-1]['length']
        if end < size:
            said.append(f'the read stopped at offset {end}, where no further frame could be '
                        f'read, leaving {size - end} byte(s) unread')
    undecoded = [f for f in frames if f['error'] and f['crc_ok']]
    if undecoded:
        said.append(f'{len(undecoded)} frame(s) did not decode cleanly and are left out '
                    f'of the entry and displaced counts')
    return '; '.join(said) if said else 'the read reached the end of the file'


@artifact_processor
def hive_boxes(context):
    data_list = []
    sources = []

    files = tuple(dict.fromkeys(map(str, context.get_files_found())))
    # The container metadata plists are matched so the owner can be read from the
    # extraction rather than inferred from the path; they are not rows themselves.
    resolver = WebKitOwnerResolver(context, files)

    for file_found in sorted(files):
        if not file_found.replace('\\', '/').rsplit('/', 1)[-1].lower().endswith('.hive'):
            continue
        try:
            with open(file_found, 'rb') as handle:
                data = handle.read()
            frames = read_frames(data)
        except READ_ERRORS as ex:
            logfunc(f'Hive boxes: {evidence_path(context, file_found)} could not be read as '
                    f'a Hive box: {type(ex).__name__}: {ex}')
            continue

        encrypted = looks_encrypted(frames)
        # An encrypted box's values are ciphertext, so it has no entries to read back
        # and no displaced values that can be counted.
        live = {} if encrypted else live_entries(frames)
        overwritten, removed = (0, 0) if encrypted else displaced_counts(frames)

        data_list.append((
            _container_identifier(resolver, file_found),
            evidence_path(context, file_found),
            len(frames),
            len(live),
            overwritten,
            removed,
            _how_it_read(frames, encrypted, len(data)),
        ))
        sources.append(file_found)

    # The boxes holding what a live read drops are the reason this table exists, so
    # they lead it.
    data_list.sort(key=lambda row: (-(row[4] + row[5]), row[1]))

    data_headers = (
        'Container Identifier',
        'Box',
        'Frames Read',
        'Entries a Live Read Returns',
        'Frames Holding an Overwritten Value',
        'Frames Holding a Deleted Value',
        'How the Box Read',
    )
    return data_headers, data_list, '\n'.join(sources)
