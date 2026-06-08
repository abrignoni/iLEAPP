"""Context class"""

import json
import re
from os.path import basename
from pathlib import Path


class Context:
    """
    Context class provides a static context for managing and accessing global
    state and configuration used during artifact processing in the LEAPPs
    framework. It stores information such as report folder, artifact details,
    files found, device IDs, and OS build mappings, and provides utility
    methods for retrieving and manipulating this data.
    """

    _output_params = None
    _report_folder = None
    _seeker = None
    _artifact_info = None
    _module_name = None
    _module_file_path = None
    _artifact_name = None
    _files_found = []
    _filename_lookup_map = {}
    _data_folder = None
    _metadata = {}
    _installed_os_version = ""

    @staticmethod
    def set_output_params(output_params):
        """
        Sets the OutputParameters instance in the Context. This should only be
        called once at the start of a run.

        Args:
            output_params: The initialized OutputParameters object.
        """
        Context._output_params = output_params
        Context._data_folder = getattr(output_params, 'data_folder', None)

    @staticmethod
    def set_report_folder(report_folder):
        """
        Sets the report folder path in the Context.

        Args:
            report_folder (str): The path to the folder where reports will be
            stored.
        """

        Context._report_folder = report_folder

    @staticmethod
    def set_seeker(seeker):
        """
        Sets the seeker object in the Context class.

        Args:
            seeker: The seeker object to be set as the current context seeker.
        """

        Context._seeker = seeker

    @staticmethod
    def set_artifact_info(artifact_info):
        """
        Sets the artifact information in the Context.

        Args:
            artifact_info: The artifact information to be stored.
        """

        Context._artifact_info = artifact_info

    @staticmethod
    def set_module_name(module_name):
        """
        Sets the module name in the Context class.

        Args:
            module_name (str): The name of the module to set.
        """

        Context._module_name = module_name

    @staticmethod
    def set_module_file_path(module_file_path):
        """
        Sets the file path for the current module in the Context.

        Args:
            module_file_path (str): The file path to be set for the module.
        """

        Context._module_file_path = module_file_path

    @staticmethod
    def set_artifact_name(artifact_name):
        """
        Sets the artifact name in the Context.

        Args:
            artifact_name (str): The name of the artifact to set.
        """

        Context._artifact_name = artifact_name

    @staticmethod
    def set_files_found(files_found):
        """
        Sets the list of files found in the current context.

        Args:
            files_found (list): A list of file paths that have been found
            using the paths regex of __artifact_v2__ and that are to be stored
            in the context.
        """

        Context._files_found = files_found

    @staticmethod
    def get_metadata(collection):
        """
        Lazily loads and caches metadata from a JSON file in the scripts/data/
        directory.

        Args:
            collection (str): The name of the collection (filename without .json).

        Returns:
            dict: The decoded JSON collection, or {} if the file does not exist.
        """
        if collection not in Context._metadata:
            metadata_path = Path(__file__).parent.absolute().joinpath(
                'data', f'{collection}.json')
            if metadata_path.exists():
                with open(metadata_path, 'rt', encoding='utf-8') as json_file:
                    Context._metadata[collection] = json.load(json_file)
            else:
                Context._metadata[collection] = {}
        return Context._metadata[collection]

    @staticmethod
    def lookup_metadata(collection, key, group=None):
        """
        Retrieves a value from a metadata collection.

        Args:
            collection (str): The name of the collection.
            key (str): The key to look up.
            group (str, optional): The group within the collection to search.

        Returns:
            str: The matching value, or '' if not found.
        """
        data = Context.get_metadata(collection)
        if not data:
            return ''

        if group:
            return data.get(group, {}).get(key, '')

        key = str(key)
        # Check if it's a flat collection
        if key in data and not isinstance(data[key], dict):
            return data[key]

        # Check if it's a grouped collection and search all groups
        matches = []
        for group_data in data.values():
            if isinstance(group_data, dict) and key in group_data:
                matches.append(group_data[key])

        if matches:
            return " or ".join(matches)

        return ''

    @staticmethod
    def set_installed_os_version(os_version):
        """
        Sets the OS version of the analyzed device only once.
        """
        if not Context._installed_os_version:
            Context._installed_os_version = os_version

    @staticmethod
    def _build_lookup_map():
        """Builds and returns a dictionary mapping filenames to a list
        of full paths."""

        if not Context._files_found:
            raise ValueError(
                "Cannot build lookup map: _files_found is not set.")

        filename_lookup = {}
        for full_path in Context._files_found:
            filename = basename(full_path)
            if filename not in filename_lookup:
                filename_lookup[filename] = []
            filename_lookup[filename].append(full_path)
        return filename_lookup

    @staticmethod
    def get_output_params():
        """
        Retrieves the current OutputParameters instance from the Context.

        Raises:
            ValueError: If the output parameters are not set.

        Returns:
            OutputParameters: The OutputParameters instance.
        """
        if not Context._output_params:
            raise ValueError("Context not set. OutputParameters not available.")
        return Context._output_params

    @staticmethod
    def get_report_folder():
        """
        Retrieves the current report folder path from the Context.

        Raises:
            ValueError: If the report folder is not set, indicating that the
            function is called outside of an artifact context.

        Returns:
            str: The path to the report folder.
        """

        if not Context._report_folder:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._report_folder

    @staticmethod
    def get_seeker():
        """
        Retrieve the current seeker object from the Context.

        Raises:
            ValueError: If the Context has not been set, indicating that this
            function should only be called from within an artifact.

        Returns:
            The seeker object associated with the current Context.
        """

        if not Context._seeker:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._seeker

    @staticmethod
    def get_artifact_info():
        """
        Retrieve the current artifact information (__artifact_v2__) from the
        Context.

        Raises:
            ValueError: If the Context's artifact information is not set,
            indicating that this function was called outside of an artifact
            context.

        Returns:
            dict: The artifact information stored in the Context.
        """

        if not Context._artifact_info:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._artifact_info

    @staticmethod
    def get_module_name():
        """
        Retrieves the current module name from the Context.

        Raises:
            ValueError: If the Context has not been set, indicating that this
            function should only be called from within an artifact.

        Returns:
            str: The name of the current module.
        """

        if not Context._module_name:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._module_name

    @staticmethod
    def get_module_file_path():
        """
        Returns the file path of the current module set in the Context.

        Raises:
            ValueError: If the module file path is not set in the Context,
            indicating that this function was called outside of an artifact
            context.

        Returns:
            str: The file path of the current module.
        """

        if not Context._module_file_path:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._module_file_path

    @staticmethod
    def get_artifact_name():
        """
        Retrieves the current artifact name from the Context.

        Raises:
            ValueError: If the artifact name has not been set in the Context,
            indicating that this function was called outside of an artifact
            context.

        Returns:
            str: The name of the current artifact.
        """

        if not Context._artifact_name:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._artifact_name

    @staticmethod
    def get_files_found():
        """
        Retrieves the list of files found in the current context.

        Raises:
            ValueError: If the context has not been set, indicating that this
            function should only be called from within an artifact.

        Returns:
            list: The list of files found in the current context.
        """

        if not Context._files_found:
            raise ValueError("Context not set. This function should be" +
                             " called from within an artifact.")
        return Context._files_found

    @staticmethod
    def get_filename_lookup_map():
        """
        Retrieves the filename lookup map, initializing it if necessary.

        Returns:
            dict: A mapping of filenames to their corresponding lookup values.
        """

        if not Context._filename_lookup_map:
            Context._filename_lookup_map = Context._build_lookup_map()
        return Context._filename_lookup_map

    @staticmethod
    def get_source_file_path(partial_path):
        """
        Finds the full source path for a given partial or relative path.
        This function uses a pre-computed lookup map for high-speed searching.
        It first finds candidate paths based on the filename and then verifies
        the match using the full partial path provided.

        Args:
            partial_path (str): The partial or relative path of the file
                                 to find.

        Returns:
            str: The full path of the matching source file, or None
                  if not found.
        """
        lookup_map = Context.get_filename_lookup_map()

        # Defensive check to satisfy the linter.
        # This state should not be possible in practice.
        if lookup_map is None:
            return None

        filename = basename(partial_path)

        if filename in lookup_map:
            candidate_paths = lookup_map[filename]
            for candidate in candidate_paths:
                if Path(candidate).match(partial_path):
                    return candidate

        return None

    @staticmethod
    def get_data_folder():
        """
        Returns the global extraction folder path.
        """
        return Context._data_folder

    @staticmethod
    def get_relative_path(full_path):
        """
        Converts a full on-disk path (from files_found) to a relative
        extraction path by removing the global data_folder prefix.

        Args:
            full_path (str): The full path to the file.

        Returns:
            str: The relative extraction path, or the original path if
                 the data_folder is not available.
        """
        if not full_path or not Context._data_folder:
            return full_path

        if full_path.startswith(Context._data_folder):
            # Strip the base path and any leading separators
            return full_path[len(Context._data_folder):].lstrip('/\\')

        return full_path

    @staticmethod
    def get_apple_os_version(build, device_family=''):
        """
        Returns the Apple operating system version corresponding to a given
        build number and device family.

        Args:
            build (str): The build number to look up.
            device_family (str, optional): The device family (e.g., 'iPhone',
            'iPad', 'Mac', 'RealityDevice', 'Watch', 'AppleTV').
            Defaults to ''.

        Returns:
            str: The OS version string associated with the build and device
            family. If not found, returns an empty string.
        """
        group = None
        if 'iPhone' in device_family:
            group = 'iOS'
        elif 'iPad' in device_family:
            group = 'iOS'
        elif 'Mac' in device_family:
            group = 'macOS'
        elif 'RealityDevice' in device_family:
            group = 'visionOS'
        elif 'Watch' in device_family:
            group = 'watchOS'
        elif 'AppleTV' in device_family:
            group = 'tvOS'

        resolved = Context.lookup_metadata(
            'apple_build_id_to_os_version', build, group)

        if not resolved:
            return ''

        if 'iPad' in device_family:
            try:
                build_major = int(re.match(r'^(\d+)', build).group(1))
                if build_major >= 17:
                    resolved = resolved.replace('iOS', 'iPadOS', 1)
            except (TypeError, ValueError, AttributeError):
                pass

        return resolved

    @staticmethod
    def get_installed_os_version():
        """
        Retrieves the OS version of the installed device.
        """

        return Context._installed_os_version

    @staticmethod
    def clear():
        """
        Resets all context-related class variables to None, effectively
        clearing any stored state or references, except for the metadata
        cache and output parameters which are retained for efficiency.
        """
        Context._report_folder = None
        Context._seeker = None
        Context._artifact_info = None
        Context._module_name = None
        Context._module_file_path = None
        Context._artifact_name = None
        Context._files_found = []
        Context._filename_lookup_map = {}
