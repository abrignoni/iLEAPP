"""Shared fixtures and helpers for artifact integration tests."""
import fnmatch
import json
import zipfile
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ILEAPP_ROOT = Path(__file__).parents[2]
CASES_DIR = ILEAPP_ROOT / "admin" / "test" / "cases"
DATA_DIR = CASES_DIR / "data"
GOLDEN_DIR = Path(__file__).parent / "golden"


# ---------------------------------------------------------------------------
# Test parameter collection
# ---------------------------------------------------------------------------

def _collect_artifact_test_params():
    """Scan test case JSON files and ZIP data to build parametrize list."""
    params = []
    if not DATA_DIR.exists():
        return params

    for json_file in sorted(CASES_DIR.glob("testdata.*.json")):
        module_name = json_file.stem[len("testdata."):]
        try:
            cases = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        for case_key, case_data in cases.items():
            for artifact_name, artifact_data in case_data.get("artifacts", {}).items():
                # Skip cases with no test data files
                if artifact_data.get("file_count", 0) == 0:
                    continue

                zip_path = (
                    DATA_DIR / module_name
                    / f"testdata.{module_name}.{artifact_name}.{case_key}.zip"
                )
                if not zip_path.exists():
                    continue

                params.append(
                    pytest.param(
                        module_name,
                        artifact_name,
                        case_key,
                        zip_path,
                        case_data,
                        id=f"{module_name}.{artifact_name}.{case_key}",
                        marks=pytest.mark.artifact,
                    )
                )
    return params


ARTIFACT_TEST_PARAMS = _collect_artifact_test_params()


# ---------------------------------------------------------------------------
# Mock seeker
# ---------------------------------------------------------------------------

class MockSeeker:
    """Seeker backed by a flat list of extracted files; searches via fnmatch."""

    def __init__(self, root: Path):
        self._root = root
        self._all_files = [str(p) for p in root.rglob("*") if p.is_file()]
        self.file_infos = _MockFileInfos(self._all_files)

    def search(self, pattern, return_on_first_hit=False):
        matches = [f for f in self._all_files if fnmatch.fnmatch(f, pattern)]
        if return_on_first_hit:
            return matches[0] if matches else None
        return matches


class _MockFileInfos:
    """Dict-like object returning synthetic FileInfo for any path."""

    def __init__(self, all_files):
        self._all_files = set(all_files)

    def get(self, key, default=None):
        fi = MagicMock()
        fi.source_path = key
        fi.creation_date = datetime.now(timezone.utc)
        fi.modification_date = datetime.now(timezone.utc)
        return fi


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def make_seeker(tmp_path):
    """Extract a ZIP to tmp_path and return a (MockSeeker, extraction_root) tuple."""

    def _factory(zip_path: Path):
        extraction_root = tmp_path / "extracted"
        extraction_root.mkdir()
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extraction_root)
        return MockSeeker(extraction_root), extraction_root

    return _factory


# ---------------------------------------------------------------------------
# Standard patch set for artifact runs
# ---------------------------------------------------------------------------

def build_artifact_patches(module_name: str):
    """
    Return a list of patch objects needed to run an artifact function in
    isolation (no LAVA DB, no HTML output, no file I/O side effects).
    """
    mock_lava_cursor = MagicMock()
    mock_lava_cursor.fetchone.return_value = None
    mock_lava_cursor.fetchall.return_value = []
    mock_lava_db = MagicMock()
    mock_lava_db.cursor.return_value = mock_lava_cursor

    def mock_check_in_media(*args, **kwargs):
        # Accept both positional (fp) and keyword (file_path=) call styles
        fp = args[0] if args else kwargs.get("file_path", kwargs.get("fp", ""))
        return f"mock_hash_{Path(str(fp)).name}"

    def mock_check_in_embedded_media(*args, **kwargs):
        return "mock_embedded"

    # Match the tuple structure that real lava_get_full_media_info returns
    # (ref_id, item_id, module, artifact, name, media_path, source_path,
    #  extraction_path, mimetype, metadata, created_at, updated_at)
    _MAC_BDAY_TS = 443750400
    def mock_lava_get_full_media_info(ref_id):
        return (
            "mock_ref_id", "mock_item_id", "mock_module", "mock_artifact",
            "mock_name", "mock_media_path", "mock_source_path",
            "mock_extraction_path", "image/png", "mock_metadata",
            _MAC_BDAY_TS, _MAC_BDAY_TS,
        )

    return [
        patch("scripts.ilapfuncs.logdevinfo",               lambda msg: None),
        patch("scripts.ilapfuncs.logfunc",                  lambda msg="": None),
        patch(f"scripts.artifacts.{module_name}.logdevinfo", lambda msg: None,    create=True),
        patch(f"scripts.artifacts.{module_name}.logfunc",    lambda msg="": None, create=True),
        patch("scripts.lavafuncs.lava_db",                  mock_lava_db),
        patch("scripts.ilapfuncs.check_in_media",           mock_check_in_media),
        patch("scripts.ilapfuncs.check_in_embedded_media",  mock_check_in_embedded_media),
        patch(f"scripts.artifacts.{module_name}.check_in_media",
              mock_check_in_media, create=True),
        patch(f"scripts.artifacts.{module_name}.check_in_embedded_media",
              mock_check_in_embedded_media, create=True),
        patch(f"scripts.artifacts.{module_name}.lava_get_full_media_info",
              mock_lava_get_full_media_info, create=True),
        patch("scripts.ilapfuncs.lava_process_artifact",    MagicMock(return_value=("t", "[]", "{}"))),
        patch("scripts.ilapfuncs.lava_insert_sqlite_data",  MagicMock()),
        patch("scripts.artifact_report.ArtifactHtmlReport", MagicMock()),
        patch("scripts.ilapfuncs.tsv",                      MagicMock()),
        patch("scripts.ilapfuncs.timeline",                 MagicMock()),
        patch("scripts.ilapfuncs.kmlgen",                   MagicMock()),
    ]


# ---------------------------------------------------------------------------
# Path normalisation helper
# ---------------------------------------------------------------------------

def normalize_paths(data_list, extraction_root: Path):
    """Replace extraction_root prefix in all string cells with <ROOT>."""
    root_str = str(extraction_root)

    def _norm(val):
        if isinstance(val, str) and root_str in val:
            return val.replace(root_str, "<ROOT>")
        return val

    return [[_norm(cell) for cell in row] for row in data_list]
