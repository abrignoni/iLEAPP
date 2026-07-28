"""
Parses artifact modules to generate comprehensive documentation.

This script scans all Python files in the 'scripts/artifacts' directory to
extract metadata about the artifacts they define. It supports two formats for
artifact definitions: a legacy `__artifacts__` (v1) dictionary and a newer,
more detailed `__artifacts_v2__` dictionary.

The script processes each module to determine its artifact version and extracts
relevant details. For v2 artifacts, it captures the name, description, search
paths, output types, icon, version, and last update date. For v1 artifacts, it
simply lists the artifact names.

Finally, it aggregates all this information and generates a detailed summary in
a Markdown file ('admin/docs/generated/module_info.md'). The summary includes:
- A statistical overview (total modules, v1/v2 artifact counts, etc.).
- A detailed table for v2 artifacts.
- A simpler table for v1 artifacts.
- A table listing any modules that caused parsing errors.

This provides a centralized, auto-generated reference for all artifacts in the
project, which is kept up-to-date by running this script.
"""
import os
import re
import ast
from pathlib import Path

# Get the root directory of the repository (2 directories above the script)
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))

# Define key paths and constants
ARTIFACTS_DIR = os.path.join(REPO_ROOT, 'scripts', 'artifacts')
VERSION_INFO_PATH = os.path.join(REPO_ROOT, 'scripts', 'version_info.py')
MD_FILE_PATH = os.path.join(
    REPO_ROOT, 'admin', 'docs', 'generated', 'module_info.md')
GITHUB_MODULE_URL = "/scripts/artifacts/"
START_MARKER = "<!-- MODULE_INFO_START -->"
END_MARKER = "<!-- MODULE_INFO_END -->"


def get_tool_name():
    """Get the LEAPP tool name from project metadata."""
    try:
        with open(VERSION_INFO_PATH, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError):
        return ""

    for item in tree.body:
        if not isinstance(item, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == 'leapp_name'
            for target in item.targets
        ):
            continue
        try:
            leapp_name = ast.literal_eval(item.value)
        except (ValueError, TypeError, SyntaxError):
            return ""
        if isinstance(leapp_name, str) and leapp_name:
            return leapp_name
    return ""


TOOL_NAME = get_tool_name()


def section_title(title):
    """Add the tool name to generated section titles when available."""
    if TOOL_NAME:
        return f"{TOOL_NAME} {title}"
    return title


def decorator_name(decorator):
    """Return the simple decorator name from an AST decorator node."""
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Call):
        return decorator_name(decorator.func)
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    return ""


def format_paths(paths):
    """Format artifact paths for markdown."""
    if isinstance(paths, (list, tuple)):
        return ', '.join(f'`{path}`' for path in paths)
    if paths:
        return f'`{paths}`'
    return ""


def normalize_output_types(output_types):
    """Return output types as a list for stats and rendering."""
    if isinstance(output_types, (list, tuple, set)):
        return [str(output_type) for output_type in output_types]
    if output_types:
        return [str(output_types)]
    return []


def format_output_types(output_types):
    """Format artifact output types for markdown."""
    return ', '.join(normalize_output_types(output_types))


def has_lava_output(output_types):
    """Match the runtime output group behavior for LAVA availability."""
    output_type_set = set(normalize_output_types(output_types))
    return bool(output_type_set.intersection(
        {'all', 'standard', 'lava', 'lava_only'}
    ))


def clean_string(s):
    """
    Sanitize a string by removing line breaks and limiting its length.

    Args:
        s (str): The input string to clean.

    Returns:
        str: The cleaned and truncated string.
    """
    return ' '.join(s.split())[:150]


