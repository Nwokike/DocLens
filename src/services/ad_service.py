import asyncio
import logging
import sys

import flet as ft

logger = logging.getLogger(__name__)

_HAS_ADS = False
try:
    from flet_ads import BannerAd, InterstitialAd

    _HAS_ADS = True
except ImportError:
    pass


def _is_mobile() -> bool:
    return sys.platform not in ("win32", "linux", "darwin")


class AdService:
    def __init__(self, page: ft.Page):
        self._page = page
        self._interstitial = None
        self._available = _HAS_ADS and _is_mobile()

    @property
    def available(self) -> bool:
        return self._available

    def get_banner_ad(self) -> ft.Control:
        if not self._available:
            return ft.Container(width=0, height=0)
        try:
            from core.constants import AD_BANNER_ANDROID

            ad = BannerAd(
                unit_id=AD_BANNER_ANDROID,
                on_error=lambda e: None,
            )
            return ft.Container(
                content=ad,
                width=320,
                height=50,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding(0, 10, 0, 10),
            )
        except Exception:
            return ft.Container(width=0, height=0)

    async def preload_interstitial(self):
        if not self._available:
            return
        try:
            from core.constants import AD_INTERSTITIAL_ANDROID

            self._interstitial = InterstitialAd(
                unit_id=AD_INTERSTITIAL_ANDROID,
                on_load=lambda e: None,
                on_error=lambda e: None,
                on_close=self._handle_close,
            )
        except Exception:
            self._interstitial = None

    async def _handle_close(self, e):
        await self.preload_interstitial()

    async def show_interstitial(self) -> bool:
        if self._interstitial:
            try:
                await self._interstitial.show()
                return True
            except Exception:
                return False
        return False
