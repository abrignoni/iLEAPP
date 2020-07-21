# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


#
# Update baseDir to the location where you downloaded the iLEAPP repository
#

baseDir = 'C:\\Users\\forensic user\\Documents\\GitHub\\iLEAPP'

a = Analysis(['ileappGUI.py'],
             pathex=[baseDir],
             binaries=[],
             datas=[(baseDir + '\\scripts\\logo.jpg', '.\\scripts'),
                    (baseDir + '\\scripts\\dashboard.css', '.\\scripts'),
                    (baseDir + '\\scripts\\feather.min.js', '.\\scripts'),
                    (baseDir + '\\scripts\\MDB-Free_4.13.0', '.\\scripts\\MDB-Free_4.13.0')],
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
          name='ileappGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
