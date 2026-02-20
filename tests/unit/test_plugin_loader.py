"""Unit tests for scripts/plugin_loader.py"""
import dataclasses
import pytest

pytestmark = pytest.mark.unit


def test_discovers_plugins():
    """PluginLoader finds at least one plugin from scripts/artifacts/."""
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    assert len(loader) > 0


def test_all_plugins_have_required_fields():
    """Every PluginSpec has name, category, and a callable method.

    Search patterns may be None for LAVA-only plugins that query the
    database rather than searching the filesystem.
    """
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    for spec in loader.plugins:
        assert spec.name, f"Plugin {spec.module_name!r} has empty name"
        assert spec.category, f"Plugin {spec.name!r} has empty category"
        assert callable(spec.method), f"Plugin {spec.name!r} method is not callable"


def test_no_duplicate_function_names():
    """Function names (dict keys) are unique across all loaded plugins."""
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    seen = set()
    for spec in loader.plugins:
        assert spec.module_name + "." + spec.name not in seen, (
            f"Duplicate plugin key: {spec.name!r} in {spec.module_name!r}"
        )
        seen.add(spec.module_name + "." + spec.name)


def test_v2_metadata_parsed_correctly():
    """The celWireless v2 plugin has the expected display name, category, and paths.

    PluginSpec.name is the function key (dict key in __artifacts_v2__).
    The human-readable display name is in spec.artifact_info['name'].
    """
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    assert "celWireless" in loader
    spec = loader["celWireless"]
    # Function key (used as dict key in __artifacts_v2__)
    assert spec.name == "celWireless"
    # Human-readable display name lives in artifact_info
    assert spec.artifact_info["name"] == "Cellular Wireless"
    assert spec.category == "Cellular"
    assert isinstance(spec.search, (list, tuple))
    assert any("commcenter" in p for p in spec.search)


def test_plugin_callable_is_callable():
    """Each plugin's method attribute is callable."""
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    for spec in loader.plugins:
        assert callable(spec.method), (
            f"spec.method for {spec.name!r} in {spec.module_name!r} is not callable"
        )


def test_plugin_spec_frozen():
    """PluginSpec is a frozen dataclass — setting an attribute raises FrozenInstanceError."""
    from scripts.plugin_loader import PluginLoader
    loader = PluginLoader()
    spec = next(iter(loader.plugins))
    with pytest.raises((dataclasses.FrozenInstanceError, TypeError, AttributeError)):
        spec.name = "mutated"


def test_lazy_loading_does_not_execute_plugin(tmp_path):
    """Creating a PluginLoader reads metadata but does not call artifact functions."""
    from scripts.plugin_loader import PluginLoader

    plugin_file = tmp_path / "fake_art.py"
    plugin_file.write_text(
        """
__artifacts_v2__ = {
    "fake_art": {
        "name": "Fake Artifact",
        "description": "test",
        "author": "test",
        "version": "0.1",
        "date": "2024-01-01",
        "requirements": "none",
        "category": "Test",
        "notes": "",
        "paths": ("*/fake.txt",),
        "output_types": "none",
        "artifact_icon": "file",
    }
}

from scripts.ilapfuncs import artifact_processor

@artifact_processor
def fake_art(files_found, report_folder, seeker, wrap_text, timezone_offset):
    raise RuntimeError("This must NOT be called during plugin loading!")
    return (), [], ""
"""
    )

    loader = PluginLoader(plugin_path=tmp_path)
    # If RuntimeError was raised, we'd never reach here
    assert len(loader) == 1
    assert "fake_art" in loader
