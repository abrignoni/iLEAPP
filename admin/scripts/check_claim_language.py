"""Guard the examiner-facing artifact metadata against unsupported claims.

Every artifact module declares an `__artifacts_v2__` dict. Its `name` and
`description` fields are not developer notes: they are rendered into the HTML
report, written into the LAVA manifest, and from there they get pasted into
examination notes and quoted in court. A description that says an artifact holds
"every site the user visited" is a statement about a person's conduct that the
underlying database does not make. The standard for these fields is therefore:

    Say what the data is and where it came from. Do not say what it means about
    the world, or who did it, unless the data itself establishes that or the
    description cites a source that documents it.

The failure mode this check exists to stop is a partial fix. In PR #1852 a Waze
artifact's docstring was corrected to drop an unsupported claim, but the
`description` field a few lines above it kept the original wording, so the claim
kept shipping to reports until PR #1854 caught it. Prose fixes go stale exactly
where nothing is watching them.

The check parses each artifact module with `ast`, evaluates its `__artifacts_v2__`
literal, and matches the `name` and `description` of every entry against a
vocabulary of phrasing that has historically signalled an unsupported claim
(completeness words, attributions of an act to "the user", certainty words).

Two ways a match gets resolved:

* The wording overstates what the parser can show. Reword it to what the data
  shows -- name the table, file, or stream, and drop the actor and the
  completeness word. This is the common case.
* The match is a false positive: a product feature literally named "All Files",
  a verbatim database enum value, a UI path reproduced from the app, or a
  cautionary sentence whose matched word is part of the hedge. Add a
  `(filename, artifact_key, field)` tuple to ALLOWLIST **with an inline comment
  saying why**. The allowlist is a record of decisions someone made on purpose;
  it is not a place to park a description nobody wanted to rewrite.

Two things the check reports rather than hides, because both are ways it can
quietly stop doing its job:

* An ALLOWLIST entry that no longer matches anything. It means the description
  was reworded or the artifact key changed, and the entry now shields nothing --
  except the next claim that lands under the same key. Stale entries fail the
  run and must be deleted.
* A module whose `__artifacts_v2__` is not a static literal (built by a helper,
  or absent). Its fields cannot be read without importing the module, so they
  are never checked. Those modules are printed as NOT CHECKED on every run, so
  the coverage hole stays visible.

Usage:
    python admin/scripts/check_claim_language.py           # CI mode, exits 1 on a violation
    python admin/scripts/check_claim_language.py --list    # every match, allowlisted included
    python admin/scripts/check_claim_language.py --verbose # coverage and allowlist counts
"""

import argparse
import ast
import glob
import os
import re
import sys

# The claim vocabulary. Each alternative is a phrasing that has, in past audits,
# turned out to be an assertion the parsed data does not support:
#   - completeness claims over a source that is rotated, cached, or truncated
#     ("all", "every", "complete", "full list", "entire")
#   - attributing an act to a person when the record only shows a stored value
#     ("the user viewed", "user-created", "searched by", "manually")
#   - certainty and inference-about-conduct words ("proves", "definitively",
#     "always", "reliable", "visited", "habits")
#
# Every alternative is anchored with an explicit \b. Do NOT express a boundary as
# a trailing space ("all ", "every ", "always "): that spelling matches inside
# "call log", "calllog.db" and similar, and in a sibling implementation it turned
# 35 of 37 raw hits into call-log false positives, which is enough noise to make
# the check worth ignoring. Word boundaries also keep the hedges quiet -- neither
# "unreliable" nor "incomplete" trips, because there is no boundary mid-word.
#
# The stems below are left UNCLOSED on purpose so inflections still match:
#   \bcomplete -> complete, completeness, completely
#   \breliable -> reliable and its compounds
#   \bhabit    -> habit, habits
# The cost of the open \bhabit is that it also matches "habitat"; no artifact in
# this repo uses that word today, and this spelling is kept deliberately in sync
# with the ALEAPP implementation of the same check. If a habitat-related artifact
# ever lands, close it to \bhabits?\b rather than allowlisting the artifact.
CLAIM_PATTERN = re.compile(
    r'\ball\b'
    r'|\bevery\b'
    r'|\bcomplete'
    r'|\bfull list\b'
    r'|\bentire\b'
    r'|\bthe user (?:searched|typed|viewed|visited|opened|selected|deleted|read|sent'
    r'|created|hid|chose)\b'
    r'|\buser[- ](?:created|entered|typed|searched|selected|initiated)\b'
    r'|\bsearched by\b'
    r'|\btyped by\b'
    r'|\bviewed by\b'
    r'|\bread by\b'
    r'|\bmanually\b'
    r'|\bproves?\b'
    r'|\bdefinitively\b'
    r'|\balways\b'
    r'|\breliable'
    r'|\bvisited\b'
    r'|\bhabit',
    re.IGNORECASE)

