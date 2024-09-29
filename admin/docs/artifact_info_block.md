# Artifact Info Block Structure

The artifact info block is defined as a dictionary named `__artifacts_v2__` at the top of the artifact script. It contains key information about the artifact. Here's the structure:

```python
__artifacts_v2__ = {
    "function_name": {
        "name": "Human-readable name of the artifact",
        "description": "Brief description of what the artifact does",
        "author": "@AuthorUsername",
        "version": "X.Y",
        "date": "YYYY-MM-DD",
        "requirements": "Any specific requirements, or 'none'",
        "category": "Category of the artifact",
        "notes": "Additional notes, if any",
        "paths": ('Path/to/artifact/files',),
        "output_types": "Output types, often 'all'"
    }
}
```

- `function_name`: The name of the function that processes this artifact. This should match exactly with the function name in the script.
- `name`: A human-readable name for the artifact as it will be displayed in the output files
- `description`: A brief explanation of what the artifact extracts or analyzes
- `author`: The name and/or username of the module's author
- `version`: The current version of the module script
- `date`: The date of the latest update in YYYY-MM-DD format
- `requirements`: Any specific requirements for the artifact, or "none" if there are no special requirements
- `category`: The category the artifact belongs to
- `notes`: Any additional information about the artifact (can be an empty string)
- `paths`: A tuple containing one or more file paths (with wildcards if needed) where the artifact data can be found
- `output_types`: A list of strings or the string 'all' specifying the types of output the artifact produces. Options are:
    - `["html", "tsv", "timeline", "lava"]`: A list containing any combination of these values
    - `"all"`: Generates all available output types
    - Individual options:
        - `"html"`: Generates HTML output
        - `"tsv"`: Generates TSV (Tab-Separated Values) output
        - `"timeline"`: Generates timeline output
        - `"lava"`: Generates output for LAVA (a specific data processing format)

This info block provides essential metadata about the artifact and is used by the artifact processor to handle the artifact correctly. The plugin loader will attach this information to the corresponding function, making it accessible via the function's globals.

Note: The key in the `__artifacts_v2__` dictionary must exactly match the name of the function that processes the artifact. This ensures that the artifact processor can correctly associate the artifact information with the processing function.