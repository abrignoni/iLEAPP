"""Cross-platform filename and path string safety utilities."""

import re

ILLEGAL_FILENAME_CHARS = {
    '\\': '\\ backslash',
    '/': '/ forward slash',
    '*': '* asterisk',
    '?': '? question mark',
    ':': ': colon',
    '"': '" double quote',
    '<': '< less than',
    '>': '> greater than',
    '|': '| pipe',
    "'": "' apostrophe",
    '\r': '\\r carriage return',
    '\n': '\\n newline',
}

# ASCII control characters (0x00-0x1F, 0x7F): Windows rejects them in paths
# with EINVAL, so they must be sanitized alongside the printable illegal set.
# iOS extractions really do contain them, e.g. chronod icon files named
# '╞¼\x01\x0e::com.apple.siri.heic'.
_CONTROL_CHARS_PATTERN = '\\x00-\\x1f\\x7f'


def _is_control_char(char):
    return ord(char) < 0x20 or ord(char) == 0x7f


def _illegal_filename_char_pattern():
    return '[' + re.escape(''.join(ILLEGAL_FILENAME_CHARS)) + _CONTROL_CHARS_PATTERN + ']'


def _illegal_filepath_char_pattern():
    chars = ''.join(c for c in ILLEGAL_FILENAME_CHARS if c not in '\\/')
    return '[' + re.escape(chars) + _CONTROL_CHARS_PATTERN + ']'


def format_illegal_filename_chars(chars):
    '''Format illegal characters for user-facing messages.'''
    order = {char: index for index, char in enumerate(ILLEGAL_FILENAME_CHARS)}
    unique_chars = sorted(set(chars), key=lambda c: order.get(c, len(order)))
    return ', '.join(ILLEGAL_FILENAME_CHARS.get(c, repr(c)) for c in unique_chars)


def illegal_chars_in_filename(filename):
    '''Return sorted illegal characters present in filename.'''
    order = {char: index for index, char in enumerate(ILLEGAL_FILENAME_CHARS)}
    return sorted({c for c in filename
                   if c in ILLEGAL_FILENAME_CHARS or _is_control_char(c)},
                  key=lambda c: order.get(c, len(order)))


def sanitize_file_path(filename, replacement_char='_'):
    r'''
    Removes illegal characters (for windows) from the string passed. Does not replace \ or /
    '''
    return re.sub(_illegal_filepath_char_pattern(), replacement_char, filename)


def sanitize_file_name(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed.
    '''
    return re.sub(_illegal_filename_char_pattern(), replacement_char, filename)


def validate_filename(filename):
    '''Return (is_valid, error_message) using centralized filename rules.'''
    sanitized_filename = sanitize_file_name(filename)
    if sanitized_filename == filename:
        return True, None
    char_list = format_illegal_filename_chars(illegal_chars_in_filename(filename))
    allowed_list = ', '.join(ILLEGAL_FILENAME_CHARS.values())
    return False, (
        f'Output folder name contains invalid character(s): {char_list}\n\n'
        f'Folder names cannot include: {allowed_list}'
    )
