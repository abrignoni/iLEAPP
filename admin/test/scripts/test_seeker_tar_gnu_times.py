"""Pin the times a tar member's headers record beyond the ustar mtime.

A GNU-format header (magic "ustar  " and a NUL) keeps an access time at byte 345
and a change time at byte 357, 12 bytes each, where a POSIX header keeps its name
prefix (tar.h in the GNU tar manual, Standard section). GNU tar fills them for
--incremental (-G) and --listed-incremental (-g) archives. tarfile does not read
them: it takes bytes 345 to 500 of every header as a name prefix, so such a member
was named '<atime digits>/<name>'. libarchive (bsdtar) writes a file's birth time
as the PAX record LIBARCHIVE.creationtime.

The three archives below were written by GNU tar 1.35 (--format=gnu -G, and
--format=oldgnu --listed-incremental=/dev/null) and by bsdtar 3.5.3 with
libarchive 3.7.4 (--format pax). The other inputs are hand-built headers. Every
expected value is read from the raw header bytes by spec_members() below, which
follows the GNU tar manual and POSIX pax and does not use tarfile or the code under
test, or is a literal written into a hand-built header.
"""
import base64
import contextlib
import gzip
import io
import os
import pathlib
import sys
import tempfile
import unittest
import zlib
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerTar  # pylint: disable=wrong-import-position

GNU_INCREMENTAL_TAR = (
    'eNrt1kEOgjAQheGuPQUngHY67VyAS7hEcSsJ1OjxnRoXhoVxIQjyvk0TmpA07U8Z+mNlJmaVhPAY1XjMs8b5aEmi'
    '5fzcWfFsitrM4DKkpi+Kr7/3dUEuUBTnJYo3C1O3TWoMbNWg/ecjUP2yf6JR/y4yof857LvzqWwPZp+uXZluCUVs'
    'tP/nOZiq/8j85v5n4zgo69jn/kl0KOyq+9cFxSAhr2TB/eu271AB+q8m/P5/1r8PrCLrf4LzZGnt/a/j/tdtR/8A'
    'AAAAAAAAAAAAAAB/5A7w9V1p')
OLDGNU_LISTED_TAR = (
    'eNrt1j0OwjAMhmHPnKInoHbi2BfgEozlZwWJBsHxMYgBMSAGCgW+Z4lUVZGi5G3a75YtDYxZ2UuJ8eJ+DE6SjZNb'
    'vBnPhV2Zmhm9wb6v3a5pXj7v7YKkJHPJbp5pZGarrnYE/6qP/s9HoP1k/ynd9S+mhv7fYb7drKerBc3rYTutx4oi'
    '/rT/6zkYpH9hNtUH97+SaAksms/9J89CDX91/7EgK148j7r/2PYJKkD/7YDf/+f6z0WDafwnSE7Jvr3/m+ZH3H9s'
    'O/oHAAAAAAAAAAAAAAD4IScuWF2O')
BSDTAR_PAX_TAR = (
    'eNrtl01Lw0AQhnPur9hfkM7MzuxuDh5UhBY8FA/eY5uDB1tII/bnO0HUtCB+kKa2neeyhA0ky/C8bzIrN5OqXFT1'
    'eF3Ps/0AAFHEtauyuyqBHPoAFAOwbgBihJC5TTYAz+umrPVVejjk1uGOBA9u3jw+VRcYC0qCqShy4ihE4P2IwJVv'
    'uxJj8iEBjDLjhFDrx/t+xrf+68W2/6ARkDkx/weZ/+yjAxZlU/6H/KeA0fL/kPkPKJb/Z5L/rfX7LIE/5H8ksvwf'
    'dP6fJdC8rPJm0/Q6/8D89fyR0SF7YSWw6PyZAlj+Hy7/OTIXbf4X7/nf2ZUkgT2OfHK306vLu+vJ9P4mn9eV3rpa'
    'Wl0cZ/73bv3P/QfgHf/Jg2QOzP+9o2M3Rc3/bv+vllW+eBjQf9QSQhZFm9+3338+BrT+P1j/+5QCJpHO/1+EEIWK'
    'xFb7p+l/79b/tv+7/pP+Alr/D4GO3Vw1DMM4Q14B9Lzw5w==')

