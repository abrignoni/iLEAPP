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
            "**/*.avif", "**/*.jp2", "**/*.qoi", "**/*.gif", 
            "**/*.svg", "**/*.jxl"
        ),
        "output_types": ["html", "tsv", "lava"],
    }
}

import json

from scripts.ilapfuncs import logfunc, check_in_media, artifact_processor

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
