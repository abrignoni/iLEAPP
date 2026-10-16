"""Rebuild the media stored in CachedMedia files of Apple's media disk cache."""

__artifacts_v2__ = {
    'webkit_media_cache': {
        'name': 'Media Cache - CachedMedia',
        'description': 'Rebuilds video and audio stored in CachedMedia files (the media disk '
                       'cache used by WebKit and other media clients) from their block tables, '
                       'with the resource URL, the owning app container and the cache '
                       'repository entry.',
        'author': '@ForensikITGmbH, @AlexisBrignoni, Claude',
        'creation_date': '2026-10-15', 'last_update_date': '2026-10-16',
        'requirements': 'none', 'category': 'Media Cache',
        'notes': 'The repository and block-table strings (diskcacherepository.plist, lastmodtime, '
                 "checkedinlist, checkedoutlist, crab) are in Apple's MediaToolbox framework, and "
                 'WebCore holds the CachedMedia- file name (checked on macOS 27.0.1); no writer code '
                 'was read. Apps keep the cache in tmp/WebKit/MediaCache or under Library/WebKit; it '
                 'is also found outside app containers, in tmp/MediaCache, Library/WebClips and '
                 'tmp/com.apple.mediaplaybackd/MediaCache (repository file only, in the corpus). The '
                 'file layout is read from the files, not from a published specification. A resource '
                 'is exported only when its block table covers every stored byte once; nothing is '
                 'padded or filled in. "Incomplete resource" rows have gaps in the table. "Cache '
                 'header zeroed" rows have zeros where the block table is kept, so the stored bytes '
                 'cannot be put in order. Both are listed without an export. A complete stored '
                 'resource can still be a segment or a preview of a longer original. MP4 box structure'
                 ' and MP3 frame headers are checked; no decoder runs. A cached resource does not show'
                 ' that it was played or viewed. Repository Last Modified is lastmodtime read as '
                 'seconds since 2001-01-01 UTC. In the 20 zip-format corpus images, 77 repositories '
                 'were compared with the modification time the extraction recorded for the plist. Five'
                 ' had no recorded time and one had a placeholder time at the Unix epoch. Of the other'
                 ' 71, lastmodtime matched within one second in 48 and was later in 23, never earlier.'
                 ' The tar images were not compared. It belongs to the repository, not to any one '
                 'resource, and is written to the timeline once per repository that has one. '
                 'Identifier and Container GUID come from the container metadata and name the app '
                 'recorded for that container in the extraction. Application / Service is the app name'
                 ' from its bundle metadata and is blank when no bundle name for that identifier was '
                 'found in the extraction. Caches outside an app container have blank owner columns; '
                 'their folder path is the only pointer to the writer. Web Data Store is '
                 'SafariViewService for caches under that service and blank otherwise. Container Type '
                 'held Data/Application on every row with an owner. Covered Bytes equalled Stored '
                 'Resource Bytes on all 180 exported corpus rows and was smaller on all 23 Incomplete '
                 'resource rows. Resource URL, Stored Resource Bytes, Covered Bytes, Block Size and '
                 'Block Count are blank where the cache file has no readable header (all-zero and '
                 'zeroed-header files) and on rows whose source is the repository plist (a repository '
                 'with no cache files, or a reference to a cache file not acquired), which also have '
                 'no Source Bytes. Repository URLs equalled Resource URL on all 203 corpus rows that '
                 'have both, and is the only URL on rows whose cache file has none. Recovered Media, '
                 'Media Kind, Duration Seconds, Dimensions, Codecs, Output SHA256, Output MD5, '
                 'Validation and Recovered File are blank for rows without an export. The block map of'
                 ' each row is in its Provenance File.',
        'paths': (
            '*/MediaCache/CachedMedia-*',
            '*/MediaCache/diskcacherepository.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/Bundle/Application/*/*.app/Info.plist',
            '*/[Cc]ontainers/Bundle/Application/*/iTunesMetadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'movie',
        'sample_data': {
            'abe_ios16': 'iOS 16.5 | 30 rows, 24 exported',
            'adams_iphone12mini': 'iOS 17.1.1 | 4 rows, 2 exported',
            'cookbook_ios1751': 'iOS 17.5.1 | 16 rows, 13 exported',
            'ctf2020_ios12': 'iOS 12.4 | 6 rows, 5 exported',
            'dexter_ios18': 'iOS 18.3.2 | 29 rows, 21 exported',
            'falken_ios26': 'iOS 26.2.1 | 8 rows, 5 exported',
            'felix23_ios16': 'iOS 16.5 | 2 rows, 0 exported',
            'felix_ios17': 'iOS 17.6.1 | 1 row, 0 exported',
            'fsfull002_ios17': 'iOS 17.1 | 4 rows, 1 exported',
            'hc_ios17_2': 'iOS 17.2.1 | 13 rows, 5 exported',
            'hc_ios18_7': 'iOS 18.7.8 | 12 rows, 5 exported',
            'hc_ios26': 'iOS 26.5.2 | 2 rows, 0 exported',
            'hexordia_ios1651': 'iOS 16.5.1 | 29 rows, 24 exported',
            'hickman_ios13': 'iOS 13.3.1 | 4 rows, 2 exported',
            'hickman_ios14': 'iOS 14.3 | 2 rows, 1 exported',
            'hickman_ios15': 'iOS 15.3.1 | 14 rows, 6 exported',
            'iphone11_ios17': 'iOS 17.3 | 36 rows, 26 exported',
            'iphone12_ios18': 'iOS 18.7 | 4 rows, 2 exported',
            'iphone14plus_ios18': 'iOS 18.0 | 4 rows, 3 exported',
            'iphone14plus_ios18_mvs2025': 'iOS 18.0 | 5 rows, 3 exported',
            'jess_ios15': 'iOS 15.0.2 | 2 rows, 0 exported',
            'magnet_ios16': 'iOS 16.1.1 | 11 rows, 6 exported',
            'otto_ios17': 'iOS 17.5.1 | 35 rows, 26 exported',
        },
    },
}

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, timeline
from scripts.webkit_helpers import OWNER_HEADERS, WebKitOwnerResolver, evidence_path
from scripts.webkit_media_cache import (
    PLIST_ERRORS, error_text, file_hashes, media_info, read_cache, reconstruct, valid_number,
)
import plistlib

_REPOSITORY = 'diskcacherepository.plist'
_CHECKOUT = re.compile(r'^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}=')
_MAX_REPOSITORY = 16 * 1024 * 1024
_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

HEADERS = (
    ('Recovered Media', 'media'), 'Recovery Status', 'Media Kind', 'Duration Seconds',
    'Dimensions', 'Codecs', 'Resource URL',
) + OWNER_HEADERS + (
    ('Repository Last Modified', 'datetime'), 'Repository Association', 'Repository URLs',
    'Source File', 'Repository Source', 'Source Bytes', 'Stored Resource Bytes',
    'Covered Bytes', 'Block Size', 'Block Count', 'Source SHA256', 'Output SHA256',
    'Output MD5', 'Recovered File', 'Validation', 'Provenance File', 'Metadata',
)


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      default=lambda item: item.hex() if isinstance(item, bytes) else str(item))


