__artifacts_v2__ = {
    "applicationSnapshots": {
        "name": "App Snapshots",
        "description": "Snapshots saved by iOS for individual apps. KTX images are converted to "
                       "PNG for display, and XBApplicationSnapshotManifest metadata is joined when "
                       "applicationState.db is available. KTX files smaller than 2500 bytes and "
                       "KTX files that do not decode are left out.",
        "author": "@ydkhatri - @AlexisBrignoni",
        "creation_date": "2020-07-23",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Apple explains that UIKit takes a snapshot of the app's user interface after it enters the "
                 "background, for display in the app switcher. Apps may deliberately hide or replace sensitive content before capture, so an "
                 "image can be a launch/default screen or privacy overlay and should not by itself be treated as proof "
                 "that the user viewed the depicted content. File Modified Date is source-file metadata; Manifest "
                 "Creation Date and Manifest Last Used Date are separate fields stored by SplashBoard. "
                 "On iOS 26 and 27 the KTX blocks can be stored in tiles; they are put back in order before "
                 "conversion, in one of two bit orders. A file name ending in @2x selects the second order; every "
                 "other name uses the first. The @2x order "
                 "comes from a single 2x device, so a 2x snapshot that still looks scrambled may be a "
                 "decoding limit rather than what the file holds. Reference: "
                 "https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background ; "
                 "foundational research: https://gforce4n6.blogspot.com/2019/09/a-quick-look-into-ios-snapshots.html "
                 "and https://abrignoni.blogspot.com/2019/09/ios-snapshots-triage-parser-working.html",
        "paths": (
            '*/Library/Caches/Snapshots/*.ktx', 
            '*/Library/Caches/Snapshots/*.jpeg', 
            '*/SplashBoard/Snapshots/*.ktx', 
            '*/SplashBoard/Snapshots/*.jpeg',
            '*/mobile/Library/FrontBoard/applicationState.db*'),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 68 rows",
            "dexter_ios18": "iOS 18.3.2 | 305 rows",
            "felix_ios17": "iOS 17.6.1 | 178 rows",
            "fsfull002_ios17": "iOS 17.1 | 106 rows",
            "hc_ios18_7": "iOS 18.7.8 | 207 rows",
            "iphone11_ios17": "iOS 17.3 | 482 rows",
            "iphone12_ios18": "iOS 18.7 | 194 rows",
            "iphone14plus_ios18": "iOS 18.0 | 529 rows",
            "otto_ios17": "iOS 17.5.1 | 360 rows",
            "abe_ios16": "iOS 16.5 | 364 rows",
            "felix23_ios16": "iOS 16.5 | 234 rows",
            "hickman_ios13": "iOS 13.3.1 | 287 rows",
            "hickman_ios14": "iOS 14.3 | 342 rows",
            "jess_ios15": "iOS 15.0.2 | 84 rows",
            "magnet_ios16": "iOS 16.1.1 | 219 rows",
            "falken_ios26": "iOS 26.2.1 | 271 rows",
            "hc_ios26": "iOS 26.5.2 | 283 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 655 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 430 rows",
        }
    },
}

from collections import defaultdict
from pathlib import Path, PurePosixPath
import re
import sqlite3

from scripts.artifacts.applicationStateDB import _get_snapshots
from scripts.ktx.ios_ktx2png import KTX_reader
from scripts.ilapfuncs import artifact_processor, check_in_media, lava_get_full_media_info, logfunc, convert_unix_ts_to_utc


_SCALE_IN_NAME = re.compile(r'@(\d+)x\.ktx$', re.IGNORECASE)


def _image_scale_from_name(ktx_path):
    '''The image scale in the file name (<id>@2x.ktx), or None. It matched the manifest
    imageScale on every snapshot record in the images run. Read from the file name
    alone, never from the folders above it.'''
    match = _SCALE_IN_NAME.search(PurePosixPath(str(ktx_path).replace('\\', '/')).name)
    return int(match.group(1)) if match else None


def _image_scale_for(file_found, seeker):
    '''The scale from the evidence file name. The seeker can stage a file under
    another name (name~case-<tag>.ktx when two evidence paths differ only in
    case), so the name it recorded for the source is read first.'''
    infos = getattr(seeker, 'file_infos', None)
    info = infos.get(file_found) if isinstance(infos, dict) else None
    source = getattr(info, 'source_path', None)
    return _image_scale_from_name(source if isinstance(source, str) and source else file_found)


def save_ktx_to_png_if_valid(ktx_path, save_to_path, image_scale=None):
    '''Convert a valid iOS KTX image to PNG.'''

    with open(ktx_path, 'rb') as f:
        ktx = KTX_reader(image_scale=image_scale)
        try:
            if ktx.validate_header(f):
                data = ktx.get_uncompressed_texture_data(f)
                dec_img = ktx.to_image(data)
                # either all black or all white https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
                # if sum(dec_img.convert("L").getextrema()) in (0, 2):
                #     logfunc('Skipping image as it is blank')
                #     return False
                    
                dec_img.save(save_to_path, "PNG", compress_type=3)
                #                                    ^
                # as per https://github.com/python-pillow/Pillow/issues/5986

                return True
        except (OSError, ValueError) as ex:
            logfunc(f'Left out {Path(ktx_path).name}, it was not converted: {ex}')
    return False


