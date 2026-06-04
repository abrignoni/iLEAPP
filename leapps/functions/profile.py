"""Profile creation and loading helpers for LEAPP artifact selection."""

from pathlib import Path
from leapps.functions.data_sources.json_files import get_json_file_content, save_content_to_json_file


def create_profile(leapp, artifacts, path):
    """Create and save a profile JSON file for a LEAPP tool.
    Presents available artifacts, allows users to add/remove artifact selections
    by number, and saves the final selection to disk when the user quits.
    """
    available_artifacts = [(artifact.category, artifact.name) for artifact in artifacts]
    available_artifacts.sort()
    artifacts_in_profile = {}

    user_choice = ""
    print(f"--- {leapp.name} Profile file creation ---\n")
    instructions = "You can type:\n"
    instructions += "   - 'a' to add or remove artifacts in the profile file\n"
    instructions += "   - 'l' to display the list of all available artifacts with their number\n"
    instructions += "   - 'p' to display the artifacts added into the profile file\n"
    instructions += "   - 'q' to quit and save\n"
    while not user_choice:
        print(instructions)
        user_choice = input("Please enter your choice: ").lower()
        print()
        if user_choice == "l":
            print("Available artifacts:")
            for number, available_artifact in enumerate(available_artifacts):
                print(number + 1, available_artifact)
            print()
            user_choice = ""
        elif user_choice == "p":
            if artifacts_in_profile:
                for number, artifact in artifacts_in_profile.items():
                    print(number, artifact)
                print()
            else:
                print("No artifact added to the profile file\n")
            user_choice = ""
        elif user_choice == "a":
            artifacts_numbers = input(
                "Enter the artifact numbers, seperated by a comma, to add or remove them in the profile file: ")
            artifacts_numbers = artifacts_numbers.split(",")
            artifacts_numbers = [artifact_number.strip() for artifact_number in artifacts_numbers]
            for artifact_number in artifacts_numbers:
                if artifact_number.isdigit():
                    artifact_number = int(artifact_number)
                    if artifact_number > 0 and artifact_number <= len(available_artifacts):
                        if artifact_number not in artifacts_in_profile:
                            artifact_to_add = available_artifacts[artifact_number - 1]
                            artifacts_in_profile[artifact_number] = artifact_to_add
                            print(f"artifact number {artifact_number} {artifact_to_add} was added")
                        else:
                            artifact_to_remove = artifacts_in_profile[artifact_number]
                            print(f"artifact number {artifact_number} {artifact_to_remove} was removed")
                            del artifacts_in_profile[artifact_number]
                    else:
                        print("Please enter the number of an artifact!!!\n")
            print()
            user_choice = ""
        elif user_choice == "q":
            if artifacts_in_profile:
                artifacts_list = [module_info[1] for module_info in artifacts_in_profile.values()]
                profile_filename = ""
                while not profile_filename:
                    profile_filename = input("Enter the name of the profile: ")
                profile_filename += leapp.profile_extension
                filename = Path(path).joinpath(profile_filename)
                json_data = {"leapp": leapp.name, "format_version": 1, "artifacts": artifacts_list}
                save_content_to_json_file(filename, json_data)
                print("\nProfile saved:", filename)
                print()
            else:
                print("No artifact added. The profile file was not created.\n")
                print()
            return
        else:
            print("Please enter a valid choice!!!\n")
            user_choice = ""


def load_profile(leapp, profile_path, available_artifacts):
    """Load a profile file and return matching selected artifacts.

    Validates the profile metadata (LEAPP name and format version), then
    returns artifacts whose names appear in the profile plugin list.
    """
    profile_path = Path(profile_path)
    profile_load_error = None
    profile = get_json_file_content(profile_path)

    if profile:
        if isinstance(profile, dict):
            if profile.get("leapp") != leapp.name or profile.get("format_version") != 1:
                profile_load_error = "File is not a valid profile file: incorrect LEAPP or version"
                print(profile_load_error)
                return []
            profile_plugins = set(profile.get("plugins", []))
            return [selected_plugin for selected_plugin in available_artifacts
                    if selected_plugin.name in profile_plugins]
        profile_load_error = "File was not a valid profile file: invalid format"
        print(profile_load_error)
        return []
    return []
