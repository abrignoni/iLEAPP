import plugin_loader

# Hey PyInstaller? Yeah you! Take a look at these plugins! I know they're not actually imported anywhere but you
# better believe that they will be a runtime, so, if you wouldn't mind, it'd be fantastic if you pretended that
# they're imported normally and pick up *their* imports. OK? Great. Fantastic.

print("Hooking plugins for pyinstaller")

loader = plugin_loader.PluginLoader()

tmp = []

for py_file in plugin_loader.PLUGINPATH.glob("*.py"):
    mod = plugin_loader.PluginLoader.load_module_lazy(py_file)
    try:
        mod_artifacts = mod.__artifacts__
    except AttributeError:
        pass  # any unconverted plugins still get checked out so they don't break the loader during runtime

    tmp.append("scripts.artifacts." + mod.__name__)  # TODO this is a hack, if we ever move plugins this breaks

print(f"{len(tmp)} plugins loaded as hidden imports")

hiddenimports = list(tmp)
