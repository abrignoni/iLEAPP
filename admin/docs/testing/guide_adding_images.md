# Guide: Adding a New Image to the Manifest

This guide outlines the process of adding a new test image to the LEAPP project's image manifest (`admin/image_manifest.json`). The manifest is used to track metadata about publicly available test images (which are typically too large to store in the repository) and allows the `make_test_data.py` script to locate these images on a contributor's local system to generate focused test case data. Accurate image metadata, especially `os_version`, is also helpful for creating targeted test cases for conditional module logic.

## Steps to Add a New Image

1. **Obtain the Test Image**:
   - Acquire a publicly available test image containing sample data for iOS artifacts.
   - Note the source, creation date, and any relevant information about the image.

2. **Extract File Path List**:
   - Extract a list of file paths from the test image.
   - Save this list as a CSV file in the `admin/data/filepath-lists/` directory.
   - Compress the CSV file as a zip archive.

3. **Analyze File Path Patterns**:
   - Run the file path analysis script to generate search pattern results.
   - Review the results in `admin/docs/filepath_results.csv` and `admin/docs/filepath_search_summary.md`.

4. **Update the Image Manifest**:
   - Open the `admin/image_manifest.json` file.
   - Add a new entry to the `"images"` array with the following structure:

```json
{
  "image_name": "unique_image_name",
  "sample_data_key": "corpus_key_used_in_sample_data",
  "description": "Brief description of the image and its contents",
  "published_file": "Image-Filename-As-Published.zip",
  "file_path_list": "admin/data/filepath-lists/your-image-name.csv.zip",
  "download_url": "https://example.com/download/link/for/image",
  "author": {
    "name": "Author Name",
    "organization": "Organization Name (if applicable)"
  },
  "image_info": {
    "creation_date": "YYYY-MM-DD",
    "os_name": "iPhone OS",
    "os_version": "iOS X.X.X",
    "device_model": "iPhone Model (if known)",
    "extraction_method": "Full Filesystem / Logical / etc.",
    "extraction_tool": "Tool used for extraction"
  },
  "file_info": {
    "file_count": 123456,
    "md5_hash": "md5_hash_of_the_image_file"
  },
  "notes": "Any additional notes or comments about the image"
}
```

   - `sample_data_key` is the corpus key artifacts cite in `sample_data` and in
     [public_corpus_images.md](public_corpus_images.md). For new entries make it the same
     string as `image_name`.
   - `published_file` is the exact filename the publisher distributes, with no path.
   - Manifest entries carry no machine-specific paths. Older entries still list
     `local_image_paths` and those keep working, but do not add that field to new entries.

5. **Record Your Local Path**:
   - Machine-specific locations live in `admin/image_manifest.local.json`, which is
     git-ignored. Map the image directly, or name folders to search for `published_file`:

```json
{
  "image_paths": {
    "unique_image_name": "~/phone-images/Image-Filename-As-Published.zip"
  },
  "search_roots": [
    "~/phone-images"
  ]
}
```

   - `image_paths` keys can be either the `image_name` or the `sample_data_key`.
   - A direct `image_paths` mapping is checked first and is the reliable option when your
     copy is renamed or is the un-nested inner image rather than the published wrapper.

6. **Commit Changes**:
   - Commit the updated `image_manifest.json` file to the repository.
   - Include the new file path list zip file in your commit.

## Best Practices

- Use concise and unique names for the `image_name` field.
- Provide as much detail as possible in the `description` and `notes` fields.

## Troubleshooting

- If the `make_test_data.py` script fails to locate your image, check your mapping in `admin/image_manifest.local.json`, and that the mapped file exists.
- Ensure that the `file_path_list` points to a valid CSV zip file in the correct directory.

