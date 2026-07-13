__artifacts_v2__ = {
    "c2paProvenance": {
        "name": "C2PA Content Provenance (AI Provenance)",
        "description": "Extracts content-provenance metadata from media files via two independent "
                       "paths: (1) C2PA / Content Credentials manifests and (2) IPTC/XMP "
                       "DigitalSourceType tags. Reports the claim generator, edit actions, digital "
                       "source type, author/creator, credit/copyright, ingredients (prior assets), "
                       "the stated signer certificate and signing time, and an AI-generated "
                       "indicator. Useful for establishing whether an image was AI-generated or "
                       "edited and by what tool.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-12",
        "last_update_date": "2026-07-12",
        "requirements": "none",
        "category": "AI Provenance",
        "notes": "SIGNATURE CAVEAT: the signer, issuer, algorithm, and signing time are read "
                 "from the C2PA manifest AS STATED. This artifact does NOT cryptographically "
                 "verify the signature, validate the certificate chain, or check revocation, so "
                 "'Signed By' is a lead to corroborate, not proof of origin. Implementation is "
                 "pure-Python with no external dependencies: a JUMBF/CBOR parser for C2PA, an XML "
                 "reader for the IPTC/XMP DigitalSourceType (which AI tools often embed with no "
                 "C2PA manifest at all), and a COSE_Sign1 + X.509 + RFC 3161 reader for the "
                 "signature. The 'Metadata Source' column distinguishes C2PA from XMP/IPTC "
                 "findings. JPEG (C2PA + XMP + signature) is validated against test files and real "
                 "Google/Gemini images; PNG and ISOBMFF (HEIC/AVIF/MP4/MOV) containers are handled "
                 "per the C2PA specification.",
        "paths": (  # case-insensitive extensions; fnmatch '*' already spans '/', so these
                    # match media at ANY depth. Uppercase forms catch iOS defaults (.HEIC/.JPG/.MOV).
            '*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]', '*.[jJ][pP][eE]',
            '*.[pP][nN][gG]', '*.[hH][eE][iI][cC]', '*.[hH][eE][iI][fF]',
            '*.[hH][iI][fF]', '*.[aA][vV][iI][fF]', '*.[wW][eE][bB][pP]',
            '*.[jJ][xX][lL]', '*.[tT][iI][fF]', '*.[tT][iI][fF][fF]',
            '*.[dD][nN][gG]', '*.[mM][pP]4', '*.[mM][oO][vV]', '*.[mM]4[vV]',
        ),
        "output_types": "all",
        "artifact_icon": "certificate",
    }
}

import os
import json
import struct
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc


# ===========================================================================
# Minimal CBOR decoder (RFC 8949 core data model — the subset C2PA uses).
# ===========================================================================
class _CBOR:
    def __init__(self, data):
        self.d = data
        self.i = 0

    def _u(self, n):
        v = int.from_bytes(self.d[self.i:self.i + n], 'big')
        self.i += n
        return v

    def _length(self, info):
        if info < 24:
            return info
        if info == 24:
            return self._u(1)
        if info == 25:
            return self._u(2)
        if info == 26:
            return self._u(4)
        if info == 27:
            return self._u(8)
        if info == 31:
            return None  # indefinite length
        raise ValueError(f'bad CBOR length info {info}')

    def _items_until_break(self, pairs=False):
        out = {} if pairs else []
        while self.d[self.i] != 0xff:
            if pairs:
                k = self.decode()
                out[k if isinstance(k, (str, int)) else str(k)] = self.decode()
            else:
                out.append(self.decode())
        self.i += 1
        return out

    def decode(self):
        ib = self.d[self.i]
        self.i += 1
        mt = ib >> 5
        info = ib & 0x1f
        if mt == 0:                       # unsigned int
            return self._length(info)
        if mt == 1:                       # negative int
            return -1 - self._length(info)
        if mt == 2:                       # byte string
            n = self._length(info)
            if n is None:
                return b''.join(self._items_until_break())
            v = bytes(self.d[self.i:self.i + n])
            self.i += n
            return v
        if mt == 3:                       # text string
            n = self._length(info)
            if n is None:
                return ''.join(self._items_until_break())
            v = self.d[self.i:self.i + n].decode('utf-8', 'replace')
            self.i += n
            return v
        if mt == 4:                       # array
            n = self._length(info)
            if n is None:
                return self._items_until_break()
            return [self.decode() for _ in range(n)]
        if mt == 5:                       # map
            n = self._length(info)
            if n is None:
                return self._items_until_break(pairs=True)
            out = {}
            for _ in range(n):
                k = self.decode()
                out[k if isinstance(k, (str, int)) else str(k)] = self.decode()
            return out
        if mt == 6:                       # tag (semantics ignored)
            self._length(info)
            return self.decode()
        if mt == 7:                       # simple / float
            if info == 20:
                return False
            if info == 21:
                return True
            if info in (22, 23):
                return None
            if info == 25:
                v = _half_to_float(self._u(2))
                return v
            if info == 26:
                v = struct.unpack('>f', self.d[self.i:self.i + 4])[0]
                self.i += 4
                return v
            if info == 27:
                v = struct.unpack('>d', self.d[self.i:self.i + 8])[0]
                self.i += 8
                return v
            return None
        raise ValueError(f'unknown CBOR major type {mt}')


