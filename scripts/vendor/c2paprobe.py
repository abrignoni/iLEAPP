"""Read the Content Credentials (C2PA) and IPTC digital source type a media file declares.

c2paprobe is a read-only, standard-library-only reader for forensic work. It
walks a file's container from its own bytes, finds the C2PA manifest store and
the XMP packets the container holds, and decodes what they state: the manifests
(claim generator, title, format, actions, software agents, digital source types,
authors, ingredients) and the signature's stated signer, issuer, algorithm,
validity and time-stamp.

It does NOT verify anything. No signature is checked, no certificate chain is
built and no revocation is looked up, so every signer and time it returns is
what the file states, not what has been proven. A reader that verifies needs a
C2PA validator (c2pa-rs and its bindings) and trust lists; this one is meant to
work where neither can be shipped.

    result = probe('photo.jpg')
    result['container']   # 'jpeg', 'png', 'isobmff', 'riff', 'gif', 'tiff', 'jxl' or None
    result['complete']    # True when the walk read every place this reader looks
    result['stores']      # where each manifest store sits in the file
    result['manifests']   # the decoded manifests of the first store, active last
    result['xmp']         # the IPTC/XMP fields of each XMP packet the container holds

``complete`` is what makes a missing store mean something. It is True only
when the walk reached the container's own end (or, for JPEG, the first scan,
after which no metadata segment is read), so a file with ``complete`` True and
no store holds none in any place this reader looks. When it is False the walk
stopped early (truncated or malformed structure) and absence is not established.

Formats and where they are read (C2PA 2.2, section A.3 "Embedding manifests
into assets", and each container's own specification):

    JPEG     APP11 JUMBF segments (C2PA); APP1 XMP and extended XMP
    PNG      caBX chunk (C2PA); iTXt "XML:com.adobe.xmp" (XMP)
    ISOBMFF  top-level C2PA uuid box (HEIC, HEIF, AVIF, MP4, MOV, M4V); XMP in the
             XMP uuid box, moov/udta/XMP_ and a HEIF meta item of MIME type
             application/rdf+xml
    RIFF     C2PA chunk (WebP, AVI, WAV); "XMP " and "_PMX" chunks
    GIF      C2PA_GIF application extension; "XMP DataXMP" application extension
    TIFF     tag 52545 (C2PA) and tag 700 (XMP) in the IFD chain (TIFF, DNG)
    JPEG XL  top-level jumb box (C2PA); "xml " box (XMP). Brotli-compressed
             metadata boxes (brob) are reported, not decompressed.

Anything else returns ``container`` None and is not examined.
"""

from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
import zlib

__version__ = '0.1.1'

__all__ = ['probe', 'probe_bytes', 'parse_store', 'parse_xmp', 'source_type',
           'IPTC_TERMS', 'MAX_STORE', '__version__']

MAX_STORE = 64 * 1024 * 1024   # largest manifest store or XMP packet read into memory


# ===========================================================================
# CBOR (RFC 8949): the subset C2PA uses. Tags are read and their content kept.
# ===========================================================================
class _CBOR:
    def __init__(self, data):
        self.d = data
        self.i = 0
        self.depth = 0

    def _u(self, n):
        if self.i + n > len(self.d):
            raise ValueError('CBOR value runs past its data')
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
            return None                    # indefinite length
        raise ValueError(f'bad CBOR length info {info}')

    def _bytes(self, n):
        if self.i + n > len(self.d):
            raise ValueError('CBOR string runs past its data')
        v = bytes(self.d[self.i:self.i + n])
        self.i += n
        return v

    def _until_break(self, pairs=False):
        out = {} if pairs else []
        while True:
            if self.i >= len(self.d):
                raise ValueError('CBOR indefinite item has no break')
            if self.d[self.i] == 0xff:
                break
            if pairs:
                k = self.decode()
                out[_key(k)] = self.decode()
            else:
                out.append(self.decode())
        self.i += 1
        return out

    def decode(self):
        if self.i >= len(self.d):
            raise ValueError('CBOR data ends early')
        self.depth += 1
        if self.depth > 200:
            raise ValueError('CBOR nesting too deep')
        try:
            ib = self.d[self.i]
            self.i += 1
            mt, info = ib >> 5, ib & 0x1f
            if mt == 0:
                return self._length(info)
            if mt == 1:
                return -1 - self._length(info)
            if mt in (2, 3):
                n = self._length(info)
                if n is None:
                    parts = self._until_break()
                    return b''.join(parts) if mt == 2 else ''.join(parts)
                raw = self._bytes(n)
                return raw if mt == 2 else raw.decode('utf-8', 'replace')
            if mt == 4:
                n = self._length(info)
                return self._until_break() if n is None else [self.decode() for _ in range(n)]
            if mt == 5:
                n = self._length(info)
                if n is None:
                    return self._until_break(pairs=True)
                out = {}
                for _ in range(n):
                    k = self.decode()
                    out[_key(k)] = self.decode()
                return out
            if mt == 6:                    # tag: the content is what matters here
                self._length(info)
                return self.decode()
            if info == 20:
                return False
            if info == 21:
                return True
            if info in (22, 23):
                return None
            if info == 25:
                return _half_to_float(self._u(2))
            if info == 26:
                return struct.unpack('>f', self._bytes(4))[0]
            if info == 27:
                return struct.unpack('>d', self._bytes(8))[0]
            return None
        finally:
            self.depth -= 1


def _key(k):
    return k if isinstance(k, (str, int)) else str(k)


def _half_to_float(h):
    sign, exp, frac = (h >> 15) & 1, (h >> 10) & 0x1f, h & 0x3ff
    if exp == 0:
        val = frac / 1024.0 * (2 ** -14)
    elif exp == 31:
        val = float('inf') if frac == 0 else float('nan')
    else:
        val = (1 + frac / 1024.0) * (2 ** (exp - 15))
    return -val if sign else val


