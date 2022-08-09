import pathlib
import dataclasses
import typing
import importlib.util

#PLUGINPATH = pathlib.Path("./scripts/artifacts")
# a bit long-winded to make compatible with PyInstaller
PLUGINPATH = pathlib.Path(__file__).resolve().parent / pathlib.Path("scripts/artifacts")


@dataclasses.dataclass(frozen=True)
class PluginSpec:
    name: str
    module_name: str
    category: str
    search: str
    method: typing.Callable  # todo define callable signature


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
            try:
                mod_artifacts = mod.__artifacts__
            except AttributeError:
                continue  # no artifacts defined in this plugin

            for name, (category, search, func) in mod_artifacts.items():
                #self._plugins.append(PluginSpec(name, search, func))
                if name in self._plugins:
                    raise KeyError("Duplicate plugin")
                self._plugins[name] = PluginSpec(name, py_file.stem, category, search, func)

    @property
    def plugins(self) -> typing.Iterable[PluginSpec]:
        yield from self._plugins.values()

    def __getitem__(self, item: str) -> PluginSpec:
        return self._plugins[item]

    def __contains__(self, item):
        return item in self._plugins

    def __len__(self):
        return len(self._plugins)





