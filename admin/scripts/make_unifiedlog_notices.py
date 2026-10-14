"""Write the third-party notices for the Rust crates linked into unifiedlog_iterator.

The unifiedlog_iterator release binaries (mandiant/macos-UnifiedLogs, Apache-2.0) are
built by upstream's release workflow with `cargo build --release` in examples/, with no
Cargo.lock committed, so the crates they link are whatever Cargo resolved when the
release ran. This script repeats that resolution without Cargo: it reads the manifests
at the pinned tag, takes each dependency's newest version on the crates.io index that
was published before the release (the index records a pubtime for each version),
activates features the way Cargo does, and keeps the crates linked into the binary on
each target the fetch script can download. Build-only dependencies and proc-macro
crates, which run at compile time and are not linked, are left out.

It then downloads each linked crate from crates.io and writes the license files the
crate ships into the notices file, a text shared by several crates printed once.

    python admin/scripts/make_unifiedlog_notices.py --check-binary bin/unifiedlog_iterator
    python admin/scripts/make_unifiedlog_notices.py --verify bin/unifiedlog_iterator

--check-binary compares the resolution with the crate versions whose source paths the
compiled binary embeds before anything is written, and refuses when one is missing or
differs. --verify makes the same comparison against the committed notices file, needs no
network, and is what a build runs after fetching the binary. Run the first form again,
and commit the result, whenever the pinned version changes. Writing the notices needs
Python 3.11 or later (tomllib); --verify runs on any Python the project supports.
"""
import argparse
import functools
import gzip
import io
import json
import pathlib
import re
import ssl
import hashlib
import tarfile
import textwrap
import urllib.request

PINNED_VERSION = 'v0.7.0'
TAG_COMMIT = '09e6e6e43098a71d48250af552d732f630929208'
# The release's published_at; the binaries were built by the workflow that published it.
CUTOFF = '2026-09-14T00:33:09Z'
REPO = 'mandiant/macos-UnifiedLogs'
RAW = f'https://raw.githubusercontent.com/{REPO}/{TAG_COMMIT}'
INDEX = 'https://index.crates.io'
DOWNLOAD = 'https://static.crates.io/crates'
USER_AGENT = 'leapp-unifiedlog-notices'

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / 'bin' / 'THIRD-PARTY-NOTICES-unifiedlog_iterator.txt'

# The targets of the archives the fetch script can download, as rustc describes them.
TARGETS = {
    'aarch64-apple-darwin': dict(target_arch='aarch64', target_os='macos', target_family='unix',
                                 target_vendor='apple', target_env='', target_pointer_width='64',
                                 target_endian='little'),
    'x86_64-apple-darwin': dict(target_arch='x86_64', target_os='macos', target_family='unix',
                                target_vendor='apple', target_env='', target_pointer_width='64',
                                target_endian='little'),
    'aarch64-unknown-linux-gnu': dict(target_arch='aarch64', target_os='linux',
                                      target_family='unix', target_vendor='unknown',
                                      target_env='gnu', target_pointer_width='64',
                                      target_endian='little'),
    'x86_64-unknown-linux-musl': dict(target_arch='x86_64', target_os='linux', target_family='unix',
                                      target_vendor='unknown', target_env='musl',
                                      target_pointer_width='64', target_endian='little'),
    'x86_64-unknown-linux-gnu': dict(target_arch='x86_64', target_os='linux', target_family='unix',
                                     target_vendor='unknown', target_env='gnu',
                                     target_pointer_width='64', target_endian='little'),
    'x86_64-pc-windows-msvc': dict(target_arch='x86_64', target_os='windows',
                                   target_family='windows', target_vendor='pc', target_env='msvc',
                                   target_pointer_width='64', target_endian='little'),
}
LICENSE_FILE = re.compile(r'^(licen[cs]e|copying|unlicense|notice|copyright|authors)', re.I)


def _ssl_context():
    try:
        import certifi  # pylint: disable=import-outside-toplevel
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _toml(text):
    """Parse a Cargo.toml. tomllib arrived in Python 3.11, and only resolution needs it."""
    try:
        import tomllib  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise SystemExit('writing the notices needs Python 3.11 or later (tomllib)') from exc
    return tomllib.loads(text)


@functools.lru_cache(maxsize=None)
def _get(url):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, context=_ssl_context()) as response:  # nosec B310
        return response.read()


# --------------------------------------------------------------------------- versions

