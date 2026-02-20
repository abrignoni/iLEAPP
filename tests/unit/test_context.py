"""Unit tests for scripts/context.py"""
import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit


def test_set_and_get_report_folder():
    """Setter/getter round-trip for report_folder."""
    from scripts.context import Context
    Context.set_report_folder("/tmp/test_reports")
    assert Context.get_report_folder() == "/tmp/test_reports"


def test_set_and_get_files_found():
    """Setter/getter for files_found (list)."""
    from scripts.context import Context
    files = ["/a/b/foo.db", "/a/b/bar.plist"]
    Context.set_files_found(files)
    assert Context.get_files_found() == files


def test_set_and_get_seeker():
    """Setter/getter for seeker object."""
    from scripts.context import Context
    mock_seeker = MagicMock()
    Context.set_seeker(mock_seeker)
    assert Context.get_seeker() is mock_seeker


def test_clear_resets_all_state():
    """After clear(), getters for transient state raise ValueError."""
    from scripts.context import Context
    Context.set_report_folder("/tmp/foo")
    Context.set_files_found(["/tmp/foo.db"])
    Context.set_seeker(MagicMock())
    Context.set_artifact_name("test_artifact")

    Context.clear()

    with pytest.raises(ValueError):
        Context.get_report_folder()
    with pytest.raises(ValueError):
        Context.get_files_found()
    with pytest.raises(ValueError):
        Context.get_seeker()
    with pytest.raises(ValueError):
        Context.get_artifact_name()


def test_state_isolated_between_uses():
    """Set state, clear, set new state — only the new state is visible."""
    from scripts.context import Context
    Context.set_report_folder("/tmp/first")
    Context.clear()
    Context.set_report_folder("/tmp/second")
    assert Context.get_report_folder() == "/tmp/second"


def test_device_id_lookup():
    """get_device_model returns a non-empty string for a known identifier."""
    from scripts.context import Context
    # iPhone1,1 is the original iPhone — must be in the JSON
    result = Context.get_device_model("iPhone1,1")
    assert isinstance(result, str)
    assert len(result) > 0


def test_device_id_lookup_unknown_returns_empty():
    """get_device_model returns '' for an unknown identifier."""
    from scripts.context import Context
    result = Context.get_device_model("NotARealDevice99,99")
    assert result == ""


def test_get_filename_lookup_map():
    """get_filename_lookup_map returns a non-empty dict when files_found is set."""
    from scripts.context import Context
    Context.set_files_found(["/tmp/foo.db", "/tmp/bar.plist"])
    lookup = Context.get_filename_lookup_map()
    assert isinstance(lookup, dict)
    assert len(lookup) > 0
    assert "foo.db" in lookup
    assert lookup["foo.db"] == ["/tmp/foo.db"]
