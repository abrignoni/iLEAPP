"""Known-answer tests for scripts.mmkv_parser. Expected bytes are written out as literals
so the test cannot inherit a defect from the code it checks."""
import struct, pathlib, pytest
from scripts.mmkv_parser import read_entries, read_dict, decode_value, MMKVError

def varint(n):
    out=bytearray()
    while True:
        b=n&0x7f; n>>=7
        out.append(b|0x80 if n else b)
        if not n: return bytes(out)

def entry(k,v):
    kb=k.encode(); vb=v.encode()
    return varint(len(kb))+kb+varint(len(vb)+len(varint(len(vb))))+varint(len(vb))+vb   # string container = varint len + bytes

def store(items_size_bytes, entries, pad=64):
    body=items_size_bytes+b''.join(entries)
    return struct.pack('<I',len(body))+body+b'\x00'*pad

@pytest.mark.parametrize('holder', [
    b'\xff\xff\xff\x07',      # 4-byte append-path placeholder (0x00ffffff)
    b'\x96\xf6\xc2\x01',      # 4-byte real size, as in a 3 MB store
    b'\xb7\xd7\x5a',          # 3-byte size: the shape that read as zero keys before
    b'\x9f\x1f',              # 2-byte
    b'\x00',                  # 1-byte (small full-rewrite store)
])
def test_first_key_follows_the_items_size_varint(tmp_path, holder):
    p=tmp_path/'s'; p.write_bytes(store(holder,[entry('alpha','one'),entry('beta','two')]))
    ents=read_entries(str(p))
    assert [k for k,_ in ents]==['alpha','beta']
    assert read_dict(str(p))=={'alpha':'one','beta':'two'}

def test_superseded_entries_are_kept_by_read_entries_and_collapsed_by_read_dict(tmp_path):
    p=tmp_path/'s'; p.write_bytes(store(b'\x00',[entry('k','v1'),entry('k','v2')]))
    assert [k for k,_ in read_entries(str(p))]==['k','k']
    assert read_dict(str(p))=={'k':'v2'}

def test_zero_actual_size_is_empty(tmp_path):
    p=tmp_path/'s'; p.write_bytes(b'\x00\x00\x00\x00'+b'\x00'*60)
    assert read_entries(str(p))==[]

def test_encrypted_store_is_refused_not_garbage(tmp_path):
    p=tmp_path/'s'; p.write_bytes(store(b'\x00',[entry('a','b')]))
    meta=bytearray(32); meta[12:28]=bytes(range(1,17))          # non-zero AES vector
    (tmp_path/'s.crc').write_bytes(bytes(meta))
    with pytest.raises(MMKVError):
        read_entries(str(p))

def test_zero_vector_meta_is_not_encryption(tmp_path):
    p=tmp_path/'s'; p.write_bytes(store(b'\x00',[entry('a','b')]))
    (tmp_path/'s.crc').write_bytes(bytes(32))
    assert read_dict(str(p))=={'a':'b'}
