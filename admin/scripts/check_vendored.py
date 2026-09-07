#!/usr/bin/env python3
"""Confirm a vendored file still matches the upstream commit its banner names.

Vendored code is a copy, so it drifts in two directions and both are silent. A
local edit looks like a fix until the next re-vendor reverts it, and an upstream
release leaves this copy quietly old. Neither shows up in a diff of this repo.

Each vendored file opens with a banner that records where it came from: the
upstream repository, the file inside it, and the commit it was copied at. This
script reads that banner, fetches the upstream file at that exact commit, and
fails when anything below the banner differs from it. Only the banner is
ignored; the rest has to match byte for byte.

"Could not check" is reported separately from "has drifted", and they are not the
same result. A failed fetch says nothing about this copy, so printing it as drift
asserts a finding nothing measured. Both still exit non-zero: an unreachable
upstream must not read as a pass, or a broken network silently stops guarding the
file. Drift exits 1, an unreadable upstream exits 2.

    python3 admin/scripts/check_vendored.py                    # CI: fetch and compare
    python3 admin/scripts/check_vendored.py --upstream ../mmkv-parser
                                                                # offline: compare against a
                                                                # local checkout instead

To re-vendor: copy the upstream file over the body below the banner, set the
banner's upstream commit line to the commit you copied from, and run this script
before pushing.

The banner is the block from the first line of the file through the next rule
line (``# ----``). Inside it the script looks for ``github.com/<owner>/<repo>``,
``upstream commit <40 hex>`` and ``upstream file <path>``.
"""

from __future__ import annotations

import argparse
import collections
import difflib
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Every file this guards, relative to the repository root. Each one carries its
# own banner naming the upstream it was copied from.
VENDORED = [
    'scripts/mmkv_parser.py',
]

RAW_URL = 'https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}'
_RULE = re.compile(rb'^# -{20,}\s*$')
_REPO = re.compile(r'github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)')
_COMMIT = re.compile(r'upstream commit ([0-9a-f]{40})\b')
_FILE = re.compile(r'upstream file (\S+?)[.,]?(?:\s|$)')


DRIFT = 'drift'      # compared against the upstream, and it differs
BLOCKED = 'blocked'  # the upstream could not be read, so nothing was compared

Problem = collections.namedtuple('Problem', 'kind text')


class BannerError(Exception):
    """The vendored file does not open with a banner this script can read."""


def split_banner(data):
    """Return (banner_bytes, body_bytes) for a vendored file's contents."""
    lines = data.splitlines(keepends=True)
    if not lines or not _RULE.match(lines[0]):
        raise BannerError('does not open with a "# ----" rule line')
    for index in range(1, len(lines)):
        if _RULE.match(lines[index]):
            cut = sum(len(line) for line in lines[:index + 1])
            return data[:cut], data[cut:]
    raise BannerError('banner has no closing "# ----" rule line')


def parse_banner(banner):
    """Return {'owner', 'repo', 'commit', 'file'} read out of the banner text."""
    text = banner.decode('utf-8', errors='replace')
    repo = _REPO.search(text)
    commit = _COMMIT.search(text)
    upstream_file = _FILE.search(text)
    missing = [name for name, found in (('github.com/<owner>/<repo>', repo),
                                        ('upstream commit <sha>', commit),
                                        ('upstream file <path>', upstream_file))
               if not found]
    if missing:
        raise BannerError('banner is missing ' + ', '.join(missing))
    return {'owner': repo.group(1), 'repo': repo.group(2),
            'commit': commit.group(1), 'file': upstream_file.group(1)}


def fetch_upstream(info, timeout=30):
    """Return the bytes of the upstream file at the pinned commit."""
    url = RAW_URL.format(owner=info['owner'], repo=info['repo'],
                         commit=info['commit'], path=info['file'])
    with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec: fixed https host
        return response.read()


def read_local_upstream(info, upstream_dir):
    """Return the bytes of the upstream file from a local checkout."""
    path = os.path.join(upstream_dir, info['file'])
    with open(path, 'rb') as handle:
        return handle.read()


def compare(rel_path, body, upstream):
    """Return a list of DRIFT problems; empty when body matches upstream."""
    if body == upstream:
        return []
    diff = difflib.unified_diff(
        upstream.decode('utf-8', errors='replace').splitlines(keepends=True),
        body.decode('utf-8', errors='replace').splitlines(keepends=True),
        fromfile='upstream', tofile=rel_path, n=1)
    excerpt = ''.join(list(diff)[:40])
    return [Problem(DRIFT,
                    f'{rel_path}: does not match the upstream file at the pinned commit\n'
                    f'    Either it was edited here, which is not the place to fix it, or it was\n'
                    f'    re-vendored without updating the banner\'s upstream commit line.\n'
                    + ''.join('    ' + line for line in excerpt.splitlines(keepends=True)))]


def check_file(rel_path, upstream_dir=None):
    """Return a list of Problems for one vendored file; empty means it matches.

    A missing file or an unreadable banner is a DRIFT problem: both are statements
    about this repository's copy. An upstream that cannot be read is BLOCKED, because
    no comparison happened and nothing was learned about the copy either way.
    """
    path = os.path.join(REPO, rel_path)
    if not os.path.isfile(path):
        return [Problem(DRIFT, f'{rel_path}: listed in VENDORED but not on disk')]
    with open(path, 'rb') as handle:
        data = handle.read()
    try:
        banner, body = split_banner(data)
        info = parse_banner(banner)
    except BannerError as exc:
        return [Problem(DRIFT, f'{rel_path}: {exc}')]
    try:
        if upstream_dir:
            upstream = read_local_upstream(info, upstream_dir)
            source = os.path.join(upstream_dir, info['file'])
        else:
            upstream = fetch_upstream(info)
            source = f"{info['owner']}/{info['repo']}@{info['commit'][:7]}:{info['file']}"
    except (OSError, urllib.error.URLError) as exc:
        return [Problem(BLOCKED,
                        f'{rel_path}: could not read the upstream file ({exc}); '
                        f'pass --upstream <checkout> to compare offline')]
    problems = compare(rel_path, body, upstream)
    if not problems:
        print(f'  {rel_path}  matches {source}')
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--upstream', metavar='DIR',
                        help='a local checkout of the upstream repository, compared against '
                             'instead of fetching the pinned commit from GitHub')
    args = parser.parse_args(argv)

    problems = []
    for rel_path in VENDORED:
        problems.extend(check_file(rel_path, args.upstream))

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
    print(f'\n{len(VENDORED)} vendored file(s), all matching the pinned upstream commit.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
