__artifacts_v2__ = {
    "ne_configurations": {
        "name": "Sysdiagnose - Network Extension Configurations",
        "description": "Configurations stored in com.apple.networkextension.plist of a sysdiagnose (logs/Networking): "
                       "name, identifier, grade, the service types that hold settings, and the path rule count",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "com.apple.networkextension.plist is an NSKeyedArchiver archive holding a list of "
            "dictionaries: one dictionary per configuration, keyed by the configuration's identifier "
            "(a UUID), plus a version, an index and a generation entry. One row per configuration. Name, "
            "Identifier, Grade, Application and Application Name are as stored (blank when empty). "
            "Service Types lists the keys among VPN, AppVPN, AlwaysOnVPN, ContentFilter, DNSProxy, "
            "DNSSettings, AppPush, Relay, Hotspot and URLFilter whose value is not empty, so a "
            "configuration with no listed type holds none of those settings. Service Settings is the "
            "content of those values as JSON, with binary values replaced by their length, so it can be "
            "long. Path Rules Enabled and Path Rule Count come from the PathController entry. Observed on "
            "three sysdiagnoses (two iOS 26.6 of one device, one iOS 26.6.2 of another): two configurations on each device, com.apple.commcenter.ne."
            "cellularusage and com.apple.preferences.networkprivacy, both with an empty Service Types. "
            "The three contributor sysdiagnoses held none of these. The iOS 26.5.2 corpus sysdiagnose holds one VPN and one AppVPN configuration and the iOS 26.6 (23G71) one holds one VPN configuration; their Service Settings were produced as stored and were not checked against the device's own configuration screen. Content filter and DNS proxy configurations remain unexercised. "
            "On the three contributor sysdiagnoses Application, Application Name, Service Types and Service Settings were empty on both configurations and Grade (2) and Path Rules Enabled (True) were uniform; the corpus VPN and AppVPN configurations carry Grade 1, a blank Path Rules Enabled and a non-empty Application. "
            "The names of the two configurations above are shown as stored and what each controls is "
            "not established by the file. Also in the file and not reported: the index mapping user "
            "identifiers to configurations and the signature entry. The companion file "
            "com.apple.networkextension.uuidcache.plist is not reported. An "
            "empty result is not evidence that no VPN or filter was configured. On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data."
        ),
        "paths": (
            '*/com.apple.networkextension.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield-lock",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 1 row",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 2 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 2 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 4 rows",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 3 rows",
        },
    },
    "ne_path_rules": {
        "name": "Sysdiagnose - Network Extension Path Rule Groups",
        "description": "Path rules of each Network Extension configuration in a sysdiagnose, grouped by the "
                       "behavior values stored on the rule, with the signing identifiers of small groups",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": (
            "Each configuration's PathController holds a list of rules, one per signing identifier "
            "(an app or process). One row per configuration and combination of Cellular Behavior, "
            "WiFi Behavior, Deny All, Deny Cellular Fallback, Deny Multicast and No Divert DNS, with the "
            "number of rules in the group. The behavior values are integers shown as stored; their "
            "meaning is not established by the file. Signing Identifiers lists the identifiers of a "
            "group of 25 rules or fewer, and is blank for a larger group, whose members are in the "
            "source file. Deny All, Deny Cellular Fallback and No Divert DNS were false in every rule of the iOS 26.6.2 file. On the iOS 13.3.1 and 14.3 corpus files the Deny All key is absent and the column is blank. Cellular Behavior and WiFi Behavior held identical values in every group of the tested files. In the tested file the 163 rules of one configuration had one combination of "
            "values, and the 84 rules of the other had two combinations (80 and 4 rules), so a group "
            "is the unit that stands out and a list of every rule would repeat the same values. A rule "
            "list is not evidence of which apps are installed or have used the network: rule lists can "
            "include identifiers the system ships. Observed on three sysdiagnoses: two iOS 26.6 (23G71) of one device and one iOS 26.6.2 (23G90) of another device. On five corpus sysdiagnoses (iOS 13.3.1, 14.3, 17.3, 26.5.2 and 26.6 build 23G71) the artifact ran without error and reported the rows listed in sample_data."
        ),
        "paths": (
            '*/com.apple.networkextension.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "network",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 sysdiagnose | 1 row",
            "hickman_ios14_sysdiag": "iOS 14.3 sysdiagnose | 3 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 3 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 3 rows",
            "hc_ios26_sysdiag": "iOS 26.6 (23G71) sysdiagnose | 2 rows",
        },
    },
}

