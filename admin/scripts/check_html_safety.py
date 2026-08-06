"""Guard the HTML report against unescaped evidence and remote destinations.

Columns listed in an artifact's `__artifacts_v2__` `html_columns` are written to the
report *without* `html.escape` (see `scripts/artifact_report.py`, the `html_no_escape`
branch). Anything an artifact places in such a cell is emitted verbatim, so the report
inherits two distinct risks from the evidence it parses:

* **Injection.** Markup in a parsed value renders live in the examiner's report
  (stored XSS, CWE-79; GHSA-45q2-q93c-cfv2). `scripts/html_safe.py` exists to stop
  this: route the dynamic parts through `esc`/`safe_join`/`safe_source` and let only
  tool-authored markup through unescaped.

* **Disclosure.** A cell that names a remote host makes the examiner's browser reach
  it. An `<img src="https://...">` needs no click at all: opening the report tells
  the service operator that the account is under examination, when, and from which
  IP address. Reports are read on analyst workstations and mailed to counsel, so a
  report must never be a beacon.

The standard these two risks produce is:

    Escape every evidence-derived value before it reaches a no-escape cell, and
    point no `href` or `src` at anything outside the report folder.

Report-relative destinations stay live -- `media/<file>` thumbnails and the files
artifacts write beside the report are what make the report navigable, and they
resolve offline. Remote destinations do not, whatever the scheme: `http`/`https`
fetch from a third party, and `mailto:`/`tel:` hand the subject's own address or
number to a mail client or dialer, where one stray click in front of a suspect's
counsel is its own kind of incident.

The failure mode this check exists to stop is a partial fix. When html_safe.py landed,
iLEAPP's `walStrings` anchor was escaped and ALEAPP's identical `walStrings` anchor was
not; it stayed unescaped for weeks because nothing was watching. Cross-core drift is
the normal outcome here, not the exception.

THREE RULES
-----------
`unescaped-interpolation`
    A string expression whose literal parts contain markup interpolates something
    that is not a constant and not a call to an approved escaper. Covers f-strings,
    `+` concatenation, `%`, `.format()`, and `"<br>".join(...)`, because HTML gets
    built every one of those ways in this repo.

`remote-destination`
    A literal remote URL appears in a markup-bearing string, or an `href=`/`src=`
    attribute is completed by an interpolation. A dynamic destination cannot be shown
    to be report-relative by reading the source, so it fails unless it comes from
    `safe_local_link()`.

`unguarded-html-columns`
    A module declares `html_columns` but never references an escaper. This catches the
    case the other two rules cannot see: a value assembled with no markup anywhere near
    it -- a bare URL, say -- that still lands in a no-escape cell.

BASELINE vs ALLOWLIST
---------------------
`BASELINE` holds violations that already existed when this check landed. They do not
fail the build, so the check can be enabled before the cleanup finishes, but they are
debt: delete each entry as its violation is fixed.

`ALLOWLIST` holds reviewed exceptions that are correct as they stand and are expected
to stay -- markup built only from tool-owned constants, a media-only column.

Both lists fail the run when an entry stops matching anything. A stale entry means the
code moved or was fixed, and the entry now shields whatever lands under the same name
next. Entries are keyed by (path, rule, enclosing function) so they survive line moves;
a module-level violation uses `<module>`.

Coverage holes are printed, never hidden. A module whose `__artifacts_v2__` is not a
static literal cannot have its `html_columns` read, so `unguarded-html-columns` cannot
run on it; those are listed as NOT CHECKED on every run.

`scripts/artifact_report.py` is deliberately out of scope. It implements the
escape/no-escape branch itself, so it is the sink these rules protect, not a producer.

Usage:
    python admin/scripts/check_html_safety.py            # CI mode, exits 1 on a violation
    python admin/scripts/check_html_safety.py --list     # every finding, baselined included
    python admin/scripts/check_html_safety.py --verbose  # coverage and list counts
"""

