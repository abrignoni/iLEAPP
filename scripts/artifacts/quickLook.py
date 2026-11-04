__artifacts_v2__ = {
    "quickLook": {
        "name": "iCloud Quick Look",
        "description": "Entries from the Quick Look cloudthumbnails.db cache: the last seen path and size of each thumbnails row as stored, with its last-hit date read as Unix seconds. A cache entry does not establish that the file was viewed.",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "iCloud Quick Look",
        "notes": "On iOS 12 test images the database sits under Library/Application Support/Quick Look/; "
                 "on newer test images it sits under "
                 "Library/Caches/com.apple.QuickLook.thumbnailcache/ "
                 "with the main file a 4 KB shell whose thumbnails table and rows live entirely in the "
                 "-wal sidecar, so the -wal and -shm files must be collected with the database."
                 " Which of the two locations each image in sample_data used is not recorded here.",
        "paths": ('*/Quick Look/cloudthumbnails.db*',
                  '*/Library/Caches/com.apple.QuickLook.thumbnailcache/cloudthumbnails.db*'),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    },
    "quickLookThumbnails": {
        "name": "Quick Look Thumbnails",
        "description": "Thumbnails in the Quick Look thumbnail cache, rendered, with the cache's last hit "
                       "time and hit count and the generator, extension, size and date its version record "
                       "holds for each file.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "iCloud Quick Look",
        "notes": "Reads the thumbnails, basic_files and provider_files tables of index.sqlite, with its "
                 "-wal, and the bitmaps in thumbnails.data, in each "
                 "Library/Caches/com.apple.QuickLook.thumbnailcache folder; an index is read only against "
                 "the thumbnails.data in its own folder. On the tested images that folder existed only "
                 "under mobile/Library/Caches. One row is reported per thumbnails row. These tables hold "
                 "no file name or path. When a thumbnails.file_id has its top bit set, File ID is that "
                 "value with the bit cleared, which named a basic_files row (its fileId) for all 2,901 "
                 "such thumbnails on the tested images. When the top bit is clear, file_id named an "
                 "existing provider_files rowid on all 93 such thumbnails, and File Provider and File "
                 "Provider Item ID are that row's fileProviderId and itemId; this join is a pattern in "
                 "the data, not a documented format. On iphone14plus_ios18 one of them was byte-identical "
                 "to the thumbnail of a basic_files record with the same Extension (e) and Version Size "
                 "(s). Version Date (m), Extension (e), Version Size (s), Generator (g) and Version (v, "
                 "as stored) are the m, e, s, g and v values of the QLThumbnailVersion keyed archive in "
                 "that record's version column, named by the archive's keys, with m read as an NSDate "
                 "(seconds since 2001-01-01 UTC); DLEAPP's macOS QuickLook Thumbnails artifact matched m "
                 "and s to the file's modification time and size on a macOS 11 image, which was not "
                 "tested on iOS. Last Hit is last_hit_date read as seconds since 2001-01-01 UTC, and it "
                 "was on or after Version Date (m) on 2,993 of the 2,994 tested rows; what a hit is, and "
                 "so what Last Hit and Hit Count (as stored) record, is not established. Generator was "
                 "com.apple.UserNotificationsUIKit.ThumbnailProvider on 2,596 of the 2,994 rows; what "
                 "that generator thumbnails is not established. Thumbnail is the bitmap at "
                 "bitmapdata_location, bitmapdata_length bytes long, in thumbnails.data, written out as a "
                 "PNG. Its layout is read from the bitmapFormat keyed archive (w, h, bpc, bpp, bpr and i) "
                 "or, in the older thumbnails table of ctf2020_ios12, hickman_ios13 and hickman_ios14, "
                 "from the bitspercomponent, bitsperpixel, bytesperrow and bitmapinfo columns. i and "
                 "bitmapinfo are read as a CGBitmapInfo value using Apple's CoreGraphics CGImage.h (macOS "
                 "27.0 SDK): the CGImageAlphaInfo in the low five bits, the component type in bit 8 and "
                 "the byte order in bits 12 to 14. Integer layouts of 8 bits per component in 32-bit "
                 "pixels and 16 bits per component in 64-bit pixels are rendered, with premultiplied "
                 "colour divided back out by alpha; a float layout, any other layout, and a bitmap that "
                 "does not fit its stated size or thumbnails.data are not rendered and the run log counts "
                 "them (1 float bitmap on abe_ios16). The colour space named with the layout is not "
                 "applied: on the tested images it was sRGB, Display P3, extended sRGB, an embedded "
                 "profile, or, on 58 rows of hc_ios26, an integer whose meaning is not established, and "
                 "values are written to the PNG without colour conversion. On the tested images the 2,954 "
                 "rendered thumbnails in layouts Pillow's raw decoders read (bitmap info 1, 6 and 0x2002) "
                 "matched Pillow's decode within one level per channel, and the other 39 (16 bits per "
                 "component, or bitmap info 2) matched an independent decode within one level per "
                 "channel. Not reported: basic_files and provider_files records with no thumbnails row, "
                 "which hold no image and which the run log counts (1,724 on abe_ios16, for example), the "
                 "missing_remote_thumbnails, preferences and reserved_buffer tables, basic_files.fsid, "
                 "the archive's i and vi keys, and the other thumbnails columns (icon_mode, flavor, "
                 "content_rect, badge_type, the plistbuffer, and on newer tables icon_variant, "
                 "interpolation and externalGeneratorDataHash). cloudthumbnails.db in the same folder is "
                 "read by the iCloud Quick Look artifact.",
        "paths": ('*/Library/Caches/com.apple.QuickLook.thumbnailcache/index.sqlite*',
                  '*/Library/Caches/com.apple.QuickLook.thumbnailcache/thumbnails.data'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 667 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 10 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 371 rows",
            "felix23_ios16": "iOS 16.5 | 36 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 37 rows",
            "hc_ios18_7": "iOS 18.7.8 | 15 rows",
            "hc_ios26": "iOS 26.5.2 | 58 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 73 rows",
            "hickman_ios13": "iOS 13.3.1 | 21 rows",
            "hickman_ios14": "iOS 14.3 | 180 rows",
            "hickman_ios15": "iOS 15.3.1 | 243 rows",
            "iphone11_ios17": "iOS 17.3 | 408 rows",
            "iphone14plus_ios18": "iOS 18.0 | 26 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 15 rows",
            "jess_ios15": "iOS 15.0.2 | 26 rows",
            "magnet_ios16": "iOS 16.1.1 | 34 rows",
            "otto_ios17": "iOS 17.5.1 | 771 rows",
        },
    }
}

