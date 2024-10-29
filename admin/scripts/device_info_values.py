import os
import re
import ast
from pathlib import Path

def find_function_calls(file_path, function_name):
    """
    Parse a Python file and find all calls to the specified function
    Returns a list of tuples containing (category, label) for device_info
    or (key) for logdevinfo
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
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent
    
    artifacts_dir = Path( root_dir, 'scripts/artifacts')
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
    doc_path = Path( root_dir, 'admin/docs/device_info_values.md')
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