def _parse(version):
    """(major, minor, patch, prerelease) of a semver string, build metadata dropped."""
    core, _, pre = version.split('+')[0].partition('-')
    parts = [int(p) for p in core.split('.')]
    return tuple(parts + [0] * (3 - len(parts))) + (pre,)


def _bucket(version):
    """The part of a version Cargo keeps one copy of: major, else minor, else patch."""
    major, minor, patch, _ = version
    return (major,) if major else ((0, minor) if minor else (0, 0, patch))


def _comparators(req):
    """[(op, version tuple)] for a Cargo version requirement."""
    out = []
    for part in [p.strip() for p in req.split(',') if p.strip()]:
        match = re.match(r'^(\^|~|=|>=|>|<=|<)?\s*(.*)$', part)
        op, rest = match.group(1) or '^', match.group(2).strip()
        if rest in ('*', ''):
            continue
        nums = rest.split('-')[0].split('.')
        stars = [n for n in nums if n in ('*', 'x', 'X')]
        nums = [int(n) for n in nums if n not in ('*', 'x', 'X')]
        if stars:
            op = '~' if len(nums) >= 2 else '^'
        pre = rest.split('-', 1)[1] if '-' in rest else ''
        full = tuple(nums + [0] * (3 - len(nums))) + (pre,)
        if op in ('=', '>=', '>', '<=', '<'):
            if op == '=' and len(nums) < 3:
                out += _range_for('~' if len(nums) == 2 else '^', nums)
            else:
                out.append((op, full))
        else:
            out += _range_for(op, nums, pre)
    return out


def _range_for(op, nums, pre=''):
    low = tuple(nums + [0] * (3 - len(nums))) + (pre,)
    if op == '~':
        high = (nums[0] + 1, 0, 0) if len(nums) == 1 else (nums[0], nums[1] + 1, 0)
    else:  # caret
        if nums[0] > 0 or len(nums) == 1:
            high = (nums[0] + 1, 0, 0)
        elif nums[1] > 0 or len(nums) == 2:
            high = (0, nums[1] + 1, 0)
        else:
            high = (0, 0, nums[2] + 1)
    return [('>=', low), ('<', high + ('',))]


def _before(a, b):
    """a < b by semver precedence, a prerelease sorting before its release."""
    if a[:3] != b[:3]:
        return a[:3] < b[:3]
    if a[3] == b[3]:
        return False
    return bool(a[3]) and (not b[3] or a[3] < b[3])


def _matches(version, comparators):
    if version[3]:
        return False  # Cargo only takes prereleases a requirement names; none here do
    for op, bound in comparators:
        if op == '=' and version[:3] != bound[:3]:
            return False
        if op == '>=' and _before(version, bound):
            return False
        if op == '>' and not _before(bound, version):
            return False
        if op == '<' and not _before(version, bound):
            return False
        if op == '<=' and _before(bound, version):
            return False
    return True


def _index_path(name):
    name = name.lower()
    if len(name) <= 2:
        return f'{len(name)}/{name}'
    if len(name) == 3:
        return f'3/{name[0]}/{name}'
    return f'{name[:2]}/{name[2:4]}/{name}'


@functools.lru_cache(maxsize=None)
def _versions(name):
    """[(version tuple, version string, deps, features)] published before the cutoff."""
    out = []
    for line in _get(f'{INDEX}/{_index_path(name)}').decode().splitlines():
        entry = json.loads(line)
        if entry.get('yanked') or (entry.get('pubtime') and entry['pubtime'] > CUTOFF):
            continue
        features = dict(entry.get('features') or {})
        features.update(entry.get('features2') or {})
        out.append((_parse(entry['vers']), entry['vers'], entry['deps'], features))
    return out


# --------------------------------------------------------------------------- cfg

def _cfg(expression, target):
    """Evaluate a dependency's target: a triple or a cfg(...) expression."""
    if not expression:
        return True
    if not expression.startswith('cfg('):
        return expression == target
    spec = TARGETS[target]
    tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_]*|"[^"]*"|[(),=]', expression[4:-1])
    pos = [0]

    def parse():
        name = tokens[pos[0]]
        pos[0] += 1
        if name in ('all', 'any', 'not') and pos[0] < len(tokens) and tokens[pos[0]] == '(':
            pos[0] += 1
            values = []
            while tokens[pos[0]] != ')':
                values.append(parse())
                if tokens[pos[0]] == ',':
                    pos[0] += 1
            pos[0] += 1
            if name == 'all':
                return all(values)
            if name == 'any':
                return any(values)
            return not values[0]
        if pos[0] < len(tokens) and tokens[pos[0]] == '=':
            value = tokens[pos[0] + 1].strip('"')
            pos[0] += 2
            if name == 'target_has_atomic':
                return value in ('8', '16', '32', '64', 'ptr')
            if name == 'target_feature':
                return False
            if name == 'panic':
                return value == 'unwind'
            return spec.get(name) == value
        return {'unix': spec['target_family'] == 'unix',
                'windows': spec['target_family'] == 'windows'}.get(name, False)

    return parse()