import os
import plistlib
import struct
import zlib
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, does_table_exist_in_db, \
    get_sqlite_db_records, logfunc

_MAC_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
# thumbnails.file_id is basic_files.fileId with the top bit of the 64-bit value set.
_ID_MASK = (1 << 63) - 1
# CGImage.h: CGImageAlphaInfo in the low five bits of the bitmap info, the component type in
# bit 8 (float when set), the byte order in bits 12 to 14 and the pixel format in bits 16 to 19.
# Component positions for each alpha value read here; X is an ignored byte.
_ALPHA_ORDER = {1: 'RGBA', 2: 'ARGB', 3: 'RGBA', 4: 'ARGB', 5: 'RGBX', 6: 'XRGB'}
_PREMULTIPLIED = {1, 2}
_ORDER_DEFAULT, _ORDER_16_LITTLE, _ORDER_32_LITTLE, _ORDER_16_BIG, _ORDER_32_BIG = 0, 0x1000, 0x2000, 0x3000, 0x4000


@artifact_processor
def quickLook(context):
    data_headers = (
        ('Last Hit Date', 'datetime'),
        'Last Seen Path',
        'Size')
    data_list = []
    sources = []

    query = '''
    SELECT
        datetime(last_hit_date, 'unixepoch'),
        last_seen_path,
        size
    FROM thumbnails
    '''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('cloudthumbnails.db'):
            continue
        for row in get_sqlite_db_records(file_found, query):
            data_list.append((row[0], row[1], row[2]))
        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _time(value):
    """Seconds since 2001-01-01 UTC as a UTC datetime; blank for no value and for 0."""
    if value is None or value == 0 or isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    try:
        return _MAC_EPOCH + timedelta(seconds=value)
    except (OverflowError, ValueError):
        return ''


