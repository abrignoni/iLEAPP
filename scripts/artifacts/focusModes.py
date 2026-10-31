__artifacts_v2__ = {
    "focusModeConfigurations": {
        "name": "Focus Mode Configurations",
        "description": "Focus modes and their triggers from the DoNotDisturb ModeConfigurations.json "
                       "file",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Focus",
        "notes": "One row per entry in data[0].modeConfigurations of ModeConfigurations.json. Created and "
                 "Last Modified are the entry's created and lastModified values, read as Unix (1970 epoch) "
                 "seconds. Source: the DNDSModeConfigurationRecord decoder in Apple's DoNotDisturbServer "
                 "framework, called on macOS 27.0.1 (26A434) with probe values, returned those values as "
                 "seconds since 1970. The iOS copy of that decoder was not called; all 44 created and "
                 "lastModified values on the 14 iOS images carrying the file are 10-digit numbers, "
                 "consistent with that reading. What each time marks is not established. Triggers lists each entry of triggers.triggers as its class followed by its "
                 "other keys as stored (for a DNDModeConfigurationScheduleTrigger: enabledSetting, start "
                 "and end hour and minute, weekdays and creationDate; for the sleeping and driving "
                 "triggers seen: enabledSetting only); one entry on dexter_ios18 had no trigger. The file "
                 "held 3 entries on abe_ios16 and dexter_ios18, 2 on iphone11_ios17 and 1 on "
                 "hickman_ios15, hc_ios18_7 and hc_ios26, and was absent on ctf2020_ios12 (iOS 12.4) and "
                 "hickman_ios14 (iOS 14.3). An entry is a configured mode, not evidence that the mode was "
                 "ever on. Columns marked (as stored) are the file's own values under the key named in the "
                 "header, as decoded by the JSON reader (JSON booleans appear as True and False); no "
                 "public source defining them was found, so what each means is not established. "
                 "ModeConfigurationsSecure.json is not read: it was present on 14 of 18 iOS images checked "
                 "and on every one of them each allowed, denied and silenced application, web application, "
                 "contact, contact group and contact type list was empty or its key was absent, so it had "
                 "no app or contact to report. Its phoneCallBypassSettings integers are not read either. Also not "
                 "read: MeDeviceStatus.json, Metrics.json (metricsByDay, "
                 "metricsByWeek and metricsByMonth dictionaries and three heartbeat timestamps), "
                 "Settings.json (present on hickman_ios14 only), Settings.sqlite, whose ZFOCUSMODE, "
                 "ZAPPLICATION and ZPERMODESETTINGS tables held no rows on the five images that carried "
                 "it, and the SyncEngineMetadata, IDSSyncEngineMetadata, AssertionSyncMetadata and "
                 "IconCache/AppInfoMetadata plists. Do Not Disturb state records are read by the "
                 "knowledgeC - Do Not Disturb and Biome - Do Not Disturb DKEvent artifacts.",
        "paths": ('*/mobile/Library/DoNotDisturb/DB/ModeConfigurations.json',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 1 row",
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
        },
    },
    "focusAssertions": {
        "name": "Focus Assertions",
        "description": "Assertion, invalidation and invalidation request records from the "
                       "DoNotDisturb Assertions.json file",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Focus",
        "notes": "One row per record in the storeAssertionRecords, storeInvalidationRecords and "
                 "storeInvalidationRequestRecords lists of Assertions.json; Record names the list. The "
                 "file held 0 to 5 records on the six of the eight sample_data images that carried it (5 on abe_ios16, 0 on "
                 "hickman_ios15) and was absent on hc_ios18_7 and hc_ios26. These counts do not amount to "
                 "a history. Assertion Start, Invalidation Time and the request time are read as Cocoa "
                 "(2001 epoch) seconds. Source: the DNDSModeAssertionStore decoder in Apple's "
                 "DoNotDisturbServer framework, called on macOS 27.0.1 (26A434) with probe values, returned "
                 "the assertion start, invalidation and invalidation request values as seconds since 2001. "
                 "The iOS copy of that decoder was not called; all 29 such values on the 11 iOS images "
                 "carrying the file are 9-digit numbers, consistent with that reading. What each time "
                 "marks is not established. Mode Name is looked up from ModeConfigurations.json by "
                 "mode identifier and was found for every invalidation record on abe_ios16, dexter_ios18 "
                 "and iphone11_ios17; ctf2020_ios12 and hickman_ios14 carry no ModeConfigurations.json, so "
                 "their rows have no name. The invalidation request records seen carry no mode identifier "
                 "or start time, so Assertion Start is blank on those rows, Invalidation Time holds "
                 "invalidationRequestDateTimestamp, Invalidation Reason holds invalidationRequestReason "
                 "and Assertion UUID holds invalidationRequestUUID. assertionDetailsUserRequested was "
                 "present only on the one assertion record, on ctf2020_ios12. Columns marked (as stored) "
                 "are the file's own values under the key named in the header, as decoded by the JSON "
                 "reader (JSON booleans appear as True and False); no public source defining them was "
                 "found, so what each means is not established. Do Not Disturb state records are read by "
                 "the knowledgeC - Do Not Disturb and Biome - Do Not Disturb DKEvent artifacts.",
        "paths": ('*/mobile/Library/DoNotDisturb/DB/Assertions.json',
                  '*/mobile/Library/DoNotDisturb/DB/ModeConfigurations.json'),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import json

from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc, \
    convert_cocoa_core_data_ts_to_utc


def _files(context, name):
    return [str(f) for f in context.get_files_found() if str(f).endswith('/' + name) or str(f) == name]


def _data(file_found):
    """The first element of the file's data list, or None when the file is not that shape."""
    try:
        with open(file_found, 'rb') as f:
            doc = json.load(f)
    except (UnicodeDecodeError, ValueError, OSError) as error:
        logfunc(f'{file_found}: not read ({type(error).__name__})')
        return None
    data = doc.get('data') if isinstance(doc, dict) else None
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        logfunc(f'{file_found}: no data record')
        return None
    return data[0]


def _unix(value):
    return convert_unix_ts_to_utc(value) if isinstance(value, (int, float)) and value else ''


def _cocoa(value):
    return convert_cocoa_core_data_ts_to_utc(value) if isinstance(value, (int, float)) and value else ''


def _trigger_text(trigger):
    """One trigger as its class followed by its other keys, as stored."""
    if not isinstance(trigger, dict):
        return str(trigger)
    parts = [str(trigger.get('class', ''))]
    parts += [f'{key}={value}' for key, value in trigger.items() if key != 'class']
    return ' '.join(parts)


def _modes(data):
    modes = data.get('modeConfigurations') if isinstance(data, dict) else None
    return modes if isinstance(modes, dict) else {}


@artifact_processor
def focusModeConfigurations(context):
    data_headers = (('Created', 'datetime'), ('Last Modified', 'datetime'), 'Mode Name', 'Mode Identifier',
                    'semanticType (as stored)', 'Triggers (as stored)', 'automaticallyGenerated (as stored)',
                    'Last Modified By Version')
    data_list = []
    sources = []
    for file_found in _files(context, 'ModeConfigurations.json'):
        data = _data(file_found)
        if data is None:
            continue
        sources.append(file_found)
        for key, config in _modes(data).items():
            if not isinstance(config, dict):
                continue
            mode = config.get('mode') if isinstance(config.get('mode'), dict) else {}
            triggers = (config.get('triggers') or {}).get('triggers') if isinstance(config.get('triggers'), dict) else None
            data_list.append((_unix(config.get('created')), _unix(config.get('lastModified')),
                              mode.get('name', ''), mode.get('modeIdentifier', key), mode.get('semanticType', ''),
                              '; '.join(_trigger_text(t) for t in triggers or []),
                              config.get('automaticallyGenerated', ''), config.get('lastModifiedByVersion', '')))
    return data_headers, data_list, '\n'.join(sources)


def _mode_names(context):
    names = {}
    for file_found in _files(context, 'ModeConfigurations.json'):
        data = _data(file_found)
        for key, config in _modes(data).items():
            mode = config.get('mode') if isinstance(config, dict) and isinstance(config.get('mode'), dict) else {}
            names[mode.get('modeIdentifier', key)] = mode.get('name', '')
    return names


def _assertion_cols(assertion):
    """Start time, mode identifier, client and details of an assertion dictionary."""
    assertion = assertion if isinstance(assertion, dict) else {}
    details = assertion.get('assertionDetails') if isinstance(assertion.get('assertionDetails'), dict) else {}
    source = assertion.get('assertionSource') if isinstance(assertion.get('assertionSource'), dict) else {}
    mode_id = details.get('assertionDetailsModeIdentifier', assertion.get('assertionDetailsModeIdentifier', ''))
    client = source.get('assertionClientIdentifier', assertion.get('assertionClientIdentifier', ''))
    reason = details.get('assertionDetailsReason', '')
    user_requested = details.get('assertionDetailsUserRequested',
                                 assertion.get('assertionDetailsUserRequested', ''))
    return (_cocoa(assertion.get('assertionStartDateTimestamp')), mode_id, client, reason, user_requested,
            assertion.get('assertionUUID', ''))


@artifact_processor
def focusAssertions(context):
    data_headers = (('Assertion Start', 'datetime'), ('Invalidation Time', 'datetime'), 'Record', 'Mode Name',
                    'Mode Identifier', 'Client Identifier', 'assertionDetailsReason (as stored)',
                    'assertionDetailsUserRequested (as stored)', 'Invalidation Reason (as stored)',
                    'Invalidated By Client', 'Assertion UUID')
    data_list = []
    sources = []
    names = None
    for file_found in _files(context, 'Assertions.json'):
        data = _data(file_found)
        if data is None:
            continue
        sources.append(file_found)
        if names is None:
            names = _mode_names(context)
        for record in data.get('storeAssertionRecords') or []:
            start, mode_id, client, reason, user_requested, uuid = _assertion_cols(record)
            data_list.append((start, '', 'assertion', names.get(mode_id, ''), mode_id, client, reason,
                              user_requested, '', '', uuid))
        for record in data.get('storeInvalidationRecords') or []:
            if not isinstance(record, dict):
                continue
            start, mode_id, client, reason, user_requested, uuid = _assertion_cols(
                record.get('invalidationAssertion'))
            by = record.get('invalidationSource') if isinstance(record.get('invalidationSource'), dict) else {}
            data_list.append((start, _cocoa(record.get('invalidationDateTimestamp')), 'invalidation',
                              names.get(mode_id, ''), mode_id, client, reason, user_requested,
                              record.get('invalidationReason', ''), by.get('assertionClientIdentifier', ''),
                              uuid))
        for record in data.get('storeInvalidationRequestRecords') or []:
            if not isinstance(record, dict):
                continue
            by = record.get('invalidationRequestSource') if isinstance(record.get('invalidationRequestSource'),
                                                                       dict) else {}
            data_list.append(('', _cocoa(record.get('invalidationRequestDateTimestamp')), 'invalidation request',
                              '', '', '', '', '', record.get('invalidationRequestReason', ''),
                              by.get('assertionClientIdentifier', ''), record.get('invalidationRequestUUID', '')))
    return data_headers, data_list, '\n'.join(sources)
