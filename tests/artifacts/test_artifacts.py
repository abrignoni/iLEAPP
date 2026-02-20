"""
Parametrized integration tests for iLEAPP artifact plugins.

Each test case:
  - Extracts the matching ZIP file to a temp directory
  - Calls the original (unwrapped) artifact function
  - Validates the return structure
  - Compares output against a golden JSON file (or writes it with --update-golden)
"""
import importlib
import inspect
import json
from contextlib import ExitStack
from pathlib import Path

import pytest

from tests.artifacts.conftest import (
    ARTIFACT_TEST_PARAMS,
    GOLDEN_DIR,
    ILEAPP_ROOT,
    build_artifact_patches,
    normalize_paths,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_original_function(module_name: str, artifact_name: str):
    """Import the artifact module and return the unwrapped original function.

    Uses importlib.import_module so the module is properly cached under
    'scripts.artifacts.<module_name>' in sys.modules, ensuring that patches
    applied to that key affect the same module object that the function uses.

    Returns None if the artifact function name does not exist in the module
    (e.g. the function was renamed since the test data JSON was created).
    """
    module = importlib.import_module(f"scripts.artifacts.{module_name}")

    func = getattr(module, artifact_name, None)
    if func is None:
        return None

    # Unwrap decorator chain to reach the original function
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


def _unwrap_data_list(data_list):
    """Handle the (data_list, html_data_list) tuple pattern used by some artifacts.

    Artifacts that render media return a tuple of two lists; we test
    against the primary (non-HTML) data list.
    """
    if isinstance(data_list, tuple) and len(data_list) == 2:
        primary, _ = data_list
        if isinstance(primary, (list, tuple)):
            return primary
    return data_list


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "module_name,artifact_name,case_key,zip_path,case_data",
    ARTIFACT_TEST_PARAMS,
)
def test_artifact_runs_without_error(
    module_name,
    artifact_name,
    case_key,
    zip_path,
    case_data,
    make_seeker,
    update_golden,
    tmp_path,
):
    """Artifact runs without exception and returns a valid (headers, data, source) tuple."""
    # --- Skip if function was renamed since the test-data JSON was generated ---
    func = _load_original_function(module_name, artifact_name)
    if func is None:
        pytest.skip(
            f"Function {artifact_name!r} not found in scripts/artifacts/{module_name}.py "
            "(may have been renamed). Update the test-data JSON to regenerate."
        )

    seeker, extraction_root = make_seeker(zip_path)
    files_found = seeker.search("*")
    os_version = (case_data.get("image_info") or {}).get("os_version", "16.0")
    report_folder = str(tmp_path / "reports")
    (tmp_path / "reports").mkdir()

    from scripts.context import Context
    import scripts.ilapfuncs as ilapfuncs

    patches = build_artifact_patches(module_name)

    # Patch iOS version if provided by the test case
    from unittest.mock import patch
    patches.append(
        patch.object(ilapfuncs.iOS, "_version", os_version)
    )

    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)

        Context.set_report_folder(report_folder)
        Context.set_seeker(seeker)
        Context.set_files_found(files_found)
        Context.set_artifact_info({})
        Context.set_module_name(module_name)
        Context.set_module_file_path(
            str(ILEAPP_ROOT / "scripts" / "artifacts" / f"{module_name}.py")
        )
        Context.set_artifact_name(artifact_name)

        sig = inspect.signature(func)
        if len(sig.parameters) == 1:
            result = func(Context)
        else:
            result = func(files_found, report_folder, seeker, False, "UTC")

    # --- Structural assertions ---
    assert isinstance(result, tuple), "Artifact must return a tuple"
    assert len(result) == 3, "Artifact must return exactly (headers, data_list, source_path)"

    headers, data_list, source_path = result

    # Unwrap (data_list, html_data_list) media pattern
    data_list = _unwrap_data_list(data_list)

    assert isinstance(headers, (list, tuple)), "headers must be list or tuple"
    assert isinstance(data_list, (list, tuple)), "data_list must be list or tuple"
    assert isinstance(source_path, (str, type(None))), "source_path must be str or None"

    if headers and data_list:
        n_cols = len(headers)
        for i, row in enumerate(data_list):
            assert len(row) == n_cols, (
                f"Row {i} has {len(row)} columns but headers has {n_cols}"
            )

    # --- Golden-file comparison ---
    golden_path = GOLDEN_DIR / f"{module_name}.{artifact_name}.{case_key}.json"

    # Build normalised snapshot
    normalized_data = normalize_paths(
        [[str(cell) for cell in row] for row in data_list],
        extraction_root,
    )
    normalized_headers = [
        h[0] if isinstance(h, tuple) else h for h in headers
    ]
    actual = {"headers": normalized_headers, "data": normalized_data}

    if update_golden:
        GOLDEN_DIR.mkdir(exist_ok=True)
        golden_path.write_text(
            json.dumps(actual, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return  # Pass on update runs

    if golden_path.exists():
        expected = json.loads(golden_path.read_text(encoding="utf-8"))
        assert actual["headers"] == expected["headers"], (
            f"Headers changed for {module_name}.{artifact_name}.{case_key}\n"
            f"  got:      {actual['headers']}\n"
            f"  expected: {expected['headers']}"
        )
        assert actual["data"] == expected["data"], (
            f"Data changed for {module_name}.{artifact_name}.{case_key}. "
            "Re-run with --update-golden if intentional."
        )
