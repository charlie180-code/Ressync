# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os


binaries=[
    ('./apps/libs/*.dll', 'libs')
]

datas = [
    ('.env', '.'),
    ('apps/templates', 'templates'),
    ('apps/static', 'static')
]

hidden_imports = collect_submodules('apps')
hidden_imports += ['tkinter']

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ressync',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='./build/icon.ico'
)
