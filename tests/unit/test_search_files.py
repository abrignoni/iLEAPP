"""Unit tests for file-seeker classes in scripts/search_files.py"""
import zipfile
import pytest

pytestmark = pytest.mark.unit


def test_file_seeker_dir_finds_file(tmp_path):
    """FileSeekerDir.search('*.txt') returns at least the created .txt file."""
    from scripts.search_files import FileSeekerDir

    test_file = tmp_path / "hello.txt"
    test_file.write_text("content")
    data_folder = tmp_path / "data"
    data_folder.mkdir()

    seeker = FileSeekerDir(str(tmp_path), str(data_folder))
    results = seeker.search("*.txt")
    assert isinstance(results, list)
    assert len(results) >= 1
    assert any("hello.txt" in r for r in results)


def test_file_seeker_dir_glob_pattern(tmp_path):
    """FileSeekerDir matches nested glob pattern */subdir/*.py correctly."""
    from scripts.search_files import FileSeekerDir

    subdir = tmp_path / "pkg" / "subdir"
    subdir.mkdir(parents=True)
    (subdir / "module.py").write_text("# python")
    (tmp_path / "other.py").write_text("# other")
    data_folder = tmp_path / "data"
    data_folder.mkdir()

    seeker = FileSeekerDir(str(tmp_path), str(data_folder))
    results = seeker.search("*/subdir/*.py")
    assert len(results) >= 1
    assert any("module.py" in r for r in results)
    # The top-level other.py should NOT match */subdir/*.py
    assert not any(r.endswith("other.py") for r in results)


def test_file_seeker_dir_no_match(tmp_path):
    """FileSeekerDir returns empty list when pattern matches nothing."""
    from scripts.search_files import FileSeekerDir

    (tmp_path / "readme.md").write_text("hello")
    data_folder = tmp_path / "data"
    data_folder.mkdir()

    seeker = FileSeekerDir(str(tmp_path), str(data_folder))
    results = seeker.search("*.nonexistent_extension_xyz")
    assert results == []


def test_file_seeker_zip_finds_file(tmp_path):
    """FileSeekerZip extracts and returns files matching a pattern."""
    from scripts.search_files import FileSeekerZip

    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("docs/readme.txt", "hello from zip")
        zf.writestr("src/main.py", "# python")

    data_folder = tmp_path / "data"
    data_folder.mkdir()

    seeker = FileSeekerZip(str(zip_path), str(data_folder))
    results = seeker.search("*.txt")
    assert isinstance(results, list)
    assert len(results) >= 1
    assert any("readme.txt" in r for r in results)


def test_file_seeker_base_is_abstract():
    """FileSeekerBase can be instantiated but search() returns None (no-op base)."""
    from scripts.search_files import FileSeekerBase

    seeker = FileSeekerBase()
    result = seeker.search("*.txt")
    # Base class has no implementation — returns None implicitly
    assert result is None


def test_fileinfo_has_source_path():
    """FileInfo objects expose a source_path attribute set at construction."""
    from scripts.search_files import FileInfo

    info = FileInfo("/path/to/evidence/file.db", 1234567890.0, 1234567890.0)
    assert info.source_path == "/path/to/evidence/file.db"
    assert info.creation_date == 1234567890.0
    assert info.modification_date == 1234567890.0
