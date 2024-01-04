# -*- coding: utf-8 -*-

from .base import Type


class XmlTextBase(Type):
    """
    Implements the XML base type.
    """
    def __init__(self, mime, extension):
        super(XmlTextBase, self).__init__(
            mime=mime,
            extension=extension
        )

    def _is_xml(self, buf):
        signature = b"\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22"
        if len(buf) > 19 and buf[0:19] == signature:
            return True
        return False


class Json(Type):
    """Implements the Json text type matcher."""

    MIME = 'application/json'
    EXTENSION = 'json'

    def __init__(self):
        super(Json, self).__init__(
            mime=Json.MIME,
            extension=Json.EXTENSION
        )

    def match(self, buf):
        if len(buf) > 4:
            return ((buf[0] == 0x5B and buf[1] == 0x7B) or
                (buf[0] == 0x7B and buf[1] == 0x22) or
                (buf[0] == 0x7B and buf[1] == 0x0A and buf[2] == 0x20 and buf[3] == 0x20 and buf[4] == 0x22))


class Html(Type):
    """Implements the Html text type matcher."""

    MIME = 'text/html'
    EXTENSION = 'html'

    def __init__(self):
        super(Html, self).__init__(
            mime=Html.MIME,
            extension=Html.EXTENSION
        )

    def match(self, buf):
        if len(buf) > 14:
            return (buf[0] == 0x3C and 
                    buf[1] == 0x21 and
                    buf[2] == 0x44 or buf[2] == 0x64 and 
                    buf[3] == 0x4F or buf[3] == 0x6F and
                    buf[4] == 0x43 or buf[4] == 0x63 and 
                    buf[5] == 0x54 or buf[5] == 0x74 and
                    buf[6] == 0x59 or buf[6] == 0x79 and 
                    buf[7] == 0x50 or buf[7] == 0x70 and
                    buf[8] == 0x45 or buf[8] == 0x65 and 
                    buf[9] == 0x20 and
                    buf[10] == 0x68 and 
                    buf[11] == 0x74 and
                    buf[12] == 0x6D and 
                    buf[13] == 0x6C and
                    buf[14] == 0x3E)
      


class Plist(XmlTextBase):
    """Implements the XML Property List type matcher."""

    MIME = 'application/x-plist'
    EXTENSION = 'plist'

    def __init__(self):
        super(Plist, self).__init__(
            mime=Plist.MIME,
            extension=Plist.EXTENSION
        )

    def match(self, buf):
        if not self._is_xml(buf):
            return False
        return (len(buf) > 19 and
                (b"\x3C\x21\x44\x4F\x43\x54\x59\x50\x45\x20\x70\x6C\x69\x73\x74\x20\x50\x55\x42\x4C\x49\x43"
                in buf[19:80] or
                b"\x3C\x70\x6C\x69\x73\x74\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22\x3E"
                in buf[19:64]))
