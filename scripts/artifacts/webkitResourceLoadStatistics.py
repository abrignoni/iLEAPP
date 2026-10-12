"""WebKit Intelligent Tracking Prevention domain statistics and relationships."""

import json
import math
import sqlite3
from datetime import date

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.webkit_helpers import (
    OWNER_HEADERS, OWNER_PATHS, WebKitOwnerResolver, evidence_path, unix_timestamp,
)


_PATHS = (
    '*/ResourceLoadStatistics/observations.db*',
    '*/WebKit/*observations.db*',
) + OWNER_PATHS
_NOTES = (
    'These are WebKit tracking-prevention statistics, not a complete browsing history. '
    'A domain may be observed as a subresource. Interaction flags do not establish a '
    'particular link click. Zero, negative and invalid time values remain in Stored Values '
    'and are not rendered as dates. Database reads include acquired WAL files. '
    'Shared-group identifiers and plugin identifiers are reported as stored; no host app '
    'is inferred. Source: https://github.com/WebKit/WebKit/blob/main/Source/WebKit/'
    'NetworkProcess/Classifier/ResourceLoadStatisticsStore.cpp'
)

__artifacts_v2__ = {
    'webkit_observed_domains': {
        'name': 'WebKit - Observed Domains',
        'description': 'Observed domain statistics from each acquired observations.db.',
        'author': '', 'creation_date': '2026-10-11', 'last_update_date': '2026-10-11',
        'requirements': 'none', 'category': 'Browser', 'notes': _NOTES,
        'paths': _PATHS, 'output_types': 'standard', 'artifact_icon': 'world',
    },
    'webkit_operating_dates': {
        'name': 'WebKit - Operating Dates',
        'description': 'Calendar dates retained by the WebKit statistics store.',
        'author': '', 'creation_date': '2026-10-11', 'last_update_date': '2026-10-11',
        'requirements': 'none', 'category': 'Browser',
        'notes': _NOTES + ' OperatingDates.month is zero-based. Dates are date-only '
                 'values, without a time or timezone, and do not prove foreground app use.',
        'paths': _PATHS, 'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'calendar',
    },
    'webkit_domain_relationships': {
        'name': 'WebKit - Domain Relationships',
        'description': 'Domain references in statistics tables, resolved using declared '
                       'foreign keys to ObservedDomains while retaining original fields.',
        'author': '', 'creation_date': '2026-10-11', 'last_update_date': '2026-10-11',
        'requirements': 'none', 'category': 'Browser', 'notes': _NOTES,
        'paths': _PATHS, 'output_types': 'standard', 'artifact_icon': 'arrows-exchange',
    },
}


def _quote(name):
    return '"' + name.replace('"', '""') + '"'


def _json_value(value):
    if isinstance(value, bytes):
        return {'hex': value.hex()}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def _stored_values(row):
    return json.dumps({key: _json_value(row[key]) for key in row.keys()},
                      ensure_ascii=False, sort_keys=True, allow_nan=False)


