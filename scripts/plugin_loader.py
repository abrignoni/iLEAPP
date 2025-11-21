"""
Plugin loader module for dynamically loading and managing artifact plugins.

Provides functionality to discover and load modules from the artifacts directory.
It supports both v1 and v2 artifact formats and manages theit metadata through
the PluginSpec dataclass.

Classes:
    PluginSpec: A frozen dataclass containing artifact metadata including name, module name,
                category, search paths, callable method, and artifact information.
    PluginLoader: Main class for loading and managing artifacts. Discovers Python files in
                  the artifacts directory, extracts artifact definitions, and provides access
                  to loaded artifacts.

Constants:
    PLUGINPATH: Default path to the artifacts directory, resolved relative to this file's
                location for PyInstaller compatibility.

"""

import pathlib
import dataclasses
import typing
import importlib.util

# PLUGINPATH = pathlib.Path("./scripts/artifacts")
# a bit long-winded to make compatible with PyInstaller
PLUGINPATH = pathlib.Path(__file__).resolve().parent / pathlib.Path("artifacts")


@dataclasses.dataclass(frozen=True)
class PluginSpec:
    """
    Specification class for artifact metadata and configuration.
    This class stores essential information about an artifact including its identification,
    categorization, search criteria, execution method, and details.
    Attributes:
        name (str): The name of the artifact.
        module_name (str): The Python module name where the artifact is defined.
        category (str): The category this artifact belongs to.
        search (str): Search pattern used to identify relevant files.
        method (Callable): The callable function that executes the artifact's main logic.
        artifact_info (dict): Dictionary containing metadata and information about artifacts.
    """

    name: str
    module_name: str
    category: str
    search: str
    method: typing.Callable  # to do: define callable signature
    artifact_info: dict  # Add this line to include artifact_info


class PluginLoader:
    """
    A class responsible for dynamically loading and managing artifacts from Python files.
    The PluginLoader scans a specified directory for Python files containing artifact definitions
    and loads them lazily. It supports two versions of artifact definitions:
    - Version 2 (__artifacts_v2__): Dictionary-based with detailed metadata
    - Version 1 (__artifacts__): Tuple-based (category, search, func)
    Attributes:
        _plugin_path (pathlib.Path): The directory path containing LEAPPs module.
        _plugins (dict[str, PluginSpec]): Dictionary mapping artifact names to their specifications.
    Args:
        plugin_path (typing.Optional[pathlib.Path]): Optional path to LEAPPs module directory.
            If not provided, defaults to PLUGINPATH.
    Raises:
        KeyError: If duplicate function names are found across different modules.
    """

    def __init__(self, plugin_path: typing.Optional[pathlib.Path] = None):
        self._plugin_path = plugin_path or PLUGINPATH
        self._plugins: dict[str, PluginSpec] = {}
        self._load_plugins()

    @staticmethod
    def load_module_lazy(path: pathlib.Path):
        """
        Lazily loads a Python module from a file path.
        This function creates a module specification from the given file path and uses
        LazyLoader to defer the execution of the module until its attributes are accessed.
        This can improve startup performance when loading many plugins.
        Args:
            path (pathlib.Path): The file path to the Python module to be loaded.
                The module name will be derived from the file stem (filename without extension).
        Returns:
            module: The loaded module object. The module's code is executed lazily upon
                first attribute access.
        """

        spec = importlib.util.spec_from_file_location(path.stem, path)
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod

    def _load_plugins(self):
        artifact_names = {}
        for py_file in self._plugin_path.glob("*.py"):
            mod = PluginLoader.load_module_lazy(py_file)
            mod_artifacts = getattr(mod, '__artifacts_v2__', None) or getattr(mod, '__artifacts__', None)
            if mod_artifacts is None:
                continue  # no artifacts defined in this plugin

            version = 2 if '__artifacts_v2__' in dir(mod) else 1  # determine the version

            for name, artifact in mod_artifacts.items():
                if version == 2:
                    category = artifact.get('category')
                    search = artifact.get('paths')
                    artifact_name = artifact.get('name')
                    func = None
                    # 1. Look for a wrapped function with the name of the dictionary
                    for item_name in dir(mod):
                        item = getattr(mod, item_name)
                        if callable(item) and item_name == name and hasattr(item, '__wrapped__'):
                            func = item
                            break

                    # 2. If no wrapped function, look for declared function
                    if func is None:
                        func_name = artifact.get('function')
                        if func_name:
                            func = getattr(mod, func_name, None)

                    # 3. If neither above work, log the failure
                    if func is None:
                        print(f"Warning: No matching function found for artifact '{name}' in module '{py_file.stem}'")
                        continue

                    # Store the entire artifact dictionary as artifact_info
                    artifact_info = artifact
                    if func:
                        func.artifact_info = artifact_info  # Attach artifact_info to the function

                else:
                    # 4. If no v2, then use v1
                    artifact_name = name
                    category, search, func = artifact
                    artifact_info = {'category': category, 'paths': search}

                if name in self._plugins:
                    raise KeyError(f"Duplicate plugin: '{name}' in module '{py_file.stem}'")
                if artifact_name in artifact_names:
                    raise KeyError(f"Duplicate artifact name in {py_file.name}: "
                                   f"'{artifact_name}' was also found in module '{artifact_names[artifact_name]}'")
                artifact_names[artifact_name] = py_file.name

                # Add artifact_info to PluginSpec
                self._plugins[name] = PluginSpec(name, py_file.stem, category, search, func, artifact_info)

    @property
    def plugins(self) -> typing.Iterable[PluginSpec]:
        """
        Yields all loaded artifacts specifications.
        This method provides an iterable access to all artifacts that have been
        loaded and stored in the internal _plugins dictionary.
        Yields
        ------
        PluginSpec
            Individual plugin specification objects from the internal plugins collection.
        """

        yield from self._plugins.values()

    def __getitem__(self, item: str) -> PluginSpec:
        return self._plugins[item]

    def __contains__(self, item):
        return item in self._plugins

    def __len__(self):
        return len(self._plugins)
