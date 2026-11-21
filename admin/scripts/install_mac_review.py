"""Install the signed-in user's iLEAPP pickup worker and launchd definition."""
import os
import plistlib
import shutil
import sys
import tempfile
from pathlib import Path

LABEL = "org.ileapp.mac-review"
ROOT = Path.home() / "Library/Application Support/iLEAPP/PR Review"


def install(path, content):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(content)
    os.replace(tmp.name, path)


def main():
    os.umask(0o077)
    if sys.platform != "darwin":
        raise SystemExit("This pickup worker requires macOS.")
    binaries = [shutil.which(tool) for tool in ("gh", "codex")]
    if not all(binaries):
        raise SystemExit("Both gh and codex must be installed.")
    source = Path(__file__).resolve().parent
    target = ROOT / "bin"
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    ROOT.chmod(0o700)
    for name in ("mac_review_worker.py", "review_ileapp_pr.py", "check_pr_test_data.py"):
        install(target / name, (source / name).read_bytes())
    agents = Path.home() / "Library/LaunchAgents"
    agents.mkdir(exist_ok=True)
    node = shutil.which("node")
    if node:
        binaries.append(node)
    search = list(dict.fromkeys(str(Path(binary).parent) for binary in binaries))
    plist = {"Label": LABEL, "RunAtLoad": True, "StartInterval": 300,
             "ProgramArguments": [sys.executable, "-B", str(target / "mac_review_worker.py")],
             "WorkingDirectory": str(ROOT), "ProcessType": "Background", "Umask": 0o077,
             "EnvironmentVariables": {"GH_PROMPT_DISABLED": "1", "PATH": ":".join([*search, "/usr/bin", "/bin", "/usr/sbin"])},
             "StandardErrorPath": str(ROOT / "pickup.log"), "StandardOutPath": str(ROOT / "pickup.log")}
    install(agents / (LABEL + ".plist"), plistlib.dumps(plist))


if __name__ == "__main__":
    main()
