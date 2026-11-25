"""Cut-short and damaged KTX textures are refused, not decoded into a full-size picture (#2894, #2890)."""

import io
import os
import struct
import tempfile
import unittest

import liblzfse

from scripts.ktx.ios_ktx2png import ASTC_BLOCK_BYTES, TILE_BLOCKS, KTX_reader

# A valid ASTC void-extent block (one solid colour). Zero-filled blocks decode to transparent
# pixels with no error in this decoder, so a solid colour block is used.
VOID = bytes.fromhex('fcfdffffffffffff') + b'\xff\xff\x00\x00\x00\x00\xff\xff'


def _aapl(width, height, tag, payload, word12=0, declared=None):
    '''An AAPL file: HEAD (21 words) and one payload chunk. declared overrides the chunk size.'''
    head = [0] * 21
    head[4], head[5], head[6], head[7], head[8] = 0x93B0, 0x1908, width, height, 1
    head[12] = word12
    head[19], head[20] = 3, 5
    head_bytes = struct.pack('<21I', *head)
    body = struct.pack('<I', len(payload)) + payload
    size = len(body) if declared is None else declared
    return (b'AAPL\r\n\x1a\n' + struct.pack('<I', len(head_bytes)) + b'HEAD' + head_bytes
            + struct.pack('<I', size) + tag + body)


def _blocks(width, height):
    return -(-width // 4) * -(-height // 4)


def _padded(width, height):
    tiles = -(-(-(-width // 4)) // TILE_BLOCKS) * -(-(-(-height // 4)) // TILE_BLOCKS)
    return tiles * TILE_BLOCKS * TILE_BLOCKS


def _read(blob, image_scale=None):
    reader = KTX_reader(image_scale=image_scale)
    handle = io.BytesIO(blob)
    if not reader.validate_header(handle):
        raise AssertionError('header did not validate')
    return reader.get_uncompressed_texture_data(handle)


class AaplLengthTests(unittest.TestCase):
    W, H = 132, 260   # not whole tiles: 33x65 blocks on a 64x96 block surface

    def test_the_two_measured_lengths_are_accepted(self):
        exact = _blocks(self.W, self.H)
        self.assertEqual(len(_read(_aapl(self.W, self.H, b'astc', VOID * exact))), exact * ASTC_BLOCK_BYTES)
        padded = _padded(self.W, self.H)
        tiled = _read(_aapl(self.W, self.H, b'astc', VOID * (padded + 1), word12=1))
        self.assertEqual(len(tiled), exact * ASTC_BLOCK_BYTES)

    def test_lzfs_linear_is_accepted(self):
        exact = _blocks(self.W, self.H)
        data = _read(_aapl(self.W, self.H, b'LZFS', liblzfse.compress(VOID * exact)))
        self.assertEqual(len(data), exact * ASTC_BLOCK_BYTES)

    def test_short_linear_is_refused(self):
        exact = _blocks(self.W, self.H)
        with self.assertRaises(ValueError):
            _read(_aapl(self.W, self.H, b'astc', VOID * (exact - 1)))

    def test_cut_tiled_between_exact_and_padded_is_refused(self):
        # More blocks than the image needs but fewer than the tiled surface: before this
        # change it was decoded in raster order and came out scrambled.
        padded = _padded(self.W, self.H)
        with self.assertRaises(ValueError):
            _read(_aapl(self.W, self.H, b'astc', VOID * (padded - 100), word12=1))

    def test_partial_block_is_refused(self):
        exact = _blocks(self.W, self.H)
        with self.assertRaises(ValueError):
            _read(_aapl(self.W, self.H, b'astc', VOID * exact + b'\x00' * 7))

    def test_chunk_shorter_than_declared_is_refused(self):
        exact = _blocks(self.W, self.H)
        blob = _aapl(self.W, self.H, b'astc', VOID * exact)
        with self.assertRaises(ValueError):
            _read(blob[:-ASTC_BLOCK_BYTES])

    def test_truncated_lzfs_raises_value_error(self):
        exact = _blocks(self.W, self.H)
        cut = liblzfse.compress(VOID * exact)[:-20]
        with self.assertRaises(ValueError):
            _read(_aapl(self.W, self.H, b'LZFS', cut))


class CallerTests(unittest.TestCase):
    '''The artifacts leave a damaged file out and keep going instead of failing.'''

    def _write(self, blob):
        handle = tempfile.NamedTemporaryFile(suffix='@2x.ktx', delete=False)
        handle.write(blob)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        png = handle.name + '.png'
        self.addCleanup(lambda: os.path.exists(png) and os.remove(png))
        return handle.name, png

    def test_app_snapshots_and_widgets_skip_truncated_lzfs(self):
        from scripts.artifacts import appSnapshots, widgets
        exact = _blocks(64, 64)
        good = _aapl(64, 64, b'LZFS', liblzfse.compress(VOID * exact))
        cut = _aapl(64, 64, b'LZFS', liblzfse.compress(VOID * exact)[:-20])
        for module in (appSnapshots, widgets):
            path, png = self._write(good)
            self.assertTrue(module.save_ktx_to_png_if_valid(path, png))
            path, png = self._write(cut)
            self.assertFalse(module.save_ktx_to_png_if_valid(path, png))

    def test_atx_parser_reports_truncated_lzfs_as_a_warning(self):
        from leapp_functions.parsers.apple_atx import decode_atx
        exact = _blocks(64, 64)
        result = decode_atx(_aapl(64, 64, b'LZFS', liblzfse.compress(VOID * exact)[:-20]))
        self.assertIsNone(result.image)
        self.assertTrue(any('did not decompress' in w for w in result.warnings), result.warnings)


if __name__ == '__main__':
    unittest.main()
