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
        'lib2to3.refactor',
        'liblzfse',
        'mdplist',
        'mmh3',
        'nska_deserialize',
        'pandas',
        'pgpy',
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
    [],
    exclude_binaries=True,
    name='ileappGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ileappGUI',
)
app = BUNDLE(
    coll,
    name='ileappGUI.app',
    icon='../../assets/icon.icns',
    bundle_identifier='4n6.brigs.iLEAPP',
    version='2.1.3'
)
