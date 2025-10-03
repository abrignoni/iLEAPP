import pathlib
import dataclasses
import typing
import importlib.util

#PLUGINPATH = pathlib.Path("./scripts/artifacts")
# a bit long-winded to make compatible with PyInstaller
PLUGINPATH = pathlib.Path(__file__).resolve().parent / pathlib.Path("artifacts")


@dataclasses.dataclass(frozen=True)
class PluginSpec:
    name: str
    module_name: str
    category: str
    search: str
    method: typing.Callable  # todo define callable signature
    artifact_info: dict  # Add this line to include artifact_info


class PluginLoader:
    def __init__(self, plugin_path: typing.Optional[pathlib.Path] = None):
        self._plugin_path = plugin_path or PLUGINPATH
        self._plugins: dict[str, PluginSpec] = {}
        self._load_plugins()

    @staticmethod
    def load_module_lazy(path: pathlib.Path):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod

    def _load_plugins(self):
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
                    category, search, func = artifact
                    artifact_info = {'category': category, 'paths': search}

                if name in self._plugins:
                    raise KeyError(f"Duplicate plugin: '{name}' in module '{py_file.stem}'")
                
                # Add artifact_info to PluginSpec
                self._plugins[name] = PluginSpec(name, py_file.stem, category, search, func, artifact_info)


    @property
    def plugins(self) -> typing.Iterable[PluginSpec]:
        yield from self._plugins.values()

    def __getitem__(self, item: str) -> PluginSpec:
        return self._plugins[item]

    def __contains__(self, item):
        return item in self._plugins

    def __len__(self):
        return len(self._plugins)