import collections
import json
import tarfile
import zlib

from scripts.ilapfuncs import artifact_processor, get_plist_content, get_sysdiagnose_files, logfunc

_READ_ERRORS = (OSError, EOFError, tarfile.TarError, zlib.error, ValueError)

_SERVICE_KEYS = ('VPN', 'AppVPN', 'AlwaysOnVPN', 'ContentFilter', 'DNSProxy', 'DNSSettings',
                 'AppPush', 'Relay', 'Hotspot', 'URLFilter')
_GROUP_LIST_LIMIT = 25


def _plain(value):
    """JSON-safe copy of a value; bytes become a length marker."""
    if isinstance(value, bytes):
        return f'<{len(value)} bytes>'
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _configurations(file_obj, rel):
    """Return [(identifier, config dict)] from a networkextension archive; None when unreadable."""
    try:
        data = file_obj.read()
        archive = get_plist_content(data)
    except _READ_ERRORS as ex:
        logfunc(f'Failed to read {rel}: {ex}')
        return None
    if not isinstance(archive, list):
        return None
    found = []
    for item in archive:
        if not isinstance(item, dict):
            continue
        for key, value in item.items():
            if isinstance(value, dict) and 'Name' in value and 'Identifier' in value:
                found.append((str(key), value))
    return found


def _text(value):
    return '' if value is None else str(value)


def _each_file(context):
    for file_obj, source_path in get_sysdiagnose_files(
            context.get_files_found(), 'com.apple.networkextension.plist', text_mode=False):
        rel = context.get_relative_path(source_path)
        configs = _configurations(file_obj, rel)
        if configs is not None:
            yield source_path, rel, configs


@artifact_processor
def ne_configurations(context):
    data_headers = ('Name', 'Identifier', 'Grade', 'Application', 'Application Name', 'Service Types',
                    'Service Settings', 'Path Rules Enabled', 'Path Rule Count', 'Source File')
    data_list = []
    sources = []
    for source_path, rel, configs in _each_file(context):
        sources.append(source_path)
        for _key, config in configs:
            types = [k for k in _SERVICE_KEYS if config.get(k)]
            settings = json.dumps({k: _plain(config[k]) for k in types}, sort_keys=True) if types else ''
            controller = config.get('PathController') if isinstance(config.get('PathController'), dict) else {}
            rules = controller.get('Rules') if isinstance(controller.get('Rules'), list) else []
            enabled = controller.get('Enabled')
            data_list.append((
                _text(config.get('Name')), _text(config.get('Identifier')), _text(config.get('Grade')),
                _text(config.get('Application')), _text(config.get('ApplicationName')),
                ', '.join(types), settings, '' if enabled is None else str(enabled), len(rules), rel))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ne_path_rules(context):
    data_headers = ('Configuration', 'Cellular Behavior (as stored)', 'WiFi Behavior (as stored)',
                    'Deny All', 'Deny Cellular Fallback', 'Deny Multicast', 'No Divert DNS',
                    'Rule Count', 'Signing Identifiers', 'Source File')
    data_list = []
    sources = []
    for source_path, rel, configs in _each_file(context):
        sources.append(source_path)
        for _key, config in configs:
            controller = config.get('PathController') if isinstance(config.get('PathController'), dict) else {}
            rules = controller.get('Rules') if isinstance(controller.get('Rules'), list) else []
            groups = collections.OrderedDict()
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                key = tuple(_text(rule.get(k)) for k in (
                    'CellularBehavior', 'WiFiBehavior', 'DenyAll', 'DenyCellularFallback',
                    'DenyMulticast', 'NoDivertDNS'))
                groups.setdefault(key, []).append(_text(rule.get('SigningIdentifier')))
            for key, members in sorted(groups.items(), key=lambda item: -len(item[1])):
                listed = ', '.join(sorted(members)) if len(members) <= _GROUP_LIST_LIMIT else ''
                data_list.append((_text(config.get('Name')),) + key + (len(members), listed, rel))
    return data_headers, data_list, '\n'.join(sources)
