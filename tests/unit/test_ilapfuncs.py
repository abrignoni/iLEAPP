"""Unit tests for key utilities in scripts/ilapfuncs.py"""
import sqlite3
import plistlib
import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# artifact_processor decorator tests
# ---------------------------------------------------------------------------

def test_artifact_processor_wraps_function():
    """Decorated function exposes __wrapped__ attribute pointing to original."""
    from scripts.ilapfuncs import artifact_processor

    @artifact_processor
    def _test_wrap(files_found, report_folder, seeker, wrap_text, timezone_offset):
        return (), [], ""

    assert hasattr(_test_wrap, "__wrapped__")
    assert callable(_test_wrap.__wrapped__)


def test_detects_five_arg_signature():
    """Decorator calls original function with 5 legacy args when it has 5 params."""
    from scripts.ilapfuncs import artifact_processor

    called_with = {}

    @artifact_processor
    def _test_5arg(files_found, report_folder, seeker, wrap_text, timezone_offset):
        called_with["files_found"] = files_found
        called_with["report_folder"] = report_folder
        return (), [], ""

    _test_5arg([], "/tmp/rpt", MagicMock(), False, 0)
    assert called_with["files_found"] == []
    assert called_with["report_folder"] == "/tmp/rpt"


def test_detects_one_arg_signature():
    """Decorator calls original function with Context when it has 1 param."""
    from scripts.ilapfuncs import artifact_processor
    from scripts.context import Context

    received = {}

    @artifact_processor
    def _test_1arg(context):
        received["ctx"] = context
        return (), [], ""

    Context.set_report_folder("/tmp/ctx_test")
    Context.set_files_found(["/tmp/x.db"])
    Context.set_seeker(MagicMock())
    _test_1arg(["/tmp/x.db"], "/tmp/ctx_test", MagicMock(), False, 0)
    assert received["ctx"] is Context


def test_decorator_sets_context_before_call():
    """Context.get_files_found() is set when the decorated function executes."""
    from scripts.ilapfuncs import artifact_processor
    from scripts.context import Context

    observed = {}

    @artifact_processor
    def _test_ctx_set(files_found, report_folder, seeker, wrap_text, timezone_offset):
        # Context should already be set with the same files_found
        observed["files"] = Context._files_found
        return (), [], ""

    test_files = ["/tmp/a.db", "/tmp/b.plist"]
    _test_ctx_set(test_files, "/tmp/rpt", MagicMock(), False, 0)
    assert observed["files"] == test_files


def test_returns_headers_data_source():
    """Decorated call returns a valid (headers, data_list, source_path) 3-tuple."""
    from scripts.ilapfuncs import artifact_processor

    @artifact_processor
    def _test_return(files_found, report_folder, seeker, wrap_text, timezone_offset):
        return ("Col1", "Col2"), [], "/tmp/source.db"

    result = _test_return([], "/tmp/rpt", MagicMock(), False, 0)
    assert isinstance(result, tuple)
    assert len(result) == 3
    headers, data_list, source_path = result
    assert headers == ("Col1", "Col2")
    assert data_list == []
    assert source_path == "/tmp/source.db"


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def test_open_sqlite_db_readonly(tmp_path):
    """open_sqlite_db_readonly opens a real SQLite DB in read-only mode."""
    from scripts.ilapfuncs import open_sqlite_db_readonly

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, val TEXT)")
    conn.commit()
    conn.close()

    ro_conn = open_sqlite_db_readonly(str(db_path))
    assert ro_conn is not None
    # Read-only: selecting works
    cursor = ro_conn.cursor()
    cursor.execute("SELECT count(*) FROM items")
    (count,) = cursor.fetchone()
    assert count == 0
    ro_conn.close()


def test_get_sqlite_db_records(tmp_path):
    """get_sqlite_db_records returns sqlite3.Row objects with named column access."""
    from scripts.ilapfuncs import get_sqlite_db_records

    db_path = tmp_path / "records.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'hello')")
    conn.execute("INSERT INTO t VALUES (2, 'world')")
    conn.commit()
    conn.close()

    rows = get_sqlite_db_records(str(db_path), "SELECT id, name FROM t ORDER BY id")
    assert len(rows) == 2
    assert rows[0]["id"] == 1
    assert rows[0]["name"] == "hello"
    assert rows[1]["id"] == 2
    assert rows[1]["name"] == "world"


# ---------------------------------------------------------------------------
# Plist helper
# ---------------------------------------------------------------------------

def test_get_plist_file_content_standard(tmp_path):
    """get_plist_file_content parses a standard binary plist and returns a dict."""
    from scripts.ilapfuncs import get_plist_file_content

    plist_path = tmp_path / "test.plist"
    data = {"key": "value", "number": 42, "flag": True}
    plist_path.write_bytes(plistlib.dumps(data))

    result = get_plist_file_content(str(plist_path))
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 42
    assert result["flag"] is True