# Fields that reach the examiner through the report and the LAVA manifest.
CHECKED_FIELDS = ('name', 'description')

# Reviewed exceptions, keyed by (filename, artifact_key, field). Every entry
# needs a comment justifying it. See the module docstring before adding one.
ALLOWLIST = {
    # "All Files" is Box's own name for the product feature; renaming it would
    # make the artifact harder to match to what the examiner sees in the app.
    ('box.py', 'box_all_files', 'name'),
    ('box.py', 'box_all_files', 'description'),

    # The match is inside the cautionary note itself -- "these timestamps do not
    # always indicate application usage" is the hedge, not a claim.
    ('applicationStateDB.py', 'get_snapshot_creationDate', 'description'),
    ('applicationStateDB.py', 'get_snapshot_lastUsedDate', 'description'),

    # "may be user-entered or written by apps and connected devices" is an
    # explicit statement that authorship is unknown, which is the point.
    ('health.py', 'health_height', 'description'),
    ('health.py', 'health_weight', 'description'),

    # Both reproduce a path through the Apple Health UI ("Show All Health Data",
    # "All Recorded Data", "All Watch Sleep Data"), so the word is a label the
    # examiner can navigate to, not a completeness claim by us.
    ('health.py', 'health_all_watch_sleep_data', 'name'),
    ('health.py', 'health_wrist_temperature', 'description'),

    # The match is inside verbatim ZSYNDICATIONSTATE enum labels quoted from the
    # schema (e.g. "2-SyndPs-Manually-Saved_SWY_Synd_Asset-2"), not prose.
    ('Ph026SyndicationPLAssets.py', 'Ph026_1SyndicationIDAssetsPhDaPsql', 'description'),
    ('Ph026SyndicationPLAssets.py', 'Ph026_2SyndicationPLAssetsSyndPL', 'description'),

    # "visited places" restates the name of the Location.Visit stream being
    # parsed, and the description goes on to caution against relying on its
    # timestamps.
    ('biomeLocationVisit.py', 'get_biomeLocationVisit', 'description'),

    # "all interfaces listed in NetworkInterfaces.plist" is scoped to the file
    # being parsed, not a claim about the interfaces the device ever had.
    ('wifiIdentifiers.py', 'wifiIdentifiers', 'description'),

    # A Foursquare list is user-created by the definition of the feature, and
    # the artifact reads the account holder's own list table.
    ('foursquareSwarm.py', 'foursquare_swarm_saved_lists', 'description'),
}

STANDARD_NOTE = (
    'Artifact name/description reach the examiner through the HTML report and the LAVA\n'
    'manifest and get quoted in casework. State what the data is and where it came from;\n'
    'do not state what it means in the real world, or who performed an act, unless the\n'
    'data establishes it or a cited source documents it.\n'
    'Reword to what the data shows, or -- if the match is a product name, a verbatim\n'
    'schema value, a UI path, or part of a hedge -- add it to ALLOWLIST in\n'
    'admin/scripts/check_claim_language.py with a comment saying why.'
)


def find_artifacts_dict(tree):
    """Return the AST node assigned to `__artifacts_v2__`, or None."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                return node.value
    return None


def load_artifacts(path):
    """Return (artifacts_dict, skip_reason). Exactly one of the two is None."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            source = handle.read()
    except OSError as ex:
        return None, f'could not read file: {ex}'

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as ex:
        return None, f'could not parse module: {ex}'

    node = find_artifacts_dict(tree)
    if node is None:
        return None, 'no __artifacts_v2__ assignment'

    # Modules that build the dict dynamically cannot be evaluated statically.
    try:
        artifacts = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as ex:
        return None, f'__artifacts_v2__ is not a literal: {ex}'

    if not isinstance(artifacts, dict):
        return None, '__artifacts_v2__ is not a dict'
    return artifacts, None