BLOCK = 512
GNU_MAGIC = b'ustar  \x00'
POSIX_MAGIC = b'ustar\x0000'


def fixture(encoded):
    return zlib.decompress(base64.b64decode(encoded))


def spec_number(field):
    """A numeric header field as the GNU tar manual describes it: octal digits and a
    NUL, or a leading 0x80 (0xFF when negative) and a big-endian base-256 number in
    two's complement. None for an all-NUL field, ValueError for anything else."""
    if not field.strip(b'\x00'):
        return None
    if field[0] in (0x80, 0xFF):
        value = int.from_bytes(field[1:], 'big')
        return value - 256 ** (len(field) - 1) if field[0] == 0xFF else value
    text = field.split(b'\x00', 1)[0].strip(b' ')
    if not text or text.strip(b'01234567'):
        raise ValueError(field)
    return int(text, 8)


def spec_members(data):
    """{name: (gnu atime field, gnu ctime field, pax records)} read from raw blocks."""
    members = {}
    pax = {}
    long_name = None
    pos = 0
    while pos + BLOCK <= len(data):
        block = data[pos:pos + BLOCK]
        if not block.strip(b'\x00'):
            break
        size = spec_number(block[124:136]) or 0
        body = data[pos + BLOCK:pos + BLOCK + size]
        pos += BLOCK + (size + BLOCK - 1) // BLOCK * BLOCK
        kind = block[156:157]
        if kind == b'x':
            while body:
                length = int(body.split(b' ', 1)[0])
                key, value = body[:length].split(b' ', 1)[1][:-1].split(b'=', 1)
                pax[key.decode()] = value.decode()
                body = body[length:]
            continue
        if kind == b'L':
            long_name = body.rstrip(b'\x00').decode()
            continue
        name = long_name or block[0:100].rstrip(b'\x00').decode()
        if block[257:263] == b'ustar\x00' and block[345]:
            name = block[345:500].rstrip(b'\x00').decode() + '/' + name
        gnu = block[257:265] == GNU_MAGIC
        members[name.rstrip('/')] = ((spec_number(block[345:357]) if gnu else None),
                                     (spec_number(block[357:369]) if gnu else None), pax)
        pax, long_name = {}, None
    return members


def octal(value, width):
    return b'%0*o\x00' % (width - 1, value)


def header(name, size=0, kind=b'0', mtime=1706400000, magic=GNU_MAGIC,
           atime=b'\x00' * 12, ctime=b'\x00' * 12, prefix=b''):
    block = bytearray(BLOCK)
    block[0:len(name)] = name.encode()
    block[100:108] = octal(0o644, 8)
    block[108:116] = octal(0, 8)
    block[116:124] = octal(0, 8)
    block[124:136] = octal(size, 12)
    block[136:148] = octal(mtime, 12)
    block[156:157] = kind
    block[257:265] = magic
    if magic == GNU_MAGIC:
        block[345:357] = atime
        block[357:369] = ctime
    else:
        block[345:345 + len(prefix)] = prefix
    block[148:156] = b' ' * 8
    block[148:156] = b'%06o\x00 ' % sum(block)
    return bytes(block)


def padded(content):
    return content + b'\x00' * (-len(content) % BLOCK)


def member(name, content=b'content', **fields):
    return header(name, len(content), **fields) + padded(content)


def pax_member(records, name, content=b'content', **fields):
    body = b''
    for key, value in records.items():
        record = f' {key}={value}\n'.encode()
        length = len(record) + len(str(len(record)))
        length = len(record) + len(str(length))
        body += str(length).encode() + record
    return (header('PaxHeader/x', len(body), kind=b'x', magic=POSIX_MAGIC) + padded(body)
            + member(name, content, **fields))


