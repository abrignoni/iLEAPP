#!/usr/bin/env python3
"""Checks a generated report for column-level defects that only the output reveals.

The other checkers in this directory read artifact source. These findings cannot be seen
there: whether a column is populated, whether it varies, and whether one column is a copy
of another are properties of a run against real data.

Every finding here has shipped in a merged artifact at least once:

  empty-column       a column with no value on any row. Either the query never fills it or
                     the field is not what it was taken for.
  constant-column    one distinct value across every row. Sometimes the data is uniform,
                     and sometimes a derivation never ran.
  identical-columns  two columns holding the same value on every row, where the values
                     vary. A derived column that equals its input is a no-op: the classic
                     case is a basename split on the wrong path separator.
  sparse-lead        the first column is a timestamp that is empty on most rows, so the
                     table leads with a blank and sorts on nothing.

A column is NOT reported when the artifact's own notes name it. That is the documented way
to keep a uniform column: say in the notes that it was uniform and why it still earns its
place. So this check enforces the rule rather than second-guessing it.

Scaling is checked separately with --compare, which takes the report of the same profile
run against a tree holding the same container twice plus a second tenant. Per artifact:

  exactly 2x   correct
  1x           a second tenant's rows are being dropped or merged
  3x           the duplicate storage views are not collapsing
  more than 2x a decoy or foreign container is leaking in

Usage:
  check_artifact_output.py REPORT_DIR [--compare MULTI_REPORT_DIR] [--strict]

REPORT_DIR is a report folder, the one holding "_TSV Exports". Exits 0 unless --strict.
"""

import argparse
import ast
import csv
import glob
import os
import re
import sys

MIN_ROWS_FOR_CONSTANT = 3
SPARSE_LEAD_FRACTION = 0.5
# Columns that are bookkeeping rather than findings.
IGNORED = {'source file', 'source files', 'source path', 'source paths'}
# A header often carries a qualifier the prose does not repeat, so a note saying
# "Disappearing TTL was empty" should silence a column headed "Disappearing TTL (as stored)".
QUALIFIER = re.compile(r'\s*\((?:as stored|seconds|utc|local)[^)]*\)\s*$', re.I)


def named_in(notes, *columns):
    """Whether the notes name every one of these columns, qualifier or not."""
    lowered = notes.lower()
    for column in columns:
        bare = QUALIFIER.sub('', column).strip().lower()
        if not bare or bare not in lowered:
            return False
    return True


def artifact_notes(repo_root):
    """{artifact name: notes} for every statically readable artifact in the repo."""
    notes = {}
    pattern = os.path.join(repo_root, 'scripts', 'artifacts', '*.py')
    for path in sorted(glob.glob(pattern)):
        try:
            tree = ast.parse(open(path, encoding='utf-8', errors='replace').read())
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if getattr(node.targets[0], 'id', '') != '__artifacts_v2__':
                continue
            try:
                block = ast.literal_eval(node.value)
            except ValueError:
                continue
            for entry in block.values():
                if isinstance(entry, dict) and entry.get('name'):
                    notes[entry['name']] = entry.get('notes', '') or ''
    return notes


def allow_oversized_fields():
    """Accept cells over csv's 128KB default; a rendered message body exceeds it.

    sys.maxsize overflows the C long on some platforms, so halve until accepted.
    """
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 2


allow_oversized_fields()