def scan_file(path):
    """Return (matches, skip_reason) for one artifact module.

    Each match is a (rel_path, artifact_key, field, text, matched_terms,
    allowlisted) tuple.
    """
    artifacts, skip_reason = load_artifacts(path)
    if artifacts is None:
        return [], skip_reason

    filename = os.path.basename(path)
    matches = []
    for artifact_key, entry in artifacts.items():
        if not isinstance(entry, dict):
            continue
        for field in CHECKED_FIELDS:
            text = entry.get(field)
            if not isinstance(text, str):
                continue
            terms = CLAIM_PATTERN.findall(text)
            if not terms:
                continue
            allowlisted = (filename, str(artifact_key), field) in ALLOWLIST
            matches.append((path, str(artifact_key), field, text, terms, allowlisted))
    return matches, None


def repo_root():
    """Return the repository root, derived from this script's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def format_match(match):
    """Render one match as `path:artifact_key:field: <text>`."""
    path, artifact_key, field, text, terms, _ = match
    collapsed = ' '.join(text.split())
    if len(collapsed) > 300:
        collapsed = collapsed[:297] + '...'
    quoted = ', '.join(sorted({term.lower() for term in terms}))
    return f'{path}:{artifact_key}:{field}: {collapsed}\n    matched: {quoted}'


def main():
    """Scan the artifact modules and report unallowlisted claim language."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--list', action='store_true', dest='list_all',
                        help='print every match, including allowlisted ones')
    parser.add_argument('--verbose', action='store_true',
                        help='also report modules whose __artifacts_v2__ could not be read')
    args = parser.parse_args()

    root = repo_root()
    pattern = os.path.join(root, 'scripts', 'artifacts', '*.py')
    paths = sorted(glob.glob(pattern))
    if not paths:
        print(f'No artifact modules found under {pattern}', file=sys.stderr)
        return 2

    violations = []
    allowlisted = []
    skipped = []
    fired = set()
    for path in paths:
        rel_path = os.path.relpath(path, root)
        matches, skip_reason = scan_file(path)
        if skip_reason:
            skipped.append((rel_path, skip_reason))
            continue
        for match in matches:
            entry = (rel_path,) + match[1:]
            fired.add((os.path.basename(path), match[1], match[2]))
            if match[5]:
                allowlisted.append(entry)
            else:
                violations.append(entry)

    # An allowlist entry that no longer matches anything is either a fixed
    # description or a stale key, and it hides the next real claim behind a name
    # nobody rechecks. Surface it so the allowlist stays a list of live decisions.
    stale = sorted(ALLOWLIST - fired)

    # A module whose __artifacts_v2__ cannot be evaluated statically is a real
    # coverage hole: its fields are never checked. Report it rather than hide it.
    if skipped:
        print(f'NOT CHECKED -- {len(skipped)} module(s) have no statically readable '
              f'__artifacts_v2__:')
        for rel_path, reason in skipped:
            print(f'  {rel_path}: {reason}')
        print()

    if args.verbose:
        print(f'Scanned {len(paths)} module(s); {len(paths) - len(skipped)} checked, '
              f'{len(skipped)} skipped.')
        print(f'Allowlist holds {len(ALLOWLIST)} entr(ies); {len(allowlisted)} fired '
              f'this run.')
        print()

    if stale:
        print(f'Stale ALLOWLIST entr(ies) ({len(stale)}) -- these no longer match '
              f'anything and should be deleted:')
        for entry in stale:
            print(f'  {entry[0]}:{entry[1]}:{entry[2]}')
        print()

    if args.list_all and allowlisted:
        print(f'Allowlisted matches ({len(allowlisted)}):')
        for match in allowlisted:
            print(f'  {format_match(match)}')
        print()

    if violations:
        print(f'Unsupported claim language in examiner-facing artifact fields '
              f'({len(violations)}):')
        for match in violations:
            print(f'  {format_match(match)}')
        print()
        print(STANDARD_NOTE)
        return 1

    if stale:
        print('Remove the stale entr(ies) above from ALLOWLIST in '
              'admin/scripts/check_claim_language.py.')
        return 1

    summary = (f'Checked {len(paths) - len(skipped)} artifact module(s): no unsupported '
               f'claim language ({len(allowlisted)} reviewed exception(s) allowlisted).')
    if skipped:
        summary += f' {len(skipped)} module(s) NOT checked, listed above.'
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
