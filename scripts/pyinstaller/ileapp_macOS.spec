# -*- mode: python ; coding: utf-8 -*-

import sys

sys.path.insert(0, SPECPATH)
from unifiedlog_binary import unifiedlog_binaries, unifiedlog_datas
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['../../ileapp.py'],
    pathex=['../scripts/artifacts'],
    binaries=unifiedlog_binaries(),
    datas=[
        ('../', 'scripts'),
        ('../../leapp_functions', 'leapp_functions'),
        ('../../assets', 'assets')] + unifiedlog_datas(),
    hiddenimports=[
        'astc_decomp_faster',
        'bencoding',
        'blackboxprotobuf',
        # blackboxprotobuf above is the vendored copy under scripts/ (PyInstaller
        # reports it 'not found'); what actually has to be collected is the real
        # google.protobuf package it imports internals from.
        *collect_submodules('google.protobuf'),
        *collect_submodules('PIL'),
        'Crypto.Cipher.AES',
        'ijson',
        'lib2to3.refactor',
        'liblzfse',
        'mdplist',
        'mmh3',
        'nska_deserialize',
        'pandas',
        'pgpy',
        'pillow_heif',
        'typedstream',
        'xml.etree.ElementTree',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ileapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
