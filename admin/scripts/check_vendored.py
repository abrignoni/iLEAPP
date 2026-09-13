#!/usr/bin/env python3
"""Confirm the vendored third-party files still match what was vendored.

Vendored code is a copy, so it drifts in two directions and both are silent. A
local edit looks like a fix until the next re-vendor reverts it, and an upstream
release leaves this copy quietly old. Neither shows up in a diff of this repo.

Every vendored file is recorded in scripts/vendor/vendored.json: its path in this
repository, the upstream repository and file, the upstream commit it was copied
at, and the sha256 of the copy. Two checks run per entry:

  1. the file on disk hashes to what the manifest records, which needs nothing
     but the checkout, and catches an edit made here;
  2. the file's body equals the upstream file at the pinned commit, fetched
     from GitHub, or read from a checkout named with --upstream, which catches a
     re-vendor whose commit line was not updated, or a copy that was edited and
     then had its hash re-recorded.

A file whose copy opens with a vendoring banner (a block from the first ``# ----``
rule line to the next) is marked ``"banner": true`` in the manifest; the banner
is this repository's, so the body below it is what has to match upstream. The
recorded sha256 still covers the whole file.

"Could not check" is reported separately from "has drifted", and they are not the
same result. An upstream that cannot be read was never compared, so calling it
drift asserts a finding nothing measured. Both still exit non-zero: an unreadable
upstream must not read as a pass. Drift exits 1, an unreadable upstream exits 2.

    python3 admin/scripts/check_vendored.py                     # CI: hashes and the pinned upstream
    python3 admin/scripts/check_vendored.py --offline           # hashes only
    python3 admin/scripts/check_vendored.py --upstream ../qnxprobe
    python3 admin/scripts/check_vendored.py --upstream qnxprobe=../qnxprobe --upstream ewfprobe=../ewfprobe
    python3 admin/scripts/check_vendored.py --update            # after a deliberate re-vendor

--update rewrites the recorded hashes from the files on disk and nothing else:
the upstream commit and date are what say which version a copy is, so set those
by hand from the upstream's log before running it.
"""

from __future__ import annotations

import argparse
import collections
import difflib
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(REPO, 'scripts', 'vendor', 'vendored.json')

RAW_URL = 'https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}'
_RULE = re.compile(rb'^# -{20,}\s*$')
_REPO = re.compile(r'github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$')

DRIFT = 'drift'      # compared, and the bytes differ
BLOCKED = 'blocked'  # nothing was compared, so this says nothing about the copy

Problem = collections.namedtuple('Problem', 'kind text')


