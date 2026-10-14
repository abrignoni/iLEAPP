---
paths:
  - "scripts/artifacts/**/*.py"
  - "scripts/*_parser.py"
---

<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# A field means what every writer of it means, not the one you went looking for

Before an artifact reads a field as a flag ("this record is encrypted", "this row was
deleted", "this entry was synced"), there are **two** questions, and only the second one
decides what the field means:

1. *Does the thing I suspect write this field?* Almost always yes. That is why you went
   looking, and finding it feels like confirmation.
2. **What else writes this field?** This is the question that establishes the meaning, and
   it is the one that goes unasked.

Answering only (1) produces a claim that is sourced, cited and wrong. That is worse than an
open guess, because it ships with a file and a line number and so reads as *more* checked
than an ordinary assertion.

## The check is one grep against the producer

```
grep -n "<the field>" <producer source>
```

Read **every** hit, not the one you predicted. A field with N writers has N meanings until
all N have been read. Then ask two follow-ups:

- **Is any writer outside the conditional you assumed guards it?** That unguarded writer is
  the one that breaks the claim.
- **Does anything ever clear it?** A field nothing resets accumulates history, so its value
  describes the record's whole life rather than its current state. Set once and never
  cleared turns a flag into a scar.

## What it cost (2026-09-07)

The MMKV reader treated the 16-byte AES vector at bytes 12 to 28 of the sibling `.crc` file
as the flag saying a store is encrypted. The encryption path really does write a random IV
there, so the source backed it up. The grep above returns four hits, and the fourth is
`MMKV::clearAll`, which fills the field with random bytes for **every** store it clears and
only afterwards checks whether there is a crypter to reset. Nothing anywhere zeroes it, so a
plaintext store that has ever been cleared carries a vector for life.

Measured over all 91 registered extractions: 1,840 MMKV stores, 106 carrying a vector, and
**47 of those (44%) ordinary readable plaintext**, including 18 WeChat stores. The reader
refused all 47 and its `recover` path refused a further 24 cleared stores, which is exactly
the population `recover` exists to read. A real profile run of one Android corpus gained
**570 rows** the moment the field stopped being read as a flag.

## Prefer deciding by content

Wherever the bytes can answer, read them instead of trusting somebody else's summary. The
MMKV fix requires the store's records to account for every byte of its recorded size, which
is decisive: 2,500 AES-CFB trials produced zero false plaintext verdicts. Use the flag only
for what it literally is, here an initialisation vector for a key the examiner supplies.

The same applies to any app store: a `deleted` column, a `dirty` bit, an `is_synced`
integer, a `modified` timestamp. Where a second field or the row's own content can
corroborate the flag, say so in the notes and report what you measured.

## Auditing for it

Three tells, all cheap:

- **A refusal is not audited the way an output is.** "This is encrypted, I will not guess"
  reads as caution, and nobody rechecks it. Being wrong in the careful direction hides a
  defect far longer than printing garbage would. Audit what an artifact refuses, not only
  what it emits.
- **A count produced by the suspect test looks like validation of it.** If the same rule
  both selects and counts, the number says nothing.
- **A test whose fixture asserts the premise cannot fail.** The MMKV suite had one that
  built a *plaintext* store, set a vector on it, and asserted refusal. Build the negative
  fixture out of the real thing (actual ciphertext), never out of the flag.

Related: `leapp-claims.md` for the wording an unestablished meaning gets in `notes`.
