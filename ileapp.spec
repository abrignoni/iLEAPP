# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['ileapp.py'],
             pathex=[],
             binaries=[],
            datas=[('.\\scripts\\logo.jpg', '.\\scripts'),
                    ('.\\scripts\\dashboard.css', '.\\scripts'),
                    ('.\\scripts\\dark-mode.css', '.\\scripts'),
                    ('.\\scripts\\dark-mode-switch.js', '.\\scripts'),
                    ('.\\scripts\\feather.min.js', '.\\scripts'),
                    ('.\\scripts\\chats.css', '.\\scripts'),
                    ('.\\scripts\\MDB-Free_4.13.0', '.\\scripts\\MDB-Free_4.13.0')],
             hiddenimports=[],
             hookspath=[],
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
          name='ileapp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
