"""
Provides functionality to discover and load LEAPPs modules from the artifacts directory.
It supports both v1 and v2 artifact formats and manages their metadata through
the ArtifactSpec dataclass.

Classes:
    ArtifactSpec: A frozen dataclass containing artifact metadata including name, module name,
                category, search paths, callable method, and artifact information.
    ArtifactLoader: Main class for loading LEAPPs modules in the artifacts directory,
                accessing to them, and extracting artifact definitions.

Constants:
    ARTIFACT_PATHS: Default path to the artifacts directory

"""

import pathlib
import dataclasses
import typing
import importlib.util

# Resolved relative to this file's location for PyInstaller compatibility.
ARTIFACT_PATHS = pathlib.Path(__file__) \
    .resolve().parent.resolve().parent.resolve().parent.resolve().parent \
    .joinpath("scripts", "artifacts")


@dataclasses.dataclass(frozen=True)
class ArtifactSpec:
    """
    Specification class for artifact metadata and configuration.
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


class ArtifactLoader:
    """
    Dynamically loading and managing artifacts from Python files.
    It supports two versions of artifact definitions:
        - Version 2 (__artifacts_v2__): Dictionary-based with detailed metadata
        - Version 1 (__artifacts__): Tuple-based (category, search, func)
    Attributes:
        _artifact_paths (pathlib.Path): The directory path containing LEAPPs module.
        _artifacts (dict[str, ArtifactSpec]): Dictionary mapping artifact names to their specifications.
    Args:
        artifact_paths (typing.Optional[pathlib.Path]): Optional path to LEAPPs module directory.
            If not provided, defaults to ARTIFACTS_PATH.
    Raises:
        KeyError: If duplicate artifact names are found across different modules.
    """

    def __init__(self, artifact_paths: typing.Optional[typing.List[pathlib.Path]] = None):
        self._artifact_paths = artifact_paths or [ARTIFACT_PATHS]
        self._artifacts: dict[str, ArtifactSpec] = {}
        self._artifact_names = {}
        self._artifact_sources = {}
        for path in self._artifact_paths:
            self._load_artifacts(path)

    @staticmethod
    def load_module_lazy(path: pathlib.Path):
        """
        Lazily loads a Python module from a file path.
        This function creates a module specification from the given file path and uses
        LazyLoader to defer the execution of the module until its attributes are accessed.
        This can improve startup performance when loading many artifacts.
        Args:
            path (pathlib.Path): The file path to the Python module to be loaded.
                The module name will be derived from the file stem (filename without extension).
        Returns:
            module: The loaded module object. The module's code is executed lazily upon
                first attribute access.
        """

        # Use the full module path to avoid name collisions between different artifact directories
        module_name = f"{path.parent.name}.{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod

    def _load_artifacts(self, artifact_path: pathlib.Path):
        for py_file in artifact_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            mod = ArtifactLoader.load_module_lazy(py_file)
            mod_artifacts = getattr(mod, "__artifacts_v2__", None) or getattr(mod, "__artifacts__", None)
            if mod_artifacts is None:
                continue  # no artifacts defined in this artifact

            version = 2 if "__artifacts_v2__" in dir(mod) else 1  # determine the version

            for name, artifact in mod_artifacts.items():
                if version == 2:
                    category = artifact.get("category")
                    search = artifact.get("paths")
                    artifact_name = artifact.get("name")
                    func = None
                    # 1. Look for a wrapped function with the name of the dictionary
                    for item_name in dir(mod):
                        item = getattr(mod, item_name)
                        if callable(item) and item_name == name and hasattr(item, "__wrapped__"):
                            func = item
                            break

                    # 2. If no wrapped function, look for declared function
                    if func is None:
                        func_name = artifact.get("function")
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
                    artifact_info = {"category": category, "paths": search}

                # Check for duplicate artifact keys within the same artifact folder and error
                # Identify duplicate artifact in alternate artifact folder and override standard
                if name in self._artifacts:
                    prev_path = self._artifact_sources[name]
                    if prev_path == artifact_path:
                        raise KeyError(f"Duplicate artifact key: '{name}' in module '{py_file.stem}'")
                    print(f"Info: Overriding artifact key '{name}' from {prev_path.name} "
                          f"with version from {artifact_path.name}/{py_file.name}")

                # Check for duplicate artifact names within the same artifact folder
                if artifact_name in self._artifact_names:
                    prev_file, prev_path = self._artifact_names[artifact_name]
                    if prev_path == artifact_path:
                        raise KeyError(f"Duplicate artifact name in {py_file.name}: "
                                       f"'{artifact_name}' was also found in module '{prev_file}'")

                self._artifact_names[artifact_name] = (py_file.name, artifact_path)
                self._artifact_sources[name] = artifact_path

                # Add artifact_info to ArtifactSpec
                self._artifacts[name] = ArtifactSpec(name, py_file.stem, category, search, func, artifact_info)

    @property
    def artifacts(self) -> typing.Iterable[ArtifactSpec]:
        """
        Yields all loaded artifacts specifications.
        This method provides an iterable access to all artifacts that have been
        loaded and stored in the internal _artifacts dictionary.
        Yields
        ------
        ArtifactSpec
            Individual artifact specification objects from the internal artifacts collection.
        """

        yield from self._artifacts.values()

    def __getitem__(self, item: str) -> ArtifactSpec:
        return self._artifacts[item]

    def __contains__(self, item):
        return item in self._artifacts

    def __len__(self):
        return len(self._artifacts)