def _databases(context):
    files = tuple(dict.fromkeys(map(str, context.get_files_found())))
    resolver = WebKitOwnerResolver(context, files)
    for path in sorted(files):
        if path.replace('\\', '/').rsplit('/', 1)[-1] != 'observations.db':
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        db.row_factory = sqlite3.Row
        try:
            tables = {row[0].lower(): row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            yield path, db, tables, resolver.resolve(path)
        except sqlite3.DatabaseError as error:
            logfunc(f'Could not read WebKit statistics {evidence_path(context, path)}: {error}')
        finally:
            db.close()


def _get(row, field):
    fields = {key.lower(): key for key in row.keys()}
    key = fields.get(field.lower())
    return row[key] if key is not None else None


@artifact_processor
def webkit_observed_domains(context):
    headers = (
        ('Last Seen', 'datetime'), ('Most Recent User Interaction', 'datetime'),
        ('Most Recent Web Push Interaction', 'datetime'), 'Domain', 'Domain ID',
        'Had User Interaction', 'Is Prevalent', 'Is Very Prevalent', 'Grandfathered',
        'Data Records Removed', 'First Party Accesses Due To User Interaction',
        'First Party Accesses Due To Storage Access API', 'Scheduled For Data Removal',
    ) + OWNER_HEADERS + ('Stored Values', 'Source File')
    result = context.create_artifact_result(headers=headers)
    sources = set()
    for path, db, tables, owner in _databases(context):
        table = tables.get('observeddomains')
        if not table:
            continue
        relative = evidence_path(context, path)
        sources.add(relative)
        for row in db.execute(f'SELECT * FROM {_quote(table)}'):
            result.add_row((
                unix_timestamp(_get(row, 'lastSeen')),
                unix_timestamp(_get(row, 'mostRecentUserInteractionTime')),
                unix_timestamp(_get(row, 'mostRecentWebPushInteractionTime')),
                _get(row, 'registrableDomain'), _get(row, 'domainID'),
                _get(row, 'hadUserInteraction'), _get(row, 'isPrevalent'),
                _get(row, 'isVeryPrevalent'), _get(row, 'grandfathered'),
                _get(row, 'dataRecordsRemoved'),
                _get(row, 'timesAccessedAsFirstPartyDueToUserInteraction'),
                _get(row, 'timesAccessedAsFirstPartyDueToStorageAccessAPI'),
                _get(row, 'isScheduledForAllButCookieDataRemoval'),
            ) + owner + (_stored_values(row), relative))
    result.set_source_path('\n'.join(sorted(sources)))
    return result


@artifact_processor
def webkit_operating_dates(context):
    headers = (('Operating Date', 'date'), 'Year', 'Month (Zero-Based)', 'Month Day',
               'Date Status') + OWNER_HEADERS + ('Stored Values', 'Source File')
    result = context.create_artifact_result(headers=headers)
    sources = set()
    for path, db, tables, owner in _databases(context):
        table = tables.get('operatingdates')
        if not table:
            continue
        relative = evidence_path(context, path)
        sources.add(relative)
        for row in db.execute(f'SELECT * FROM {_quote(table)}'):
            year, month, day = (_get(row, field) for field in ('year', 'month', 'monthDay'))
            converted = None
            try:
                if all(isinstance(value, int) and not isinstance(value, bool)
                       for value in (year, month, day)):
                    converted = date(year, month + 1, day)
            except ValueError:
                pass
            result.add_row((converted, year, month, day,
                            'Valid' if converted else 'Invalid stored date')
                           + owner + (_stored_values(row), relative))
    result.set_source_path('\n'.join(sorted(sources)))
    return result


@artifact_processor
def webkit_domain_relationships(context):
    headers = (('Last Updated', 'datetime'), 'Relationship Table',
               'Domain 1 Field', 'Domain 1', 'Domain 2 Field', 'Domain 2',
               'Resolved Domain Fields') + OWNER_HEADERS + ('Stored Values', 'Source File')
    result = context.create_artifact_result(headers=headers)
    sources = set()
    for path, db, tables, owner in _databases(context):
        observed = tables.get('observeddomains')
        if not observed:
            continue
        domains = {}
        for row in db.execute(f'SELECT * FROM {_quote(observed)}'):
            domains[_get(row, 'domainID')] = _get(row, 'registrableDomain')
        relative = evidence_path(context, path)
        for table in sorted(tables.values()):
            if table.lower() in ('observeddomains', 'operatingdates'):
                continue
            references = {row['from'] for row in db.execute(
                f'PRAGMA foreign_key_list({_quote(table)})')
                if row['table'].lower() == 'observeddomains'
                and (row['to'] is None or row['to'].lower() == 'domainid')}
            if not references:
                continue
            sources.add(relative)
            for row in db.execute(f'SELECT * FROM {_quote(table)}'):
                resolved = {key: domains.get(row[key]) for key in row.keys() if key in references}
                fields = list(resolved)
                pairs = tuple(value for key in fields[:2] for value in (key, resolved[key]))
                pairs += ('',) * (4 - len(pairs))
                result.add_row((unix_timestamp(_get(row, 'lastUpdated')), table)
                               + pairs + (json.dumps(resolved, ensure_ascii=False, sort_keys=True),)
                               + owner + (_stored_values(row), relative))
    result.set_source_path('\n'.join(sorted(sources)))
    return result
