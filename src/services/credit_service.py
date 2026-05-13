import logging

from core.constants import DAILY_SCAN_LIMIT
from core.state import state

logger = logging.getLogger(__name__)


class CreditService:
    def __init__(self, page=None):
        state.scans_today = 0

    async def use_scan(self) -> bool:
        if state.scans_today >= DAILY_SCAN_LIMIT:
            return False
        state.scans_today += 1
        return True

    async def get_remaining(self) -> int:
        return max(0, DAILY_SCAN_LIMIT - state.scans_today)
