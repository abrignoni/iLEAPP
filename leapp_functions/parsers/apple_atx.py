"""Parser and best-effort decoder for Apple ATX texture archives.

The public API is intentionally small and result-oriented so artifacts can use
it similarly to Crush parser helpers: feed bytes in, receive parsed metadata,
decoded output when possible, and warnings instead of surprise exceptions for
expected format drift.

Some ATX files store ASTC blocks in the same 32x32-block macro tiles but differ
in how the Morton-order X/Y bits are interpreted inside each tile. When decoding
raw `astc` chunks, this parser tries both plausible X/Y orientations, decodes
both images, and scores the visible boundaries between 128-pixel macro tiles.
The orientation with the smaller brightness jump at those boundaries is used.
In simpler terms: if one block order leaves a checkerboard/grid artifact and the
other looks smooth, the smoother one wins. This is a heuristic based on observed
iOS PosterBoard samples, not a fully documented Apple format flag.
"""

from __future__ import annotations

import math
import struct
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

AAPL_MAGIC = b"AAPL\r\n\x1a\n"
HEAD_TAG = b"HEAD"
FILL_TAG = b"FILL"
ASTC_TAG = b"astc"
ASTC_UPPER_TAG = b"ASTC"
LZFS_TAG = b"LZFS"
ASTC_4X4_FORMAT = (3, 5)
INFERRED_ASTC_4X4_FORMATS = {(1, 1), (3, 1)}
ASTC_BLOCK_BYTES = 16
ASTC_BLOCK_WIDTH = 4
ASTC_BLOCK_HEIGHT = 4
DEFAULT_MACRO_BLOCKS = 32
MAX_IMAGE_PIXELS = 100_000_000


@dataclass(frozen=True)
class AtxChunk:
    """A parsed AAPL container chunk."""

    tag: str
    offset: int
    size: int
    payload_offset: int


@dataclass(frozen=True)
class AtxHeader:
    """Metadata from the ATX HEAD chunk."""

    flags: int
    width: int
    height: int
    depth: int
    array_layers: int
    mipmap_count: int
    texture_uuid: str
    pixel_format_a: int
    pixel_format_b: int

    @property
    def pixel_format(self) -> str:
        if (self.pixel_format_a, self.pixel_format_b) == ASTC_4X4_FORMAT:
            return "ASTC 4x4"
        if (self.pixel_format_a, self.pixel_format_b) in INFERRED_ASTC_4X4_FORMATS:
            return f"Inferred ASTC 4x4 ({self.pixel_format_a}, {self.pixel_format_b})"
        return f"Unknown ({self.pixel_format_a}, {self.pixel_format_b})"


@dataclass(frozen=True)
class TexturePayload:
    """Texture payload bytes found in an ATX container."""

    kind: str
    data: bytes
    declared_size: int
    compressed: bool


@dataclass(frozen=True)
class DecodedImage:
    """RGBA8 image produced from an ATX texture."""

    width: int
    height: int
    pixels: bytes

    def to_pil(self):
        from PIL import Image

        return Image.frombytes("RGBA", (self.width, self.height), self.pixels)


@dataclass(frozen=True)
class AtxDecodeResult:
    """Parsed ATX metadata plus optional decoded RGBA image."""

    header: AtxHeader | None
    chunks: tuple[AtxChunk, ...]
    payload: TexturePayload | None
    image: DecodedImage | None
    warnings: tuple[str, ...]


class _Reader:
    def __init__(self, data: bytes):
        self.data = data

    def u32(self, offset: int) -> int:
        if offset + 4 > len(self.data):
            raise ValueError("unexpected end of ATX data")
        return struct.unpack_from("<I", self.data, offset)[0]

    def slice(self, offset: int, size: int) -> bytes:
        if offset + size > len(self.data):
            raise ValueError("unexpected end of ATX data")
        return self.data[offset:offset + size]


def is_atx(data: bytes) -> bool:
    return data.startswith(AAPL_MAGIC)


def parse_atx(data: bytes) -> AtxDecodeResult:
    """Parse ATX container metadata without attempting image decode."""

    return decode_atx(data, decode_image=False)


def decode_atx_file(path: str | Path, decode_image: bool = True) -> AtxDecodeResult:
    return decode_atx(Path(path).read_bytes(), decode_image=decode_image)


def decode_atx(data: bytes, decode_image: bool = True) -> AtxDecodeResult:
    """Parse an ATX file and optionally decode supported ASTC 4x4 textures."""

    warnings = []
    if not is_atx(data):
        return AtxDecodeResult(None, tuple(), None, None, ("Not an AAPL ATX container",))

    reader = _Reader(data)
    chunks = tuple(_iter_chunks(reader, warnings))
    header = _parse_header(reader, chunks, warnings)
    payload = _parse_payload(reader, chunks, warnings)
    image = None

    if decode_image and header and payload:
        try:
            image = _decode_image(header, payload, warnings)
        except (ImportError, OSError, ValueError, struct.error) as ex:
            warnings.append(f"ATX image decode failed: {ex}")

    return AtxDecodeResult(header, chunks, payload, image, tuple(warnings))