import argparse
import ast
import glob
import os
import re
import sys

# Markup that means the surrounding string is being built for the report rather than
# for a log line or a query. An opening tag, or an attribute that takes a URL.
# A complete tag, not a fragment: `<i` alone also spells the struct format string
# f'<{count}i', and matching that made every binary parser in the repo a finding.
MARKUP_PATTERN = re.compile(
    r'</?(?:a|img|br|td|tr|table|div|span|i|p|ul|li|audio|video|source|iframe)'
    r'\b[^<>]*>'
    r'|\b(?:href|src)\s*=\s*["\']',
    re.IGNORECASE)

# Schemes that leave the report folder. `mailto`/`tel` do not fetch, but they hand the
# subject's contact details to a local app on a click, so they are destinations too.
REMOTE_SCHEME_PATTERN = re.compile(
    r'\b(?:https?|ftps?|ws|wss|mailto|tel|data)\s*:', re.IGNORECASE)

# A literal part ending here means the attribute's value is whatever comes next.
DESTINATION_ATTR_PATTERN = re.compile(r'\b(?:href|src)\s*=\s*["\']?\s*$', re.IGNORECASE)

# The flag artifacts use to pick the HTML output arm of a two-output helper.
HTML_FLAG_PATTERN = re.compile(r'html_format|html_output|is_html|as_html')

# Calls whose result is safe to drop into a no-escape cell. `esc`/`safe_*` come from
# scripts/html_safe.py; `escape` is the stdlib import artifacts predating it still use;
# `quote` is urllib's percent-encoder, used on report-relative media paths.
ESCAPER_NAMES = frozenset({
    'esc', 'safe_url', 'safe_join', 'safe_source', 'safe_local_link', 'escape', 'quote',
})

# The subset of the above that yields a destination which resolves inside the report
# folder. Only these may complete an href= or src=. The media helpers belong here
# because they rewrite an extraction path to `media/<file>` beside the report.
LOCAL_LINK_NAMES = frozenset({
    'safe_local_link', 'media_to_html', 'check_in_media', 'html_media_tag',
})

# Pre-existing violations. Delete an entry when its violation is fixed; a stale entry
# fails the run. See the module docstring before adding one.
BASELINE = {
    # -- Report-relative destinations the checker cannot yet prove are local. These
    # clear when the media path and the artifact output path are produced by
    # safe_local_link() instead of by hand-built string concatenation.
    ('scripts/ilapfuncs.py', 'remote-destination', 'html_media_tag'),
    ('scripts/ilapfuncs.py', 'remote-destination', 'media_to_html'),
    ('scripts/artifacts/walStrings.py', 'remote-destination', 'process_journal_files'),
    ('scripts/artifacts/googleTranslate.py', 'remote-destination', 'googleTranslateTts'),

    # -- Unescaped evidence in a no-escape cell.
    # html_media_tag / media_to_html put the media item's name into title= and into
    # the fallback anchor text with no escaping, tool-wide. A crafted attachment
    # filename breaks out of the title attribute. GHSA-45q2-q93c-cfv2 deferred this.
    ('scripts/ilapfuncs.py', 'unescaped-interpolation', 'html_media_tag'),
    ('scripts/ilapfuncs.py', 'unescaped-interpolation', 'media_to_html'),
    # BeReal joins raw contact phone numbers with <br />; the value is never escaped.
    ('scripts/artifacts/BeReal.py', 'unescaped-interpolation', 'bereal_contacts'),
    # BeReal's generic_url() helper returns a prebuilt anchor the checker cannot see
    # into. Both callers clear once that helper stops emitting remote anchors.
    ('scripts/artifacts/BeReal.py', 'unescaped-interpolation', 'get_links'),
    ('scripts/artifacts/BeReal.py', 'unescaped-interpolation', 'get_realmojis'),
    ('scripts/artifacts/appleMapsTrips.py', 'unescaped-interpolation',
     'get_google_dir_link'),

    # -- Live remote destinations. Each becomes escaped text.
    # Tool-authored map links: openstreetmap.org and google.com/maps.
    ('scripts/artifacts/calendarAll.py', 'remote-destination', 'calendarEvents'),
    ('scripts/artifacts/Oura.py', 'remote-destination', 'oura_find_my_ring_location'),
    ('scripts/artifacts/appleMapsTrips.py', 'remote-destination', 'get_google_map_link'),
    ('scripts/artifacts/appleMapsTrips.py', 'remote-destination', 'get_google_dir_link'),
    # Evidence-derived destinations: each format_url() anchors a URL read from the app.
    ('scripts/artifacts/box.py', 'remote-destination', 'format_url'),
    ('scripts/artifacts/booking.py', 'remote-destination', 'format_url'),
    ('scripts/artifacts/foursquareSwarm.py', 'remote-destination', 'format_url'),
    ('scripts/artifacts/waze.py', 'remote-destination', 'format_url'),

    # -- swissmeteo and sbbmobile put a bare openstreetmap.org URL in an html_column
    # and escape nothing. The URL is not an anchor, so the cell already renders as
    # text; dropping html_columns removes the sink at no cost to the report.
    ('scripts/artifacts/swissmeteo.py', 'unguarded-html-columns', '<module>'),
    ('scripts/artifacts/sbbmobile.py', 'unguarded-html-columns', '<module>'),
}

