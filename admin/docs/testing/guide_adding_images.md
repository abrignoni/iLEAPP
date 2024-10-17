# Guide: Adding a New Image to the Manifest

This guide outlines the process of adding a new test image to the LEAPP project's image manifest. The manifest is used to track metadata about publicly available test images and facilitate test data creation.

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
  "description": "Brief description of the image and its contents",
  "local_image_paths": [
    "~/path/to/image/on/your/system.tar.gz",
    "/alternative/path/to/image.zip"
  ],
  "file_path_list": "admin/data/filepath-lists/your-image-name.csv.zip",
  "download_url": "https://example.com/download/link/for/image",
  "author": {
    "name": "Author Name",
    "organization": "Organization Name (if applicable)"
  },
  "image_info": {
    "creation_date": "YYYY-MM-DD",
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

5. **Verify Local Paths**:
   - Ensure that at least one of the `local_image_paths` exists on your system.
   - Add multiple paths to accommodate different contributor environments.

6. **Commit Changes**:
   - Commit the updated `image_manifest.json` file to the repository.
   - Include the new file path list zip file in your commit.

## Best Practices

- Use concise and unique names for the `image_name` field.
- Provide as much detail as possible in the `description` and `notes` fields.

## Troubleshooting

- If the `make_test_data.py` script fails to locate your image, check that at least one of the `local_image_paths` is correct for your system.
- Ensure that the `file_path_list` points to a valid CSV zip file in the correct directory.