def _half_to_float(h):
    sign = (h >> 15) & 1
    exp = (h >> 10) & 0x1f
    frac = h & 0x3ff
    if exp == 0:
        val = frac / 1024.0 * (2 ** -14)
    elif exp == 31:
        val = float('inf') if frac == 0 else float('nan')
    else:
        val = (1 + frac / 1024.0) * (2 ** (exp - 15))
    return -val if sign else val


def _cbor_decode(data):
    return _CBOR(data).decode()


# ===========================================================================
# JUMBF box walker (ISO/IEC 19566-5).
# ===========================================================================
def _iter_boxes(data):
    i, n = 0, len(data)
    while i + 8 <= n:
        size = struct.unpack('>I', data[i:i + 4])[0]
        btype = data[i + 4:i + 8].decode('latin-1')
        hdr = 8
        if size == 1:
            if i + 16 > n:
                break
            size = struct.unpack('>Q', data[i + 8:i + 16])[0]
            hdr = 16
        elif size == 0:
            size = n - i
        if size < hdr or i + size > n:
            break
        yield btype, data[i + hdr:i + size]
        i += size


def _parse_jumd(payload):
    """Description box: 16-byte UUID (type), 1 toggle byte, optional null-terminated label."""
    if len(payload) < 17:
        return None, None
    uuid = payload[:16].hex()
    toggles = payload[16]
    label = None
    if toggles & 0x02:  # label present
        try:
            end = payload.index(b'\x00', 17)
            label = payload[17:end].decode('utf-8', 'replace')
        except ValueError:
            pass
    return uuid, label


def _parse_jumbf_content(box_bytes):
    """Parse the *contents* of a jumb box payload into a node tree."""
    node = {'label': None, 'uuid': None, 'content': [], 'boxes': []}
    for btype, payload in _iter_boxes(box_bytes):
        if btype == 'jumd':
            node['uuid'], node['label'] = _parse_jumd(payload)
        elif btype == 'jumb':
            node['boxes'].append(_parse_jumbf_content(payload))
        elif btype == 'cbor':
            try:
                node['content'].append(('cbor', _cbor_decode(payload)))
            except Exception as ex:   # pylint: disable=broad-exception-caught
                node['content'].append(('cbor_error', str(ex)))
        elif btype == 'json':
            try:
                node['content'].append(('json', json.loads(payload.decode('utf-8', 'replace'))))
            except Exception as ex:   # pylint: disable=broad-exception-caught
                node['content'].append(('json_error', str(ex)))
        else:
            node['content'].append((btype, len(payload)))
    return node


def _parse_jumbf(box_bytes):
    """box_bytes is a full 'jumb' box (LBox/TBox + payload)."""
    root = {'label': None, 'uuid': None, 'content': [], 'boxes': []}
    for btype, payload in _iter_boxes(box_bytes):
        if btype == 'jumb':
            root['boxes'].append(_parse_jumbf_content(payload))
    return root


# ===========================================================================
# Container extraction: pull the raw C2PA JUMBF box bytes out of a media file.
# ===========================================================================
_C2PA_BMFF_UUID = bytes.fromhex('d8fec3d61b0e483c92975828877ec481')


