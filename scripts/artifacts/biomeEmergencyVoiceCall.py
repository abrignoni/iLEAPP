__artifacts_v2__ = {
    "get_biomeEmergencyVoiceCall": {
        "name": "Biome - Emergency Voice Call",
        "description": "Parses emergency voice calls from the "
                       "CommCenter.Call.EmergencyVoiceCall biome stream: the emergency number "
                       "(the class's emNum field) and two short numeric strings read as a mobile "
                       "country code and a mobile network code; which network they describe "
                       "is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field mapped from a small private sample, so read the columns with that in "
                 "mind. The Call Duration, Matched Em Num Source, SIP380 Procedure and SIP380 "
                 "Redirected URN field names, and the value names of the last three, are those of the BMCommCenterEmergencyVoiceCall class, read "
                 "from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class "
                 "was read. The class reads only data version 2 (the unnamed integer the SEGB reader "
                 "returns with each entry); a record of another version, or a value outside the class's "
                 "lists, keeps its integer in the (raw) column with the name blank. Matched Em Num "
                 "Source, SIP380 Procedure and SIP380 Redirected URN were reported before as Field "
                 "4 (raw), Field 5 (raw) and Field 6 (raw), and Call Duration as Duration Seconds "
                 "(unconfirmed). The class names field 1 emNum. The published stream research lists "
                 "an Emergency Number value for this stream (Mattia Epifani, '84 Streams Later, Part 2: "
                 "Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html). "
                 "The class names fields 2 and 3 MCC and MNC; which network they describe is not "
                 "established. The class names field 7 callDuration and does not state a unit; on "
                 "the private sample it was a small integer that varied per call, consistent with "
                 "seconds. Fields 4, 5 and 6 were constant across the sample. No record of this "
                 "stream was on the tested images, so these columns were not exercised on them. "
                 "Corroborate against CallHistory.storedata where the call still exists there.",
        "paths": ('*/streams/*/CommCenter.Call.EmergencyVoiceCall/local/*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    }
}


import os
import struct
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# matchedEmNumSource, sip380Procedure and sip380RedirectedURN names, read from
# BiomeLibrary.framework BMCommCenterEmergencyVoiceCall on macOS 27.2.1 (26B131). The class
# reads only data version 2 (the unnamed int the SEGB reader returns per entry); other versions get
# no name, and so do values the class renders only as its fallback.
MATCHED_EM_NUM_SOURCE_BY_VERSION = {
    2: dict(enumerate((
        'Unknown', 'NotMatched', 'Invalid', 'Operator', 'OperatorNormalSetupWhenRoaming',
        'Carrier', 'SIM', 'NW', 'BBNV', 'BBHardcoded', 'Default', 'Test',
        'OperatorNormalSetup', 'CarrierNormalSetup', 'MCC', 'Local', 'Disambiguation',
        'Preferred',
    ))),
}
SIP380_PROCEDURE_BY_VERSION = {
    2: dict(enumerate(('Unknown', 'IMSEmergency', 'CSEmergency', 'CSNormal', 'Termination'))),
}
SIP380_REDIRECTED_URN_BY_VERSION = {
    2: dict(enumerate(('Unknown', 'Invalid', 'Police', 'Ambulance', 'FireBrigade',
                       'MarineGuard', 'MountainRescue'))),
}

TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


@artifact_processor
def get_biomeEmergencyVoiceCall(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Emergency Voice Call: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                version = getattr(record, '_unknown_value', None)
                em_num_source = protostuff.get('4', '')
                sip380_procedure = protostuff.get('5', '')
                sip380_urn = protostuff.get('6', '')
                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(protostuff.get('3', b'')),
                                  protostuff.get('7', ''),
                                  MATCHED_EM_NUM_SOURCE_BY_VERSION.get(version, {}).get(
                                      em_num_source, ''),
                                  em_num_source,
                                  SIP380_PROCEDURE_BY_VERSION.get(version, {}).get(
                                      sip380_procedure, ''),
                                  sip380_procedure,
                                  SIP380_REDIRECTED_URN_BY_VERSION.get(version, {}).get(
                                      sip380_urn, ''),
                                  sip380_urn, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Emergency Number',
                    'Mobile Country Code', 'Mobile Network Code',
                    'Call Duration', 'Matched Em Num Source', 'Matched Em Num Source (raw)',
                    'SIP380 Procedure', 'SIP380 Procedure (raw)', 'SIP380 Redirected URN',
                    'SIP380 Redirected URN (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
