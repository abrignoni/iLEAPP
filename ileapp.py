#!/usr/bin/env python3

"""LEAPP tool CLI main script."""

import sys
import argparse
import leapps.functions as leapps

from pathlib import Path

from scripts.lavafuncs import initialize_lava, lava_finalize_output
from scripts.crunch_artifacts import crunch_artifacts

leapp = leapps.convert_json_file_to_namedtuple("leapps/settings.json")


def validate_args(args):
    """Validate provided CLI arguments."""
    if args.artifact_paths or args.create_profile_casedata:
        return  # Skip further validation if --artifact_paths is used

    # Ensure other arguments are provided
    mandatory_args = ["input_path", "output_path", "t"]
    for arg in mandatory_args:
        value = getattr(args, arg)
        if value is None:
            raise argparse.ArgumentError(
                None, f"No {arg.upper()} provided. Run the program again.")

    # Check existence of paths
    if not Path(args.input_path).exists():
        raise argparse.ArgumentError(
            None, f"INPUT path '{args.input_path}' does not exist! Run the program again.")

    if not Path(args.output_path).exists():
        raise argparse.ArgumentError(
            None, f"OUTPUT path '{args.output_path}' does not exist! Run the program again.")

    if not Path(args.output_path).absolute().is_dir():
        raise argparse.ArgumentError(
            None, f"OUTPUT path '{args.output_path}' must be a directory! Run the program again.")

    # Validate input_path based on type
    abs_input_path = Path(args.input_path).absolute()
    if args.t == "fs":  # Filesystem input type
        # Check if input path is a directory
        if not Path(abs_input_path).is_dir():
            raise argparse.ArgumentError(
                None, f"INPUT path '{args.input_path}' is not a directory. """
                "Type 'fs' requires a directory input. Run the program again.")
        # Check if directory is empty
        if not Path(abs_input_path).iterdir():
            raise argparse.ArgumentError(
                None, f"Input directory '{args.input_path}' is empty. Run the program again.")
    elif args.t == "file":  # Single file input type
        if not Path(abs_input_path).is_file():
            raise argparse.ArgumentError(
                None, f"INPUT path '{args.input_path}' is not a file. "
                "Type 'file' requires a single file input. Run the program again.")

    if args.load_case_data and not Path(args.load_case_data).exists():
        raise argparse.ArgumentError(
            None, "LEAPP Case Data file not found! Run the program again.")

    if args.load_profile and not Path(args.load_profile).exists():
        raise argparse.ArgumentError(
            None, f"{leapp.name} profile file not found! Run the program again.")