def _archive_values(blob):
    """The root object of a keyed archive as {key: value}, dates as UTC datetimes; {} when unreadable."""
    try:
        archive = plistlib.loads(bytes(blob))
        objects = archive['$objects']
        root = objects[archive['$top']['root'].data]
    except (plistlib.InvalidFileException, KeyError, IndexError, TypeError, AttributeError, ValueError):
        return {}
    if not isinstance(root, dict):
        return {}
    if 'NS.keys' in root and 'NS.objects' in root:
        # An NSDictionary root (bitmapFormat): resolve its keys and values.
        keys = [objects[k.data] if isinstance(k, plistlib.UID) and k.data < len(objects) else k
                for k in root['NS.keys']]
        root = dict(zip(keys, root['NS.objects']))
    values = {}
    for key, value in root.items():
        if key == '$class':
            continue
        if isinstance(value, plistlib.UID):
            value = objects[value.data] if value.data < len(objects) else None
        if value == '$null':
            value = None
        if isinstance(value, dict) and 'NS.time' in value:
            value = _time(value['NS.time'])
        values[key] = value
    return values


def _png(width, height, rgba):
    """An RGBA image as PNG bytes, with the standard library."""
    rows = b''.join(b'\x00' + rgba[y * width * 4:(y + 1) * width * 4] for y in range(height))

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    header = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rows, 9))
            + chunk(b'IEND', b''))


