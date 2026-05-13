import logging
from datetime import date

import flet as ft
from flet_secure_storage import SecureStorage

from core.constants import DAILY_SCAN_LIMIT
from core.state import state

logger = logging.getLogger(__name__)


class CreditService:
    def __init__(self):
        self._storage = SecureStorage()
        self._ready = False

    @property
    def ready(self) -> bool:
        return self._ready

    async def _ensure_ready(self):
        if self._ready:
            return
        try:
            today = date.today().isoformat()
            last_reset = await self._storage.get("dc_last_reset")
            if last_reset != today:
                await self._storage.set("dc_scans", "0")
                await self._storage.set("dc_last_reset", today)
                state.scans_today = 0
            else:
                val = await self._storage.get("dc_scans")
                state.scans_today = int(val) if val else 0
            self._ready = True
        except Exception:
            state.scans_today = 0

    async def use_scan(self) -> bool:
        await self._ensure_ready()
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        state.scans_today += 1
        try:
            if self._ready:
                await self._storage.set("dc_scans", str(state.scans_today))
        except Exception:
            pass
        return True

    async def get_remaining(self) -> int:
        await self._ensure_ready()
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)