def _key(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:24]


def repository_time(value):
    """Interpret a finite stored Cocoa value without inventing missing dates."""
    if not valid_number(value) or value <= 0:
        return None
    try:
        return _EPOCH + timedelta(seconds=value)
    except (ValueError, OverflowError):
        return None


def _repository(path, context):
    row = {'source': evidence_path(context, path), 'references': [], 'metadata': {},
           'status': 'Repository not decoded', 'timestamp': None}
    try:
        row['sha256'] = file_hashes(path)['sha256']
        if path.stat().st_size > _MAX_REPOSITORY:
            row['status'] = 'Repository exceeds size limit'
            return row
        value = plistlib.loads(path.read_bytes())
        if not isinstance(value, dict):
            row['status'] = 'Repository is not a dictionary'
            return row
        row['metadata'] = value
        row['timestamp'] = repository_time(value.get('lastmodtime'))
        for state in ('checkedinlist', 'checkedoutlist'):
            entries = value.get(state, {})
            if not isinstance(entries, dict):
                continue
            for key, stored in sorted(entries.items(), key=lambda item: str(item[0])):
                if not isinstance(key, str) or not isinstance(stored, str):
                    continue
                url = _CHECKOUT.sub('', key, count=1) if state == 'checkedoutlist' else key
                filename = stored.replace('\\', '/').rsplit('/', 1)[-1]
                row['references'].append({'state': state, 'key': key, 'url': url,
                                          'stored_path': stored, 'filename': filename})
        row['status'] = 'Decoded repository'
    except PLIST_ERRORS as error:
        row['status'] = 'Invalid repository: ' + error_text(error)
    return row


