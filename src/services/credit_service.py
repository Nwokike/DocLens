import base64
import contextlib
import logging
import os
from datetime import date

import flet as ft
import flet_secure_storage as fss

from core.constants import DAILY_SCAN_LIMIT
from core.state import state

logger = logging.getLogger(__name__)


class CreditService:
    def __init__(self, page: ft.Page):
        self._page = page
        self._storage = None
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    async def _ensure_storage(self):
        if self._storage is not None:
            return
        try:
            self._storage = fss.SecureStorage(
                web_options=fss.WebOptions(
                    db_name="doclens_secure",
                    public_key="doclens_public",
                    wrap_key=base64.urlsafe_b64encode(os.urandom(32)).decode(),
                    wrap_key_iv=base64.urlsafe_b64encode(os.urandom(16)).decode(),
                ),
                android_options=fss.AndroidOptions(
                    reset_on_error=True,
                    migrate_on_algorithm_change=True,
                    enforce_biometrics=False,
                    key_cipher_algorithm=fss.KeyCipherAlgorithm.AES_GCM_NO_PADDING,
                    storage_cipher_algorithm=fss.StorageCipherAlgorithm.AES_GCM_NO_PADDING,
                ),
            )
            self._page.overlay.append(self._storage)
        except Exception as e:
            logger.warning("SecureStorage init failed (%s)", e)
            self._storage = None

    async def _load(self):
        if self._ready:
            return
        await self._ensure_storage()
        if self._storage is None:
            self._ready = True
            return
        try:
            today = date.today().isoformat()
            last = await self._storage.get("dc_last_reset")
            if last != today:
                await self._storage.set("dc_scans", "0")
                await self._storage.set("dc_last_reset", today)
                state.scans_today = 0
            else:
                val = await self._storage.get("dc_scans")
                state.scans_today = int(val) if val else 0
            self._ready = True
        except Exception as e:
            logger.warning("SecureStorage load failed (%s) — using in-memory", e)
            self._ready = True

    async def use_scan(self) -> bool:
        await self._load()
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        state.scans_today += 1
        if self._storage is not None and self._ready:
            with contextlib.suppress(Exception):
                await self._storage.set("dc_scans", str(state.scans_today))
        return True

    async def get_remaining(self) -> int:
        await self._load()
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)

    async def initialize(self):
        await self._load()
