# AleSwitcher GUI

Desktop application for managing multiple Claude Code accounts.

## Quick Start (Development)

```bash
pip install -e .
python -m ale_switcher
# or with debug: python -m ale_switcher --debug
```

## Build Installer

### Prerequisites

- Python 3.10+
- [Inno Setup](https://jrsoftware.org/isdl.php) (for installer)

### Steps

```bash
# 1. Install dependencies
pip install -e .
pip install pyinstaller

# 2. Build with PyInstaller
python build/build.py

# 3. Test the exe
dist/ale_switcher/ale_switcher.exe

# 4. Create installer (requires Inno Setup)
iscc build/installer.iss
# Output: dist/AleSwitcher-Setup.exe
```

### Rebuild Tailwind CSS (optional)

Only needed if you modify `index.html` or `app.js`:

```bash
cd ale_switcher/gui
npm install -D tailwindcss@3
npx tailwindcss -i static/css/input.css -o static/css/tailwind.min.css --minify
```

## Project Structure

```
ale_switcher/
  __main__.py          # Entry point
  constants.py         # Paths & config
  log.py               # Simple logger (replaces Rich console)
  config.py            # Headers config
  utils.py             # Utilities
  core/                # Business logic models
  data/                # SQLite store, credential management
  infrastructure/      # API client, OAuth, file locking
  services/            # Account, session, switching services
  gui/                 # pywebview app + HTML/JS/CSS frontend
    app.py             # Window management
    bridge.py          # Python <-> JS API bridge
    tray.py            # System tray icon
    notifications.py   # Windows toast alerts
    static/            # Web UI (Tailwind + Alpine.js)
build/
  build.py             # PyInstaller build script
  ale_switcher.spec      # PyInstaller config
  installer.iss        # Inno Setup installer script
  rsrc/icon.ico        # App icon
```
