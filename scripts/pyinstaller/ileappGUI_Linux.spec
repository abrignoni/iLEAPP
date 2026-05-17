# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../../ileappGUI.py'],
    pathex=['../scripts/artifacts'],
    binaries=[],
    datas=[('../', 'scripts'), ('../../assets', 'assets')],
    hiddenimports=[
        'astc_decomp_faster',
        'bencoding',
        'blackboxprotobuf',
        'Crypto.Cipher.AES',
        'ijson',
        'lib2to3.refactor',
        'liblzfse',
        'mdplist',
        'mmh3',
        'nska_deserialize',
        'pandas',
        'pgpy',
        'PIL._tkinter_finder',
        'pillow_heif',
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
    name='ileappGUI',
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
)
