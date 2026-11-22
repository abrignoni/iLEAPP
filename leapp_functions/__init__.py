""" LEAPPs package """

import sys
from pathlib import Path

from .data_sources.json_files import convert_json_file_to_namedtuple

# From source, data/ is one folder above this package.
# In a build, PyInstaller unpacks it into the folder named by sys._MEIPASS.
DATA = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1])) / 'data'
CONFIG_FILE = DATA / 'leapp_config.json'

# The window and the command line both need these, the release tag and the build too.
REQUIRED = ('name', 'version')


def load_config():
    """ The tool's configuration, or an exit that says what is missing from it. """
    config = convert_json_file_to_namedtuple(CONFIG_FILE)
    missing = [field for field in REQUIRED if not getattr(config, field, '')]
    if missing:
        sys.exit(f"Cannot start: no {' and no '.join(missing)} in {CONFIG_FILE}.")
    return config


leapp = load_config()
