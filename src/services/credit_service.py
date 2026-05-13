import contextlib
import logging
from datetime import date

from core.constants import DAILY_SCAN_LIMIT
from core.state import state

logger = logging.getLogger(__name__)

try:
    from flet_secure_storage import AndroidOptions
    from flet_secure_storage import SecureStorage as _SecureStorage

    _STORAGE = _SecureStorage(
        android_options=AndroidOptions(
            reset_on_error=True,
            migrate_on_algorithm_change=True,
        ),
    )
    _HAS_STORAGE = True
except Exception:
    _STORAGE = None
    _HAS_STORAGE = False
    logger.info("SecureStorage not available — using in-memory credits")


class CreditService:
    def __init__(self):
        state.scans_today = 0
        self._loaded = False

    async def _load(self):
        if self._loaded or not _HAS_STORAGE:
            return
        try:
            today = date.today().isoformat()
            last = await _STORAGE.get("dc_last_reset")
            if last != today:
                await _STORAGE.set("dc_scans", "0")
                await _STORAGE.set("dc_last_reset", today)
                state.scans_today = 0
            else:
                val = await _STORAGE.get("dc_scans")
                state.scans_today = int(val) if val else 0
            self._loaded = True
        except Exception as e:
            logger.warning("SecureStorage load failed (%s) — using in-memory", e)
            self._loaded = True

    async def _save(self):
        if not _HAS_STORAGE or not self._loaded:
            return
        with contextlib.suppress(Exception):
            await _STORAGE.set("dc_scans", str(state.scans_today))

    async def use_scan(self) -> bool:
        await self._load()
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        state.scans_today += 1
        await self._save()
        return True

    async def get_remaining(self) -> int:
        await self._load()
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)
