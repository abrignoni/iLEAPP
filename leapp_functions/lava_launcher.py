"""Detect and launch the LAVA desktop application."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


LAVA_WEBSITE = "https://www.leapps.org/#lava"


def _windows_detached_popen(args):
    subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=(
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        ),
    )


def _windows_registry_value(root, key_path):
    try:
        import winreg

        with winreg.OpenKey(root, key_path) as key:
            return winreg.QueryValueEx(key, None)[0]
    except (ImportError, OSError):
        return None


def _windows_has_lava_association():
    try:
        import winreg
    except ImportError:
        return False

    prog_ids = []
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.lava\UserChoice",
        ) as key:
            prog_ids.append(winreg.QueryValueEx(key, "ProgId")[0])
    except OSError:
        pass

    for root, prefix in (
        (winreg.HKEY_CURRENT_USER, r"Software\Classes"),
        (winreg.HKEY_CLASSES_ROOT, ""),
    ):
        extension_key = rf"{prefix}\.lava" if prefix else r".lava"
        prog_id = _windows_registry_value(root, extension_key)
        if prog_id:
            prog_ids.append(prog_id)

        for prog_id in prog_ids:
            command_key = (
                rf"{prefix}\{prog_id}\shell\open\command"
                if prefix
                else rf"{prog_id}\shell\open\command"
            )
            command = _windows_registry_value(root, command_key)
            if command and "lava" in command.lower():
                return True

    return False


def _windows_lava_executable():
    executable = shutil.which("LAVA.exe") or shutil.which("lava.exe")
    if executable:
        return executable

    candidates = []
    for env_name in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"):
        base_path = os.environ.get(env_name)
        if base_path:
            candidates.extend(
                (
                    Path(base_path, "Programs", "LAVA", "LAVA.exe"),
                    Path(base_path, "LAVA", "LAVA.exe"),
                )
            )

    for path in candidates:
        try:
            if path.is_file():
                return str(path)
        except OSError:
            continue
    return None


def _linux_lava_desktop_file(project_path):
    xdg_mime = shutil.which("xdg-mime")
    if not xdg_mime or not shutil.which("xdg-open"):
        return None

    try:
        mime_type = subprocess.run(
            [xdg_mime, "query", "filetype", project_path],
            capture_output=True,
            check=False,
            text=True,
        ).stdout.strip()
        desktop_file = subprocess.run(
            [xdg_mime, "query", "default", mime_type],
            capture_output=True,
            check=False,
            text=True,
        ).stdout.strip()
    except OSError:
        return None

    if mime_type and desktop_file and "lava" in desktop_file.lower():
        return desktop_file
    return None


def _linux_lava_executable():
    for executable_name in ("lava", "LAVA", "lava.AppImage", "LAVA.AppImage"):
        executable = shutil.which(executable_name)
        if executable:
            return executable

    candidates = (
        Path.home() / "Applications" / "LAVA.AppImage",
        Path.home() / "Applications" / "lava.AppImage",
        Path.home() / ".local" / "bin" / "lava",
        Path("/opt/LAVA/LAVA.AppImage"),
        Path("/opt/lava/lava.AppImage"),
    )
    for path in candidates:
        try:
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)
        except OSError:
            continue
    return None


def find_lava_launcher(project_path):
    """Return a launcher description for LAVA, or None when it is not found."""

    if sys.platform == "win32":
        executable = _windows_lava_executable()
        if executable:
            return ("executable", executable)
        if _windows_has_lava_association():
            return ("association", None)
        return None

    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["open", "-Ra", "LAVA"],
                capture_output=True,
                check=False,
            )
        except OSError:
            return None
        return ("application", "LAVA") if result.returncode == 0 else None

    executable = _linux_lava_executable()
    if executable:
        return ("executable", executable)
    if _linux_lava_desktop_file(project_path):
        return ("association", None)
    return None


def open_lava_project(project_path, launcher, log=print):
    """Open a LEAPP project using a launcher returned by find_lava_launcher."""

    launcher_type, launcher_value = launcher
    log(
        f"LAVA launcher: type={launcher_type!r}, value={launcher_value!r}, "
        f"project={project_path!r}"
    )
    if launcher_type == "executable":
        if sys.platform == "win32":
            log("LAVA detected as executable")
            _windows_detached_popen([launcher_value, project_path])
        else:
            subprocess.Popen([launcher_value, project_path])
    elif launcher_type == "application":
        log("LAVA detected as application")
        subprocess.Popen(["open", "-a", launcher_value, project_path])
    elif launcher_type == "association":
        log("LAVA detected as association")
        if sys.platform == "win32":
            explorer = shutil.which("explorer.exe")
            if not explorer:
                raise FileNotFoundError("explorer.exe is not available")
            _windows_detached_popen([explorer, project_path])
        else:
            xdg_open = shutil.which("xdg-open")
            if not xdg_open:
                raise FileNotFoundError("xdg-open is not installed")
            subprocess.Popen([xdg_open, project_path])
    else:
        raise ValueError(f"Unknown LAVA launcher type: {launcher_type}")


def open_output_folder(output_path):
    """Open an output directory in the platform's file manager."""

    if sys.platform == "win32":
        os.startfile(output_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", output_path])
    else:
        xdg_open = shutil.which("xdg-open")
        if not xdg_open:
            raise FileNotFoundError("xdg-open is not installed")
        subprocess.Popen([xdg_open, output_path])
