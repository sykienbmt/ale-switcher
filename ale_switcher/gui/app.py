"""pywebview application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import webview

from ..infrastructure.factory import ServiceFactory
from .bridge import Api


def _get_static_dir() -> Path:
    """Resolve static directory, handling PyInstaller bundles."""
    if getattr(sys, '_MEIPASS', None):
        return Path(sys._MEIPASS) / 'ale_switcher' / 'gui' / 'static'
    return Path(__file__).parent / 'static'


STATIC_DIR = _get_static_dir()


def start_app(debug: bool = False):
    """Launch the AleSwitcher GUI application."""
    factory = ServiceFactory()
    api = Api(factory)

    window = webview.create_window(
        title='AleSwitcher',
        url=str(STATIC_DIR / 'index.html'),
        js_api=api,
        width=1000,
        height=700,
        min_size=(800, 500),
        text_select=False,
    )

    def on_loaded():
        """Initialize tray and notifications after window is ready."""
        try:
            from .tray import TrayManager

            tray = TrayManager(window, api)
            tray.start()

            # Override close to minimize to tray instead of quitting
            def on_closing():
                tray.hide_window()
                return False  # Cancel close

            window.events.closing += on_closing
        except Exception as e:
            print(f'[AleSwitcher] Tray init failed: {e}')

        try:
            from .notifications import NotificationManager

            notifier = NotificationManager(api)
            notifier.start(interval=300)
        except Exception as e:
            print(f'[AleSwitcher] Notification init failed: {e}')

    webview.start(func=on_loaded, debug=debug)
    factory.close()