class BannerError(Exception):
    """The vendored file does not open with a banner this script can read."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def split_banner(data):
    """Return (banner_bytes, body_bytes) for a file that opens with a banner block."""
    lines = data.splitlines(keepends=True)
    if not lines or not _RULE.match(lines[0]):
        raise BannerError('does not open with a "# ----" rule line')
    for index in range(1, len(lines)):
        if _RULE.match(lines[index]):
            cut = sum(len(line) for line in lines[:index + 1])
            return data[:cut], data[cut:]
    raise BannerError('banner has no closing "# ----" rule line')


def body_of(entry, data):
    """The part of a vendored copy that has to equal the upstream file."""
    if entry.get('banner'):
        return split_banner(data)[1]
    return data


def fetch_upstream(entry, timeout=30):
    """Return the bytes of the upstream file at the pinned commit, from GitHub."""
    match = _REPO.search(entry['upstream'])
    if not match:
        raise urllib.error.URLError(f"cannot read an owner/repo out of {entry['upstream']!r}")
    url = RAW_URL.format(owner=match.group(1), repo=match.group(2),
                         commit=entry['commit'], path=entry['upstream_file'])
    with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec: fixed https host
        return response.read()


def parse_upstream_args(values):
    """{name or '*': directory} from repeated --upstream NAME=DIR or DIR values."""
    out = {}
    for value in values or ():
        name, sep, folder = value.partition('=')
        if sep and name and folder:
            out[name] = folder
        else:
            out['*'] = value
    return out


def upstream_bytes(entry, upstreams):
    """(bytes, description, from_checkout) for the upstream file, or raise OSError/URLError."""
    folder = upstreams.get(entry['name']) or upstreams.get('*')
    if folder:
        path = os.path.join(folder, entry['upstream_file'])
        with open(path, 'rb') as handle:
            return handle.read(), path, True
    return (fetch_upstream(entry),
            f"{entry['upstream']}@{entry['commit'][:7]}:{entry['upstream_file']}", False)


def compare(rel_path, body, upstream, source, from_checkout):
    """A DRIFT problem describing how body differs from upstream, or None.

    A checkout is whatever it has checked out, which may be ahead of or behind
    the pinned commit, so a difference against one is worded as the checkout
    differing rather than as the copy being wrong; both are worth knowing and
    both exit 1. A fetch is the pinned commit itself, so a difference there is
    the copy's.
    """
    if body == upstream:
        return None
    diff = difflib.unified_diff(
        upstream.decode('utf-8', errors='replace').splitlines(keepends=True),
        body.decode('utf-8', errors='replace').splitlines(keepends=True),
        fromfile=source, tofile=rel_path, n=1)
    excerpt = ''.join(list(diff)[:40])
    if from_checkout:
        head = (f'{rel_path}: differs from the checkout at {source}\n'
                f'    The checkout may be ahead of the commit this copy was vendored at, in\n'
                f'    which case re-vendor if the upstream change is wanted here; or the copy\n'
                f'    was edited, which is not the place to fix it.\n')
    else:
        head = (f'{rel_path}: does not match the upstream file at the pinned commit\n'
                f'    Either it was edited here, which is not the place to fix it, or it was\n'
                f'    re-vendored without updating the manifest\'s commit.\n')
    return Problem(DRIFT, head + ''.join('    ' + line for line in excerpt.splitlines(keepends=True)))


def check_entry(entry, upstreams, offline):
    """Return a list of Problems for one manifest entry; empty means it matches."""
    path = os.path.join(REPO, entry['path'])
    if not os.path.isfile(path):
        return [Problem(DRIFT, f"{entry['path']}: recorded in the manifest but not on disk")]
    with open(path, 'rb') as handle:
        data = handle.read()
    actual = sha256(data)
    if actual != entry['sha256']:
        return [Problem(
            DRIFT,
            f"{entry['path']}: does not match what was vendored\n"
            f"    recorded {entry['sha256']}\n"
            f"    on disk  {actual}\n"
            f"    Either it was edited here, which is not the place to fix it, or it was\n"
            f"    re-vendored without running --update.")]
    print(f"  {entry['path']}  matches {entry['name']} {entry['version']} "
          f"({entry['commit'][:7]})")
    if offline:
        return []
    try:
        body = body_of(entry, data)
    except BannerError as exc:
        return [Problem(DRIFT, f"{entry['path']}: {exc}")]
    try:
        upstream, source, from_checkout = upstream_bytes(entry, upstreams)
    except (OSError, urllib.error.URLError) as exc:
        return [Problem(BLOCKED,
                        f"{entry['path']}: could not read the upstream file ({exc}); "
                        f"pass --upstream <checkout> to compare offline, or --offline "
                        f"to check the recorded hashes alone")]
    problem = compare(entry['path'], body, upstream, source, from_checkout)
    if problem:
        return [problem]
    print(f'    and matches {source}')
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--upstream', metavar='[NAME=]DIR', action='append',
                        help='a checkout of an upstream repo to compare against instead '
                             'of fetching; NAME= limits it to that manifest entry name')
    parser.add_argument('--offline', action='store_true',
                        help='check only the recorded hashes; do not read any upstream')
    parser.add_argument('--update', action='store_true',
                        help='rewrite the recorded hashes from the files on disk, '
                             'for use only after a deliberate re-vendor')
    args = parser.parse_args(argv)

    with open(MANIFEST, encoding='utf-8') as handle:
        manifest = json.load(handle)

    if args.update:
        for entry in manifest['vendored']:
            path = os.path.join(REPO, entry['path'])
            if not os.path.isfile(path):
                print(f"  {entry['path']}: recorded in the manifest but not on disk")
                return 1
            with open(path, 'rb') as handle:
                entry['sha256'] = sha256(handle.read())
            print(f"  recorded {entry['path']} at {entry['sha256']}")
        with open(MANIFEST, 'w', encoding='utf-8') as handle:
            json.dump(manifest, handle, indent=2)
            handle.write('\n')
        print('manifest updated')
        return 0

    upstreams = parse_upstream_args(args.upstream)
    problems = []
    for entry in manifest['vendored']:
        problems.extend(check_entry(entry, upstreams, args.offline))

    drifted = [p.text for p in problems if p.kind == DRIFT]
    blocked = [p.text for p in problems if p.kind == BLOCKED]

    if drifted:
        print('\nVendored files have drifted:\n')
        for text in drifted:
            print(f'  {text}\n')
    if blocked:
        print('\nVendored files could not be checked. The upstream could not be read, so\n'
              'nothing was compared and this is not evidence either way about the copies\n'
              'in this repository:\n')
        for text in blocked:
            print(f'  {text}\n')

    if drifted:
        return 1
    if blocked:
        return 2

    what = 'what was recorded' if args.offline else 'what was recorded and the pinned upstream'
    print(f"\n{len(manifest['vendored'])} vendored file(s), all matching {what}.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