def extract_v2_info(module_content):
    """
    Extract artifact information from a v2 `__artifacts_v2__` block
    and number of parameters in the corresponding function definition to detect
    usage of new context.

    This function uses ast module to parse the module content and extract
    the `__artifacts_v2__` dictionary and function definitions. It counts the
    number of parameters in each function to determine if context is used.

    Args:
        module_content (str): The string content of the Python module.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains
                    the details for a single v2 artifact with the number of
                    parameters in the corresponding function definition.
                    Returns "error" and an error message if parsing fails.
    """

    results = []
    artifacts_dict = {}
    parameters_dict = {}
    artifact_functions = set()
    warnings = []

    try:
        tree = ast.parse(module_content)
    except SyntaxError as e:
        return "error", [f"Syntax error: {clean_string(str(e))}"], []

    for item in tree.body:
        if (
            isinstance(item, ast.Assign) and
            any(
                isinstance(target, ast.Name) and target.id == '__artifacts_v2__'
                for target in item.targets
            )
        ):
            if isinstance(item.value, ast.Dict):
                try:
                    artifacts_dict = ast.literal_eval(item.value)
                except (ValueError, TypeError, SyntaxError) as e:
                    return "error", [
                        f"Error evaluating __artifacts_v2__: "
                        f"{clean_string(str(e))}"
                    ], []
            else:
                return "error", [
                    "__artifacts_v2__ must be a literal dictionary"
                ], []
        if isinstance(item, ast.FunctionDef):
            parameters_len = len([arg.arg for arg in item.args.args])
            parameters_dict[item.name] = parameters_len
            if any(
                decorator_name(decorator) == 'artifact_processor'
                for decorator in item.decorator_list
            ):
                artifact_functions.add(item.name)

    artifact_function_names = {
        details.get('function', artifact_name)
        for artifact_name, details in artifacts_dict.items()
    }
    missing_functions = sorted(
        artifact_function_name
        for artifact_function_name in artifact_function_names
        if artifact_function_name not in parameters_dict
    )
    missing_metadata = sorted(artifact_functions - artifact_function_names)
    if missing_functions:
        warnings.append(
            "Artifact metadata without matching function: "
            + ', '.join(missing_functions)
        )
    if missing_metadata:
        warnings.append(
            "@artifact_processor function without matching artifact metadata: "
            + ', '.join(missing_metadata)
        )

    for artifact_name, details in artifacts_dict.items():
        paths = details.get("paths", "")
        output_types = details.get("output_types", "")
        uses_function_key = "function" in details
        function_name = details.get("function", artifact_name)
        version = details.get("version", "")
        last_update_date = details.get("last_update_date", "")
        artifact_icon = details.get("artifact_icon", "")
        results.append({
            "artifact": artifact_name,
            "name": clean_string(details.get("name", "")),
            "category": details.get("category", ""),
            "description": clean_string(details.get("description", "")),
            "paths": paths,
            "output_types": output_types,
            "version": version,
            "last_update_date": last_update_date,
            "artifact_icon": artifact_icon,
            "parameters_len": parameters_dict.get(function_name, 0),
            "uses_function_key": uses_function_key
        })
    return "v2", results, warnings


def extract_v1_info(module_content):
    """
    Extract artifact names from a legacy v1 `__artifacts__` block.

    Args:
        module_content (str): The string content of the Python module.

    Returns:
        list[str]: A list of artifact names found in the block.
    """
    pattern = re.compile(r"__artifacts__\s*=\s*{(.*?)}", re.DOTALL)
    match = pattern.search(module_content)
    if not match:
        return []

    artifact_block = match.group(1)
    artifact_names = re.findall(r'"(\w+)":', artifact_block)
    return artifact_names


