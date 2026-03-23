# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None
ROOT = Path(os.path.abspath(SPECPATH)).parent
IS_MAC = sys.platform == 'darwin'

a = Analysis(
    [str(ROOT / 'ale_switcher' / '__main__.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / 'ale_switcher' / 'gui' / 'static'), 'ale_switcher/gui/static'),
    ],
    hiddenimports=[
        'bottle',
    ] + (
        # Windows-specific
        [
            'pystray._win32',
            'plyer.platforms.win.notification',
            'PIL._tkinter_finder',
            'webview.platforms.edgechromium',
            'clr_loader',
            'pythonnet',
        ] if not IS_MAC else
        # macOS-specific
        [
            'pystray._darwin',
            'plyer.platforms.macosx.notification',
            'webview.platforms.cocoa',
            'objc',
            'Foundation',
            'AppKit',
            'WebKit',
        ]
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'tkinter',
        'test',
        'unittest',
        'pytest',
        'rich',
        'click',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if IS_MAC:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='AleSwitcher',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name='AleSwitcher',
    )

    # Use .icns if available, fallback to .png
    _icns = ROOT / 'build' / 'rsrc' / 'icon.icns'
    _icon_mac = str(_icns) if _icns.exists() else str(ROOT / 'ale_switcher' / 'icon.png')

    app = BUNDLE(
        coll,
        name='AleSwitcher.app',
        icon=_icon_mac,
        bundle_identifier='com.aletech.aleswitcher',
        info_plist={
            'CFBundleShortVersionString': '2.0.0',
            'CFBundleName': 'AleSwitcher',
            'CFBundleDisplayName': 'AleSwitcher',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15',
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='AleSwitcher',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon=str(ROOT / 'build' / 'rsrc' / 'icon.ico'),
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='AleSwitcher',
    )
