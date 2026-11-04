"""Pin the bitmap layouts scripts/artifacts/quickLook.py renders from a Quick Look thumbnails.data.

Every pixel is invented: two pixels per bitmap, opaque red and half-transparent green."""
# pylint: disable=protected-access
import io
import struct
import unittest

from PIL import Image

from scripts.artifacts import quickLook

RED, GREEN = (255, 0, 0, 255), (0, 255, 0, 128)


def _pixels(png):
    return list(Image.open(io.BytesIO(png)).convert('RGBA').getdata())


def _bitmap(order, premultiplied=True, depth=8, little=False):
    """Two pixels, components in the given order (letters of RGBAX), as stored."""
    out = b''
    for colour in (RED, GREEN):
        values = dict(zip('RGBA', colour))
        if premultiplied:
            values.update({c: (values[c] * values['A'] + 127) // 255 for c in 'RGB'})
        if 'X' in order:
            values['A'] = 255
        values['X'] = 0
        if depth == 8:
            word = bytes(values[c] for c in order)
            out += word[::-1] if little else word
        else:
            fmt = '<H' if little else '>H'
            out += b''.join(struct.pack(fmt, values[c] * 257) for c in order)
    return out


def _layout(info, depth=8):
    return {'w': 2, 'h': 1, 'bpc': depth, 'bpp': depth * 4, 'bpr': 8 * depth // 8, 'i': info}


class RenderTest(unittest.TestCase):
    def _render(self, data, info, depth=8):
        return quickLook._render(data, _layout(info, depth), 0, len(data))

    def test_rgba_premultiplied(self):
        png, reason = self._render(_bitmap('RGBA'), 1)
        self.assertIsNone(reason)
        self.assertEqual(_pixels(png), [RED, (0, 255, 0, 128)])

    def test_argb_premultiplied(self):
        png, _ = self._render(_bitmap('ARGB'), 2)
        self.assertEqual(_pixels(png), [RED, (0, 255, 0, 128)])

    def test_xrgb_is_opaque(self):
        png, _ = self._render(_bitmap('XRGB', premultiplied=False), 6)
        self.assertEqual(_pixels(png), [RED, (0, 255, 0, 255)])

    def test_32_bit_little_endian_premultiplied_first(self):
        png, _ = self._render(_bitmap('ARGB', little=True), 0x2002)
        self.assertEqual(_pixels(png), [RED, (0, 255, 0, 128)])

    def test_16_bit_components_both_byte_orders(self):
        for info, little in ((1, False), (0x3001, False), (0x1001, True)):
            png, reason = self._render(_bitmap('RGBA', depth=16, little=little), info, depth=16)
            self.assertIsNone(reason, info)
            self.assertEqual(_pixels(png), [RED, (0, 255, 0, 128)], info)

    def test_float_components_are_not_rendered(self):
        png, reason = self._render(b'\x00' * 16, 0x1101, depth=16)
        self.assertIsNone(png)
        self.assertIn('0x1101', reason)

    def test_bitmap_past_the_data_is_not_rendered(self):
        data = _bitmap('RGBA')
        png, reason = quickLook._render(data, _layout(1), 4, len(data))
        self.assertIsNone(png)
        self.assertIn('does not fit', reason)


if __name__ == '__main__':
    unittest.main()