def _iter_chunks(reader: _Reader, warnings: list[str]) -> Iterable[AtxChunk]:
    offset = len(AAPL_MAGIC)
    while offset + 8 <= len(reader.data):
        try:
            size = reader.u32(offset)
            tag_bytes = reader.slice(offset + 4, 4)
        except ValueError as ex:
            warnings.append(str(ex))
            return

        payload_offset = offset + 8
        end = payload_offset + size
        tag = tag_bytes.decode("ascii", errors="replace")
        if end > len(reader.data):
            warnings.append(f"Chunk {tag} at offset {offset} extends beyond EOF")
            return

        yield AtxChunk(tag, offset, size, payload_offset)
        offset = end

    if offset != len(reader.data):
        warnings.append(f"{len(reader.data) - offset} trailing byte(s) after last complete chunk")


def _parse_header(reader: _Reader, chunks: tuple[AtxChunk, ...], warnings: list[str]) -> AtxHeader | None:
    head = next((chunk for chunk in chunks if chunk.tag == HEAD_TAG.decode("ascii")), None)
    if not head:
        warnings.append("No HEAD chunk found")
        return None

    if head.size < 0x54:
        warnings.append(f"HEAD chunk too small for documented ATX header: {head.size} bytes")
        return None

    payload = reader.slice(head.payload_offset, head.size)
    texture_uuid = str(uuid.UUID(bytes=payload[0x3C:0x4C]))
    return AtxHeader(
        flags=struct.unpack_from("<I", payload, 0x00)[0],
        width=struct.unpack_from("<I", payload, 0x18)[0],
        height=struct.unpack_from("<I", payload, 0x1C)[0],
        depth=struct.unpack_from("<I", payload, 0x20)[0],
        array_layers=struct.unpack_from("<I", payload, 0x28)[0],
        mipmap_count=struct.unpack_from("<I", payload, 0x2C)[0],
        texture_uuid=texture_uuid,
        pixel_format_a=struct.unpack_from("<I", payload, 0x4C)[0],
        pixel_format_b=struct.unpack_from("<I", payload, 0x50)[0],
    )


def _parse_payload(reader: _Reader, chunks: tuple[AtxChunk, ...], warnings: list[str]) -> TexturePayload | None:
    payload_chunk = next((chunk for chunk in chunks if chunk.tag in ("astc", "ASTC", "LZFS")), None)
    if not payload_chunk:
        warnings.append("No astc, ASTC, or LZFS texture payload chunk found")
        return None

    if payload_chunk.size < 4:
        warnings.append(f"{payload_chunk.tag} chunk is too small to include an inner size")
        return None

    declared_size = reader.u32(payload_chunk.payload_offset)
    payload_data = reader.slice(payload_chunk.payload_offset + 4, payload_chunk.size - 4)
    return TexturePayload(
        kind=payload_chunk.tag,
        data=payload_data,
        declared_size=declared_size,
        compressed=payload_chunk.tag == "LZFS",
    )


def _decode_image(header: AtxHeader, payload: TexturePayload, warnings: list[str]) -> DecodedImage:
    if header.width <= 0 or header.height <= 0:
        raise ValueError(f"invalid ATX dimensions: {header.width}x{header.height}")
    if header.width * header.height > MAX_IMAGE_PIXELS:
        raise ValueError(f"ATX image dimensions are too large: {header.width}x{header.height}")
    if header.depth not in (0, 1):
        warnings.append(f"Unexpected ATX depth {header.depth}; attempting 2D decode")
    if header.array_layers not in (0, 1):
        warnings.append(f"Unexpected ATX array layer count {header.array_layers}; attempting first image decode")
    if header.mipmap_count not in (0, 1):
        warnings.append(f"Unexpected ATX mipmap count {header.mipmap_count}; attempting first image decode")
    pixel_format = (header.pixel_format_a, header.pixel_format_b)
    if pixel_format not in {ASTC_4X4_FORMAT, *INFERRED_ASTC_4X4_FORMATS}:
        raise ValueError(f"unsupported ATX pixel format {header.pixel_format}")
    if pixel_format in INFERRED_ASTC_4X4_FORMATS:
        warnings.append(f"ATX pixel format {pixel_format} inferred as ASTC 4x4")

    if payload.compressed:
        astc_data, padded_width, padded_height = _linear_lzfs_payload(header, payload)
        image = _decode_astc_4x4(astc_data, padded_width, padded_height)
    else:
        image, padded_width, padded_height = _decode_macro_tiled_payload(header, payload)

    if (padded_width, padded_height) != (header.width, header.height):
        image = image.crop((0, 0, header.width, header.height))
    return DecodedImage(header.width, header.height, image.convert("RGBA").tobytes())