def _cbor(data):
    return _CBOR(data).decode()


# ===========================================================================
# JUMBF (ISO/IEC 19566-5): the box tree a manifest store is written as.
# ===========================================================================
_UUID_C2PA_STORE = '6332706100110010800000aa00389b71'      # 'c2pa'
_UUID_MANIFESTS = ('63326d6100110010800000aa00389b71',     # 'c2ma' standard manifest
                   '6332756d00110010800000aa00389b71')     # 'c2um' update manifest


def _boxes(data):
    """(type, payload) for each box laid end to end in ``data``."""
    i, n = 0, len(data)
    while i + 8 <= n:
        size = struct.unpack('>I', data[i:i + 4])[0]
        btype = data[i + 4:i + 8].decode('latin-1')
        hdr = 8
        if size == 1:
            if i + 16 > n:
                return
            size = struct.unpack('>Q', data[i + 8:i + 16])[0]
            hdr = 16
        elif size == 0:
            size = n - i
        if size < hdr or i + size > n:
            return
        yield btype, data[i + hdr:i + size]
        i += size


def _jumd(payload):
    """Description box: 16-byte type UUID, a toggles byte, then an optional label."""
    if len(payload) < 17:
        return None, None
    label = None
    if payload[16] & 0x02:
        end = payload.find(b'\x00', 17)
        if end != -1:
            label = payload[17:end].decode('utf-8', 'replace')
    return payload[:16].hex(), label


def _superbox(payload, depth=0):
    node = {'label': None, 'uuid': None, 'content': [], 'boxes': []}
    if depth > 32:
        return node
    for btype, body in _boxes(payload):
        if btype == 'jumd':
            node['uuid'], node['label'] = _jumd(body)
        elif btype == 'jumb':
            node['boxes'].append(_superbox(body, depth + 1))
        elif btype == 'cbor':
            try:
                node['content'].append(('cbor', _cbor(body)))
            except (ValueError, IndexError, struct.error, RecursionError) as exc:
                node['content'].append(('cbor_error', str(exc)))
        elif btype == 'json':
            try:
                node['content'].append(('json', json.loads(body.decode('utf-8', 'replace'))))
            except ValueError as exc:
                node['content'].append(('json_error', str(exc)))
        else:
            node['content'].append((btype, len(body)))
    return node


def _store_tree(store):
    """The tree of a manifest store: ``store`` is a whole 'jumb' box."""
    for btype, body in _boxes(store):
        if btype == 'jumb':
            return _superbox(body)
    return None


def _is_c2pa_store(store):
    for btype, body in _boxes(store):
        if btype == 'jumb':
            for ctype, cbody in _boxes(body):
                if ctype == 'jumd':
                    uuid, label = _jumd(cbody)
                    return uuid == _UUID_C2PA_STORE or label == 'c2pa'
            return False
    return False


# ===========================================================================
# Digital source type vocabulary.
# ===========================================================================
# IPTC NewsCodes Digital Source Type, release dated 2024-10-23
# (http://cv.iptc.org/newscodes/digitalsourcetype/, CC BY 4.0): code -> (IPTC's
# preferred label, retired). ``ai`` below is this reader's own reading of each
# definition, kept separate from IPTC's words.
IPTC_TERMS = {
    'digitalCapture': ('Digital capture sampled from real life', False),
    'computationalCapture': ('Multi-frame computational capture sampled from real life', False),
    'negativeFilm': ('Digitised from a transparent negative', False),
    'positiveFilm': ('Digitised from a transparent positive', False),
    'print': ('Digitised from a non-transparent medium', False),
    'minorHumanEdits': ('Original media with minor human edits', True),
    'humanEdits': ('Human-edited media', False),
    'compositeWithTrainedAlgorithmicMedia': ('Edited using Generative AI', False),
    'algorithmicallyEnhanced': ('Algorithmically-altered media', False),
    'softwareImage': ('Created by software', True),
    'digitalArt': ('Digital art', True),
    'digitalCreation': ('Digital creation', False),
    'dataDrivenMedia': ('Data-driven media', False),
    'trainedAlgorithmicMedia': ('Created using Generative AI', False),
    'algorithmicMedia': ('Pure algorithmic media', False),
    'screenCapture': ('Screen capture', False),
    'virtualRecording': ('Virtual event recording', False),
    'composite': ('Composite of elements', False),
    'compositeCapture': ('Composite of captured elements', False),
    'compositeSynthetic': ('Composite including generative AI elements', False),
}

# Yes: the three codes whose IPTC definition names generative AI or a model
# trained on captured content. No: capture, scan, human edit, screen capture and
# software image codes. Everything else, including a code no vocabulary here
# holds, is None (unknown): algorithmicMedia ("not based on any sampled training
# data"), algorithmicallyEnhanced, digitalArt, digitalCreation, dataDrivenMedia,
# composite (its elements may or may not be AI) and virtualRecording ("based on
# Generative AI and/or captured elements").
_AI_YES = frozenset(('trainedAlgorithmicMedia', 'compositeWithTrainedAlgorithmicMedia',
                     'compositeSynthetic'))
_AI_NO = frozenset(('digitalCapture', 'computationalCapture', 'originalPhotograph',
                    'negativeFilm', 'positiveFilm', 'print', 'minorHumanEdits', 'humanEdits',
                    'compositeCapture', 'screenCapture', 'softwareImage'))
_DST_NAMESPACES = ('http://cv.iptc.org/newscodes/digitalsourcetype/',
                   'https://cv.iptc.org/newscodes/digitalsourcetype/',
                   'http://c2pa.org/digitalsourcetype/',
                   'https://c2pa.org/digitalsourcetype/')


