import contextlib
import logging
from datetime import date

from core.constants import DAILY_SCAN_LIMIT, STORAGE_LAST_RESET, STORAGE_SCANS
from core.state import state

logger = logging.getLogger(__name__)


class CreditService:
    def __init__(self, storage):
        self._storage = storage

    async def initialize(self):
        try:
            today = date.today().isoformat()
            last = await self._storage.get(STORAGE_LAST_RESET)
            if last != today:
                await self._storage.set(STORAGE_SCANS, "0")
                await self._storage.set(STORAGE_LAST_RESET, today)
                state.scans_today = 0
            else:
                val = await self._storage.get(STORAGE_SCANS)
                state.scans_today = int(val) if val else 0
        except Exception as e:
            logger.warning("Credit load failed: %s", e)
            state.scans_today = 0

    async def use_scan(self) -> bool:
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        state.scans_today += 1
        with contextlib.suppress(Exception):
            await self._storage.set(STORAGE_SCANS, str(state.scans_today))
        return True

    async def get_remaining(self) -> int:
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)
