""" springboard """
__artifacts_v2__ = {
    "icons_screen": {
        "name": "iOS Home Screen Layout",
        "description": "Home screen layout: apps, folders, widgets and the dock, per screen page",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "Parsed from SpringBoard/IconState.plist. Items are listed in their on-screen "
                 "flow order. See 'iOS Home Screen Layout - Visual' for a rendered image of each screen.",
        "paths": ('**/SpringBoard/IconState.plist',),
        "output_types": "standard",
        "artifact_icon": "layout-grid",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 96 rows",
            "dexter_ios18": "iOS 18.3.2 | 109 rows",
            "felix_ios17": "iOS 17.6.1 | 71 rows",
            "fsfull002_ios17": "iOS 17.1 | 63 rows",
            "hc_ios18_7": "iOS 18.7.8 | 74 rows",
            "iphone11_ios17": "iOS 17.3 | 99 rows",
            "iphone12_ios18": "iOS 18.7 | 75 rows",
            "iphone14plus_ios18": "iOS 18.0 | 61 rows",
            "otto_ios17": "iOS 17.5.1 | 89 rows",
            "abe_ios16": "iOS 16.5 | 95 rows",
            "felix23_ios16": "iOS 16.5 | 64 rows",
            "hickman_ios13": "iOS 13.3.1 | 77 rows",
            "hickman_ios14": "iOS 14.3 | 84 rows",
            "jess_ios15": "iOS 15.0.2 | 51 rows",
            "magnet_ios16": "iOS 16.1.1 | 73 rows",
        }
    },
    "icons_screen_visual": {
        "name": "iOS Home Screen Layout - Visual",
        "description": "Rendered image of each home screen page (apps, folders, widgets, dock)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "A PNG is rendered per screen page from SpringBoard/IconState.plist as a visual "
                 "reference. The 'iOS Home Screen Layout' artifact holds the same data in queryable form.",
        "paths": ('**/SpringBoard/IconState.plist',),
        "output_types": "standard",
        "artifact_icon": "layout-grid",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 5 rows",
            "felix23_ios16": "iOS 16.5 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 4 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
        }
    },
    "springboard_wallpaper": {
        "name": "SpringBoard Wallpaper",
        "description": "Legacy wallpaper files and thumbnails stored by SpringBoard",
        "author": "@JamesHabben",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "Legacy cpbitmap wallpaper files are converted to PNG when possible. Image-backed "
                 "wallpapers and thumbnails are checked into the media report as PNG when conversion "
                 "is needed.",
        "paths": (
            '**/SpringBoard/*Background*.cpbitmap',
            '**/SpringBoard/*Background*.jpg',
            '**/SpringBoard/*Background*.jpeg',
            '**/SpringBoard/*Background*.png',
            '**/SpringBoard/*Background*.heic',
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
        }
    },
    "posterboard_wallpaper": {
        "name": "PosterBoard Wallpaper",
        "description": "PosterBoard output.layerStack image layer files",
        "author": "@JamesHabben",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "iOS Screens",
        "notes": "PosterBoard output.layerStack image files are reported. HEIC/HEIF image layers "
                 "are converted to PNG for reporting.",
        "paths": (
            '**/output.layerStack/*.heic',
            '**/output.layerStack/*.jpg',
            '**/output.layerStack/*.jpeg',
            '**/output.layerStack/*.png',
        ),
        "output_types": "standard",
        "artifact_icon": "photo"
    }
}

import io
import plistlib
import struct
from pathlib import Path

from packaging import version
from PIL import Image, ImageDraw, ImageFont
from pillow_heif import register_heif_opener

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    check_in_media,
    convert_unix_ts_to_utc,
    logfunc
)

_COLS = 4
_CELL_W = 200
_CELL_H = 70
_PAD = 8
_HEADER = 34
_KIND_COLORS = {'app': '#2d4a7a', 'folder': '#7a5a2d', 'widget': '#2d7a4a', 'stack': '#5a2d7a'}
_CPBITMAP_EXT = '.cpbitmap'
_HEIC_EXTS = {'.heic', '.heif'}
_MAX_CPBITMAP_PIXELS = 50000000


