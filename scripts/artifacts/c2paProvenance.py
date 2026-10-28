__artifacts_v2__ = {
    "c2paProvenance": {
        "name": "C2PA Content Provenance (AI Provenance)",
        "description": "Content-provenance metadata media files declare about themselves, read two "
                       "ways: (1) C2PA / Content Credentials manifests and (2) IPTC/XMP "
                       "DigitalSourceType tags. Reports the claim generator, edit actions, digital "
                       "source type, author/creator, credit/copyright, ingredients (prior assets), "
                       "the stated signer certificate and signing time, and an AI Generated? column "
                       "derived by this parser from the IPTC DigitalSourceType code the file states "
                       "(Yes, No or Unknown under the parser's own mapping; Yes only for the three "
                       "codes whose IPTC label or definition names generative AI). Values are read from "
                       "the file and are not cryptographically verified.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-12",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "AI Provenance",
        "notes": "Read by c2pareader (github.com/abrignoni/c2pareader), vendored as "
                 "scripts/vendor/c2pareader.py: standard library only, a JUMBF/CBOR reader for the "
                 "manifest store, an XML reader for XMP, and a COSE_Sign1, X.509 and RFC 3161 reader "
                 "for the signature. SIGNATURE CAVEAT: the signer, issuer, algorithm, validity and "
                 "signing time are read from the manifest AS STATED. Nothing is cryptographically "
                 "verified, no certificate chain is validated and no revocation is checked, so "
                 "'Signed By' is a lead to corroborate, not proof of origin. "
                 "The container is decided from the file's bytes, not its extension, and walked to "
                 "the end of its metadata (for JPEG, to the first scan): JPEG APP11 and APP1, PNG caBX and iTXt, ISOBMFF (HEIC, HEIF, AVIF, MP4, "
                 "MOV) C2PA and XMP uuid boxes, moov/udta/XMP_ and HEIF XMP items, WebP C2PA and XMP "
                 "chunks, GIF application extensions, TIFF/DNG tags 52545 and 700, and JPEG XL "
                 "jumb and xml boxes. Location in File names the place a row came from. A file "
                 "gets a row per manifest in its first manifest store (a second store, not seen on any "
                 "tested file, is not decoded) and per distinct XMP statement of a digital source type "
                 "(two packets in one file that state the same source type, creator tool, creators, "
                 "credit and rights give one row); a "
                 "file with no row is not shown to carry no provenance metadata, and a file whose "
                 "walk stopped early is counted in the log. "
                 "Digital Source Type shows IPTC's own label and the stated code, from the IPTC "
                 "Digital Source Type vocabulary (cv.iptc.org/newscodes/digitalsourcetype, release "
                 "dated 2024-10-23); a code outside it is shown as stated. AI Generated? is Yes for "
                 "trainedAlgorithmicMedia, compositeWithTrainedAlgorithmicMedia and "
                 "compositeSynthetic, whose definitions there name generative AI or a model trained "
                 "on captured content; No for the capture, scan, human edit, screen capture and "
                 "software image codes (originalPhotograph, which the cited release does not hold, "
                 "included); and Unknown for every other code, including algorithmicMedia, "
                 "composite and virtualRecording, and when a manifest states no code. When one "
                 "manifest states several codes any Yes makes the row Yes, and an Unknown code "
                 "leaves the others' result unchanged. "
                 "Manifest numbers the manifests in the store; the last is the active one, and the "
                 "earlier ones belong to the ingredients it names, which may be a prior version or a "
                 "component. The thumbnail is shown for JPEG, PNG, GIF and WebP files (GIF not "
                 "exercised on any tested file). On dexter_ios18, felix_ios17, "
                 "hc_ios18_7, hc_ios26, iphone12_ios18 and iphone14plus_ios18 the 89 rows came from "
                 "JPEG APP11 stores (8), JPEG APP1 XMP (30), HEIF XMP items (50) and PNG iTXt XMP (1), "
                 "and every row declared trainedAlgorithmicMedia (72) or "
                 "compositeWithTrainedAlgorithmicMedia (17). No file on those images held a store in an ISOBMFF, GIF, TIFF or JPEG XL container; those readers are written from the specifications and tested on synthetic files only.",
        "paths": (  # case-insensitive extensions; fnmatch '*' already spans '/', so these
                    # match media at ANY depth. Uppercase forms catch iOS defaults (.HEIC/.JPG/.MOV).
            '*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]', '*.[jJ][pP][eE]',
            '*.[pP][nN][gG]', '*.[hH][eE][iI][cC]', '*.[hH][eE][iI][fF]',
            '*.[hH][iI][fF]', '*.[aA][vV][iI][fF]', '*.[wW][eE][bB][pP]',
            '*.[jJ][xX][lL]', '*.[tT][iI][fF]', '*.[tT][iI][fF][fF]',
            '*.[dD][nN][gG]', '*.[mM][pP]4', '*.[mM][oO][vV]', '*.[mM]4[vV]',
            '*.[gG][iI][fF]',
        ),
        "output_types": "standard",
        "artifact_icon": "certificate",
        "sample_data": {
            "dexter_ios18": "82 rows",
            "felix_ios17": "1 row",
            "hc_ios18_7": "2 rows",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "iphone12_ios18": "2 rows",
            "iphone14plus_ios18": "1 row",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc
from scripts.vendor import c2pareader

_THUMBNAIL_CONTAINERS = ('jpeg', 'png', 'gif')


def _ai_str(val):
    return 'Yes' if val is True else 'No' if val is False else 'Unknown'


def _source_type_text(st):
    if not st:
        return ''
    return f"{st['label']} ({st['code']})" if st['label'] else st['uri']


def _fmt(items):
    return ', '.join(str(x) for x in items if x)


@artifact_processor
def c2paProvenance(context):
    data_headers = (
        ('Signing Time (TSA)', 'datetime'),
        ('Media', 'media'),
        'Manifest',
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
        'Signed By (stated)',
        'Certificate Issuer',
        'Certificate Validity',
        'Signature Algorithm',
        'Manifest ID',
        'Format',
        'Location in File',
        'Source File',
    )
    data_list = []
    sources = []
    incomplete = 0

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        try:
            result = c2pareader.probe(file_found)
        except OSError as ex:
            logfunc(f'C2PA: could not read {os.path.basename(file_found)}: {ex.strerror or ex}')
            continue
        if result['container'] and not result['complete']:
            incomplete += 1
        # One row per distinct XMP statement: a file can repeat the same packet
        # (two APP1 XMP segments with identical fields were seen in a JPEG).
        xmp_rows, seen = [], set()
        for x in result['xmp']:
            key = (x['source_type'] or {}).get('uri'), x['creator_tool'], tuple(x['creators']), \
                x['credit'], x['copyright']
            if x['source_type'] and key not in seen:
                seen.add(key)
                xmp_rows.append(x)
        if not result['manifests'] and not xmp_rows:
            continue

        thumb = ''
        ext = os.path.splitext(file_found)[1].lower()
        if result['container'] in _THUMBNAIL_CONTAINERS or (
                result['container'] == 'riff' and ext == '.webp'):
            thumb = check_in_media(file_found) or ''
        rel = context.get_relative_path(file_found)
        sources.append(rel)
        store_where = result['stores'][0]['where'] if result['stores'] else ''

        manifests = result['manifests']
        for i, m in enumerate(manifests, 1):
            sig = m['signature'] or {}
            # The last manifest in the store is the active one; the earlier ones
            # belong to the ingredients it names.
            state = f'{i} of {len(manifests)}'
            if len(manifests) > 1 and i == len(manifests):
                state += ' (active)'
            validity = ''
            if sig.get('not_before') or sig.get('not_after'):
                validity = f"{sig.get('not_before', '')} to {sig.get('not_after', '')} UTC"
            data_list.append((
                sig.get('signing_time', ''),
                thumb,
                state,
                _ai_str(m['ai']),
                _fmt(_source_type_text(st) for st in m['source_types']),
                'C2PA',
                m['claim_generator'],
                _fmt(m['actions']),
                _fmt(m['software_agents']),
                _fmt(m['authors']),
                '',
                m['title'],
                _fmt(ing['title'] or '(unnamed)' for ing in m['ingredients']),
                sig.get('signed_by', ''),
                sig.get('issuer', ''),
                validity,
                sig.get('alg', ''),
                m['label'],
                m['format'],
                store_where,
                rel,
            ))

        for x in xmp_rows:
            data_list.append((
                '',
                thumb,
                'IPTC tag',
                _ai_str(x['source_type']['ai']),
                _source_type_text(x['source_type']),
                'XMP/IPTC',
                x['creator_tool'],
                '',
                '',
                _fmt(x['creators']),
                _fmt([x['credit'], x['copyright']]),
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                x['where'],
                rel,
            ))

    if incomplete:
        logfunc(f'C2PA: {incomplete} file(s) could not be walked to the end of their container; '
                'a missing row there does not settle that the file holds no provenance metadata')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