def _association(source, identity_url, references):
    statuses = set()
    for ref in references:
        stored = ref['stored_path'].replace('\\', '/').lstrip('/')
        exact = source.lstrip('/') == stored or source.endswith('/' + stored)
        if exact:
            label = 'Exact stored path'
        elif identity_url and identity_url == ref['url']:
            label = 'Same repository, filename and identity URL; stored path differs'
        else:
            label = 'Same repository and filename only; stored path differs (unverified)'
        if identity_url and identity_url != ref['url']:
            label += '; identity URL conflicts with repository URL'
        statuses.add(ref['state'] + ': ' + label)
    return '\n'.join(sorted(statuses))


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(value) + '\n', encoding='utf-8')


def _row(context, resolver, path, cache, repository, references, output_root):
    source = evidence_path(context, path)
    key = _key(source + _json(cache.get('missing_reference', {})))
    values = {'Source File': source, 'Recovery Status': cache['status'],
              'Source Bytes': cache.get('source_bytes', ''),
              'Source SHA256': cache.get('source_sha256', ''),
              'Resource URL': cache.get('url', ''),
              'Stored Resource Bytes': cache.get('resource_bytes', ''),
              'Covered Bytes': cache.get('covered_bytes', ''),
              'Block Size': cache.get('block_size', ''), 'Block Count': cache.get('block_count', '')}
    values.update(zip(OWNER_HEADERS, resolver.resolve(path)))
    info = {}
    if cache['status'] == 'Ready for reconstruction':
        recovered = output_root / 'recovered' / (key + '.bin')
        recovered.parent.mkdir(parents=True, exist_ok=True)
        # A repeated run may replace only this module's generated derivative.
        if recovered.exists():
            recovered.unlink()
        if reconstruct(path, recovered, cache):
            info = media_info(recovered)
            target = recovered.with_suffix('.' + info['extension'])
            if target != recovered:
                recovered.replace(target)
            values['Recovered File'] = evidence_path(context, target)
            values['Recovered Media'] = check_in_media(
                str(path), name=path.name + '.' + info['extension'],
                converted_file_path=str(target), force_type=info['mime'],
                force_extension=info['extension'])
            if not values['Recovered Media']:
                cache['warnings'].append('Media registration unavailable; derivative retained in Recovered File')
            values.update({'Media Kind': info['kind'],
                           'Duration Seconds': info.get('duration_seconds', ''),
                           'Codecs': ', '.join(sorted({codec for track in info['tracks']
                                                     for codec in track.get('codecs', [])})),
                           'Dimensions': ', '.join(f"{track['width']:g}x{track['height']:g}"
                                                   for track in info['tracks'] if 'width' in track),
                           'Output SHA256': cache['output_sha256'], 'Output MD5': cache['output_md5'],
                           'Validation': info['validation']})
    values['Recovery Status'] = cache['status']
    if repository:
        values.update({'Repository Source': repository['source'],
                       'Repository Last Modified': repository['timestamp'],
                       'Repository Association': _association(source, cache.get('url', ''), references),
                       'Repository URLs': '\n'.join(sorted({ref['url'] for ref in references}))})
        if 'missing_reference' in cache:
            values['Repository Association'] = 'Repository reference only; cache file not acquired'
    metadata = {key: value for key, value in cache.items() if key not in ('blocks',)}
    metadata.update(media=info, repository_references=references)
    if repository:
        metadata.update(repository_status=repository['status'],
                        repository_sha256=repository.get('sha256', ''),
                        repository_raw_lastmodtime=repository['metadata'].get('lastmodtime'))
    values['Metadata'] = _json(metadata)
    provenance = output_root / 'provenance' / (key + '.json')
    _write_json(provenance, {'source': source, **metadata, 'blocks': cache.get('blocks', []),
                             'recovered_file': values.get('Recovered File', ''),
                             'owner': dict(zip(OWNER_HEADERS, resolver.resolve(path)))})
    values['Provenance File'] = evidence_path(context, provenance)
    return tuple(values.get(header[0] if isinstance(header, tuple) else header, '') for header in HEADERS)