# --------------------------------------------------------------------------- crates

@functools.lru_cache(maxsize=None)
def _crate(name, version):
    """(Cargo.toml dict, {license file name: bytes}) from the published .crate."""
    data = _get(f'{DOWNLOAD}/{name}/{name}-{version}.crate')
    manifest, licenses = {}, {}
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(data))) as archive:
        for member in archive.getmembers():
            parts = member.name.split('/')
            if len(parts) != 2 or not member.isfile():
                continue
            if parts[1] == 'Cargo.toml':
                manifest = _toml(archive.extractfile(member).read().decode('utf-8'))
            elif LICENSE_FILE.match(parts[1]):
                licenses[parts[1]] = archive.extractfile(member).read()
    return manifest, licenses


def _is_proc_macro(name, version):
    manifest, _ = _crate(name, version)
    return bool((manifest.get('lib') or {}).get('proc-macro') or
                (manifest.get('lib') or {}).get('proc_macro'))


# --------------------------------------------------------------------------- resolve

def _root_dependencies():
    """[(dep dict in index form)] of the binary and the path library it builds with."""
    deps = []
    for path in ('examples/unifiedlog_iterator/Cargo.toml', 'Cargo.toml'):
        manifest = _toml(_get(f'{RAW}/{path}').decode())
        for name, spec in (manifest.get('dependencies') or {}).items():
            if isinstance(spec, str):
                spec = {'version': spec}
            if 'path' in spec:
                continue  # the library itself; its dependencies are read from its manifest
            deps.append({'name': name, 'req': spec['version'], 'optional': False,
                         'default_features': spec.get('default-features', True),
                         'features': spec.get('features', []), 'target': None, 'kind': 'normal',
                         'package': spec.get('package')})
    return deps


def _walk(root_deps, pick, target):
    """One pass over the graph: (edges, roots) with features activated as Cargo does."""
    features = {}      # (name, version) -> enabled features
    edges = {}         # (name, version) -> set of (child name, child version)
    queue = []

    def request(parent, dep, extra=()):
        name = dep.get('package') or dep['name']
        key = (name, pick(name, dep['req'])[1])
        wanted = set(dep.get('features') or []) | set(extra)
        if dep.get('default_features', True):
            wanted.add('default')
        new = wanted - features.setdefault(key, set())
        first_visit = key not in edges
        edges.setdefault(key, set())
        if parent is not None:
            edges[parent].add(key)
        if new or first_visit:
            features[key] |= wanted
            queue.append(key)
        return key

    roots = {request(None, dep) for dep in root_deps}
    while queue:
        key = queue.pop()
        name, version = key
        if _is_proc_macro(name, version):
            continue  # compile-time only: its own dependencies are not linked
        entry = next(v for v in _versions(name) if v[1] == version)
        table = entry[3]
        deps = [d for d in entry[2]
                if d.get('kind') in (None, 'normal') and _cfg(d.get('target'), target)]
        by_name = {d['name']: d for d in deps}
        explicit = {item[4:] for items in table.values() for item in items if item.startswith('dep:')}
        switched_on, extra = set(), {}
        seen, stack = set(), list(features[key])
        while stack:
            feature = stack.pop()
            if feature in seen:
                continue
            seen.add(feature)
            if feature in table:
                for item in table[feature]:
                    if item.startswith('dep:'):
                        switched_on.add(item[4:])
                    elif '/' in item:
                        dep_name, sub = item.split('/', 1)
                        weak = dep_name.endswith('?')
                        dep_name = dep_name.rstrip('?')
                        if not weak:
                            switched_on.add(dep_name)
                            if dep_name not in explicit and dep_name in table:
                                stack.append(dep_name)
                        extra.setdefault(dep_name, set()).add(sub)
                    else:
                        stack.append(item)
            elif feature in by_name and by_name[feature].get('optional') and feature not in explicit:
                switched_on.add(feature)
        for dep in deps:
            if dep.get('optional') and dep['name'] not in switched_on:
                continue
            request(key, dep, extra.get(dep['name'], ()))
    return edges, roots


