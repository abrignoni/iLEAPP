# Testing Against Non-Public Images

The normal test-case route records image content in the repository. `make_test_data.py`
copies every responsive file verbatim into `admin/test/cases/data/<module>/testdata.*.zip`,
and those zips are committed on purpose (`.gitignore` ignores that directory but
re-includes `testdata*.zip`). `test_module_output.py` then writes the parsed rows
themselves into `admin/test/results/<module>/`. Every case in the repository today comes
from one of the four publicly distributed images in
[image_manifest.json](../../image_manifest.json), so their device identifiers are already
public.

Some artifacts only appear in images that cannot be published. `devicelist.db` is the
first: it is absent from all four manifest images. For these,
`admin/test/scripts/test_local_corpus_artifacts.py` gives a repeatable check that leaves
no image content behind.

## Running

```
ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
    python -m pytest admin/test/scripts/test_local_corpus_artifacts.py -v
```

A `.zip` extraction or a directory of extracted files both work. Without the variable the
tests skip, which is what happens in CI and for anyone who does not hold the image. When
the image simply lacks the file, the test skips rather than fails.

## What these tests may assert

Structure only. Column counts, value shapes, timestamp ranges, whether a column came back
empty for every row. Never a value from the image, because an assertion failure prints
what it compared, and that output ends up in terminals, CI logs and pasted bug reports.

Use the helpers on `LocalCorpusTestCase` rather than the bare `unittest` ones where an
image value is involved:

- `assert_matches(value, pattern, label)` instead of `assertRegex`
- `assert_plausible_timestamp(value)` instead of comparing datetimes directly
- `assert_row_shape(headers, rows)` for the row-length check

Both redact through `_redact()` before reporting, so a failure shows `####-##-##` rather
than a real date.

## What they catch

Real regressions in the parts that synthetic fixtures cannot reach: a misread epoch, a
query naming a column the real schema does not have, a decode step that quietly returns
nothing, a value shape that only occurs in the wild. Injecting a wrong-epoch bug into
`appleAccountDeviceList` fails `test_device_list_structure` with a redacted message.

They are not a substitute for the synthetic unit tests in
`test_requested_ios_databases.py`, which run everywhere and are what a reviewer without
the image can execute. Write both: synthetic tests for the logic, a local corpus test for
fidelity against the real file.

## When an image becomes public

Add it to [image_manifest.json](../../image_manifest.json) following
[guide_adding_images.md](guide_adding_images.md) and generate normal test cases. The local
corpus test can stay; it costs nothing and keeps working for whoever holds the image.
