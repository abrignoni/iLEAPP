"""
    (c) Yogesh Khatri 2020, MIT License

    This library converts ios created KTX files to PNG. These are 
    textures in KTX format, with raw texture  data in compressed ATSC
    format using a block size of 4x4, which is further compressed with
    LZFSE compression.

    iOS created KTX files use Adaptive Scalable Texture Compression 
    (ASTC) as the compressed texture format. Note that a KTX file
    can contain other formats too like PVR and several other 
    variations of ASTC which can't be read by this code. Here we
    only focus on ASTC 4x4, which is the default on iOS. Some apps 
    ship with KTX files that are not of the same type and can't be
    parsed with this code.

    Dependencies
    ------------
    pillow, pyliblzfse, astc_decomp

    Install deps via pip:
      pip3 install pyliblzfse astc_decomp pillow

    Usage
    -----

    python3 ios_ktx2png.py SAMPLE.KTX

    Output will be in the same folder, called SAMPLE.KTX.png

    See main 
"""

import astc_decomp_faster # pylint: disable=unused-import
import liblzfse
import os
import struct
import sys

from PIL import Image

version = 1.0

ASTC_BLOCK_BYTES = 16
TILE_BLOCKS = 32


def _spread_bits(value):
    '''Interleave a 5-bit value with zeros: abcde -> 0a0b0c0d0e.'''
    result = 0
    for bit in range(5):
        result |= ((value >> bit) & 1) << (2 * bit)
    return result


_LZFSE_ERROR = getattr(liblzfse, 'error', ValueError)


def _lzfse_decompress(data):
    '''liblzfse.decompress, raising ValueError instead of liblzfse.error, which is
    neither an OSError nor a ValueError and so got past the callers' handlers.'''
    try:
        return liblzfse.decompress(data)  # pylint: disable=c-extension-no-member
    except _LZFSE_ERROR as ex:
        raise ValueError('LZFSE data did not decompress') from ex


_MORTON_X = tuple(_spread_bits(v) for v in range(TILE_BLOCKS))
_MORTON_Y = tuple(_spread_bits(v) << 1 for v in range(TILE_BLOCKS))

