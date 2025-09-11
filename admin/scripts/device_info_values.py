"""
Parses artifact modules to find usage of device_info and logdevinfo.

This script scans all Python files in the scripts/artifacts directory to
identify calls to the `device_info` and `logdevinfo` functions. It extracts
the arguments passed to these functions and aggregates them to create a summary
of what device information is being logged and by which modules.

The aggregated data is then formatted into two Markdown tables:
1. `device_info` usage, showing Category, Label, and Source Modules.
2. `logdevinfo` usage, showing the Key and Source Modules.

Finally, the script updates the 'admin/docs/generated/device_info_values.md'
file by replacing placeholder sections with the newly generated tables. This
provides an up-to-date reference of device info usage across all artifacts.
"""
import os
import re
import ast
from pathlib import Path

# Define project structure paths
ARTIFACTS_DIR_NAME = 'scripts/artifacts'
DEVICE_INFO_DOC_PATH = 'admin/docs/generated/device_info_values.md'


def find_function_calls(file_path, function_name):
    """
    Parse a Python file and find all calls to the specified function.

    This function attempts to use Abstract Syntax Trees (AST) for accurately
    finding function calls and their arguments. If AST parsing fails for any
    reason, it falls back to using regular expressions to find matches.

    Args:
        file_path (str or Path): The path to the Python file to analyze.
        function_name (str): The name of the function to search for
                             ('device_info' or 'logdevinfo').

    Returns:
        list[tuple]: A list of tuples containing the captured arguments.
                     For 'device_info', it's (category, label).
                     For 'logdevinfo', it's (key,).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    calls = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == function_name:
                    if function_name == 'device_info' and len(node.args) >= 2:
                        # Get the string values if they're string literals
                        if isinstance(node.args[0], ast.Constant) and isinstance(node.args[1], ast.Constant):
                            calls.append((node.args[0].value, node.args[1].value))
                    elif function_name == 'logdevinfo' and len(node.args) >= 1:
                        # For logdevinfo, try to extract the message without HTML tags
                        if isinstance(node.args[0], (ast.Constant, ast.JoinedStr)):
                            # Convert the argument to string and strip HTML
                            arg_str = ast.unparse(node.args[0])
                            # Remove f-string prefix if present
                            arg_str = arg_str.strip('f').strip('"\'')
                            # Basic HTML tag removal (can be enhanced if needed)
                            clean_str = re.sub(r'<[^>]+>', '', arg_str)
                            calls.append((clean_str,))
    except:
        # If parsing fails, try regex as fallback
        if function_name == 'device_info':
            pattern = r'device_info\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\s*,'
            calls.extend(re.findall(pattern, content))
        else:
            # Updated pattern to handle f-strings and HTML tags
            pattern = r'logdevinfo\(f?[\'"].*?<b>([^<]+)</b>'
            matches = re.findall(pattern, content)
            calls.extend([(m.strip(),) for m in matches])
    
    return calls


def generate_markdown():
    """
    Generate markdown documentation for device_info and logdevinfo usage.

    This function orchestrates the process of scanning artifact files,
    collecting usage data, formatting it into markdown tables, and
    updating the documentation file.
    """
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent
    
    artifacts_dir = Path(root_dir, ARTIFACTS_DIR_NAME)
    device_info_usage = {}
    logdevinfo_usage = {}
    
    # Scan all Python files in artifacts directory
    for file_path in artifacts_dir.glob('*.py'):
        module_name = file_path.stem
        
        # Find device_info calls
        device_calls = find_function_calls(file_path, 'device_info')
        if device_calls:
            for category, label in device_calls:
                if category not in device_info_usage:
                    device_info_usage[category] = {}
                if label not in device_info_usage[category]:
                    device_info_usage[category][label] = []
                device_info_usage[category][label].append(module_name)
        
        # Find logdevinfo calls
        log_calls = find_function_calls(file_path, 'logdevinfo')
        if log_calls:
            for (key,) in log_calls:
                if key not in logdevinfo_usage:
                    logdevinfo_usage[key] = []
                logdevinfo_usage[key].append(module_name)
    
    # Generate markdown content
    device_info_md = "| Category | Label | Source Modules |\n|-----------|-------|----------------|\n"
    for category in sorted(device_info_usage.keys()):
        for label in sorted(device_info_usage[category].keys()):
            modules = ", ".join(sorted(set(device_info_usage[category][label])))
            device_info_md += f"| {category} | {label} | {modules} |\n"
    
    logdevinfo_md = "| Key | Source Modules |\n|-----|----------------|\n"
    for key in sorted(logdevinfo_usage.keys()):
        modules = ", ".join(sorted(set(logdevinfo_usage[key])))
        logdevinfo_md += f"| {key} | {modules} |\n"
    
    # Read the existing markdown file
    doc_path = Path(root_dir, DEVICE_INFO_DOC_PATH)
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the placeholders
    content = re.sub(
        r'<!-- DEVICE_INFO_START -->.*<!-- DEVICE_INFO_END -->',
        f'<!-- DEVICE_INFO_START -->\n{device_info_md}<!-- DEVICE_INFO_END -->',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'<!-- LOGDEVINFO_START -->.*<!-- LOGDEVINFO_END -->',
        f'<!-- LOGDEVINFO_START -->\n{logdevinfo_md}<!-- LOGDEVINFO_END -->',
        content,
        flags=re.DOTALL
    )
    
    # Write the updated content
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    generate_markdown()
