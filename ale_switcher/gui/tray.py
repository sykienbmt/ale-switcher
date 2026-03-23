"""System tray icon and menu management."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, Menu, MenuItem

if TYPE_CHECKING:
    from .bridge import Api

ICON_PATH = Path(__file__).parent / 'static' / 'img' / 'icon.png'


def _generate_icon_image(size: int = 64) -> Image.Image:
    """Generate a simple 'C2' icon if no icon file exists."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Blue circle background
    draw.ellipse([2, 2, size - 2, size - 2], fill=(59, 130, 246, 255))

    # 'C2' text
    try:
        font = ImageFont.truetype('arial', size // 3)
    except (IOError, OSError):
        font = ImageFont.load_default()

    text = 'Ale'
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    return img


def _get_icon_image() -> Image.Image:
    """Load icon from file or generate one."""
    if ICON_PATH.exists():
        return Image.open(ICON_PATH)
    return _generate_icon_image()


class TrayManager:
    """Manages system tray icon and menu."""

    def __init__(self, window, api: Api):
        self.window = window
        self.api = api
        self.icon = None
        self._visible = True
        self._thread = None

    def start(self):
        """Start tray icon in background thread."""
        image = _get_icon_image()
        self.icon = Icon(
            'AleSwitcher',
            image,
            'AleSwitcher',
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        """Remove tray icon."""
        if self.icon:
            self.icon.stop()

    def _build_menu(self) -> Menu:
        return Menu(
            MenuItem('Show/Hide', self._toggle_window, default=True),
            Menu.SEPARATOR,
            MenuItem('Switch to Optimal', self._switch_optimal),
            MenuItem('Refresh Usage', self._refresh),
            Menu.SEPARATOR,
            MenuItem('Quit', self._quit),
        )

    def _toggle_window(self, icon=None, item=None):
        if self._visible:
            self.window.hide()
        else:
            self.window.show()
        self._visible = not self._visible

    def hide_window(self):
        """Hide window (called from close handler)."""
        self.window.hide()
        self._visible = False

    def _switch_optimal(self, icon=None, item=None):
        try:
            self.api.select_optimal(dry_run=False)
        except Exception:
            pass

    def _refresh(self, icon=None, item=None):
        try:
            self.api.get_usage(force=True)
        except Exception:
            pass

    def _quit(self, icon=None, item=None):
        self.stop()
        self.window.destroy()
