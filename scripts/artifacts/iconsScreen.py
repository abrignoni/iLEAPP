__artifacts_v2__ = {
    "iconsScreen": {
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
        "artifact_icon": "grid"
    },
    "iconsScreenVisual": {
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
        "artifact_icon": "grid"
    }
}

import io
import plistlib

from PIL import Image, ImageDraw, ImageFont

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc

_COLS = 4
_CELL_W = 200
_CELL_H = 70
_PAD = 8
_HEADER = 34
_KIND_COLORS = {'app': '#2d4a7a', 'folder': '#7a5a2d', 'widget': '#2d7a4a', 'stack': '#5a2d7a'}


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


@artifact_processor
def iconsScreen(context):
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
def iconsScreenVisual(context):
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
