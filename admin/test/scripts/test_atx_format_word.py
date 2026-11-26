"""apple_atx: an ASTC 4x4 texture whose pixel format words are not listed is decoded when
HEAD word 4 (glInternalFormat) is 0x93B0, and still refused when it is not."""

import struct
import unittest

from leapp_functions.parsers.apple_atx import decode_atx

# A valid ASTC void-extent block (one solid colour).
VOID = bytes.fromhex('fcfdffffffffffff') + b'\xff\xff\x00\x00\x00\x00\xff\xff'


def _tiled_atx(width, height, format_words, gl_internal_format):
    '''HEAD (21 words) and a raw astc chunk holding the padded 32x32-block surface plus one block.'''
    head = [0] * 21
    head[4], head[6], head[7], head[8] = gl_internal_format, width, height, 1
    head[11], head[12] = 1, 1
    head[19], head[20] = format_words
    head_bytes = struct.pack('<21I', *head)
    blocks_x, blocks_y = -(-width // 4), -(-height // 4)
    padded = -(-blocks_x // 32) * -(-blocks_y // 32) * 1024
    body = struct.pack('<I', (padded + 1) * 16) + VOID * (padded + 1)
    return (b'AAPL\r\n\x1a\n' + struct.pack('<I', len(head_bytes)) + b'HEAD' + head_bytes
            + struct.pack('<I', len(body)) + b'astc' + body)


class FormatWordTests(unittest.TestCase):

    def test_unlisted_format_with_astc_gl_internal_format_is_decoded(self):
        result = decode_atx(_tiled_atx(132, 260, (1, 5), 0x93B0))
        self.assertIsNotNone(result.image)
        self.assertEqual((result.image.width, result.image.height), (132, 260))
        self.assertTrue(any('glInternalFormat' in w for w in result.warnings), result.warnings)
        self.assertEqual(result.header.pixel_format, 'Unknown (1, 5)')

    def test_unlisted_format_without_it_is_still_refused(self):
        result = decode_atx(_tiled_atx(132, 260, (1, 5), 0x93B1))
        self.assertIsNone(result.image)
        self.assertTrue(any('unsupported ATX pixel format' in w for w in result.warnings), result.warnings)

    def test_listed_format_is_unchanged(self):
        result = decode_atx(_tiled_atx(132, 260, (3, 5), 0))
        self.assertIsNotNone(result.image)
        self.assertFalse(any('glInternalFormat' in w for w in result.warnings), result.warnings)


if __name__ == '__main__':
    unittest.main()
