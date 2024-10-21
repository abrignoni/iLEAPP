# ADR: Implement Safe File and Plist Handling Functions

## Status

Proposed

## Context

Currently, individual artifact modules in iLEAPP handle file opening and plist parsing directly, without consistent error handling. This can lead to module failures that stop the execution of the entire artifact when encountering issues with file access or plist parsing. There's a need for a more robust and consistent approach to handle these operations across all modules.

## Decision

We will implement two new utility functions in the `ilapfuncs.py` file:

1. `get_file_content(file_path, binary_mode=False, encoding=None)`
2. `get_plist_content(file_path)`

These functions will encapsulate file opening and plist parsing operations with proper error handling, allowing artifact modules to focus on data processing logic rather than error handling.

## Details

### `get_file_content` Function

```python
def get_file_content(file_path, binary_mode=False, encoding=None):
    mode = 'rb' if binary_mode else 'r'
    try:
        with open(file_path, mode, encoding=encoding) as file:
            return file.read()
    except Exception as e:
        logfunc(f"Error reading file {file_path}: {str(e)}")
        return None
```

This function provides a safe way to read file contents, allowing only read operations. It simplifies the choice between text and binary modes using a boolean flag, and includes error handling and logging for file access issues.

### `get_plist_content` Function

```python
def get_plist_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            return plistlib.load(file)
    except FileNotFoundError:
        logfunc(f"Error: Plist file not found at {file_path}")
    except PermissionError:
        logfunc(f"Error: Permission denied when trying to read {file_path}")
    except plistlib.InvalidFileException:
        logfunc(f"Error: Invalid plist file format in {file_path}")
    except xml.parsers.expat.ExpatError:
        logfunc(f"Error: Malformed XML in plist file {file_path}")
    except ValueError as e:
        logfunc(f"Error: Value error when parsing plist {file_path}: {str(e)}")
    except Exception as e:
        logfunc(f"Unexpected error reading plist file {file_path}: {str(e)}")
    return None
```

## Consequences

### Positive

1. Improved error handling and logging across all artifact modules.
2. Simplified code in individual artifact modules, reducing the chance of errors.
3. Consistent behavior when encountering file access or parsing issues.
4. Easier maintenance and updates to error handling logic.
5. Does not block module author from continuiing to use direct file access for advanced devs.

### Negative

1. Existing modules will need to be updated to use the new functions.

## Implementation

1. Add the new functions to `ilapfuncs.py`.
2. Update existing artifact modules to use these new functions.
3. Document the new functions and their usage in the developer guide.
4. Implement a gradual rollout, starting with a few key modules to validate the approach.

## Notes

- Consider adding more specific error types and handling if needed in the future.
- Consider if there are other needs to access file content in other ways.
- Consider if there are other parameters needed for proposed functions.