class KTX_reader:

    def __init__(self, image_scale=None):
        '''image_scale: the snapshot's image scale when the caller knows it from
        a recorded source, such as the @2x in a snapshot file name. It chooses
        the bit order of tiled AAPL textures; see untile_astc_4x4.'''
        self.image_scale = image_scale
        # KTX header fields
        self.identifier = b'' # b"«KTX 11»\r\n\x1A\x0A"
        self.endianness = ''
        self.glType = 0
        self.glTypeSize = 0
        self.glFormat = 0
        self.glInternalFormat = 0
        self.glBaseInternalFormat = 0
        self.pixelWidth = 0
        self.pixelHeight = 0
        self.pixelDepth = 0
        self.numberOfArrayElements = 0
        self.numberOfFaces = 0
        self.numberOfMipmapLevels = 0
        self.bytesOfKeyValueData = 0

        self.error_message = ''
        self.is_aapl_file = False
        self.aapl_data_pos = 0
        self.aapl_data_size = 0
        self.aapl_is_compressed = False
        self.aapl_head_words = ()
        self.is_tiled = False

    def validate_header(self, f):
        '''Reads header and validates version

            Arguments
            ---------
            f : file-like object

            Returns
            -------
            Bool : True if file can be parsed else False
        '''
        f.seek(0)
        header = f.read(0x40)
        if len(header) < 0x40:
            self.error_message = 'File too small or can\'t read'
            return False

        self.identifier = header[0:12]
        self.endianness = header[12:16]
        if self.endianness == bytes.fromhex('01020304'):
            endianness = '<'
        else:
            endianness = '>'
        if self.identifier[0:7] == b'\xabKTX 11': # good
            self.glType, \
            self.glTypeSize, \
            self.glFormat, \
            self.glInternalFormat, \
            self.glBaseInternalFormat, \
            self.pixelWidth, \
            self.pixelHeight, \
            self.pixelDepth, \
            self.numberOfArrayElements, \
            self.numberOfFaces, \
            self.numberOfMipmapLevels, \
            self.bytesOfKeyValueData = \
                struct.unpack(endianness + '12I', header[16:64])
            return True
        elif self.identifier[0:4] == b'\xabKTX': # different version
            self.error_message = 'Unknown KTX version'
        elif self.identifier[0:8] == b'AAPL\x0D\x0A\x1A\x0A': # Not KTX, but similar!!
            self.is_aapl_file = True
            return self.parse_aapl_file(f)
        else:
            self.error_message = 'Not a KTX file'
        return False

    def parse_aapl_file(self, f):
        '''Returns True if HEAD was found and header items could be read'''
        ret = False
        next_header_pos = 8
        f.seek(next_header_pos)
        data = f.read(8)
        while data:
            item_size = struct.unpack('<I', data[0:4])[0]
            item_identifier = data[4:8]
            if item_identifier == b'HEAD':
                item_data = f.read(item_size)
                self.aapl_head_words = struct.unpack(f'<{len(item_data) // 4}I',
                                                     item_data[:len(item_data) // 4 * 4])
                # read metadata here...
                _, _, _, _, \
                self.glInternalFormat, \
                self.glBaseInternalFormat, \
                self.pixelWidth, \
                self.pixelHeight, \
                self.pixelDepth, \
                self.numberOfArrayElements, \
                self.numberOfFaces = \
                    struct.unpack('<11I', item_data[0:44])
                ret = True
            elif item_identifier == b'LZFS':
                self.aapl_data_pos = f.tell() + 4
                self.aapl_data_size = item_size - 4
                self.aapl_is_compressed = True
            elif item_identifier in (b'astc', b'ASTC'):
                self.aapl_data_pos = f.tell() + 4
                self.aapl_data_size = item_size - 4
            next_header_pos += 8 + item_size
            f.seek(next_header_pos)
            data = f.read(8)
        return ret

    def get_uncompressed_texture_data(self, f):
        '''Just read the texture data which is lzfse compressed, uncompress and return it.
            Exceptions raised are ValueError, including for LZFSE data that does not
            decompress. The ASTC decoder returned a full-size image with no error
            for short data in the cases tried, so data too short for the image raises
            ValueError here and does not reach it.
        '''
        if self.glInternalFormat == 0x93B0:
            if self.is_aapl_file:
                f.seek(self.aapl_data_pos)
                data = f.read(self.aapl_data_size)
                if len(data) != self.aapl_data_size:
                    raise ValueError(f'AAPL texture chunk holds {len(data)} of the '
                                     f'{self.aapl_data_size} bytes it declares')
                if self.aapl_is_compressed:
                    data = _lzfse_decompress(data)
                return self.untile_astc_4x4(data)
            else:
                f.seek(0x40)
                k_v_data = f.read(self.bytesOfKeyValueData)
                compressed = True if k_v_data.find(b'Compression_APPLE') >= 0 else False
                f.seek(0x40 + self.bytesOfKeyValueData)
                data = f.read()
                if compressed:
                    if data[12:15] == b'bvx':
                        return self._require_whole_image(_lzfse_decompress(data[12:]))
                    else:
                        raise ValueError('Unsupported compression, not lzfse!')
                else:
                    # first 4 bytes is size (which is practically rest of file)
                    return self._require_whole_image(data[4:])
        else:
            raise ValueError('Unsupported Format')
        return b''

    def _require_whole_image(self, data):
        '''Raise ValueError when data holds fewer ASTC 4x4 blocks than the image needs.'''
        needed = -(-self.pixelWidth // 4) * -(-self.pixelHeight // 4) * ASTC_BLOCK_BYTES
        if len(data) < needed:
            raise ValueError(f'KTX texture holds {len(data)} of the {needed} bytes '
                             f'a {self.pixelWidth}x{self.pixelHeight} image needs')
        return data

    def to_image(self, data):
        '''Decode ASTC 4x4 data to an RGBA image of the texture's size.

        The decoder is given the size padded to whole 4x4 blocks and the result is
        cropped. Measured with astc_decomp_faster 1.1.5 and Pillow 12.3.0 on
        solid-colour blocks: given a width that is not a multiple of 4, the pixels
        of each pixel row's last block land in the first columns of the next pixel
        row, so a direct decode at the true size can have wrong pixels in its first
        (4 - width mod 4) columns.
        '''
        width = -(-self.pixelWidth // 4) * 4
        height = -(-self.pixelHeight // 4) * 4
        image = Image.frombytes('RGBA', (width, height), data, 'astc', (4, 4, False))
        if (width, height) == (self.pixelWidth, self.pixelHeight):
            return image
        return image.crop((0, 0, self.pixelWidth, self.pixelHeight))

    def untile_astc_4x4(self, data):
        '''Return ASTC 4x4 blocks in the raster order the decoder expects.

        Some AAPL textures, seen on iOS 26 and 27, hold their blocks in tiles of
        32x32 blocks, Morton (Z) ordered inside each tile with x in the even bits
        and y in the odd bits, on a surface padded to whole tiles, followed by one
        more block. Linear files hold exactly one block per 4x4 pixels in raster
        order and are returned unchanged. The block count decides. HEAD word 12 is
        read when the count equals the padded surface. It was 1 in every tiled file
        and 0 in every linear file observed. It is not documented by Apple.

        Only those lengths are accepted, each with its HEAD word 12: linear at
        exactly one block per 4x4 pixels with word 12 = 0 (or no word 12), tiled at
        exactly the padded surface plus one block, or exactly the padded surface,
        with word 12 = 1. Every AAPL file measured (10,628 in 24 images, iOS 15 to
        27) had one of the first two with that word 12; the third was not seen in
        any file. Anything else, such as a cut-short file,
        raises ValueError, because the decoder would turn it into a full-size
        picture with no error.

        When image_scale is 2, the x and y bits are swapped inside each tile (y in
        the even bits). That order was measured on one 2x device on iOS 26.2.1;
        every tiled file with enough image detail to tell, from the 3x devices
        checked, used the order above. No field with an established meaning was
        found to tell the two apart. HEAD words 15 to 18 differ between the 2x
        device and the 3x devices, and also between 3x devices; their meaning is
        not established, so they are not used and the scale the caller passes
        decides. Whether the order follows the image scale or the GPU is not
        established. With any other scale, or none, the order above is used.
        '''
        blocks_x = -(-self.pixelWidth // 4)
        blocks_y = -(-self.pixelHeight // 4)
        exact = blocks_x * blocks_y
        tiles_x = -(-blocks_x // TILE_BLOCKS)
        tiles_y = -(-blocks_y // TILE_BLOCKS)
        padded = tiles_x * tiles_y * TILE_BLOCKS * TILE_BLOCKS
        count, remainder = divmod(len(data), ASTC_BLOCK_BYTES)
        words = self.aapl_head_words
        word12 = words[12] if len(words) > 12 else 0
        if remainder == 0 and count == exact and word12 == 0:
            return data
        if remainder != 0 or word12 != 1 or count not in (padded, padded + 1):
            raise ValueError(
                f'AAPL texture holds {len(data)} bytes with HEAD word 12 = {word12}, which is '
                f'not an accepted linear ({exact * ASTC_BLOCK_BYTES}, word 12 = 0) or tiled '
                f'({(padded + 1) * ASTC_BLOCK_BYTES}, word 12 = 1) size for '
                f'{self.pixelWidth}x{self.pixelHeight}')
        self.is_tiled = True
        if self.image_scale == 2:
            morton_x, morton_y = _MORTON_Y, _MORTON_X
        else:
            morton_x, morton_y = _MORTON_X, _MORTON_Y
        src = memoryview(data)
        out = bytearray(exact * ASTC_BLOCK_BYTES)
        pos = 0
        for y in range(blocks_y):
            row_base = (y // TILE_BLOCKS) * tiles_x
            y_bits = morton_y[y % TILE_BLOCKS]
            for x in range(blocks_x):
                index = (row_base + x // TILE_BLOCKS) * TILE_BLOCKS * TILE_BLOCKS \
                    + (morton_x[x % TILE_BLOCKS] | y_bits)
                start = index * ASTC_BLOCK_BYTES
                out[pos:pos + ASTC_BLOCK_BYTES] = src[start:start + ASTC_BLOCK_BYTES]
                pos += ASTC_BLOCK_BYTES
        return bytes(out)

    def convert_to_png(self, f, save_to_path):
        # using astc_decomp
        '''Exports KTX as a PNG file
            Arguments
            ---------
            f            : file-like object

            save_to_path : Path of file to save to. If file exists, it will be 
            overwritten.

            Returns
            -------
            Bool : True if file was successfully exported else False
        
            Raises
            ----------
            OSError, ValueError
        '''
        if self.validate_header(f):
            data = self.get_uncompressed_texture_data(f)
            dec_img = self.to_image(data)
            dec_img.save(save_to_path, "PNG")
            return True
        return False
    
    def save_uncompressed_texture(self, f, save_to_path):
        if self.validate_header(f):
            data = self.get_uncompressed_texture_data(f)
            f = open(save_to_path, 'wb')
            f.write(data)
            f.close()
            return True
        return False

def main():
    if sys.argv[0].lower().endswith('.exe'):
        executor = os.path.basename(sys.argv[0])
    else:
        executor = 'python3 ' + os.path.basename(sys.argv[0])
    usage = '\nios_ktx2png ver {0} - converts ios created KTX to PNG\n' + \
            '  (c) 2020 Yogesh Khatri MIT License\n\n' + \
            'Usage:\n-----\n  {1} SAMPLE.KTX\n\n' + \
            'Output will be stored as SAMPLE.KTX.png in same folder\n'
    usage = usage.format(version, executor)
    argc = len(sys.argv)
    if argc < 2:
        print('Exiting.. Not enough arguments. See usage below.')
        print(usage)
        return
    elif ('-h' in sys.argv) or ('--help' in sys.argv):
        print(usage)
        return
    else:
        ktx_path = sys.argv[1]
        with open(ktx_path, 'rb') as f:
            ktx = KTX_reader()
            #ktx.save_uncompressed_texture(f, ktx_path + '.astc') # If you wish to inspect raw data
            try:
                if ktx.convert_to_png(f, ktx_path + '.png'):
                    print(f'Conversion successful!\nOutput is at {ktx_path}.png')
                else:
                    print('Conversion to PNG failed ' + (ktx.error_message if ktx.error_message else ''))
            except (OSError, ValueError, liblzfse.error) as ex:
                print(f'Had an exception - {str(ex)}')

if __name__ == "__main__":
    main()
