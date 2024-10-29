import os
import sys
import json
import argparse
import zipfile
import shutil
import importlib
import datetime
from pathlib import Path

# Add the root directory to sys.path to import ileapp
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_dir)
import ileapp

def validate_module(module_name):
    # Remove .py extension if present
    module_name = module_name.replace('.py', '')
    
    # Check if the module exists
    module_path = Path('scripts/artifacts') / f'{module_name}.py'
    if not module_path.exists():
        print(f"Error: Module '{module_name}' not found.")
        sys.exit(1)
    
    return module_name

def get_test_cases(module_name):
    test_case_file = Path('admin/test/cases') / f'testdata.{module_name}.json'
    if not test_case_file.exists():
        print(f"No test cases found for module '{module_name}'.")
        sys.exit(1)
    
    with open(test_case_file, 'r') as f:
        test_cases = json.load(f)
    
    return test_cases

def select_test_case(test_cases):
    print("Available test cases:")
    for i, (case_name, case_data) in enumerate(test_cases.items(), 1):
        input_path = case_data.get('make_data', {}).get('input_data_path', 'N/A')
        description = case_data.get('description', 'No description available')
        print(f"{i}. {case_name}")
        print(f"   Input: {os.path.basename(input_path)}")
        print(f"   Description: {description or 'No description available'}")
        print()
    
    while True:
        try:
            choice = int(input("Select a test case number: "))
            if 1 <= choice <= len(test_cases):
                selected_case_name = list(test_cases.keys())[choice - 1]
                return selected_case_name, test_cases[selected_case_name]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def extract_test_data(module_name, case_name, test_case, temp_folder):
    data_folder = Path('admin/test/cases/data') / module_name  # Updated path
    for artifact_name in test_case['artifacts'].keys():
        zip_path = data_folder / f"testdata.{module_name}.{artifact_name}.{case_name}.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_folder)
        else:
            print(f"Warning: Test data file '{zip_path}' not found.")

class SingleModuleLoaderWrapper:
    def __init__(self, plugin_path, module_name):
        self.plugin_path = plugin_path
        self.module_name = module_name
        self._plugins = self._load_plugins()

    def _load_plugins(self):
        plugins = []
        essential_modules = ['lastBuild', 'iTunesBackupInfo']  # Add other essential modules if needed
        modules_to_load = essential_modules + [self.module_name]

        for module in modules_to_load:
            py_file = self.plugin_path / f"{module}.py"
            if py_file.exists():
                mod = ileapp.plugin_loader.PluginLoader.load_module_lazy(py_file)
                mod_artifacts = getattr(mod, '__artifacts_v2__', None) or getattr(mod, '__artifacts__', None)
                if mod_artifacts:
                    for name, artifact in mod_artifacts.items():
                        if isinstance(artifact, dict):  # v2 format
                            category = artifact.get('category')
                            search = artifact.get('paths')
                            func = getattr(mod, name, None)
                            if func:
                                func.artifact_info = artifact  # Attach artifact_info to the function
                        else:  # v1 format
                            category, search, func = artifact
                            func.artifact_info = {'category': category, 'paths': search}  # Create artifact_info for v1
                        if func:
                            plugin_spec = ileapp.plugin_loader.PluginSpec(name, module, category, search, func, func.artifact_info)
                            plugins.append(plugin_spec)
        return plugins

    @property
    def plugins(self):
        return self._plugins

    def __len__(self):
        return len(self._plugins)

    def __getitem__(self, item):
        for plugin in self._plugins:
            if plugin.name == item:
                return plugin
        raise KeyError(item)

    def __contains__(self, item):
        return any(plugin.name == item for plugin in self._plugins)

def run_module_test(module_name, temp_folder):
    output_folder = Path('admin/test/output')
    output_folder.mkdir(parents=True, exist_ok=True)

    # Prepare arguments for ileapp.main()
    sys.argv = [
        'ileapp.py',
        '-i', str(temp_folder),
        '-o', str(output_folder),
        '-t', 'fs',
        '-w',
        '--custom_output_folder', f'test.{module_name}.{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}'
    ]

    # Create a wrapper for the single module
    plugin_path = ileapp.plugin_loader.PLUGINPATH
    wrapper_loader = SingleModuleLoaderWrapper(plugin_path, module_name)

    # Monkey-patch ileapp to use our wrapper loader
    original_PluginLoader = ileapp.plugin_loader.PluginLoader
    ileapp.plugin_loader.PluginLoader = lambda: wrapper_loader

    try:
        ileapp.main()
    finally:
        # Restore the original loader
        ileapp.plugin_loader.PluginLoader = original_PluginLoader

def main():
    parser = argparse.ArgumentParser(description="Run a single module test for iLEAPP")
    parser.add_argument("module_name", help="Name of the module to test (with or without .py)")
    args = parser.parse_args()

    module_name = validate_module(args.module_name)
    test_cases = get_test_cases(module_name)
    selected_case_name, selected_case = select_test_case(test_cases)

    temp_folder = Path('admin/test/temp')
    if temp_folder.exists():
        # Delete contents of temp folder instead of the folder itself
        for item in temp_folder.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        temp_folder.mkdir(parents=True)

    try:
        extract_test_data(module_name, selected_case_name, selected_case, temp_folder)
        run_module_test(module_name, temp_folder)
    finally:
        # Clean up contents of temp folder
        for item in temp_folder.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    print(f"Test completed. Check the output folder for results: {Path('admin/test/output').absolute()}")

if __name__ == "__main__":
    main()
