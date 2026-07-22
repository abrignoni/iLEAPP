"""
Regression tests for streaming sidebar injection in the HTML report generator.

These tests cover the fix for issue #1746 ("MemoryError during HTML report
generation"). The previous implementation read each artifact's entire
``.temphtml`` page into memory and rebuilt it with string concatenation to
insert the navigation sidebar. For large extractions an artifact page can grow
to several GB, so that approach peaked at roughly three times the file size and
raised ``MemoryError``.

``scripts.report.stream_insert_sidebar_code`` now copies the page to its final
location in fixed-size chunks, keeping peak memory bounded regardless of file
size, while producing byte-identical output to the old whole-file approach.

The tests are self-contained: they build small synthetic pages (no forensic
data required) and can be run either with ``pytest`` or directly:

    python admin/test/scripts/test_report_streaming.py
"""

import os
import sys
import tracemalloc
import tempfile
import shutil

# Add the repository root to sys.path so ``scripts`` is importable.
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scripts import report
from scripts.html_parts import body_sidebar_dynamic_data_placeholder as PLACEHOLDER

SIDEBAR = "<nav id='sidebar'>SIDEBAR-NAV-CODE</nav>"


def _reference_render(content):
    """Whole-file reference implementation matching the pre-fix behaviour."""
    pos = content.find(PLACEHOLDER)
    if pos < 0:
        return content
    return content[:pos] + SIDEBAR + content[pos + len(PLACEHOLDER):]


def _render_via_stream(tmpdir, name, content):
    src = os.path.join(tmpdir, name + ".temphtml")
    dst = os.path.join(tmpdir, name + ".html")
    with open(src, "w", encoding="utf8") as handle:
        handle.write(content)
    report.stream_insert_sidebar_code(src, dst, SIDEBAR)
    with open(dst, "r", encoding="utf8") as handle:
        return handle.read()


def test_stream_insert_matches_reference_for_various_shapes():
    """Streaming output is byte-identical to the whole-file rendering."""
    big_row = "<tr>" + "".join("<td>c%d</td>" % i for i in range(20)) + "</tr>\n"
    chunk = 1024 * 1024  # matches the streaming chunk size

    cases = {
        # Placeholder near the top followed by a large table body.
        "big_body": "<html><body>\nsetup\n" + PLACEHOLDER + "\n"
        + big_row * 50000 + "</body></html>\n",
        "small": "A" + PLACEHOLDER + "B",
        "at_start": PLACEHOLDER + "trailing data",
        "at_end": "leading data" + PLACEHOLDER,
        # Placeholder deliberately straddling a chunk boundary.
        "split_boundary": "x" * (chunk - len(PLACEHOLDER) // 2)
        + PLACEHOLDER + "AFTER" + "y" * 32,
        "empty": "",
    }

    tmpdir = tempfile.mkdtemp()
    try:
        for name, content in cases.items():
            got = _render_via_stream(tmpdir, name, content)
            assert got == _reference_render(content), f"mismatch for case {name}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_missing_placeholder_copies_content_verbatim():
    """When the placeholder is absent the page is copied unchanged."""
    content = "no placeholder here " * 500
    tmpdir = tempfile.mkdtemp()
    try:
        got = _render_via_stream(tmpdir, "no_marker", content)
        assert got == content
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_peak_memory_is_bounded_for_large_page():
    """Peak memory stays far below the file size (issue #1746 regression).

    The old whole-file approach peaked at ~3x the page size; the streaming
    implementation must stay a small fraction of it, independent of page size.
    """
    big_row = "<tr>" + "".join("<td>c%d</td>" % i for i in range(20)) + "</tr>\n"
    content = "<html><body>\nsetup\n" + PLACEHOLDER + "\n" + big_row * 120000 \
        + "</body></html>\n"

    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, "large.temphtml")
        dst = os.path.join(tmpdir, "large.html")
        with open(src, "w", encoding="utf8") as handle:
            handle.write(content)
        file_size = os.path.getsize(src)
        # Sanity: fixture is large enough for the multiplier to matter.
        assert file_size > 16 * 1024 * 1024

        tracemalloc.start()
        report.stream_insert_sidebar_code(src, dst, SIDEBAR)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Streaming keeps peak well under half the file size; the old approach
        # would have needed roughly three times the file size.
        assert peak < file_size / 2, (
            f"peak {peak} not bounded vs file {file_size}")

        with open(dst, "r", encoding="utf8") as handle:
            assert handle.read() == _reference_render(content)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    test_stream_insert_matches_reference_for_various_shapes()
    test_missing_placeholder_copies_content_verbatim()
    test_peak_memory_is_bounded_for_large_page()
    print("All report streaming regression tests passed.")
