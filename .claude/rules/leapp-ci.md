<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# CI facts that are not obvious from the workflow files

## Lint warnings are build failures

`.github/workflows/python_lint.yml` runs `pylint --disable=C,R`, which disables only
convention and refactor messages. **Every remaining `W` fails the job.** "It ran fine
locally" is not evidence CI passed.

It lints the **whole file** for any file the change touches, so a one-line edit surfaces
pre-existing warnings elsewhere in that file. That is expected, not a regression you
introduced. The repo convention for genuinely-unavoidable cases is an inline
`# pylint: disable=...`. Generated `*_pb2.py` and vendored code carry `# pylint: skip-file`
headers so they stay silent.

Two warnings bite new artifacts in particular:

- `W0718` broad-exception-caught. Do not write a bare `except Exception` around a protobuf
  decode. Use the house error tuple.
- `W0102` dangerous-default-value. Never default a parameter to a shared dict or list.

Reproduce it before pushing:

```bash
PYTHONPATH=. python3 -m pylint $(git diff --name-only main...HEAD | grep '\.py$') --disable=C,R
```

Note this shell is zsh, where an unquoted `$FILES` does **not** word-split. Passing one
newline-embedded argument to pylint produces a bogus roaming `F0001: No module named`.
Use `xargs` or `${=VAR}` for multi-file commands.

## The runtime contract is the guard against old-Python breaks

Lint runs on one newer Python. Syntax that only parses on 3.12+ (notably a multi-line
expression inside an f-string, PEP 701) reaches main unnoticed and then fails unrelated
PRs. `python_runtime_contract.yml` runs the test suite across the supported versions and
imports every artifact module through the real plugin loader.

**Its path filter must include `scripts/**`**, or artifact changes never trigger it. A job
that is green because it tested nothing is worse than no job.

`ast.parse(..., feature_version=...)` does **not** catch the f-string case; tokenization
changed at the tokenizer level, not the grammar level. To verify a port properly, build a
real venv on the oldest supported version, run the exact CI command, then inject a
multi-line f-string into an artifact and confirm it fails there while still passing on new.

## Before merging

Run `gh pr checks <n>` and wait for it to pass. Do not merge on the assumption that a
green local run means a green build.
