"""Base file type abstraction used by specific file type matchers."""

# -*- coding: utf-8 -*-


class Type(object):
    """
    Represents the file type object inherited by
    specific file type matchers.
    Provides convenient accessor and helper methods.
    """

    def __init__(self, mime, extension):
        """Initialize a file type with MIME type and extension."""
        self.__mime = mime
        self.__extension = extension

    @property
    def mime(self):
        """Return the MIME type for this file type."""
        return self.__mime

    @property
    def extension(self):
        """Return the file extension for this file type."""
        return self.__extension

    def is_extension(self, extension):
        """Return True when the given extension matches this file type extension."""
        return self.__extension is extension

    def is_mime(self, mime):
        """Return True when the given MIME type matches this file type MIME."""
        return self.__mime is mime

    def match(self, buf):
        """Determine whether the provided buffer matches this file type."""
        raise NotImplementedError