def _linear_lzfs_payload(header: AtxHeader, payload: TexturePayload) -> tuple[bytes, int, int]:
    import liblzfse

    astc_data = liblzfse.decompress(payload.data)
    padded_width = _round_up(header.width, ASTC_BLOCK_WIDTH)
    padded_height = _round_up(header.height, ASTC_BLOCK_HEIGHT)
    expected = _astc_byte_count(padded_width, padded_height)
    if len(astc_data) < expected:
        raise ValueError(f"LZFS payload decompressed to {len(astc_data)} bytes; expected at least {expected}")
    return astc_data[:expected], padded_width, padded_height


def _macro_tiled_payload(
    header: AtxHeader,
    payload: TexturePayload,
    swap_morton_xy: bool = True,
) -> tuple[bytes, int, int]:
    padded_width = _round_up(header.width, DEFAULT_MACRO_BLOCKS * ASTC_BLOCK_WIDTH)
    padded_height = _round_up(header.height, DEFAULT_MACRO_BLOCKS * ASTC_BLOCK_HEIGHT)
    blocks_w = padded_width // ASTC_BLOCK_WIDTH
    blocks_h = padded_height // ASTC_BLOCK_HEIGHT
    expected = blocks_w * blocks_h * ASTC_BLOCK_BYTES
    if len(payload.data) < expected:
        raise ValueError(f"ASTC payload is {len(payload.data)} bytes; expected at least {expected}")

    linear = bytearray(expected)
    src_offset = 0
    for macro_y in range(0, blocks_h, DEFAULT_MACRO_BLOCKS):
        for macro_x in range(0, blocks_w, DEFAULT_MACRO_BLOCKS):
            for morton_index in range(DEFAULT_MACRO_BLOCKS * DEFAULT_MACRO_BLOCKS):
                local_x, local_y = _decode_morton_5bit(morton_index)
                if swap_morton_xy:
                    local_x, local_y = local_y, local_x
                block_x = macro_x + local_x
                block_y = macro_y + local_y
                dst_offset = (block_y * blocks_w + block_x) * ASTC_BLOCK_BYTES
                linear[dst_offset:dst_offset + ASTC_BLOCK_BYTES] = (
                    payload.data[src_offset:src_offset + ASTC_BLOCK_BYTES]
                )
                src_offset += ASTC_BLOCK_BYTES

    return bytes(linear), padded_width, padded_height


def _decode_macro_tiled_payload(header: AtxHeader, payload: TexturePayload):
    candidates = []
    for swap_morton_xy in (False, True):
        astc_data, padded_width, padded_height = _macro_tiled_payload(
            header,
            payload,
            swap_morton_xy=swap_morton_xy,
        )
        image = _decode_astc_4x4(astc_data, padded_width, padded_height)
        cropped = image.crop((0, 0, header.width, header.height)).convert("RGB")
        candidates.append((
            _grid_seam_score(cropped, DEFAULT_MACRO_BLOCKS * ASTC_BLOCK_WIDTH),
            image,
            padded_width,
            padded_height,
        ))

    _, image, padded_width, padded_height = min(candidates, key=lambda item: item[0])
    return image, padded_width, padded_height


def _decode_astc_4x4(astc_data: bytes, width: int, height: int):
    import astc_decomp_faster  # pylint: disable=unused-import
    from PIL import Image

    return Image.frombytes("RGBA", (width, height), astc_data, "astc", (4, 4, False))


def _grid_seam_score(image, step: int) -> float:
    gray = image.convert("L")
    pixels = gray.load()
    width, height = gray.size
    total = 0
    count = 0

    for x in range(step, width, step):
        for y in range(height):
            total += abs(pixels[x, y] - pixels[x - 1, y])
            count += 1

    for y in range(step, height, step):
        for x in range(width):
            total += abs(pixels[x, y] - pixels[x, y - 1])
            count += 1

    return total / count if count else 0


def _decode_morton_5bit(index: int) -> tuple[int, int]:
    x = 0
    y = 0
    for bit in range(5):
        x |= ((index >> (bit * 2)) & 1) << bit
        y |= ((index >> (bit * 2 + 1)) & 1) << bit
    return x, y


def _round_up(value: int, multiple: int) -> int:
    return int(math.ceil(value / multiple) * multiple)


def _astc_byte_count(width: int, height: int) -> int:
    blocks_w = _round_up(width, ASTC_BLOCK_WIDTH) // ASTC_BLOCK_WIDTH
    blocks_h = _round_up(height, ASTC_BLOCK_HEIGHT) // ASTC_BLOCK_HEIGHT
    return blocks_w * blocks_h * ASTC_BLOCK_BYTES