def resolve(target):
    """{(name, version string)} linked into the binary for one target."""
    root_deps = _root_dependencies()
    requirements = {}   # crate name -> set of requirement strings
    selected = {}       # (crate name, bucket) -> (version tuple, version string, deps, features)

    def pick(name, req):
        """The version Cargo would choose: the newest in the newest matching bucket that
        satisfies every requirement that bucket can meet."""
        requirements.setdefault(name, set()).add(req)
        candidates = [v for v in _versions(name) if _matches(v[0], _comparators(req))]
        if not candidates:
            raise SystemExit(f'no version of {name} matches {req} before {CUTOFF}')
        bucket = _bucket(max(candidates, key=lambda v: v[0][:3])[0])
        in_bucket = [v for v in _versions(name) if _bucket(v[0]) == bucket]
        applying = [r for r in requirements[name]
                    if any(_matches(v[0], _comparators(r)) for v in in_bucket)]
        together = [v for v in in_bucket if all(_matches(v[0], _comparators(r)) for r in applying)]
        best = max(together, key=lambda v: v[0][:3])
        selected[(name, bucket)] = best
        return best

    edges, roots = {}, set()
    for _ in range(20):  # iterate to a fixed point: a pick can raise another requirement
        before = {k: v[1] for k, v in selected.items()}
        edges, roots = _walk(root_deps, pick, target)
        if {k: v[1] for k, v in selected.items()} == before:
            break

    linked, stack = set(), list(roots)
    while stack:
        key = stack.pop()
        if key in linked or _is_proc_macro(*key):
            continue
        linked.add(key)
        stack.extend(edges.get(key, ()))
    return linked


# --------------------------------------------------------------------------- binary check

def binary_kind(data):
    """'Mach-O arm64', 'ELF x86_64', 'PE x86_64' and so on, from an executable's header."""
    if data[:4] == b'\xcf\xfa\xed\xfe' and len(data) >= 8:
        cpu = int.from_bytes(data[4:8], 'little')
        return 'Mach-O ' + {0x0100000c: 'arm64', 0x01000007: 'x86_64'}.get(cpu, hex(cpu))
    if data[:4] == b'\x7fELF' and len(data) >= 20:
        machine = int.from_bytes(data[18:20], 'little')
        return 'ELF ' + {0x3e: 'x86_64', 0xb7: 'aarch64'}.get(machine, hex(machine))
    if data[:2] == b'MZ' and len(data) >= 0x40:
        offset = int.from_bytes(data[0x3c:0x40], 'little')
        if data[offset:offset + 4] == b'PE\x00\x00':
            machine = int.from_bytes(data[offset + 4:offset + 6], 'little')
            return 'PE ' + {0x8664: 'x86_64', 0xaa64: 'arm64'}.get(machine, hex(machine))
    return 'unrecognised'


def describe_binary(binary):
    """'Mach-O arm64, sha256 ...' for the notices and the build log."""
    data = pathlib.Path(binary).read_bytes()
    return f'{binary_kind(data)}, sha256 {hashlib.sha256(data).hexdigest()}'


def embedded_crates(binary):
    """{(name, version)} whose crates.io source paths the compiled binary embeds."""
    text = pathlib.Path(binary).read_bytes().decode('latin-1')
    found = set()
    for match in re.finditer(r'index\.crates\.io-[0-9a-f]+[/\\]([A-Za-z0-9_-]+?)-(\d+\.\d+\.\d+[0-9A-Za-z.+-]*?)[/\\]', text):
        found.add((match.group(1), match.group(2)))
    return found


# --------------------------------------------------------------------------- notices

def listed_crates(notices):
    """{(name, version)} from the table at the top of a notices file."""
    listed, in_table = set(), False
    for line in pathlib.Path(notices).read_text(encoding='utf-8').splitlines():
        if line.startswith('Crate '):
            in_table = True
            continue
        if in_table:
            if not line.strip():
                break
            name, version = line.split()[:2]
            listed.add((name, version))
    return listed


def _wrapped(text):
    return textwrap.wrap(text, 88, break_on_hyphens=False, break_long_words=False)


