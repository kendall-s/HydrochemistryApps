# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\she384\\Documents\\Python_Apps\\Hydrochemistry_Apps'],
             binaries=[],
             datas=[],
             hiddenimports=['cftime'],
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
          name='Hydrochemistry Apps',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
		  icon = 'assets\\2dropsshadow.ico',
		  version = 'C:\\Users\\she384\\Documents\\Python_Apps\\Hydrochemistry_Apps\\hydro_apps_version.rc')