def main():
    """Parse command-line arguments and run requested actions."""
    itunes_choice = ["itunes"] if leapp.name == "ileapp" else []
    itunes_help_message = "'itunes' for a folder containing a raw iTunes backup with hashed paths and names, "

    parser = argparse.ArgumentParser(description=f"{leapp.name} v{leapp.version}: "
                                     f"{leapp.description}")
    parser.add_argument("-t", choices=["fs", "tar", "zip", "gz", "file"] + itunes_choice,
                        required=False, action="store",
                        help=("Specify the input type. "
                              "'fs' for a folder containing extracted files with normal paths and names, "
                              "'tar', 'zip', or 'gz' for compressed packages containing files with normal names, "
                              + itunes_help_message if leapp.name == "iLEAPP" else "" +
                              "'file' for a single file input."))
    parser.add_argument("-o", "--output_path", required=False, action="store",
                        help="Path to base output folder (this must exist)")
    parser.add_argument("-i", "--input_path", required=False, action="store", help="Path to input file/folder")
    parser.add_argument("-w", "--wrap_text", required=False, action="store_false", default=True,
                        help="Do not wrap text for output of data files")
    parser.add_argument("-m", "--load_profile", required=False, action="store",
                        help=f"Path to {leapp.name} Profile file ({leapp.profile_extension}).")
    parser.add_argument("-d", "--load_case_data", required=False, action="store",
                        help=f"Path to LEAPP Case Data file ({leapp.casedata_extension}).")
    parser.add_argument("-c", "--create_profile_casedata", required=False, action="store",
                        help=(f"Generate an {leapp.name} Profile file ({leapp.profile_extension}) or "
                              f"LEAPP Case Data file ({leapp.casedata_extension}) into the specified path. "
                              "This argument is meant to be used alone, without any other arguments."))
    parser.add_argument("-p", "--artifact_paths", required=False, action="store_true",
                        help=("Generate a text file list of artifact paths. "
                              "This argument is meant to be used alone, without any other arguments."))
    parser.add_argument("--custom_output_folder", required=False, action="store",
                        help="Custom name for the output folder")
    parser.add_argument("--custom_artifacts_path", required=False, action="store",
                        help="Additional path to load artifacts from (e.g., scripts/alternate_artifacts)")
    if leapp.name == "iLEAPP":
        parser.add_argument("--itunes_password", required=False, action="store",
                            help="Password used for encrypted iTunes backup")

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit()

    args = parser.parse_args()

    available_artifacts = []
    loader_paths = [leapps.artifacts.artifact_loader.ARTIFACT_PATHS]
    if args.custom_artifacts_path:
        loader_paths.append(Path(args.custom_artifacts_path))
    loader = leapps.ArtifactLoader(artifact_paths=loader_paths)
    for artifact in sorted(loader.artifacts, key=lambda p: p.category):
        if (artifact.module_name == 'iTunesBackupInfo'
                or artifact.name == 'last_build'
                or artifact.module_name == 'logarchive' and artifact.name != 'logarchive'):
            continue
        available_artifacts.append(artifact)
    selected_artifacts = available_artifacts.copy()
    casedata = {}

    try:
        validate_args(args)
    except argparse.ArgumentError as e:
        parser.error(str(e))

    if args.artifact_paths:
        print("Artifact path list generation started.\n")
        path_list = set()
        for artifact in loader.artifacts:
            if artifact.module_name == "logarchive":
                continue
            if isinstance(artifact.search, tuple):
                for x in artifact.search:
                    path_list.add(x)
            elif isinstance(artifact.search, str):
                path_list.add(artifact.search)
            else:
                continue
        with open("path_list.txt", "w", encoding="utf-8") as paths:
            for path in sorted(path_list):
                paths.write(f"{path}\n")
                print(path)
        print("\nArtifact path list generation completed")
        return

    if args.create_profile_casedata:
        if Path(args.create_profile_casedata).is_dir():
            create_choice = ""
            print("-" * 55)
            print(f"Welcome to {leapp.name} Profile or Case Data file creation\n")
            instructions = "You can type:\n"
            instructions += f"   - '1' to create an {leapp.name} Profile file ({leapp.profile_extension})\n"
            instructions += f"   - '2' to create a LEAPP Case Data file ({leapp.casedata_extension})\n"
            instructions += "   - 'q' to quit\n"
            while not create_choice:
                print(instructions)
                create_choice = input("Please enter your choice: ").lower()
                print()
                if create_choice == "1":
                    leapps.create_profile(leapp, available_artifacts, args.create_profile_casedata)
                    create_choice = ""
                elif create_choice == "2":
                    leapps.create_casedata(leapp, args.create_profile_casedata)
                    create_choice = ""
                elif create_choice == "q":
                    return
                else:
                    print("Please enter a valid choice!!!\n")
                    create_choice = ""
        else:
            print(f"OUTPUT folder for storing f{leapp.name} Profile file does not exist!\n"
                  "Run the program again.")
            return

    if args.load_case_data:
        casedata = leapps.load_casedata(args.load_case_data)

    if args.load_profile:
        selected_artifacts = leapps.load_profile(leapp, args.load_profile, available_artifacts)

    extracttype = args.t
    input_path = Path(args.input_path)
    output_path = Path(args.output_path).absolute()
    custom_output_folder = Path(args.custom_output_folder) if args.custom_output_folder else None
    wrap_text = args.wrap_text
    itunes_backup_password = args.itunes_password

    # ios file system extractions contain paths > 260 char, which causes problems
    # This fixes the problem by prefixing \\?\ on each windows path.
    if sys.platform == 'win32':
        if input_path.drive and extracttype == 'fs':
            input_path = Path(r"\\?\\" + input_path.as_posix().replace('/', '\\'))
        if output_path.drive:
            output_path = Path(r"\\?\\" + output_path.as_posix().replace('/', '\\'))

    out_params = leapps.OutputParameters(output_path, custom_output_folder)
    leapps.Context.set_output_params(out_params)

    initialize_lava(input_path, out_params.output_folder_base, extracttype)

    crunch_artifacts(selected_artifacts, extracttype, input_path, out_params, wrap_text, loader,
                     casedata, args.load_profile, itunes_backup_password)

    lava_finalize_output(out_params.output_folder_base)


if __name__ == "__main__":
    main()