@artifact_processor
def webkit_media_cache(context):
    """One selection produces the media table and repository-level timeline."""
    files = sorted({Path(path) for path in context.get_files_found() if Path(path).is_file()})
    resolver = WebKitOwnerResolver(context, files)
    caches = [path for path in files if path.name.startswith('CachedMedia-') and path.parent.name == 'MediaCache']
    repositories = {path.parent: _repository(path, context) for path in files if path.name == _REPOSITORY}
    output_root = Path(context.get_report_folder()) / 'webkit_media_cache'
    rows = []
    events = []
    for path in caches:
        try:
            cache = read_cache(path)
        except OSError as error:
            cache = {'status': 'Cache read failed: ' + error_text(error), 'warnings': []}
        repo = repositories.get(path.parent)
        refs = [ref for ref in repo['references'] if ref['filename'] == path.name] if repo else []
        rows.append(_row(context, resolver, path, cache, repo, refs, output_root))
    for folder, repo in sorted(repositories.items()):
        present = {path.name for path in caches if path.parent == folder}
        missing = [ref for ref in repo['references'] if ref['filename'] not in present]
        for ref in missing:
            # The source is the acquired index, never a guessed file elsewhere.
            marker = folder / _REPOSITORY
            cache = {'status': 'Repository reference; cache file not acquired', 'warnings': [],
                     'missing_reference': ref}
            rows.append(_row(context, resolver, marker, cache, repo, [ref], output_root))
        if not present and not repo['references']:
            cache = {'status': repo['status'] + '; no cache references or acquired media', 'warnings': []}
            rows.append(_row(context, resolver, folder / _REPOSITORY, cache, repo, [], output_root))
        repository_provenance = output_root / 'repositories' / (_key(repo['source']) + '.json')
        _write_json(repository_provenance, repo)
        if repo['timestamp'] is not None:
            owner = resolver.resolve(folder / _REPOSITORY)
            events.append((repo['timestamp'], 'Repository lastmodtime (Cocoa interpretation)',
                           repo['metadata'].get('lastmodtime'), repo['source'], repo.get('sha256', ''),
                           owner[1], owner[2], owner[4], len(present), len(repo['references']),
                           evidence_path(context, repository_provenance),
                           'Repository-level timestamp; not an individual resource request or playback time'))
    if events:
        timeline(context.get_report_folder(), 'Media Cache - Repository Last Modified', events,
                 ('Timestamp', 'Event Type', 'Raw lastmodtime', 'Source File', 'Source SHA256',
                  'Identifier', 'Container GUID', 'Web Data Store', 'Acquired Cache Files',
                  'Repository References', 'Provenance File', 'Interpretation'))
    logfunc(f'Media Cache - CachedMedia: {len(caches)} cache files, {len(rows)} report rows, '
            f'{len(events)} repository timeline events')
    sources = [evidence_path(context, path) for path in caches]
    sources.extend(repo['source'] for repo in repositories.values())
    return HEADERS, rows, '\n'.join(sorted(sources))
