# Architectural Decision Record: Media Management System

## Status
Proposed

## Context
We need a centralized system to manage media files (images, videos, audio) across different modules and across xLEAPP and LAVA projects. This system should handle metadata extraction, indexing, and provide a unified interface for modules to interact with media files, while avoiding duplication and maintaining references.

For ongoing discussion and updates related to this ADR, please refer to [Issue #851: Media Manager](https://github.com/abrignoni/iLEAPP/issues/851).

## Decision
We will implement a Media Management Function that acts as a central point for "checking in" media files. This function will:
1. Check if the file has already been added to the database
2. Determine the media type (image, video, audio, etc.) for new files
3. Extract appropriate metadata (resolution, duration, format, etc.) for new files
4. Build and maintain a central media index for Lava
5. Record references to media items from different modules and artifacts
6. Return a MediaReference object to the calling module

## Consequences
Positive:
- Centralized media management improves consistency and reduces duplication
- Pre-extracted metadata enables rich features like hover-over previews and advanced searching
- Modules can easily reference media without handling low-level details
- Automatic tracking of which modules and artifacts reference each media item

Considerations:
- Need to implement efficient lookup for existing media items
- May need to optimize for performance with large numbers of media files
- Automatic parser in ilapfuncs.py and lavafuncs.py needs to handle MediaReference objects appropriately

## Implementation Notes
- Modules will pass MediaReference objects as cell values in their data structures
- Implement an automatic parser to extract necessary information from MediaReference objects
- Design the system to support future media filtering and searching capabilities
- Consider implementing a background process for enhanced metadata extraction (e.g., EXIF data) in the future