def base256(value):
    return bytes([0xFF if value < 0 else 0x80]) + (value % 256 ** 11).to_bytes(11, 'big')


@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


class TarHeaderTimesTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.logged = []
        patcher = mock.patch.object(search_files, 'logfunc', self.logged.append)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self._tmp.cleanup()

    def seek(self, data, pattern='*/data/*', name='in.tar', opener=open):
        path = os.path.join(self.tmp, name)
        with opener(path, 'wb') as out:
            out.write(data)
        out_dir = os.path.join(self.tmp, 'out-' + name)
        with quiet():
            seeker = FileSeekerTar(path, os.path.join(out_dir, 'data'))
            staged = seeker.search(pattern)
        self.addCleanup(seeker.cleanup)
        return {seeker.file_infos[p].source_path: seeker.file_infos[p]
                for p in staged if p in seeker.file_infos}  # folders have no record

    def archive(self, *members):
        return b''.join(members) + b'\x00' * (2 * BLOCK)

    def assert_gnu_archive(self, data):
        expected = spec_members(data)
        infos = self.seek(data)
        self.assertEqual(sorted(infos), ['src/data/one.db', 'src/data/two.txt'])
        for name, info in infos.items():
            atime, ctime, _ = expected[name]
            self.assertIsNotNone(atime)
            self.assertIsNotNone(ctime)
            self.assertEqual(info.times.accessed, atime)
            self.assertEqual(info.times.changed, ctime)
            self.assertIsNone(info.times.created)
            self.assertEqual(info.times.source, 'tar header')
        self.assertEqual(self.logged, [])

    def test_gnu_tar_incremental_archive(self):
        self.assert_gnu_archive(fixture(GNU_INCREMENTAL_TAR))

    def test_gnu_tar_oldgnu_listed_incremental_archive(self):
        self.assert_gnu_archive(fixture(OLDGNU_LISTED_TAR))

    def test_a_compressed_gnu_archive_is_read_the_same(self):
        data = fixture(GNU_INCREMENTAL_TAR)
        plain = self.seek(data)
        packed = self.seek(data, name='in.tar.gz', opener=gzip.open)
        self.assertEqual({n: i.times for n, i in packed.items()},
                         {n: i.times for n, i in plain.items()})

    def test_the_names_are_the_names_stored_and_a_dumpdir_is_a_folder(self):
        data = fixture(GNU_INCREMENTAL_TAR)
        path = os.path.join(self.tmp, 'in.tar')
        with open(path, 'wb') as out:
            out.write(data)
        folder = os.path.join(self.tmp, 'staged')
        with quiet():
            seeker = FileSeekerTar(path, folder)
            staged = seeker.search('*')
        self.addCleanup(seeker.cleanup)
        names = sorted(os.path.relpath(p, folder).replace(os.sep, '/') for p in staged)
        self.assertEqual(names, sorted(spec_members(data)))
        self.assertEqual(names, ['src', 'src/data', 'src/data/one.db', 'src/data/two.txt'])
        self.assertTrue(os.path.isdir(os.path.join(folder, 'src', 'data')))
        self.assertTrue(os.path.isfile(os.path.join(folder, 'src', 'data', 'one.db')))

    def test_bsdtar_creation_time_fills_created(self):
        data = fixture(BSDTAR_PAX_TAR)
        expected = spec_members(data)
        infos = self.seek(data)
        self.assertEqual(sorted(infos), ['src/data/one.db', 'src/data/two.txt'])
        for name, info in infos.items():
            pax = expected[name][2]
            self.assertEqual(info.times.created, float(pax['LIBARCHIVE.creationtime']))
            self.assertEqual(info.times.accessed, float(pax['atime']))
            self.assertEqual(info.times.changed, float(pax['ctime']))
            self.assertEqual(info.times.source, 'tar header')

    def test_base_256_fields(self):
        data = self.archive(member('d/data/one.db', atime=base256(1706400001),
                                   ctime=base256(-86400)))
        info = self.seek(data)['d/data/one.db']
        self.assertEqual(spec_members(data)['d/data/one.db'][:2], (1706400001, -86400))
        self.assertEqual((info.times.accessed, info.times.changed), (1706400001, -86400))

    def test_a_zero_field_is_kept_and_an_empty_one_is_not_recorded(self):
        data = self.archive(member('d/data/one.db', atime=octal(0, 12)))
        info = self.seek(data)['d/data/one.db']
        self.assertEqual(spec_members(data)['d/data/one.db'][:2], (0, None))
        self.assertEqual(info.times[:5], (1706400000, 0, None, None, 'tar header'))

    def test_leading_spaces_are_read_as_gnu_tar_reads_them(self):
        info = self.seek(self.archive(member('d/data/one.db', atime=b'  1234567\x00  ')))
        self.assertEqual(info['d/data/one.db'].times.accessed, 0o1234567)

    def test_a_malformed_field_is_logged_and_not_recorded(self):
        info = self.seek(self.archive(member('d/data/one.db', atime=b'12345678x\x00\x00\x00',
                                             ctime=octal(1706400002, 12))))['d/data/one.db']
        self.assertEqual((info.times.accessed, info.times.changed), (None, 1706400002))
        self.assertEqual(len(self.logged), 1)
        self.assertIn('access time field', self.logged[0])

    def test_a_time_a_date_cannot_hold_is_logged_and_not_recorded(self):
        info = self.seek(self.archive(member('d/data/one.db', ctime=base256(1 << 80))))
        self.assertIsNone(info['d/data/one.db'].times.changed)
        self.assertEqual(len(self.logged), 1)
        self.assertIn('change time field', self.logged[0])

    def test_a_pax_record_wins_over_the_gnu_field(self):
        data = self.archive(pax_member({'atime': '1706400005.5', 'ctime': ''}, 'd/data/one.db',
                                       atime=octal(1706400001, 12), ctime=octal(1706400002, 12)))
        info = self.seek(data)['d/data/one.db']
        self.assertEqual(spec_members(data)['d/data/one.db'][:2], (1706400001, 1706400002))
        # an empty PAX record deletes the value, header field included (POSIX pax)
        self.assertEqual((info.times.accessed, info.times.changed), (1706400005.5, None))

    def test_a_malformed_creation_time_is_logged_and_not_recorded(self):
        data = self.archive(pax_member({'LIBARCHIVE.creationtime': 'soon'}, 'd/data/one.db',
                                       magic=POSIX_MAGIC))
        self.assertIsNone(self.seek(data)['d/data/one.db'].times.created)
        self.assertEqual(len(self.logged), 1)
        self.assertIn('LIBARCHIVE.creationtime', self.logged[0])

    def test_a_long_name_keeps_its_name_and_times(self):
        name = 'd/data/' + 'n' * 120 + '.db'
        data = self.archive(header('././@LongLink', len(name) + 1, kind=b'L')
                            + padded(name.encode() + b'\x00'),
                            member(name[:100], atime=octal(1706400001, 12)))
        info = self.seek(data)
        self.assertEqual(list(info), [name])
        self.assertEqual(info[name].times.accessed, spec_members(data)[name][0])

    def test_a_posix_prefix_is_still_read(self):
        data = self.archive(member('one.db', magic=POSIX_MAGIC, prefix=b'd/data'))
        info = self.seek(data)
        self.assertEqual(list(info), ['d/data/one.db'])
        self.assertEqual(list(spec_members(data)), ['d/data/one.db'])
        self.assertEqual(info['d/data/one.db'].times[:5], (1706400000, None, None, None, 'tar header'))


if __name__ == '__main__':
    unittest.main()