# Reviewed exceptions expected to stay. Every entry needs a comment saying why.
ALLOWLIST = {
    # Both declare a single media column and nothing else. The cell is built by the
    # framework's media helper, so the module itself has no evidence text to escape.
    ('scripts/artifacts/googleTranslate.py', 'unguarded-html-columns', '<module>'),
    ('scripts/artifacts/nsVault.py', 'unguarded-html-columns', '<module>'),
}

# Framework helpers that build the contents of a report *cell* for artifacts to use.
# They have no __artifacts_v2__ of their own, so they are named rather than detected,
# and they are named per-function on purpose.
#
# ilapfuncs.py also writes the device-info page and the log page, which interpolate
# evidence-derived values into markup on a surface this check does not cover. That is
# a real surface and a larger one; guarding it is its own piece of work, and pulling
# it in here would bury the cell findings this check exists to hold the line on.
FRAMEWORK_FUNCTIONS = {
    'scripts/ilapfuncs.py': frozenset({
        'html_media_tag', 'media_to_html', 'get_data_list_with_media',
    }),
}

STANDARD_NOTE = (
    'Values in an html_columns cell are written to the report unescaped.\n'
    'Escape evidence-derived text with esc()/safe_join()/safe_source() from\n'
    'scripts/html_safe.py, and keep every href/src inside the report folder --\n'
    'no http, https, ftp, mailto or tel destination reaches the report.\n'
    'If the finding is markup built only from tool-owned constants, add it to\n'
    'ALLOWLIST in admin/scripts/check_html_safety.py with a comment saying why.'
)


def enclosing_functions(tree):
    """Map each node to the name of the function that contains it.

    Keys are `id()` values, so the tree must stay alive while the map is used.
    Nodes outside any function map to `<module>`.
    """
    owner = {}

    def walk(node, name):
        for child in ast.iter_child_nodes(node):
            child_name = name
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                child_name = child.name
            owner[id(child)] = child_name
            walk(child, child_name)

    owner[id(tree)] = '<module>'
    walk(tree, '<module>')
    return owner


def flatten_concat(node):
    """Return the operands of a `+` chain in source order, or None if not one."""
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
        return None
    left = flatten_concat(node.left) or [node.left]
    right = flatten_concat(node.right) or [node.right]
    return left + right


