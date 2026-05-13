import logging
from datetime import date

import flet as ft
from flet_secure_storage import SecureStorage

from core.constants import DAILY_SCAN_LIMIT, STORAGE_LAST_RESET, STORAGE_SCANS
from core.state import state

logger = logging.getLogger(__name__)


class CreditService:
    def __init__(self, page: ft.Page):
        self._page = page
        self._storage = SecureStorage()

    async def initialize(self) -> int:
        try:
            await self._check_daily_reset()
            used = await self._get_scans()
            state.scans_today = used
            return used
        except Exception as e:
            logger.warning("SecureStorage not available: %s", e)
            state.scans_today = 0
            return 0

    async def can_scan(self) -> bool:
        return state.scans_today < DAILY_SCAN_LIMIT

    async def use_scan(self) -> bool:
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        new_count = state.scans_today + 1
        try:
            await self._storage.set(STORAGE_SCANS, str(new_count))
        except Exception:
            logger.warning("Failed to persist scan count")
        state.scans_today = new_count
        return True

    async def get_remaining(self) -> int:
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)

    async def _check_daily_reset(self):
        today = date.today().isoformat()
        last_reset = await self._storage.get(STORAGE_LAST_RESET)
        if last_reset != today:
            await self._storage.set(STORAGE_SCANS, "0")
            await self._storage.set(STORAGE_LAST_RESET, today)

    async def _get_scans(self) -> int:
        val = await self._storage.get(STORAGE_SCANS)
        try:
            return int(val) if val else 0
        except (TypeError, ValueError):
            return 0