def _extract_jumbf_jpeg(data):
    """Reassemble the C2PA JUMBF box from JPEG APP11 marker segments."""
    i, n = 2, len(data)
    packets = {}  # box-instance (En) -> {packet-seq (Z): payload}
    while i + 4 <= n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if marker == 0xDA:  # start of scan -> compressed data, stop
            break
        if i + 4 > n:
            break
        seg_len = struct.unpack('>H', data[i + 2:i + 4])[0]
        seg = data[i + 4:i + 2 + seg_len]
        if marker == 0xEB and seg[:2] == b'\x4A\x50' and len(seg) >= 8:  # APP11, CI == "JP"
            en = struct.unpack('>H', seg[2:4])[0]
            z = struct.unpack('>I', seg[4:8])[0]
            packets.setdefault(en, {})[z] = seg[8:]
        i += 2 + seg_len
    if not packets:
        return None
    # First box-instance is the C2PA manifest store. Continuation packets (Z>1)
    # repeat the superbox LBox+TBox header, which must be stripped before joining.
    en = sorted(packets)[0]
    zs = sorted(packets[en])
    first = packets[en][zs[0]]
    hdr = 16 if first[:4] == b'\x00\x00\x00\x01' else 8
    parts = [first] + [packets[en][z][hdr:] for z in zs[1:]]
    return b''.join(parts)


def _extract_jumbf_png(data):
    """C2PA in PNG lives in a 'caBX' ancillary chunk holding the JUMBF box."""
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    i, n = 8, len(data)
    while i + 8 <= n:
        length = struct.unpack('>I', data[i:i + 4])[0]
        ctype = data[i + 4:i + 8]
        start = i + 8
        if ctype == b'caBX':
            return data[start:start + length]
        i = start + length + 4  # skip data + CRC
    return None


def _extract_jumbf_bmff(data):
    """C2PA in ISOBMFF (HEIC/AVIF/MP4/MOV): a top-level 'uuid' box with the C2PA UUID."""
    for btype, payload in _iter_boxes(data):
        if btype == 'uuid' and payload[:16] == _C2PA_BMFF_UUID:
            body = payload[16:]
            # After the C2PA UUID there may be a version/flags + a JUMBF superbox.
            idx = body.find(b'jumb')
            if idx >= 4:
                return body[idx - 4:]
            return body
    return None


def _extract_jumbf(data, ext):
    if ext in ('.jpg', '.jpeg', '.jpe'):
        return _extract_jumbf_jpeg(data)
    if ext == '.png':
        return _extract_jumbf_png(data)
    if ext in ('.heic', '.heif', '.avif', '.mp4', '.mov', '.m4v'):
        return _extract_jumbf_bmff(data)
    # Fallback: try each container heuristically.
    return (_extract_jumbf_jpeg(data) or _extract_jumbf_png(data)
            or _extract_jumbf_bmff(data))


# ===========================================================================
# XMP / IPTC extraction (container-agnostic; no ExifTool dependency).
# AI-generated images frequently carry the IPTC DigitalSourceType in XMP with
# no C2PA manifest at all — this path catches those.
# ===========================================================================
def _extract_xmp(data):
    """Locate the raw XMP packet (XML) anywhere in the file bytes."""
    start = data.find(b'<x:xmpmeta')
    if start != -1:
        end = data.find(b'</x:xmpmeta>')
        if end != -1:
            return data[start:end + len(b'</x:xmpmeta>')]
    start = data.find(b'<rdf:RDF')
    if start != -1:
        end = data.find(b'</rdf:RDF>')
        if end != -1:
            return data[start:end + len(b'</rdf:RDF>')]
    return None


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _rdf_values(el):
    """Collect the text of rdf:li items (or the element's own text)."""
    out = []
    for li in el.iter():
        if _local(li.tag) == 'li' and (li.text or '').strip():
            out.append(li.text.strip())
    if not out and (el.text or '').strip():
        out.append(el.text.strip())
    return out