def string_parts(node):
    """Return this node's string parts as [(literal, dynamic_expr_or_None), ...].

    Returns None when the node does not build a string. Each entry is either a
    literal fragment or a dynamic expression; the caller reads them in source order,
    so a literal ending in `href="` is known to be completed by the next entry.
    """
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append((value.value, None))
            elif isinstance(value, ast.FormattedValue):
                parts.append((None, value.value))
        return parts

    operands = flatten_concat(node)
    if operands and any(isinstance(op, ast.Constant) and isinstance(op.value, str)
                        for op in operands):
        return [(op.value, None) if isinstance(op, ast.Constant)
                and isinstance(op.value, str) else (None, op) for op in operands]

    # "<td>%s</td>" % value
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)
            and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)):
        args = (node.right.elts if isinstance(node.right, ast.Tuple) else [node.right])
        return [(node.left.value, None)] + [(None, arg) for arg in args]

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        target = node.func.value
        is_literal_target = (isinstance(target, ast.Constant)
                             and isinstance(target.value, str))
        # "<td>{}</td>".format(value)
        if node.func.attr == 'format' and is_literal_target:
            return ([(target.value, None)]
                    + [(None, arg) for arg in node.args]
                    + [(None, kw.value) for kw in node.keywords])
        # "<br>".join(values) -- the separator is the markup, the values are dynamic.
        if node.func.attr == 'join' and is_literal_target and node.args:
            return [(target.value, None), (None, node.args[0])]

    return None


def call_name(node):
    """Return the callee name for a Call node, or None."""
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _resolve(node, assignments, names, seen):
    """True when `node` is safe under the callee set `names`.

    `assignments` maps a local variable to every expression assigned to it in the
    enclosing function, so the common `thumb = media_to_html(...)` then
    `f'src="{thumb}"'` shape resolves instead of failing for lack of context. A name
    is safe only when *every* assignment to it is, which keeps a conditional
    reassignment from laundering a raw value.
    """
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.IfExp):
        # `esc(v) if html_format else v` is the repo's standard two-output idiom: the
        # escaped arm builds the HTML row, the raw arm builds the TSV/LAVA row, and
        # only the first reaches a no-escape cell. Judge the HTML arm alone when the
        # test names that flag; otherwise both arms have to be safe.
        if HTML_FLAG_PATTERN.search(ast.dump(node.test)):
            return _resolve(node.body, assignments, names, seen)
        return (_resolve(node.body, assignments, names, seen)
                and _resolve(node.orelse, assignments, names, seen))
    if isinstance(node, ast.BoolOp):
        return all(_resolve(v, assignments, names, seen) for v in node.values)
    # "<br>".join(esc(v) for v in values) -- the element is what reaches the cell.
    if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        return _resolve(node.elt, assignments, names, seen)
    if isinstance(node, ast.JoinedStr):
        return all(_resolve(v.value, assignments, names, seen)
                   for v in node.values if isinstance(v, ast.FormattedValue))
    if isinstance(node, ast.Call):
        if call_name(node) in names:
            return True
        # str.join() is transparent: safety is decided by what is being joined.
        if (isinstance(node.func, ast.Attribute) and node.func.attr == 'join'
                and node.args):
            return _resolve(node.args[0], assignments, names, seen)
        return False
    if isinstance(node, ast.Name):
        if node.id in seen:          # a self-referential accumulator (x = x + ...)
            return True
        values = assignments.get(node.id)
        if not values:
            return False
        return all(_resolve(v, assignments, names, seen | {node.id}) for v in values)
    # An empty container is safe on its own; what matters is what gets put in it,
    # which local_assignments() records from .append()/.extend().
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(_resolve(elt, assignments, names, seen) for elt in node.elts)
    return False


def is_escaped(node, assignments):
    """True when this interpolated expression is safe in a no-escape cell."""
    return _resolve(node, assignments, ESCAPER_NAMES, frozenset())


def is_local_link(node, assignments):
    """True when this expression yields a destination inside the report folder."""
    return _resolve(node, assignments, LOCAL_LINK_NAMES, frozenset())


