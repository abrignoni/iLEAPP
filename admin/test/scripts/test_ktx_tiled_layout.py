"""KTX_reader.untile_astc_4x4: the tiled block layout of AAPL textures seen on iOS 26 and 27."""

import unittest

from scripts.ktx.ios_ktx2png import ASTC_BLOCK_BYTES, TILE_BLOCKS, KTX_reader


def _morton(x, y):
    value = 0
    for bit in range(5):
        value |= ((x >> bit) & 1) << (2 * bit) | ((y >> bit) & 1) << (2 * bit + 1)
    return value


def _block(n):
    return n.to_bytes(4, 'little') * 4


def _reader(width, height, head_words=(), image_scale=None):
    reader = KTX_reader(image_scale=image_scale)
    reader.pixelWidth = width
    reader.pixelHeight = height
    reader.aapl_head_words = head_words
    return reader


def _tile(width, height, trailing_blocks=1, swapped=False):
    '''Lay raster blocks 0..n-1 out the way the tiled iOS 26 and 27 files hold them.
    swapped puts y in the even bits, the order measured on a 2x device.'''
    blocks_x, blocks_y = -(-width // 4), -(-height // 4)
    tiles_x = -(-blocks_x // TILE_BLOCKS)
    tiles_y = -(-blocks_y // TILE_BLOCKS)
    out = bytearray((tiles_x * tiles_y * TILE_BLOCKS * TILE_BLOCKS + trailing_blocks) * ASTC_BLOCK_BYTES)
    for y in range(blocks_y):
        for x in range(blocks_x):
            index = ((y // TILE_BLOCKS) * tiles_x + x // TILE_BLOCKS) * TILE_BLOCKS * TILE_BLOCKS \
                + (_morton(y % TILE_BLOCKS, x % TILE_BLOCKS) if swapped
                   else _morton(x % TILE_BLOCKS, y % TILE_BLOCKS))
            out[index * ASTC_BLOCK_BYTES:(index + 1) * ASTC_BLOCK_BYTES] = _block(y * blocks_x + x)
    return bytes(out)


def _raster(width, height):
    count = -(-width // 4) * -(-height // 4)
    return b''.join(_block(n) for n in range(count))


class UntileTests(unittest.TestCase):

    def test_padded_tiled_texture_is_returned_in_raster_order(self):
        # 1170x2532 is the size of most snapshots in the iOS 27.2 extraction tested here:
        # 293x633 blocks on a 320x640 block surface, plus one block.
        reader = _reader(1170, 2532)
        self.assertEqual(reader.untile_astc_4x4(_tile(1170, 2532)), _raster(1170, 2532))
        self.assertTrue(reader.is_tiled)

    def test_landscape_texture(self):
        reader = _reader(2532, 1170)
        self.assertEqual(reader.untile_astc_4x4(_tile(2532, 1170)), _raster(2532, 1170))

    def test_linear_texture_is_unchanged(self):
        data = _raster(1170, 2532)
        reader = _reader(1170, 2532, head_words=(0,) * 21)
        self.assertIs(reader.untile_astc_4x4(data), data)
        self.assertFalse(reader.is_tiled)

    def test_tile_aligned_size_uses_head_word_12(self):
        # 512x256 px is whole tiles, so the block count cannot tell the layouts apart.
        tiled = _tile(512, 256, trailing_blocks=0)
        linear = _raster(512, 256)
        flagged = (0,) * 12 + (1,) + (0,) * 8
        self.assertEqual(_reader(512, 256, flagged).untile_astc_4x4(tiled), linear)
        self.assertIs(_reader(512, 256, (0,) * 21).untile_astc_4x4(linear), linear)

    def test_scale_2_uses_swapped_bit_order(self):
        # 828x1792 is the size of most snapshots on the 2x device tested here.
        swapped = _tile(828, 1792, swapped=True)
        self.assertEqual(_reader(828, 1792, image_scale=2).untile_astc_4x4(swapped),
                         _raster(828, 1792))
        self.assertNotEqual(_reader(828, 1792).untile_astc_4x4(swapped), _raster(828, 1792))

    def test_scale_3_and_unknown_keep_the_default_order(self):
        tiled = _tile(1170, 2532)
        for scale in (None, 3):
            self.assertEqual(_reader(1170, 2532, image_scale=scale).untile_astc_4x4(tiled),
                             _raster(1170, 2532))

    def test_scale_does_not_touch_linear_data(self):
        data = _raster(828, 1792)
        self.assertIs(_reader(828, 1792, (0,) * 21, image_scale=2).untile_astc_4x4(data), data)

    def test_short_data_is_left_alone(self):
        data = _raster(1170, 2532)[:-ASTC_BLOCK_BYTES]
        self.assertIs(_reader(1170, 2532).untile_astc_4x4(data), data)


class ScaleFromNameTests(unittest.TestCase):

    def test_scale_is_read_from_the_file_name_only(self):
        from scripts.artifacts.appSnapshots import _image_scale_from_name
        self.assertEqual(_image_scale_from_name('/a/Snapshots/x/ABC@2x.ktx'), 2)
        self.assertEqual(_image_scale_from_name('/a/Snapshots/x/downscaled/ABC@3x.KTX'), 3)
        self.assertIsNone(_image_scale_from_name('/case@2x.ktx/Snapshots/x/ABC.ktx'))
        self.assertIsNone(_image_scale_from_name('/a/Snapshots/x/ABC.jpeg'))
        self.assertEqual(_image_scale_from_name('C:\\case\\Snapshots\\x\\ABC@2x.ktx'), 2)

    def test_renamed_staged_copy_takes_the_scale_from_the_source_name(self):
        # Two evidence paths differing only in case are staged as name~case-<tag>.ktx.
        from types import SimpleNamespace
        from scripts.artifacts.appSnapshots import _image_scale_for
        staged = '/report/data/var/Snapshots/x/ABC@2x~case-1a2b3c4d.ktx'
        seeker = SimpleNamespace(file_infos={
            staged: SimpleNamespace(source_path='var/Snapshots/x/ABC@2x.ktx')})
        self.assertEqual(_image_scale_for(staged, seeker), 2)
        self.assertIsNone(_image_scale_for(staged, None))
        self.assertEqual(_image_scale_for('/report/data/x/DEF@3x.ktx', seeker), 3)


if __name__ == '__main__':
    unittest.main()
