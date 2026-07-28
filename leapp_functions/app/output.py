"""Output folder path resolution and availability checks."""

import os
from datetime import datetime

from leapp_functions.app.platform import validate_filename
from scripts.version_info import leapp_name


def default_output_folder_name():
    '''Return the default report subfolder name for a new run.'''
    currenttime = datetime.now().strftime('%Y-%m-%d_%A_%H%M%S')
    return f'{leapp_name}_Output_{currenttime}'


def resolve_output_folder_name(custom_folder_name=None):
    '''Return the report subfolder name that will be created under the output path.'''
    if custom_folder_name:
        return custom_folder_name
    return default_output_folder_name()


def get_output_folder_base(output_folder, custom_folder_name=None):
    '''Return the full path to the report output folder.'''
    return os.path.join(output_folder, resolve_output_folder_name(custom_folder_name))


def validate_output_folder_available(output_folder, custom_folder_name=None):
    '''Return (is_valid, error_message) for filename rules and folder availability.'''
    folder_name = resolve_output_folder_name(custom_folder_name)
    if custom_folder_name:
        is_valid, error_message = validate_filename(folder_name)
        if not is_valid:
            return False, error_message
    output_folder_base = os.path.join(output_folder, folder_name)
    if os.path.exists(output_folder_base):
        return False, (
            f'Output folder already exists:\n{output_folder_base}\n\n'
            'Choose a different folder name or output path to avoid overwriting existing data.'
        )
    return True, None