def parse_module_file(module_path):
    """
    Parse a module file to extract artifact details for either v1 or v2.

    Args:
        module_path (str): The path to the artifact module file.

    Returns:
        tuple[str, list]: A tuple containing the artifact version ('v1', 'v2',
                          or 'error') and a list of the extracted artifact
                          details or error messages.
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "__artifacts_v2__" in content:
            return extract_v2_info(content)
        if "__artifacts__" in content:
            return "v1", extract_v1_info(content), []
        return "error", ["No recognized artifacts found"], []
    except OSError as e:
        return "error", [f"Error reading file: {clean_string(str(e))}"], []
    except UnicodeDecodeError as e:
        return "error", [f"Encoding error: {clean_string(str(e))}"], []


def generate_v2_markdown_table(artifact_data):
    """
    Generate a markdown table for v2 artifacts.

    Args:
        artifact_data (dict): A dictionary mapping module names to their
                              v2 artifact data.

    Returns:
        str: A string containing the formatted markdown table.
    """
    table = "| Module | Artifact | Name | Category | Output Types | Context | Icon " + \
        "| Version | Last Update Date | Description | Paths |\n"
    table += "|--------|----------|------|----------|--------------|---------|------" + \
        "|---------|------------------|-------------|-------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}]({GITHUB_MODULE_URL}{module})"
        for artifact in artifacts:
            name = clean_string(artifact.get('name', ''))
            description = clean_string(artifact.get('description', ''))
            category = artifact.get('category', '')
            paths = format_paths(artifact.get('paths', ''))
            output_types = format_output_types(
                artifact.get('output_types', '-')
            )
            context = "Yes" if artifact.get('parameters_len') == 1 else "No"
            artifact_icon = artifact.get('artifact_icon', '')
            version = artifact.get('version', '')
            last_update_date = artifact.get('last_update_date', '')
            table += f"| {module_link} | {artifact['artifact']} | {name} " + \
                f"| {category} | {output_types} | {context} | {artifact_icon} | " + \
                f"{version} | {last_update_date} | {description} | {paths} |\n"

    return table


def generate_v1_markdown_table(artifact_data):
    """
    Generate a markdown table for v1 artifacts.

    Args:
        artifact_data (dict): A dictionary mapping module names to their
                              v1 artifact data.

    Returns:
        str: A string containing the formatted markdown table.
    """
    table = "| Module | Artifacts |\n"
    table += "|--------|----------|\n"
    for module, artifacts in artifact_data.items():
        module_link = f"[{module}]({GITHUB_MODULE_URL}{module})"
        artifacts_str = ', '.join(artifacts)
        table += f"| {module_link} | {artifacts_str} |\n"
    return table


def generate_error_markdown_table(error_data):
    """
    Generate a markdown table for modules with errors.

    Args:
        error_data (dict): A dictionary mapping module names to the
                           errors encountered.

    Returns:
        str: A string containing the formatted markdown table for errors.
    """
    table = "| Module | Error/Issue |\n"
    table += "|--------|-------------|\n"
    for module, errors in error_data.items():
        error_str = ', '.join(map(clean_string, errors))
        table += f"| {module} | {error_str} |\n"
    return table


def update_markdown_file(v1_data, v2_data, error_data, issue_data):
    """
    Update the markdown file with the parsed artifact data and summary.

    This function calculates summary statistics, generates markdown tables for
    v1, v2, and error data, and then replaces a designated section in the
    markdown file with this new content.

    Args:
        v1_data (dict): Data for v1 artifacts.
        v2_data (dict): Data for v2 artifacts.
        error_data (dict): Data for modules with errors.
        issue_data (dict): Data for modules with metadata issues.
    """
    total_modules = len(v1_data) + len(v2_data) + len(error_data)
    v1_count = sum(len(artifacts) for artifacts in v1_data.values())
    v2_count = sum(len(artifacts) for artifacts in v2_data.values())
    total_artifacts = v1_count + v2_count
    error_count = len(error_data)
    issue_count = len(issue_data)

    # Count modules with 'lava output'
    lava_output_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if has_lava_output(artifact.get('output_types'))
    )

    # Count modules using 'artifact_icon'
    artifact_icon_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('artifact_icon')
    )

    # Count modules using 'version'
    version_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('version')
    )

    # Count modules using 'last_update_date'
    last_update_date_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('last_update_date')
    )

    # Count modules using 'context'
    context_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('parameters_len') == 1
    )

    # Count modules using deprecated 'function' key
    function_key_count = sum(
        1 for artifacts in v2_data.values()
        for artifact in artifacts
        if artifact.get('uses_function_key')
    )

    with open(MD_FILE_PATH, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Split the content into before, between, and after the markers
    before_marker, _, after_marker = content.partition(START_MARKER)
    _, _, after_info_marker = after_marker.partition(END_MARKER)

    # Generate new markdown content
    new_module_info = f"## {section_title('Summary')}\n\n"
    new_module_info += f"Total number of modules: {total_modules}  \n"
    new_module_info += f"Total number of artifacts: {total_artifacts}  \n"
    new_module_info += f"Number of v1 artifacts: {v1_count}  \n"
    new_module_info += f"Number of v2 artifacts: {v2_count}  \n"
    new_module_info += "Number of artifacts with 'lava output': " + \
        f"{lava_output_count}  \n"
    new_module_info += "Number of artifacts using 'artifact_icon': " + \
        f"{artifact_icon_count}  \n"
    new_module_info += "Number of artifacts using 'last_update_date': " + \
        f"{last_update_date_count}  \n"
    new_module_info += "Number of artifacts using context parameter: " + \
        f"{context_count}  \n"
    new_module_info += "Number of artifacts with errors or no recognized " + \
        f"artifacts: {error_count}  \n"
    new_module_info += "Number of modules with artifact metadata issues: " + \
        f"{issue_count}  \n"
    new_module_info += "Number of artifacts using **deprecated** 'version' " + \
        f"key: {version_count}  \n"
    new_module_info += "Number of artifacts using **deprecated** 'function' " + \
        f"key: {function_key_count}  \n\n"

    if v2_data:
        new_module_info += \
            f"## {section_title('V2 Artifacts Table')}\n\n"
        new_module_info += generate_v2_markdown_table(v2_data)
        new_module_info += "\n"

    if v1_data:
        new_module_info += \
            f"## {section_title('V1 Artifacts Table')}\n\n"
        new_module_info += generate_v1_markdown_table(v1_data)
        new_module_info += "\n"

    if error_data:
        new_module_info += \
            "## " + section_title(
                'Modules with Errors or No Recognized Artifacts'
            ) + "\n\n"
        new_module_info += generate_error_markdown_table(error_data)

    if issue_data:
        new_module_info += \
            "\n## " + section_title(
                'Modules with Artifact Metadata Issues'
            ) + "\n\n"
        new_module_info += generate_error_markdown_table(issue_data)

    # Rebuild the file content with the updated section
    new_content = f"{before_marker}{START_MARKER}\n\n{new_module_info}\n" + \
        f"{END_MARKER}{after_info_marker}"

    # Write the updated content back to the markdown file
    with open(MD_FILE_PATH, 'w', encoding='utf-8') as md_file:
        md_file.write(new_content)


def main():
    """
    Main function to drive the artifact parsing and documentation generation.

    It initializes data structures, iterates through all artifact modules,
    parses each file, sorts the collected data, and then calls the function
    to update the final markdown documentation file.
    """
    v1_data = {}
    v2_data = {}
    error_data = {}
    issue_data = {}

    print(f"Scanning directory: {ARTIFACTS_DIR}")
    # Scan the artifacts directory for module files
    for module_path in sorted(Path(ARTIFACTS_DIR).iterdir()):
        if module_path.is_file():
            module_name = module_path.name
            print(f"Processing module: {module_name}")
            version, artifacts, issues = parse_module_file(str(module_path))
            if version == "v1":
                v1_data[module_name] = artifacts
            elif version == "v2":
                v2_data[module_name] = artifacts
            else:
                error_data[module_name] = artifacts
            if issues:
                issue_data[module_name] = issues

    # Sort the artifact_data dictionaries by keys (module filenames)
    v1_data = dict(sorted(v1_data.items()))
    v2_data = dict(sorted(v2_data.items()))
    error_data = dict(sorted(error_data.items()))
    issue_data = dict(sorted(issue_data.items()))

    # Update the markdown file with the sorted artifact data
    update_markdown_file(v1_data, v2_data, error_data, issue_data)
    print(f"\nMarkdown file updated: {MD_FILE_PATH}")


if __name__ == "__main__":
    main()
