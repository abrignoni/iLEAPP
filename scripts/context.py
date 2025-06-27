class Context:
    _report_folder = None
    _seeker = None
    _artifact_info = None
    _module_name = None
    _module_file_path = None
    _artifact_name = None
    _files_found = None

    @staticmethod
    def set_report_folder(report_folder):
        Context._report_folder = report_folder

    @staticmethod
    def set_seeker(seeker):
        Context._seeker = seeker
        
    @staticmethod
    def set_artifact_info(artifact_info):
        Context._artifact_info = artifact_info

    @staticmethod
    def set_module_name(module_name):
        Context._module_name = module_name

    @staticmethod
    def set_module_file_path(module_file_path):
        Context._module_file_path = module_file_path

    @staticmethod
    def set_artifact_name(artifact_name):
        Context._artifact_name = artifact_name

    @staticmethod
    def set_files_found(files_found):
        Context._files_found = files_found

    @staticmethod
    def get_report_folder():
        if not Context._report_folder:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._report_folder

    @staticmethod
    def get_seeker():
        if not Context._seeker:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._seeker

    @staticmethod
    def get_artifact_info():
        if not Context._artifact_info:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._artifact_info

    @staticmethod
    def get_module_name():
        if not Context._module_name:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._module_name

    @staticmethod
    def get_module_file_path():
        if not Context._module_file_path:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._module_file_path

    @staticmethod
    def get_artifact_name():
        if not Context._artifact_name:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._artifact_name

    @staticmethod
    def get_files_found():
        if not Context._files_found:
            raise ValueError("Context not set. This function should be called from within an artifact.")
        return Context._files_found

    @staticmethod
    def clear():
        Context._report_folder = None
        Context._seeker = None
        Context._artifact_info = None
        Context._module_name = None
        Context._module_file_path = None
        Context._artifact_name = None
        Context._files_found = None