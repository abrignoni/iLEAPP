# PyInstaller spec for iLEAPP. Driven by packaging/build.py:
#
#   python packaging/build.py exe              one folder -> dist/iLEAPP/, and dist/iLEAPP.app on macOS
#   python packaging/build.py exe --onefile    one executable -> dist/ileapp, or dist/ileapp.exe
#
# One spec for every platform, building one executable, ileapp, from packaging/entrypoint.py:
# the window when it is started without arguments, the command line when it is given some.
# It replaced six specs, one per program and platform, each with its own copy of the
# hidden imports and its own copy of the version.
#
# ONEFILE comes from the ILEAPP_ONEFILE environment variable, which build.py sets, so a
# build never edits this file. What goes into the bundle, the version included, is decided
# in build.py, which this file loads; what is left here is the PyInstaller wiring.

import importlib.util
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ONEFILE = os.environ.get("ILEAPP_ONEFILE", "") == "1"   # set by build.py, never by editing

# Loaded under its own name: "build" is also the name of a PyPI package.
_driver_spec = importlib.util.spec_from_file_location("ileapp_build_driver",
                                                      Path(SPECPATH) / "build.py")
driver = importlib.util.module_from_spec(_driver_spec)
_driver_spec.loader.exec_module(driver)

VERSION = driver.read_version()
NUMERIC = driver.numeric_version(VERSION)

hiddenimports = driver.hidden_imports() + [
    # The vendored scripts/blackboxprotobuf imports google.protobuf internals, and the
    # artifacts reach PIL submodules its hook leaves out. A frozen build crashed on
    # startup without each of them.
    *collect_submodules("google.protobuf"),
    *collect_submodules("PIL"),
]

a = Analysis(
    [str(driver.ENTRYPOINT)],
    pathex=[str(driver.ROOT)],
    binaries=driver.bundle_binaries(),
    datas=driver.bundle_datas(),
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe_kwargs = dict(
    name=driver.EXE,
    # A console program, so the command line prints and returns its exit code. On Windows
    # the console is hidden at once when the program did not inherit one, as when the
    # window is started from Explorer or the Start menu; started from a terminal it keeps
    # that terminal. The GUI build used hide-early the same way before the two merged.
    console=True,
    hide_console="hide-early" if sys.platform == "win32" else None,
    strip=False,
    upx=False,
)

if sys.platform == "win32":
    from PyInstaller.utils.win32 import versioninfo as vi

    fields = driver.windows_version_fields(VERSION)
    exe_kwargs["icon"] = str(driver.ICO)
    exe_kwargs["version"] = vi.VSVersionInfo(
        ffi=vi.FixedFileInfo(filevers=fields["numbers"], prodvers=fields["numbers"],
                             mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0,
                             date=(0, 0)),
        kids=[
            vi.StringFileInfo([vi.StringTable("040904b0", [
                vi.StringStruct(key, value) for key, value in fields["strings"].items()])]),
            vi.VarFileInfo([vi.VarStruct("Translation", [1033, 1200])]),
        ])

if ONEFILE:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], runtime_tmpdir=None, **exe_kwargs)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
              contents_directory=driver.CONTENTS, **exe_kwargs)
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=driver.APP)

    if sys.platform == "darwin":
        # A .app around the one-folder build. PyInstaller signs it ad hoc while it builds,
        # so a Developer ID signature goes on after this, on the finished bundle.
        app = BUNDLE(
            coll,
            name=driver.macos_app().name,
            icon=str(driver.ICNS),
            bundle_identifier=driver.BUNDLE_ID,
            version=NUMERIC,
            info_plist={
                "CFBundleShortVersionString": NUMERIC,
                "CFBundleVersion": NUMERIC,
                "NSHighResolutionCapable": True,
                # console=True, which the command line needs, makes PyInstaller mark the
                # bundle background-only, and a background-only app has no Dock icon and
                # no menu bar while its window is open.
                "LSBackgroundOnly": False,
            },
        )