def source_type(uri):
    """What a stated digital source type is: {'uri', 'code', 'label', 'retired', 'ai'}.

    ``code`` is the last path segment; ``label`` is IPTC's own label, or None for a
    code outside the IPTC vocabulary (C2PA's own terms included); ``ai`` is True,
    False or None as described at _AI_YES. Returns None for an empty value."""
    if not isinstance(uri, str) or not uri.strip():
        return None
    uri = uri.strip()
    code = uri.rstrip('/').rsplit('/', 1)[-1]
    iptc = uri.startswith(_DST_NAMESPACES[:2]) or '/' not in uri
    label, retired = IPTC_TERMS.get(code, (None, False)) if iptc else (None, False)
    ai = True if code in _AI_YES else False if code in _AI_NO else None
    return {'uri': uri, 'code': code, 'label': label, 'retired': retired, 'ai': ai}


def _merge_ai(prev, new):
    """Several stated codes: any True wins, and None never overrides a known value."""
    if new is None:
        return prev
    if prev is None:
        return new
    return prev or new


# ===========================================================================
# Signature: COSE_Sign1 (RFC 9052), X.509 (RFC 5280) and RFC 3161 time-stamps.
# Decoded for what they state. Nothing is verified.
# ===========================================================================
_COSE_ALG = {-7: 'ES256', -35: 'ES384', -36: 'ES512', -8: 'EdDSA', -37: 'PS256',
             -38: 'PS384', -39: 'PS512', -257: 'RS256', -258: 'RS384', -259: 'RS512'}
_OID_CN = bytes((0x55, 0x04, 0x03))
_OID_O = bytes((0x55, 0x04, 0x0A))
_OID_TSTINFO = bytes((0x2A, 0x86, 0x48, 0x86, 0xF7, 0x0D, 0x01, 0x09, 0x10, 0x01, 0x04))


def _der(data, i):
    """One DER TLV at ``i``: (tag, value, next offset)."""
    if i + 2 > len(data):
        raise ValueError('DER item runs past its data')
    tag, ln = data[i], data[i + 1]
    i += 2
    if ln & 0x80:
        n = ln & 0x7f
        if n == 0 or n > 8 or i + n > len(data):
            raise ValueError('bad DER length')
        ln = int.from_bytes(data[i:i + n], 'big')
        i += n
    if i + ln > len(data):
        raise ValueError('DER value runs past its data')
    return tag, data[i:i + ln], i + ln


def _der_children(data):
    out, i = [], 0
    while i + 2 <= len(data):
        tag, val, i = _der(data, i)
        out.append((tag, val))
    return out


def _der_name(data):
    res = {}
    for _, rdn in _der_children(data):
        for _, atv in _der_children(rdn):
            kids = _der_children(atv)
            if len(kids) >= 2 and kids[0][0] == 0x06:
                if kids[0][1] == _OID_CN:
                    res['cn'] = kids[1][1].decode('utf-8', 'replace')
                elif kids[0][1] == _OID_O:
                    res['o'] = kids[1][1].decode('utf-8', 'replace')
    return res


def _der_time(tag, val):
    """A UTCTime or GeneralizedTime as 'YYYY-MM-DD HH:MM:SS' (the value is UTC)."""
    s = val.decode('ascii', 'replace')
    if tag == 0x17 and len(s) >= 12:
        yy = int(s[0:2])
        year = 2000 + yy if yy < 50 else 1900 + yy
        return f'{year}-{s[2:4]}-{s[4:6]} {s[6:8]}:{s[8:10]}:{s[10:12]}'
    if tag == 0x18 and len(s) >= 14:
        return f'{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}'
    return s.rstrip('Z')


def _x509(der):
    cert = _der_children(der)[0][1]
    tbs = _der_children(_der_children(cert)[0][1])
    idx = 1 if tbs and tbs[0][0] == 0xA0 else 0
    idx += 2                                        # serialNumber, signature algorithm
    issuer = _der_name(tbs[idx][1])
    validity = _der_children(tbs[idx + 1][1])
    subject = _der_name(tbs[idx + 2][1])
    return {'subject': subject, 'issuer': issuer,
            'not_before': _der_time(*validity[0]), 'not_after': _der_time(*validity[1])}


def _tst_gentime(token, depth=0):
    """The genTime of the TSTInfo inside an RFC 3161 time-stamp token."""
    if depth > 16:
        return None
    kids = _der_children(token)
    for idx, (tag, val) in enumerate(kids):
        if tag == 0x06 and val == _OID_TSTINFO and idx + 1 < len(kids):
            ntag, nval = kids[idx + 1]
            if ntag == 0xA0:
                octets = _der_children(nval)
                if octets and octets[0][0] == 0x04:
                    inner = _der_children(octets[0][1])
                    tstinfo = inner[0][1] if inner and inner[0][0] == 0x30 else octets[0][1]
                    for t, v in _der_children(tstinfo):
                        if t == 0x18:
                            return _der_time(0x18, v)
        if tag & 0x20:
            got = _tst_gentime(val, depth + 1)
            if got:
                return got
    return None


def _dn(name):
    org, cn = name.get('o'), name.get('cn')
    if org and cn:
        return f'{org} ({cn})'
    return org or cn or ''


