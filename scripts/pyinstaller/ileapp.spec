# -*- mode: python ; coding: utf-8 -*-

import sys

sys.path.insert(0, SPECPATH)
from unifiedlog_binary import unifiedlog_binaries, unifiedlog_datas
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
   ['..\\..\\ileapp.py'],
   pathex=['..\\scripts\\artifacts'],
   binaries=unifiedlog_binaries(windows=True),
   datas=[
      ('..\\', '.\\scripts'),
      ('..\\..\\leapp_functions', '.\\leapp_functions'),
      ('..\\..\\assets', '.\\assets')] + unifiedlog_datas(windows=True),
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
   hookspath=['./'],
   runtime_hooks=[],
   excludes=[],
   win_no_prefer_redirects=False,
   win_private_assemblies=False,
   cipher=block_cipher,
   noarchive=False)

pyz = PYZ(
   a.pure,
   a.zipped_data,
   cipher=block_cipher)

exe = EXE(
   pyz,
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
   version='ileapp-file_version_info.txt',
   console=True )
