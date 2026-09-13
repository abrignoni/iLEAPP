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

| Platform | Archive sha256 |
|---|---|
| macOS arm64 | `d3e0e620b51358dc3f4a7d376551a435153e9a4a7942cb52ddb7144a72bbdb63` |
| macOS x86_64 | `28f4a5641543559ef90472537950fafb344a13eb64c432d7929748b45007afe8` |
| Linux arm64 (gnu) | `1e519eef11e5763d44311600077318d9bdd2c8b1c806191b7c9b345e1c995c5f` |
| Linux x86_64 (musl) | `43fb304af5b3cc19ce15490f6e0ff4255e7707b69c51fc67e279677ea9784adb` |
| Linux x86_64 (gnu) | `f5a17b056092be347e5d7f5051a6c3698e635bd7eeb22e595efbf13897e03419` |
| Windows x86_64 | `749731fc09d0d107958d777188c99682db8f2d7810835d6afe46172e1d0d9d36` |

Project: [mandiant/macos-UnifiedLogs](https://github.com/mandiant/macos-UnifiedLogs),
version v0.6.0 (released 2026-05-07), Apache-2.0 (`LICENSE-unifiedlog_iterator`).

Every digest above was verified by downloading the archive and hashing it independently,
not by trusting the published `.sha256` files alone. Digest comparison in the fetch
script is case-insensitive: upstream's Windows `.sha256` is published in UPPERCASE
(PowerShell `Get-FileHash` style) while the others are lowercase, and some files print
the digest twice on one line. Presentation quirks of the publication, not corruption.
When bumping PINNED_VERSION, verify and pin all six the same way.

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
