__artifacts_v2__ = {
    "get_cnaAutocompleteFeedback": {
        "name": "Biome - Contact Autocomplete Feedback (CNA)",
        "description": "Parses contact autocomplete feedback records (stream _PSCNAutocompleteFeedback) from the "
                       "SEGB stream files at CoreDuet/People/Feedback/CNA. Each record is a feedback event from the "
                       "recipient autocomplete facility used by apps such as Messages and FaceTime, and can include "
                       "suggested contact names, handles (phone numbers), conversation identifiers, and the stated "
                       "suggestion reason.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Biome",
        "notes": "Biome-format SEGB stream stored outside the Biome folder; location reported by Mattia Epifani. "
                 "A suggested contact in this stream reflects the system offering a suggestion; it does not by "
                 "itself establish that the user selected the suggestion or communicated with that contact. "
                 "Feedback Type labels are derived from which payload field is populated for each observed type "
                 "value; type values not observed in test data are reported as numbers. The stream metadata "
                 "declares a 28-day maximum age, but records in test images persisted for many months beyond "
                 "that.",
        "paths": ('*/mobile/Library/CoreDuet/People/Feedback/CNA/local/*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 30 rows",
            "otto_ios17": "iOS 17.5.1 | 230 rows",
            "hc_ios18_7": "iOS 18.7.8 | 185 rows",
            "hc_ios26": "iOS 26 | 16 rows; recipient identifier is <UUID>:ABPerson instead of the raw handle",
        }
    }
}


import os
from datetime import datetime, timezone
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, get_plist_content

FEEDBACK_TYPES = {
    0: 'Entered',
    1: 'Exited',
    2: 'Suggestions Vended',
    4: 'Typed Handle',
    5: 'Erased Handle',
}


def _utc(value):
    """Set UTC tzinfo on datetime objects; anything else becomes None."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc)
    return None


def _compact(value):
    """Render a payload sub-dictionary as 'key=value; ...', skipping empty values."""
    if not isinstance(value, dict):
        return str(value) if value not in ('', None) else ''
    parts = [f'{k}={v}' for k, v in value.items() if v not in ('', None)]
    return '; '.join(parts)


@artifact_processor
def get_cnaAutocompleteFeedback(context):

    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                payload = get_plist_content(record.data)
                if not isinstance(payload, dict) or not payload:
                    continue

                report_time = _utc(payload.get('reportTime'))
                app = payload.get('bundleIdentifier', '')
                feedback_type = payload.get('feedbackType')
                feedback_label = FEEDBACK_TYPES.get(feedback_type, str(feedback_type))
                is_implicit = payload.get('isImplicit', '')

                interaction_parts = []
                for key in ('entered', 'exited', 'typedHandle', 'tappedSuggestion', 'erasedHandle'):
                    compacted = _compact(payload.get(key))
                    if compacted:
                        interaction_parts.append(f'{key}: {compacted}')
                interaction = ' | '.join(interaction_parts)

                vended = payload.get('vendedSuggestions')
                suggestions = vended.get('suggestions', []) if isinstance(vended, dict) else []

                base_row = [ts, report_time, record.state.name, app, feedback_label, is_implicit]
                tail_row = [interaction, filename, record.data_start_offset]

                suggestion_rows = []
                for suggestion in suggestions:
                    if not isinstance(suggestion, dict):
                        continue
                    conversation_id = suggestion.get('conversationIdentifier', '')
                    reason = suggestion.get('reason', '')
                    group_name = suggestion.get('groupName', '')
                    family = suggestion.get('familySuggestion', '')
                    recipients = suggestion.get('recipients')
                    if not isinstance(recipients, list) or not recipients:
                        recipients = [{}]
                    for recipient in recipients:
                        if not isinstance(recipient, dict):
                            recipient = {}
                        suggestion_rows.append(base_row + [
                            recipient.get('displayName', ''),
                            recipient.get('handle', ''),
                            recipient.get('handleType', ''),
                            recipient.get('identifier', ''),
                            conversation_id,
                            reason,
                            group_name,
                            family,
                        ] + tail_row)

                if suggestion_rows:
                    data_list.extend(suggestion_rows)
                else:
                    data_list.append(base_row + ['', '', '', '', '', '', '', ''] + tail_row)

            elif record.state == EntryState.Deleted:
                data_list.append([ts, None, record.state.name, None, None, None, None, None, None, None,
                                  None, None, None, None, None, filename, record.data_start_offset])

    data_list.sort(key=lambda row: row[0])

    data_headers = (('SEGB Timestamp', 'datetime'), ('Report Time', 'datetime'), 'SEGB State', 'App',
                    'Feedback Type', 'Is Implicit', 'Suggested Name', 'Suggested Handle', 'Handle Type',
                    'Recipient Identifier', 'Conversation ID', 'Suggestion Reason', 'Group Name',
                    'Family Suggestion', 'Interaction Detail', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