def _parse_xmp(xmp_bytes):
    """Extract the provenance-relevant IPTC/XMP fields from an XMP packet."""
    try:
        root = ET.fromstring(xmp_bytes)
    except ET.ParseError:
        return None
    res = {'digital_source': None, 'digital_source_label': None, 'ai': None,
           'creators': [], 'credit': None, 'copyright': None, 'creator_tool': None}
    for el in root.iter():
        # RDF shorthand: many properties appear as attributes on rdf:Description.
        for akey, aval in el.attrib.items():
            aln = _local(akey)
            if aln == 'DigitalSourceType' and aval:
                res['digital_source'] = aval
            elif aln == 'CreatorTool' and aval:
                res['creator_tool'] = aval
            elif aln == 'Credit' and aval:
                res['credit'] = aval
        ln = _local(el.tag)
        text = (el.text or '').strip()
        if ln == 'DigitalSourceType' and text:
            res['digital_source'] = text
        elif ln == 'CreatorTool' and text:
            res['creator_tool'] = text
        elif ln == 'Credit' and text:
            res['credit'] = text
        elif ln == 'creator':
            res['creators'].extend(_rdf_values(el))
        elif ln == 'rights' and not res['copyright']:
            vals = _rdf_values(el)
            if vals:
                res['copyright'] = vals[0]
    if res['digital_source']:
        res['digital_source_label'], res['ai'] = _source_type_label(res['digital_source'])
    return res


def _cheap_has_provenance(path):
    """Fast pre-filter: fully parse only files whose header carries a C2PA or
    IPTC/XMP DigitalSourceType marker."""
    try:
        with open(path, 'rb') as f:
            head = f.read(512 * 1024)
    except OSError:
        return False
    return (b'c2pa' in head or b'jumb' in head or b'DigitalSourceType' in head)


# ===========================================================================
# Normalization: flatten manifests into forensic row fields.
# IPTC DigitalSourceType codes -> (human label, is_ai_generated)
# ===========================================================================
_DIGITAL_SOURCE_TYPES = {
    'trainedAlgorithmicMedia': ('AI-generated (trained algorithmic media)', True),
    'compositeWithTrainedAlgorithmicMedia': ('AI composite (with trained algorithmic media)', True),
    'algorithmicMedia': ('Algorithmically generated', True),
    'algorithmicallyEnhanced': ('Algorithmically enhanced', True),
    'compositeSynthetic': ('Composite synthetic', True),
    'digitalArt': ('Digital art', True),
    'virtualRecording': ('Virtual recording', True),
    'dataDrivenMedia': ('Data-driven media', True),
    'digitalCapture': ('Digital capture (camera)', False),
    'originalPhotograph': ('Original photograph', False),
    'minorHumanEdits': ('Minor human edits', False),
    'humanEdits': ('Human edits', False),
    'compositeCapture': ('Composite capture', False),
    'negativeFilm': ('Negative film', False),
    'positiveFilm': ('Positive film', False),
    'print': ('Print', False),
    'screenCapture': ('Screen capture', False),
    'softwareImage': ('Software image', False),
}


def _base_label(label):
    """Strip a trailing version suffix, e.g. 'c2pa.actions.v2' -> 'c2pa.actions'."""
    if not label:
        return ''
    parts = label.split('.')
    if parts and parts[-1] and parts[-1][0] == 'v' and parts[-1][1:].isdigit():
        return '.'.join(parts[:-1])
    return label


def _source_type_label(uri):
    if not uri:
        return None, None
    code = uri.rstrip('/').rsplit('/', 1)[-1]
    return _DIGITAL_SOURCE_TYPES.get(code, (code, None))


def _content_value(node, prefer=('cbor', 'json')):
    for kind, val in node['content']:
        if kind in prefer:
            return val
    return None


def _claim_generator_str(claim):
    cg = claim.get('claim_generator')
    if isinstance(cg, str) and cg.strip():
        return cg
    info = claim.get('claim_generator_info')
    if isinstance(info, dict):
        info = [info]
    if isinstance(info, list):
        names = []
        for c in info:
            if isinstance(c, dict) and c.get('name'):
                ver = c.get('version', '')
                names.append(f"{c['name']} {ver}".strip())
        if names:
            return ', '.join(names)
    return ''