def _render(data, layout, location, length):
    """PNG bytes of one thumbnail's bitmap, or None and the reason it is not rendered.

    layout holds w, h, bpc, bpp, bpr and i (the CGBitmapInfo value)."""
    width, height, per_row = layout.get('w'), layout.get('h'), layout.get('bpr')
    bpc, bpp, info = layout.get('bpc'), layout.get('bpp'), layout.get('i')
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in (bpc, bpp, info)):
        return None, 'no bitmap layout'
    alpha, order = info & 0x1F, info & 0x7000
    if info & 0x100 or info & 0xF0000 or alpha not in _ALPHA_ORDER:
        return None, f'a bitmap layout not decoded here (bitmap info {info:#x})'
    if (bpc, bpp) == (8, 32) and order in (_ORDER_DEFAULT, _ORDER_32_BIG, _ORDER_32_LITTLE):
        step = 1
    elif (bpc, bpp) == (16, 64) and order in (_ORDER_DEFAULT, _ORDER_16_BIG, _ORDER_16_LITTLE):
        step = 2
    else:
        return None, f'a bitmap layout not decoded here ({bpc} bits per component, {bpp} per pixel, ' \
                     f'bitmap info {info:#x})'
    if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in (width, height, per_row, length)) \
            or not isinstance(location, int) or location < 0:
        return None, 'no bitmap size or location'
    pixel = 4 * step
    if per_row < width * pixel or length < per_row * (height - 1) + width * pixel or location + length > len(data):
        return None, 'a bitmap that does not fit its stated size or thumbnails.data'
    names = _ALPHA_ORDER[alpha]
    if step == 1 and order == _ORDER_32_LITTLE:
        names = names[::-1]
    # Byte offset of the most significant byte of each component within a pixel.
    high = 0 if step == 1 or order != _ORDER_16_LITTLE else 1
    offset = {name: index * step + high for index, name in enumerate(names)}
    red_at, green_at, blue_at = offset['R'], offset['G'], offset['B']
    alpha_at = offset.get('A')
    pixels = bytearray()
    for y in range(height):
        start = location + y * per_row
        row = data[start:start + width * pixel]
        for x in range(0, width * pixel, pixel):
            red, green, blue = row[x + red_at], row[x + green_at], row[x + blue_at]
            value = 255 if alpha_at is None else row[x + alpha_at]
            if alpha in _PREMULTIPLIED and 0 < value < 255:
                red, green, blue = (min(255, (c * 255 + value // 2) // value) for c in (red, green, blue))
            pixels += bytes((red, green, blue, value))
    return _png(width, height, bytes(pixels)), None


def _layout(row):
    """The bitmap layout of a thumbnails row, from bitmapFormat or, in the older table, its columns."""
    if 'bitmapFormat' in row.keys():
        return _archive_values(row['bitmapFormat']) if row['bitmapFormat'] else {}
    return {'w': row['width'], 'h': row['height'], 'bpc': row['bitspercomponent'], 'bpp': row['bitsperpixel'],
            'bpr': row['bytesperrow'], 'i': row['bitmapinfo']}


def _columns(path, table):
    return {row['name'] for row in get_sqlite_db_records(path, f'PRAGMA table_info("{table}")')}


@artifact_processor
def quickLookThumbnails(context):
    data_headers = (
        ('Last Hit', 'datetime'), ('Version Date (m)', 'datetime'), ('Thumbnail', 'media'),
        'File ID', 'File Provider', 'File Provider Item ID', 'Extension (e)', 'Version Size (s)',
        'Generator (g)', 'Version (v, as stored)', 'Thumbnail Size (as stored)', 'Width', 'Height',
        'Hit Count (as stored)')
    data_list, read = [], []
    indexes = sorted({str(p) for p in context.get_files_found() if os.path.basename(str(p)) == 'index.sqlite'})
    for path in indexes:
        relative = context.get_relative_path(path)
        if not (does_table_exist_in_db(path, 'basic_files') and does_table_exist_in_db(path, 'thumbnails')):
            logfunc(f'Quick Look Thumbnails: no basic_files and thumbnails tables in {relative}')
            continue
        # The bitmaps of this index are in the thumbnails.data of its own folder.
        store = os.path.join(os.path.dirname(path), 'thumbnails.data')
        data = b''
        if os.path.isfile(store):
            with open(store, 'rb') as handle:
                data = handle.read()
        files = {row['fileId']: _archive_values(row['version'])
                 for row in get_sqlite_db_records(path, 'SELECT fileId, version FROM basic_files')}
        providers = {}
        if does_table_exist_in_db(path, 'provider_files'):
            providers = {row['rowid']: (row['fileProviderId'] or '', row['itemId'] or '', _archive_values(row['version']))
                         for row in get_sqlite_db_records(
                             path, 'SELECT rowid, fileProviderId, itemId, version FROM provider_files')}
        layout_columns = ('bitmapFormat',) if 'bitmapFormat' in _columns(path, 'thumbnails') else \
            ('bitspercomponent', 'bitsperpixel', 'bytesperrow', 'bitmapinfo')
        thumbs = get_sqlite_db_records(
            path, f'SELECT file_id, size, hit_count, last_hit_date, width, height, {", ".join(layout_columns)}, '
                  'bitmapdata_location, bitmapdata_length FROM thumbnails ORDER BY last_hit_date, file_id, size')
        skipped, seen_files, seen_providers = {}, set(), set()
        for row in thumbs:
            raw_id = row['file_id']
            file_id, provider, item, version = '', '', '', {}
            if isinstance(raw_id, int) and raw_id < 0:
                file_id = raw_id & _ID_MASK
                seen_files.add(file_id)
                version = files.get(file_id, {})
            elif raw_id in providers:
                seen_providers.add(raw_id)
                provider, item, version = providers[raw_id]
            else:
                file_id = raw_id
            image, reason = _render(data, _layout(row), row['bitmapdata_location'], row['bitmapdata_length'])
            media = ''
            if image:
                size = row['size']
                label = f'_{size:g}' if isinstance(size, (int, float)) and not isinstance(size, bool) else ''
                media = check_in_embedded_media(store, image, name=f'{file_id or item}{label}.png',
                                                force_type='image/png', force_extension='png') or ''
            else:
                skipped[reason] = skipped.get(reason, 0) + 1
            data_list.append((
                _time(row['last_hit_date']), version.get('m') or '', media, file_id, provider, item,
                version.get('e') or '', _blank(version.get('s')), version.get('g') or '',
                _blank(version.get('v')), _blank(row['size']), _blank(row['width']), _blank(row['height']),
                _blank(row['hit_count'])))
        # Version records without a thumbnail hold no image; they are counted, not reported.
        unthumbed = sum(1 for file_id in files if file_id not in seen_files) + \
            sum(1 for rowid in providers if rowid not in seen_providers)
        if unthumbed:
            logfunc(f'Quick Look Thumbnails: {unthumbed} version record(s) in {relative} have no thumbnail '
                    'row and are not reported')
        for reason, count in skipped.items():
            logfunc(f'Quick Look Thumbnails: {count} thumbnail(s) in {relative} not rendered: {reason}')
        read.append(path)
        if data:
            read.append(store)
    return data_headers, data_list, '\n'.join(read)


def _blank(value):
    return '' if value is None else value