def local_assignments(tree):
    """Map each function to {variable: [assigned expressions]} within it.

    Augmented assignment (`aggregate += f'...'`) records the right-hand side, so an
    accumulator built only from escaped fragments still resolves as escaped.
    """
    per_function = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        key = node.name if hasattr(node, 'name') else '<module>'
        table = per_function.setdefault(key, {})
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        table.setdefault(target.id, []).append(child.value)
            elif isinstance(child, ast.AugAssign) and isinstance(child.target, ast.Name):
                table.setdefault(child.target.id, []).append(child.value)
            # `parts.append(esc(v))` is how most list-then-join builders fill up, so
            # the appended expression counts as a value the name can hold.
            elif (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                    and child.func.attr in ('append', 'extend', 'add')
                    and isinstance(child.func.value, ast.Name) and child.args):
                table.setdefault(child.func.value.id, []).append(child.args[0])
    return per_function


def scan_string_builders(tree, owner, assignments_by_function):
    """Return (rule, function, line, detail) for every markup string built unsafely."""
    findings = []
    for node in ast.walk(tree):
        parts = string_parts(node)
        if not parts:
            continue
        literal_text = ''.join(text for text, _ in parts if text)
        if not MARKUP_PATTERN.search(literal_text):
            continue

        function = owner.get(id(node), '<module>')
        assignments = assignments_by_function.get(function, {})
        line = getattr(node, 'lineno', 0)
        snippet = ' '.join(literal_text.split())[:120]

        if REMOTE_SCHEME_PATTERN.search(literal_text):
            findings.append(('remote-destination', function, line,
                             f'literal remote destination in markup: {snippet}'))

        previous_literal = ''
        for text, dynamic in parts:
            if dynamic is None:
                previous_literal = text or ''
                continue
            completes_destination = DESTINATION_ATTR_PATTERN.search(previous_literal)
            if completes_destination and not is_local_link(dynamic, assignments):
                findings.append(('remote-destination', function, line,
                                 f'href/src completed by an expression that is not a '
                                 f'report-relative destination: {snippet}'))
            elif not is_escaped(dynamic, assignments):
                findings.append(('unescaped-interpolation', function, line,
                                 f'unescaped value interpolated into markup: {snippet}'))
            previous_literal = ''
    return findings


def find_artifacts_dict(tree):
    """Return the AST node assigned to `__artifacts_v2__`, or None."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                return node.value
    return None


def declares_html_columns(tree):
    """Return (declares, skip_reason). `declares` is None when it cannot be read."""
    node = find_artifacts_dict(tree)
    if node is None:
        return False, None
    try:
        artifacts = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as ex:
        return None, f'__artifacts_v2__ is not a literal: {ex}'
    if not isinstance(artifacts, dict):
        return None, '__artifacts_v2__ is not a dict'
    return any(isinstance(entry, dict) and entry.get('html_columns')
               for entry in artifacts.values()), None


def uses_media_helper(tree):
    """True when the module builds a media cell, which the framework never escapes."""
    return any(call_name(node) in LOCAL_LINK_NAMES for node in ast.walk(tree)
               if isinstance(node, ast.Call))


def references_escaper(tree):
    """True when the module calls any approved escaper anywhere."""
    return any(call_name(node) in ESCAPER_NAMES for node in ast.walk(tree)
               if isinstance(node, ast.Call))


def scan_file(path, rel_path):
    """Return (findings, skip_reason) for one module."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            source = handle.read()
    except OSError as ex:
        return [], f'could not read file: {ex}'
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as ex:
        return [], f'could not parse module: {ex}'

    declares, skip_reason = declares_html_columns(tree)

    # Markup only matters where it can reach a cell the report writes unescaped: a
    # declared html_columns, a media column (the framework adds those to
    # html_no_escape itself), or a framework helper that builds markup for others.
    # Elsewhere the writer escapes the whole cell, so a hand-built tag renders as
    # visible text -- a display bug, not an injection, and not this check's business.
    in_scope_functions = FRAMEWORK_FUNCTIONS.get(rel_path)
    is_sink = bool(declares) or uses_media_helper(tree) or in_scope_functions

    findings = []
    if is_sink:
        found = scan_string_builders(tree, enclosing_functions(tree),
                                     local_assignments(tree))
        if in_scope_functions is not None:
            found = [f for f in found if f[1] in in_scope_functions]
        findings.extend(found)
    if declares and not references_escaper(tree):
        findings.append(('unguarded-html-columns', '<module>', 0,
                         'module declares html_columns but calls no escaper'))
    return findings, skip_reason