def _font(size):
    for path in ('DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                 '/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf'):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def _find_plist(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('IconState.plist'):
            return file_found
    return ''


def _load(context):
    source_path = _find_plist(context)
    if not source_path:
        return None, ''
    try:
        with open(source_path, 'rb') as fp:
            return plistlib.load(fp), context.get_relative_path(source_path)
    except (plistlib.InvalidFileException, ValueError, OSError) as ex:
        logfunc(f'Failed to read IconState.plist {source_path}: {ex}')
        return None, context.get_relative_path(source_path)


def _iter_items(page):
    """Normalize a single screen page into a list of {kind, name, grid, contents} dicts."""
    items = []
    for entry in page:
        if isinstance(entry, str):
            items.append({'kind': 'app', 'name': entry, 'grid': '', 'contents': []})
        elif isinstance(entry, dict):
            if 'listType' in entry:
                contents = [bundle for sub in entry.get('iconLists', []) for bundle in sub]
                items.append({'kind': 'folder', 'name': entry.get('displayName', ''),
                              'grid': '', 'contents': contents})
            elif 'gridSize' in entry:
                grid = entry.get('gridSize', '')
                if 'elementType' in entry:
                    name = (entry.get('widgetIdentifier') if entry.get('elementType') == 'widget'
                            else entry.get('elementType')) or ''
                    items.append({'kind': 'widget', 'name': name, 'grid': grid, 'contents': []})
                elif 'elements' in entry:
                    widgets = [(w.get('widgetIdentifier') if w.get('elementType') == 'widget'
                                else w.get('elementType')) or '' for w in entry.get('elements', [])]
                    items.append({'kind': 'stack', 'name': 'Stack', 'grid': grid, 'contents': widgets})
    return items


def _render_page(title, items):
    """Render a screen page (list of normalized items) to PNG bytes."""
    rows = max(1, (len(items) + _COLS - 1) // _COLS)
    width = _COLS * _CELL_W + _PAD
    height = _HEADER + rows * _CELL_H + _PAD
    img = Image.new('RGB', (width, height), '#1e1e1e')
    draw = ImageDraw.Draw(img)
    draw.text((_PAD, _PAD), title, fill='#ffffff', font=_font(16))

    for i, item in enumerate(items):
        cx = (i % _COLS) * _CELL_W + _PAD
        cy = _HEADER + (i // _COLS) * _CELL_H
        draw.rectangle([cx, cy, cx + _CELL_W - _PAD, cy + _CELL_H - _PAD],
                       fill=_KIND_COLORS.get(item['kind'], '#444444'), outline='#888888')
        if item['kind'] == 'app':
            header = item['name']
            subs = []
        elif item['kind'] == 'folder':
            header = f"[Folder] {item['name']}"
            subs = item['contents']
        elif item['kind'] == 'widget':
            header = f"[Widget] {item['grid']}".strip()
            subs = [item['name']]
        else:
            header = f"[Stack] {item['grid']}".strip()
            subs = item['contents']
        draw.text((cx + 4, cy + 4), header[:30], fill='#ffffff', font=_font(11))
        sy = cy + 22
        for sub in subs[:4]:
            draw.text((cx + 6, sy), str(sub)[:32], fill='#cfcfcf', font=_font(9))
            sy += 11

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def _path_name(path):
    return str(path).replace('\\', '/').rstrip('/').split('/')[-1]


def _springboard_variant(name):
    lowered = name.lower()
    variants = []
    if 'lock' in lowered:
        variants.append('Lock Screen')
    if 'home' in lowered:
        variants.append('Home Screen')
    if 'original' in lowered:
        variants.append('Original')
    if 'thumbnail' in lowered:
        variants.append('Thumbnail')
    if 'dark' in lowered:
        variants.append('Dark')
    return ', '.join(variants) if variants else 'Unspecified'


def _posterboard_layer_name(name):
    return Path(name).stem.replace('_', ' ').replace('-', ' ')


def _file_timestamps(context, file_found):
    file_info = context.get_seeker().file_infos.get(file_found)
    if not file_info:
        return '', ''

    return (
        convert_unix_ts_to_utc(file_info.creation_date),
        convert_unix_ts_to_utc(file_info.modification_date)
    )


def _cpbitmap_alignment_candidates(ios_version):
    if not ios_version:
        return (16, 8, 4)

    try:
        parsed_version = version.parse(ios_version)
    except version.InvalidVersion:
        return (16, 8, 4)

    if parsed_version < version.parse('10'):
        preferred = 4
    elif parsed_version < version.parse('12'):
        preferred = 8
    else:
        preferred = 16

    return (preferred,) + tuple(offset for offset in (16, 8, 4) if offset != preferred)


def _convert_cpbitmap_to_png(cpbitmap_path, png_path, ios_version=''):
    cpbitmap = Path(cpbitmap_path).read_bytes()
    if len(cpbitmap) < 20:
        raise ValueError('cpbitmap is too small to contain dimensions')

    width = struct.unpack_from('<i', cpbitmap, len(cpbitmap) - 20)[0]
    height = struct.unpack_from('<i', cpbitmap, len(cpbitmap) - 16)[0]
    if width <= 0 or height <= 0 or width * height > _MAX_CPBITMAP_PIXELS:
        raise ValueError(f'invalid cpbitmap dimensions: {width}x{height}')

    for alignment in _cpbitmap_alignment_candidates(ios_version):
        line_width = ((width + alignment - 1) // alignment) * alignment
        required_size = line_width * height * 4
        if required_size > len(cpbitmap):
            continue

        image = Image.frombytes('RGBA', (width, height), cpbitmap[:required_size],
                                'raw', 'BGRA', line_width * 4, 1)
        image.save(png_path, 'PNG')
        return alignment

    raise ValueError(f'cpbitmap data is too small for dimensions: {width}x{height}')


def _convert_heic_to_png(heic_path, png_path):
    register_heif_opener()
    with Image.open(heic_path) as image:
        image.convert('RGBA').save(png_path, 'PNG')


@artifact_processor
def icons_screen(context):
    """ See artifact description """
    data_headers = ('Screen', 'Type', 'Name', 'Folder', 'Grid Size')
    data_list = []
    plist, source_path = _load(context)
    if not plist:
        return data_headers, data_list, source_path

    for page_index, page in enumerate(plist.get('iconLists', [])):
        screen = f'Page {page_index}'
        for item in _iter_items(page):
            if item['kind'] == 'app':
                data_list.append((screen, 'App', item['name'], '', ''))
            elif item['kind'] == 'folder':
                data_list.append((screen, 'Folder', item['name'], '', f"{len(item['contents'])} apps"))
                for bundle in item['contents']:
                    data_list.append((screen, 'App', bundle, item['name'], ''))
            elif item['kind'] == 'widget':
                data_list.append((screen, 'Widget', item['name'], '', item['grid']))
            else:
                data_list.append((screen, 'Stack', ', '.join(item['contents']), '', item['grid']))

    for bundle in plist.get('buttonBar', []):
        data_list.append(('Dock', 'App', bundle, '', ''))

    return data_headers, data_list, source_path


@artifact_processor
def icons_screen_visual(context):
    """ See artifact description """
    data_headers = ('Screen', ('Layout', 'media'))
    data_list = []
    plist, source_path = _load(context)
    if not plist:
        return data_headers, data_list, source_path

    pages = list(enumerate(plist.get('iconLists', [])))
    dock = plist.get('buttonBar', [])
    if dock:
        pages.append(('Dock', [b for b in dock if isinstance(b, str)]))

    for label, page in pages:
        title = f'Screen {label}' if isinstance(label, int) else label
        try:
            png = _render_page(title, _iter_items(page))
            media_ref = check_in_embedded_media(source_path, png, f'home_screen_{label}.png',
                                                force_type='image/png', force_extension='png')
        except (OSError, ValueError) as ex:
            logfunc(f'Failed to render home screen {label}: {ex}')
            media_ref = None
        data_list.append((title, media_ref))

    return data_headers, data_list, source_path


@artifact_processor
def springboard_wallpaper(context):
    """ See artifact description """
    data_headers = (
        ('Wallpaper', 'media'),
        'Variant',
        'Filename',
        'Status',
        ('File Created', 'datetime'),
        ('File Modified', 'datetime'),
        'Source Path',
    )
    data_list = []
    ios_version = context.get_installed_os_version()

    for file_found in context.get_files_found():
        file_found = str(file_found)
        source_path = context.get_relative_path(file_found)
        filename = _path_name(file_found)
        suffix = Path(filename).suffix.lower()
        variant = _springboard_variant(filename)
        created_at, modified_at = _file_timestamps(context, file_found)
        media_ref = None

        if suffix == _CPBITMAP_EXT:
            png_path = Path(file_found).with_suffix('.png')
            try:
                alignment = _convert_cpbitmap_to_png(file_found, png_path, ios_version)
                media_ref = check_in_media(file_found, filename, png_path,
                                           force_type='image/png', force_extension='png')
                status = f'Converted cpbitmap to PNG (alignment {alignment})'
            except (OSError, ValueError) as ex:
                logfunc(f'Failed to convert cpbitmap wallpaper {file_found}: {ex}')
                status = 'Found, but cpbitmap conversion failed'
        elif suffix in _HEIC_EXTS:
            png_path = Path(file_found).with_suffix('.png')
            try:
                _convert_heic_to_png(file_found, png_path)
                media_ref = check_in_media(file_found, filename, png_path,
                                           force_type='image/png', force_extension='png')
                status = 'Converted HEIC to PNG'
            except (OSError, ValueError) as ex:
                logfunc(f'Failed to convert HEIC wallpaper {file_found}: {ex}')
                status = 'Found, but HEIC conversion failed'
        else:
            try:
                media_ref = check_in_media(file_found, filename)
            except OSError as ex:
                logfunc(f'Failed to check in SpringBoard wallpaper media {file_found}: {ex}')
            status = 'Media checked in' if media_ref else 'Found, but media check-in failed'

        data_list.append((
            media_ref,
            variant,
            filename,
            status,
            created_at,
            modified_at,
            source_path,
        ))

    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def posterboard_wallpaper(context):
    """ See artifact description """
    data_headers = (
        ('Wallpaper', 'media'),
        'Layer Name',
        'Filename',
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
        suffix = Path(filename).suffix.lower()
        layer_name = _posterboard_layer_name(filename)
        created_at, modified_at = _file_timestamps(context, file_found)
        media_ref = None

        if suffix in _HEIC_EXTS:
            png_path = Path(file_found).with_suffix('.png')
            try:
                _convert_heic_to_png(file_found, png_path)
                media_ref = check_in_media(file_found, filename, png_path,
                                           force_type='image/png', force_extension='png')
                status = 'Converted HEIC to PNG'
            except (OSError, ValueError) as ex:
                logfunc(f'Failed to convert HEIC wallpaper {file_found}: {ex}')
                status = 'Found, but HEIC conversion failed'
        else:
            try:
                media_ref = check_in_media(file_found, filename)
            except OSError as ex:
                logfunc(f'Failed to check in PosterBoard wallpaper media {file_found}: {ex}')
            status = 'Media checked in' if media_ref else 'Found, but media check-in failed'

        data_list.append((
            media_ref,
            layer_name,
            filename,
            status,
            created_at,
            modified_at,
            source_path,
        ))

    return data_headers, data_list, 'See Source Path column'
