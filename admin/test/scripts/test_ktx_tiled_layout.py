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


def _reader(width, height, head_words=()):
    reader = KTX_reader()
    reader.pixelWidth = width
    reader.pixelHeight = height
    reader.aapl_head_words = head_words
    return reader


def _tile(width, height, trailing_blocks=1):
    '''Lay raster blocks 0..n-1 out the way the tiled iOS 26 and 27 files hold them.'''
    blocks_x, blocks_y = -(-width // 4), -(-height // 4)
    tiles_x = -(-blocks_x // TILE_BLOCKS)
    tiles_y = -(-blocks_y // TILE_BLOCKS)
    out = bytearray((tiles_x * tiles_y * TILE_BLOCKS * TILE_BLOCKS + trailing_blocks) * ASTC_BLOCK_BYTES)
    for y in range(blocks_y):
        for x in range(blocks_x):
            index = ((y // TILE_BLOCKS) * tiles_x + x // TILE_BLOCKS) * TILE_BLOCKS * TILE_BLOCKS \
                + _morton(x % TILE_BLOCKS, y % TILE_BLOCKS)
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

    def test_short_data_is_left_alone(self):
        data = _raster(1170, 2532)[:-ASTC_BLOCK_BYTES]
        self.assertIs(_reader(1170, 2532).untile_astc_4x4(data), data)


if __name__ == '__main__':
    unittest.main()