def repo_root():
    """Return the repository root, derived from this script's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def scan_paths(root):
    """Return the modules in scope: every artifact, plus the framework helpers."""
    paths = sorted(glob.glob(os.path.join(root, 'scripts', 'artifacts', '*.py')))
    helper = os.path.join(root, 'scripts', 'ilapfuncs.py')
    if os.path.exists(helper):
        paths.append(helper)
    return paths


def main():
    """Scan for unescaped markup and remote destinations in report output."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--list', action='store_true', dest='list_all',
                        help='print every finding, including baselined and allowlisted')
    parser.add_argument('--verbose', action='store_true',
                        help='also report coverage and list counts')
    args = parser.parse_args()

    root = repo_root()
    paths = scan_paths(root)
    if not paths:
        print(f'No modules found under {os.path.join(root, "scripts")}', file=sys.stderr)
        return 2

    violations = []
    known = []
    skipped = []
    fired = set()
    for path in paths:
        rel_path = os.path.relpath(path, root).replace(os.sep, '/')
        findings, skip_reason = scan_file(path, rel_path)
        if skip_reason:
            skipped.append((rel_path, skip_reason))
        for rule, function, line, detail in findings:
            key = (rel_path, rule, function)
            fired.add(key)
            entry = (rel_path, rule, function, line, detail)
            if key in BASELINE or key in ALLOWLIST:
                known.append(entry)
            else:
                violations.append(entry)

    stale_baseline = sorted(BASELINE - fired)
    stale_allowlist = sorted(ALLOWLIST - fired)

    if skipped:
        print(f'NOT CHECKED -- {len(skipped)} module(s) have no statically readable '
              f'__artifacts_v2__, so html_columns could not be read:')
        for rel_path, reason in skipped:
            print(f'  {rel_path}: {reason}')
        print()

    if args.verbose:
        print(f'Scanned {len(paths)} module(s).')
        print(f'BASELINE holds {len(BASELINE)} entr(ies); ALLOWLIST holds '
              f'{len(ALLOWLIST)}; {len(known)} finding(s) matched one this run.')
        print()

    if args.list_all and known:
        print(f'Known findings ({len(known)}):')
        for rel_path, rule, function, line, detail in known:
            print(f'  {rel_path}:{line}: [{rule}] in {function}(): {detail}')
        print()

    for label, stale in (('BASELINE', stale_baseline),
                         ('ALLOWLIST', stale_allowlist)):
        if stale:
            print(f'Stale {label} entr(ies) ({len(stale)}) -- these no longer match '
                  f'anything and should be deleted:')
            for rel_path, rule, function in stale:
                print(f'  {rel_path}: [{rule}] in {function}()')
            print()

    if violations:
        print(f'Unsafe report output ({len(violations)}):')
        for rel_path, rule, function, line, detail in violations:
            print(f'  {rel_path}:{line}: [{rule}] in {function}(): {detail}')
        print()
        print(STANDARD_NOTE)
        return 1

    if stale_baseline or stale_allowlist:
        print('Remove the stale entr(ies) above from '
              'admin/scripts/check_html_safety.py.')
        return 1

    summary = (f'Checked {len(paths)} module(s): no new unsafe report output '
               f'({len(BASELINE)} baselined, {len(ALLOWLIST)} allowlisted).')
    if skipped:
        summary += f' {len(skipped)} module(s) NOT fully checked, listed above.'
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