def _iter_manifests(node):
    # A manifest description box uses the 'c2ma' UUID (hex prefix 63326d61).
    if node['uuid'] and node['uuid'].startswith('63326d61'):
        yield node
    for child in node['boxes']:
        yield from _iter_manifests(child)


# ===========================================================================
# Signature parsing: COSE_Sign1 (RFC 9052) + minimal X.509 (RFC 5280) and the
# RFC 3161 timestamp. This extracts the STATED signer, issuer, algorithm, and
# signing time. It does NOT cryptographically verify the signature or validate
# the certificate chain — treat the values as claimed, not proven.
# ===========================================================================
_COSE_ALG = {-7: 'ES256', -35: 'ES384', -36: 'ES512', -8: 'EdDSA', -37: 'PS256',
             -38: 'PS384', -39: 'PS512', -257: 'RS256', -258: 'RS384', -259: 'RS512'}
_OID_CN = bytes([0x55, 0x04, 0x03])          # 2.5.4.3 commonName
_OID_O = bytes([0x55, 0x04, 0x0A])           # 2.5.4.10 organizationName
_OID_TSTINFO = bytes([0x2A, 0x86, 0x48, 0x86, 0xF7, 0x0D, 0x01, 0x09, 0x10, 0x01, 0x04])


def _der_read(data, i):
    """Read one DER TLV at offset i. Returns (tag, value_bytes, next_offset)."""
    tag = data[i]
    ln = data[i + 1]
    i += 2
    if ln & 0x80:
        n = ln & 0x7f
        ln = int.from_bytes(data[i:i + n], 'big')
        i += n
    return tag, data[i:i + ln], i + ln


def _der_children(data):
    out = []
    i = 0
    while i + 2 <= len(data):
        tag, val, i = _der_read(data, i)
        out.append((tag, val))
    return out


def _der_name(name_bytes):
    """X.501 Name -> {'cn':..., 'o':...} (commonName / organizationName)."""
    res = {}
    for _, rdn in _der_children(name_bytes):
        for _, atv in _der_children(rdn):
            kids = _der_children(atv)
            if len(kids) >= 2 and kids[0][0] == 0x06:
                oid, val = kids[0][1], kids[1][1].decode('utf-8', 'replace')
                if oid == _OID_CN:
                    res['cn'] = val
                elif oid == _OID_O:
                    res['o'] = val
    return res


def _der_time(tag, val):
    s = val.decode('ascii', 'replace')
    if tag == 0x17 and len(s) >= 12:         # UTCTime YYMMDDHHMMSSZ
        yy = int(s[0:2])
        year = 2000 + yy if yy < 50 else 1900 + yy
        return f"{year}-{s[2:4]}-{s[4:6]} {s[6:8]}:{s[8:10]}:{s[10:12]}"
    if tag == 0x18 and len(s) >= 14:         # GeneralizedTime YYYYMMDDHHMMSSZ
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
    return s.rstrip('Z')


def _parse_x509(der):
    """Return {'subject','issuer','not_before','not_after'} from a DER cert."""
    cert = _der_children(der)[0][1]                      # Certificate SEQUENCE value
    tbs = _der_children(_der_children(cert)[0][1])       # tbsCertificate children
    idx = 1 if tbs and tbs[0][0] == 0xA0 else 0          # skip optional [0] version
    idx += 2                                             # serialNumber, signature alg
    issuer = _der_name(tbs[idx][1]); idx += 1
    validity = _der_children(tbs[idx][1]); idx += 1
    subject = _der_name(tbs[idx][1])
    return {'subject': subject, 'issuer': issuer,
            'not_before': _der_time(*validity[0]), 'not_after': _der_time(*validity[1])}


def _tsa_gentime(token):
    """Walk an RFC 3161 timestamp token (CMS) to the TSTInfo genTime."""
    def rec(data):
        kids = _der_children(data)
        for idx, (tag, val) in enumerate(kids):
            if tag == 0x06 and val == _OID_TSTINFO and idx + 1 < len(kids):
                ntag, nval = kids[idx + 1]
                if ntag == 0xA0:
                    oct_kids = _der_children(nval)
                    if oct_kids and oct_kids[0][0] == 0x04:
                        inner = _der_children(oct_kids[0][1])
                        tstinfo = inner[0][1] if inner and inner[0][0] == 0x30 else oct_kids[0][1]
                        for t, v in _der_children(tstinfo):
                            if t == 0x18:
                                return _der_time(0x18, v)
            if tag & 0x20:
                got = rec(val)
                if got:
                    return got
        return None
    return rec(token)


