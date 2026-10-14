"""
Image List Test
"""
__artifacts_v2__ = {
    "image_list": {
        "name": "Image List Test",
        "category": "Test",
        "notes": "Processes a test set of images from a manifest.json",
        "paths": (
            "**/manifest.json",
            "**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.webp",
            "**/*.avif", "**/*.heic", "**/*.jp2", "**/*.qoi", "**/*.gif",
            "**/*.svg", "**/*.jxl"
        ),
        "output_types": ["html", "tsv", "lava"],
    },
    "media_path_probe": {
        "name": "Media Path Probe",
        "description": (
            "Emits one generated PNG so a test runner can stamp "
            "report/media and _HTML/media with different banners."
        ),
        "author": "@jameshabben",
        "creation_date": "2026-09-19",
        "last_update_date": "2026-09-19",
        "category": "Test",
        "notes": (
            "The test runner unlinks the HTML copy if it shares an inode "
            "with the canonical file, then paints report/media on one copy "
            "and _HTML/media on the other. Open this table in LAVA: the "
            "banner on the image is the folder that was actually read."
        ),
        "paths": ("**/manifest.json",),
        "output_types": ["html", "tsv", "lava"],
    }
}

import json
from io import BytesIO

from PIL import Image, ImageDraw

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    check_in_media,
    logfunc,
)


def _probe_png_bytes():
    img = Image.new("RGB", (800, 400), (40, 40, 50))
    draw = ImageDraw.Draw(img)
    draw.text((40, 160), "LAVA media path probe (unstamped)", fill=(220, 220, 220))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@artifact_processor
def image_list(context):
    """
    Processes a test set of images from a manifest.json
    """

    data_list = []
    source_path = ""
    seeker = context.get_seeker()

    manifest_files = [f for f in context.get_files_found() if f.endswith('manifest.json')]
    for file_found in manifest_files:
        source_path = file_found
        with open(file_found, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        for entry in manifest:
            image_filename = entry.get('file')
            mime_type = entry.get('mime')
            notes = entry.get('notes', '')

            # Search for the actual image file
            found_images = seeker.search(f"**/{image_filename}")
            if found_images:
                image_path = found_images[0]

                # Get first 8 bytes in hex
                hex_bytes = ""
                try:
                    with open(image_path, 'rb') as img_f:
                        header = img_f.read(8)
                        hex_bytes = ' '.join(f'{b:02X}' for b in header)
                except IOError as e:
                    logfunc(f"Could not read header for {image_filename}: {str(e)}")

                media_ref_id = check_in_media(image_path, name=image_filename)

                data_list.append((
                    image_filename,
                    mime_type,
                    hex_bytes,
                    media_ref_id,
                    notes
                ))
            else:
                logfunc(f"Could not find image file: {image_filename}")

    data_headers = ('Filename', 'MIME Type', 'First 8 Bytes (Hex)', ('Image', 'media'), 'Notes')
    return data_headers, data_list, source_path


@artifact_processor
def media_path_probe(context):
    """
    Register one generated PNG for the LAVA media-path probe.
    """
    data_list = []
    source_path = ""
    manifests = [f for f in context.get_files_found() if f.endswith("manifest.json")]
    if not manifests:
        logfunc("media_path_probe: no manifest.json; skipping")
    else:
        source_path = manifests[0]
        media_ref_id = check_in_embedded_media(
            source_path,
            _probe_png_bytes(),
            name="media_path_probe.png",
            force_type="image/png",
            force_extension="png",
        )
        data_list.append((
            media_ref_id,
            "Runner stamps report/media vs _HTML/media after extract. "
            "The banner on this image in LAVA is the folder that was read.",
        ))

    data_headers = (('Image', 'media'), 'Notes')
    return data_headers, data_list, source_path
