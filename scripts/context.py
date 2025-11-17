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

    _report_folder = None
    _seeker = None
    _artifact_info = None
    _module_name = None
    _module_file_path = None
    _artifact_name = None
    _files_found = []
    _filename_lookup_map = {}
    _device_ids = {}
    _device_boards = {}
    _os_builds = {}
    _installed_os_version = ""

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
    def _set_device_ids():
        """
        Loads device IDs from the data/device_ids.json file and
        assigns them to _device_ids Context class variable.
        """

        device_ids_path = Path(
            __file__).parent.absolute().joinpath('data', 'device_ids.json')
        with open(device_ids_path, 'rt', encoding='utf-8') as json_file:
            Context._device_ids = json.load(json_file)

    @staticmethod
    def _set_device_boards():
        """
        Loads device boards from the data/device_boards.json file and
        assigns them to _device_boards Context class variable.
        """

        device_boards_path = Path(
            __file__).parent.absolute().joinpath('data', 'device_boards.json')
        with open(device_boards_path, 'rt', encoding='utf-8') as json_file:
            Context._device_boards = json.load(json_file)

    @staticmethod
    def _set_os_builds():
        """
        Loads OS builds information from the data/os_builds.json file and
        assigns it to the _os_builds Context class variable.
        """

        os_builds_path = Path(
            __file__).parent.absolute().joinpath('data', 'os_builds.json')
        with open(os_builds_path, 'rt', encoding='utf-8') as json_file:
            Context._os_builds = json.load(json_file)

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
    def get_device_model(identifier):
        """
        Retrieves the device model name corresponding to a given identifier.

        Args:
            identifier (str): The device identifier to look up.

        Returns:
            str: The device model name if found; otherwise, an empty string.
        """

        if not Context._device_ids:
            Context._set_device_ids()
        return Context._device_ids.get(identifier, '')

    @staticmethod
    def get_device_model_from_board(board_id):
        """
        Retrieves the device model name corresponding to a given board ID.

        Args:
            board_id (str): The board ID to look up.

        Returns:
            str: The device model name if found; otherwise, an empty string.
        """

        if not Context._device_boards:
            Context._set_device_boards()
        return Context._device_boards.get(board_id, '')

    @staticmethod
    def get_os_version(build, device_family=''):
        """
        Returns the operating system version corresponding to a given build
        number and device family.

        Args:
            build (str): The build number to look up.
            device_family (str, optional): The device family (e.g., 'iPhone',
            'iPad', 'Mac', 'RealityDevice', 'Watch', 'AppleTV').
            Defaults to ''.

        Returns:
            str: The OS version string associated with the build and device
            family. If not found, returns an empty string.
        """

        if not Context._os_builds:
            Context._set_os_builds()
        if 'iPhone' in device_family:
            return Context._os_builds['iOS'].get(build, '')
        if 'iPad' in device_family:
            try:
                kernel_major_version = int(re.match(r'^(\d+)', build).group(1))
                if kernel_major_version >= 17:
                    return Context._os_builds['iOS'].get(
                        build, '').replace('iOS', 'iPadOS')
            except TypeError:
                pass
            return Context._os_builds['iOS'].get(build, '')
        if 'Mac' in device_family:
            return Context._os_builds['macOS'].get(build, '')
        if 'RealityDevice' in device_family:
            return Context._os_builds['visionOS'].get(build, '')
        if 'Watch' in device_family:
            return Context._os_builds['watchOS'].get(build, '')
        if 'AppleTV' in device_family:
            return Context._os_builds['tvOS'].get(build, '')
        os_version = []
        for os_family, builds in Context._os_builds.items():
            if build in builds:
                os_version.append(Context._os_builds[os_family][build])
        return (" or ").join(os_version)

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
        clearing any stored state or references, except for the device IDs and
        OS builds which are retained for efficiency.
        """
        Context._report_folder = None
        Context._seeker = None
        Context._artifact_info = None
        Context._module_name = None
        Context._module_file_path = None
        Context._artifact_name = None
        Context._files_found = []
        Context._filename_lookup_map = {}