def _fmt_dn(name):
    """Format a distinguished name as 'Org (Common Name)'."""
    org, cn = name.get('o'), name.get('cn')
    if org and cn:
        return f'{org} ({cn})'
    return org or cn or ''


def _parse_signature(cose):
    """Parse a c2pa.signature COSE_Sign1 into stated signer/issuer/alg/time."""
    sig = {'present': True, 'alg': '', 'signed_by': '', 'issuer': '',
           'validity': '', 'signing_time': ''}
    if not (isinstance(cose, list) and len(cose) >= 2):
        return sig
    try:
        ph = _cbor_decode(cose[0]) if isinstance(cose[0], (bytes, bytearray)) else {}
    except Exception:   # pylint: disable=broad-exception-caught
        ph = {}
    if isinstance(ph, dict):
        sig['alg'] = _COSE_ALG.get(ph.get(1), '')
        x5 = ph.get(33)
        if isinstance(x5, (bytes, bytearray)):
            x5 = [x5]
        if isinstance(x5, list) and x5:
            try:
                cert = _parse_x509(x5[0])
                sig['signed_by'] = _fmt_dn(cert['subject'])
                sig['issuer'] = _fmt_dn(cert['issuer'])
                if cert['not_before'] or cert['not_after']:
                    sig['validity'] = f"{cert['not_before']} to {cert['not_after']} UTC"
            except Exception:   # pylint: disable=broad-exception-caught
                pass
    unprot = cose[1] if len(cose) > 1 else None
    if isinstance(unprot, dict):
        for key in ('sigTst', 'sigTst2'):
            box = unprot.get(key)
            if isinstance(box, dict):
                for tok in box.get('tstTokens', []) or []:
                    val = tok.get('val') if isinstance(tok, dict) else None
                    if isinstance(val, (bytes, bytearray)):
                        try:
                            gt = _tsa_gentime(bytes(val))
                        except Exception:   # pylint: disable=broad-exception-caught
                            gt = None
                        if gt:
                            sig['signing_time'] = gt
                            break
            if sig['signing_time']:
                break
    return sig


def _normalize(tree):
    rows = []
    for man in _iter_manifests(tree):
        row = {
            'manifest': man['label'], 'claim_generator': '', 'title': '', 'format': '',
            'actions': [], 'software_agents': set(), 'digital_source': set(), 'ai': None,
            'authors': [], 'sig': None, 'ingredients': [], 'when': set(),
        }
        for child in man['boxes']:
            base = _base_label(child['label'])
            if base == 'c2pa.claim':
                claim = _content_value(child) or {}
                row['claim_generator'] = _claim_generator_str(claim)
                row['title'] = claim.get('dc:title') or claim.get('title') or ''
                row['format'] = claim.get('dc:format') or claim.get('format') or ''
            elif base == 'c2pa.signature':
                row['sig'] = _parse_signature(_content_value(child))
            elif base == 'c2pa.assertions':
                for a in child['boxes']:
                    abase = _base_label(a['label'])
                    val = _content_value(a)
                    if abase == 'c2pa.actions' and isinstance(val, dict):
                        for act in val.get('actions', []) or []:
                            if not isinstance(act, dict):
                                continue
                            if act.get('action'):
                                row['actions'].append(act['action'])
                            sa = act.get('softwareAgent')
                            if isinstance(sa, str):
                                row['software_agents'].add(sa)
                            elif isinstance(sa, dict) and sa.get('name'):
                                row['software_agents'].add(sa['name'])
                            lbl, ai = _source_type_label(act.get('digitalSourceType'))
                            if lbl:
                                row['digital_source'].add(lbl)
                                if ai is not None:
                                    row['ai'] = ai if row['ai'] is None else (row['ai'] or ai)
                            if act.get('when'):
                                row['when'].add(str(act['when']))
                    elif abase.startswith('stds.schema-org.CreativeWork') and isinstance(val, dict):
                        for au in val.get('author', []) or []:
                            if isinstance(au, dict) and au.get('name'):
                                row['authors'].append(au['name'])
                    elif abase == 'c2pa.ingredient' and isinstance(val, dict):
                        row['ingredients'].append(val.get('title') or val.get('dc:title') or '(unnamed)')
        rows.append(row)
    return rows


