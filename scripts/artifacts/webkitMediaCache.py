"""Reconstruct supported WebKit CachedMedia resources with block provenance."""

__artifacts_v2__ = {
    'webkit_media_cache': {
        'name': 'WebKit - Media Cache',
        'description': 'Reconstructs stored CachedMedia resources from validated block mappings '
                       'and reports URLs, container ownership and repository metadata.',
        'author': '@ForensikITGmbH',
        'creation_date': '2026-10-15', 'last_update_date': '2026-10-15',
        'requirements': 'none', 'category': 'Browser',
        'notes': 'Experimental layout inferred from public MVS 2023 iOS 16.1.1 files: '
                 'outer version 2, identity version 1, block table version 5 (crab), '
                 '16/64 KiB blocks. Only fully covered, non-overlapping stored resources '
                 'are exported, without transcoding or filling gaps. MP4 metadata is '
                 'structurally checked; no decoder is run at runtime. A complete stored '
                 'resource is not necessarily a complete original video. Cache presence '
                 'does not establish a click, playback or viewing duration. Repository '
                 'Last Modified interprets lastmodtime as Cocoa seconds since 2001; it '
                 'applies to the repository, not to each resource. Only one timeline '
                 'event per repository is emitted. Raw times and block maps are retained '
                 'in provenance JSON. App ownership is the current acquired container '
                 'metadata, not evidence of the initiating email or page. Stored paths '
                 'may name an older container GUID; filename-only repository associations '
                 'are qualified and kept separate from the resource identity URL. '
                 'Application / Service was empty throughout the public subset because '
                 'no application display-name metadata was acquired. Web Data Store was '
                 'empty for direct Chrome and YouTube stores. Recovered Media, Recovered '
                 'File, Media Kind, Duration Seconds, Dimensions, Codecs, Output SHA256 '
                 'and Output MD5 have no value for unreconstructed entries. Resource URL, '
                 'Stored Resource Bytes, Covered Bytes, Block Size and Block Count have '
                 'no value where no supported identity/block table was decoded. The '
                 'empty repository has no Source SHA256 or Source Bytes; its index hash '
                 'is retained in Metadata and provenance. Container Type was uniform '
                 '(Data/Application) on all 11 public-subset rows. Stored Resource '
                 'Bytes and Covered Bytes were identical where populated in that subset: '
                 'the six supported tables each fully covered their stored resource. '
                 'See admin/docs/webkit_media_cache.md.',
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
            'mvs2023_ios16_subset': 'iOS 16.1.1 | 10 cache files, 3 repositories | '
                                   '11 rows, 6 recovered resources, 3 repository events',
            'mvs2021_ios14_empty': 'iOS 14.4 | 2 empty repositories | '
                                 '2 rows, 0 recovered resources, 2 repository events',
            'synthetic': 'Reversed blocks, gaps, invalid layouts and isolated containers',
            'mvs2023_fullzip_manual': 'Full archive run confirmed by contributor on 2026-10-15; '
                                      'no exported report acquired for an independent count check',
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
        timeline(context.get_report_folder(), 'WebKit MediaCache - Repository Last Modified', events,
                 ('Timestamp', 'Event Type', 'Raw lastmodtime', 'Source File', 'Source SHA256',
                  'Identifier', 'Container GUID', 'Web Data Store', 'Acquired Cache Files',
                  'Repository References', 'Provenance File', 'Interpretation'))
    logfunc(f'WebKit MediaCache: {len(caches)} cache files, {len(rows)} report rows, '
            f'{len(events)} repository timeline events')
    sources = [evidence_path(context, path) for path in caches]
    sources.extend(repo['source'] for repo in repositories.values())
    return HEADERS, rows, '\n'.join(sorted(sources))