def _signature(cose):
    """What a c2pa.signature COSE_Sign1 states. Nothing here is verified."""
    sig = {'alg': '', 'signed_by': '', 'issuer': '', 'not_before': '', 'not_after': '',
           'signing_time': '', 'errors': []}
    if not (isinstance(cose, list) and len(cose) >= 2):
        sig['errors'].append('signature is not a COSE_Sign1 array')
        return sig
    protected = {}
    if isinstance(cose[0], (bytes, bytearray)) and cose[0]:
        try:
            protected = _cbor(bytes(cose[0]))
        except (ValueError, IndexError, struct.error, RecursionError) as exc:
            sig['errors'].append(f'protected header: {exc}')
    unprotected = cose[1] if isinstance(cose[1], dict) else {}
    if isinstance(protected, dict):
        sig['alg'] = _COSE_ALG.get(protected.get(1), str(protected.get(1) or ''))
    # x5chain (label 33) is in the protected header from C2PA 1.3 on, the
    # unprotected one before that.
    x5 = None
    for header in (protected, unprotected):
        if isinstance(header, dict) and header.get(33) is not None:
            x5 = header.get(33)
            break
    if isinstance(x5, (bytes, bytearray)):
        x5 = [x5]
    if isinstance(x5, list) and x5 and isinstance(x5[0], (bytes, bytearray)):
        try:
            cert = _x509(bytes(x5[0]))
            sig['signed_by'] = _dn(cert['subject'])
            sig['issuer'] = _dn(cert['issuer'])
            sig['not_before'], sig['not_after'] = cert['not_before'], cert['not_after']
        except (ValueError, IndexError) as exc:
            sig['errors'].append(f'signer certificate: {exc}')
    for key in ('sigTst2', 'sigTst'):
        box = unprotected.get(key)
        if not isinstance(box, dict):
            continue
        for tok in box.get('tstTokens') or []:
            val = tok.get('val') if isinstance(tok, dict) else None
            if isinstance(val, (bytes, bytearray)):
                try:
                    got = _tst_gentime(bytes(val))
                except (ValueError, IndexError) as exc:
                    sig['errors'].append(f'time-stamp: {exc}')
                    got = None
                if got:
                    sig['signing_time'] = got
                    return sig
    return sig


# ===========================================================================
# Manifest store -> manifests.
# ===========================================================================
def _base_label(label):
    """'c2pa.actions.v2' -> 'c2pa.actions'; a '__1' instance suffix is dropped too."""
    if not label:
        return ''
    label = label.split('__', 1)[0]
    parts = label.split('.')
    if parts and parts[-1][:1] == 'v' and parts[-1][1:].isdigit():
        return '.'.join(parts[:-1])
    return label


def _content(node):
    for kind, val in node['content']:
        if kind in ('cbor', 'json'):
            return val
    return None


def _claim_generator(claim):
    cg = claim.get('claim_generator')
    if isinstance(cg, str) and cg.strip():
        return cg
    info = claim.get('claim_generator_info')
    if isinstance(info, dict):
        info = [info]
    names = []
    for item in info if isinstance(info, list) else ():
        if isinstance(item, dict) and item.get('name'):
            names.append(f"{item['name']} {item.get('version', '')}".strip())
    return ', '.join(names)


