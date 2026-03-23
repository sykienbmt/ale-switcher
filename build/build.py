"""Build AleSwitcher GUI application for Windows and macOS."""

import platform
import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).parent
ROOT = BUILD_DIR.parent
SPEC = BUILD_DIR / 'ale_switcher.spec'
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'


def main():
    print(f'Building AleSwitcher GUI for {platform.system()}...')
    print(f'  Root: {ROOT}')
    print(f'  Spec: {SPEC}')

    # Install PyInstaller if needed
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print('Installing PyInstaller...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--clean', '-y',
        '--distpath', str(ROOT / 'dist'),
        '--workpath', str(ROOT / 'build_temp'),
        str(SPEC),
    ]

    print(f'  Running: {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode != 0:
        print('Build failed!')
        sys.exit(1)

    if IS_MAC:
        app_path = ROOT / 'dist' / 'AleSwitcher.app'
        print(f'\nBuild complete: {app_path}')
        print(f'Test with: open {app_path}')
        print(f'To create DMG: hdiutil create -volname AleSwitcher -srcfolder {app_path} -ov -format UDZO dist/AleSwitcher.dmg')
    else:
        dist_dir = ROOT / 'dist' / 'AleSwitcher'
        print(f'\nBuild complete: {dist_dir}')
        print(f'Test with: {dist_dir / "AleSwitcher.exe"}')
        print(f'To create installer: compile build/installer.iss with Inno Setup')


if __name__ == '__main__':
    main()
