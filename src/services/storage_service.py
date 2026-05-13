"""Platform-resilient key-value storage.

Uses a local JSON file — pure Python, no Flet plugin dependencies.
Avoids all TimeoutException errors from client-side plugins
(SecureStorage, SharedPreferences) in ``flet run --android`` dev mode.

Works on desktop, Android dev, and production APK.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import flet as ft

logger = logging.getLogger(__name__)

_STORAGE_DIR = Path.home() / ".doclens"
_STORAGE_FILE = _STORAGE_DIR / "storage.json"


class StorageService:
    """Async key-value store backed by a local JSON file."""

    def __init__(self, page: ft.Page):
        self._page = page
        self._data: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        try:
            _STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            if _STORAGE_FILE.exists():
                self._data = json.loads(_STORAGE_FILE.read_text(encoding="utf-8"))
            else:
                self._data = {}
        except Exception as e:
            logger.warning("Storage load failed: %s", e)
            self._data = {}

    def _save(self) -> None:
        try:
            _STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            _STORAGE_FILE.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("Storage save failed: %s", e)

    async def get(self, key: str) -> str | None:
        async with self._lock:
            return self._data.get(key)

    async def set(self, key: str, value: str) -> None:
        async with self._lock:
            self._data[key] = value
            self._save()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)
            self._save()
