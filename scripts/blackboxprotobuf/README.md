# Vendored: blackboxprotobuf 1.0.1

Vendored copy of the `blackboxprotobuf` package from PyPI, version 1.0.1
(Yogesh Khatri's packaging of NCC Group's blackboxprotobuf library, MIT
licensed — see LICENSE). The only changes from the released package are the
internal absolute imports, rewritten from `blackboxprotobuf.lib...` to
`scripts.blackboxprotobuf.lib...` so the copy is self-contained.

## Why vendored

The PyPI release pins `protobuf==3.10.0` in its metadata, which blocks
upgrading the protobuf runtime past known CVEs (GHSA-8gq9-2x98-w8hf,
GHSA-8qvm-5x2c-j2w7, GHSA-7gcm-g887-7qv7). The library itself works
unchanged on protobuf 5.x — only the pin is stale, and 1.0.1 is the final
PyPI release under this name.

NCC Group's maintained successor (`bbpb` on PyPI) was evaluated instead,
but its decoder output differs from 1.0.1 in ways that change parsed
artifact data: length-delimited fields that happen to be valid UTF-8 decode
as `str` instead of `bytes`, and fields with alternate typedefs are
returned as lists instead of split `'N-M'` keys (which
`scripts/artifacts/googleLastTrip.py`, among others, depends on). ALEAPP's
artifacts are written against the 1.0.1 output contract, so the exact 1.0.1
decoder is kept.

## Usage

Do not import this package directly from artifacts. Use the wrapper:

```python
from scripts.ilapfuncs import decode_protobuf
values, types = decode_protobuf(data)
```

Keeping every call behind `decode_protobuf` means a future migration to the
maintained `bbpb` package only has to reconcile decoder behavior in one
place, with per-artifact fixes handled on their own schedule.
