"""
The secrets of data/leapp_config.json: what opens the data some apps keep encrypted.
Each field of "secrets" is one of two kinds:
- "file", the default: a file to choose, such as iLEAPP's keychain;
- "text": a text to type or to read from a file, hidden on screen, such as a recovery key.
A field may name, in "check", the function that says whether a text can be used, as
"module:function": it raises ValueError, whose message never holds the text.
The window never writes a secret to a file: not to the history, nor to the case data. Whether
the log of a run records it is each tool's choice.
"""

import importlib
from functools import cache

from leapp_functions import leapp

SECRETS = getattr(leapp, "secrets", None)
FIELDS = tuple(SECRETS.fields) if SECRETS else ()
DEFAULT_FILE_TYPES = (("All files", "*"),)


def kind(field):
    """ "file" or "text". """
    return field.get("kind", "file")


def name(field):
    """ The name of the secret inside a sentence: "keychain", "Signal recovery key". """
    return field.get("display", field["name"])


def title(field):
    """ The name of the secret at the start of a line: "Keychain". """
    text = name(field)
    return text[:1].upper() + text[1:]


def file_types(field):
    """ The kinds of files the file dialog of the field offers. """
    return [tuple(file_type) for file_type in field.get("filetypes", DEFAULT_FILE_TYPES)]


@cache
def checker(spec):
    """ The function that "module:function" names. """
    module, _, function = spec.partition(":")
    return getattr(importlib.import_module(module), function)


def text_problem(field, text):
    """ Why the text typed for a "text" field cannot be used, or "" when it can or is empty. """
    spec = field.get("check")
    if not text or not spec:
        return ""
    try:
        checker(spec)(text)
    except ValueError as error:
        return f"{title(field)}: {error}"
    return ""
