"""Reads the privacy designation a corpus registry entry carries.

A corpus registry (``samples.json``) lives with the test data, outside this
repository. An entry whose provider set terms for it carries four fields:

* ``private``: true when the provider designated the content private, false
  when the designation is recorded as not private, null when the terms are
  not established.
* ``allow_fixtures``: whether bytes from the corpus, or a test case cut from
  it, may be committed to a repository.
* ``allow_public_metadata``: whether the corpus key, row counts and other
  non-identifying metadata may appear in repository text (``sample_data``,
  notes, test baselines).
* ``privacy_basis``: one sentence naming where the designation comes from.

An entry without these fields has no designation recorded. That is not a
statement that it is public, so nothing here treats a missing field as
permission or as a refusal; the callers decide what absence means for them.

Standard library only, so every caller stays importable in CI. The file is the
same in all five LEAPP cores.
"""
import hashlib
from pathlib import Path

PRIVACY_FIELDS = ("private", "allow_fixtures", "allow_public_metadata", "privacy_basis")

# Returned by field_state for a field the entry does not carry, so that a
# recorded null (terms not established) is never confused with no record.
ABSENT = "absent"

_HASH_CHUNK = 1 << 22


def field_state(entry, field):
    """Return True, False or None as recorded for ``field``, or ABSENT."""
    if not isinstance(entry, dict) or field not in entry:
        return ABSENT
    value = entry[field]
    if value is None or isinstance(value, bool):
        return value
    # Anything else is not a value the schema defines; treat it as not
    # established rather than guessing which way it was meant.
    return None


def basis(entry):
    """The entry's privacy_basis sentence, or an empty string."""
    value = entry.get("privacy_basis") if isinstance(entry, dict) else None
    return value.strip() if isinstance(value, str) else ""


def describe(name, entry, field):
    """A one-line reason naming the key, the field's value and its basis."""
    state = field_state(entry, field)
    shown = "null (terms not established)" if state is None else str(state).lower()
    reason = f"registry entry '{name}' has {field}: {shown}"
    why = basis(entry)
    return f"{reason}. Basis: {why}" if why else reason


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_entry(registry, registry_path, input_path):
    """Find the registry entry for a file, or return (None, None).

    Tries the registered path first, resolving symlinks on both sides. A copy
    that was moved or renamed is then found by content: only entries whose
    registered file has the same size are hashed, so a miss costs one stat per
    entry and at most one hash of the input.
    """
    samples = (registry or {}).get("samples") or {}
    base = Path(registry_path).resolve().parent
    source = Path(input_path).expanduser().resolve()
    if not source.is_file():
        return None, None

    same_size = []
    size = source.stat().st_size
    for name, entry in samples.items():
        relative = ((entry or {}).get("match") or {}).get("zip")
        if not relative:
            continue
        target = (base / relative).resolve()
        if target == source:
            return name, entry
        try:
            if target.is_file() and target.stat().st_size == size:
                same_size.append((name, entry))
        except OSError:
            continue

    if not same_size:
        return None, None
    actual = None
    for name, entry in same_size:
        expected = ((entry or {}).get("match") or {}).get("sha256")
        if not expected:
            continue
        if actual is None:
            actual = _sha256(source)
        if actual == expected.lower():
            return name, entry
    return None, None


def refuses(entry, field):
    """True when ``field`` is recorded as false or null on the entry."""
    return field_state(entry, field) in (False, None)
