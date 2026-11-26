"""KTX_reader.to_image: every pixel comes from its own ASTC block, including at widths and
heights that are not multiples of 4."""

import random
import unittest

from scripts.ktx.ios_ktx2png import KTX_reader


def _void(red, green, blue):
    '''A valid ASTC void-extent block: one solid colour.'''
    def channel(value):
        return (value * 257).to_bytes(2, 'little')
    return bytes.fromhex('fcfdffffffffffff') + channel(red) + channel(green) + channel(blue) + channel(255)


class ToImageTests(unittest.TestCase):

    def _check(self, width, height):
        rng = random.Random(width * 10007 + height)
        blocks_x, blocks_y = -(-width // 4), -(-height // 4)
        colours = [(rng.randrange(256), rng.randrange(256), rng.randrange(256))
                   for _ in range(blocks_x * blocks_y)]
        reader = KTX_reader()
        reader.pixelWidth, reader.pixelHeight = width, height
        image = reader.to_image(b''.join(_void(*c) for c in colours))
        self.assertEqual(image.size, (width, height))
        pixels = image.load()
        wrong = [(x, y) for y in range(height) for x in range(width)
                 if pixels[x, y][:3] != colours[(y // 4) * blocks_x + x // 4]]
        self.assertEqual(wrong, [], f'{len(wrong)} pixels came from the wrong block at {width}x{height}')

    def test_unaligned_width(self):
        self._check(9, 8)
        self._check(345, 163)

    def test_unaligned_height(self):
        self._check(8, 10)

    def test_aligned(self):
        self._check(16, 8)


if __name__ == '__main__':
    unittest.main()
