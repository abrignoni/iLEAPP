__artifacts_v2__ = {
    "textinputTyping": {
        "name": "Text Input Messages",
        "description": "Reads .desdata records of com.apple.TextInput.TypingDESPlugin. No tested image holds one, so this artifact has not been run against data and the meaning of its columns is not established",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Text Input Messages",
        "notes": "No com.apple.TextInput.TypingDESPlugin records were found under DES/Records in the corpus images and public path listings checked; the number of images and the date of that check are not recorded here. The system plugin binary ships under System/Library/DistributedEvaluation on the images checked, but no image carries recorded .desdata for it, so none of the images checked returns rows. The parser is unexercised: it reads only the last alignedEntries item, reports the timestamp as stored, and adds one row per file holding the contextBeforeInput text in the Text column and the text True in the contextBeforeInput column.",
        "paths": ('*/DES/Records/com.apple.TextInput.TypingDESPlugin/*.desdata',),
        "output_types": "standard",
        "artifact_icon": "typography"
    }
}

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, logfunc

_PLIST_ERRORS = (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                 nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                 nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError)


@artifact_processor
def textinputTyping(context):
    data_headers = ('Timestamp', 'Sender Identifier', 'Text', 'contextBeforeInput')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            try:
                deserialized_plist = nd.deserialize_plist(f)
            except _PLIST_ERRORS as ex:
                logfunc(f'Failed to read {file_found}: {ex}')
                continue

        aligned = deserialized_plist.get('alignedEntries') if isinstance(deserialized_plist, dict) else None
        if not aligned:
            continue

        finalvalue = ''
        testrun = aligned[-1]
        for key, value in testrun.get('originalWord', {}).items():
            if key == 'documentState':
                finalvalue = value.get('contextBeforeInput', '')
            elif key == 'keyboardState':
                history = value.get('inputContextHistory', {})
                for entry in history.get('pendingEntries', []):
                    data_list.append((entry.get('timestamp'), entry.get('senderIdentifier'),
                                      entry.get('text'), ''))

        data_list.append(('', '', finalvalue, 'True'))
        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
