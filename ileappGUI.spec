# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['ileappGUI.py'],
             pathex=['.\\scripts\\artifacts'],
             binaries=[],
             datas=[('.\\scripts', '.\\scripts')],
             hiddenimports=[],
             hookspath=['.\\'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ileappGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
	  hide_console='hide-early',
	  disable_windowed_traceback=False,
          upx_exclude=[],
          version='ileappGUI-file_version_info.txt',
          runtime_tmpdir=None )
