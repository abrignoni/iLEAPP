"""Shared path, owner and timestamp handling for WebKit artifacts."""

import math
import plistlib
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.parsers.expat import ExpatError


OWNER_PATHS = (
    '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
    '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
    '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
    '*/[Cc]ontainers/Bundle/Application/*/*.app/Info.plist',
    '*/[Cc]ontainers/Bundle/Application/*/iTunesMetadata.plist',
)

OWNER_HEADERS = (
    'Application / Service', 'Identifier', 'Container GUID', 'Container Type',
    'Web Data Store', 'Owner Metadata Source',
)

_CONTAINER = re.compile(
    r'(?P<root>(?:^|/)Containers/(?P<kind>Data/Application|Data/PluginKitPlugin|'
    r'Shared/AppGroup|Bundle/Application)/(?P<guid>[^/]+))(?=/|$)')
_SERVICE = re.compile(r'/Library/(?:WebKit|Caches)/([^/]+)/')
_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'


def unix_timestamp(value):
    """Return UTC for positive, finite Unix seconds; retain sentinels separately."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def evidence_path(context, path):
    return context.get_relative_path(str(path)).replace('\\', '/')


def web_data_store(path):
    path = str(path).replace('\\', '/')
    if '/SystemData/com.apple.SafariViewService/' in path:
        return 'SafariViewService'
    return 'WebKit'


def _read_plist(path):
    try:
        with open(path, 'rb') as handle:
            value = plistlib.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, plistlib.InvalidFileException, ValueError, TypeError, OverflowError, ExpatError):
        return {}


class WebKitOwnerResolver:
    """Resolve owners from acquired metadata without guessing a host application."""

    def __init__(self, context, files):
        self.context = context
        self.containers = {}
        self.names = {}
        for path in sorted(set(map(str, files))):
            relative = evidence_path(context, path)
            filename = Path(path).name
            if filename not in (_METADATA_NAME, 'Info.plist', 'iTunesMetadata.plist'):
                continue
            value = _read_plist(path)
            if not value:
                continue
            if filename == _METADATA_NAME:
                match = _CONTAINER.search(relative)
                root = relative[:match.end()].lstrip('/') if match else ''
                if match and relative.lstrip('/') == root + '/' + filename:
                    identifier = value.get('MCMMetadataIdentifier', '')
                    if isinstance(identifier, str) and identifier:
                        self.containers[root] = (identifier, relative)
            else:
                identifier = value.get('CFBundleIdentifier') or value.get('softwareVersionBundleId')
                name = value.get('CFBundleDisplayName') or value.get('CFBundleName') or value.get('itemName')
                if isinstance(identifier, str) and isinstance(name, str) and name:
                    self.names.setdefault(identifier, set()).add((name, relative))

    def resolve(self, path):
        relative = evidence_path(self.context, path)
        match = _CONTAINER.search(relative)
        name = identifier = guid = kind = metadata = ''
        if match:
            guid, kind = match['guid'], match['kind']
            root = relative[:match.end()].lstrip('/')
            identifier, metadata = self.containers.get(root, ('', ''))
        else:
            service = _SERVICE.search('/' + relative.lstrip('/'))
            if service and service[1].startswith('com.'):
                identifier, kind = service[1], 'System service'
        if identifier in self.names:
            values = self.names[identifier]
            name = '; '.join(sorted({item[0] for item in values}))
            sources = {item[1] for item in values}
            if metadata:
                sources.add(metadata)
            metadata = '\n'.join(sorted(sources))
        return name, identifier, guid, kind, web_data_store(relative), metadata
