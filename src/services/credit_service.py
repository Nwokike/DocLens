import base64
import contextlib
import logging
import os
from datetime import date

import flet_secure_storage as fss

from core.constants import DAILY_SCAN_LIMIT
from core.state import state

logger = logging.getLogger(__name__)

try:
    _STORAGE = fss.SecureStorage(
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
    _HAS_STORAGE = True
except Exception as e:
    logger.warning("SecureStorage init failed (%s)", e)
    _STORAGE = None
    _HAS_STORAGE = False


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