def write_notices(per_target, output, checked=()):
    union = sorted(set().union(*per_target.values()))
    texts = {}  # bytes -> first (crate, file) that shipped it
    about = (
        f'unifiedlog_iterator is built by Mandiant from https://github.com/{REPO} and is '
        'licensed under Apache-2.0 (LICENSE-unifiedlog_iterator beside this file). Its release '
        'binaries are built with the Rust crates listed below, which are distributed under their '
        'own licenses. Each crate\'s license files follow the list as the crate publishes them; '
        'a text that several crates ship identically is printed once, at its first crate.')
    method = (
        'The list reproduces, without Cargo, the dependency resolution of '
        f'examples/unifiedlog_iterator at tag {PINNED_VERSION} (commit {TAG_COMMIT}) against '
        f'the crates.io index as it stood at {CUTOFF}, when that release was published, '
        'keeping for each target the crates its build links (build-time and proc-macro crates '
        'are left out). Targets: ' + ', '.join(TARGETS) + '. Produced by '
        'admin/scripts/make_unifiedlog_notices.py.'
        + ''.join(f' Checked against {line}.' for line in checked))
    lines = ([f'Third-party notices for unifiedlog_iterator {PINNED_VERSION}', '']
             + _wrapped(about) + [''] + _wrapped(method)
             + ['', f'{"Crate":32} {"Version":12} {"License":30} Targets'])
    for name, version in union:
        manifest, _ = _crate(name, version)
        license_expr = (manifest.get('package') or {}).get('license', '(none declared)')
        on = [t for t in TARGETS if (name, version) in per_target[t]]
        where = 'all' if len(on) == len(TARGETS) else ', '.join(on)
        lines.append(f'{name:32} {version:12} {license_expr:30} {where}')
    for name, version in union:
        manifest, licenses = _crate(name, version)
        package = manifest.get('package') or {}
        lines += ['', '=' * 78, f'{name} {version}', f'License: {package.get("license", "(none declared)")}']
        if package.get('repository'):
            lines.append(f'Repository: {package["repository"]}')
        if not licenses:
            lines.append('This crate publishes no license file; the license above is the one its '
                         'Cargo.toml declares.')
        for file_name in sorted(licenses):
            body = licenses[file_name]
            if body in texts:
                first = texts[body]
                lines += ['', f'--- {file_name}: identical to {first[2]} of {first[0]} {first[1]} above']
                continue
            texts[body] = (name, version, file_name)
            lines += ['', f'--- {file_name}', body.decode('utf-8', 'replace').rstrip()]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return union


def verify(binaries, notices):
    """Check binaries against a notices file, raising SystemExit when one is not covered.

    A binary that names no crate at all fails too: stripped paths would pass any list.
    """
    listed = listed_crates(notices)
    failed = False
    for binary in binaries:
        embedded = embedded_crates(binary)
        missing = sorted(embedded - listed)
        print(f'{binary} ({describe_binary(binary)}): {len(embedded)} crate versions '
              f'embedded, {len(embedded) - len(missing)} of them listed in '
              f'{pathlib.Path(notices).name}')
        for name, version in missing:
            print(f'  NOT LISTED: {name} {version}')
        failed = failed or bool(missing) or not embedded
    if failed:
        raise SystemExit('the notices do not cover this binary')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--check-binary', action='append', default=[], metavar='PATH',
                        help='a downloaded unifiedlog_iterator binary to compare with')
    parser.add_argument('--verify', action='append', default=[], metavar='PATH',
                        help='check a binary against the committed notices file; no network')
    parser.add_argument('--output', type=pathlib.Path, default=OUTPUT)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify, args.output)
        return
    per_target = {target: resolve(target) for target in TARGETS}
    for target, crates in per_target.items():
        print(f'{target}: {len(crates)} linked crates')
    failed, checked = False, []
    for binary in args.check_binary:
        embedded = embedded_crates(binary)
        resolved = set().union(*per_target.values())
        missing = sorted(embedded - resolved)
        print(f'{binary}: {len(embedded)} crate versions embedded, '
              f'{len(embedded) - len(missing)} of them resolved')
        for name, version in missing:
            print(f'  NOT RESOLVED: {name} {version}')
        failed = failed or bool(missing) or not embedded
        checked.append(f'the binary ({describe_binary(binary)}) whose source paths name '
                       f'{len(embedded)} crate versions, all in the list')
    if failed:
        raise SystemExit('the resolution does not match the binary; nothing was written')
    union = write_notices(per_target, args.output, checked)
    print(f'wrote {args.output} ({len(union)} crates)')


if __name__ == '__main__':
    main()
