# bin/

Holds the third-party `unifiedlog_iterator` executable used to read Apple Unified Log
`.tracev3` data directly, so Unified Logs can be imported without a Mac and without
Apple's `log show`. See `scripts/unifiedlogs.py` for how iLEAPP calls it.

The executable is **not committed**. It is fetched per build:

```
python admin/scripts/fetch_unifiedlog_iterator.py
```

That verifies a pinned SHA-256 before writing anything, and also writes
`LICENSE-unifiedlog_iterator` next to the binary. Builds without it still succeed; they
just ship without native Unified Log support, and the artifact reports that at runtime.

## What is pinned

| | |
|---|---|
| Project | [mandiant/macos-UnifiedLogs](https://github.com/mandiant/macos-UnifiedLogs) |
| Version | v0.6.0 (released 2026-05-07) |
| License | Apache-2.0 (`LICENSE-unifiedlog_iterator`) |
| macOS arm64 archive sha256 | `d3e0e620b51358dc3f4a7d376551a435153e9a4a7942cb52ddb7144a72bbdb63` |
| Linux x86_64 (musl) archive sha256 | `43fb304af5b3cc19ce15490f6e0ff4255e7707b69c51fc67e279677ea9784adb` |

Digests for the other platforms are read from the `.sha256` files published with the
release and printed by the fetch script; pin them in `ASSETS` as each is first used for a
build. Some of upstream's `.sha256` files repeat the digest twice on one line, which is a
quirk of their release workflow, not a corrupted file.

## Linux: musl, not gnu

`linux-x86_64` fetches the **musl** build, verified `static-pie linked` - it carries no
dynamic libc dependency at all. The gnu build links the glibc of whatever machine built
it, and a binary built against a newer glibc refuses to start on older distros with
`version 'GLIBC_x.yy' not found`. iLEAPP ships Linux as an AppImage, whose whole premise
is one file that runs anywhere; forensic workstations also skew old and locked down.
`--platform linux-x86_64-gnu` remains available. No musl build is published for aarch64.

## Why the version is pinned

An examiner needs to be able to say which parser produced a set of records. Pin the
version, record it here, and change both together. When a release is built, the version
above is the one that shipped.

## License obligations

Apache-2.0 permits redistribution inside this MIT-licensed project. Two things must hold
for any build that includes the binary:

- `LICENSE-unifiedlog_iterator` ships alongside it. The PyInstaller specs refuse to build
  if the binary is present and the license is not.
- Attribution stays in `ATTRIBUTIONS.md`.

The published binary statically links its Rust dependencies, which carry their own
(predominantly MIT and Apache-2.0) licenses. Upstream ships only its own LICENSE in the
release archive, and that is what is redistributed here. A build that wants a complete
third-party notice file would need to generate one from the upstream crate graph.
