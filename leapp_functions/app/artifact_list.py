"""
The artifacts lists, and those selected when it opens.
"""

from collections import namedtuple
from fnmatch import fnmatchcase
from types import SimpleNamespace

from leapp_functions import leapp
from leapp_functions.data_sources.json_files import (get_json_file_content,
                                                     save_content_to_json_file)
from scripts import plugin_loader
from scripts.modules_to_exclude import modules_to_exclude

HIDDEN = tuple(getattr(leapp, "hidden_artifacts", ()))
PROFILE_LEAPP = leapp.name.lower()
PROFILE_VERSION = 1

Artifact = namedtuple("Artifact", "name title category module default")
Profile = namedtuple("Profile", "path names unknown")


def is_hidden(name):
    """ Whether an artifact is left out of the list, from its name. """
    return any(fnmatchcase(name, pattern) for pattern in HIDDEN)


def list_artifacts(loader):
    """
    The artifacts that can be chosen, sorted by category then by title.
    Args:
        loader (PluginLoader): the artifacts found in scripts/artifacts.
    Returns:
        list of Artifact: name is the key used in profiles and by the loader, title the name
        shown, default whether it is selected when the window opens (modules_to_exclude
        holds the modules that are not).
    """
    listed = [Artifact(plugin.name, plugin.artifact_info.get("name", plugin.name), plugin.category,
                       plugin.module_name, plugin.module_name not in modules_to_exclude)
              for plugin in loader.plugins if not is_hidden(plugin.name)]
    return sorted(listed, key=lambda artifact: (artifact.category.upper(), artifact.title.upper()))


def search(listed, term):
    """ The artifacts whose category or title holds the term, case insensitive. """
    term = term.lower()
    return [artifact for artifact in listed
            if term in f"{artifact.category} {artifact.title}".lower()]


def by_title(listed):
    """ The names of the artifacts, in the alphabetical order of their titles. """
    return [artifact.name for artifact in sorted(listed, key=lambda item: item.title.upper())]


def group_by_category(listed):
    """ Category names in alphabetical order. """
    groups = {}
    for artifact in listed:
        groups.setdefault(artifact.category, []).append(artifact.name)
    return groups


def toggle(names, selected):
    """ Select every artifact named, or unselect them all when they are all selected already.
    Args:
        names (list of str): the artifacts the user acts on.
        selected (set of str): the names of the artifacts selected, changed in place.
    """
    if selected.issuperset(names):
        selected.difference_update(names)
    else:
        selected.update(names)


def read_profile(path):
    """ The names of the artifacts a profile file holds.
    Raises:
        ValueError: the file is not a profile of this LEAPP, with the message to show.
    """
    content = get_json_file_content(path)
    if not content or not isinstance(content, dict):
        raise ValueError("File was not a valid profile file: invalid format")
    if (str(content.get("leapp")).lower() != PROFILE_LEAPP
            or content.get("format_version") != PROFILE_VERSION):
        raise ValueError("File was not a valid profile file: incorrect LEAPP or version")
    names = content.get("plugins", [])
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise ValueError("File was not a valid profile file: invalid format")
    return names


def write_profile(path, artifacts):
    """ Write the names of the artifacts selected to a profile file, in the order of the list.
    Returns:
        bool: the file was written or not.
    """
    names = [artifact.name for artifact in artifacts.listed if artifact.name in artifacts.selected]
    return save_content_to_json_file(path, {"leapp": PROFILE_LEAPP, "format_version": PROFILE_VERSION,
                                            "plugins": names})


def load_profile(path, artifacts):
    """ Select the artifacts of a profile file.
    Raises:
        ValueError: see read_profile. The selection and the profile are left as they were.
    """
    names = read_profile(path)
    listed = {artifact.name for artifact in artifacts.listed}
    artifacts.profile = Profile(path, listed.intersection(names), sorted(set(names) - listed))
    artifacts.selected.clear()
    artifacts.selected.update(artifacts.profile.names)


def profile_artifacts(artifacts):
    """ The artifacts loaded from the profile. """
    return [artifact for artifact in artifacts.listed if artifact.name in artifacts.profile.names]


def profile_for_report(artifacts):
    """ The path of the profile loaded or None. """
    profile = artifacts.profile
    return profile.path if profile and artifacts.selected == profile.names else None


def run_order(artifacts):
    """ The plugins of the selected artifacts. """
    return [plugin for plugin in sorted(artifacts.loader.plugins, key=lambda item: item.category.upper())
            if plugin.name in artifacts.selected]


def load_artifacts():
    """ Load every artifact module once.
    Returns:
        SimpleNamespace: loader; listed, the artifacts that can be
        chosen; selected, the names of those selected by default; search, the text searched;
        view, how the list is shown; profile, the Profile loaded.
    """
    loader = plugin_loader.PluginLoader()
    listed = list_artifacts(loader)
    return SimpleNamespace(loader=loader, listed=listed,
                           selected={artifact.name for artifact in listed if artifact.default},
                           search="", view="all", profile=None)