def _agent(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and value.get('name'):
        return f"{value['name']} {value.get('version', '')}".strip()
    return ''


def _manifest(node):
    m = {'label': node['label'] or '', 'kind': 'update' if node['uuid'] == _UUID_MANIFESTS[1]
         else 'standard', 'claim_generator': '', 'title': '', 'format': '', 'instance_id': '',
         'actions': [], 'software_agents': [], 'source_types': [], 'ai': None,
         'authors': [], 'ingredients': [], 'signature': None, 'errors': []}
    for child in node['boxes']:
        base = _base_label(child['label'])
        for kind, val in child['content']:
            if kind.endswith('_error'):
                m['errors'].append(f'{child["label"]}: {val}')
        if base == 'c2pa.claim':
            claim = _content(child)
            claim = claim if isinstance(claim, dict) else {}
            m['claim_generator'] = _claim_generator(claim)
            m['title'] = claim.get('dc:title') or claim.get('title') or ''
            m['format'] = claim.get('dc:format') or claim.get('format') or ''
            m['instance_id'] = claim.get('instanceID') or claim.get('instance_id') or ''
        elif base == 'c2pa.signature':
            m['signature'] = _signature(_content(child))
        elif base == 'c2pa.assertions':
            for a in child['boxes']:
                abase, val = _base_label(a['label']), _content(a)
                if abase == 'c2pa.actions' and isinstance(val, dict):
                    for act in val.get('actions') or []:
                        if not isinstance(act, dict):
                            continue
                        if act.get('action'):
                            m['actions'].append(str(act['action']))
                        agent = _agent(act.get('softwareAgent'))
                        if agent and agent not in m['software_agents']:
                            m['software_agents'].append(agent)
                        st = source_type(act.get('digitalSourceType'))
                        if st:
                            if st['uri'] not in [s['uri'] for s in m['source_types']]:
                                m['source_types'].append(st)
                            m['ai'] = _merge_ai(m['ai'], st['ai'])
                elif abase.startswith('stds.schema-org.CreativeWork') and isinstance(val, dict):
                    authors = val.get('author') or []
                    for au in authors if isinstance(authors, list) else [authors]:
                        if isinstance(au, dict) and au.get('name'):
                            m['authors'].append(str(au['name']))
                elif abase == 'c2pa.ingredient' and isinstance(val, dict):
                    m['ingredients'].append({
                        'title': val.get('dc:title') or val.get('title') or '',
                        'format': val.get('dc:format') or val.get('format') or '',
                        'relationship': val.get('relationship') or '',
                    })
    return m


def _manifest_nodes(node, depth=0):
    if node['uuid'] in _UUID_MANIFESTS:
        yield node
        return
    if depth < 8:
        for child in node['boxes']:
            yield from _manifest_nodes(child, depth + 1)


def parse_store(store):
    """The manifests of a manifest store (a whole 'jumb' box), in store order.

    The C2PA specification makes the last manifest in the store the active one;
    the others are the manifests of ingredients carried along with it."""
    tree = _store_tree(store)
    if tree is None:
        return []
    return [_manifest(n) for n in _manifest_nodes(tree)]


# ===========================================================================
# XMP: the IPTC digital source type and the few fields beside it.
# ===========================================================================
def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _rdf_values(el):
    out = [li.text.strip() for li in el.iter() if _local(li.tag) == 'li' and (li.text or '').strip()]
    if not out and (el.text or '').strip():
        out.append(el.text.strip())
    return out


def parse_xmp(packet):
    """IPTC/XMP fields of one XMP packet, or None when it is not well-formed XML.

    Returns {'source_type', 'creator_tool', 'creators', 'credit', 'copyright',
    'remote_manifest'}; ``remote_manifest`` is dcterms:provenance, the address
    C2PA uses for a manifest store kept outside the file."""
    start = packet.find(b'<x:xmpmeta')
    if start == -1:
        start = packet.find(b'<rdf:RDF')
    end_tag = b'</x:xmpmeta>' if packet[start:start + 10] == b'<x:xmpmeta' else b'</rdf:RDF>'
    end = packet.find(end_tag, max(start, 0))
    if start == -1 or end == -1:
        return None
    try:
        root = ET.fromstring(packet[start:end + len(end_tag)])
    except ET.ParseError:
        return None
    res = {'source_type': None, 'creator_tool': '', 'creators': [], 'credit': '',
           'copyright': '', 'remote_manifest': ''}
    dst = None
    for el in root.iter():
        for akey, aval in el.attrib.items():
            name = _local(akey)
            if name == 'DigitalSourceType' and aval:
                dst = aval
            elif name == 'CreatorTool' and aval:
                res['creator_tool'] = aval
            elif name == 'Credit' and aval:
                res['credit'] = aval
            elif name == 'provenance' and akey.startswith('{http://purl.org/dc/terms/}') and aval:
                res['remote_manifest'] = aval
            elif name == 'resource' and _local(el.tag) == 'DigitalSourceType' and aval:
                dst = aval
        name, text = _local(el.tag), (el.text or '').strip()
        if name == 'DigitalSourceType' and text:
            dst = text
        elif name == 'CreatorTool' and text:
            res['creator_tool'] = text
        elif name == 'Credit' and text:
            res['credit'] = text
        elif name == 'provenance' and el.tag.startswith('{http://purl.org/dc/terms/}') and text:
            res['remote_manifest'] = text
        elif name == 'creator':
            res['creators'].extend(_rdf_values(el))
        elif name == 'rights' and not res['copyright']:
            vals = _rdf_values(el)
            if vals:
                res['copyright'] = vals[0]
    res['source_type'] = source_type(dst)
    return res


# ===========================================================================
# Container walkers. Each records what it finds in a _Found and sets
# ``complete`` only when it reached the end of the places it reads.
# ===========================================================================
class _Found:
    def __init__(self, container):
        self.container = container
        self.complete = False
        self.stores = []       # (where, offset, bytes)
        self.xmp = []          # (where, bytes)
        self.notes = []
        self.errors = []


class _Truncated(Exception):
    """The structure points past the bytes the file holds."""


def _read(fh, n):
    if n > MAX_STORE:
        raise _Truncated(f'a block of {n} bytes is larger than {MAX_STORE}')
    data = fh.read(n)
    if len(data) != n:
        raise _Truncated('file ends inside a block')
    return data


def _jpeg(fh, size, out):
    fh.seek(2)
    jumbf = {}                          # En -> {Z: (offset, bytes)}
    ext_xmp = {}                        # guid -> {offset: bytes}
    while True:
        b = fh.read(1)
        if not b:
            raise _Truncated('JPEG ends before its first scan')
        if b != b'\xff':
            raise _Truncated('JPEG marker expected')
        marker = fh.read(1)
        while marker == b'\xff':        # fill bytes
            marker = fh.read(1)
        if not marker:
            raise _Truncated('JPEG ends inside a marker')
        m = marker[0]
        if m == 0xD9 or m == 0xDA:      # EOI, or SOS: no metadata segment is read past it
            out.complete = True
            break
        if m == 0x01 or 0xD0 <= m <= 0xD8:
            continue
        pos = fh.tell()
        seg_len = struct.unpack('>H', _read(fh, 2))[0]
        if seg_len < 2 or pos + seg_len > size:
            raise _Truncated('JPEG segment runs past the file')
        if m in (0xEB, 0xE1):
            seg = _read(fh, seg_len - 2)
            if m == 0xEB and seg[:2] == b'JP' and len(seg) >= 8:
                en = struct.unpack('>H', seg[2:4])[0]
                z = struct.unpack('>I', seg[4:8])[0]
                jumbf.setdefault(en, {})[z] = (pos - 2, seg[8:])
            elif m == 0xE1 and seg.startswith(b'http://ns.adobe.com/xap/1.0/\x00'):
                out.xmp.append(('APP1 XMP', seg[29:]))
            elif m == 0xE1 and seg.startswith(b'http://ns.adobe.com/xmp/extension/\x00') \
                    and len(seg) >= 75:
                guid = seg[35:67]
                offset = struct.unpack('>I', seg[71:75])[0]
                ext_xmp.setdefault(guid, {})[offset] = seg[75:]
        else:
            fh.seek(pos + seg_len)
    for parts in ext_xmp.values():
        out.xmp.append(('APP1 extended XMP', b''.join(parts[k] for k in sorted(parts))))
    for en in sorted(jumbf):
        packets = jumbf[en]
        zs = sorted(packets)
        first_off, first = packets[zs[0]]
        # Each continuation packet repeats the superbox's LBox/TBox (and XLBox).
        hdr = 16 if first[:4] == b'\x00\x00\x00\x01' else 8
        store = first + b''.join(packets[z][1][hdr:] for z in zs[1:])
        if _is_c2pa_store(store):
            out.stores.append((f'APP11 JUMBF (box instance {en}, {len(zs)} segments)',
                               first_off, store))


def _png(fh, size, out):
    fh.seek(8)
    while True:
        pos = fh.tell()
        hdr = fh.read(8)
        if len(hdr) < 8:
            raise _Truncated('PNG ends before IEND')
        length, ctype = struct.unpack('>I4s', hdr)
        if pos + 12 + length > size:
            raise _Truncated('PNG chunk runs past the file')
        if ctype == b'caBX':
            out.stores.append(('caBX chunk', pos, _read(fh, length)))
            fh.seek(4, 1)
        elif ctype == b'iTXt':
            data = _read(fh, length)
            fh.seek(4, 1)
            if data.startswith(b'XML:com.adobe.xmp\x00'):
                rest = data[18:]
                compressed = rest[:1] == b'\x01'
                # compression flag, method, language tag\0, translated keyword\0, text
                tail = rest[2:]
                tail = tail[tail.find(b'\x00') + 1:]
                tail = tail[tail.find(b'\x00') + 1:]
                if compressed:
                    try:
                        tail = zlib.decompress(tail)
                    except zlib.error as exc:
                        out.errors.append(f'compressed XMP iTXt: {exc}')
                        continue
                out.xmp.append(('iTXt XMP', tail))
        elif ctype == b'IEND':
            out.complete = True
            return
        else:
            fh.seek(pos + 12 + length)


_UUID_C2PA_BMFF = bytes.fromhex('d8fec3d61b0e483c92975828877ec481')
_UUID_XMP_BMFF = bytes.fromhex('be7acfcb97a942e89c71999491e3afac')


def _bmff_children(fh, start, end):
    """(type, payload offset, payload end) for each box between start and end."""
    pos = start
    while pos + 8 <= end:
        fh.seek(pos)
        hdr = fh.read(16)
        if len(hdr) < 8:
            raise _Truncated('box header past the end of the file')
        n, btype = struct.unpack('>I4s', hdr[:8])
        head = 8
        if n == 1:
            if len(hdr) < 16:
                raise _Truncated('large box header past the end of the file')
            n = struct.unpack('>Q', hdr[8:16])[0]
            head = 16
        elif n == 0:
            n = end - pos
        if n < head or pos + n > end:
            raise _Truncated(f'box {btype!r} runs past its parent')
        yield btype, pos + head, pos + n
        pos += n
    # Fewer than 8 bytes may be left over; no box fits in them, so the walk is whole.


def _bmff_c2pa(fh, start, end, out):
    fh.seek(start + 16)
    body = _read(fh, end - start - 16)
    # C2PA box: version and flags (4), purpose (null-terminated), then for a
    # "manifest" purpose an 8-byte offset to the first merkle box, then the store.
    zero = body.find(b'\x00', 4)
    purpose = body[4:zero].decode('latin-1') if zero != -1 else ''
    if purpose == 'manifest':
        store = body[zero + 1 + 8:]
        out.stores.append(('ISOBMFF C2PA uuid box', start - 8, store))
    elif purpose == 'original':
        out.notes.append('C2PA uuid box with purpose "original" (BMFF v2 merkle data)')
    elif purpose != 'merkle':
        idx = body.find(b'jumb')
        if idx >= 4:
            out.stores.append(('ISOBMFF C2PA uuid box', start - 8, body[idx - 4:]))


def _heif_meta(fh, start, end, out):
    """XMP held as a HEIF item of content type application/rdf+xml."""
    fh.seek(start)
    full = fh.read(12)
    # HEIF's meta is a FullBox; QuickTime's is not. Tell them apart by where hdlr sits.
    first = start + 4 if full[8:12] == b'hdlr' else start
    boxes = {t: (s, e) for t, s, e in _bmff_children(fh, first, end)}
    if b'iinf' not in boxes or b'iloc' not in boxes:
        return
    s, e = boxes[b'iinf']
    fh.seek(s)
    data = _read(fh, e - s)
    ver = data[0]
    pos = 4 + (2 if ver == 0 else 4)
    xmp_items = set()
    while pos + 8 <= len(data):
        n, btype = struct.unpack('>I4s', data[pos:pos + 8])
        if n < 8 or pos + n > len(data):
            break
        if btype == b'infe':
            body = data[pos + 8:pos + n]
            iver = body[0]
            if iver >= 2:
                q = 4
                item_id = struct.unpack('>H' if iver == 2 else '>I', body[q:q + (2 if iver == 2 else 4)])[0]
                q += 2 if iver == 2 else 4
                q += 2                                      # protection index
                item_type = body[q:q + 4]
                q += 4
                q = body.find(b'\x00', q) + 1               # item name
                if item_type == b'mime':
                    ctype = body[q:body.find(b'\x00', q)]
                    if ctype == b'application/rdf+xml':
                        xmp_items.add(item_id)
        pos += n
    if not xmp_items:
        return
    s, e = boxes[b'iloc']
    fh.seek(s)
    data = _read(fh, e - s)
    ver = data[0]
    sizes = struct.unpack('>H', data[4:6])[0]
    off_sz, len_sz, base_sz = sizes >> 12, (sizes >> 8) & 0xF, (sizes >> 4) & 0xF
    idx_sz = sizes & 0xF if ver in (1, 2) else 0
    pos = 6
    count_fmt = '>I' if ver == 2 else '>H'
    count = struct.unpack(count_fmt, data[pos:pos + (4 if ver == 2 else 2)])[0]
    pos += 4 if ver == 2 else 2

    def take(n):
        nonlocal pos
        v = int.from_bytes(data[pos:pos + n], 'big') if n else 0
        pos += n
        return v

    idat = boxes.get(b'idat')
    for _ in range(count):
        item_id = take(4 if ver == 2 else 2)
        method = take(2) & 0xF if ver in (1, 2) else 0
        take(2)                                             # data reference index
        base = take(base_sz)
        extents = []
        for _ in range(take(2)):
            take(idx_sz)
            extents.append((take(off_sz), take(len_sz)))
        if item_id not in xmp_items:
            continue
        parts = []
        for off, ln in extents:
            if method == 0:
                fh.seek(base + off)
            elif method == 1 and idat:
                fh.seek(idat[0] + base + off)
            else:
                out.notes.append(f'XMP item {item_id} uses construction method {method}; not read')
                parts = None
                break
            parts.append(_read(fh, ln))
        if parts is not None:
            packet = b''.join(parts)
            if packet:
                out.xmp.append((f'HEIF XMP item {item_id}', packet))
            else:
                out.notes.append(f'XMP item {item_id} is empty')


def _isobmff(fh, size, out):
    for btype, start, end in _bmff_children(fh, 0, size):
        if btype == b'uuid':
            fh.seek(start)
            kind = fh.read(16)
            if kind == _UUID_C2PA_BMFF:
                _bmff_c2pa(fh, start, end, out)
            elif kind == _UUID_XMP_BMFF:
                fh.seek(start + 16)
                out.xmp.append(('ISOBMFF XMP uuid box', _read(fh, end - start - 16)))
        elif btype == b'meta':
            try:
                _heif_meta(fh, start, end, out)
            except (_Truncated, struct.error, IndexError, ValueError) as exc:
                out.errors.append(f'meta box: {exc}')
        elif btype == b'moov':
            for ctype, cstart, cend in _bmff_children(fh, start, end):
                if ctype == b'udta':
                    for utype, ustart, uend in _bmff_children(fh, cstart, cend):
                        if utype == b'XMP_':
                            fh.seek(ustart)
                            out.xmp.append(('moov/udta/XMP_', _read(fh, uend - ustart)))
    out.complete = True


def _riff(fh, size, out):
    fh.seek(4)
    riff_size = struct.unpack('<I', fh.read(4))[0]
    end = min(8 + riff_size, size)
    pos = 12
    while pos + 8 <= end:
        fh.seek(pos)
        cid, n = struct.unpack('<4sI', fh.read(8))
        if pos + 8 + n > end:
            raise _Truncated(f'RIFF chunk {cid!r} runs past the file')
        if cid == b'C2PA':
            out.stores.append(('RIFF C2PA chunk', pos, _read(fh, n)))
        elif cid in (b'XMP ', b'_PMX'):
            out.xmp.append((f'RIFF {cid.decode("latin-1").strip()} chunk', _read(fh, n)))
        elif cid == b'LIST' and n >= 4:
            pass                                # AVI LIST chunks hold no C2PA or XMP here
        pos += 8 + n + (n & 1)
    if pos >= end:
        out.complete = True
        if 8 + riff_size > size:
            out.complete = False
            out.errors.append('RIFF size is larger than the file')


def _gif_sub_blocks(fh, raw=False):
    """The data of a sub-block chain, up to and including its terminator.
    With ``raw`` the length bytes are kept, which is how XMP is laid out in GIF."""
    parts = []
    while True:
        b = fh.read(1)
        if not b:
            raise _Truncated('GIF ends inside a sub-block chain')
        n = b[0]
        if n == 0:
            if raw:
                parts.append(b)
            return b''.join(parts)
        data = fh.read(n)
        if len(data) != n:
            raise _Truncated('GIF ends inside a sub-block')
        parts.append(b + data if raw else data)


def _gif_skip_sub_blocks(fh):
    while True:
        b = fh.read(1)
        if not b:
            raise _Truncated('GIF ends inside image data')
        if b[0] == 0:
            return
        here = fh.tell()
        fh.seek(here + b[0])


# What follows a GIF's XMP packet (XMP Part 3): 01, then FF down to 00. Read as
# sub-blocks from anywhere in the packet, it lands on the terminator after it.
_GIF_XMP_TRAILER = bytes([1]) + bytes(range(255, -1, -1))


def _gif_xmp(raw):
    """The XMP packet of a GIF's XMP application extension, from its data as it lies
    (length bytes kept, terminator included). The XMP specification writes the packet
    raw, then the magic trailer. c2pa-rs 0.91 writes packet and trailer as data
    sub-blocks, a length byte every 255 bytes, so those are taken out."""
    if raw.endswith(_GIF_XMP_TRAILER + b'\x00'):
        return raw[:-len(_GIF_XMP_TRAILER) - 1]
    parts, i = [], 0
    while i < len(raw) and raw[i]:
        parts.append(raw[i + 1:i + 1 + raw[i]])
        i += 1 + raw[i]
    return b''.join(parts).removesuffix(_GIF_XMP_TRAILER)


def _gif(fh, size, out):
    fh.seek(10)
    flags = fh.read(1)[0]
    fh.seek(13)
    if flags & 0x80:
        fh.seek(3 * (2 << (flags & 7)), 1)
    while True:
        b = fh.read(1)
        if not b:
            raise _Truncated('GIF ends before its trailer')
        if b == b'\x3b':
            out.complete = True
            return
        if b == b'\x2c':
            desc = fh.read(9)
            if len(desc) != 9:
                raise _Truncated('GIF ends inside an image descriptor')
            if desc[8] & 0x80:
                fh.seek(3 * (2 << (desc[8] & 7)), 1)
            fh.seek(1, 1)                                   # LZW minimum code size
            _gif_skip_sub_blocks(fh)
        elif b == b'\x21':
            label = fh.read(1)
            if label == b'\xff':
                pos = fh.tell() - 2
                head = fh.read(12)
                if len(head) != 12 or head[0] != 11:
                    raise _Truncated('GIF application extension is short')
                ident = head[1:12]
                if ident[:8] == b'C2PA_GIF':
                    out.stores.append(('GIF C2PA_GIF application extension', pos,
                                       _gif_sub_blocks(fh)))
                elif ident == b'XMP DataXMP':
                    raw = _gif_sub_blocks(fh, raw=True)
                    out.xmp.append(('GIF XMP application extension', _gif_xmp(raw)))
                else:
                    _gif_skip_sub_blocks(fh)
            else:
                _gif_skip_sub_blocks(fh)
        else:
            raise _Truncated(f'GIF block 0x{b[0]:02x} is not a known block')
        if fh.tell() > size:
            raise _Truncated('GIF block runs past the file')


_TIFF_C2PA_TAG = 52545
_TIFF_XMP_TAG = 700


def _tiff(fh, size, out):
    fh.seek(0)
    head = fh.read(8)
    endian = '<' if head[:2] == b'II' else '>'
    ifd = struct.unpack(endian + 'I', head[4:8])[0]
    seen = set()
    while ifd:
        if ifd in seen or ifd + 2 > size:
            raise _Truncated('TIFF IFD chain loops or points past the file')
        seen.add(ifd)
        fh.seek(ifd)
        count = struct.unpack(endian + 'H', _read(fh, 2))[0]
        entries = _read(fh, 12 * count)
        for k in range(count):
            tag, ftype, n, value = struct.unpack(endian + 'HHI4s', entries[12 * k:12 * k + 12])
            if tag not in (_TIFF_C2PA_TAG, _TIFF_XMP_TAG):
                continue
            unit = {1: 1, 2: 1, 7: 1}.get(ftype, 1)
            length = n * unit
            if length <= 4:
                data = value[:length]
            else:
                off = struct.unpack(endian + 'I', value)[0]
                if off + length > size:
                    raise _Truncated('TIFF tag data runs past the file')
                here = fh.tell()
                fh.seek(off)
                data = _read(fh, length)
                fh.seek(here)
            if tag == _TIFF_C2PA_TAG:
                out.stores.append(('TIFF tag 52545', ifd, data))
            else:
                out.xmp.append(('TIFF tag 700', data))
        ifd = struct.unpack(endian + 'I', _read(fh, 4))[0]
    out.complete = True


def _jxl(fh, size, out):
    for btype, start, end in _bmff_children(fh, 0, size):
        if btype == b'jumb':
            fh.seek(start)
            payload = _read(fh, end - start)
            # rebuilt with an 8-byte header whatever size field the file used
            store = struct.pack('>I', 8 + len(payload)) + b'jumb' + payload
            if _is_c2pa_store(store):
                out.stores.append(('JPEG XL jumb box', start - 8, store))
        elif btype == b'xml ':
            fh.seek(start)
            out.xmp.append(('JPEG XL xml box', _read(fh, end - start)))
        elif btype == b'brob':
            fh.seek(start)
            inner = fh.read(4)
            out.notes.append(f'Brotli-compressed {inner.decode("latin-1")!r} box not read')
            if inner in (b'jumb', b'xml '):
                out.complete = False
                out.errors.append('a metadata box is Brotli-compressed and was not read')
                return
    out.complete = True


_ISOBMFF_FIRST = (b'ftyp', b'moov', b'mdat', b'wide', b'free', b'skip', b'uuid', b'pnot')
_JXL_SIGNATURE = b'\x00\x00\x00\x0cJXL \r\n\x87\n'


def _container(head):
    if head[:3] == b'\xff\xd8\xff':
        return 'jpeg', _jpeg
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png', _png
    if head[:12] == _JXL_SIGNATURE:
        return 'jxl', _jxl
    if head[:2] == b'\xff\x0a':
        return 'jxl-codestream', None
    if head[:4] == b'RIFF' and head[8:12] in (b'WEBP', b'AVI ', b'WAVE'):
        return 'riff', _riff
    if head[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif', _gif
    if head[:4] in (b'II*\x00', b'MM\x00*'):
        return 'tiff', _tiff
    if head[4:8] in _ISOBMFF_FIRST:
        return 'isobmff', _isobmff
    return None, None


def _walk(fh, size):
    head = fh.read(16)
    name, walker = _container(head)
    out = _Found(name)
    if name == 'jxl-codestream':
        out.complete = True                      # a bare codestream carries no metadata boxes
        return out
    if walker is None:
        return out
    try:
        walker(fh, size, out)
    except _Truncated as exc:
        out.complete = False
        out.errors.append(str(exc))
    except (struct.error, IndexError, ValueError) as exc:
        out.complete = False
        out.errors.append(f'{type(exc).__name__}: {exc}')
    return out


def _result(found):
    result = {'container': found.container, 'complete': found.complete,
              'stores': [], 'manifests': [], 'active_manifest': '', 'xmp': [],
              'remote_manifest': '', 'notes': list(found.notes), 'errors': list(found.errors)}
    for where, offset, store in found.stores:
        result['stores'].append({'where': where, 'offset': offset, 'size': len(store)})
    if found.stores:
        manifests = parse_store(found.stores[0][2])
        result['manifests'] = manifests
        if manifests:
            result['active_manifest'] = manifests[-1]['label']
        if len(found.stores) > 1:
            result['notes'].append(f'{len(found.stores)} manifest stores; only the first is decoded')
    for where, packet in found.xmp:
        fields = parse_xmp(packet)
        if fields is None:
            result['errors'].append(f'{where}: not well-formed XMP')
            continue
        result['xmp'].append({'where': where, **fields})
        if fields['remote_manifest'] and not result['remote_manifest']:
            result['remote_manifest'] = fields['remote_manifest']
    return result


def probe(path):
    """Walk the file at ``path`` and decode what its C2PA store and XMP state.

    Raises OSError when the file cannot be opened. Everything else (truncation,
    malformed structure, undecodable CBOR) is reported in ``errors`` and, where
    it stopped the walk, by ``complete`` being False."""
    with open(path, 'rb') as fh:
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(0)
        return _result(_walk(fh, size))


def probe_bytes(data):
    """As probe(), for bytes already in memory."""
    import io  # pylint: disable=import-outside-toplevel
    return _result(_walk(io.BytesIO(data), len(data)))
