"""Windows toast notifications for high usage alerts."""

from __future__ import annotations

import time
import threading
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .bridge import Api


class NotificationManager:
    """Polls usage and sends toast notifications when thresholds are exceeded."""

    def __init__(self, api: Api, threshold: float = 85.0, cooldown_seconds: int = 900):
        self.api = api
        self.threshold = threshold
        self.cooldown = cooldown_seconds
        self._last_notified: Dict[str, float] = {}
        self._running = False
        self._thread = None

    def start(self, interval: int = 300):
        """Start polling in background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _poll_loop(self, interval: int):
        # Wait before first check to let app initialize
        time.sleep(30)
        while self._running:
            try:
                self._check_usage()
            except Exception:
                pass
            time.sleep(interval)

    def _check_usage(self):
        data = self.api.get_usage(force=False)
        if isinstance(data, dict) and 'error' in data:
            return
        if not isinstance(data, list):
            return

        for acc in data:
            usage = acc.get('usage')
            if not usage:
                continue

            uuid = acc.get('uuid', '')
            name = acc.get('nickname') or acc.get('email', 'Unknown')

            overall = (usage.get('seven_day') or {}).get('utilization')
            if overall is not None and overall >= self.threshold:
                self._notify(uuid, name, '7d Overall', overall)

            sonnet = (usage.get('seven_day_sonnet') or {}).get('utilization')
            if sonnet is not None and sonnet >= self.threshold:
                self._notify(uuid, name, '7d Sonnet', sonnet)

    def _notify(self, uuid: str, name: str, window: str, utilization: float):
        key = f'{uuid}_{window}'
        now = time.time()

        if key in self._last_notified and (now - self._last_notified[key]) < self.cooldown:
            return

        self._last_notified[key] = now

        try:
            from plyer import notification

            notification.notify(
                title='AleSwitcher - High Usage',
                message=f'{name}: {window} at {utilization:.0f}%',
                app_name='AleSwitcher',
                timeout=10,
            )
        except Exception:
            pass