# The manifest names a scene directory sceneID:<bundle>-<suffix>. Extractions write
# it as sceneID_ or without the colon (iphone12_ios18 uses the colon-less spelling,
# with -default and -<UUID> suffixes), so accept all three spellings.
_SCENE_PREFIX = re.compile(r'^sceneID[:_]?')


def _bundle_id_from_path(media_path):
    """Return the bundle directory immediately below a Snapshots directory."""

    parts = media_path.parts
    for idx in range(len(parts) - 1, -1, -1):
        if parts[idx] == 'Snapshots' and idx + 1 < len(parts):
            bundle_id = parts[idx + 1]
            bundle_id = bundle_id.split(' - {', 1)[0]
            if _SCENE_PREFIX.match(bundle_id):
                bundle_id = _SCENE_PREFIX.sub('', bundle_id, count=1)
                bundle_id = re.sub(
                    r'-(?:default|[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})$',
                    '',
                    bundle_id,
                )
            return bundle_id

    # Fallback for an unexpected layout. The parent is normally either the
    # snapshot group or its downscaled variant directory.
    group_path = media_path.parent.parent if media_path.parent.name == 'downscaled' else media_path.parent
    group_name = _SCENE_PREFIX.sub('', group_path.name, count=1)
    return group_name.split(' - {', 1)[0].rsplit('-default', 1)[0]


def _snapshot_group_from_path(media_path):
    """Return the group or scene directory that contains a snapshot, with a scene
    directory spelled sceneID: as the manifest stores it."""

    group_path = media_path.parent.parent if media_path.parent.name == 'downscaled' else media_path.parent
    return _SCENE_PREFIX.sub('sceneID:', group_path.name, count=1)


def _manifest_index(files_found):
    """Index XBApplicationSnapshotManifest rows by their relative filename."""

    db_path = next((path for path in files_found if Path(path).name == 'applicationState.db'), None)
    index = defaultdict(list)
    if not db_path:
        return index

    try:
        for snapshot in _get_snapshots(db_path):
            if snapshot.relativePath:
                index[Path(snapshot.relativePath).name].append(snapshot)
    except (OSError, ValueError, sqlite3.Error) as ex:
        logfunc(f'Unable to parse snapshot metadata from applicationState.db: {ex}')
    return index


def _manifest_record(index, media_path, bundle_id, snapshot_group):
    """Find the manifest record for an image, tolerating sanitized ZIP paths."""

    candidates = index.get(media_path.name, ())
    if len(candidates) == 1:
        return candidates[0]

    for candidate in candidates:
        if candidate.bundleID == bundle_id and candidate.snapshot_group == snapshot_group:
            return candidate
    for candidate in candidates:
        if candidate.bundleID == bundle_id:
            return candidate
    return None


@artifact_processor
def applicationSnapshots(context): #files_found, report_folder, seeker, wrap_text, timezone_offset):
    # artifact_info = inspect.stack()[0]
    data_list = []
    source_dirs = set()

    files_found = context.get_files_found()
    seeker = context.get_seeker()
    manifest_index = _manifest_index(files_found)

    for file_found in files_found:
        media_path = Path(file_found)
        suffix = media_path.suffix.lower()
        if suffix not in ('.ktx', '.jpeg'):
            continue

        bundle_id = _bundle_id_from_path(media_path)
        snapshot_group = _snapshot_group_from_path(media_path)
        variant = 'downscaled' if media_path.parent.name == 'downscaled' else 'default'
        manifest = _manifest_record(manifest_index, media_path, bundle_id, snapshot_group)
        if manifest and manifest.bundleID:
            bundle_id = manifest.bundleID

        if suffix == '.ktx':
            # Preserve the artifact's established lower-size threshold. Some
            # very small files are incomplete or do not contain a useful image.
            if media_path.stat().st_size < 2500:
                continue
            png_path = media_path.with_suffix((".png"))
            if save_ktx_to_png_if_valid(media_path, png_path, _image_scale_for(file_found, seeker)):
                media_item = check_in_media(
                    file_found,
                    bundle_id,
                    png_path,
                    force_type='image/png',
                    force_extension='png',
                )
            else:
                continue
        else:
            media_item = check_in_media(
                file_found,
                bundle_id,
                force_type='image/jpeg',
                force_extension='jpeg',
            )
        
        if not media_item:
            continue

        source_dirs.add(str(media_path.parent))
            
        last_modified_date = convert_unix_ts_to_utc(lava_get_full_media_info(media_item)['updated_at'])
        creation_date = manifest.creationDate if manifest else ''
        last_used_date = manifest.lastUsedDate if manifest else ''
        manifest_group = manifest.snapshot_group if manifest else snapshot_group
        identifier = manifest.identifier if manifest else media_path.stem.split('@', 1)[0]
        data_list.append([
            last_modified_date,
            creation_date,
            last_used_date,
            bundle_id,
            manifest_group,
            identifier,
            variant,
            context.get_relative_path(file_found),
            media_item,
        ])

    data_headers = (
        ('File Modified Date', 'datetime'),
        ('Manifest Creation Date', 'datetime'),
        ('Manifest Last Used Date', 'datetime'),
        'Bundle ID',
        'Snapshot Group',
        'Snapshot Identifier',
        'Variant',
        'Source Path',
        ('Snapshot', 'media'),
    )

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