def _fmt(items):
    return ', '.join(str(x) for x in items if x)


@artifact_processor
def c2paProvenance(context):
    data_headers = (
        ('Media', 'media'),
        'Media State',
        'AI Generated?',
        'Digital Source Type',
        'Metadata Source',
        'Claim Generator / Creator Tool',
        'Actions',
        'Software Agent(s)',
        'Author(s) / Creator',
        'Credit / Copyright',
        'Title',
        'Ingredients (Prior Assets)',
        ('Signing Time (TSA)', 'datetime'),
        'Signed By (stated)',
        'Certificate Issuer',
        'Certificate Validity',
        'Signature Algorithm',
        'Manifest ID',
        'Format',
        'Source File',
    )
    data_list = []
    sources = []
    _media_ext = ('.jpg', '.jpeg', '.jpe', '.png')  # thumbnailable by the report

    def _ai_str(val):
        return 'Yes' if val is True else 'No' if val is False else 'Unknown'

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        ext = os.path.splitext(file_found)[1].lower()
        if not _cheap_has_provenance(file_found):
            continue
        try:
            with open(file_found, 'rb') as f:
                data = f.read()
        except OSError as ex:
            logfunc(f'C2PA: error reading {file_found}: {ex}')
            continue

        # --- C2PA manifests -------------------------------------------------
        c2pa_rows = []
        try:
            box = _extract_jumbf(data, ext)
            if box and b'jumb' in box[:8]:
                c2pa_rows = _normalize(_parse_jumbf(box))
        except Exception as ex:   # pylint: disable=broad-exception-caught
            logfunc(f'C2PA: error parsing manifest in {file_found}: {ex}')

        # --- IPTC / XMP DigitalSourceType (no C2PA needed) ------------------
        xmp = None
        try:
            xmp_bytes = _extract_xmp(data)
            if xmp_bytes:
                xmp = _parse_xmp(xmp_bytes)
        except Exception as ex:   # pylint: disable=broad-exception-caught
            logfunc(f'C2PA: error parsing XMP in {file_found}: {ex}')

        xmp_has_signal = bool(xmp and xmp.get('digital_source'))
        if not c2pa_rows and not xmp_has_signal:
            continue

        thumb = ''
        if ext in _media_ext:
            try:
                thumb = check_in_media(file_found)
            except Exception:   # pylint: disable=broad-exception-caught
                thumb = ''
        rel = context.get_relative_path(file_found)
        sources.append(rel)

        n_states = len(c2pa_rows)
        for i, r in enumerate(c2pa_rows, 1):
            sig = r['sig'] or {}
            # Each C2PA manifest is one provenance state of the SAME media file;
            # number them so multiple rows don't read as separate pictures. The
            # last manifest in the store is the active (current) one.
            state = f'{i} of {n_states}'
            if n_states > 1 and i == n_states:
                state += ' (current)'
            data_list.append((
                thumb,
                state,
                _ai_str(r['ai']),
                _fmt(sorted(r['digital_source'])),
                'C2PA',
                r['claim_generator'],
                _fmt(r['actions']),
                _fmt(sorted(x for x in r['software_agents'] if x)),
                _fmt(r['authors']),
                '',
                r['title'],
                _fmt(r['ingredients']),
                sig.get('signing_time', ''),
                sig.get('signed_by', ''),
                sig.get('issuer', ''),
                sig.get('validity', ''),
                sig.get('alg', ''),
                r['manifest'] or '',
                r['format'],
                rel,
            ))

        if xmp_has_signal:
            data_list.append((
                thumb,
                'IPTC tag',
                _ai_str(xmp['ai']),
                xmp['digital_source_label'] or xmp['digital_source'],
                'XMP/IPTC',
                xmp['creator_tool'] or '',
                '',
                '',
                _fmt(xmp['creators']),
                _fmt([xmp['credit'], xmp['copyright']]),
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                rel,
            ))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