def read_table(path):
    """(column names, rows) for one tab separated export."""
    with open(path, encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        rows = list(reader)
    columns = [c for c in (reader.fieldnames or []) if c]
    return columns, rows


def looks_like_a_time(values):
    """Whether a column's values look like rendered timestamps."""
    for value in values:
        if value and value[:4].isdigit() and '-' in value[:10]:
            return True
    return False


def check_table(columns, rows, notes):
    """The findings for one artifact's export."""
    findings = []
    if not rows:
        return findings
    mentioned = notes.lower()
    total = len(rows)

    series = {c: [(r.get(c) or '') for r in rows] for c in columns}
    for column in columns:
        if column.lower() in IGNORED:
            continue
        values = series[column]
        filled = sum(1 for v in values if v != '')
        distinct = len(set(values))
        if named_in(mentioned, column):
            continue
        if filled == 0:
            findings.append(('empty-column', f'{column!r} has no value on any of {total} rows'))
        elif distinct == 1 and total >= MIN_ROWS_FOR_CONSTANT:
            findings.append(('constant-column',
                             f'{column!r} holds one value on all {total} rows: '
                             f'{values[0][:40]!r}'))

    for index, first in enumerate(columns):
        if first.lower() in IGNORED:
            continue
        for second in columns[index + 1:]:
            if second.lower() in IGNORED:
                continue
            left, right = series[first], series[second]
            if named_in(mentioned, first, second):
                continue
            if left == right and len(set(left)) > 1 and any(v != '' for v in left):
                findings.append(('identical-columns',
                                 f'{first!r} and {second!r} are identical on all {total} rows'))

    lead = columns[0] if columns else ''
    if lead and lead.lower() not in IGNORED:
        values = series[lead]
        filled = sum(1 for v in values if v != '')
        if looks_like_a_time(values) and 0 < filled < total * SPARSE_LEAD_FRACTION:
            findings.append(('sparse-lead',
                             f'{lead!r} leads the table and is filled on {filled} of {total} rows'))
    return findings


def counts(report_dir):
    """{artifact name: row count} for a report folder."""
    result = {}
    for path in sorted(glob.glob(os.path.join(report_dir, '_TSV Exports', '*.tsv'))):
        _, rows = read_table(path)
        result[os.path.basename(path)[:-4]] = len(rows)
    return result


def check_scaling(single, multi):
    """The scaling findings between a one container and a multi container run."""
    findings = []
    for name, one in sorted(single.items()):
        many = multi.get(name, 0)
        if not one:
            continue
        if many == one * 2:
            continue
        if many == one:
            findings.append((name, 'scaling-1x',
                             f'{one} then {many}: a second tenant is dropped or merged'))
        elif many == one * 3:
            findings.append((name, 'scaling-3x',
                             f'{one} then {many}: duplicate storage views are not collapsing'))
        elif many > one * 2:
            findings.append((name, 'scaling-high',
                             f'{one} then {many}: a foreign container may be leaking in'))
        else:
            findings.append((name, 'scaling-other', f'{one} then {many}: not exactly double'))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('report', help='report folder holding "_TSV Exports"')
    parser.add_argument('--compare', help='report folder for the multi container run')
    parser.add_argument('--strict', action='store_true', help='exit 1 when anything is found')
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    notes = artifact_notes(repo_root)

    exports = sorted(glob.glob(os.path.join(args.report, '_TSV Exports', '*.tsv')))
    if not exports:
        print(f'No "_TSV Exports" found under {args.report}', file=sys.stderr)
        return 2

    total_findings = 0
    checked = 0
    for path in exports:
        name = os.path.basename(path)[:-4]
        columns, rows = read_table(path)
        if not rows:
            continue
        checked += 1
        findings = check_table(columns, rows, notes.get(name, ''))
        if findings:
            print(f'\n{name}  ({len(rows)} rows)')
            for kind, message in findings:
                print(f'   {kind:<18} {message}')
            total_findings += len(findings)

    if args.compare:
        scaling = check_scaling(counts(args.report), counts(args.compare))
        if scaling:
            print('\nScaling against the multi container run')
            for name, kind, message in scaling:
                print(f'   {kind:<18} {name}: {message}')
            total_findings += len(scaling)
        else:
            print('\nScaling against the multi container run: every artifact exactly doubled.')

    print(f'\nChecked {checked} artifact export(s): '
          f'{total_findings or "nothing"} to look at.')
    if total_findings:
        print('A column named in its artifact\'s notes is not reported, so the documented way '
              'to keep a uniform column is to say so in the notes.')
    return 1 if (args.strict and total_findings) else 0


if __name__ == '__main__':
    sys.exit(main())
